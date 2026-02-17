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
# pylint: disable=too-many-public-methods

"""Module for flat-review commands"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import braille
from . import braille_presenter
from . import clipboard
from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import gsettings_registry
from . import flat_review
from . import focus_manager
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import presentation_manager
from . import script_manager
from . import settings
from . import speech_presenter
from .ax_event_synthesizer import AXEventSynthesizer
from .ax_object import AXObject
from .ax_text import AXText

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.FlatReview", name="flat-review")
class FlatReviewPresenter:
    """Provides access to on-screen objects via flat-review."""

    _SCHEMA = "flat-review"

    def _get_setting(self, key: str, fallback: bool) -> bool:
        """Returns the dconf value for key, or fallback if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA, key, "b", fallback=fallback
        )

    def __init__(self) -> None:
        self._context: flat_review.Context | None = None
        self._current_contents: str = ""
        self._restrict: bool = self.get_is_restricted()
        self._gui: FlatReviewContextGUI | None = None
        self._initialized: bool = False

        msg = "FLAT REVIEW PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("FlatReviewPresenter", self)

    # pylint: disable-next=too-many-locals
    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_FLAT_REVIEW

        # Build keybinding mapping: cmd_name -> (desktop_kb, laptop_kb)
        def kb(keysym: str, mod: int, clicks: int = 1) -> keybindings.KeyBinding:
            return keybindings.KeyBinding(keysym, mod, click_count=clicks)

        cmd_bindings: dict[
            str, tuple[keybindings.KeyBinding | None, keybindings.KeyBinding | None]
        ] = {
            "toggleFlatReviewModeHandler": (
                kb("KP_Subtract", keybindings.NO_MODIFIER_MASK),
                kb("p", keybindings.ORCA_MODIFIER_MASK),
            ),
            "flatReviewSayAllHandler": (
                kb("KP_Add", keybindings.NO_MODIFIER_MASK, 2),
                kb("semicolon", keybindings.ORCA_MODIFIER_MASK, 2),
            ),
            "reviewHomeHandler": (
                kb("KP_Home", keybindings.ORCA_MODIFIER_MASK),
                kb("u", keybindings.ORCA_CTRL_MODIFIER_MASK),
            ),
            "reviewPreviousLineHandler": (
                kb("KP_Home", keybindings.NO_MODIFIER_MASK),
                kb("u", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewCurrentLineHandler": (
                kb("KP_Up", keybindings.NO_MODIFIER_MASK),
                kb("i", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewSpellCurrentLineHandler": (
                kb("KP_Up", keybindings.NO_MODIFIER_MASK, 2),
                kb("i", keybindings.ORCA_MODIFIER_MASK, 2),
            ),
            "reviewPhoneticCurrentLineHandler": (
                kb("KP_Up", keybindings.NO_MODIFIER_MASK, 3),
                kb("i", keybindings.ORCA_MODIFIER_MASK, 3),
            ),
            "reviewNextLineHandler": (
                kb("KP_Page_Up", keybindings.NO_MODIFIER_MASK),
                kb("o", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewEndHandler": (
                kb("KP_Page_Up", keybindings.ORCA_MODIFIER_MASK),
                kb("o", keybindings.ORCA_CTRL_MODIFIER_MASK),
            ),
            "reviewPreviousItemHandler": (
                kb("KP_Left", keybindings.NO_MODIFIER_MASK),
                kb("j", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewAboveHandler": (
                kb("KP_Left", keybindings.ORCA_MODIFIER_MASK),
                kb("j", keybindings.ORCA_CTRL_MODIFIER_MASK),
            ),
            "reviewCurrentItemHandler": (
                kb("KP_Begin", keybindings.NO_MODIFIER_MASK),
                kb("k", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewSpellCurrentItemHandler": (
                kb("KP_Begin", keybindings.NO_MODIFIER_MASK, 2),
                kb("k", keybindings.ORCA_MODIFIER_MASK, 2),
            ),
            "reviewPhoneticCurrentItemHandler": (
                kb("KP_Begin", keybindings.NO_MODIFIER_MASK, 3),
                kb("k", keybindings.ORCA_MODIFIER_MASK, 3),
            ),
            "reviewCurrentAccessibleHandler": (
                kb("KP_Begin", keybindings.ORCA_MODIFIER_MASK),
                kb("k", keybindings.ORCA_CTRL_MODIFIER_MASK),
            ),
            "reviewNextItemHandler": (
                kb("KP_Right", keybindings.NO_MODIFIER_MASK),
                kb("l", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewBelowHandler": (
                kb("KP_Right", keybindings.ORCA_MODIFIER_MASK),
                kb("l", keybindings.ORCA_CTRL_MODIFIER_MASK),
            ),
            "reviewPreviousCharacterHandler": (
                kb("KP_End", keybindings.NO_MODIFIER_MASK),
                kb("m", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewEndOfLineHandler": (
                kb("KP_End", keybindings.ORCA_MODIFIER_MASK),
                kb("m", keybindings.ORCA_CTRL_MODIFIER_MASK),
            ),
            "reviewCurrentCharacterHandler": (
                kb("KP_Down", keybindings.NO_MODIFIER_MASK),
                kb("comma", keybindings.ORCA_MODIFIER_MASK),
            ),
            "reviewSpellCurrentCharacterHandler": (
                kb("KP_Down", keybindings.NO_MODIFIER_MASK, 2),
                kb("comma", keybindings.ORCA_MODIFIER_MASK, 2),
            ),
            "reviewUnicodeCurrentCharacterHandler": (
                kb("KP_Down", keybindings.NO_MODIFIER_MASK, 3),
                kb("comma", keybindings.ORCA_MODIFIER_MASK, 3),
            ),
            "reviewNextCharacterHandler": (
                kb("KP_Page_Down", keybindings.NO_MODIFIER_MASK),
                kb("period", keybindings.ORCA_MODIFIER_MASK),
            ),
            # Commands with no keybinding
            "reviewBottomLeftHandler": (None, None),
            "showContentsHandler": (None, None),
            "flatReviewCopyHandler": (None, None),
            "flatReviewAppendHandler": (None, None),
            "flatReviewToggleRestrictHandler": (None, None),
        }

        commands_data = [
            (
                "toggleFlatReviewModeHandler",
                self.toggle_flat_review_mode,
                cmdnames.TOGGLE_FLAT_REVIEW,
            ),
            ("reviewHomeHandler", self.go_home, cmdnames.REVIEW_HOME),
            ("reviewEndHandler", self.go_end, cmdnames.REVIEW_END),
            ("reviewBottomLeftHandler", self.go_bottom_left, cmdnames.REVIEW_BOTTOM_LEFT),
            ("reviewPreviousLineHandler", self.go_previous_line, cmdnames.REVIEW_PREVIOUS_LINE),
            ("reviewCurrentLineHandler", self.present_line, cmdnames.REVIEW_CURRENT_LINE),
            ("reviewNextLineHandler", self.go_next_line, cmdnames.REVIEW_NEXT_LINE),
            ("reviewSpellCurrentLineHandler", self.spell_line, cmdnames.REVIEW_SPELL_CURRENT_LINE),
            (
                "reviewPhoneticCurrentLineHandler",
                self.phonetic_line,
                cmdnames.REVIEW_PHONETIC_CURRENT_LINE,
            ),
            ("reviewEndOfLineHandler", self.go_end_of_line, cmdnames.REVIEW_END_OF_LINE),
            ("reviewPreviousItemHandler", self.go_previous_item, cmdnames.REVIEW_PREVIOUS_ITEM),
            ("reviewCurrentItemHandler", self.present_item, cmdnames.REVIEW_CURRENT_ITEM),
            ("reviewNextItemHandler", self.go_next_item, cmdnames.REVIEW_NEXT_ITEM),
            ("reviewSpellCurrentItemHandler", self.spell_item, cmdnames.REVIEW_SPELL_CURRENT_ITEM),
            (
                "reviewPhoneticCurrentItemHandler",
                self.phonetic_item,
                cmdnames.REVIEW_PHONETIC_CURRENT_ITEM,
            ),
            (
                "reviewPreviousCharacterHandler",
                self.go_previous_character,
                cmdnames.REVIEW_PREVIOUS_CHARACTER,
            ),
            (
                "reviewCurrentCharacterHandler",
                self.present_character,
                cmdnames.REVIEW_CURRENT_CHARACTER,
            ),
            (
                "reviewSpellCurrentCharacterHandler",
                self.spell_character,
                cmdnames.REVIEW_SPELL_CURRENT_CHARACTER,
            ),
            (
                "reviewUnicodeCurrentCharacterHandler",
                self.unicode_current_character,
                cmdnames.REVIEW_UNICODE_CURRENT_CHARACTER,
            ),
            ("reviewNextCharacterHandler", self.go_next_character, cmdnames.REVIEW_NEXT_CHARACTER),
            (
                "reviewCurrentAccessibleHandler",
                self.present_object,
                cmdnames.REVIEW_CURRENT_ACCESSIBLE,
            ),
            ("reviewAboveHandler", self.go_above, cmdnames.REVIEW_ABOVE),
            ("reviewBelowHandler", self.go_below, cmdnames.REVIEW_BELOW),
            ("showContentsHandler", self.show_contents, cmdnames.FLAT_REVIEW_SHOW_CONTENTS),
            ("flatReviewCopyHandler", self.copy_to_clipboard, cmdnames.FLAT_REVIEW_COPY),
            ("flatReviewAppendHandler", self.append_to_clipboard, cmdnames.FLAT_REVIEW_APPEND),
            ("flatReviewSayAllHandler", self.say_all, cmdnames.SAY_ALL_FLAT_REVIEW),
            (
                "flatReviewToggleRestrictHandler",
                self.toggle_restrict,
                cmdnames.TOGGLE_RESTRICT_FLAT_REVIEW,
            ),
        ]

        braille_bindings: dict[str, tuple[int, ...]] = {}
        bindings = [
            ("reviewAboveHandler", braille.BRLAPI_KEY_CMD_LNUP),
            ("reviewBelowHandler", braille.BRLAPI_KEY_CMD_LNDN),
            ("toggleFlatReviewModeHandler", braille.BRLAPI_KEY_CMD_FREEZE),
            ("reviewHomeHandler", braille.BRLAPI_KEY_CMD_TOP_LEFT),
            ("reviewBottomLeftHandler", braille.BRLAPI_KEY_CMD_BOT_LEFT),
        ]
        for name, key in bindings:
            if key is not None:
                braille_bindings[name] = (key,)
        if not braille_bindings:
            msg = "FLAT REVIEW PRESENTER: Braille bindings unavailable."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        for name, function, description in commands_data:
            desktop_kb, laptop_kb = cmd_bindings.get(name, (None, None))
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=desktop_kb,
                    laptop_keybinding=laptop_kb,
                )
            )
            if name in braille_bindings:
                bb = braille_bindings[name]
                # All flat review braille commands are navigation and should execute in learn mode
                manager.add_command(
                    command_manager.BrailleCommand(
                        name,
                        function,
                        group_label,
                        description,
                        braille_bindings=bb,
                        executes_in_learn_mode=True,
                    )
                )

        msg = "FLAT REVIEW PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

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
                self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW
            )

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
        if (
            mode != focus_manager.FLAT_REVIEW
            and obj != self._context.get_current_object()
            and not self._restrict
        ):
            tokens = [
                "FLAT REVIEW PRESENTER: Attempting to update location from",
                self._context.get_current_object(),
                "to",
                obj,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._context.set_current_to_zone_with_object(obj)

        # If we are restricting, and the current mode is not flat review, calculate a new context
        if self._restrict and mode != focus_manager.FLAT_REVIEW:
            msg = "FLAT REVIEW PRESENTER: Creating new restricted context."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._context = flat_review.Context(script, obj)

        return self._context

    def start(
        self, script: default.Script | None = None, event: input_event.InputEvent | None = None
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

        if speech_presenter.get_presenter().use_verbose_speech():
            presentation_manager.get_manager().present_message(messages.FLAT_REVIEW_START)
        self._item_presentation(script, event)

    def quit(
        self, script: default.Script | None = None, event: input_event.InputEvent | None = None
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

        if speech_presenter.get_presenter().use_verbose_speech():
            presentation_manager.get_manager().present_message(messages.FLAT_REVIEW_STOP)
        script.update_braille(focus)

    @dbus_service.command
    def toggle_flat_review_mode(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Toggles between flat review mode and focus tracking mode."""

        tokens = [
            "FLAT REVIEW PRESENTER: toggle_flat_review_mode. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Moves to the top left of the current window."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_home. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Moves to the bottom right of the current window."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_end. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Moves to the bottom left of the current window."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_bottom_left. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous line."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_previous_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Presents the current line."""

        tokens = [
            "FLAT REVIEW PRESENTER: present_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._line_presentation(script, event, 1)
        return True

    @dbus_service.command
    def go_next_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next line."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_next_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Presents the current line letter by letter."""

        tokens = [
            "FLAT REVIEW PRESENTER: spell_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._line_presentation(script, event, 2)
        return True

    @dbus_service.command
    def phonetic_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the current line letter by letter phonetically."""

        tokens = [
            "FLAT REVIEW PRESENTER: phonetic_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._line_presentation(script, event, 3)
        return True

    @dbus_service.command
    def go_start_of_line(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the beginning of the current line."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_start_of_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Moves to the end of the line."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_end_of_line. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous item or word."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_previous_item. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Presents the current item/word."""

        tokens = [
            "FLAT REVIEW PRESENTER: present_item. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._item_presentation(script, event, 1)
        return True

    @dbus_service.command
    def go_next_item(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next item or word."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_next_item. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Presents the current item/word letter by letter."""

        tokens = [
            "FLAT REVIEW PRESENTER: spell_item. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._item_presentation(script, event, 2)
        return True

    @dbus_service.command
    def phonetic_item(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the current word letter by letter phonetically."""

        tokens = [
            "FLAT REVIEW PRESENTER: phonetic_item. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._item_presentation(script, event, 3)
        return True

    @dbus_service.command
    def go_previous_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the previous character."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_previous_character. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Presents the current character."""

        tokens = [
            "FLAT REVIEW PRESENTER: present_character. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._character_presentation(script, event, 1)
        return True

    @dbus_service.command
    def go_next_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the next character."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_next_character. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Presents the current character phonetically."""

        tokens = [
            "FLAT REVIEW PRESENTER: spell_character. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._character_presentation(script, event, 2)
        return True

    @dbus_service.command
    def unicode_current_character(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the current character's unicode value."""

        tokens = [
            "FLAT REVIEW PRESENTER: unicode_current_character. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._character_presentation(script, event, 3)
        return True

    @dbus_service.command
    def go_above(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the character above."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_above. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Moves to the character below."""

        tokens = [
            "FLAT REVIEW PRESENTER: go_below. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> Atspi.Accessible:
        """Returns the current accessible object."""

        tokens = [
            "FLAT REVIEW PRESENTER: get_current_object. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        return self._context.get_current_object()

    @dbus_service.command
    def present_object(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the current accessible object."""

        tokens = [
            "FLAT REVIEW PRESENTER: present_object. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._context = self.get_or_create_context(script)
        if not isinstance(event, input_event.BrailleEvent):
            script.present_object(self._context.get_current_object(), speechonly=True)

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW
        )
        return True

    @dbus_service.command
    def left_click_on_object(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Attempts to synthesize a left click on the current accessible."""

        tokens = [
            "FLAT REVIEW PRESENTER: left_click_on_object. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Attempts to synthesize a right click on the current accessible."""

        tokens = [
            "FLAT REVIEW PRESENTER: right_click_on_object. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Routes the mouse pointer to the current accessible."""

        tokens = [
            "FLAT REVIEW PRESENTER: route_pointer_to_object. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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

        braille_presenter.get_presenter().present_regions(
            list(regions),
            focused_region,
        )

    def pan_braille_left(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Pans the braille display left."""

        self._context = self.get_or_create_context(script)

        # Try to pan left. If we couldn't (at edge), move to previous line.
        if not braille_presenter.get_presenter().pan_left():
            self._context.go_to_start_of(flat_review.Context.LINE)
            self._context.go_previous_character()
            self._update_braille(script)
            return True

        # After panning, find a region that has a zone attribute to sync flat review context.
        # We do cell-by-cell panning here because not all braille regions have zones (e.g.,
        # buttons don't have zones, only text regions do). This finds the first region with
        # a zone so we can update the flat review position accordingly.
        region_info = braille.get_region_at_cell(1)
        braille_region = region_info.region
        offset_in_zone = region_info.offset_in_region
        while braille_region and not hasattr(braille_region, "zone"):
            # Cell-by-cell panning (amount=1) to find the first region with a zone attribute.
            if not braille.pan_left(1):
                break
            region_info = braille.get_region_at_cell(1)
            braille_region = region_info.region
            offset_in_zone = region_info.offset_in_region

        if braille_region and not hasattr(braille_region, "zone"):
            self._context.go_to_start_of(flat_review.Context.LINE)
            self._context.go_previous_character()
        elif braille_region and hasattr(braille_region, "zone"):
            self._context.set_current_zone(braille_region.zone, offset_in_zone)

        self._update_braille(script)
        return True

    def pan_braille_right(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Pans the braille display right."""

        self._context = self.get_or_create_context(script)

        # Try to pan right. If we couldn't (at edge), move to next line.
        if not braille_presenter.get_presenter().pan_right():
            self._context.go_next_line()
            self._update_braille(script)
            return True

        # After panning, find a region that has a zone attribute to sync flat review context.
        # We do cell-by-cell panning here because not all braille regions have zones (e.g.,
        # buttons don't have zones, only text regions do). This finds the first region with
        # a zone so we can update the flat review position accordingly.
        region_info = braille.get_region_at_cell(1)
        braille_region = region_info.region
        offset_in_zone = region_info.offset_in_region
        while braille_region and not hasattr(braille_region, "zone"):
            # Cell-by-cell panning (amount=1) to find the first region with a zone attribute.
            if not braille.pan_right(1):
                break
            region_info = braille.get_region_at_cell(1)
            braille_region = region_info.region
            offset_in_zone = region_info.offset_in_region

        if braille_region and not hasattr(braille_region, "zone"):
            self._context.go_next_line()
        elif braille_region and hasattr(braille_region, "zone"):
            self._context.set_current_zone(braille_region.zone, offset_in_zone)

        self._update_braille(script)
        return True

    def _get_all_lines(
        self, script: default.Script, _event: input_event.InputEvent | None = None
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
        notify_user: bool = True,
    ) -> bool:
        """Speaks the contents of the entire window."""

        tokens = [
            "FLAT REVIEW PRESENTER: say_all. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for string in self._get_all_lines(script, event)[0]:
            if not string.isspace():
                presentation_manager.get_manager().speak_message(
                    string, script.speech_generator.voice(string=string)
                )

        return True

    @dbus_service.command
    def show_contents(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Displays the entire flat review contents in a text view."""

        tokens = [
            "FLAT REVIEW PRESENTER: show_contents. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
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
        notify_user: bool = True,
    ) -> bool:
        """Copies the string just presented to the clipboard."""

        tokens = [
            "FLAT REVIEW PRESENTER: copy_to_clipboard. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.is_active():
            if notify_user:
                presentation_manager.get_manager().present_message(messages.FLAT_REVIEW_NOT_IN)
            return True

        clipboard.get_presenter().set_text(self._current_contents.rstrip("\n"))
        if notify_user:
            presentation_manager.get_manager().present_message(messages.FLAT_REVIEW_COPIED)
        return True

    @dbus_service.command
    def append_to_clipboard(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Appends the string just presented to the clipboard."""

        tokens = [
            "FLAT REVIEW PRESENTER: append_to_clipboard. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.is_active():
            if notify_user:
                presentation_manager.get_manager().present_message(messages.FLAT_REVIEW_NOT_IN)
            return True

        clipboard.get_presenter().append_text(self._current_contents.rstrip("\n"))
        if notify_user:
            presentation_manager.get_manager().present_message(messages.FLAT_REVIEW_APPENDED)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="restricted",
        schema="flat-review",
        gtype="b",
        default=False,
        summary="Restrict flat review to current object",
        settings_key="flatReviewIsRestricted",
    )
    @dbus_service.getter
    def get_is_restricted(self) -> bool:
        """Returns whether flat review is restricted to the current object."""

        return self._get_setting("restricted", settings.flatReviewIsRestricted)

    @dbus_service.setter
    def set_is_restricted(self, value: bool) -> bool:
        """Sets whether flat review is restricted to the current object."""

        msg = f"FLAT REVIEW PRESENTER: Setting is-restricted to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "restricted", value)
        return True

    @dbus_service.command
    def toggle_restrict(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles the restricting of flat review to the current object."""

        tokens = [
            "FLAT REVIEW PRESENTER: toggle_restrict. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._restrict = not self._restrict
        self.set_is_restricted(self._restrict)

        if self._restrict:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.FLAT_REVIEW_RESTRICTED)
        else:
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.FLAT_REVIEW_UNRESTRICTED
                )
        if self.is_active():
            # Reset the context
            self._context = None
            self.start()

        return True

    def _line_presentation(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        speech_type: int = 1,
    ) -> bool:
        """Presents the current line."""

        self._context = self.get_or_create_context(script)
        line_string = self._context.get_current_line_string()
        voice = script.speech_generator.voice(string=line_string)

        if not isinstance(event, input_event.BrailleEvent):
            presenter = presentation_manager.get_manager()
            if not line_string or line_string == "\n":
                presenter.speak_message(messages.BLANK)
            elif line_string.isspace():
                presenter.speak_message(messages.WHITE_SPACE)
            elif line_string.isupper() and (speech_type < 2 or speech_type > 3):
                presenter.speak_message(line_string, voice)
            elif speech_type == 2:
                presenter.spell_item(line_string)
            elif speech_type == 3:
                presenter.spell_phonetically(line_string)
            else:
                manager = speech_presenter.get_presenter()
                line_string = manager.adjust_for_presentation(
                    self._context.get_current_object(), line_string
                )
                presenter.speak_message(line_string, voice)

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW
        )
        self._update_braille(script)
        self._current_contents = line_string
        return True

    def _item_presentation(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        speech_type: int = 1,
    ) -> bool:
        """Presents the current item/word."""

        self._context = self.get_or_create_context(script)
        word_string = self._context.get_current_word_string()
        voice = script.speech_generator.voice(string=word_string)
        if not isinstance(event, input_event.BrailleEvent):
            presenter = presentation_manager.get_manager()
            if not word_string or word_string == "\n":
                presenter.speak_message(messages.BLANK)
            else:
                line_string = self._context.get_current_line_string()
                if line_string == "\n":
                    presenter.speak_message(messages.BLANK)
                elif word_string.isspace():
                    presenter.speak_message(messages.WHITE_SPACE)
                elif word_string.isupper() and speech_type == 1:
                    presenter.speak_message(word_string, voice)
                elif speech_type == 2:
                    presenter.spell_item(word_string)
                elif speech_type == 3:
                    presenter.spell_phonetically(word_string)
                elif speech_type == 1:
                    manager = speech_presenter.get_presenter()
                    word_string = manager.adjust_for_presentation(
                        self._context.get_current_object(), word_string
                    )
                    presenter.speak_message(word_string, voice)

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW
        )
        self._update_braille(script)
        self._current_contents = word_string
        return True

    def _character_presentation(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        speech_type: int = 1,
    ) -> bool:
        """Presents the current character."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not self._context and AXObject.supports_text(focus):
            char_string = AXText.get_character_at_offset(focus)[0]
        else:
            self._context = self.get_or_create_context(script)
            char_string = self._context.get_current_character_string()
        if not isinstance(event, input_event.BrailleEvent):
            presenter = presentation_manager.get_manager()
            if not char_string:
                presenter.speak_message(messages.BLANK)
            else:
                if char_string == "\n" and speech_type != 3:
                    presenter.speak_message(messages.BLANK)
                elif speech_type == 3:
                    presenter.speak_message(messages.UNICODE % f"{ord(char_string):04x}")
                elif speech_type == 2:
                    presenter.spell_phonetically(char_string)
                else:
                    presenter.speak_character(char_string)

        if not self._context:
            return True

        focus_manager.get_manager().emit_region_changed(
            self._context.get_current_object(), mode=focus_manager.FLAT_REVIEW
        )
        self._update_braille(script)
        self._current_contents = char_string
        return True


class FlatReviewContextGUI:
    """Presents the entire flat review context in a text view"""

    def __init__(
        self, script: default.Script, title: str, text: str, location: tuple[int, int, int, int]
    ) -> None:
        self._script: default.Script = script
        self._gui: Gtk.Dialog = self._create_dialog(title, text, location)

    def _create_dialog(
        self, title: str, text: str, location: tuple[int, int, int, int]
    ) -> Gtk.Dialog:
        """Creates the dialog."""

        dialog = Gtk.Dialog(
            title, None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        )
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
        scrolled_window.add(textview)  # pylint: disable=no-member
        dialog.get_content_area().pack_start(scrolled_window, True, True, 0)
        dialog.connect("response", self.on_response)
        return dialog

    def on_response(self, _dialog: Gtk.Dialog, response: Gtk.ResponseType) -> None:
        """Handler for the 'response' signal of the dialog."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()

    def show_gui(self) -> None:
        """Shows the dialog."""

        self._gui.show_all()  # pylint: disable=no-member
        self._gui.present_with_time(time.time())


_presenter: FlatReviewPresenter = FlatReviewPresenter()


def get_presenter() -> FlatReviewPresenter:
    """Returns the Flat Review Presenter"""

    return _presenter
