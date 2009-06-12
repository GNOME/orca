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

import copy

import pyatspi

# pylint: disable-msg=C0301

TUTORIAL = '(tutorial and (pause + tutorial) or [])'

formatting = {
    'speech': {
        'prefix': {
            'focused': '[]',
            'unfocused': 'newAncestors + newRowHeader + newColumnHeader + newRadioButtonGroup',
            'basicWhereAmI': 'toolbar',
            'detailedWhereAmI' : '[]'
            },
        'suffix': {
            'focused': '[]',
            'unfocused': 'newNodeLevel + unselectedCell + ' + TUTORIAL,
            'basicWhereAmI': TUTORIAL + ' + description',
            'detailedWhereAmI' : '[]'
            },
        'default': {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + mnemonic + accelerator',
            'basicWhereAmI': 'labelAndName + roleName',
            'detailedWhereAmI' : '[]'
            },
        pyatspi.ROLE_ALERT: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        pyatspi.ROLE_ANIMATION: {
            'unfocused': 'labelAndName'
            },
        pyatspi.ROLE_CHECK_BOX: {
            'focused': 'checkedState',
            'unfocused': 'labelAndName + roleName + checkedState + required + availability + mnemonic + accelerator',
            'basicWhereAmI': 'labelAndName + roleName + checkedState + mnemonic + accelerator + required'
            },
        pyatspi.ROLE_CHECK_MENU_ITEM: {
            'focused': 'checkedState',
            'unfocused': 'labelAndName + roleName + checkedState + required + availability + mnemonic + accelerator',
            'basicWhereAmI': 'ancestors + labelAndName + roleName + checkedState + accelerator + positionInList + mnemonic'
            },
        pyatspi.ROLE_COMBO_BOX: {
            'focused': 'name',
            'basicWhereAmI': 'label + roleName + name + positionInList + mnemonic + accelerator'
            },
        pyatspi.ROLE_DIALOG: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
            },
        pyatspi.ROLE_EMBEDDED: {
            'focused': 'embedded',
            'unfocused': 'embedded'
            },
        pyatspi.ROLE_ENTRY: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + mnemonic',
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
            },
        pyatspi.ROLE_FRAME: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + unfocusedDialogCount + availability'
            },
        pyatspi.ROLE_HEADING: {
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
            },
        pyatspi.ROLE_ICON: {
            'focused': 'labelAndName + imageDescription + roleName',
            'unfocused': 'labelAndName + imageDescription + roleName',
            'basicWhereAmI': 'parentRoleName + labelAndName + selectedItemCount',
            'detailedWhereAmI': 'parentRoleName + labelAndName + selectedItemCount + selectedItems'
            },
        pyatspi.ROLE_LABEL: {
            'basicWhereAmI': 'labelAndName + allTextSelection + roleName'
            },
        pyatspi.ROLE_LAYERED_PANE: {
            'focused': 'labelAndName + allTextSelection + roleName + availability + noShowingChildren',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + noShowingChildren',
            'basicWhereAmI': 'labelAndName + roleName + selectedItemCount',
            'detailedWhereAmI': 'labelAndName + roleName + selectedItemCount + selectedItems'
            },
        pyatspi.ROLE_LINK: {
            'unfocused': 'labelAndName + roleName + availability',
            'basicWhereAmI': 'linkInfo + siteDescription + fileSize'
            },
        pyatspi.ROLE_LIST_ITEM: {
            'focused': 'expandableState + availability',
            'unfocused': 'labelAndName + allTextSelection + expandableState + availability',
            'basicWhereAmI': 'label + roleName + name + positionInList + expandableState + (nodeLevel or nestingLevel)'
            },
        pyatspi.ROLE_MENU: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + mnemonic + accelerator',
            'basicWhereAmI': '(ancestors or parentRoleName) + labelAndName + roleName +  positionInList + mnemonic'
            },
        pyatspi.ROLE_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelAndName + menuItemCheckedState + availability + mnemonic + accelerator',
            'basicWhereAmI': 'ancestors + labelAndName + accelerator + positionInList + mnemonic'
            },
        pyatspi.ROLE_PAGE_TAB: {
            'basicWhereAmI': 'parentRoleName + labelAndName + roleName + positionInList + mnemonic + accelerator'
            },
        pyatspi.ROLE_PARAGRAPH: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + mnemonic',
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
            },
        pyatspi.ROLE_PASSWORD_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + mnemonic',
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
            },
        pyatspi.ROLE_PROGRESS_BAR: {
            'focused': 'percentage',
            'unfocused': 'labelAndName + percentage'
            },
        pyatspi.ROLE_PUSH_BUTTON: {
            'unfocused': 'labelAndName + roleName + availability + mnemonic + accelerator',
            'basicWhereAmI': 'labelAndName + roleName + mnemonic + accelerator'
            },
        pyatspi.ROLE_RADIO_BUTTON: {
            'focused': 'radioState',
            'unfocused': 'labelAndName + radioState + roleName + availability + mnemonic + accelerator',
            'basicWhereAmI': 'radioButtonGroup + labelAndName + roleName + radioState + positionInGroup + mnemonic + accelerator'
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
            'unfocused': 'labelAndName + radioState + roleName + availability + mnemonic + accelerator',
            'basicWhereAmI': 'ancestors + labelAndName + roleName + radioState + accelerator + positionInList + mnemonic'
            },
        pyatspi.ROLE_SECTION: {
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
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
            'unfocused': 'label + roleName + value + required + availability + mnemonic',
            'basicWhereAmI': 'label + roleName + value + percentage + mnemonic + accelerator + required'
            },
        pyatspi.ROLE_SPIN_BUTTON: {
            'focused': 'name',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + mnemonic + required',
            'basicWhereAmI': 'label + roleName + name + allTextSelection + mnemonic + accelerator + required'
            },
        pyatspi.ROLE_SPLIT_PANE: {
            'focused': 'value',
            'unfocused': 'labelAndName + roleName + value + availability + mnemonic',
            'basicWhereAmI' : 'labelAndName + roleName + value'
            },
        pyatspi.ROLE_TABLE: {
            'focused': 'labelAndName + allTextSelection + roleName + availability + noChildren',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + noChildren',
            'basicWhereAmI': 'labelAndName + allTextSelection + roleName + availability + noChildren'
            },
        pyatspi.ROLE_TABLE_CELL: {
            'focused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (expandableState and (expandableState + numberOfChildren))',
            'unfocused': 'tableCellRow',
            'basicWhereAmI': 'parentRoleName + columnHeader + rowHeader + roleName + cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + columnAndRow + expandableState + nodeLevel',
            'detailedWhereAmI': 'parentRoleName + columnHeader + rowHeader + roleName + cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + columnAndRow + tableCellRow + expandableState + nodeLevel'
            },
        'REAL_ROLE_TABLE_CELL': {
            # the real cell information
            # note that pyatspi.ROLE_TABLE_CELL is used to work out if we need to
            # read a whole row. It calls REAL_ROLE_TABLE_CELL internally.
            # maybe it can be done in a cleaner way?
            #
            'focused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (expandableState and (expandableState + numberOfChildren))',
            'unfocused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + (expandableState and (expandableState + numberOfChildren)) + required'
            },
        pyatspi.ROLE_TEAROFF_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability '
            },
        pyatspi.ROLE_TERMINAL: {
            'focused': 'terminal',
            'unfocused': 'terminal',
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
            },
        pyatspi.ROLE_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + mnemonic',
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + mnemonic',
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + mnemonic + ' + TUTORIAL
            },
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'focused': 'toggleState',
            'unfocused': 'labelAndName + roleName + toggleState + availability + mnemonic + accelerator',
            'basicWhereAmI': 'labelAndName + roleName + toggleState'
            },
        pyatspi.ROLE_TOOL_TIP: {
            'unfocused': 'labelAndName',
            'basicWhereAmI': 'labelAndName'
            },
    }
}

