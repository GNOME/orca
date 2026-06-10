# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches

"""Provides centralized storage and invalidation for accessibility-related caches."""

from __future__ import annotations

import math
import threading
import time
import weakref
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from . import debug

if TYPE_CHECKING:
    from collections.abc import Callable, Hashable
    from types import TracebackType

# Internal miss sentinel for callers that need to distinguish a cache miss from cached None.
MISSING = object()

# Local caches can be forced clear in response to accessibility events.
# The timeout limits stale data and cache growth when those events are missing.
DEFAULT_CLEAR_INTERVAL_SECONDS = 60


class Lifetime(Enum):
    """Defines how long a cache registration retains its owner."""

    # For caches shared by process-lifetime owners such as Generator and AX* classes.
    PROCESS = auto()
    # For caches owned by reclaimable objects such as per-script utility instances.
    OWNER = auto()


class ClearPolicy(Enum):
    """Defines whether routine forced clearing includes a cache."""

    # Most cached values should be discarded when a routine forced clear is requested.
    CLEAR = auto()

    # Values governed by a distinct validity policy remain until that policy invalidates them.
    PRESERVE = auto()


@dataclass
class _Cache:
    """Stores ownership and clearing policy for one cache."""

    values: dict[Hashable, Any] = field(default_factory=dict)
    invalidation_groups: frozenset[str] = field(default_factory=frozenset)
    clear_on_demand: ClearPolicy = ClearPolicy.CLEAR
    clear_interval_seconds: float | None = None
    next_clear_time: float | None = None
    expiration_times: dict[Hashable, float] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class _ProcessOwnerReference:
    """Retains an owner of process-lifetime caches."""

    owner: object

    def get(self) -> object:
        """Returns the retained owner."""

        return self.owner


@dataclass
class _ReclaimableOwnerReference:
    """Provides an owner reference without extending its lifetime."""

    reference: weakref.ReferenceType[object]

    def get(self) -> object | None:
        """Returns the owner while it remains alive."""

        return self.reference()


@dataclass
class _OwnerCaches:
    """Stores caches belonging to one owner."""

    owner_ref: _ProcessOwnerReference | _ReclaimableOwnerReference
    lifetime: Lifetime
    caches: dict[str, _Cache] = field(default_factory=dict)


@dataclass(frozen=True)
class _CacheAccessorBackend:
    """Stores manager operations used by cache accessors."""

    get_value: Callable[[_Cache, Hashable, Any], Any]
    contains_value: Callable[[_Cache, Hashable], bool]
    get_scoped_value: Callable[[int, str, _Cache, CacheScope, Hashable, Any], Any]
    contains_scoped_value: Callable[[int, str, _Cache, CacheScope, Hashable], bool]
    put_value: Callable[[_Cache, Hashable, Any, float | None], None]
    put_scoped_value: Callable[[int, str, _Cache, CacheScope, Hashable, Any], None]
    discard_value: Callable[[_Cache, Hashable], None]
    discard_scoped_value: Callable[[int, str, _Cache, CacheScope, Hashable], None]
    invalidate_cache: Callable[[int, str, _Cache, str, bool], None]


class CacheScope:
    """Identifies cached values retained only for one bounded operation."""

    def __init__(self, manager: AXCacheManager) -> None:
        self._manager = manager

    def __enter__(self) -> CacheScope:  # noqa: PYI034 - Python 3.10 has no typing.Self.
        """Returns the active scope."""

        return self

    def __exit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """Ends this scope and discards its cached values."""

        self._manager.end_scope(self)

    def is_owned_by(self, manager: AXCacheManager) -> bool:
        """Returns True if manager created this scope."""

        return self._manager is manager


