# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2013 Igalia, S.L.
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

"""Custom script for Evolution."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.scripts.default as default
import orca.keybindings as keybindings
import orca.input_event as input_event
import orca.braille as braille
import orca.messages as messages
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.speechserver as speechserver
import orca.settings as settings
import orca.settings_manager as settings_manager

from .formatting import Formatting
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The Evolution script class.                                          #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        default.Script.__init__(self, app)

        # This will be used to cache a handle to the message area in the
        # Mail compose window.

        self.message_panel = None

        # A handle to the Spellcheck dialog.
        #
        self.spellCheckDialog = None

        # The last row and column we were on in the mail message header list.

        self.lastMessageColumn = -1
        self.lastMessageRow = -1

        # The last locusOfFocusChanged roles hierarchy.
        #
        self.rolesList = []

        # By default, don't present if Evolution is not the active application.
        #
        self.presentIfInactive = False

        # Evolution defines new custom roles. We need to make them known
        # to Orca for Speech and Braille output.

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to define our own sayAll() method.
        """

        default.Script.setupInputEventHandlers(self)

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                cmdnames.SAY_ALL)

    def isActivatableEvent(self, event):
        """Returns True if the given event is one that should cause this
        script to become the active script.  This is only a hint to
        the focus tracking manager and it is not guaranteed this
        request will be honored.  Note that by the time the focus
        tracking manager calls this method, it thinks the script
        should become active.  This is an opportunity for the script
        to say it shouldn't.
        """

        # If the Evolution window is not focused, ignore this event.
        #
        window = self.utilities.topLevelObject(event.source)
        if window and not window.getState().contains(pyatspi.STATE_ACTIVE):
            return False

        return True

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        return False

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        # The default script's onActiveDescendantChanged method is cutting
        # off speech with a speech.stop. If we're in the spellcheck dialog,
        # this interrupts the presentation of the context.
        #
        if self.utilities.isSpellingSuggestionsList(event.source):
            orca.setLocusOfFocus(event, event.any_data)

            # We'll tuck away the activeDescendant information for future
            # reference since the AT-SPI gives us little help in finding
            # this.
            #
            if orca_state.locusOfFocus \
               and (orca_state.locusOfFocus != event.source):
                self.pointOfReference['activeDescendantInfo'] = \
                    [orca_state.locusOfFocus.parent,
                     orca_state.locusOfFocus.getIndexInParent()]
            return

        default.Script.onActiveDescendantChanged(self, event)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # When a message is deleted from within the table of messages, we get
        # two focus events:  One for the index of the new message prior to
        # deletion and one for the index of the new message after deletion.
        # This causes us to speak the message after the one that gets focus
        # prior to speaking the actual message that gets focus.
        # See bug #347964.
        #
        string, mods = self.utilities.lastKeyAndModifiers()
        if string == "Delete":
            roles = [pyatspi.ROLE_TABLE_CELL,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_UNKNOWN,
                     pyatspi.ROLE_SCROLL_PANE]
            oldLocusOfFocus = orca_state.locusOfFocus
            if self.utilities.hasMatchingHierarchy(event.source, roles) \
               and self.utilities.hasMatchingHierarchy(oldLocusOfFocus, roles):
                parent = event.source.parent
                parentTable = parent.queryTable()
                newIndex = self.utilities.cellIndex(event.source)
                newRow = parentTable.getRowAtIndex(newIndex)
                oldIndex = self.utilities.cellIndex(oldLocusOfFocus)
                oldRow = parentTable.getRowAtIndex(oldIndex)
                nRows = parentTable.nRows
                if (newRow != oldRow) and (oldRow != nRows):
                    return

        # For everything else, pass the event onto the parent class
        # to be handled in the default way.
        #
        default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        if not event.detail1:
            default.Script.onStateChanged(self, event)
            return

        # Present text in the Account Assistant
        if event.type.startswith("object:state-changed:showing"):
            try:
                role = event.source.getRole()
                relationSet = event.source.getRelationSet()
            except:
                return

            if role != pyatspi.ROLE_LABEL or relationSet:
                default.Script.onStateChanged(self, event)
                return

            window = self.utilities.topLevelObject(event.source)
            focusedObj = self.utilities.focusedObject(window)
            if self.utilities.spatialComparison(event.source, focusedObj) >= 0:
                return

            # TODO - JD: The very last screen results in a crazy-huge number
            # of events, and they come in an order that is not good for this
            # approach. So we'll need to handle this particular case elsewhere.
            if focusedObj.getRole() == pyatspi.ROLE_CHECK_BOX:
                labels = self.utilities.unrelatedLabels(window)
                if len(labels) > 15:
                    return

            voice = self.voices.get(settings.DEFAULT_VOICE)
            text = self.utilities.displayedText(event.source)
            self.presentMessage(text, voice=voice)
            return

        default.Script.onStateChanged(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # When the active descendant in the list of misspelled words
        # changes, we typically get an object:active-descendant-changed
        # event. Unfortunately, we don't seem to get this event (or a
        # focus: event) when the user presses a button without moving
        # focus there explicitly. (e.g. pressing Alt+R) The label which
        # is associated with the spelling list gets new text. So we'll
        # try to look for that instead.
        #
        if event.source.getRole() == pyatspi.ROLE_LABEL:
            relations = event.source.getRelationSet()
            for relation in relations:
                if relation.getRelationType() == pyatspi.RELATION_LABEL_FOR:
                    target = relation.getTarget(0)
                    if self.utilities.isSpellingSuggestionsList(target):
                        [badWord, allTokens] = \
                            self.utilities.misspelledWordAndBody(
                                target, self.message_panel)
                        self.speakMisspeltWord(allTokens, badWord)

                        try:
                            selection = target.querySelection()
                        except NotImplementedError:
                            selection = None
                        if selection and selection.nSelectedChildren > 0:
                            newFocus = selection.getSelectedChild(0)
                            orca.setLocusOfFocus(event, newFocus)
                            self.pointOfReference['activeDescendantInfo'] = \
                                [target, newFocus.getIndexInParent()]

                        return

        default.Script.onTextInserted(self, event)

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def presentMessageLine(self, obj, newLocusOfFocus):
        """Speak/braille the line at the current text caret offset.
        """

        [string, caretOffset, startOffset] = self.getTextLineAtCaret(obj)
        self.updateBraille(newLocusOfFocus)
        result = self.speechGenerator.generateTextIndentation(obj, line=string)
        if result:
            speech.speak(result[0])
        line = self.utilities.adjustForRepeats(string)

        if self.utilities.speakBlankLine(obj):
            speech.speak(messages.BLANK, None, False)
        else:
            speech.speak(line, None, False)

    def readPageTab(self, tab):
        """Speak/Braille the given page tab. The speech verbosity is set
           to VERBOSITY_LEVEL_BRIEF for this operation and then restored
           to its previous value on completion.

        Arguments:
        - tab: the page tab to speak/braille.
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        savedSpeechVerbosityLevel = settings.speechVerbosityLevel
        _settingsManager.setSetting(
            'speechVerbosityLevel', settings.VERBOSITY_LEVEL_BRIEF)
        utterances = speechGen.generateSpeech(tab)
        speech.speak(utterances)
        _settingsManager.setSetting(
            'speechVerbosityLevel', savedSpeechVerbosityLevel)

        self.displayBrailleRegions(brailleGen.generateBraille(tab))

    def textLines(self, obj):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        We have to subclass this because Evolution lays out its messages
        such that each paragraph is in its own panel, each of which is
        in a higher level panel.  So, we just traverse through the
        children.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        if not obj:
            return

        try:
            text = obj.queryText()
        except NotImplementedError:
            return

        panel = obj.parent
        htmlPanel = panel.parent
        startIndex = panel.getIndexInParent()
        i = startIndex
        total = htmlPanel.childCount
        textObjs = []
        startOffset = text.caretOffset
        offset = text.caretOffset
        string = ""
        done = False

        # Determine the correct "say all by" mode to use.
        #
        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
        if sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = pyatspi.TEXT_BOUNDARY_SENTENCE_END
        elif sayAllStyle == settings.SAYALL_STYLE_LINE:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        else:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        voices = _settingsManager.getSetting('voices')

        while not done:
            panel = htmlPanel.getChildAtIndex(i)
            if panel != None:
                textObj = panel.getChildAtIndex(0)
                try:
                    text = textObj.queryText()
                except NotImplementedError:
                    return
                textObjs.append(textObj)
                length = text.characterCount

                while offset <= length:
                    [mystr, start, end] = text.getTextAtOffset(offset, mode)
                    endOffset = end

                    if len(mystr) != 0:
                        string += " " + mystr

                    if mode == pyatspi.TEXT_BOUNDARY_LINE_START or \
                       len(mystr) == 0 or mystr[len(mystr)-1] in '.?!':
                        string = self.utilities.adjustForRepeats(string)
                        if string.isupper():
                            voice = voices[settings.UPPERCASE_VOICE]
                        else:
                            voice = voices[settings.DEFAULT_VOICE]

                        if not textObjs:
                            textObjs.append(textObj)
                        if len(string) != 0:
                            yield [speechserver.SayAllContext(textObjs, string,
                                                      startOffset, endOffset),
                               voice]
                        textObjs = []
                        string = ""
                        startOffset = endOffset

                    if len(mystr) == 0 or end == length:
                        break
                    else:
                        offset = end

            offset = 0
            i += 1
            if i == total:
                done = True

        # If there is anything left unspoken, speak it now.
        #
        if len(string) != 0:
            string = self.utilities.adjustForRepeats(string)
            if string.isupper():
                voice = voices[settings.UPPERCASE_VOICE]
            else:
                voice = voices[settings.DEFAULT_VOICE]

            yield [speechserver.SayAllContext(textObjs, string,
                                              startOffset, endOffset),
                   voice]

    def __sayAllProgressCallback(self, context, callbackType):
        """Provide feedback during the sayAll operation.
        """

        if callbackType == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            return
        elif callbackType == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            offset = context.currentOffset
            for i in range(0, len(context.obj)):
                obj = context.obj[i]
                charCount = obj.queryText().characterCount
                if offset > charCount:
                    offset -= charCount
                else:
                    obj.queryText().setCaretOffset(offset)
                    break
        elif callbackType == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            obj = context.obj[len(context.obj)-1]
            obj.queryText().setCaretOffset(context.currentOffset)
            orca.setLocusOfFocus(None, obj, notifyScript=False)

        # If there is a selection, clear it. See bug #489504 for more details.
        # This is not straight forward with Evolution. all the text is in
        # an HTML panel which contains multiple panels, each containing a
        # single text object.
        #
        panel = obj.parent
        htmlPanel = panel.parent
        for i in range(0, htmlPanel.childCount):
            panel = htmlPanel.getChildAtIndex(i)
            if panel != None:
                textObj = panel.getChildAtIndex(0)
                try:
                    text = textObj.queryText()
                except:
                    pass
                else:
                    if text.getNSelections():
                        text.removeSelection(0)

    def sayAll(self, inputEvent):
        """Speak all the text associated with the text object that has
           focus. We have to define our own method here because Evolution
           does not implement the FLOWS_TO relationship and all the text
           are in an HTML panel which contains multiple panels, each
           containing a single text object.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "evolution.sayAll.")
        try:
            if orca_state.locusOfFocus and orca_state.locusOfFocus.queryText():
                speech.sayAll(self.textLines(orca_state.locusOfFocus),
                              self.__sayAllProgressCallback)
        except:
            default.Script.sayAll(self, inputEvent)

        return True
