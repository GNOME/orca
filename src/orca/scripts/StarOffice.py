# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

import orca.debug as debug
import orca.atspi as atspi
import orca.default as default
import orca.input_event as input_event
import orca.rolenames as rolenames
import orca.orca as orca
import orca.braille as braille
import orca.braillegenerator as braillegenerator
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.settings as settings
import orca.keybindings as keybindings
import orca.util as util

from orca.orca_i18n import _ # for gettext support

inputLineForCell = None

def locateInputLine(obj):
    """Return the spread sheet input line. This only needs to be found
    the very first time a spread sheet table cell gets focus. We use the
    table cell to work back up the component hierarchy until we have found
    the common panel that both it and the input line reside in. We then
    use that as the base component to search for a component which has a
    paragraph role. This will be the input line.

    Arguments:
    - obj: the spread sheet table cell that has just got focus.

    Returns the spread sheet input line component.
    """

    inputLine = None
    panel = obj.parent.parent.parent.parent
    if panel and panel.role == rolenames.ROLE_PANEL:
        allParagraphs = util.findByRole(panel, rolenames.ROLE_PARAGRAPH)
        if len(allParagraphs) == 1:
            inputLine = allParagraphs[0]
        else:
            debug.println(debug.LEVEL_SEVERE,
                  "StarOffice: locateInputLine: incorrect paragraph count.")
    else:
        debug.println(debug.LEVEL_SEVERE,
                  "StarOffice: locateInputLine: couldn't find common panel.")

    return inputLine

def isSpreadSheetCell(obj):
    """Return an indication of whether the given obj is a spread sheet
    table cell.

    Arguments:
    - obj: the object to check.

    Returns True if this is a table cell, False otherwise.
    """

    rolesList = [rolenames.ROLE_TABLE_CELL, \
                 rolenames.ROLE_TABLE, \
                 rolenames.ROLE_UNKNOWN, \
                 rolenames.ROLE_SCROLL_PANE, \
                 rolenames.ROLE_PANEL, \
                 rolenames.ROLE_ROOT_PANE, \
                 rolenames.ROLE_FRAME, \
                 rolenames.ROLE_APPLICATION]
    return util.isDesiredFocusedItem(obj, rolesList)

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Overrides _getBrailleRegionsForTableCell so that, when we are in 
    a spread sheet, we can braille the location of the table cell as well 
    as the contents.
    """

    def _getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a table cell. If this isn't inside a
        spread sheet, just return the regions returned by the default
        table cell braille handler.

        Arguments:
        - obj: the table cell

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        global inputLineForCell, isSpreadSheetCell, locateInputLine

        if isSpreadSheetCell(obj):
            if inputLineForCell == None:
                inputLineForCell = locateInputLine(obj)

            text = util.getDisplayedText(obj)
            regions = []
            componentRegion = braille.Component(obj, text)
            regions.append(componentRegion)

            # If the spread sheet table cell has something in it, then we
            # want to append the name of the cell (which will be its location).
            # Note that if the cell was empty, then util.getDisplayedText will
            # have already done this for us.
            #
            if obj.text:
                objectText = obj.text.getText(0, -1)
                if objectText and len(objectText) != 0:
                    regions.append(braille.Region(" " + obj.name))

            return [regions, componentRegion]

        else:
            brailleGen = braillegenerator.BrailleGenerator
            regions = brailleGen._getBrailleRegionsForTableCell(self, obj)

            return regions

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForTableCell so that, when we are in a spread
    sheet, we can speak the location of the table cell as well as the 
    contents.
    """

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        speechGen = speechgenerator.SpeechGenerator
        utterances = speechGen._getSpeechForTableCell(self, obj, 
                                                      already_focused)

        global inputLineForCell, isSpreadSheetCell, locateInputLine

        if isSpreadSheetCell(obj):

            if inputLineForCell == None:
                inputLineForCell = locateInputLine(obj)

            # If the spread sheet table cell has something in it, then we
            # want to append the name of the cell (which will be its location).
            # Note that if the cell was empty, then util.getDisplayedText will
            # have already done this for us.
            #
            if obj.text:
                objectText = obj.text.getText(0, -1)
                if objectText and len(objectText) != 0:
                    utterances.append(" " + obj.name)

        return utterances

