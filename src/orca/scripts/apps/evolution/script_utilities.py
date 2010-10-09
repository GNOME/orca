# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.script_utilities as script_utilities
import orca.settings as settings

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        script_utilities.Utilities.__init__(self, script)

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def isMessageBody(self, obj):
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

        topLevel = self.topLevelObject(obj.parent)
        if not self.isSameObject(topLevel, self._script.spellCheckDialog):
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
                        self._script.spellCheckDialog = topLevel
                        return True
        else:
            return True

        return False

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
        window = self.topLevelObject(obj) or obj
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
             and not self.isSameObject(event.source, 
                                       self._script.lastSetupPanel):
            rolesList = [pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_FRAME]
            if self.hasMatchingHierarchy(event.source, rolesList):
                return self.isWizard(event.source)

        return False

    def unrelatedLabels(self, root):
        """Returns a list containing all the unrelated (i.e., have no
        relations to anything and are not a fundamental element of a
        more atomic component like a combo box) labels under the given
        root.  Note that the labels must also be showing on the display.

        Arguments:
        - root the Accessible object to traverse

        Returns a list of unrelated labels under the given root.
        """

        labels = script_utilities.Utilities.unrelatedLabels(self, root)
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
                            self.stringToKeysAndDict(attr[0])
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

    #########################################################################
    #                                                                       #
    # Utilities for working with the accessible text interface              #
    #                                                                       #
    #########################################################################

    def allSelectedText(self, obj):
        """Get all the text applicable text selections for the given object.
        If there is selected text, look to see if there are any previous
        or next text objects that also have selected text and add in their
        text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        if not obj or not obj.parent:
            return ["", 0, 0]

        textContents = ""
        startOffset = 0
        endOffset = 0
        if obj.queryText().getNSelections() > 0:
            [textContents, startOffset, endOffset] = self.selectedText(obj)

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
                    displayedText = self.substring(prevObj, 0, -1)
                    if len(displayedText) == 0:
                        current -= 1
                        morePossibleSelections = True
                    elif prevObj.queryText().getNSelections() > 0:
                        [newTextContents, start, end] = \
                            self.selectedText(prevObj)
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
                    displayedText = self.substring(nextObj, 0, -1)
                    if len(displayedText) == 0:
                        current += 1
                        morePossibleSelections = True
                    elif nextObj.queryText().getNSelections() > 0:
                        [newTextContents, start, end] = \
                            self.selectedText(nextObj)
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
            displayedText = self.substring(obj, 0, -1)
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

    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################

    def misspelledWordAndBody(self, suggestionsList, messagePanel):
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
        text = self.displayedLabel(suggestionsList) or ""
        words = text.split()
        for word in words:
            if word[0] in ["'", '"']:
                misspelledWord = word[1:len(word) - 1]
                break

        if messagePanel != None:
            allTextObjects = self.descendantsWithRole(
                messagePanel, pyatspi.ROLE_TEXT)
            for obj in allTextObjects:
                for word in self.substring(obj, 0, -1).split():
                    messageBody.append(word)

        return [misspelledWord, messageBody]

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

    def timeForCalRow(self, row, noIncs):
        """Return a string equivalent to the time of the given row in
        the calendar day view. Each calendar row is equivalent to a
        certain time interval (from 5 minutes upto 1 hour), with time
        (row 0) starting at 12 am (midnight).

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
