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

"""Provides an Orca-controlled caret for text content."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2013-2025 Igalia, S.L."
__license__ = "LGPL"

from typing import TYPE_CHECKING

from . import cmdnames
from . import dbus_service
from . import debug
from . import focus_manager
from . import input_event
from . import input_event_manager
from . import keybindings
from . import messages
from . import say_all_presenter
from . import script_manager
from . import settings_manager
from .ax_object import AXObject
from .ax_text import AXText

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default

class CaretNavigator:
    """Implements the caret navigation support available to scripts."""

    def __init__(self) -> None:
        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended: bool = False
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._last_input_event: input_event.InputEvent | None = None
        self._enabled_for_script: dict[default.Script, bool] = {}

        msg = "CARET NAVIGATOR: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("CaretNavigator", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the caret-navigation keybindings."""

        if refresh:
            msg = f"CARET NAVIGATOR: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("CARET NAVIGATOR: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the caret-navigation handlers."""

        if refresh:
            msg = "CARET NAVIGATOR: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the caret-navigation input event handlers."""

        self._handlers = {}

        self._handlers["toggle_enabled"] = \
            input_event.InputEventHandler(
                self.toggle_enabled,
                cmdnames.CARET_NAVIGATION_TOGGLE,
                enabled = not self._suspended)

        enabled = self.get_is_enabled() and not self._suspended

        self._handlers["next_character"] = \
            input_event.InputEventHandler(
                self.next_character,
                cmdnames.CARET_NAVIGATION_NEXT_CHAR,
                enabled = enabled)

        self._handlers["previous_character"] = \
            input_event.InputEventHandler(
                self.previous_character,
                cmdnames.CARET_NAVIGATION_PREV_CHAR,
                enabled = enabled)

        self._handlers["next_word"] = \
            input_event.InputEventHandler(
                self.next_word,
                cmdnames.CARET_NAVIGATION_NEXT_WORD,
                enabled = enabled)

        self._handlers["previous_word"] = \
            input_event.InputEventHandler(
                self.previous_word,
                cmdnames.CARET_NAVIGATION_PREV_WORD,
                enabled = enabled)

        self._handlers["next_line"] = \
            input_event.InputEventHandler(
                self.next_line,
                cmdnames.CARET_NAVIGATION_NEXT_LINE,
                enabled = enabled)

        self._handlers["previous_line"] = \
            input_event.InputEventHandler(
                self.previous_line,
                cmdnames.CARET_NAVIGATION_PREV_LINE,
                enabled = enabled)

        self._handlers["start_of_file"] = \
            input_event.InputEventHandler(
                self.start_of_file,
                cmdnames.CARET_NAVIGATION_FILE_START,
                enabled = enabled)

        self._handlers["end_of_file"] = \
            input_event.InputEventHandler(
                self.end_of_file,
                cmdnames.CARET_NAVIGATION_FILE_END,
                enabled = enabled)

        self._handlers["start_of_line"] = \
            input_event.InputEventHandler(
                self.start_of_line,
                cmdnames.CARET_NAVIGATION_LINE_START,
                enabled = enabled)

        self._handlers["end_of_line"] = \
            input_event.InputEventHandler(
                self.end_of_line,
                cmdnames.CARET_NAVIGATION_LINE_END,
                enabled = enabled)

        msg = f"CARET NAVIGATOR: Handlers set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up the caret-navigation key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "F12",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["toggle_enabled"],
                1,
                not self._suspended))

        enabled = self.get_is_enabled() and not self._suspended

        self._bindings.add(
            keybindings.KeyBinding(
                "Right",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_character"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "Left",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["previous_character"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "Right",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers["next_word"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "Left",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers["previous_word"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_line"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["previous_line"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "End",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["end_of_line"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "Home",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["start_of_line"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "End",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers["end_of_file"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "Home",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers["start_of_file"],
                1,
                enabled))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.get_manager().override_key_bindings(
            self._handlers, self._bindings, False)

        msg = f"CARET NAVIGATOR: Bindings set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _is_active_script(self, script):
        active_script = script_manager.get_manager().get_active_script()
        if active_script == script:
            return True

        tokens = ["CARET NAVIGATOR:", script, "is not the active script", active_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    @dbus_service.getter
    def get_is_enabled(self) -> bool:
        """Returns whether caret navigation is enabled."""

        return settings_manager.get_manager().get_setting("caretNavigationEnabled")

    @dbus_service.setter
    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether caret navigation is enabled."""

        if self.get_is_enabled() == value:
            return True

        msg = f"CARET NAVIGATOR: Setting enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("caretNavigationEnabled", value)

        self._last_input_event = None
        if script := script_manager.get_manager().get_active_script():
            self.refresh_bindings_and_grabs(script, msg)

        return True

    @dbus_service.getter
    def get_triggers_focus_mode(self) -> bool:
        """Returns whether caret navigation triggers focus mode."""

        return settings_manager.get_manager().get_setting("caretNavTriggersFocusMode")

    @dbus_service.setter
    def set_triggers_focus_mode(self, value: bool) -> bool:
        """Sets whether caret navigation triggers focus mode."""

        if self.get_triggers_focus_mode() == value:
            return True

        msg = f"CARET NAVIGATOR: Setting triggers focus mode to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("caretNavTriggersFocusMode", value)
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

        self.set_is_enabled(enabled)

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

    def refresh_bindings_and_grabs(self, script: default.Script, reason: str = "") -> None:
        """Refreshes caret navigation bindings and grabs for script."""

        msg = "CARET NAVIGATOR: Refreshing bindings and grabs"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.remove_bindings(script, reason)
        self.add_bindings(script, reason)

    def add_bindings(self, script: default.Script, reason: str = "") -> None:
        """Adds caret navigation bindings for script."""

        tokens = ["CARET NAVIGATOR: Adding bindings for", script]
        if reason:
            tokens.append(f": {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and self._is_active_script(script)):
            tokens = ["CARET NAVIGATOR: Not adding bindings for non-active script", script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["CARET NAVIGATOR:", script,
                      f"had {len(has_grabs)} key grabs prior to adding bindings."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.add(binding, include_grabs=not self._suspended)

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["CARET NAVIGATOR:", script, f"now has {len(has_grabs)} key grabs."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def remove_bindings(self, script: default.Script, reason: str = "") -> None:
        """Removes caret navigation bindings for script."""

        tokens = ["CARET NAVIGATOR: Removing bindings for", script]
        if reason:
            tokens.append(f": {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and self._is_active_script(script)):
            tokens = ["CARET NAVIGATOR: Not removing bindings for non-active script", script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["CARET NAVIGATOR:", script,
                      f"had {len(has_grabs)} key grabs prior to removing bindings."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.remove(binding, include_grabs=True)

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["CARET NAVIGATOR:", script, f"now has {len(has_grabs)} key grabs."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    @dbus_service.command
    def toggle_enabled(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles caret navigation."""

        tokens = ["CARET NAVIGATOR: toggle_enabled. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        enabled = not self.get_is_enabled()
        if enabled:
            string = messages.CARET_CONTROL_ORCA
        else:
            string = messages.CARET_CONTROL_APP
            script.utilities.clear_caret_context()

        if notify_user:
            script.present_message(string)

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
        self.refresh_bindings_and_grabs(script, f"Suspended changed to {suspended}")

    def _get_root_object(
        self,
        script: default.Script,
        obj: Atspi.Accessible | None = None
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
        root: Atspi.Accessible | None = None
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

    @dbus_service.command
    def next_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the next character."""

        tokens = ["CARET NAVIGATOR: next_character. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.next_context()
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, offset)
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
        notify_user: bool = True
    ) -> bool:
        """Moves to the previous character."""

        tokens = ["CARET NAVIGATOR: previous_character. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.previous_context()
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, offset)
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
        notify_user: bool = True
    ) -> bool:
        """Moves to the next word."""

        tokens = ["CARET NAVIGATOR: next_word. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
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

        obj, end, string = contents[-1][0], contents[-1][2], contents[-1][3]
        if not self._is_navigable_object(script, obj):
            return False

        if string and string[-1].isspace():
            end -= 1

        self._last_input_event = event
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, end)
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
        notify_user: bool = True
    ) -> bool:
        """Moves to the previous word."""

        tokens = ["CARET NAVIGATOR: previous_word. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.previous_context(skip_space=True)
        if obj is None:
            return False

        contents = script.utilities.get_word_contents_at_offset(obj, offset)
        if not contents:
            return False

        obj, start = contents[0][0], contents[0][1]
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
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
        notify_user: bool = True
    ) -> bool:
        """Moves to the next line."""

        tokens = ["CARET NAVIGATOR: next_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if focus_manager.get_manager().in_say_all() and \
           say_all_presenter.get_presenter().get_rewind_and_fast_forward_enabled():
            msg = "CARET NAVIGATOR: In say all and rewind/fast-forward is enabled"
            debug.print_message(debug.LEVEL_INFO, msg)
            return True

        obj, offset = script.utilities.get_caret_context()
        if obj is None:
            return False

        # We get the current line in order to set the last object on the line as the prior object,
        # so that we don't re-announce context.
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        contents = script.utilities.get_next_line_contents()
        if not contents:
            return False

        obj, start = contents[0][0], contents[0][1]
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
        if not notify_user:
            return True

        script.speak_contents(contents, priorObj=line[-1][0])
        script.display_contents(contents)
        return True

    @dbus_service.command
    def previous_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the previous line."""

        tokens = ["CARET NAVIGATOR: previous_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if focus_manager.get_manager().in_say_all() and \
           say_all_presenter.get_presenter().get_rewind_and_fast_forward_enabled():
            msg = "CARET NAVIGATOR: In say all and rewind/fast-forward is enabled"
            debug.print_message(debug.LEVEL_INFO, msg)
            return True

        obj, offset = script.utilities.get_caret_context()
        if obj is None:
            return False

        contents = script.utilities.get_previous_line_contents(obj, offset)
        if not contents:
            return False

        obj, start = contents[0][0], contents[0][1]
        if not self._is_navigable_object(script, obj):
            return False

        self._last_input_event = event
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
        if not notify_user:
            return True

        script.speak_contents(contents)
        script.display_contents(contents)
        return True

    @dbus_service.command
    def start_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the start of the line."""

        tokens = ["CARET NAVIGATOR: start_of_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        self._last_input_event = event
        obj, start = line[0][0], line[0][1]
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, start)
        if not notify_user:
            return True

        script.say_character(obj)
        script.display_contents(line)
        return True

    @dbus_service.command
    def end_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the end of the line."""

        tokens = ["CARET NAVIGATOR: end_of_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        obj, end, string = line[-1][0], line[-1][2], line[-1][3]
        if string.strip() and string[-1].isspace():
            end -= 1

        self._last_input_event = event
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, end)
        if not notify_user:
            return True

        script.say_character(obj)
        script.display_contents(line)
        return True

    @dbus_service.command
    def start_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the start of the file."""

        tokens = ["CARET NAVIGATOR: start_of_file. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        root = self._get_root_object(script)
        obj, offset = script.utilities.first_context(root, 0)
        if obj is None:
            return False

        while obj:
            prev_obj, prev_offset = script.utilities.previous_context(obj, offset, restrict_to=root)
            if prev_obj is None or (prev_obj, prev_offset) == (obj, offset):
                break
            obj, offset = prev_obj, prev_offset

        contents = script.utilities.get_line_contents_at_offset(obj, offset)
        if not contents:
            return False

        self._last_input_event = event
        obj, offset = contents[0][0], contents[0][1]
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, offset)
        if not notify_user:
            return True

        script.speak_contents(contents)
        script.display_contents(contents)
        return True

    @dbus_service.command
    def end_of_file(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the end of the file."""

        tokens = ["CARET NAVIGATOR: end_of_file. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        root = self._get_root_object(script)
        obj = AXObject.find_deepest_descendant(root)
        if obj is None:
            return False

        tokens = ["CARET NAVIGATOR: Last object in", root, "is", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        offset = max(0, AXText.get_character_count(obj) - 1)
        while obj:
            last_obj, last_offset = script.utilities.next_context(obj, offset, restrict_to=root)
            if last_obj is None or (last_obj, last_offset) == (obj, offset):
                break
            obj, offset = last_obj, last_offset

        contents = script.utilities.get_line_contents_at_offset(obj, offset)
        if not contents:
            return False

        self._last_input_event = event
        obj, offset = contents[-1][0], contents[-1][2]
        script.interrupt_presentation()
        script.utilities.set_caret_position(obj, offset)
        if not notify_user:
            return True

        script.speak_contents(contents)
        script.display_contents(contents)
        return True

_navigator = CaretNavigator()
def get_navigator() -> CaretNavigator:
    """Returns the Caret Navigator."""

    return _navigator
