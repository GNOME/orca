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
        try:
            action = obj.queryAction()
        except NotImplementedError:
            action = None

        if action:
            for i in range(0, action.nActions):
                # Translators: this is the action name for
                # the 'toggle' action. It must be the same
                # string used in the *.po file for gail.
                #
                if action.getName(i) in ["toggle", _("toggle")]:
                    if not obj.getState().contains(pyatspi.STATE_CHECKED):
                        notChecked = True
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
        if obj.queryText().getNSelections() > 0:
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
                                         self._getTextSelection(prevObj)
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
                                         self._getTextSelection(nextObj)
                            textContents += " " + newTextContents
                            current += 1
                            morePossibleSelections = True
                    except:
                        pass

        return [textContents, startOffset, endOffset]
