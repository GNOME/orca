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

# pylint: disable=too-many-return-statements
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals

"""Provides an Orca-controlled caret for text content."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

from typing import TYPE_CHECKING

from . import (
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    input_event_manager,
    keybindings,
    messages,
    presentation_manager,
    say_all_presenter,
    script_manager,
)
from .ax_object import AXObject
from .ax_text import AXText

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.CaretNavigation",
    name="caret-navigation",
)
class CaretNavigator:
    """Implements the caret navigation support available to scripts."""

    _SCHEMA = "caret-navigation"

    def _get_setting(self, key: str, default: bool) -> bool:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            "b",
            default=default,
        )

    def __init__(self) -> None:
        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended: bool = False
        self._last_input_event: input_event.InputEvent | None = None
        self._enabled_for_script: dict[default.Script, bool] = {}
        self._initialized: bool = False

        msg = "CARET NAVIGATOR: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("CaretNavigator", self)

    def set_up_commands(self) -> None:
        """Sets up the caret-navigation commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_CARET_NAVIGATION

        # Keybindings (same for desktop and laptop)
        kb_f12 = keybindings.KeyBinding("F12", keybindings.ORCA_MODIFIER_MASK)
        kb_right = keybindings.KeyBinding("Right", keybindings.NO_MODIFIER_MASK)
        kb_left = keybindings.KeyBinding("Left", keybindings.NO_MODIFIER_MASK)
        kb_right_ctrl = keybindings.KeyBinding("Right", keybindings.CTRL_MODIFIER_MASK)
        kb_left_ctrl = keybindings.KeyBinding("Left", keybindings.CTRL_MODIFIER_MASK)
        kb_down = keybindings.KeyBinding("Down", keybindings.NO_MODIFIER_MASK)
        kb_up = keybindings.KeyBinding("Up", keybindings.NO_MODIFIER_MASK)
        kb_end = keybindings.KeyBinding("End", keybindings.NO_MODIFIER_MASK)
        kb_home = keybindings.KeyBinding("Home", keybindings.NO_MODIFIER_MASK)
        kb_end_ctrl = keybindings.KeyBinding("End", keybindings.CTRL_MODIFIER_MASK)
        kb_home_ctrl = keybindings.KeyBinding("Home", keybindings.CTRL_MODIFIER_MASK)

        manager.add_command(
            command_manager.KeyboardCommand(
                "toggle_enabled",
                self.toggle_enabled,
                group_label,
                cmdnames.CARET_NAVIGATION_TOGGLE,
                desktop_keybinding=kb_f12,
                laptop_keybinding=kb_f12,
                enabled=not self._suspended,
                is_group_toggle=True,
            ),
        )

        enabled = self.get_is_enabled() and not self._suspended

        # (name, function, description, keybinding)
        commands_data = [
            ("next_character", self.next_character, cmdnames.CARET_NAVIGATION_NEXT_CHAR, kb_right),
            (
                "previous_character",
                self.previous_character,
                cmdnames.CARET_NAVIGATION_PREV_CHAR,
                kb_left,
            ),
            ("next_word", self.next_word, cmdnames.CARET_NAVIGATION_NEXT_WORD, kb_right_ctrl),
            (
                "previous_word",
                self.previous_word,
                cmdnames.CARET_NAVIGATION_PREV_WORD,
                kb_left_ctrl,
            ),
            ("next_line", self.next_line, cmdnames.CARET_NAVIGATION_NEXT_LINE, kb_down),
            ("previous_line", self.previous_line, cmdnames.CARET_NAVIGATION_PREV_LINE, kb_up),
            (
                "start_of_file",
                self.start_of_file,
                cmdnames.CARET_NAVIGATION_FILE_START,
                kb_home_ctrl,
            ),
            ("end_of_file", self.end_of_file, cmdnames.CARET_NAVIGATION_FILE_END, kb_end_ctrl),
            ("start_of_line", self.start_of_line, cmdnames.CARET_NAVIGATION_LINE_START, kb_home),
            ("end_of_line", self.end_of_line, cmdnames.CARET_NAVIGATION_LINE_END, kb_end),
        ]

        for name, function, description, kb in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=kb,
                    laptop_keybinding=kb,
                    enabled=enabled,
                ),
            )

        manager.add_command(
            command_manager.KeyboardCommand(
                "toggle_layout_mode",
                self.toggle_layout_mode,
                group_label,
                cmdnames.TOGGLE_LAYOUT_MODE,
                enabled=enabled,
            ),
        )

        msg = f"CARET NAVIGATOR: Commands set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _is_active_script(self, script):
        active_script = script_manager.get_manager().get_active_script()
        if active_script == script:
            return True

        tokens = ["CARET NAVIGATOR:", script, "is not the active script", active_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    @gsettings_registry.get_registry().gsetting(
        key="enabled",
        schema="caret-navigation",
        gtype="b",
        default=True,
        summary="Enable caret navigation",
        migration_key="caretNavigationEnabled",
    )
    @dbus_service.getter
    def get_is_enabled(self) -> bool:
        """Returns whether caret navigation is enabled."""

        return self._get_setting("enabled", True)

    @dbus_service.setter
    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether caret navigation is enabled."""

        if self.get_is_enabled() == value:
            msg = f"CARET NAVIGATOR: Enabled already {value}. Refreshing command group."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            command_manager.get_manager().set_group_enabled(
                guilabels.KB_GROUP_CARET_NAVIGATION,
                value,
            )
            return True

        msg = f"CARET NAVIGATOR: Setting enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "enabled", value)

        self._last_input_event = None
        command_manager.get_manager().set_group_enabled(guilabels.KB_GROUP_CARET_NAVIGATION, value)

        return True

    @gsettings_registry.get_registry().gsetting(
        key="triggers-focus-mode",
        schema="caret-navigation",
        gtype="b",
        default=False,
        summary="Caret navigation triggers focus mode",
        migration_key="caretNavTriggersFocusMode",
    )
    @dbus_service.getter
    def get_triggers_focus_mode(self) -> bool:
        """Returns whether caret navigation triggers focus mode."""

        return self._get_setting("triggers-focus-mode", False)

    @dbus_service.setter
    def set_triggers_focus_mode(self, value: bool) -> bool:
        """Sets whether caret navigation triggers focus mode."""

        if self.get_triggers_focus_mode() == value:
            return True

        msg = f"CARET NAVIGATOR: Setting triggers focus mode to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "triggers-focus-mode",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="layout-mode",
        schema="caret-navigation",
        gtype="b",
        default=True,
        summary="Use document layout mode",
        migration_key="layoutMode",
    )
    @dbus_service.getter
    def get_layout_mode(self) -> bool:
        """Returns whether layout mode is enabled."""

        return self._get_setting("layout-mode", True)

    @dbus_service.setter
    def set_layout_mode(self, value: bool) -> bool:
        """Sets whether layout mode is enabled."""

        if self.get_layout_mode() == value:
            return True

        msg = f"CARET NAVIGATOR: Setting layout mode to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "layout-mode", value)
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
        tokens = ["CARET NAVIGATOR: Enabled state for", script, f"is {enabled}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return enabled

    def set_enabled_for_script(self, script: default.Script, enabled: bool) -> None:
        """Sets the current caret-navigator enabled state associated with script."""

        tokens = ["CARET NAVIGATOR: Setting enabled state for", script, f"to {enabled}"]
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

        msg = f"CARET NAVIGATOR: Last navigation event ({string}) is last input event: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
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

        msg = f"CARET NAVIGATOR: Commands suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._suspended = suspended
        command_manager.get_manager().set_group_suspended(
            guilabels.KB_GROUP_CARET_NAVIGATION,
            suspended,
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

        return AXObject.is_ancestor(obj, root, True)

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

    def _get_start_of_file(self, script: default.Script) -> tuple[Atspi.Accessible | None, int]:
        """Returns the start of the file as (obj, offset)."""

        root = self._get_root_object(script)
        obj, offset = script.utilities.first_context(root, 0)
        if obj is None:
            return None, -1

        while obj:
            prev_obj, prev_offset = script.utilities.previous_context(obj, offset, restrict_to=root)
            if prev_obj is None or (prev_obj, prev_offset) == (obj, offset):
                break
            obj, offset = prev_obj, prev_offset

        return obj, offset

    def _get_end_of_file(self, script: default.Script) -> tuple[Atspi.Accessible | None, int]:
        """Returns the end of the file as (obj, offset)."""

        root = self._get_root_object(script)
        obj = AXObject.find_deepest_descendant(root)
        if obj is None:
            return None, -1

        offset = max(0, AXText.get_character_count(obj) - 1)
        while obj:
            next_obj, next_offset = script.utilities.next_context(obj, offset, restrict_to=root)
            if next_obj is None or (next_obj, next_offset) == (obj, offset):
                break
            obj, offset = next_obj, next_offset

        return obj, offset

    @dbus_service.command
    def next_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next character."""

        tokens = [
            "CARET NAVIGATOR: next_character. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.next_context()
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start_offset=offset,
            mode=focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        script.update_braille(obj, offset=offset)
        script.say_character(obj)
        return True

    @dbus_service.command
    def previous_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous character."""

        tokens = [
            "CARET NAVIGATOR: previous_character. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.previous_context()
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start_offset=offset,
            mode=focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        script.update_braille(obj, offset=offset)
        script.say_character(obj)
        return True

    @dbus_service.command
    def next_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next word."""

        tokens = [
            "CARET NAVIGATOR: next_word. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

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

        if string and string[-1].isspace():
            end -= 1

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, end)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        script.update_braille(obj, offset=end)
        script.say_word(obj)
        return True

    @dbus_service.command
    def previous_word(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous word."""

        tokens = [
            "CARET NAVIGATOR: previous_word. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.previous_context(skip_space=True)
        if obj is None:
            return False

        contents = script.utilities.get_word_contents_at_offset(obj, offset)
        if not contents:
            return False

        obj, start, end, _string = contents[0]
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        script.update_braille(obj, offset=start)
        script.say_word(obj)
        return True

    @dbus_service.command
    def next_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next line."""

        tokens = [
            "CARET NAVIGATOR: next_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

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

        contents = script.utilities.get_next_line_contents()
        if not contents:
            last_obj, last_offset = self._get_end_of_file(script)
            if self._line_contains_context(line, (last_obj, last_offset)):
                msg = "CARET NAVIGATOR: At end of document; cannot move to next line."
                debug.print_message(debug.LEVEL_INFO, msg)
                contents = line

        if not contents:
            return False

        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()

        if line != contents:
            obj, offset, end, _string = contents[0]
        else:
            obj, offset, end, _string = contents[-1]

        script.utilities.set_caret_position(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj,
            offset,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        # Setting the last object on the current line as priorObj prevents re-announcing context.
        presenter = presentation_manager.get_manager()
        presenter.speak_contents(contents, priorObj=line[-1][0])
        presenter.display_contents(contents)
        return True

    @dbus_service.command
    def previous_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous line."""

        tokens = [
            "CARET NAVIGATOR: previous_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

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

        contents = script.utilities.get_previous_line_contents(obj, offset)
        if not contents:
            first_obj, first_offset = self._get_start_of_file(script)
            if self._line_contains_context(line, (first_obj, first_offset)):
                msg = "CARET NAVIGATOR: At start of document; cannot move to previous line."
                debug.print_message(debug.LEVEL_INFO, msg)
                contents = line

        if not contents:
            return False

        obj, start, end, _string = contents[0]
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        # Setting the first object on the current line as priorObj prevents re-announcing context.
        presenter = presentation_manager.get_manager()
        presenter.speak_contents(contents, priorObj=line[0][0])
        presenter.display_contents(contents)
        return True

    @dbus_service.command
    def start_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the start of the line."""

        tokens = [
            "CARET NAVIGATOR: start_of_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        self._last_input_event = event
        obj, start, end, _string = line[0]
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        script.say_character(obj)
        presentation_manager.get_manager().display_contents(line)
        return True

    @dbus_service.command
    def end_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the end of the line."""

        tokens = [
            "CARET NAVIGATOR: end_of_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        obj, start, end, string = line[-1]
        if string.strip() and string[-1].isspace():
            end -= 1

        self._last_input_event = event
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, end)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        script.say_character(obj)
        presentation_manager.get_manager().display_contents(line)
        return True

    @dbus_service.command
    def start_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the start of the file."""

        tokens = [
            "CARET NAVIGATOR: start_of_file. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, start = self._get_start_of_file(script)
        if obj is None:
            return False

        contents = script.utilities.get_line_contents_at_offset(obj, start)
        if not contents:
            return False

        self._last_input_event = event
        obj, start, end, _string = contents[0]
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )

        if not notify_user:
            return True

        presenter = presentation_manager.get_manager()
        presenter.speak_contents(contents)
        presenter.display_contents(contents)
        return True

    @dbus_service.command
    def end_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the end of the file."""

        tokens = [
            "CARET NAVIGATOR: end_of_file. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, end = self._get_end_of_file(script)
        if obj is None:
            return False

        contents = script.utilities.get_line_contents_at_offset(obj, end)
        if not contents:
            return False

        self._last_input_event = event
        obj, start, end, _string = contents[-1]
        presentation_manager.get_manager().interrupt_presentation()
        script.utilities.set_caret_position(obj, end)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start,
            end,
            focus_manager.CARET_NAVIGATOR,
        )
        if not notify_user:
            return True

        presenter = presentation_manager.get_manager()
        presenter.speak_contents(contents)
        presenter.display_contents(contents)
        return True


_navigator = CaretNavigator()


def get_navigator() -> CaretNavigator:
    """Returns the Caret Navigator."""

    return _navigator
