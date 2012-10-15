# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Manages the formatting settings for Orca."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import copy

import pyatspi

from . import settings

# pylint: disable-msg=C0301

TUTORIAL = '(tutorial and (pause + tutorial) or [])'
MNEMONIC = '(mnemonic and (pause + mnemonic + lineBreak) or [])'

BRAILLE_TEXT = '[Text(obj, asString(label + placeholderText), asString(eol))]\
                + (required and [Region(" " + asString(required))])\
                + (readOnly and [Region(" " + asString(readOnly))])'

formatting = {

    ####################################################################
    #                                                                  #
    # Strings Orca includes on its own (versus getting them from the   #
    # application.                                                     #
    #                                                                  #
    ####################################################################

    'strings' : {
        'speech': {
            'required': settings.speechRequiredStateString,
            'readonly': settings.speechReadOnlyString,
            'insensitive': settings.speechInsensitiveString,
            'checkbox': settings.speechCheckboxIndicators,
            'radiobutton': settings.speechRadioButtonIndicators,
            'togglebutton': settings.speechToggleButtonIndicators,
            'expansion': settings.speechExpansionIndicators,
            'nodelevel': settings.speechNodeLevelString,
            'nestinglevel': settings.speechNestingLevelString,
            'multiselect': settings.speechMultiSelectString,
            'iconindex': settings.speechIconIndexString,
            'groupindex': settings.speechGroupIndexString,
        },
        'braille': {
            'eol': settings.brailleEOLIndicator,
            'required': settings.brailleRequiredStateString,
            'readonly': settings.brailleReadOnlyString,
            'insensitive': settings.brailleInsensitiveString,
            'checkbox': settings.brailleCheckBoxIndicators,
            'radiobutton': settings.brailleRadioButtonIndicators,
            'togglebutton': settings.brailleToggleButtonIndicators,
            'expansion': settings.brailleExpansionIndicators,
            'nodelevel': settings.brailleNodeLevelString,
            'nestinglevel': settings.brailleNestingLevelString,
        },
    },

    ####################################################################
    #                                                                  #
    # Formatting for speech.                                           #
    #                                                                  #
    ####################################################################

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
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelAndName + roleName',
            'detailedWhereAmI' : '[]'
            },
        pyatspi.ROLE_ALERT: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        pyatspi.ROLE_ANIMATION: {
            'unfocused': 'labelAndName'
            },
        pyatspi.ROLE_CANVAS: {
            'focused': 'labelAndName + imageDescription + roleName + positionInList',
            'unfocused': 'labelAndName + imageDescription + roleName + positionInList',
            'basicWhereAmI': 'parentRoleName + labelAndName + selectedItemCount',
            'detailedWhereAmI': 'parentRoleName + labelAndName + selectedItemCount + selectedItems'
            },
        pyatspi.ROLE_CHECK_BOX: {
            'focused': 'checkedState',
            'unfocused': 'labelAndName + roleName + checkedState + required + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'namedContainingPanel + labelAndName + roleName + checkedState + ' + MNEMONIC + ' + accelerator + required'
            },
        pyatspi.ROLE_CHECK_MENU_ITEM: {
            'focused': 'checkedState',
            'unfocused': 'labelAndName + roleName + checkedState + required + availability + ' + MNEMONIC + ' + accelerator + positionInList',
            'basicWhereAmI': 'ancestors + labelAndName + roleName + checkedState + accelerator + positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_COLOR_CHOOSER: {
            'focused': 'value',
            'unfocused': 'label + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'label + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        pyatspi.ROLE_COMBO_BOX: {
            'focused': 'name + positionInList',
            'unfocused': 'label + name + roleName + positionInList + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'label + roleName + name + positionInList + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_DIALOG: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_EMBEDDED: {
            'focused': 'embedded',
            'unfocused': 'embedded'
            },
        pyatspi.ROLE_ENTRY: {
            'focused': 'labelOrName + placeholderText + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + placeholderText + readOnly + textRole + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + placeholderText + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + placeholderText + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_FRAME: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + unfocusedDialogCount + availability'
            },
        pyatspi.ROLE_HEADING: {
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_ICON: {
            'focused': 'labelAndName + imageDescription + roleName + positionInList',
            'unfocused': 'labelAndName + imageDescription + roleName + positionInList',
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
            'unfocused': 'labelAndName + roleName + availability + ' + MNEMONIC,
            'basicWhereAmI': 'linkInfo + siteDescription + fileSize + ' + MNEMONIC
            },
        pyatspi.ROLE_LIST: {
            'focused': 'focusedItem',
            'unfocused': 'labelOrName + focusedItem + multiselectableState + numberOfChildren'
            },
        pyatspi.ROLE_LIST_ITEM: {
            'focused': 'expandableState + availability',
            'unfocused': 'labelAndName + allTextSelection + expandableState + availability + positionInList',
            'basicWhereAmI': 'label + roleName + name + positionInList + expandableState + (nodeLevel or nestingLevel)'
            },
        pyatspi.ROLE_MENU: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + ' + MNEMONIC + ' + accelerator + positionInList',
            'basicWhereAmI': '(ancestors or parentRoleName) + labelAndName + roleName +  positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelAndName + menuItemCheckedState + availability + ' + MNEMONIC + ' + accelerator + positionInList',
            'basicWhereAmI': 'ancestors + labelAndName + accelerator + positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_NOTIFICATION: {
            'unfocused': 'roleName + unrelatedLabels'
            },
        pyatspi.ROLE_PAGE_TAB: {
            'focused': 'labelAndName + roleName + positionInList + ' + MNEMONIC + ' + accelerator',
            'unfocused': 'labelAndName + roleName + positionInList + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'parentRoleName + labelAndName + roleName + positionInList + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_PARAGRAPH: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_PASSWORD_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_PROGRESS_BAR: {
            'focused': 'percentage',
            'unfocused': 'labelAndName + percentage'
            },
        pyatspi.ROLE_PUSH_BUTTON: {
            'unfocused': 'labelAndName + expandableState + roleName + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelAndName + expandableState + roleName + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_RADIO_BUTTON: {
            'focused': 'radioState',
            'unfocused': 'labelAndName + radioState + roleName + availability + ' + MNEMONIC + ' + accelerator + positionInList',
            'basicWhereAmI': 'radioButtonGroup + labelAndName + roleName + radioState + positionInGroup + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_RADIO_MENU_ITEM: {
            # OpenOffice check menu items currently have a role of "menu item"
            # rather then "check menu item", so we need to test if one of the
            # states is CHECKED. If it is, then add that in to the list of
            # speech utterances. Note that we can't tell if this is a "check
            # menu item" that is currently unchecked and speak that state.
            # See Orca bug #433398 for more details.
            #
            'focused': 'labelAndName + radioState + roleName + availability + positionInList',
            'unfocused': 'labelAndName + radioState + roleName + availability + ' + MNEMONIC + ' + accelerator + positionInList',
            'basicWhereAmI': 'ancestors + labelAndName + roleName + radioState + accelerator + positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_SECTION: {
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_SLIDER: {
            'focused': 'value',
            'unfocused': 'labelOrName + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        pyatspi.ROLE_SPIN_BUTTON: {
            'focused': 'name',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + ' + MNEMONIC + ' + required',
            'basicWhereAmI': 'label + roleName + name + allTextSelection + ' + MNEMONIC + ' + accelerator + required'
            },
        pyatspi.ROLE_SPLIT_PANE: {
            'focused': 'value',
            'unfocused': 'labelAndName + roleName + value + availability + ' + MNEMONIC,
            'basicWhereAmI' : 'labelAndName + roleName + value'
            },
        pyatspi.ROLE_TABLE: {
            'focused': 'labelAndName + allTextSelection + roleName + availability + noChildren',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + noChildren',
            'basicWhereAmI': 'labelAndName + allTextSelection + roleName + availability + noChildren'
            },
        pyatspi.ROLE_TABLE_CELL: {
            'focused': '(tableCell2ChildLabel + tableCell2ChildToggle)\
                        or (cellCheckedState + (expandableState and (expandableState + numberOfChildren)))',
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
            'focused':   '(tableCell2ChildLabel + tableCell2ChildToggle)\
                          or (cellCheckedState + (expandableState and (expandableState + numberOfChildren)))',
            'unfocused': '(tableCell2ChildLabel + tableCell2ChildToggle)\
                          or (columnHeaderIfToggleAndNoText\
                              + cellCheckedState\
                              + (realActiveDescendantDisplayedText or imageDescription + image)\
                              + (expandableState and (expandableState + numberOfChildren))\
                              + required)'
            },
        pyatspi.ROLE_TEAROFF_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability '
            },
        pyatspi.ROLE_TERMINAL: {
            'focused': 'terminal',
            'unfocused': 'terminal',
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_TEXT: {
            'focused': 'labelOrName + placeholderText + readOnly + textRole + textIndentation + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + placeholderText + readOnly + textRole + textIndentation + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + placeholderText + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + placeholderText + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
            },
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'focused': 'expandableState or toggleState',
            'unfocused': 'labelAndName + roleName + (expandableState or toggleState) + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelAndName + roleName + (expandableState or toggleState)'
            },
        pyatspi.ROLE_TOOL_TIP: {
            'unfocused': 'labelAndName',
            'basicWhereAmI': 'labelAndName'
            },
    },

    ####################################################################
    #                                                                  #
    # Formatting for braille.                                          #
    #                                                                  #
    ####################################################################

    'braille': {
        'prefix': {
#            'focused':   'ancestors\
#                         + (rowHeader and [Region(" " + asString(rowHeader))])\
#                         + (columnHeader and [Region(" " + asString(columnHeader))])\
#                         + (radioButtonGroup and [Region(" " + asString(radioButtonGroup))])\
#                         + [Region(" ")]',
#            'unfocused': 'ancestors\
#                         + (rowHeader and [Region(" " + asString(rowHeader))])\
#                         + (columnHeader and [Region(" " + asString(columnHeader))])\
#                         + (radioButtonGroup and [Region(" " + asString(radioButtonGroup))])\
#                         + [Region(" ")]',
            'focused':   '(includeContext\
                           and (ancestors\
                                + (rowHeader and [Region(" " + asString(rowHeader))])\
                                + (columnHeader and [Region(" " + asString(columnHeader))])\
                                + (radioButtonGroup and [Region(" " + asString(radioButtonGroup))])\
                                + [Region(" ")])\
                           or [])',
            'unfocused': '(includeContext\
                           and (ancestors\
                                + (rowHeader and [Region(" " + asString(rowHeader))])\
                                + (columnHeader and [Region(" " + asString(columnHeader))])\
                                + (radioButtonGroup and [Region(" " + asString(radioButtonGroup))])\
                                + [Region(" ")])\
                           or [])',
            },
        'suffix': {
            'focused':   '(nodeLevel and [Region(" " + asString(nodeLevel))])',
            'unfocused': '(nodeLevel and [Region(" " + asString(nodeLevel))])',
            },
        'default': {
            'focused':   '[Component(obj,\
                                     asString(label + displayedText + value + roleName + required))]',
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + value + roleName + required))]',
            },
        #pyatspi.ROLE_ALERT: 'default'
        pyatspi.ROLE_ANIMATION: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName + (description and space(": ") + description)))]',
            },
        #pyatspi.ROLE_ARROW: 'default'
        pyatspi.ROLE_CANVAS: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText + imageDescription) or name) + roleName))]'
            },
        pyatspi.ROLE_CHECK_BOX: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName),\
                                     indicator=asString(checkedState))]'
            },
        pyatspi.ROLE_CHECK_MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName + availability) + asString(accelerator),\
                                     indicator=asString(checkedState))]'
            },
        #pyatspi.ROLE_COLUMN_HEADER: 'default'
        pyatspi.ROLE_COMBO_BOX: {
            # [[[TODO: WDW - maybe pass the label into the region constructor?
            # We could then use the cursorOffset field to indicate where the
            # combobox starts.]]]
            #
            'unfocused': '((comboBoxTextObj and [Text(comboBoxTextObj[0], asString(label), asString(eol))])\
                           or [Component(obj, asString(label + displayedText), label and (len(asString(label)) + 1) or 0)])\
                          + [Region(" " + asString(roleName))]'
            },
        #pyatspi.ROLE_DESKTOP_ICON: 'default'
        #pyatspi.ROLE_DIAL: 'default'
        #pyatspi.ROLE_DIALOG: 'default'
        #pyatspi.ROLE_DIRECTORY_PANE: 'default'
        pyatspi.ROLE_EMBEDDED: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText) or asString(applicationName))]'
            },
        pyatspi.ROLE_ENTRY: {
            'unfocused': BRAILLE_TEXT
            },
        pyatspi.ROLE_FRAME: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText) or name) + value + roleName + alertAndDialogCount))]'
            },
        pyatspi.ROLE_HEADING: {
            'unfocused': '[Text(obj)] + [Region(" " + asString(roleName))]'
            },
        #pyatspi.ROLE_HTML_CONTAINER: 'default'
        pyatspi.ROLE_ICON: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText + imageDescription) or name) + roleName))]'
            },
        pyatspi.ROLE_IMAGE: {
            'focused':   '[Component(obj,\
                                     asString(labelAndName + value + roleName + required))]',
            'unfocused': '[Component(obj,\
                                     asString(labelAndName + value + roleName + required))]',
            },
        pyatspi.ROLE_LABEL: {
            'unfocused': '[Text(obj,\
                                asString(label),\
                                asString(eol))]'
            },
        pyatspi.ROLE_LINK: {
            'unfocused': '[Link(obj, asString(currentLineText)\
                                     or asString(displayedText)\
                                     or asString(name))]',
        },
        pyatspi.ROLE_LIST: {
            'unfocused': '[Component(obj,\
                                     asString(label + focusedItem + roleName),\
                                     asString(label) and (len(asString(label)) + 1) or 0)]'
        },
        pyatspi.ROLE_LIST_ITEM: {
            'focused':   '[Component(obj,\
                                     asString(label + displayedText + expandableState + roleName + availability) + asString(accelerator))]\
                          + (nestingLevel and [Region(" " + asString(nestingLevel))])',
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + expandableState))]\
                          + (nestingLevel and [Region(" " + asString(nestingLevel))])',
            },
        pyatspi.ROLE_MENU: {
            'focused':   '[Component(obj,\
                                     asString(label + displayedText + roleName + availability) + asString(accelerator))]',
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName))]',
            },
        #pyatspi.ROLE_MENU_BAR: 'default'
        pyatspi.ROLE_MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + availability) + asString(accelerator),\
                                     indicator=asString(menuItemCheckedState))]'
            },
        #pyatspi.ROLE_OPTION_PANE: 'default'
        pyatspi.ROLE_PAGE_TAB: {
            'focused':   '[Component(obj,\
                                     asString(label + displayedText + roleName + availability) + asString(accelerator))]',
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName))]'
            },
        #pyatspi.ROLE_PAGE_TAB_LIST: 'default'
        pyatspi.ROLE_PANEL: {
            'unfocused': '[Component(obj,\
                                     asString((label or displayedText) + roleName))]'
            },
        pyatspi.ROLE_PARAGRAPH: {
            'unfocused': BRAILLE_TEXT
            },
        pyatspi.ROLE_PASSWORD_TEXT: {
            'unfocused': BRAILLE_TEXT
            },
        #pyatspi.ROLE_PROGRESS_BAR: 'default'
        pyatspi.ROLE_PUSH_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText) or description) + expandableState + roleName))]'
            },
        pyatspi.ROLE_RADIO_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText) or description) + roleName),\
                                     indicator=asString(radioState))]'
            },
        pyatspi.ROLE_RADIO_MENU_ITEM: {
            'focused':   '[Component(obj,\
                                     asString(((label + displayedText) or description) + roleName + availability)\
                                     + asString(accelerator),\
                                     indicator=asString(radioState))]',
            'unfocused': '[Component(obj,\
                                     asString((label + displayedText) or description)\
                                     + asString(accelerator),\
                                     indicator=asString(radioState))]'
            },
        #pyatspi.ROLE_ROW_HEADER: 'default'
        #pyatspi.ROLE_SCROLL_BAR: 'default'
        pyatspi.ROLE_SCROLL_PANE: {
            'unfocused': 'asPageTabOrScrollPane'
            },
        #'REAL_ROLE_SCROLL_PANE': 'default'
        pyatspi.ROLE_SLIDER: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + value + roleName + required))]'
            },
        pyatspi.ROLE_SPIN_BUTTON: {
            'unfocused': '[Text(obj, asString(label), asString(eol))]\
                          + (required and [Region(" " + asString(required))] or [])\
                          + (readOnly and [Region(" " + asString(readOnly))] or [])'
            },
        #pyatspi.ROLE_SPLIT_PANE: 'default'
        #pyatspi.ROLE_TABLE: 'default'
        pyatspi.ROLE_TABLE_CELL: {
            'unfocused': 'tableCellRow',
            },
        'REAL_ROLE_TABLE_CELL': {
            'unfocused': '(tableCell2ChildToggle + tableCell2ChildLabel)\
                          or (cellCheckedState\
                              + (columnHeaderIfToggleAndNoText and [Region(" "), Component(obj, asString(columnHeaderIfToggleAndNoText))])\
                              + ((realActiveDescendantDisplayedText and [Component(obj, asString(realActiveDescendantDisplayedText))])\
                                 or (imageDescription and [Region(" "), Component(obj, asString(imageDescription))]))\
                              + (realActiveDescendantRoleName and [Component(obj, (realActiveDescendantDisplayedText and " " or "") + asString(realActiveDescendantRoleName))])\
                              + (expandableState and [Region(" " + asString(expandableState))])\
                              + (required and [Region(" " + asString(required))]))\
                          or ([Component(obj,"")])'
            },
        #pyatspi.ROLE_TABLE_COLUMN_HEADER: 'default'
        #pyatspi.ROLE_TABLE_ROW_HEADER: 'default'
        pyatspi.ROLE_TEAROFF_MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(roleName))]'
            },
        pyatspi.ROLE_TERMINAL: {
            'unfocused': '[Text(obj)]'
            },
        pyatspi.ROLE_TEXT: {
            'unfocused': BRAILLE_TEXT
            },
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText) or description) + expandableState + roleName),\
                                     indicator=asString(toggleState))]'
            },
        #pyatspi.ROLE_TOOL_BAR: 'default'
        #pyatspi.ROLE_TREE: 'default'
        #pyatspi.ROLE_TREE_TABLE: 'default'
        #pyatspi.ROLE_WINDOW: 'default'
    }
}

