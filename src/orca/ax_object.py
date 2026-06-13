# Orca
#
# Copyright 2023 Igalia, S.L.
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

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods

"""Wrapper for the Atspi.Accessible interface."""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import ax_cache_manager, debug

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Hashable


class _AXObjectCache:
    """Provides AXObject-specific access to manager-backed cached values."""

    KNOWN_DEAD = "AXObject.known-dead"
    OBJECT_ATTRIBUTES = "AXObject.object-attributes"
    SUPPORTED_INTERFACES = "AXObject.supported-interfaces"
    HUNG_OBJECTS = "AXObject.hung-objects"
    _HUNG_TIMEOUT_SECONDS = 1.0

    def __init__(self) -> None:
        self._manager = ax_cache_manager.get_manager()
        for namespace in (
            self.KNOWN_DEAD,
            self.OBJECT_ATTRIBUTES,
            self.SUPPORTED_INTERFACES,
        ):
            self._manager.register_cache(
                self,
                namespace,
                lifetime=ax_cache_manager.Lifetime.PROCESS,
                clear_on_demand=ax_cache_manager.ClearPolicy.CLEAR,
            )
        self._known_dead = self._manager.get_cache(self, self.KNOWN_DEAD)
        self._object_attributes = self._manager.get_cache(self, self.OBJECT_ATTRIBUTES)
        self._supported_interfaces = self._manager.get_cache(self, self.SUPPORTED_INTERFACES)
        self._manager.register_cache(
            self,
            self.HUNG_OBJECTS,
            lifetime=ax_cache_manager.Lifetime.PROCESS,
            clear_on_demand=ax_cache_manager.ClearPolicy.PRESERVE,
            clear_interval_seconds=None,
        )
        self._hung_objects = self._manager.get_cache(self, self.HUNG_OBJECTS)

    def get_dead_status(self, obj: Atspi.Accessible) -> bool | None:
        """Returns the recorded result of a prior deadness probe."""

        return self.get_dead_status_for_key(ax_cache_manager.get_object_key(obj))

    def get_dead_status_for_key(self, key: Hashable) -> bool | None:
        """Returns the recorded result of a prior deadness probe."""

        if self._known_dead is None:
            return None
        return self._known_dead.get(key, None)

    def set_dead_status(self, obj: Atspi.Accessible, is_dead: bool) -> None:
        """Stores the result of a deadness probe."""

        if self._known_dead is not None:
            self._known_dead.put(ax_cache_manager.get_object_key(obj), is_dead)

    def get_attributes(self, obj: Atspi.Accessible) -> Any:
        """Returns the cached object attributes for obj."""

        if self._object_attributes is None:
            return ax_cache_manager.MISSING
        return self._object_attributes.get(ax_cache_manager.get_object_key(obj))

    def set_attributes(self, obj: Atspi.Accessible, attributes: dict[str, str]) -> None:
        """Stores object attributes."""

        if self._object_attributes is not None:
            self._object_attributes.put(ax_cache_manager.get_object_key(obj), attributes)

    def get_interface_support(self, obj: Atspi.Accessible, name: str) -> bool | None:
        """Returns cached interface support, or None when absent."""

        if self._supported_interfaces is None:
            return None
        return self._supported_interfaces.get((ax_cache_manager.get_object_key(obj), name), None)

    def set_interface_support(self, obj: Atspi.Accessible, name: str, supported: bool) -> None:
        """Stores interface support."""

        if self._supported_interfaces is not None:
            self._supported_interfaces.put((ax_cache_manager.get_object_key(obj), name), supported)

    def get_hung_timestamp(self, obj: Atspi.Accessible | None) -> float | None:
        """Returns an unexpired hung marker timestamp, or None."""

        if obj is None:
            return None

        return self.get_hung_timestamp_for_key(ax_cache_manager.get_object_key(obj))

    def get_hung_timestamp_for_key(self, key: Hashable) -> float | None:
        """Returns an unexpired hung marker timestamp, or None."""

        if self._hung_objects is None:
            return None
        return self._hung_objects.get(key, None)

    def mark_hung(self, obj: Atspi.Accessible, timestamp: float | None = None) -> None:
        """Marks an object hung until one second after the supplied timestamp."""

        if timestamp is None:
            timestamp = time.monotonic()
        if self._hung_objects is not None:
            self._hung_objects.put(
                ax_cache_manager.get_object_key(obj),
                timestamp,
                expires_at=timestamp + self._HUNG_TIMEOUT_SECONDS,
            )


