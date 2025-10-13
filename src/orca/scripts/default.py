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
# pylint: disable=too-many-branches
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements

"""The default Script for presenting information to the user."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2011-2025 Igalia, S.L."
__license__   = "LGPL"

import re
from typing import Any, Callable, TYPE_CHECKING

from orca import braille
from orca import braille_presenter
from orca import cmdnames
from orca import debug
from orca import event_manager
from orca import focus_manager
from orca import input_event_manager
from orca import input_event
from orca import keybindings
from orca import messages
from orca import orca
from orca import orca_gui_prefs
from orca import orca_modifier_manager
from orca import phonnames
from orca import script
from orca import script_manager
from orca import settings
from orca import settings_manager
from orca import sound
from orca import speech
from orca import speech_and_verbosity_manager

from orca.acss import ACSS
from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_event import TextEventReason
from orca.ax_value import AXValue

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from orca.sound_generator import Icon, Tone

class Script(script.Script):
    """The default Script for presenting information to the user."""

    def __init__(self, app: Atspi.Accessible) -> None:
        super().__init__(app)
        self.grab_ids: list = [int]

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

        self.input_event_handlers["routePointerToItemHandler"] = \
            input_event.InputEventHandler(
                Script.route_pointer_to_item,
                cmdnames.ROUTE_POINTER_TO_ITEM)

        self.input_event_handlers["leftClickReviewItemHandler"] = \
            input_event.InputEventHandler(
                Script.left_click_item,
                cmdnames.LEFT_CLICK_REVIEW_ITEM)

        self.input_event_handlers["rightClickReviewItemHandler"] = \
             input_event.InputEventHandler(
                Script.right_click_item,
                cmdnames.RIGHT_CLICK_REVIEW_ITEM)

        self.input_event_handlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_left,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_right,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["goBrailleHomeHandler"] = \
            input_event.InputEventHandler(
                Script.go_braille_home,
                cmdnames.GO_BRAILLE_HOME)

        self.input_event_handlers["contractedBrailleHandler"] = \
            input_event.InputEventHandler(
                Script.set_contracted_braille,
                cmdnames.SET_CONTRACTED_BRAILLE)

        self.input_event_handlers["processRoutingKeyHandler"] = \
            input_event.InputEventHandler(
                Script.process_routing_key,
                cmdnames.PROCESS_ROUTING_KEY)

        self.input_event_handlers["processBrailleCutBeginHandler"] = \
            input_event.InputEventHandler(
                Script.process_braille_cut_begin,
                cmdnames.PROCESS_BRAILLE_CUT_BEGIN)

        self.input_event_handlers["processBrailleCutLineHandler"] = \
            input_event.InputEventHandler(
                Script.process_braille_cut_line,
                cmdnames.PROCESS_BRAILLE_CUT_LINE)

        self.input_event_handlers["shutdownHandler"] = \
            input_event.InputEventHandler(
                Script.quit_orca,
                cmdnames.QUIT_ORCA)

        self.input_event_handlers["preferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                Script.show_preferences_gui,
                cmdnames.SHOW_PREFERENCES_GUI)

        self.input_event_handlers["appPreferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                Script.show_app_preferences_gui,
                cmdnames.SHOW_APP_PREFERENCES_GUI)

        self.input_event_handlers["cycleSettingsProfileHandler"] = \
            input_event.InputEventHandler(
                Script.cycle_settings_profile,
                cmdnames.CYCLE_SETTINGS_PROFILE)

        self.input_event_handlers.update(self.get_clipboard_presenter().get_handlers())
        self.input_event_handlers.update(self.get_notification_presenter().get_handlers())
        self.input_event_handlers.update(self.get_flat_review_finder().get_handlers())
        self.input_event_handlers.update(self.get_flat_review_presenter().get_handlers())
        self.input_event_handlers.update(self.get_speech_and_verbosity_manager().get_handlers())
        self.input_event_handlers.update(self.get_bypass_mode_manager().get_handlers())
        self.input_event_handlers.update(self.get_system_information_presenter().get_handlers())
        self.input_event_handlers.update(self.bookmarks.get_handlers())
        self.input_event_handlers.update(self.get_object_navigator().get_handlers())
        self.input_event_handlers.update(self.get_say_all_presenter().get_handlers())
        self.input_event_handlers.update(self.get_caret_navigator().get_handlers())
        self.input_event_handlers.update(self.get_structural_navigator().get_handlers())
        self.input_event_handlers.update(self.get_table_navigator().get_handlers())
        self.input_event_handlers.update(self.get_typing_echo_presenter().get_handlers())
        self.input_event_handlers.update(self.get_where_am_i_presenter().get_handlers())
        self.input_event_handlers.update(self.get_learn_mode_presenter().get_handlers())
        self.input_event_handlers.update(self.get_mouse_reviewer().get_handlers())
        self.input_event_handlers.update(self.get_action_presenter().get_handlers())
        self.input_event_handlers.update(self.get_debugging_tools_manager().get_handlers())

    def get_listeners(self) -> dict[str, Callable]:
        """Sets up the AT-SPI event listeners for this script."""

        listeners = script.Script.get_listeners(self)
        listeners["document:attributes-changed"] = self.on_document_attributes_changed
        listeners["document:reload"] = self.on_document_reload
        listeners["document:load-complete"] = self.on_document_load_complete
        listeners["document:load-stopped"] = self.on_document_load_stopped
        listeners["document:page-changed"] = self.on_document_page_changed
        listeners["mouse:button"] = self.on_mouse_button
        listeners["object:announcement"] = self.on_announcement
        listeners["object:active-descendant-changed"] = self.on_active_descendant_changed
        listeners["object:attributes-changed"] = self.on_object_attributes_changed
        listeners["object:children-changed:add"] = self.on_children_added
        listeners["object:children-changed:remove"] = self.on_children_removed
        listeners["object:column-reordered"] = self.on_column_reordered
        listeners["object:property-change:accessible-description"] = self.on_description_changed
        listeners["object:property-change:accessible-name"] = self.on_name_changed
        listeners["object:property-change:accessible-value"] =  self.on_value_changed
        listeners["object:row-reordered"] = self.on_row_reordered
        listeners["object:selection-changed"] = self.on_selection_changed
        listeners["object:state-changed:active"] = self.on_active_changed
        listeners["object:state-changed:busy"] = self.on_busy_changed
        listeners["object:state-changed:checked"] = self.on_checked_changed
        listeners["object:state-changed:expanded"] = self.on_expanded_changed
        listeners["object:state-changed:focused"] = self.on_focused_changed
        listeners["object:state-changed:indeterminate"] = self.on_indeterminate_changed
        listeners["object:state-changed:invalid-entry"] = self.on_invalid_entry_changed
        listeners["object:state-changed:pressed"] = self.on_pressed_changed
        listeners["object:state-changed:selected"] = self.on_selected_changed
        listeners["object:state-changed:sensitive"] = self.on_sensitive_changed
        listeners["object:state-changed:showing"] = self.on_showing_changed
        listeners["object:text-attributes-changed"] = self.on_text_attributes_changed
        listeners["object:text-caret-moved"] = self.on_caret_moved
        listeners["object:text-changed:delete"] = self.on_text_deleted
        listeners["object:text-changed:insert"] = self.on_text_inserted
        listeners["object:text-selection-changed"] = self.on_text_selection_changed
        listeners["object:value-changed"] = self.on_value_changed
        listeners["window:activate"] = self.on_window_activated
        listeners["window:create"] = self.on_window_created
        listeners["window:deactivate"] = self.on_window_deactivated
        listeners["window:destroy"] = self.on_window_destroyed
        return listeners

    def _get_extension_bindings(self) -> keybindings.KeyBindings:
        key_bindings = keybindings.KeyBindings()

        layout = settings_manager.get_manager().get_setting("keyboardLayout")
        is_desktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        bindings = self.get_sleep_mode_manager().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_notification_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_clipboard_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_flat_review_finder().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_flat_review_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_where_am_i_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_learn_mode_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_speech_and_verbosity_manager().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_system_information_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_object_navigator().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_caret_navigator().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_structural_navigator().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_table_navigator().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.bookmarks.get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_mouse_reviewer().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_action_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_debugging_tools_manager().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        return key_bindings

    def get_key_bindings(self, enabled_only: bool = True) -> keybindings.KeyBindings:
        """Returns the key bindings for this script."""

        tokens = ["DEFAULT: Getting keybindings for", self]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        key_bindings = script.Script.get_key_bindings(self)

        bindings = self.get_default_keybindings_deprecated()
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self.get_app_key_bindings()
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        bindings = self._get_extension_bindings()
        for binding in bindings.key_bindings:
            key_bindings.add(binding)

        key_bindings = settings_manager.get_manager().override_key_bindings(
                self.input_event_handlers, key_bindings, enabled_only)

        return key_bindings

    def get_default_keybindings_deprecated(self) -> keybindings.KeyBindings:
        """Returns the basic keybindings (i.e. without extension bindings)"""

        bindings = keybindings.KeyBindings()

        layout = settings_manager.get_manager().get_setting("keyboardLayout")
        is_desktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
        if is_desktop:
            bindings.add(
                keybindings.KeyBinding(
                    "KP_Divide",
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.ORCA_MODIFIER_MASK,
                    self.input_event_handlers["routePointerToItemHandler"]))

            # We want the user to be able to combine modifiers with the mouse click, therefore we
            # do not "care" about the modifiers -- unless it's the Orca modifier.
            bindings.add(
                keybindings.KeyBinding(
                    "KP_Divide",
                    keybindings.ORCA_MODIFIER_MASK,
                    keybindings.NO_MODIFIER_MASK,
                    self.input_event_handlers["leftClickReviewItemHandler"]))

            bindings.add(
                keybindings.KeyBinding(
                    "KP_Multiply",
                    keybindings.ORCA_MODIFIER_MASK,
                    keybindings.NO_MODIFIER_MASK,
                    self.input_event_handlers["rightClickReviewItemHandler"]))
        else:
            bindings.add(
                keybindings.KeyBinding(
                    "9",
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.ORCA_MODIFIER_MASK,
                    self.input_event_handlers["routePointerToItemHandler"]))

            # We want the user to be able to combine modifiers with the mouse click, therefore we
            # do not "care" about the modifiers -- unless it's the Orca modifier.
            bindings.add(
                keybindings.KeyBinding(
                    "7",
                    keybindings.ORCA_MODIFIER_MASK,
                    keybindings.ORCA_MODIFIER_MASK,
                    self.input_event_handlers["leftClickReviewItemHandler"]))

            bindings.add(
                keybindings.KeyBinding(
                    "8",
                    keybindings.ORCA_MODIFIER_MASK,
                    keybindings.ORCA_MODIFIER_MASK,
                    self.input_event_handlers["rightClickReviewItemHandler"]))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["cycleSettingsProfileHandler"]))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["panBrailleLeftHandler"]))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["panBrailleRightHandler"]))

        bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["shutdownHandler"]))

        bindings.add(
            keybindings.KeyBinding(
                "space",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers["preferencesSettingsHandler"]))

        bindings.add(
            keybindings.KeyBinding(
                "space",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self.input_event_handlers["appPreferencesSettingsHandler"]))

        # TODO - JD: Move these into the extension commands. That will require a new string
        # and GUI change.
        bypass_mode_bindings = self.get_bypass_mode_manager().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in bypass_mode_bindings.key_bindings:
            bindings.add(binding)

        say_all_bindings = self.get_say_all_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in say_all_bindings.key_bindings:
            bindings.add(binding)

        typing_echo_bindings = self.get_typing_echo_presenter().get_bindings(
            refresh=True, is_desktop=is_desktop)
        for binding in typing_echo_bindings.key_bindings:
            bindings.add(binding)

        return bindings

    def get_braille_bindings(self) -> dict:
        """Returns the braille bindings for this script."""

        msg = "DEFAULT: Getting braille bindings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        braille_bindings = script.Script.get_braille_bindings(self)
        try:
            braille_bindings[braille.brlapi.KEY_CMD_HWINLT]     = \
                self.input_event_handlers["panBrailleLeftHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_FWINLT]     = \
                self.input_event_handlers["panBrailleLeftHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_FWINLTSKIP] = \
                self.input_event_handlers["panBrailleLeftHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_HWINRT]     = \
                self.input_event_handlers["panBrailleRightHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_FWINRT]     = \
                self.input_event_handlers["panBrailleRightHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_FWINRTSKIP] = \
                self.input_event_handlers["panBrailleRightHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_HOME]       = \
                self.input_event_handlers["goBrailleHomeHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_SIXDOTS]     = \
                self.input_event_handlers["contractedBrailleHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_ROUTE]     = \
                self.input_event_handlers["processRoutingKeyHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_CUTBEGIN]   = \
                self.input_event_handlers["processBrailleCutBeginHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_CUTLINE]   = \
                self.input_event_handlers["processBrailleCutLineHandler"]
            braille_bindings[braille.brlapi.KEY_CMD_HOME] = \
                self.input_event_handlers["goBrailleHomeHandler"]
        except AttributeError:
            tokens = ["DEFAULT: Braille bindings unavailable in", self]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        except (KeyError, TypeError) as error:
            tokens = ["DEFAULT: Exception getting braille bindings in", self, ":", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        braille_bindings.update(self.get_flat_review_presenter().get_braille_bindings())

        msg = "DEFAULT: Finished getting braille bindings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        return braille_bindings

    def get_app_preferences_gui(self) -> None:
        """Return a GtkGrid, or None if there's no app-specific UI."""

        return None

    def get_preferences_from_gui(self) -> dict:
        """Returns a dictionary with the app-specific preferences."""

        return {}

    def deactivate(self) -> None:
        """Called when this script is deactivated."""

        self.point_of_reference = {}
        if self.get_bypass_mode_manager().is_active():
            self.get_bypass_mode_manager().toggle_enabled(self)

        self.remove_key_grabs("script deactivation")
        input_event_manager.get_manager().check_grabbed_bindings()

    def add_key_grabs(self, reason: str = "") -> None:
        """ Sets up the key grabs currently needed by this script. """

        tokens = ["DEFAULT: Adding key grabs for", self]
        if reason:
            tokens.append(f": {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.key_bindings = self.get_key_bindings()
        self.key_bindings.add_key_grabs(reason)
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = self.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["DEFAULT:", self, f"now has {len(has_grabs)} key grabs."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def remove_key_grabs(self, reason: str = "") -> None:
        """ Removes this script's AT-SPI key grabs. """

        tokens = ["DEFAULT: Removing key grabs for", self]
        if reason:
            tokens.append(f": {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        orca_modifier_manager.get_manager().remove_grabs_for_orca_modifiers()
        self.key_bindings.remove_key_grabs(reason)

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = self.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["DEFAULT:", self, f"now has {len(has_grabs)} key grabs."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.key_bindings = keybindings.KeyBindings()

    def refresh_key_grabs(self, reason: str = "") -> None:
        """ Refreshes the enabled key grabs for this script. """

        msg = "DEFAULT: refreshing key grabs"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # TODO: Should probably avoid removing key grabs and re-adding them.
        # Otherwise, a key could conceivably leak through while the script is
        # in the process of updating the bindings.
        self.remove_key_grabs("refreshing")
        self.add_key_grabs("refreshing")

    def register_event_listeners(self) -> None:
        """Registers for listeners needed by this script."""

        event_manager.get_manager().register_script_listeners(self)

    def deregister_event_listeners(self) -> None:
        """De-registers the listeners needed by this script."""

        event_manager.get_manager().deregister_script_listeners(self)

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
                self.get_flat_review_finder().find(self)
            return True

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        if self.get_learn_mode_presenter().is_active():
            self.get_learn_mode_presenter().quit()

        active_window = self.utilities.top_level_object(new_focus)
        focus_manager.get_manager().set_active_window(active_window)
        self.update_braille(new_focus)

        if old_focus is None:
            old_focus = active_window

        utterances = self.speech_generator.generate_speech(
            new_focus,
            priorObj=old_focus)

        if self.utilities.should_interrupt_for_locus_of_focus_change(
           old_focus, new_focus, event):
            self.interrupt_presentation()
        speech.speak(utterances, interrupt=False)
        return True

    def activate(self) -> None:
        """Called when this script is activated."""

        tokens = ["DEFAULT: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        settings_manager.get_manager().load_app_settings(self)

        # TODO - JD: Should these be moved into check_speech_setting?
        self.get_speech_and_verbosity_manager().update_punctuation_level()
        self.get_speech_and_verbosity_manager().update_capitalization_style()
        self.get_speech_and_verbosity_manager().update_synthesizer()

        self.get_structural_navigator().set_mode(self, self._default_sn_mode)
        self.get_caret_navigator().set_enabled_for_script(
            self, self._default_caret_navigation_enabled)

        self.add_key_grabs("script activation")
        tokens = ["DEFAULT: Script for", self.app, "activated"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def update_braille(self, obj: Atspi.Accessible, **args) -> None:
        """Updates the braille display to show obj."""

        if not braille_presenter.get_presenter().use_braille():
            return

        if not obj:
            return

        result, focused_region = self.braille_generator.generate_braille(obj, **args)
        if not result:
            return

        braille.clear()
        line = braille.Line()
        braille.add_line(line)
        line.add_regions(result)

        extra_region = args.get("extraRegion")
        if extra_region:
            line.add_region(extra_region)
            braille.setFocus(extra_region)
        else:
            braille.setFocus(focused_region)

        braille.refresh(True)

    ########################################################################
    #                                                                      #
    # INPUT EVENT HANDLERS (AKA ORCA COMMANDS)                             #
    #                                                                      #
    ########################################################################

    def show_app_preferences_gui(self, _event: input_event.InputEvent | None = None) -> bool:
        """Shows the app Preferences dialog."""

        prefs = {}
        manager = settings_manager.get_manager()
        for key in settings.userCustomizableSettings:
            prefs[key] = manager.get_setting(key)

        ui = orca_gui_prefs.OrcaSetupGUI(self, prefs)
        ui.showGUI()
        return True

    def show_preferences_gui(self, _event: input_event.InputEvent | None = None) -> bool:
        """Displays the Preferences dialog."""

        manager = settings_manager.get_manager()
        prefs = manager.get_general_settings(manager.profile or "default")
        ui = orca_gui_prefs.OrcaSetupGUI(script_manager.get_manager().get_default_script(), prefs)
        ui.showGUI()
        return True

    def quit_orca(self, _event: input_event.InputEvent | None = None) -> bool:
        """Quit Orca."""

        orca.shutdown()
        return True

    def pan_braille_left(
        self,
        event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans the braille display to the left.  If pan_amount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if isinstance(event, input_event.KeyboardEvent) \
           and not braille_presenter.get_presenter().use_braille():
            msg = "DEFAULT: panBrailleLeft command requires braille or braille monitor"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_flat_review_presenter().is_active():
            return self.get_flat_review_presenter().pan_braille_left(self, event, pan_amount)

        focus = focus_manager.get_manager().get_locus_of_focus()
        is_text_area = AXUtilities.is_editable(focus) or AXUtilities.is_terminal(focus)
        if braille.beginningIsShowing and is_text_area:
            # If we're at the beginning of a line of a multiline text
            # area, then force it's caret to the end of the previous
            # line.  The assumption here is that we're currently
            # viewing the line that has the caret -- which is a pretty
            # good assumption for focus tacking mode.  When we set the
            # caret position, we will get a caret event, which will
            # then update the braille.
            #
            start_offset = AXText.get_line_at_offset(focus)[1]
            moved_caret = False
            if start_offset > 0:
                moved_caret = AXText.set_caret_offset(focus, start_offset - 1)

            # If we didn't move the caret and we're in a terminal, we
            # jump into flat review to review the text.  See
            # http://bugzilla.gnome.org/show_bug.cgi?id=482294.
            #
            if not moved_caret and AXUtilities.is_terminal(focus):
                self.get_flat_review_presenter().go_start_of_line(self, event)
                self.get_flat_review_presenter().go_previous_character(self, event)
        else:
            braille.panLeft(pan_amount)
            # We might be panning through a flashed message.
            braille.resetFlashTimer()
            braille.refresh(False, stopFlash=False)

        return True

    def pan_braille_right(
        self,
        event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans the braille display to the right.  If pan_amount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the end will take you to the beginning of the next line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if isinstance(event, input_event.KeyboardEvent) \
           and not braille_presenter.get_presenter().use_braille():
            msg = "DEFAULT: panBrailleRight command requires braille or braille monitor"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_flat_review_presenter().is_active():
            return self.get_flat_review_presenter().pan_braille_right(self, event, pan_amount)

        focus = focus_manager.get_manager().get_locus_of_focus()
        is_text_area = AXUtilities.is_editable(focus) or AXUtilities.is_terminal(focus)
        if braille.endIsShowing and is_text_area:
            # If we're at the end of a line of a multiline text area, then
            # force it's caret to the beginning of the next line.  The
            # assumption here is that we're currently viewing the line that
            # has the caret -- which is a pretty good assumption for focus
            # tacking mode.  When we set the caret position, we will get a
            # caret event, which will then update the braille.
            #
            end_offset = AXText.get_line_at_offset(focus)[2]
            if end_offset < AXText.get_character_count(focus):
                AXText.set_caret_offset(focus, end_offset)
        else:
            braille.panRight(pan_amount)
            # We might be panning through a flashed message.
            braille.resetFlashTimer()
            braille.refresh(False, stopFlash=False)

        return True

    def go_braille_home(self, event: input_event.InputEvent | None = None) -> bool:
        """Returns to the component with focus."""

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()
            return True

        self.interrupt_presentation()
        return braille.returnToRegionWithFocus(event)

    def set_contracted_braille(self, event: input_event.InputEvent | None = None) -> bool:
        """Toggles contracted braille."""

        braille.set_contracted_braille(event)
        return True

    def process_routing_key(self, event: input_event.InputEvent | None = None) -> bool:
        """Processes a cursor routing key."""

        # Don't kill flash here because it will restore the previous contents and
        # then process the routing key. If the contents accept a click action, this
        # would result in clicking on the link instead of clearing the flash message.
        self.interrupt_presentation(kill_flash=False)
        braille.process_routing_key(event)
        return True

    def process_braille_cut_begin(self, event: input_event.InputEvent | None = None) -> bool:
        """Clears the selection and moves the caret offset in the currently
        active text area.
        """

        obj, offset = braille.getCaretContext(event)
        if offset < 0:
            return True

        self.interrupt_presentation()
        AXText.clear_all_selected_text(obj)
        self.utilities.set_caret_offset(obj, offset)
        return True

    def process_braille_cut_line(self, event: input_event.InputEvent | None = None) -> bool:
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        obj, offset = braille.getCaretContext(event)
        if offset < 0:
            return True

        self.interrupt_presentation()
        start_offset = AXText.get_selection_start_offset(obj)
        end_offset = AXText.get_selection_end_offset(obj)
        if (start_offset < 0 or end_offset < 0):
            caret_offset = AXText.get_caret_offset(obj)
            start_offset = min(offset, caret_offset)
            end_offset = max(offset, caret_offset)

        AXText.set_selected_text(obj, start_offset, end_offset)
        text = AXText.get_selected_text(obj)[0]
        self.get_clipboard_presenter().set_text(text)
        return True

    def route_pointer_to_item(self, event: input_event.InputEvent | None = None) -> bool:
        """Moves the mouse pointer to the current item."""

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().route_pointer_to_object(self, event)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_event_synthesizer().route_to_character(focus) \
           or self.get_event_synthesizer().route_to_object(focus):
            self.present_message(messages.MOUSE_MOVED_SUCCESS)
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.present_message(full, brief)
        return False

    def left_click_item(self, event: input_event.InputEvent | None = None) -> bool:
        """Performs a left mouse button click on the current item."""

        if self.get_flat_review_presenter().is_active():
            obj = self.get_flat_review_presenter().get_current_object(self, event)
            if self.get_event_synthesizer().try_all_clickable_actions(obj):
                return True
            return self.get_flat_review_presenter().left_click_on_object(self, event)

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_event_synthesizer().try_all_clickable_actions(focus):
            return True

        if AXText.get_character_count(focus):
            if self.get_event_synthesizer().click_character(focus, None, 1):
                return True

        if self.get_event_synthesizer().click_object(focus, 1):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.present_message(full, brief)
        return False

    def right_click_item(self, event: input_event.InputEvent | None = None) -> bool:
        """Performs a right mouse button click on the current item."""

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().right_click_on_object(self, event)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_event_synthesizer().click_character(focus, None, 3):
            return True

        if self.get_event_synthesizer().click_object(focus, 3):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.present_message(full, brief)
        return False

    def cycle_settings_profile(self, _event: input_event.InputEvent | None = None) -> bool:
        """Cycle through the user's existing settings profiles."""

        profile_names = settings_manager.get_manager().available_profiles()
        if not profile_names:
            self.present_message(messages.PROFILE_NOT_FOUND)
            return True

        # profile_names is now list[list[str]] where each is [display_name, internal_name]
        profiles = [(profile[0], profile[1]) for profile in profile_names]

        def is_match(x: tuple[str, str]) -> bool:
            return x[1] == settings_manager.get_manager().get_profile()

        current_matches: list[tuple[str, str]] = list(filter(is_match, profiles))
        if not current_matches:
            # If no current match, start with first profile
            current_index = 0
        else:
            current_index = profiles.index(current_matches[0])

        try:
            name, profile_id = profiles[current_index + 1]
        except IndexError:
            name, profile_id = profiles[0]

        settings_manager.get_manager().set_profile(profile_id, updateLocale=True)

        braille.checkBrailleSetting()
        speech_and_verbosity_manager.get_manager().refresh_speech()

        # TODO: This is another "too close to code freeze" hack to cause the
        # command names to be presented in the correct language.
        self.setup_input_event_handlers()

        self.present_message(messages.PROFILE_CHANGED % name, name)
        return True

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
                    window, set_window_as_focus=True, notify_script=True)

        return True

    def on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:active-descendant-changed accessibility events."""

        if AXUtilities.is_presentable_active_descendant_change(event):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)

        return True

    def on_busy_changed(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
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

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        offset = AXText.get_caret_offset(event.source)

        # TODO - JD: These need to be harmonized / unified / simplified.
        manager.set_last_cursor_position(event.source, offset)
        self.utilities.set_caret_context(event.source, offset)

        ignore = [TextEventReason.CUT,
                  TextEventReason.PASTE,
                  TextEventReason.REDO,
                  TextEventReason.UNDO]
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
            self.present_message(event.any_data)
        return True

    def on_document_attributes_changed(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
        """Callback for document:attributes-changed accessibility events."""

        return True

    def on_document_reload(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
        """Callback for document:reload accessibility events."""

        return True

    def on_document_load_complete(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
        """Callback for document:load-complete accessibility events."""

        return True

    def on_document_load_stopped(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
        """Callback for document:load-stopped accessibility events."""

        return True

    def on_document_page_changed(self, event: Atspi.Event) -> bool:
        """Callback for document:page-changed accessibility events."""

        if event.detail1 < 0:
            return True

        if not AXDocument.did_page_change(event.source):
            return True

        self.present_message(messages.PAGE_NUMBER % event.detail1)
        return True

    def on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "expanded-changed event.")
        if not AXUtilities.is_presentable_expanded_change(event):
            return True

        self.present_object(event.source, alreadyFocused=True, interrupt=True)
        details = self.utilities.details_content_for_object(event.source)
        for detail in details:
            self.speak_message(detail, interrupt=False)

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
            msg = self.speech_generator.get_error_message(event.source)
        else:
            msg = messages.INVALID_ENTRY_FIXED
        self.speak_message(msg)
        self.update_braille(event.source)
        return True

    def on_mouse_button(self, event: Atspi.Event) -> bool:
        """Callback for mouse:button events."""

        input_event_manager.get_manager().process_mouse_button_event(event)
        return True

    def on_announcement(self, event: Atspi.Event) -> bool:
        """Callback for object:announcement events."""

        if isinstance(event.any_data, str):
            self.present_message(event.any_data)

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

        self.present_message(event.any_data)
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

        if speech_and_verbosity_manager.get_manager().get_only_speak_displayed_text():
            return True

        announce_state = False
        manager = input_event_manager.get_manager()
        if manager.last_event_was_space():
            announce_state = True
        elif (manager.last_event_was_up() or manager.last_event_was_down()) \
                and AXUtilities.is_table_cell(event.source):
            announce_state = AXUtilities.is_selected(event.source)

        if not announce_state:
            return True

        # TODO - JD: Unlike the other state-changed callbacks, it seems unwise
        # to call generate_speech() here because that also will present the
        # expandable state if appropriate for the object type. The generators
        # need to gain some smarts w.r.t. state changes.

        if event.detail1:
            self.speak_message(messages.TEXT_SELECTED, interrupt=False)
        else:
            self.speak_message(messages.TEXT_UNSELECTED, interrupt=False)

        return True

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.utilities.handle_paste_locus_of_focus_change():
            if self.utilities.top_level_object_is_active_and_current(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
        elif self.utilities.handle_container_selection_change(event.source):
            return True
        elif AXUtilities.manages_descendants(event.source):
            return True
        elif event.source == focus:
            # There is a bug in (at least) Pidgin in which a newly-expanded submenu lacks the
            # showing and visible states, causing the logic below to be triggered. Work around
            # that here by trusting selection changes from the locus of focus are probably valid
            # even if the state set is not.
            pass
        elif not (AXUtilities.is_showing(event.source) and AXUtilities.is_visible(event.source)):
            # If the current combobox is collapsed, its menu child that fired the event might lack
            # the showing and visible states. This happens in (at least) Thunderbird's calendar
            # new-appointment comboboxes. Therefore check to see if the event came from the current
            # combobox. This is necessary because (at least) VSCode's debugger has some hidden menu
            # that the user is not in which is firing this event. This is why we cannot have nice
            # things.
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

        # If the current item's selection is toggled, we'll present that
        # via the state-changed event.
        if input_event_manager.get_manager().last_event_was_space():
            return True

        if AXUtilities.is_combo_box(event.source) and not AXUtilities.is_expanded(event.source):
            if AXUtilities.is_focused(
                 AXObject.find_descendant(event.source, AXUtilities.is_text_input)):
                return True
        elif AXUtilities.is_page_tab_list(event.source) \
            and self.get_flat_review_presenter().is_active():
            # If a wizard-like notebook page being reviewed changes, we might not get
            # any events to update the locusOfFocus. As a result, subsequent flat
            # review commands will continue to present the stale content.
            # TODO - JD: We can potentially do some automatic reading here.
            self.get_flat_review_presenter().quit()

        selected_children = self.utilities.selected_children(event.source)
        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus in selected_children:
            msg = "DEFAULT: Ignoring event believed to be redundant to focus change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        mouse_review_item = self.get_mouse_reviewer().get_current_item()
        for child in selected_children:
            if AXObject.is_ancestor(focus, child):
                tokens = ["DEFAULT: Child", child, "is ancestor of locusOfFocus"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

            if child == mouse_review_item:
                tokens = ["DEFAULT: Child", child, "is current mouse review item"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                continue

            if AXUtilities.is_page_tab(child) and focus \
               and AXObject.get_name(child) == AXObject.get_name(focus) \
               and not AXUtilities.is_focused(event.source):
                tokens = ["DEFAULT:", child, "'s selection redundant to", focus]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                break

            if not AXUtilities.is_layout_only(child):
                focus_manager.get_manager().set_locus_of_focus(event, child)
                break

        return True

    def on_sensitive_changed(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
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

            self.speak_message(self.speech_generator.get_localized_role_name(obj))
            msg = self.utilities.get_notification_content(obj)
            self.present_message(msg, reset_styles=False)
            self.get_notification_presenter().save_notification(msg)
            return True

        if AXUtilities.is_tool_tip(obj):
            was_f1 = input_event_manager.get_manager().last_event_was_f1()
            if not was_f1 and not settings_manager.get_manager().get_setting("presentToolTips"):
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

        self.speak_misspelled_indicator(event.source)
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
            self.present_message(messages.SELECTION_DELETED)
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
            self.speak_character(text)
        else:
            voice = self.speech_generator.voice(string=text)
            manager = speech_and_verbosity_manager.get_manager()
            text = manager.adjust_for_presentation(event.source, text)
            self.speak_message(text, voice)

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
            self.present_message(messages.SELECTION_RESTORED)
            AXText.update_cached_selected_text(event.source)
            return True

        speak_string = True
        if reason == TextEventReason.PAGE_SWITCH:
            msg = "DEFAULT: Insertion is believed to be due to page switch"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            speak_string = False
        elif reason == TextEventReason.PASTE:
            msg = "DEFAULT: Insertion is believed to be due to paste"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            speak_string = False
        elif reason == TextEventReason.UNSPECIFIED_COMMAND:
            msg = "DEFAULT: Insertion is believed to be due to command"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif reason == TextEventReason.MOUSE_MIDDLE_BUTTON:
            msg = "DEFAULT: Insertion is believed to be due to middle mouse button"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif reason == TextEventReason.TYPING_ECHOABLE:
            msg = "DEFAULT: Insertion is believed to be echoable"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif reason == TextEventReason.AUTO_INSERTION_PRESENTABLE:
            msg = "DEFAULT: Insertion is believed to be presentable auto text event"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif reason == TextEventReason.SELECTED_TEXT_INSERTION:
            msg = "DEFAULT: Insertion is also selected"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = "DEFAULT: Not speaking inserted string due to lack of cause"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            speak_string = False

        # Because some implementations are broken.
        text = self.utilities.inserted_text(event)
        if speak_string:
            if len(text) == 1:
                self.speak_character(text)
            else:
                voice = self.speech_generator.voice(obj=event.source, string=text)
                manager = speech_and_verbosity_manager.get_manager()
                text = manager.adjust_for_presentation(event.source, text)
                self.speak_message(text, voice)

        if len(text) != 1 \
           or reason not in [TextEventReason.TYPING, TextEventReason.TYPING_ECHOABLE]:
            return True

        presenter = self.get_typing_echo_presenter()
        if presenter.echo_previous_sentence(self, event.source):
            return True

        presenter.echo_previous_word(self, event.source)
        return True

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

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

        self.present_message(messages.TABLE_REORDERED_COLUMNS)
        return True

    def on_row_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:row-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "row-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return True

        if event.source != AXTable.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return True

        self.present_message(messages.TABLE_REORDERED_ROWS)
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
            self.interrupt_presentation()

        self.update_braille(event.source, isProgressBarUpdate=is_progress_bar_update)
        speech.speak(self.speech_generator.generate_speech(
            event.source, alreadyFocused=True, isProgressBarUpdate=is_progress_bar_update))
        self.__play(self.sound_generator.generate_sound(
            event.source, alreadyFocused=True, isProgressBarUpdate=is_progress_bar_update))
        return True

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        if not AXUtilities.can_be_active_window(event.source):
            return True

        if event.source == focus_manager.get_manager().get_active_window():
            msg = "DEFAULT: Event is for active window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        self.point_of_reference = {}

        focus_manager.get_manager().set_active_window(event.source)
        if AXObject.get_child_count(event.source) == 1:
            child = AXObject.get_child(event.source, 0)
            # Popup menus in Chromium live in a menu bar whose first child is a panel.
            if AXUtilities.is_menu_bar(child):
                child = AXObject.find_descendant(child, AXUtilities.is_menu)
            if AXUtilities.is_menu(child):
                focus_manager.get_manager().set_locus_of_focus(event, child)
                return True

        focus_manager.get_manager().set_locus_of_focus(event, event.source)
        return True

    def on_window_created(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
        """Callback for window:create accessibility events."""

        return True

    def on_window_destroyed(self, event: Atspi.Event) -> bool: # pylint: disable=unused-argument
        """Callback for window:destroy accessibility events."""

        return True

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.find_ancestor_inclusive(focus, AXUtilities.is_menu):
            msg = "DEFAULT: Ignoring event. In menu."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if event.source != focus_manager.get_manager().get_active_window():
            msg = "DEFAULT: Ignoring event. Not for active window"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        if self.get_learn_mode_presenter().is_active():
            self.get_learn_mode_presenter().quit()

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

        needs_repainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) and region.accessible == obj:
                if region.reposition_cursor():
                    braille.refresh(True)
                    needs_repainting = False
                break

        if needs_repainting:
            self.update_braille(obj)

    def _present_caret_moved_event(
        self,
        event: Atspi.Event,
        obj: Atspi.Accessible | None = None,
        reason: TextEventReason = TextEventReason.UNKNOWN
    ) -> bool:
        """Presents text at the new position, based on heuristics. Returns True if handled."""

        obj = obj or event.source
        self._update_braille_caret_position(obj)

        # TODO - JD: Make this a TextEventReason. Also handle structural navigation
        # and table navigation here. Technically that's not been necessary because
        # it won't match anything below. But it would be cleaner to cover each cause
        # explicitly.
        if self.get_caret_navigator().last_input_event_was_navigation_command():
            msg = "DEFAULT: Event ignored: Last command was caret nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.SAY_ALL:
            msg = "DEFAULT: Not presenting text because SayAll is active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        if reason == TextEventReason.NAVIGATION_BY_LINE:
            self.say_line(obj)
            return True
        if reason == TextEventReason.NAVIGATION_BY_WORD:
            self.say_word(obj)
            return True
        if reason == TextEventReason.NAVIGATION_BY_CHARACTER:
            self.say_character(obj)
            return True
        if reason == TextEventReason.NAVIGATION_BY_PAGE:
            self.say_line(obj)
            return True
        if reason == TextEventReason.NAVIGATION_TO_LINE_BOUNDARY:
            self.say_character(obj)
            return True
        if reason == TextEventReason.NAVIGATION_TO_FILE_BOUNDARY:
            self.say_line(obj)
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

        # If we have selected text and the last event was a move to the
        # right, then speak the character to the left of where the text
        # caret is (i.e. the selected character).
        if input_event_manager.get_manager().last_event_was_forward_caret_selection():
            offset -= 1

        character, start_offset, end_offset = AXText.get_character_at_offset(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj, start_offset, end_offset, focus_manager.CARET_TRACKING)

        if not character or character == "\r":
            character = "\n"

        speak_blank_lines = speech_and_verbosity_manager.get_manager().get_speak_blank_lines()
        if character == "\n":
            line_string = AXText.get_line_at_offset(obj, max(0, offset))[0]
            if not line_string or line_string == "\n":
                # This is a blank line. Announce it if the user requested
                # that blank lines be spoken.
                if speak_blank_lines:
                    self.speak_message(messages.BLANK, interrupt=False)
                return

        if character in ["\n", "\r\n"]:
            # This is a blank line. Announce it if the user requested
            # that blank lines be spoken.
            if speak_blank_lines:
                self.speak_message(messages.BLANK, interrupt=False)
            return

        self.speak_misspelled_indicator(obj, offset)
        self.speak_character(character)
        self.point_of_reference["lastTextUnitSpoken"] = "char"

    def say_line(self, obj: Atspi.Accessible, offset: int | None = None) -> None:
        """Speaks the line at the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)
        else:
            AXText.set_caret_offset(obj, offset)

        line, start_offset = AXText.get_line_at_offset(obj, offset)[0:2]
        if line and line != "\n":
            manager = speech_and_verbosity_manager.get_manager()
            indentation_description = manager.get_indentation_description(line)
            if indentation_description:
                self.speak_message(indentation_description)

            end_offset = start_offset + len(line)
            focus_manager.get_manager().emit_region_changed(
                obj, start_offset, end_offset, focus_manager.CARET_TRACKING)

            utterance = []
            split = self.utilities.split_substring_by_language(obj, start_offset, end_offset)
            if not split:
                speech.speak(line)
                return

            for start, _end, text, language, dialect in split:
                if not text:
                    continue

                # TODO - JD: This needs to be done in the generators.
                voice = self.speech_generator.voice(
                    obj=obj, string=text, language=language, dialect=dialect)
                text = manager.adjust_for_presentation(obj, text, start)

                # Some synthesizers will verbalize initial whitespace.
                text = text.lstrip()
                result: list[Any] = [text]
                result.extend(voice)
                utterance.append(result)
            speech.speak(utterance)
        elif speech_and_verbosity_manager.get_manager().get_speak_blank_lines():
            self.speak_message(messages.BLANK, interrupt=False)

        self.point_of_reference["lastTextUnitSpoken"] = "line"

    def say_phrase(self, obj: Atspi.Accessible, start_offset: int, end_offset: int) -> None:
        """Speaks the substring between start and end offset."""

        phrase = self.utilities.expand_eocs(obj, start_offset, end_offset)
        if not phrase:
            return

        if len(phrase) > 1 or phrase.isalnum():
            manager = speech_and_verbosity_manager.get_manager()
            result = manager.get_indentation_description(phrase)
            if result:
                self.speak_message(result)

            focus_manager.get_manager().emit_region_changed(
                obj, start_offset, end_offset, focus_manager.CARET_TRACKING)

            voice = self.speech_generator.voice(obj=obj, string=phrase)
            phrase = manager.adjust_for_presentation(obj, phrase)
            utterance: list[Any] = [phrase]
            utterance.extend(voice)
            speech.speak(utterance)
        else:
            self.speak_character(phrase)

        self.point_of_reference["lastTextUnitSpoken"] = "phrase"

    def say_word(self, obj: Atspi.Accessible) -> None:
        """Speaks the word at the caret, taking into account the previous caret position."""

        context_obj, context_offset = self.utilities.get_caret_context(obj)
        if context_obj == obj:
            offset = context_offset
        else:
            offset = AXText.get_caret_offset(obj)

        word, start_offset, end_offset = \
            self.utilities.get_word_at_offset_adjusted_for_navigation(obj, offset)

        if "\n" in word:
            # Announce when we cross a hard line boundary, based on whether or not indentation and
            # justification should be spoken. This was done to avoid yet another setting in
            # response to some users saying this announcement was too chatty. The idea of using
            # this setting for the decision is that if the user wants indentation and justification
            # announced, they are interested in explicit whitespace information.
            if speech_and_verbosity_manager.get_manager().get_speak_indentation_and_justification():
                self.speak_character("\n")
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
        msg = (
            f"DEFAULT: Final word at offset {offset} is '{text}' "
            f"({start_offset}-{end_offset})"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.speak_misspelled_indicator(obj, start_offset)
        self.say_phrase(obj, start_offset, end_offset)
        self.point_of_reference["lastTextUnitSpoken"] = "word"

    def present_object(self, obj: Atspi.Accessible, **args) -> None:
        """Presents the current object."""

        interrupt = args.get("interrupt", False)
        tokens = ["DEFAULT: Presenting object", obj, ". Interrupt:", interrupt]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        offset = args.get("offset")
        if offset is not None:
            AXText.set_caret_offset(obj, offset)

        if not args.get("speechonly", False):
            self.update_braille(obj, **args)
        utterances = self.speech_generator.generate_speech(obj, **args)
        speech.speak(utterances, interrupt=interrupt)

    def speak_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args
    ) -> None:
        """Speaks the specified contents."""

        tokens = ["DEFAULT: Speaking", contents, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
        utterances = self.speech_generator.generate_contents(contents, **args)
        speech.speak(utterances)

    def display_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args
    ) -> None:
        """Displays contents in braille."""

        tokens = ["DEFAULT: Displaying", contents, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        if not braille_presenter.get_presenter().use_braille():
            return

        braille.clear()
        line = braille.Line()
        braille.add_line(line)

        regions_list, focused_region = self.braille_generator.generate_contents(contents, **args)
        if not regions_list:
            msg = "DEFAULT: Generating braille contents failed"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        tokens = ["DEFAULT: Generated result", regions_list,
                  "focused region", focused_region or "None"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for regions in regions_list:
            line.add_regions(regions)

        if line.regions:
            line.regions[-1].string = line.regions[-1].string.rstrip(" ")

        braille.setFocus(focused_region, indicate_links=False)
        braille.refresh(panToCursor=True, indicate_links=False)

    def spell_phonetically(self, item_string: str) -> None:
        """Phonetically spell item_string."""

        for character in item_string:
            voice = self.speech_generator.voice(string=character)
            phonetic_string = phonnames.get_phonetic_name(character.lower())
            self.speak_message(phonetic_string, voice)

    def speak_misspelled_indicator(self, obj: Atspi.Accessible, offset: int | None = None) -> None:
        """Speaks the misspelled-word indicator."""

        # TODO - JD: Remove this and have callers use the speech-adjustment logic.
        manager = speech_and_verbosity_manager.get_manager()
        error = manager.get_error_description(obj, offset)
        if error:
            self.speak_message(error)

    ############################################################################
    #                                                                          #
    # Presentation methods                                                     #
    # (scripts should not call methods in braille.py or speech.py directly)    #
    #                                                                          #
    ############################################################################

    def interrupt_presentation(self, kill_flash=True):
        """Convenience method to interrupt whatever is being presented at the moment."""

        msg = "DEFAULT: Interrupting presentation"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        speech_and_verbosity_manager.get_manager().interrupt_speech()
        if kill_flash:
            braille.killFlash()
        if self.live_region_manager is not None:
            self.live_region_manager.flushMessages()

    def present_keyboard_event(self, event: input_event.KeyboardEvent) -> None:
        """Presents the KeyboardEvent event."""

        self.get_typing_echo_presenter().echo_keyboard_event(self, event)

    def present_message(
        self,
        full: str,
        brief: str | None = None,
        voice: ACSS | None = None,
        reset_styles: bool = True,
        force: bool = False
    ) -> None:
        """Convenience method to speak a message and 'flash' it in braille."""

        if not full:
            return

        if brief is None:
            brief = full

        speech_manager = speech_and_verbosity_manager.get_manager()
        if speech_manager.get_speech_is_enabled_and_not_muted():
            if not speech_manager.get_messages_are_detailed():
                message = brief
            else:
                message = full
            if message:
                self.speak_message(message, voice=voice, reset_styles=reset_styles, force=force)

        presenter = braille_presenter.get_presenter()
        if not (presenter.use_braille() and presenter.get_flash_messages_are_enabled()):
            return

        message = full if presenter.get_flash_messages_are_detailed() else brief
        if not message:
            return

        if isinstance(message[0], list):
            message = message[0]
        if isinstance(message, list):
            message = [i for i in message if isinstance(i, str)]
            message = " ".join(message)

        duration = presenter.get_flashtime_from_settings()
        braille.displayMessage(message, flashTime=duration)

    @staticmethod
    def __play(sounds: list[Icon | Tone] | Icon | Tone, interrupt: bool = True) -> None:
        if not sounds:
            return

        if not isinstance(sounds, list):
            sounds = [sounds]

        _player = sound.get_player()
        _player.play(sounds[0], interrupt)
        for i in range(1, len(sounds)):
            _player.play(sounds[i], interrupt=False)

    @staticmethod
    def display_message(message: str, cursor: int = -1, flash_time: int = 0) -> None:
        """Displays a single line, setting the cursor to the given position,
        ensuring that the cursor is in view.

        Arguments:
        - message: the string to display
        - cursor: the 0-based cursor position, where -1 (default) means no cursor
        - flash_time:  if non-0, the number of milliseconds to display the
          regions before reverting back to what was there before. A 0 means
          to not do any flashing.  A negative number means to display the
          message until some other message comes along or the user presses
          a cursor routing key.
        """

        if not braille_presenter.get_presenter().use_braille():
            return

        braille.displayMessage(message, cursor, flash_time)

    def spell_item(self, text: str) -> None:
        """Speak the characters in the string one by one."""

        for character in text:
            self.speak_character(character)

    def speak_character(self, character: str) -> None:
        """Speaks a single character."""

        voice = self.speech_generator.voice(string=character)
        speech.speak_character(character, voice[0] if voice else None)

    def speak_message(
        self,
        text: str,
        voice: ACSS | list[ACSS] | None = None,
        interrupt: bool = True,
        reset_styles: bool = True,
        force: bool = False,
        obj: Atspi.Accessible | None = None
    ) -> None:
        """Method to speak a single string."""

        try:
            assert isinstance(text, str)
        except AssertionError:
            tokens = ["DEFAULT: speak_message called with non-string:", text]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            debug.print_exception(debug.LEVEL_WARNING)
            return

        speech_manager = speech_and_verbosity_manager.get_manager()
        if speech_manager.get_speech_is_muted() \
           or (speech_manager.get_only_speak_displayed_text() and not force):
            return

        voices = settings_manager.get_manager().get_setting("voices")
        system_voice = voices.get(settings.SYSTEM_VOICE)
        voice = voice or system_voice
        if voice == system_voice and reset_styles:
            cap_style = speech_manager.get_capitalization_style()
            speech_manager.set_capitalization_style("none")

            punct_style = speech_manager.get_punctuation_level()
            speech_manager.set_punctuation_level("some")

        text = speech_manager.adjust_for_presentation(obj, text)
        voice_to_use: ACSS | dict[str, Any] | None = None
        if isinstance(voice, list) and voice:
            voice_to_use = voice[0]
        elif not isinstance(voice, list):
            voice_to_use = voice
        speech.speak(text, voice_to_use, interrupt)

        if voice == system_voice and reset_styles:
            speech_manager.set_capitalization_style(cap_style)
            speech_manager.set_punctuation_level(punct_style)

    # TODO - JD: This is temporary and in place just so that we could include D-Bus support
    # for the web script's commands prior to having global browse mode.
    # pylint: disable=unused-argument
    def toggle_presentation_mode(
        self,
        event: input_event.InputEvent | None = None,
        document: Atspi.Accessible | None = None,
        notify_user: bool = True
    ) -> bool:
        """Switches between browse mode and focus mode."""

        return False

    def toggle_layout_mode(
        self,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Switches between object mode and layout mode for line presentation."""

        return False

    def enable_sticky_browse_mode(
        self,
        event: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        """Enables sticky browse mode."""

        return False

    def enable_sticky_focus_mode(
        self,
        event: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        """Enables sticky focus mode."""

        return False

    def in_focus_mode(self) -> bool:
        """ Returns True if we're in focus mode."""

        return False

    def focus_mode_is_sticky(self) -> bool:
        """Returns True if we're in 'sticky' focus mode."""

        return False

    def browse_mode_is_sticky(self) -> bool:
        """Returns True if we're in 'sticky' browse mode."""

        return False

    def in_layout_mode(self) -> bool:
        """ Returns True if we're in layout mode."""

        return False
