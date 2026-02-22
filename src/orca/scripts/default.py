# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2011-2025 Igalia, S.L.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods

"""The default Script for presenting information to the user."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from orca import (
    action_presenter,
    ax_event_synthesizer,
    braille,
    braille_presenter,
    bypass_mode_manager,
    caret_navigator,
    chat_presenter,
    clipboard,
    cmdnames,
    command_manager,
    debug,
    debugging_tools_manager,
    document_presenter,
    event_manager,
    flat_review_finder,
    flat_review_presenter,
    focus_manager,
    guilabels,
    input_event,
    input_event_manager,
    keybindings,
    learn_mode_presenter,
    live_region_presenter,
    messages,
    mouse_review,
    notification_presenter,
    object_navigator,
    orca,
    orca_gui_prefs,
    presentation_manager,
    profile_manager,
    say_all_presenter,
    script,
    script_manager,
    sleep_mode_manager,
    speech_manager,
    speech_presenter,
    spellcheck_presenter,
    structural_navigator,
    system_information_presenter,
    table_navigator,
    typing_echo_presenter,
    where_am_i_presenter,
)
from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_event import TextEventReason
from orca.ax_value import AXValue

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    gi.require_version("Atspi", "2.0")
    gi.require_version("Gtk", "3.0")
    from gi.repository import Atspi, Gtk


class Script(script.Script):
    """The default Script for presenting information to the user."""

    _commands_initialized: bool = False

    def _get_all_extensions(self) -> list[tuple[Callable, str]]:
        """Returns (extension_getter, localized_name) for each extension."""

        return [
            (braille_presenter.get_presenter, guilabels.BRAILLE),
            (notification_presenter.get_presenter, guilabels.KB_GROUP_NOTIFICATIONS),
            (clipboard.get_presenter, guilabels.KB_GROUP_CLIPBOARD),
            (command_manager.get_manager, guilabels.KB_GROUP_DEFAULT),
            (say_all_presenter.get_presenter, guilabels.KB_GROUP_DEFAULT),
            (typing_echo_presenter.get_presenter, guilabels.KB_GROUP_DEFAULT),
            (speech_manager.get_manager, guilabels.KB_GROUP_SPEECH_VERBOSITY),
            (speech_presenter.get_presenter, guilabels.KB_GROUP_SPEECH_VERBOSITY),
            (bypass_mode_manager.get_manager, guilabels.KB_GROUP_DEFAULT),
            (sleep_mode_manager.get_manager, guilabels.KB_GROUP_SLEEP_MODE),
            (system_information_presenter.get_presenter, guilabels.KB_GROUP_SYSTEM_INFORMATION),
            (object_navigator.get_navigator, guilabels.KB_GROUP_OBJECT_NAVIGATION),
            (caret_navigator.get_navigator, guilabels.KB_GROUP_CARET_NAVIGATION),
            (structural_navigator.get_navigator, guilabels.KB_GROUP_STRUCTURAL_NAVIGATION),
            (table_navigator.get_navigator, guilabels.KB_GROUP_TABLE_NAVIGATION),
            (document_presenter.get_presenter, guilabels.KB_GROUP_DOCUMENTS),
            (live_region_presenter.get_presenter, guilabels.KB_GROUP_LIVE_REGIONS),
            (learn_mode_presenter.get_presenter, guilabels.KB_GROUP_LEARN_MODE),
            (mouse_review.get_reviewer, guilabels.KB_GROUP_MOUSE_REVIEW),
            (action_presenter.get_presenter, guilabels.KB_GROUP_ACTIONS),
            (flat_review_presenter.get_presenter, guilabels.KB_GROUP_FLAT_REVIEW),
            (flat_review_finder.get_finder, guilabels.KB_GROUP_FIND),
            (where_am_i_presenter.get_presenter, guilabels.KB_GROUP_WHERE_AM_I),
            (debugging_tools_manager.get_manager, guilabels.KB_GROUP_DEBUGGING_TOOLS),
            (chat_presenter.get_presenter, guilabels.KB_GROUP_CHAT),
            (profile_manager.get_manager, guilabels.GENERAL_PROFILES),
        ]

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        tokens = ["DEFAULT: Setting up commands for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if Script._commands_initialized:
            msg = "DEFAULT: Commands already initialized."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        Script._commands_initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_DEFAULT

        kb_kp_divide_orca = keybindings.KeyBinding("KP_Divide", keybindings.ORCA_MODIFIER_MASK)
        kb_kp_divide = keybindings.KeyBinding("KP_Divide", keybindings.NO_MODIFIER_MASK)
        kb_kp_multiply = keybindings.KeyBinding("KP_Multiply", keybindings.NO_MODIFIER_MASK)
        kb_9_orca = keybindings.KeyBinding("9", keybindings.ORCA_MODIFIER_MASK)
        kb_7_orca = keybindings.KeyBinding("7", keybindings.ORCA_MODIFIER_MASK)
        kb_8_orca = keybindings.KeyBinding("8", keybindings.ORCA_MODIFIER_MASK)
        kb_space_orca = keybindings.KeyBinding("space", keybindings.ORCA_MODIFIER_MASK)
        kb_space_ctrl_orca = keybindings.KeyBinding("space", keybindings.ORCA_CTRL_MODIFIER_MASK)

        script_commands: list[
            tuple[
                str,
                Callable[..., bool],
                str,
                keybindings.KeyBinding | None,
                keybindings.KeyBinding | None,
            ]
        ] = [
            (
                "routePointerToItemHandler",
                self.route_pointer_to_item,
                cmdnames.ROUTE_POINTER_TO_ITEM,
                kb_kp_divide_orca,
                kb_9_orca,
            ),
            (
                "leftClickReviewItemHandler",
                self.left_click_item,
                cmdnames.LEFT_CLICK_REVIEW_ITEM,
                kb_kp_divide,
                kb_7_orca,
            ),
            (
                "rightClickReviewItemHandler",
                self.right_click_item,
                cmdnames.RIGHT_CLICK_REVIEW_ITEM,
                kb_kp_multiply,
                kb_8_orca,
            ),
            (
                "panBrailleLeftHandler",
                self.pan_braille_left,
                cmdnames.PAN_BRAILLE_LEFT,
                None,
                None,
            ),
            (
                "panBrailleRightHandler",
                self.pan_braille_right,
                cmdnames.PAN_BRAILLE_RIGHT,
                None,
                None,
            ),
            (
                "contractedBrailleHandler",
                self.set_contracted_braille,
                cmdnames.SET_CONTRACTED_BRAILLE,
                None,
                None,
            ),
            ("shutdownHandler", self.quit_orca, cmdnames.QUIT_ORCA, None, None),
            (
                "preferencesSettingsHandler",
                self.show_preferences_gui,
                cmdnames.SHOW_PREFERENCES_GUI,
                kb_space_orca,
                kb_space_orca,
            ),
            (
                "appPreferencesSettingsHandler",
                self.show_app_preferences_gui,
                cmdnames.SHOW_APP_PREFERENCES_GUI,
                kb_space_ctrl_orca,
                kb_space_ctrl_orca,
            ),
        ]

        for (
            name,
            function,
            description,
            desktop_kb,
            laptop_kb,
        ) in script_commands:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=desktop_kb,
                    laptop_keybinding=laptop_kb,
                ),
            )

        braille_bindings: dict[str, tuple[int, ...]] = {}
        left_keys = tuple(
            key
            for key in (
                braille.BRLAPI_KEY_CMD_HWINLT,
                braille.BRLAPI_KEY_CMD_FWINLT,
                braille.BRLAPI_KEY_CMD_FWINLTSKIP,
            )
            if key is not None
        )
        right_keys = tuple(
            key
            for key in (
                braille.BRLAPI_KEY_CMD_HWINRT,
                braille.BRLAPI_KEY_CMD_FWINRT,
                braille.BRLAPI_KEY_CMD_FWINRTSKIP,
            )
            if key is not None
        )
        if left_keys:
            braille_bindings["panBrailleLeftHandler"] = left_keys
        if right_keys:
            braille_bindings["panBrailleRightHandler"] = right_keys

        single_key_bindings: list[tuple[str, int | None]] = [
            ("goBrailleHomeHandler", braille.BRLAPI_KEY_CMD_HOME),
            ("contractedBrailleHandler", braille.BRLAPI_KEY_CMD_SIXDOTS),
            ("processRoutingKeyHandler", braille.BRLAPI_KEY_CMD_ROUTE),
            ("processBrailleCutBeginHandler", braille.BRLAPI_KEY_CMD_CUTBEGIN),
            ("processBrailleCutLineHandler", braille.BRLAPI_KEY_CMD_CUTLINE),
        ]
        for handler_name, key in single_key_bindings:
            if key is not None:
                braille_bindings[handler_name] = (key,)
        if not braille_bindings:
            msg = "DEFAULT: Braille bindings unavailable."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        braille_commands: list[tuple[str, Callable[..., bool], str, bool]] = [
            ("panBrailleLeftHandler", self.pan_braille_left, cmdnames.PAN_BRAILLE_LEFT, True),
            ("panBrailleRightHandler", self.pan_braille_right, cmdnames.PAN_BRAILLE_RIGHT, True),
            (
                "contractedBrailleHandler",
                self.set_contracted_braille,
                cmdnames.SET_CONTRACTED_BRAILLE,
                True,
            ),
            ("goBrailleHomeHandler", self.go_braille_home, cmdnames.GO_BRAILLE_HOME, True),
            (
                "processRoutingKeyHandler",
                self.process_routing_key,
                cmdnames.PROCESS_ROUTING_KEY,
                False,
            ),
            (
                "processBrailleCutBeginHandler",
                self.process_braille_cut_begin,
                cmdnames.PROCESS_BRAILLE_CUT_BEGIN,
                False,
            ),
            (
                "processBrailleCutLineHandler",
                self.process_braille_cut_line,
                cmdnames.PROCESS_BRAILLE_CUT_LINE,
                False,
            ),
        ]

        for name, function, description, executes_in_learn_mode in braille_commands:
            bb = braille_bindings.get(name, ())
            manager.add_command(
                command_manager.BrailleCommand(
                    name,
                    function,
                    group_label,
                    description,
                    braille_bindings=bb,
                    executes_in_learn_mode=executes_in_learn_mode,
                ),
            )

        for extension_getter, _localized_name in self._get_all_extensions():
            extension_getter().set_up_commands()

        all_braille_keys: set[int] = set()
        for cmd in manager.get_all_braille_commands():
            all_braille_keys.update(cmd.get_braille_bindings())
        braille.setup_key_ranges(all_braille_keys)

        cmd_count = len(command_manager.get_manager().get_all_keyboard_commands())
        msg = f"DEFAULT: Commands set up: {cmd_count} keyboard commands"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_app_preferences_gui(self) -> Gtk.Grid | None:
        """Return a GtkGrid, or None if there's no app-specific UI."""

        return None

    def get_preferences_from_gui(self) -> dict:
        """Returns a dictionary with the app-specific preferences."""

        return {}

    def register_event_listeners(self) -> None:
        """Registers for listeners needed by this script."""

        event_manager.get_manager().register_script_listeners(self)

    def deregister_event_listeners(self) -> None:
        """De-registers the listeners needed by this script."""

        event_manager.get_manager().deregister_script_listeners(self)

    def _get_queued_event(
        self,
        event_type: str,
        detail1: int | None = None,
        detail2: int | None = None,
        any_data=None,
    ) -> Atspi.Event | None:
        cached_event = self.event_cache.get(event_type, [None, 0])[0]
        if not cached_event:
            tokens = ["SCRIPT: No queued event of type", event_type]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail1 is not None and detail1 != cached_event.detail1:
            tokens = [
                "SCRIPT: Queued event's detail1 (",
                str(cached_event.detail1),
                ") doesn't match",
                str(detail1),
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail2 is not None and detail2 != cached_event.detail2:
            tokens = [
                "SCRIPT: Queued event's detail2 (",
                str(cached_event.detail2),
                ") doesn't match",
                str(detail2),
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if any_data is not None and any_data != cached_event.any_data:
            tokens = [
                "SCRIPT: Queued event's any_data (",
                cached_event.any_data,
                ") doesn't match",
                any_data,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        tokens = ["SCRIPT: Found matching queued event:", cached_event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cached_event

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Called when the visual object with focus changes."""

        if not self.utilities.handle_undo_locus_of_focus_change():
            self.utilities.handle_paste_locus_of_focus_change()

        if not new_focus:
            return True

        if AXUtilities.is_defunct(new_focus):
            return True

        is_name_change = event and event.type.endswith("accessible-name")
        if old_focus == new_focus and not is_name_change:
            msg = "DEFAULT: old focus == new focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.run_find_command_on:
            if self.run_find_command_on == new_focus:
                self.run_find_command_on = None
                flat_review_finder.get_finder().find(self)
            return True

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().quit()

        if learn_mode_presenter.get_presenter().is_active():
            learn_mode_presenter.get_presenter().quit()

        document_presenter.get_presenter().update_mode_if_needed(self, old_focus, new_focus)

        active_window = self.utilities.top_level_object(new_focus)
        focus_manager.get_manager().set_active_window(active_window)
        if old_focus is None:
            old_focus = active_window

        if self.utilities.should_interrupt_for_locus_of_focus_change(old_focus, new_focus, event):
            presentation_manager.get_manager().interrupt_presentation()
        presentation_manager.get_manager().present_object(self, new_focus, priorObj=old_focus)
        return True

    def activate(self) -> None:
        """Called when this script is activated."""

        tokens = ["DEFAULT: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not focus_manager.get_manager().is_in_preferences_window():
            speech_manager.get_manager().update_punctuation_level()
            speech_manager.get_manager().update_capitalization_style()
            speech_manager.get_manager().update_synthesizer()

        presenter = document_presenter.get_presenter()
        if presenter.has_state_for_app(self.app):
            presenter.restore_mode_for_script(self)
        else:
            reason = "script activation, no prior state"
            presenter.suspend_navigators(self, False, reason)
            structural_navigator.get_navigator().set_mode(self, self._default_sn_mode)
            caret_navigator.get_navigator().set_enabled_for_script(
                self,
                self._default_caret_navigation_enabled,
            )

        command_manager.get_manager().activate_commands(f"activated {self.name}")

    def deactivate(self) -> None:
        """Called when this script is deactivated."""

        self.point_of_reference = {}
        if bypass_mode_manager.get_manager().is_active():
            bypass_mode_manager.get_manager().toggle_enabled(self)

    def update_braille(self, obj: Atspi.Accessible, **args) -> None:
        """Updates the braille display to show obj."""

        if not obj:
            return
        braille_presenter.get_presenter().present_generated_braille(self, obj, **args)

    ########################################################################
    #                                                                      #
    # INPUT EVENT HANDLERS (AKA ORCA COMMANDS)                             #
    #                                                                      #
    ########################################################################

    def show_app_preferences_gui(
        self,
        current_script: Script | None = None,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Shows the app Preferences dialog."""

        current_script = current_script or self
        ui = orca_gui_prefs.OrcaSetupGUI(current_script)
        ui.show_gui()
        return True

    def show_preferences_gui(
        self,
        _script: Script | None = None,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Displays the Preferences dialog."""

        ui = orca_gui_prefs.OrcaSetupGUI(script_manager.get_manager().get_default_script())
        ui.show_gui()
        return True

    def quit_orca(
        self,
        _script: Script | None = None,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Quit Orca."""

        orca.shutdown()
        return True

    def pan_braille_left(
        self,
        current_script: Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Pans the braille display to the left."""

        if (
            isinstance(event, input_event.KeyboardEvent)
            and not braille_presenter.get_presenter().use_braille()
        ):
            msg = "DEFAULT: panBrailleLeft command requires braille or braille monitor"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        target = current_script or self
        if target is not self:
            return target.pan_braille_left(target, event)

        tokens = ["DEFAULT: pan_braille_left using", target]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._pan_braille_left(event)

    def _pan_braille_left(self, event: input_event.InputEvent | None = None) -> bool:
        """Pans the braille display to the left."""

        if flat_review_presenter.get_presenter().is_active():
            return flat_review_presenter.get_presenter().pan_braille_left(self, event)

        presenter = braille_presenter.get_presenter()
        if presenter.pan_left():
            return True

        # Couldn't pan (at edge). For text areas, move caret to get more content.
        focus = focus_manager.get_manager().get_locus_of_focus()
        is_text_area = AXUtilities.is_editable(focus) or AXUtilities.is_terminal(focus)
        if not is_text_area:
            return True

        start_offset = AXText.get_line_at_offset(focus)[1]
        moved_caret = False
        if start_offset > 0:
            moved_caret = AXText.set_caret_offset(focus, start_offset - 1)

        # If we didn't move the caret and we're in a terminal, we
        # jump into flat review to review the text.  See
        # http://bugzilla.gnome.org/show_bug.cgi?id=482294.
        if not moved_caret and AXUtilities.is_terminal(focus):
            flat_review_presenter.get_presenter().go_start_of_line(self, event)
            flat_review_presenter.get_presenter().go_previous_character(self, event)

        return True

    def pan_braille_right(
        self,
        current_script: Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Pans the braille display to the right."""

        if (
            isinstance(event, input_event.KeyboardEvent)
            and not braille_presenter.get_presenter().use_braille()
        ):
            msg = "DEFAULT: panBrailleRight command requires braille or braille monitor"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        target = current_script or self
        if target is not self:
            return target.pan_braille_right(target, event)

        tokens = ["DEFAULT: pan_braille_right using", target]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._pan_braille_right(event)

    def _pan_braille_right(self, event: input_event.InputEvent | None = None) -> bool:
        """Pans the braille display to the right."""

        if flat_review_presenter.get_presenter().is_active():
            return flat_review_presenter.get_presenter().pan_braille_right(self, event)

        presenter = braille_presenter.get_presenter()
        if presenter.pan_right():
            return True

        # Couldn't pan (at edge). For text areas, move caret to get more content.
        focus = focus_manager.get_manager().get_locus_of_focus()
        is_text_area = AXUtilities.is_editable(focus) or AXUtilities.is_terminal(focus)
        if not is_text_area:
            return True

        end_offset = AXText.get_line_at_offset(focus)[2]
        if end_offset < AXText.get_character_count(focus):
            AXText.set_caret_offset(focus, end_offset)

        return True

    def go_braille_home(
        self,
        _script: Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Returns to the component with focus."""

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().quit()
            return True

        presentation_manager.get_manager().interrupt_presentation()
        return braille.return_to_region_with_focus(event)

    def set_contracted_braille(
        self,
        _script: Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Toggles contracted braille."""

        braille.toggle_contracted_braille(event)
        return True

    def process_routing_key(
        self,
        _script: Script | None = None,
        event: input_event.BrailleEvent | None = None,
    ) -> bool:
        """Processes a cursor routing key."""

        # Don't kill flash here because it will restore the previous contents and
        # then process the routing key. If the contents accept a click action, this
        # would result in clicking on the link instead of clearing the flash message.
        presentation_manager.get_manager().interrupt_presentation(kill_flash=False)
        if event is None:
            return True
        braille.process_routing_key(event)
        return True

    def process_braille_cut_begin(
        self,
        _script: Script | None = None,
        event: input_event.BrailleEvent | None = None,
    ) -> bool:
        """Clears the selection and moves the caret offset in the currently
        active text area.
        """

        if event is None:
            return True
        caret_context = braille.get_caret_context(event)
        if caret_context.offset < 0:
            return True

        presentation_manager.get_manager().interrupt_presentation()
        AXText.clear_all_selected_text(caret_context.accessible)
        self.utilities.set_caret_offset(caret_context.accessible, caret_context.offset)
        return True

    def process_braille_cut_line(
        self,
        _script: Script | None = None,
        event: input_event.BrailleEvent | None = None,
    ) -> bool:
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        if event is None:
            return True
        caret_context = braille.get_caret_context(event)
        if caret_context.offset < 0:
            return True

        presentation_manager.get_manager().interrupt_presentation()
        start_offset = AXText.get_selection_start_offset(caret_context.accessible)
        end_offset = AXText.get_selection_end_offset(caret_context.accessible)
        if start_offset < 0 or end_offset < 0:
            caret_offset = AXText.get_caret_offset(caret_context.accessible)
            start_offset = min(caret_context.offset, caret_offset)
            end_offset = max(caret_context.offset, caret_offset)

        AXText.set_selected_text(caret_context.accessible, start_offset, end_offset)
        text = AXText.get_selected_text(caret_context.accessible)[0]
        clipboard.get_presenter().set_text(text)
        return True

    def route_pointer_to_item(
        self,
        _script: Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Moves the mouse pointer to the current item."""

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().route_pointer_to_object(self, event)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if ax_event_synthesizer.get_synthesizer().route_to_character(
            focus,
        ) or ax_event_synthesizer.get_synthesizer().route_to_object(focus):
            presentation_manager.get_manager().present_message(messages.MOUSE_MOVED_SUCCESS)
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        presentation_manager.get_manager().present_message(full, brief)
        return False

    def left_click_item(
        self,
        _script: Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Performs a left mouse button click on the current item."""

        if flat_review_presenter.get_presenter().is_active():
            obj = flat_review_presenter.get_presenter().get_current_object(self, event)
            if ax_event_synthesizer.get_synthesizer().try_all_clickable_actions(obj):
                return True
            return flat_review_presenter.get_presenter().left_click_on_object(self, event)

        focus = focus_manager.get_manager().get_locus_of_focus()
        if ax_event_synthesizer.get_synthesizer().try_all_clickable_actions(focus):
            return True

        if AXText.get_character_count(focus):
            if ax_event_synthesizer.get_synthesizer().click_character(focus, None, 1):
                return True

        if ax_event_synthesizer.get_synthesizer().click_object(focus, 1):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        presentation_manager.get_manager().present_message(full, brief)
        return False

    def right_click_item(
        self,
        _script: Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Performs a right mouse button click on the current item."""

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().right_click_on_object(self, event)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if ax_event_synthesizer.get_synthesizer().click_character(focus, None, 3):
            return True

        if ax_event_synthesizer.get_synthesizer().click_object(focus, 3):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        presentation_manager.get_manager().present_message(full, brief)
        return False

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    # Event handlers return bool:                                          #
    # - True: Event was fully handled, no further processing needed        #
    # - False: Event wasn't handled, should be passed to parent handlers   #
    # Default return value is True (event handled by default script)       #
    #                                                                      #
    ########################################################################

    def on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        window = event.source
        if AXUtilities.is_dialog_or_alert(window) or AXUtilities.is_frame(window):
            if event.detail1 and not AXUtilities.can_be_active_window(window):
                return True

            source_is_active_window = window == focus_manager.get_manager().get_active_window()
            if source_is_active_window and not event.detail1:
                focus = focus_manager.get_manager().get_locus_of_focus()
                if AXObject.find_ancestor_inclusive(focus, AXUtilities.is_menu):
                    msg = "DEFAULT: Ignoring event. In menu."
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    return True

                msg = "DEFAULT: Event is for active window. Clearing state."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(None)
                return True

            if not source_is_active_window and event.detail1:
                msg = "DEFAULT: Updating active window."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(
                    window,
                    set_window_as_focus=True,
                    notify_script=True,
                )

        return True

    def on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:active-descendant-changed accessibility events."""

        if AXUtilities.is_presentable_active_descendant_change(event):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)

        return True

    def on_busy_changed(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for object:state-changed:busy accessibility events."""

        return True

    def on_checked_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:checked accessibility events."""

        if AXUtilities.is_presentable_checked_change(event):
            self.present_object(event.source, alreadyFocused=True, interrupt=True)

        return True

    def on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")
        return True

    def on_children_removed(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:remove accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")
        return True

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if focus != event.source:
            if not AXUtilities.is_focused(event.source):
                msg = "DEFAULT: Change is from unfocused source that is not the locus of focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            # TODO - JD: See if this can be removed. If it's still needed document why.
            manager.set_locus_of_focus(event, event.source, False)

        obj, offset = manager.get_last_cursor_position()
        if offset == event.detail1 and obj == event.source:
            msg = "DEFAULT: Event is for last saved cursor position"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().quit()

        offset = AXText.get_caret_offset(event.source)

        # TODO - JD: These need to be harmonized / unified / simplified.
        manager.set_last_cursor_position(event.source, offset)
        self.utilities.set_caret_context(event.source, offset)

        ignore = [
            TextEventReason.CUT,
            TextEventReason.PASTE,
            TextEventReason.REDO,
            TextEventReason.UNDO,
        ]
        if reason in ignore:
            msg = f"DEFAULT: Ignoring event due to reason ({reason})"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return True

        if AXText.has_selected_text(event.source):
            msg = "DEFAULT: Event source has text selections"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.utilities.handle_text_selection_change(event.source)
            return True

        text, _start, _end = AXText.get_cached_selected_text(obj)
        if text and self.utilities.handle_text_selection_change(obj):
            msg = "DEFAULT: Event handled as text selection change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "DEFAULT: Presenting text at new caret position"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._present_caret_moved_event(event, reason=reason)
        return True

    def on_description_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-description events."""

        if AXUtilities.is_presentable_description_change(event):
            presentation_manager.get_manager().present_message(event.any_data)
        return True

    def on_document_attributes_changed(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for document:attributes-changed accessibility events."""

        return True

    def on_document_reload(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for document:reload accessibility events."""

        return True

    def on_document_load_complete(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for document:load-complete accessibility events."""

        return True

    def on_document_load_stopped(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for document:load-stopped accessibility events."""

        return True

    def on_document_page_changed(self, event: Atspi.Event) -> bool:
        """Callback for document:page-changed accessibility events."""

        if event.detail1 < 0:
            return True

        if not AXDocument.did_page_change(event.source):
            return True

        presentation_manager.get_manager().present_message(messages.PAGE_NUMBER % event.detail1)
        return True

    def on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "expanded-changed event.")
        if not AXUtilities.is_presentable_expanded_change(event):
            return True

        self.present_object(event.source, alreadyFocused=True, interrupt=True)
        details = self.utilities.details_content_for_object(event.source)
        for detail in details:
            presentation_manager.get_manager().speak_message(detail)

        return True

    def on_indeterminate_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:indeterminate accessibility events."""

        if AXUtilities.is_presentable_indeterminate_change(event):
            self.present_object(event.source, alreadyFocused=True, interrupt=True)

        return True

    def on_invalid_entry_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:invalid-entry accessibility events."""

        if not AXUtilities.is_presentable_invalid_entry_change(event):
            return True

        if event.detail1:
            msg = self.get_speech_generator().get_error_message(event.source)
        else:
            msg = messages.INVALID_ENTRY_FIXED
        presentation_manager.get_manager().speak_message(msg)
        self.update_braille(event.source)
        return True

    def on_mouse_button(self, event: Atspi.Event) -> bool:
        """Callback for mouse:button events."""

        input_event_manager.get_manager().process_mouse_button_event(event)
        return True

    def on_announcement(self, event: Atspi.Event) -> bool:
        """Callback for object:announcement events."""

        if isinstance(event.any_data, str):
            presentation_manager.get_manager().present_message(event.any_data)

        return True

    def on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        if not AXUtilities.is_presentable_name_change(event):
            return True

        manager = focus_manager.get_manager()
        if event.source == manager.get_locus_of_focus():
            # Force the update so that braille is refreshed.
            manager.set_locus_of_focus(event, event.source, True, True)
            return True

        presentation_manager.get_manager().present_message(event.any_data)
        return True

    def on_object_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:attributes-changed accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "object-attributes-changed event.")
        return True

    def on_pressed_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:pressed accessibility events."""

        if AXUtilities.is_presentable_pressed_change(event):
            self.present_object(event.source, alreadyFocused=True, interrupt=True)

        return True

    def on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        if not AXUtilities.is_presentable_selected_change(event):
            return True

        if speech_presenter.get_presenter().get_only_speak_displayed_text():
            return True

        announce_state = False
        manager = input_event_manager.get_manager()
        if manager.last_event_was_space():
            announce_state = True
        elif (
            manager.last_event_was_up() or manager.last_event_was_down()
        ) and AXUtilities.is_table_cell(event.source):
            announce_state = AXUtilities.is_selected(event.source)

        if not announce_state:
            return True

        # TODO - JD: Unlike the other state-changed callbacks, it seems unwise
        # to call generate_speech() here because that also will present the
        # expandable state if appropriate for the object type. The generators
        # need to gain some smarts w.r.t. state changes.

        if event.detail1:
            presentation_manager.get_manager().speak_message(messages.TEXT_SELECTED)
        else:
            presentation_manager.get_manager().speak_message(messages.TEXT_UNSELECTED)

        return True

    def _ignore_selection_based_on_source(
        self,
        event: Atspi.Event,
        focus: Atspi.Accessible | None,
    ) -> bool:
        """Returns True if this selection-changed event should be ignored based on its source."""

        if self.utilities.handle_paste_locus_of_focus_change():
            if self.utilities.top_level_object_is_active_and_current(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
            return False

        if self.utilities.handle_container_selection_change(
            event.source,
        ) or AXUtilities.manages_descendants(event.source):
            return True

        # There is a bug in (at least) Pidgin in which a newly-expanded submenu lacks the
        # showing and visible states. Trust selection changes from the locus of focus.
        if event.source != focus and not (
            AXUtilities.is_showing(event.source) and AXUtilities.is_visible(event.source)
        ):
            # If the current combobox is collapsed, its menu child that fired the event might
            # lack the showing and visible states. This happens in (at least) Thunderbird's
            # calendar new-appointment comboboxes. Therefore check to see if the event came
            # from the current combobox. This is necessary because (at least) VSCode's debugger
            # has some hidden menu that the user is not in which is firing this event.
            combobox = AXObject.find_ancestor(event.source, AXUtilities.is_combo_box)
            if combobox != focus and event.source != AXObject.get_parent(focus):
                tokens = ["DEFAULT: Ignoring event: source lacks showing + visible", event.source]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

        if AXUtilities.is_tree_or_tree_table(event.source):
            active_window = focus_manager.get_manager().get_active_window()
            if not AXObject.find_ancestor(event.source, lambda x: x and x == active_window):
                tokens = ["DEFAULT: Ignoring event:", event.source, "is not inside", active_window]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

        return False

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self._ignore_selection_based_on_source(event, focus):
            return True

        # If the current item's selection is toggled, we'll present that
        # via the state-changed event.
        if input_event_manager.get_manager().last_event_was_space():
            return True

        if AXUtilities.is_combo_box(event.source) and not AXUtilities.is_expanded(event.source):
            if AXUtilities.is_focused(
                AXObject.find_descendant(event.source, AXUtilities.is_text_input),
            ):
                return True
        elif (
            AXUtilities.is_page_tab_list(event.source)
            and flat_review_presenter.get_presenter().is_active()
        ):
            # If a wizard-like notebook page being reviewed changes, we might not get
            # any events to update the locusOfFocus. As a result, subsequent flat
            # review commands will continue to present the stale content.
            # TODO - JD: We can potentially do some automatic reading here.
            flat_review_presenter.get_presenter().quit()

        selected_children = self.utilities.selected_children(event.source)
        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus in selected_children:
            msg = "DEFAULT: Ignoring event believed to be redundant to focus change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        mouse_review_item = mouse_review.get_reviewer().get_current_item()
        for child in selected_children:
            if AXObject.is_ancestor(focus, child):
                tokens = ["DEFAULT: Child", child, "is ancestor of locusOfFocus"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

            if child == mouse_review_item:
                tokens = ["DEFAULT: Child", child, "is current mouse review item"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                continue

            if (
                AXUtilities.is_page_tab(child)
                and focus
                and AXObject.get_name(child) == AXObject.get_name(focus)
                and not AXUtilities.is_focused(event.source)
            ):
                tokens = ["DEFAULT:", child, "'s selection redundant to", focus]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                break

            if not AXUtilities.is_layout_only(child):
                focus_manager.get_manager().set_locus_of_focus(event, child)
                break

        return True

    def on_sensitive_changed(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for object:state-changed:sensitive accessibility events."""

        return True

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return True

        if not AXUtilities.is_focused(event.source):
            tokens = ["DEFAULT:", event.source, "lacks focused state. Clearing cache."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            AXObject.clear_cache(event.source, reason="Event detail1 does not match state.")
            if not AXUtilities.is_focused(event.source):
                msg = "DEFAULT: Clearing cache did not update state."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        obj = event.source
        window, dialog = self.utilities.frame_and_dialog(obj)
        if window and not AXUtilities.can_be_active_window(window) and not dialog:
            return True

        if AXObject.get_child_count(obj) and not AXUtilities.is_combo_box(obj):
            selected_children = self.utilities.selected_children(obj)
            if selected_children:
                obj = selected_children[0]

        focus_manager.get_manager().set_locus_of_focus(event, obj)
        return True

    def on_showing_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""

        obj = event.source
        if AXUtilities.is_notification(obj):
            if not event.detail1:
                return True

            presentation_manager.get_manager().speak_message(
                self.get_speech_generator().get_localized_role_name(obj),
            )
            msg = self.utilities.get_notification_content(obj)
            presentation_manager.get_manager().present_message(msg, reset_styles=False)
            notification_presenter.get_presenter().save_notification(msg)
            return True

        if AXUtilities.is_tool_tip(obj):
            was_f1 = input_event_manager.get_manager().last_event_was_f1()
            if not was_f1 and not mouse_review.get_reviewer().get_present_tooltips():
                return True
            if event.detail1:
                self.present_object(obj, interrupt=True)
                return True

            focus = focus_manager.get_manager().get_locus_of_focus()
            if focus and was_f1:
                obj = focus
                self.present_object(obj, priorObj=event.source, interrupt=True)
                return True

        return True

    def on_text_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-attributes-changed accessibility events."""

        if not AXUtilities.is_presentable_text_attributes_change(event):
            return True

        word, start, _end = AXText.get_word_at_offset(event.source)
        if not word.strip():
            word, start, _end = AXText.get_word_at_offset(event.source, start - 1)

        speech_pres = speech_presenter.get_presenter()
        if error := speech_pres.get_error_description(event.source, start, False):
            presentation_manager.get_manager().speak_message(error)

        return True

    def on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        if not AXUtilities.is_presentable_text_deletion(event):
            return True

        reason = AXUtilities.get_text_event_reason(event)
        self.utilities.handle_undo_text_event(event)
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_DELETION:
            msg = "DEFAULT: Deletion is believed to be due to deleting selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            presentation_manager.get_manager().present_message(messages.SELECTION_DELETED)
            AXText.update_cached_selected_text(event.source)
            return True

        text = self.utilities.deleted_text(event)
        selected_text, _start, _end = AXText.get_cached_selected_text(event.source)
        if reason == TextEventReason.DELETE:
            msg = "DEFAULT: Deletion is believed to be due to Delete command"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            text = AXText.get_character_at_offset(event.source)[0]
        elif reason == TextEventReason.BACKSPACE and text != selected_text:
            msg = "DEFAULT: Deletion is believed to be due to BackSpace command"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = "DEFAULT: Event is not being presented due to lack of cause"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if len(text) == 1:
            presentation_manager.get_manager().speak_character(text)
        else:
            presentation_manager.get_manager().speak_accessible_text(event.source, text)

        return True

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        if not AXUtilities.is_presentable_text_insertion(event):
            return True

        reason = AXUtilities.get_text_event_reason(event)
        self.utilities.handle_undo_text_event(event)
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_RESTORATION:
            msg = "DEFAULT: Insertion is believed to be due to restoring selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            presentation_manager.get_manager().present_message(messages.SELECTION_RESTORED)
            AXText.update_cached_selected_text(event.source)
            return True

        if reason == TextEventReason.LIVE_REGION_UPDATE:
            msg = "DEFAULT: Event is from live region"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            live_region_presenter.get_presenter().handle_event(self, event)
            return True

        reason_messages: dict[TextEventReason, str] = {
            TextEventReason.PAGE_SWITCH: "due to page switch",
            TextEventReason.PASTE: "due to paste",
            TextEventReason.UNSPECIFIED_COMMAND: "due to command",
            TextEventReason.MOUSE_MIDDLE_BUTTON: "due to middle mouse button",
            TextEventReason.TYPING_ECHOABLE: "echoable",
            TextEventReason.AUTO_INSERTION_PRESENTABLE: "presentable auto text event",
            TextEventReason.SELECTED_TEXT_INSERTION: "also selected",
        }
        silent_reasons = {TextEventReason.PAGE_SWITCH, TextEventReason.PASTE}
        description = reason_messages.get(reason)
        if description is not None:
            msg = f"DEFAULT: Insertion is believed to be {description}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            speak_string = reason not in silent_reasons
        else:
            msg = "DEFAULT: Not speaking inserted string due to lack of cause"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            speak_string = False

        # Because some implementations are broken.
        text = self.utilities.inserted_text(event)
        if speak_string:
            if len(text) == 1:
                presentation_manager.get_manager().speak_character(text)
            else:
                presentation_manager.get_manager().speak_accessible_text(event.source, text)

        if len(text) != 1 or reason not in [
            TextEventReason.TYPING,
            TextEventReason.TYPING_ECHOABLE,
        ]:
            return True

        presenter = typing_echo_presenter.get_presenter()
        if presenter.echo_previous_sentence(event.source):
            return True

        presenter.echo_previous_word(event.source)
        return True

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        if AXUtilities.is_focusable(event.source) and not AXUtilities.is_focused(event.source):
            msg = "DEFAULT: Ignoring event from focusable but unfocused source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        # We won't handle undo here as it can lead to double-presentation.
        # If there is an application for which text-changed events are
        # missing upon undo, handle them in an app or toolkit script.

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.UNKNOWN:
            msg = "DEFAULT: Ignoring event because reason for change is unknown"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return True
        if reason == TextEventReason.SEARCH_PRESENTABLE:
            msg = "DEFAULT: Presenting line believed to be search match"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.say_line(event.source)
            AXText.update_cached_selected_text(event.source)
            return True
        if reason == TextEventReason.SEARCH_UNPRESENTABLE:
            msg = "DEFAULT: Ignoring event believed to be unpresentable search results change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return True
        if reason in [TextEventReason.CUT, TextEventReason.BACKSPACE, TextEventReason.DELETE]:
            msg = "DEFAULT: Ignoring event believed to be text removal"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return True

        self.utilities.handle_text_selection_change(event.source)
        self.update_braille(event.source)
        return True

    def on_column_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:column-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "column-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return True

        if event.source != AXTable.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return True

        presentation_manager.get_manager().present_message(messages.TABLE_REORDERED_COLUMNS)
        return True

    def on_row_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:row-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "row-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return True

        if event.source != AXTable.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return True

        presentation_manager.get_manager().present_message(messages.TABLE_REORDERED_ROWS)
        return True

    def on_value_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-value accessibility events."""

        if not AXValue.did_value_change(event.source):
            return True

        is_progress_bar_update, msg = self.utilities.is_progress_bar_update(event.source)
        tokens = ["DEFAULT: Is progress bar update:", is_progress_bar_update, ",", msg]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = focus_manager.get_manager()
        if not is_progress_bar_update and event.source != manager.get_locus_of_focus():
            msg = "DEFAULT: Source != locusOfFocus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_spin_button(event.source):
            manager.set_last_cursor_position(event.source, AXText.get_caret_offset(event.source))

        if not is_progress_bar_update:
            presentation_manager.get_manager().interrupt_presentation()

        presentation_manager.get_manager().present_object(
            self,
            event.source,
            generate_sound=True,
            alreadyFocused=True,
            isProgressBarUpdate=is_progress_bar_update,
        )
        return True

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        if not AXUtilities.can_be_active_window(event.source):
            return True

        manager = focus_manager.get_manager()
        active_window = manager.get_active_window()
        if event.source == active_window:
            msg = "DEFAULT: Event is for active window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            spellcheck_presenter.get_presenter().handle_window_event(event, self)
            return True

        manager.set_active_window(event.source)
        if AXUtilities.is_combo_box_popup(active_window):
            return True

        self.point_of_reference = {}
        if AXObject.get_child_count(event.source) == 1:
            child = AXObject.get_child(event.source, 0)
            # Popup menus in Chromium live in a menu bar whose first child is a panel.
            if AXUtilities.is_menu_bar(child):
                child = AXObject.find_descendant(child, AXUtilities.is_menu)
            if AXUtilities.is_menu(child):
                selected_item = AXSelection.get_selected_child(child, 0)
                if AXUtilities.is_selected(selected_item):
                    child = selected_item
                manager.set_locus_of_focus(event, child)
                return True

        if not spellcheck_presenter.get_presenter().handle_window_event(event, self):
            manager.set_locus_of_focus(event, event.source)
        return True

    def on_window_created(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for window:create accessibility events."""

        return True

    def on_window_destroyed(self, event: Atspi.Event) -> bool:  # pylint: disable=unused-argument
        """Callback for window:destroy accessibility events."""

        return True

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if AXObject.find_ancestor_inclusive(focus, AXUtilities.is_menu):
            msg = "DEFAULT: Ignoring event. In menu."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if event.source != manager.get_active_window():
            msg = "DEFAULT: Ignoring event. Not for active window"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_combo_box_popup(AXUtilities.find_active_window()):
            msg = "DEFAULT: Ignoring event. Combo box popup is the new active window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_combo_box_popup(event.source):
            msg = "DEFAULT: Ignoring event. Combo box popup."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().quit()

        if learn_mode_presenter.get_presenter().is_active():
            learn_mode_presenter.get_presenter().quit()

        self.point_of_reference = {}

        focus_manager.get_manager().clear_state("Window deactivated")
        script_manager.get_manager().set_active_script(None, "Window deactivated")
        return True

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def _update_braille_caret_position(self, obj: Atspi.Accessible) -> None:
        """Try to reposition the cursor without having to do a full update."""

        if not braille_presenter.get_presenter().use_braille():
            return

        if braille.try_reposition_cursor(obj):
            return

        self.update_braille(obj)

    def _present_caret_moved_event(
        self,
        event: Atspi.Event,
        obj: Atspi.Accessible | None = None,
        reason: TextEventReason = TextEventReason.UNKNOWN,
    ) -> bool:
        """Presents text at the new position, based on heuristics. Returns True if handled."""

        obj = obj or event.source
        self._update_braille_caret_position(obj)

        # TODO - JD: Make this a TextEventReason. Also handle structural navigation
        # and table navigation here. Technically that's not been necessary because
        # it won't match anything below. But it would be cleaner to cover each cause
        # explicitly.
        if caret_navigator.get_navigator().last_input_event_was_navigation_command():
            msg = "DEFAULT: Event ignored: Last command was caret nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.SAY_ALL:
            msg = "DEFAULT: Not presenting text because SayAll is active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        navigation_handlers: dict[TextEventReason, Callable[[Atspi.Accessible], None]] = {
            TextEventReason.NAVIGATION_BY_LINE: self.say_line,
            TextEventReason.NAVIGATION_BY_WORD: self.say_word,
            TextEventReason.NAVIGATION_BY_CHARACTER: self.say_character,
            TextEventReason.NAVIGATION_BY_PAGE: self.say_line,
            TextEventReason.NAVIGATION_TO_LINE_BOUNDARY: self.say_character,
            TextEventReason.NAVIGATION_TO_FILE_BOUNDARY: self.say_line,
        }
        handler = navigation_handlers.get(reason)
        if handler is not None:
            handler(obj)
            return True

        if reason == TextEventReason.MOUSE_PRIMARY_BUTTON:
            text, _start, _end = AXText.get_cached_selected_text(event.source)
            if not text:
                self.say_line(obj)
                return True
        return False

    def say_character(self, obj: Atspi.Accessible) -> None:
        """Speak the character at the caret."""

        context_obj, context_offset = self.utilities.get_caret_context(obj)
        if context_obj == obj:
            offset = context_offset
        else:
            offset = AXText.get_caret_offset(obj)

        if input_event_manager.get_manager().last_event_was_forward_caret_selection():
            offset -= 1

        character, start_offset, end_offset = AXText.get_character_at_offset(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start_offset,
            end_offset,
            focus_manager.CARET_TRACKING,
        )

        speech_presenter.get_presenter().speak_character_at_offset(obj, offset, character)
        self.point_of_reference["lastTextUnitSpoken"] = "char"

    def say_line(self, obj: Atspi.Accessible, offset: int | None = None) -> None:
        """Speaks the line at the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)
        else:
            AXText.set_caret_offset(obj, offset)

        line, start_offset = AXText.get_line_at_offset(obj, offset)[0:2]
        if line and line != "\n":
            end_offset = start_offset + len(line)
            focus_manager.get_manager().emit_region_changed(
                obj,
                start_offset,
                end_offset,
                focus_manager.CARET_TRACKING,
            )

        speech_presenter.get_presenter().speak_line(
            self,
            obj,
            start_offset,
            start_offset + len(line),
            line,
        )

        self.point_of_reference["lastTextUnitSpoken"] = "line"

    def say_phrase(self, obj: Atspi.Accessible, start_offset: int, end_offset: int) -> None:
        """Speaks the substring between start and end offset."""

        phrase = self.utilities.expand_eocs(obj, start_offset, end_offset)
        if not phrase:
            return

        if len(phrase) > 1 or phrase.isalnum():
            focus_manager.get_manager().emit_region_changed(
                obj,
                start_offset,
                end_offset,
                focus_manager.CARET_TRACKING,
            )

        speech_presenter.get_presenter().speak_phrase(self, obj, start_offset, end_offset, phrase)
        self.point_of_reference["lastTextUnitSpoken"] = "phrase"

    def say_word(self, obj: Atspi.Accessible) -> None:
        """Speaks the word at the caret, taking into account the previous caret position."""

        context_obj, context_offset = self.utilities.get_caret_context(obj)
        if context_obj == obj:
            offset = context_offset
        else:
            offset = AXText.get_caret_offset(obj)

        word, start_offset, end_offset = self.utilities.get_word_at_offset_adjusted_for_navigation(
            obj,
            offset,
        )

        speech_pres = speech_presenter.get_presenter()
        if "\n" in word:
            # Announce when we cross a hard line boundary, based on whether or not indentation and
            # justification should be spoken. This was done to avoid yet another setting in
            # response to some users saying this announcement was too chatty. The idea of using
            # this setting for the decision is that if the user wants indentation and justification
            # announced, they are interested in explicit whitespace information.
            if speech_pres.get_speak_indentation_and_justification():
                presentation_manager.get_manager().speak_character("\n")
            if word.startswith("\n"):
                start_offset += 1
            elif word.endswith("\n"):
                end_offset -= 1
            word = AXText.get_substring(obj, start_offset, end_offset)

        # say_phrase is useful because it handles punctuation verbalization, but we don't want
        # to trigger its whitespace presentation.
        matches = list(re.finditer(r"\S+", word))
        if matches:
            start_offset += matches[0].start()
            end_offset -= len(word) - matches[-1].end()
            word = AXText.get_substring(obj, start_offset, end_offset)

        text = word.replace("\n", "\\n")
        msg = f"DEFAULT: Final word at offset {offset} is '{text}' ({start_offset}-{end_offset})"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if error := speech_presenter.get_presenter().get_error_description(obj, start_offset):
            presentation_manager.get_manager().speak_message(error)

        self.say_phrase(obj, start_offset, end_offset)
        self.point_of_reference["lastTextUnitSpoken"] = "word"

    def present_object(self, obj: Atspi.Accessible, **args) -> None:
        """Presents the current object."""

        tokens = ["DEFAULT: Presenting object", obj, ". Interrupt:", args.get("interrupt", False)]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        offset = args.get("offset")
        if offset is not None:
            AXText.set_caret_offset(obj, offset)

        speech_only = args.pop("speechonly", False)
        presentation_manager.get_manager().present_object(
            self,
            obj,
            generate_braille=not speech_only,
            **args,
        )
