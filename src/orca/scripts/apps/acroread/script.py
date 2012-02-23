# Orca
#
# Copyright 2007-2009 Sun Microsystems Inc. and Joanmarie Diggs
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

"""Custom script for acroread"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2007-2009 Sun Microsystems Inc. Joanmarie Diggs"
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.scripts.default as default
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech

from orca.orca_i18n import _ # for gettext support
from orca.orca_i18n import ngettext

########################################################################
#                                                                      #
# The acroread script class.                                           #
#                                                                      #
########################################################################

class Script(default.Script):

    ROLE_DOCUMENT = "Document"
    ROLE_LINK = "Link"

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        self.debugLevel = debug.LEVEL_FINEST
        default.Script.__init__(self, app)

        # To handle the multiple, identical object:text-caret-moved events
        # and possible focus events that result from a single key press
        #
        self.currentInputEvent = None

        # To handle the case when we get an object:text-caret-moved event
        # for some text we just left, but which is still showing on the
        # screen.
        #
        self.lastCaretMovedLine = None

        # To minimize chattiness related to focused events when the Find
        # toolbar is active.
        #
        self.findToolbarActive = False
        self.findToolbarName = None
        self.preFindLine = None

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

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["object:state-changed:checked"]           = \
            self.onStateChanged
        listeners["object:state-changed:focused"]           = \
            self.onStateChanged

        return listeners

    def getDocument(self, locusOfFocus):
        """ Obtains the Document object that contains the locusOfFocus.

        Arguments:
        - locusOfFocus: the locusOfFocus

        Returns: the Document object, if found.
        """

        document = None
        obj = locusOfFocus
        while obj.getRole() != pyatspi.ROLE_UNKNOWN:
            obj = obj.parent

        # This is probably it, but the parent of a text object
        # in a table also has a role of 'unknown' which in turn
        # has a parent with a role of 'unknown'.  The parent of
        # the Document object is a drawing area.
        #
        if obj.parent.getRole() == pyatspi.ROLE_DRAWING_AREA:
            document = obj
        else:
            while obj.getRole() != pyatspi.ROLE_TABLE:
                obj = obj.parent
            # For now, let's assume no nested tables! :-)
            #
            while obj.getRole() != pyatspi.ROLE_UNKNOWN:
                obj = obj.parent
            document = obj

        return document

    def findNodeInDocument(self, obj):
        """ Obtains the location of an object with respect to the
        Document object.

        Arguments:
        - obj: the accessible whose location we're trying to obtain

        Returns: a list that represents the object's position,
        ordered from child to parent
        """

        nodeList = []
        document = self.getDocument(obj)
        while obj != document:
            nodeList.append(obj.getIndexInParent())
            obj = obj.parent

        return nodeList

    def getNextTextObject(self, obj, nodeList=None):
        """A generator of objects with text in the Document object.
        Acroread organizes document content into a collection of
        individual objects that contain (or have associated) text
        and drawing areas which contain such objects along with
        additional drawing areas. The depth of the drawing areas
        in any given document or drawing area is unknown.

        Arguments:
        - obj:      an Accessible that contains children
        - nodeList: a list reflecting the current object's position
        """

        if nodeList:
            index = nodeList.pop()
        else:
            index = 0

        for i in range(index, obj.childCount):
            child = obj[i]
            for nextObject in self.getNextTextObject(child, nodeList):
                yield nextObject
            yield child

    def getTableAndDimensions(self, obj):
        """Get the table that this text object is in, along with its
        dimensions.

        Arguments:
        - obj: a text object within the Document object.

        Returns the table that this text object cell is in, along with
        the number of rows and columns.
        """

        table = None
        rows = 0
        columns = 0

        # HACK: Rows, columns, and cells are not labeled or assigned
        # roles.  However, the table structure and what can claim focus
        # SEEM to be consistent. So let's punt until things get properly
        # labeled.
        #
        rolesList = [pyatspi.ROLE_TEXT,
                     pyatspi.ROLE_UNKNOWN,
                     pyatspi.ROLE_UNKNOWN,
                     pyatspi.ROLE_TABLE]
        if self.utilities.hasMatchingHierarchy(obj, rolesList):
            table = obj.parent.parent.parent
            rows = table.childCount
            columns = table[0].childCount

        return [table, rows, columns]

    def getCellCoordinates(self, table, cell):
        """Get the coordinates of the specified text object with respect
         to the table that contains it.

        Arguments:
        - obj: a text object within a table

        Returns the row number and column number.
        """

        # HACK: Again, these things are not labeled or assigned roles,
        # so we're punting for now.
        #
        column = cell.parent.getIndexInParent() + 1
        row = cell.parent.parent.getIndexInParent() + 1

        return [row, column]

    def checkForTableBoundary (self, oldFocus, newFocus):
        """Check to see if we've crossed any table boundaries,
        speaking the appropriate details when we have.

        Arguments:
        - oldFocus: Accessible that is the old locus of focus
        - newFocus: Accessible that is the new locus of focus
        """

        if oldFocus == None or newFocus == None:
            return

        [oldFocusIsTable, oldFocusRows, oldFocusColumns] = \
                   self.getTableAndDimensions(oldFocus)
        [newFocusIsTable, newFocusRows, newFocusColumns] = \
                   self.getTableAndDimensions(newFocus)

        # [[[TODO: JD - It is possible to move focus into the object
        # that contains the object that contains the text object. We
        # need to detect this and adjust accordingly.]]]

        if not oldFocusIsTable and newFocusIsTable:
            # Translators: this represents the number of rows in a table.
            #
            rowString = ngettext("table with %d row",
                                 "table with %d rows",
                                 newFocusRows) % newFocusRows
            # Translators: this represents the number of columns in a table.
            #
            colString = ngettext("%d column",
                                 "%d columns",
                                 newFocusColumns) % newFocusColumns

            line = rowString + " " + colString
            self.presentMessage(line)

        elif oldFocusIsTable and not newFocusIsTable:
            # We've left a table.  Announce this fact.
            #
            self.presentMessage(_("leaving table."))

        elif oldFocusIsTable and newFocusIsTable:
            # See if we've crossed a cell boundary.  If so, speak
            # what has changed (per Mike).
            #
            [oldRow, oldCol] = \
                   self.getCellCoordinates(oldFocusIsTable, oldFocus)
            [newRow, newCol] = \
                   self.getCellCoordinates(newFocusIsTable, newFocus)
            # We can't count on being in the first/last cell
            # of the new row -- only the first/last cell of
            # the new row that contains data.
            #
            if newRow != oldRow:
                # Translators: this represents the row and column we're
                # on in a table.
                #
                line = _("row %(row)d, column %(column)d") \
                       % {"row": newRow, "column": newCol}
                self.presentMessage(line)
            elif newCol != oldCol:
                # Translators: this represents the column we're
                # on in a table.
                #
                line = _("column %d") % newCol
                self.presentMessage(line)

    def isInFindToolbar(self, obj):
        """Examines the current object to identify if it is in the Find
        tool bar.  If so, it also sets findToolbarName so that we can
        identify this frame by name independent of localization.

        Arguments:
        - obj: an Accessible

        Returns True if the object is in the Find tool bar.
        """

        inFindToolbar = False
        rolesList = [pyatspi.ROLE_DRAWING_AREA,
                     pyatspi.ROLE_DRAWING_AREA,
                     pyatspi.ROLE_DRAWING_AREA,
                     pyatspi.ROLE_TOOL_BAR,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_FRAME]

        try:
            while obj.getRole() != pyatspi.ROLE_DRAWING_AREA:
                obj = obj.parent
            if self.utilities.hasMatchingHierarchy(obj, rolesList):
                inFindToolbar = True
                frame = self.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_FRAME], [])
                self.findToolbarName = frame.name
        except:
            pass

        return inFindToolbar

    def onFocus(self, event):
        """Called whenever an object gets focus. Overridden in this script
        because we sometimes get a focus event in addition to caret-moved
        events when we change from one area in the document to another. We
        want to minimize the repetition of text along with the unnecessary
        speaking of object types (e.g. drawing area, text, etc.).

        Arguments:
        - event: the Event
        """

        self.currentInputEvent = None

        # We sometimes get focus events for items that don't --
        # or don't yet) have focus.  Ignore these.
        #
        if event.source.getRole() in [pyatspi.ROLE_CHECK_BOX,
                                      pyatspi.ROLE_PUSH_BUTTON,
                                      pyatspi.ROLE_RADIO_BUTTON] \
           and not event.source.getState().contains(pyatspi.STATE_FOCUSED):
            return

        if not event.source.getState().contains(pyatspi.STATE_SHOWING):
            return

        if not self.findToolbarActive \
           and event.source.getRole() == pyatspi.ROLE_TEXT:
            parent = event.source.parent
            if parent and parent.getRole() in [pyatspi.ROLE_DRAWING_AREA,
                                               pyatspi.ROLE_UNKNOWN]:
                # We're going to get at least one (and likely several)
                # caret-moved events which will cause this to get spoken,
                # so skip it for now.
                #
                return

        if event.source.getRole() == pyatspi.ROLE_DRAWING_AREA:
            # A drawing area can claim focus when visually what has focus is
            # a text object that is a child of the drawing area.  When this
            # occurs, Orca doesn't see the text.  Therefore, try to figure out
            # where we are based on where we were and what key we pressed.
            # Then set the event.source accordingly before handing things off
            # to the default script.
            #
            debug.println(self.debugLevel, "acroread: Drawing area bug")
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            locusOfFocusIndex = orca_state.locusOfFocus.getIndexInParent()
            childIndex = None

            # [[[TODO: JD - These aren't all of the possibilities.  This is
            # very much a work in progress and of testing.]]]
            #
            if lastKey == "Up":
                childIndex = locusOfFocusIndex - 1
            elif lastKey == "Down":
                childIndex = locusOfFocusIndex + 1
            elif lastKey == "Right" or lastKey == "End":
                childIndex = locusOfFocusIndex
            elif lastKey == "Left" or lastKey == "Home":
                childIndex = locusOfFocusIndex

            if (childIndex >= 0):
                child = event.source[childIndex]
                event.source = child

        default.Script.onFocus(self, event)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes. Overridden
        in this script to minimize the repetition of text along with
        the unnecessary speaking of object types.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        if not newLocusOfFocus or (oldLocusOfFocus == newLocusOfFocus):
            return

        # Eliminate unnecessary chattiness related to the Find toolbar.
        #
        if self.findToolbarActive:
            if newLocusOfFocus.getRole() == pyatspi.ROLE_TEXT:
                newText = self.getTextLineAtCaret(newLocusOfFocus)
                if newText == self.preFindLine:
                    orca.setLocusOfFocus(
                        event, oldLocusOfFocus, notifyScript=False)
                    return
            if newLocusOfFocus.getRole() == pyatspi.ROLE_DRAWING_AREA:
                orca.setLocusOfFocus(event, oldLocusOfFocus, notifyScript=False)
                return

            utterances = \
                 self.speechGenerator.generateSpeech(newLocusOfFocus)
            speech.speak(utterances)
            self.displayBrailleForObject(newLocusOfFocus)
            orca.setLocusOfFocus(event, newLocusOfFocus, notifyScript=False)
            return

        # Eliminate unnecessary chattiness in the Search panel.
        #
        if newLocusOfFocus.getRole() == pyatspi.ROLE_PUSH_BUTTON \
           and oldLocusOfFocus \
           and oldLocusOfFocus.getRole() == self.ROLE_LINK \
           and newLocusOfFocus.name == oldLocusOfFocus.name:
            return

        # Eliminate general document chattiness.
        #
        if newLocusOfFocus.getRole() in [self.ROLE_DOCUMENT,
                                         pyatspi.ROLE_DRAWING_AREA]:
            orca.setLocusOfFocus(event, newLocusOfFocus, notifyScript=False)
            return

        elif newLocusOfFocus.getRole() == self.ROLE_LINK:
            # It seems that this will be the only event we will get.  But
            # the default script's onFocus will result in unnecessary
            # verboseness: reporting the drawing area(s) in which this link
            # is contained, speaking the periods in a table of contents, etc.
            #
            utterances = self.speechGenerator.generateSpeech(newLocusOfFocus)
            adjustedUtterances = []
            for utterance in utterances:
                adjustedUtterances.append(
                    self.utilities.adjustForRepeats(utterance))
            speech.speak(adjustedUtterances)
            self.displayBrailleForObject(newLocusOfFocus)
            orca.setLocusOfFocus(event, newLocusOfFocus, notifyScript=False)
            return

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.  Overridden in this script
        because we want to minimize the repetition of text and the speaking
        of erroneous events.

        Arguments:
        - event: the Event
        """

        lastInputEvent = orca_state.lastInputEvent
        lastKey, mods = self.utilities.lastKeyAndModifiers()

        # A single keypress usually results in multiple, not necessarily
        # identical, caret-moved events.  Check to see if the events are
        # identical or very closely timed (time chosen based on testing).
        #
        if self.currentInputEvent and lastInputEvent:
            timeDiff = abs(self.currentInputEvent.time - lastInputEvent.time)
            if self.currentInputEvent == lastInputEvent or timeDiff < 0.2:
                return

        # Changing pages sometimes results in a caret-moved event for
        # text that may or may NOT have had focus recently.  Sometimes
        # we luck out and it's not showing.
        #
        if not event.source.getState().contains(pyatspi.STATE_SHOWING):
            return

        # Other times, it's showing, but happens to be the text we just
        # left. Since this SEEMS limited to page up/page down, let's be
        # conservative until we have evidence to the contrary.
        #
        textLine = self.getTextLineAtCaret(event.source)
        isOldLine = textLine == self.lastCaretMovedLine and \
                    (lastKey == "Page_Down" or lastKey == "Page_Up")
        if isOldLine:
            self.lastCaretMovedLine = None
            return
        else:
            self.lastCaretMovedLine = textLine

        # [[[TODO: JD - Sometimes it's showing AND we didn't just leave
        # it. This also seems to occur sometimes with the Find toolbar.]]]

        self.currentInputEvent = orca_state.lastInputEvent
        self.checkForTableBoundary(orca_state.locusOfFocus, event.source)
        default.Script.onCaretMoved(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        if event.type.startswith("object:state-changed:checked") \
           and event.source.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            # Radio buttons in the Search panel are not automatically
            # selected when you arrow to them.  You have to press Space
            # to select the current radio button.  Watch for this.
            #
            self.visualAppearanceChanged(event, event.source)
            return

        elif event.type.startswith("object:state-changed:focused") \
             and event.detail1 == 1:
            if event.source.getRole() == pyatspi.ROLE_PUSH_BUTTON:
                # Try to minimize chattiness in the Search panel
                #
                utterances = \
                     self.speechGenerator.generateSpeech(event.source)
                speech.speak(utterances)
                self.displayBrailleForObject(event.source)
                orca.setLocusOfFocus(event, event.source, notifyScript=False)
                return

            elif event.source.getRole() == pyatspi.ROLE_TEXT:
                # There's an excellent chance that the Find toolbar just
                # gained focus.  Check.
                #
                if self.isInFindToolbar(event.source):
                    self.findToolbarActive = True

        default.Script.onStateChanged(self, event)

    def onWindowDeactivated(self, event):
        """Called whenever a toplevel window is deactivated. Overridden
        in this script to deal with significant chattiness surrounding
        the use of the Find toolbar.

        Arguments:
        - event: the Event
        """

        locusOfFocus = orca_state.locusOfFocus

        if event.source.name == self.findToolbarName:
            self.findToolbarActive = False
        else:
            try:
                locusOfFocus.queryText()
            except NotImplementedError:
                pass
            else:
                self.preFindLine = self.getTextLineAtCaret(locusOfFocus)

        default.Script.onWindowDeactivated(self, event)

    def textLinesFromNodeList(self, obj, nodeList=None):
        """A generator that can be used to iterate over each line of a
        text object, starting at the caret offset. Overridden here
        because we are not getting any RELATION_FLOWS_TO from acroread.

        Arguments:
        - obj:      An Accessible that contains children.  Initially, the
                    document itself.
        - nodeList: A list reflecting the position of the current text object
        """

        for textObj in self.getNextTextObject(obj, nodeList):
            for [context, acss] in default.Script.textLines(self, textObj):
                yield [context, acss]

    def sayAll(self, inputEvent):
        """Speaks the contents of the document beginning with the present
        location.  Overridden in this script because the default sayAll
        only speaks the current text object.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        if orca_state.locusOfFocus:
            nodeList = self.findNodeInDocument(orca_state.locusOfFocus)
            document = self.getDocument(orca_state.locusOfFocus)
            # Note:  We get the correct progress callback, but acroread
            # doesn't seem to respond to setCaretOffset, so we cannot
            # update our location when sayAll is interrupted or finished.
            #
            speech.sayAll(self.textLinesFromNodeList(document, nodeList),
                          self.__sayAllProgressCallback)
        else:
            default.Script.sayAll(self, inputEvent)

        return True

    def sayWord(self, obj):
        """Speaks the word at the caret.  Overridden here because we seem
        to be getting the details of the word we just left when moving
        forward with Control Right Arrow. Control Left Arrow works as
        expected with the default script with the exception of crossing
        over a blank line (which sometimes causes the word with focus to
        be repeated).  Both problems are addressed here.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        if not (obj.parent.getRole() in [pyatspi.ROLE_DRAWING_AREA,
                                         pyatspi.ROLE_UNKNOWN]):
            default.Script.sayWord(self, obj)

        else:
            text = obj.queryText()
            offset = text.caretOffset
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey == "Right":
                penultimateWord = orca_state.lastWord
                [lastWord, startOffset, endOffset] = \
                    text.getTextAtOffset(offset,
                                         pyatspi.TEXT_BOUNDARY_WORD_START)
                [word, startOffset, endOffset] = \
                    text.getTextAfterOffset(endOffset+1,
                                 pyatspi.TEXT_BOUNDARY_WORD_START)
                if len(penultimateWord) > 0:
                    lastCharPW = penultimateWord[len(penultimateWord) - 1]
                    if lastCharPW == "\n":
                        voice = self.voices[settings.DEFAULT_VOICE]
                        speech.speakCharacter("\n", voice)
                        if penultimateWord != lastWord:
                            word = lastWord

            if lastKey == "Left":
                lastWord = orca_state.lastWord
                [word, startOffset, endOffset] = \
                    text.getTextAtOffset(offset,
                                 pyatspi.TEXT_BOUNDARY_WORD_START)
                if len(word) > 0:
                    lastChar = word[len(word) - 1]
                    if lastChar == "\n" and lastWord != word:
                        voice = self.voices[settings.DEFAULT_VOICE]
                        speech.speakCharacter("\n", voice)
                    if lastWord == word:
                        return

            if self.utilities.linkIndex(obj, offset) >= 0:
                voice = self.voices[settings.HYPERLINK_VOICE]
            elif word.decode("UTF-8").isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            word = self.utilities.adjustForRepeats(word)
            orca_state.lastWord = word
            speech.speak(word, voice)
            self.speakTextSelectionState(obj, startOffset, endOffset)
