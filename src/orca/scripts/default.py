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

import pyatspi
import orca.braille as braille
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
import orca.sound as sound
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
                pyatspi.cache.DEFAULT ^ pyatspi.cache.CHILDREN ^ pyatspi.cache.NAME ^ pyatspi.cache.DESCRIPTION)

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

        self.inputEventHandlers["flatReviewSayAllHandler"] = \
            input_event.InputEventHandler(
                Script.flatReviewSayAll,
                cmdnames.SAY_ALL_FLAT_REVIEW)

        self.inputEventHandlers["whereAmIBasicHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmIBasic,
                cmdnames.WHERE_AM_I_BASIC)

        self.inputEventHandlers["whereAmIDetailedHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmIDetailed,
                cmdnames.WHERE_AM_I_DETAILED)

        self.inputEventHandlers["whereAmILinkHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmILink,
                cmdnames.WHERE_AM_I_LINK)

        self.inputEventHandlers["whereAmISelectionHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmISelection,
                cmdnames.WHERE_AM_I_SELECTION)

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

        self.inputEventHandlers[ \
          "changeNumberStyleHandler"] = \
            input_event.InputEventHandler(
                Script.changeNumberStyle,
                cmdnames.CHANGE_NUMBER_STYLE)

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
                mouse_review.reviewer.toggle,
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

        self.inputEventHandlers["presentSizeAndPositionHandler"] = \
            input_event.InputEventHandler(
                Script.presentSizeAndPosition,
                cmdnames.PRESENT_SIZE_AND_POSITION)

        self.inputEventHandlers.update(notification_messages.inputEventHandlers)

    def getInputEventHandlerKey(self, inputEventHandler):
        """Returns the name of the key that contains an inputEventHadler
        passed as argument
        """

        for keyName, handler in self.inputEventHandlers.items():
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
        listeners["window:destroy"]                          = \
            self.onWindowDestroyed

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
            msg = 'ERROR: Exception when overriding keybindings in %s' % self
            debug.println(debug.LEVEL_WARNING, msg, True)
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
            brailleBindings[braille.brlapi.KEY_CMD_FWINLT]     = \
                self.inputEventHandlers["panBrailleLeftHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FWINLTSKIP] = \
                self.inputEventHandlers["panBrailleLeftHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FWINRT]     = \
                self.inputEventHandlers["panBrailleRightHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FWINRTSKIP] = \
                self.inputEventHandlers["panBrailleRightHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_LNUP]       = \
                self.inputEventHandlers["reviewAboveHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_LNDN]       = \
                self.inputEventHandlers["reviewBelowHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FREEZE]     = \
                self.inputEventHandlers["toggleFlatReviewModeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_TOP_LEFT]   = \
                self.inputEventHandlers["reviewHomeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_BOT_LEFT]   = \
                self.inputEventHandlers["reviewBottomLeftHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_HOME]       = \
                self.inputEventHandlers["goBrailleHomeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_SIXDOTS]     = \
                self.inputEventHandlers["contractedBrailleHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_ROUTE]     = \
                self.inputEventHandlers["processRoutingKeyHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_CUTBEGIN]   = \
                self.inputEventHandlers["processBrailleCutBeginHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_CUTLINE]   = \
                self.inputEventHandlers["processBrailleCutLineHandler"]
        except AttributeError:
            msg = 'DEFAULT: Braille bindings unavailable in %s' % self
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = 'ERROR: Exception getting braille bindings in %s' % self
            debug.println(debug.LEVEL_INFO, msg, True)
            debug.printException(debug.LEVEL_CONFIGURATION)
        return brailleBindings

    def deactivate(self):
        """Called when this script is deactivated."""

        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self.pointOfReference = {}

    def registerEventListeners(self):
        super().registerEventListeners()
        self.utilities.connectToClipboard()

    def deregisterEventListeners(self):
        super().deregisterEventListeners()
        self.utilities.disconnectFromClipboard()

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
        if orca_state.activeWindow:
            try:
                names[hash(orca_state.activeWindow)] = orca_state.activeWindow.name
            except:
                msg = "ERROR: Exception getting name for %s" % orca_state.activeWindow
                debug.println(debug.LEVEL_INFO, msg, True)

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
            self.utilities.updateCachedTextSelection(obj)

        # We want to save the current row and column of a newly focused
        # or selected table cell so that on subsequent cell focus/selection
        # we only present the changed location.
        row, column = self.utilities.coordinatesForCell(obj)
        self.pointOfReference['lastColumn'] = column
        self.pointOfReference['lastRow'] = row

        self.pointOfReference['checkedChange'] = \
            hash(obj), state.contains(pyatspi.STATE_CHECKED)
        self.pointOfReference['selectedChange'] = \
            hash(obj), state.contains(pyatspi.STATE_SELECTED)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        self.utilities.presentFocusChangeReason()

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

        topLevel = self.utilities.topLevelObject(newLocusOfFocus)
        if orca_state.activeWindow != topLevel:
            orca_state.activeWindow = topLevel
            self.windowActivateTime = time.time()

        self.updateBraille(newLocusOfFocus)

        shouldNotInterrupt = \
           self.windowActivateTime and time.time() - self.windowActivateTime < 1

        utterances = self.speechGenerator.generateSpeech(
            newLocusOfFocus,
            priorObj=oldLocusOfFocus)

        speech.speak(utterances, interrupt=not shouldNotInterrupt)
        self._saveFocusedObjectInfo(newLocusOfFocus)

    def activate(self):
        """Called when this script is activated."""

        _settingsManager.loadAppSettings(self)
        braille.setupKeyRanges(self.brailleBindings.keys())
        speech.updatePunctuationLevel()
        speech.updateCapitalizationStyle()

    def updateBraille(self, obj, **args):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        """

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: update disabled", True)
            return

        if not obj:
            return

        result, focusedRegion = self.brailleGenerator.generateBraille(obj, **args)
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

    def showHelp(self, inputEvent=None):
        return orca.helpForOrca()

    def listNotifications(self, inputEvent=None):
        if inputEvent is None:
            inputEvent = orca_state.lastNonModifierKeyEvent

        return notification_messages.listNotificationMessages(self, inputEvent)

    def listOrcaShortcuts(self, inputEvent=None):
        """Shows a simple gui listing Orca's bound commands."""

        if inputEvent is None:
            inputEvent = orca_state.lastNonModifierKeyEvent

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
        beyond the end will take you to the beginning of the next line.

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
            self.utilities.setClipboardText(texti.getText(startOffset, endOffset))

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
            return True

        if eventsynthesizer.routeToCharacter(orca_state.locusOfFocus):
            return True

        if eventsynthesizer.routeToObject(orca_state.locusOfFocus):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.presentMessage(full, brief)
        return False

    def presentStatusBar(self, inputEvent):
        """Speaks and brailles the contents of the status bar and/or default
        button of the window with focus.
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)

        frame, dialog = self.utilities.frameAndDialog(obj)
        if frame:
            speech.speak(self.speechGenerator.generateStatusBar(frame))
            infobar = self.utilities.infoBar(frame)
            if infobar:
                speech.speak(self.speechGenerator.generateSpeech(infobar))

        window = dialog or frame
        if window:
            speech.speak(self.speechGenerator.generateDefaultButton(window))

    def presentTitle(self, inputEvent):
        """Speaks and brailles the title of the window with focus."""

        obj = orca_state.locusOfFocus
        if self.utilities.isDead(obj):
            obj = orca_state.activeWindow

        if not obj or self.utilities.isDead(obj):
            self.presentMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        title = self.speechGenerator.generateTitle(obj)
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
            if self.flatReviewContext.clickCurrent(1):
                return True

            obj = self.flatReviewContext.getCurrentAccessible()
            if eventsynthesizer.clickActionOn(obj):
                return True
            if eventsynthesizer.pressActionOn(obj):
                return True
            if eventsynthesizer.grabFocusOn(obj):
                return True
            return False

        if self.utilities.queryNonEmptyText(orca_state.locusOfFocus):
            if eventsynthesizer.clickCharacter(orca_state.locusOfFocus, 1):
                return True

        if eventsynthesizer.clickObject(orca_state.locusOfFocus, 1):
            return True

        full = messages.LOCATION_NOT_FOUND_FULL
        brief = messages.LOCATION_NOT_FOUND_BRIEF
        self.presentMessage(full, brief)
        return False

    def rightClickReviewItem(self, inputEvent=None):
        """Performs a right mouse button click on the current item."""

        if self.flatReviewContext:
            self.flatReviewContext.clickCurrent(3)
            return True

        if eventsynthesizer.clickCharacter(orca_state.locusOfFocus, 3):
            return True

        if eventsynthesizer.clickObject(orca_state.locusOfFocus, 3):
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

        voice = self.speechGenerator.voice(string=wordString)

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
                    speech.speak(wordString, voice)
                elif speechType == 2:
                    self.spellCurrentItem(wordString)
                elif speechType == 3:
                    self.phoneticSpellCurrentItem(wordString)
                elif speechType == 1:
                    wordString = self.utilities.adjustForRepeats(wordString)
                    speech.speak(wordString, voice)

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

        voice = self.speechGenerator.voice(string=lineString)

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
            elif lineString.isupper() and (speechType < 2 or speechType > 3):
                speech.speak(lineString, voice)
            elif speechType == 2:
                self.spellCurrentItem(lineString)
            elif speechType == 3:
                self.phoneticSpellCurrentItem(lineString)
            else:
                lineString = self.utilities.adjustForRepeats(lineString)
                speech.speak(lineString, voice)

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
            self.utilities.setClipboardText(self.currentReviewContents.rstrip("\n"))
            self.presentMessage(messages.FLAT_REVIEW_COPIED)
        else:
            self.presentMessage(messages.FLAT_REVIEW_NOT_IN)

        return True

    def flatReviewAppend(self, inputEvent):
        """Appends the contents of the item under flat review to
        the clipboard."""

        if self.flatReviewContext:
            self.utilities.appendTextToClipboard(self.currentReviewContents.rstrip("\n"))
            self.presentMessage(messages.FLAT_REVIEW_APPENDED)
        else:
            self.presentMessage(messages.FLAT_REVIEW_NOT_IN)

        return True

    def flatReviewSayAll(self, inputEvent):
        context = self.getFlatReviewContext()
        context.goBegin()

        while True:
            [string, x, y, width, height] = context.getCurrent(flat_review.Context.LINE)
            if string is not None:
                speech.speak(string)
            moved = context.goNext(flat_review.Context.LINE, flat_review.Context.WRAP_LINE)
            if not moved:
                break

        return True

    def sayAll(self, inputEvent, obj=None, offset=None):
        obj = obj or orca_state.locusOfFocus
        if not obj or self.utilities.isDead(obj):
            self.presentMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        try:
            text = obj.queryText()
        except NotImplementedError:
            utterances = self.speechGenerator.generateSpeech(obj)
            utterances.extend(self.tutorialGenerator.getTutorial(obj, False))
            speech.speak(utterances)
        except AttributeError:
            pass
        else:
            if offset is None:
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

        self.presentationInterrupt()
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

        speech.shutdown()
        speech.init()

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

    def changeNumberStyle(self, inputEvent=None):
        """Changes spoken number style between digits and words."""

        speakDigits = _settingsManager.getSetting('speakNumbersAsDigits')
        if speakDigits:
            brief = messages.NUMBER_STYLE_WORDS_BRIEF
            full = messages.NUMBER_STYLE_WORDS_FULL
        else:
            brief = messages.NUMBER_STYLE_DIGITS_BRIEF
            full = messages.NUMBER_STYLE_DIGITS_FULL

        _settingsManager.setSetting('speakNumbersAsDigits', not speakDigits)
        self.presentMessage(full, brief)
        return True

    def toggleTableCellReadMode(self, inputEvent=None):
        """Toggles an indicator for whether we should just read the current
        table cell or read the whole row."""

        table = self.utilities.getTable(orca_state.locusOfFocus)
        if not table:
            self.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if not self.utilities.getContainingDocument(table):
            settingName = 'readFullRowInGUITable'
        elif self.utilities.isSpreadSheetTable(table):
            settingName = 'readFullRowInSpreadSheet'
        else:
            settingName = 'readFullRowInDocumentTable'

        speakRow = _settingsManager.getSetting(settingName)
        _settingsManager.setSetting(settingName, not speakRow)

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

        if self.spellcheck and self.spellcheck.isActive():
            self.spellcheck.presentErrorDetails(not basicOnly)

        obj = orca_state.locusOfFocus
        if self.utilities.isDead(obj):
            obj = orca_state.activeWindow

        if not obj or self.utilities.isDead(obj):
            self.presentMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        self.updateBraille(obj)

        if basicOnly:
            formatType = 'basicWhereAmI'
        else:
            formatType = 'detailedWhereAmI'
        speech.speak(self.speechGenerator.generateSpeech(
            self.utilities.realActiveAncestor(obj),
            alreadyFocused=True,
            formatType=formatType,
            forceMnemonic=True,
            forceList=True,
            forceTutorial=True))

        return True

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

    def whereAmILink(self, inputEvent=None, link=None):
        link = link or orca_state.locusOfFocus
        if not self.utilities.isLink(link):
            self.presentMessage(messages.NOT_ON_A_LINK)
        else:
            speech.speak(self.speechGenerator.generateLinkInfo(link))
        return True

    def _whereAmISelectedText(self, inputEvent, obj):
        text, startOffset, endOffset = self.utilities.allSelectedText(obj)
        if not text:
            msg = messages.NO_SELECTED_TEXT
        else:
            msg = messages.SELECTED_TEXT_IS % text
        self.speakMessage(msg)
        return True

    def whereAmISelection(self, inputEvent=None, obj=None):
        obj = obj or orca_state.locusOfFocus
        if not obj:
            return True

        container = self.utilities.getSelectionContainer(obj)
        if not container:
            msg = "INFO: Selection container not found for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return self._whereAmISelectedText(inputEvent, obj)

        count = self.utilities.selectedChildCount(container)
        childCount = self.utilities.selectableChildCount(container)
        self.presentMessage(messages.selectedItemsCount(count, childCount))
        if not count:
            return True

        utterances = self.speechGenerator.generateSelectedItems(container)
        speech.speak(utterances)
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

        frames = [pyatspi.ROLE_FRAME,
                  pyatspi.ROLE_DIALOG,
                  pyatspi.ROLE_FILE_CHOOSER,
                  pyatspi.ROLE_COLOR_CHOOSER]

        if event.source.getRole() in frames:
            if event.detail1 and not self.utilities.canBeActiveWindow(event.source):
                return

            sourceIsActiveWindow = self.utilities.isSameObject(
                event.source, orca_state.activeWindow)

            if sourceIsActiveWindow and not event.detail1:
                if self.utilities.inMenu():
                    msg = "DEFAULT: Ignoring event. In menu."
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return

                if not self.utilities.eventIsUserTriggered(event):
                    msg = "DEFAULT: Not clearing state. Event is not user triggered."
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return

                msg = "DEFAULT: Event is for active window. Clearing state."
                debug.println(debug.LEVEL_INFO, msg, True)
                orca_state.activeWindow = None
                return

            if not sourceIsActiveWindow and event.detail1:
                msg = "DEFAULT: Updating active window to event source."
                debug.println(debug.LEVEL_INFO, msg, True)
                self.windowActivateTime = time.time()
                orca.setLocusOfFocus(event, event.source)
                orca_state.activeWindow = event.source

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
            self.presentationInterrupt()

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
        """Callback for object:text-caret-moved accessibility events."""

        obj, offset = self.pointOfReference.get("lastCursorPosition", (None, -1))
        if offset == event.detail1 and obj == event.source:
            msg = "DEFAULT: Event is for last saved cursor position"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        state = event.source.getState()
        if not state.contains(pyatspi.STATE_SHOWING):
            msg = "DEFAULT: Event source is not showing"
            debug.println(debug.LEVEL_INFO, msg, True)
            if not self.utilities.presentEventFromNonShowingObject(event):
                return

        if event.source != orca_state.locusOfFocus \
           and state.contains(pyatspi.STATE_FOCUSED):
            topLevelObject = self.utilities.topLevelObject(event.source)
            if self.utilities.isSameObject(orca_state.activeWindow, topLevelObject):
                msg = "DEFAULT: Updating locusOfFocus from %s to %s" % \
                      (orca_state.locusOfFocus, event.source)
                debug.println(debug.LEVEL_INFO, msg, True)
                orca.setLocusOfFocus(event, event.source, False)
            else:
                msg = "DEFAULT: Source window (%s) is not active window(%s)" \
                      % (topLevelObject, orca_state.activeWindow)
                debug.println(debug.LEVEL_INFO, msg, True)

        if event.source != orca_state.locusOfFocus:
            msg = "DEFAULT: Event source (%s) is not locusOfFocus (%s)" \
                  % (event.source, orca_state.locusOfFocus)
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        text = event.source.queryText()
        try:
            caretOffset = text.caretOffset
        except:
            msg = "DEFAULT: Exception getting caretOffset for %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        self._saveLastCursorPosition(event.source, text.caretOffset)
        if text.getNSelections() > 0:
            msg = "DEFAULT: Event source has text selections"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.utilities.handleTextSelectionChange(event.source)
            return
        else:
            start, end, string = self.utilities.getCachedTextSelection(obj)
            if string and self.utilities.handleTextSelectionChange(obj):
                return

        msg = "DEFAULT: Presenting text at new caret position"
        debug.println(debug.LEVEL_INFO, msg, True)
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

        if not self.utilities.isPresentableExpandedChangedEvent(event):
            return

        obj = event.source
        oldObj, oldState = self.pointOfReference.get('expandedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            return

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['expandedChange'] = hash(obj), event.detail1

        details = self.utilities.detailsContentForObject(obj)
        for detail in details:
            self.speakMessage(detail, interrupt=False)

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
        """Callback for mouse:button events."""

        mouseEvent = input_event.MouseButtonEvent(event)
        orca_state.lastInputEvent = mouseEvent
        if not mouseEvent.pressed:
            return

        windowChanged = orca_state.activeWindow != mouseEvent.window
        if windowChanged:
            orca_state.activeWindow = mouseEvent.window
            orca.setLocusOfFocus(None, mouseEvent.window, False)

        self.presentationInterrupt()
        obj = mouseEvent.obj
        if obj and obj.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(None, obj, windowChanged)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        obj = event.source
        names = self.pointOfReference.get('names', {})
        oldName = names.get(hash(obj))
        if oldName == event.any_data:
            msg = "DEFAULT: Old name (%s) is the same as new name" % oldName
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        role = obj.getRole()
        if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_TABLE_CELL]:
            msg = "DEFAULT: Event is redundant notification for this role"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if role == pyatspi.ROLE_FRAME:
            if obj != orca_state.activeWindow:
                msg = "DEFAULT: Event is for frame other than the active window"
                debug.println(debug.LEVEL_INFO, msg, True)
                return
        elif obj != orca_state.locusOfFocus:
            msg = "DEFAULT: Event is for object other than the locusOfFocus"
            debug.println(debug.LEVEL_INFO, msg, True)
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
        obj.clearCache()
        state = obj.getState()
        if not state.contains(pyatspi.STATE_FOCUSED):
            return

        if not self.utilities.isSameObject(orca_state.locusOfFocus, obj):
            return

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return

        isSelected = state.contains(pyatspi.STATE_SELECTED)
        if isSelected != event.detail1:
            msg = "DEFAULT: Bogus event: detail1 doesn't match state"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        oldObj, oldState = self.pointOfReference.get('selectedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            msg = "DEFAULT: Duplicate or spam event"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

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

        if event.detail1:
            self.speakMessage(messages.TEXT_SELECTED, interrupt=False)
        else:
            self.speakMessage(messages.TEXT_UNSELECTED, interrupt=False)

        self.pointOfReference['selectedChange'] = hash(obj), event.detail1

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        obj = event.source
        state = obj.getState()

        if self.utilities.handlePasteLocusOfFocusChange():
            orca.setLocusOfFocus(event, event.source, False)
        elif self.utilities.handleContainerSelectionChange(event.source):
            return
        else:
            if state.contains(pyatspi.STATE_MANAGES_DESCENDANTS):
                return

        # TODO - JD: We need to give more thought to where we look to this
        # event and where we prefer object:state-changed:selected.

        # If the current item's selection is toggled, we'll present that
        # via the state-changed event.
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if keyString == "space":
            return

        role = obj.getRole()
        if role == pyatspi.ROLE_COMBO_BOX and not state.contains(pyatspi.STATE_EXPANDED):
            entry = self.utilities.getEntryForEditableComboBox(event.source)
            if entry and entry.getState().contains(pyatspi.STATE_FOCUSED):
                return
 
        mouseReviewItem = mouse_review.reviewer.getCurrentItem()
        selectedChildren = self.utilities.selectedChildren(obj)
        for child in selectedChildren:
            if pyatspi.findAncestor(orca_state.locusOfFocus, lambda x: x == child):
                msg = "DEFAULT: Child %s is ancestor of locusOfFocus" % child
                debug.println(debug.LEVEL_INFO, msg, True)
                self._saveFocusedObjectInfo(orca_state.locusOfFocus)
                return

            if child == mouseReviewItem:
                msg = "DEFAULT: Child %s is current mouse review item" % child
                debug.println(debug.LEVEL_INFO, msg, True)
                continue

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

        window, dialog = self.utilities.frameAndDialog(obj)
        clearCache = window != orca_state.activeWindow
        if window and not self.utilities.canBeActiveWindow(window, clearCache) and not dialog:
            return

        try:
            childCount = obj.childCount
            role = obj.getRole()
        except:
            msg = "DEFAULT: Exception getting childCount and role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if childCount and role != pyatspi.ROLE_COMBO_BOX:
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
            labels = self.utilities.unrelatedLabels(obj, visibleOnly, 1)
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
                self.presentObject(obj)
                return
 
            if orca_state.locusOfFocus and keyString == "F1":
                obj = orca_state.locusOfFocus
                self.updateBraille(obj)
                speech.speak(self.speechGenerator.generateSpeech(obj, priorObj=event.source))
                return

    def onTextAttributesChanged(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        if not self.utilities.isPresentableTextChangedEventForLocusOfFocus(event):
            return

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "DEFAULT: Querying non-empty text returned None"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if _settingsManager.getSetting('speakMisspelledIndicator'):
            offset = text.caretOffset
            if not text.getText(offset, offset+1).isalnum():
                offset -= 1
            if self.utilities.isWordMisspelled(event.source, offset-1) \
               or self.utilities.isWordMisspelled(event.source, offset+1):
                self.speakMessage(messages.MISSPELLED)

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if not self.utilities.isPresentableTextChangedEventForLocusOfFocus(event):
            return

        self.utilities.handleUndoTextEvent(event)

        orca.setLocusOfFocus(event, event.source, False)
        self.updateBraille(event.source)

        full, brief = "", ""
        if self.utilities.isClipboardTextChangedEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to clipboard cut"
            debug.println(debug.LEVEL_INFO, msg, True)
            full, brief = messages.CLIPBOARD_CUT_FULL, messages.CLIPBOARD_CUT_BRIEF
        elif self.utilities.isSelectedTextDeletionEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to deleting selected text"
            debug.println(debug.LEVEL_INFO, msg, True)
            full = messages.SELECTION_DELETED

        if full or brief:
            self.presentMessage(full, brief)
            self.utilities.updateCachedTextSelection(event.source)
            return

        string = self.utilities.deletedText(event)
        if self.utilities.isDeleteCommandTextDeletionEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to Delete command"
            debug.println(debug.LEVEL_INFO, msg, True)
            string = self.utilities.getCharacterAtOffset(event.source)
        elif self.utilities.isBackSpaceCommandTextDeletionEvent(event):
            msg = "DEFAULT: Deletion is believed to be due to BackSpace command"
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            msg = "INFO: Event is not being presented due to lack of cause"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if len(string) == 1:
            self.speakCharacter(string)
        else:
            voice = self.speechGenerator.voice(string=string)
            speech.speak(string, voice)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not self.utilities.isPresentableTextChangedEventForLocusOfFocus(event):
            return

        self.utilities.handleUndoTextEvent(event)

        if event.source == orca_state.locusOfFocus and self.utilities.isAutoTextEvent(event):
            self._saveFocusedObjectInfo(event.source)
        orca.setLocusOfFocus(event, event.source, False)
        self.updateBraille(event.source)

        full, brief = "", ""
        if self.utilities.isClipboardTextChangedEvent(event):
            msg = "DEFAULT: Insertion is believed to be due to clipboard paste"
            debug.println(debug.LEVEL_INFO, msg, True)
            full, brief = messages.CLIPBOARD_PASTED_FULL, messages.CLIPBOARD_PASTED_BRIEF
        elif self.utilities.isSelectedTextRestoredEvent(event):
            msg = "DEFAULT: Insertion is believed to be due to restoring selected text"
            debug.println(debug.LEVEL_INFO, msg, True)
            full = messages.SELECTION_RESTORED

        if full or brief:
            self.presentMessage(full, brief)
            self.utilities.updateCachedTextSelection(event.source)
            return

        speakString = True

        # Because some implementations are broken.
        string = self.utilities.insertedText(event)

        if self.utilities.lastInputEventWasCommand():
            msg = "DEFAULT: Insertion is believed to be due to command"
            debug.println(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isMiddleMouseButtonTextInsertionEvent(event):
            msg = "DEFAULT: Insertion is believed to be due to middle mouse button"
            debug.println(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isEchoableTextInsertionEvent(event):
            msg = "DEFAULT: Insertion is believed to be echoable"
            debug.println(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isAutoTextEvent(event):
            msg = "DEFAULT: Insertion is believed to be auto text event"
            debug.println(debug.LEVEL_INFO, msg, True)
        elif self.utilities.isSelectedTextInsertionEvent(event):
            msg = "DEFAULT: Insertion is also selected"
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            msg = "DEFAULT: Not speaking inserted string due to lack of cause"
            debug.println(debug.LEVEL_INFO, msg, True)
            speakString = False

        if speakString:
            if len(string) == 1:
                self.speakCharacter(string)
            else:
                voice = self.speechGenerator.voice(string=string)
                speech.speak(string, voice)

        if len(string) != 1:
            return

        if _settingsManager.getSetting('enableEchoBySentence') \
           and self.echoPreviousSentence(event.source):
            return

        if _settingsManager.getSetting('enableEchoByWord'):
            self.echoPreviousWord(event.source)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source

        # We won't handle undo here as it can lead to double-presentation.
        # If there is an application for which text-changed events are
        # missing upon undo, handle them in an app or toolkit script.

        self.utilities.handleTextSelectionChange(obj)
        self.updateBraille(obj)

    def onColumnReordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        if not self.utilities.lastInputEventWasTableSort():
            return

        if event.source != self.utilities.getTable(orca_state.locusOfFocus):
            return

        self.pointOfReference['last-table-sort-time'] = time.time()
        self.presentMessage(messages.TABLE_REORDERED_COLUMNS)

    def onRowReordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        if not self.utilities.lastInputEventWasTableSort():
            return

        if event.source != self.utilities.getTable(orca_state.locusOfFocus):
            return

        self.pointOfReference['last-table-sort-time'] = time.time()
        self.presentMessage(messages.TABLE_REORDERED_ROWS)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        obj = event.source
        role = obj.getRole()

        try:
            value = obj.queryValue()
            currentValue = value.currentValue
        except NotImplementedError:
            msg = "ERROR: %s doesn't implement AtspiValue" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return
        except:
            msg = "ERROR: Exception getting current value for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if "oldValue" in self.pointOfReference \
           and (currentValue == self.pointOfReference["oldValue"]):
            return

        isProgressBarUpdate, msg = self.utilities.isProgressBarUpdate(obj, event)
        msg = "DEFAULT: Is progress bar update: %s, %s" % (isProgressBarUpdate, msg)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not isProgressBarUpdate and obj != orca_state.locusOfFocus:
            msg = "DEFAULT: Source != locusOfFocus (%s)" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if role == pyatspi.ROLE_SPIN_BUTTON:
            self._saveFocusedObjectInfo(event.source)

        self.pointOfReference["oldValue"] = currentValue
        self.updateBraille(obj, isProgressBarUpdate=isProgressBarUpdate)
        speech.speak(self.speechGenerator.generateSpeech(
            obj, alreadyFocused=True, isProgressBarUpdate=isProgressBarUpdate))
        self.__play(self.soundGenerator.generateSound(
            obj, alreadyFocused=True, isProgressBarUpdate=isProgressBarUpdate))

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated.

        Arguments:
        - event: the Event
        """

        if not self.utilities.canBeActiveWindow(event.source, False):
            return

        if self.utilities.isSameObject(event.source, orca_state.activeWindow):
            msg = "DEFAULT: Event is for active window."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        self.pointOfReference = {}

        self.windowActivateTime = time.time()
        orca_state.activeWindow = event.source

        try:
            childCount = event.source.childCount
            childRole = event.source[0].getRole()
        except:
            pass
        else:
            if childCount == 1 and childRole == pyatspi.ROLE_MENU:
                orca.setLocusOfFocus(event, event.source[0])
                return

        orca.setLocusOfFocus(event, event.source)

    def onWindowCreated(self, event):
        """Callback for window:create accessibility events."""

        pass

    def onWindowDestroyed(self, event):
        """Callback for window:destroy accessibility events."""

        pass

    def onWindowDeactivated(self, event):
        """Called whenever a toplevel window is deactivated.

        Arguments:
        - event: the Event
        """

        if self.utilities.inMenu():
            msg = "DEFAULT: Ignoring event. In menu."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if event.source != orca_state.activeWindow:
            msg = "DEFAULT: Ignoring event. Not for active window %s." % orca_state.activeWindow
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        self.presentationInterrupt()
        self.clearBraille()

        if self.flatReviewContext:
            self.flatReviewContext = None

        self.pointOfReference = {}

        if not self.utilities.eventIsUserTriggered(event):
            msg = "DEFAULT: Not clearing state. Event is not user triggered."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        msg = "DEFAULT: Clearing state."
        debug.println(debug.LEVEL_INFO, msg, True)

        orca.setLocusOfFocus(event, None)
        orca_state.activeWindow = None
        orca_state.activeScript = None
        orca_state.listNotificationsModeEnabled = False
        orca_state.learnModeEnabled = False

    def onClipboardContentsChanged(self, *args):
        if self.flatReviewContext:
            return

        if not self.utilities.objectContentsAreInClipboard():
            return

        if not self.utilities.topLevelObjectIsActiveAndCurrent():
            return

        if self.utilities.lastInputEventWasCopy():
            self.presentMessage(messages.CLIPBOARD_COPIED_FULL, messages.CLIPBOARD_COPIED_BRIEF)
            return

        if not self.utilities.lastInputEventWasCut():
            return

        try:
            state = orca_state.locusOfFocus.getState()
        except:
            msg = "ERROR: Exception getting state of %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            if state.contains(pyatspi.STATE_EDITABLE):
                return

        self.presentMessage(messages.CLIPBOARD_CUT_FULL, messages.CLIPBOARD_CUT_BRIEF)

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        obj = otherObj or event.source
        self.updateBrailleForNewCaretPosition(obj)
        if self._inSayAll:
            return

        if self.utilities.lastInputEventWasLineNav():
            msg = "DEFAULT: Presenting result of line nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.sayLine(obj)
            return

        if self.utilities.lastInputEventWasWordNav():
            msg = "DEFAULT: Presenting result of word nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.sayWord(obj)
            return

        if self.utilities.lastInputEventWasCharNav():
            msg = "DEFAULT: Presenting result of char nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.sayCharacter(obj)
            return

        if self.utilities.lastInputEventWasPageNav():
            msg = "DEFAULT: Presenting result of page nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.sayLine(obj)
            return

        if self.utilities.lastInputEventWasLineBoundaryNav():
            msg = "DEFAULT: Presenting result of line boundary nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.sayCharacter(obj)
            return

        if self.utilities.lastInputEventWasFileBoundaryNav():
            msg = "DEFAULT: Presenting result of file boundary nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.sayLine(obj)
            return

        if self.utilities.lastInputEventWasPrimaryMouseRelease():
            start, end, string = self.utilities.getCachedTextSelection(event.source)
            if not string:
                msg = "DEFAULT: Presenting result of primary mouse button release"
                debug.println(debug.LEVEL_INFO, msg, True)
                self.sayLine(obj)
                return

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
        if text.getNSelections() > 0:
            text.setSelection(0, context.currentOffset, context.currentOffset)

    def inSayAll(self):
        if self._inSayAll:
            msg = "DEFAULT: In SayAll"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._sayAllIsInterrupted:
            msg = "DEFAULT: SayAll is interrupted"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "DEFAULT: Not in SayAll"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

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
            return False

        offset = text.caretOffset - 1
        previousOffset = text.caretOffset - 2
        if (offset < 0 or previousOffset < 0):
            return False

        [currentChar, startOffset, endOffset] = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        [previousChar, startOffset, endOffset] = \
            text.getTextAtOffset(previousOffset, pyatspi.TEXT_BOUNDARY_CHAR)
        if not self.utilities.isSentenceDelimiter(currentChar, previousChar):
            return False

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
            return False
        else:
            sentence = self.utilities.substring(obj, sentenceStartOffset + 1,
                                         sentenceEndOffset + 1)

        voice = self.speechGenerator.voice(string=sentence)
        sentence = self.utilities.adjustForRepeats(sentence)
        speech.speak(sentence, voice)
        return True

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
            return False

        if not offset:
            if text.caretOffset == -1:
                offset = text.characterCount
            else:
                offset = text.caretOffset - 1

        if (offset < 0):
            return False

        [char, startOffset, endOffset] = \
            text.getTextAtOffset( \
                offset,
                pyatspi.TEXT_BOUNDARY_CHAR)
        if not self.utilities.isWordDelimiter(char):
            return False

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
            return False
        else:
            word = self.utilities.\
                substring(obj, wordStartOffset + 1, wordEndOffset + 1)

        voice = self.speechGenerator.voice(string=word)
        word = self.utilities.adjustForRepeats(word)
        speech.speak(word, voice)
        return True

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

        speakBlankLines = _settingsManager.getSetting('speakBlankLines')
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

        [line, caretOffset, startOffset] = self.getTextLineAtCaret(obj)
        if len(line) and line != "\n":
            result = self.utilities.indentationDescription(line)
            if result:
                self.speakMessage(result)

            voice = self.speechGenerator.voice(string=line)
            line = self.utilities.adjustForLinks(obj, line, startOffset)
            line = self.utilities.adjustForRepeats(line)
            utterance = [line]
            utterance.extend(voice)
            speech.speak(utterance)
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
            result = self.utilities.indentationDescription(phrase)
            if result:
                self.speakMessage(result)

            voice = self.speechGenerator.voice(string=phrase)
            phrase = self.utilities.adjustForRepeats(phrase)
            utterance = [phrase]
            utterance.extend(voice)
            speech.speak(utterance)
        else:
            self.speakCharacter(phrase)

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


        self.speakMisspelledIndicator(obj, startOffset)

        voice = self.speechGenerator.voice(string=word)
        word = self.utilities.adjustForRepeats(word)
        self._lastWord = word
        speech.speak(word, voice)

    def presentObject(self, obj, **args):
        interrupt = args.get("interrupt", False)
        self.updateBraille(obj, **args)
        utterances = self.speechGenerator.generateSpeech(obj, **args)
        speech.speak(utterances, interrupt=interrupt)

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
            self.flatReviewContext = flat_review.Context(self)
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
        is non-0, then an attempt will be made to position the review cursor
        at that cell.  Otherwise, we will pan in display-sized increments
        to show the review cursor."""

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: update review disabled", True)
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
        if offset is None:
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

        priorObj = obj

        # Get the next line of text to read
        #
        done = False
        while not done:
            speech.speak(self.speechGenerator.generateContext(obj, priorObj=priorObj))

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

                if endOffset > text.characterCount:
                    msg = "WARNING: endOffset: %i > characterCount: %i " \
                          " resulting from text.getTextAtOffset(%i, %s) for %s" \
                          % (endOffset, text.characterCount, offset, mode, obj)
                    debug.println(debug.LEVEL_INFO, msg, True)
                    endOffset = text.characterCount

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

                voice = self.speechGenerator.voice(string=lineString)
                if voice and isinstance(voice, list):
                    voice = voice[0]

                lineString = \
                    self.utilities.adjustForLinks(obj, lineString, startOffset)
                lineString = self.utilities.adjustForRepeats(lineString)

                context = speechserver.SayAllContext(
                    obj, lineString, startOffset, endOffset)
                self._sayAllContexts.append(context)
                eventsynthesizer.scrollIntoView(obj, startOffset, endOffset)
                yield [context, voice]

            moreLines = False
            relations = obj.getRelationSet()
            for relation in relations:
                if relation.getRelationType() == pyatspi.RELATION_FLOWS_TO:
                    priorObj = obj
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

        msg = "DEFAULT: textLines complete. Verifying SayAll status"
        debug.println(debug.LEVEL_INFO, msg, True)
        self.inSayAll()

    def getTextLineAtCaret(self, obj, offset=None, startOffset=None, endOffset=None):
        """To-be-removed. Returns the string, caretOffset, startOffset."""

        try:
            text = obj.queryText()
        except NotImplementedError:
            return ["", 0, 0]

        targetOffset = startOffset
        if targetOffset is None:
            targetOffset = max(0, text.caretOffset)

        # The offset might be positioned at the very end of the text area.
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
        if targetOffset == text.characterCount:
            fixedTargetOffset = max(0, targetOffset - 1)
            character = text.getText(fixedTargetOffset, fixedTargetOffset + 1)
        else:
            fixedTargetOffset = targetOffset
            character = None

        if (targetOffset == text.characterCount) \
            and (character == "\n"):
            lineString = ""
            startOffset = fixedTargetOffset
        else:
            # Get the line containing the caret.  [[[TODO: HACK WDW - If
            # there's only 1 character in the string, well, we get it.  We
            # do this because Gecko's implementation of getTextAtOffset
            # is broken if there is just one character in the string.]]]
            #
            if (text.characterCount == 1):
                lineString = text.getText(fixedTargetOffset, fixedTargetOffset + 1)
                startOffset = fixedTargetOffset
            else:
                if fixedTargetOffset == -1:
                    fixedTargetOffset = text.characterCount
                try:
                    [lineString, startOffset, endOffset] = text.getTextAtOffset(
                        fixedTargetOffset, pyatspi.TEXT_BOUNDARY_LINE_START)
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
            voice = self.speechGenerator.voice(string=character)
            phoneticString = phonnames.getPhoneticName(character.lower())
            speech.speak(phoneticString, voice)

    def _saveLastCursorPosition(self, obj, caretOffset):
        """Save away the current text cursor position for next time.

        Arguments:
        - obj: the current accessible
        - caretOffset: the cursor position within this object
        """

        self.pointOfReference["lastCursorPosition"] = [obj, caretOffset]

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

        if _settingsManager.getSetting('speakMisspelledIndicator'):
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

        msg = "DEFAULT: Interrupting presentation"
        debug.println(debug.LEVEL_INFO, msg, True)
        speech.stop()
        braille.killFlash()

    def presentKeyboardEvent(self, event):
        """Convenience method to present the KeyboardEvent event. Returns True
        if we fully present the event; False otherwise."""

        if not event.isPressedKey():
            self._sayAllIsInterrupted = False
            self.utilities.clearCachedCommandState()

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

        if role == pyatspi.ROLE_PASSWORD_TEXT and not event.isLockingKey():
            return False

        if not event.isPressedKey():
            return False

        braille.displayKeyEvent(event)
        orcaModifierPressed = event.isOrcaModifier() and event.isPressedKey()
        if event.isCharacterEchoable() and not orcaModifierPressed:
            return False
        if orca_state.learnModeEnabled:
            if event.isPrintableKey() and event.getClickCount() == 2:
                self.phoneticSpellCurrentItem(event.event_string)
                return True

        string = None
        if event.isPrintableKey():
            string = event.event_string

        msg = "DEFAULT: Presenting keyboard event"
        debug.println(debug.LEVEL_INFO, msg, True)

        voice = self.speechGenerator.voice(string=string)
        speech.speakKeyEvent(event, voice)
        return True

    def presentMessage(self, fullMessage, briefMessage=None, voice=None, resetStyles=True, force=False):
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
            if not _settingsManager.getSetting('messagesAreDetailed'):
                message = briefMessage
            else:
                message = fullMessage
            if message:
                self.speakMessage(message, voice=voice, resetStyles=resetStyles, force=force)

        if (_settingsManager.getSetting('enableBraille') \
             or _settingsManager.getSetting('enableBrailleMonitor')) \
           and _settingsManager.getSetting('enableFlashMessages'):
            if not _settingsManager.getSetting('flashIsDetailed'):
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
    def __play(sounds, interrupt=True):
        if not sounds:
            return

        if not isinstance(sounds, list):
            icon = [sounds]

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
            debug.println(debug.LEVEL_INFO, "BRAILLE: display message disabled", True)
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
            debug.println(debug.LEVEL_INFO, "BRAILLE: display regions disabled", True)
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
            debug.println(debug.LEVEL_INFO, "BRAILLE: update caret disabled", True)
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

        voice = self.speechGenerator.voice(string=character)
        speech.speakCharacter(character, voice)

    def speakMessage(self, string, voice=None, interrupt=True, resetStyles=True, force=False):
        """Method to speak a single string. Scripts should use this
        method rather than calling speech.speak directly.

        - string: The string to be spoken.
        - voice: The voice to use. By default, the "system" voice will
          be used.
        - interrupt: If True, any current speech should be interrupted
          prior to speaking the new text.
        """

        if not _settingsManager.getSetting('enableSpeech') \
           or (_settingsManager.getSetting('onlySpeakDisplayedText') and not force):
            return

        voices = _settingsManager.getSetting('voices')
        systemVoice = voices.get(settings.SYSTEM_VOICE)

        voice = voice or systemVoice
        if voice == systemVoice and resetStyles:
            capStyle = _settingsManager.getSetting('capitalizationStyle')
            _settingsManager.setSetting('capitalizationStyle', settings.CAPITALIZATION_STYLE_NONE)
            speech.updateCapitalizationStyle()

            punctStyle = _settingsManager.getSetting('verbalizePunctuationStyle')
            _settingsManager.setSetting('verbalizePunctuationStyle', settings.PUNCTUATION_STYLE_NONE)
            speech.updatePunctuationLevel()

        speech.speak(string, voice, interrupt)

        if voice == systemVoice and resetStyles:
            _settingsManager.setSetting('capitalizationStyle', capStyle)
            speech.updateCapitalizationStyle()

            _settingsManager.setSetting('verbalizePunctuationStyle', punctStyle)
            speech.updatePunctuationLevel()

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
        At the moment it just announces the character unicode number but
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

    def presentSizeAndPosition(self, inputEvent):
        """ Presents the size and position of the locusOfFocus. """

        if self.flatReviewContext:
            obj = self.flatReviewContext.getCurrentAccessible()
        else:
            obj = orca_state.locusOfFocus

        x, y, width, height = self.utilities.getBoundingBox(obj)
        if (x, y, width, height) == (-1, -1, 0, 0):
            full = messages.LOCATION_NOT_FOUND_FULL
            brief = messages.LOCATION_NOT_FOUND_BRIEF
            self.presentMessage(full, brief)
            return True

        full = messages.SIZE_AND_POSITION_FULL % (width, height, x, y)
        brief = messages.SIZE_AND_POSITION_BRIEF % (width, height, x, y)
        self.presentMessage(full, brief)
        return True