class Formatting(dict):

    def __init__(self, script):
        dict.__init__(self)
        self._script = script
        self.update(copy.deepcopy(formatting))

    def update(self, newDict):
        for key, val in newDict.iteritems():
            if self.has_key(key):
                if isinstance(self[key], dict) and isinstance(val, dict):
                    self[key].update(val)
                elif isinstance(self[key], basestring) \
                     and isinstance(val, basestring):
                    self[key] = val
                else:
                    # exception or such like, we are trying to murge
                    # incompatible trees.
                    # throw an exception?
                    print("an error has occured, cant murge dicts.")
            else:
                self[key] = val

    def getPrefix(self, **args):
        """Get a formatting string to add on to the end of
        formatting strings obtained by getFormat.

        Arguments expected in args:
        - mode: output mode, such as 'speech', 'braille'.
        - formatType: the type of formatting, such as
          'focused', 'basicWhereAmI', etc.
        """
        prefix = self[args['mode']]['prefix'][args['formatType']]
        return prefix

    def getSuffix(self, **args):
        """Get a formatting string to add on to the end of
        formatting strings obtained by getFormat.

        Arguments expected in args:
        - mode: output mode, such as 'speech', 'braille'.
        - role: the role, such as pyatspi.ROLE_TEXT
        - formatType: the type of formatting, such as
          'focused', 'basicWhereAmI', etc.
        """
        suffix = self[args['mode']]['suffix'][args['formatType']]
        return suffix

    def getFormat(self, **args):
        """Get a formatting string for the given mode and
        formatType.

        Arguments expected in args:
        - mode: output mode, such as 'speech', 'braille'.
        - role: the role, such as pyatspi.ROLE_TEXT
        - formatType: the type of formatting, such as
          'focused', 'basicWhereAmI', etc.
        """
        try:
            # First try to find the exact match.
            #
            format = self[args['mode']][args['role']][args['formatType']]
        except:
            try:
                # Failing that, fallback to the 'unfocused' formatType
                # for the mode and role, if it exists.
                #
                format = self[args['mode']][args['role']]['unfocused']
            except:
                try:
                    # Failing that, fallback to the default for the
                    # formatType
                    #
                    format = self[args['mode']]['default'][args['formatType']]
                except:
                    # Failing that, just used the default 'unfocused' format
                    #
                    format = self[args['mode']]['default']['unfocused']
        return format