class AXObject:
    """Wrapper for the Atspi.Accessible interface."""

    _CACHE = _AXObjectCache()

    @staticmethod
    def get_toolkit_name(obj: Atspi.Accessible) -> str:
        """Returns the toolkit name of obj as a lowercase string"""

        try:
            app = Atspi.Accessible.get_application(obj)
            name = Atspi.Accessible.get_toolkit_name(app) or ""
        except GLib.GError as error:
            tokens = ["AXObject: Exception calling _get_toolkit_name_on", app, f": {error}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        return name.lower()

    @staticmethod
    def is_bogus(obj: Atspi.Accessible) -> bool:
        """Hack to ignore certain objects. All entries must have a bug."""

        # TODO - JD: Periodically check for fixes and remove hacks which are no
        # longer needed.

        # https://bugzilla.mozilla.org/show_bug.cgi?id=1879750
        if (
            AXObject.get_role(obj) == Atspi.Role.SECTION
            and AXObject.get_role(AXObject.get_parent(obj)) == Atspi.Role.FRAME
            and AXObject.get_toolkit_name(obj) == "gecko"
        ):
            tokens = ["AXObject:", obj, "is bogus. See mozilla bug 1879750."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            return True

        return False

    @staticmethod
    def _can_reach_application(obj: Atspi.Accessible) -> bool:
        """Returns True if we can ascend the ancestry of obj all the way to the application."""

        reached_app = False
        parent = AXObject.get_parent(obj)
        while parent and not reached_app:
            reached_app = AXObject.get_role(parent) == Atspi.Role.APPLICATION
            parent = AXObject.get_parent(parent)

        return reached_app

    @staticmethod
    def has_broken_ancestry(obj: Atspi.Accessible) -> bool:
        """Returns True if obj's ancestry is broken."""

        if obj is None:
            return False

        # https://bugreports.qt.io/browse/QTBUG-130116
        toolkit_name = AXObject.get_toolkit_name(obj)
        if not toolkit_name.startswith("qt"):
            return False

        if not AXObject._can_reach_application(obj):
            tokens = ["AXObject:", obj, "has broken ancestry. See qt bug 130116."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def has_broken_popup_ancestry(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a popup item whose ancestry is broken."""

        if obj is None or AXObject.is_dead(obj):
            return False

        # TODO - JD: File a bug. The scenario is that when the omnibox popup is closed and then
        # re-opened, we cannot ascend all the way to the frame. In addition, parents along the
        # way claim to have 0 children.
        if not AXObject.get_toolkit_name(obj).startswith("chromium"):
            return False

        if AXObject.get_role(obj) != Atspi.Role.LIST_ITEM:
            return False

        if not AXObject._can_reach_application(obj):
            tokens = ["AXObject:", obj, "has broken ancestry."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_valid(obj: Atspi.Accessible, app: Atspi.Accessible | None = None) -> bool:
        """Returns False if we know for certain this object is invalid"""

        if obj is None:
            return False

        obj_key = ax_cache_manager.get_object_key(obj)
        if AXObject._CACHE.get_dead_status_for_key(obj_key):
            return False

        if app is None:
            return AXObject._CACHE.get_hung_timestamp_for_key(obj_key) is None

        return not AXObject.check_hung(obj, app)

    @staticmethod
    def object_is_known_dead(obj: Atspi.Accessible) -> bool:
        """Returns True if we know for certain this object no longer exists"""

        if not obj:
            return False

        return AXObject._CACHE.get_dead_status(obj) is True

    @staticmethod
    def check_hung(
        obj: Atspi.Accessible | None,
        app: Atspi.Accessible | None = None,
    ) -> bool:
        """Returns True if obj or its app is hung, propagating obj-hung to app."""

        obj_hung_ts = AXObject._CACHE.get_hung_timestamp(obj)
        app_hung_ts = AXObject._CACHE.get_hung_timestamp(app)
        if obj_hung_ts is not None and app is not None and app_hung_ts is None:
            tokens = ["AXObject: Marking", app, "as hung due to hung source"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            AXObject._CACHE.mark_hung(app, obj_hung_ts)
            app_hung_ts = AXObject._CACHE.get_hung_timestamp(app)
        return obj_hung_ts is not None or app_hung_ts is not None

    @staticmethod
    def _set_known_dead_status(obj: Atspi.Accessible, is_dead: bool) -> None:
        """Updates the known-dead status of obj"""

        if obj is None:
            return

        current_status = AXObject._CACHE.get_dead_status(obj)
        if current_status == is_dead:
            return

        AXObject._CACHE.set_dead_status(obj, is_dead)
        if is_dead:
            msg = "AXObject: Adding to known dead objects"
            debug.print_message(debug.LEVEL_INFO, msg, True, True)
            return

        if current_status:
            tokens = ["AXObject: Removing", obj, "from known-dead objects"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    @staticmethod
    def handle_error(obj: Atspi.Accessible, error: Exception, msg: str) -> None:
        """Parses the exception and potentially updates our status for obj"""

        if AXObject.object_is_known_dead(obj):
            return

        error_string = str(error)
        if "Object does not exist at path" in error_string:
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif "The application no longer exists" in error_string:
            msg = msg.replace(error_string, "app no longer exists")
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif "The process appears to be hung" in error_string:
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXObject._CACHE.mark_hung(obj)
            return
        elif re.search(r"accessible/\d+ does not exist", error_string):
            msg = msg.replace(error_string, "object no longer exists")
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if AXObject._CACHE.get_dead_status(obj) is False:
            AXObject._set_known_dead_status(obj, True)

    @staticmethod
    def _supports_interface(obj: Atspi.Accessible, getter: Callable[..., object]) -> bool:
        """Returns True if obj supports the interface returned by getter, caching the result."""

        if not AXObject.is_valid(obj):
            return False

        name = getter.__name__
        cached = AXObject._CACHE.get_interface_support(obj, name)
        if cached is not None:
            return cached

        try:
            iface = getter(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling {name} on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        result = iface is not None
        AXObject._CACHE.set_interface_support(obj, name, result)
        return result

    @staticmethod
    def supports_action(obj: Atspi.Accessible) -> bool:
        """Returns True if the action interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_action_iface)

    @staticmethod
    def _find_ancestor_with_role(
        obj: Atspi.Accessible,
        role: Atspi.Role,
    ) -> Atspi.Accessible | None:
        """Returns obj or the nearest ancestor with the specified role."""

        current = obj
        while current:
            if AXObject.get_role(current) == role:
                return current
            current = AXObject.get_parent(current)
        return None

    @staticmethod
    def _has_document_spreadsheet(obj: Atspi.Accessible) -> bool:
        # To avoid circular import. pylint: disable=import-outside-toplevel
        from .ax_collection import AXCollection

        rule = AXCollection.create_match_rule(roles=[Atspi.Role.DOCUMENT_SPREADSHEET])
        if rule is None:
            return False

        frame = AXObject._find_ancestor_with_role(obj, Atspi.Role.FRAME)
        if frame is None:
            return False
        return bool(
            Atspi.Collection.get_matches(frame, rule, Atspi.CollectionSortOrder.CANONICAL, 1, True),
        )

    @staticmethod
    def supports_collection(obj: Atspi.Accessible) -> bool:
        """Returns True if the collection interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            app = Atspi.Accessible.get_application(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in supports_collection: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        try:
            iface = Atspi.Accessible.get_collection_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_collection_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        app_name = AXObject.get_name(app)
        if app_name != "soffice":
            result = iface is not None
        elif AXObject._find_ancestor_with_role(obj, Atspi.Role.DOCUMENT_TEXT):
            result = True
        elif AXObject._has_document_spreadsheet(obj):
            msg = "AXObject: Treating soffice as not supporting collection due to spreadsheet."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            result = False
        else:
            result = True
        return result

    @staticmethod
    def supports_component(obj: Atspi.Accessible) -> bool:
        """Returns True if the component interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_component_iface)

    @staticmethod
    def supports_document(obj: Atspi.Accessible) -> bool:
        """Returns True if the document interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_document_iface)

    @staticmethod
    def supports_editable_text(obj: Atspi.Accessible) -> bool:
        """Returns True if the editable-text interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_editable_text_iface)

    @staticmethod
    def supports_hyperlink(obj: Atspi.Accessible) -> bool:
        """Returns True if the hyperlink interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_hyperlink)

    @staticmethod
    def supports_hypertext(obj: Atspi.Accessible) -> bool:
        """Returns True if the hypertext interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_hypertext_iface)

    @staticmethod
    def supports_image(obj: Atspi.Accessible) -> bool:
        """Returns True if the image interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_image_iface)

    @staticmethod
    def supports_selection(obj: Atspi.Accessible) -> bool:
        """Returns True if the selection interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_selection_iface)

    @staticmethod
    def supports_table(obj: Atspi.Accessible) -> bool:
        """Returns True if the table interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_table_iface)

    @staticmethod
    def supports_table_cell(obj: Atspi.Accessible) -> bool:
        """Returns True if the table cell interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_table_cell)

    @staticmethod
    def supports_text(obj: Atspi.Accessible) -> bool:
        """Returns True if the text interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_text_iface)

    @staticmethod
    def supports_value(obj: Atspi.Accessible) -> bool:
        """Returns True if the value interface is supported on obj"""

        return AXObject._supports_interface(obj, Atspi.Accessible.get_value_iface)

    @staticmethod
    def get_path(obj: Atspi.Accessible) -> list[int]:
        """Returns the path from application to obj as list of child indices"""

        if not AXObject.is_valid(obj):
            return []

        path = []
        acc = obj
        while acc:
            try:
                path.append(Atspi.Accessible.get_index_in_parent(acc))
            except GLib.GError as error:
                msg = f"AXObject: Exception getting index in parent for {acc}: {error}"
                AXObject.handle_error(acc, error, msg)
                return []
            acc = AXObject.get_parent_checked(acc)

        path.reverse()
        return path

    @staticmethod
    def get_index_in_parent(obj: Atspi.Accessible) -> int:
        """Returns the child index of obj within its parent"""

        if not AXObject.is_valid(obj):
            return -1

        try:
            index = Atspi.Accessible.get_index_in_parent(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_index_in_parent: {error}"
            AXObject.handle_error(obj, error, msg)
            return -1

        return index

    @staticmethod
    def get_parent(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the accessible parent of obj. See also get_parent_checked."""

        if not AXObject.is_valid(obj):
            return None

        try:
            parent = Atspi.Accessible.get_parent(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_parent: {error}"
            AXObject.handle_error(obj, error, msg)
            return None

        if parent == obj:
            tokens = ["AXObject:", obj, "claims to be its own parent"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if parent is None and AXObject.get_role(obj) not in [
            Atspi.Role.INVALID,
            Atspi.Role.DESKTOP_FRAME,
        ]:
            tokens = ["AXObject:", obj, "claims to have no parent"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return parent

    @staticmethod
    def get_parent_checked(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the parent of obj, doing checks for tree validity"""

        if AXObject.get_role(obj) in (Atspi.Role.INVALID, Atspi.Role.APPLICATION):
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        if debug.debugLevel > debug.LEVEL_INFO or AXObject.is_dead(obj):
            return parent

        index = AXObject.get_index_in_parent(obj)
        n_children = AXObject.get_child_count(parent)
        if index < 0 or index >= n_children:
            tokens = [
                "AXObject:",
                obj,
                "has index",
                index,
                "; parent",
                parent,
                "has",
                n_children,
                "children",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        else:
            # This performs our check and includes any errors.
            AXObject.get_active_descendant_checked(parent, obj)

        return parent

    @staticmethod
    def get_child(
        obj: Atspi.Accessible,
        index: int,
        n_children: int | None = None,
    ) -> Atspi.Accessible | None:
        """Returns the nth child of obj. See also get_child_checked."""

        if not AXObject.is_valid(obj):
            return None

        if n_children is None:
            n_children = AXObject.get_child_count(obj)

        if n_children <= 0:
            return None

        if index == -1:
            index = n_children - 1

        if not 0 <= index < n_children:
            return None

        try:
            child = Atspi.Accessible.get_child_at_index(obj, index)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_child: {error}"
            AXObject.handle_error(obj, error, msg)
            return None

        if child == obj:
            tokens = ["AXObject:", obj, "claims to be its own child"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return child

    @staticmethod
    def get_child_checked(obj: Atspi.Accessible, index: int) -> Atspi.Accessible | None:
        """Returns the nth child of obj, doing checks for tree validity"""

        if not AXObject.is_valid(obj):
            return None

        child = AXObject.get_child(obj, index)
        if debug.debugLevel > debug.LEVEL_INFO:
            return child

        parent = AXObject.get_parent(child)
        if obj != parent:
            tokens = ["AXObject:", obj, "claims", child, "as child; child's parent is", parent]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return child

    @staticmethod
    def get_active_descendant_checked(
        container: Atspi.Accessible,
        reported_child: Atspi.Accessible,
    ) -> Atspi.Accessible | None:
        """Checks the reported active descendant and return the real/valid one."""

        if not AXObject.has_state(container, Atspi.StateType.MANAGES_DESCENDANTS):
            return reported_child

        index = AXObject.get_index_in_parent(reported_child)
        try:
            real_child = Atspi.Accessible.get_child_at_index(container, index)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_active_descendant_checked: {error}"
            AXObject.handle_error(container, error, msg)
            return reported_child

        if real_child != reported_child:
            tokens = [
                "AXObject: ",
                container,
                f"'s child at {index} is ",
                real_child,
                "; not reported child",
                reported_child,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return real_child

    @staticmethod
    def get_role(obj: Atspi.Accessible) -> Atspi.Role:
        """Returns the accessible role of obj"""

        if not AXObject.is_valid(obj):
            return Atspi.Role.INVALID

        try:
            role = Atspi.Accessible.get_role(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_role: {error}"
            AXObject.handle_error(obj, error, msg)
            return Atspi.Role.INVALID

        AXObject._set_known_dead_status(obj, False)
        return role

    @staticmethod
    def get_role_name(obj: Atspi.Accessible, localized: bool = False) -> str:
        """Returns the accessible role name of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            if not localized:
                role_name = Atspi.Accessible.get_role_name(obj)
            else:
                role_name = Atspi.Accessible.get_localized_role_name(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_role_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return role_name

    @staticmethod
    def get_role_description(obj: Atspi.Accessible, is_braille: bool = False) -> str:
        """Returns the accessible role description of obj"""

        if not AXObject.is_valid(obj):
            return ""

        attrs = AXObject.get_attributes_dict(obj)
        rv = attrs.get("roledescription", "")
        if is_braille:
            rv = attrs.get("brailleroledescription", rv)
        return rv

    @staticmethod
    def get_accessible_id(obj: Atspi.Accessible) -> str:
        """Returns the accessible id of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            result = Atspi.Accessible.get_accessible_id(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_accessible_id: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        AXObject._set_known_dead_status(obj, False)
        return result

    @staticmethod
    def get_name(obj: Atspi.Accessible) -> str:
        """Returns the accessible name of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            name = Atspi.Accessible.get_name(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        AXObject._set_known_dead_status(obj, False)
        return name

    @staticmethod
    def has_same_non_empty_name(obj1: Atspi.Accessible, obj2: Atspi.Accessible) -> bool:
        """Returns true if obj1 and obj2 share the same non-empty name"""

        name1 = AXObject.get_name(obj1)
        if not name1:
            return False

        return name1 == AXObject.get_name(obj2)

    @staticmethod
    def get_description(obj: Atspi.Accessible) -> str:
        """Returns the accessible description of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            description = Atspi.Accessible.get_description(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_image_description(obj: Atspi.Accessible) -> str:
        """Returns the accessible image description of obj"""

        if not AXObject.supports_image(obj):
            return ""

        try:
            description = Atspi.Image.get_image_description(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_image_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_image_size(obj: Atspi.Accessible) -> tuple[int, int]:
        """Returns a (width, height) tuple of the image in obj"""

        if not AXObject.supports_image(obj):
            return 0, 0

        try:
            result = Atspi.Image.get_image_size(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_image_size: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0, 0

        # The return value is an AtspiPoint, hence x and y.
        return result.x, result.y

    @staticmethod
    def get_help_text(obj: Atspi.Accessible) -> str:
        """Returns the accessible help text of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            # Added in Atspi 2.52.
            text = Atspi.Accessible.get_help_text(obj) or ""
        except GLib.GError:
            # This is for prototyping in the meantime.
            text = AXObject.get_attribute(obj, "helptext") or ""

        return text

    @staticmethod
    def get_child_count(obj: Atspi.Accessible) -> int:
        """Returns the child count of obj"""

        if not AXObject.is_valid(obj):
            return 0

        try:
            count = Atspi.Accessible.get_child_count(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_child_count: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0

        return count

    @staticmethod
    def iter_children(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> Generator[Atspi.Accessible, None, None]:
        """Generator to iterate through obj's children. If the function pred is
        specified, children for which pred is False will be skipped."""

        if not AXObject.is_valid(obj):
            return

        child_count = AXObject.get_child_count(obj)
        if child_count > 500:
            tokens = ["AXObject:", obj, "has more than 500 children"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        for index in range(child_count):
            child = AXObject.get_child(obj, index, child_count)
            if child is None and not AXObject.is_valid(obj):
                tokens = ["AXObject:", obj, "is no longer valid"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return

            if child is not None and (pred is None or pred(child)):
                yield child

    @staticmethod
    def get_previous_sibling(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the previous sibling of obj, based on child indices"""

        if not AXObject.is_valid(obj):
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        index = AXObject.get_index_in_parent(obj)
        if index <= 0:
            return None

        sibling = AXObject.get_child(parent, index - 1)
        if sibling == obj:
            tokens = ["AXObject:", obj, "claims to be its own sibling"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return sibling

    @staticmethod
    def get_next_sibling(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the next sibling of obj, based on child indices"""

        if not AXObject.is_valid(obj):
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        index = AXObject.get_index_in_parent(obj)
        if index < 0:
            return None

        sibling = AXObject.get_child(parent, index + 1)
        if sibling == obj:
            tokens = ["AXObject:", obj, "claims to be its own sibling"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return sibling

    @staticmethod
    def get_locale(obj: Atspi.Accessible) -> str:
        """Returns the locale of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            locale = Atspi.Accessible.get_object_locale(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_locale: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return locale or ""

    @staticmethod
    def get_state_set(obj: Atspi.Accessible) -> Atspi.StateSet:
        """Returns the state set associated with obj"""

        if not AXObject.is_valid(obj):
            return Atspi.StateSet()

        try:
            state_set = Atspi.Accessible.get_state_set(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_state_set: {error}"
            AXObject.handle_error(obj, error, msg)
            return Atspi.StateSet()

        if state_set is None:
            tokens = ["AXObject: get_state_set failed for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return Atspi.StateSet()

        AXObject._set_known_dead_status(obj, False)
        return state_set

    @staticmethod
    def has_state(
        obj: Atspi.Accessible,
        state: Atspi.StateType,
        state_set: Atspi.StateSet | None = None,
    ) -> bool:
        """Returns true if obj has the specified state"""

        if state_set is not None:
            return state_set.contains(state)

        if not AXObject.is_valid(obj):
            return False

        return AXObject.get_state_set(obj).contains(state)

    @staticmethod
    def clear_cache(obj: Atspi.Accessible, recursive: bool = False, reason: str = "") -> None:
        """Clears the Atspi cached information associated with obj"""

        if obj is None:
            return

        tokens = ["AXObject: Clearing AT-SPI cache on", obj, f"Recursive: {recursive}."]
        if reason:
            tokens.append(f" Reason: {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not recursive:
            try:
                Atspi.Accessible.clear_cache_single(obj)
            except GLib.GError as error:
                msg = f"AXObject: Exception in clear_cache_single: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        try:
            Atspi.Accessible.clear_cache(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in clear_cache: {error}"
            AXObject.handle_error(obj, error, msg)

    @staticmethod
    def get_process_id(obj: Atspi.Accessible) -> int:
        """Returns the process id associated with obj"""

        if not AXObject.is_valid(obj):
            return -1

        try:
            pid = Atspi.Accessible.get_process_id(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_process_id: {error}"
            AXObject.handle_error(obj, error, msg)
            return -1

        return pid

    @staticmethod
    def is_dead(obj: Atspi.Accessible, app: Atspi.Accessible | None = None) -> bool:
        """Returns true of obj exists but is believed to be dead."""

        if obj is None:
            return False

        if not AXObject.is_valid(obj, app):
            return True

        try:
            # We use the Atspi function rather than the AXObject function because the
            # latter intentionally handles exceptions.
            Atspi.Accessible.get_name(obj)
        except GLib.GError as error:
            msg = f"AXObject: Accessible is dead: {error}"
            AXObject.handle_error(obj, error, msg)
            return True

        AXObject._set_known_dead_status(obj, False)
        return False

    @staticmethod
    def get_attributes_dict(obj: Atspi.Accessible, use_cache: bool = True) -> dict[str, str]:
        """Returns the object attributes of obj as a dictionary."""

        if not AXObject.is_valid(obj):
            return {}

        if use_cache:
            attributes = AXObject._CACHE.get_attributes(obj)
            if attributes is not ax_cache_manager.MISSING:
                return attributes

        try:
            attributes = Atspi.Accessible.get_attributes(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_attributes_dict: {error}"
            AXObject.handle_error(obj, error, msg)
            return {}

        if attributes is None:
            return {}

        AXObject._CACHE.set_attributes(obj, attributes)
        return attributes

    @staticmethod
    def get_attribute(obj: Atspi.Accessible, attribute_name: str, use_cache: bool = True) -> str:
        """Returns the value of the specified attribute as a string."""

        if not AXObject.is_valid(obj):
            return ""

        attributes = AXObject.get_attributes_dict(obj, use_cache)
        return attributes.get(attribute_name, "")

    @staticmethod
    def grab_focus(obj: Atspi.Accessible) -> bool:
        """Attempts to grab focus on obj. Returns true if successful."""

        if not AXObject.supports_component(obj):
            return False

        try:
            result = Atspi.Component.grab_focus(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in grab_focus: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        if debug.debugLevel > debug.LEVEL_INFO:
            return result

        if result and not AXObject.has_state(obj, Atspi.StateType.FOCUSED):
            tokens = ["AXObject:", obj, "lacks focused state after focus grab"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result
