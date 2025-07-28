# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

"""The default Script for presenting information to the user."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import re
import string

from orca import braille
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
from orca import speechserver

from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_event import TextEventReason
from orca.ax_value import AXValue

class Script(script.Script):

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'

    def __init__(self, app):
        super().__init__(app)
        self._sayAllContexts = []
        self.grab_ids = []

    def setup_input_event_handlers(self):
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

        self.input_event_handlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.say_all,
                cmdnames.SAY_ALL)

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
        self.input_event_handlers.update(self.get_structural_navigator().get_handlers())
        self.input_event_handlers.update(self.get_table_navigator().get_handlers())
        self.input_event_handlers.update(self.get_where_am_i_presenter().get_handlers())
        self.input_event_handlers.update(self.get_learn_mode_presenter().get_handlers())
        self.input_event_handlers.update(self.get_mouse_reviewer().get_handlers())
        self.input_event_handlers.update(self.get_action_presenter().get_handlers())
        self.input_event_handlers.update(self.get_debugging_tools_manager().get_handlers())

    def get_listeners(self):
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

    def __getDesktopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        numeric keypad for focus tracking and flat review.
        """

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("sayAllHandler"),
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Divide",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("routePointerToItemHandler")))

        # We want the user to be able to combine modifiers with the mouse click, therefore we
        # do not "care" about the modifiers -- unless it's the Orca modifier.
        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Divide",
                keybindings.ORCA_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("leftClickReviewItemHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Multiply",
                keybindings.ORCA_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("rightClickReviewItemHandler")))

        return keyBindings

    def __getLaptopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        the main keyboard keys for focus tracking and flat review.
        """

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "semicolon",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("sayAllHandler"),
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "9",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("routePointerToItemHandler")))

        # We want the user to be able to combine modifiers with the mouse click, therefore we
        # do not "care" about the modifiers -- unless it's the Orca modifier.
        keyBindings.add(
            keybindings.KeyBinding(
                "7",
                keybindings.ORCA_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("leftClickReviewItemHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "8",
                keybindings.ORCA_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("rightClickReviewItemHandler")))

        return keyBindings

    def getExtensionBindings(self):
        keyBindings = keybindings.KeyBindings()

        layout = settings_manager.get_manager().get_setting('keyboardLayout')
        isDesktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        bindings = self.get_sleep_mode_manager().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_notification_presenter().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_clipboard_presenter().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_flat_review_finder().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_flat_review_presenter().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_where_am_i_presenter().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_learn_mode_presenter().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_speech_and_verbosity_manager().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_system_information_presenter().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_object_navigator().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_structural_navigator().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_table_navigator().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.bookmarks.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_mouse_reviewer().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_action_presenter().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_debugging_tools_manager().get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def get_key_bindings(self, enabled_only=True):
        """Returns the key bindings for this script."""

        tokens = ["DEFAULT: Getting keybindings for", self]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        keyBindings = script.Script.get_key_bindings(self)

        bindings = self.getDefaultKeyBindings()
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.get_app_key_bindings()
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        bindings = self.getExtensionBindings()
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        try:
            keyBindings = settings_manager.get_manager().override_key_bindings(
                self.input_event_handlers, keyBindings, enabled_only)
        except Exception as error:
            tokens = ["DEFAULT: Exception when overriding keybindings in", self, ":", error]
            debug.print_tokens(debug.LEVEL_WARNING, tokens, True)

        return keyBindings

    def getDefaultKeyBindings(self):
        """Returns the default script's keybindings, i.e. without any of
        the toolkit or application specific commands added."""

        keyBindings = keybindings.KeyBindings()

        layout = settings_manager.get_manager().get_setting('keyboardLayout')
        isDesktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
        if isDesktop:
            for keyBinding in self.__getDesktopBindings().key_bindings:
                keyBindings.add(keyBinding)
        else:
            for keyBinding in self.__getLaptopBindings().key_bindings:
                keyBindings.add(keyBinding)

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("cycleSettingsProfileHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("panBrailleLeftHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("panBrailleRightHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("shutdownHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("preferencesSettingsHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self.input_event_handlers.get("appPreferencesSettingsHandler")))

        # TODO - JD: Move this into the extension commands. That will require a new string
        # and GUI change.
        bindings = self.get_bypass_mode_manager().get_bindings(refresh=True, is_desktop=isDesktop)
        for keyBinding in bindings.key_bindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def get_braille_bindings(self):
        """Returns the braille bindings for this script."""

        msg = 'DEFAULT: Getting braille bindings.'
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
        except Exception as error:
            tokens = ["DEFAULT: Exception getting braille bindings in", self, ":", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        reviewBindings = self.get_flat_review_presenter().get_braille_bindings()
        braille_bindings.update(reviewBindings)

        msg = 'DEFAULT: Finished getting braille bindings.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        return braille_bindings

    def get_app_preferences_gui(self):
        """Return a GtkGrid, or None if there's no app-specific UI."""

        return None

    def get_preferences_from_gui(self):
        """Returns a dictionary with the app-specific preferences."""

        return {}

    def deactivate(self):
        """Called when this script is deactivated."""

        self.point_of_reference = {}

        if self.get_bypass_mode_manager().is_active():
            self.get_bypass_mode_manager().toggle_enabled(self)

        self.remove_key_grabs("script deactivation")
        input_event_manager.get_manager().check_grabbed_bindings()

    def add_key_grabs(self, reason=""):
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

    def remove_key_grabs(self, reason=""):
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

    def refresh_key_grabs(self, reason=""):
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

    def register_event_listeners(self):
        """Registers for listeners needed by this script."""

        event_manager.get_manager().register_script_listeners(self)

    def deregister_event_listeners(self):
        """De-registers the listeners needed by this script."""

        event_manager.get_manager().deregister_script_listeners(self)

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - old_focus: Accessible that is the old locus of focus
        - new_focus: Accessible that is the new locus of focus
        """

        self.utilities.presentFocusChangeReason()

        if not new_focus:
            return

        if AXUtilities.is_defunct(new_focus):
            return

        if old_focus == new_focus and not event.type.endswith("accessible-name"):
            msg = 'DEFAULT: old focus == new focus'
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self.run_find_command_on:
            if self.run_find_command_on == new_focus:
                self.run_find_command_on = None
                self.get_flat_review_finder().find(self)
            return

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        if self.get_learn_mode_presenter().is_active():
            self.get_learn_mode_presenter().quit()

        active_window = self.utilities.topLevelObject(new_focus)
        focus_manager.get_manager().set_active_window(active_window)
        self.update_braille(new_focus)

        if old_focus is None:
            old_focus = active_window

        utterances = self.speech_generator.generate_speech(
            new_focus,
            priorObj=old_focus)

        if self.utilities.shouldInterruptForLocusOfFocusChange(
           old_focus, new_focus, event):
            self.interrupt_presentation()
        speech.speak(utterances, interrupt=False)

    def activate(self):
        """Called when this script is activated."""

        tokens = ["DEFAULT: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        settings_manager.get_manager().load_app_settings(self)

        # TODO - JD: Should these be moved into check_speech_setting?
        self.get_speech_and_verbosity_manager().update_punctuation_level()
        self.get_speech_and_verbosity_manager().update_capitalization_style()
        self.get_speech_and_verbosity_manager().update_synthesizer()

        self.get_structural_navigator().set_mode(self, self._default_sn_mode)

        self.add_key_grabs("script activation")
        tokens = ["DEFAULT: Script for", self.app, "activated"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def update_braille(self, obj, **args):
        """Updates the braille display to show obj."""

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.print_message(debug.LEVEL_INFO, "BRAILLE: update disabled", True)
            return

        if not obj:
            return

        result, focusedRegion = self.braille_generator.generate_braille(obj, **args)
        if not result:
            return

        braille.clear()
        line = braille.Line()
        braille.addLine(line)
        line.addRegions(result)

        extraRegion = args.get('extraRegion')
        if extraRegion:
            line.addRegion(extraRegion)
            braille.setFocus(extraRegion)
        else:
            braille.setFocus(focusedRegion)

        braille.refresh(True)

    ########################################################################
    #                                                                      #
    # INPUT EVENT HANDLERS (AKA ORCA COMMANDS)                             #
    #                                                                      #
    ########################################################################

    def show_app_preferences_gui(self, _event=None):
        """Shows the app Preferences dialog."""

        prefs = {}
        manager = settings_manager.get_manager()
        for key in settings.userCustomizableSettings:
            prefs[key] = manager.get_setting(key)

        ui = orca_gui_prefs.OrcaSetupGUI(self, prefs)
        ui.showGUI()
        return True

    def show_preferences_gui(self, _event=None):
        """Displays the Preferences dialog."""

        manager = settings_manager.get_manager()
        prefs = manager.get_general_settings(manager.profile)
        ui = orca_gui_prefs.OrcaSetupGUI(script_manager.get_manager().get_default_script(), prefs)
        ui.showGUI()
        return True

    def quit_orca(self, _event=None):
        """Quit Orca."""

        orca.shutdown()
        return True

    def pan_braille_left(self, event=None, pan_amount=0):
        """Pans the braille display to the left.  If pan_amount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if isinstance(event, input_event.KeyboardEvent) \
           and not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
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
            movedCaret = False
            if start_offset > 0:
                movedCaret = AXText.set_caret_offset(focus, start_offset - 1)

            # If we didn't move the caret and we're in a terminal, we
            # jump into flat review to review the text.  See
            # http://bugzilla.gnome.org/show_bug.cgi?id=482294.
            #
            if not movedCaret and AXUtilities.is_terminal(focus):
                self.get_flat_review_presenter().go_start_of_line(self, event)
                self.get_flat_review_presenter().go_previous_character(self, event)
        else:
            braille.panLeft(pan_amount)
            # We might be panning through a flashed message.
            braille.resetFlashTimer()
            braille.refresh(False, stopFlash=False)

        return True

    def pan_braille_right(self, event=None, pan_amount=0):
        """Pans the braille display to the right.  If pan_amount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the end will take you to the beginning of the next line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if isinstance(event, input_event.KeyboardEvent) \
           and not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
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

    def go_braille_home(self, event=None):
        """Returns to the component with focus."""

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()
            return True

        self.interrupt_presentation()
        return braille.returnToRegionWithFocus(event)

    def set_contracted_braille(self, event=None):
        """Toggles contracted braille."""

        braille.set_contracted_braille(event)
        return True

    def process_routing_key(self, event=None):
        """Processes a cursor routing key."""

        # Don't kill flash here because it will restore the previous contents and
        # then process the routing key. If the contents accept a click action, this
        # would result in clicking on the link instead of clearing the flash message.
        self.interrupt_presentation(kill_flash=False)
        braille.process_routing_key(event)
        return True

    def process_braille_cut_begin(self, event=None):
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

    def process_braille_cut_line(self, event=None):
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        obj, offset = braille.getCaretContext(event)
        if offset < 0:
            return True

        self.interrupt_presentation()
        start_offset = AXText.get_selection_start_offset(obj)
        end_offset = AXText.get_selection_end_offset(obj)
        if (start_offset < 0 or end_offset < 0):
            caretOffset = AXText.get_caret_offset(obj)
            start_offset = min(offset, caretOffset)
            end_offset = max(offset, caretOffset)

        AXText.set_selected_text(obj, start_offset, end_offset)
        text = AXText.get_selected_text(obj)[0]
        self.get_clipboard_presenter().set_text(text)
        return True

    def route_pointer_to_item(self, event=None):
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

    def left_click_item(self, event=None):
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

    def right_click_item(self, event=None):
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

    def say_all(self, _event, obj=None, offset=None):
        """Speaks the contents of obj."""

        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        tokens = ["DEFAULT: SayAll requested starting from", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not obj or AXObject.is_dead(obj):
            self.present_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        speech.say_all(self.textLines(obj, offset), self.__sayAllProgressCallback)
        return True

    def cycle_settings_profile(self, _event=None):
        """Cycle through the user's existing settings profiles."""

        profiles = settings_manager.get_manager().available_profiles()
        if not (profiles and profiles[0]):
            self.present_message(messages.PROFILE_NOT_FOUND)
            return True

        def isMatch(x):
            return x is not None and x[1] == settings_manager.get_manager().get_profile()

        current = list(filter(isMatch, profiles))[0]
        try:
            name, profileID = profiles[profiles.index(current) + 1]
        except IndexError:
            name, profileID = profiles[0]

        settings_manager.get_manager().set_profile(profileID, updateLocale=True)

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
    ########################################################################

    def on_active_changed(self, event):
        """Callback for object:state-changed:active accessibility events."""

        window = event.source
        if AXUtilities.is_dialog_or_alert(window) or AXUtilities.is_frame(window):
            if event.detail1 and not AXUtilities.can_be_active_window(window):
                return

            sourceIsActiveWindow = window == focus_manager.get_manager().get_active_window()
            if sourceIsActiveWindow and not event.detail1:
                focus = focus_manager.get_manager().get_locus_of_focus()
                if AXObject.find_ancestor_inclusive(focus, AXUtilities.is_menu):
                    msg = "DEFAULT: Ignoring event. In menu."
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    return

                msg = "DEFAULT: Event is for active window. Clearing state."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(None)
                return

            if not sourceIsActiveWindow and event.detail1:
                msg = "DEFAULT: Updating active window."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(
                    window, set_window_as_focus=True, notify_script=True)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if AXUtilities.is_presentable_active_descendant_change(event):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if AXUtilities.is_presentable_checked_change(event):
            self.present_object(event.source, alreadyFocused=True, interrupt=True)

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

    def on_children_removed(self, event):
        """Callback for object:children-changed:remove accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if focus != event.source:
            if not AXUtilities.is_focused(event.source):
                msg = "DEFAULT: Change is from unfocused source that is not the locus of focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return
            # TODO - JD: See if this can be removed. If it's still needed document why.
            manager.set_locus_of_focus(event, event.source, False)

        obj, offset = manager.get_last_cursor_position()
        if offset == event.detail1 and obj == event.source:
            msg = "DEFAULT: Event is for last saved cursor position"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        offset = AXText.get_caret_offset(event.source)
        manager.set_last_cursor_position(event.source, offset)

        ignore = [TextEventReason.CUT,
                  TextEventReason.PASTE,
                  TextEventReason.REDO,
                  TextEventReason.UNDO]
        if reason in ignore:
            msg = f"DEFAULT: Ignoring event due to reason ({reason})"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return

        if AXText.has_selected_text(event.source):
            msg = "DEFAULT: Event source has text selections"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.utilities.handleTextSelectionChange(event.source)
            return

        text, _start, _end = AXText.get_cached_selected_text(obj)
        if text and self.utilities.handleTextSelectionChange(obj):
            msg = "DEFAULT: Event handled as text selection change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = "DEFAULT: Presenting text at new caret position"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._presentTextAtNewCaretPosition(event, reason=reason)

    def on_description_changed(self, event):
        """Callback for object:property-change:accessible-description events."""

        if AXUtilities.is_presentable_description_change(event):
            self.present_message(event.any_data)

    def on_document_attributes_changed(self, event):
        """Callback for document:attributes-changed accessibility events."""

    def on_document_reload(self, event):
        """Callback for document:reload accessibility events."""

    def on_document_load_complete(self, event):
        """Callback for document:load-complete accessibility events."""

    def on_document_load_stopped(self, event):
        """Callback for document:load-stopped accessibility events."""

    def on_document_page_changed(self, event):
        """Callback for document:page-changed accessibility events."""

        if event.detail1 < 0:
            return

        if not AXDocument.did_page_change(event.source):
            return

        self.present_message(messages.PAGE_NUMBER % event.detail1)

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "expanded-changed event.")
        if not AXUtilities.is_presentable_expanded_change(event):
            return

        self.present_object(event.source, alreadyFocused=True, interrupt=True)
        details = self.utilities.detailsContentForObject(event.source)
        for detail in details:
            self.speak_message(detail, interrupt=False)

    def on_indeterminate_changed(self, event):
        """Callback for object:state-changed:indeterminate accessibility events."""

        if AXUtilities.is_presentable_indeterminate_change(event):
            self.present_object(event.source, alreadyFocused=True, interrupt=True)

    def on_invalid_entry_changed(self, event):
        """Callback for object:state-changed:invalid-entry accessibility events."""

        if not AXUtilities.is_presentable_invalid_entry_change(event):
            return

        if event.detail1:
            msg = self.speech_generator.get_error_message(event.source)
        else:
            msg = messages.INVALID_ENTRY_FIXED
        self.speak_message(msg)
        self.update_braille(event.source)

    def on_mouse_button(self, event):
        """Callback for mouse:button events."""

        input_event_manager.get_manager().process_mouse_button_event(event)

    def on_announcement(self, event):
        """Callback for object:announcement events."""

        if isinstance(event.any_data, str):
            self.present_message(event.any_data)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if not AXUtilities.is_presentable_name_change(event):
            return

        manager = focus_manager.get_manager()
        if event.source == manager.get_locus_of_focus():
            # Force the update so that braille is refreshed.
            manager.set_locus_of_focus(event, event.source, True, True)
            return

        self.present_message(event.any_data)

    def on_object_attributes_changed(self, event):
        """Callback for object:attributes-changed accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "object-attributes-changed event.")

    def on_pressed_changed(self, event):
        """Callback for object:state-changed:pressed accessibility events."""

        if AXUtilities.is_presentable_pressed_change(event):
            self.present_object(event.source, alreadyFocused=True, interrupt=True)

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if not AXUtilities.is_presentable_selected_change(event):
            return

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return

        announceState = False
        manager = input_event_manager.get_manager()
        if manager.last_event_was_space():
            announceState = True
        elif (manager.last_event_was_up() or manager.last_event_was_down()) \
                and AXUtilities.is_table_cell(event.source):
            announceState = AXUtilities.is_selected(event.source)

        if not announceState:
            return

        # TODO - JD: Unlike the other state-changed callbacks, it seems unwise
        # to call generate_speech() here because that also will present the
        # expandable state if appropriate for the object type. The generators
        # need to gain some smarts w.r.t. state changes.

        if event.detail1:
            self.speak_message(messages.TEXT_SELECTED, interrupt=False)
        else:
            self.speak_message(messages.TEXT_UNSELECTED, interrupt=False)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.utilities.handlePasteLocusOfFocusChange():
            if self.utilities.topLevelObjectIsActiveAndCurrent(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
        elif self.utilities.handleContainerSelectionChange(event.source):
            return
        elif AXUtilities.manages_descendants(event.source):
            return
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
                return

        if AXUtilities.is_tree_or_tree_table(event.source):
            active_window = focus_manager.get_manager().get_active_window()
            if not AXObject.find_ancestor(event.source, lambda x: x and x == active_window):
                tokens = ["DEFAULT: Ignoring event:", event.source, "is not inside", active_window]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return

        # If the current item's selection is toggled, we'll present that
        # via the state-changed event.
        if input_event_manager.get_manager().last_event_was_space():
            return

        if AXUtilities.is_combo_box(event.source) and not AXUtilities.is_expanded(event.source):
            if AXUtilities.is_focused(
                 AXObject.find_descendant(event.source, AXUtilities.is_text_input)):
                return
        elif AXUtilities.is_page_tab_list(event.source) \
            and self.get_flat_review_presenter().is_active():
            # If a wizard-like notebook page being reviewed changes, we might not get
            # any events to update the locusOfFocus. As a result, subsequent flat
            # review commands will continue to present the stale content.
            # TODO - JD: We can potentially do some automatic reading here.
            self.get_flat_review_presenter().quit()

        mouseReviewItem = self.get_mouse_reviewer().get_current_item()
        selectedChildren = self.utilities.selectedChildren(event.source)
        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus in selectedChildren:
            msg = "DEFAULT: Ignoring event believed to be redundant to focus change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        for child in selectedChildren:
            if AXObject.find_ancestor(focus, lambda x: x == child):
                tokens = ["DEFAULT: Child", child, "is ancestor of locusOfFocus"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return

            if child == mouseReviewItem:
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

    def on_sensitive_changed(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        if not AXUtilities.is_focused(event.source):
            tokens = ["DEFAULT:", event.source, "lacks focused state. Clearing cache."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            AXObject.clear_cache(event.source, reason="Event detail1 does not match state.")
            if not AXUtilities.is_focused(event.source):
                msg = "DEFAULT: Clearing cache did not update state."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return

        obj = event.source
        window, dialog = self.utilities.frameAndDialog(obj)
        if window and not AXUtilities.can_be_active_window(window) and not dialog:
            return

        if AXObject.get_child_count(obj) and not AXUtilities.is_combo_box(obj):
            selectedChildren = self.utilities.selectedChildren(obj)
            if selectedChildren:
                obj = selectedChildren[0]

        focus_manager.get_manager().set_locus_of_focus(event, obj)

    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        obj = event.source
        if AXUtilities.is_notification(obj):
            if not event.detail1:
                return

            self.speak_message(self.speech_generator.get_localized_role_name(obj))
            msg = self.utilities.getNotificationContent(obj)
            self.present_message(msg, reset_styles=False)
            self.get_notification_presenter().save_notification(msg)
            return

        if AXUtilities.is_tool_tip(obj):
            was_f1 = input_event_manager.get_manager().last_event_was_f1()
            if not was_f1 and not settings_manager.get_manager().get_setting('presentToolTips'):
                return
            if event.detail1:
                self.present_object(obj, interrupt=True)
                return

            focus = focus_manager.get_manager().get_locus_of_focus()
            if focus and was_f1:
                obj = focus
                self.present_object(obj, priorObj=event.source, interrupt=True)
                return

    def on_text_attributes_changed(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        if not AXUtilities.is_presentable_text_attributes_change(event):
            return

        self.speakMisspelledIndicator(event.source)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if not AXUtilities.is_presentable_text_deletion(event):
            return

        reason = AXUtilities.get_text_event_reason(event)
        self.utilities.handleUndoTextEvent(event)
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_DELETION:
            msg = "DEFAULT: Deletion is believed to be due to deleting selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.present_message(messages.SELECTION_DELETED)
            AXText.update_cached_selected_text(event.source)
            return

        text = self.utilities.deletedText(event)
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
            return

        if len(text) == 1:
            self.speak_character(text)
        else:
            voice = self.speech_generator.voice(string=text)
            manager = speech_and_verbosity_manager.get_manager()
            text = manager.adjust_for_presentation(event.source, text)
            self.speak_message(text, voice)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not AXUtilities.is_presentable_text_insertion(event):
            return

        reason = AXUtilities.get_text_event_reason(event)
        self.utilities.handleUndoTextEvent(event)
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_RESTORATION:
            msg = "DEFAULT: Insertion is believed to be due to restoring selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.present_message(messages.SELECTION_RESTORED)
            AXText.update_cached_selected_text(event.source)
            return

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
        text = self.utilities.insertedText(event)
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
            return

        if settings_manager.get_manager().get_setting('enableEchoBySentence') \
           and self.echo_previous_sentence(event.source):
            return

        if settings_manager.get_manager().get_setting('enableEchoByWord'):
            self.echo_previous_word(event.source)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        # We won't handle undo here as it can lead to double-presentation.
        # If there is an application for which text-changed events are
        # missing upon undo, handle them in an app or toolkit script.

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.UNKNOWN:
            msg = "DEFAULT: Ignoring event because reason for change is unknown"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return
        if reason == TextEventReason.SEARCH_PRESENTABLE:
            msg = "DEFAULT: Presenting line believed to be search match"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.say_line(event.source)
            AXText.update_cached_selected_text(event.source)
            return
        if reason == TextEventReason.SEARCH_UNPRESENTABLE:
            msg = "DEFAULT: Ignoring event believed to be unpresentable search results change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return
        if reason in [TextEventReason.CUT, TextEventReason.BACKSPACE, TextEventReason.DELETE]:
            msg = "DEFAULT: Ignoring event believed to be text removal"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXText.update_cached_selected_text(event.source)
            return

        self.utilities.handleTextSelectionChange(event.source)
        self.update_braille(event.source)

    def on_column_reordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "column-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return

        if event.source != AXTable.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return

        self.present_message(messages.TABLE_REORDERED_COLUMNS)

    def on_row_reordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "row-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return

        if event.source != AXTable.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return

        self.present_message(messages.TABLE_REORDERED_ROWS)

    def on_value_changed(self, event):
        """Callback for object:property-change:accessible-value accessibility events."""

        if not AXValue.did_value_change(event.source):
            return

        is_progress_bar_update, msg = self.utilities.isProgressBarUpdate(event.source)
        tokens = ["DEFAULT: Is progress bar update:", is_progress_bar_update, ",", msg]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = focus_manager.get_manager()
        if not is_progress_bar_update and event.source != manager.get_locus_of_focus():
            msg = "DEFAULT: Source != locusOfFocus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if AXUtilities.is_spin_button(event.source):
            manager.set_last_cursor_position(event.source, AXText.get_caret_offset(event.source))

        if not is_progress_bar_update:
            self.interrupt_presentation()

        self.update_braille(event.source, isProgressBarUpdate=is_progress_bar_update)
        speech.speak(self.speech_generator.generate_speech(
            event.source, alreadyFocused=True, isProgressBarUpdate=is_progress_bar_update))
        self.__play(self.sound_generator.generate_sound(
            event.source, alreadyFocused=True, isProgressBarUpdate=is_progress_bar_update))

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        if not AXUtilities.can_be_active_window(event.source):
            return

        if event.source == focus_manager.get_manager().get_active_window():
            msg = "DEFAULT: Event is for active window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self.point_of_reference = {}

        focus_manager.get_manager().set_active_window(event.source)
        if AXObject.get_child_count(event.source) == 1:
            child = AXObject.get_child(event.source, 0)
            # Popup menus in Chromium live in a menu bar whose first child is a panel.
            if AXUtilities.is_menu_bar(child):
                child = AXObject.find_descendant(child, AXUtilities.is_menu)
            if AXUtilities.is_menu(child):
                focus_manager.get_manager().set_locus_of_focus(event, child)
                return

        focus_manager.get_manager().set_locus_of_focus(event, event.source)

    def on_window_created(self, event):
        """Callback for window:create accessibility events."""

    def on_window_destroyed(self, event):
        """Callback for window:destroy accessibility events."""

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.find_ancestor_inclusive(focus, AXUtilities.is_menu):
            msg = "DEFAULT: Ignoring event. In menu."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if event.source != focus_manager.get_manager().get_active_window():
            msg = "DEFAULT: Ignoring event. Not for active window"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        if self.get_learn_mode_presenter().is_active():
            self.get_learn_mode_presenter().quit()

        self.point_of_reference = {}

        focus_manager.get_manager().clear_state("Window deactivated")
        script_manager.get_manager().set_active_script(None, "Window deactivated")

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def _presentTextAtNewCaretPosition(self, event, other_obj=None, reason=TextEventReason.UNKNOWN):
        """Presents text at the new position, based on heuristics. Returns True if handled."""

        obj = other_obj or event.source
        self.updateBrailleForNewCaretPosition(obj)
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

    def _rewindSayAll(self, context, minCharCount=10):
        if not settings_manager.get_manager().get_setting('rewindAndFastForwardInSayAll'):
            return False

        index = self._sayAllContexts.index(context)
        self._sayAllContexts = self._sayAllContexts[0:index]
        while self._sayAllContexts:
            context = self._sayAllContexts.pop()
            if context.end_offset - context.start_offset > minCharCount:
                break

        # TODO - JD: Why do we only update focus if text is supported?
        if AXText.set_caret_offset(context.obj, context.start_offset):
            focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)

        self.say_all(None, context.obj, context.start_offset)
        return True

    def _fastForwardSayAll(self, context):
        if not settings_manager.get_manager().get_setting('rewindAndFastForwardInSayAll'):
            return False

        # TODO - JD: Why do we only update focus if text is supported?
        if AXText.set_caret_offset(context.obj, context.end_offset):
            focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)

        self.say_all(None, context.obj, context.end_offset)
        return True

    def __sayAllProgressCallback(self, context, progressType):
        # TODO - JD: Can we scroll the content into view instead of setting
        # the caret?

        # TODO - JD: This condition shouldn't happen. Make sure of that.
        if AXText.character_at_offset_is_eoc(context.obj, context.current_offset):
            return

        if progressType == speechserver.SayAllContext.PROGRESS:
            focus_manager.get_manager().emit_region_changed(
                context.obj, context.current_offset, context.current_end_offset,
                focus_manager.SAY_ALL)
            return

        if progressType == speechserver.SayAllContext.INTERRUPTED:
            manager = input_event_manager.get_manager()
            if manager.last_event_was_keyboard():
                if manager.last_event_was_down() and self._fastForwardSayAll(context):
                    return
                if manager.last_event_was_up() and self._rewindSayAll(context):
                    return

        self._sayAllContexts = []
        focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)
        focus_manager.get_manager().emit_region_changed(context.obj, context.current_offset)
        AXText.set_caret_offset(context.obj, context.current_offset)

    def echo_previous_sentence(self, obj):
        """Speaks the sentence prior to the caret if at a sentence boundary."""

        offset = AXText.get_caret_offset(obj)
        char, start = AXText.get_character_at_offset(obj, offset - 1)[0:-1]
        previous_char, previous_start = AXText.get_character_at_offset(obj, start - 1)[0:-1]
        if not (char in string.whitespace + "\u00a0" and previous_char in "!.?:;"):
            return False

        sentence = AXText.get_sentence_at_offset(obj, previous_start)[0]
        if not sentence:
            msg = "DEFAULT: At a sentence boundary, but no sentence found. Missing implementation?"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        voice = self.speech_generator.voice(obj=obj, string=sentence)
        self.speak_message(sentence, voice, obj=obj)
        return True

    def echo_previous_word(self, obj):
        """Speaks the word prior to the caret if at a word boundary."""

        offset = AXText.get_caret_offset(obj)
        if offset == -1:
            offset = AXText.get_character_count(obj)

        if offset <= 0:
            return False

        # If the previous character is not a word delimiter, there's nothing to echo.
        prev_char, prev_start = AXText.get_character_at_offset(obj, offset - 1)[0:-1]
        if prev_char not in string.punctuation + string.whitespace + "\u00a0":
            return False

        # Two back-to-back delimiters should not result in a re-echo.
        prev_char, prev_start = AXText.get_character_at_offset(obj, prev_start - 1)[0:-1]
        if prev_char in string.punctuation + string.whitespace + "\u00a0":
            return False

        word = AXText.get_word_at_offset(obj, prev_start)[0]
        if not word:
            return False

        voice = self.speech_generator.voice(obj=obj, string=word)
        self.speak_message(word, voice, obj=obj)
        return True

    def say_character(self, obj):
        """Speak the character at the caret."""

        offset = AXText.get_caret_offset(obj)

        # If we have selected text and the last event was a move to the
        # right, then speak the character to the left of where the text
        # caret is (i.e. the selected character).
        if input_event_manager.get_manager().last_event_was_forward_caret_selection():
            offset -= 1

        character, start_offset, end_offset = AXText.get_character_at_offset(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj, start_offset, end_offset, focus_manager.CARET_TRACKING)

        if not character or character == '\r':
            character = "\n"

        speak_blank_lines = settings_manager.get_manager().get_setting("speakBlankLines")
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

        self.speakMisspelledIndicator(obj, offset)
        self.speak_character(character)
        self.point_of_reference["lastTextUnitSpoken"] = "char"

    def say_line(self, obj, offset=None):
        """Speaks the line of text at the given offset or at the caret."""

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
            split = self.utilities.splitSubstringByLanguage(obj, start_offset, end_offset)
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
                result = [text]
                result.extend(voice)
                utterance.append(result)
            speech.speak(utterance)
        elif settings_manager.get_manager().get_setting("speakBlankLines"):
            self.speak_message(messages.BLANK, interrupt=False)

        self.point_of_reference["lastTextUnitSpoken"] = "line"

    def say_phrase(self, obj, start_offset, end_offset):
        """Speaks the text of an Accessible object between the start and end offsets."""

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
            utterance = [phrase]
            utterance.extend(voice)
            speech.speak(utterance)
        else:
            self.speak_character(phrase)

        self.point_of_reference["lastTextUnitSpoken"] = "phrase"

    def say_word(self, obj):
        """Speaks the word at the caret, taking into account the previous caret position."""


        offset = AXText.get_caret_offset(obj)
        word, start_offset, end_offset = \
            self.utilities.getWordAtOffsetAdjustedForNavigation(obj, offset)

        # Announce when we cross a hard line boundary.
        if "\n" in word:
            if settings_manager.get_manager().get_setting('enableSpeechIndentation'):
                self.speak_character("\n")
            if word.startswith("\n"):
                start_offset += 1
            elif word.endswith("\n"):
                end_offset -= 1
            word = AXText.get_substring(obj, start_offset, end_offset)

        # say_phrase() is useful because it handles punctuation verbalization, but we don't want
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

        self.speakMisspelledIndicator(obj, start_offset)
        self.say_phrase(obj, start_offset, end_offset)
        self.point_of_reference["lastTextUnitSpoken"] = "word"

    def present_object(self, obj, **args):
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

    def textLines(self, obj, offset=None):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        prior_obj = obj
        if offset is None:
            offset = AXText.get_caret_offset(obj)

        while obj:
            speech.speak(self.speech_generator.generate_context(obj, priorObj=prior_obj))

            style = settings_manager.get_manager().get_setting('sayAllStyle')
            if style == settings.SAYALL_STYLE_SENTENCE and AXText.supports_sentence_iteration(obj):
                iterator = AXText.iter_sentence
            else:
                iterator = AXText.iter_line

            for text, start, end in iterator(obj, offset):
                voice = self.speech_generator.voice(obj=obj, string=text)
                if voice and isinstance(voice, list):
                    voice = voice[0]

                manager = speech_and_verbosity_manager.get_manager()
                text = manager.adjust_for_presentation(obj, text, start)
                context = speechserver.SayAllContext(obj, text, start, end)
                tokens = ["DEFAULT:", context]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

                self._sayAllContexts.append(context)
                self.get_event_synthesizer().scroll_into_view(obj, start, end)
                yield [context, voice]

            prior_obj = obj
            offset = 0
            obj = self.utilities.findNextObject(obj)

        self._sayAllContexts = []

    def phoneticSpellCurrentItem(self, itemString):
        """Phonetically spell the current flat review word or line.

        Arguments:
        - itemString: the string to phonetically spell.
        """

        for (charIndex, character) in enumerate(itemString):
            voice = self.speech_generator.voice(string=character)
            phoneticString = phonnames.get_phonetic_name(character.lower())
            self.speak_message(phoneticString, voice)

    def speakMisspelledIndicator(self, obj, offset=None):
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

    def present_keyboard_event(self, event):
        """Presents the keyboard event to the user."""

        if not event.is_pressed_key():
            self.utilities.clearCachedCommandState()

        if not event.should_echo() or event.is_orca_modified():
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_dialog_or_window(focus):
            focused_object = focus_manager.get_manager().find_focused_object()
            if focused_object:
                focus_manager.get_manager().set_locus_of_focus(None, focused_object, False)
                AXObject.get_role(focused_object)

        if AXUtilities.is_password_text(focus) and not event.is_locking_key():
            return False

        if not event.is_pressed_key():
            return False

        braille.displayKeyEvent(event)
        orca_modifier_presssed = event.is_orca_modifier() and event.is_pressed_key()
        if event.is_character_echoable() and not orca_modifier_presssed:
            return False

        msg = "DEFAULT: Presenting keyboard event"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.speak_key_event(event)
        return True

    def present_message(self, full, brief=None, voice=None, reset_styles=True, force=False):
        """Convenience method to speak a message and 'flash' it in braille."""

        if not full:
            return

        if brief is None:
            brief = full

        if settings_manager.get_manager().get_setting('enableSpeech'):
            if not settings_manager.get_manager().get_setting('messagesAreDetailed'):
                message = brief
            else:
                message = full
            if message:
                self.speak_message(message, voice=voice, reset_styles=reset_styles, force=force)

        if (settings_manager.get_manager().get_setting('enableBraille') \
             or settings_manager.get_manager().get_setting('enableBrailleMonitor')) \
           and settings_manager.get_manager().get_setting('enableFlashMessages'):
            if not settings_manager.get_manager().get_setting('flashIsDetailed'):
                message = brief
            else:
                message = full
            if not message:
                return

            if isinstance(message[0], list):
                message = message[0]
            if isinstance(message, list):
                message = [i for i in message if isinstance(i, str)]
                message = " ".join(message)

            if settings_manager.get_manager().get_setting('flashIsPersistent'):
                duration = -1
            else:
                duration = settings_manager.get_manager().get_setting('brailleFlashTime')

            braille.displayMessage(message, flashTime=duration)

    @staticmethod
    def __play(sounds, interrupt=True):
        if not sounds:
            return

        if not isinstance(sounds, list):
            sounds = [sounds]

        _player = sound.get_player()
        _player.play(sounds[0], interrupt)
        for i in range(1, len(sounds)):
            _player.play(sounds[i], interrupt=False)

    @staticmethod
    def display_message(message, cursor=-1, flash_time=0):
        """Displays a single line, setting the cursor to the given positon
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

        if not settings_manager.get_manager().get_setting("enableBraille") \
           and not settings_manager.get_manager().get_setting("enableBrailleMonitor"):
            debug.print_message(debug.LEVEL_INFO, "BRAILLE: display message disabled", True)
            return

        braille.displayMessage(message, cursor, flash_time)

    def updateBrailleForNewCaretPosition(self, obj):
        """Try to reposition the cursor without having to do a full update."""

        if not settings_manager.get_manager().get_setting("enableBraille") \
           and not settings_manager.get_manager().get_setting("enableBrailleMonitor"):
            debug.print_message(debug.LEVEL_INFO, "BRAILLE: update caret disabled", True)
            return

        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) and region.accessible == obj:
                if region.repositionCursor():
                    braille.refresh(True)
                    brailleNeedsRepainting = False
                break

        if brailleNeedsRepainting:
            self.update_braille(obj)

    ########################################################################
    #                                                                      #
    # Speech methods                                                       #
    # (scripts should not call methods in speech.py directly)              #
    #                                                                      #
    ########################################################################

    def speak_key_event(self, event):
        """Method to speak a keyboard event. Scripts should use this method
        rather than calling speech.speakKeyEvent directly."""

        key_name = None
        if event.is_printable_key():
            key_name = event.get_key_name()

        voice = self.speech_generator.voice(string=key_name)
        speech.speak_key_event(event, voice)

    def spell_item(self, string):
        """Speak the characters in the string one by one."""

        for character in string:
            self.speak_character(character)

    def speak_character(self, character):
        """Method to speak a single character."""

        voice = self.speech_generator.voice(string=character)
        speech.speak_character(character, voice)

    def speak_message(
        self, text, voice=None, interrupt=True, reset_styles=True, force=False, obj=None):
        """Method to speak a single string."""

        try:
            assert isinstance(text, str)
        except AssertionError:
            tokens = ["DEFAULT: speakMessage called with non-string:", text]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            debug.print_exception(debug.LEVEL_WARNING)
            return

        manager = settings_manager.get_manager()
        if not manager.get_setting('enableSpeech') \
           or (manager.get_setting('onlySpeakDisplayedText') and not force):
            return

        voices = settings_manager.get_manager().get_setting('voices')
        systemVoice = voices.get(settings.SYSTEM_VOICE)

        voice = voice or systemVoice
        if voice == systemVoice and reset_styles:
            capStyle = settings_manager.get_manager().get_setting('capitalizationStyle')
            manager.set_setting('capitalizationStyle', settings.CAPITALIZATION_STYLE_NONE)
            self.get_speech_and_verbosity_manager().update_capitalization_style()

            punctStyle = manager.get_setting('verbalizePunctuationStyle')
            manager.set_setting('verbalizePunctuationStyle', settings.PUNCTUATION_STYLE_NONE)
            self.get_speech_and_verbosity_manager().update_punctuation_level()

        text = speech_and_verbosity_manager.get_manager().adjust_for_presentation(obj, text)
        speech.speak(text, voice, interrupt)

        if voice == systemVoice and reset_styles:
            manager.set_setting('capitalizationStyle', capStyle)
            self.get_speech_and_verbosity_manager().update_capitalization_style()

            manager.set_setting('verbalizePunctuationStyle', punctStyle)
            self.get_speech_and_verbosity_manager().update_punctuation_level()
