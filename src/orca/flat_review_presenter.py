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

# pylint: disable=too-many-lines
# pylint: disable=wrong-import-position
# pylint: disable=c-extension-no-member
# pylint: disable=too-many-public-methods

"""Module for flat-review commands"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

import time
from typing import TYPE_CHECKING

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import braille
from . import braille_presenter
from . import cmdnames
from . import dbus_service
from . import debug
from . import flat_review
from . import focus_manager
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import script_manager
from . import settings_manager
from . import speech_and_verbosity_manager
from .ax_event_synthesizer import AXEventSynthesizer
from .ax_object import AXObject
from .ax_text import AXText

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class FlatReviewPresenter:
    """Provides access to on-screen objects via flat-review."""

    def __init__(self) -> None:
        self._context: flat_review.Context | None = None
        self._current_contents: str = ""
        self._restrict: bool = self.get_is_restricted()
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._desktop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._laptop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._gui: FlatReviewContextGUI | None = None

        msg = "FLAT REVIEW PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("FlatReviewPresenter", self)

    def is_active(self) -> bool:
        """Returns True if the flat review presenter is active."""

        return self._context is not None

    def get_or_create_context(self, script: default.Script | None = None) -> flat_review.Context:
        """Returns the flat review context, creating one if necessary."""

        if not self._context:
            msg = f"FLAT REVIEW PRESENTER: Creating new context. Restrict: {self._restrict}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

            if self._restrict:
                mode, obj = focus_manager.get_manager().get_active_mode_and_object_of_interest()
                self._context = flat_review.Context(script, root=obj)
            else:
                self._context = flat_review.Context(script)

            focus_manager.get_manager().emit_region_changed(
                self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW)

            return self._context

        msg = f"FLAT REVIEW PRESENTER: Using existing context. Restrict: {self._restrict}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # If we are in unrestricted mode, update the context as below.
        # If the context already exists, but the active mode is not flat review, update
        # the flat review location to that of the object of interest -- if the object of
        # interest is in the flat review context (which means it's on screen). In some
        # cases the object of interest will not be in the flat review context because it
        # is represented by descendant text objects. set_current_to_zone_with_object checks
        # for this condition and if it can find a zone whose ancestor is the object of
        # interest, it will set the current zone to the descendant, causing Orca to
        # present the text at the location of the object of interest.
        mode, obj = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if mode != focus_manager.FLAT_REVIEW and obj != self._context.get_current_object() \
           and not self._restrict:
            tokens = ["FLAT REVIEW PRESENTER: Attempting to update location from",
                      self._context.get_current_object(), "to", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._context.set_current_to_zone_with_object(obj)

        # If we are restricting, and the current mode is not flat review, calculate a new context
        if self._restrict and mode != focus_manager.FLAT_REVIEW:
            msg = "FLAT REVIEW PRESENTER: Creating new restricted context."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._context = flat_review.Context(script, obj)

        return self._context

    def get_bindings(
        self,
        refresh: bool = False,
        is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the flat-review-presenter keybindings."""

        if refresh:
            msg = "FLAT REVIEW PRESENTER: Refreshing bindings."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._laptop_bindings.remove_key_grabs("FLAT REVIEW PRESENTER: Refreshing bindings.")
            self._desktop_bindings.remove_key_grabs("FLAT REVIEW PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif is_desktop and self._desktop_bindings.is_empty():
            self._setup_bindings()
        elif not is_desktop and self._laptop_bindings.is_empty():
            self._setup_bindings()

        if is_desktop:
            return self._desktop_bindings
        return self._laptop_bindings

    def get_braille_bindings(self) -> dict[int, input_event.InputEventHandler]:
        """Returns the flat-review-presenter braille bindings."""

        bindings = {}
        try:
            bindings[braille.brlapi.KEY_CMD_LNUP] = \
                self._handlers["reviewAboveHandler"]
            bindings[braille.brlapi.KEY_CMD_LNDN] = \
                self._handlers["reviewBelowHandler"]
            bindings[braille.brlapi.KEY_CMD_FREEZE] = \
                self._handlers["toggleFlatReviewModeHandler"]
            bindings[braille.brlapi.KEY_CMD_TOP_LEFT] = \
                self._handlers["reviewHomeHandler"]
            bindings[braille.brlapi.KEY_CMD_BOT_LEFT] = \
                self._handlers["reviewBottomLeftHandler"]
        except AttributeError as error:
            tokens = ["FLAT REVIEW PRESENTER: Exception getting braille bindings:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return {}
        return bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the flat-review-presenter handlers."""

        if refresh:
            msg = "FLAT REVIEW PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_bindings(self) -> None:
        """Sets up the flat-review-presenter key bindings."""

        self._setup_desktop_bindings()
        self._setup_laptop_bindings()

    def _setup_handlers(self) -> None:
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

    def _setup_desktop_bindings(self) -> None:
        """Sets up the flat-review-presenter desktop key bindings."""

        self._desktop_bindings = keybindings.KeyBindings()

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Subtract",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["toggleFlatReviewModeHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["flatReviewSayAllHandler"],
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewHomeHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewPreviousLineHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewCurrentLineHandler"],
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewSpellCurrentLineHandler"],
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewPhoneticCurrentLineHandler"],
                3))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewNextLineHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewEndHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewPreviousItemHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewAboveHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewCurrentItemHandler"],
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewSpellCurrentItemHandler"],
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewPhoneticCurrentItemHandler"],
                3))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewCurrentAccessibleHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewNextItemHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewBelowHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_End",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewPreviousCharacterHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_End",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewEndOfLineHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewCurrentCharacterHandler"],
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewSpellCurrentCharacterHandler"],
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewUnicodeCurrentCharacterHandler"],
                3))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Page_Down",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["reviewNextCharacterHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["showContentsHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["flatReviewCopyHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["flatReviewAppendHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["flatReviewToggleRestrictHandler"]))

        msg = "FLAT REVIEW PRESENTER: Desktop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_laptop_bindings(self) -> None:
        """Sets up the flat-review-presenter laptop key bindings."""

        self._laptop_bindings = keybindings.KeyBindings()

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "p",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["toggleFlatReviewModeHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "semicolon",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["flatReviewSayAllHandler"],
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewPreviousLineHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers["reviewHomeHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewCurrentLineHandler"],
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewSpellCurrentLineHandler"],
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewPhoneticCurrentLineHandler"],
                3))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewNextLineHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers["reviewEndHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "j",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewPreviousItemHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "j",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers["reviewAboveHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewCurrentItemHandler"],
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewSpellCurrentItemHandler"],
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewPhoneticCurrentItemHandler"],
                3))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers["reviewCurrentAccessibleHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewNextItemHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers["reviewBelowHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewPreviousCharacterHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers["reviewEndOfLineHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewCurrentCharacterHandler"],
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewSpellCurrentCharacterHandler"],
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewUnicodeCurrentCharacterHandler"],
                3))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "period",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["reviewNextCharacterHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["showContentsHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["flatReviewCopyHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["flatReviewAppendHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["flatReviewToggleRestrictHandler"]))

        msg = "FLAT REVIEW PRESENTER: Laptop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def start(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None
    ) -> None:
        """Starts flat review."""

        if self._context:
            msg = "FLAT REVIEW PRESENTER: Already in flat review"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = "FLAT REVIEW PRESENTER: Starting flat review"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if script is None:
            script = script_manager.get_manager().get_active_script()
            assert script is not None

        self.get_or_create_context(script)
        if event is None:
            return

        if speech_and_verbosity_manager.get_manager().use_verbose_speech():
            script.present_message(messages.FLAT_REVIEW_START)
        self._item_presentation(script, event)

    def quit(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None
    ) -> None:
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

        if speech_and_verbosity_manager.get_manager().use_verbose_speech():
            script.present_message(messages.FLAT_REVIEW_STOP)
        script.update_braille(focus)

    @dbus_service.command
    def toggle_flat_review_mode(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> bool:
        """Toggles between flat review mode and focus tracking mode."""

        tokens = ["FLAT REVIEW PRESENTER: toggle_flat_review_mode. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self.is_active():
            self.quit(script, event)
            return True

        self.start(script, event)
        return True

    @dbus_service.command
    def go_home(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the top left of the current window."""

        tokens = ["FLAT REVIEW PRESENTER: go_home. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        self._context.go_to_start_of(flat_review.Context.WINDOW)
        self.present_line(script, event)
        return True

    @dbus_service.command
    def go_end(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the bottom right of the current window."""

        tokens = ["FLAT REVIEW PRESENTER: go_end. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        self._context.go_to_end_of(flat_review.Context.WINDOW)
        self.present_line(script, event)
        return True

    @dbus_service.command
    def go_bottom_left(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the bottom left of the current window."""

        tokens = ["FLAT REVIEW PRESENTER: go_bottom_left. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        self._context.go_to_end_of(flat_review.Context.WINDOW)
        self._context.go_to_start_of(flat_review.Context.LINE)
        self.present_line(script, event)
        return True

    @dbus_service.command
    def go_previous_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the previous line."""

        tokens = ["FLAT REVIEW PRESENTER: go_previous_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_previous_line():
            self.present_line(script, event)
        return True

    @dbus_service.command
    def present_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current line."""

        tokens = ["FLAT REVIEW PRESENTER: present_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._line_presentation(script, event, 1)
        return True

    @dbus_service.command
    def go_next_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the next line."""

        tokens = ["FLAT REVIEW PRESENTER: go_next_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_next_line():
            self.present_line(script, event)
        return True

    @dbus_service.command
    def spell_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current line letter by letter."""

        tokens = ["FLAT REVIEW PRESENTER: spell_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._line_presentation(script, event, 2)
        return True

    @dbus_service.command
    def phonetic_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current line letter by letter phonetically."""

        tokens = ["FLAT REVIEW PRESENTER: phonetic_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._line_presentation(script, event, 3)
        return True

    @dbus_service.command
    def go_start_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the beginning of the current line."""

        tokens = ["FLAT REVIEW PRESENTER: go_start_of_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        self._context.go_to_start_of(flat_review.Context.LINE)
        self.present_character(script, event)
        return True

    @dbus_service.command
    def go_end_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the end of the line."""

        tokens = ["FLAT REVIEW PRESENTER: go_end_of_line. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        self._context.go_to_end_of(flat_review.Context.LINE)
        self.present_character(script, event)
        return True

    @dbus_service.command
    def go_previous_item(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the previous item or word."""

        tokens = ["FLAT REVIEW PRESENTER: go_previous_item. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_previous_word():
            self.present_item(script, event)
        return True

    @dbus_service.command
    def present_item(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current item/word."""

        tokens = ["FLAT REVIEW PRESENTER: present_item. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._item_presentation(script, event, 1)
        return True

    @dbus_service.command
    def go_next_item(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the next item or word."""

        tokens = ["FLAT REVIEW PRESENTER: go_next_item. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_next_word():
            self.present_item(script, event)
        return True

    @dbus_service.command
    def spell_item(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current item/word letter by letter."""

        tokens = ["FLAT REVIEW PRESENTER: spell_item. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._item_presentation(script, event, 2)
        return True

    @dbus_service.command
    def phonetic_item(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current word letter by letter phonetically."""

        tokens = ["FLAT REVIEW PRESENTER: phonetic_item. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._item_presentation(script, event, 3)
        return True

    @dbus_service.command
    def go_previous_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the previous character."""

        tokens = ["FLAT REVIEW PRESENTER: go_previous_character. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_previous_character():
            self.present_character(script, event)
        return True

    @dbus_service.command
    def present_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current character."""

        tokens = ["FLAT REVIEW PRESENTER: present_character. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._character_presentation(script, event, 1)
        return True

    @dbus_service.command
    def go_next_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the next character."""

        tokens = ["FLAT REVIEW PRESENTER: go_next_character. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_next_character():
            self.present_character(script, event)
        return True

    @dbus_service.command
    def spell_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current character phonetically."""

        tokens = ["FLAT REVIEW PRESENTER: spell_character. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._character_presentation(script, event, 2)
        return True

    @dbus_service.command
    def unicode_current_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current character's unicode value."""

        tokens = ["FLAT REVIEW PRESENTER: unicode_current_character. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._character_presentation(script, event, 3)
        return True

    @dbus_service.command
    def go_above(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the character above."""

        tokens = ["FLAT REVIEW PRESENTER: go_above. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_up():
            self.present_item(script, event)
        return True

    @dbus_service.command
    def go_below(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the character below."""

        tokens = ["FLAT REVIEW PRESENTER: go_below. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if self._context.go_down():
            self.present_item(script, event)
        return True

    @dbus_service.command
    def get_current_object(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> Atspi.Accessible:
        """Returns the current accessible object."""

        tokens = ["FLAT REVIEW PRESENTER: get_current_object. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        return self._context.get_current_object()

    @dbus_service.command
    def present_object(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current accessible object."""

        tokens = ["FLAT REVIEW PRESENTER: present_object. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if not isinstance(event, input_event.BrailleEvent):
            script.present_object(self._context.get_current_object(), speechonly=True)

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW)
        return True

    @dbus_service.command
    def left_click_on_object(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Attempts to synthesize a left click on the current accessible."""

        tokens = ["FLAT REVIEW PRESENTER: left_click_on_object. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        obj = self._context.get_current_object()
        offset = self._context.get_current_text_offset()
        if offset >= 0 and AXEventSynthesizer.click_character(obj, offset, 1):
            return True
        return AXEventSynthesizer.click_object(obj, 1)

    @dbus_service.command
    def right_click_on_object(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Attempts to synthesize a right click on the current accessible."""

        tokens = ["FLAT REVIEW PRESENTER: right_click_on_object. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        obj = self._context.get_current_object()
        offset = self._context.get_current_text_offset()
        if offset >= 0 and AXEventSynthesizer.click_character(obj, offset, 3):
            return True
        return AXEventSynthesizer.click_object(obj, 3)

    @dbus_service.command
    def route_pointer_to_object(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Routes the mouse pointer to the current accessible."""

        tokens = ["FLAT REVIEW PRESENTER: route_pointer_to_object. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        obj = self._context.get_current_object()
        offset = self._context.get_current_text_offset()
        if offset >= 0 and AXEventSynthesizer.route_to_character(obj, offset):
            return True
        return AXEventSynthesizer.route_to_object(obj)

    def _update_braille(self, script: default.Script) -> None:
        """Obtains the braille regions for the current flat review line and displays them."""

        if not braille_presenter.get_presenter().use_braille():
            return

        self._context = self.get_or_create_context(script)
        regions, focused_region = self._context.get_current_braille_regions()
        if not regions:
            braille.refresh(True)
            return

        line = braille.Line()
        line.add_regions(regions)
        braille.set_lines([line])
        braille.setFocus(focused_region)
        braille.refresh(True)

    # TODO - JD: See what adjustments might be needed for the pan_amount parameter
    def pan_braille_left(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans the braille display left."""

        self._context = self.get_or_create_context(script)
        if braille.beginningIsShowing:
            self._context.go_to_start_of(flat_review.Context.LINE)
            self._context.go_previous_character()
            self._update_braille(script)
            return True

        braille.panLeft(pan_amount)
        braille_region, offset_in_zone = braille.getRegionAtCell(1)
        while braille_region and not hasattr(braille_region, "zone"):
            if not braille.panLeft(1):
                break
            braille_region, offset_in_zone = braille.getRegionAtCell(1)

        if braille_region and not hasattr(braille_region, "zone"):
            self._context.go_to_start_of(flat_review.Context.LINE)
            self._context.go_previous_character()
            self._update_braille(script)
            return True

        if braille_region and hasattr(braille_region, "zone"):
            self._context.set_current_zone(braille_region.zone, offset_in_zone)
            self._update_braille(script)
        return True

    # TODO - JD: See what adjustments might be needed for the pan_amount parameter
    def pan_braille_right(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans the braille display right."""

        self._context = self.get_or_create_context(script)
        if braille.endIsShowing:
            self._context.go_next_line()
            self._update_braille(script)
            return True

        braille.panRight(pan_amount)
        braille_region, offset_in_zone = braille.getRegionAtCell(1)
        while braille_region and not hasattr(braille_region, "zone"):
            if not braille.panRight(1):
                break
            braille_region, offset_in_zone = braille.getRegionAtCell(1)

        if braille_region and not hasattr(braille_region, "zone"):
            self._context.go_next_line()
            self._update_braille(script)
            return True

        if braille_region and hasattr(braille_region, "zone"):
            self._context.set_current_zone(braille_region.zone, offset_in_zone)
            self._update_braille(script)
        return True

    def _get_all_lines(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None = None
    ) -> tuple[list[str], tuple[int, int, int, int]]:
        """Returns a (textual lines, current location) tuple."""

        lines = []
        self._context = self.get_or_create_context(script)
        location = self._context.get_current_location()
        self._context.go_to_start_of(flat_review.Context.WINDOW)
        string = self._context.get_current_line_string()
        while string is not None:
            lines.append(string.rstrip("\n"))
            if not self._context.go_next_line():
                break
            string = self._context.get_current_line_string()
        return lines, location

    @dbus_service.command
    def say_all(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Speaks the contents of the entire window."""

        tokens = ["FLAT REVIEW PRESENTER: say_all. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for string in self._get_all_lines(script, event)[0]:
            if not string.isspace():
                script.speak_message(string, script.speech_generator.voice(string=string))

        return True

    @dbus_service.command
    def show_contents(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays the entire flat review contents in a text view."""

        tokens = ["FLAT REVIEW PRESENTER: show_contents. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        lines, location = self._get_all_lines(script, event)
        text = "\n".join(lines)
        title = guilabels.FLAT_REVIEW_CONTENTS
        self._gui = FlatReviewContextGUI(script, title, text, location)
        self._gui.show_gui()
        return True

    @dbus_service.command
    def copy_to_clipboard(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Copies the string just presented to the clipboard."""

        tokens = ["FLAT REVIEW PRESENTER: copy_to_clipboard. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.is_active():
            if notify_user:
                script.present_message(messages.FLAT_REVIEW_NOT_IN)
            return True

        script.get_clipboard_presenter().set_text(self._current_contents.rstrip("\n"))
        if notify_user:
            script.present_message(messages.FLAT_REVIEW_COPIED)
        return True

    @dbus_service.command
    def append_to_clipboard(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Appends the string just presented to the clipboard."""

        tokens = ["FLAT REVIEW PRESENTER: append_to_clipboard. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.is_active():
            if notify_user:
                script.present_message(messages.FLAT_REVIEW_NOT_IN)
            return True

        script.get_clipboard_presenter().append_text(self._current_contents.rstrip("\n"))
        if notify_user:
            script.present_message(messages.FLAT_REVIEW_APPENDED)
        return True

    @dbus_service.getter
    def get_is_restricted(self) -> bool:
        """Returns whether flat review is restricted to the current object."""

        return settings_manager.get_manager().get_setting("flatReviewIsRestricted")

    @dbus_service.setter
    def set_is_restricted(self, value: bool) -> bool:
        """Sets whether flat review is restricted to the current object."""

        msg = f"FLAT REVIEW PRESENTER: Setting is-restricted to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("flatReviewIsRestricted", value)
        return True

    @dbus_service.command
    def toggle_restrict(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """ Toggles the restricting of flat review to the current object. """

        tokens = ["FLAT REVIEW PRESENTER: toggle_restrict. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._restrict = not self._restrict
        settings_manager.get_manager().set_setting("flatReviewIsRestricted", self._restrict)

        if self._restrict:
            if notify_user:
                script.present_message(messages.FLAT_REVIEW_RESTRICTED)
        else:
            if notify_user:
                script.present_message(messages.FLAT_REVIEW_UNRESTRICTED)
        if self.is_active():
            # Reset the context
            self._context = None
            self.start()

        return True

    def _line_presentation(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        speech_type: int = 1
    ) -> bool:
        """Presents the current line."""

        self._context = self.get_or_create_context(script)
        line_string = self._context.get_current_line_string()
        voice = script.speech_generator.voice(string=line_string)

        if not isinstance(event, input_event.BrailleEvent):
            if not line_string or line_string == "\n":
                script.speak_message(messages.BLANK)
            elif line_string.isspace():
                script.speak_message(messages.WHITE_SPACE)
            elif line_string.isupper() and (speech_type < 2 or speech_type > 3):
                script.speak_message(line_string, voice)
            elif speech_type == 2:
                script.spell_item(line_string)
            elif speech_type == 3:
                script.spell_phonetically(line_string)
            else:
                manager = speech_and_verbosity_manager.get_manager()
                line_string = manager.adjust_for_presentation(
                    self._context.get_current_object(), line_string)
                script.speak_message(line_string, voice)

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW)
        self._update_braille(script)
        self._current_contents = line_string
        return True

    def _item_presentation(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        speech_type: int = 1
    ) -> bool:
        """Presents the current item/word."""

        self._context = self.get_or_create_context(script)
        word_string = self._context.get_current_word_string()
        voice = script.speech_generator.voice(string=word_string)
        if not isinstance(event, input_event.BrailleEvent):
            if not word_string or word_string == "\n":
                script.speak_message(messages.BLANK)
            else:
                line_string = self._context.get_current_line_string()
                if line_string == "\n":
                    script.speak_message(messages.BLANK)
                elif word_string.isspace():
                    script.speak_message(messages.WHITE_SPACE)
                elif word_string.isupper() and speech_type == 1:
                    script.speak_message(word_string, voice)
                elif speech_type == 2:
                    script.spell_item(word_string)
                elif speech_type == 3:
                    script.spell_phonetically(word_string)
                elif speech_type == 1:
                    manager = speech_and_verbosity_manager.get_manager()
                    word_string = manager.adjust_for_presentation(
                        self._context.get_current_object(), word_string)
                    script.speak_message(word_string, voice)

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW)
        self._update_braille(script)
        self._current_contents = word_string
        return True

    def _character_presentation(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        speech_type: int = 1
    ) -> bool:
        """Presents the current character."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not self._context and AXObject.supports_text(focus):
            char_string = AXText.get_character_at_offset(focus)[0]
        else:
            self._context = self.get_or_create_context(script)
            char_string = self._context.get_current_character_string()
        if not isinstance(event, input_event.BrailleEvent):
            if not char_string:
                script.speak_message(messages.BLANK)
            else:
                if char_string == "\n" and speech_type != 3:
                    script.speak_message(messages.BLANK)
                elif speech_type == 3:
                    script.speak_message(messages.UNICODE % f"{ord(char_string):04x}")
                elif speech_type == 2:
                    script.spell_phonetically(char_string)
                else:
                    script.speak_character(char_string)

        if not self._context:
            return True

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW)
        self._update_braille(script)
        self._current_contents = char_string
        return True

class FlatReviewContextGUI:
    """Presents the entire flat review context in a text view"""

    def __init__(
        self,
        script: default.Script,
        title: str,
        text: str,
        location: tuple[int, int, int, int]
    ) -> None:
        self._script: default.Script = script
        self._gui: Gtk.Dialog = self._create_dialog(title, text, location)

    def _create_dialog(
        self,
        title: str,
        text: str,
        location: tuple[int, int, int, int]
    ) -> Gtk.Dialog:
        """Creates the dialog."""

        dialog = Gtk.Dialog(title,
                            None,
                            Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        dialog.set_default_size(800, 600)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)

        textbuffer = Gtk.TextBuffer()
        textbuffer.set_text(text)

        line_index, _zone_index, word_index, char_index = location
        start_iter = textbuffer.get_start_iter()
        start_iter.forward_lines(line_index)
        for _ in range(word_index):
            start_iter.forward_word_end()
            # This is needed to get past any punctuation. Note that we cannot check starts_word
            # here. Example: The letter after an apostrophe is reported as a word start.
            while not start_iter.get_char().isspace():
                if not start_iter.forward_char():
                    break

        # The text iter word can start with one or more spaces. Move to the beginning of the flat
        # review word before advancing by character.
        while not start_iter.starts_word():
            if not start_iter.forward_char():
                break

        start_iter.forward_chars(char_index)
        textbuffer.place_cursor(start_iter)

        textview = Gtk.TextView(buffer=textbuffer)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(textview) # pylint: disable=no-member
        dialog.get_content_area().pack_start(scrolled_window, True, True, 0)
        dialog.connect("response", self.on_response)
        return dialog

    def on_response(self, _dialog: Gtk.Dialog, response: Gtk.ResponseType) -> None:
        """Handler for the 'response' signal of the dialog."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()

    def show_gui(self) -> None:
        """Shows the dialog."""

        self._gui.show_all() # pylint: disable=no-member
        self._gui.present_with_time(time.time())


_presenter: FlatReviewPresenter = FlatReviewPresenter()

def get_presenter() -> FlatReviewPresenter:
    """Returns the Flat Review Presenter"""

    return _presenter
