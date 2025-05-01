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
import time

from orca import braille
from orca import cmdnames
from orca import debug
from orca import event_manager
from orca import focus_manager
from orca import flat_review
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

        self.targetCursorCell = None

        self.justEnteredFlatReviewMode = False

        # Keep track of the last time we issued a mouse routing command
        # so that we can guess if a change resulted from our moving the
        # pointer.
        #
        self.lastMouseRoutingTime = None

        self._inSayAll = False
        self._sayAllIsInterrupted = False
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

        bindings = self.get_toolkit_key_bindings()
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

        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self.point_of_reference = {}

        if self.get_bypass_mode_manager().is_active():
            self.get_bypass_mode_manager().toggle_enabled(self)

        self.remove_key_grabs("script deactivation")

    def add_key_grabs(self, reason=""):
        """ Sets up the key grabs currently needed by this script. """

        msg = "DEFAULT: Setting up key bindings"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.key_bindings = self.get_key_bindings()
        self.key_bindings.add_key_grabs(reason)
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()

    def remove_key_grabs(self, reason=""):
        """ Removes this script's AT-SPI key grabs. """

        orca_modifier_manager.get_manager().remove_grabs_for_orca_modifiers()
        self.key_bindings.remove_key_grabs(reason)

        msg = "DEFAULT: Clearing key bindings"
        debug.print_message(debug.LEVEL_INFO, msg, True)
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

    def _save_focused_object_info(self, obj):
        """Saves some basic information about obj. Note that this method is
        intended to be called primarily (if not only) by locus_of_focus_changed()."""

        # We want to save the offset for text objects because some apps and
        # toolkits emit caret-moved events immediately after a text object
        # gains focus, even though the caret has not actually moved.
        caretOffset = AXText.get_caret_offset(obj)
        self._saveLastCursorPosition(obj, max(0, caretOffset))
        AXText.update_cached_selected_text(obj)

        # We want to save the current row and column of a newly focused
        # or selected table cell so that on subsequent cell focus/selection
        # we only present the changed location.
        row, column = AXTable.get_cell_coordinates(obj, find_cell=True)
        self.point_of_reference['lastColumn'] = column
        self.point_of_reference['lastRow'] = row

        AXUtilities.save_object_info_for_events(obj)

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

        try:
            if self.run_find_command:
                # Then the Orca Find dialog has just given up focus
                # to the original window.  We don't want to speak
                # the window title, current line, etc.
                return
        except Exception:
            pass

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
            self.presentationInterrupt()
        speech.speak(utterances, interrupt=False)
        self._save_focused_object_info(new_focus)

    def activate(self):
        """Called when this script is activated."""

        tokens = ["DEFAULT: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        settings_manager.get_manager().load_app_settings(self)

        # TODO - JD: Should these be moved into check_speech_setting?
        self.get_speech_and_verbosity_manager().update_punctuation_level()
        self.get_speech_and_verbosity_manager().update_capitalization_style()
        self.get_speech_and_verbosity_manager().update_synthesizer()

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

        self.clearBraille()
        line = self.getNewBrailleLine()
        braille.addLine(line)
        self.addBrailleRegionsToLine(result, line)

        extraRegion = args.get('extraRegion')
        if extraRegion:
            self.addBrailleRegionToLine(extraRegion, line)
            self.setBrailleFocus(extraRegion)
        else:
            self.setBrailleFocus(focusedRegion)

        self.refreshBraille(True)

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
            if self.isBrailleBeginningShowing():
                self.get_flat_review_presenter().go_start_of_line(self, event)
                self.get_flat_review_presenter().go_previous_character(self, event)
            else:
                self.panBrailleInDirection(pan_amount, panToLeft=True)

            self._setFlatReviewContextToBeginningOfBrailleDisplay()
            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.isBrailleBeginningShowing() and self.utilities.isTextArea(focus):
            # If we're at the beginning of a line of a multiline text
            # area, then force it's caret to the end of the previous
            # line.  The assumption here is that we're currently
            # viewing the line that has the caret -- which is a pretty
            # good assumption for focus tacking mode.  When we set the
            # caret position, we will get a caret event, which will
            # then update the braille.
            #
            startOffset = AXText.get_line_at_offset(focus)[1]
            movedCaret = False
            if startOffset > 0:
                movedCaret = AXText.set_caret_offset(focus, startOffset - 1)

            # If we didn't move the caret and we're in a terminal, we
            # jump into flat review to review the text.  See
            # http://bugzilla.gnome.org/show_bug.cgi?id=482294.
            #
            if not movedCaret and AXUtilities.is_terminal(focus):
                context = self.getFlatReviewContext()
                context.goBegin(flat_review.Context.LINE)
                self.get_flat_review_presenter().go_previous_character(self, event)
        else:
            self.panBrailleInDirection(pan_amount, panToLeft=True)
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            self.refreshBraille(False, stopFlash=False)

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
            if self.isBrailleEndShowing():
                self.get_flat_review_presenter().go_end_of_line(self, event)
                # Reviewing the next character also updates the braille output
                # and refreshes the display.
                self.get_flat_review_presenter().go_next_character(self, event)
                return True
            self.panBrailleInDirection(pan_amount, panToLeft=False)
            self._setFlatReviewContextToBeginningOfBrailleDisplay()
            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.isBrailleEndShowing() and self.utilities.isTextArea(focus):
            # If we're at the end of a line of a multiline text area, then
            # force it's caret to the beginning of the next line.  The
            # assumption here is that we're currently viewing the line that
            # has the caret -- which is a pretty good assumption for focus
            # tacking mode.  When we set the caret position, we will get a
            # caret event, which will then update the braille.
            #
            endOffset = AXText.get_line_at_offset(focus)[2]
            if endOffset < AXText.get_character_count(focus):
                AXText.set_caret_offset(focus, endOffset)
        else:
            self.panBrailleInDirection(pan_amount, panToLeft=False)
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            self.refreshBraille(False, stopFlash=False)

        return True

    def go_braille_home(self, event=None):
        """Returns to the component with focus."""

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()
            return True

        self.presentationInterrupt()
        return braille.returnToRegionWithFocus(event)

    def set_contracted_braille(self, event=None):
        """Toggles contracted braille."""

        self._set_contracted_braille(event)
        return True

    def process_routing_key(self, event=None):
        """Processes a cursor routing key."""

        # Don't kill flash here because it will restore the previous contents and
        # then process the routing key. If the contents accept a click action, this
        # would result in clicking on the link instead of clearing the flash message.
        self.presentationInterrupt(killFlash=False)
        braille.process_routing_key(event)
        return True

    def process_braille_cut_begin(self, event=None):
        """Clears the selection and moves the caret offset in the currently
        active text area.
        """

        obj, offset = self.getBrailleCaretContext(event)
        if offset < 0:
            return True

        self.presentationInterrupt()
        AXText.clear_all_selected_text(obj)
        self.utilities.setCaretOffset(obj, offset)
        return True

    def process_braille_cut_line(self, event=None):
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        obj, offset = self.getBrailleCaretContext(event)
        if offset < 0:
            return True

        self.presentationInterrupt()
        startOffset = AXText.get_selection_start_offset(obj)
        endOffset = AXText.get_selection_end_offset(obj)
        if (startOffset < 0 or endOffset < 0):
            caretOffset = AXText.get_caret_offset(obj)
            startOffset = min(offset, caretOffset)
            endOffset = max(offset, caretOffset)

        AXText.set_selected_text(obj, startOffset, endOffset)
        text = AXText.get_selected_text(obj)[0]
        self.get_clipboard_presenter().set_text(text)
        return True

    def route_pointer_to_item(self, event=None):
        """Moves the mouse pointer to the current item."""

        self.lastMouseRoutingTime = time.time()
        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().route_pointer_to_object(self, event)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_event_synthesizer().route_to_character(focus) \
           or self.get_event_synthesizer().route_to_object(focus):
            self.presentMessage(messages.MOUSE_MOVED_SUCCESS)
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.presentMessage(full, brief)
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
        self.presentMessage(full, brief)
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
        self.presentMessage(full, brief)
        return False

    def say_all(self, _event, obj=None, offset=None):
        """Speaks the contents of obj."""

        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        tokens = ["DEFAULT: SayAll requested starting from", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not obj or AXObject.is_dead(obj):
            self.presentMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        speech.say_all(self.textLines(obj, offset), self.__sayAllProgressCallback)
        return True

    def cycle_settings_profile(self, _event=None):
        """Cycle through the user's existing settings profiles."""

        profiles = settings_manager.get_manager().available_profiles()
        if not (profiles and profiles[0]):
            self.presentMessage(messages.PROFILE_NOT_FOUND)
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

        self.presentMessage(messages.PROFILE_CHANGED % name, name)
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

        if self.run_find_command:
            self.run_find_command = False
            self.get_flat_review_finder().find(self)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if AXUtilities.is_presentable_active_descendant_change(event):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if AXUtilities.is_presentable_checked_change(event):
            self.presentObject(event.source, alreadyFocused=True, interrupt=True)

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

    def on_children_removed(self, event):
        """Callback for object:children-changed:remove accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)
        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus != event.source:
            if not AXUtilities.is_focused(event.source):
                msg = "DEFAULT: Change is from unfocused source that is not the locus of focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return
            # TODO - JD: See if this can be removed. If it's still needed document why.
            focus_manager.get_manager().set_locus_of_focus(event, event.source, False)

        obj, offset = self.point_of_reference.get("lastCursorPosition", (None, -1))
        if offset == event.detail1 and obj == event.source:
            msg = "DEFAULT: Event is for last saved cursor position"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        offset = AXText.get_caret_offset(event.source)
        self._saveLastCursorPosition(event.source, offset)

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

        string, _start, _end = AXText.get_cached_selected_text(obj)
        if string and self.utilities.handleTextSelectionChange(obj):
            msg = "DEFAULT: Event handled as text selection change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = "DEFAULT: Presenting text at new caret position"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._presentTextAtNewCaretPosition(event, reason=reason)

    def on_description_changed(self, event):
        """Callback for object:property-change:accessible-description events."""

        if AXUtilities.is_presentable_description_change(event):
            self.presentMessage(event.any_data)

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

        self.presentMessage(messages.PAGE_NUMBER % event.detail1)

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "expanded-changed event.")
        if not AXUtilities.is_presentable_expanded_change(event):
            return

        self.presentObject(event.source, alreadyFocused=True, interrupt=True)
        details = self.utilities.detailsContentForObject(event.source)
        for detail in details:
            self.speakMessage(detail, interrupt=False)

    def on_indeterminate_changed(self, event):
        """Callback for object:state-changed:indeterminate accessibility events."""

        if AXUtilities.is_presentable_indeterminate_change(event):
            self.presentObject(event.source, alreadyFocused=True, interrupt=True)

    def on_mouse_button(self, event):
        """Callback for mouse:button events."""

        input_event_manager.get_manager().process_mouse_button_event(event)

    def on_announcement(self, event):
        """Callback for object:announcement events."""

        if isinstance(event.any_data, str):
            self.presentMessage(event.any_data)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if not AXUtilities.is_presentable_name_change(event):
            return

        manager = focus_manager.get_manager()
        if event.source == manager.get_locus_of_focus():
            # Force the update so that braille is refreshed.
            manager.set_locus_of_focus(event, event.source, True, True)
            return

        self.presentMessage(event.any_data)

    def on_object_attributes_changed(self, event):
        """Callback for object:attributes-changed accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "object-attributes-changed event.")

    def on_pressed_changed(self, event):
        """Callback for object:state-changed:pressed accessibility events."""

        if AXUtilities.is_presentable_pressed_change(event):
            self.presentObject(event.source, alreadyFocused=True, interrupt=True)

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
            self.speakMessage(messages.TEXT_SELECTED, interrupt=False)
        else:
            self.speakMessage(messages.TEXT_UNSELECTED, interrupt=False)

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
                self._save_focused_object_info(focus)
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

            self.speakMessage(self.speech_generator.get_localized_role_name(obj))
            msg = self.utilities.getNotificationContent(obj)
            self.presentMessage(msg, resetStyles=False)
            self.get_notification_presenter().save_notification(msg)
            return

        if AXUtilities.is_tool_tip(obj):
            was_f1 = input_event_manager.get_manager().last_event_was_f1()
            if not was_f1 and not settings_manager.get_manager().get_setting('presentToolTips'):
                return
            if event.detail1:
                self.presentObject(obj, interrupt=True)
                return

            focus = focus_manager.get_manager().get_locus_of_focus()
            if focus and was_f1:
                obj = focus
                self.presentObject(obj, priorObj=event.source, interrupt=True)
                return

    def on_text_attributes_changed(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        if not (AXUtilities.is_editable(event.source) or AXUtilities.is_terminal(event.source)):
            msg = "DEFAULT: Change is from not editable or terminal source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus != event.source and not AXUtilities.is_focused(event.source):
            msg = "DEFAULT: Change is from unfocused source that is not the locus of focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self.speakMisspelledIndicator(event.source)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)

        if not (AXUtilities.is_editable(event.source) or AXUtilities.is_terminal(event.source)):
            msg = "DEFAULT: Change is from not editable or terminal source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus != event.source and not AXUtilities.is_focused(event.source):
            msg = "DEFAULT: Change is from unfocused source that is not the locus of focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self.utilities.handleUndoTextEvent(event)
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_DELETION:
            msg = "DEFAULT: Deletion is believed to be due to deleting selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.presentMessage(messages.SELECTION_DELETED)
            AXText.update_cached_selected_text(event.source)
            return

        text = self.utilities.deletedText(event)
        if reason == TextEventReason.DELETE:
            msg = "DEFAULT: Deletion is believed to be due to Delete command"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            text = AXText.get_character_at_offset(event.source)[0]
        elif reason == TextEventReason.BACKSPACE:
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
            self.speakMessage(text, voice)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)

        if not (AXUtilities.is_editable(event.source) or AXUtilities.is_terminal(event.source)):
            msg = "DEFAULT: Change is from not editable or terminal source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus != event.source and not AXUtilities.is_focused(event.source):
            msg = "DEFAULT: Change is from unfocused source that is not the locus of focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self.utilities.handleUndoTextEvent(event)
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_RESTORATION:
            msg = "DEFAULT: Insertion is believed to be due to restoring selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.presentMessage(messages.SELECTION_RESTORED)
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
                self.speakMessage(text, voice)

        if len(text) != 1 \
           or reason not in [TextEventReason.TYPING, TextEventReason.TYPING_ECHOABLE]:
            return

        if settings_manager.get_manager().get_setting('enableEchoBySentence') \
           and self.echoPreviousSentence(event.source):
            return

        if settings_manager.get_manager().get_setting('enableEchoByWord'):
            self.echoPreviousWord(event.source)

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
            self.sayLine(event.source)
            AXText.update_cached_selected_text(event.source)
            return
        if reason == TextEventReason.SEARCH_UNPRESENTABLE:
            msg = "DEFAULT: Ignoring event believed to be unpresentable search results change"
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

        self.presentMessage(messages.TABLE_REORDERED_COLUMNS)

    def on_row_reordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "row-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return

        if event.source != AXTable.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return

        self.presentMessage(messages.TABLE_REORDERED_ROWS)

    def on_value_changed(self, event):
        """Callback for object:property-change:accessible-value accessibility events."""

        if not AXValue.did_value_change(event.source):
            return

        isProgressBarUpdate, msg = self.utilities.isProgressBarUpdate(event.source)
        tokens = ["DEFAULT: Is progress bar update:", isProgressBarUpdate, ",", msg]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not isProgressBarUpdate \
           and event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "DEFAULT: Source != locusOfFocus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if AXUtilities.is_spin_button(event.source):
            self._save_focused_object_info(event.source)

        self.update_braille(event.source, isProgressBarUpdate=isProgressBarUpdate)
        speech.speak(self.speech_generator.generate_speech(
            event.source, alreadyFocused=True, isProgressBarUpdate=isProgressBarUpdate))
        self.__play(self.sound_generator.generate_sound(
            event.source, alreadyFocused=True, isProgressBarUpdate=isProgressBarUpdate))

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

    def _presentTextAtNewCaretPosition(self, event, otherObj=None, reason=TextEventReason.UNKNOWN):
        """Presents text at the new position, based on heuristics. Returns True if handled."""

        obj = otherObj or event.source
        self.updateBrailleForNewCaretPosition(obj)
        if reason == TextEventReason.SAY_ALL:
            msg = "DEFAULT: Not presenting text because SayAll is active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        if reason == TextEventReason.NAVIGATION_BY_LINE:
            self.sayLine(obj)
            return True
        if reason == TextEventReason.NAVIGATION_BY_WORD:
            self.sayWord(obj)
            return True
        if reason == TextEventReason.NAVIGATION_BY_CHARACTER:
            self.sayCharacter(obj)
            return True
        if reason == TextEventReason.NAVIGATION_BY_PAGE:
            self.sayLine(obj)
            return True
        if reason == TextEventReason.NAVIGATION_TO_LINE_BOUNDARY:
            self.sayCharacter(obj)
            return True
        if reason == TextEventReason.NAVIGATION_TO_FILE_BOUNDARY:
            self.sayLine(obj)
            return True
        if reason == TextEventReason.MOUSE_PRIMARY_BUTTON:
            text, _start, _end = AXText.get_cached_selected_text(event.source)
            if not text:
                self.sayLine(obj)
                return True
        return False

    def _rewindSayAll(self, context, minCharCount=10):
        if not settings_manager.get_manager().get_setting('rewindAndFastForwardInSayAll'):
            return False

        index = self._sayAllContexts.index(context)
        self._sayAllContexts = self._sayAllContexts[0:index]
        while self._sayAllContexts:
            context = self._sayAllContexts.pop()
            if context.endOffset - context.startOffset > minCharCount:
                break

        # TODO - JD: Why do we only update focus if text is supported?
        if AXText.set_caret_offset(context.obj, context.startOffset):
            focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)

        self.say_all(None, context.obj, context.startOffset)
        return True

    def _fastForwardSayAll(self, context):
        if not settings_manager.get_manager().get_setting('rewindAndFastForwardInSayAll'):
            return False

        # TODO - JD: Why do we only update focus if text is supported?
        if AXText.set_caret_offset(context.obj, context.endOffset):
            focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)

        self.say_all(None, context.obj, context.endOffset)
        return True

    def __sayAllProgressCallback(self, context, progressType):
        # TODO - JD: Can we scroll the content into view instead of setting
        # the caret?

        # TODO - JD: This condition shouldn't happen. Make sure of that.
        if AXText.character_at_offset_is_eoc(context.obj, context.currentOffset):
            return

        if progressType == speechserver.SayAllContext.PROGRESS:
            focus_manager.get_manager().emit_region_changed(
                context.obj, context.currentOffset, context.currentEndOffset,
                focus_manager.SAY_ALL)
            return

        if progressType == speechserver.SayAllContext.INTERRUPTED:
            manager = input_event_manager.get_manager()
            if manager.last_event_was_keyboard():
                self._sayAllIsInterrupted = True
                if manager.last_event_was_down() and self._fastForwardSayAll(context):
                    return
                if manager.last_event_was_up() and self._rewindSayAll(context):
                    return

            self._inSayAll = False
            self._sayAllContexts = []
            focus_manager.get_manager().emit_region_changed(context.obj, context.currentOffset)
            AXText.set_caret_offset(context.obj, context.currentOffset)
        elif progressType == speechserver.SayAllContext.COMPLETED:
            focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)
            focus_manager.get_manager().emit_region_changed(
                context.obj, context.currentOffset, mode=focus_manager.SAY_ALL)
            AXText.set_caret_offset(context.obj, context.currentOffset)

        # TODO - JD: This was in place for bgo#489504. But setting the caret should cause
        # the selection to be cleared by the implementation. Find out where that's not the
        # case and see if they'll fix it.
        AXText.clear_all_selected_text(context.obj)

    def inSayAll(self, treatInterruptedAsIn=True):
        if self._inSayAll:
            msg = "DEFAULT: In SayAll"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self._sayAllIsInterrupted:
            msg = "DEFAULT: SayAll is interrupted"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return treatInterruptedAsIn

        msg = "DEFAULT: Not in SayAll"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def echoPreviousSentence(self, obj):
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
        self.speakMessage(sentence, voice, obj=obj)
        return True

    def echoPreviousWord(self, obj):
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
        self.speakMessage(word, voice, obj=obj)
        return True

    def sayCharacter(self, obj):
        """Speak the character at the caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        offset = AXText.get_caret_offset(obj)

        # If we have selected text and the last event was a move to the
        # right, then speak the character to the left of where the text
        # caret is (i.e. the selected character).
        if input_event_manager.get_manager().last_event_was_forward_caret_selection():
            offset -= 1

        character, startOffset, endOffset = AXText.get_character_at_offset(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj, startOffset, endOffset, focus_manager.CARET_TRACKING)

        if not character or character == '\r':
            character = "\n"

        speakBlankLines = settings_manager.get_manager().get_setting('speakBlankLines')
        if character == "\n":
            lineString = AXText.get_line_at_offset(obj, max(0, offset))[0]
            if not lineString or lineString == "\n":
                # This is a blank line. Announce it if the user requested
                # that blank lines be spoken.
                if speakBlankLines:
                    self.speakMessage(messages.BLANK, interrupt=False)
                return

        if character in ["\n", "\r\n"]:
            # This is a blank line. Announce it if the user requested
            # that blank lines be spoken.
            if speakBlankLines:
                self.speakMessage(messages.BLANK, interrupt=False)
            return
        else:
            self.speakMisspelledIndicator(obj, offset)
            self.speak_character(character)

        self.point_of_reference["lastTextUnitSpoken"] = "char"

    def sayLine(self, obj, offset=None):
        """Speaks the line of an AccessibleText object that contains the
        caret, unless the line is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        line, startOffset = AXText.get_line_at_offset(obj, offset)[0:2]
        if line and line != "\n":
            manager = speech_and_verbosity_manager.get_manager()
            indentation_description = manager.get_indentation_description(line)
            if indentation_description:
                self.speakMessage(indentation_description)

            endOffset = startOffset + len(line)
            focus_manager.get_manager().emit_region_changed(
                obj, startOffset, endOffset, focus_manager.CARET_TRACKING)

            utterance = []
            split = self.utilities.splitSubstringByLanguage(obj, startOffset, endOffset)
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
            self.speakMessage(messages.BLANK, interrupt=False)

        self.point_of_reference["lastTextUnitSpoken"] = "line"

    def sayPhrase(self, obj, startOffset, endOffset):
        """Speaks the text of an Accessible object between the start and
        end offsets, unless the phrase is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - startOffset: the start text offset.
        - endOffset: the end text offset.
        """

        phrase = self.utilities.expandEOCs(obj, startOffset, endOffset)
        if not phrase:
            return

        if len(phrase) > 1 or phrase.isalnum():
            manager = speech_and_verbosity_manager.get_manager()
            result = manager.get_indentation_description(phrase)
            if result:
                self.speakMessage(result)

            focus_manager.get_manager().emit_region_changed(
                obj, startOffset, endOffset, focus_manager.CARET_TRACKING)

            voice = self.speech_generator.voice(obj=obj, string=phrase)
            phrase = manager.adjust_for_presentation(obj, phrase)
            utterance = [phrase]
            utterance.extend(voice)
            speech.speak(utterance)
        else:
            self.speak_character(phrase)

        self.point_of_reference["lastTextUnitSpoken"] = "phrase"

    def sayWord(self, obj):
        """Speaks the word at the caret, taking into account the previous caret position."""


        offset = AXText.get_caret_offset(obj)
        word, startOffset, endOffset = \
            self.utilities.getWordAtOffsetAdjustedForNavigation(obj, offset)

        # Announce when we cross a hard line boundary.
        if "\n" in word:
            if settings_manager.get_manager().get_setting('enableSpeechIndentation'):
                self.speak_character("\n")
            if word.startswith("\n"):
                startOffset += 1
            elif word.endswith("\n"):
                endOffset -= 1
            word = AXText.get_substring(obj, startOffset, endOffset)

        # sayPhrase is useful because it handles punctuation verbalization, but we don't want
        # to trigger its whitespace presentation.
        matches = list(re.finditer(r"\S+", word))
        if matches:
            startOffset += matches[0].start()
            endOffset -= len(word) - matches[-1].end()
            word = AXText.get_substring(obj, startOffset, endOffset)

        text = word.replace("\n", "\\n")
        msg = (
            f"DEFAULT: Final word at offset {offset} is '{text}' "
            f"({startOffset}-{endOffset})"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.speakMisspelledIndicator(obj, startOffset)
        self.sayPhrase(obj, startOffset, endOffset)
        self.point_of_reference["lastTextUnitSpoken"] = "word"

    def presentObject(self, obj, **args):
        interrupt = args.get("interrupt", False)
        tokens = ["DEFAULT: Presenting object", obj, ". Interrupt:", interrupt]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not args.get("speechonly", False):
            self.update_braille(obj, **args)
        utterances = self.speech_generator.generate_speech(obj, **args)
        speech.speak(utterances, interrupt=interrupt)

    def getFlatReviewContext(self):
        """Returns the flat review context, creating one if necessary."""

        return self.get_flat_review_presenter().get_or_create_context(self)

    def updateBrailleReview(self, targetCursorCell=0):
        """Obtains the braille regions for the current flat review line
        and displays them on the braille display.  If the targetCursorCell
        is non-0, then an attempt will be made to position the review cursor
        at that cell.  Otherwise, we will pan in display-sized increments
        to show the review cursor."""

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.print_message(debug.LEVEL_INFO, "BRAILLE: update review disabled", True)
            return

        [regions, regionWithFocus] = self.get_flat_review_presenter().get_braille_regions(self)
        if not regions:
            regions = []
            regionWithFocus = None

        line = self.getNewBrailleLine()
        self.addBrailleRegionsToLine(regions, line)
        braille.setLines([line])
        self.setBrailleFocus(regionWithFocus, False)
        if regionWithFocus and not targetCursorCell:
            offset = regionWithFocus.brailleOffset + regionWithFocus.cursorOffset
            tokens = ["DEFAULT: Update to", offset, "in", regionWithFocus]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.panBrailleToOffset(offset)

        if self.justEnteredFlatReviewMode:
            self.refreshBraille(True, self.targetCursorCell)
            self.justEnteredFlatReviewMode = False
        else:
            self.refreshBraille(True, targetCursorCell)

    def _setFlatReviewContextToBeginningOfBrailleDisplay(self):
        """Sets the character of interest to be the first character showing
        at the beginning of the braille display."""

        # The first character on the flat review line has to be in object with text.
        def isTextOrComponent(x):
            return isinstance(x, (braille.ReviewText, braille.ReviewComponent))

        regions = self.get_flat_review_presenter().get_braille_regions(self)[0]
        regions = list(filter(isTextOrComponent, regions))
        tokens = ["DEFAULT: Text/Component regions on line:"]
        for region in regions:
            tokens.extend(["\n", region])
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: The current code was stopping on the first region which met the
        # following condition. Is that definitely the right thing to do? Assume so for now.
        # Also: Should the default script be accessing things like the viewport directly??
        def isMatch(x):
            return x is not None and x.brailleOffset + len(x.string) > braille.viewport[0]

        regions = list(filter(isMatch, regions))
        if not regions:
            msg = "DEFAULT: Could not find review region to move to start of display"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        tokens = ["DEFAULT: Candidates for start of display:"]
        for region in regions:
            tokens.extend(["\n", region])
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)


        # TODO - JD: Again, for now we're preserving the original behavior of choosing the first.
        region = regions[0]
        position = max(region.brailleOffset, braille.viewport[0])
        if region.contracted:
            offset = region.inPos[position - region.brailleOffset]
        else:
            offset = position - region.brailleOffset
        if isinstance(region.zone, flat_review.TextZone):
            offset += region.zone.startOffset
        msg = f"DEFAULT: Offset for region: {offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        [word, charOffset] = region.zone.getWordAtOffset(offset)
        if word:
            tokens = ["DEFAULT: Setting start of display to", word, ", ", charOffset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            context = self.getFlatReviewContext()
            context.setCurrent(
                word.zone.line.index,
                word.zone.index,
                word.index,
                charOffset)
        else:
            tokens = ["DEFAULT: Setting start of display to", region.zone]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            context = self.getFlatReviewContext()
            context.setCurrent(
                region.zone.line.index,
                region.zone.index,
                0, # word index
                0) # character index

    def textLines(self, obj, offset=None):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        self._sayAllIsInterrupted = False
        self._inSayAll = True
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

        self._inSayAll = False
        self._sayAllContexts = []

        msg = "DEFAULT: textLines complete. Verifying SayAll status"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.inSayAll()

    def phoneticSpellCurrentItem(self, itemString):
        """Phonetically spell the current flat review word or line.

        Arguments:
        - itemString: the string to phonetically spell.
        """

        for (charIndex, character) in enumerate(itemString):
            voice = self.speech_generator.voice(string=character)
            phoneticString = phonnames.getPhoneticName(character.lower())
            self.speakMessage(phoneticString, voice)

    def _saveLastCursorPosition(self, obj, caretOffset):
        """Save away the current text cursor position for next time.

        Arguments:
        - obj: the current accessible
        - caretOffset: the cursor position within this object
        """

        prevObj, prevOffset = self.point_of_reference.get("lastCursorPosition", (None, -1))
        self.point_of_reference["penultimateCursorPosition"] = prevObj, prevOffset
        self.point_of_reference["lastCursorPosition"] = obj, caretOffset

    def systemBeep(self):
        """Rings the system bell. This is really a hack. Ideally, we want
        a method that will present an earcon (any sound designated for the
        purpose of representing an error, event etc)
        """

        print("\a")

    def speakMisspelledIndicator(self, obj, offset=None):
        # TODO - JD: Remove this and have callers use the speech-adjustment logic.
        manager = speech_and_verbosity_manager.get_manager()
        error = manager.get_error_description(obj, offset)
        if error:
            self.speakMessage(error)

    ############################################################################
    #                                                                          #
    # Presentation methods                                                     #
    # (scripts should not call methods in braille.py or speech.py directly)    #
    #                                                                          #
    ############################################################################

    def presentationInterrupt(self, killFlash=True):
        """Convenience method to interrupt presentation of whatever is being
        presented at the moment."""

        msg = "DEFAULT: Interrupting presentation"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        speech_and_verbosity_manager.get_manager().interrupt_speech()
        if killFlash:
            braille.killFlash()

    def presentKeyboardEvent(self, event):
        """Convenience method to present the KeyboardEvent event. Returns True
        if we fully present the event; False otherwise."""

        if not event.is_pressed_key():
            self._sayAllIsInterrupted = False
            self.utilities.clearCachedCommandState()

        if not event.should_echo() or event.is_orca_modified():
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_dialog_or_window(focus):
            focusedObject = focus_manager.get_manager().find_focused_object()
            if focusedObject:
                focus_manager.get_manager().set_locus_of_focus(None, focusedObject, False)
                AXObject.get_role(focusedObject)

        if AXUtilities.is_password_text(focus) and not event.is_locking_key():
            return False

        if not event.is_pressed_key():
            return False

        braille.displayKeyEvent(event)
        orcaModifierPressed = event.is_orca_modifier() and event.is_pressed_key()
        if event.is_character_echoable() and not orcaModifierPressed:
            return False

        msg = "DEFAULT: Presenting keyboard event"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.speak_key_event(event)
        return True

    def presentMessage(self, fullMessage, briefMessage=None, voice=None, resetStyles=True,
                       force=False):
        """Convenience method to speak a message and 'flash' it in braille.

        Arguments:
        - fullMessage: This can be a string or a list. This will be presented
          as the message for users whose flash or message verbosity level is
          verbose.
        - briefMessage: This can be a string or a list. This will be presented
          as the message for users whose flash or message verbosity level is
          brief. Note that providing no briefMessage will result in the full
          message being used for either. Callers wishing to present nothing as
          the briefMessage should set briefMessage to an empty string.
        - voice: The voice to use when speaking this message. By default, the
          "system" voice will be used.
        """

        if not fullMessage:
            return

        if briefMessage is None:
            briefMessage = fullMessage

        if settings_manager.get_manager().get_setting('enableSpeech'):
            if not settings_manager.get_manager().get_setting('messagesAreDetailed'):
                message = briefMessage
            else:
                message = fullMessage
            if message:
                self.speakMessage(message, voice=voice, resetStyles=resetStyles, force=force)

        if (settings_manager.get_manager().get_setting('enableBraille') \
             or settings_manager.get_manager().get_setting('enableBrailleMonitor')) \
           and settings_manager.get_manager().get_setting('enableFlashMessages'):
            if not settings_manager.get_manager().get_setting('flashIsDetailed'):
                message = briefMessage
            else:
                message = fullMessage
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

    def idleMessage(self):
        """Convenience method to tell speech and braille engines to hand off
        control to other screen readers."""

        braille.disableBraille()

    @staticmethod
    def __play(sounds, interrupt=True):
        if not sounds:
            return

        if not isinstance(sounds, list):
            sounds = [sounds]

        _player = sound.getPlayer()
        _player.play(sounds[0], interrupt)
        for i in range(1, len(sounds)):
            _player.play(sounds[i], interrupt=False)

    @staticmethod
    def addBrailleRegionToLine(region, line):
        """Adds the braille region to the line.

        Arguments:
        - region: a braille.Region (e.g. what is returned by the braille
          generator's generate_braille() method.
        - line: a braille.Line
        """

        line.addRegion(region)

    @staticmethod
    def addBrailleRegionsToLine(regions, line):
        """Adds the braille region to the line.

        Arguments:
        - regions: a series of braille.Region instances (a single instance
          being what is returned by the braille generator's generate_braille()
          method.
        - line: a braille.Line
        """

        line.addRegions(regions)

    @staticmethod
    def clearBraille():
        """Clears the logical structure, but keeps the Braille display as is
        (until a refresh operation)."""

        braille.clear()

    @staticmethod
    def displayBrailleMessage(message, cursor=-1, flashTime=0):
        """Displays a single line, setting the cursor to the given position,
        ensuring that the cursor is in view.

        Arguments:
        - message: the string to display
        - cursor: the 0-based cursor position, where -1 (default) means no
          cursor
        - flashTime:  if non-0, the number of milliseconds to display the
          regions before reverting back to what was there before. A 0 means
          to not do any flashing.  A negative number means to display the
          message until some other message comes along or the user presses
          a cursor routing key.
        """

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.print_message(debug.LEVEL_INFO, "BRAILLE: display message disabled", True)
            return

        braille.displayMessage(message, cursor, flashTime)

    @staticmethod
    def getBrailleCaretContext(event):
        """Gets the accesible and caret offset associated with the given
        event.  The event should have a BrlAPI event that contains an
        argument value that corresponds to a cell on the display.

        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
          the dictionary form of the expanded BrlAPI event.
        """

        return braille.getCaretContext(event)

    @staticmethod
    def getBrailleCursorCell():
        """Returns the value of position of the braille cell which has the
        cursor. A value of 0 means no cell has the cursor."""

        return braille.cursorCell

    @staticmethod
    def getNewBrailleLine(clearBraille=False, addLine=False):
        """Creates a new braille Line.

        Arguments:
        - clearBraille: Whether the display should be cleared.
        - addLine: Whether the line should be added to the logical display
          for painting.

        Returns the new Line.
        """

        if clearBraille:
            braille.clear()
        line = braille.Line()
        if addLine:
            braille.addLine(line)

        return line

    @staticmethod
    def isBrailleBeginningShowing():
        """If True, the beginning of the line is showing on the braille
        display."""

        return braille.beginningIsShowing

    @staticmethod
    def isBrailleEndShowing():
        """If True, the end of the line is showing on the braille display."""

        return braille.endIsShowing

    @staticmethod
    def panBrailleInDirection(pan_amount=0, panToLeft=True):
        """Pans the display to the left, limiting the pan to the beginning
        of the line being displayed.

        Arguments:
        - pan_amount: the amount to pan.  A value of 0 means the entire
          width of the physical display.
        - panToLeft: if True, pan to the left; otherwise to the right

        Returns True if a pan actually happened.
        """

        if panToLeft:
            return braille.panLeft(pan_amount)
        else:
            return braille.panRight(pan_amount)

    @staticmethod
    def panBrailleToOffset(offset):
        """Automatically pan left or right to make sure the current offset
        is showing."""

        braille.panToOffset(offset)

    def updateBrailleForNewCaretPosition(self, obj):
        """Try to reposition the cursor without having to do a full update."""

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.print_message(debug.LEVEL_INFO, "BRAILLE: update caret disabled", True)
            return

        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) and region.accessible == obj:
                if region.repositionCursor():
                    self.refreshBraille(True)
                    brailleNeedsRepainting = False
                break

        if brailleNeedsRepainting:
            self.update_braille(obj)

    @staticmethod
    def refreshBraille(panToCursor=True, targetCursorCell=0, getLinkMask=True,
                       stopFlash=True):
        """This is the method scripts should use to refresh braille rather
        than calling self.refreshBraille() directly. The intent is to centralize
        such calls into as few places as possible so that we can easily and
        safely not perform braille-related functions for users who do not
        have braille and/or the braille monitor enabled.

        Arguments:

        - panToCursor: if True, will adjust the viewport so the cursor is
          showing.
        - targetCursorCell: Only effective if panToCursor is True.
          0 means automatically place the cursor somewhere on the display so
          as to minimize movement but show as much of the line as possible.
          A positive value is a 1-based target cell from the left side of
          the display and a negative value is a 1-based target cell from the
          right side of the display.
        - getLinkMask: Whether or not we should take the time to get the
          attributeMask for links. Reasons we might not want to include
          knowing that we will fail and/or it taking an unreasonable
          amount of time (AKA Gecko).
        - stopFlash: if True, kill any flashed message that may be showing.
        """

        braille.refresh(panToCursor, targetCursorCell, getLinkMask, stopFlash)

    @staticmethod
    def setBrailleFocus(region, panToFocus=True, getLinkMask=True):
        """Specififes the region with focus.  This region will be positioned
        at the home position if panToFocus is True.

        Arguments:
        - region: the given region, which much be in a line that has been
          added to the logical display
        - panToFocus: whether or not to position the region at the home
          position
        - getLinkMask: Whether or not we should take the time to get the
          attributeMask for links. Reasons we might not want to include
          knowing that we will fail and/or it taking an unreasonable
          amount of time (AKA Gecko).
        """

        braille.setFocus(region, panToFocus, getLinkMask)

    @staticmethod
    def _set_contracted_braille(event):
        """Turns contracted braille on or off based upon the event.

        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
          the dictionary form of the expanded BrlAPI event.
        """

        braille.set_contracted_braille(event)

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
        """Method to speak a single character. Scripts should use this
        method rather than calling speech.speakCharacter directly."""

        voice = self.speech_generator.voice(string=character)
        speech.speak_character(character, voice)

    def speakMessage(
        self, text, voice=None, interrupt=True, resetStyles=True, force=False, obj=None):
        """Method to speak a single string. Scripts should use this
        method rather than calling speech.speak directly.

        - string: The string to be spoken.
        - voice: The voice to use. By default, the "system" voice will
          be used.
        - interrupt: If True, any current speech should be interrupted
          prior to speaking the new text.
        """

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
        if voice == systemVoice and resetStyles:
            capStyle = settings_manager.get_manager().get_setting('capitalizationStyle')
            manager.set_setting('capitalizationStyle', settings.CAPITALIZATION_STYLE_NONE)
            self.get_speech_and_verbosity_manager().update_capitalization_style()

            punctStyle = manager.get_setting('verbalizePunctuationStyle')
            manager.set_setting('verbalizePunctuationStyle', settings.PUNCTUATION_STYLE_NONE)
            self.get_speech_and_verbosity_manager().update_punctuation_level()

        text = speech_and_verbosity_manager.get_manager().adjust_for_presentation(obj, text)
        speech.speak(text, voice, interrupt)

        if voice == systemVoice and resetStyles:
            manager.set_setting('capitalizationStyle', capStyle)
            self.get_speech_and_verbosity_manager().update_capitalization_style()

            manager.set_setting('verbalizePunctuationStyle', punctStyle)
            self.get_speech_and_verbosity_manager().update_punctuation_level()
