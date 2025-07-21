# Orca
#
# Copyright 2013-2015 Igalia, S.L.
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

"""Provides an Orca-controlled caret for text content."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2013-2015 Igalia, S.L."
__license__ = "LGPL"

from typing import TYPE_CHECKING

from . import cmdnames
from . import debug
from . import focus_manager
from . import input_event
from . import input_event_manager
from . import keybindings
from . import messages
from . import settings_manager
from .ax_object import AXObject
from .ax_text import AXText

if TYPE_CHECKING:
    from .input_event import InputEvent
    from .scripts import web

class CaretNavigation:
    """Implements the caret navigation support available to scripts."""

    def __init__(self) -> None:
        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended: bool = False
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._last_input_event: input_event.InputEvent | None = None

    def handles_navigation(self, handler: input_event.InputEventHandler) -> bool:
        """Returns True if handler is a navigation command."""

        if handler not in self._handlers.values():
            return False

        if handler.function is self.toggle_enabled:
            return False

        return True

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the caret-navigation keybindings."""

        if refresh:
            msg = f"CARET NAVIGATION: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("CARET NAVIGATION: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the caret-navigation handlers."""

        if refresh:
            msg = "CARET NAVIGATION: Refreshing handlers."
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

        enabled = settings_manager.get_manager().get_setting('caretNavigationEnabled') \
            and not self._suspended

        self._handlers["next_character"] = \
            input_event.InputEventHandler(
                self._next_character,
                cmdnames.CARET_NAVIGATION_NEXT_CHAR,
                enabled = enabled)

        self._handlers["previous_character"] = \
            input_event.InputEventHandler(
                self._previous_character,
                cmdnames.CARET_NAVIGATION_PREV_CHAR,
                enabled = enabled)

        self._handlers["next_word"] = \
            input_event.InputEventHandler(
                self._next_word,
                cmdnames.CARET_NAVIGATION_NEXT_WORD,
                enabled = enabled)

        self._handlers["previous_word"] = \
            input_event.InputEventHandler(
                self._previous_word,
                cmdnames.CARET_NAVIGATION_PREV_WORD,
                enabled = enabled)

        self._handlers["next_line"] = \
            input_event.InputEventHandler(
                self._next_line,
                cmdnames.CARET_NAVIGATION_NEXT_LINE,
                enabled = enabled)

        self._handlers["previous_line"] = \
            input_event.InputEventHandler(
                self._previous_line,
                cmdnames.CARET_NAVIGATION_PREV_LINE,
                enabled = enabled)

        self._handlers["start_of_file"] = \
            input_event.InputEventHandler(
                self._start_of_file,
                cmdnames.CARET_NAVIGATION_FILE_START,
                enabled = enabled)

        self._handlers["end_of_file"] = \
            input_event.InputEventHandler(
                self._end_of_file,
                cmdnames.CARET_NAVIGATION_FILE_END,
                enabled = enabled)

        self._handlers["start_of_line"] = \
            input_event.InputEventHandler(
                self._start_of_line,
                cmdnames.CARET_NAVIGATION_LINE_START,
                enabled = enabled)

        self._handlers["end_of_line"] = \
            input_event.InputEventHandler(
                self._end_of_line,
                cmdnames.CARET_NAVIGATION_LINE_END,
                enabled = enabled)

        msg = f"CARET NAVIGATION: Handlers set up. Suspended: {self._suspended}"
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

        enabled = settings_manager.get_manager().get_setting('caretNavigationEnabled') \
            and not self._suspended

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

        msg = f"CARET NAVIGATION: Bindings set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def last_input_event_was_navigation_command(self) -> bool:
        """Returns true if the last input event was a navigation command."""

        manager = input_event_manager.get_manager()
        result = manager.last_event_equals_or_is_release_for_event(self._last_input_event)
        if self._last_input_event is not None:
            string = self._last_input_event.as_single_line_string()
        else:
            string = "None"

        msg = f"CARET NAVIGATION: Last navigation event ({string}) is last key event: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def refresh_bindings_and_grabs(self, script: web.Script, reason: str = "") -> None:
        """Refreshes caret navigation bindings and grabs for script."""

        msg = "CARET NAVIGATION: Refreshing bindings and grabs"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.remove(binding, include_grabs=True)

        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.add(binding, include_grabs=not self._suspended)

    def toggle_enabled(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Toggles caret navigation."""

        if not event:
            return False

        _settings_manager = settings_manager.get_manager()
        enabled = not _settings_manager.get_setting('caretNavigationEnabled')
        if enabled:
            string = messages.CARET_CONTROL_ORCA
        else:
            string = messages.CARET_CONTROL_APP

        script.present_message(string)
        _settings_manager.set_setting('caretNavigationEnabled', enabled)
        self._last_input_event = None
        self.refresh_bindings_and_grabs(script, "toggling caret navigation")
        return True

    def suspend_commands(self, script: web.Script, suspended: bool, reason: str = "") -> None:
        """Suspends caret navigation independent of the enabled setting."""

        if suspended == self._suspended:
            return

        msg = f"CARET NAVIGATION: Commands suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._suspended = suspended
        self.refresh_bindings_and_grabs(script, f"Suspended changed to {suspended}")

    def _next_character(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the next character."""

        if not event:
            return False

        obj, offset = script.utilities.next_context()
        if not obj:
            return False

        self._last_input_event = event
        script.utilities.set_caret_position(obj, offset)
        script.interrupt_presentation()
        script.update_braille(obj)
        script.say_character(obj)
        return True

    def _previous_character(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the previous character."""

        if not event:
            return False

        obj, offset = script.utilities.previous_context()
        if not obj:
            return False

        self._last_input_event = event
        script.utilities.set_caret_position(obj, offset)
        script.interrupt_presentation()
        script.update_braille(obj)
        script.say_character(obj)
        return True

    def _next_word(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the next word."""

        if not event:
            return False

        obj, offset = script.utilities.next_context(skip_space=True)
        contents = script.utilities.get_word_contents_at_offset(obj, offset)
        if not contents:
            return False

        # If the "word" to the right consists of the content of the last word in an embedded
        # object followed by the space of the parent object, the normal space-adjustment we
        # do will cause us to set the caret to the offset with the embedded child and then
        # present the first word in that child.
        if len(contents) > 1 and contents[-1][3].isspace():
            msg = "CARET NAVIGATION: Adjusting next word contents to eliminate trailing space."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            contents = contents[:-1]

        obj, end, string = contents[-1][0], contents[-1][2], contents[-1][3]
        if string and string[-1].isspace():
            end -= 1

        self._last_input_event = event
        script.utilities.set_caret_position(obj, end)
        script.interrupt_presentation()
        script.update_braille(obj)
        script.say_word(obj)
        return True

    def _previous_word(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the previous word."""

        if not event:
            return False

        obj, offset = script.utilities.previous_context(skip_space=True)
        contents = script.utilities.get_word_contents_at_offset(obj, offset)
        if not contents:
            return False

        self._last_input_event = event
        obj, start = contents[0][0], contents[0][1]
        script.utilities.set_caret_position(obj, start)
        script.interrupt_presentation()
        script.update_braille(obj)
        script.say_word(obj)
        return True

    def _next_line(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the next line."""

        if not event:
            return False

        if focus_manager.get_manager().in_say_all():
            _settings_manager = settings_manager.get_manager()
            if _settings_manager.get_setting("rewindAndFastForwardInSayAll"):
                msg = "CARET NAVIGATION: In say all and rewind/fast-forward is enabled"
                debug.print_message(debug.LEVEL_INFO, msg)
                return True

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        contents = script.utilities.get_next_line_contents()
        if not contents:
            return False

        self._last_input_event = event
        obj, start = contents[0][0], contents[0][1]
        script.utilities.set_caret_position(obj, start)
        script.interrupt_presentation()
        script.speakContents(contents, priorObj=line[-1][0])
        script.displayContents(contents)
        return True

    def _previous_line(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the previous line."""

        if not event:
            return False

        if focus_manager.get_manager().in_say_all():
            _settings_manager = settings_manager.get_manager()
            if _settings_manager.get_setting("rewindAndFastForwardInSayAll"):
                msg = "CARET NAVIGATION: In say all and rewind/fast-forward is enabled"
                debug.print_message(debug.LEVEL_INFO, msg)
                return True

        contents = script.utilities.get_previous_line_contents()
        if not contents:
            return False

        self._last_input_event = event
        obj, start = contents[0][0], contents[0][1]
        script.utilities.set_caret_position(obj, start)
        script.interrupt_presentation()
        script.speakContents(contents)
        script.displayContents(contents)
        return True

    def _start_of_line(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the start of the line."""

        if not event:
            return False

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        self._last_input_event = event
        obj, start = line[0][0], line[0][1]
        script.utilities.set_caret_position(obj, start)
        script.interrupt_presentation()
        script.say_character(obj)
        script.displayContents(line)
        return True

    def _end_of_line(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the end of the line."""

        if not event:
            return False

        obj, offset = script.utilities.get_caret_context()
        line = script.utilities.get_line_contents_at_offset(obj, offset)
        if not (line and line[0]):
            return False

        obj, end, string = line[-1][0], line[-1][2], line[-1][3]
        if string.strip() and string[-1].isspace():
            end -= 1

        self._last_input_event = event
        script.utilities.set_caret_position(obj, end)
        script.interrupt_presentation()
        script.say_character(obj)
        script.displayContents(line)
        return True

    def _start_of_file(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the start of the file."""

        if not event:
            return False

        document = script.utilities.documentFrame()
        obj, offset = script.utilities.first_context(document, 0)
        contents = script.utilities.get_line_contents_at_offset(obj, offset)
        if not contents:
            return False

        self._last_input_event = event
        obj, offset = contents[0][0], contents[0][1]
        script.utilities.set_caret_position(obj, offset)
        script.interrupt_presentation()
        script.speakContents(contents)
        script.displayContents(contents)
        return True

    def _end_of_file(self, script: web.Script, event: InputEvent | None = None) -> bool:
        """Moves to the end of the file."""

        if not event:
            return False

        document = script.utilities.documentFrame()
        tokens = ["CARET NAVIGATION: Go to end of", document]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = AXObject.find_deepest_descendant(document)
        tokens = ["CARET NAVIGATION: Last object in", document, "is", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        offset = max(0, AXText.get_character_count(obj) - 1)
        while obj:
            last_obj, last_offset = script.utilities.next_context(obj, offset)
            if not last_obj:
                break
            obj, offset = last_obj, last_offset

        contents = script.utilities.get_line_contents_at_offset(obj, offset)
        if not contents:
            return False

        self._last_input_event = event
        obj, offset = contents[-1][0], contents[-1][2]
        script.utilities.set_caret_position(obj, offset)
        script.interrupt_presentation()
        script.speakContents(contents)
        script.displayContents(contents)
        return True