class CacheAccessor:
    """Provides direct access to one registered cache."""

    def __init__(
        self,
        backend: _CacheAccessorBackend,
        owner_id: int,
        cache_name: str,
        cache: _Cache,
    ) -> None:
        self._backend = backend
        self._owner_id = owner_id
        self._cache_name = cache_name
        self._cache = cache

    def get(self, key: Hashable, default: Any = MISSING) -> Any:
        """Returns the stored value for key, or default on a miss."""

        return self._backend.get_value(self._cache, key, default)

    def contains(self, key: Hashable) -> bool:
        """Returns True if key has a non-expired stored value."""

        return self._backend.contains_value(self._cache, key)

    def get_scoped(self, scope: CacheScope, key: Hashable, default: Any = MISSING) -> Any:
        """Returns the scoped value for key, or default on a miss."""

        return self._backend.get_scoped_value(
            self._owner_id, self._cache_name, self._cache, scope, key, default
        )

    def contains_scoped(self, scope: CacheScope, key: Hashable) -> bool:
        """Returns True if key has a scoped value."""

        return self._backend.contains_scoped_value(
            self._owner_id, self._cache_name, self._cache, scope, key
        )

    def put(self, key: Hashable, value: Any, *, expires_at: float | None = None) -> None:
        """Stores value for key, optionally until a monotonic deadline."""

        if expires_at is not None and (
            not isinstance(expires_at, (int, float)) or not math.isfinite(expires_at)
        ):
            msg = f"AXCacheManager: Invalid expiration time for {self._cache_name}: {expires_at}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._backend.put_value(self._cache, key, value, expires_at)

    def put_scoped(self, scope: CacheScope, key: Hashable, value: Any) -> None:
        """Stores value until the bounded scope ends."""

        self._backend.put_scoped_value(
            self._owner_id, self._cache_name, self._cache, scope, key, value
        )

    def discard(self, key: Hashable) -> None:
        """Removes the stored value for key, if present."""

        self._backend.discard_value(self._cache, key)

    def discard_scoped(self, scope: CacheScope, key: Hashable) -> None:
        """Removes the scoped value for key, if present."""

        self._backend.discard_scoped_value(
            self._owner_id, self._cache_name, self._cache, scope, key
        )

    def invalidate(self, reason: str = "", *, log: bool = True) -> None:
        """Clears all values in the cache."""

        self._backend.invalidate_cache(self._owner_id, self._cache_name, self._cache, reason, log)


