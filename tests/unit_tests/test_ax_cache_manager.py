# Unit tests for ax_cache_manager.py methods.
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

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods

"""Unit tests for ax_cache_manager.py methods."""

from __future__ import annotations

import gc
import weakref
from typing import TYPE_CHECKING

import pytest

from orca import ax_cache_manager, debug
from orca.ax_cache_manager import (
    DEFAULT_CLEAR_INTERVAL_SECONDS,
    MISSING,
    AXCacheManager,
    CacheAccessor,
    ClearPolicy,
    Lifetime,
    get_manager,
    get_object_key,
)

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


class FakeClock:
    """Provides a controllable clock for automatic clearing tests."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class Owner:
    """Provides a weak-referenceable cache owner for tests."""


class MutatingOwnerCaches(dict):
    """Simulates weak-owner cleanup mutating registrations during snapshot creation."""

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.fail_once = True

    def items(self):
        if self.fail_once:
            self.fail_once = False
            raise RuntimeError("dictionary changed size during iteration")
        return super().items()


@pytest.mark.unit
class TestAXCacheManager:
    """Test AXCacheManager methods."""

    @staticmethod
    def _register_cache(
        manager: AXCacheManager,
        owner: object,
        cache_name: str,
        *,
        lifetime: Lifetime = Lifetime.OWNER,
        clear_on_demand: ClearPolicy = ClearPolicy.CLEAR,
        clear_interval_seconds: float | None = None,
        invalidation_groups: set[str] | frozenset[str] = frozenset(),
    ) -> CacheAccessor:
        """Registers a cache and returns its accessor."""

        assert (
            manager.register_cache(
                owner,
                cache_name,
                lifetime=lifetime,
                clear_on_demand=clear_on_demand,
                clear_interval_seconds=clear_interval_seconds,
                invalidation_groups=invalidation_groups,
            )
            is True
        )
        cache = manager.get_cache(owner, cache_name)
        assert cache is not None
        return cache

    def test_register_cache_detects_collision(self, test_context: OrcaTestContext) -> None:
        """Test that registering an existing cache reports a collision."""

        manager = AXCacheManager()
        print_message = test_context.patch_object(debug, "print_message")
        owner = Owner()

        assert (
            manager.register_cache(
                owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=None
            )
            is True
        )
        assert (
            manager.register_cache(
                owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=None
            )
            is False
        )
        assert "Cache already registered: objects" in print_message.call_args[0][1]

    def test_same_cache_can_be_registered_by_different_owners(self) -> None:
        """Test an instance-scoped cache name can be used by multiple owners."""

        manager = AXCacheManager()
        first_owner = Owner()
        second_owner = Owner()

        first_cache = self._register_cache(manager, first_owner, "objects")
        second_cache = self._register_cache(manager, second_owner, "objects")
        first_cache.put("key", "first")
        second_cache.put("key", "second")

        assert first_cache.get("key") == "first"
        assert second_cache.get("key") == "second"

    @pytest.mark.parametrize(
        "cache_name,interval",
        [
            pytest.param("", None, id="empty_cache"),
            pytest.param("objects", 0, id="zero_interval"),
            pytest.param("objects", -1, id="negative_interval"),
        ],
    )
    def test_register_cache_invalid_parameters_do_not_raise(
        self, test_context: OrcaTestContext, cache_name: str, interval: float | None
    ) -> None:
        """Test invalid registration is logged and rejected."""

        manager = AXCacheManager()
        print_message = test_context.patch_object(debug, "print_message")

        assert (
            manager.register_cache(
                Owner(), cache_name, lifetime=Lifetime.OWNER, clear_interval_seconds=interval
            )
            is False
        )
        print_message.assert_called_once()

    def test_register_cache_rejects_non_weak_instance_owner(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test an instance owner cannot be retained just to retain its cache."""

        manager = AXCacheManager()
        print_message = test_context.patch_object(debug, "print_message")

        assert manager.register_cache(object(), "objects", lifetime=Lifetime.OWNER) is False
        assert "Owner-lifetime cache owner cannot be referenced" in print_message.call_args[0][1]

    def test_register_cache_rejects_invalid_lifetime(self, test_context: OrcaTestContext) -> None:
        """Test registration with an unknown lifetime is logged and rejected."""

        manager = AXCacheManager()
        print_message = test_context.patch_object(debug, "print_message")

        assert manager.register_cache(Owner(), "objects", lifetime=None) is False
        assert "Invalid cache lifetime" in print_message.call_args[0][1]

    def test_register_cache_rejects_invalid_on_demand_policy(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test registration with an unknown on-demand policy is rejected."""

        manager = AXCacheManager()
        print_message = test_context.patch_object(debug, "print_message")

        assert (
            manager.register_cache(
                Owner(),
                "objects",
                lifetime=Lifetime.OWNER,
                clear_on_demand=None,
            )
            is False
        )
        assert "Invalid on-demand clearing policy" in print_message.call_args[0][1]

    def test_process_lifetime_cache_retains_its_owner(self) -> None:
        """Test process lifetime is an explicit policy rather than inferred from owner type."""

        manager = AXCacheManager()
        owner = object()

        cache = self._register_cache(manager, owner, "objects", lifetime=Lifetime.PROCESS)
        cache.put("key", "value")
        assert cache.get("key") == "value"

    def test_owner_cannot_mix_cache_lifetime_policies(self, test_context: OrcaTestContext) -> None:
        """Test one owner cannot declare contradictory cache lifetimes."""

        manager = AXCacheManager()
        owner = Owner()
        print_message = test_context.patch_object(debug, "print_message")

        assert (
            manager.register_cache(
                owner, "first", lifetime=Lifetime.OWNER, clear_interval_seconds=None
            )
            is True
        )
        assert (
            manager.register_cache(
                owner, "second", lifetime=Lifetime.PROCESS, clear_interval_seconds=None
            )
            is False
        )
        assert "conflicting lifetime policy" in print_message.call_args[0][1]

    def test_collected_instance_owner_removes_its_caches(self) -> None:
        """Test reclaiming an instance owner also reclaims its cached values."""

        manager = AXCacheManager()
        owner = Owner()
        owner_reference = weakref.ref(owner)
        assert (
            manager.register_cache(
                owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=None
            )
            is True
        )
        cache = manager.get_cache(owner, "objects")
        assert cache is not None
        cache.put("key", "value")

        del owner
        gc.collect()

        assert owner_reference() is None
        assert manager._owner_caches == {}

    def test_collected_timed_owner_wakes_clearing_worker(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test removing scheduled instance data causes the worker to recalculate."""

        manager = AXCacheManager()
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        notify = test_context.patch_object(manager._condition, "notify")
        manager.register_cache(owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=60)
        notify.reset_mock()

        del owner
        gc.collect()

        notify.assert_called_once_with()

    def test_invalidation_can_reclaim_owner_stored_in_another_cache(self) -> None:
        """Test weak-owner cleanup can run while cached values are being cleared."""

        manager = AXCacheManager()
        first_owner = Owner()
        cached_owner = Owner()
        cached_owner_reference = weakref.ref(cached_owner)
        first_cache = self._register_cache(
            manager, first_owner, "first", invalidation_groups={"structure"}
        )
        self._register_cache(manager, cached_owner, "second")
        first_cache.put("key", cached_owner)

        del cached_owner
        manager.invalidate_group("structure")

        assert cached_owner_reference() is None
        assert len(manager._owner_caches) == 1

    def test_owner_cache_snapshot_retries_after_reentrant_cleanup(self) -> None:
        """Test owner-cache scans tolerate weak-owner cleanup during snapshot creation."""

        manager = AXCacheManager()
        owner = Owner()
        manager.register_cache(
            owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=None
        )
        manager._owner_caches = MutatingOwnerCaches(manager._owner_caches)  # type: ignore[assignment]

        with manager._lock:
            items = manager._get_owner_cache_items_locked()

        assert len(items) == 1
        assert manager._owner_caches.fail_once is False

    def test_cache_accessor_handles_values_and_invalidation(self) -> None:
        """Test direct cache access preserves ordinary cache semantics."""

        manager = AXCacheManager()
        owner = Owner()
        manager.register_cache(
            owner, "values", lifetime=Lifetime.OWNER, clear_interval_seconds=None
        )
        cache = manager.get_cache(owner, "values")
        assert cache is not None

        cache.put("false", False)
        cache.put("none", None)
        assert cache.get("false") is False
        assert cache.get("none") is None
        assert cache.get("missing") is MISSING

        cache.discard("false")
        assert cache.get("false") is MISSING
        cache.invalidate(log=False)
        assert cache.get("none") is MISSING

    def test_cache_accessor_observes_expiration(self, test_context: OrcaTestContext) -> None:
        """Test direct cache access treats expired entries as misses."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        manager.register_cache(
            owner, "values", lifetime=Lifetime.OWNER, clear_interval_seconds=None
        )
        cache = manager.get_cache(owner, "values")
        assert cache is not None

        cache.put("key", "value", expires_at=1)
        assert cache.get("key") == "value"
        clock.now = 1
        assert cache.get("key") is MISSING

    def test_cache_accessor_handles_scoped_values(self) -> None:
        """Test direct cache access supports bounded operation values."""

        manager = AXCacheManager()
        owner = Owner()
        manager.register_cache(
            owner, "values", lifetime=Lifetime.OWNER, clear_interval_seconds=None
        )
        cache = manager.get_cache(owner, "values")
        assert cache is not None

        with manager.begin_scope() as scope:
            assert cache.get_scoped(scope, "key") is MISSING
            cache.put_scoped(scope, "key", "value")
            assert cache.get_scoped(scope, "key") == "value"
            cache.discard_scoped(scope, "key")
            assert cache.get_scoped(scope, "key") is MISSING

    def test_cache_accessor_does_not_keep_owner_alive(self) -> None:
        """Test stale owner-lifetime accessors stop using reclaimed caches."""

        manager = AXCacheManager()
        owner = Owner()
        owner_reference = weakref.ref(owner)
        manager.register_cache(
            owner, "values", lifetime=Lifetime.OWNER, clear_interval_seconds=None
        )
        cache = manager.get_cache(owner, "values")
        assert cache is not None
        cache.put("key", "value")

        del owner
        gc.collect()

        assert owner_reference() is None
        assert manager._owner_caches == {}
        assert cache.get("key") is MISSING
        cache.put("replacement", "value")
        assert cache.get("replacement") is MISSING

    def test_get_cache_rejects_non_owner(self, test_context: OrcaTestContext) -> None:
        """Test one owner cannot obtain another owner's cache accessor."""

        manager = AXCacheManager()
        owner = Owner()
        other = Owner()
        print_message = test_context.patch_object(debug, "print_message")
        manager.register_cache(
            owner, "values", lifetime=Lifetime.OWNER, clear_interval_seconds=None
        )

        assert manager.get_cache(other, "values") is None
        print_message.assert_called_once()

    def test_scope_keeps_values_separate_and_discards_them_on_exit(self) -> None:
        """Test scoped values are isolated from ordinary storage and bounded by context."""

        manager = AXCacheManager()
        owner = Owner()
        cache = self._register_cache(manager, owner, "values")
        cache.put("key", "ordinary")

        with manager.begin_scope() as scope:
            assert cache.get_scoped(scope, "key") is MISSING
            cache.put_scoped(scope, "key", "scoped")
            assert cache.get_scoped(scope, "key") == "scoped"
            assert cache.get("key") == "ordinary"
            cache.discard_scoped(scope, "key")
            assert cache.get_scoped(scope, "key") is MISSING

        assert scope not in manager._scoped_values
        assert cache.get("key") == "ordinary"

    def test_nested_scopes_keep_values_separate(self) -> None:
        """Test nested bounded operations cannot reuse one another's values."""

        manager = AXCacheManager()
        owner = Owner()
        cache = self._register_cache(manager, owner, "values")

        with manager.begin_scope() as outer_scope:
            cache.put_scoped(outer_scope, "key", "outer")
            with manager.begin_scope() as inner_scope:
                assert cache.get_scoped(inner_scope, "key") is MISSING
                cache.put_scoped(inner_scope, "key", "inner")
                assert cache.get_scoped(inner_scope, "key") == "inner"
            assert cache.get_scoped(outer_scope, "key") == "outer"

    def test_scoped_operations_do_not_raise_for_invalid_scope(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test inactive and foreign scopes are logged and ignored."""

        manager = AXCacheManager()
        other_manager = AXCacheManager()
        owner = Owner()
        cache = self._register_cache(manager, owner, "values")
        print_message = test_context.patch_object(debug, "print_message")

        with other_manager.begin_scope() as foreign_scope:
            assert cache.get_scoped(foreign_scope, "key") is MISSING
            cache.put_scoped(foreign_scope, "key", "value")
            cache.discard_scoped(foreign_scope, "key")

        with manager.begin_scope() as ended_scope:
            pass
        assert cache.get_scoped(ended_scope, "key") is MISSING
        assert cache.get_scoped(None, "key") is MISSING  # type: ignore[arg-type]
        manager.end_scope(None)  # type: ignore[arg-type]

        assert print_message.call_count == 6

    def test_put_rejects_invalid_expiration_time(self, test_context: OrcaTestContext) -> None:
        """Test invalid expiration input is logged and not stored."""

        manager = AXCacheManager()
        owner = Owner()
        print_message = test_context.patch_object(debug, "print_message")
        cache = self._register_cache(manager, owner, "values")

        cache.put("key", "value", expires_at=float("nan"))

        assert cache.get("key") is MISSING
        assert "Invalid expiration time" in print_message.call_args[0][1]

    def test_put_expiring_values_starts_worker_and_notifies_for_earlier_deadline(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test expiration-only caches schedule and update timed cleanup."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        start_worker = test_context.patch_object(manager, "_start_cache_cleanup_thread")
        notify = test_context.patch_object(manager._condition, "notify")
        cache = self._register_cache(manager, owner, "values")

        cache.put("later", "value", expires_at=20)
        start_worker.assert_called_once_with()
        notify.assert_not_called()

        cache.put("earlier", "value", expires_at=10)
        notify.assert_called_once_with()
        with manager._condition:
            assert manager._get_seconds_until_next_cleanup_locked() == 10

    def test_non_owner_operations_do_not_access_cache(self, test_context: OrcaTestContext) -> None:
        """Test that one owner cannot access another owner's values."""

        manager = AXCacheManager()
        owner = Owner()
        other = Owner()
        cache = self._register_cache(manager, owner, "objects")
        cache.put("key", "value")
        test_context.patch_object(debug, "print_message")

        manager.invalidate_cache(other, "objects")

        assert cache.get("key") == "value"

    def test_unregistered_cache_invalidation_does_not_raise(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test unknown cache invalidation is logged and ignored."""

        manager = AXCacheManager()
        owner = Owner()
        test_context.patch_object(debug, "print_message")

        manager.invalidate_cache(owner, "objects")

        cache = self._register_cache(manager, owner, "objects")
        assert cache.get("key") is MISSING

    def test_discard_and_invalidate_cache_remove_owned_values(self) -> None:
        """Test individual and full invalidation by a cache owner."""

        manager = AXCacheManager()
        owner = Owner()
        cache = self._register_cache(manager, owner, "objects")
        cache.put(1, "first")
        cache.put(2, "second")

        cache.discard(1)
        assert cache.get(1) is MISSING
        assert cache.get(2) == "second"

        manager.invalidate_cache(owner, "objects", "Reset values.")
        assert cache.get(2) is MISSING

    def test_invalidate_cache_can_skip_success_logging(self, test_context: OrcaTestContext) -> None:
        """Test callers can silence routine cache invalidation."""

        manager = AXCacheManager()
        owner = Owner()
        print_tokens = test_context.patch_object(debug, "print_tokens")
        cache = self._register_cache(manager, owner, "objects")
        cache.put("key", "value")

        manager.invalidate_cache(owner, "objects", log=False)

        assert cache.get("key") is MISSING
        print_tokens.assert_not_called()

    def test_invalidate_group_clears_only_registered_members(self) -> None:
        """Test manager-controlled invalidation across owners."""

        manager = AXCacheManager()
        first_owner = Owner()
        second_owner = Owner()
        first_cache = self._register_cache(
            manager,
            first_owner,
            "first",
            invalidation_groups={"structure"},
        )
        second_cache = self._register_cache(
            manager,
            second_owner,
            "second",
            invalidation_groups={"content"},
        )
        first_cache.put("key", "one")
        second_cache.put("key", "two")

        manager.invalidate_group("structure", "Children changed.")

        assert first_cache.get("key") is MISSING
        assert second_cache.get("key") == "two"

    def test_invalidation_clears_scoped_values(self) -> None:
        """Test explicit cache invalidation removes active scoped values."""

        manager = AXCacheManager()
        owner = Owner()
        cache = self._register_cache(manager, owner, "values")

        with manager.begin_scope() as scope:
            cache.put_scoped(scope, "key", "value")
            manager.invalidate_cache(owner, "values", "Changed.")
            assert cache.get_scoped(scope, "key") is MISSING

    def test_clear_cache_now_preserves_caches_with_preserve_policy(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test ordinary forced clearing observes cache policy."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        memo_cache = self._register_cache(
            manager,
            owner,
            "memo",
        )
        preserved_cache = self._register_cache(
            manager,
            owner,
            "preserved",
            clear_on_demand=ClearPolicy.PRESERVE,
        )
        memo_cache.put("key", "value")
        preserved_cache.put("key", "value", expires_at=1)

        manager.clear_cache_now("Forced refresh.")

        assert memo_cache.get("key") is MISSING
        assert preserved_cache.get("key") == "value"

    def test_clear_cache_now_observes_active_scoped_cache_policy(self) -> None:
        """Test forced clearing observes active scoped caches' policy."""

        manager = AXCacheManager()
        owner = Owner()
        memo_cache = self._register_cache(manager, owner, "memo")
        preserved_cache = self._register_cache(
            manager,
            owner,
            "preserved",
            clear_on_demand=ClearPolicy.PRESERVE,
        )

        with manager.begin_scope() as scope:
            memo_cache.put_scoped(scope, "key", "value")
            preserved_cache.put_scoped(scope, "key", "value")
            manager.clear_cache_now("Forced refresh.")
            assert memo_cache.get_scoped(scope, "key") is MISSING
            assert preserved_cache.get_scoped(scope, "key") == "value"

    def test_register_timed_caches_starts_one_worker(self, test_context: OrcaTestContext) -> None:
        """Test one automatic-clearing worker handles all timed caches."""

        manager = AXCacheManager()
        mock_thread = test_context.Mock()
        notify = test_context.patch_object(manager._condition, "notify")
        first_owner = Owner()
        second_owner = Owner()
        thread_constructor = test_context.patch_object(
            ax_cache_manager.threading,
            "Thread",
            return_value=mock_thread,
        )

        assert manager.register_cache(first_owner, "first", lifetime=Lifetime.OWNER) is True
        assert (
            manager.register_cache(
                second_owner, "second", lifetime=Lifetime.OWNER, clear_interval_seconds=120
            )
            is True
        )

        thread_constructor.assert_called_once_with(target=manager._clear_stored_data)
        assert mock_thread.daemon is True
        mock_thread.start.assert_called_once_with()
        notify.assert_called_once_with()

    def test_cleanup_thread_continues_after_unexpected_exception(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test an unexpected cleanup failure does not end the cleanup thread."""

        manager = AXCacheManager()
        run_iteration = test_context.patch_object(
            manager,
            "_run_cache_cleanup_iteration",
            side_effect=[RuntimeError("boom"), SystemExit],
        )
        print_message = test_context.patch_object(debug, "print_message")
        print_exception = test_context.patch_object(debug, "print_exception")
        wait = test_context.patch_object(manager._condition, "wait")

        with pytest.raises(SystemExit):
            manager._clear_stored_data()

        assert run_iteration.call_count == 2
        print_message.assert_called_once_with(
            debug.LEVEL_WARNING,
            "AXCacheManager: Exception in cache cleanup thread: boom",
            True,
        )
        print_exception.assert_called_once_with(debug.LEVEL_WARNING)
        wait.assert_called_once_with(DEFAULT_CLEAR_INTERVAL_SECONDS)

    def test_due_cache_clearing_uses_default_interval(self, test_context: OrcaTestContext) -> None:
        """Test the default interval clears a cache at its scheduled boundary."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        manager.register_cache(owner, "objects", lifetime=Lifetime.OWNER)
        cache = manager.get_cache(owner, "objects")
        assert cache is not None
        cache.put("early", "value")

        clock.now = DEFAULT_CLEAR_INTERVAL_SECONDS - 1
        cache.put("late", "value")
        with manager._condition:
            assert manager._get_seconds_until_next_cleanup_locked() == 1
        manager._clear_due_values()
        assert cache.get("early") == "value"
        assert cache.get("late") == "value"

        clock.now = DEFAULT_CLEAR_INTERVAL_SECONDS
        manager._clear_due_values()
        assert cache.get("early") is MISSING
        assert cache.get("late") is MISSING
        with manager._condition:
            assert (
                manager._get_seconds_until_next_cleanup_locked() == DEFAULT_CLEAR_INTERVAL_SECONDS
            )

    def test_interval_clearing_does_not_end_active_scope(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test bounded operation values remain valid until that operation exits."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        manager.register_cache(owner, "values", lifetime=Lifetime.OWNER, clear_interval_seconds=2)
        cache = manager.get_cache(owner, "values")
        assert cache is not None

        with manager.begin_scope() as scope:
            cache.put("key", "ordinary")
            cache.put_scoped(scope, "key", "scoped")
            clock.now = 2
            manager._clear_due_values()
            assert cache.get("key") is MISSING
            assert cache.get_scoped(scope, "key") == "scoped"

    def test_bulk_clearing_logs_caches_once(self, test_context: OrcaTestContext) -> None:
        """Test one diagnostic reports caches cleared in the same scheduled pass."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        print_tokens = test_context.patch_object(debug, "print_tokens")
        manager.register_cache(owner, "first", lifetime=Lifetime.OWNER, clear_interval_seconds=2)
        manager.register_cache(owner, "second", lifetime=Lifetime.OWNER, clear_interval_seconds=2)

        clock.now = 2
        manager._clear_due_values()

        print_tokens.assert_called_once_with(
            debug.LEVEL_INFO,
            [
                "AXCacheManager: Invalidating caches",
                "first, second",
                " Reason: Automatic interval-based clearing.",
            ],
            True,
        )

    def test_entry_deadlines_and_cache_clearing_share_cleanup_worker(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test entry expiration is scheduled before later cache clearing."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        manager.register_cache(owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=60)
        cache = manager.get_cache(owner, "objects")
        assert cache is not None
        cache.put("short-lived", "value", expires_at=10)
        cache.put("persistent", "value")

        with manager._condition:
            assert manager._get_seconds_until_next_cleanup_locked() == 10
        clock.now = 10
        manager._clear_due_values()
        assert cache.get("short-lived") is MISSING
        assert cache.get("persistent") == "value"
        with manager._condition:
            assert manager._get_seconds_until_next_cleanup_locked() == 50

    def test_entries_can_share_original_expiration_deadline(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test later insertion can inherit an existing entry deadline."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")
        manager.register_cache(owner, "hung", lifetime=Lifetime.OWNER, clear_interval_seconds=None)
        cache = manager.get_cache(owner, "hung")
        assert cache is not None
        cache.put("object", 0.0, expires_at=1)

        clock.now = 0.8
        cache.put("application", 0.0, expires_at=1)
        assert cache.get("application") == 0.0

        clock.now = 1
        manager._clear_due_values()
        assert cache.get("object") is MISSING
        assert cache.get("application") is MISSING

    def test_debug_output_is_not_emitted_while_manager_is_locked(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test diagnostics do not execute while cache state is locked."""

        clock = FakeClock()
        manager = AXCacheManager(clock)
        owner = Owner()
        test_context.patch_object(manager, "_start_cache_cleanup_thread")

        def assert_unlocked(*_args: object) -> None:
            assert not manager._lock.locked()

        test_context.patch_object(debug, "print_message", side_effect=assert_unlocked)
        test_context.patch_object(debug, "print_tokens", side_effect=assert_unlocked)

        manager.register_cache(owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=60)
        assert (
            manager.register_cache(
                owner, "objects", lifetime=Lifetime.OWNER, clear_interval_seconds=None
            )
            is False
        )
        assert manager.get_cache(Owner(), "objects") is None
        manager.invalidate_cache(owner, "objects")
        clock.now = 60
        manager._clear_due_values()

    def test_get_manager_returns_singleton(self) -> None:
        """Test the process-wide manager accessor."""

        assert get_manager() is get_manager()

    def test_get_object_key_preserves_current_hash_behavior(self) -> None:
        """Test object cache keys currently match hash values."""

        obj = Owner()
        assert get_object_key(obj) == hash(obj)
