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

"""The default Script for presenting information to the user using
both speech and Braille.  This is based primarily on the de-facto
standard implementation of the AT-SPI, which is the GAIL support
for GTK."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import time

from gi.repository import Gtk, Gdk

import pyatspi
import orca.braille as braille
import orca.chnames as chnames
import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.eventsynthesizer as eventsynthesizer
import orca.find as find
import orca.flat_review as flat_review
import orca.guilabels as guilabels
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.messages as messages
import orca.orca as orca
import orca.orca_gui_commandlist as commandlist
import orca.orca_state as orca_state
import orca.phonnames as phonnames
import orca.script as script
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech as speech
import orca.speechserver as speechserver
import orca.mouse_review as mouse_review
import orca.notification_messages as notification_messages

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Script(script.Script):

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'
    NO_BREAK_SPACE_CHARACTER  = '\u00a0'

    # generatorCache
    #
    DISPLAYED_LABEL = 'displayedLabel'
    DISPLAYED_TEXT = 'displayedText'
    KEY_BINDING = 'keyBinding'
    NESTING_LEVEL = 'nestingLevel'
    NODE_LEVEL = 'nodeLevel'
    REAL_ACTIVE_DESCENDANT = 'realActiveDescendant'

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """
        script.Script.__init__(self, app)

        self.flatReviewContext  = None
        self.windowActivateTime = None
        self.targetCursorCell = None

        self.justEnteredFlatReviewMode = False

        self.digits = '0123456789'
        self.whitespace = ' \t\n\r\v\f'

        # Unicode currency symbols (populated by the
        # getUnicodeCurrencySymbols() routine).
        #
        self._unicodeCurrencySymbols = []

        # Used to determine whether progress bar value changes presented.
        self.lastProgressBarTime = {}
        self.lastProgressBarValue = {}

        self.lastSelectedMenu = None

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

        # Used to copy/append the current flat review contents to the
        # clipboard.
        #
        self.currentReviewContents = ""

        self._lastWord = ""
        self._lastWordCheckedForSpelling = ""

        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._sayAllContexts = []

        if app:
            app.setCacheMask(
                pyatspi.cache.DEFAULT ^ pyatspi.cache.CHILDREN ^ pyatspi.cache.NAME)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        self.inputEventHandlers["routePointerToItemHandler"] = \
            input_event.InputEventHandler(
                Script.routePointerToItem,
                cmdnames.ROUTE_POINTER_TO_ITEM)

        self.inputEventHandlers["leftClickReviewItemHandler"] = \
            input_event.InputEventHandler(
                Script.leftClickReviewItem,
                cmdnames.LEFT_CLICK_REVIEW_ITEM)

        self.inputEventHandlers["rightClickReviewItemHandler"] = \
             input_event.InputEventHandler(
                Script.rightClickReviewItem,
                cmdnames.RIGHT_CLICK_REVIEW_ITEM)

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                cmdnames.SAY_ALL)

        self.inputEventHandlers["whereAmIBasicHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmIBasic,
                cmdnames.WHERE_AM_I_BASIC)

        self.inputEventHandlers["whereAmIDetailedHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmIDetailed,
                cmdnames.WHERE_AM_I_DETAILED)

        self.inputEventHandlers["getTitleHandler"] = \
            input_event.InputEventHandler(
                Script.presentTitle,
                cmdnames.PRESENT_TITLE)

        self.inputEventHandlers["getStatusBarHandler"] = \
            input_event.InputEventHandler(
                Script.presentStatusBar,
                cmdnames.PRESENT_STATUS_BAR)

        self.inputEventHandlers["findHandler"] = \
            input_event.InputEventHandler(
                orca.showFindGUI,
                cmdnames.SHOW_FIND_GUI)

        self.inputEventHandlers["findNextHandler"] = \
            input_event.InputEventHandler(
                Script.findNext,
                cmdnames.FIND_NEXT)

        self.inputEventHandlers["findPreviousHandler"] = \
            input_event.InputEventHandler(
                Script.findPrevious,
                cmdnames.FIND_PREVIOUS)

        self.inputEventHandlers["toggleFlatReviewModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggleFlatReviewMode,
                cmdnames.TOGGLE_FLAT_REVIEW)

        self.inputEventHandlers["reviewPreviousLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPreviousLine,
                cmdnames.REVIEW_PREVIOUS_LINE)

        self.inputEventHandlers["reviewHomeHandler"] = \
            input_event.InputEventHandler(
                Script.reviewHome,
                cmdnames.REVIEW_HOME)

        self.inputEventHandlers["reviewCurrentLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentLine,
                cmdnames.REVIEW_CURRENT_LINE)

        self.inputEventHandlers["reviewSpellCurrentLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewSpellCurrentLine,
                cmdnames.REVIEW_SPELL_CURRENT_LINE)

        self.inputEventHandlers["reviewPhoneticCurrentLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPhoneticCurrentLine,
                cmdnames.REVIEW_PHONETIC_CURRENT_LINE)

        self.inputEventHandlers["reviewNextLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewNextLine,
                cmdnames.REVIEW_NEXT_LINE)

        self.inputEventHandlers["reviewEndHandler"] = \
            input_event.InputEventHandler(
                Script.reviewEnd,
                cmdnames.REVIEW_END)

        self.inputEventHandlers["reviewPreviousItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPreviousItem,
                cmdnames.REVIEW_PREVIOUS_ITEM)

        self.inputEventHandlers["reviewAboveHandler"] = \
            input_event.InputEventHandler(
                Script.reviewAbove,
                cmdnames.REVIEW_ABOVE)

        self.inputEventHandlers["reviewCurrentItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentItem,
                cmdnames.REVIEW_CURRENT_ITEM)

        self.inputEventHandlers["reviewSpellCurrentItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewSpellCurrentItem,
                cmdnames.REVIEW_SPELL_CURRENT_ITEM)

        self.inputEventHandlers["reviewPhoneticCurrentItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPhoneticCurrentItem,
                cmdnames.REVIEW_PHONETIC_CURRENT_ITEM)

        self.inputEventHandlers["reviewNextItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewNextItem,
                cmdnames.REVIEW_NEXT_ITEM)

        self.inputEventHandlers["reviewCurrentAccessibleHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentAccessible,
                cmdnames.REVIEW_CURRENT_ACCESSIBLE)

        self.inputEventHandlers["reviewBelowHandler"] = \
            input_event.InputEventHandler(
                Script.reviewBelow,
                cmdnames.REVIEW_BELOW)

        self.inputEventHandlers["reviewPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPreviousCharacter,
                cmdnames.REVIEW_PREVIOUS_CHARACTER)

        self.inputEventHandlers["reviewEndOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewEndOfLine,
                cmdnames.REVIEW_END_OF_LINE)

        self.inputEventHandlers["reviewBottomLeftHandler"] = \
            input_event.InputEventHandler(
                Script.reviewBottomLeft,
                cmdnames.REVIEW_BOTTOM_LEFT)

        self.inputEventHandlers["reviewCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentCharacter,
                cmdnames.REVIEW_CURRENT_CHARACTER)

        self.inputEventHandlers["reviewSpellCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewSpellCurrentCharacter,
                cmdnames.REVIEW_SPELL_CURRENT_CHARACTER)

        self.inputEventHandlers["reviewUnicodeCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewUnicodeCurrentCharacter,
                cmdnames.REVIEW_UNICODE_CURRENT_CHARACTER)

        self.inputEventHandlers["reviewNextCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewNextCharacter,
                cmdnames.REVIEW_NEXT_CHARACTER)

        self.inputEventHandlers["flatReviewCopyHandler"] = \
            input_event.InputEventHandler(
                Script.flatReviewCopy,
                cmdnames.FLAT_REVIEW_COPY)

        self.inputEventHandlers["flatReviewAppendHandler"] = \
            input_event.InputEventHandler(
                Script.flatReviewAppend,
                cmdnames.FLAT_REVIEW_APPEND)

        self.inputEventHandlers["toggleTableCellReadModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggleTableCellReadMode,
                cmdnames.TOGGLE_TABLE_CELL_READ_MODE)

        self.inputEventHandlers["readCharAttributesHandler"] = \
            input_event.InputEventHandler(
                Script.readCharAttributes,
                cmdnames.READ_CHAR_ATTRIBUTES)

        self.inputEventHandlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["goBrailleHomeHandler"] = \
            input_event.InputEventHandler(
                Script.goBrailleHome,
                cmdnames.GO_BRAILLE_HOME)

        self.inputEventHandlers["contractedBrailleHandler"] = \
            input_event.InputEventHandler(
                Script.setContractedBraille,
                cmdnames.SET_CONTRACTED_BRAILLE)

        self.inputEventHandlers["processRoutingKeyHandler"] = \
            input_event.InputEventHandler(
                Script.processRoutingKey,
                cmdnames.PROCESS_ROUTING_KEY)

        self.inputEventHandlers["processBrailleCutBeginHandler"] = \
            input_event.InputEventHandler(
                Script.processBrailleCutBegin,
                cmdnames.PROCESS_BRAILLE_CUT_BEGIN)

        self.inputEventHandlers["processBrailleCutLineHandler"] = \
            input_event.InputEventHandler(
                Script.processBrailleCutLine,
                cmdnames.PROCESS_BRAILLE_CUT_LINE)

        self.inputEventHandlers["enterLearnModeHandler"] = \
            input_event.InputEventHandler(
                Script.enterLearnMode,
                cmdnames.ENTER_LEARN_MODE)

        self.inputEventHandlers["decreaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                speech.decreaseSpeechRate,
                cmdnames.DECREASE_SPEECH_RATE)

        self.inputEventHandlers["increaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                speech.increaseSpeechRate,
                cmdnames.INCREASE_SPEECH_RATE)

        self.inputEventHandlers["decreaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                speech.decreaseSpeechPitch,
                cmdnames.DECREASE_SPEECH_PITCH)

        self.inputEventHandlers["increaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                speech.increaseSpeechPitch,
                cmdnames.INCREASE_SPEECH_PITCH)

        self.inputEventHandlers["decreaseSpeechVolumeHandler"] = \
            input_event.InputEventHandler(
                speech.decreaseSpeechVolume,
                cmdnames.DECREASE_SPEECH_VOLUME)

        self.inputEventHandlers["increaseSpeechVolumeHandler"] = \
            input_event.InputEventHandler(
                speech.increaseSpeechVolume,
                cmdnames.INCREASE_SPEECH_VOLUME)

        self.inputEventHandlers["shutdownHandler"] = \
            input_event.InputEventHandler(
                orca.quitOrca,
                cmdnames.QUIT_ORCA)

        self.inputEventHandlers["preferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                orca.showPreferencesGUI,
                cmdnames.SHOW_PREFERENCES_GUI)

        self.inputEventHandlers["appPreferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                orca.showAppPreferencesGUI,
                cmdnames.SHOW_APP_PREFERENCES_GUI)

        self.inputEventHandlers["toggleSilenceSpeechHandler"] = \
            input_event.InputEventHandler(
                Script.toggleSilenceSpeech,
                cmdnames.TOGGLE_SPEECH)

        self.inputEventHandlers["toggleSpeechVerbosityHandler"] = \
            input_event.InputEventHandler(
                Script.toggleSpeechVerbosity,
                cmdnames.TOGGLE_SPEECH_VERBOSITY)

        self.inputEventHandlers[ \
          "toggleSpeakingIndentationJustificationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleSpeakingIndentationJustification,
                cmdnames.TOGGLE_SPOKEN_INDENTATION_AND_JUSTIFICATION)

        self.inputEventHandlers["cycleSpeakingPunctuationLevelHandler"] = \
            input_event.InputEventHandler(
                Script.cycleSpeakingPunctuationLevel,
                cmdnames.CYCLE_PUNCTUATION_LEVEL)

        self.inputEventHandlers["cycleSettingsProfileHandler"] = \
            input_event.InputEventHandler(
                Script.cycleSettingsProfile,
                cmdnames.CYCLE_SETTINGS_PROFILE)

        self.inputEventHandlers["cycleCapitalizationStyleHandler"] = \
            input_event.InputEventHandler(
                Script.cycleCapitalizationStyle,
                cmdnames.CYCLE_CAPITALIZATION_STYLE)

        self.inputEventHandlers["cycleKeyEchoHandler"] = \
            input_event.InputEventHandler(
                Script.cycleKeyEcho,
                cmdnames.CYCLE_KEY_ECHO)

        self.inputEventHandlers["cycleDebugLevelHandler"] = \
            input_event.InputEventHandler(
                Script.cycleDebugLevel,
                cmdnames.CYCLE_DEBUG_LEVEL)

        self.inputEventHandlers["goToPrevBookmark"] = \
            input_event.InputEventHandler(
                Script.goToPrevBookmark,
                cmdnames.BOOKMARK_GO_TO_PREVIOUS)

        self.inputEventHandlers["goToBookmark"] = \
            input_event.InputEventHandler(
                Script.goToBookmark,
                cmdnames.BOOKMARK_GO_TO)

        self.inputEventHandlers["goToNextBookmark"] = \
            input_event.InputEventHandler(
                Script.goToNextBookmark,
                cmdnames.BOOKMARK_GO_TO_NEXT)

        self.inputEventHandlers["addBookmark"] = \
            input_event.InputEventHandler(
                Script.addBookmark,
                cmdnames.BOOKMARK_ADD)

        self.inputEventHandlers["saveBookmarks"] = \
            input_event.InputEventHandler(
                Script.saveBookmarks,
                cmdnames.BOOKMARK_SAVE)

        self.inputEventHandlers["toggleMouseReviewHandler"] = \
            input_event.InputEventHandler(
                mouse_review.toggle,
                cmdnames.MOUSE_REVIEW_TOGGLE)

        self.inputEventHandlers["presentTimeHandler"] = \
            input_event.InputEventHandler(
                Script.presentTime,
                cmdnames.PRESENT_CURRENT_TIME)

        self.inputEventHandlers["presentDateHandler"] = \
            input_event.InputEventHandler(
                Script.presentDate,
                cmdnames.PRESENT_CURRENT_DATE)

        self.inputEventHandlers["bypassNextCommandHandler"] = \
            input_event.InputEventHandler(
                Script.bypassNextCommand,
                cmdnames.BYPASS_NEXT_COMMAND)

        self.inputEventHandlers.update(notification_messages.inputEventHandlers)

    def getInputEventHandlerKey(self, inputEventHandler):
        """Returns the name of the key that contains an inputEventHadler
        passed as argument
        """

        for keyName, handler in list(self.inputEventHandlers.items()):
            if handler == inputEventHandler:
                return keyName

        return None

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = script.Script.getListeners(self)
        listeners["focus:"]                                 = \
            self.onFocus
        #listeners["keyboard:modifiers"]                     = \
        #    self.noOp
        listeners["document:reload"]                        = \
            self.onDocumentReload
        listeners["document:load-complete"]                 = \
            self.onDocumentLoadComplete
        listeners["document:load-stopped"]                  = \
            self.onDocumentLoadStopped
        listeners["mouse:button"]                           = \
            self.onMouseButton
        listeners["object:property-change:accessible-name"] = \
            self.onNameChanged
        listeners["object:text-caret-moved"]                = \
            self.onCaretMoved
        listeners["object:text-changed:delete"]             = \
            self.onTextDeleted
        listeners["object:text-changed:insert"]             = \
            self.onTextInserted
        listeners["object:active-descendant-changed"]       = \
            self.onActiveDescendantChanged
        listeners["object:children-changed"]                = \
            self.onChildrenChanged
        listeners["object:state-changed:active"]            = \
            self.onActiveChanged
        listeners["object:state-changed:busy"]              = \
            self.onBusyChanged
        listeners["object:state-changed:focused"]           = \
            self.onFocusedChanged
        listeners["object:state-changed:showing"]           = \
            self.onShowingChanged
        listeners["object:state-changed:checked"]           = \
            self.onCheckedChanged
        listeners["object:state-changed:pressed"]           = \
            self.onPressedChanged
        listeners["object:state-changed:indeterminate"]     = \
            self.onIndeterminateChanged
        listeners["object:state-changed:expanded"]          = \
            self.onExpandedChanged
        listeners["object:state-changed:selected"]          = \
            self.onSelectedChanged
        listeners["object:state-changed:sensitive"]         = \
            self.onSensitiveChanged
        listeners["object:text-attributes-changed"]         = \
            self.onTextAttributesChanged
        listeners["object:text-selection-changed"]          = \
            self.onTextSelectionChanged
        listeners["object:selection-changed"]               = \
            self.onSelectionChanged
        listeners["object:property-change:accessible-value"] = \
            self.onValueChanged
        listeners["object:value-changed"]                   = \
            self.onValueChanged
        listeners["object:column-reordered"]                = \
            self.onColumnReordered
        listeners["object:row-reordered"]                   = \
            self.onRowReordered
        listeners["window:activate"]                        = \
            self.onWindowActivated
        listeners["window:deactivate"]                      = \
            self.onWindowDeactivated
        listeners["window:create"]                          = \
            self.onWindowCreated

        return listeners

    def __getDesktopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        numeric keypad for focus tracking and flat review.
        """

        import orca.desktop_keyboardmap as desktop_keyboardmap
        keyBindings = keybindings.KeyBindings()
        keyBindings.load(desktop_keyboardmap.keymap, self.inputEventHandlers)
        return keyBindings

    def __getLaptopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        the main keyboard keys for focus tracking and flat review.
        """

        import orca.laptop_keyboardmap as laptop_keyboardmap
        keyBindings = keybindings.KeyBindings()
        keyBindings.load(laptop_keyboardmap.keymap, self.inputEventHandlers)
        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = script.Script.getKeyBindings(self)

        bindings = self.getDefaultKeyBindings()
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        bindings = self.getToolkitKeyBindings()
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        bindings = self.getAppKeyBindings()
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        try:
            keyBindings = _settingsManager.overrideKeyBindings(self, keyBindings)
        except:
            debug.println(debug.LEVEL_WARNING,
                          "WARNING: problem overriding keybindings:")
            debug.printException(debug.LEVEL_WARNING)

        return keyBindings

    def getDefaultKeyBindings(self):
        """Returns the default script's keybindings, i.e. without any of
        the toolkit or application specific commands added."""

        keyBindings = keybindings.KeyBindings()

        layout = _settingsManager.getSetting('keyboardLayout')
        if layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            for keyBinding in self.__getDesktopBindings().keyBindings:
                keyBindings.add(keyBinding)
        else:
            for keyBinding in self.__getLaptopBindings().keyBindings:
                keyBindings.add(keyBinding)

        import orca.common_keyboardmap as common_keyboardmap
        keyBindings.load(common_keyboardmap.keymap, self.inputEventHandlers)

        return keyBindings

    def getBrailleBindings(self):
        """Defines the braille bindings for this script.

        Returns a dictionary where the keys are BrlTTY commands and the
        values are InputEventHandler instances.
        """
        brailleBindings = script.Script.getBrailleBindings(self)
        try:
            brailleBindings[braille.brlapi.KEY_CMD_FWINLT]   = \
                self.inputEventHandlers["panBrailleLeftHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FWINRT]   = \
                self.inputEventHandlers["panBrailleRightHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_LNUP]     = \
                self.inputEventHandlers["reviewAboveHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_LNDN]     = \
                self.inputEventHandlers["reviewBelowHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FREEZE]   = \
                self.inputEventHandlers["toggleFlatReviewModeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_TOP_LEFT] = \
                self.inputEventHandlers["reviewHomeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_BOT_LEFT] = \
                self.inputEventHandlers["reviewBottomLeftHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_HOME]     = \
                self.inputEventHandlers["goBrailleHomeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_SIXDOTS]   = \
                self.inputEventHandlers["contractedBrailleHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_ROUTE]   = \
                self.inputEventHandlers["processRoutingKeyHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_CUTBEGIN] = \
                self.inputEventHandlers["processBrailleCutBeginHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_CUTLINE] = \
                self.inputEventHandlers["processBrailleCutLineHandler"]
        except AttributeError:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "WARNING: braille bindings unavailable:")
        except:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "WARNING: braille bindings unavailable:")
            debug.printException(debug.LEVEL_CONFIGURATION)
        return brailleBindings

    def deactivate(self):
        """Called when this script is deactivated."""

        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self.pointOfReference = {}

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event. It uses the super
        class equivalent to do most of the work. The only thing done here
        is to detect when the user is trying to get out of learn mode.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

        return script.Script.processKeyboardEvent(self, keyboardEvent)

    def _saveFocusedObjectInfo(self, obj):
        """Saves some basic information about obj. Note that this method is
        intended to be called primarily (if not only) by locusOfFocusChanged().
        It is expected that accessible event callbacks will update the point
        of reference data specific to that event. The goal here is to weed
        out duplicate events."""

        if not obj:
            return

        try:
            role = obj.getRole()
            state = obj.getState()
            name = obj.name
        except:
            return

        # We want to save the name because some apps and toolkits emit name
        # changes after the focus or selection has changed, even though the
        # name has not.
        names = self.pointOfReference.get('names', {})
        names[hash(obj)] = name
        self.pointOfReference['names'] = names

        # We want to save the offset for text objects because some apps and
        # toolkits emit caret-moved events immediately after a text object
        # gains focus, even though the caret has not actually moved.
        try:
            text = obj.queryText()
        except:
            pass
        else:
            self._saveLastCursorPosition(obj, max(0, text.caretOffset))
            textSelections = self.pointOfReference.get('textSelections', {})
            textSelections[hash(obj)] = text.getSelection(0)
            self.pointOfReference['textSelections'] = textSelections

        # We want to save the current row and column of a newly focused
        # or selected table cell so that on subsequent cell focus/selection
        # we only present the changed location.
        if role == pyatspi.ROLE_TABLE_CELL:
            try:
                table = obj.parent.queryTable()
            except:
                pass
            else:
                index = self.utilities.cellIndex(obj)
                column = table.getColumnAtIndex(index)
                row = table.getRowAtIndex(index)
                self.pointOfReference['lastColumn'] = column
                self.pointOfReference['lastRow'] = row
        else:
            self.pointOfReference['lastColumn'] = -1
            self.pointOfReference['lastRow'] = -1

        self.pointOfReference['checkedChange'] = \
            hash(obj), state.contains(pyatspi.STATE_CHECKED)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        if not newLocusOfFocus:
            orca_state.noFocusTimeStamp = time.time()
            return

        if newLocusOfFocus.getState().contains(pyatspi.STATE_DEFUNCT):
            return

        if self.utilities.isSameObject(oldLocusOfFocus, newLocusOfFocus):
            return

        try:
            if self.findCommandRun:
                # Then the Orca Find dialog has just given up focus
                # to the original window.  We don't want to speak
                # the window title, current line, etc.
                return
        except:
            pass

        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        self.updateBraille(newLocusOfFocus)

        shouldNotInterrupt = \
           self.windowActivateTime and time.time() - self.windowActivateTime < 1

        # [[[TODO: WDW - this should move to the generator.]]]
        if newLocusOfFocus.getRole() == pyatspi.ROLE_LINK:
            voice = self.voices[settings.HYPERLINK_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]
        utterances = self.speechGenerator.generateSpeech(
            newLocusOfFocus,
            priorObj=oldLocusOfFocus)
        speech.speak(utterances, voice, not shouldNotInterrupt)
        self._saveFocusedObjectInfo(newLocusOfFocus)

    def activate(self):
        """Called when this script is activated."""

        _settingsManager.loadAppSettings(self)
        braille.setupKeyRanges(list(self.brailleBindings.keys()))
        speech.updatePunctuationLevel()

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: update disabled")
            return

        if not obj:
            return

        self.clearBraille()

        line = self.getNewBrailleLine()
        braille.addLine(line)

        result = self.brailleGenerator.generateBraille(obj)
        self.addBrailleRegionsToLine(result[0], line)

        if extraRegion:
            self.addBrailleRegionToLine(extraRegion, line)

        if extraRegion:
            self.setBrailleFocus(extraRegion)
        else:
            self.setBrailleFocus(result[1])

        self.refreshBraille(True)

    ########################################################################
    #                                                                      #
    # INPUT EVENT HANDLERS (AKA ORCA COMMANDS)                             #
    #                                                                      #
    ########################################################################

    def bypassNextCommand(self, inputEvent=None):
        """Causes the next keyboard command to be ignored by Orca
        and passed along to the current application.

        Returns True to indicate the input event has been consumed.
        """

        self.presentMessage(messages.BYPASS_MODE_ENABLED)
        orca_state.bypassNextCommand = True
        return True

    def enterLearnMode(self, inputEvent=None):
        """Turns learn mode on.  The user must press the escape key to exit
        learn mode.

        Returns True to indicate the input event has been consumed.
        """

        if orca_state.learnModeEnabled:
            return True

        self.presentMessage(messages.VERSION)
        self.speakMessage(messages.LEARN_MODE_START_SPEECH)
        self.displayBrailleMessage(messages.LEARN_MODE_START_BRAILLE)
        orca_state.learnModeEnabled = True
        return True

    def exitLearnMode(self, inputEvent=None):
        """Turns learn mode off.

        Returns True to indicate the input event has been consumed.
        """

        if not orca_state.learnModeEnabled:
            return False

        if isinstance(inputEvent, input_event.KeyboardEvent) \
           and not inputEvent.event_string == 'Escape':
            return False

        self.presentMessage(messages.LEARN_MODE_STOP)
        orca_state.learnModeEnabled = False
        return True

    def listOrcaShortcuts(self, inputEvent=None):
        """Shows a simple gui listing Orca's bound commands."""

        if not inputEvent or inputEvent.event_string == "F2":
            bound = self.getDefaultKeyBindings().getBoundBindings()
            title = messages.shortcutsFoundOrca(len(bound))
        else:
            try:
                appName = self.app.name
            except AttributeError:
                appName = messages.APPLICATION_NO_NAME

            bound = self.getAppKeyBindings().getBoundBindings()
            bound.extend(self.getToolkitKeyBindings().getBoundBindings())
            title = messages.shortcutsFoundApp(len(bound), appName)

        if not bound:
            self.presentMessage(title)
            return True

        self.exitLearnMode()

        rows = [(kb.handler.function,
                 kb.handler.description,
                 kb.asString()) for kb in bound]
        sorted(rows, key=lambda cmd: cmd[2])

        header1 = guilabels.KB_HEADER_FUNCTION
        header2 = guilabels.KB_HEADER_KEY_BINDING
        commandlist.showUI(title, ("", header1, header2), rows, False)
        return True

    def findNext(self, inputEvent):
        """Searches forward for the next instance of the string
        searched for via the Orca Find dialog.  Other than direction
        and the starting point, the search options initially specified
        (case sensitivity, window wrap, and full/partial match) are
        preserved.
        """

        lastQuery = find.getLastQuery()
        if lastQuery:
            lastQuery.searchBackwards = False
            lastQuery.startAtTop = False
            self.find(lastQuery)
        else:
            orca.showFindGUI()

    def findPrevious(self, inputEvent):
        """Searches backwards for the next instance of the string
        searched for via the Orca Find dialog.  Other than direction
        and the starting point, the search options initially specified
        (case sensitivity, window wrap, and full/or partial match) are
        preserved.
        """

        lastQuery = find.getLastQuery()
        if lastQuery:
            lastQuery.searchBackwards = True
            lastQuery.startAtTop = False
            self.find(lastQuery)
        else:
            orca.showFindGUI()

    def addBookmark(self, inputEvent):
        """ Add an in-page accessible object bookmark for this key.
        Delegates to Bookmark.addBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.addBookmark(inputEvent)

    def goToBookmark(self, inputEvent):
        """ Go to the bookmark indexed by inputEvent.hw_code.  Delegates to
        Bookmark.goToBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.goToBookmark(inputEvent)

    def goToNextBookmark(self, inputEvent):
        """ Go to the next bookmark location.  If no bookmark has yet to be
        selected, the first bookmark will be used.  Delegates to
        Bookmark.goToNextBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.goToNextBookmark(inputEvent)

    def goToPrevBookmark(self, inputEvent):
        """ Go to the previous bookmark location.  If no bookmark has yet to
        be selected, the first bookmark will be used.  Delegates to
        Bookmark.goToPrevBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.goToPrevBookmark(inputEvent)

    def saveBookmarks(self, inputEvent):
        """ Save the bookmarks for this script. Delegates to
        Bookmark.saveBookmarks """
        bookmarks = self.getBookmarks()
        bookmarks.saveBookmarks(inputEvent)

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the left.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if self.isBrailleBeginningShowing():
                self.flatReviewContext.goBegin(flat_review.Context.LINE)
                self.reviewPreviousCharacter(inputEvent)
            else:
                self.panBrailleInDirection(panAmount, panToLeft=True)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [charString, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif self.isBrailleBeginningShowing() and orca_state.locusOfFocus \
             and self.utilities.isTextArea(orca_state.locusOfFocus):

            # If we're at the beginning of a line of a multiline text
            # area, then force it's caret to the end of the previous
            # line.  The assumption here is that we're currently
            # viewing the line that has the caret -- which is a pretty
            # good assumption for focus tacking mode.  When we set the
            # caret position, we will get a caret event, which will
            # then update the braille.
            #
            text = orca_state.locusOfFocus.queryText()
            [lineString, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            movedCaret = False
            if startOffset > 0:
                movedCaret = text.setCaretOffset(startOffset - 1)

            # If we didn't move the caret and we're in a terminal, we
            # jump into flat review to review the text.  See
            # http://bugzilla.gnome.org/show_bug.cgi?id=482294.
            #
            if (not movedCaret) \
               and (orca_state.locusOfFocus.getRole() \
                    == pyatspi.ROLE_TERMINAL):
                context = self.getFlatReviewContext()
                context.goBegin(flat_review.Context.LINE)
                self.reviewPreviousCharacter(inputEvent)
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
        beyond the end will take you to the begininng of the next line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if self.isBrailleEndShowing():
                self.flatReviewContext.goEnd(flat_review.Context.LINE)
                self.reviewNextCharacter(inputEvent)
            else:
                self.panBrailleInDirection(panAmount, panToLeft=False)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [charString, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif self.isBrailleEndShowing() and orca_state.locusOfFocus \
             and self.utilities.isTextArea(orca_state.locusOfFocus):
            # If we're at the end of a line of a multiline text area, then
            # force it's caret to the beginning of the next line.  The
            # assumption here is that we're currently viewing the line that
            # has the caret -- which is a pretty good assumption for focus
            # tacking mode.  When we set the caret position, we will get a
            # caret event, which will then update the braille.
            #
            text = orca_state.locusOfFocus.queryText()
            [lineString, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            if endOffset < text.characterCount:
                text.setCaretOffset(endOffset)
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

        if self.flatReviewContext:
            return self.toggleFlatReviewMode(inputEvent)
        else:
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

        obj, caretOffset = self.getBrailleCaretContext(inputEvent)

        if caretOffset >= 0:
            self.utilities.clearTextSelection(obj)
            self.utilities.setCaretOffset(obj, caretOffset)

        return True

    def processBrailleCutLine(self, inputEvent=None):
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        obj, caretOffset = self.getBrailleCaretContext(inputEvent)

        if caretOffset >= 0:
            self.utilities.adjustTextSelection(obj, caretOffset)
            texti = obj.queryText()
            startOffset, endOffset = texti.getSelection(0)
            string = texti.getText(startOffset, endOffset)
            clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
            clipboard.set_text(string, len(string))

        return True

    def routePointerToItem(self, inputEvent=None):
        """Moves the mouse pointer to the current item."""

        # Store the original location for scripts which want to restore
        # it later.
        #
        self.oldMouseCoordinates = self.utilities.absoluteMouseCoordinates()
        self.lastMouseRoutingTime = time.time()
        if self.flatReviewContext:
            self.flatReviewContext.routeToCurrent()
        else:
            try:
                eventsynthesizer.routeToCharacter(orca_state.locusOfFocus)
            except:
                try:
                    eventsynthesizer.routeToObject(orca_state.locusOfFocus)
                except:
                    full = messages.LOCATION_NOT_FOUND_FULL
                    brief = messages.LOCATION_NOT_FOUND_BRIEF
                    self.presentMessage(full, brief)

        return True

    def presentStatusBar(self, inputEvent):
        """Speaks and brailles the contents of the status bar and/or default
        button of the window with focus.
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)
        voice = self.voices[settings.DEFAULT_VOICE]

        frame, dialog = self.utilities.frameAndDialog(obj)
        if frame:
            # In windows with lots of objects (Thunderbird, Firefox, etc.)
            # If we wait until we've checked for both the status bar and
            # a default button, there may be a noticable delay. Therefore,
            # speak the status bar info immediately and then go looking
            # for a default button.
            #
            msg = self.speechGenerator.generateStatusBar(frame)
            if msg:
                self.presentMessage(msg, voice=voice)

        window = dialog or frame
        if window:
            msg = self.speechGenerator.generateDefaultButton(window)
            if msg:
                self.presentMessage(msg, voice=voice)

    def presentTitle(self, inputEvent):
        """Speaks and brailles the title of the window with focus."""

        title = self.speechGenerator.generateTitle(orca_state.locusOfFocus)
        for (string, voice) in title:
            self.presentMessage(string, voice=voice)

    def readCharAttributes(self, inputEvent=None):
        """Reads the attributes associated with the current text character.
        Calls outCharAttributes to speak a list of attributes. By default,
        a certain set of attributes will be spoken. If this is not desired,
        then individual application scripts should override this method to
        only speak the subset required.
        """

        attrs, start, end = self.utilities.textAttributes(orca_state.locusOfFocus, None, True)

        # Get a dictionary of text attributes that the user cares about.
        [userAttrList, userAttrDict] = self.utilities.stringToKeysAndDict(
            _settingsManager.getSetting('enabledSpokenTextAttributes'))

        # Because some implementors make up their own attribute names,
        # we need to convert.
        userAttrList = list(map(self.utilities.getAppNameForAttribute, userAttrList))
        nullValues = ['0', '0mm', 'none', 'false']

        for key in userAttrList:
            value = attrs.get(key)
            ignoreIfValue = userAttrDict.get(key)
            if value in nullValues and ignoreIfValue in nullValues:
                continue

            if value and value != ignoreIfValue:
                self.speakMessage(self.utilities.localizeTextAttribute(key, value))

        return True

    def leftClickReviewItem(self, inputEvent=None):
        """Performs a left mouse button click on the current item."""

        if self.flatReviewContext:
            self.flatReviewContext.clickCurrent(1)
        else:
            try:
                eventsynthesizer.clickCharacter(orca_state.locusOfFocus, 1)
            except:
                try:
                    eventsynthesizer.clickObject(orca_state.locusOfFocus, 1)
                except:
                    self.speakMessage(messages.LOCATION_NOT_FOUND_FULL)
        return True

    def rightClickReviewItem(self, inputEvent=None):
        """Performs a right mouse button click on the current item."""

        if self.flatReviewContext:
            self.flatReviewContext.clickCurrent(3)
        else:
            try:
                eventsynthesizer.clickCharacter(orca_state.locusOfFocus, 3)
            except:
                try:
                    eventsynthesizer.clickObject(orca_state.locusOfFocus, 3)
                except:
                    full = messages.LOCATION_NOT_FOUND_FULL
                    brief = messages.LOCATION_NOT_FOUND_BRIEF
                    self.presentMessage(full, brief)

        return True

    def spellCurrentItem(self, itemString):
        """Spell the current flat review word or line.

        Arguments:
        - itemString: the string to spell.
        """

        for character in itemString:
            self.speakCharacter(character)

    def _reviewCurrentItem(self, inputEvent, targetCursorCell=0,
                           speechType=1):
        """Presents the current item to the user.

        Arguments:
        - inputEvent - the current input event.
        - targetCursorCell - if non-zero, the target braille cursor cell.
        - speechType - the desired presentation: speak (1), spell (2), or
                       phonetic (3).
        """

        context = self.getFlatReviewContext()
        [wordString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.WORD)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not wordString) \
               or (not len(wordString)) \
               or (wordString == "\n"):
                speech.speak(messages.BLANK)
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n":
                    speech.speak(messages.BLANK)
                elif wordString.isspace():
                    speech.speak(messages.WHITE_SPACE)
                elif wordString.isupper() and speechType == 1:
                    speech.speak(wordString,
                                 self.voices[settings.UPPERCASE_VOICE])
                elif speechType == 2:
                    self.spellCurrentItem(wordString)
                elif speechType == 3:
                    self.phoneticSpellCurrentItem(wordString)
                elif speechType == 1:
                    wordString = self.utilities.adjustForRepeats(wordString)
                    speech.speak(wordString)

        self.updateBrailleReview(targetCursorCell)
        self.currentReviewContents = wordString

        return True

    def reviewCurrentAccessible(self, inputEvent):
        context = self.getFlatReviewContext()
        [zoneString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.ZONE)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            utterances = self.speechGenerator.generateSpeech(
                    context.getCurrentAccessible())
            utterances.extend(self.tutorialGenerator.getTutorial(
                    context.getCurrentAccessible(), False))
            speech.speak(utterances)
        return True

    def reviewPreviousItem(self, inputEvent):
        """Moves the flat review context to the previous item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.WORD,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewNextItem(self, inputEvent):
        """Moves the flat review context to the next item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.WORD,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewCurrentCharacter(self, inputEvent):
        """Brailles and speaks the current flat review character."""

        self._reviewCurrentCharacter(inputEvent, 1)

        return True

    def reviewSpellCurrentCharacter(self, inputEvent):
        """Brailles and 'spells' (phonetically) the current flat review
        character.
        """

        self._reviewCurrentCharacter(inputEvent, 2)

        return True

    def reviewUnicodeCurrentCharacter(self, inputEvent):
        """Brailles and speaks unicode information about the current flat
        review character.
        """

        self._reviewCurrentCharacter(inputEvent, 3)

        return True

    def _reviewCurrentCharacter(self, inputEvent, speechType=1):
        """Presents the current flat review character via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - speechType - the desired presentation:
                       speak (1),
                       phonetic (2)
                       unicode value information (3)
        """

        context = self.getFlatReviewContext()

        [charString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.CHAR)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not charString) or (not len(charString)):
                speech.speak(messages.BLANK)
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n" and speechType != 3:
                    speech.speak(messages.BLANK)
                elif speechType == 3:
                    self.speakUnicodeCharacter(charString)
                elif speechType == 2:
                    self.phoneticSpellCurrentItem(charString)
                else:
                    self.speakCharacter(charString)

        self.updateBrailleReview()
        self.currentReviewContents = charString

        return True

    def reviewPreviousCharacter(self, inputEvent):
        """Moves the flat review context to the previous character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.CHAR,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewEndOfLine(self, inputEvent):
        """Moves the flat review context to the end of the line.  Places
        the flat review cursor at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd(flat_review.Context.LINE)

        self.reviewCurrentCharacter(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewNextCharacter(self, inputEvent):
        """Moves the flat review context to the next character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.CHAR,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewAbove(self, inputEvent):
        """Moves the flat review context to the character most directly
        above the current flat review cursor.  Places the flat review
        cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goAbove(flat_review.Context.CHAR,
                                flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def reviewBelow(self, inputEvent):
        """Moves the flat review context to the character most directly
        below the current flat review cursor.  Places the flat review
        cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goBelow(flat_review.Context.CHAR,
                                flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def reviewCurrentLine(self, inputEvent):
        """Brailles and speaks the current flat review line."""

        self._reviewCurrentLine(inputEvent, 1)

        return True

    def reviewSpellCurrentLine(self, inputEvent):
        """Brailles and spells the current flat review line."""

        self._reviewCurrentLine(inputEvent, 2)

        return True

    def reviewPhoneticCurrentLine(self, inputEvent):
        """Brailles and phonetically spells the current flat review line."""

        self._reviewCurrentLine(inputEvent, 3)

        return True

    def _reviewCurrentLine(self, inputEvent, speechType=1):
        """Presents the current flat review line via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - speechType - the desired presentation: speak (1), spell (2), or
                       phonetic (3)
        """

        context = self.getFlatReviewContext()

        [lineString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.LINE)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not lineString) \
               or (not len(lineString)) \
               or (lineString == "\n"):
                speech.speak(messages.BLANK)
            elif lineString.isspace():
                speech.speak(messages.WHITE_SPACE)
            elif lineString.isupper() \
                 and (speechType < 2 or speechType > 3):
                speech.speak(lineString, self.voices[settings.UPPERCASE_VOICE])
            elif speechType == 2:
                self.spellCurrentItem(lineString)
            elif speechType == 3:
                self.phoneticSpellCurrentItem(lineString)
            else:
                lineString = self.utilities.adjustForRepeats(lineString)
                speech.speak(lineString)

        self.updateBrailleReview()
        self.currentReviewContents = lineString

        return True

    def reviewPreviousLine(self, inputEvent):
        """Moves the flat review context to the beginning of the
        previous line."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.LINE,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentLine(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewHome(self, inputEvent):
        """Moves the flat review context to the top left of the current
        window."""

        context = self.getFlatReviewContext()

        context.goBegin()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewNextLine(self, inputEvent):
        """Moves the flat review context to the beginning of the
        next line.  Places the flat review cursor at the beginning
        of the line."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.LINE,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentLine(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewBottomLeft(self, inputEvent):
        """Moves the flat review context to the beginning of the
        last line in the window.  Places the flat review cursor at
        the beginning of the line."""

        context = self.getFlatReviewContext()

        context.goEnd(flat_review.Context.WINDOW)
        context.goBegin(flat_review.Context.LINE)
        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewEnd(self, inputEvent):
        """Moves the flat review context to the end of the
        last line in the window.  Places the flat review cursor
        at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewCurrentItem(self, inputEvent, targetCursorCell=0):
        """Brailles and speaks the current item to the user."""

        self._reviewCurrentItem(inputEvent, targetCursorCell, 1)

        return True

    def reviewSpellCurrentItem(self, inputEvent, targetCursorCell=0):
        """Brailles and spells the current item to the user."""

        self._reviewCurrentItem(inputEvent, targetCursorCell, 2)

        return True

    def reviewPhoneticCurrentItem(self, inputEvent, targetCursorCell=0):
        """Brailles and phonetically spells the current item to the user."""

        self._reviewCurrentItem(inputEvent, targetCursorCell, 3)

        return True

    def flatReviewCopy(self, inputEvent):
        """Copies the contents of the item under flat review to and places
        them in the clipboard."""

        if self.flatReviewContext:
            clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
            clipboard.set_text(
                self.currentReviewContents, len(self.currentReviewContents))
            self.presentMessage(messages.FLAT_REVIEW_COPIED)
        else:
            self.presentMessage(messages.FLAT_REVIEW_NOT_IN)

        return True

    def _appendToClipboard(self, clipboard, text, newText):
        """Appends newText to text and places the results in the 
        clipboard."""

        text = text.rstrip("\n")
        text = "%s\n%s" % (text, newText)
        if clipboard:
            clipboard.set_text(text, len(text))

        return True

    def flatReviewAppend(self, inputEvent):
        """Appends the contents of the item under flat review to
        the clipboard."""

        if self.flatReviewContext:
            clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
            clipboard.request_text(
                self._appendToClipboard, self.currentReviewContents)
            self.presentMessage(messages.FLAT_REVIEW_APPENDED)
        else:
            self.presentMessage(messages.FLAT_REVIEW_NOT_IN)

        return True

    def sayAll(self, inputEvent, obj=None, offset=None):
        try:
            clickCount = inputEvent.getClickCount()
        except:
            clickCount = 1
        doubleClick = clickCount == 2

        if doubleClick:
            # Try to "say all" for the current dialog/window by flat
            # reviewing everything. See bug #354462 for more details.
            #
            context = self.getFlatReviewContext()

            utterances = []
            context.goBegin()
            while True:
                [wordString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.ZONE)

                utterances.append(wordString)

                moved = context.goNext(flat_review.Context.ZONE,
                                       flat_review.Context.WRAP_LINE)

                if not moved:
                    break

            speech.speak(utterances)
            return

        obj = obj or orca_state.locusOfFocus
        try:
            text = obj.queryText()
        except NotImplementedError:
            utterances = self.speechGenerator.generateSpeech(obj)
            utterances.extend(self.tutorialGenerator.getTutorial(obj, False))
            speech.speak(utterances)
        except AttributeError:
            pass
        else:
            if offset == None:
                offset = text.caretOffset
            speech.sayAll(self.textLines(obj, offset),
                          self.__sayAllProgressCallback)

        return True

    def toggleFlatReviewMode(self, inputEvent=None):
        """Toggles between flat review mode and focus tracking mode."""

        verbosity = _settingsManager.getSetting('speechVerbosityLevel')
        if self.flatReviewContext:
            if inputEvent and verbosity != settings.VERBOSITY_LEVEL_BRIEF:
                self.presentMessage(messages.FLAT_REVIEW_STOP)
            self.flatReviewContext = None
            self.updateBraille(orca_state.locusOfFocus)
        else:
            if inputEvent and verbosity != settings.VERBOSITY_LEVEL_BRIEF:
                self.presentMessage(messages.FLAT_REVIEW_START)
            context = self.getFlatReviewContext()
            [wordString, x, y, width, height] = \
                     context.getCurrent(flat_review.Context.WORD)
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def toggleSilenceSpeech(self, inputEvent=None):
        """Toggle the silencing of speech.

        Returns True to indicate the input event has been consumed.
        """
        speech.stop()
        if _settingsManager.getSetting('silenceSpeech'):
            _settingsManager.setSetting('silenceSpeech', False)
            self.presentMessage(messages.SPEECH_ENABLED)
        elif not _settingsManager.getSetting('enableSpeech'):
            _settingsManager.setSetting('enableSpeech', True)
            speech.init()
            self.presentMessage(messages.SPEECH_ENABLED)
        else:
            self.presentMessage(messages.SPEECH_DISABLED)
            _settingsManager.setSetting('silenceSpeech', True)
        return True

    def toggleSpeechVerbosity(self, inputEvent=None):
        """Toggles speech verbosity level between verbose and brief."""

        value = _settingsManager.getSetting('speechVerbosityLevel')
        if value == settings.VERBOSITY_LEVEL_BRIEF:
            self.presentMessage(messages.SPEECH_VERBOSITY_VERBOSE)
            _settingsManager.setSetting(
                'speechVerbosityLevel', settings.VERBOSITY_LEVEL_VERBOSE)
        else:
            self.presentMessage(messages.SPEECH_VERBOSITY_BRIEF)
            _settingsManager.setSetting(
                'speechVerbosityLevel', settings.VERBOSITY_LEVEL_BRIEF)

        return True

    def toggleSpeakingIndentationJustification(self, inputEvent=None):
        """Toggles the speaking of indentation and justification."""

        value = _settingsManager.getSetting('enableSpeechIndentation')
        _settingsManager.setSetting('enableSpeechIndentation', not value)
        if _settingsManager.getSetting('enableSpeechIndentation'):
            full = messages.INDENTATION_JUSTIFICATION_ON_FULL
            brief = messages.INDENTATION_JUSTIFICATION_ON_BRIEF
        else:
            full = messages.INDENTATION_JUSTIFICATION_OFF_FULL
            brief = messages.INDENTATION_JUSTIFICATION_OFF_BRIEF
        self.presentMessage(full, brief)

        return True

    def cycleSpeakingPunctuationLevel(self, inputEvent=None):
        """ Cycle through the punctuation levels for speech. """

        currentLevel = _settingsManager.getSetting('verbalizePunctuationStyle')
        if currentLevel == settings.PUNCTUATION_STYLE_NONE:
            newLevel = settings.PUNCTUATION_STYLE_SOME
            full = messages.PUNCTUATION_SOME_FULL
            brief = messages.PUNCTUATION_SOME_BRIEF
        elif currentLevel == settings.PUNCTUATION_STYLE_SOME:
            newLevel = settings.PUNCTUATION_STYLE_MOST
            full = messages.PUNCTUATION_MOST_FULL
            brief = messages.PUNCTUATION_MOST_BRIEF
        elif currentLevel == settings.PUNCTUATION_STYLE_MOST:
            newLevel = settings.PUNCTUATION_STYLE_ALL
            full = messages.PUNCTUATION_ALL_FULL
            brief = messages.PUNCTUATION_ALL_BRIEF
        else:
            newLevel = settings.PUNCTUATION_STYLE_NONE
            full = messages.PUNCTUATION_NONE_FULL
            brief = messages.PUNCTUATION_NONE_BRIEF

        _settingsManager.setSetting('verbalizePunctuationStyle', newLevel)
        self.presentMessage(full, brief)
        speech.updatePunctuationLevel()
        return True

    def cycleSettingsProfile(self, inputEvent=None):
        """Cycle through the user's existing settings profiles."""

        profiles = _settingsManager.availableProfiles()
        if not (profiles and profiles[0]):
            self.presentMessage(messages.PROFILE_NOT_FOUND)
            return True

        isMatch = lambda x: x[1] == _settingsManager.getProfile()
        current = list(filter(isMatch, profiles))[0]
        try:
            name, profileID = profiles[profiles.index(current) + 1]
        except IndexError:
            name, profileID = profiles[0]

        _settingsManager.setProfile(profileID, updateLocale=True)

        # TODO: The right fix is to go find each and every case where we use
        # self.voices directly and instead get the voices from the Settings
        # Manager. But that's too big a change too close to code freeze. So
        # for now we'll hack.
        self.voices = _settingsManager.getSetting('voices')

        # TODO: This is another "too close to code freeze" hack to cause the
        # command names to be presented in the correct language.
        self.setupInputEventHandlers()

        self.presentMessage(messages.PROFILE_CHANGED % name, name)
        return True

    def cycleCapitalizationStyle(self, inputEvent=None):
        """ Cycle through the speech-dispatcher capitalization styles. """

        currentStyle = _settingsManager.getSetting('capitalizationStyle')
        if currentStyle == settings.CAPITALIZATION_STYLE_NONE:
            newStyle = settings.CAPITALIZATION_STYLE_SPELL
            full = messages.CAPITALIZATION_SPELL_FULL
            brief = messages.CAPITALIZATION_SPELL_BRIEF
        elif currentStyle == settings.CAPITALIZATION_STYLE_SPELL:
            newStyle = settings.CAPITALIZATION_STYLE_ICON
            full = messages.CAPITALIZATION_ICON_FULL
            brief = messages.CAPITALIZATION_ICON_BRIEF
        else:
            newStyle = settings.CAPITALIZATION_STYLE_NONE
            full = messages.CAPITALIZATION_NONE_FULL
            brief = messages.CAPITALIZATION_NONE_BRIEF

        _settingsManager.setSetting('capitalizationStyle', newStyle)
        self.presentMessage(full, brief)
        speech.updateCapitalizationStyle()
        return True

    def cycleKeyEcho(self, inputEvent=None):
        (newKey, newWord, newSentence) = (False, False, False)
        key = _settingsManager.getSetting('enableKeyEcho')
        word = _settingsManager.getSetting('enableEchoByWord')
        sentence = _settingsManager.getSetting('enableEchoBySentence')

        if (key, word, sentence) == (False, False, False):
            (newKey, newWord, newSentence) = (True, False, False)
            full = messages.KEY_ECHO_KEY_FULL
            brief = messages.KEY_ECHO_KEY_BRIEF
        elif (key, word, sentence) == (True, False, False):
            (newKey, newWord, newSentence) = (False, True, False)
            full = messages.KEY_ECHO_WORD_FULL
            brief = messages.KEY_ECHO_WORD_BRIEF
        elif (key, word, sentence) == (False, True, False):
            (newKey, newWord, newSentence) = (False, False, True)
            full = messages.KEY_ECHO_SENTENCE_FULL
            brief = messages.KEY_ECHO_SENTENCE_BRIEF
        elif (key, word, sentence) == (False, False, True):
            (newKey, newWord, newSentence) = (True, True, False)
            full = messages.KEY_ECHO_KEY_AND_WORD_FULL
            brief = messages.KEY_ECHO_KEY_AND_WORD_BRIEF
        elif (key, word, sentence) == (True, True, False):
            (newKey, newWord, newSentence) = (False, True, True)
            full = messages.KEY_ECHO_WORD_AND_SENTENCE_FULL
            brief = messages.KEY_ECHO_WORD_AND_SENTENCE_BRIEF
        else:
            (newKey, newWord, newSentence) = (False, False, False)
            full = messages.KEY_ECHO_NONE_FULL
            brief = messages.KEY_ECHO_NONE_BRIEF

        _settingsManager.setSetting('enableKeyEcho', newKey)
        _settingsManager.setSetting('enableEchoByWord', newWord)
        _settingsManager.setSetting('enableEchoBySentence', newSentence)
        self.presentMessage(full, brief)
        return True

    def toggleTableCellReadMode(self, inputEvent=None):
        """Toggles an indicator for whether we should just read the current
        table cell or read the whole row."""

        speakRow = _settingsManager.getSetting('readTableCellRow')
        _settingsManager.setSetting('readTableCellRow', not speakRow)
        if not speakRow:
            line = messages.TABLE_MODE_ROW
        else:
            line = messages.TABLE_MODE_CELL

        self.presentMessage(line)

        return True

    def doWhereAmI(self, inputEvent, basicOnly):
        """Peforms the whereAmI operation.

        Arguments:
        - inputEvent:     The original inputEvent
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)

        return self.whereAmI.whereAmI(obj, basicOnly)

    def whereAmIBasic(self, inputEvent):
        """Speaks basic information about the current object of interest.
        """

        self.doWhereAmI(inputEvent, True)

    def whereAmIDetailed(self, inputEvent):
        """Speaks detailed/custom information about the current object of
        interest.
        """

        self.doWhereAmI(inputEvent, False)

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
        except:
            levelIndex = 0
        else:
            if levelIndex >= len(levels):
                levelIndex = 0

        debug.debugLevel = levels[levelIndex]
        briefMessage = levels[levelIndex + 1]
        fullMessage =  "Debug level %s." % briefMessage
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

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if self.findCommandRun:
            self.findCommandRun = False
            self.find()

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not event.any_data:
            return

        if not event.source.getState().contains(pyatspi.STATE_FOCUSED) \
           and not event.any_data.getState().contains(pyatspi.STATE_FOCUSED):
            return

        if self.stopSpeechOnActiveDescendantChanged(event):
            speech.stop()

        orca.setLocusOfFocus(event, event.any_data)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""
        pass

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            return
 
        # Radio buttons normally change their state when you arrow to them,
        # so we handle the announcement of their state changes in the focus
        # handling code.  However, we do need to handle radio buttons where
        # the user needs to press the space key to select them.
        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            eventString, mods = self.utilities.lastKeyAndModifiers()
            if not eventString in [" ", "space"]:
                return

        oldObj, oldState = self.pointOfReference.get('checkedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return
 
        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['checkedChange'] = hash(obj), event.detail1

    def onChildrenChanged(self, event):
        """Called when a child node has changed.

        Arguments:
        - event: the Event
        """
        pass

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        if not orca_state.locusOfFocus:
            return

        obj, offset = self.pointOfReference.get("lastCursorPosition", (None, -1))
        if offset == event.detail1 \
           and self.utilities.isSameObject(obj, event.source):
            return

        # Should the event source be the locusOfFocus?
        #
        try:
            role = orca_state.locusOfFocus.getRole()
        except (LookupError, RuntimeError):
            role = None
        if role in [pyatspi.ROLE_FRAME, pyatspi.ROLE_DIALOG]:
            frameApp = orca_state.locusOfFocus.getApplication()
            eventApp = event.source.getApplication()
            if frameApp == eventApp \
               and event.source.getState().contains(pyatspi.STATE_FOCUSED):
                orca.setLocusOfFocus(event, event.source, False)

        # Ignore caret movements from non-focused objects, unless the
        # currently focused object is the parent of the object which
        # has the caret.
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        # We always automatically go back to focus tracking mode when
        # the caret moves in the focused object.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        text = event.source.queryText()
        self._saveLastCursorPosition(event.source, text.caretOffset)
        if text.getNSelections():
            return

        self._presentTextAtNewCaretPosition(event)

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        pass

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        pass

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        pass

    def onExpandedChanged(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        obj = event.source
        role = obj.getRole()
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus) \
           and not role in [pyatspi.ROLE_TABLE_ROW, pyatspi.ROLE_COMBO_BOX]:
            return

        oldObj, oldState = self.pointOfReference.get('expandedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['expandedChange'] = hash(obj), event.detail1

    def onIndeterminateChanged(self, event):
        """Callback for object:state-changed:indeterminate accessibility events."""

        # If this state is cleared, the new state will become checked or unchecked
        # and we should get object:state-changed:checked events for those cases.
        # Therefore, if the state is not now indeterminate/partially checked,
        # ignore this event.
        if not event.detail1:
            return

        obj = event.source
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        oldObj, oldState = self.pointOfReference.get('indeterminateChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['indeterminateChange'] = hash(obj), event.detail1

    def onMouseButton(self, event):
        """Called whenever the user presses or releases a mouse button.

        Arguments:
        - event: the Event
        """

        mouseEvent = input_event.MouseButtonEvent(event)
        orca_state.lastInputEvent = mouseEvent

        if mouseEvent.pressed:
            speech.stop()
            return

        # If we've received a mouse button released event, then check if
        # there are and text selections for the locus of focus and speak
        # them.
        #
        obj = orca_state.locusOfFocus
        try:
            text = obj.queryText()
        except:
            return

        self.updateBraille(orca_state.locusOfFocus)
        textContents = self.utilities.allSelectedText(obj)[0]
        if not textContents:
            return

        utterances = []
        utterances.append(textContents)
        utterances.append(messages.TEXT_SELECTED)
        speech.speak(utterances)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        obj = event.source
        names = self.pointOfReference.get('names', {})
        oldName = names.get(hash(obj))
        if oldName == event.any_data:
            return

        # We are ignoring name changes in comboboxes that have focus
        # see bgo#617204
        role = obj.getRole()
        if role == pyatspi.ROLE_COMBO_BOX:
            return

        # Table cell accessibles in trees are often reused. When this occurs,
        # we get name-changed events when the selection changes.
        if role == pyatspi.ROLE_TABLE_CELL:
            return

        # Normally, we only care about name changes in the current object.
        # But with the new GtkHeaderBar, we are seeing instances where the
        # real frame remains the same, but the functional frame changes
        # e.g. g-c-c going from all settings to a specific panel.
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            if role != pyatspi.ROLE_FRAME \
               or not obj.getState().contains(pyatspi.STATE_ACTIVE):
                return

        names[hash(obj)] = event.any_data
        self.pointOfReference['names'] = names
        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))

    def onPressedChanged(self, event):
        """Callback for object:state-changed:pressed accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        oldObj, oldState = self.pointOfReference.get('pressedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['pressedChange'] = hash(obj), event.detail1

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        obj = event.source
        state = obj.getState()
        if not state.contains(pyatspi.STATE_FOCUSED):
            return

        if not self.utilities.isSameObject(orca_state.locusOfFocus, obj):
            return

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return

        isSelected = state.contains(pyatspi.STATE_SELECTED)
        announceState = False
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if keyString == "space":
            announceState = True
        elif keyString in ["Down", "Up"] \
             and isSelected and obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            announceState = True

        if not announceState:
            return

        # TODO - JD: Unlike the other state-changed callbacks, it seems unwise
        # to call generateSpeech() here because that also will present the
        # expandable state if appropriate for the object type. The generators
        # need to gain some smarts w.r.t. state changes.

        voice = self.voices.get(settings.SYSTEM_VOICE)
        if event.detail1:
            speech.speak(messages.TEXT_SELECTED, voice, False)
        else:
            speech.speak(messages.TEXT_UNSELECTED, voice, False)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        obj = event.source
        state = obj.getState()
        if state.contains(pyatspi.STATE_MANAGES_DESCENDANTS):
            return

        # TODO - JD: We need to give more thought to where we look to this
        # event and where we prefer object:state-changed:selected.

        # If the current item's selection is toggled, we'll present that
        # via the state-changed event.
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if keyString == "space":
            return
 
        # Save the event source, if it is a menu or combo box. It will be
        # useful for optimizing componentAtDesktopCoords in the case that
        # the pointer is hovering over a menu item. The alternative is to
        # traverse the application's tree looking for potential moused-over
        # menu items.
        if obj.getRole() in (pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_MENU):
            self.lastSelectedMenu = obj

        selectedChildren = self.utilities.selectedChildren(obj)
        for child in selectedChildren:
            if not self.utilities.isLayoutOnly(child):
                orca.setLocusOfFocus(event, child)
                break

    def onSensitiveChanged(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""
        pass

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        pass

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        obj = event.source
        state = obj.getState()
        if not state.contains(pyatspi.STATE_FOCUSED):
            return

        window = self.utilities.topLevelObject(obj)
        if window:
            try:
                iconified = window.getState().contains(pyatspi.STATE_ICONIFIED)
            except:
                return

            if iconified:
                return

        if obj and obj.childCount and obj.getRole() != pyatspi.ROLE_COMBO_BOX:
            selectedChildren = self.utilities.selectedChildren(obj)
            if selectedChildren:
                obj = selectedChildren[0]

        orca.setLocusOfFocus(event, obj)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        obj = event.source
        role = obj.getRole()
        if role == pyatspi.ROLE_NOTIFICATION:
            speech.speak(self.speechGenerator.generateSpeech(obj))
            visibleOnly = not self.utilities.isStatusBarNotification(obj)
            labels = self.utilities.unrelatedLabels(obj, visibleOnly)
            msg = ''.join(map(self.utilities.displayedText, labels))
            self.displayBrailleMessage(msg, flashTime=settings.brailleFlashTime)
            notification_messages.saveMessage(msg)
            return

        if role == pyatspi.ROLE_TOOL_TIP:
            keyString, mods = self.utilities.lastKeyAndModifiers()
            if keyString != "F1" \
               and not _settingsManager.getSetting('presentToolTips'):
                return
            if event.detail1:
                self.presentToolTip(obj)
                return
 
            if orca_state.locusOfFocus and keyString == "F1":
                obj = orca_state.locusOfFocus
                self.updateBraille(obj)
                speech.speak(self.speechGenerator.generateSpeech(obj))
                return

    def onTextAttributesChanged(self, event):
        """Called when an object's text attributes change. Right now this
        method is only to handle the presentation of spelling errors on
        the fly. Also note that right now, the Gecko toolkit is the only
        one to present this information to us.

        Arguments:
        - event: the Event
        """

        verbosity = _settingsManager.getSetting('speechVerbosityLevel')
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE \
           and self.utilities.isSameObject(
                event.source, orca_state.locusOfFocus):
            try:
                text = event.source.queryText()
            except:
                return

            # If the misspelled word indicator has just appeared, it's
            # because the user typed a word boundary or navigated out
            # of the word. We don't want to have to store a full set of
            # each object's text attributes to compare, therefore, we'll
            # check the previous word (most likely case) and the next
            # word with respect to the current position.
            #
            offset = text.caretOffset
            if not text.getText(offset, offset+1).isalnum():
                offset -= 1
            if self.utilities.isWordMisspelled(event.source, offset-1) \
               or self.utilities.isWordMisspelled(event.source, offset+1):
                self.speakMessage(messages.MISSPELLED)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        role = event.source.getRole()
        state = event.source.getState()
        if role == pyatspi.ROLE_PASSWORD_TEXT and state.contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source, False)

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        # We'll also ignore sliders because we get their output via
        # their values changing.
        #
        if role == pyatspi.ROLE_SLIDER:
            return

        # [[[NOTE: WDW - if we handle events synchronously, we'll
        # be looking at the text object *before* the text was
        # actually removed from the object.  If we handle events
        # asynchronously, we'll be looking at the text object
        # *after* the text was removed.  The importance of knowing
        # this is that the output will differ depending upon how
        # orca.settings.asyncMode has been set.  For example, the
        # regression tests run in synchronous mode, so the output
        # they see will not be the same as what the user normally
        # experiences.]]]

        self.updateBraille(event.source)

        # The any_data member of the event object has the deleted text in
        # it - If the last key pressed was a backspace or delete key,
        # speak the deleted text.  [[[TODO: WDW - again, need to think
        # about the ramifications of this when it comes to editors such
        # as vi or emacs.
        #
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if not keyString:
            return

        text = event.source.queryText()
        if keyString == "BackSpace":
            # Speak the character that has just been deleted.
            #
            character = event.any_data

        elif keyString == "Delete" \
             or (keyString == "D" and mods & keybindings.CTRL_MODIFIER_MASK):
            # Speak the character to the right of the caret after
            # the current right character has been deleted.
            #
            offset = text.caretOffset
            [character, startOffset, endOffset] = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)

        else:
            return

        if len(character) == 1:
            self.speakCharacter(character)
            return

        if self.utilities.linkIndex(event.source, text.caretOffset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif character.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        # We won't interrupt what else might be being spoken
        # right now because it is typically something else
        # related to this event.
        #
        speech.speak(character, voice, False)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        role = event.source.getRole()
        state = event.source.getState()
        if role == pyatspi.ROLE_PASSWORD_TEXT and state.contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source, False)

        # Ignore text insertions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was inserted.
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        ignoreRoles = [pyatspi.ROLE_LABEL,
                       pyatspi.ROLE_MENU,
                       pyatspi.ROLE_MENU_ITEM,
                       pyatspi.ROLE_SLIDER,
                       pyatspi.ROLE_SPIN_BUTTON]
        if role in ignoreRoles:
            return

        if role == pyatspi.ROLE_TABLE_CELL \
           and not state.contains(pyatspi.STATE_FOCUSED) \
           and not state.contains(pyatspi.STATE_SELECTED):
            return

        self.updateBraille(event.source)

        # If the last input event was a keyboard event, check to see if
        # the text for this event matches what the user typed. If it does,
        # then don't speak it.
        #
        # Note that the text widgets sometimes compress their events,
        # thus we might get a longer string from a single text inserted
        # event, while we also get individual keyboard events for the
        # characters used to type the string.  This is ugly.  We attempt
        # to handle it here by only echoing text if we think it was the
        # result of a command (e.g., a paste operation).
        #
        # Note that we have to special case the space character as it
        # comes across as "space" in the keyboard event and " " in the
        # text event.
        #
        string = event.any_data
        speakThis = False
        wasCommand = False
        wasAutoComplete = False
        if isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent):
            speakThis = orca_state.lastInputEvent.button == "2"
        else:
            keyString, mods = self.utilities.lastKeyAndModifiers()
            wasCommand = mods & keybindings.COMMAND_MODIFIER_MASK
            if not wasCommand and keyString in ["Return", "Tab", "space"] \
               and role == pyatspi.ROLE_TERMINAL \
               and event.any_data.strip():
                wasCommand = True
            try:
                selections = event.source.queryText().getNSelections()
            except:
                selections = 0

            if selections:
                wasAutoComplete = role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_ENTRY]

            if (string == " " and keyString == "space") or string == keyString:
                pass
            elif wasCommand or wasAutoComplete:
                speakThis = True
            elif role == pyatspi.ROLE_PASSWORD_TEXT \
                 and _settingsManager.getSetting('enableKeyEcho') \
                 and _settingsManager.getSetting('enablePrintableKeys'):
                # Echoing "star" is preferable to echoing the descriptive
                # name of the bullet that has appeared (e.g. "black circle")
                #
                string = "*"
                speakThis = True

        # Auto-completed, auto-corrected, auto-inserted, etc.
        #
        speakThis = speakThis or self.utilities.isAutoTextEvent(event)

        # We might need to echo this if it is a single character.
        #
        speakThis = speakThis \
                    or (_settingsManager.getSetting('enableEchoByCharacter') \
                        and string \
                        and role != pyatspi.ROLE_PASSWORD_TEXT \
                        and len(string.strip()) == 1)

        if speakThis:
            if string.isupper():
                speech.speak(string, self.voices[settings.UPPERCASE_VOICE])
            elif not string.isalnum():
                self.speakCharacter(string)
            else:
                speech.speak(string)

        if wasCommand:
            return

        if wasAutoComplete:
            self.pointOfReference['lastAutoComplete'] = hash(event.source)

        try:
            text = event.source.queryText()
        except NotImplementedError:
            return

        offset = text.caretOffset - 1
        previousOffset = offset - 1
        if (offset < 0 or previousOffset < 0):
            return

        [currentChar, startOffset, endOffset] = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        [previousChar, startOffset, endOffset] = \
            text.getTextAtOffset(previousOffset, pyatspi.TEXT_BOUNDARY_CHAR)

        if _settingsManager.getSetting('enableEchoBySentence') \
           and self.utilities.isSentenceDelimiter(currentChar, previousChar):
            self.echoPreviousSentence(event.source)

        elif _settingsManager.getSetting('enableEchoByWord') \
             and self.utilities.isWordDelimiter(currentChar):
            self.echoPreviousWord(event.source)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        self.updateBraille(obj)

        # Note: This guesswork to figure out what actually changed with respect
        # to text selection will get eliminated once the new text-selection API
        # is added to ATK and implemented by the toolkits. (BGO 638378)

        textSelections = self.pointOfReference.get('textSelections', {})
        oldStart, oldEnd = textSelections.get(hash(obj), (0, 0))

        # TODO: JD - this doesn't yet handle the case of multiple non-contiguous
        # selections in a single accessible object.

        text = obj.queryText()
        newStart, newEnd = text.getSelection(0)
        textSelections[hash(obj)] = newStart, newEnd
        self.pointOfReference['textSelections'] = textSelections

        if self.pointOfReference.get('lastAutoComplete') == hash(obj):
            return

        nSelections = text.getNSelections()
        handled = self._speakTextSelectionState(nSelections)
        if handled:
            return

        changes = []
        oldChars = set(range(oldStart, oldEnd))
        newChars = set(range(newStart, newEnd))
        if not oldChars.union(newChars):
            return

        if oldChars and newChars and not oldChars.intersection(newChars):
            # A simultaneous unselection and selection centered at one offset.
            changes.append([oldStart, oldEnd, messages.TEXT_UNSELECTED])
            changes.append([newStart, newEnd, messages.TEXT_SELECTED])
        else:
            change = sorted(oldChars.symmetric_difference(newChars))
            if not change:
                return

            changeStart, changeEnd = change[0], change[-1] + 1
            if oldChars < newChars:
                changes.append([changeStart, changeEnd, messages.TEXT_SELECTED])
            else:
                changes.append([changeStart, changeEnd, messages.TEXT_UNSELECTED])

        speakMessage = not _settingsManager.getSetting('onlySpeakDisplayedText')
        for start, end, message in changes:
            self.sayPhrase(obj, start, end)
            if speakMessage:
                self.speakMessage(message, interrupt=False)

    def onColumnReordered(self, event):
        """Called whenever the columns in a table are reordered.

        Arguments:
        - event: the Event
        """

        parentTable = self.utilities.ancestorWithRole(
            orca_state.locusOfFocus, [pyatspi.ROLE_TABLE], [pyatspi.ROLE_FRAME])
        if event.source != parentTable:
            return

        self.presentMessage(messages.TABLE_REORDERED_COLUMNS)

    def onRowReordered(self, event):
        """Called whenever the rows in a table are reordered.

        Arguments:
        - event: the Event
        """

        parentTable = self.utilities.ancestorWithRole(
            orca_state.locusOfFocus, [pyatspi.ROLE_TABLE], [pyatspi.ROLE_FRAME])
        if event.source != parentTable:
            return

        self.presentMessage(messages.TABLE_REORDERED_ROWS)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        obj = event.source
        role = obj.getRole()

        value = obj.queryValue()
        if "oldValue" in self.pointOfReference \
           and (value.currentValue == self.pointOfReference["oldValue"]):
            return

        if role == pyatspi.ROLE_PROGRESS_BAR:
            self.handleProgressBarUpdate(event, obj)
            return

        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        self.pointOfReference["oldValue"] = value.currentValue
        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated.

        Arguments:
        - event: the Event
        """

        self.pointOfReference = {}

        self.windowActivateTime = time.time()
        orca.setLocusOfFocus(event, event.source)

        # We keep track of the active window to handle situations where
        # we get window activated and window deactivated events out of
        # order (see onWindowDeactivated).
        #
        # For example, events can be:
        #
        #    window:activate   (w1)
        #    window:activate   (w2)
        #    window:deactivate (w1)
        #
        # as well as:
        #
        #    window:activate   (w1)
        #    window:deactivate (w1)
        #    window:activate   (w2)
        #
        orca_state.activeWindow = event.source

    def onWindowCreated(self, event):
        """Callback for window:create accessibility events."""

        pass

    def onWindowDeactivated(self, event):
        """Called whenever a toplevel window is deactivated.

        Arguments:
        - event: the Event
        """

        self.pointOfReference = {}

        menuRoles = [pyatspi.ROLE_MENU,
                     pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM]

        # If we get into a popup menu, the parent application will likely
        # emit a window-deactivate event. But functionally we're still in
        # the same window. In this case, we do not want to update anything.
        try:
            role = orca_state.locusOfFocus.getRole()
        except:
            pass
        else:
            if role in menuRoles:
                return

        # If we receive a "window:deactivate" event for the object that
        # currently has focus, then stop the current speech output.
        # This is very useful for terminating long speech output from
        # commands running in gnome-terminal.
        #
        if orca_state.locusOfFocus and \
          (orca_state.locusOfFocus.getApplication() == \
             event.source.getApplication()):
            speech.stop()

            # Clear the braille display just in case we are about to give
            # focus to an inaccessible application. See bug #519901 for
            # more details.
            #
            self.clearBraille()

            # Hide the flat review window and reset it so that it will be
            # recreated.
            #
            if self.flatReviewContext:
                self.flatReviewContext = None
                self.updateBraille(orca_state.locusOfFocus)

        # Because window activated and deactivated events may be
        # received in any order when switching from one application to
        # another, locusOfFocus and activeWindow, we really only change
        # the locusOfFocus and activeWindow when we are dealing with
        # an event from the current activeWindow.
        #
        if event.source == orca_state.activeWindow:
            orca.setLocusOfFocus(event, None)
            orca_state.activeWindow = None

        # disable list notification  messages mode
        notification_messages.listNotificationMessagesModeEnabled = False

        # disable learn mode
        orca_state.learnModeEnabled = False

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        """Updates braille and outputs speech for the event.source or the
        otherObj."""

        obj = otherObj or event.source
        text = obj.queryText()

        self.updateBrailleForNewCaretPosition(obj)
        if self._inSayAll:
            return

        if not orca_state.lastInputEvent:
            return

        if isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent):
            if not orca_state.lastInputEvent.pressed:
                self.sayLine(obj)
            return

        # Guess why the caret moved and say something appropriate.
        # [[[TODO: WDW - this motion assumes traditional GUI
        # navigation gestures.  In an editor such as vi, line up and
        # down is done via other actions such as "i" or "j".  We may
        # need to think about this a little harder.]]]
        #
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if not keyString:
            return

        isControlKey = mods & keybindings.CTRL_MODIFIER_MASK

        if keyString in ["Up", "Down"]:
            self.sayLine(obj)

        elif keyString in ["Left", "Right"]:
            if isControlKey:
                self.sayWord(obj)
            else:
                self.sayCharacter(obj)

        elif keyString == "Page_Up":
            # TODO - JD: Why is Control special here?
            # If the user has typed Control-Page_Up, then we
            # speak the character to the right of the current text cursor
            # position otherwise we speak the current line.
            #
            if isControlKey:
                self.sayCharacter(obj)
            else:
                self.sayLine(obj)

        elif keyString == "Page_Down":
            self.sayLine(obj)

        elif keyString in ["Home", "End"]:
            if isControlKey:
                self.sayLine(obj)
            else:
                self.sayCharacter(obj)

    def _rewindSayAll(self, context, minCharCount=10):
        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        index = self._sayAllContexts.index(context)
        self._sayAllContexts = self._sayAllContexts[0:index]
        while self._sayAllContexts:
            context = self._sayAllContexts.pop()
            if context.endOffset - context.startOffset > minCharCount:
                break

        try:
            text = context.obj.queryText()
        except:
            pass
        else:
            orca.setLocusOfFocus(None, context.obj, notifyScript=False)
            text.setCaretOffset(context.startOffset)

        self.sayAll(None, context.obj, context.startOffset)
        return True

    def _fastForwardSayAll(self, context):
        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        try:
            text = context.obj.queryText()
        except:
            pass
        else:
            orca.setLocusOfFocus(None, context.obj, notifyScript=False)
            text.setCaretOffset(context.endOffset)

        self.sayAll(None, context.obj, context.endOffset)
        return True

    def __sayAllProgressCallback(self, context, progressType):
        # [[[TODO: WDW - this needs work.  Need to be able to manage
        # the monitoring of progress and couple that with both updating
        # the visual progress of what is being spoken as well as
        # positioning the cursor when speech has stopped.]]]
        #
        try:
            text = context.obj.queryText()
            char = text.getText(context.currentOffset, context.currentOffset+1)
        except:
            return

        # Setting the caret at the offset of an embedded object results in
        # focus changes.
        if char == self.EMBEDDED_OBJECT_CHARACTER:
            return

        if progressType == speechserver.SayAllContext.PROGRESS:
            return
        elif progressType == speechserver.SayAllContext.INTERRUPTED:
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                self._sayAllIsInterrupted = True
                lastKey = orca_state.lastInputEvent.event_string
                if lastKey == "Down" and self._fastForwardSayAll(context):
                    return
                elif lastKey == "Up" and self._rewindSayAll(context):
                    return

            self._inSayAll = False
            self._sayAllContexts = []
            text.setCaretOffset(context.currentOffset)
        elif progressType == speechserver.SayAllContext.COMPLETED:
            orca.setLocusOfFocus(None, context.obj, notifyScript=False)
            text.setCaretOffset(context.currentOffset)

        # If there is a selection, clear it. See bug #489504 for more details.
        #
        if text.getNSelections():
            text.setSelection(0, context.currentOffset, context.currentOffset)

    def inSayAll(self):
        return self._inSayAll or self._sayAllIsInterrupted

    def echoPreviousSentence(self, obj):
        """Speaks the sentence prior to the caret, as long as there is
        a sentence prior to the caret and there is no intervening sentence
        delimiter between the caret and the end of the sentence.

        The entry condition for this method is that the character
        prior to the current caret position is a sentence delimiter,
        and it's what caused this method to be called in the first
        place.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
        interface.
        """

        try:
            text = obj.queryText()
        except NotImplementedError:
            return

        offset = text.caretOffset - 1
        previousOffset = text.caretOffset - 2
        if (offset < 0 or previousOffset < 0):
            return

        [currentChar, startOffset, endOffset] = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        [previousChar, startOffset, endOffset] = \
            text.getTextAtOffset(previousOffset, pyatspi.TEXT_BOUNDARY_CHAR)
        if not self.utilities.isSentenceDelimiter(currentChar, previousChar):
            return

        # OK - we seem to be cool so far.  So...starting with what
        # should be the last character in the sentence (caretOffset - 2),
        # work our way to the beginning of the sentence, stopping when
        # we hit another sentence delimiter.
        #
        sentenceEndOffset = text.caretOffset - 2
        sentenceStartOffset = sentenceEndOffset

        while sentenceStartOffset >= 0:
            [currentChar, startOffset, endOffset] = \
                text.getTextAtOffset(sentenceStartOffset,
                                     pyatspi.TEXT_BOUNDARY_CHAR)
            [previousChar, startOffset, endOffset] = \
                text.getTextAtOffset(sentenceStartOffset-1,
                                     pyatspi.TEXT_BOUNDARY_CHAR)
            if self.utilities.isSentenceDelimiter(currentChar, previousChar):
                break
            else:
                sentenceStartOffset -= 1

        # If we came across a sentence delimiter before hitting any
        # text, we really don't have a previous sentence.
        #
        # Otherwise, get the sentence.  Remember we stopped when we
        # hit a sentence delimiter, so the sentence really starts at
        # sentenceStartOffset + 1.  getText also does not include
        # the character at sentenceEndOffset, so we need to adjust
        # for that, too.
        #
        if sentenceStartOffset == sentenceEndOffset:
            return
        else:
            sentence = self.utilities.substring(obj, sentenceStartOffset + 1,
                                         sentenceEndOffset + 1)

        if self.utilities.linkIndex(obj, sentenceStartOffset + 1) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif sentence.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        sentence = self.utilities.adjustForRepeats(sentence)
        speech.speak(sentence, voice)

    def echoPreviousWord(self, obj, offset=None):
        """Speaks the word prior to the caret, as long as there is
        a word prior to the caret and there is no intervening word
        delimiter between the caret and the end of the word.

        The entry condition for this method is that the character
        prior to the current caret position is a word delimiter,
        and it's what caused this method to be called in the first
        place.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface.
        - offset: if not None, the offset within the text to use as the
                  end of the word.
        """

        try:
            text = obj.queryText()
        except NotImplementedError:
            return

        if not offset:
            if text.caretOffset == -1:
                offset = text.characterCount
            else:
                offset = text.caretOffset - 1

        if (offset < 0):
            return

        [char, startOffset, endOffset] = \
            text.getTextAtOffset( \
                offset,
                pyatspi.TEXT_BOUNDARY_CHAR)
        if not self.utilities.isWordDelimiter(char):
            return

        # OK - we seem to be cool so far.  So...starting with what
        # should be the last character in the word (caretOffset - 2),
        # work our way to the beginning of the word, stopping when
        # we hit another word delimiter.
        #
        wordEndOffset = offset - 1
        wordStartOffset = wordEndOffset

        while wordStartOffset >= 0:
            [char, startOffset, endOffset] = \
                text.getTextAtOffset( \
                    wordStartOffset,
                    pyatspi.TEXT_BOUNDARY_CHAR)
            if self.utilities.isWordDelimiter(char):
                break
            else:
                wordStartOffset -= 1

        # If we came across a word delimiter before hitting any
        # text, we really don't have a previous word.
        #
        # Otherwise, get the word.  Remember we stopped when we
        # hit a word delimiter, so the word really starts at
        # wordStartOffset + 1.  getText also does not include
        # the character at wordEndOffset, so we need to adjust
        # for that, too.
        #
        if wordStartOffset == wordEndOffset:
            return
        else:
            word = self.utilities.\
                substring(obj, wordStartOffset + 1, wordEndOffset + 1)

        if self.utilities.linkIndex(obj, wordStartOffset + 1) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        word = self.utilities.adjustForRepeats(word)
        speech.speak(word, voice)

    def handleProgressBarUpdate(self, event, obj):
        """Determine whether this progress bar event should be spoken or not.
        It should be spoken if:
        1/ settings.enableProgressBarUpdates is True.
        2/ settings.progressBarVerbosity matches the current location of the
           progress bar.
        3/ The time of this event exceeds the
           settings.progressBarUpdateInterval value.  This value
           indicates the time (in seconds) between potential spoken
           progress bar updates.
        4/ The new value of the progress bar (converted to an integer),
           is different from the last one or equals 100 (i.e complete).

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj:  the Accessible progress bar object.
        """

        if _settingsManager.getSetting('enableProgressBarUpdates'):
            makeAnnouncement = False
            verbosity = _settingsManager.getSetting('progressBarVerbosity')
            if verbosity == settings.PROGRESS_BAR_ALL:
                makeAnnouncement = True
            elif verbosity == settings.PROGRESS_BAR_WINDOW:
                makeAnnouncement = self.utilities.isSameObject(
                    self.utilities.topLevelObject(obj),
                    self.utilities.activeWindow())
            elif orca_state.locusOfFocus:
                makeAnnouncement = self.utilities.isSameObject( \
                    obj.getApplication(),
                    orca_state.locusOfFocus.getApplication())

            if makeAnnouncement:
                currentTime = time.time()

                # Check for defunct progress bars. Get rid of them if they
                # are all defunct. Also find out which progress bar was
                # the most recently updated.
                #
                defunctBars = 0
                mostRecentUpdate = [obj, 0]
                for key, value in list(self.lastProgressBarTime.items()):
                    if value > mostRecentUpdate[1]:
                        mostRecentUpdate = [key, value]
                    try:
                        isDefunct = \
                            key.getState().contains(pyatspi.STATE_DEFUNCT)
                    except:
                        isDefunct = True
                    if isDefunct:
                        defunctBars += 1

                if defunctBars == len(self.lastProgressBarTime):
                    self.lastProgressBarTime = {}
                    self.lastProgressBarValue = {}

                # If this progress bar is not already known, create initial
                # values for it.
                #
                if obj not in self.lastProgressBarTime:
                    self.lastProgressBarTime[obj] = 0.0
                if obj not in self.lastProgressBarValue:
                    self.lastProgressBarValue[obj] = None

                lastProgressBarTime = self.lastProgressBarTime[obj]
                lastProgressBarValue = self.lastProgressBarValue[obj]
                value = obj.queryValue()
                try:
                    if value.maximumValue == value.minimumValue:
                        # This is a busy indicator and not a real progress bar.
                        return
                except:
                    return
                percentValue = int((value.currentValue / \
                    (value.maximumValue - value.minimumValue)) * 100.0)

                if (currentTime - lastProgressBarTime) > \
                      _settingsManager.getSetting('progressBarUpdateInterval') \
                   or percentValue == 100:
                    if lastProgressBarValue != percentValue:
                        utterances = []

                        # There may be cases when more than one progress
                        # bar is updating at the same time in a window.
                        # If this is the case, then speak the index of this
                        # progress bar in the dictionary of known progress
                        # bars, as well as the value. But only speak the
                        # index if this progress bar was not the most
                        # recently updated to prevent chattiness.
                        #
                        if len(self.lastProgressBarTime) > 1:
                            index = 0
                            for key in list(self.lastProgressBarTime.keys()):
                                if key == obj and key != mostRecentUpdate[0]:
                                    label = messages.PROGRESS_BAR_NUMBER % (index + 1)
                                    utterances.append(label)
                                else:
                                    index += 1

                        utterances.extend(self.speechGenerator.generateSpeech(
                            obj, alreadyFocused=True))

                        speech.speak(utterances)

                        self.lastProgressBarTime[obj] = currentTime
                        self.lastProgressBarValue[obj] = percentValue

    def presentToolTip(self, obj):
        """
        Speaks the tooltip for the current object of interest.
        """

        # The tooltip is generally the accessible description. If
        # the description is not set, present the text that is
        # spoken when the object receives keyboard focus.
        #
        speechResult = brailleResult = None
        text = ""
        if obj.description:
            speechResult = brailleResult = obj.description
        else:
            speechResult = self.whereAmI.getWhereAmI(obj, True)
            if speechResult:
                brailleResult = speechResult[0]
        debug.println(debug.LEVEL_FINEST,
                      "presentToolTip: text='%s'" % speechResult)
        if speechResult:
            speech.speak(speechResult)
        if brailleResult:
            self.displayBrailleMessage(brailleResult)

    def sayCharacter(self, obj):
        """Speak the character at the caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        text = obj.queryText()
        offset = text.caretOffset

        # If we have selected text and the last event was a move to the
        # right, then speak the character to the left of where the text
        # caret is (i.e. the selected character).
        #
        eventString, mods = self.utilities.lastKeyAndModifiers()
        if (mods & keybindings.SHIFT_MODIFIER_MASK) \
           and eventString in ["Right", "Down"]:
            offset -= 1

        character, startOffset, endOffset = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        if not character or character == '\r':
            character = "\n"

        if self.utilities.linkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif character.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        speakBlankLines = _settingsManager.getSetting('speakBlankLines')
        debug.println(debug.LEVEL_FINEST, \
            "sayCharacter: char=<%s>, startOffset=%d, " % \
            (character, startOffset))
        debug.println(debug.LEVEL_FINEST, \
            "caretOffset=%d, endOffset=%d, speakBlankLines=%s" % \
            (offset, endOffset, speakBlankLines))

        if character == "\n":
            line = text.getTextAtOffset(max(0, offset),
                                        pyatspi.TEXT_BOUNDARY_LINE_START)
            if not line[0] or line[0] == "\n":
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
            self.speakCharacter(character)

    def sayLine(self, obj):
        """Speaks the line of an AccessibleText object that contains the
        caret, unless the line is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        # Get the AccessibleText interface of the provided object
        #
        [line, caretOffset, startOffset] = self.getTextLineAtCaret(obj)
        debug.println(debug.LEVEL_FINEST, \
            "sayLine: line=<%s>, len=%d, start=%d, " % \
            (line, len(line), startOffset))
        debug.println(debug.LEVEL_FINEST, \
            "caret=%d, speakBlankLines=%s" % \
            (caretOffset, _settingsManager.getSetting('speakBlankLines')))

        if len(line) and line != "\n":
            if line.isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            result = \
              self.speechGenerator.generateTextIndentation(obj, line=line)
            if result:
                self.speakMessage(result[0])
            line = self.utilities.adjustForLinks(obj, line, startOffset)
            line = self.utilities.adjustForRepeats(line)
            speech.speak(line, voice)
        else:
            # Speak blank line if appropriate.
            #
            self.sayCharacter(obj)

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
            if phrase.isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            phrase = self.utilities.adjustForRepeats(phrase)
            speech.speak(phrase, voice)
        else:
            self.sayCharacter(obj)

    def sayWord(self, obj):
        """Speaks the word at the caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        text = obj.queryText()
        offset = text.caretOffset
        lastKey, mods = self.utilities.lastKeyAndModifiers()
        lastWord = self._lastWord

        [word, startOffset, endOffset] = \
            text.getTextAtOffset(offset,
                                 pyatspi.TEXT_BOUNDARY_WORD_START)

        if not word:
            self.sayCharacter(obj)
            return

        # Speak a newline if a control-right-arrow or control-left-arrow
        # was used to cross a line boundary. Handling is different for
        # the two keys since control-right-arrow places the cursor after
        # the last character in a word, but control-left-arrow places
        # the cursor at the beginning of a word.
        #
        if lastKey == "Right" and len(lastWord) > 0:
            lastChar = lastWord[len(lastWord) - 1]
            if lastChar == "\n" and lastWord != word:
                self.speakCharacter("\n")

        if lastKey == "Left" and len(word) > 0:
            lastChar = word[len(word) - 1]
            if lastChar == "\n" and lastWord != word:
                self.speakCharacter("\n")

        if self.utilities.linkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        self.speakMisspelledIndicator(obj, startOffset)

        word = self.utilities.adjustForRepeats(word)
        self._lastWord = word
        speech.speak(word, voice)

    def presentObject(self, obj, offset=0):
        self.updateBraille(obj)
        utterances = self.speechGenerator.generateSpeech(obj)
        speech.speak(utterances)

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

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

        if orca_state.locusOfFocus == event.any_data:
            names = self.pointOfReference.get('names', {})
            oldName = names.get(hash(orca_state.locusOfFocus), '')
            if not oldName or event.any_data.name == oldName:
                return False

        if event.source == orca_state.locusOfFocus == event.any_data.parent:
            return False

        return True

    def getFlatReviewContext(self):
        """Returns the flat review context, creating one if necessary."""

        if not self.flatReviewContext:
            self.flatReviewContext = self.flatReviewContextClass(self)
            self.justEnteredFlatReviewMode = True

            # Remember where the cursor currently was
            # when the user was in focus tracking mode.  We'll try to
            # keep the position the same as we move to characters above
            # and below us.
            #
            self.targetCursorCell = self.getBrailleCursorCell()

        return self.flatReviewContext

    def updateBrailleReview(self, targetCursorCell=0):
        """Obtains the braille regions for the current flat review line
        and displays them on the braille display.  If the targetCursorCell
        is non-0, then an attempt will be made to postion the review cursor
        at that cell.  Otherwise, we will pan in display-sized increments
        to show the review cursor."""

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: update review disabled")
            return

        context = self.getFlatReviewContext()

        [regions, regionWithFocus] = context.getCurrentBrailleRegions()
        if not regions:
            regions = []
            regionWithFocus = None

        line = self.getNewBrailleLine()
        self.addBrailleRegionsToLine(regions, line)
        braille.setLines([line])
        self.setBrailleFocus(regionWithFocus, False)
        if regionWithFocus:
            self.panBrailleToOffset(regionWithFocus.brailleOffset \
                                    + regionWithFocus.cursorOffset)

        if self.justEnteredFlatReviewMode:
            self.refreshBraille(True, self.targetCursorCell)
            self.justEnteredFlatReviewMode = False
        else:
            self.refreshBraille(True, targetCursorCell)

    def _setFlatReviewContextToBeginningOfBrailleDisplay(self):
        """Sets the character of interest to be the first character showing
        at the beginning of the braille display."""

        context = self.getFlatReviewContext()
        [regions, regionWithFocus] = context.getCurrentBrailleRegions()
        for region in regions:
            if ((region.brailleOffset + len(region.string)) \
                   > braille.viewport[0]) \
                and (isinstance(region, braille.ReviewText) \
                     or isinstance(region, braille.ReviewComponent)):
                position = max(region.brailleOffset, braille.viewport[0])
                offset = position - region.brailleOffset
                self.targetCursorCell = region.brailleOffset \
                                        - braille.viewport[0]
                [word, charOffset] = region.zone.getWordAtOffset(offset)
                if word:
                    self.flatReviewContext.setCurrent(
                        word.zone.line.index,
                        word.zone.index,
                        word.index,
                        charOffset)
                else:
                    self.flatReviewContext.setCurrent(
                        region.zone.line.index,
                        region.zone.index,
                        0, # word index
                        0) # character index
                break

    def find(self, query=None):
        """Searches for the specified query.  If no query is specified,
        it searches for the query specified in the Orca Find dialog.

        Arguments:
        - query: The search query to find.
        """

        if not query:
            query = find.getLastQuery()
        if query:
            context = self.getFlatReviewContext()
            location = query.findQuery(context, self.justEnteredFlatReviewMode)
            if not location:
                self.presentMessage(messages.STRING_NOT_FOUND)
            else:
                context.setCurrent(location.lineIndex, location.zoneIndex, \
                                   location.wordIndex, location.charIndex)
                self.reviewCurrentItem(None)
                self.targetCursorCell = self.getBrailleCursorCell()

    def getUnicodeCurrencySymbols(self):
        """Return a list of the unicode currency symbols, populating the list
        if this is the first time that this routine has been called.

        Returns a list of unicode currency symbols.
        """

        if not self._unicodeCurrencySymbols:
            self._unicodeCurrencySymbols = [ \
                '\u0024',     # dollar sign
                '\u00A2',     # cent sign
                '\u00A3',     # pound sign
                '\u00A4',     # currency sign
                '\u00A5',     # yen sign
                '\u0192',     # latin small letter f with hook
                '\u060B',     # afghani sign
                '\u09F2',     # bengali rupee mark
                '\u09F3',     # bengali rupee sign
                '\u0AF1',     # gujarati rupee sign
                '\u0BF9',     # tamil rupee sign
                '\u0E3F',     # thai currency symbol baht
                '\u17DB',     # khmer currency symbol riel
                '\u2133',     # script capital m
                '\u5143',     # cjk unified ideograph-5143
                '\u5186',     # cjk unified ideograph-5186
                '\u5706',     # cjk unified ideograph-5706
                '\u5713',     # cjk unified ideograph-5713
                '\uFDFC',     # rial sign
            ]

            # Add 20A0 (EURO-CURRENCY SIGN) to 20B5 (CEDI SIGN)
            #
            for ordChar in range(ord('\u20A0'), ord('\u20B5') + 1):
                self._unicodeCurrencySymbols.append(chr(ordChar))

        return self._unicodeCurrencySymbols

    def speakMisspeltWord(self, allTokens, badWord):
        """Called by various spell checking routine to speak the misspelt word,
           plus the context that it is being used in.

        Arguments:
        - allTokens: a list of all the words.
        - badWord: the misspelt word.
        """

        # Create an utterance to speak consisting of the misspelt
        # word plus the context where it is used (upto five words
        # to either side of it).
        #
        for i in range(0, len(allTokens)):
            if allTokens[i].startswith(badWord):
                minIndex = i - 5
                if minIndex < 0:
                    minIndex = 0
                maxIndex = i + 5
                if maxIndex > (len(allTokens) - 1):
                    maxIndex = len(allTokens) - 1

                utterances = [messages.MISSPELLED_WORD % badWord]
                contextPhrase = " ".join(allTokens[minIndex:maxIndex+1])
                utterances.append(messages.MISSPELLED_WORD_CONTEXT % contextPhrase)

                # Turn the list of utterances into a string.
                text = " ".join(utterances)
                speech.speak(text)

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
        try:
            text = obj.queryText()
        except:
            self._inSayAll = False
            self._sayAllContexts = []
            return

        self._inSayAll = True
        length = text.characterCount
        if offset == None:
            offset = text.caretOffset

        # Determine the correct "say all by" mode to use.
        #
        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
        if sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = pyatspi.TEXT_BOUNDARY_SENTENCE_START
        elif sayAllStyle == settings.SAYALL_STYLE_LINE:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        else:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START

        # Get the next line of text to read
        #
        done = False
        while not done:
            lastEndOffset = -1
            while offset < length:
                [lineString, startOffset, endOffset] = text.getTextAtOffset(
                    offset, mode)

                # Some applications that don't support sentence boundaries
                # will provide the line boundary results instead; others
                # will return nothing.
                #
                if not lineString:
                    mode = pyatspi.TEXT_BOUNDARY_LINE_START
                    [lineString, startOffset, endOffset] = \
                        text.getTextAtOffset(offset, mode)

                # [[[WDW - HACK: well...gnome-terminal sometimes wants to
                # give us outrageous values back from getTextAtOffset
                # (see http://bugzilla.gnome.org/show_bug.cgi?id=343133),
                # so we try to handle it.]]]
                #
                if startOffset < 0:
                    break

                # [[[WDW - HACK: this is here because getTextAtOffset
                # tends not to be implemented consistently across toolkits.
                # Sometimes it behaves properly (i.e., giving us an endOffset
                # that is the beginning of the next line), sometimes it
                # doesn't (e.g., giving us an endOffset that is the end of
                # the current line).  So...we hack.  The whole 'max' deal
                # is to account for lines that might be a brazillion lines
                # long.]]]
                #
                if endOffset == lastEndOffset:
                    offset = max(offset + 1, lastEndOffset + 1)
                    lastEndOffset = endOffset
                    continue

                lastEndOffset = endOffset
                offset = endOffset

                lineString = \
                    self.utilities.adjustForLinks(obj, lineString, startOffset)
                lineString = self.utilities.adjustForRepeats(lineString)
                if lineString.isupper():
                    voice = settings.voices[settings.UPPERCASE_VOICE]
                else:
                    voice = settings.voices[settings.DEFAULT_VOICE]

                context = speechserver.SayAllContext(
                    obj, lineString, startOffset, endOffset)
                self._sayAllContexts.append(context)
                yield [context, voice]

            moreLines = False
            relations = obj.getRelationSet()
            for relation in relations:
                if relation.getRelationType()  \
                       == pyatspi.RELATION_FLOWS_TO:
                    obj = relation.getTarget(0)

                    try:
                        text = obj.queryText()
                    except NotImplementedError:
                        return

                    length = text.characterCount
                    offset = 0
                    moreLines = True
                    break
            if not moreLines:
                done = True

        self._inSayAll = False
        self._sayAllContexts = []

    def getTextLineAtCaret(self, obj, offset=None, startOffset=None, endOffset=None):
        """To-be-removed. Returns the string, caretOffset, startOffset."""

        try:
            text = obj.queryText()
        except NotImplementedError:
            return ["", 0, 0]

        # The caret might be positioned at the very end of the text area.
        # In these cases, calling text.getTextAtOffset on an offset that's
        # not positioned to a character can yield unexpected results.  In
        # particular, we'll see the Gecko toolkit return a start and end
        # offset of (0, 0), and we'll see other implementations, such as
        # gedit, return reasonable results (i.e., gedit will give us the
        # last line).
        #
        # In order to accommodate the differing behavior of different
        # AT-SPI implementations, we'll make sure we give getTextAtOffset
        # the offset of an actual character.  Then, we'll do a little check
        # to see if that character is a newline - if it is, we'll treat it
        # as the line.
        #
        if text.caretOffset == text.characterCount:
            caretOffset = max(0, text.caretOffset - 1)
            character = text.getText(caretOffset, caretOffset + 1)
        else:
            caretOffset = text.caretOffset
            character = None

        if (text.caretOffset == text.characterCount) \
            and (character == "\n"):
            lineString = ""
            startOffset = caretOffset
        else:
            # Get the line containing the caret.  [[[TODO: HACK WDW - If
            # there's only 1 character in the string, well, we get it.  We
            # do this because Gecko's implementation of getTextAtOffset
            # is broken if there is just one character in the string.]]]
            #
            if (text.characterCount == 1):
                lineString = text.getText(caretOffset, caretOffset + 1)
                startOffset = caretOffset
            else:
                if caretOffset == -1:
                    caretOffset = text.characterCount
                try:
                    [lineString, startOffset, endOffset] = text.getTextAtOffset(
                        caretOffset, pyatspi.TEXT_BOUNDARY_LINE_START)
                except:
                    return ["", 0, 0]

            # Sometimes we get the trailing line-feed-- remove it
            # It is important that these are in order.
            # In some circumstances we might get:
            # word word\r\n
            # so remove \n, and then remove \r.
            # See bgo#619332.
            #
            lineString = lineString.rstrip('\n')
            lineString = lineString.rstrip('\r')

        return [lineString, text.caretOffset, startOffset]

    def phoneticSpellCurrentItem(self, itemString):
        """Phonetically spell the current flat review word or line.

        Arguments:
        - itemString: the string to phonetically spell.
        """

        for (charIndex, character) in enumerate(itemString):
            if character.isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
                character = character.lower()
            else:
                voice =  settings.voices[settings.DEFAULT_VOICE]
            phoneticString = phonnames.getPhoneticName(character)
            speech.speak(phoneticString, voice)

    def _saveLastCursorPosition(self, obj, caretOffset):
        """Save away the current text cursor position for next time.

        Arguments:
        - obj: the current accessible
        - caretOffset: the cursor position within this object
        """

        self.pointOfReference["lastCursorPosition"] = [obj, caretOffset]

    def _getCtrlShiftSelectionsStrings(self):
        return [messages.PARAGRAPH_SELECTED_DOWN,
                messages.PARAGRAPH_UNSELECTED_DOWN,
                messages.PARAGRAPH_SELECTED_UP,
                messages.PARAGRAPH_UNSELECTED_UP]

    def _speakTextSelectionState(self, nSelections):
        """Hacky method to speak special cases without any valid sanity
        checking. It is not long for this world. Do not call it."""

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return False

        eventStr, mods = self.utilities.lastKeyAndModifiers()
        isControlKey = mods & keybindings.CTRL_MODIFIER_MASK
        isShiftKey = mods & keybindings.SHIFT_MODIFIER_MASK
        selectedText = nSelections > 0

        line = None
        if (eventStr == "Page_Down") and isShiftKey and isControlKey:
            line = messages.LINE_SELECTED_RIGHT
        elif (eventStr == "Page_Up") and isShiftKey and isControlKey:
            line = messages.LINE_SELECTED_LEFT
        elif (eventStr == "Page_Down") and isShiftKey and not isControlKey:
            if selectedText:
                line = messages.PAGE_SELECTED_DOWN
            else:
                line = messages.PAGE_UNSELECTED_DOWN
        elif (eventStr == "Page_Up") and isShiftKey and not isControlKey:
            if selectedText:
                line = messages.PAGE_SELECTED_UP
            else:
                line = messages.PAGE_UNSELECTED_UP
        elif (eventStr == "Down") and isShiftKey and isControlKey:
            strings = self._getCtrlShiftSelectionsStrings()
            if selectedText:
                line = strings[0]
            else:
                line = strings[1]
        elif (eventStr == "Up") and isShiftKey and isControlKey:
            strings = self._getCtrlShiftSelectionsStrings()
            if selectedText:
                line = strings[2]
            else:
                line = strings[3]
        elif (eventStr == "Home") and isShiftKey and isControlKey:
            if selectedText:
                line = messages.DOCUMENT_SELECTED_UP
            else:
                line = messages.DOCUMENT_UNSELECTED_UP
        elif (eventStr == "End") and isShiftKey and isControlKey:
            if selectedText:
                line = messages.DOCUMENT_SELECTED_DOWN
            else:
                line = messages.DOCUMENT_SELECTED_UP
        elif (eventStr == "A") and isControlKey and selectedText:
            line = messages.DOCUMENT_SELECTED_ALL

        if line:
            speech.speak(line, None, False)
            return True

        return False

    def systemBeep(self):
        """Rings the system bell. This is really a hack. Ideally, we want
        a method that will present an earcon (any sound designated for the
        purpose of representing an error, event etc)
        """

        print("\a")

    def speakWordUnderMouse(self, acc):
        """Determine if the speak-word-under-mouse capability applies to
        the given accessible.

        Arguments:
        - acc: Accessible to test.

        Returns True if this accessible should provide the single word.
        """
        return acc and acc.getState().contains(pyatspi.STATE_EDITABLE)

    def speakMisspelledIndicator(self, obj, offset):
        """Speaks an announcement indicating that a given word is misspelled.

        Arguments:
        - obj: An accessible which implements the accessible text interface.
        - offset: Offset in the accessible's text for which to retrieve the
          attributes.
        """

        verbosity = _settingsManager.getSetting('speechVerbosityLevel')
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            try:
                text = obj.queryText()
            except:
                return
            # If we're on whitespace, we cannot be on a misspelled word.
            #
            charAndOffsets = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
            if not charAndOffsets[0].strip() \
               or self.utilities.isWordDelimiter(charAndOffsets[0]):
                self._lastWordCheckedForSpelling = charAndOffsets[0]
                return

            wordAndOffsets = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_WORD_START)
            if self.utilities.isWordMisspelled(obj, offset) \
               and wordAndOffsets[0] != self._lastWordCheckedForSpelling:
                self.speakMessage(messages.MISSPELLED)
            # Store this word so that we do not continue to present the
            # presence of the red squiggly as the user arrows amongst
            # the characters.
            #
            self._lastWordCheckedForSpelling = wordAndOffsets[0]

    ############################################################################
    #                                                                          #
    # Presentation methods                                                     #
    # (scripts should not call methods in braille.py or speech.py directly)    #
    #                                                                          #
    ############################################################################

    def presentationInterrupt(self):
        """Convenience method to interrupt presentation of whatever is being
        presented at the moment."""

        speech.stop()
        braille.killFlash()

    def presentKeyboardEvent(self, event):
        """Convenience method to present the KeyboardEvent event. Returns True
        if we fully present the event; False otherwise."""

        if not event.isPressedKey():
            self._sayAllIsInterrupted = False

        if not orca_state.learnModeEnabled:
            if event.shouldEcho == False or event.isOrcaModified():
                return False

        try:
            role = orca_state.locusOfFocus.getRole()
        except:
            return False

        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_FRAME, pyatspi.ROLE_WINDOW]:
            focusedObject = self.utilities.focusedObject(orca_state.activeWindow)
            if focusedObject:
                orca.setLocusOfFocus(None, focusedObject, False)
                role = focusedObject.getRole()

        if role == pyatspi.ROLE_PASSWORD_TEXT:
            return False

        # Worst. Hack. EVER. We have no reliable way of knowing a password is
        # being entered into a terminal -- other than the fact that the text
        # typed ain't there. As a result, we have to do special things when
        # not in special modes. :( See bgo 668025.
        if role == pyatspi.ROLE_TERMINAL:
            if not event.isPressedKey():
                try:
                    text = orca_state.locusOfFocus.queryText()
                    o = text.caretOffset
                    string = text.getText(o-1, o)
                except:
                    pass
                else:
                    if not event.event_string in [string, 'space']:
                        return False
            elif not (orca_state.learnModeEnabled or event.isLockingKey()):
                return False

        elif not event.isPressedKey():
            return False

        debug.println(debug.LEVEL_FINEST,
                      "Script.presentKeyboardEvent: %s" % event.event_string)

        braille.displayKeyEvent(event)
        orcaModifierPressed = event.isOrcaModifier() and event.isPressedKey()
        if event.isCharacterEchoable() and not orcaModifierPressed:
            return False
        if orca_state.learnModeEnabled:
            if event.isPrintableKey() and event.getClickCount() == 2:
                self.phoneticSpellCurrentItem(event.event_string)
                return True

        speech.speakKeyEvent(event)
        return True

    def presentMessage(self, fullMessage, briefMessage=None, voice=None):
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

        if _settingsManager.getSetting('enableSpeech'):
            currentCapStyle = _settingsManager.getSetting('capitalizationStyle')
            _settingsManager.setSetting(
                'capitalizationStyle', settings.CAPITALIZATION_STYLE_NONE)
            speech.updateCapitalizationStyle()

            if _settingsManager.getSetting('messageVerbosityLevel') \
                    == settings.VERBOSITY_LEVEL_BRIEF:
                message = briefMessage
            else:
                message = fullMessage
            if message:
                voice = voice or self.voices.get(settings.SYSTEM_VOICE)
                speech.speak(message, voice)

            _settingsManager.setSetting('capitalizationStyle', currentCapStyle)
            speech.updateCapitalizationStyle()

        if (_settingsManager.getSetting('enableBraille') \
             or _settingsManager.getSetting('enableBrailleMonitor')) \
           and _settingsManager.getSetting('enableFlashMessages'):
            if _settingsManager.getSetting('flashVerbosityLevel') \
                    == settings.VERBOSITY_LEVEL_BRIEF:
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

            if _settingsManager.getSetting('flashIsPersistent'):
                duration = -1
            else:
                duration = _settingsManager.getSetting('brailleFlashTime')

            braille.displayMessage(message, flashTime=duration)

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
    def addToLineAsBrailleRegion(string, line):
        """Creates a Braille Region out of string and adds it to the line.

        Arguments:
        - string: the string to be displayed
        - line: a braille.Line
        """

        line.addRegion(braille.Region(string))

    @staticmethod
    def brailleRegionsFromStrings(strings):
        """Creates a list of braille regions from the list of strings.

        Arguments:
        - strings: a list of strings from which to create the list of
          braille Region instances

        Returns the list of braille Region instances
        """

        brailleRegions = []
        for string in strings:
            brailleRegions.append(braille.Region(string))

        return brailleRegions

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

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: display message disabled")
            return

        braille.displayMessage(message, cursor, flashTime)

    @staticmethod
    def displayBrailleRegions(regionInfo, flashTime=0):
        """Displays a list of regions on a single line, setting focus to the
        specified region.  The regionInfo parameter is something that is
        typically returned by a call to braille_generator.generateBraille.

        Arguments:
        - regionInfo: a list where the first element is a list of regions
          to display and the second element is the region with focus (must
          be in the list from element 0)
        - flashTime:  if non-0, the number of milliseconds to display the
          regions before reverting back to what was there before. A 0 means
          to not do any flashing. A negative number means to display the
          message until some other message comes along or the user presses
          a cursor routing key.
        """

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: display regions disabled")
            return

        braille.displayRegions(regionInfo, flashTime)

    def displayBrailleForObject(self, obj):
        """Convenience method for scripts combining the call to the braille
        generator for the script with the call to displayBrailleRegions.

        Arguments:
        - obj: the accessible object to display in braille
        """

        regions = self.brailleGenerator.generateBraille(obj)
        self.displayBrailleRegions(regions)

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
    def getNewBrailleComponent(accessible, string, cursorOffset=0,
                               indicator='', expandOnCursor=False):
        """Creates a new braille Component.

        Arguments:
        - accessible: the accessible associated with this region
        - string: the string to be displayed
        - cursorOffset: a 0-based index saying where to draw the cursor
          for this Region if it gets focus

        Returns the new Component.
        """

        return braille.Component(accessible, string, cursorOffset,
                                 indicator, expandOnCursor)

    @staticmethod
    def getNewBrailleRegion(string, cursorOffset=0, expandOnCursor=False):
        """Creates a new braille Region.

        Arguments:
        - string: the string to be displayed
        - cursorOffset: a 0-based index saying where to draw the cursor
          for this Region if it gets focus

        Returns the new Region.
        """

        return braille.Region(string, cursorOffset, expandOnCursor)

    @staticmethod
    def getNewBrailleText(accessible, label="", eol="", startOffset=None,
                          endOffset=None):

        """Creates a new braille Text region.

        Arguments:
        - accessible: the accessible associated with this region and which
          implements AtkText
        - label: an optional label to display
        - eol: the endOfLine indicator

        Returns the new Text region.
        """

        return braille.Text(accessible, label, eol, startOffset, endOffset)

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

    @staticmethod
    def presentItemsInBraille(items):
        """Method to braille a list of items. Scripts should call this
        method rather than handling the creation and displaying of a
        braille line directly.

        Arguments:
        - items: a list of strings to be presented
        """

        line = braille.getShowingLine()
        for item in items:
            line.addRegion(braille.Region(" " + item))

        braille.refresh()

    def updateBrailleForNewCaretPosition(self, obj):
        """Try to reposition the cursor without having to do a full update."""

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: update caret disabled")
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
          knowning that we will fail and/or it taking an unreasonable
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

    def speakCharacter(self, character):
        """Method to speak a single character. Scripts should use this
        method rather than calling speech.speakCharacter directly."""

        if character.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        spokenCharacter = chnames.getCharacterName(character)
        speech.speakCharacter(spokenCharacter, voice)

    def speakMessage(self, string, voice=None, interrupt=True):
        """Method to speak a single string. Scripts should use this
        method rather than calling speech.speak directly.

        - string: The string to be spoken.
        - voice: The voice to use. By default, the "system" voice will
          be used.
        - interrupt: If True, any current speech should be interrupted
          prior to speaking the new text.
        """

        if _settingsManager.getSetting('enableSpeech'):
            voice = voice or self.voices.get(settings.SYSTEM_VOICE)
            speech.speak(string, voice, interrupt)

    @staticmethod
    def presentItemsInSpeech(items):
        """Method to speak a list of items. Scripts should call this
        method rather than handling the creation and speaking of
        utterances directly.

        Arguments:
        - items: a list of strings to be presented
        """

        utterances = []
        for item in items:
            utterances.append(item)

        speech.speak(utterances)

    def speakUnicodeCharacter(self, character):
        """ Speaks some information about an unicode character.
        At the Momment it just anounces the character unicode number but
        this information may be changed in the future

        Arguments:
        - character: the character to speak information of
        """
        speech.speak(messages.UNICODE % \
                         self.utilities.unicodeValueString(character))

    def presentTime(self, inputEvent):
        """ Presents the current time. """
        timeFormat = _settingsManager.getSetting('presentTimeFormat')
        message = time.strftime(timeFormat, time.localtime())
        self.presentMessage(message)
        return True

    def presentDate(self, inputEvent):
        """ Presents the current date. """
        dateFormat = _settingsManager.getSetting('presentDateFormat')
        message = time.strftime(dateFormat, time.localtime())
        self.presentMessage(message)
        return True
