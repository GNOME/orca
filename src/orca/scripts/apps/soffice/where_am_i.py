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

"""Custom script for StarOffice and OpenOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.speech as speech
import orca.where_am_I as where_am_I

from orca.orca_i18n import _ # for gettext support
from orca.orca_i18n import C_     # to provide qualified translatable strings

class WhereAmI(where_am_I.WhereAmI):

    def __init__(self, script):
        """Create a new WhereAmI that will be used to speak information
        about the current object of interest.
        """

        where_am_I.WhereAmI.__init__(self, script)

    def _speakTableCell(self, obj, basicOnly):
        """Given the nature of OpenOffice Calc, Orca should override the
        default whereAmI behavior when the item with focus is a cell
        within Calc. In this instance, the following information should
        be spoken/displayed:

        1. "Cell"
        2. the cell coordinates
        3. the cell contents:
            A. if the cell is empty, "blank"
            B. if the cell is being edited AND if some text within the cell
            is selected, the selected text followed by "selected"
            C. otherwise, the full contents of the cell
        """

        if not self._script.isSpreadSheetCell(obj):
            return where_am_I.WhereAmI._speakTableCell(self, obj, basicOnly)

        utterances = []
        utterances.append(_("cell"))

        table = obj.parent.queryTable()

        # Translators: this represents the column we're
        # on in a table.
        #
        index = self._script.getCellIndex(obj)
        text = _("column %d") % (table.getColumnAtIndex(index) + 1)
        utterances.append(text)

        # Speak the dynamic column header (if any).
        #
        if table in self._script.dynamicColumnHeaders:
            row = self._script.dynamicColumnHeaders[table]
            header = self._script.getDynamicRowHeaderCell(obj, row)
            try:
                headerText = header.queryText()
            except:
                headerText = None

            if header.childCount > 0:
                for child in header:
                    text = self._script.getText(child, 0, -1)
                    if text:
                        utterances.append(text)
            elif headerText:
                text = self._script.getText(header, 0, -1)
                if text:
                    utterances.append(text)

        # Translators: this represents the row number of a table.
        #
        index = self._script.getCellIndex(obj)
        text = _("row %d") % (table.getRowAtIndex(index) + 1)
        utterances.append(text)

        # Speak the dynamic row header (if any).
        #
        if table in self._script.dynamicRowHeaders:
            column = self._script.dynamicRowHeaders[table]
            header = self._script.getDynamicColumnHeaderCell(obj, column)
            try:
                headerText = header.queryText()
            except:
                headerText = None

            if header.childCount > 0:
                for child in header:
                    text = self._script.getText(child, 0, -1)
                    if text:
                        utterances.append(text)
            elif headerText:
                text = self._script.getText(header, 0, -1)
                if text:
                    utterances.append(text)

        text = obj.queryText().getText(0, -1)
        utterances.append(text)

        debug.println(self._debugLevel, "calc table cell utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakParagraph(self, obj, basicOnly):
        """OpenOffice Calc cells have the role "paragraph" when
        they are being edited.
        """

        top = self._script.getTopLevel(obj)
        if top and top.name.endswith(" Calc"):
            self._speakCalc(obj, basicOnly)
        elif top and top.name.endswith(" Writer"):
            self._speakText(obj, basicOnly)
        else:
            where_am_I.WhereAmI._speakParagraph(self, obj, basicOnly)

    def _speakCalc(self, obj, basicOnly):
        """Speak a OpenOffice Calc cell.
        """

        utterances = []
        utterances.append(_("cell"))

        # No way to get cell coordinates?

        [textContents, startOffset, endOffset, selected] = \
            self._getTextContents(obj, basicOnly)
        text = textContents
        utterances.append(text)
        if selected:
            # Translators: when the user selects (highlights) text in
            # a document, Orca lets them know this.
            #
            text = C_("text", "selected")
            utterances.append(text)

        debug.println(self._debugLevel, "editable table cell utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _getCalcFrameAndSheet(self, obj):
        """Returns the Calc frame and sheet
        """

        mylist = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            # debug.println(self._debugLevel,
            #             "_getCalcFrameAndSheet: parent=%s, %s" % \
            #             (parent.getRole(), self._getObjLabelAndName(parent)))
            if parent.getRole() == pyatspi.ROLE_FRAME:
                mylist[0] = parent
            if parent.getRole() == pyatspi.ROLE_TABLE:
                mylist[1] = parent
            parent = parent.parent

        return mylist

    def _speakCalcStatusBar(self):
        """Speaks the OpenOffice Calc statusbar.
        """

        if not self._statusBar:
            return

        utterances = []
        for child in self._statusBar:
            text = self._getObjName(child)
            utterances.append(text)

        debug.println(self._debugLevel, "Calc statusbar utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def speakTitle(self, obj):
        """Speak the title bar.

        Calc-Specific Handling: 

        1. The contents of the title bar of the application main window
        2. The title of the current worksheet

        Note that if the application with focus is Calc, but a cell does not
        have focus, the default behavior should be used.
        """

        top = self._script.getTopLevel(obj)
        if top and not top.name.endswith(" Calc"):
            return where_am_I.WhereAmI.speakTitle(self, obj)

        utterances = []

        mylist = self._getCalcFrameAndSheet(obj)
        if mylist[0]:
            text = self.getObjLabelAndName(mylist[0])
            utterances.append(text)
        if mylist[1]:
            text = self.getObjLabelAndName(mylist[1])
            utterances.append(text)

        debug.println(self._debugLevel,
                      "Calc titlebar and sheet utterances=%s" % utterances)
        speech.speak(utterances)

    def speakStatusBar(self, obj):
        """Speak the status bar contents.

        Note that if the application with focus is Calc, but a cell does not
        have focus, the default behavior should be used.
        """

        top = self._script.getTopLevel(obj)
        if top and not top.name.endswith(" Calc"):
            return where_am_I.WhereAmI.speakStatusBar(self, obj)

        utterances = []

        mylist = self._getCalcFrameAndSheet(obj)
        if mylist[0]:
            self._statusBar = None
            self._getStatusBar(mylist[0])
            if self._statusBar:
                self._speakCalcStatusBar()

        debug.println(self._debugLevel,
                      "Calc status bar utterances=%s" % utterances)
        speech.speak(utterances)

    def _getObjLabel(self, obj):
        """Returns the label to speak for an object.
        """

        label = self._script.getDisplayedLabel(obj) or ""
        if not label and obj.getRole() == pyatspi.ROLE_PARAGRAPH \
           and self._script.getAncestor(obj,
                                        [pyatspi.ROLE_DIALOG],
                                        [pyatspi.ROLE_APPLICATION]):
            label = self._script.getDisplayedLabel(obj.parent) or ""

        return label.strip()

    def _speakObjDescription(self, obj):
        """Speaks the object's description if it is not the same as
        the object's name and displayed contents.
        """

        if not obj.description:
            return

        # The descriptions of some OOo paragraphs consists of the name and
        # the displayed text, with punctuation added. Try to spot this and,
        # if found, ignore the description.
        #
        text = self._script.getDisplayedText(obj) or ""
        desc = obj.description.replace(text, "")
        for item in obj.name.split():
            desc = desc.replace(item, "")
        for char in desc.decode("UTF-8").strip():
            if char.isalnum():
                return where_am_I.WhereAmI._speakObjDescription(self, obj)