if settings.useExperimentalSpeechProsody:
    formatting['speech'][pyatspi.ROLE_CANVAS]['focused'] = 'labelAndName + imageDescription + roleName + pause + positionInList'
    formatting['speech'][pyatspi.ROLE_CANVAS]['unfocused'] = 'labelAndName + imageDescription + roleName + pause + positionInList'
    formatting['speech'][pyatspi.ROLE_CANVAS]['basicWhereAmI'] = \
        'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause'
    formatting['speech'][pyatspi.ROLE_CANVAS]['detailedWhereAmI'] = \
        'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause + selectedItems + pause'
    formatting['speech'][pyatspi.ROLE_CHECK_MENU_ITEM]['unfocused'] = \
        'labelAndName + roleName + checkedState + required + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList'
    formatting['speech'][pyatspi.ROLE_CHECK_MENU_ITEM]['basicWhereAmI'] = \
        'ancestors + pause + labelAndName + roleName + checkedState + pause + accelerator + pause + positionInList + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_COMBO_BOX]['focused'] = 'name + pause + positionInList + pause'
    formatting['speech'][pyatspi.ROLE_COMBO_BOX]['unfocused'] = 'label + name + roleName + pause + positionInList + ' + MNEMONIC + ' + accelerator'
    formatting['speech'][pyatspi.ROLE_COMBO_BOX]['basicWhereAmI'] = \
        'label + roleName + pause + name + positionInList + ' + MNEMONIC + ' + accelerator'
    formatting['speech'][pyatspi.ROLE_HEADING]['basicWhereAmI'] = \
        'label + readOnly + textRole + pause + textContent + anyTextSelection + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_HEADING]['detailedWhereAmI'] = \
        'label + readOnly + textRole + pause +textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
    formatting['speech'][pyatspi.ROLE_ICON]['focused'] = 'labelAndName + imageDescription + roleName + pause + positionInList'
    formatting['speech'][pyatspi.ROLE_ICON]['unfocused'] = 'labelAndName + imageDescription + roleName + pause + positionInList'
    formatting['speech'][pyatspi.ROLE_ICON]['basicWhereAmI'] = \
        'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause'
    formatting['speech'][pyatspi.ROLE_ICON]['detailedWhereAmI'] = \
        'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause + selectedItems + pause'
    formatting['speech'][pyatspi.ROLE_LAYERED_PANE]['basicWhereAmI'] = \
        'labelAndName + pause+ roleName + pause + selectedItemCount + pause'
    formatting['speech'][pyatspi.ROLE_LAYERED_PANE]['detailedWhereAmI'] = \
        'labelAndName + pause + roleName + pause + selectedItemCount + pause+ selectedItems + pause'
    formatting['speech'][pyatspi.ROLE_LINK]['basicWhereAmI'] = \
        'linkInfo + pause + siteDescription + pause + fileSize + pause + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_LIST]['unfocused'] = \
        'labelOrName + pause + focusedItem + pause + multiselectableState + numberOfChildren + pause'
    formatting['speech'][pyatspi.ROLE_LIST_ITEM]['unfocused'] = \
        'labelAndName + allTextSelection + pause + expandableState + pause + availability + positionInList'
    formatting['speech'][pyatspi.ROLE_LIST_ITEM]['basicWhereAmI'] = \
        'label + roleName + pause + name + pause + positionInList + pause + expandableState + (nodeLevel or nestingLevel) + pause'
    formatting['speech'][pyatspi.ROLE_MENU]['unfocused'] = 'labelAndName + allTextSelection + roleName + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList'
    formatting['speech'][pyatspi.ROLE_MENU]['basicWhereAmI'] = \
        '(ancestors or parentRoleName) + pause + labelAndName + roleName + pause +  positionInList + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_MENU_ITEM]['unfocused'] = 'labelAndName + menuItemCheckedState + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList'
    formatting['speech'][pyatspi.ROLE_MENU_ITEM]['basicWhereAmI'] = \
        'ancestors + pause + labelAndName + pause + accelerator + pause + positionInList + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_PAGE_TAB]['focused'] = 'labelAndName + roleName + pause + positionInList + ' + MNEMONIC + ' + accelerator'
    formatting['speech'][pyatspi.ROLE_PAGE_TAB]['unfocused'] = 'labelAndName + roleName + pause + positionInList + ' + MNEMONIC + ' + accelerator'
    formatting['speech'][pyatspi.ROLE_PAGE_TAB]['basicWhereAmI'] = \
        'parentRoleName + pause + labelAndName + roleName + pause + positionInList + ' + MNEMONIC + ' + accelerator'
    formatting['speech'][pyatspi.ROLE_RADIO_BUTTON]['unfocused'] = \
        'labelAndName + pause + radioState + roleName + availability + lineBreak + ' + MNEMONIC + ' + accelerator + pause + positionInList + pause'
    formatting['speech'][pyatspi.ROLE_RADIO_BUTTON]['basicWhereAmI'] = \
        'radioButtonGroup + pause + labelAndName + roleName + pause + radioState + pause + positionInGroup + ' + MNEMONIC + ' + accelerator'
    formatting['speech'][pyatspi.ROLE_TABLE]['focused'] = \
        'labelAndName + pause + allTextSelection + roleName + availability + noChildren'
    formatting['speech'][pyatspi.ROLE_TABLE]['unfocused'] = \
        'labelAndName + pause + allTextSelection + roleName + availability + noChildren'
    formatting['speech'][pyatspi.ROLE_TABLE]['basicWhereAmI'] = \
        'labelAndName + pause + allTextSelection + roleName + availability + noChildren'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['focused'] = \
        '((tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState) + pause + (expandableState and (expandableState + pause + numberOfChildren + pause))'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['unfocused'] = \
        'tableCellRow + pause'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['basicWhereAmI'] = \
        'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + expandableState + pause + nodeLevel + pause'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['detailedWhereAmI'] = \
        'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + tableCellRow + pause + expandableState + pause + nodeLevel + pause'
    formatting['speech'][pyatspi.ROLE_TERMINAL]['basicWhereAmI'] = \
        'label + readOnly + pause + textRole + pause + textContent + anyTextSelection + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_TERMINAL]['detailedWhereAmI'] = \
        'label + readOnly + pause + textRole + pause + textContentWithAttributes + anyTextSelection + ' + MNEMONIC + ' + ' + TUTORIAL
    formatting['speech'][pyatspi.ROLE_TEXT]['focused'] = \
        'labelOrName + placeholderText + readOnly + textRole + pause + textIndentation + currentLineText + allTextSelection'
    formatting['speech'][pyatspi.ROLE_TEXT]['unfocused'] = \
        'labelOrName + placeholderText + readOnly + textRole + pause + textIndentation + currentLineText + allTextSelection + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_TEXT]['basicWhereAmI'] = \
        'label + placeholderText + readOnly + textRole + pause + textContent + anyTextSelection + pause + ' + MNEMONIC
    formatting['speech'][pyatspi.ROLE_TEXT]['detailedWhereAmI'] = \
        'label + placeholderText + readOnly + textRole + pause + textContentWithAttributes + anyTextSelection + pause + ' + MNEMONIC + ' + ' + TUTORIAL

class Formatting(dict):

    def __init__(self, script):
        dict.__init__(self)
        self._script = script
        self.update(copy.deepcopy(formatting))

    def update(self, newDict):
        for key, val in list(newDict.items()):
            if key in self:
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

    def getString(self, **args):
        """Gets a human consumable string for a specific value
        (e.g., an indicator for a checkbox state).

        Arguments expected in args:
        - mode: output mode, such as 'speech', 'braille'.
        - stringType: the type of the string to get (see the dictionary above).
        """
        return self['strings'][args['mode']][args['stringType']]

    def getFormat(self, **args):
        """Get a formatting string for the given mode and formatType for a
        role (e.g., a where am I string for a text object).

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
