# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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

"""Custom script for Evolution."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.debug as debug
import orca.default as default
import orca.atspi as atspi
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.rolenames as rolenames
import orca.braille as braille
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.speechserver as speechserver
import orca.settings as settings
import orca.chnames as chnames
import orca.where_am_I as where_am_I

from orca.orca_i18n import _ # for gettext support

class WhereAmI(where_am_I.WhereAmI):

    def __init__(self, script):
        """Create a new WhereAmI that will be used to speak information
        about the current object of interest.
        """

        where_am_I.WhereAmI.__init__(self, script)

    def _getTableCell(self, obj):
        """Get the speech utterances for a single table cell.
        """

        # Don't speak check box cells that area not checked.
        notChecked = False
        action = obj.action
        if action:
            for i in range(0, action.nActions):
                if action.getName(i) == "toggle":
                    obj.role = rolenames.ROLE_CHECK_BOX
                    if not obj.state.count(atspi.Accessibility.STATE_CHECKED):
                        notChecked = True
                    obj.role = rolenames.ROLE_TABLE_CELL
                    break

        if notChecked:
            return ""

        descendant = self._script.getRealActiveDescendant(obj)
        text = self._script.getDisplayedText(descendant)

        # For Evolution mail header list.
        if text == "Status":
            # Translators: this in reference to an e-mail message status of
            # having been read or unread.
            #
            text = _("Read")

        debug.println(self._debugLevel, "cell=<%s>" % text)

        return text

    def _hasTextSelections(self, obj):
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
        nSelections = obj.text.getNSelections()
        if nSelections:
            currentSelected = True
        else:
            otherSelected = False
            displayedText = obj.text.getText(0, -1)
            if len(displayedText) == 0:
                container = obj.parent.parent
                current = obj.parent.index
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    if (current-1) >= 0:
                        prevPanel = container.child(current-1)
                        prevObj = prevPanel.child(0)
                        if prevObj and prevObj.text:
                            if prevObj.text.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = prevObj.text.getText(0, -1)
                                if len(displayedText) == 0:
                                    current -= 1
                                    morePossibleSelections = True

                current = obj.parent.index
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    if (current+1) < container.childCount:
                        nextPanel = container.child(current+1)
                        nextObj = nextPanel.child(0)
                        if nextObj and nextObj.text:
                            if nextObj.text.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = nextObj.text.getText(0, -1)
                                if len(displayedText) == 0:
                                    current += 1
                                    morePossibleSelections = True

        return [currentSelected, otherSelected]

    def _getTextSelections(self, obj, doubleClick):
        """Get all the text applicable text selections for the given object.
        If the user doubleclicked, look to see if there are any previous
        or next text objects that also have selected text and add in their
        text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.
        - doubleClick: True if the user double-clicked the "where am I" key.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        textContents = ""
        startOffset = 0
        endOffset = 0
        if obj.text.getNSelections() > 0:
            [textContents, startOffset, endOffset] = \
                                            self._getTextSelection(obj)

        if doubleClick:
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
            current = obj.parent.index
            morePossibleSelections = True
            while morePossibleSelections:
                morePossibleSelections = False
                if (current-1) >= 0:
                    prevPanel = container.child(current-1)
                    prevObj = prevPanel.child(0)
                    displayedText = prevObj.text.getText(0, -1)
                    if len(displayedText) == 0:
                        current -= 1
                        morePossibleSelections = True
                    elif prevObj.text.getNSelections() > 0:
                        [newTextContents, start, end] = \
                                     self._getTextSelection(prevObj)
                        textContents = newTextContents + " " + textContents
                        current -= 1
                        morePossibleSelections = True

            current = obj.parent.index
            morePossibleSelections = True
            while morePossibleSelections:
                morePossibleSelections = False
                if (current+1) < container.childCount:
                    nextPanel = container.child(current+1)
                    nextObj = nextPanel.child(0)
                    displayedText = nextObj.text.getText(0, -1)
                    if len(displayedText) == 0:
                        current += 1
                        morePossibleSelections = True
                    elif nextObj.text.getNSelections() > 0:
                        [newTextContents, start, end] = \
                                     self._getTextSelection(nextObj)
                        textContents += " " + newTextContents
                        current += 1
                        morePossibleSelections = True

        return [textContents, startOffset, endOffset]

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

        # Dictionary of Setup Assistant panels already handled.
        #
        self.setupPanels = {}

        # Dictionary of Setup Assistant labels already handled.
        #
        self.setupLabels = {}

        # The last row and column we were on in the mail message header list.

        self.lastMessageColumn = -1
        self.lastMessageRow = -1

        # By default, don't present if Evolution is not the active application.
        #
        self.presentIfInactive = False

        # Evolution defines new custom roles. We need to make them known
        # to Orca for Speech and Braille output.

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

    def getWhereAmI(self):
        """Returns the "where am I" class for this script.
        """

        return WhereAmI(self)

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
                _("Toggle whether we present new mail if we are not the active script."))

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
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["toggleReadMailHandler"]))
        return keyBindings

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

    def speakSetupAssistantLabel(self, label):
        """Perform a variety of tests on this Setup Assistant label to see
        if we want to speak it.

        Arguments:
        - label: the Setup Assistant Label.
        """

        if label.state.count(atspi.Accessibility.STATE_SHOWING):
            # We are only interested in a label if all the panels in the
            # component hierarchy have states of ENABLED, SHOWING and VISIBLE.
            # If this is not the case, then just return.
            #
            obj = label.parent
            while obj and obj.role != rolenames.ROLE_APPLICATION:
                if obj.role == rolenames.ROLE_PANEL:
                    state = obj.state
                    if not state.count(atspi.Accessibility.STATE_ENABLED) or \
                       not state.count(atspi.Accessibility.STATE_SHOWING) or \
                       not state.count(atspi.Accessibility.STATE_VISIBLE):
                        return
                obj = obj.parent

            # Each Setup Assistant screen has one label in the top left
            # corner that describes what this screen is for. It has a text
            # weight attribute of 800. We always speak those labels with
            # " screen" appended.
            #
            if label.text:
                charAttributes = label.text.getAttributes(0)
                if charAttributes[0]:
                    [charKeys, charDict] = \
                        self.textAttrsToDictionary(charAttributes[0])
                    weight = charDict.get('weight')
                    if weight and weight == '800':
                        text = self.getDisplayedText(label)

                        # Only speak the screen label if we haven't already
                        # done so.
                        #
                        if text and not self.setupLabels.has_key(label):
                            # Translators: this is the name of a setup
                            # assistant window/screen in Evolution.
                            #
                            speech.speak(_("%s screen") % text, None, False)
                            self.setupLabels[label] = True

                            # If the locus of focus is a push button that's
                            # insensitive, speak/braille about it. (The
                            # Identity screen has such a component).
                            #
                            if orca_state.locusOfFocus and \
                               orca_state.locusOfFocus.role == \
                                   rolenames.ROLE_PUSH_BUTTON and \
                               (orca_state.locusOfFocus.state.count( \
                                   atspi.Accessibility.STATE_SENSITIVE) == 0):
                                self.updateBraille(orca_state.locusOfFocus)
                                speech.speakUtterances(
                                    self.speechGenerator.getSpeech( \
                                        orca_state.locusOfFocus, False))

            # It's possible to get multiple "object:state-changed:showing"
            # events for the same label. If we've already handled this
            # label, then just ignore it.
            #
            text = self.getDisplayedText(label)
            if text and not self.setupLabels.has_key(label):
                # Most of the Setup Assistant screens have a useful piece
                # of text starting with the word "Please". We want to speak
                # these. For the first screen, the useful piece of text
                # starts with "Welcome". For the last screen, it starts
                # with "Congratulations". Speak those too.
                #
                # Translators: we regret having to do this, but the
                # translated string here has to match what the translated
                # string is for Evolution.
                #
                if text.startswith(_("Please")) or \
                    text.startswith(_("Welcome")) or \
                    text.startswith(_("Congratulations")):
                    speech.speak(text, None, False)
                    self.setupLabels[label] = True

    def handleSetupAssistantPanel(self, panel):
        """Find all the labels in this Setup Assistant panel and see if
        we want to speak them.

        Arguments:
        - panel: the Setup Assistant panel.
        """

        allLabels = self.findByRole(panel, rolenames.ROLE_LABEL)
        for label in allLabels:
            self.speakSetupAssistantLabel(label)

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
        utterances = speechGen.getSpeech(tab, False)
        speech.speakUtterances(utterances)
        settings.speechVerbosityLevel = savedSpeechVerbosityLevel

        braille.displayRegions(brailleGen.getBrailleRegions(tab))

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

        text = obj.text
        if not text:
            return

        panel = obj.parent
        htmlPanel = panel.parent
        startIndex = panel.index
        i = startIndex
        total = htmlPanel.childCount
        textObjs = []
        startOffset = obj.text.caretOffset
        offset = obj.text.caretOffset
        string = ""
        done = False

        # Determine the correct "say all by" mode to use.
        #
        if settings.sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = atspi.Accessibility.TEXT_BOUNDARY_SENTENCE_END
        elif settings.sayAllStyle == settings.SAYALL_STYLE_LINE:
            mode = atspi.Accessibility.TEXT_BOUNDARY_LINE_START
        else:
            mode = atspi.Accessibility.TEXT_BOUNDARY_LINE_START

        while not done:
            accPanel = htmlPanel.accessible.getChildAtIndex(i)
            panel = atspi.Accessible.makeAccessible(accPanel)
            if panel != None:
                accTextObj = panel.accessible.getChildAtIndex(0)
                textObj = atspi.Accessible.makeAccessible(accTextObj)
                text = textObj.text
                if not text:
                    return
                textObjs.append(textObj)
                length = text.characterCount

                while offset <= length:
                    [mystr, start, end] = textObj.text.getTextAtOffset(offset,
                                                                       mode)
                    endOffset = end

                    if len(mystr) != 0:
                        string += " " + mystr

                    if mode == atspi.Accessibility.TEXT_BOUNDARY_LINE_START or \
                       len(mystr) == 0 or mystr[len(mystr)-1] in '.?!':
                        string = self.adjustForRepeats(string)
                        if string.isupper():
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
            if string.isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
            else:
                voice = settings.voices[settings.DEFAULT_VOICE]

            yield [speechserver.SayAllContext(textObjs, string,
                                              startOffset, endOffset),
                   voice]

    def __sayAllProgressCallback(self, context, type):
        """Provide feedback during the sayAll operation.
        """

        if type == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            pass
        elif type == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            offset = context.currentOffset
            for i in range(0, len(context.obj)):
                obj = context.obj[i]
                charCount = obj.text.characterCount
                if offset > charCount:
                    offset -= charCount
                else:
                    obj.text.setCaretOffset(offset)
                    break
        elif type == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            obj = context.obj[len(context.obj)-1]
            obj.text.setCaretOffset(context.currentOffset)
            orca.setLocusOfFocus(None, obj, False)

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
        if orca_state.locusOfFocus and orca_state.locusOfFocus.text:
            speech.sayAll(self.textLines(orca_state.locusOfFocus),
                          self.__sayAllProgressCallback)
        else:
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
    # 11) Setup Assistant

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

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

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_UNKNOWN]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "current message pane: " \
                          + "individual lines of text.")

            [string, caretOffset, startOffset] = \
                self.getTextLineAtCaret(event.source)
            self.updateBraille(newLocusOfFocus)
            if settings.enableSpeechIndentation:
                self.speakTextIndentation(event.source, string)
            line = self.adjustForRepeats(string)

            if self.speakNewLine(event.source):
                speech.speak(chnames.getCharacterName("\n"), None, False)

            if self.speakBlankLine(event.source):
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                speech.speak(_("blank"), None, False)
            else:
                speech.speak(line, None, False)

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

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_TABLE_CELL]
        if settings.readTableCellRow \
            and (self.isDesiredFocusedItem(event.source, rolesList)):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "current message pane: " \
                          + "standard mail header lines.")

            obj = event.source.parent.parent
            parent = obj.parent
            if parent.role == rolenames.ROLE_TABLE:
                row = parent.table.getRowAtIndex(obj.index)
                utterances = []
                regions = []
                for i in range(0, parent.table.nColumns):
                    obj = parent.table.getAccessibleAt(row, i)
                    cell = atspi.Accessible.makeAccessible(obj)

                    while cell.childCount:
                        cell = cell.child(0)

                    if cell.role == rolenames.ROLE_TEXT:
                        regions.append(braille.Text(cell))
                        [string, caretOffset, startOffset] = \
                            self.getTextLineAtCaret(cell)
                        utterances.append(string)

                braille.displayRegions([regions, regions[0]])
                speech.speakUtterances(utterances)
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

        rolesList = [rolenames.ROLE_TABLE_CELL, \
                     rolenames.ROLE_TREE_TABLE]
        if settings.readTableCellRow \
            and (self.isDesiredFocusedItem(event.source, rolesList)):
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
            row = parent.table.getRowAtIndex(event.source.index)
            column = parent.table.getColumnAtIndex(event.source.index)

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
                       ((row == 0 or row == parent.table.nRows-1) and \
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

            if orca_state.locusOfFocus.role != rolenames.ROLE_TABLE_CELL:
                speakAll = True
                message = "%d messages" % \
                    parent.table.nRows
                brailleRegions.append(braille.Region(message))
                speech.speak(message)

            for i in range(0, parent.table.nColumns):
                obj = parent.table.getAccessibleAt(row, i)
                if obj:
                    cell = atspi.Accessible.makeAccessible(obj)
                    verbose = (cell.index == event.source.index)

                    # Check if the current table cell is a check box. If it
                    # is, then to reduce verbosity, only speak and braille it,
                    # if it's checked or if we are moving the focus from to the
                    # left or right on the same row.
                    #
                    # The one exception to the above is if this is for the
                    # Status checkbox, in which case we speake/braille it if
                    # the message is unread (not checked).
                    #
                    header_obj = parent.table.getColumnHeader(i)
                    header = atspi.Accessible.makeAccessible(header_obj)

                    checkbox = False
                    toRead = True
                    action = cell.action
                    if action:
                        for j in range(0, action.nActions):
                            if action.getName(j) == "toggle":
                                checkbox = True
                                checked = cell.state.count( \
                                    atspi.Accessibility.STATE_CHECKED)
                                if speakAll:
                                    # Translators: this is the name of the
                                    # status column header in the message
                                    # list in Evolution.  The name needs to
                                    # match what Evolution is using.
                                    #
                                    if header.name == _("Status"):
                                        toRead = not checked
                                        break
                                    if not checked:
                                        toRead = False
                                break

                    if toRead:
                        # Speak/braille the column header for this table cell
                        # if it has focus (unless it's a checkbox).
                        #
                        if not checkbox and verbose:
                            settings.brailleVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF
                            settings.speechVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF

                            utterances = speechGen.getSpeech(header, False)
                            [headerRegions, focusedRegion] = \
                                         brailleGen.getBrailleRegions(header)
                            brailleRegions.extend(headerRegions)
                            brailleRegions.append(braille.Region(" "))

                            if column == i:
                                cellWithFocus = focusedRegion
                            if speakAll or (column == i):
                                speech.speakUtterances(utterances)

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
                        utterances = speechGen.getSpeech(cell, False)
                        [cellRegions, focusedRegion] = \
                                           brailleGen.getBrailleRegions(cell)

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
                            speech.speakUtterances(utterances)

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

        rolesList = [rolenames.ROLE_CALENDAR_EVENT, \
                     rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - calendar view: " \
                          + "day view: tabbing to day with appts.")

            parent = event.source.parent
            utterances = speechGen.getSpeech(parent, False)
            [brailleRegions, focusedRegion] = \
                    brailleGen.getBrailleRegions(parent)
            speech.speakUtterances(utterances)

            apptExtents = event.source.component.getExtents(0)

            for i in range(0, parent.childCount):
                child = parent.child(i)
                if (child.role == rolenames.ROLE_TABLE):
                    noRows = child.table.nRows
                    for j in range(0, noRows):
                        row = child.table.getRowAtIndex(j)
                        obj = child.table.getAccessibleAt(row, 0)
                        appt = atspi.Accessible.makeAccessible(obj)
                        extents = appt.component.getExtents(0)
                        if extents.y == apptExtents.y:
                            utterances = speechGen.getSpeech(event.source, \
                                                             False)
                            [apptRegions, focusedRegion] = \
                                brailleGen.getBrailleRegions(event.source)
                            brailleRegions.extend(apptRegions)
                            speech.speakUtterances(utterances)

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

        rolesList = [rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_TABLE, \
                     rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - calendar view: " \
                      + "day view: moving with arrow keys.")

            brailleRegions = []
            index = event.source.index
            parent = event.source.parent
            calendarView = event.source.parent.parent
            extents = event.source.component.getExtents(0)
            noRows = parent.table.nRows
            found = False

            for i in range(0, calendarView.childCount):
                child = calendarView.child(i)
                if (child.role == rolenames.ROLE_CALENDAR_EVENT):
                    apptExtents = child.component.getExtents(0)

                    if extents.y == apptExtents.y:
                        utterances = speechGen.getSpeech(child, False)
                        [apptRegions, focusedRegion] = \
                            brailleGen.getBrailleRegions(child)
                        brailleRegions.extend(apptRegions)
                        speech.speakUtterances(utterances)

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

        rolesList = [rolenames.ROLE_TABLE_CELL, \
                     rolenames.ROLE_TABLE, \
                     rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_SCROLL_PANE]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - preferences dialog: " \
                      + "table cell in options list.")

            index = event.source.index
            obj = event.source.parent.parent.parent
            parent = obj.parent
            if parent.role == rolenames.ROLE_FILLER:
                for i in range(0, parent.childCount):
                    child = parent.child(i)
                    if (child.role == rolenames.ROLE_PAGE_TAB_LIST):
                        tabList = child
                        tab = tabList.child(index-1)
                        if (tab.role == rolenames.ROLE_PAGE_TAB):
                            self.readPageTab(tab)
                            return

        # 7) Mail view: insert attachment dialog: unlabelled arrow button.
        #
        # Check if the focus is on the unlabelled arrow button near the
        # top of the mail view Insert Attachment dialog. If it is, then
        # rather than just speak/braille "button", output something a
        # little more useful.

        rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_SPLIT_PANE, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_DIALOG]
        if self.isDesiredFocusedItem(event.source, rolesList):
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

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_SCROLL_PANE]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail " \
                          + "compose window: message area.")

            self.message_panel = event.source.parent.parent

            if self.speakNewLine(event.source):
                speech.speak(chnames.getCharacterName("\n"), None, False)


            if self.speakBlankLine(event.source):
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                speech.speak(_("blank"), None, False)


        # 9) Spell Checking Dialog
        #
        # This works in conjunction with code in section 8). Check to see if
        # current focus is in the table of possible replacement words in the
        # spell checking dialog. If it is, then we use a cached handle to
        # the Mail compose window message area, to find out where the text
        # caret currently is, and use this to speak a selection of the
        # surrounding text, to give the user context for the current misspelt
        # word.

        rolesList = [rolenames.ROLE_TABLE, \
                    rolenames.ROLE_SCROLL_PANE, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_FILLER, \
                    rolenames.ROLE_DIALOG]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - spell checking dialog.")

            # Braille the default action for this component.
            #
            self.updateBraille(orca_state.locusOfFocus)

            # Look for the "Suggestions for 'xxxxx' label in the spell
            # checker dialog panel. Extract out the xxxxx. This will be the
            # misspelt word.
            #
            panel = event.source.parent.parent
            allLabels = self.findByRole(panel, rolenames.ROLE_LABEL)
            found = False
            for label in allLabels:
                if not found:
                    text = self.getDisplayedText(label)
                    if text:
                        tokens = text.split()
                    else:
                        tokens = []
                    for token in tokens:
                        if token.startswith("'"):
                            badWord = token
                            badWord = badWord[1:len(badWord)-1]
                            found = True
                            break

            # If we have a handle to the HTML message panel, then extract out
            # all the text objects, and create a list of all the words found
            # in them.
            #
            if self.message_panel != None:
                allTokens = []
                panel = self.message_panel
                allText = self.findByRole(panel, rolenames.ROLE_TEXT)
                for i in range(0, len(allText)):
                    text = self.getText(allText[i], 0, -1)
                    tokens = text.split()
                    allTokens += tokens

                self.speakMisspeltWord(allTokens, badWord)
                return

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

        rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                    rolenames.ROLE_FILLER, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_TABLE_CELL, \
                    rolenames.ROLE_TABLE, \
                    rolenames.ROLE_PANEL]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - " \
                          + "mail message area attachments.")

            # Speak/braille the default action for this component.
            #
            default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

            tmp = event.source.parent.parent
            table = tmp.parent.parent.parent
            cell = table.child(table.childCount-1)
            allText = self.findByRole(cell, rolenames.ROLE_TEXT)
            utterance = "for " + self.getText(allText[0], 0, -1)
            speech.speak(utterance)
            return

        # 11) Setup Assistant.
        #
        # If the name of the frame of the object that currently has focus is
        # "Evolution Setup Assistant", then empty out the two dictionaries
        # containing which setup assistant panels and labels we've already
        # seen.

        obj = event.source.parent
        while obj and obj.role != rolenames.ROLE_APPLICATION:
            # Translators: this is the ending of the name of the
            # Evolution Setup Assistant window.  The translated
            # form has to match what Evolution is using.  We hate
            # keying off stuff like this, but we're forced to do
            # so in this case.
            #
            if obj.role == rolenames.ROLE_FRAME and \
                obj.name.endswith(_("Assistant")):
                debug.println(self.debugLevel,
                              "evolution.locusOfFocusChanged - " \
                              + "setup assistant.")
                self.setupPanels = {}
                self.setupLabels = {}
                break
            obj = obj.parent

        # For everything else, pass the focus event onto the parent class
        # to be handled in the default way.
        #
        # Note that this includes table cells if we only want to read the
        # current cell.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    def speakNewLine(self, obj):
        """Returns True if a newline should be spoken.
           Otherwise, returns False.
        """

        # Get the the AccessibleText interrface.
        text = obj.text
        if not text:
            return False

        # Was a left or right-arrow key pressed?
        if not (orca_state.lastInputEvent and \
                orca_state.lastInputEvent.__dict__.has_key("event_string")):
            return False

        lastKey = orca_state.lastNonModifierKeyEvent.event_string
        if lastKey != "Left" and lastKey != "Right":
            return False

        # Was a control key pressed?
        mods = orca_state.lastInputEvent.modifiers
        isControlKey = mods & (1 << atspi.Accessibility.MODIFIER_CONTROL)

        # Get the line containing the caret
        caretOffset = text.caretOffset
        line = text.getTextAtOffset(caretOffset, \
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
        lineStart = line[1]
        lineEnd = line[2]

        if isControlKey:  # control-right-arrow or control-left-arrow

            # Get the word containing the caret.
            word = text.getTextAtOffset(caretOffset, \
                atspi.Accessibility.TEXT_BOUNDARY_WORD_START)
            wordStart = word[1]
            wordEnd = word[2]

            if lastKey == "Right":
                if wordStart == lineStart:
                    return True
            else:
                if wordEnd == lineEnd:
                    return True

        else:  # right arrow or left arrow

            if lastKey == "Right":
                if caretOffset == lineStart:
                    return True
            else:
                if caretOffset == lineEnd:
                    return True

        return False
    def speakBlankLine(self, obj):
        """Returns True if a blank line should be spoken.
        Otherwise, returns False.
        """

        # Get the the AccessibleText interrface.
        text = obj.text
        if not text:
            return False

        # Get the line containing the caret
        caretOffset = text.caretOffset
        line = text.getTextAtOffset(caretOffset, \
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)

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

        if event.type.endswith("showing"):
            # Check to see if this "object:state-changed:showing" event is
            # for an object in the Setup Assistant by walking back up the
            # object hierarchy until we get to the frame object and check
            # to see if it has a name that ends with "Assistant", which is
            # what we see when we configure Evolution for the first time
            # and when we add new accounts.
            #
            obj = event.source.parent
            while obj and obj.role != rolenames.ROLE_APPLICATION:
                # Translators: this is the ending of the name of the
                # Evolution Setup Assistant window.  The translated
                # form has to match what Evolution is using.  We hate
                # keying off stuff like this, but we're forced to do
                # so in this case.
                #
                if obj.role == rolenames.ROLE_FRAME and \
                    obj.name.endswith(_("Assistant")):
                    debug.println(self.debugLevel,
                                  "evolution.onStateChanged - " \
                                  + "setup assistant.")

                    # If the event is for a label see if we want to speak it.
                    #
                    if event.source.role == rolenames.ROLE_LABEL:
                        self.speakSetupAssistantLabel(event.source)
                        break

                    # If the event is for a panel and we haven't already
                    # seen this panel, then handle it.
                    #
                    elif event.source.role == rolenames.ROLE_PANEL and \
                        not self.setupPanels.has_key(event.source):
                        self.handleSetupAssistantPanel(event.source)
                        self.setupPanels[event.source] = True
                        break

                obj = obj.parent

        # For everything else, pass the event onto the parent class
        # to be handled in the default way.
        #
        default.Script.onStateChanged(self, event)

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
        if isinstance(orca_state.lastInputEvent,
                      input_event.KeyboardEvent):
            string = orca_state.lastNonModifierKeyEvent.event_string
            if string == "Delete":
                rolesList = [rolenames.ROLE_TABLE_CELL, \
                             rolenames.ROLE_TREE_TABLE, \
                             rolenames.ROLE_UNKNOWN, \
                             rolenames.ROLE_SCROLL_PANE]
                oldLocusOfFocus = orca_state.locusOfFocus
                if self.isDesiredFocusedItem(event.source, rolesList) and \
                   self.isDesiredFocusedItem(oldLocusOfFocus, rolesList):
                    parent = event.source.parent
                    newRow = parent.table.getRowAtIndex(event.source.index)
                    oldRow = parent.table.getRowAtIndex(oldLocusOfFocus.index)
                    nRows = parent.table.nRows
                    if (newRow != oldRow) and (oldRow != nRows):
                        return

        # For everything else, pass the event onto the parent class
        # to be handled in the default way.
        #
        default.Script.onFocus(self, event)

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
