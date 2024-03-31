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
from orca import speechserver

from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_value import AXValue

class Script(script.Script):

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'
    NO_BREAK_SPACE_CHARACTER  = '\u00a0'

    # generator_cache
    #
    DISPLAYED_LABEL = 'displayedLabel'
    DISPLAYED_TEXT = 'displayedText'
    KEY_BINDING = 'keyBinding'
    NESTING_LEVEL = 'nestingLevel'
    NODE_LEVEL = 'nodeLevel'
    REAL_ACTIVE_DESCENDANT = 'realActiveDescendant'

    def __init__(self, app):
        super().__init__(app)

        self.targetCursorCell = None

        self.justEnteredFlatReviewMode = False

        self.digits = '0123456789'
        self.whitespace = ' \t\n\r\v\f'

        # A dictionary of non-standardly-named text attributes and their
        # Atk equivalents.
        #
        self.attributeNamesDict = {}

        # Keep track of the last time we issued a mouse routing command
        # so that we can guess if a change resulted from our moving the
        # pointer.
        #
        self.lastMouseRoutingTime = None

        # The last location of the mouse, which we might want if routing
        # the pointer elsewhere.
        #
        self.oldMouseCoordinates = [0, 0]

        self._lastWordCheckedForSpelling = ""

        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._sayAllContexts = []
        self.grab_ids = []

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        self.input_event_handlers["routePointerToItemHandler"] = \
            input_event.InputEventHandler(
                Script.routePointerToItem,
                cmdnames.ROUTE_POINTER_TO_ITEM)

        self.input_event_handlers["leftClickReviewItemHandler"] = \
            input_event.InputEventHandler(
                Script.leftClickReviewItem,
                cmdnames.LEFT_CLICK_REVIEW_ITEM)

        self.input_event_handlers["rightClickReviewItemHandler"] = \
             input_event.InputEventHandler(
                Script.rightClickReviewItem,
                cmdnames.RIGHT_CLICK_REVIEW_ITEM)

        self.input_event_handlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.say_all,
                cmdnames.SAY_ALL)

        self.input_event_handlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["goBrailleHomeHandler"] = \
            input_event.InputEventHandler(
                Script.goBrailleHome,
                cmdnames.GO_BRAILLE_HOME)

        self.input_event_handlers["contractedBrailleHandler"] = \
            input_event.InputEventHandler(
                Script.setContractedBraille,
                cmdnames.SET_CONTRACTED_BRAILLE)

        self.input_event_handlers["processRoutingKeyHandler"] = \
            input_event.InputEventHandler(
                Script.processRoutingKey,
                cmdnames.PROCESS_ROUTING_KEY)

        self.input_event_handlers["processBrailleCutBeginHandler"] = \
            input_event.InputEventHandler(
                Script.processBrailleCutBegin,
                cmdnames.PROCESS_BRAILLE_CUT_BEGIN)

        self.input_event_handlers["processBrailleCutLineHandler"] = \
            input_event.InputEventHandler(
                Script.processBrailleCutLine,
                cmdnames.PROCESS_BRAILLE_CUT_LINE)

        self.input_event_handlers["shutdownHandler"] = \
            input_event.InputEventHandler(
                Script.quitOrca,
                cmdnames.QUIT_ORCA)

        self.input_event_handlers["preferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                Script.showPreferencesGUI,
                cmdnames.SHOW_PREFERENCES_GUI)

        self.input_event_handlers["appPreferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                Script.showAppPreferencesGUI,
                cmdnames.SHOW_APP_PREFERENCES_GUI)

        self.input_event_handlers["cycleSettingsProfileHandler"] = \
            input_event.InputEventHandler(
                Script.cycleSettingsProfile,
                cmdnames.CYCLE_SETTINGS_PROFILE)

        self.input_event_handlers["cycleDebugLevelHandler"] = \
            input_event.InputEventHandler(
                Script.cycleDebugLevel,
                cmdnames.CYCLE_DEBUG_LEVEL)

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

    def get_listeners(self):
        """Sets up the AT-SPI event listeners for this script."""

        listeners = script.Script.get_listeners(self)
        listeners["document:attributes-changed"] = self.on_document_attributes_changed
        listeners["document:reload"] = self.on_document_reload
        listeners["document:load-complete"] = self.on_document_load_complete
        listeners["document:load-stopped"] = self.on_document_load_stopped
        listeners["document:page-changed"] = self.on_document_page_changed
        listeners["focus:"] = self.on_focus
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
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("sayAllHandler"),
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Divide",
                keybindings.defaultModifierMask,
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
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("sayAllHandler"),
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "9",
                keybindings.defaultModifierMask,
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

        return keyBindings

    def get_key_bindings(self, enabled_only=True):
        """Returns the key bindings for this script."""

        tokens = ["DEFAULT: Getting keybindings for", self]
        debug.printTokens(debug.LEVEL_INFO, tokens, True, True)

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
            debug.printTokens(debug.LEVEL_WARNING, tokens, True)

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
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("cycleSettingsProfileHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("cycleDebugLevelHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("panBrailleLeftHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("panBrailleRightHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("shutdownHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("preferencesSettingsHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                keybindings.defaultModifierMask,
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
        debug.printMessage(debug.LEVEL_INFO, msg, True)

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
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
        except Exception as error:
            tokens = ["DEFAULT: Exception getting braille bindings in", self, ":", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        reviewBindings = self.get_flat_review_presenter().get_braille_bindings()
        braille_bindings.update(reviewBindings)

        msg = 'DEFAULT: Finished getting braille bindings.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

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

        self.removeKeyGrabs("script deactivation")

    def addKeyGrabs(self, reason=""):
        """ Sets up the key grabs currently needed by this script. """

        msg = "DEFAULT: Setting up key bindings"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.key_bindings = self.get_key_bindings()
        self.key_bindings.addKeyGrabs(reason)
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()

    def removeKeyGrabs(self, reason=""):
        """ Removes this script's AT-SPI key grabs. """

        orca_modifier_manager.get_manager().remove_grabs_for_orca_modifiers()
        self.key_bindings.removeKeyGrabs(reason)

        msg = "DEFAULT: Clearing key bindings"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.key_bindings = keybindings.KeyBindings()

    def refreshKeyGrabs(self, reason=""):
        """ Refreshes the enabled key grabs for this script. """

        msg = "DEFAULT: refreshing key grabs"
        if reason:
            msg += f": {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # TODO: Should probably avoid removing key grabs and re-adding them.
        # Otherwise, a key could conceivably leak through while the script is
        # in the process of updating the bindings.
        self.removeKeyGrabs("refreshing")
        self.addKeyGrabs("refreshing")

    def registerEventListeners(self):
        event_manager.get_manager().register_script_listeners(self)
        self.utilities.connectToClipboard()

    def deregisterEventListeners(self):
        event_manager.get_manager().deregister_script_listeners(self)
        self.utilities.disconnectFromClipboard()

    def _saveFocusedObjectInfo(self, obj):
        """Saves some basic information about obj. Note that this method is
        intended to be called primarily (if not only) by locus_of_focus_changed().
        It is expected that accessible event callbacks will update the point
        of reference data specific to that event. The goal here is to weed
        out duplicate events."""

        if not obj:
            return

        # We want to save the name because some apps and toolkits emit name
        # changes after the focus or selection has changed, even though the
        # name has not.
        name = AXObject.get_name(obj)
        names = self.point_of_reference.get('names', {})
        names[hash(obj)] = name
        window = focus_manager.get_manager().get_active_window()
        if window:
            names[hash(window)] = AXObject.get_name(window)
        self.point_of_reference['names'] = names

        descriptions = self.point_of_reference.get('descriptions', {})
        descriptions[hash(obj)] = AXObject.get_description(obj)
        self.point_of_reference['descriptions'] = descriptions

        # We want to save the offset for text objects because some apps and
        # toolkits emit caret-moved events immediately after a text object
        # gains focus, even though the caret has not actually moved.
        caretOffset = AXText.get_caret_offset(obj)
        self._saveLastCursorPosition(obj, max(0, caretOffset))
        self.utilities.updateCachedTextSelection(obj)

        # We want to save the current row and column of a newly focused
        # or selected table cell so that on subsequent cell focus/selection
        # we only present the changed location.
        row, column = AXTable.get_cell_coordinates(obj, find_cell=True)
        self.point_of_reference['lastColumn'] = column
        self.point_of_reference['lastRow'] = row

        self.point_of_reference['checkedChange'] = hash(obj), AXUtilities.is_checked(obj)
        self.point_of_reference['selectedChange'] = hash(obj), AXUtilities.is_selected(obj)
        self.point_of_reference['expandedChange'] = hash(obj), AXUtilities.is_expanded(obj)

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

        if old_focus == new_focus:
            msg = 'DEFAULT: old focus == new focus'
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        # Don't apply the is-same-object heuristic in the case of table cells.
        # One scenario is email client message lists. When you delete a message
        # and land on the next one, the cells likely occupy the same space,
        # have the same role, and might even have the same name, same path, etc.
        if not AXUtilities.is_table_cell(old_focus) \
           and not AXUtilities.is_table_cell(new_focus) \
           and self.utilities.isSameObject(old_focus, new_focus):
            tokens = ["DEFAULT: old focus", old_focus,
                      "believed to be same as new focus", new_focus]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
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

        focus_manager.get_manager().set_active_window(self.utilities.topLevelObject(new_focus))
        self.updateBraille(new_focus)

        utterances = self.speech_generator.generateSpeech(
            new_focus,
            priorObj=old_focus)

        if self.utilities.shouldInterruptForLocusOfFocusChange(
           old_focus, new_focus, event):
            self.presentationInterrupt()
        speech.speak(utterances, interrupt=False)
        self._saveFocusedObjectInfo(new_focus)

    def activate(self):
        """Called when this script is activated."""

        tokens = ["DEFAULT: Activating script for", self.app]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        settings_manager.get_manager().load_app_settings(self)
        braille.checkBrailleSetting()
        braille.setupKeyRanges(self.braille_bindings.keys())
        speech.check_speech_setting()
        self.get_speech_and_verbosity_manager().update_punctuation_level()
        self.get_speech_and_verbosity_manager().update_capitalization_style()

        self.addKeyGrabs("script activation")
        tokens = ["DEFAULT: Script for", self.app, "activated"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    def updateBraille(self, obj, **args):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        """

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: update disabled", True)
            return

        if not obj:
            return

        result, focusedRegion = self.braille_generator.generateBraille(obj, **args)
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

    def showAppPreferencesGUI(self, inputEvent=None):
        """Shows the app Preferences dialog."""

        prefs = {}
        manager = settings_manager.get_manager()
        for key in settings.userCustomizableSettings:
            prefs[key] = manager.get_setting(key)

        ui = orca_gui_prefs.OrcaSetupGUI(self, prefs)
        ui.showGUI()
        return True

    def showPreferencesGUI(self, inputEvent=None):
        """Displays the Preferences dialog."""

        manager = settings_manager.get_manager()
        prefs = manager.get_general_settings(manager.profile)
        ui = orca_gui_prefs.OrcaSetupGUI(script_manager.get_manager().get_default_script(), prefs)
        ui.showGUI()
        return True

    def quitOrca(self, inputEvent=None):
        """Quit Orca."""

        orca.shutdown()
        return True

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the left.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if isinstance(inputEvent, input_event.KeyboardEvent) \
           and not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            msg = "DEFAULT: panBrailleLeft command requires braille or braille monitor"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_flat_review_presenter().is_active():
            if self.isBrailleBeginningShowing():
                self.get_flat_review_presenter().go_start_of_line(self, inputEvent)
                self.get_flat_review_presenter().go_previous_character(self, inputEvent)
            else:
                self.panBrailleInDirection(panAmount, panToLeft=True)

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
                self.get_flat_review_presenter().go_previous_character(self, inputEvent)
        else:
            self.panBrailleInDirection(panAmount, panToLeft=True)
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            self.refreshBraille(False, stopFlash=False)

        return True

    def panBrailleLeftOneChar(self, inputEvent=None):
        """Nudges the braille display one character to the left.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        self.panBrailleLeft(inputEvent, 1)

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the right.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the end will take you to the beginning of the next line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if isinstance(inputEvent, input_event.KeyboardEvent) \
           and not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            msg = "DEFAULT: panBrailleRight command requires braille or braille monitor"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_flat_review_presenter().is_active():
            if self.isBrailleEndShowing():
                self.get_flat_review_presenter().go_end_of_line(self, inputEvent)
                # Reviewing the next character also updates the braille output
                # and refreshes the display.
                self.get_flat_review_presenter().go_next_character(self, inputEvent)
                return True
            self.panBrailleInDirection(panAmount, panToLeft=False)
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
            self.panBrailleInDirection(panAmount, panToLeft=False)
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            self.refreshBraille(False, stopFlash=False)

        return True

    def panBrailleRightOneChar(self, inputEvent=None):
        """Nudges the braille display one character to the right.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        self.panBrailleRight(inputEvent, 1)

    def goBrailleHome(self, inputEvent=None):
        """Returns to the component with focus."""

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()
            return True

        return braille.returnToRegionWithFocus(inputEvent)

    def setContractedBraille(self, inputEvent=None):
        """Toggles contracted braille."""

        self._setContractedBraille(inputEvent)
        return True

    def processRoutingKey(self, inputEvent=None):
        """Processes a cursor routing key."""

        braille.processRoutingKey(inputEvent)
        return True

    def processBrailleCutBegin(self, inputEvent=None):
        """Clears the selection and moves the caret offset in the currently
        active text area.
        """

        obj, offset = self.getBrailleCaretContext(inputEvent)
        if offset < 0:
            return True

        AXText.clear_all_selected_text(obj)
        self.utilities.setCaretOffset(obj, offset)
        return True

    def processBrailleCutLine(self, inputEvent=None):
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        obj, offset = self.getBrailleCaretContext(inputEvent)
        if offset < 0:
            return True

        startOffset = AXText.get_selection_start_offset(obj)
        endOffset = AXText.get_selection_end_offset(obj)
        if (startOffset < 0 or endOffset < 0):
            caretOffset = AXText.get_caret_offset(obj)
            startOffset = min(offset, caretOffset)
            endOffset = max(offset, caretOffset)

        AXText.set_selected_text(obj, startOffset, endOffset)
        text = AXText.get_selected_text(obj)[0]
        self.utilities.setClipboardText(text)
        return True

    def routePointerToItem(self, inputEvent=None):
        """Moves the mouse pointer to the current item."""

        # Store the original location for scripts which want to restore
        # it later.
        #
        self.oldMouseCoordinates = self.utilities.absoluteMouseCoordinates()
        self.lastMouseRoutingTime = time.time()
        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().route_pointer_to_object(self, inputEvent)
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

    def leftClickReviewItem(self, inputEvent=None):
        """Performs a left mouse button click on the current item."""

        if self.get_flat_review_presenter().is_active():
            obj = self.get_flat_review_presenter().get_current_object(self, inputEvent)
            if self.get_event_synthesizer().try_all_clickable_actions(obj):
                return True
            return self.get_flat_review_presenter().left_click_on_object(self, inputEvent)

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_event_synthesizer().try_all_clickable_actions(focus):
            return True

        if AXText.get_character_count(focus):
            if self.get_event_synthesizer().click_character(focus, 1):
                return True

        if self.get_event_synthesizer().click_object(focus, 1):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.presentMessage(full, brief)
        return False

    def rightClickReviewItem(self, inputEvent=None):
        """Performs a right mouse button click on the current item."""

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().right_click_on_object(self, inputEvent)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_event_synthesizer().click_character(focus, 3):
            return True

        if self.get_event_synthesizer().click_object(focus, 3):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.presentMessage(full, brief)
        return False

    def spellCurrentItem(self, itemString):
        """Spell the current flat review word or line.

        Arguments:
        - itemString: the string to spell.
        """

        for character in itemString:
            self.speak_character(character)

    def say_all(self, inputEvent, obj=None, offset=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        tokens = ["DEFAULT: SayAll requested starting from", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not obj or AXObject.is_dead(obj):
            self.presentMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        if AXText.is_whitespace_or_empty(obj):
            utterances = self.speech_generator.generateSpeech(obj)
            speech.speak(utterances)
            return True

        speech.say_all(self.textLines(obj, offset), self.__sayAllProgressCallback)
        return True

    def cycleSettingsProfile(self, inputEvent=None):
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

        speech.shutdown()
        speech.init()

        # TODO: This is another "too close to code freeze" hack to cause the
        # command names to be presented in the correct language.
        self.setup_input_event_handlers()

        self.presentMessage(messages.PROFILE_CHANGED % name, name)
        return True

    def cycleDebugLevel(self, inputEvent=None):
        levels = [debug.LEVEL_ALL, "all",
                  debug.LEVEL_FINEST, "finest",
                  debug.LEVEL_FINER, "finer",
                  debug.LEVEL_FINE, "fine",
                  debug.LEVEL_CONFIGURATION, "configuration",
                  debug.LEVEL_INFO, "info",
                  debug.LEVEL_WARNING, "warning",
                  debug.LEVEL_SEVERE, "severe",
                  debug.LEVEL_OFF, "off"]

        try:
            levelIndex = levels.index(debug.debugLevel) + 2
        except Exception:
            levelIndex = 0
        else:
            if levelIndex >= len(levels):
                levelIndex = 0

        debug.debugLevel = levels[levelIndex]
        briefMessage = levels[levelIndex + 1]
        fullMessage =  f"Debug level {briefMessage}."
        self.presentMessage(fullMessage, briefMessage)

        return True

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def noOp(self, event):
        """Just here to capture events.

        Arguments:
        - event: the Event
        """
        pass

    def on_active_changed(self, event):
        """Callback for object:state-changed:active accessibility events."""

        window = event.source
        if AXUtilities.is_application(AXObject.get_parent(event.source)):
            window = AXObject.find_real_app_and_window_for(event.source)[1]

        if AXUtilities.is_dialog_or_alert(window) or AXUtilities.is_frame(window):
            if event.detail1 and not focus_manager.get_manager().can_be_active_window(window):
                return

            sourceIsActiveWindow = self.utilities.isSameObject(
                window, focus_manager.get_manager().get_active_window())
            if sourceIsActiveWindow and not event.detail1:
                if self.utilities.inMenu():
                    msg = "DEFAULT: Ignoring event. In menu."
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return

                msg = "DEFAULT: Event is for active window. Clearing state."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(None)
                return

            if not sourceIsActiveWindow and event.detail1:
                msg = "DEFAULT: Updating active window."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(
                    window, set_window_as_focus=True, notify_script=True)

        if self.run_find_command:
            self.run_find_command = False
            self.get_flat_review_finder().find(self)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not event.any_data:
            msg = "DEFAULT: Ignoring event. No any_data."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if not AXUtilities.is_focused(event.source) \
           and not AXUtilities.is_focused(event.any_data):
            msg = "DEFAULT: Ignoring event. Neither source nor child have focused state."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if self.stopSpeechOnActiveDescendantChanged(event):
            self.presentationInterrupt()

        tokens = ["DEFAULT: Setting locus of focus to any_data", event.any_data]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        focus_manager.get_manager().set_locus_of_focus(event, event.any_data)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""
        pass

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if not self.utilities.isSameObject(
           event.source, focus_manager.get_manager().get_locus_of_focus()):
            return

        if AXUtilities.is_expandable(event.source):
            return

        # Radio buttons normally change their state when you arrow to them,
        # so we handle the announcement of their state changes in the focus
        # handling code.  However, we do need to handle radio buttons where
        # the user needs to press the space key to select them.
        if AXUtilities.is_radio_button(event.source) \
           and input_event_manager.get_manager().last_event_was_space():
            return

        oldObj, oldState = self.point_of_reference.get('checkedChange', (None, 0))
        if hash(oldObj) == hash(event.source) and oldState == event.detail1:
            return

        self.presentObject(event.source, alreadyFocused=True, interrupt=True)
        self.point_of_reference['checkedChange'] = hash(event.source), event.detail1

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        AXObject.clear_cache_now("children-changed event.")
        if AXUtilities.is_table_related(event.source):
            AXTable.clear_cache_now("children-changed event.")

    def on_children_removed(self, event):
        """Callback for object:children-changed:remove accessibility events."""

        AXObject.clear_cache_now("children-changed event.")
        if AXUtilities.is_table_related(event.source):
            AXTable.clear_cache_now("children-changed event.")

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        obj, offset = self.point_of_reference.get("lastCursorPosition", (None, -1))
        if offset == event.detail1 and obj == event.source:
            msg = "DEFAULT: Event is for last saved cursor position"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if not AXUtilities.is_showing(event.source):
            msg = "DEFAULT: Event source is not showing. Clearing cache."
            AXObject.clear_cache(obj, False, msg)
            if not AXUtilities.is_showing(event.source):
                msg = "DEFAULT: Event source is still not showing."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                if not self.utilities.presentEventFromNonShowingObject(event):
                    return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != focus and AXUtilities.is_focused(event.source):
            if self.utilities.topLevelObjectIsActiveWindow(event.source):
                tokens = ["DEFAULT: Updating locusOfFocus to", event.source]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
            else:
                msg = "DEFAULT: Source window is not active window"
                debug.printMessage(debug.LEVEL_INFO, msg, True)

        if event.source != focus:
            tokens = ["DEFAULT: Event source (", event.source, ") is not locusOfFocus"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()


        offset = AXText.get_caret_offset(event.source)
        self._saveLastCursorPosition(event.source, offset)
        if AXText.has_selected_text(event.source):
            msg = "DEFAULT: Event source has text selections"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.utilities.handleTextSelectionChange(event.source)
            return

        string = self.utilities.getCachedTextSelection(obj)[2]
        if string and self.utilities.handleTextSelectionChange(obj):
            msg = "DEFAULT: Event handled as text selection change"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        msg = "DEFAULT: Presenting text at new caret position"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._presentTextAtNewCaretPosition(event)

    def on_description_changed(self, event):
        """Callback for object:property-change:accessible-description events."""

        obj = event.source
        descriptions = self.point_of_reference.get('description', {})
        oldDescription = descriptions.get(hash(obj))
        if oldDescription == event.any_data:
            tokens = ["DEFAULT: Old description (", oldDescription, ") is the same as new one"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        if obj != focus_manager.get_manager().get_locus_of_focus():
            msg = "DEFAULT: Event is for object other than the locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        descriptions[hash(obj)] = event.any_data
        self.point_of_reference['descriptions'] = descriptions
        if event.any_data:
            self.presentMessage(event.any_data)

    def on_document_attributes_changed(self, event):
        """Callback for document:attributes-changed accessibility events."""

        pass

    def on_document_reload(self, event):
        """Callback for document:reload accessibility events."""

        pass

    def on_document_load_complete(self, event):
        """Callback for document:load-complete accessibility events."""

        pass

    def on_document_load_stopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        pass

    def on_document_page_changed(self, event):
        """Callback for document:page-changed accessibility events."""

        if event.detail1 < 0:
            return

        if not AXDocument.did_page_change(event.source):
            return

        self.presentMessage(messages.PAGE_NUMBER % event.detail1)

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if AXUtilities.is_table_related(event.source):
            AXTable.clear_cache_now("expanded-changed event.")

        if not self.utilities.isPresentableExpandedChangedEvent(event):
            return

        obj = event.source
        oldObj, oldState = self.point_of_reference.get('expandedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return

        self.presentObject(obj, alreadyFocused=True, interrupt=True)
        self.point_of_reference['expandedChange'] = hash(obj), event.detail1

        details = self.utilities.detailsContentForObject(obj)
        for detail in details:
            self.speakMessage(detail, interrupt=False)

    def on_indeterminate_changed(self, event):
        """Callback for object:state-changed:indeterminate accessibility events."""

        # If this state is cleared, the new state will become checked or unchecked
        # and we should get object:state-changed:checked events for those cases.
        # Therefore, if the state is not now indeterminate/partially checked,
        # ignore this event.
        if not event.detail1:
            return

        obj = event.source
        if not self.utilities.isSameObject(obj, focus_manager.get_manager().get_locus_of_focus()):
            return

        oldObj, oldState = self.point_of_reference.get('indeterminateChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return

        self.presentObject(obj, alreadyFocused=True, interrupt=True)
        self.point_of_reference['indeterminateChange'] = hash(obj), event.detail1

    def on_mouse_button(self, event):
        """Callback for mouse:button events."""

        input_event_manager.get_manager().process_mouse_button_event(event)

    def on_announcement(self, event):
        """Callback for object:announcement events."""

        if isinstance(event.any_data, str):
            self.presentMessage(event.any_data)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        names = self.point_of_reference.get('names', {})
        oldName = names.get(hash(event.source))
        if oldName == event.any_data:
            tokens = ["DEFAULT: Old name (", oldName, ") is the same as new name"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        if AXUtilities.is_combo_box(event.source) or AXUtilities.is_table_cell(event.source):
            msg = "DEFAULT: Event is redundant notification for this role"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if AXUtilities.is_frame(event.source):
            if event.source != focus_manager.get_manager().get_active_window():
                msg = "DEFAULT: Event is for frame other than the active window"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return
            focus = focus_manager.get_manager().get_locus_of_focus()
            if AXUtilities.is_editable(focus) and AXText.get_character_count(focus) \
               and AXText.get_all_text(focus) in event.any_data:
                msg = "DEFAULT: Event is redundant notification for the locusOfFocus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return
        elif event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "DEFAULT: Event is for object other than the locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        names[hash(event.source)] = event.any_data
        self.point_of_reference['names'] = names
        if event.any_data:
            self.presentMessage(event.any_data)

    def on_object_attributes_changed(self, event):
        """Callback for object:attributes-changed accessibility events."""

        AXObject.clear_cache_now("object-attributes-changed event.")
        if AXUtilities.is_table_related(event.source):
            AXTable.clear_cache_now("object-attributes-changed event.")

    def on_pressed_changed(self, event):
        """Callback for object:state-changed:pressed accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, focus_manager.get_manager().get_locus_of_focus()):
            return

        oldObj, oldState = self.point_of_reference.get('pressedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return

        self.presentObject(obj, alreadyFocused=True, interrupt=True)
        self.point_of_reference['pressedChange'] = hash(obj), event.detail1

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        # TODO - JD: Is this still needed?
        AXObject.clear_cache(event.source, False, "Ensuring we have the correct state.")
        if not AXUtilities.is_focused(event.source):
            msg = "DEFAULT: Event is not toggling of currently-focused object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if not self.utilities.isSameObject(
           focus_manager.get_manager().get_locus_of_focus(), event.source):
            msg = "DEFAULT: Event is not for locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return

        isSelected = AXUtilities.is_selected(event.source)
        if isSelected != event.detail1:
            msg = "DEFAULT: Bogus event: detail1 doesn't match state"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        oldObj, oldState = self.point_of_reference.get('selectedChange', (None, 0))
        if hash(oldObj) == hash(event.source) and oldState == event.detail1:
            msg = "DEFAULT: Duplicate or spam event"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        announceState = False
        manager = input_event_manager.get_manager()
        if manager.last_event_was_space():
            announceState = True
        elif (manager.last_event_was_up() or manager.last_event_was_down()) \
                and AXUtilities.is_table_cell(event.source):
            announceState = isSelected

        if not announceState:
            return

        # TODO - JD: Unlike the other state-changed callbacks, it seems unwise
        # to call generateSpeech() here because that also will present the
        # expandable state if appropriate for the object type. The generators
        # need to gain some smarts w.r.t. state changes.

        if event.detail1:
            self.speakMessage(messages.TEXT_SELECTED, interrupt=False)
        else:
            self.speakMessage(messages.TEXT_UNSELECTED, interrupt=False)

        self.point_of_reference['selectedChange'] = hash(event.source), event.detail1

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self.utilities.handlePasteLocusOfFocusChange():
            if self.utilities.topLevelObjectIsActiveAndCurrent(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
        elif self.utilities.handleContainerSelectionChange(event.source):
            return
        elif AXUtilities.manages_descendants(event.source):
            return
        elif not (AXUtilities.is_showing(event.source) and AXUtilities.is_visible(event.source)):
            tokens = ["DEFAULT: Ignoring event: source is not showing and visible", event.source]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        if AXUtilities.is_tree_or_tree_table(event.source):
            active_window = focus_manager.get_manager().get_active_window()
            if not AXObject.find_ancestor(event.source, lambda x: x and x == active_window):
                tokens = ["DEFAULT: Ignoring event:", event.source, "is not inside", active_window]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return

        # If the current item's selection is toggled, we'll present that
        # via the state-changed event.
        if input_event_manager.get_manager().last_event_was_space():
            return

        if AXUtilities.is_combo_box(event.source) and not AXUtilities.is_expanded(event.source):
            if AXUtilities.is_focused(self.utilities.getEntryForEditableComboBox(event.source)):
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
        for child in selectedChildren:
            if AXObject.find_ancestor(focus, lambda x: x == child):
                tokens = ["DEFAULT: Child", child, "is ancestor of locusOfFocus"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                self._saveFocusedObjectInfo(focus)
                return

            if child == mouseReviewItem:
                tokens = ["DEFAULT: Child", child, "is current mouse review item"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                continue

            if AXUtilities.is_page_tab(child) and focus \
               and AXObject.get_name(child) == AXObject.get_name(focus) \
               and not AXUtilities.is_focused(event.source):
                tokens = ["DEFAULT:", child, "'s selection redundant to", focus]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                break

            if not self.utilities.isLayoutOnly(child):
                focus_manager.get_manager().set_locus_of_focus(event, child)
                break

    def on_sensitive_changed(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""
        pass

    def on_focus(self, event):
        """Callback for focus: accessibility events."""

        pass

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        if not AXUtilities.is_focused(event.source):
            return

        obj = event.source
        window, dialog = self.utilities.frameAndDialog(obj)
        if window and not focus_manager.get_manager().can_be_active_window(window) and not dialog:
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

            speech.speak(self.speech_generator.generateSpeech(obj))
            msg = self.utilities.getNotificationContent(obj)
            self.displayBrailleMessage(msg, flashTime=settings.brailleFlashTime)
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

        if not self.utilities.isPresentableTextChangedEventForLocusOfFocus(event):
            return

        if settings_manager.get_manager().get_setting('speakMisspelledIndicator'):
            offset = AXText.get_caret_offset(event.source)
            if not AXText.get_substring(event.source, offset, offset + 1).isalnum():
                offset -= 1
            if AXText.is_word_misspelled(event.source, offset - 1) \
               or AXText.is_word_misspelled(event.source, offset + 1):
                self.speakMessage(messages.MISSPELLED)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if not self.utilities.isPresentableTextChangedEventForLocusOfFocus(event):
            return

        self.utilities.handleUndoTextEvent(event)

        focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
        self.updateBraille(event.source)

        full, brief = "", ""
        if self.utilities.isClipboardTextChangedEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to clipboard cut"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            full, brief = messages.CLIPBOARD_CUT_FULL, messages.CLIPBOARD_CUT_BRIEF
        elif self.utilities.isSelectedTextDeletionEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to deleting selected text"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            full = messages.SELECTION_DELETED

        if full or brief:
            self.presentMessage(full, brief)
            self.utilities.updateCachedTextSelection(event.source)
            return

        string = self.utilities.deletedText(event)
        if self.utilities.isDeleteCommandTextDeletionEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to Delete command"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            string = AXText.get_character_at_offset(event.source)[0]
        elif self.utilities.isBackSpaceCommandTextDeletionEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to BackSpace command"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        else:
            msg = "DEFAULT: Event is not being presented due to lack of cause"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if len(string) == 1:
            self.speak_character(string)
        else:
            voice = self.speech_generator.voice(string=string)
            string = self.utilities.adjustForRepeats(string)
            self.speakMessage(string, voice)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not self.utilities.isPresentableTextChangedEventForLocusOfFocus(event):
            return

        self.utilities.handleUndoTextEvent(event)

        if event.source == focus_manager.get_manager().get_locus_of_focus() \
           and self.utilities.isAutoTextEvent(event):
            self._saveFocusedObjectInfo(event.source)
        focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
        self.updateBraille(event.source)

        full, brief = "", ""
        if self.utilities.isClipboardTextChangedEvent(event):
            msg = "DEFAULT: Insertion is believed to be due to clipboard paste"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            full, brief = messages.CLIPBOARD_PASTED_FULL, messages.CLIPBOARD_PASTED_BRIEF
        elif self.utilities.isSelectedTextRestoredEvent(event):
            msg = "DEFAULT: Insertion is believed to be due to restoring selected text"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            full = messages.SELECTION_RESTORED

        if full or brief:
            self.presentMessage(full, brief)
            self.utilities.updateCachedTextSelection(event.source)
            return

        speakString = True

        # Because some implementations are broken.
        string = self.utilities.insertedText(event)

        manager = input_event_manager.get_manager()
        if manager.last_event_was_page_switch():
            msg = "DEFAULT: Insertion is believed to be due to page switch"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            speakString = False
        elif manager.last_event_was_command():
            msg = "DEFAULT: Insertion is believed to be due to command"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isMiddleMouseButtonTextInsertionEvent(event):
            msg = "DEFAULT: Insertion is believed to be due to middle mouse button"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isEchoableTextInsertionEvent(event):
            msg = "DEFAULT: Insertion is believed to be echoable"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isAutoTextEvent(event):
            msg = "DEFAULT: Insertion is believed to be auto text event"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isSelectedTextInsertionEvent(event):
            msg = "DEFAULT: Insertion is also selected"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        else:
            msg = "DEFAULT: Not speaking inserted string due to lack of cause"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            speakString = False

        if speakString:
            if len(string) == 1:
                self.speak_character(string)
            else:
                voice = self.speech_generator.voice(obj=event.source, string=string)
                string = self.utilities.adjustForRepeats(string)
                self.speakMessage(string, voice)

        if len(string) != 1:
            return

        if settings_manager.get_manager().get_setting('enableEchoBySentence') \
           and self.echoPreviousSentence(event.source):
            return

        if settings_manager.get_manager().get_setting('enableEchoByWord'):
            self.echoPreviousWord(event.source)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source

        # We won't handle undo here as it can lead to double-presentation.
        # If there is an application for which text-changed events are
        # missing upon undo, handle them in an app or toolkit script.

        self.utilities.handleTextSelectionChange(obj)
        self.updateBraille(obj)

    def on_column_reordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        AXTable.clear_cache_now("column-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return

        if event.source != AXTable.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return

        self.presentMessage(messages.TABLE_REORDERED_COLUMNS)

    def on_row_reordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        AXTable.clear_cache_now("row-reordered event.")
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
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not isProgressBarUpdate \
           and event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "DEFAULT: Source != locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if AXUtilities.is_spin_button(event.source):
            self._saveFocusedObjectInfo(event.source)

        self.updateBraille(event.source, isProgressBarUpdate=isProgressBarUpdate)
        speech.speak(self.speech_generator.generateSpeech(
            event.source, alreadyFocused=True, isProgressBarUpdate=isProgressBarUpdate))
        self.__play(self.sound_generator.generateSound(
            event.source, alreadyFocused=True, isProgressBarUpdate=isProgressBarUpdate))

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        window = AXObject.find_real_app_and_window_for(event.source)[1]
        if not focus_manager.get_manager().can_be_active_window(window):
            return

        activeWindow = focus_manager.get_manager().get_active_window()
        if self.utilities.isSameObject(window, activeWindow):
            msg = "DEFAULT: Event is for active window."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        self.point_of_reference = {}

        focus_manager.get_manager().set_active_window(window)
        if AXObject.get_child_count(window) == 1:
            child = AXObject.get_child(window, 0)
            if AXUtilities.is_menu(child):
                focus_manager.get_manager().set_locus_of_focus(event, child)
                return

        focus_manager.get_manager().set_locus_of_focus(event, window)

    def on_window_created(self, event):
        """Callback for window:create accessibility events."""

        pass

    def on_window_destroyed(self, event):
        """Callback for window:destroy accessibility events."""

        pass

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        if self.utilities.inMenu():
            msg = "DEFAULT: Ignoring event. In menu."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if event.source != focus_manager.get_manager().get_active_window():
            msg = "DEFAULT: Ignoring event. Not for active window"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        if self.get_learn_mode_presenter().is_active():
            self.get_learn_mode_presenter().quit()

        self.point_of_reference = {}

        focus_manager.get_manager().clear_state("Window deactivated")
        script_manager.get_manager().set_active_script(None, "Window deactivated")

    def onClipboardContentsChanged(self, *args):
        if self.get_flat_review_presenter().is_active():
            return

        if not self.utilities.objectContentsAreInClipboard():
            return

        if not self.utilities.topLevelObjectIsActiveAndCurrent():
            return

        manager = input_event_manager.get_manager()
        if manager.last_event_was_copy():
            self.presentMessage(messages.CLIPBOARD_COPIED_FULL, messages.CLIPBOARD_COPIED_BRIEF)
            return

        if not manager.last_event_was_cut():
            return

        if AXUtilities.is_editable(focus_manager.get_manager().get_locus_of_focus()):
            return

        self.presentMessage(messages.CLIPBOARD_CUT_FULL, messages.CLIPBOARD_CUT_BRIEF)

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        """Presents text at the new position, based on heuristics. Returns True if handled."""

        obj = otherObj or event.source
        self.updateBrailleForNewCaretPosition(obj)
        if self._inSayAll:
            msg = "DEFAULT: Not presenting text because SayAll is active"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        manager = input_event_manager.get_manager()
        if manager.last_event_was_line_navigation():
            self.sayLine(obj)
            return True
        if manager.last_event_was_word_navigation():
            self.sayWord(obj)
            return True
        if manager.last_event_was_character_navigation():
            self.sayCharacter(obj)
            return True
        if manager.last_event_was_page_navigation():
            self.sayLine(obj)
            return True
        if manager.last_event_was_line_boundary_navigation():
            self.sayCharacter(obj)
            return True
        if manager.last_event_was_file_boundary_navigation():
            self.sayLine(obj)
            return True
        if manager.last_event_was_primary_click_or_release():
            string = self.utilities.getCachedTextSelection(event.source)[-1]
            if not string:
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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self._sayAllIsInterrupted:
            msg = "DEFAULT: SayAll is interrupted"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return treatInterruptedAsIn

        msg = "DEFAULT: Not in SayAll"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return False

    def echoPreviousSentence(self, obj):
        """Speaks the sentence prior to the caret if at a sentence boundary."""

        offset = AXText.get_caret_offset(obj)
        char, start = AXText.get_character_at_offset(obj, offset - 1)[0:-1]
        previousChar, previousStart = AXText.get_character_at_offset(obj, start - 1)[0:-1]
        if not (previousChar and self.utilities.isSentenceDelimiter(char, previousChar)):
            return False

        sentence = AXText.get_sentence_at_offset(obj, previousStart)[0]
        if not sentence:
            return False

        voice = self.speech_generator.voice(obj=obj, string=sentence)
        sentence = self.utilities.adjustForRepeats(sentence)
        self.speakMessage(sentence, voice)
        return True

    def echoPreviousWord(self, obj):
        """Speaks the word prior to the caret if at a word boundary."""

        offset = AXText.get_caret_offset(obj)
        if offset == -1:
            offset = AXText.get_character_count(obj)

        if offset <= 0:
            return False

        previousChar, previousStart = AXText.get_character_at_offset(obj, offset - 1)[0:-1]
        if not self.utilities.isWordDelimiter(previousChar):
            return False

        # Two back-to-back delimiters should not result in a re-echo.
        previousChar, previousStart = AXText.get_character_at_offset(obj, previousStart - 1)[0:-1]
        if self.utilities.isWordDelimiter(previousChar):
            return False

        word = AXText.get_word_at_offset(obj, previousStart)[0]
        if not word:
            return False

        voice = self.speech_generator.voice(obj=obj, string=word)
        word = self.utilities.adjustForRepeats(word)
        self.speakMessage(word, voice)
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

    def sayLine(self, obj):
        """Speaks the line of an AccessibleText object that contains the
        caret, unless the line is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        line, startOffset = AXText.get_line_at_offset(obj)[0:2]
        if len(line) and line != "\n":
            indentationDescription = self.utilities.indentationDescription(line)
            if indentationDescription:
                self.speakMessage(indentationDescription)

            endOffset = startOffset + len(line)
            focus_manager.get_manager().emit_region_changed(
                obj, startOffset, endOffset, focus_manager.CARET_TRACKING)

            utterance = []
            split = self.utilities.splitSubstringByLanguage(obj, startOffset, endOffset)
            for start, end, string, language, dialect in split:
                if not string:
                    continue

                voice = self.speech_generator.voice(
                    obj=obj, string=string, language=language, dialect=dialect)
                string = self.utilities.adjustForLinks(obj, string, start)
                string = self.utilities.adjustForRepeats(string)
                if self.utilities.shouldVerbalizeAllPunctuation(obj):
                    string = self.utilities.verbalizeAllPunctuation(string)

                # Some synthesizers will verbalize the whitespace, so if we've already
                # described it, prevent double-presentation by stripping it off.
                if not utterance and indentationDescription:
                    string = string.lstrip()

                result = [string]
                result.extend(voice)
                utterance.append(result)
            speech.speak(utterance)
        else:
            # Speak blank line if appropriate.
            #
            self.sayCharacter(obj)

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
            result = self.utilities.indentationDescription(phrase)
            if result:
                self.speakMessage(result)

            focus_manager.get_manager().emit_region_changed(
                obj, startOffset, endOffset, focus_manager.CARET_TRACKING)

            voice = self.speech_generator.voice(obj=obj, string=phrase)
            phrase = self.utilities.adjustForRepeats(phrase)
            if self.utilities.shouldVerbalizeAllPunctuation(obj):
                phrase = self.utilities.verbalizeAllPunctuation(phrase)

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

        string = word.replace("\n", "\\n")
        msg = (
            f"DEFAULT: Final word at offset {offset} is '{string}' "
            f"({startOffset}-{endOffset})"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        self.speakMisspelledIndicator(obj, startOffset)
        self.sayPhrase(obj, startOffset, endOffset)
        self.point_of_reference["lastTextUnitSpoken"] = "word"

    def presentObject(self, obj, **args):
        interrupt = args.get("interrupt", False)
        tokens = ["DEFAULT: Presenting object", obj, ". Interrupt:", interrupt]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not args.get("speechonly", False):
            self.updateBraille(obj, **args)
        utterances = self.speech_generator.generateSpeech(obj, **args)
        speech.speak(utterances, interrupt=interrupt)

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in on_active_descendant_changed.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        if not event.any_data:
            return True

        # In an object which manages its descendants, the
        # 'descendants' may really be a single object which changes
        # its name. If the name-change occurs followed by the active
        # descendant changing (to the same object) we won't present
        # the locusOfFocus because it hasn't changed. Thus we need to
        # be sure not to cut of the presentation of the name-change
        # event.

        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus == event.any_data:
            names = self.point_of_reference.get('names', {})
            oldName = names.get(hash(focus), '')
            if not oldName or AXObject.get_name(event.any_data) == oldName:
                return False

        if event.source == focus == AXObject.get_parent(event.any_data):
            return False

        return True

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
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: update review disabled", True)
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
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
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
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: The current code was stopping on the first region which met the
        # following condition. Is that definitely the right thing to do? Assume so for now.
        # Also: Should the default script be accessing things like the viewport directly??
        def isMatch(x):
            return x is not None and x.brailleOffset + len(x.string) > braille.viewport[0]

        regions = list(filter(isMatch, regions))
        if not regions:
            msg = "DEFAULT: Could not find review region to move to start of display"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        tokens = ["DEFAULT: Candidates for start of display:"]
        for region in regions:
            tokens.extend(["\n", region])
        debug.printTokens(debug.LEVEL_INFO, tokens, True)


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
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        [word, charOffset] = region.zone.getWordAtOffset(offset)
        if word:
            tokens = ["DEFAULT: Setting start of display to", word, ", ", charOffset]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            context = self.getFlatReviewContext()
            context.setCurrent(
                word.zone.line.index,
                word.zone.index,
                word.index,
                charOffset)
        else:
            tokens = ["DEFAULT: Setting start of display to", region.zone]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
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
        priorObj = obj
        document = self.utilities.getDocumentForObject(obj)

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        while obj:
            speech.speak(self.speech_generator.generateContext(obj, priorObj=priorObj))

            style = settings_manager.get_manager().get_setting('sayAllStyle')
            if style == settings.SAYALL_STYLE_SENTENCE and AXText.supports_sentence_iteration(obj):
                iterator = AXText.iter_sentence
            else:
                iterator = AXText.iter_line

            for string, start, end in iterator(obj, offset):
                voice = self.speech_generator.voice(obj=obj, string=string)
                if voice and isinstance(voice, list):
                    voice = voice[0]

                string = self.utilities.adjustForLinks(obj, string, start)
                string = self.utilities.adjustForRepeats(string)

                context = speechserver.SayAllContext(obj, string, start, end)
                tokens = ["DEFAULT:", context]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)

                self._sayAllContexts.append(context)
                self.get_event_synthesizer().scroll_into_view(obj, start, end)
                yield [context, voice]

            priorObj = obj
            offset = 0
            obj = self.utilities.findNextObject(obj)
            if document != self.utilities.getDocumentForObject(obj):
                break

        self._inSayAll = False
        self._sayAllContexts = []

        msg = "DEFAULT: textLines complete. Verifying SayAll status"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
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

    def speakMisspelledIndicator(self, obj, offset):
        """Speaks an announcement indicating that a given word is misspelled.

        Arguments:
        - obj: An accessible which implements the accessible text interface.
        - offset: Offset in the accessible's text for which to retrieve the
          attributes.
        """

        if not settings_manager.get_manager().get_setting('speakMisspelledIndicator'):
            return

        # If we're on whitespace, we cannot be on a misspelled word.
        char = AXText.get_character_at_offset(obj, offset)[0]
        if not char.strip() or self.utilities.isWordDelimiter(char):
            self._lastWordCheckedForSpelling = char[0]
            return

        if not AXText.is_word_misspelled(obj, offset):
            return

        word = AXText.get_word_at_offset(obj, offset)[0]
        if word != self._lastWordCheckedForSpelling:
            self.speakMessage(messages.MISSPELLED)

        # Store this word so that we do not continue to present the
        # presence of the red squiggly as the user arrows amongst
        # the characters.
        self._lastWordCheckedForSpelling = word

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
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        speech.stop()
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
        debug.printMessage(debug.LEVEL_INFO, msg, True)
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
            sound.play(sounds[i], interrupt=False)

    @staticmethod
    def addBrailleRegionToLine(region, line):
        """Adds the braille region to the line.

        Arguments:
        - region: a braille.Region (e.g. what is returned by the braille
          generator's generateBraille() method.
        - line: a braille.Line
        """

        line.addRegion(region)

    @staticmethod
    def addBrailleRegionsToLine(regions, line):
        """Adds the braille region to the line.

        Arguments:
        - regions: a series of braille.Region instances (a single instance
          being what is returned by the braille generator's generateBraille()
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
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: display message disabled", True)
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
    def panBrailleInDirection(panAmount=0, panToLeft=True):
        """Pans the display to the left, limiting the pan to the beginning
        of the line being displayed.

        Arguments:
        - panAmount: the amount to pan.  A value of 0 means the entire
          width of the physical display.
        - panToLeft: if True, pan to the left; otherwise to the right

        Returns True if a pan actually happened.
        """

        if panToLeft:
            return braille.panLeft(panAmount)
        else:
            return braille.panRight(panAmount)

    @staticmethod
    def panBrailleToOffset(offset):
        """Automatically pan left or right to make sure the current offset
        is showing."""

        braille.panToOffset(offset)

    def updateBrailleForNewCaretPosition(self, obj):
        """Try to reposition the cursor without having to do a full update."""

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: update caret disabled", True)
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
            self.updateBraille(obj)

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
    def _setContractedBraille(event):
        """Turns contracted braille on or off based upon the event.

        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
          the dictionary form of the expanded BrlAPI event.
        """

        braille.setContractedBraille(event)

    ########################################################################
    #                                                                      #
    # Speech methods                                                       #
    # (scripts should not call methods in speech.py directly)              #
    #                                                                      #
    ########################################################################

    def speak_key_event(self, event):
        """Method to speak a keyboard event. Scripts should use this method
        rather than calling speech.speakKeyEvent directly."""

        string = None
        if event.is_printable_key():
            string = event.event_string

        voice = self.speech_generator.voice(string=string)
        speech.speak_key_event(event, voice)

    def speak_character(self, character):
        """Method to speak a single character. Scripts should use this
        method rather than calling speech.speakCharacter directly."""

        voice = self.speech_generator.voice(string=character)
        speech.speak_character(character, voice)

    def speakMessage(self, string, voice=None, interrupt=True, resetStyles=True, force=False):
        """Method to speak a single string. Scripts should use this
        method rather than calling speech.speak directly.

        - string: The string to be spoken.
        - voice: The voice to use. By default, the "system" voice will
          be used.
        - interrupt: If True, any current speech should be interrupted
          prior to speaking the new text.
        """

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

        speech.speak(string, voice, interrupt)

        if voice == systemVoice and resetStyles:
            manager.set_setting('capitalizationStyle', capStyle)
            self.get_speech_and_verbosity_manager().update_capitalization_style()

            manager.set_setting('verbalizePunctuationStyle', punctStyle)
            self.get_speech_and_verbosity_manager().update_punctuation_level()
