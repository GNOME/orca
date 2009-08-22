# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom script for Evolution."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.rolenames as rolenames
import orca.braille as braille
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.speechserver as speechserver
import orca.settings as settings

from orca.orca_i18n import _ # for gettext support

from speech_generator import SpeechGenerator
from formatting import Formatting
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

        # Last Setup Assistant panel spoken.
        #
        self.lastSetupPanel = None

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

        # Pylint is confused and flags several errors of the type:
        #
        # E1101:282:Script.__init__: Module 'orca.rolenames' has no
        # 'ROLE_CALENDAR_VIEW' member
        #
        # So for now, we just disable these errors in this method.
        #
        # pylint: disable-msg=E1101

        rolenames.ROLE_CALENDAR_VIEW = "Calendar View"
        rolenames.rolenames[rolenames.ROLE_CALENDAR_VIEW] = rolenames.Rolename(
            rolenames.ROLE_CALENDAR_VIEW,
            # Translators: short braille for the rolename of a calendar view.
            #
            _("calv"),
            # Translators: long braille for the rolename of a calendar view.
            #
            _("CalendarView"),
            # Translators: spoken words for the rolename of a calendar view.
            #
            _("calendar view"))

        rolenames.ROLE_CALENDAR_EVENT = "Calendar Event"
        rolenames.rolenames[rolenames.ROLE_CALENDAR_EVENT] = \
            rolenames.Rolename(
            rolenames.ROLE_CALENDAR_EVENT,
            # Translators: short braille for the rolename of a calendar event.
            #
            _("cale"),
            # Translators: long braille for the rolename of a calendar event.
            #
            _("CalendarEvent"),
            # Translators: spoken words for the rolename of a calendar event.
            #
            _("calendar event"))

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to define our own sayAll() method.
        """

        default.Script.setupInputEventHandlers(self)

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                _("Speaks entire document."))

        self.inputEventHandlers["toggleReadMailHandler"] = \
            input_event.InputEventHandler(
                Script.toggleReadMail,
                # Translators: this tells Orca to act like 'biff', or let
                # the user know when new mail has arrived, even if Evolution
                # doesn't have focus.
                #
                _("Toggle whether we present new mail " \
                  "if we are not the active script."))

    def getKeyBindings(self):
        """Defines the new key binding for this script. Setup the default
        key bindings, then add one in for toggling whether we present new
        mail if we not not the active script.

        Returns an instance of keybindings.KeyBindings.
        """

        debug.println(self.debugLevel, "Evolution.getKeyBindings.")

        keyBindings = default.Script.getKeyBindings(self)

        keyBindings.add(
            keybindings.KeyBinding(
                "n",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleReadMailHandler"]))
        return keyBindings

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["object:state-changed:showing"]           = \
            self.onStateChanged

        return listeners

    def findUnrelatedLabels(self, root):
        """Returns a list containing all the unrelated (i.e., have no
        relations to anything and are not a fundamental element of a
        more atomic component like a combo box) labels under the given
        root.  Note that the labels must also be showing on the display.

        Arguments:
        - root the Accessible object to traverse

        Returns a list of unrelated labels under the given root.
        """

        labels = default.Script.findUnrelatedLabels(self, root)
        for i, label in enumerate(labels):
            if not label.getState().contains(pyatspi.STATE_SENSITIVE):
                labels.remove(label)
            else:
                try:
                    text = label.queryText()
                except:
                    pass
                else:
                    attr = text.getAttributes(0)
                    if attr[0]:
                        [charKeys, charDict] = \
                            self.textAttrsToDictionary(attr[0])
                        if charDict.get('weight', '400') == '700':
                            if self.isWizard(root):
                                # We've passed the wizard info at the top,
                                # which is what we want to present. The rest
                                # is noise.
                                #
                                return labels[0:i]
                            else:
                                # This label is bold and thus serving as a
                                # heading. As such, it's not really unrelated.
                                #
                                labels.remove(label)

        return labels

    def toggleReadMail(self, inputEvent):
        """ Toggle whether we present new mail if we not not the active script.+
        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "Evolution.toggleReadMail.")

        # Translators: this tells Orca to act like 'biff', or let
        # the user know when new mail has arrived, even if Evolution
        # doesn't have focus.
        #
        line = _("present new mail if this script is not active.")
        self.presentIfInactive = not self.presentIfInactive
        if not self.presentIfInactive:
            # Translators: this tells Orca to act like 'biff', or let
            # the user know when new mail has arrived, even if Evolution
            # doesn't have focus.
            #
            line = _("do not present new mail if this script is not active.")

        speech.speak(line)

        return True

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
        settings.speechVerbosityLevel = settings.VERBOSITY_LEVEL_BRIEF
        utterances = speechGen.generateSpeech(tab)
        speech.speak(utterances)
        settings.speechVerbosityLevel = savedSpeechVerbosityLevel

        braille.displayRegions(brailleGen.generateBraille(tab))

    def getTimeForCalRow(self, row, noIncs):
        """Return a string equivalent to the time of the given row in
           the calendar day view. Each calendar row is equivalent to
           a certain time interval (from 5 minutes upto 1 hour), with
           time (row 0) starting at 12 am (midnight).

        Arguments:
        - row: the row number.
        - noIncs: the number of equal increments that the 24 hour period
                  is divided into.

        Returns the time as a string.
        """

        totalMins = timeIncrements[noIncs] * row

        if totalMins < 720:
            suffix = 'A.M.'
        else:
            totalMins -= 720
            suffix = 'P.M.'

        hrs = hours[totalMins / 60]
        mins = minutes[totalMins % 60]

        return hrs + ' ' + mins + ' ' + suffix

    def getAllSelectedText(self, obj):
        """Get all the text applicable text selections for the given object.
        If there is selected text, look to see if there are any previous
        or next text objects that also have selected text and add in their
        text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        textContents = ""
        startOffset = 0
        endOffset = 0
        if obj.queryText().getNSelections() > 0:
            [textContents, startOffset, endOffset] = \
                                            self.getSelectedText(obj)

        # Unfortunately, Evolution doesn't use the FLOWS_FROM and
        # FLOWS_TO relationships to easily allow us to get to previous
        # and next text objects. Instead we have to move up the
        # component hierarchy until we get to the object containing all
        # the panels (with each line containing a single text item).
        # We can then check in both directions to see if there is other
        # contiguous text that is selected. We also have to jump over
        # zero length (empty) text lines and continue checking on the
        # other side.
        #
        container = obj.parent.parent
        current = obj.parent.getIndexInParent()
        morePossibleSelections = True
        while morePossibleSelections:
            morePossibleSelections = False
            if (current-1) >= 0:
                prevPanel = container[current-1]
                try:
                    prevObj = prevPanel[0]
                    displayedText = prevObj.queryText().getText(0, -1)
                    if len(displayedText) == 0:
                        current -= 1
                        morePossibleSelections = True
                    elif prevObj.queryText().getNSelections() > 0:
                        [newTextContents, start, end] = \
                                     self.getSelectedText(prevObj)
                        textContents = newTextContents + " " + textContents
                        current -= 1
                        morePossibleSelections = True
                except:
                    pass

        current = obj.parent.getIndexInParent()
        morePossibleSelections = True
        while morePossibleSelections:
            morePossibleSelections = False
            if (current+1) < container.childCount:
                nextPanel = container[current+1]
                try:
                    nextObj = nextPanel[0]
                    displayedText = nextObj.queryText().getText(0, -1)
                    if len(displayedText) == 0:
                        current += 1
                        morePossibleSelections = True
                    elif nextObj.queryText().getNSelections() > 0:
                        [newTextContents, start, end] = \
                                     self.getSelectedText(nextObj)
                        textContents += " " + newTextContents
                        current += 1
                        morePossibleSelections = True
                except:
                    pass

        return [textContents, startOffset, endOffset]

    def hasTextSelections(self, obj):
        """Return an indication of whether this object has selected text.
        Note that it's possible that this object has no text, but is part
        of a selected text area. Because of this, we need to check the
        objects on either side to see if they are none zero length and
        have text selections.

        Arguments:
        - obj: the text object to start checking for selected text.

        Returns: an indication of whether this object has selected text,
        or adjacent text objects have selected text.
        """

        currentSelected = False
        otherSelected = False
        nSelections = obj.queryText().getNSelections()
        if nSelections:
            currentSelected = True
        else:
            otherSelected = False
            displayedText = obj.queryText().getText(0, -1)
            if len(displayedText) == 0:
                container = obj.parent.parent
                current = obj.parent.getIndexInParent()
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    if (current-1) >= 0:
                        prevPanel = container[current-1]
                        prevObj = prevPanel[0]
                        try:
                            prevObjText = prevObj.queryText()
                        except:
                            prevObjText = None

                        if prevObj and prevObjText:
                            if prevObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = prevObjText.getText(0, -1)
                                if len(displayedText) == 0:
                                    current -= 1
                                    morePossibleSelections = True

                current = obj.parent.getIndexInParent()
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    if (current+1) < container.childCount:
                        nextPanel = container[current+1]
                        nextObj = nextPanel[0]
                        try:
                            nextObjText = nextObj.queryText()
                        except:
                            nextObjText = None

                        if nextObj and nextObjText:
                            if nextObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = nextObjText.getText(0, -1)
                                if len(displayedText) == 0:
                                    current += 1
                                    morePossibleSelections = True

        return [currentSelected, otherSelected]

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
        if settings.sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = pyatspi.TEXT_BOUNDARY_SENTENCE_END
        elif settings.sayAllStyle == settings.SAYALL_STYLE_LINE:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        else:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START

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
                        string = self.adjustForRepeats(string)
                        if string.decode("UTF-8").isupper():
                            voice = settings.voices[settings.UPPERCASE_VOICE]
                        else:
                            voice = settings.voices[settings.DEFAULT_VOICE]

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
            string = self.adjustForRepeats(string)
            if string.decode("UTF-8").isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
            else:
                voice = settings.voices[settings.DEFAULT_VOICE]

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
            orca.setLocusOfFocus(None, obj, notifyPresentationManager=False)

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

    def isSpellingSuggestionsList(self, obj):
        """Returns True if obj is the list of spelling suggestions
        in the spellcheck dialog.

        Arguments:
        - obj: the Accessible object of interest.
        """

        # The list of spelling suggestions is a table whose parent is
        # a scroll pane. This in and of itself is not sufficiently
        # unique. What makes the spell check dialog unique is the
        # quantity of push buttons found. If we find this combination,
        # we'll assume its the spelling dialog.
        #
        if obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent

        if not obj \
           or obj.getRole() != pyatspi.ROLE_TABLE \
           or obj.parent.getRole() != pyatspi.ROLE_SCROLL_PANE:
            return False

        topLevel = self.getTopLevel(obj.parent)
        if not self.isSameObject(topLevel, self.spellCheckDialog):
            # The group of buttons is found in a filler which is a
            # sibling of the scroll pane.
            #
            for sibling in obj.parent.parent:
                if sibling.getRole() == pyatspi.ROLE_FILLER:
                    buttonCount = 0
                    for child in sibling:
                        if child.getRole() == pyatspi.ROLE_PUSH_BUTTON:
                            buttonCount += 1
                    if buttonCount >= 5:
                        self.spellCheckDialog = topLevel
                        return True
        else:
            return True

        return False

    def getMisspelledWordAndBody(self, suggestionsList, messagePanel):
        """Gets the misspelled word from the spelling dialog and the
        list of words from the message body.

        Arguments:
        - suggestionsList: the list of spelling suggestions from the
          spellcheck dialog
        - messagePanel: the panel containing the message being checked
          for spelling

        Returns [mispelledWord, messageBody]
        """

        misspelledWord, messageBody = "", []

        # Look for the "Suggestions for "xxxxx" label in the spell
        # checker dialog panel. Extract out the xxxxx. This will be
        # the misspelled word.
        #
        text = self.getDisplayedLabel(suggestionsList) or ""
        words = text.split()
        for word in words:
            if word[0] in ["'", '"']:
                misspelledWord = word[1:len(word) - 1]
                break

        if messagePanel != None:
            allTextObjects = self.findByRole(messagePanel, pyatspi.ROLE_TEXT)
            for obj in allTextObjects:
                for word in self.getText(obj, 0, -1).split():
                    messageBody.append(word)

        return [misspelledWord, messageBody]

    def isMessageBodyText(self, obj):
        """Returns True if obj is in the body of an email message.

        Arguments:
        - obj: the Accessible object of interest.
        """

        try:
            obj.queryHypertext()
            ancestor = obj.parent.parent
        except:
            return False
        else:
            # The accessible text objects in the header at the top
            # of the message also have STATE_MULTI_LINE. But they
            # are inside panels which are inside table cells; the
            # body text is not. See bug #567428.
            #
            return (obj.getState().contains(pyatspi.STATE_MULTI_LINE) \
                    and ancestor.getRole() != pyatspi.ROLE_TABLE_CELL)

    def presentMessageLine(self, obj, newLocusOfFocus):
        """Speak/braille the line at the current text caret offset.
        """

        [string, caretOffset, startOffset] = self.getTextLineAtCaret(obj)
        self.updateBraille(newLocusOfFocus)
        if settings.enableSpeechIndentation:
            self.speakTextIndentation(obj, string)
        line = self.adjustForRepeats(string)

        if self.speakBlankLine(obj):
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            speech.speak(_("blank"), None, False)
        else:
            speech.speak(line, None, False)

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

    # This method tries to detect and handle the following cases:
    # 1) Mail view: current message pane: individual lines of text.
    # 2) Mail view: current message pane: "standard" mail header lines.
    # 3) Mail view: message header list
    # 4) Calendar view: day view: tabbing to day with appts.
    # 5) Calendar view: day view: moving with arrow keys.
    # 6) Preferences Dialog: options list.
    # 7) Mail view: insert attachment dialog: unlabelled arrow button.
    # 8) Mail compose window: message area
    # 9) Spell Checking Dialog
    # 10) Mail view: message area - attachments.

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # Pylint is confused and flags several errors of the type:
        #
        # E1101:1040:Script.locusOfFocusChanged: Module 'orca.rolenames'
        # has no 'ROLE_CALENDAR_EVENT' member
        #
        # So for now, we just disable these errors in this method.
        #
        # pylint: disable-msg=E1101

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # We always automatically go back to focus tracking mode when
        # the focus changes.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # self.printAncestry(event.source)

        # 1) Mail view: current message pane: individual lines of text.
        #
        # When the focus is in the pane containing the lines of an
        # actual mail message, then, for each of those lines, we
        # don't want to speak "text", the role of the component that
        # currently has focus.
        #
        # The situation is determine by checking the roles of the current
        # component, plus its parent, plus its parent. We are looking for
        # "text", "panel" and "unknown". If we find that, then (hopefully)
        # it's a line in the mail message and we get the utterances to
        # speak for that Text.
        if self.isMessageBodyText(event.source) \
           and not event.source.getState().contains(pyatspi.STATE_EDITABLE):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "current message pane: " \
                          + "individual lines of text.")

            self.presentMessageLine(event.source, newLocusOfFocus)
            return

        # 2) Mail view: current message pane: "standard" mail header lines.
        #
        # Check if the focus is in the From:, To:, Subject: or Date: headers
        # of a message in the message area, and that we want to speak all of
        # the tables cells for that current row.
        #
        # The situation is determine by checking the roles of the current
        # component, plus its parent, plus its parent. We are looking for
        # "text", "panel" and "table cell". If we find that, then (hopefully)
        # it's a header line in the mail message.
        #
        # For each of the table cells in the current row in the table, we
        # have to work our way back down the component hierarchy until we
        # get a component with no children. We then use the role of that
        # component to determine how to speak its contents.
        #
        # NOTE: the code assumes that there is only one child within each
        # component and that the final component (with no children) is of
        # role TEXT.

        self.rolesList = [pyatspi.ROLE_TEXT, \
                          pyatspi.ROLE_PANEL, \
                          pyatspi.ROLE_TABLE_CELL]
        if settings.readTableCellRow \
            and (self.isDesiredFocusedItem(event.source, self.rolesList)):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "current message pane: " \
                          + "standard mail header lines.")

            obj = event.source.parent.parent
            parent = obj.parent
            if parent.getRole() == pyatspi.ROLE_TABLE:
                parentTable = parent.queryTable()
                index = self.getCellIndex(obj)
                row = parentTable.getRowAtIndex(index)
                utterances = []
                regions = []
                for i in range(0, parentTable.nColumns):
                    cell = parentTable.getAccessibleAt(row, i)

                    while cell.childCount:
                        cell = cell[0]

                    if cell.getRole() == pyatspi.ROLE_TEXT:
                        regions.append(braille.Text(cell))
                        [string, caretOffset, startOffset] = \
                            self.getTextLineAtCaret(cell)
                        utterances.append(string)

                braille.displayRegions([regions, regions[0]])
                speech.speak(utterances)
                return

        # 3) Mail view: message header list
        #
        # Check if the focus is in the message header list. If this focus
        # event is for a different row that the last time we got a similar
        # focus event, we want to speak all of the tables cells (and the
        # header for the one that currently has focus) in the current
        # highlighted message. (The role is only spoken/brailled for the
        # table cell that currently has focus).
        #
        # If this focus event is just for a different table cell on the same
        # row as last time, then we just speak the current cell (and its
        # header).
        #
        # The braille cursor to set to point to the current cell.
        #
        # Note that the Evolution user can adjust which columns appear in
        # the message list and the order in which they appear, so that
        # Orca will just speak the ones that they are interested in.

        self.rolesList = [pyatspi.ROLE_TABLE_CELL, \
                          pyatspi.ROLE_TREE_TABLE]
        if settings.readTableCellRow \
            and (self.isDesiredFocusedItem(event.source, self.rolesList)):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "message header list.")

            # Unfortunately the default read table cell row handling won't
            # just work with Evolution (see bogusity comment below). We
            # quickly solve this by setting readTableCellRow to False
            # for the duration of this code section, then resetting it to
            # True at the end.
            #
            settings.readTableCellRow = False

            parent = event.source.parent
            parentTable = parent.queryTable()
            index = self.getCellIndex(event.source)
            row = parentTable.getRowAtIndex(index)
            column = parentTable.getColumnAtIndex(index)

            # If we are on the same row, then just speak/braille the table
            # cell as if settings.readTableCellRow was False.
            # See bug #503874 for more details.
            #
            if self.lastMessageRow == row:
                default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)
                settings.readTableCellRow = True
                return

            # This is an indication of whether we should speak all the table
            # cells (the user has moved focus up or down the list, or just
            # deleted a message), or just the current one (focus has moved
            # left or right in the same row). If we at the start or the end
            # of the message header list and the row and column haven't
            # changed, then speak all the table cells.
            #
            justDeleted = False
            if isinstance(orca_state.lastInputEvent,
                          input_event.KeyboardEvent):
                string = orca_state.lastNonModifierKeyEvent.event_string
                if string == "Delete":
                    justDeleted = True

            speakAll = (self.lastMessageRow != row) or \
                       ((row == 0 or row == parentTable.nRows-1) and \
                        self.lastMessageColumn == column) or \
                       justDeleted

            savedBrailleVerbosityLevel = settings.brailleVerbosityLevel
            savedSpeechVerbosityLevel = settings.speechVerbosityLevel

            brailleRegions = []
            cellWithFocus = None

            # If the current locus of focus is not a table cell, then we
            # are entering the mail message header list (rather than moving
            # around inside it), so speak/braille the number of mail messages
            # total.
            #
            # This code section handles one other bogusity. As Evolution is
            # initially being rendered on the screen, the focus at some point
            # is given to the highlighted row in the mail message header list.
            # Because of this, self.lastMessageRow and self.lastMessageColumn
            # will be set to that row number and column number, making the
            # setting of the speakAll variable above, incorrect. We fix that
            # up here.

            if orca_state.locusOfFocus.getRole() != pyatspi.ROLE_TABLE_CELL:
                speakAll = True
                message = "%d messages" % parentTable.nRows
                brailleRegions.append(braille.Region(message))
                speech.speak(message)

            for i in range(0, parentTable.nColumns):
                cell = parentTable.getAccessibleAt(row, i)
                if cell:
                    verbose = (cell.getIndexInParent() == \
                               event.source.getIndexInParent())

                    # Check if the current table cell is a check box. If it
                    # is, then to reduce verbosity, only speak and braille it,
                    # if it's checked or if we are moving the focus from to the
                    # left or right on the same row.
                    #
                    # The one exception to the above is if this is for the
                    # Status checkbox, in which case we speake/braille it if
                    # the message is unread (not checked).
                    #
                    header = parentTable.getColumnHeader(i)

                    checkbox = False
                    toRead = True
                    # Whether or not we want to replace the cell's column
                    # header with a more user-friendly alternative name.
                    # Currently we only do this with the "status" column,
                    # which we replace with "unread" if it is not checked.
                    #
                    useAlternativeName = False
                    try:
                        action = cell.queryAction()
                    except NotImplementedError:
                        action = None

                    if action:
                        for j in range(0, action.nActions):
                            # Translators: this is the action name for
                            # the 'toggle' action. It must be the same
                            # string used in the *.po file for gail.
                            #
                            if action.getName(j) in ["toggle", _("toggle")]:
                                checkbox = True
                                checked = cell.getState().contains( \
                                    pyatspi.STATE_CHECKED)
                                if speakAll:
                                    # Translators: this is the name of the
                                    # status column header in the message
                                    # list in Evolution.  The name needs to
                                    # match what Evolution is using.
                                    #
                                    if header.name == _("Status"):
                                        toRead = not checked
                                        useAlternativeName = True
                                        break
                                    # Translators: this is the name of the
                                    # flagged column header in the message
                                    # list in Evolution.  The name needs to
                                    # match what Evolution is using.
                                    #
                                    elif header.name == _("Flagged"):
                                        toRead = checked
                                        break
                                    if not checked:
                                        toRead = False
                                break

                    if toRead:
                        # Speak/braille the column header for this table cell
                        # if it has focus (unless it's a checkbox).
                        #
                        if (verbose or (checkbox and column == i)) \
                           and not useAlternativeName:
                            settings.brailleVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF
                            settings.speechVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF

                            utterances = speechGen.generateSpeech(
                                header,
                                includeContext=False,
                                priorObj=oldLocusOfFocus)
                            [headerRegions, focusedRegion] = \
                                         brailleGen.generateBraille(header)
                            brailleRegions.extend(headerRegions)
                            brailleRegions.append(braille.Region(" "))

                            if column == i:
                                cellWithFocus = focusedRegion
                            if speakAll or (column == i):
                                speech.speak(utterances)

                        # Speak/braille the table cell.
                        #
                        # If this cell has a column header of "Status",
                        # then speak/braille "read".
                        # If this cell has a column header of "Attachment",
                        # then speak/braille "attachment".
                        #
                        if verbose:
                            settings.brailleVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_VERBOSE
                        else:
                            settings.brailleVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF
                        settings.speechVerbosityLevel = \
                            savedSpeechVerbosityLevel
                        utterances = speechGen.generateSpeech(
                            cell,
                            includeContext=False,
                            priorObj=oldLocusOfFocus)
                        [cellRegions, focusedRegion] = \
                                           brailleGen.generateBraille(cell)

                        # Translators: this is the name of the
                        # status column header in the message
                        # list in Evolution.  The name needs to
                        # match what Evolution is using.
                        #
                        if header.name == _("Status"):
                            # Translators: we present this to the user to
                            # indicate that an email message has not been
                            # marked as having been read.
                            #
                            text = _("unread")
                            utterances = [ text ]
                            brailleRegions.append(braille.Region(text))
                            brailleRegions.append(braille.Region(" "))
                        # Translators: this is the name of the
                        # attachment column header in the message
                        # list in Evolution.  The name needs to
                        # match what Evolution is using.
                        #
                        elif header.name == _("Attachment"):
                            text = header.name
                            utterances = [ text ]
                            if column != i:
                                brailleRegions.append(braille.Region(text))
                                brailleRegions.append(braille.Region(" "))
                        # Translators: this is the name of the
                        # flagged column header in the message
                        # list in Evolution.  The name needs to
                        # match what Evolution is using.
                        #
                        elif header.name == _("Flagged"):
                            text = header.name
                            utterances = [ text ]
                            if column != i:
                                brailleRegions.append(braille.Region(text))
                                brailleRegions.append(braille.Region(" "))
                        else:
                            brailleRegions.extend(cellRegions)
                            brailleRegions.append(braille.Region(" "))

                        # If the current focus is on a checkbox then we won't
                        # have set braille line focus to its header above, so
                        # set it to the cell instead.
                        #
                        if column == i and cellWithFocus == None:
                            cellWithFocus = focusedRegion

                        if speakAll or (column == i):
                            speech.speak(utterances)

            if brailleRegions != []:
                braille.displayRegions([brailleRegions, cellWithFocus])

            settings.brailleVerbosityLevel = savedBrailleVerbosityLevel
            settings.speechVerbosityLevel = savedSpeechVerbosityLevel
            self.lastMessageColumn = column
            self.lastMessageRow = row
            settings.readTableCellRow = True
            return

        # 4) Calendar view: day view: tabbing to day with appts.
        #
        # If the focus is in the Calendar Day View on an appointment, then
        # provide the user with useful feedback. First we get the current
        # date and appointment summary from the parent. This is then followed
        # by getting the information on the current appointment.
        #
        # The start time for the appointment is determined by detecting the
        # equivalent child in the parent Calendar View's table has the same
        # y position on the screen.
        #
        # The end time for the appointment is determined by using the height
        # of the current appointment component divided by the height of a
        # single child in the parent Calendar View's table
        #
        # Both of these time values depend upon the value of a time increment
        # which is determined by the number of children in the parent Calendar
        # View's table.

        self.rolesList = [rolenames.ROLE_CALENDAR_EVENT, \
                          rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, self.rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - calendar view: " \
                          + "day view: tabbing to day with appts.")

            parent = event.source.parent
            utterances = speechGen.generateSpeech(parent,
                                                  includeContext=False,
                                                  priorObj=oldLocusOfFocus)
            [brailleRegions, focusedRegion] = \
                    brailleGen.generateBraille(parent)
            speech.speak(utterances)

            apptExtents = event.source.queryComponent().getExtents(0)

            for child in parent:
                if (child.getRole() == pyatspi.ROLE_TABLE):
                    childTable = child.queryTable()
                    noRows = childTable.nRows
                    for j in range(0, noRows):
                        row = childTable.getRowAtIndex(j)
                        appt = childTable.getAccessibleAt(row, 0)
                        extents = appt.queryComponent().getExtents(0)
                        if extents.y == apptExtents.y:
                            utterances = speechGen.generateSpeech(
                                event.source,
                                includeContext=False,
                                priorObj=oldLocusOfFocus)
                            [apptRegions, focusedRegion] = \
                                brailleGen.generateBraille(event.source)
                            brailleRegions.extend(apptRegions)
                            speech.speak(utterances)

                            startTime = 'Start time ' + \
                                self.getTimeForCalRow(j, noRows)
                            brailleRegions.append(braille.Region(startTime))
                            speech.speak(startTime)

                            apptLen = apptExtents.height / extents.height
                            endTime = 'End time ' + \
                                self.getTimeForCalRow(j + apptLen, noRows)
                            brailleRegions.append(braille.Region(endTime))
                            speech.speak(endTime)
                            braille.displayRegions([brailleRegions,
                                                    brailleRegions[0]])
                            return

        # 5) Calendar view: day view: moving with arrow keys.
        #
        # If the focus is in the Calendar Day View, check to see if there
        # are any appointments starting at the current time. If there are,
        # then provide the user with useful feedback for that appointment,
        # otherwise output the current time and state that there are no
        # appointments.
        #
        # First get the y position of the current table entry. Then compare
        # this will any Calendar Events in the parent Calendar View. If their
        # y position is the same, then speak that information.
        #
        # The end time for the appointment is determined by using the height
        # of the current appointment component divided by the height of a
        # single child in the parent Calendar View's table
        #
        # Both of these time values depend upon the value of a time increment
        # which is determined by the number of children in the parent Calendar
        # View's table.

        self.rolesList = [pyatspi.ROLE_UNKNOWN, \
                          pyatspi.ROLE_TABLE, \
                          rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, self.rolesList):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - calendar view: " \
                      + "day view: moving with arrow keys.")

            brailleRegions = []
            index = event.source.getIndexInParent()
            parent = event.source.parent
            calendarView = event.source.parent.parent
            extents = event.source.queryComponent().getExtents(0)
            noRows = parent.queryTable().nRows
            found = False

            for child in calendarView:
                if (child.getRoleName() == rolenames.ROLE_CALENDAR_EVENT):
                    apptExtents = child.queryComponent().getExtents(0)

                    if extents.y == apptExtents.y:
                        utterances = speechGen.generateSpeech(
                            child,
                            includeContext=False,
                            priorObj=oldLocusOfFocus)
                        [apptRegions, focusedRegion] = \
                            brailleGen.generateBraille(child)
                        brailleRegions.extend(apptRegions)
                        speech.speak(utterances)

                        startTime = 'Start time ' + \
                            self.getTimeForCalRow(index, noRows)
                        brailleRegions.append(braille.Region(startTime))
                        speech.speak(startTime)

                        apptLen = apptExtents.height / extents.height
                        endTime = 'End time ' + \
                            self.getTimeForCalRow(index + apptLen, noRows)
                        brailleRegions.append(braille.Region(endTime))
                        speech.speak(endTime)
                        braille.displayRegions([brailleRegions,
                                                brailleRegions[0]])
                        found = True

            if not found:
                startTime = 'Start time ' + self.getTimeForCalRow(index, noRows)
                brailleRegions.append(braille.Region(startTime))
                speech.speak(startTime)

                # Translators: this means there are no scheduled entries
                # in the calendar.
                #
                utterance = _("No appointments")
                speech.speak(utterance)
                brailleRegions.append(braille.Region(utterance))
                braille.displayRegions([brailleRegions,
                                        brailleRegions[0]])

            return

        # 6) Preferences Dialog: options list.
        #
        # Check if the focus is in one of the various options on the left
        # side of the Preferences dialog. If it is, then we just want to
        # speak the name of the page we are currently on.
        #
        # Even though it looks like the focus is on one of the page tabs
        # in this dialog, it's possible that it's actually on a table cell,
        # within a table which is contained within a scroll pane. We check
        # for this my looking for a component hierarchy of "table cell",
        # "table", "unknown" and "scroll pane".
        #
        # If this is the case, then we get the parent of the scroll pane
        # and look to see if one of its other children is a "page tab list".
        # If that's true, then we get the Nth child, when N is the index of
        # the initial table cell minus 1. We double check that this is a
        # "page tab", then if so, speak and braille that component.
        #
        # NOTE: assumes there is only one "page tab list" in the "filler"
        # component.

        self.rolesList = [pyatspi.ROLE_TABLE_CELL, \
                          pyatspi.ROLE_TABLE, \
                          pyatspi.ROLE_UNKNOWN, \
                          pyatspi.ROLE_SCROLL_PANE]
        if self.isDesiredFocusedItem(event.source, self.rolesList):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - preferences dialog: " \
                      + "table cell in options list.")

            index = event.source.getIndexInParent()
            obj = event.source.parent.parent.parent
            parent = obj.parent
            if parent.getRole() == pyatspi.ROLE_FILLER:
                for child in parent:
                    if (child.getRole() == pyatspi.ROLE_PAGE_TAB_LIST):
                        tabList = child
                        tab = tabList[index-1]
                        if (tab.getRole() == pyatspi.ROLE_PAGE_TAB):
                            self.readPageTab(tab)
                            return

        # 7) Mail view: insert attachment dialog: unlabelled arrow button.
        #
        # Check if the focus is on the unlabelled arrow button near the
        # top of the mail view Insert Attachment dialog. If it is, then
        # rather than just speak/braille "button", output something a
        # little more useful.

        self.rolesList = [pyatspi.ROLE_PUSH_BUTTON, \
                          pyatspi.ROLE_PANEL, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_SPLIT_PANE, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_DIALOG]
        if self.isDesiredFocusedItem(event.source, self.rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail insert " \
                          + "attachment dialog: unlabelled button.")

            brailleRegions = []
            # Translators: this is the unlabelled arrow button near the
            # top of the mail view Insert Attachment dialog in Evolution.
            # We give it a name.
            #
            utterance = _("Directories button")
            speech.speak(utterance)
            brailleRegions.append(braille.Region(utterance))
            braille.displayRegions([brailleRegions,
                                    brailleRegions[0]])
            return

        # 8) Mail compose window: message area
        #
        # This works in conjunction with code in section 9). Check to see if
        # focus is currently in the Mail compose window message area. If it
        # is, then, if this is the first time, save a pointer to the HTML
        # panel that will contain a variety of components that will, in turn,
        # contain the message text.
        #
        # Note that this drops through to then use the default event
        # processing in the parent class for this "focus:" event.
        if self.isMessageBodyText(event.source) \
           and event.source.getState().contains(pyatspi.STATE_EDITABLE):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail " \
                          + "compose window: message area.")

            # We are getting extra (bogus?) "focus:" events from Evolution
            # when we type the first character at the beginning of a line.
            # If the last input event was a keyboard event and the parent
            # of the locusOfFocus and the event.source are the same, and
            # the last roles hierarchy is the same as this one and
            # the last key pressed wasn't a navigation key, then just
            # ignore it. See bug #490317 for more details.
            #
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                if self.isSameObject(event.source.parent,
                                     orca_state.locusOfFocus.parent):
                    lastKey = orca_state.lastNonModifierKeyEvent.event_string
                    if self.isMessageBodyText(orca_state.locusOfFocus) \
                       and lastKey not in ["Left", "Right", "Up", "Down",
                                           "Home", "End", "Return", "Tab"]:
                        return

                    # If the last keyboard event was a "same line"
                    # navigation key, then pass this event onto the
                    # onCaretMoved() method in the parent class for
                    # speaking. See bug #516565 for more details.
                    #
                    if lastKey in ["Left", "Right", "Home", "End"]:
                        default.Script.onCaretMoved(self, event)
                        return

            self.message_panel = event.source.parent.parent

            self.presentMessageLine(event.source, newLocusOfFocus)
            return

        # 9) Spell Checking Dialog
        #
        # This works in conjunction with code in section 8). Check to see if
        # current focus is in the table of possible replacement words in the
        # spell checking dialog. If it is, then we use a cached handle to
        # the Mail compose window message area, to find out where the text
        # caret currently is, and use this to speak a selection of the
        # surrounding text, to give the user context for the current misspelt
        # word.
        if self.isSpellingSuggestionsList(event.source) \
           or self.isSpellingSuggestionsList(newLocusOfFocus):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - spell checking dialog.")

            # Braille the default action for this component.
            #
            self.updateBraille(orca_state.locusOfFocus)

            if not self.pointOfReference.get('activeDescendantInfo'):
                [badWord, allTokens] = \
                    self.getMisspelledWordAndBody(event.source,
                                                  self.message_panel)
                self.speakMisspeltWord(allTokens, badWord)

        # 10) Mail view: message area - attachments.
        #
        # Check if the focus is on the "go forward" button or the
        # "attachment button" for an attachment in the mail message
        # attachment area. (There will be a pair of these buttons
        # for each attachment in the mail message).
        #
        # If it is, then get the text which describes the current
        # attachment and speak it after doing the default action
        # for the button.
        #
        # NOTE: it is assumed that the last table cell in the table
        # contains this information.

        self.rolesList = [pyatspi.ROLE_PUSH_BUTTON, \
                         pyatspi.ROLE_FILLER, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_TABLE_CELL, \
                         pyatspi.ROLE_TABLE, \
                         pyatspi.ROLE_PANEL]
        if self.isDesiredFocusedItem(event.source, self.rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - " \
                          + "mail message area attachments.")

            # Speak/braille the default action for this component.
            #
            default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

            tmp = event.source.parent.parent
            table = tmp.parent.parent.parent
            cell = table[table.childCount-1]
            allText = self.findByRole(cell, pyatspi.ROLE_TEXT)
            utterance = "for " + self.getText(allText[0], 0, -1)
            speech.speak(utterance)
            return

        # For everything else, pass the focus event onto the parent class
        # to be handled in the default way.
        #
        # Note that this includes table cells if we only want to read the
        # current cell.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    def speakBlankLine(self, obj):
        """Returns True if a blank line should be spoken.
        Otherwise, returns False.
        """

        # Get the the AccessibleText interrface.
        try:
            text = obj.queryText()
        except NotImplementedError:
            return False

        # Get the line containing the caret
        caretOffset = text.caretOffset
        line = text.getTextAtOffset(caretOffset, \
            pyatspi.TEXT_BOUNDARY_LINE_START)

        debug.println(debug.LEVEL_FINEST,
            "speakBlankLine: start=%d, end=%d, line=<%s>" % \
            (line[1], line[2], line[0]))

        # If this is a blank line, announce it if the user requested
        # that blank lines be spoken.
        if line[1] == 0 and line[2] == 0:
            return settings.speakBlankLines
        else:
            return False

    def onStateChanged(self, event):
        """Called whenever an object's state changes.  We are only
        interested in "object:state-changed:showing" events for any
        object in the Setup Assistant.

        Arguments:
        - event: the Event
        """

        if self.isWizardNewInfoEvent(event):
            if event.source.getRole() == pyatspi.ROLE_PANEL:
                self.lastSetupPanel = event.source
            self.presentWizardNewInfo(self.getTopLevel(event.source))
            return

        # For everything else, pass the event onto the parent class
        # to be handled in the default way.
        #
        default.Script.onStateChanged(self, event)

    def presentWizardNewInfo(self, obj):
        """Causes the new information displayed in a wizard to be presented
        to the user.

        Arguments:
        - obj: the Accessible object
        """

        if not obj:
            return

        # TODO - JD: Presenting the Setup Assistant (or any Wizard) as a
        # dialog means that we will repeat the dialog's name for each new
        # "screen". We should consider a 'ROLE_WIZARD' or some other means
        # for presenting these objects.
        #
        utterances = \
            self.speechGenerator.generateSpeech(obj, role=pyatspi.ROLE_DIALOG)

        # The following falls under the heading of "suck it and see." The
        # worst case scenario is that we present the push button and then
        # process a focus:/object:state-changed:focused event and present
        # it.
        #
        if orca_state.locusOfFocus \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_PUSH_BUTTON \
           and orca_state.locusOfFocus.getState().\
               contains(pyatspi.STATE_FOCUSED):
            utterances.append(
                self.speechGenerator.generateSpeech(orca_state.locusOfFocus))

        speech.speak(utterances)

    def isWizard(self, obj):
        """Returns True if this object is, or is within, a wizard.

        Arguments:
        - obj: the Accessible object
        """

        # The Setup Assistant is a frame whose child is a panel. That panel
        # holds a bunch of other panels, one for each stage in the wizard.
        # Only the active stage's panel has STATE_SHOWING. There is also
        # one child of ROLE_FILLER which holds the buttons.
        #
        window = self.getTopLevel(obj) or obj
        if window and window.getRole() == pyatspi.ROLE_FRAME \
           and window.childCount and window[0].getRole() == pyatspi.ROLE_PANEL:
            allPanels = panelsNotShowing = 0
            for child in window[0]:
                if child.getRole() == pyatspi.ROLE_PANEL:
                    allPanels += 1
                    if not child.getState().contains(pyatspi.STATE_SHOWING):
                        panelsNotShowing += 1
            if allPanels - panelsNotShowing == 1 \
               and window[0].childCount - allPanels == 1:
                return True

        return False

    def isWizardNewInfoEvent(self, event):
        """Returns True if the event is judged to be the presentation of
        new information in a wizard. This method should be subclassed by
        application scripts as needed.

        Arguments:
        - event: the Accessible event being examined
        """

        if event.source.getRole() == pyatspi.ROLE_FRAME \
           and (event.type.startswith("window:activate") \
                or (event.type.startswith("object:state-changed:active") \
                    and event.detail1 == 1)):
            return self.isWizard(event.source)

        elif event.source.getRole() == pyatspi.ROLE_PANEL \
             and event.type.startswith("object:state-changed:showing") \
             and event.detail1 == 1 \
             and not self.isSameObject(event.source, self.lastSetupPanel):
            rolesList = [pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_FRAME]
            if self.isDesiredFocusedItem(event.source, rolesList):
                return self.isWizard(event.source)

        return False

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
        window = self.getTopLevel(event.source)
        if window and not window.getState().contains(pyatspi.STATE_ACTIVE):
            return False

        return True

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
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent) \
           and orca_state.lastNonModifierKeyEvent:
            string = orca_state.lastNonModifierKeyEvent.event_string
            if string == "Delete":
                rolesList = [pyatspi.ROLE_TABLE_CELL, \
                             pyatspi.ROLE_TREE_TABLE, \
                             pyatspi.ROLE_UNKNOWN, \
                             pyatspi.ROLE_SCROLL_PANE]
                oldLocusOfFocus = orca_state.locusOfFocus
                if self.isDesiredFocusedItem(event.source, rolesList) and \
                   self.isDesiredFocusedItem(oldLocusOfFocus, rolesList):
                    parent = event.source.parent
                    parentTable = parent.queryTable()
                    newIndex = self.getCellIndex(event.source)
                    newRow = parentTable.getRowAtIndex(newIndex)
                    oldIndex = self.getCellIndex(oldLocusOfFocus)
                    oldRow = parentTable.getRowAtIndex(oldIndex)
                    nRows = parentTable.nRows
                    if (newRow != oldRow) and (oldRow != nRows):
                        return

        # For everything else, pass the event onto the parent class
        # to be handled in the default way.
        #
        default.Script.onFocus(self, event)

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
        if self.isSpellingSuggestionsList(event.source):
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
                    if self.isSpellingSuggestionsList(target):
                        [badWord, allTokens] = \
                            self.getMisspelledWordAndBody(target,
                                                          self.message_panel)
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

# Values used to construct a time string for calendar appointments.
#
timeIncrements = {}
timeIncrements[288] = 5
timeIncrements[144] = 10
timeIncrements[96] = 15
timeIncrements[48] = 30
timeIncrements[24] = 60

minutes = {}
minutes[0] = ''
minutes[5] = '5'
minutes[10] = '10'
minutes[15] = '15'
minutes[20] = '20'
minutes[25] = '25'
minutes[30] = '30'
minutes[35] = '35'
minutes[40] = '40'
minutes[45] = '45'
minutes[50] = '50'
minutes[55] = '55'

hours = ['12', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
