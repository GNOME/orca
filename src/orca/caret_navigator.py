# Orca
#
# Copyright 2013-2025 Igalia, S.L.
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

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines

"""Provides an Orca-controlled caret for text content."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from . import (
    caret_navigator_command_definitions,
    command_manager,
    dbus_service,
    debug,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    input_event_manager,
    messages,
    presentation_manager,
    say_all_presenter,
    script_manager,
    text_selection_manager,
    text_selection_presenter,
)
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_utilities_text import CaretSetReason
from .extension import Extension

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .command import Command
    from .scripts import default


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.CaretNavigation",
    name="caret-navigation",
)
class CaretNavigator(Extension):
    """Implements the caret navigation support available to scripts."""

    _SCHEMA = "caret-navigation"
    KEY_ENABLED = "enabled"
    KEY_SELECTION_ENABLED = "selection-enabled"
    KEY_TRIGGERS_FOCUS_MODE = "triggers-focus-mode"
    KEY_LAYOUT_MODE = "layout-mode"
    SELECTION_ACTIVATION_GROUP = "caret-selection"

    def _get_setting(self, key: str, default: bool) -> bool:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            "b",
            default=default,
        )

    GROUP_LABEL = guilabels.KB_GROUP_CARET_NAVIGATION

    def __init__(self) -> None:
        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended: bool = False
        self._last_input_event: input_event.InputEvent | None = None
        self._enabled_for_script: dict[default.Script, bool] = {}
        super().__init__()

    @staticmethod
    def navigation_command(func):
        """Decorator that logs the command, then dispatches to it."""

        @functools.wraps(func)
        def wrapper(self, script, event=None, notify_user=True) -> bool:
            tokens = [
                "CARET NAVIGATOR:",
                func,
                "\nScript:",
                script,
                "\nEvent:",
                event,
                "\nnotify_user:",
                notify_user,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return func(self, script, event, notify_user)

        return wrapper

    def _get_commands(self) -> list[Command]:
        return caret_navigator_command_definitions.get_commands(self)

    def _is_active_script(self, script):
        active_script = script_manager.get_manager().get_active_script()
        if active_script == script:
            return True

        tokens = ["CARET NAVIGATOR:", script, "is not the active script", active_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ENABLED,
        schema="caret-navigation",
        gtype="b",
        default=True,
        summary="Enable caret navigation",
        migration_key="caretNavigationEnabled",
    )
    @dbus_service.getter
    def get_is_enabled(self) -> bool:
        """Returns whether caret navigation is enabled."""

        return self._get_setting(self.KEY_ENABLED, True)

    @dbus_service.setter
    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether caret navigation is enabled."""

        if self.get_is_enabled() == value:
            tokens = ["CARET NAVIGATOR: Enabled already", value, ". Refreshing command group."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            command_manager.get_manager().set_group_enabled(
                guilabels.KB_GROUP_CARET_NAVIGATION,
                value,
            )
            command_manager.get_manager().set_group_enabled(
                self.SELECTION_ACTIVATION_GROUP,
                value and self.get_selection_enabled(),
            )
            return True

        tokens = ["CARET NAVIGATOR: Setting enabled to", value, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, self.KEY_ENABLED, value)

        self._last_input_event = None
        command_manager.get_manager().set_group_enabled(guilabels.KB_GROUP_CARET_NAVIGATION, value)
        command_manager.get_manager().set_group_enabled(
            self.SELECTION_ACTIVATION_GROUP,
            value and self.get_selection_enabled(),
        )

        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SELECTION_ENABLED,
        schema="caret-navigation",
        gtype="b",
        default=False,
        summary="Enable Orca-controlled text selection",
        user_visible=False,
    )
    def get_selection_enabled(self) -> bool:
        """Returns whether Orca-controlled text selection is enabled."""

        return self._get_setting(self.KEY_SELECTION_ENABLED, False)

    def set_selection_enabled(self, value: bool) -> bool:
        """Sets whether Orca-controlled text selection is enabled."""

        if self.get_selection_enabled() != value:
            tokens = ["CARET NAVIGATOR: Setting text selection enabled to", value, "."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            gsettings_registry.get_registry().set_runtime_value(
                self._SCHEMA,
                self.KEY_SELECTION_ENABLED,
                value,
            )

        manager = command_manager.get_manager()
        manager.set_group_enabled(
            self.SELECTION_ACTIVATION_GROUP,
            value and manager.is_group_enabled(guilabels.KB_GROUP_CARET_NAVIGATION),
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_TRIGGERS_FOCUS_MODE,
        schema="caret-navigation",
        gtype="b",
        default=False,
        summary="Caret navigation triggers focus mode",
        migration_key="caretNavTriggersFocusMode",
    )
    @dbus_service.getter
    def get_triggers_focus_mode(self) -> bool:
        """Returns whether caret navigation triggers focus mode."""

        return self._get_setting(self.KEY_TRIGGERS_FOCUS_MODE, False)

    @dbus_service.setter
    def set_triggers_focus_mode(self, value: bool) -> bool:
        """Sets whether caret navigation triggers focus mode."""

        if self.get_triggers_focus_mode() == value:
            return True

        tokens = ["CARET NAVIGATOR: Setting triggers focus mode to", value, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_TRIGGERS_FOCUS_MODE,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_LAYOUT_MODE,
        schema="caret-navigation",
        gtype="b",
        default=True,
        summary="Use document layout mode",
        migration_key="layoutMode",
    )
    @dbus_service.getter
    def get_layout_mode(self) -> bool:
        """Returns whether layout mode is enabled."""

        return self._get_setting(self.KEY_LAYOUT_MODE, True)

    @dbus_service.setter
    def set_layout_mode(self, value: bool) -> bool:
        """Sets whether layout mode is enabled."""

        if self.get_layout_mode() == value:
            return True

        tokens = ["CARET NAVIGATOR: Setting layout mode to", value, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_LAYOUT_MODE, value
        )
        return True

    @dbus_service.command
    def toggle_layout_mode(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Switches between object mode and layout mode for line presentation."""

        tokens = [
            "CARET NAVIGATOR: toggle_layout_mode. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        layout_mode = not self.get_layout_mode()
        if notify_user:
            if layout_mode:
                presentation_manager.get_manager().present_message(messages.MODE_LAYOUT)
            else:
                presentation_manager.get_manager().present_message(messages.MODE_OBJECT)
        self.set_layout_mode(layout_mode)
        return True

    def get_enabled_for_script(self, script: default.Script) -> bool:
        """Returns the current caret-navigator enabled state associated with script."""

        enabled = self._enabled_for_script.get(script, False)
        tokens = ["CARET NAVIGATOR: Enabled state for", script, "is", enabled]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return enabled

    def set_enabled_for_script(self, script: default.Script, enabled: bool) -> None:
        """Sets the current caret-navigator enabled state associated with script."""

        tokens = ["CARET NAVIGATOR: Setting enabled state for", script, "to", enabled]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._enabled_for_script[script] = enabled

        if not (script and self._is_active_script(script)):
            return

        # Use the per-script state combined with the user's preference to determine
        # whether commands should be active, without overwriting the preference.
        effective = enabled and self.get_is_enabled()
        command_manager.get_manager().set_group_enabled(
            guilabels.KB_GROUP_CARET_NAVIGATION,
            effective,
        )
        command_manager.get_manager().set_group_enabled(
            self.SELECTION_ACTIVATION_GROUP,
            effective and self.get_selection_enabled(),
        )

    def last_input_event_was_navigation_command(self) -> bool:
        """Returns true if the last input event was a navigation command."""

        if self._last_input_event is None:
            return False

        manager = input_event_manager.get_manager()
        result = manager.last_event_equals_or_is_release_for_event(self._last_input_event)
        if self._last_input_event is not None:
            string = self._last_input_event.as_single_line_string()
        else:
            string = "None"

        tokens = [
            "CARET NAVIGATOR: Last navigation event (",
            string,
            ") is last input event:",
            result,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def last_command_prevents_focus_mode(self) -> bool:
        """Returns True if the last command was navigation but the setting disallows focus mode."""

        if not self.last_input_event_was_navigation_command():
            return False

        return not self.get_triggers_focus_mode()

    @dbus_service.command
    def toggle_enabled(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles caret navigation."""

        tokens = [
            "CARET NAVIGATOR: toggle_enabled. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        enabled = not command_manager.get_manager().is_group_enabled(
            guilabels.KB_GROUP_CARET_NAVIGATION,
        )
        if enabled:
            string = messages.CARET_CONTROL_ORCA
        else:
            string = messages.CARET_CONTROL_APP
            script.utilities.clear_caret_context()

        if notify_user:
            presentation_manager.get_manager().present_message(string)

        self.set_is_enabled(enabled)
        return True

    def suspend_commands(self, script: default.Script, suspended: bool, reason: str = "") -> None:
        """Suspends caret navigation independent of the enabled setting."""

        if not (script and self._is_active_script(script)):
            return

        tokens = ["CARET NAVIGATOR: Commands suspended:", suspended]
        if reason:
            tokens += [":", reason]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._suspended = suspended
        command_manager.get_manager().set_group_suspended(
            guilabels.KB_GROUP_CARET_NAVIGATION,
            suspended,
        )
        command_manager.get_manager().set_group_suspended(
            self.SELECTION_ACTIVATION_GROUP,
            suspended,
        )

    def _select_with_command(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        command: Callable[[default.Script, input_event.InputEvent | None, bool], bool],
        selection_forward: bool,
    ) -> bool:
        """Extends a text selection by executing command."""

        caret_obj, caret_offset = script.utilities.get_caret_context()
        obj, offset = AXUtilities.get_text_selection_endpoint_for_caret_context(
            caret_obj,
            caret_offset,
            after_embedded_object=not selection_forward,
        )
        if obj is None:
            msg = "CARET NAVIGATOR: Cannot find an AtspiText endpoint for this object."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        selection_container = self._get_root_object(script, obj)
        # We'll present the selection change in response to the event that results.
        if not command(script, event, False):
            return False

        new_caret_obj, new_caret_offset = script.utilities.get_caret_context()
        new_obj, new_offset = AXUtilities.get_text_selection_endpoint_for_caret_context(
            new_caret_obj,
            new_caret_offset,
            after_embedded_object=selection_forward,
        )
        if new_obj is None:
            msg = "CARET NAVIGATOR: Cannot find an AtspiText endpoint for the new object."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return text_selection_manager.get_manager().set_text_selection(
            selection_container,
            obj,
            offset,
            new_obj,
            new_offset,
            new_caret_obj,
            selection_forward=selection_forward,
            event=event,
            notify_user=notify_user,
        )

    def _get_root_object(
        self,
        script: default.Script,
        obj: Atspi.Accessible | None = None,
    ) -> Atspi.Accessible | None:
        """Returns the object which should be treated as the root/container for navigation."""

        root = script.utilities.active_document()
        if root is None:
            if obj is None:
                obj, _offset = script.utilities.get_caret_context()
            if AXObject.supports_text(obj):
                root = obj

        tokens = ["CARET NAVIGATOR: Root is", root]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return root

    def _set_caret_position(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        offset: int,
        *,
        reason: CaretSetReason,
        selection_root: Atspi.Accessible | None = None,
    ) -> None:
        """Sets the caret position, preserving selection when the reason requires it."""

        cleared_selection_objs: list[Atspi.Accessible] = []
        clear_selection = not reason.is_text_selection()
        if clear_selection:
            root = selection_root
            if root is None:
                root = self._get_root_object(script, obj)
            manager = text_selection_manager.get_manager()
            cleared_selection_objs = manager.clear_selection_for_navigation(
                root,
                obj,
            )

        script.utilities.set_caret_position(
            obj,
            offset,
            reason=reason,
        )

        if cleared_selection_objs:
            text_selection_presenter.get_presenter().present_selection_removed()

    def _is_navigable_object(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        root: Atspi.Accessible | None = None,
    ) -> bool:
        """Returns True if obj is a valid location for navigation."""

        # There's a small, theoretical possibility that we can creep out of the logical container,
        # but until that happens, this check is the most performant.
        if AXObject.supports_text(obj):
            return True

        if root is None:
            root = self._get_root_object(script)

        if root is None:
            return False

        return AXUtilities.is_ancestor(obj, root, True)

    def _line_contains_context(
        self,
        line: list[tuple[Atspi.Accessible, int, int, str]],
        context: tuple[Atspi.Accessible, int],
    ) -> bool:
        """Returns True if line contains the (obj, offset) context."""

        for entry in line:
            line_obj, start, end = entry[0], entry[1], entry[2]
            if line_obj == context[0] and start <= context[1] <= end:
                return True

        return False

    def _get_embedded_document_frame(self, script: default.Script) -> Atspi.Accessible | None:
        """Returns the embedded document frame that confines file-boundary navigation, if any."""

        obj, _offset = script.utilities.get_caret_context()
        if obj is None:
            return None
        return AXUtilities.get_embedded_document_frame_for_object(obj)

    def _get_start_of_file(self, script: default.Script) -> tuple[Atspi.Accessible | None, int]:
        """Returns the start of the file as (obj, offset)."""

        frame = self._get_embedded_document_frame(script)
        root = frame if frame is not None else self._get_root_object(script)
        obj, offset = script.utilities.first_context(root, 0)
        if obj is None:
            return None, -1

        while obj:
            prev_obj, prev_offset = script.utilities.previous_context(obj, offset, restrict_to=root)
            if prev_obj is None or (prev_obj, prev_offset) == (obj, offset):
                break
            # The web context walkers ignore restrict_to, so enforce the frame boundary here.
            if frame is not None and not AXUtilities.is_ancestor(prev_obj, frame, True):
                break
            obj, offset = prev_obj, prev_offset

        return obj, offset

    def _get_end_of_file(self, script: default.Script) -> tuple[Atspi.Accessible | None, int]:
        """Returns the end of the file as (obj, offset)."""

        frame = self._get_embedded_document_frame(script)
        root = frame if frame is not None else self._get_root_object(script)
        if root is None:
            return None, -1

        root_in_document = script.utilities.in_document_content(root)
        if not root_in_document:
            if not AXObject.supports_text(root):
                return None, -1
            return root, AXText.get_character_count(root)

        obj = AXUtilities.find_deepest_descendant(root)
        if obj is None:
            return None, -1

        # Chromium includes static text leaf nodes which we ignore; use the navigable parent.
        obj_in_document = (
            root_in_document if obj == root else script.utilities.in_document_content(obj)
        )
        if obj_in_document and not AXUtilities.is_web_element(obj):
            parent = AXObject.get_parent(obj)
            if AXUtilities.is_web_element(parent):
                obj = parent

        offset = max(0, AXText.get_character_count(obj) - 1)
        while obj:
            next_obj, next_offset = script.utilities.next_context(obj, offset, restrict_to=root)
            if next_obj is None or (next_obj, next_offset) == (obj, offset):
                break
            if not AXUtilities.is_ancestor(next_obj, root, True):
                break
            obj, offset = next_obj, next_offset

        return obj, offset

    def _get_caret_context_for_collapsing_selection(
        self,
        selection_root: Atspi.Accessible | None,
        *,
        forward: bool,
    ) -> tuple[Atspi.Accessible, int] | None:
        """Returns the selection boundary for Orca-driven caret navigation."""

        if selection_root is None:
            return None

        manager = text_selection_manager.get_manager()
        start, end = manager.get_known_text_selection_endpoints(selection_root)
        target_obj, target_offset = end if forward else start
        if target_obj is None:
            return None
        return AXUtilities.get_caret_context_for_text_selection_endpoint(
            target_obj,
            target_offset,
            endpoint_is_start=not forward,
        )

    def _get_text_selection_character_navigation_context(
        self,
        script: default.Script,
        forward: bool,
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the context for moving a text-selection endpoint by character."""

        obj, offset = script.utilities.get_caret_context()
        if forward:
            next_obj, next_offset = script.utilities.next_context()
            if next_obj == obj:
                return next_obj, next_offset

            if AXObject.supports_text(obj):
                character_count = AXText.get_character_count(obj)
                if 0 <= offset < character_count:
                    string, _start, end = AXText.get_character_at_offset(
                        obj,
                        offset,
                        ensure_whole_characters=True,
                    )
                    if string and not AXUtilities.is_eoc(string):
                        tokens = [
                            "CARET NAVIGATOR: Selecting through the current character in",
                            obj,
                            "before crossing to",
                            next_obj,
                        ]
                        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                        return obj, end

            if AXObject.supports_text(next_obj):
                string, _start, end = AXText.get_character_at_offset(
                    next_obj,
                    next_offset,
                    ensure_whole_characters=True,
                )
                if string:
                    tokens = [
                        "CARET NAVIGATOR: Selecting through the first character in",
                        next_obj,
                        "after crossing from",
                        obj,
                    ]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return next_obj, end
            return next_obj, next_offset
        return script.utilities.previous_context()

    def _move_text_selection_endpoint_by_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        forward: bool,
    ) -> bool:
        """Moves the active text-selection endpoint one character."""

        obj, offset = self._get_text_selection_character_navigation_context(script, forward)
        if not self._is_navigable_object(script, obj):
            return False

        string, char_start, char_end = AXText.get_character_at_offset(
            obj, offset, ensure_whole_characters=True
        )
        if string and offset > char_start:
            offset = char_end if forward else char_start

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            offset,
            reason=CaretSetReason.TEXT_SELECTION_BY_CHARACTER,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start_offset=offset,
            mode=focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        script.update_braille(obj, offset=offset)
        script.say_character(obj, offset)
        return True

    @dbus_service.command
    @navigation_command
    def next_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next character."""

        selection_root = self._get_root_object(script)
        context = self._get_caret_context_for_collapsing_selection(
            selection_root,
            forward=True,
        )
        if context is None:
            obj, offset = script.utilities.next_context()
        else:
            obj, offset = context
        if not self._is_navigable_object(script, obj):
            return False
        if selection_root is None:
            selection_root = obj

        string, char_start, char_end = AXText.get_character_at_offset(
            obj, offset, ensure_whole_characters=True
        )
        if string and offset > char_start:
            offset = char_end

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            offset,
            reason=CaretSetReason.CARET_NAVIGATION,
            selection_root=selection_root,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start_offset=offset,
            mode=focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        script.update_braille(obj, offset=offset)
        script.say_character(obj, offset)
        return True

    @dbus_service.command
    @navigation_command
    def previous_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous character."""

        selection_root = self._get_root_object(script)
        context = self._get_caret_context_for_collapsing_selection(
            selection_root,
            forward=False,
        )
        if context is None:
            obj, offset = script.utilities.previous_context()
        else:
            obj, offset = context
        if not self._is_navigable_object(script, obj):
            return False
        if selection_root is None:
            selection_root = obj

        string, char_start, _char_end = AXText.get_character_at_offset(
            obj, offset, ensure_whole_characters=True
        )
        if string and offset > char_start:
            offset = char_start

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            offset,
            reason=CaretSetReason.CARET_NAVIGATION,
            selection_root=selection_root,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start_offset=offset,
            mode=focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        script.update_braille(obj, offset=offset)
        script.say_character(obj, offset)
        return True

    @dbus_service.command
    @navigation_command
    def next_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next word."""

        return self._move_to_next_word(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_next_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the next word."""

        selection_root = None
        selection_boundary = None
        if not caret_set_reason.is_text_selection():
            selection_root = self._get_root_object(script)
            selection_boundary = self._get_caret_context_for_collapsing_selection(
                selection_root,
                forward=True,
            )
        if selection_boundary is not None:
            obj, offset = script.utilities.next_context(*selection_boundary, skip_space=True)
        else:
            obj, offset = script.utilities.next_context(skip_space=True)
        if obj is None:
            return False

        contents = script.utilities.get_word_contents_at_offset(obj, offset)
        if not contents:
            return False

        # If the "word" to the right consists of the content of the last word in an embedded
        # object followed by the space of the parent object, the normal space-adjustment we
        # do will cause us to set the caret to the offset with the embedded child and then
        # present the first word in that child.
        if len(contents) > 1 and contents[-1][3].isspace():
            msg = "CARET NAVIGATOR: Adjusting next word contents to eliminate trailing space."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            contents = contents[:-1]

        obj, start, end, string = contents[-1]
        if not self._is_navigable_object(script, obj):
            return False
        if selection_root is None:
            selection_root = obj

        # Strip trailing whitespace so a paragraph break does not cause the word to be skipped.
        end = start + len(string.rstrip())

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            end,
            reason=caret_set_reason,
            selection_root=selection_root,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        script.update_braille(obj, offset=end)
        script.say_word(obj, end)
        return True

    @dbus_service.command
    @navigation_command
    def previous_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous word."""

        return self._move_to_previous_word(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_previous_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the previous word."""

        selection_root = None
        selection_boundary = None
        if not caret_set_reason.is_text_selection():
            selection_root = self._get_root_object(script)
            selection_boundary = self._get_caret_context_for_collapsing_selection(
                selection_root,
                forward=False,
            )
        if selection_boundary is not None:
            obj, offset = script.utilities.previous_context(*selection_boundary, skip_space=True)
        else:
            obj, offset = script.utilities.previous_context(skip_space=True)
        if obj is None:
            return False

        contents = script.utilities.get_word_contents_at_offset(obj, offset)
        if not contents:
            return False

        obj, start, end, _string = contents[0]
        if not self._is_navigable_object(script, obj):
            return False
        if selection_root is None:
            selection_root = obj

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            start,
            reason=caret_set_reason,
            selection_root=selection_root,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        script.update_braille(obj, offset=start)
        script.say_word(obj, start)
        return True

    @dbus_service.command
    @navigation_command
    def next_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next line."""

        return self._move_to_next_line(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_next_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the next line."""

        if (
            focus_manager.get_manager().in_say_all()
            and say_all_presenter.get_presenter().get_rewind_and_fast_forward_enabled()
        ):
            msg = "CARET NAVIGATOR: In say all and rewind/fast-forward is enabled"
            debug.print_message(debug.LEVEL_INFO, msg)
            return True

        obj, offset = script.utilities.get_caret_context()
        if obj is None:
            return False

        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        move_to_line_end = False
        if caret_set_reason == CaretSetReason.TEXT_SELECTION_BY_LINE:
            line_obj, _start, end, _string = line[-1]
            move_to_line_end = line_obj == obj and offset == end

        selection_boundary = None
        selection_root = None
        if not caret_set_reason.is_text_selection():
            selection_root = self._get_root_object(script, obj)
            selection_boundary = self._get_caret_context_for_collapsing_selection(
                selection_root,
                forward=True,
            )
        if selection_boundary is not None:
            contents = script.utilities.get_next_line_contents(*selection_boundary)
        else:
            contents = script.utilities.get_next_line_contents()
        if caret_set_reason == CaretSetReason.TEXT_SELECTION_BY_LINE and contents:
            candidate = contents[-1] if line == contents or move_to_line_end else contents[0]
            if not self._is_navigable_object(script, candidate[0]):
                contents = []
        if not contents:
            last_obj, last_offset = self._get_end_of_file(script)
            boundary_line = (
                script.utilities.get_line_contents_at_offset(*selection_boundary)
                if selection_boundary is not None
                else line
            )
            if self._line_contains_context(boundary_line, (last_obj, last_offset)):
                msg = "CARET NAVIGATOR: At end of document; cannot move to next line."
                debug.print_message(debug.LEVEL_INFO, msg)
                contents = boundary_line
                if caret_set_reason == CaretSetReason.TEXT_SELECTION_BY_LINE:
                    move_to_line_end = True

        if not contents:
            return False

        if line != contents:
            if move_to_line_end:
                obj, _start, end, _string = contents[-1]
                offset = end
            else:
                obj, offset, end, _string = contents[0]
        else:
            obj, offset, end, _string = contents[-1]
            if move_to_line_end:
                offset = end

        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()

        self._set_caret_position(
            script,
            obj,
            offset,
            reason=caret_set_reason,
            selection_root=selection_root,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            offset,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if notify_user:
            # Setting the last object on the current line as priorObj
            # prevents re-announcing context.
            presenter = presentation_manager.get_manager()
            presenter.present_contents(contents, prior_obj=line[-1][0])
        return True

    @dbus_service.command
    @navigation_command
    def previous_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous line."""

        return self._move_to_previous_line(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_previous_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the previous line."""

        if (
            focus_manager.get_manager().in_say_all()
            and say_all_presenter.get_presenter().get_rewind_and_fast_forward_enabled()
        ):
            msg = "CARET NAVIGATOR: In say all and rewind/fast-forward is enabled"
            debug.print_message(debug.LEVEL_INFO, msg)
            return True

        obj, offset = script.utilities.get_caret_context()
        if obj is None:
            return False

        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if (
            caret_set_reason == CaretSetReason.TEXT_SELECTION_BY_LINE
            and line
            and any(start < 0 or end < start for _obj, start, end, _string in line)
        ):
            line = script.utilities.get_line_contents_at_offset(obj, max(0, offset - 1))
        if not (line and line[0]):
            return False

        if caret_set_reason == CaretSetReason.TEXT_SELECTION_BY_LINE:
            line_obj, start, end, _string = line[0]
            if line_obj == obj and start != end and offset == end:
                contents = line
            else:
                contents = script.utilities.get_previous_line_contents(obj, offset)
        else:
            contents = None

        selection_boundary = None
        selection_root = None
        if not caret_set_reason.is_text_selection():
            selection_root = self._get_root_object(script, obj)
            selection_boundary = self._get_caret_context_for_collapsing_selection(
                selection_root,
                forward=False,
            )
        if selection_boundary is not None:
            contents = script.utilities.get_previous_line_contents(*selection_boundary)
        elif contents is None:
            contents = script.utilities.get_previous_line_contents(obj, offset)
        if not contents:
            first_obj, first_offset = self._get_start_of_file(script)
            boundary_line = (
                script.utilities.get_line_contents_at_offset(*selection_boundary)
                if selection_boundary is not None
                else line
            )
            if self._line_contains_context(boundary_line, (first_obj, first_offset)):
                msg = "CARET NAVIGATOR: At start of document; cannot move to previous line."
                debug.print_message(debug.LEVEL_INFO, msg)
                contents = boundary_line

        if not contents:
            return False

        obj, start, end, _string = contents[0]
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            start,
            reason=caret_set_reason,
            selection_root=selection_root,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if notify_user:
            # Setting the first object on the current line as priorObj
            # prevents re-announcing context.
            presenter = presentation_manager.get_manager()
            presenter.present_contents(contents, prior_obj=line[0][0])
        return True

    @dbus_service.command
    @navigation_command
    def start_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the start of the line."""

        return self._move_to_start_of_line(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_start_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the start of the line."""

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        self._last_input_event = event
        obj, start, end, _string = line[0]
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            start,
            reason=caret_set_reason,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        script.say_character(obj, start)
        presentation_manager.get_manager().display_contents(line)
        return True

    @dbus_service.command
    @navigation_command
    def end_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the end of the line."""

        return self._move_to_end_of_line(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_end_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the end of the line."""

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        obj, start, end, string = line[-1]
        if string.strip() and string[-1].isspace():
            end -= 1

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            end,
            reason=caret_set_reason,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        script.say_character(obj, end)
        presentation_manager.get_manager().display_contents(line)
        return True

    @dbus_service.command
    @navigation_command
    def start_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the start of the file."""

        return self._move_to_start_of_file(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_start_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the start of the file."""

        prior_obj, _prior_offset = script.utilities.get_caret_context()
        obj, start = self._get_start_of_file(script)
        if obj is None:
            return False

        contents = script.utilities.get_line_contents_at_offset(obj, start)
        if not contents:
            return False

        self._last_input_event = event
        obj, start, end, _string = contents[0]
        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            start,
            reason=caret_set_reason,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        presenter = presentation_manager.get_manager()
        if AXUtilities.is_page(obj):
            prior_obj = obj
        presenter.present_contents(contents, prior_obj=prior_obj)
        return True

    @dbus_service.command
    @navigation_command
    def end_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the end of the file."""

        return self._move_to_end_of_file(
            script,
            event,
            notify_user,
            caret_set_reason=CaretSetReason.CARET_NAVIGATION,
        )

    def _move_to_end_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None,
        notify_user: bool,
        *,
        caret_set_reason: CaretSetReason,
    ) -> bool:
        """Moves to the end of the file."""

        prior_obj, _prior_offset = script.utilities.get_caret_context()
        obj, end = self._get_end_of_file(script)
        if obj is None:
            return False

        character_count = AXText.get_character_count(obj)
        line_offset = min(end, max(0, character_count - 1))
        contents = script.utilities.get_line_contents_at_offset(obj, line_offset)
        if not contents:
            return False

        self._last_input_event = event
        obj, start, end, _string = contents[-1]
        character_count = AXText.get_character_count(obj)
        if character_count > 0 and not 0 <= start <= end <= character_count:
            tokens = ["CARET NAVIGATOR: Invalid end-of-file line range:", contents[-1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        presentation_manager.get_manager().interrupt_presentation()
        self._set_caret_position(
            script,
            obj,
            end,
            reason=caret_set_reason,
        )
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        presenter = presentation_manager.get_manager()
        if AXUtilities.is_page(obj):
            prior_obj = obj
        presenter.present_contents(contents, prior_obj=prior_obj)
        return True

    @navigation_command
    def select_next_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the next character."""

        command = functools.partial(
            self._move_text_selection_endpoint_by_character,
            forward=True,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=True,
        )

    @navigation_command
    def select_previous_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the previous character."""

        command = functools.partial(
            self._move_text_selection_endpoint_by_character,
            forward=False,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=False,
        )

    @navigation_command
    def select_next_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the next word."""

        command = functools.partial(
            self._move_to_next_word,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_WORD,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=True,
        )

    @navigation_command
    def select_previous_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the previous word."""

        command = functools.partial(
            self._move_to_previous_word,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_WORD,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=False,
        )

    @navigation_command
    def select_next_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the next line."""

        command = functools.partial(
            self._move_to_next_line,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )

        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=True,
        )

    @navigation_command
    def select_previous_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the previous line."""

        command = functools.partial(
            self._move_to_previous_line,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )

        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=False,
        )

    @navigation_command
    def select_start_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the start of the file."""

        command = functools.partial(
            self._move_to_start_of_file,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_TO_FILE_BOUNDARY,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=False,
        )

    @navigation_command
    def select_end_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the end of the file."""

        command = functools.partial(
            self._move_to_end_of_file,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_TO_FILE_BOUNDARY,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=True,
        )

    @navigation_command
    def select_start_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the start of the line."""

        command = functools.partial(
            self._move_to_start_of_line,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_TO_LINE_BOUNDARY,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=False,
        )

    @navigation_command
    def select_end_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the end of the line."""

        command = functools.partial(
            self._move_to_end_of_line,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_TO_LINE_BOUNDARY,
        )
        return self._select_with_command(
            script,
            event,
            notify_user,
            command,
            selection_forward=True,
        )

    @dbus_service.testing_user_command
    def select_next_character_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the next character during integration tests."""

        if script is None:
            return False
        return self.select_next_character(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_previous_character_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the previous character during integration tests."""

        if script is None:
            return False
        return self.select_previous_character(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_next_word_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the next word during integration tests."""

        if script is None:
            return False
        return self.select_next_word(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_previous_word_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the previous word during integration tests."""

        if script is None:
            return False
        return self.select_previous_word(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_next_line_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the next line during integration tests."""

        if script is None:
            return False
        return self.select_next_line(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_previous_line_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the previous line during integration tests."""

        if script is None:
            return False
        return self.select_previous_line(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_start_of_file_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the start of the file during integration tests."""

        if script is None:
            return False
        return self.select_start_of_file(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_end_of_file_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the end of the file during integration tests."""

        if script is None:
            return False
        return self.select_end_of_file(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_start_of_line_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the start of the line during integration tests."""

        if script is None:
            return False
        return self.select_start_of_line(script, event, notify_user)

    @dbus_service.testing_user_command
    def select_end_of_line_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Extends the selection to the end of the line during integration tests."""

        if script is None:
            return False
        return self.select_end_of_line(script, event, notify_user)


_navigator = CaretNavigator()


def get_navigator() -> CaretNavigator:
    """Returns the Caret Navigator."""

    return _navigator
