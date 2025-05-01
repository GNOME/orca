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

import time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import braille
from . import cmdnames
from . import debug
from . import flat_review
from . import focus_manager
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import script_manager
from . import settings_manager
from . import settings
from . import speech_and_verbosity_manager
from .ax_event_synthesizer import AXEventSynthesizer
from .ax_object import AXObject
from .ax_text import AXText


class FlatReviewPresenter:
    """Provides access to on-screen objects via flat-review."""

    def __init__(self):
        self._context = None
        self._current_contents = ""
        self._restrict = settings_manager.get_manager().get_setting("flatReviewIsRestricted")
        self._handlers = self.get_handlers(True)
        self._desktop_bindings = keybindings.KeyBindings()
        self._laptop_bindings = keybindings.KeyBindings()
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
            msg = f"FLAT REVIEW PRESENTER: Creating new context. Restrict: {self._restrict}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

            if self._restrict:
                mode, obj = focus_manager.get_manager().get_active_mode_and_object_of_interest()
                self._context = flat_review.Context(script, root=obj)
            else:
                self._context = flat_review.Context(script)

            focus_manager.get_manager().emit_region_changed(
                self._context.getCurrentAccessible(), mode=focus_manager.FLAT_REVIEW)
            if script is not None:
                script.justEnteredFlatReviewMode = True
                script.targetCursorCell = script.getBrailleCursorCell()
            return self._context

        msg = f"FLAT REVIEW PRESENTER: Using existing context. Restrict: {self._restrict}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # If we are in unrestricted mode, update the context as below.
        # If the context already exists, but the active mode is not flat review, update
        # the flat review location to that of the object of interest -- if the object of
        # interest is in the flat review context (which means it's on screen). In some
        # cases the object of interest will not be in the flat review context because it
        # is represented by descendant text objects. setCurrentToZoneWithObject checks
        # for this condition and if it can find a zone whose ancestor is the object of
        # interest, it will set the current zone to the descendant, causing Orca to
        # present the text at the location of the object of interest.
        mode, obj = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if mode != focus_manager.FLAT_REVIEW and obj != self._context.getCurrentAccessible() \
           and not self._restrict:
            tokens = ["FLAT REVIEW PRESENTER: Attempting to update location from",
                      self._context.getCurrentAccessible(), "to", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._context.setCurrentToZoneWithObject(obj)

        # If we are restricting, and the current mode is not flat review, calculate a new context
        if self._restrict and mode != focus_manager.FLAT_REVIEW:
            msg = "FLAT REVIEW PRESENTER: Creating new restricted context."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._context = flat_review.Context(script, obj)

        return self._context

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the flat-review-presenter keybindings."""

        if refresh:
            msg = "FLAT REVIEW PRESENTER: Refreshing bindings."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif is_desktop and self._desktop_bindings.is_empty():
            self._setup_bindings()
        elif not is_desktop and self._laptop_bindings.is_empty():
            self._setup_bindings()

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
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return {}
        return bindings

    def get_handlers(self, refresh=False):
        """Returns the flat-review-presenter handlers."""

        if refresh:
            msg = "FLAT REVIEW PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_bindings(self):
        """Sets up the flat-review-presenter key bindings."""

        self._setup_desktop_bindings()
        self._setup_laptop_bindings()

    def _setup_handlers(self):
        """Sets up the flat-review-presenter input event handlers."""

        self._handlers = {}

        self._handlers["toggleFlatReviewModeHandler"] = \
            input_event.InputEventHandler(
                self.toggle_flat_review_mode,
                cmdnames.TOGGLE_FLAT_REVIEW)

        self._handlers["reviewHomeHandler"] = \
            input_event.InputEventHandler(
                self.go_home,
                cmdnames.REVIEW_HOME)

        self._handlers["reviewEndHandler"] = \
            input_event.InputEventHandler(
                self.go_end,
                cmdnames.REVIEW_END)

        self._handlers["reviewBottomLeftHandler"] = \
            input_event.InputEventHandler(
                self.go_bottom_left,
                cmdnames.REVIEW_BOTTOM_LEFT)

        self._handlers["reviewPreviousLineHandler"] = \
            input_event.InputEventHandler(
                self.go_previous_line,
                cmdnames.REVIEW_PREVIOUS_LINE)

        self._handlers["reviewCurrentLineHandler"] = \
            input_event.InputEventHandler(
                self.present_line,
                cmdnames.REVIEW_CURRENT_LINE)

        self._handlers["reviewNextLineHandler"] = \
            input_event.InputEventHandler(
                self.go_next_line,
                cmdnames.REVIEW_NEXT_LINE)

        self._handlers["reviewSpellCurrentLineHandler"] = \
            input_event.InputEventHandler(
                self.spell_line,
                cmdnames.REVIEW_SPELL_CURRENT_LINE)

        self._handlers["reviewPhoneticCurrentLineHandler"] = \
            input_event.InputEventHandler(
                self.phonetic_line,
                cmdnames.REVIEW_PHONETIC_CURRENT_LINE)

        self._handlers["reviewEndOfLineHandler"] = \
            input_event.InputEventHandler(
                self.go_end_of_line,
                cmdnames.REVIEW_END_OF_LINE)

        self._handlers["reviewPreviousItemHandler"] = \
            input_event.InputEventHandler(
                self.go_previous_item,
                cmdnames.REVIEW_PREVIOUS_ITEM)

        self._handlers["reviewCurrentItemHandler"] = \
            input_event.InputEventHandler(
                self.present_item,
                cmdnames.REVIEW_CURRENT_ITEM)

        self._handlers["reviewNextItemHandler"] = \
            input_event.InputEventHandler(
                self.go_next_item,
                cmdnames.REVIEW_NEXT_ITEM)

        self._handlers["reviewSpellCurrentItemHandler"] = \
            input_event.InputEventHandler(
                self.spell_item,
                cmdnames.REVIEW_SPELL_CURRENT_ITEM)

        self._handlers["reviewPhoneticCurrentItemHandler"] = \
            input_event.InputEventHandler(
                self.phonetic_item,
                cmdnames.REVIEW_PHONETIC_CURRENT_ITEM)

        self._handlers["reviewPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                self.go_previous_character,
                cmdnames.REVIEW_PREVIOUS_CHARACTER)

        self._handlers["reviewCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                self.present_character,
                cmdnames.REVIEW_CURRENT_CHARACTER)

        self._handlers["reviewSpellCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                self.spell_character,
                cmdnames.REVIEW_SPELL_CURRENT_CHARACTER)

        self._handlers["reviewUnicodeCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                self.unicode_current_character,
                cmdnames.REVIEW_UNICODE_CURRENT_CHARACTER)

        self._handlers["reviewNextCharacterHandler"] = \
            input_event.InputEventHandler(
                self.go_next_character,
                cmdnames.REVIEW_NEXT_CHARACTER)

        self._handlers["reviewCurrentAccessibleHandler"] = \
            input_event.InputEventHandler(
                self.present_object,
                cmdnames.REVIEW_CURRENT_ACCESSIBLE)

        self._handlers["reviewAboveHandler"] = \
            input_event.InputEventHandler(
                self.go_above,
                cmdnames.REVIEW_ABOVE)

        self._handlers["reviewBelowHandler"] = \
            input_event.InputEventHandler(
                self.go_below,
                cmdnames.REVIEW_BELOW)

        self._handlers["showContentsHandler"] = \
            input_event.InputEventHandler(
                self.show_contents,
                cmdnames.FLAT_REVIEW_SHOW_CONTENTS)

        self._handlers["flatReviewCopyHandler"] = \
            input_event.InputEventHandler(
                self.copy_to_clipboard,
                cmdnames.FLAT_REVIEW_COPY)

        self._handlers["flatReviewAppendHandler"] = \
            input_event.InputEventHandler(
                self.append_to_clipboard,
                cmdnames.FLAT_REVIEW_APPEND)

        self._handlers["flatReviewSayAllHandler"] = \
            input_event.InputEventHandler(
                self.say_all,
                cmdnames.SAY_ALL_FLAT_REVIEW)

        self._handlers["flatReviewToggleRestrictHandler"] = \
            input_event.InputEventHandler(
                self.toggle_restrict,
                cmdnames.TOGGLE_RESTRICT_FLAT_REVIEW)

        msg = "FLAT REVIEW PRESENTER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_desktop_bindings(self):
        """Sets up the flat-review-presenter desktop key bindings."""

        self._desktop_bindings = keybindings.KeyBindings()

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Subtract",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("toggleFlatReviewModeHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewSayAllHandler"),
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewHomeHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPreviousLineHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewCurrentLineHandler"),
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentLineHandler"),
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentLineHandler"),
                3))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewNextLineHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewEndHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPreviousItemHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewAboveHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewCurrentItemHandler"),
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentItemHandler"),
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentItemHandler"),
                3))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentAccessibleHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewNextItemHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewBelowHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_End",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewPreviousCharacterHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_End",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewEndOfLineHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewCurrentCharacterHandler"),
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentCharacterHandler"),
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewUnicodeCurrentCharacterHandler"),
                3))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("reviewNextCharacterHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("showContentsHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewCopyHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewAppendHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewToggleRestrictHandler")))

        msg = "FLAT REVIEW PRESENTER: Desktop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_laptop_bindings(self):
        """Sets up the flat-review-presenter laptop key bindings."""

        self._laptop_bindings = keybindings.KeyBindings()

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "p",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("toggleFlatReviewModeHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "semicolon",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("flatReviewSayAllHandler"),
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPreviousLineHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewHomeHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentLineHandler"),
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentLineHandler"),
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentLineHandler"),
                3))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewNextLineHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewEndHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "j",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPreviousItemHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "j",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewAboveHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentItemHandler"),
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentItemHandler"),
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPhoneticCurrentItemHandler"),
                3))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewCurrentAccessibleHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewNextItemHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewBelowHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewPreviousCharacterHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("reviewEndOfLineHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewCurrentCharacterHandler"),
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewSpellCurrentCharacterHandler"),
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewUnicodeCurrentCharacterHandler"),
                3))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "period",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("reviewNextCharacterHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("showContentsHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewCopyHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewAppendHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("flatReviewToggleRestrictHandler")))

        msg = "FLAT REVIEW PRESENTER: Laptop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def start(self, script=None, event=None):
        """Starts flat review."""

        if self._context:
            msg = "FLAT REVIEW PRESENTER: Already in flat review"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = "FLAT REVIEW PRESENTER: Starting flat review"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if script is None:
            script = script_manager.get_manager().get_active_script()

        self.get_or_create_context(script)
        if event is None:
            return

        if settings_manager.get_manager().get_setting('speechVerbosityLevel') \
           != settings.VERBOSITY_LEVEL_BRIEF:
            script.presentMessage(messages.FLAT_REVIEW_START)
        self._item_presentation(script, event, script.targetCursorCell)

    def quit(self, script=None, event=None):
        """Quits flat review."""

        if self._context is None:
            msg = "FLAT REVIEW PRESENTER: Not in flat review"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = "FLAT REVIEW PRESENTER: Quitting flat review"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._context = None
        focus = focus_manager.get_manager().get_locus_of_focus()
        focus_manager.get_manager().emit_region_changed(focus, mode=focus_manager.FOCUS_TRACKING)
        if event is None or script is None:
            return

        if settings_manager.get_manager().get_setting('speechVerbosityLevel') \
           != settings.VERBOSITY_LEVEL_BRIEF:
            script.presentMessage(messages.FLAT_REVIEW_STOP)
        script.update_braille(focus)

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

        focus_manager.get_manager().emit_region_changed(
            self._context.getCurrentAccessible(), mode=focus_manager.FLAT_REVIEW)
        return True

    def left_click_on_object(self, script, event=None):
        """Attempts to synthesize a left click on the current accessible."""

        self._context = self.get_or_create_context(script)
        obj = self._context.getCurrentAccessible()
        offset = self._context.getCurrentTextOffset()
        if offset >= 0 and AXEventSynthesizer.click_character(obj, offset, 1):
            return True
        return AXEventSynthesizer.click_object(obj, 1)

    def right_click_on_object(self, script, event=None):
        """Attempts to synthesize a left click on the current accessible."""

        self._context = self.get_or_create_context(script)
        obj = self._context.getCurrentAccessible()
        offset = self._context.getCurrentTextOffset()
        if offset >= 0 and AXEventSynthesizer.click_character(obj, offset, 3):
            return True
        return AXEventSynthesizer.click_object(obj, 3)

    def route_pointer_to_object(self, script, event=None):
        """Routes the mouse pointer to the current accessible."""

        self._context = self.get_or_create_context(script)
        obj = self._context.getCurrentAccessible()
        offset = self._context.getCurrentTextOffset()
        if offset >= 0 and AXEventSynthesizer.route_to_character(obj, offset):
            return True
        return AXEventSynthesizer.route_to_object(obj)

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
                script.speakMessage(string, script.speech_generator.voice(string=string))

        return True

    def show_contents(self, script, event=None):
        """Displays the entire flat review contents in a text view."""

        msg = "FLAT REVIEW PRESENTER: Showing contents."
        debug.print_message(debug.LEVEL_INFO, msg, True)

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

        script.get_clipboard_presenter().set_text(self._current_contents.rstrip("\n"))
        script.presentMessage(messages.FLAT_REVIEW_COPIED)
        return True

    def append_to_clipboard(self, script, event=None):
        """Appends the string just presented to the clipboard."""

        if not self.is_active():
            script.presentMessage(messages.FLAT_REVIEW_NOT_IN)
            return True

        script.get_clipboard_presenter().append_text(self._current_contents.rstrip("\n"))
        script.presentMessage(messages.FLAT_REVIEW_APPENDED)
        return True

    def toggle_restrict(self, script, event=None):
        """ Toggles the restricting of flat review to the current object. """

        self._restrict = not self._restrict
        settings_manager.get_manager().set_setting("flatReviewIsRestricted", self._restrict)

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
        voice = script.speech_generator.voice(string=line_string)

        if not isinstance(event, input_event.BrailleEvent):
            if not line_string or line_string == "\n":
                script.speakMessage(messages.BLANK)
            elif line_string.isspace():
                script.speakMessage(messages.WHITE_SPACE)
            elif line_string.isupper() and (speech_type < 2 or speech_type > 3):
                script.speakMessage(line_string, voice)
            elif speech_type == 2:
                script.spell_item(line_string)
            elif speech_type == 3:
                script.phoneticSpellCurrentItem(line_string)
            else:
                manager = speech_and_verbosity_manager.get_manager()
                line_string = manager.adjust_for_presentation(
                    self._context.getCurrentAccessible(), line_string)
                script.speakMessage(line_string, voice)

        focus_manager.get_manager().emit_region_changed(
            self._context.getCurrentAccessible(), mode=focus_manager.FLAT_REVIEW)
        script.updateBrailleReview()
        self._current_contents = line_string
        return True

    def _item_presentation(self, script, event, target_cursor_cell=0, speech_type=1):
        """Presents the current item/word."""

        self._context = self.get_or_create_context(script)
        word_string = self._context.getCurrent(flat_review.Context.WORD)[0] or ""
        voice = script.speech_generator.voice(string=word_string)
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
                    script.spell_item(word_string)
                elif speech_type == 3:
                    script.phoneticSpellCurrentItem(word_string)
                elif speech_type == 1:
                    manager = speech_and_verbosity_manager.get_manager()
                    word_string = manager.adjust_for_presentation(
                        self._context.getCurrentAccessible(), word_string)
                    script.speakMessage(word_string, voice)

        focus_manager.get_manager().emit_region_changed(
            self._context.getCurrentAccessible(), mode=focus_manager.FLAT_REVIEW)
        script.updateBrailleReview(target_cursor_cell)
        self._current_contents = word_string
        return True

    def _character_presentation(self, script, event, speech_type=1):
        """Presents the current character."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not self._context and AXObject.supports_text(focus):
            char_string = AXText.get_character_at_offset(focus)[0]
        else:
            self._context = self.get_or_create_context(script)
            char_string = self._context.getCurrent(flat_review.Context.CHAR)[0] or ""
        if not isinstance(event, input_event.BrailleEvent):
            if not char_string:
                script.speakMessage(messages.BLANK)
            else:
                if char_string == "\n" and speech_type != 3:
                    script.speakMessage(messages.BLANK)
                elif speech_type == 3:
                    script.speakMessage(messages.UNICODE % f"{ord(char_string):04x}")
                elif speech_type == 2:
                    script.phoneticSpellCurrentItem(char_string)
                else:
                    script.speak_character(char_string)

        if not self._context:
            return True

        focus_manager.get_manager().emit_region_changed(
            self._context.getCurrentAccessible(), mode=focus_manager.FLAT_REVIEW)
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
        self._gui.present_with_time(time.time())


_presenter = FlatReviewPresenter()
def get_presenter():
    """Returns the Flat Review Presenter"""

    return _presenter
