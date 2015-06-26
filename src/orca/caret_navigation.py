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

__id__ = "$Id$"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2013-2015 Igalia, S.L."
__license__ = "LGPL"

from . import cmdnames
from . import debug
from . import input_event
from . import keybindings
from . import messages
from . import settings_manager


class CaretNavigation:
    """Implements the caret navigation support available to scripts."""

    def __init__(self, script):
        if not (script and script.app):
            msg = "INFO: Caret navigation requires a script and app."
            debug.println(debug.LEVEL_INFO, msg)

        self._script = script
        self._handlers = self._setup_handlers()
        self._bindings = self._setup_bindings()

    def handles_navigation(self, handler):
        """Returns True if handler is a navigation command."""

        if not handler in self._handlers.values():
            return False

        if handler.function == self._toggle_enabled:
            return False

        return True

    def get_bindings(self):
        """Returns the caret-navigation keybindings."""

        return self._bindings

    def get_handlers(self):
        """Returns the caret-navigation handlers."""

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the caret-navigation input event handlers."""

        handlers = {}

        if not (self._script and self._script.app):
            return handlers

        handlers["toggle_enabled"] = \
            input_event.InputEventHandler(
                self._toggle_enabled,
                cmdnames.CARET_NAVIGATION_TOGGLE)

        handlers["next_character"] = \
            input_event.InputEventHandler(
                self._next_character,
                cmdnames.CARET_NAVIGATION_NEXT_CHAR)

        handlers["previous_character"] = \
            input_event.InputEventHandler(
                self._previous_character,
                cmdnames.CARET_NAVIGATION_PREV_CHAR)

        handlers["next_word"] = \
            input_event.InputEventHandler(
                self._next_word,
                cmdnames.CARET_NAVIGATION_NEXT_WORD)

        handlers["previous_word"] = \
            input_event.InputEventHandler(
                self._previous_word,
                cmdnames.CARET_NAVIGATION_PREV_WORD)

        handlers["next_line"] = \
            input_event.InputEventHandler(
                self._next_line,
                cmdnames.CARET_NAVIGATION_NEXT_LINE)

        handlers["previous_line"] = \
            input_event.InputEventHandler(
                self._previous_line,
                cmdnames.CARET_NAVIGATION_PREV_LINE)

        handlers["start_of_file"] = \
            input_event.InputEventHandler(
                self._start_of_file,
                cmdnames.CARET_NAVIGATION_FILE_START)

        handlers["end_of_file"] = \
            input_event.InputEventHandler(
                self._end_of_file,
                cmdnames.CARET_NAVIGATION_FILE_END)

        handlers["start_of_line"] = \
            input_event.InputEventHandler(
                self._start_of_line,
                cmdnames.CARET_NAVIGATION_LINE_START)

        handlers["end_of_line"] = \
            input_event.InputEventHandler(
                self._end_of_line,
                cmdnames.CARET_NAVIGATION_LINE_END)

        return handlers

    def _setup_bindings(self):
        """Sets up and returns the caret-navigation key bindings."""

        bindings = keybindings.KeyBindings()

        if not (self._script and self._script.app):
            return bindings

        bindings.add(
            keybindings.KeyBinding(
                "F12",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("toggle_enabled")))

        bindings.add(
            keybindings.KeyBinding(
                "Right",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("next_character")))

        bindings.add(
            keybindings.KeyBinding(
                "Left",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("previous_character")))

        bindings.add(
            keybindings.KeyBinding(
                "Right",
                keybindings.defaultModifierMask,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers.get("next_word")))

        bindings.add(
            keybindings.KeyBinding(
                "Left",
                keybindings.defaultModifierMask,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers.get("previous_word")))

        bindings.add(
            keybindings.KeyBinding(
                "Down",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("next_line")))

        bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("previous_line")))

        bindings.add(
            keybindings.KeyBinding(
                "End",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("end_of_line")))

        bindings.add(
            keybindings.KeyBinding(
                "Home",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("start_of_line")))

        bindings.add(
            keybindings.KeyBinding(
                "End",
                keybindings.defaultModifierMask,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers.get("end_of_file")))

        bindings.add(
            keybindings.KeyBinding(
                "Home",
                keybindings.defaultModifierMask,
                keybindings.CTRL_MODIFIER_MASK,
                self._handlers.get("start_of_file")))

        return bindings

    @staticmethod
    def _toggle_enabled(script, event):
        """Toggles caret navigation."""

        if not event:
            return False

        _settings_manager = settings_manager.getManager()
        enabled = not _settings_manager.getSetting('caretNavigationEnabled')
        if enabled:
            string = messages.CARET_CONTROL_ORCA
        else:
            string = messages.CARET_CONTROL_APP

        script.presentMessage(string)
        _settings_manager.setSetting('caretNavigationEnabled', enabled)
        return True

    @staticmethod
    def _next_character(script, event):
        """Moves to the next character."""

        if not event:
            return False

        obj, offset = script.utilities.nextContext()
        if not obj:
            return False

        script.utilities.setCaretPosition(obj, offset)
        script.updateBraille(obj)
        script.sayCharacter(obj)
        return True

    @staticmethod
    def _previous_character(script, event):
        """Moves to the previous character."""

        if not event:
            return False

        obj, offset = script.utilities.previousContext()
        if not obj:
            return False

        script.utilities.setCaretPosition(obj, offset)
        script.updateBraille(obj)
        script.sayCharacter(obj)
        return True

    @staticmethod
    def _next_word(script, event):
        """Moves to the next word."""

        if not event:
            return False

        obj, offset = script.utilities.nextContext(skipSpace=True)
        contents = script.utilities.getWordContentsAtOffset(obj, offset)
        if not contents:
            return False

        obj, end, string = contents[-1][0], contents[-1][2], contents[-1][3]
        if string and not string[-1].isalnum():
            end -= 1

        script.utilities.setCaretPosition(obj, end)
        script.updateBraille(obj)
        script.sayWord(obj)
        return True

    @staticmethod
    def _previous_word(script, event):
        """Moves to the previous word."""

        if not event:
            return False

        obj, offset = script.utilities.previousContext(skipSpace=True)
        contents = script.utilities.getWordContentsAtOffset(obj, offset)
        if not contents:
            return False

        obj, start = contents[0][0], contents[0][1]
        script.utilities.setCaretPosition(obj, start)
        script.updateBraille(obj)
        script.sayWord(obj)
        return True

    @staticmethod
    def _next_line(script, event):
        """Moves to the next line."""

        if not event:
            return False

        if script.inSayAll():
            _settings_manager = settings_manager.getManager()
            if _settings_manager.getSetting('rewindAndFastForwardInSayAll'):
                msg = "INFO: inSayAll and rewindAndFastforwardInSayAll is enabled"
                debug.println(debug.LEVEL_INFO, msg)
                return True

        contents = script.utilities.getNextLineContents()
        if not contents:
            return False

        obj, start = contents[0][0], contents[0][1]
        script.utilities.setCaretPosition(obj, start)
        script.speakContents(contents)
        script.displayContents(contents)
        return True

    @staticmethod
    def _previous_line(script, event):
        """Moves to the previous line."""

        if not event:
            return False

        if script.inSayAll():
            _settings_manager = settings_manager.getManager()
            if _settings_manager.getSetting('rewindAndFastForwardInSayAll'):
                msg = "INFO: inSayAll and rewindAndFastforwardInSayAll is enabled"
                debug.println(debug.LEVEL_INFO, msg)
                return True


        contents = script.utilities.getPreviousLineContents()
        if not contents:
            return False

        obj, start = contents[0][0], contents[0][1]
        script.utilities.setCaretPosition(obj, start)
        script.speakContents(contents)
        script.displayContents(contents)
        return True

    @staticmethod
    def _start_of_line(script, event):
        """Moves to the start of the line."""

        if not event:
            return False

        obj, offset = script.utilities.getCaretContext()
        line = script.utilities.getLineContentsAtOffset(obj, offset)
        if not (line and line[0]):
            return False

        obj, start = line[0][0], line[0][1]
        script.utilities.setCaretPosition(obj, start)
        script.sayCharacter(obj)
        script.displayContents(line)
        return True

    @staticmethod
    def _end_of_line(script, event):
        """Moves to the end of the line."""

        if not event:
            return False

        obj, offset = script.utilities.getCaretContext()
        line = script.utilities.getLineContentsAtOffset(obj, offset)
        if not (line and line[0]):
            return False

        obj, end, string = line[-1][0], line[-1][2], line[-1][3]
        if string.strip() and string[-1].isspace():
            end -= 1

        script.utilities.setCaretPosition(obj, end)
        script.sayCharacter(obj)
        script.displayContents(line)
        return True

    @staticmethod
    def _start_of_file(script, event):
        """Moves to the start of the file."""

        if not event:
            return False

        document = script.utilities.documentFrame()
        obj, offset = script.utilities.findFirstCaretContext(document, 0)
        contents = script.utilities.getLineContentsAtOffset(obj, offset)
        if not contents:
            return False

        obj, offset = contents[0][0], contents[0][1]
        script.utilities.setCaretPosition(obj, offset)
        script.speakContents(contents)
        script.displayContents(contents)
        return True

    @staticmethod
    def _end_of_file(script, event):
        """Moves to the end of the file."""

        if not event:
            return False

        document = script.utilities.documentFrame()
        obj = script.utilities.getLastObjectInDocument(document)
        offset = 0
        text = script.utilities.queryNonEmptyText(obj)
        if text:
            offset = text.characterCount - 1

        while obj:
            lastobj, lastoffset = script.utilities.nextContext(obj, offset)
            if not lastobj:
                break
            obj, offset = lastobj, lastoffset

        contents = script.utilities.getLineContentsAtOffset(obj, offset)
        if not contents:
            return False

        obj, offset = contents[-1][0], contents[-1][2]
        script.utilities.setCaretPosition(obj, offset)
        script.speakContents(contents)
        script.displayContents(contents)
        return True