########################################################################
#                                                                      #
# The StarOffice script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # A handle to the last spread sheet cell encountered.
        #
        self.lastCell = None

        # The following variables will be used to try to determine if we've
        # already handled this misspelt word (see readMisspeltWord() for
        # more details.

        self.lastTextLength = -1
        self.lastBadWord = ''
        self.lastStartOff = -1
        self.lastEndOff = -1

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """

        return BrailleGenerator()

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator()

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to add a handler to return the contents of
        the input line.
        """

        default.Script.setupInputEventHandlers(self)

        self.speakInputLineHandler = input_event.InputEventHandler(
            Script.speakInputLine,
            _("Speaks the contents of the input line."))

    def getKeyBindings(self):
        """Defines the key bindings for this script. Setup the default
        key bindings, then add one in for reading the input line.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                1 << orca.MODIFIER_ORCA,
                1 << orca.MODIFIER_ORCA,
                self.speakInputLineHandler))

        return keyBindings

    def speakInputLine(self, inputEvent):
        """Speak the contents of the spread sheet input line (assuming we 
        have a handle to it - generated when we first focus on a spread 
        sheet table cell.

        This will be either the contents of the table cell that has focus
        or the formula associated with it.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "StarOffice.speakInputLine.")

        # Check to see if the current focus is a table cell.
        #
        if isSpreadSheetCell(orca.locusOfFocus):
            if inputLineForCell and inputLineForCell.text:
                inputLine = inputLineForCell.text.getText(0,-1)
                if not inputLine:
                    inputLine = _("empty")
                debug.println(self.debugLevel,
                        "StarOffice.speakInputLine: contents: %s" % inputLine)
                speech.speak(inputLine)

    def readMisspeltWord(self, event, pane):
        """Speak/braille the current misspelt word plus its context.
           The spell check dialog contains a "paragraph" which shows the
           context for the current spelling mistake. After speaking/brailling
           the default action for this component, that a selection of the
           surronding text from that paragraph with the misspelt word is also
           spoken.

        Arguments:
        - event: the event.
        - pane: the option pane in the spell check dialog.
        """

        paragraph = util.findByRole(pane, rolenames.ROLE_PARAGRAPH)

        # Determine which word is the misspelt word. This word will have
        # non-default text attributes associated with it.

        textLength = paragraph[0].text.characterCount
        startFound = False
        endOff = textLength
        for i in range(0, textLength):
            attributes = paragraph[0].text.getAttributes(i)
            if len(attributes[0]) != 0:
                if not startFound:
                    startOff = i
                    startFound = True
            else:
                if startFound:
                    endOff = i
                    break

        badWord = paragraph[0].text.getText(startOff, endOff-1)

        # Note that we often get two or more of these focus or property-change
        # events each time there is a new misspelt word. We extract the
        # length of the line of text, the misspelt word, the start and end
        # offsets for that word and compare them against the values saved
        # from the last time this routine was called. If they are the same
        # then we ignore it.

        debug.println(self.debugLevel, \
            "StarOffice.readMisspeltWord: type=%s  word=%s(%d,%d)  len=%d" % \
            (event.type, badWord, startOff, endOff, textLength))

        if (textLength == self.lastTextLength) and \
           (badWord == self.lastBadWord) and \
           (startOff == self.lastStartOff) and \
           (endOff == self.lastEndOff):
            return

        # Create a list of all the words found in the misspelt paragraph.
        #
        text = paragraph[0].text.getText(0, -1)
        allTokens = text.split()

        util.speakMisspeltWord(allTokens, badWord)

        # Save misspelt word information for comparison purposes next
        # time around.
        #
        self.lastTextLength = textLength
        self.lastBadWord = badWord
        self.lastStartOff = startOff
        self.lastEndOff = endOff

    def endOfLink(self, obj, word, startOffset, endOffset):
        """Return an indication of whether the given word contains the
           end of a hypertext link.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - word: the word to check
        - startOffset: the start offset for this word
        - endOffset: the end offset for this word

        Returns True if this word contains the end of a hypertext link.
        """

        nLinks = obj.hypertext.getNLinks()
        links = []
        for i in range(0, nLinks):
            links.append(obj.hypertext.getLink(i))

        for i in range(0, len(links)):
            if links[i].endIndex > startOffset and \
               links[i].endIndex <= endOffset:
                return True

        return False

    def sayWriterWord(self, obj, word, startOffset, endOffset):
        """Speaks the given word in the appropriate voice. If this word is
        a hypertext link and it is also at the end offset for one of the
        links, then the word "link" is also spoken.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - word: the word to speak
        - startOffset: the start offset for this word
        - endOffset: the end offset for this word
        """

        isHyperText = False
        voices = settings.voices

        for i in range(startOffset, endOffset):
            if util.getLinkIndex(obj, i) >= 0:
                isHyperText = True
                voice = voices[settings.HYPERLINK_VOICE]
                break
            elif word.isupper():
                voice = voices[settings.UPPERCASE_VOICE]
            else:
                voice = voices[settings.DEFAULT_VOICE]

        speech.speak(word, voice)
        if self.endOfLink(obj, word, startOffset, endOffset):
            speech.speak(_("link"))

    # This method tries to detect and handle the following cases:
    # 1) Writer: text paragraph.
    # 2) Writer: spell checking dialog.

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

        # util.printAncestry(event.source)

        # 1) Writer: text paragraph.
        #
        # When the focus is on a paragraph in the Document view of the Writer,
        # then just speak/braille the current line (rather than speaking a
        # bogus initial "paragraph" utterance as well).

        rolesList = [rolenames.ROLE_PARAGRAPH, \
                     rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_ROOT_PANE, \
                     rolenames.ROLE_FRAME]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                  "StarOffice.locusOfFocusChanged - Writer: text paragraph.")

            result = util.getTextLineAtCaret(event.source)

            # Check to see if there are any hypertext links in this paragraph.
            # If no, then just speak the whole line. Otherwise, split the
            # line into words and call sayWriterWord() to speak that token
            # in the appropriate voice.
            #
            hypertext = event.source.hypertext
            if not hypertext or (hypertext.getNLinks() == 0):
                speech.speak(result[0], None, False)
            else:
                started = False
                startOffset = 0
                for i in range(0, len(result[0])):
                    if result[0][i] == ' ':
                        if started:
                            endOffset = i
                            self.sayWriterWord(event.source,
                                result[0][startOffset:endOffset+1],
                                startOffset, endOffset)
                            startOffset = i
                            started = False
                    else:
                        if not started:
                            startOffset = i
                            started = True

                if started:
                    endOffset = len(result[0])
                    self.sayWriterWord(event.source,
                                       result[0][startOffset:endOffset],
                                       startOffset, endOffset)

            braille.displayRegions(brailleGen.getBrailleRegions(event.source))

            return

        # 2) Writer: spell checking dialog.
        #
        # Check to see if the Spell Check dialog has just appeared and got
        # focus. If it has, then speak/braille the current misspelt word
        # plus its context.
        #
        # Note that in order to make sure that this focus event is for the
        # spell check dialog, a check is made of the localized name of the
        # option pane. Translators for other locales will need to ensure that
        # their translation of this string matches what StarOffice uses in
        # that locale.

        rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                     rolenames.ROLE_OPTION_PANE, \
                     rolenames.ROLE_DIALOG, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(event.source, rolesList):
            pane = event.source.parent
            if pane.name.startswith(_("Spellcheck:")):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Writer: spell check dialog.")

                self.readMisspeltWord(event, pane)

                # Fall-thru to process the event with the default handler.

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    # This method tries to detect and handle the following cases:
    # 1) Writer: spell checking dialog.

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

        # util.printAncestry(event.source)

        # 1) Writer: spell checking dialog.
        #
        # Check to see if if we've had a property-change event for the
        # accessible name for the option pane in the spell check dialog.
        # This (hopefully) means that the user has just corrected a
        # spelling mistake, in which case, speak/braille the current
        # misspelt word plus its context.
        #
        # Note that in order to make sure that this focus event is for the
        # spell check dialog, a check is made of the localized name of the
        # option pane. Translators for other locales will need to ensure that
        # their translation of this string matches what StarOffice uses in
        # that locale.

        rolesList = [rolenames.ROLE_OPTION_PANE, \
                     rolenames.ROLE_DIALOG, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(event.source, rolesList):
            pane = event.source
            if pane.name.startswith(_("Spellcheck:")):
                debug.println(self.debugLevel,
                      "StarOffice.onNameChanged - Writer: spell check dialog.")

                self.readMisspeltWord(event, pane)

                # Fall-thru to process the event with the default handler.

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.onNameChanged(self, event)

    # This method tries to detect and handle the following cases:
    # 1) Calc: spread sheet Name Box line.

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

        # util.printAncestry(event.source)

        # 1) Calc: spread sheet input line.
        #
        # If this "object:selection-changed" is for the spread sheet Name
        # Box, then check to see if the current locus of focus is a spread
        # sheet cell. If it is, and the contents of the input line are
        # different from what is displayed in that cell, then speak "has
        # formula" and append it to the braille line.
        #
        rolesList = [rolenames.ROLE_LIST, \
                     rolenames.ROLE_COMBO_BOX, \
                     rolenames.ROLE_TOOL_BAR, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_ROOT_PANE, \
                     rolenames.ROLE_FRAME, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(event.source, rolesList):
            if orca.locusOfFocus.role == rolenames.ROLE_TABLE_CELL:
                cell = orca.locusOfFocus

                # We are getting two "object:selection-changed" events 
                # for each spread sheet cell move, so in order to prevent 
                # appending "has formula" twice, we only do it if the last 
                # cell is different from this one.
                #
                if cell != self.lastCell:
                    self.lastCell = cell

                    if cell.text:
                        cellText = cell.text.getText(0, -1)
                        if cellText and len(cellText) != 0:
                            if inputLineForCell and inputLineForCell.text:
                                inputLine = inputLineForCell.text.getText(0,-1)
                                if inputLine and len(inputLine) != 0:
                                    if inputLine != cellText:
                                        hf = _(" has formula")
                                        speech.speak(hf, None, False)

                                        line = braille.getShowingLine()
                                        line.addRegion(braille.Region(hf))
                                        braille.refresh()
                                        #
                                        # Fall-thru to process the event with
                                        # the default handler.

        default.Script.onSelectionChanged(self, event)