class AXCacheManager:
    """Stores accessibility-related values in owner-controlled named caches."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._owner_caches: dict[int, _OwnerCaches] = {}
        self._scoped_values: weakref.WeakKeyDictionary[
            CacheScope, dict[tuple[int, str], dict[Hashable, Any]]
        ] = weakref.WeakKeyDictionary()
        # Clearing values can synchronously trigger weak-owner cleanup on this thread.
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._clearing_thread_started = False
        self._accessor_backend = _CacheAccessorBackend(
            get_value=self._get_accessor_value,
            contains_value=self._contains_accessor_value,
            get_scoped_value=self._get_scoped_accessor_value,
            contains_scoped_value=self._contains_scoped_accessor_value,
            put_value=self._put_accessor_value,
            put_scoped_value=self._put_scoped_accessor_value,
            discard_value=self._discard_accessor_value,
            discard_scoped_value=self._discard_scoped_accessor_value,
            invalidate_cache=self._invalidate_accessor_cache,
        )

    def register_cache(
        self,
        owner: object,
        cache_name: str,
        *,
        lifetime: Lifetime,
        clear_on_demand: ClearPolicy = ClearPolicy.CLEAR,
        clear_interval_seconds: float | None = DEFAULT_CLEAR_INTERVAL_SECONDS,
        invalidation_groups: set[str] | frozenset[str] = frozenset(),
    ) -> bool:
        """Registers cache ownership and clearing policy, returning False on failure."""

        if not cache_name:
            debug.print_message(debug.LEVEL_INFO, "AXCacheManager: Empty cache name.", True)
            return False

        if not isinstance(lifetime, Lifetime):
            msg = f"AXCacheManager: Invalid cache lifetime for {cache_name}: {lifetime}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not isinstance(clear_on_demand, ClearPolicy):
            msg = (
                f"AXCacheManager: Invalid on-demand clearing policy for {cache_name}: "
                f"{clear_on_demand}"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if clear_interval_seconds is not None and (
            not isinstance(clear_interval_seconds, (int, float))
            or not math.isfinite(clear_interval_seconds)
            or clear_interval_seconds <= 0
        ):
            msg = (
                f"AXCacheManager: Invalid clear interval for {cache_name}: {clear_interval_seconds}"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        start_thread = False
        collision = False
        unsupported_owner = False
        conflicting_lifetime = False
        with self._condition:
            owner_caches = self._get_owner_caches_locked(owner)
            if owner_caches is not None and owner_caches.lifetime is not lifetime:
                conflicting_lifetime = True
            elif owner_caches is None:
                owner_ref = self._make_owner_reference(id(owner), owner, lifetime)
                if owner_ref is None:
                    unsupported_owner = True
                else:
                    owner_caches = _OwnerCaches(owner_ref, lifetime)
                    self._owner_caches[id(owner)] = owner_caches

            if owner_caches is not None and not conflicting_lifetime:
                if cache_name in owner_caches.caches:
                    collision = True
                else:
                    next_clear_time = None
                    if clear_interval_seconds is not None:
                        next_clear_time = self._clock() + clear_interval_seconds
                        if not self._clearing_thread_started:
                            self._clearing_thread_started = True
                            start_thread = True
                        else:
                            self._condition.notify()

                    owner_caches.caches[cache_name] = _Cache(
                        invalidation_groups=frozenset(invalidation_groups),
                        clear_on_demand=clear_on_demand,
                        clear_interval_seconds=clear_interval_seconds,
                        next_clear_time=next_clear_time,
                    )

        if unsupported_owner:
            msg = f"AXCacheManager: Owner-lifetime cache owner cannot be referenced: {cache_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if conflicting_lifetime:
            msg = f"AXCacheManager: Owner has conflicting lifetime policy: {cache_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if collision:
            msg = f"AXCacheManager: Cache already registered: {cache_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if start_thread:
            self._start_cache_cleanup_thread()
        return True

    def begin_scope(self) -> CacheScope:
        """Begins a bounded cache scope whose values are discarded on exit."""

        scope = CacheScope(self)
        with self._lock:
            self._scoped_values[scope] = {}
        return scope

    def end_scope(self, scope: CacheScope) -> None:
        """Ends an owned scope and discards all values stored in it."""

        failure = None
        with self._lock:
            if not isinstance(scope, CacheScope) or not scope.is_owned_by(self):
                failure = "AXCacheManager: Cache scope belongs to another manager."
            else:
                self._scoped_values.pop(scope, None)
        if failure:
            debug.print_message(debug.LEVEL_INFO, failure, True)

    def get_cache(self, owner: object, cache_name: str) -> CacheAccessor | None:
        """Returns a direct accessor for an owned cache."""

        with self._lock:
            cache, failure = self._get_owned_cache_locked(owner, cache_name)
            if cache is None:
                accessor = None
            else:
                accessor = CacheAccessor(self._accessor_backend, id(owner), cache_name, cache)
        if failure:
            debug.print_message(debug.LEVEL_INFO, failure, True)
        return accessor

    def invalidate_cache(
        self, owner: object, cache_name: str, reason: str = "", *, log: bool = True
    ) -> None:
        """Clears all values in a cache when called by its owner."""

        with self._lock:
            cache, failure = self._get_owned_cache_locked(owner, cache_name)
            if cache is not None:
                self._clear_cache_values_locked(id(owner), cache_name, cache)
        if failure:
            debug.print_message(debug.LEVEL_INFO, failure, True)
        elif cache is not None and log:
            self._log_invalidation([cache_name], reason)

    def invalidate_group(self, group: str, reason: str = "") -> None:
        """Clears all caches registered for an invalidation group."""

        cleared_cache_names: list[str] = []
        with self._lock:
            for owner_id, owner_caches in self._get_owner_cache_items_locked():
                for cache_name, cache in owner_caches.caches.items():
                    if group in cache.invalidation_groups:
                        self._clear_cache_values_locked(owner_id, cache_name, cache)
                        cleared_cache_names.append(cache_name)
        self._log_invalidation(cleared_cache_names, reason)

    def clear_cache_now(self, reason: str = "") -> None:
        """Clears caches participating in ordinary forced cache resets."""

        cleared_cache_names: list[str] = []
        with self._lock:
            for owner_id, owner_caches in self._get_owner_cache_items_locked():
                for cache_name, cache in owner_caches.caches.items():
                    if cache.clear_on_demand is ClearPolicy.CLEAR:
                        self._clear_cache_values_locked(owner_id, cache_name, cache)
                        cleared_cache_names.append(cache_name)
        self._log_invalidation(cleared_cache_names, reason)

    def _get_owned_cache_locked(
        self, owner: object, cache_name: str
    ) -> tuple[_Cache | None, str | None]:
        """Returns an owned cache and any access failure to log."""

        owner_caches = self._get_owner_caches_locked(owner)
        if owner_caches is None:
            return None, f"AXCacheManager: Cache is not registered: {cache_name}"

        cache = owner_caches.caches.get(cache_name)
        if cache is None:
            return None, f"AXCacheManager: Cache is not registered: {cache_name}"

        return cache, None

    def _get_owner_caches_locked(self, owner: object) -> _OwnerCaches | None:
        """Returns registrations associated with owner identity."""

        owner_caches = self._owner_caches.get(id(owner))
        if owner_caches is None or owner_caches.owner_ref.get() is not owner:
            return None
        return owner_caches

    def _get_owner_cache_items_locked(self) -> list[tuple[int, _OwnerCaches]]:
        """Returns a stable owner-cache snapshot despite weak-owner cleanup."""

        try:
            return list(self._owner_caches.items())
        except RuntimeError:
            return self._get_owner_cache_items_locked()

    def _get_scope_values_locked(
        self, scope: CacheScope
    ) -> tuple[dict[tuple[int, str], dict[Hashable, Any]] | None, str | None]:
        """Returns active scoped storage and any access failure to log."""

        if not isinstance(scope, CacheScope) or not scope.is_owned_by(self):
            return None, "AXCacheManager: Cache scope belongs to another manager."
        values = self._scoped_values.get(scope)
        if values is None:
            return None, "AXCacheManager: Cache scope is no longer active."
        return values, None

    def _get_accessor_value(self, cache: _Cache, key: Hashable, default: Any) -> Any:
        """Returns a value for a cache accessor."""

        with self._lock:
            if not cache.is_active:
                return default

            if key in cache.expiration_times and cache.expiration_times[key] <= self._clock():
                cache.values.pop(key, None)
                cache.expiration_times.pop(key, None)
                return default

            try:
                return cache.values[key]
            except KeyError:
                return default

    def _contains_accessor_value(self, cache: _Cache, key: Hashable) -> bool:
        """Returns True if a cache accessor has a value."""

        with self._lock:
            if not cache.is_active:
                return False

            if key in cache.expiration_times and cache.expiration_times[key] <= self._clock():
                cache.values.pop(key, None)
                cache.expiration_times.pop(key, None)
                return False

            return key in cache.values

    def _get_scoped_accessor_value(
        self,
        owner_id: int,
        cache_name: str,
        cache: _Cache,
        scope: CacheScope,
        key: Hashable,
        default: Any,
    ) -> Any:
        """Returns a scoped value for a cache accessor."""

        with self._lock:
            scoped_values, failure = self._get_scope_values_locked(scope)
            if scoped_values is None or failure or not cache.is_active:
                value = default
            else:
                values = scoped_values.get((owner_id, cache_name), {})
                try:
                    value = values[key]
                except KeyError:
                    value = default
        if failure:
            debug.print_message(debug.LEVEL_INFO, failure, True)
        return value

    def _contains_scoped_accessor_value(
        self,
        owner_id: int,
        cache_name: str,
        cache: _Cache,
        scope: CacheScope,
        key: Hashable,
    ) -> bool:
        """Returns True if a cache accessor has a scoped value."""

        with self._lock:
            scoped_values, failure = self._get_scope_values_locked(scope)
            if scoped_values is None or failure or not cache.is_active:
                rv = False
            else:
                values = scoped_values.get((owner_id, cache_name), {})
                rv = key in values
        if failure:
            debug.print_message(debug.LEVEL_INFO, failure, True)
        return rv

    def _put_accessor_value(
        self,
        cache: _Cache,
        key: Hashable,
        value: Any,
        expires_at: float | None,
    ) -> None:
        """Stores a value for a cache accessor."""

        start_thread = False
        with self._condition:
            if cache.is_active:
                had_expiration = key in cache.expiration_times
                if expires_at is not None and expires_at <= self._clock():
                    cache.values.pop(key, None)
                    cache.expiration_times.pop(key, None)
                else:
                    cache.values[key] = value
                    if expires_at is None:
                        cache.expiration_times.pop(key, None)
                    else:
                        cache.expiration_times[key] = expires_at
                        if not self._clearing_thread_started:
                            self._clearing_thread_started = True
                            start_thread = True

                if (
                    self._clearing_thread_started
                    and not start_thread
                    and (had_expiration or expires_at is not None)
                ):
                    self._condition.notify()
        if start_thread:
            self._start_cache_cleanup_thread()

    def _put_scoped_accessor_value(
        self,
        owner_id: int,
        cache_name: str,
        cache: _Cache,
        scope: CacheScope,
        key: Hashable,
        value: Any,
    ) -> None:
        """Stores a scoped value for a cache accessor."""

        with self._lock:
            scoped_values, failure = self._get_scope_values_locked(scope)
            if scoped_values is not None and not failure and cache.is_active:
                values = scoped_values.setdefault((owner_id, cache_name), {})
                values[key] = value
        if failure:
            debug.print_message(debug.LEVEL_INFO, failure, True)

    def _discard_accessor_value(self, cache: _Cache, key: Hashable) -> None:
        """Discards a value for a cache accessor."""

        with self._lock:
            if cache.is_active:
                cache.values.pop(key, None)
                cache.expiration_times.pop(key, None)

    def _discard_scoped_accessor_value(
        self,
        owner_id: int,
        cache_name: str,
        cache: _Cache,
        scope: CacheScope,
        key: Hashable,
    ) -> None:
        """Discards a scoped value for a cache accessor."""

        with self._lock:
            scoped_values, failure = self._get_scope_values_locked(scope)
            if scoped_values is not None and not failure and cache.is_active:
                values = scoped_values.get((owner_id, cache_name), {})
                values.pop(key, None)
        if failure:
            debug.print_message(debug.LEVEL_INFO, failure, True)

    def _invalidate_accessor_cache(
        self, owner_id: int, cache_name: str, cache: _Cache, reason: str, log: bool
    ) -> None:
        """Invalidates a cache for a cache accessor."""

        with self._lock:
            if cache.is_active:
                self._clear_cache_values_locked(owner_id, cache_name, cache)
                cleared = True
            else:
                cleared = False
        if cleared and log:
            self._log_invalidation([cache_name], reason)

    def _clear_cache_values_locked(self, owner_id: int, cache_name: str, cache: _Cache) -> None:
        """Clears persistent and scoped values for one cache."""

        cache.values.clear()
        cache.expiration_times.clear()
        for scoped_values in self._scoped_values.values():
            scoped_values.pop((owner_id, cache_name), None)

    def _make_owner_reference(
        self, owner_id: int, owner: object, lifetime: Lifetime
    ) -> _ProcessOwnerReference | _ReclaimableOwnerReference | None:
        """Creates owner storage for a declared lifetime policy."""

        if lifetime is Lifetime.PROCESS:
            return _ProcessOwnerReference(owner)

        try:
            return _ReclaimableOwnerReference(
                weakref.ref(
                    owner,
                    lambda reference: self._remove_collected_owner(owner_id, reference),
                )
            )
        except TypeError:
            return None

    def _remove_collected_owner(
        self, owner_id: int, reference: weakref.ReferenceType[object]
    ) -> None:
        """Drops all caches after a reclaimable owner is collected."""

        with self._condition:
            owner_caches = self._owner_caches.get(owner_id)
            if (
                owner_caches is None
                or not isinstance(owner_caches.owner_ref, _ReclaimableOwnerReference)
                or owner_caches.owner_ref.reference is not reference
            ):
                return
            self._owner_caches.pop(owner_id, None)
            for cache in owner_caches.caches.values():
                cache.is_active = False
            for scoped_values in self._scoped_values.values():
                for cache_name in owner_caches.caches:
                    scoped_values.pop((owner_id, cache_name), None)
            self._condition.notify()

    def _log_invalidation(self, cache_names: list[str], reason: str) -> None:
        """Logs why one or more caches were invalidated."""

        if not cache_names:
            return

        label = "cache" if len(cache_names) == 1 else "caches"
        tokens = [f"AXCacheManager: Invalidating {label}", ", ".join(cache_names)]
        if reason:
            tokens.append(f" Reason: {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def _start_cache_cleanup_thread(self) -> None:
        """Starts the single thread used for timed cache cleanup."""

        thread = threading.Thread(target=self._clear_stored_data)
        thread.daemon = True
        thread.start()

    def _clear_stored_data(self) -> None:
        """Periodically expires entries and clears caches."""

        while True:
            self._run_cache_cleanup_iteration_safely()

    def _run_cache_cleanup_iteration_safely(self) -> None:
        """Runs one cleanup pass without letting unexpected errors end the thread."""

        try:
            self._run_cache_cleanup_iteration()
        except Exception as error:  # pylint: disable=broad-exception-caught
            msg = f"AXCacheManager: Exception in cache cleanup thread: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            debug.print_exception(debug.LEVEL_WARNING)
            with self._condition:
                self._condition.wait(DEFAULT_CLEAR_INTERVAL_SECONDS)

    def _run_cache_cleanup_iteration(self) -> None:
        """Runs one timed cache cleanup pass and waits for the next deadline."""

        self._clear_due_values()
        with self._condition:
            seconds_until_next_cleanup = self._get_seconds_until_next_cleanup_locked()
            # Serialize schedule changes with waiting so earlier deadlines are not missed.
            self._condition.wait(seconds_until_next_cleanup)

    def _clear_due_values(self) -> None:
        """Removes expired entries and clears caches whose interval has elapsed."""

        now = self._clock()
        cleared_cache_names: list[str] = []
        with self._lock:
            for _owner_id, owner_caches in self._get_owner_cache_items_locked():
                for cache_name, cache in owner_caches.caches.items():
                    if (
                        cache.next_clear_time is not None
                        and cache.clear_interval_seconds is not None
                        and now >= cache.next_clear_time
                    ):
                        cache.values.clear()
                        cache.expiration_times.clear()
                        cleared_cache_names.append(cache_name)
                        cache.next_clear_time = now + cache.clear_interval_seconds
                        continue

                    expired_keys = [
                        key
                        for key, expiration_time in cache.expiration_times.items()
                        if now >= expiration_time
                    ]
                    for key in expired_keys:
                        cache.values.pop(key, None)
                        cache.expiration_times.pop(key, None)

        self._log_invalidation(cleared_cache_names, "Automatic interval-based clearing.")

    def _get_seconds_until_next_cleanup_locked(self) -> float | None:
        """Returns seconds until the earliest scheduled timed cleanup."""

        next_cleanup_times = [
            cache.next_clear_time
            for _owner_id, owner_caches in self._get_owner_cache_items_locked()
            for cache in owner_caches.caches.values()
            if cache.next_clear_time is not None
        ]
        next_cleanup_times.extend(
            expiration_time
            for _owner_id, owner_caches in self._get_owner_cache_items_locked()
            for cache in owner_caches.caches.values()
            for expiration_time in cache.expiration_times.values()
        )
        if not next_cleanup_times:
            return None

        return max(0.0, min(next_cleanup_times) - self._clock())


_manager: AXCacheManager = AXCacheManager()


def get_object_key(obj: object) -> Hashable:
    """Returns the cache key for an accessible object."""

    return hash(obj)


def get_manager() -> AXCacheManager:
    """Returns the accessibility cache manager singleton."""

    return _manager
