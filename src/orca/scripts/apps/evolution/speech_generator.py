# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.speech_generator as speech_generator

from orca.orca_i18n import _ # for gettext support

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Overrides _generateSpeechForTableCell so that, if this is an
       expanded table cell, we can strip off the "0 items".
    """

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateRealTableCell(self, obj, **args):
        # Check that we are in a table cell in the mail message header list.
        # If we are and this table cell has an expanded state, then
        # dont speak the number of items.
        # See bug #432308 for more details.
        #
        rolesList = [pyatspi.ROLE_TABLE_CELL, \
                     pyatspi.ROLE_TREE_TABLE, \
                     pyatspi.ROLE_UNKNOWN]
        if self._script.isDesiredFocusedItem(obj, rolesList):
            state = obj.getState()
            if state and state.contains(pyatspi.STATE_EXPANDABLE):
                if state.contains(pyatspi.STATE_EXPANDED):
                    oldRole = self._overrideRole(
                        'ALTERNATIVE_REAL_ROLE_TABLE_CELL', args)
                    result = self.generateSpeech(obj, **args)
                    self._restoreRole(oldRole, args)
                    return result
        return speech_generator.SpeechGenerator._generateRealTableCell(
            self, obj, **args)

    def _generateTableCellRow(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to complexity in
        the code.  This method is used to return an array of strings
        (and possibly voice and audio specifications) for an entire row
        in a table if that's what the user has requested and if the row
        has changed.  Otherwise, it will return an array for just the
        current cell.
        """
        # The only time we want to override things is if we're doing
        # a detailed whereAmI. In that case, we want to minimize the
        # chattiness associated with presenting the full row of the
        # message list.
        #
        if args.get('formatType', 'unfocused') != 'detailedWhereAmI':
            return speech_generator.SpeechGenerator.\
                _generateTableCellRow(self, obj, **args)

        # [[[TODO - JD: Maybe we can do something clever with a
        # formatting string to address the headers associated with
        # toggle columns. That's really the difference here.]]]
        #
        result = []
        try:
            parentTable = obj.parent.queryTable()
        except NotImplementedError:
            parentTable = None
        if parentTable and parentTable.nColumns > 1 \
           and not self._script.isLayoutOnly(obj.parent):
            for i in range(0, parentTable.nColumns):
                index = self._script.getCellIndex(obj)
                row = parentTable.getRowAtIndex(index)
                cell = parentTable.getAccessibleAt(row, i)
                if not cell:
                    continue
                state = cell.getState()
                if state.contains(pyatspi.STATE_SHOWING):
                    # Don't speak check box cells that area not checked.
                    #
                    notChecked = False
                    try:
                        action = cell.queryAction()
                    except NotImplementedError:
                        action = None
                    if action:
                        for i in range(0, action.nActions):
                            # Translators: this is the action name for
                            # the 'toggle' action. It must be the same
                            # string used in the *.po file for gail.
                            #
                            if action.getName(i) in ["toggle", _("toggle")]:
                                if not state.contains(pyatspi.STATE_CHECKED):
                                    notChecked = True
                                break
                    if notChecked:
                        continue

                    descendant = self._script.getRealActiveDescendant(cell)
                    text = self._script.getDisplayedText(descendant)
                    if text == "Status":
                        # Translators: this in reference to an e-mail message
                        # status of having been read or unread.
                        #
                        text = _("Read")
                    result.append(text)

        return result

    def _generateUnrelatedLabels(self, obj, **args):
        """Returns, as an array of strings (and possibly voice
        specifications), all the labels which are underneath the obj's
        hierarchy and which are not in a label for or labelled by
        relation.
        """

        if not self._script.isWizard(obj):
            return speech_generator.SpeechGenerator.\
                _generateUnrelatedLabels(self, obj, **args)

        result = []
        labels = self._script.findUnrelatedLabels(obj)
        for label in labels:
            name = self._generateName(label, **args)
            try:
                text = label.queryText()
            except:
                pass
            else:
                attr = text.getAttributes(0)
                if attr[0]:
                    [charKeys, charDict] = \
                        self._script.textAttrsToDictionary(attr[0])
                    if charDict.get('weight', '400') == '800':
                        # It's a new "screen" in the Setup Assistant.
                        #
                        name = self._script.getDisplayedText(label)
                        # Translators: this is the name of a setup
                        # assistant window/screen in Evolution.
                        #
                        name = [_("%s screen") % name]
            result.extend(name)
        return result
