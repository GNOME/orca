# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""The default Script for presenting information to the user using
both speech and Braille.  This is based primarily on the de-facto
standard implementation of the AT-SPI, which is the GAIL support
for GTK."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import time

import atspi
import braille
import debug
import flat_review
import input_event
import keybindings
import mag
import orca
import orca_state
import rolenames
import script
import settings
import speech
import speechserver
import util

from orca_i18n import _                          # for gettext support

########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Script(script.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        script.Script.__init__(self, app)

        self.flatReviewContext  = None
        self.windowActivateTime = None
        self.lastReviewCurrentEvent = None

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        self.leftClickReviewItemHandler = input_event.InputEventHandler(
            Script.leftClickReviewItem,
            _("Performs left click on current flat review item."))

        self.rightClickReviewItemHandler = input_event.InputEventHandler(
            Script.rightClickReviewItem,
            _("Performs right click on current flat review item."))

        self.sayAllHandler = input_event.InputEventHandler(
            Script.sayAll,
            _("Speaks entire document."))

        self.whereAmIHandler = input_event.InputEventHandler(
            Script.whereAmI,
            _("Performs the where am I operation."))

        self.showZonesHandler = input_event.InputEventHandler(
            Script.showZones,
            _("Paints and prints the visible zones in the active window."))

        self.toggleFlatReviewModeHandler = input_event.InputEventHandler(
            Script.toggleFlatReviewMode,
            _("Enters and exits flat review mode."))

        self.reviewPreviousLineHandler = input_event.InputEventHandler(
            Script.reviewPreviousLine,
            _("Moves flat review to the beginning of the previous line."))

        self.reviewHomeHandler = input_event.InputEventHandler(
            Script.reviewHome,
            _("Moves flat review to the home position."))

        self.reviewCurrentLineHandler = input_event.InputEventHandler(
            Script.reviewCurrentLine,
            _("Speaks the current flat review line."))

        self.reviewNextLineHandler = input_event.InputEventHandler(
                Script.reviewNextLine,
                _("Moves flat review to the beginning of the next line."))

        self.reviewEndHandler = input_event.InputEventHandler(
            Script.reviewEnd,
            _("Moves flat review to the end position."))

        self.reviewPreviousItemHandler = input_event.InputEventHandler(
            Script.reviewPreviousItem,
            _("Moves flat review to the previous item or word."))

        self.reviewAboveHandler = input_event.InputEventHandler(
            Script.reviewAbove,
            _("Moves flat review to the word above the current word."))

        self.reviewCurrentItemHandler = input_event.InputEventHandler(
            Script.reviewCurrentItem,
            _("Speaks or spells the current flat review item or word."))

        self.reviewCurrentAccessibleHandler = input_event.InputEventHandler(
            Script.reviewCurrentAccessible,
            _("Speaks the current flat review object."))

        self.reviewNextItemHandler = input_event.InputEventHandler(
            Script.reviewNextItem,
            _("Moves flat review to the next item or word."))

        self.reviewBelowHandler = input_event.InputEventHandler(
            Script.reviewBelow,
            _("Moves flat review to the word below the current word."))

        self.reviewPreviousCharacterHandler = input_event.InputEventHandler(
            Script.reviewPreviousCharacter,
            _("Moves flat review to the previous character."))

        self.reviewEndOfLineHandler = input_event.InputEventHandler(
            Script.reviewEndOfLine,
            _("Moves flat review to the end of the line."))

        self.reviewCurrentCharacterHandler = input_event.InputEventHandler(
            Script.reviewCurrentCharacter,
            _("Speaks the current flat review character."))

        self.reviewNextCharacterHandler = input_event.InputEventHandler(
            Script.reviewNextCharacter,
            _("Moves flat review to the next character."))

        self.toggleTableCellReadModeHandler = input_event.InputEventHandler(
            Script.toggleTableCellReadMode,
            _("Toggles whether to read just the current table cell or the whole row."))

        self.readCharAttributesHandler = input_event.InputEventHandler(
            Script.readCharAttributes,
            _("Reads the attributes associated with the current text character."))

        self.reportScriptInfoHandler = input_event.InputEventHandler(
            Script.reportScriptInfo,
            _("Reports information on current script."))

        self.panBrailleLeftHandler = input_event.InputEventHandler(
            Script.panBrailleLeft,
            _("Pans the braille display to the left."))

        self.panBrailleRightHandler = input_event.InputEventHandler(
            Script.panBrailleRight,
            _("Pans the braille display to the right."))

        self.reviewBottomLeftHandler = input_event.InputEventHandler(
            Script.reviewBottomLeft,
            _("Moves flat review to the bottom left."))

        self.goBrailleHomeHandler = input_event.InputEventHandler(
            Script.goBrailleHome,
            _("Returns to object with keyboard focus."))

        self.enterLearnModeHandler = input_event.InputEventHandler(
            Script.enterLearnMode,
            _("Enters learn mode.  Press escape to exit learn mode."))

        self.exitLearnModeHandler = input_event.InputEventHandler(
            Script.exitLearnMode,
            _("Exits learn mode."))

        self.decreaseSpeechRateHandler = input_event.InputEventHandler(
            speech.decreaseSpeechRate,
            _("Decreases the speech rate."))

        self.increaseSpeechRateHandler = input_event.InputEventHandler(
            speech.increaseSpeechRate,
            _("Increases the speech rate."))

        self.decreaseSpeechPitchHandler = input_event.InputEventHandler(
            speech.decreaseSpeechPitch,
            _("Decreases the speech pitch."))

        self.increaseSpeechPitchHandler = input_event.InputEventHandler(
            speech.increaseSpeechPitch,
            _("Increases the speech pitch."))

        self.shutdownHandler = input_event.InputEventHandler(
            orca.shutdown,
            _("Quits Orca"))

        self.keystrokeRecordingHandler = input_event.InputEventHandler(
            orca.toggleKeystrokeRecording,
            _("Toggles keystroke recording on and off."))

        self.preferencesSettingsHandler = input_event.InputEventHandler(
            orca._showPreferencesGUI,
            _("Displays the preferences configuration dialog."))

        self.loadUserSettingsHandler = input_event.InputEventHandler(
            orca.loadUserSettings,
            _("Reloads user settings and reinitializes services as necessary."))

        self.toggleSilenceSpeechHandler = input_event.InputEventHandler(
            orca._toggleSilenceSpeech,
            _("Toggles the silencing of speech."))

        self.listAppsHandler = input_event.InputEventHandler(
            orca.printApps,
            _("Prints a debug listing of all known applications to the console where Orca is running."))

        self.cycleDebugLevelHandler = input_event.InputEventHandler(
            orca.cycleDebugLevel,
            _("Cycles the debug level at run time."))

        self.printActiveAppHandler = input_event.InputEventHandler(
            orca.printActiveApp,
            _("Prints debug information about the currently active application to the console where Orca is running."))

        self.printAncestryHandler = input_event.InputEventHandler(
            orca.printAncestry,
            _("Prints debug information about the ancestry of the object with focus"))

        self.printHierarchyHandler = input_event.InputEventHandler(
            orca.printHierarchy,
            _("Prints debug information about the application with focus"))

        self.nextPresentationManagerHandler = input_event.InputEventHandler(
            orca._switchToNextPresentationManager,
            _("Switches to the next presentation manager."))

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = script.Script.getListeners(self)
        listeners["focus:"]                                 = \
            self.onFocus
        #listeners["keyboard:modifiers"]                     = \
        #    self.noOp
        listeners["object:property-change:accessible-name"] = \
            self.onNameChanged
        listeners["object:text-caret-moved"]                = \
            self.onCaretMoved
        listeners["object:text-changed:delete"]             = \
            self.onTextDeleted
        listeners["object:text-changed:insert"]             = \
            self.onTextInserted
        listeners["object:text-selection-changed"]          = \
            self.noOp
        listeners["object:active-descendant-changed"]       = \
            self.onActiveDescendantChanged
        listeners["object:children-changed:"]               = \
            self.noOp
        listeners["object:link-selected"]                   = \
            self.onLinkSelected
        listeners["object:state-changed:"]                  = \
            self.onStateChanged
        listeners["object:selection-changed"]               = \
            self.onSelectionChanged
        listeners["object:property-change:accessible-value"] = \
            self.onValueChanged
        listeners["object:property-change"]                 = \
            self.noOp
        listeners["object:value-changed:"]                  = \
            self.onValueChanged
        listeners["object:visible-changed"]                 = \
            self.noOp
        listeners["window:activate"]                        = \
            self.onWindowActivated
        listeners["window:create"]                          = \
            self.noOp
        listeners["window:deactivate"]                      = \
            self.onWindowDeactivated
        listeners["window:destroy"]                         = \
            self.noOp
        listeners["window:maximize"]                        = \
            self.noOp
        listeners["window:minimize"]                        = \
            self.noOp
        listeners["window:rename"]                          = \
            self.noOp
        listeners["window:restore"]                         = \
            self.noOp
        listeners["window:switch"]                          = \
            self.noOp
        listeners["window:titlelize"]                       = \
            self.noOp

        return listeners

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """
        keyBindings = script.Script.getKeyBindings(self)

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Divide",
                0,
                0,
                self.leftClickReviewItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Multiply",
                0,
                0,
                self.rightClickReviewItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                0,
                0,
                self.sayAllHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                0,
                0,
                self.whereAmIHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "Num_Lock",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.showZonesHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Subtract",
                0,
                0,
                self.toggleFlatReviewModeHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_7",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewPreviousLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewPreviousLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_7",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewHomeHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewHomeHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_8",
                0,
                0,
                self.reviewCurrentLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                0,
                0,
                self.reviewCurrentLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_9",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewNextLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewNextLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_9",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewEndHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewEndHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_4",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewPreviousItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewPreviousItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_4",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewAboveHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewAboveHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewCurrentItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewCurrentItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewCurrentAccessibleHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewCurrentAccessibleHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_6",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewNextItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewNextItemHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_6",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewBelowHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewBelowHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_1",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewPreviousCharacterHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_End",
                1 << settings.MODIFIER_ORCA,
                0,
                self.reviewPreviousCharacterHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_1",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewEndOfLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_End",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reviewEndOfLineHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_2",
                0,
                0,
                self.reviewCurrentCharacterHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                0,
                0,
                self.reviewCurrentCharacterHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_3",
                0,
                0,
                self.reviewNextCharacterHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Down",
                0,
                0,
                self.reviewNextCharacterHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F11",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.toggleTableCellReadModeHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "SunF36",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.toggleTableCellReadModeHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "f",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.readCharAttributesHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F3",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.reportScriptInfoHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F1",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.enterLearnModeHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.decreaseSpeechRateHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.increaseSpeechRateHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.decreaseSpeechPitchHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "Up",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.increaseSpeechPitchHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "q",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.shutdownHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "Pause",
                0,
                0,
                self.keystrokeRecordingHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                (1 << settings.MODIFIER_ORCA | \
                     1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << settings.MODIFIER_ORCA,
                self.preferencesSettingsHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                (1 << settings.MODIFIER_ORCA | \
                     1 << atspi.Accessibility.MODIFIER_CONTROL),
                (1 << settings.MODIFIER_ORCA | \
                     1 << atspi.Accessibility.MODIFIER_CONTROL),
                self.loadUserSettingsHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "s",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.toggleSilenceSpeechHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F5",
                (1 << settings.MODIFIER_ORCA | \
                     1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << settings.MODIFIER_ORCA,
                self.listAppsHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F4",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.cycleDebugLevelHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F6",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.printActiveAppHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F7",
                (1 << settings.MODIFIER_ORCA | \
                     1 << atspi.Accessibility.MODIFIER_CONTROL),
                1 << settings.MODIFIER_ORCA,
                self.printAncestryHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F8",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.printHierarchyHandler))

        keyBindings.add(
            keybindings.KeyBinding(
                "F10",
                1 << settings.MODIFIER_ORCA, \
                1 << settings.MODIFIER_ORCA,
                self.nextPresentationManagerHandler))

        return keyBindings

    def getBrailleBindings(self):
        """Defines the braille bindings for this script.

        Returns a dictionary where the keys are BrlTTY commands and the
        values are InputEventHandler instances.
        """
        brailleBindings = script.Script.getBrailleBindings(self)
        brailleBindings[braille.CMD_FWINLT]   = self.panBrailleLeftHandler
        brailleBindings[braille.CMD_FWINRT]   = self.panBrailleRightHandler
        brailleBindings[braille.CMD_LNUP]     = self.reviewAboveHandler
        brailleBindings[braille.CMD_LNDN]     = self.reviewBelowHandler
        brailleBindings[braille.CMD_TOP_LEFT] = self.reviewHomeHandler
        brailleBindings[braille.CMD_BOT_LEFT] = self.reviewBottomLeftHandler
        brailleBindings[braille.CMD_HOME]     = self.goBrailleHomeHandler

        return brailleBindings

    def processObjectEvent(self, event):
        """Processes all object events of interest to this script.  Note
        that this script may be passed events it doesn't care about, so
        it needs to react accordingly.

        Arguments:
        - event: the Event
        """

        # If we receive a "window:deactivate" event for the object that
        # currently has focus, then stop the current speech output.
        # This is very useful for terminating long speech output from
        # commands running in gnome-terminal.
        #
        if event.type.find("window:deactivate") != -1:
            if orca_state.locusOfFocus \
                and (orca_state.locusOfFocus.app == event.source.app):
                speech.stop()

        # [[[TODO: WDW - HACK to set Orca's locusOfFocus if we've somehow
        # gotten out of whack.  This typically happens when going into an
        # application and we only get a window activated event for it, even
        # if one of its children has focus.  Since we're doing this, we'll
        # tell Orca to not propagate this event to us.]]]
        #
        if event and event.source \
            and (event.source != orca_state.locusOfFocus) \
            and ((event.type.find("object:selection-changed") != -1) \
                 or (event.type.find("object:text-changed") != -1)) \
            and event.source.state.count(atspi.Accessibility.STATE_FOCUSED):
            # Avoid doing this with objects that manage their descendants
            # because they'll issue a descendant changed event.
            #
            if event.source.state.count(
                atspi.Accessibility.STATE_MANAGES_DESCENDANTS) == 0:
                orca.setLocusOfFocus(event, event.source, False)

        script.Script.processObjectEvent(self, event)

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event. It uses the super
        class equivalent to do most of the work. The only thing done here
        is to detect when the user is trying to get out of learn mode.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

        if (keyboardEvent.type == atspi.Accessibility.KEY_PRESSED_EVENT) and \
           (keyboardEvent.event_string == "Escape"):
            settings.learnModeEnabled = False

        return script.Script.processKeyboardEvent(self, keyboardEvent)

    def __sayAllProgressCallback(self, context, type):
        # [[[TODO: WDW - this needs work.  Need to be able to manage
        # the monitoring of progress and couple that with both updating
        # the visual progress of what is being spoken as well as
        # positioning the cursor when speech has stopped.]]]
        #
        if type == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            #obj = context.obj
            #[x, y, width, height] = obj.text.getCharacterExtents(
            #    context.currentOffset, 0)
            #print context.currentOffset, x, y, width, height
            #util.drawOutline(x, y, width, height)
            pass
        elif type == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            context.obj.text.setCaretOffset(context.currentOffset);
        elif type == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            context.obj.text.setCaretOffset(context.currentOffset);

    def sayAll(self, inputEvent):
        if not orca_state.locusOfFocus:
            pass
        elif orca_state.locusOfFocus.text:
            speech.sayAll(util.textLines(orca_state.locusOfFocus),
                          self.__sayAllProgressCallback)
        else:
            speech.speakUtterances(
                self.speechGenerator.getSpeech(orca_state.locusOfFocus, False))
        return True

    def sayPhrase(self, obj, startOffset, endOffset):
        """Speaks the text of an Accessible object between the start and
        end offsets, unless the phrase is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - startOffset: the start text offset.
        - endOffset: the end text offset.
        """

        # Swap values if in wrong order (StarOffice is fussy about that).
        #
        if ((startOffset > endOffset) and (endOffset != -1)) or \
           (startOffset == -1):
            temp = endOffset
            endOffset = startOffset
            startOffset = temp

        phrase = obj.text.getText(startOffset, endOffset)

        if len(phrase) != 0:
            if phrase.isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            speech.speak(phrase, voice)
            util.speakTextSelectionState(obj, startOffset, endOffset)

    def sayLine(self, obj):
        """Speaks the line of an AccessibleText object that contains the
        caret, unless the line is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        # Get the AccessibleText interface of the provided object
        #
        [line, startOffset, endOffset] = util.getTextLineAtCaret(obj)

        if len(line) != 0:
            if line.isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            if settings.enableSpeechIndentation:
                self.speakTextIndentation(obj, line)
            speech.speak(line, voice)
            util.speakTextSelectionState(obj, startOffset, endOffset)

    def sayWord(self, obj):
        """Speaks the word at the caret.  [[[TODO: WDW - what if there is no
        word at the caret?]]]

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        text = obj.text
        offset = text.caretOffset
        [word, startOffset, endOffset] = \
            text.getTextAtOffset(offset,
                                 atspi.Accessibility.TEXT_BOUNDARY_WORD_START)

        if util.getLinkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        speech.speak(word, voice)
        util.speakTextSelectionState(obj, startOffset, endOffset)

    def speakTextIndentation(self, obj, line):
        """Speaks a summary of the number of spaces and/or tabs at the
        beginning of the given line.

        Arguments:
        - obj: the text object.
        - line: the string to check for spaces and tabs.
        """

        # For the purpose of speaking the text indentation, replace
        # occurances of '\302\240' (non breaking space) with spaces.
        #
        line = line.replace("\302\240",  " ")

        spaceCount = 0
        tabCount = 0
        for offset in range(0, len(line)):
            if line[offset] == ' ':
                spaceCount += 1
            elif line[offset] == '\t':
                tabCount += 1
            else:
                break

        utterance = ''
        if spaceCount:
            if spaceCount == 1:
                utterance += "1 space "
            else:
                utterance += ("%d spaces " % spaceCount)
        if tabCount:
            if tabCount == 1:
                utterance += "1 tab "
            else:
                utterance += ("%d tabs " % tabCount)
        if len(utterance):
            speech.speak(utterance)

    def echoPreviousWord(self, obj):
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
        """

        text = obj.text

        # Check for a bunch of preconditions we care about
        #
        if not text:
            return

        offset = text.caretOffset - 1
        if (offset < 0):
            return

        [char, startOffset, endOffset] = \
            text.getTextAtOffset( \
                offset,
                atspi.Accessibility.TEXT_BOUNDARY_CHAR)
        if not util.isWordDelimiter(char):
            return

        # OK - we seem to be cool so far.  So...starting with what
        # should be the last character in the word (caretOffset - 2),
        # work our way to the beginning of the word, stopping when
        # we hit another word delimiter.
        #
        wordEndOffset = text.caretOffset - 2
        wordStartOffset = wordEndOffset

        while wordStartOffset >= 0:
            [char, startOffset, endOffset] = \
                text.getTextAtOffset( \
                    wordStartOffset,
                    atspi.Accessibility.TEXT_BOUNDARY_CHAR)
            if util.isWordDelimiter(char):
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
            word = text.getText(wordStartOffset + 1, wordEndOffset + 1)

        if util.getLinkIndex(obj, wordStartOffset + 1) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        speech.speak(word, voice)

    def sayCharacter(self, obj):
        """Speak the character under the caret.  [[[TODO: WDW - isn't the
        caret between characters?]]]

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        text = obj.text
        offset = text.caretOffset

        # If we have selected text and the last event was a move to the
        # right, then speak the character to the left of where the text
        # caret is (i.e. the selected character).
        #
        mods = orca_state.lastInputEvent.modifiers
        shiftMask = 1 << atspi.Accessibility.MODIFIER_SHIFT
        if (mods & shiftMask) \
            and orca_state.lastInputEvent.event_string == "Right":
            startOffset = offset-1
            endOffset = offset
        else:
            startOffset = offset
            endOffset = offset+1
        character = text.getText(startOffset, endOffset)

        if util.getLinkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif character.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        speech.speak(character, voice)
        util.speakTextSelectionState(obj, startOffset, endOffset)

    def whereAmI(self, inputEvent):
        self.updateBraille(orca_state.locusOfFocus)

        verbosity = settings.speechVerbosityLevel

        utterances = []

        utterances.extend(
            self.speechGenerator.getSpeechContext(orca_state.locusOfFocus))

        # Now, we'll treat table row and column headers as context
        # as well.  This requires special handling because we're
        # making headers seem hierarchical in the context, but they
        # are not hierarchical in the containment hierarchicy.
        # We also only want to speak the one that changed.  If both
        # changed, first speak the row header, then the column header.
        #
        # We also keep track of tree level depth and only announce
        # that if it changes.
        #
        if orca_state.locusOfFocus.role == rolenames.ROLE_TABLE_CELL:
            parent = orca_state.locusOfFocus.parent
            if parent and parent.table:
                table = parent.table
                row = table.getRowAtIndex(orca_state.locusOfFocus.index)
                col = table.getColumnAtIndex(orca_state.locusOfFocus.index)

                desc = parent.table.getRowDescription(row)
                if desc and len(desc):
                    text = desc
                    if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                                + rolenames.rolenames[\
                                        rolenames.ROLE_ROW_HEADER].speech
                        utterances.append(text)

                desc = parent.table.getColumnDescription(col)
                if desc and len(desc):
                    text = desc
                    if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                                + rolenames.rolenames[\
                                        rolenames.ROLE_COLUMN_HEADER].speech
                        utterances.append(text)

        # Get the text for the object itself.
        #
        utterances.extend(
            self.speechGenerator.getSpeech(orca_state.locusOfFocus, False))

        # Now speak the tree node level.
        #
        level = util.getNodeLevel(orca_state.locusOfFocus)
        if level >= 0:
            utterances.append(_("tree level %d") % (level + 1))

        if orca_state.locusOfFocus.state.count(\
                    atspi.Accessibility.STATE_SENSITIVE) == 0:
            message = _("No focus")
            utterances.extend(message)

        speech.speakUtterances(utterances)

        return True

    def findCommonAncestor(self, a, b):
        """Finds the common ancestor between Accessible a and Accessible b.

        Arguments:
        - a: Accessible
        - b: Accessible
        """

        debug.println(debug.LEVEL_FINEST,
                      "default.findCommonAncestor...")

        if (not a) or (not b):
            return None

        if a == b:
            return a

        aParents = [a]
        try:
            parent = a.parent
            while parent and (parent.parent != parent):
                aParents.append(parent)
                parent = parent.parent
            aParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)
            pass

        bParents = [b]
        try:
            parent = b.parent
            while parent and (parent.parent != parent):
                bParents.append(parent)
                parent = parent.parent
            bParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)
            pass

        commonAncestor = None

        maxSearch = min(len(aParents), len(bParents))
        i = 0
        while i < maxSearch:
            if aParents[i] == bParents[i]:
                commonAncestor = aParents[i]
                i += 1
            else:
                break

        debug.println(debug.LEVEL_FINEST,
                      "...default.findCommonAncestor")

        return commonAncestor

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        if newLocusOfFocus:
            mag.magnifyAccessible(event, newLocusOfFocus)

        # We always automatically go back to focus tracking mode when
        # the focus changes.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # [[[TODO: WDW - HACK because parents that manage their descendants
        # can give us a different object each time we ask for the same
        # exact child.  So...we do a check here to see if the old object
        # and new object have the same index in the parent and if they
        # have the same name.  If so, then they are likely to be the same
        # object.  The reason we check for the name here is a small sanity
        # check.  This whole algorithm could fail because one might be
        # deleting/adding identical elements from/to a list or table, thus
        # the objects really could be different even though they seem the
        # same.  Logged as bug 319675.]]]
        #
        if oldLocusOfFocus:
            oldParent = oldLocusOfFocus.parent
        else:
            oldParent = None

        if newLocusOfFocus:
            newParent = newLocusOfFocus.parent
        else:
            newParent = None

        if newParent and (oldParent == newParent):
            state = newParent.state
            if state.count(atspi.Accessibility.STATE_MANAGES_DESCENDANTS) \
                and (oldLocusOfFocus.index == newLocusOfFocus.index) \
                and (oldLocusOfFocus.name == newLocusOfFocus.name):
                    return

        # Well...now that we got that behind us, let's do what we're supposed
        # to do.
        #
        if newLocusOfFocus:
            self.updateBraille(newLocusOfFocus)

            utterances = []

            # Now figure out how of the container context changed and
            # speech just what is different.
            #
            commonAncestor = self.findCommonAncestor(oldLocusOfFocus,
                                                     newLocusOfFocus)
            if commonAncestor:
                utterances.extend(
                    self.speechGenerator.getSpeechContext(newLocusOfFocus,
                                                          commonAncestor))

            # Now, we'll treat table row and column headers as context
            # as well.  This requires special handling because we're
            # making headers seem hierarchical in the context, but they
            # are not hierarchical in the containment hierarchicy.
            # We also only want to speak the one that changed.  If both
            # changed, first speak the row header, then the column header.
            #
            # We also keep track of tree level depth and only announce
            # that if it changes.
            #
            oldNodeLevel = -1
            newNodeLevel = -1
            if newLocusOfFocus.role == rolenames.ROLE_TABLE_CELL:
                if oldParent and oldParent.table:
                    table = oldParent.table
                    oldRow = table.getRowAtIndex(oldLocusOfFocus.index)
                    oldCol = table.getColumnAtIndex(oldLocusOfFocus.index)
                else:
                    oldRow = -1
                    oldCol = -1

                if newParent and newParent.table:
                    table = newParent.table
                    newRow = table.getRowAtIndex(newLocusOfFocus.index)
                    newCol = table.getColumnAtIndex(newLocusOfFocus.index)

                    if newRow != oldRow:
                        desc = newParent.table.getRowDescription(newRow)
                        if desc and len(desc):
                            text = desc
                            if settings.speechVerbosityLevel \
                                   == settings.VERBOSITY_LEVEL_VERBOSE:
                                text += " " \
                                        + rolenames.rolenames[\
                                        rolenames.ROLE_ROW_HEADER].speech
                            utterances.append(text)
                    if newCol != oldCol:
                        desc = newParent.table.getColumnDescription(newCol)
                        if desc and len(desc):
                            text = desc
                            if settings.speechVerbosityLevel \
                                   == settings.VERBOSITY_LEVEL_VERBOSE:
                                text += " " \
                                        + rolenames.rolenames[\
                                        rolenames.ROLE_COLUMN_HEADER].speech
                            utterances.append(text)

                oldNodeLevel = util.getNodeLevel(oldLocusOfFocus)
                newNodeLevel = util.getNodeLevel(newLocusOfFocus)

            # We'll also treat radio button groups as though they are
            # in a context, with the label for the group being the
            # name of the context.
            #
            if newLocusOfFocus.role == rolenames.ROLE_RADIO_BUTTON:
                radioGroupLabel = None
                inSameGroup = False
                relations = newLocusOfFocus.relations
                for relation in relations:
                    if (not radioGroupLabel) \
                        and (relation.getRelationType() \
                             == atspi.Accessibility.RELATION_LABELLED_BY):
                        radioGroupLabel = atspi.Accessible.makeAccessible(
                            relation.getTarget(0))
                    if (not inSameGroup) \
                        and (relation.getRelationType() \
                             == atspi.Accessibility.RELATION_MEMBER_OF):
                        for i in range(0, relation.getNTargets()):
                            target = atspi.Accessible.makeAccessible(
                                relation.getTarget(i))
                            if target == oldLocusOfFocus:
                                inSameGroup = True
                                break

                # We'll only announce the radio button group when we
                # switch groups.
                #
                if (not inSameGroup) and radioGroupLabel:
                    utterances.append(util.getDisplayedText(radioGroupLabel))

            # Get the text for the object itself.
            #
            utterances.extend(
                self.speechGenerator.getSpeech(newLocusOfFocus, False))

            # Now speak the new tree node level if it has changed.
            #
            if (oldNodeLevel != newNodeLevel) \
               and (newNodeLevel >= 0):
                utterances.append(_("tree level %d") % (newNodeLevel + 1))

            # We might be automatically speaking the unbound labels
            # in a dialog box as the result of the dialog box suddenly
            # appearing.  If so, don't interrupt this because of a
            # focus event that occurs when something like the "OK"
            # button gets focus shortly after the window appears.
            #
            shouldNotInterrupt = (event and event.type == "focus:") \
                and self.windowActivateTime \
                and ((time.time() - self.windowActivateTime) < 1.0)
            speech.speakUtterances(utterances, None, not shouldNotInterrupt)

            # If this is a table cell, save the current row and column
            # information in the table cell's table, so that we can use
            # it the next time.
            #
            if newLocusOfFocus.role == rolenames.ROLE_TABLE_CELL:
                if newParent and newParent.table:
                    table = newParent.table
                    column = table.getColumnAtIndex(newLocusOfFocus.index)
                    newParent.lastColumn = column
                    row = table.getRowAtIndex(newLocusOfFocus.index)
                    newParent.lastRow = row
        else:
            orca_state.noFocusTimeStamp = time.time()

    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.  This
        method should not be called for objects whose visual appearance
        changes solely because of focus -- setLocusOfFocus is used for that.
        Instead, it is intended mostly for objects whose notional 'value' has
        changed, such as a checkbox changing state, a progress bar advancing,
        a slider moving, text inserted, caret moved, etc.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        # We care if panels are suddenly showing.  The reason for this
        # is that some applications, such as Evolution, will bring up
        # a wizard dialog that uses "Forward" and "Backward" buttons
        # that change the contents of the dialog.  We only discover
        # this through showing events. [[[TODO: WDW - perhaps what we
        # really want is to speak unbound labels that are suddenly
        # showing?  event.detail == 1 means object is showing.]]]
        #
        # [[[TODO: WDW - I added the 'False' condition to prevent this
        # condition from ever working.  I wanted to keep the code around,
        # though, just in case we want to reuse it somewhere else.  The
        # bug that spurred all of this on is:
        #
        #    http://bugzilla.gnome.org/show_bug.cgi?id=338687
        #
        # The main problem is that the profile editor in gnome-terminal
        # ended up being very verbose and speaking lots of things it
        # should not have been speaking.]]]
        #
        if False and (obj.role == rolenames.ROLE_PANEL) \
               and (event.detail1 == 1) \
               and util.isInActiveApp(obj):

            # It's only showing if its parent is showing. [[[TODO: WDW -
            # HACK we stop at the application level because applications
            # never seem to have their showing state set.]]]
            #
            reallyShowing = True
            parent = obj.parent
            while reallyShowing \
                      and parent \
                      and (parent != parent.parent) \
                      and (parent.role != rolenames.ROLE_APPLICATION):
                debug.println(debug.LEVEL_FINEST,
                              "default.visualAppearanceChanged - " \
                              + "checking parent")
                reallyShowing = parent.state.count(\
                    atspi.Accessibility.STATE_SHOWING)
                parent = parent.parent

            # Find all the unrelated labels in the dialog and speak them.
            #
            if reallyShowing:
                utterances = []
                labels = util.findUnrelatedLabels(obj)
                for label in labels:
                    utterances.append(label.name)

                speech.speakUtterances(utterances)

                return

        # If this object is CONTROLLED_BY the object that currently
        # has focus, speak/braille this object.
        #
        relations = obj.relations
        for relation in relations:
            if relation.getRelationType() \
                   == atspi.Accessibility.RELATION_CONTROLLED_BY:
                target = atspi.Accessible.makeAccessible(relation.getTarget(0))
                if target == orca_state.locusOfFocus:
                    self.updateBraille(target)
                    speech.speakUtterances(
                        self.speechGenerator.getSpeech(target, True))
                    return

        # If this object is a label, and if it has a LABEL_FOR relation
        # to the focused object, then we should speak/braille the
        # focused object, as if it had just got focus.
        #
        if obj.role == rolenames.ROLE_LABEL:
            for relation in relations:
                if relation.getRelationType() \
                       == atspi.Accessibility.RELATION_LABEL_FOR:
                    target = \
                        atspi.Accessible.makeAccessible(relation.getTarget(0))
                    if target == orca_state.locusOfFocus:
                        self.updateBraille(target)
                        speech.speakUtterances(
                            self.speechGenerator.getSpeech(target, True))
                        return

        if obj != orca_state.locusOfFocus:
            return

        if event:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event='%s')" \
                          % (obj.name, obj.role, event.type))
        else:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event=None)" \
                          % (obj.name, obj.role))

        mag.magnifyAccessible(event, obj)
        self.updateBraille(obj)
        speech.speakUtterances(
            self.speechGenerator.getSpeech(event.source, True))

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not obj:
            return

        braille.clear()

        line = braille.Line()
        braille.addLine(line)

        # For multiline text areas, we only show the context if we
        # are on the very first line.  Otherwise, we show only the
        # line.
        #
        if obj.text \
            and ((obj.role == rolenames.ROLE_TEXT) \
                or (obj.role == rolenames.ROLE_PARAGRAPH)):
            text = obj.text
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            if startOffset == 0:
                line.addRegions(self.brailleGenerator.getBrailleContext(obj))
        else:
            line.addRegions(self.brailleGenerator.getBrailleContext(obj))

        result = self.brailleGenerator.getBrailleRegions(obj)
        line.addRegions(result[0])

        if extraRegion:
            line.addRegion(extraRegion)

        if extraRegion:
            braille.setFocus(extraRegion)
        else:
            braille.setFocus(result[1])

        braille.refresh(True)

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK to deal with quirky GTK+ menu behavior.
        # The problem is that when moving to submenus in a menu, the
        # menu gets focus first and then the submenu gets focus all
        # with a single keystroke.  So...focus in menus really means
        # that the object has focus *and* it is selected.  Now, this
        # assumes the selected state will be set before focus is given,
        # which appears to be the case from empirical analysis of the
        # event stream.  But of course, all menu items and menus in
        # the complete menu path will have their selected state set,
        # so, we really only care about the leaf menu or menu item
        # that it selected.]]]
        #
        role = event.source.role
        if (role == rolenames.ROLE_MENU) \
           or (role == rolenames.ROLE_MENU_ITEM) \
           or (role == rolenames.ROLE_CHECK_MENU_ITEM) \
           or (role == rolenames.ROLE_RADIO_MENU_ITEM):
            selection = event.source.selection
            if selection and selection.nSelectedChildren > 0:
                return

        # [[[TODO: WDW - HACK to deal with the fact that active cells
        # may or may not get focus.  Their parents, however, do tend to
        # get focus, but when the parent gets focus, it really means
        # that the selected child in it has focus.  Of course, this all
        # breaks when more than one child is selected.  Then, we really
        # need to depend upon the model where focus really works.]]]
        #
        newFocus = event.source

        if (event.source.role == rolenames.ROLE_LAYERED_PANE) \
            or (event.source.role == rolenames.ROLE_TABLE) \
            or (event.source.role == rolenames.ROLE_TREE_TABLE) \
            or (event.source.role == rolenames.ROLE_TREE):
            if event.source.childCount:
                # Well...we'll first see if there is a selection.  If there
                # is, we'll use it.
                #
                selection = event.source.selection
                if selection and selection.nSelectedChildren > 0:
                    newFocus = atspi.Accessible.makeAccessible(
                        selection.getSelectedChild(0))

                # Otherwise, we might have tucked away some information
                # for this thing in the onActiveDescendantChanged method.
                #
                elif event.source.__dict__.has_key("activeDescendantInfo"):
                    [parent, index] = event.source.activeDescendantInfo
                    newFocus = parent.child(index)

        orca.setLocusOfFocus(event, newFocus)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK because gnome-terminal issues a name changed
        # event for the edit preferences dialog even though the name really
        # didn't change.  I'm guessing this is going to be a vagary in all
        # of GTK+.]]]
        #
        if event.source and (event.source.role == rolenames.ROLE_DIALOG) \
           and (event.source == orca_state.locusOfFocus):
            return

        orca.visualAppearanceChanged(event, event.source)

    def _presentTextAtNewCaretPosition(self, event):

        if event.source:
            mag.magnifyAccessible(event, event.source)

        # Update the Braille display - if we can just reposition
        # the cursor, then go for it.
        #
        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) \
               and (region.accessible == event.source):
                if region.repositionCursor():
                    braille.refresh(True)
                    brailleNeedsRepainting = False
                break

        if brailleNeedsRepainting:
            self.updateBraille(event.source)

        if not orca_state.lastInputEvent:
            return

        if isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent):
            if not orca_state.lastInputEvent.pressed:
                self.sayLine(event.source)
            return

        # Guess why the caret moved and say something appropriate.
        # [[[TODO: WDW - this motion assumes traditional GUI
        # navigation gestures.  In an editor such as vi, line up and
        # down is done via other actions such as "i" or "j".  We may
        # need to think about this a little harder.]]]
        #
        if not isinstance(orca_state.lastInputEvent,
                          input_event.KeyboardEvent):
            return

        string = orca_state.lastInputEvent.event_string
        mods = orca_state.lastInputEvent.modifiers
        isControlKey = mods & (1 << atspi.Accessibility.MODIFIER_CONTROL)
        isShiftKey = mods & (1 << atspi.Accessibility.MODIFIER_SHIFT)
        hasLastPos = event.source.__dict__.has_key("lastCursorPosition")

        if (string == "Up") or (string == "Down"):
            # If the user has typed Shift-Up or Shift-Down, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise we speak the new line where the text cursor is
            # currently positioned.
            #
            if hasLastPos and isShiftKey and not isControlKey:
                self.sayPhrase(event.source, event.source.lastCursorPosition,
                               event.source.text.caretOffset)
            else:
                self.sayLine(event.source)

        elif (string == "Left") or (string == "Right"):
            # If the user has typed Control-Shift-Up or Control-Shift-Dowm,
            # then we want to speak the text that has just been selected
            # or unselected, otherwise if the user has typed Control-Left
            # or Control-Right, we speak the current word otherwise we speak
            # the character at the text cursor position.
            #
            if hasLastPos and isShiftKey and isControlKey:
                self.sayPhrase(event.source, event.source.lastCursorPosition,
                               event.source.text.caretOffset)
            elif isControlKey:
                self.sayWord(event.source)
            else:
                self.sayCharacter(event.source)

        elif string == "Page_Up":
            # If the user has typed Control-Shift-Page_Up, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Page_Up, then we
            # speak the character to the right of the current text cursor
            # position otherwise we speak the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                self.sayPhrase(event.source, event.source.lastCursorPosition,
                               event.source.text.caretOffset)
            elif isControlKey:
                self.sayCharacter(event.source)
            else:
                self.sayLine(event.source)

        elif string == "Page_Down":
            # If the user has typed Control-Shift-Page_Down, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has just typed Page_Down, then we speak
            # the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                self.sayPhrase(event.source, event.source.lastCursorPosition,
                               event.source.text.caretOffset)
            else:
                self.sayLine(event.source)

        elif (string == "Home") or (string == "End"):
            # If the user has typed Shift-Home or Shift-End, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Home or Control-End,
            # then we speak the current line otherwise we speak the character
            # to the right of the current text cursor position.
            #
            if hasLastPos and isShiftKey and not isControlKey:
                self.sayPhrase(event.source, event.source.lastCursorPosition,
                               event.source.text.caretOffset)
            elif isControlKey:
                self.sayLine(event.source)
            else:
                self.sayCharacter(event.source)

        elif (string == "A") and isControlKey:
            # The user has typed Control-A. Check to see if the entire
            # document has been selected, and if so, let the user know.
            #
            text = event.source.text
            charCount = text.characterCount
            for i in range(0, text.getNSelections()):
                [startSelOffset, endSelOffset] = text.getSelection(i)
                if text.caretOffset == 0 and \
                   startSelOffset == 0 and endSelOffset == charCount:
                    speech.speak(_("entire document selected"))

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

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

        self._presentTextAtNewCaretPosition(event)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

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
        if event.source.role == rolenames.ROLE_SLIDER:
            return

        self.updateBraille(event.source)

        # The any_data member of the event object has the deleted text in
        # it - If the last key pressed was a backspace or delete key,
        # speak the deleted text.  [[[TODO: WDW - again, need to think
        # about the ramifications of this when it comes to editors such
        # as vi or emacs.
        #
        if (not orca_state.lastInputEvent) \
            or \
            (not isinstance(orca_state.lastInputEvent,
                            input_event.KeyboardEvent)):
            return

        string = orca_state.lastInputEvent.event_string
        text = event.source.text
        if string == "BackSpace":
            # Speak the character that has just been deleted.
            #
            character = event.any_data.value()

        elif string == "Delete":
            # Speak the character to the right of the caret after
            # the current right character has been deleted.
            #
            offset = text.caretOffset
            [character, startOffset, endOffset] = \
                event.source.text.getTextAtOffset(
                    offset,
                    atspi.Accessibility.TEXT_BOUNDARY_CHAR)

        else:
            return

        if util.getLinkIndex(event.source, text.caretOffset) >= 0:
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

        # Ignore text insertions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was inserted.
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        # We'll also ignore sliders because we get their output via
        # their values changing.
        #
        if event.source.role == rolenames.ROLE_SLIDER:
            return

        self.updateBraille(event.source)

        text = event.any_data.value()

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
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            keyString = orca_state.lastInputEvent.event_string
            wasCommand = orca_state.lastInputEvent.modifiers \
                         & (1 << atspi.Accessibility.MODIFIER_CONTROL \
                            | 1 << atspi.Accessibility.MODIFIER_ALT \
                            | 1 << atspi.Accessibility.MODIFIER_META \
                            | 1 << atspi.Accessibility.MODIFIER_META2 \
                            | 1 << atspi.Accessibility.MODIFIER_META3)
            if (text == " " and keyString == "space") \
                or (text == keyString):
                pass
            elif wasCommand or \
                   (event.source.role == rolenames.ROLE_PASSWORD_TEXT):
                if text.isupper():
                    speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
                else:
                    speech.speak(text)

        if settings.enableEchoByWord and util.isWordDelimiter(text[-1:]):
            self.echoPreviousWord(event.source)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        child = atspi.Accessible.makeAccessible(event.any_data.value())
        orca.setLocusOfFocus(event, child)

        # We'll tuck away the activeDescendant information for future
        # reference since the AT-SPI gives us little help in finding
        # this.
        #
        if orca_state.locusOfFocus:
            event.source.activeDescendantInfo = \
                [orca_state.locusOfFocus.parent,
                 orca_state.locusOfFocus.index]
        elif event.source.__dict__.has_key("activeDescendantInfo"):
            del event.source.__dict__["activeDescendantInfo"]

    def onLinkSelected(self, event):
        """Called when a hyperlink is selected in a text area.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK one might think we could expect an
        # application to keep its name, but it appears as though
        # yelp has an identity problem and likes to start calling
        # itself "yelp," but then changes its name to "Mozilla"
        # on Fedora Core 4 after the user selects a link.  So, we'll
        # just assume that link-selected events always come from the
        # application with focus.]]]
        #
        #if orca_state.locusOfFocus \
        #   and (orca_state.locusOfFocus.app == event.source.app):
        #    orca.setLocusOfFocus(event, event.source)
        orca.setLocusOfFocus(event, event.source)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.  Currently, the
        state changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        # Do we care?
        #
        if state_change_notifiers.has_key(event.source.role):
            notifiers = state_change_notifiers[event.source.role]
            found = False
            for state in notifiers:
                if state and event.type.endswith(state):
                    found = True
                    break
            if found:
                orca.visualAppearanceChanged(event, event.source)

        # [[[TODO: WDW - HACK we'll handle this in the visual appearance
        # changed handler.]]]
        #
        # The object with focus might become insensitive, so we need to
        # flag that.  This typically occurs in wizard dialogs such as
        # the account setup assistant in Evolution.
        #
        #if event.type.endswith("sensitive") \
        #   and (event.detail1 == 0) \
        #   and event.source == orca_state.locusOfFocus:
        #    print "FOO INSENSITIVE"
        #    #orca.setLocusOfFocus(event, None)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        if not event.source:
            return

        # [[[TODO: WDW - HACK layered panes are nutty in that they
        # will change the selection and tell the selected child it is
        # focused, but the child will not issue a focus changed event.]]]
        #
        if event.source.role == rolenames.ROLE_LAYERED_PANE:
            if event.source.childCount:
                selection = event.source.selection
                if selection and selection.nSelectedChildren > 0:
                    child = selection.getSelectedChild(0)
                    if child:
                        orca.setLocusOfFocus(
                           event,
                           atspi.Accessible.makeAccessible(child))
        elif event.source.role == rolenames.ROLE_COMBO_BOX:
            orca.visualAppearanceChanged(event, event.source)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        # We'll let caret moved and text inserted events be used to
        # manage spin buttons, since they basically are text areas.
        #
        if event.source.role == rolenames.ROLE_SPIN_BUTTON:
            return

        # We'll also try to ignore those objects that keep telling
        # us their value changed even though it hasn't.
        #
        if event.source.value and event.source.__dict__.has_key("oldValue") \
           and (event.source.value.currentValue == event.source.oldValue):
            return

        orca.visualAppearanceChanged(event, event.source)
        event.source.oldValue = event.source.value.currentValue

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated.

        Arguments:
        - event: the Event
        """

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

    def onWindowDeactivated(self, event):
        """Called whenever a toplevel window is deactivated.

        Arguments:
        - event: the Event
        """

        # Because window activated and deactivated events may be
        # received in any order when switching from one application to
        # another, locusOfFocus and activeWindow, we really only change
        # the locusOfFocus and activeWindow when we are dealing with
        # an event from the current activeWindow.
        #
        if event.source == orca_state.activeWindow:
            orca.setLocusOfFocus(event, None)
            orca_state.activeWindow = None

    def noOp(self, event):
        """Just here to capture events.

        Arguments:
        - event: the Event
        """
        pass

    ########################################################################
    #                                                                      #
    # Flat review mode support.  [[[TODO: WDW - still under development,   #
    # but the idea is that a script should be able to provide custom       #
    # information about layout as well.]]]                                 #
    #                                                                      #
    ########################################################################

    def getShowingZones(self):
        """Returns a list of all interesting, non-intersecting,
        regions that are drawn in the currently active window.  Each
        element of the list is the Accessible object associated with a
        given region.  The term 'zone' here is inherited from OCR
        algorithms and techniques.

        The objects are returned in no particular order.

        Arguments:
        - root: the Accessible object to traverse

        Returns: a list of all objects under the specified object
        """
        if (not orca_state.locusOfFocus) \
            or (orca_state.locusOfFocus.app != self.app):
            return []

        # We want to stop at the window or frame or equivalent level.
        #
        obj = orca_state.locusOfFocus
        while obj \
                  and obj.parent \
                  and (obj.parent.role != rolenames.ROLE_APPLICATION) \
                  and (obj != obj.parent):
            obj = obj.parent

        if obj:
            return flat_review.getShowingZones(obj)
        else:
            return []

    def clusterZonesByLine(self, zones):
        """Given a list of interesting accessible objects (the zones),
        returns a list of lines in order from the top to bottom, where
        each line is a list of accessible objects in order from left
        to right.  """

        return flat_review.clusterZonesByLine(zones)

    def toggleTableCellReadMode(self, inputEvent=None):
        """Toggles an indicator for whether we should just read the current
        table cell or read the whole row."""

        line = _("Speak ")
        settings.readTableCellRow = not settings.readTableCellRow
        if settings.readTableCellRow:
            line += _("row")
        else:
            line += _("cell")

        speech.speak(line)

        return True

    def textAttrsToDictionary(self, str):
        """Converts a string of text attribute tokens of the form
        <key>:<value>; into a dictionary of keys and values.
        Text before the colon is the key and text afterwards is the
        value. If there is a final semi-colon, then it's ignored.

        Arguments:
        - str: the string of tokens containing <key>:<value>; pairs.

        Returns a dictionary of key/value items.
        """

        dictionary = {}
        allTokens = str.split()
        for i in range(0, len(allTokens)):
            item = allTokens[i].split(":")
            if item[1].endswith(";"):
              item[1] = item[1][0:len(item[1])-1]
            dictionary[item[0]] = item[1]

        return dictionary

    def outputCharAttributes(self, attributes):
        """Speak each of the text attributes given dictionary.

        Arguments:
        - attributes: a dictionary of text attributes to speak.
        """

        for key in attributes.keys():
            attribute = attributes[key]
            if attribute:
                line = key + " " + attribute
                speech.speak(line)

    def readCharAttributes(self, inputEvent=None):
        """Reads the attributes associated with the current text character.
        Calls outCharAttributes to speak a list of attributes. By default,
        a certain set of attributes will be spoken. If this is not desired,
        then individual application scripts should override this method to
        only speak the subset required.
        """

        if orca_state.locusOfFocus and orca_state.locusOfFocus.text:
            caretOffset = orca_state.locusOfFocus.text.caretOffset
            text = orca_state.locusOfFocus.text

            # Creates dictionaries of the default attributes, plus the set
            # of attributes specific to the character at the caret offset.
            # Combine these two dictionaries and then extract just the
            # entries we are interested in.
            #
            defAttributes = text.getDefaultAttributes()
            defDict = self.textAttrsToDictionary(defAttributes)
            allAttributes = defDict

            charAttributes = text.getAttributes(caretOffset)
            if charAttributes[0]:
                charDict = self.textAttrsToDictionary(charAttributes[0])

                # It looks like some applications like Evolution and Star
                # Office don't implement getDefaultAttributes(). In that
                # case, the best we can do is use the specific text
                # attributes for this character returned by getAttributes().
                #
                if allAttributes:
                    allAttributes = allAttributes.update(charDict)
                else:
                    allAttributes = charDict

            # Create a dictionary of just the items we are interested in.
            # Always include size and family-name. For the others, if the
            # value is the default, then ignore it.
            #
            attributes = {}
            attributes['size']        = allAttributes.get('size')
            attributes['family-name'] = allAttributes.get('family-name')

            attr = allAttributes.get('indent')
            if attr != "0":
                attributes['indent'] = attr

            attr = allAttributes.get('underline')
            if attr != "none":
                attributes['underline'] = attr

            attr = allAttributes.get('strikethrough')
            if attr != "false":
                attributes['strikethrough'] = attr

            attr = allAttributes.get('justification')
            if attr != "left":
                attributes['justification'] = attr

            attr = allAttributes.get('style')
            if attr != "normal":
                attributes['style'] = attr

            self.outputCharAttributes(attributes)

        return True

    def reportScriptInfo(self, inputEvent=None):
        """Output useful information on the current script via speech
        and braille.  This information will be helpful to script writers.
        """

        string = "SCRIPT INFO: Script name='%s'" % self.name
        if orca_state.locusOfFocus and orca_state.locusOfFocus.app:

            string += " Application name='%s'" \
                      % orca_state.locusOfFocus.app.name

            try:
                string += " Toolkit name='%s'" \
                          % orca_state.locusOfFocus.app.toolkitName
            except:
                string += " Toolkit unknown"

            try:
                string += " Version='%s'" \
                          % orca_state.locusOfFocus.app.version
            except:
                string += " Version unknown"

            debug.println(debug.LEVEL_INFO, string)
            speech.speak(string)
            braille.displayMessage(string)

        return True

    def enterLearnMode(self, inputEvent=None):
        """Turns learn mode on.  The user must press the escape key to exit
        learn mode.

        Returns True to indicate the input event has been consumed.
        """

        if settings.learnModeEnabled:
            return True

        self.exitLearnModeKeyBinding = keybindings.KeyBinding(
            "Escape",
            0,
            0,
            self.exitLearnModeHandler)
        self.keyBindings.add(self.exitLearnModeKeyBinding)

        speech.speak(
            _("Entering learn mode.  Press any key to hear its function. " \
              + "To exit learn mode, press the escape key."))
        braille.displayMessage(_("Learn mode.  Press escape to exit."))
        settings.learnModeEnabled = True
        return True

    def exitLearnMode(self, inputEvent=None):
        """Turns learn mode off.

        Returns True to indicate the input event has been consumed.
        """

        self.keyBindings.remove(self.exitLearnModeKeyBinding)

        speech.speak(_("Exiting learn mode."))
        braille.displayMessage(_("Exiting learn mode."))
        self.whereAmI(None)
        return True

    def getFlatReviewContext(self):
        """Returns the flat review context, creating one if necessary."""

        if not self.flatReviewContext:
            # The first thing we try to do is find which Zone has the
            # Accessible object with focus.
            #
            currentLineIndex = 0
            currentZoneIndex = 0
            currentWordIndex = 0
            currentCharIndex = 0
            lines = self.clusterZonesByLine(self.getShowingZones())
            foundZoneWithFocus = False
            while currentLineIndex < len(lines):
                line = lines[currentLineIndex]
                currentZoneIndex = 0
                while currentZoneIndex < len(line.zones):
                    zone = line.zones[currentZoneIndex]
                    if zone.accessible == orca_state.locusOfFocus:
                        foundZoneWithFocus = True
                        break
                    else:
                        currentZoneIndex += 1
                if foundZoneWithFocus:
                    break
                else:
                    currentLineIndex += 1

            # Fallback to the first Zone if we didn't find anything.
            #
            if not foundZoneWithFocus:
                currentLineIndex = 0
                currentZoneIndex = 0
            elif isinstance(zone, flat_review.TextZone):
                # If we're on an accessible text object, try to set the
                # review cursor to the caret position of that object.
                #
                accessible  = zone.accessible
                lineIndex   = currentLineIndex
                zoneIndex   = currentZoneIndex
                caretOffset = zone.accessible.text.caretOffset
                foundZoneWithCaret = False
                while lineIndex < len(lines):
                    line = lines[lineIndex]
                    while zoneIndex < len(line.zones):
                        zone = line.zones[zoneIndex]
                        if zone.accessible == accessible:
                            if (caretOffset >= zone.startOffset) \
                                   and (caretOffset \
                                        < (zone.startOffset + zone.length)):
                                foundZoneWithCaret = True
                                break
                        zoneIndex += 1
                    if foundZoneWithCaret:
                        currentLineIndex = lineIndex
                        currentZoneIndex = zoneIndex
                        currentWordIndex = 0
                        currentCharIndex = 0
                        offset = zone.startOffset
                        while currentWordIndex < len(zone.words):
                            word = zone.words[currentWordIndex]
                            if (word.length + offset) > caretOffset:
                                currentCharIndex = caretOffset - offset
                                break
                            else:
                                currentWordIndex += 1
                                offset += word.length
                        break
                    else:
                        zoneIndex = 0
                        lineIndex += 1

            self.flatReviewContext = flat_review.Context(lines,
                                                         currentLineIndex,
                                                         currentZoneIndex,
                                                         currentWordIndex,
                                                         currentCharIndex)

            self.justEnteredFlatReviewMode = True

            # Also, we want to remember where the cursor currently was
            # when the user was in focus tracking mode.  We'll try to
            # keep the position the same as we move to characters above
            # and below us.
            #
            self.targetCursorCell = braille.cursorCell

        return self.flatReviewContext

    def toggleFlatReviewMode(self, inputEvent=None):
        """Toggles between flat review mode and focus tracking mode."""

        if self.flatReviewContext:
            util.drawOutline(-1, 0, 0, 0)
            self.flatReviewContext = None
            self.updateBraille(orca_state.locusOfFocus)
        else:
            context = self.getFlatReviewContext()
            [string, x, y, width, height] = \
                     context.getCurrent(flat_review.Context.WORD)
            util.drawOutline(x, y, width, height)
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def updateBrailleReview(self, targetCursorCell=0):
        """Obtains the braille regions for the current flat review line
        and displays them on the braille display.  If the targetCursorCell
        is non-0, then an attempt will be made to postion the review cursor
        at that cell.  Otherwise, we will pan in display-sized increments
        to show the review cursor."""

        context = self.getFlatReviewContext()

        [regions, regionWithFocus] = context.getCurrentBrailleRegions()

        line = braille.Line()
        line.addRegions(regions)
        braille.setLines([line])
        braille.setFocus(regionWithFocus, False)
        braille.panToOffset(regionWithFocus.brailleOffset \
                            + regionWithFocus.cursorOffset)

        if self.justEnteredFlatReviewMode:
            braille.refresh(True, self.targetCursorCell)
            self.justEnteredFlatReviewMode = False
        else:
            braille.refresh(True, targetCursorCell)

    def _setFlatReviewContextToBeginningOfBrailleDisplay(self):
        """Sets the character of interest to be the first character showing
        at the beginning of the braille display."""

        context = self.getFlatReviewContext()
        [regions, regionWithFocus] = context.getCurrentBrailleRegions()
        for region in regions:
            if ((region.brailleOffset + len(region.string)) \
                   > braille._viewport[0]) \
                and (isinstance(region, braille.ReviewText) \
                     or isinstance(region, braille.ReviewComponent)):
                position = max(region.brailleOffset, braille._viewport[0])
                offset = position - region.brailleOffset
                self.targetCursorCell = region.brailleOffset \
                                        - braille._viewport[0]
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

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the left.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if braille.beginningIsShowing:
                self.flatReviewContext.goBegin(flat_review.Context.LINE)
                self.reviewPreviousCharacter(inputEvent)
            else:
                braille.panLeft(panAmount)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [string, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)
            util.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif braille.beginningIsShowing and orca_state.locusOfFocus \
             and ((orca_state.locusOfFocus.role == rolenames.ROLE_TEXT) \
                  or (orca_state.locusOfFocus.role == rolenames.ROLE_PARAGRAPH)):
            # If we're at the beginning of a line of a multiline text
            # area, then force it's caret to the end of the previous
            # line.  The assumption here is that we're currently
            # viewing the line that has the caret -- which is a pretty
            # good assumption for focus tacking mode.  When we set the
            # caret position, we will get a caret event, which will
            # then update the braille.
            #
            text = orca_state.locusOfFocus.text
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            if startOffset > 0:
                text.setCaretOffset(startOffset - 1)
        else:
            braille.panLeft(panAmount)
            braille.refresh(False)

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
            if braille.endIsShowing:
                self.flatReviewContext.goEnd(flat_review.Context.LINE)
                self.reviewNextCharacter(inputEvent)
            else:
                braille.panRight(panAmount)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [string, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)

            util.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif braille.endIsShowing and orca_state.locusOfFocus \
             and ((orca_state.locusOfFocus.role == rolenames.ROLE_TEXT) \
                  or (orca_state.locusOfFocus.role == rolenames.ROLE_PARAGRAPH)):
            # If we're at the end of a line of a multiline text area, then
            # force it's caret to the beginning of the next line.  The
            # assumption here is that we're currently viewing the line that
            # has the caret -- which is a pretty good assumption for focus
            # tacking mode.  When we set the caret position, we will get a
            # caret event, which will then update the braille.
            #
            text = orca_state.locusOfFocus.text
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            if endOffset < text.characterCount:
                text.setCaretOffset(endOffset)
        else:
            braille.panRight(panAmount)
            braille.refresh(False)

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

    def leftClickReviewItem(self, inputEvent=None):
        """Performs a left mouse button click on the current item."""

        self.getFlatReviewContext().clickCurrent(1)
        return True

    def rightClickReviewItem(self, inputEvent=None):
        """Performs a right mouse button click on the current item."""

        self.getFlatReviewContext().clickCurrent(3)
        return True

    def reviewCurrentLine(self, inputEvent):
        """Presents the current flat review line via braille and speech."""

        spellWord = util.isDoubleClick(self.lastReviewCurrentEvent,
                                       inputEvent)
        self._reviewCurrentLine(inputEvent, spellWord)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def _reviewCurrentLine(self, inputEvent, spellWord=False):
        """Presents the current flat review line via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - spellWord - if True, spell the current line, otherwise speak it.
        """

        context = self.getFlatReviewContext()

        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.LINE)
        util.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not string) or (len(string) == 0) or (string == "\n"):
                speech.speak(_("blank"))
            elif string.isspace():
                speech.speak(_("white space"))
            elif not spellWord:
                speech.speak(string)
            else:
                self.spellCurrentItem(string)

        self.updateBrailleReview()

        return True

    def reviewPreviousLine(self, inputEvent):
        """Moves the flat review context to the beginning of the
        previous line."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.LINE,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentLine(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewHome(self, inputEvent):
        """Moves the flat review context to the top left of the current
        window."""

        context = self.getFlatReviewContext()

        context.goBegin()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

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
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewBottomLeft(self, inputEvent):
        """Moves the flat review context to the beginning of the
        last line in the window.  Places the flat review cursor at
        the beginning of the line."""

        context = self.getFlatReviewContext()

        context.goEnd(flat_review.Context.WINDOW)
        context.goBegin(flat_review.Context.LINE)
        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewEnd(self, inputEvent):
        """Moves the flat review context to the end of the
        last line in the window.  Places the flat review cursor
        at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewCurrentItem(self, inputEvent, targetCursorCell=0):
        """Speak/Braille the current item to the user. A "double-click"
        of this key will cause the word to be spelt.
        """

        spellWord = util.isDoubleClick(self.lastReviewCurrentEvent,
                                       inputEvent)
        self._reviewCurrentItem(inputEvent, targetCursorCell, spellWord)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def spellCurrentItem(self, string):
        """Spell the current flat review word or line.

        Arguments:
        - string: the string to spell.
        """

        for (index, character) in enumerate(string):
            if character.isupper():
                speech.speak(character, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(character)

    def _reviewCurrentItem(self, inputEvent, targetCursorCell=0,
                           spellWord=False):
        """Presents the current item to the user.

        Arguments:
        - inputEvent - the current input event.
        - targetCursorCell - if non-zero, the target braille cursor cell.
        - spellWord - if True, spell the current word, otherwise speak it.
        """

        context = self.getFlatReviewContext()
        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.WORD)
        util.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (len(string) == 0) or (string == "\n"):
                speech.speak(_("blank"))
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n":
                    speech.speak(_("blank"))
                elif string.isspace():
                    speech.speak(_("white space"))
                elif string.isupper() and not spellWord:
                    speech.speak(string, self.voices[settings.UPPERCASE_VOICE])
                elif not spellWord:
                    speech.speak(string)
                else:
                    self.spellCurrentItem(string)

        self.updateBrailleReview(targetCursorCell)

        return True

    def reviewCurrentAccessible(self, inputEvent):
        context = self.getFlatReviewContext()
        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.ZONE)
        util.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            speech.speakUtterances(
                self.speechGenerator.getSpeech(
                    context.getCurrentAccessible(), False))

        return True

    def reviewPreviousItem(self, inputEvent):
        """Moves the flat review context to the previous item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.WORD,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextItem(self, inputEvent):
        """Moves the flat review context to the next item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.WORD,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewCurrentCharacter(self, inputEvent):
        context = self.getFlatReviewContext()

        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.CHAR)
        util.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (len(string) == 0):
                speech.speak(_("blank"))
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n":
                    speech.speak(_("blank"))
                elif string.isupper():
                    speech.speak(string, self.voices[settings.UPPERCASE_VOICE])
                else:
                    speech.speak(string)

        self.updateBrailleReview()

        return True

    def reviewPreviousCharacter(self, inputEvent):
        """Moves the flat review context to the previous character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.CHAR,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewEndOfLine(self, inputEvent):
        """Moves the flat review context to the end of the line.  Places
        the flat review cursor at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd(flat_review.Context.LINE)

        self.reviewCurrentCharacter(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextCharacter(self, inputEvent):
        """Moves the flat review context to the next character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.CHAR,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = braille.cursorCell

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

    def showZones(self, inputEvent):
        """Debug routine to paint rectangles around the discrete
        interesting (e.g., text)  zones in the active window for
        this application.
        """

        flatReviewContext = self.getFlatReviewContext()
        lines = flatReviewContext.lines
        print "Number of lines:", len(lines)
        for line in lines:
            string = ""
            for zone in line.zones:
                string += " '%s' [%s]" % (zone.string, zone.accessible.role)
                util.drawOutline(zone.x, zone.y, zone.width, zone.height,
                                 False)
            debug.println(debug.LEVEL_OFF, string)
        self.flatReviewContext = None

# Dictionary that defines the state changes we care about for various
# objects.  The key represents the role and the value represents a list
# of states that we care about.
#
state_change_notifiers = {}

state_change_notifiers[rolenames.ROLE_CHECK_MENU_ITEM] = ("checked",
                                                        None)
state_change_notifiers[rolenames.ROLE_CHECK_BOX]     = ("checked",
                                                        None)
state_change_notifiers[rolenames.ROLE_PANEL]         = ("showing",
                                                        None)
state_change_notifiers[rolenames.ROLE_LABEL]         = ("showing",
                                                        None)
state_change_notifiers[rolenames.ROLE_TOGGLE_BUTTON] = ("checked",
                                                        None)
state_change_notifiers[rolenames.ROLE_TABLE_CELL]    = ("checked",
                                                        "expanded",
                                                        None)
