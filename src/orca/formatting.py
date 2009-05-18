# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Manages the formatting settings for Orca."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

# pylint: disable-msg=C0301

formatting = {
    'speech': {
        'prefix': {
            'focused': '[]',
            'unfocused': 'newAncestors + newRowHeader + newColumnHeader + newRadioButtonGroup'
            },
        'suffix': {
            'focused': '[]',
            'unfocused': 'newNodeLevel + unselectedCell + tutorial'
            },
        'default': {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability'
            },
        pyatspi.ROLE_ALERT: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        pyatspi.ROLE_ANIMATION: {
            'unfocused': 'labelAndName'
            },
        pyatspi.ROLE_CHECK_BOX: {
            'focused': 'checkedState',
            'unfocused': 'labelAndName + roleName + checkedState + required + availability'
            },
        pyatspi.ROLE_CHECK_MENU_ITEM: {
            'focused': 'checkedState',
            'unfocused': 'labelAndName + roleName + checkedState + required + availability + accelerator'
            },
        pyatspi.ROLE_COMBO_BOX: {
            'focused': 'name',
            },
        pyatspi.ROLE_DIALOG: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        pyatspi.ROLE_FRAME: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + unfocusedDialogCount + availability'
            },
        pyatspi.ROLE_ICON: {
            'focused': 'labelAndName + imageDescription + roleName',
            'unfocused': 'labelAndName + imageDescription + roleName'
            },
        pyatspi.ROLE_LAYERED_PANE: {
            'focused': 'labelAndName + allTextSelection + roleName + availability + noShowingChildren',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + noShowingChildren'
            },
        pyatspi.ROLE_LIST_ITEM: {
            'focused': 'expandableState + availability',
            'unfocused': 'labelAndName + allTextSelection + expandableState + availability'
            },
        pyatspi.ROLE_MENU: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability'
            },
        pyatspi.ROLE_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelAndName + menuItemCheckedState + availability + accelerator'
            },
        pyatspi.ROLE_PASSWORD_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection'
            },
        pyatspi.ROLE_PROGRESS_BAR: {
            'focused': 'percentage',
            'unfocused': 'labelAndName + percentage'
            },
        pyatspi.ROLE_PUSH_BUTTON: {
            'unfocused': 'labelAndName + roleName'
            },
        pyatspi.ROLE_RADIO_BUTTON: {
            'focused': 'radioState',
            'unfocused': 'labelAndName + radioState + roleName + availability'
            },
        pyatspi.ROLE_RADIO_MENU_ITEM: {
            # OpenOffice check menu items currently have a role of "menu item"
            # rather then "check menu item", so we need to test if one of the
            # states is CHECKED. If it is, then add that in to the list of
            # speech utterances. Note that we can't tell if this is a "check
            # menu item" that is currently unchecked and speak that state.
            # See Orca bug #433398 for more details.
            #
            'focused': 'labelAndName + radioState + roleName + availability',
            'unfocused': 'labelAndName + radioState + roleName + availability + accelerator'
            },
        pyatspi.ROLE_SLIDER: {
            # Ignore the text on the slider.  See bug 340559
            # (http://bugzilla.gnome.org/show_bug.cgi?id=340559): the
            # implementors of the slider support decided to put in a
            # Unicode left-to-right character as part of the text,
            # even though that is not painted on the screen.
            #
            # In Java, however, there are sliders without a label. In
            # this case, we'll add to presentation the slider name if
            # it exists and we haven't found anything yet.
            #
            'focused': 'value',
            'unfocused': 'labelAndName + roleName + value + required + availability'
            },
        pyatspi.ROLE_SPIN_BUTTON: {
            'focused': 'name',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + required'
            },
        pyatspi.ROLE_SPLIT_PANE: {
            'focused': 'value',
            'unfocused': 'labelAndName + roleName + value + availability'
            },
        pyatspi.ROLE_TABLE: {
            'focused': 'labelAndName + allTextSelection + roleName + availability + noChildren',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + noChildren'
            },
        pyatspi.ROLE_TABLE_CELL: {
            'focused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (realActiveDescendantDisplayedText or imageDescription) + (expandableState and (expandableState + numberOfChildren)) + required',
            'unfocused': 'tableCellRow'
            },
        'REAL_ROLE_TABLE_CELL': {
            # the real cell information
            # note that pyatspi.ROLE_TABLE_CELL is used to work out if we need to
            # read a whole row. It calls REAL_ROLE_TABLE_CELL internally.
            # maybe it can be done in a cleaner way?
            #
            'focused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + (expandableState and (expandableState + numberOfChildren)) + required',
            'unfocused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + (expandableState and (expandableState + numberOfChildren)) + required'
            },
        pyatspi.ROLE_TEAROFF_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability'
            },
        pyatspi.ROLE_TERMINAL: {
            'focused': 'terminal',
            'unfocused': 'terminal'
            },
        pyatspi.ROLE_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection'
            },
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'focused': 'toggleState',
            'unfocused': 'labelAndName + roleName + toggleState + availability'
            },
        pyatspi.ROLE_PARAGRAPH: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection'
            },
        pyatspi.ROLE_EMBEDDED: {
            'focused': 'embedded',
            'unfocused': 'embedded'
            },
    }
}

class Formatting(dict):

    def __init__(self, script):
        dict.__init__(self)
        self._script = script
        self.update(formatting)

    def update(self, newDict):
        for key, val in newDict.iteritems():
            if self.has_key(key):
                if isinstance(self[key], dict) and isinstance(val, dict):
                    self[key].update(val)
                elif isinstance(self[key], basestring) and isinstance(val, basestring):
                    self[key] = val
                else:
                    # exception or such like, we are trying to murge
                    # incompatible trees.
                    # throw an exception?
                    print("an error has occured, cant murge dicts.")
            else:
                self[key] = val

    def getPrefix(self, dictType, **args):
        already_focused = args.get('already_focused', False)
        if already_focused:
            focusType = 'focused'
        else:
            focusType = 'unfocused'
        try:
            prefix = self[dictType]['prefix'][focusType]
        except:
            prefix = self[dictType]['prefix']['unfocused']
        return prefix

    def getSuffix(self, dictType, **args):
        already_focused = args.get('already_focused', False)
        if already_focused:
            focusType = 'focused'
        else:
            focusType = 'unfocused'
        try:
            suffix = self[dictType]['suffix'][focusType]
        except:
            suffix = self[dictType]['suffix']['unfocused']
        return suffix

    def getFormat(self, dictType, **args):
        already_focused = args.get('already_focused', False)
        if already_focused:
            focusType = 'focused'
        else:
            focusType = 'unfocused'

        role = args.get('role', None)
        try:
            roleDict = self[dictType][role]
        except:
            roleDict = self[dictType]['default']

        try:
            format = roleDict[focusType]
        except:
            try:
                format = roleDict['unfocused']
            except:
                format = self[dictType]['default'][focusType]

        return format
