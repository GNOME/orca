# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2023 Igalia, S.L.
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

"""Module for flat-review commands"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import braille
from . import cmdnames
from . import debug
from . import flat_review
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import orca
from . import orca_state
from . import settings_manager
from . import settings

_settingsManager = settings_manager.getManager()

class FlatReviewPresenter:
    """Provides access to on-screen objects via flat-review."""

    def __init__(self):
        self._context = None
        self._current_contents = ""
        self._restrict = False
        self._handlers = self._setup_handlers()
        self._desktop_bindings = self._setup_desktop_bindings()
        self._laptop_bindings = self._setup_laptop_bindings()
        self._gui = None

    def is_active(self):
        """Returns True if the flat review presenter is active."""

        return self._context is not None

    def get_or_create_context(self, script=None):
        """Returns the flat review context, creating one if necessary."""

        # TODO - JD: Scripts should not be able to interact with the
        # context directly. get_or_create_context is public temporarily
        # to prevent breakage.

        if not self._context:
            msg = "FLAT REVIEW PRESENTER: Creating new context"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            if self._restrict:
                mode, obj = orca.getActiveModeAndObjectOfInterest()
                self._context = flat_review.Context(script, root=obj)
            else:
                self._context = flat_review.Context(script)

            orca.emitRegionChanged(self._context.getCurrentAccessible(), mode=orca.FLAT_REVIEW)
            if script is not None:
                script.justEnteredFlatReviewMode = True
                script.targetCursorCell = script.getBrailleCursorCell()
            return self._context

        msg = "FLAT REVIEW PRESENTER: Using existing context"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # If we are in unrestricted mode, update the context as below.
        # If the context already exists, but the active mode is not flat review, update
        # the flat review location to that of the object of interest -- if the object of
        # interest is in the flat review context (which means it's on screen). In some
        # cases the object of interest will not be in the flat review context because it
        # is represented by descendant text objects. setCurrentToZoneWithObject checks
        # for this condition and if it can find a zone whose ancestor is the object of
        # interest, it will set the current zone to the descendant, causing Orca to
        # present the text at the location of the object of interest.
        mode, obj = orca.getActiveModeAndObjectOfInterest()
        obj = obj or orca_state.locusOfFocus
        if mode != orca.FLAT_REVIEW and obj != self._context.getCurrentAccessible() \
           and not self._restrict:
            tokens = ["FLAT REVIEW PRESENTER: Attempting to update location from",
                      self._context.getCurrentAccessible(), "to", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self._context.setCurrentToZoneWithObject(obj)

        # If we are restricting, and the current mode is not flat review, calculate a new context
        if self._restrict and mode != orca.FLAT_REVIEW:
            msg = "FLAT REVIEW PRESENTER: Creating new restricted context."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._context = flat_review.Context(script, obj)

        return self._context

    def get_bindings(self, is_desktop):
        """Returns the flat-review-presenter keybindings."""

        if is_desktop:
            return self._desktop_bindings
        return self._laptop_bindings

    def get_braille_bindings(self):
        """Returns the flat-review-presenter braille bindings."""

        bindings = {}
        try:
            bindings[braille.brlapi.KEY_CMD_LNUP] = \
                self._handlers.get("reviewAboveHandler")
            bindings[braille.brlapi.KEY_CMD_LNDN] = \
                self._handlers.get("reviewBelowHandler")
            bindings[braille.brlapi.KEY_CMD_FREEZE] = \
                self._handlers.get("toggleFlatReviewModeHandler")
            bindings[braille.brlapi.KEY_CMD_TOP_LEFT] = \
                self._handlers.get("reviewHomeHandler")
            bindings[braille.brlapi.KEY_CMD_BOT_LEFT] = \
                self._handlers.get("reviewBottomLeftHandler")
        except Exception as error:
            tokens = ["FLAT REVIEW PRESENTER: Exception getting braille bindings:", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return {}
        return bindings

    def get_handlers(self):
        """Returns the flat-review-presenter handlers."""

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the flat-review-presenter input event handlers."""

        handlers = {}

        handlers["toggleFlatReviewModeHandler"] = \
            input_event.InputEventHandler(
                self.toggle_flat_review_mode,
                cmdnames.TOGGLE_FLAT_REVIEW)

        handlers["reviewHomeHandler"] = \
            input_event.InputEventHandler(
                self.go_home,
                cmdnames.REVIEW_HOME)

        handlers["reviewEndHandler"] = \
            input_event.InputEventHandler(
                self.go_end,
                cmdnames.REVIEW_END)

        handlers["reviewBottomLeftHandler"] = \
            input_event.InputEventHandler(
                self.go_bottom_left,
                cmdnames.REVIEW_BOTTOM_LEFT)

        handlers["reviewPreviousLineHandler"] = \
            input_event.InputEventHandler(
                self.go_previous_line,
                cmdnames.REVIEW_PREVIOUS_LINE)

        handlers["reviewCurrentLineHandler"] = \
            input_event.InputEventHandler(
                self.present_line,
                cmdnames.REVIEW_CURRENT_LINE)

        handlers["reviewNextLineHandler"] = \
            input_event.InputEventHandler(
                self.go_next_line,
                cmdnames.REVIEW_NEXT_LINE)

        handlers["reviewSpellCurrentLineHandler"] = \
            input_event.InputEventHandler(
                self.spell_line,
                cmdnames.REVIEW_SPELL_CURRENT_LINE)

        handlers["reviewPhoneticCurrentLineHandler"] = \
            input_event.InputEventHandler(
                self.phonetic_line,
                cmdnames.REVIEW_PHONETIC_CURRENT_LINE)

        handlers["reviewEndOfLineHandler"] = \
            input_event.InputEventHandler(
                self.go_end_of_line,
                cmdnames.REVIEW_END_OF_LINE)

        handlers["reviewPreviousItemHandler"] = \
            input_event.InputEventHandler(
                self.go_previous_item,
                cmdnames.REVIEW_PREVIOUS_ITEM)

        handlers["reviewCurrentItemHandler"] = \
            input_event.InputEventHandler(
                self.present_item,
                cmdnames.REVIEW_CURRENT_ITEM)

        handlers["reviewNextItemHandler"] = \
            input_event.InputEventHandler(
                self.go_next_item,
                cmdnames.REVIEW_NEXT_ITEM)

        handlers["reviewSpellCurrentItemHandler"] = \
            input_event.InputEventHandler(
                self.spell_item,
                cmdnames.REVIEW_SPELL_CURRENT_ITEM)

        handlers["reviewPhoneticCurrentItemHandler"] = \
            input_event.InputEventHandler(
                self.phonetic_item,
                cmdnames.REVIEW_PHONETIC_CURRENT_ITEM)

        handlers["reviewPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                self.go_previous_character,
                cmdnames.REVIEW_PREVIOUS_CHARACTER)

        handlers["reviewCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                self.present_character,
                cmdnames.REVIEW_CURRENT_CHARACTER)

        handlers["reviewSpellCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                self.spell_character,
                cmdnames.REVIEW_SPELL_CURRENT_CHARACTER)

        handlers["reviewUnicodeCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                self.unicode_current_character,
                cmdnames.REVIEW_UNICODE_CURRENT_CHARACTER)

        handlers["reviewNextCharacterHandler"] = \
            input_event.InputEventHandler(
                self.go_next_character,
                cmdnames.REVIEW_NEXT_CHARACTER)

        handlers["reviewCurrentAccessibleHandler"] = \
            input_event.InputEventHandler(
                self.present_object,
                cmdnames.REVIEW_CURRENT_ACCESSIBLE)

        handlers["reviewAboveHandler"] = \
            input_event.InputEventHandler(
                self.go_above,
                cmdnames.REVIEW_ABOVE)

        handlers["reviewBelowHandler"] = \
            input_event.InputEventHandler(
                self.go_below,
                cmdnames.REVIEW_BELOW)

        handlers["showContentsHandler"] = \
            input_event.InputEventHandler(
                self.show_contents,
                cmdnames.FLAT_REVIEW_SHOW_CONTENTS)

        handlers["flatReviewCopyHandler"] = \
            input_event.InputEventHandler(
                self.copy_to_clipboard,
                cmdnames.FLAT_REVIEW_COPY)

        handlers["flatReviewAppendHandler"] = \
            input_event.InputEventHandler(
                self.append_to_clipboard,
                cmdnames.FLAT_REVIEW_APPEND)

        handlers["flatReviewSayAllHandler"] = \
            input_event.InputEventHandler(
                self.say_all,
                cmdnames.SAY_ALL_FLAT_REVIEW)

        handlers["flatReviewToggleRestrictHandler"] = \
            input_event.InputEventHandler(
                self.toggle_restrict,
                cmdnames.TOGGLE_RESTRICT_FLAT_REVIEW)

        return handlers

    def _setup_desktop_bindings(self):
        """Sets up and returns the flat-review-presenter desktop key bindings."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "KP_Subtract",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("toggleFlatReviewModeHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewSayAllHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewHomeHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPreviousLineHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewCurrentLineHandler"),
                1))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentLineHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentLineHandler"),
                3))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewNextLineHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewEndHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPreviousItemHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewAboveHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewCurrentItemHandler"),
                1))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentItemHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentItemHandler"),
                3))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentAccessibleHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewNextItemHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewBelowHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_End",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPreviousCharacterHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_End",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewEndOfLineHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewCurrentCharacterHandler"),
                1))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentCharacterHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewUnicodeCurrentCharacterHandler"),
                3))

        bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Down",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewNextCharacterHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("showContentsHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewCopyHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewAppendHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewToggleRestrictHandler")))

        return bindings

    def _setup_laptop_bindings(self):
        """Sets up and returns the flat-review-presenter laptop key bindings."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "p",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("toggleFlatReviewModeHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "semicolon",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("flatReviewSayAllHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPreviousLineHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewHomeHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentLineHandler"),
                1))

        bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentLineHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentLineHandler"),
                3))

        bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewNextLineHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewEndHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "j",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPreviousItemHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "j",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewAboveHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentItemHandler"),
                1))

        bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentItemHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentItemHandler"),
                3))

        bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewCurrentAccessibleHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewNextItemHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewBelowHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPreviousCharacterHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewEndOfLineHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentCharacterHandler"),
                1))

        bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentCharacterHandler"),
                2))

        bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewUnicodeCurrentCharacterHandler"),
                3))

        bindings.add(
            keybindings.KeyBinding(
                "period",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewNextCharacterHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("showContentsHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewCopyHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewAppendHandler")))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewToggleRestrictHandler")))

        return bindings

    def start(self, script=None, event=None):
        """Starts flat review."""

        if self._context:
            msg = "FLAT REVIEW PRESENTER: Already in flat review"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        msg = "FLAT REVIEW PRESENTER: Starting flat review"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if script is None:
            script = orca_state.activeScript

        self.get_or_create_context(script)
        if event is None:
            return

        if _settingsManager.getSetting('speechVerbosityLevel') != settings.VERBOSITY_LEVEL_BRIEF:
            script.presentMessage(messages.FLAT_REVIEW_START)
        self._item_presentation(script, event, script.targetCursorCell)

    def quit(self, script=None, event=None):
        """Quits flat review."""

        if self._context is None:
            msg = "FLAT REVIEW PRESENTER: Not in flat review"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        msg = "FLAT REVIEW PRESENTER: Quitting flat review"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        self._context = None
        orca.emitRegionChanged(orca_state.locusOfFocus, mode=orca.FOCUS_TRACKING)

        if event is None or script is None:
            return

        if _settingsManager.getSetting('speechVerbosityLevel') != settings.VERBOSITY_LEVEL_BRIEF:
            script.presentMessage(messages.FLAT_REVIEW_STOP)
        script.updateBraille(orca_state.locusOfFocus)

    def toggle_flat_review_mode(self, script, event=None):
        """Toggles between flat review mode and focus tracking mode."""

        if self.is_active():
            self.quit(script, event)
            return True

        self.start(script, event)
        return True

    def go_home(self, script, event=None):
        """Moves to the top left of the current window."""

        self._context = self.get_or_create_context(script)
        self._context.goBegin(flat_review.Context.WINDOW)
        self.present_line(script, event)
        script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def go_end(self, script, event=None):
        """Moves to the bottom right of the current window."""

        self._context = self.get_or_create_context(script)
        self._context.goEnd(flat_review.Context.WINDOW)
        self.present_line(script, event)
        script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def go_bottom_left(self, script, event=None):
        """Moves to the bottom left of the current window."""

        self._context = self.get_or_create_context(script)
        self._context.goEnd(flat_review.Context.WINDOW)
        self._context.goBegin(flat_review.Context.LINE)
        self.present_line(script, event)
        script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def go_previous_line(self, script, event=None):
        """Moves to the previous line."""

        self._context = self.get_or_create_context(script)
        if self._context.goPrevious(flat_review.Context.LINE, flat_review.Context.WRAP_LINE):
            self.present_line(script, event)
            script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def present_line(self, script, event=None):
        """Presents the current line."""

        self._line_presentation(script, event, 1)
        return True

    def go_next_line(self, script, event=None):
        """Moves to the next line."""

        self._context = self.get_or_create_context(script)
        if self._context.goNext(flat_review.Context.LINE, flat_review.Context.WRAP_LINE):
            self.present_line(script, event)
            script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def spell_line(self, script, event=None):
        """Presents the current line letter by letter."""

        self._line_presentation(script, event, 2)
        return True

    def phonetic_line(self, script, event=None):
        """Presents the current line letter by letter phonetically."""

        self._line_presentation(script, event, 3)
        return True

    def go_start_of_line(self, script, event=None):
        """Moves to the beginning of the current line."""

        self._context = self.get_or_create_context(script)
        self._context.goEnd(flat_review.Context.LINE)
        self.present_character(script, event)
        script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def go_end_of_line(self, script, event=None):
        """Moves to the end of the line."""

        self._context = self.get_or_create_context(script)
        self._context.goEnd(flat_review.Context.LINE)
        self.present_character(script, event)
        script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def go_previous_item(self, script, event=None):
        """Moves to the previous item or word."""

        self._context = self.get_or_create_context(script)
        if self._context.goPrevious(flat_review.Context.WORD, flat_review.Context.WRAP_LINE):
            self.present_item(script, event)
            script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def present_item(self, script, event=None, target_cursor_cell=0):
        """Presents the current item/word."""

        self._item_presentation(script, event, target_cursor_cell, 1)
        return True

    def go_next_item(self, script, event=None):
        """Moves to the next item or word."""

        self._context = self.get_or_create_context(script)
        if self._context.goNext(flat_review.Context.WORD, flat_review.Context.WRAP_LINE):
            self.present_item(script, event)
            script.targetCursorCell = script.getBrailleCursorCell()

        return True

    def spell_item(self, script, event=None):
        """Presents the current item/word letter by letter."""

        self._item_presentation(script, event, script.targetCursorCell, 2)
        return True

    def phonetic_item(self, script, event=None):
        """Presents the current word letter by letter phonetically."""

        self._item_presentation(script, event, script.targetCursorCell, 3)
        return True

    def go_previous_character(self, script, event=None):
        """Moves to the previous character."""

        self._context = self.get_or_create_context(script)
        if self._context.goPrevious(flat_review.Context.CHAR, flat_review.Context.WRAP_LINE):
            self.present_character(script, event)
            script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def present_character(self, script, event=None):
        """Presents the current character."""

        self._character_presentation(script, event, 1)
        return True

    def go_next_character(self, script, event=None):
        """Moves to the next character."""

        self._context = self.get_or_create_context(script)
        if self._context.goNext(flat_review.Context.CHAR, flat_review.Context.WRAP_LINE):
            self.present_character(script, event)
            script.targetCursorCell = script.getBrailleCursorCell()
        return True

    def spell_character(self, script, event=None):
        """Presents the current character phonetically."""

        self._character_presentation(script, event, 2)
        return True

    def unicode_current_character(self, script, event=None):
        """Presents the current character's unicode value."""

        self._character_presentation(script, event, 3)
        return True

    def go_above(self, script, event=None):
        """Moves to the character above."""

        self._context = self.get_or_create_context(script)
        if self._context.goAbove(flat_review.Context.CHAR, flat_review.Context.WRAP_LINE):
            self.present_item(script, event, script.targetCursorCell)
        return True

    def go_below(self, script, event=None):
        """Moves to the character below."""

        self._context = self.get_or_create_context(script)
        if self._context.goBelow(flat_review.Context.CHAR, flat_review.Context.WRAP_LINE):
            self.present_item(script, event, script.targetCursorCell)
        return True

    def get_current_object(self, script, event=None):
        """Returns the current accessible object."""

        self._context = self.get_or_create_context(script)
        return self._context.getCurrentAccessible()

    def present_object(self, script, event=None):
        """Presents the current accessible object."""

        self._context = self.get_or_create_context(script)
        if not isinstance(event, input_event.BrailleEvent):
            script.presentObject(self._context.getCurrentAccessible(), speechonly=True)

        orca.emitRegionChanged(self._context.getCurrentAccessible(), mode=orca.FLAT_REVIEW)
        return True

    def left_click_on_object(self, script, event=None):
        """Attempts to synthesize a left click on the current accessible."""

        self._context = self.get_or_create_context(script)
        return self._context.clickCurrent(1)

    def right_click_on_object(self, script, event=None):
        """Attempts to synthesize a left click on the current accessible."""

        self._context = self.get_or_create_context(script)
        return self._context.clickCurrent(3)

    def route_pointer_to_object(self, script, event=None):
        """Routes the mouse pointer to the current accessible."""

        self._context = self.get_or_create_context(script)
        return self._context.routeToCurrent()

    def get_braille_regions(self, script, event=None):
        """Returns the braille regions and region with focus being reviewed."""

        self._context = self.get_or_create_context(script)
        regions, focused_region = self._context.getCurrentBrailleRegions()
        return [regions, focused_region]

    def _get_all_lines(self, script, event=None):
        """Returns a list of textual lines representing the contents."""

        lines = []
        self._context = self.get_or_create_context(script)
        self._context.goBegin(flat_review.Context.WINDOW)
        string = self._context.getCurrent(flat_review.Context.LINE)[0]
        while string is not None:
            lines.append(string.rstrip("\n"))
            if not self._context.goNext(flat_review.Context.LINE, flat_review.Context.WRAP_LINE):
                break
            string = self._context.getCurrent(flat_review.Context.LINE)[0]
        return lines

    def say_all(self, script, event=None):
        """Speaks the contents of the entire window."""

        for string in self._get_all_lines(script, event):
            if not string.isspace():
                script.speakMessage(string, script.speechGenerator.voice(string=string))

        return True

    def show_contents(self, script, event=None):
        """Displays the entire flat review contents in a text view."""

        msg = "FLAT REVIEW PRESENTER: Showing contents."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        text = "\n".join(self._get_all_lines(script, event))
        title = guilabels.FLAT_REVIEW_CONTENTS
        self._gui = FlatReviewContextGUI(script, title, text)
        self._gui.show_gui()
        return True

    def copy_to_clipboard(self, script, event=None):
        """Copies the string just presented to the clipboard."""

        if not self.is_active():
            script.presentMessage(messages.FLAT_REVIEW_NOT_IN)
            return True

        script.utilities.setClipboardText(self._current_contents.rstrip("\n"))
        script.presentMessage(messages.FLAT_REVIEW_COPIED)
        return True

    def append_to_clipboard(self, script, event=None):
        """Appends the string just presented to the clipboard."""

        if not self.is_active():
            script.presentMessage(messages.FLAT_REVIEW_NOT_IN)
            return True

        script.utilities.appendTextToClipboard(self._current_contents.rstrip("\n"))
        script.presentMessage(messages.FLAT_REVIEW_APPENDED)
        return True

    def toggle_restrict(self, script, event=None):
        """ Toggles the restricting of flat review to the current object. """


        self._restrict = not self._restrict
        if self._restrict:
            script.presentMessage(messages.FLAT_REVIEW_RESTRICTED)
        else:
            script.presentMessage(messages.FLAT_REVIEW_UNRESTRICTED)
        if self.is_active():
            # Reset the context
            self._context = None
            self.start()

        return True

    def _line_presentation(self, script, event, speech_type=1):
        """Presents the current line."""

        self._context = self.get_or_create_context(script)
        line_string = self._context.getCurrent(flat_review.Context.LINE)[0] or ""
        voice = script.speechGenerator.voice(string=line_string)

        if not isinstance(event, input_event.BrailleEvent):
            if not line_string or line_string == "\n":
                script.speakMessage(messages.BLANK)
            elif line_string.isspace():
                script.speakMessage(messages.WHITE_SPACE)
            elif line_string.isupper() and (speech_type < 2 or speech_type > 3):
                script.speakMessage(line_string, voice)
            elif speech_type == 2:
                script.spellCurrentItem(line_string)
            elif speech_type == 3:
                script.phoneticSpellCurrentItem(line_string)
            else:
                line_string = script.utilities.adjustForRepeats(line_string)
                script.speakMessage(line_string, voice)

        orca.emitRegionChanged(self._context.getCurrentAccessible(), mode=orca.FLAT_REVIEW)
        script.updateBrailleReview()
        self._current_contents = line_string
        return True

    def _item_presentation(self, script, event, target_cursor_cell=0, speech_type=1):
        """Presents the current item/word."""

        self._context = self.get_or_create_context(script)
        word_string = self._context.getCurrent(flat_review.Context.WORD)[0] or ""
        voice = script.speechGenerator.voice(string=word_string)
        if not isinstance(event, input_event.BrailleEvent):
            if not word_string or word_string == "\n":
                script.speakMessage(messages.BLANK)
            else:
                line_string = self._context.getCurrent(flat_review.Context.LINE)[0] or ""
                if line_string == "\n":
                    script.speakMessage(messages.BLANK)
                elif word_string.isspace():
                    script.speakMessage(messages.WHITE_SPACE)
                elif word_string.isupper() and speech_type == 1:
                    script.speakMessage(word_string, voice)
                elif speech_type == 2:
                    script.spellCurrentItem(word_string)
                elif speech_type == 3:
                    script.phoneticSpellCurrentItem(word_string)
                elif speech_type == 1:
                    word_string = script.utilities.adjustForRepeats(word_string)
                    script.speakMessage(word_string, voice)

        orca.emitRegionChanged(self._context.getCurrentAccessible(), mode=orca.FLAT_REVIEW)
        script.updateBrailleReview(target_cursor_cell)
        self._current_contents = word_string
        return True

    def _character_presentation(self, script, event, speech_type=1):
        """Presents the current character."""

        self._context = self.get_or_create_context(script)
        char_string = self._context.getCurrent(flat_review.Context.CHAR)[0] or ""
        if not isinstance(event, input_event.BrailleEvent):
            if not char_string:
                script.speakMessage(messages.BLANK)
            else:
                line_string = self._context.getCurrent(flat_review.Context.LINE)[0] or ""
                if line_string == "\n" and speech_type != 3:
                    script.speakMessage(messages.BLANK)
                elif speech_type == 3:
                    script.speakUnicodeCharacter(char_string)
                elif speech_type == 2:
                    script.phoneticSpellCurrentItem(char_string)
                else:
                    script.speakCharacter(char_string)

        orca.emitRegionChanged(self._context.getCurrentAccessible(), mode=orca.FLAT_REVIEW)
        script.updateBrailleReview()
        self._current_contents = char_string
        return True

class FlatReviewContextGUI:
    """Presents the entire flat review context in a text view"""

    def __init__(self, script, title, text):
        self._script = script
        self._gui = self._create_dialog(title, text)

    def _create_dialog(self, title, text):
        """Creates the dialog."""

        dialog = Gtk.Dialog(title,
                            None,
                            Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        dialog.set_default_size(800, 600)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        textbuffer = Gtk.TextBuffer()
        textbuffer.set_text(text)
        textbuffer.place_cursor(textbuffer.get_start_iter())
        textview = Gtk.TextView(buffer=textbuffer)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)

        scrolled_window.add(textview)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)

        dialog.get_content_area().pack_start(scrolled_window, True, True, 0)
        dialog.connect("response", self.on_response)

        return dialog

    def on_response(self, dialog, response):
        """Handler for the 'response' signal of the dialog."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()

    def show_gui(self):
        """Shows the dialog."""

        self._gui.show_all()
        time_stamp = orca_state.lastInputEvent.timestamp
        if time_stamp == 0:
            time_stamp = Gtk.get_current_event_time()
        self._gui.present_with_time(time_stamp)


_presenter = FlatReviewPresenter()
def getPresenter():
    """Returns the Flat Review Presenter"""

    return _presenter
