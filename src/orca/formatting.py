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

from . import object_properties
from . import settings

# pylint: disable-msg=C0301

TUTORIAL = '(tutorial and (pause + tutorial) or [])'
MNEMONIC = '(mnemonic and (pause + mnemonic + lineBreak) or [])'

BRAILLE_TEXT = '[Text(obj, asString(labelOrName or placeholderText), asString(eol), startOffset, endOffset)]\
                + (invalid and [Region(" " + asString(invalid))])\
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
            'invalid': object_properties.INVALID_INDICATORS_SPEECH,
            'required': object_properties.STATE_REQUIRED_SPEECH,
            'readonly': object_properties.STATE_READ_ONLY_SPEECH,
            'insensitive': object_properties.STATE_INSENSITIVE_SPEECH,
            'checkbox': object_properties.CHECK_BOX_INDICATORS_SPEECH,
            'radiobutton': object_properties.RADIO_BUTTON_INDICATORS_SPEECH,
            'switch': object_properties.SWITCH_INDICATORS_SPEECH,
            'togglebutton': object_properties.TOGGLE_BUTTON_INDICATORS_SPEECH,
            'expansion': object_properties.EXPANSION_INDICATORS_SPEECH,
            'nodelevel': object_properties.NODE_LEVEL_SPEECH,
            'nestinglevel': object_properties.NESTING_LEVEL_SPEECH,
            'multiselect': object_properties.STATE_MULTISELECT_SPEECH,
            'iconindex': object_properties.ICON_INDEX_SPEECH,
            'groupindex': object_properties.GROUP_INDEX_SPEECH,
            'clickable': object_properties.STATE_CLICKABLE,
            'haslongdesc': object_properties.STATE_HAS_LONGDESC,
        },
        'braille': {
            'eol': object_properties.EOL_INDICATOR_BRAILLE,
            'required': object_properties.STATE_REQUIRED_BRAILLE,
            'readonly': object_properties.STATE_READ_ONLY_BRAILLE,
            'insensitive': object_properties.STATE_INSENSITIVE_BRAILLE,
            'invalid': object_properties.INVALID_INDICATORS_BRAILLE,
            'checkbox': object_properties.CHECK_BOX_INDICATORS_BRAILLE,
            'radiobutton': object_properties.RADIO_BUTTON_INDICATORS_BRAILLE,
            'switch': object_properties.SWITCH_INDICATORS_BRAILLE,
            'togglebutton': object_properties.TOGGLE_BUTTON_INDICATORS_BRAILLE,
            'expansion': object_properties.EXPANSION_INDICATORS_BRAILLE,
            'nodelevel': object_properties.NODE_LEVEL_BRAILLE,
            'nestinglevel': object_properties.NESTING_LEVEL_BRAILLE,
        },
        'sound': {
            'invalid': object_properties.INVALID_INDICATORS_SOUND,
            'required': object_properties.STATE_REQUIRED_SOUND,
            'readonly': object_properties.STATE_READ_ONLY_SOUND,
            'insensitive': object_properties.STATE_INSENSITIVE_SOUND,
            'checkbox': object_properties.CHECK_BOX_INDICATORS_SOUND,
            'radiobutton': object_properties.RADIO_BUTTON_INDICATORS_SOUND,
            'switch': object_properties.SWITCH_INDICATORS_SOUND,
            'togglebutton': object_properties.TOGGLE_BUTTON_INDICATORS_SOUND,
            'expansion': object_properties.EXPANSION_INDICATORS_SOUND,
            'multiselect': object_properties.STATE_MULTISELECT_SOUND,
            'clickable': object_properties.STATE_CLICKABLE_SOUND,
            'haslongdesc': object_properties.STATE_HAS_LONGDESC_SOUND,
            'visited': object_properties.STATE_VISITED_SOUND,
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
            'unfocused': 'oldAncestors + newAncestors',
            'basicWhereAmI': 'toolbar',
            'detailedWhereAmI' : '[]'
            },
        'suffix': {
            'focused': '[]',
            'unfocused': 'newNodeLevel + unselectedCell + clickable + hasLongDesc + ' + TUTORIAL + ' + description',
            'basicWhereAmI': TUTORIAL + ' + clickable + hasLongDesc + description',
            'detailedWhereAmI': TUTORIAL + ' + clickable + hasLongDesc + description'
            },
        'default': {
            'focused': '[]',
            'unfocused': 'labelOrName + roleName + availability + ' + MNEMONIC + ' + accelerator + childWidget',
            'basicWhereAmI': 'labelOrName + roleName',
            'detailedWhereAmI' : 'pageSummary'
            },
        pyatspi.ROLE_ALERT: {
            'unfocused': 'labelOrName + roleName + pause + (expandedEOCs or unrelatedLabels or description)'
            },
        pyatspi.ROLE_ANIMATION: {
            'unfocused': 'labelAndName'
            },
        pyatspi.ROLE_ARTICLE: {
            'focused': 'labelOrName + roleName',
            'unfocused': 'labelOrName + roleName + pause + currentLineText + allTextSelection',
            },
        pyatspi.ROLE_BLOCK_QUOTE: {
            'focused' : 'leaving or (roleName + pause + nestingLevel)',
            'unfocused': 'roleName + pause + nestingLevel + pause + displayedText',
            },
        pyatspi.ROLE_CANVAS: {
            'focused': 'labelAndName + imageDescription + roleName + pause + positionInList',
            'unfocused': 'labelAndName + imageDescription + roleName + pause + positionInList',
            'basicWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause',
            'detailedWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause + selectedItems + pause'
            },
        pyatspi.ROLE_CAPTION: {
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName'
            },
        pyatspi.ROLE_CHECK_BOX: {
            'focused': 'checkedState',
            'unfocused': 'labelOrName + roleName + checkedState + required + pause + invalid + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'namedContainingPanel + labelOrName + roleName + checkedState + ' + MNEMONIC + ' + accelerator + required + pause + invalid'
            },
        pyatspi.ROLE_CHECK_MENU_ITEM: {
            'focused': 'checkedState',
            'unfocused': 'labelOrName + roleName + checkedState + required + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList',
            'basicWhereAmI': 'ancestors + pause + labelOrName + roleName + checkedState + pause + accelerator + pause + positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_COLOR_CHOOSER: {
            'focused': 'value',
            'unfocused': 'label + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'label + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        pyatspi.ROLE_COLUMN_HEADER: {
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName'
            },
        pyatspi.ROLE_COMBO_BOX: {
            'focused': 'expandableState',
            'unfocused': 'labelAndName + roleName + pause + (currentLineText + anyTextSelection or positionInList) + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'label + roleName + pause + name + (currentLineText + anyTextSelection or positionInList) + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_COMMENT: {
            'focused': 'labelOrName + roleName',
            'unfocused': 'labelOrName + roleName + pause + currentLineText + allTextSelection',
            },
        pyatspi.ROLE_DIAL: {
            'focused': 'value',
            'unfocused': 'labelOrName + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        pyatspi.ROLE_DIALOG: {
            'focused': 'labelOrName + roleName + description',
            'unfocused': 'expandedEOCs or (labelOrName + (unrelatedLabels or description))'
            },
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'unfocused': 'label + readOnly + textRole + currentLineText + anyTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        'ROLE_DPUB_LANDMARK': {
            'focused': 'leaving or labelOrName',
            'unfocused': 'labelOrName + currentLineText + allTextSelection'
            },
        'ROLE_DPUB_SECTION': {
            'focused': 'leaving or (labelOrName + roleName)',
            'unfocused': 'labelOrName + currentLineText + allTextSelection'
            },
        pyatspi.ROLE_EMBEDDED: {
            'focused': 'labelOrName + roleName',
            'unfocused': '(expandedEOCs or (labelOrName + unrelatedLabels)) + roleName'
            },
        pyatspi.ROLE_ENTRY: {
            'focused': 'labelOrName + readOnly + textRole + (currentLineText or placeholderText) + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + (currentLineText or placeholderText) + allTextSelection + required + pause + invalid + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + readOnly + textRole + (textContent or placeholderText) + anyTextSelection + required + pause + invalid + ' + MNEMONIC,
            'detailedWhereAmI': 'labelOrName + readOnly + textRole + (textContentWithAttributes or placeholderText) + anyTextSelection + required + pause + invalid + ' + MNEMONIC,
            },
        'ROLE_FOOTNOTE': {
            'unfocused': 'labelOrName + roleName + pause + currentLineText + allTextSelection',
            },
        pyatspi.ROLE_FOOTER: {
            'unfocused': '(displayedText or name) + roleName',
        },
        pyatspi.ROLE_FORM: {
            'focused': 'leaving or (labelAndName + roleName)',
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName'
            },
        pyatspi.ROLE_FRAME: {
            'focused': 'labelOrName + roleName',
            'unfocused': 'labelOrName + roleName + unfocusedDialogCount + availability'
            },
        pyatspi.ROLE_HEADER: {
            'unfocused': '(displayedText or name) + roleName',
        },
        pyatspi.ROLE_HEADING: {
            'focused': 'displayedText + roleName + expandableState',
            'unfocused': 'displayedText + roleName + expandableState',
            'basicWhereAmI': 'label + readOnly + textRole + pause + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + pause + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        pyatspi.ROLE_ICON: {
            'focused': 'labelAndName + imageDescription + roleName + pause + positionInList',
            'unfocused': 'labelAndName + imageDescription + roleName + pause + positionInList',
            'basicWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause',
            'detailedWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause + selectedItems + pause'
            },
        pyatspi.ROLE_IMAGE: {
            'unfocused': 'labelAndName + roleName'
            },
        pyatspi.ROLE_INFO_BAR: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        pyatspi.ROLE_LABEL: {
            'focused': 'label + displayedText + allTextSelection + roleName',
            'unfocused': 'label + displayedText + allTextSelection + roleName',
            'basicWhereAmI': 'label + displayedText + allTextSelection + roleName'
            },
        pyatspi.ROLE_LANDMARK: {
            'focused': 'leaving or (labelAndName + roleName)',
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName + pause + unrelatedLabels'
            },
        pyatspi.ROLE_LAYERED_PANE: {
            'focused': 'labelAndName + roleName + availability + noShowingChildren',
            'unfocused': 'labelAndName + roleName + availability + noShowingChildren',
            'basicWhereAmI': 'labelAndName + pause + roleName + pause + selectedItemCount + pause',
            'detailedWhereAmI': 'labelAndName + pause + roleName + pause + selectedItemCount + pause + selectedItems + pause'
            },
        pyatspi.ROLE_LINK: {
            'unfocused': '(displayedText or name) + roleName + pause + expandableState + availability + ' + MNEMONIC,
            'basicWhereAmI': 'linkInfo + pause + siteDescription + pause + fileSize + pause + ' + MNEMONIC
            },
        pyatspi.ROLE_LIST: {
            'focused' : 'leaving or (labelOrName + pause + numberOfChildren + pause + nestingLevel)',
            'unfocused': 'labelOrName + pause + focusedItem + pause + multiselectableState + numberOfChildren + pause'
            },
        pyatspi.ROLE_LIST_BOX: {
            'focused': 'labelOrName + multiselectableState + numberOfChildren',
            'unfocused': 'labelOrName + pause + focusedItem + pause + multiselectableState + numberOfChildren + pause'
            },
        pyatspi.ROLE_LIST_ITEM: {
            'focused': 'expandableState',
            'unfocused': '(labelOrName or (displayedText + allTextSelection)) + pause + expandableState + pause + positionInList + pause + listBoxItemWidgets',
            'basicWhereAmI': 'label + roleName + pause + (name or displayedText) + pause + positionInList + pause + expandableState + (nodeLevel or nestingLevel) + pause'
            },
        pyatspi.ROLE_MATH: {
            'unfocused': 'math',
        },
        # TODO - JD: When we bump dependencies to TBD, remove this fake role and use the real one.
        'ROLE_MATH_ENCLOSED': {
            'unfocused': 'enclosedBase + enclosedEnclosures',
        },
        # TODO - JD: When we bump dependencies to TBD, remove this fake role and use the real one.
        'ROLE_MATH_FENCED': {
            'unfocused': 'fencedStart + pause + fencedContents + pause + fencedEnd',
        },
        pyatspi.ROLE_MATH_FRACTION: {
            'unfocused': 'fractionStart + pause + fractionNumerator + fractionLine + fractionDenominator + pause + fractionEnd + pause',
        },
        pyatspi.ROLE_MATH_ROOT: {
            'unfocused': 'rootStart + rootBase + pause + rootEnd + pause',
        },
        # TODO - JD: When we bump dependencies to TBD, remove this fake role and use the real one.
        'ROLE_MATH_MULTISCRIPT': {
            'unfocused': 'scriptBase + pause + scriptPrescripts + pause + scriptPostscripts + pause',
        },
        # TODO - JD: When we bump dependencies to TBD, remove this fake role and use the real one.
        'ROLE_MATH_SCRIPT_SUBSUPER': {
            'unfocused': 'scriptBase + pause + scriptSubscript + pause + scriptSuperscript + pause',
        },
        # TODO - JD: When we bump dependencies to TBD, remove this fake role and use the real one.
        'ROLE_MATH_SCRIPT_UNDEROVER': {
            'unfocused': 'scriptBase + pause + scriptUnderscript + pause + scriptOverscript + pause',
        },
        # TODO - JD: When we bump dependencies to TBD, remove this fake role and use the real one.
        'ROLE_MATH_TABLE': {
            'unfocused': 'mathTableStart + pause + mathTableRows + pause + mathTableEnd + pause',
        },
        # TODO - JD: When we bump dependencies to TBD, remove this fake role and use the real one.
        'ROLE_MATH_TABLE_ROW': {
            'unfocused': 'mathRow',
        },
        pyatspi.ROLE_MENU: {
            'focused': 'labelOrName + roleName',
            'unfocused': 'labelOrName + roleName + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList',
            'basicWhereAmI': '(ancestors or parentRoleName) + pause + labelOrName + roleName + pause + positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_MENU_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'labelOrName + menuItemCheckedState + expandableState + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList',
            'basicWhereAmI': 'ancestors + pause + labelOrName + pause + accelerator + pause + positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_NOTIFICATION: {
            'unfocused': 'roleName + unrelatedLabels'
            },
        pyatspi.ROLE_PAGE: {
            'focused': 'label + readOnly + currentLineText + anyTextSelection',
            'unfocused': 'label + readOnly + currentLineText + anyTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        pyatspi.ROLE_PAGE_TAB: {
            'focused': 'labelOrName + roleName + pause + positionInList + ' + MNEMONIC + ' + accelerator',
            'unfocused': 'labelOrName + roleName + pause + positionInList + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'parentRoleName + pause + labelOrName + roleName + pause + positionInList + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_PANEL: {
            'focused': 'leaving or (labelAndName + roleName)',
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName + pause + unrelatedLabels'
            },
        pyatspi.ROLE_PARAGRAPH: {
            'focused': 'labelOrName + readOnly + textRole + textIndentation + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + textIndentation + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        pyatspi.ROLE_PASSWORD_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        pyatspi.ROLE_PROGRESS_BAR: {
            'focused': 'progressBarIndex + progressBarValue',
            'unfocused': 'progressBarIndex + labelAndName + progressBarValue'
            },
        pyatspi.ROLE_PUSH_BUTTON: {
            'focused': 'expandableState',
            'unfocused': 'labelAndName + expandableState + roleName + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelAndName + expandableState + roleName + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_RADIO_BUTTON: {
            'focused': 'radioState',
            'unfocused': '(name or label) + pause + radioState + roleName + availability + lineBreak + ' + MNEMONIC + ' + accelerator + pause + positionInList + pause',
            'basicWhereAmI': 'radioButtonGroup + pause + (name or label) + roleName + pause + radioState + pause + positionInGroup + ' + MNEMONIC + ' + accelerator'
            },
        pyatspi.ROLE_RADIO_MENU_ITEM: {
            # OpenOffice check menu items currently have a role of "menu item"
            # rather then "check menu item", so we need to test if one of the
            # states is CHECKED. If it is, then add that in to the list of
            # speech utterances. Note that we can't tell if this is a "check
            # menu item" that is currently unchecked and speak that state.
            # See Orca bug #433398 for more details.
            #
            'focused': 'labelOrName + radioState + roleName + availability + positionInList',
            'unfocused': 'labelOrName + radioState + roleName + availability + ' + MNEMONIC + ' + accelerator + positionInList',
            'basicWhereAmI': 'ancestors + labelOrName + roleName + radioState + accelerator + positionInList + ' + MNEMONIC
            },
        pyatspi.ROLE_ROW_HEADER: {
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName'
            },
        pyatspi.ROLE_SCROLL_BAR: {
            'focused': 'value',
            'unfocused': 'labelOrName + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        pyatspi.ROLE_SECTION: {
            'focused': 'labelOrName + currentLineText + allTextSelection + roleName',
            'unfocused': 'labelOrName + currentLineText + allTextSelection + roleName + ' + MNEMONIC,
            },
        pyatspi.ROLE_SLIDER: {
            'focused': 'value',
            'unfocused': 'labelOrName + roleName + value + required + pause + invalid + availability + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required + pause + invalid'
            },
        pyatspi.ROLE_SPIN_BUTTON: {
            'focused': 'name',
            'unfocused': 'labelAndName + allTextSelection + roleName + required + pause + invalid + availability + ' + MNEMONIC,
            'basicWhereAmI': 'label + roleName + name + allTextSelection + ' + MNEMONIC + ' + accelerator + required + pause + invalid'
            },
        pyatspi.ROLE_SPLIT_PANE: {
            'focused': 'value',
            'unfocused': 'labelAndName + roleName + value + availability + ' + MNEMONIC,
            'basicWhereAmI' : 'labelAndName + roleName + value'
            },
        pyatspi.ROLE_STATIC: {
            'unfocused': '(displayedText or name) + roleName',
        },
        'ROLE_SWITCH': {
            'focused': 'switchState',
            'unfocused': 'labelOrName + roleName + switchState + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelOrName + roleName + switchState'
            },

        pyatspi.ROLE_TABLE: {
            'focused': 'leaving or (labelAndName + pause + table)',
            'unfocused': 'labelAndName + pause + table',
            'basicWhereAmI': 'labelAndName + pause + table'
            },
        pyatspi.ROLE_TABLE_CELL: {
            'focused': '((tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState) + pause + (expandableState and (expandableState + pause + numberOfChildren + pause))',
            'unfocused': 'tableCellRow + pause',
            'basicWhereAmI': 'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + expandableState + pause + nodeLevel + pause',
            'detailedWhereAmI': 'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + tableCellRow + pause + expandableState + pause + nodeLevel + pause',
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
                          or (newRowHeader + (newColumnHeader or columnHeaderIfToggleAndNoText) \
                              + cellCheckedState\
                              + (realActiveDescendantDisplayedText or imageDescription + image)\
                              + (expandableState and (expandableState + numberOfChildren))\
                              + required + pause + invalid)'
            },
        pyatspi.ROLE_TABLE_ROW: {
            'focused': 'expandableState',
            },
        pyatspi.ROLE_TEAROFF_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelOrName + roleName + availability '
            },
        pyatspi.ROLE_TERMINAL: {
            'focused': 'textContent',
            'unfocused': 'textContent',
            'basicWhereAmI': 'label + readOnly + pause + textRole + pause + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + pause + textRole + pause + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        pyatspi.ROLE_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + pause + textIndentation + (currentLineText or placeholderText) + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + pause + textIndentation + (currentLineText or placeholderText) + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + readOnly + textRole + pause + (textContent or placeholderText) + anyTextSelection + pause + ' + MNEMONIC,
            'detailedWhereAmI': 'labelOrName + readOnly + textRole + pause + (textContentWithAttributes or placeholderText) + anyTextSelection + pause + ' + MNEMONIC
            },
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'focused': 'expandableState or toggleState',
            'unfocused': 'labelOrName + roleName + (expandableState or toggleState) + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelOrName + roleName + (expandableState or toggleState)'
            },
        pyatspi.ROLE_TOOL_BAR: {
            'focused': 'labelAndName + roleName',
            'unfocused': 'labelAndName + roleName',
            },
        pyatspi.ROLE_TOOL_TIP: {
            'unfocused': 'labelAndName',
            'basicWhereAmI': 'labelAndName'
            },
        pyatspi.ROLE_TREE_ITEM: {
            'focused': 'expandableState',
            'unfocused': '(labelOrName or displayedText) + pause + expandableState + pause + positionInList',
            'basicWhereAmI': '(labelOrName or displayedText) + roleName + pause + positionInList + pause + expandableState + (nodeLevel or nestingLevel)'
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
                                     asString(label + displayedText + value + roleName + required + invalid))]',
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + value + roleName + required + invalid))]',
            },
        pyatspi.ROLE_ALERT: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]))'
            },
        pyatspi.ROLE_ANIMATION: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName + (description and space(": ") + description)))]',
            },
        pyatspi.ROLE_ARTICLE: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]\
                             + (childWidget and ([Region(" ")] + childWidget))))'
            },
        #pyatspi.ROLE_ARROW: 'default'
        pyatspi.ROLE_CANVAS: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText + imageDescription) or name) + roleName))]'
            },
        pyatspi.ROLE_CHECK_BOX: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName),\
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
            'unfocused': '((comboBoxTextObj and ([Text(comboBoxTextObj[0], asString(label), asString(eol))] \
                                               + [Region(" " + asString(roleName))])) \
                           or [Component(obj, asString(label + name + roleName), label and (len(asString(label)) + 1) or 0)])'
            },
        #pyatspi.ROLE_DESKTOP_ICON: 'default'
        pyatspi.ROLE_DIAL: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + value + roleName + required))]'
            },
        pyatspi.ROLE_DIALOG: {
            'unfocused': '[Component(obj, asString(labelOrName + roleName))]'
            },
        #pyatspi.ROLE_DIRECTORY_PANE: 'default'
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'focused': '[Text(obj, asString(placeholderText), asString(eol), startOffset, endOffset)]\
                          + (required and [Region(" " + asString(required))])\
                          + (readOnly and [Region(" " + asString(readOnly))])',
            'unfocused': BRAILLE_TEXT
            },
        pyatspi.ROLE_ENTRY: {
            'unfocused': BRAILLE_TEXT
            },
        pyatspi.ROLE_FORM: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]))'
            },
        pyatspi.ROLE_FRAME: {
            'focused':   '[Component(obj,\
                                     asString(((label + displayedText) or name) + value + roleName + alertAndDialogCount))]',
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText) or name) + value + roleName + alertAndDialogCount))]'
            },
        pyatspi.ROLE_HEADING: {
            'unfocused': '[Text(obj, asString(placeholderText), "", startOffset, endOffset)]\
                          + [Region(" " + asString(roleName))]'
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
            'unfocused': '[Text(obj, asString(labelAndName))]'
            },
        pyatspi.ROLE_LINK: {
            'unfocused': '[Link(obj, asString(currentLineText)\
                                     or asString(displayedText)\
                                     or asString(name))] \
                        + (roleName and [Region(" " + asString(roleName))])',
        },
        pyatspi.ROLE_LIST: {
            'unfocused': '[Component(obj,\
                                     asString(label + focusedItem + roleName),\
                                     asString(label) and (len(asString(label)) + 1) or 0)]'
        },
        pyatspi.ROLE_LIST_BOX: {
            'unfocused': '[Component(obj,\
                                     asString(label + focusedItem + roleName),\
                                     asString(label) and (len(asString(label)) + 1) or 0)]'
        },
        pyatspi.ROLE_LIST_ITEM: {
            'focused':   '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj,\
                                     asString(label + displayedText + expandableState + roleName + availability) + asString(accelerator))]\
                          + (nestingLevel and [Region(" " + asString(nestingLevel))])\
                          + (listBoxItemWidgets and ([Region(" ")] + listBoxItemWidgets))))',
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelOrName + expandableState))]\
                              + (nestingLevel and [Region(" " + asString(nestingLevel))])\
                              + (listBoxItemWidgets and ([Region(" ")] + listBoxItemWidgets))))',
            },
        pyatspi.ROLE_MENU: {
            'focused':   '[Component(obj,\
                                     asString(labelOrName + roleName + availability) + asString(accelerator))]',
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName))]',
            },
        #pyatspi.ROLE_MENU_BAR: 'default'
        pyatspi.ROLE_MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + expandableState + availability) + asString(accelerator),\
                                     indicator=asString(menuItemCheckedState))]'
            },
        pyatspi.ROLE_PAGE: {
            'unfocused': BRAILLE_TEXT
            },
        #pyatspi.ROLE_OPTION_PANE: 'default'
        pyatspi.ROLE_PAGE_TAB: {
            'focused':   '[Component(obj,\
                                     asString(labelOrName + roleName + availability) + asString(accelerator))]',
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName))]'
            },
        #pyatspi.ROLE_PAGE_TAB_LIST: 'default'
        pyatspi.ROLE_PANEL: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]\
                             + (childWidget and ([Region(" ")] + childWidget))))'
            },
        pyatspi.ROLE_PARAGRAPH: {
            'unfocused': BRAILLE_TEXT
            },
        pyatspi.ROLE_PASSWORD_TEXT: {
            'unfocused': BRAILLE_TEXT
            },
        pyatspi.ROLE_PROGRESS_BAR: {
            'unfocused': '(progressBarValue and \
                           [Component(obj, asString(labelAndName + progressBarValue + roleName + progressBarIndex))]) \
                           or []'
            },
        pyatspi.ROLE_PUSH_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString((labelAndName or description) + expandableState + roleName))]'
            },
        pyatspi.ROLE_RADIO_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString((labelOrName or description) + roleName),\
                                     indicator=asString(radioState))]'
            },
        pyatspi.ROLE_RADIO_MENU_ITEM: {
            'focused':   '[Component(obj,\
                                     asString((labelOrName or description) + roleName + availability)\
                                     + asString(accelerator),\
                                     indicator=asString(radioState))]',
            'unfocused': '[Component(obj,\
                                     asString(labelOrName or description)\
                                     + asString(accelerator),\
                                     indicator=asString(radioState))]'
            },
        #pyatspi.ROLE_ROW_HEADER: 'default'
        pyatspi.ROLE_SCROLL_BAR: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + value + roleName + required))]'
            },
        pyatspi.ROLE_SCROLL_PANE: {
            'unfocused': 'asPageTabOrScrollPane'
            },
        pyatspi.ROLE_SECTION: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]\
                             + (childWidget and ([Region(" ")] + childWidget))))'
            },
        #'REAL_ROLE_SCROLL_PANE': 'default'
        pyatspi.ROLE_SLIDER: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + value + roleName + required + invalid))]'
            },
        pyatspi.ROLE_SPIN_BUTTON: {
            'unfocused': '[Text(obj, asString(label), asString(eol))]\
                          + (required and [Region(" " + asString(required))] or [])\
                          + (readOnly and [Region(" " + asString(readOnly))] or [])'
            },
        'ROLE_SWITCH' : {
            'unfocused': '[Component(obj,\
                                     asString((labelOrName or description) + roleName),\
                                     indicator=asString(switchState))]'
            },
        #pyatspi.ROLE_SPLIT_PANE: 'default'
        #pyatspi.ROLE_TABLE: 'default'
        pyatspi.ROLE_TABLE_CELL: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ') or tableCellRow)',
            },
        'REAL_ROLE_TABLE_CELL': {
            'unfocused': '((tableCell2ChildToggle + tableCell2ChildLabel)\
                          or (substring and ' + BRAILLE_TEXT + ') \
                          or (cellCheckedState\
                              + (columnHeaderIfToggleAndNoText and [Region(" "), Component(obj, asString(columnHeaderIfToggleAndNoText))])\
                              + ((realActiveDescendantDisplayedText and [Component(obj, asString(realActiveDescendantDisplayedText))])\
                                 or (imageDescription and [Region(" "), Component(obj, asString(imageDescription))]))\
                              + (realActiveDescendantRoleName and [Component(obj, (realActiveDescendantDisplayedText and " " or "") + asString(realActiveDescendantRoleName))])\
                              + (expandableState and [Region(" " + asString(expandableState))])\
                              + (required and [Region(" " + asString(required))]))\
                          or ([Component(obj,"")]))'
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
                                     asString((labelOrName or description) + expandableState + roleName),\
                                     indicator=asString(toggleState))]'
            },
        pyatspi.ROLE_TOOL_BAR: {
            'unfocused': '[Component(obj, asString(labelOrName + roleName))]',
            },
        pyatspi.ROLE_TREE_ITEM: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelOrName + expandableState))]\
                              + (nestingLevel and [Region(" " + asString(nestingLevel))])))',
            },
        #pyatspi.ROLE_TREE: 'default'
        #pyatspi.ROLE_TREE_TABLE: 'default'
        #pyatspi.ROLE_WINDOW: 'default'
    },

    ####################################################################
    #                                                                  #
    # Formatting for sound.                                            #
    #                                                                  #
    ####################################################################

    'sound': {
        'prefix': {
            'focused': '[]',
            'unfocused': '[]',
            'basicWhereAmI': '[]',
            'detailedWhereAmI': '[]'
        },
        'suffix': {
            'focused': '[]',
            'unfocused': 'clickable + hasLongDesc',
            'basicWhereAmI': '[]',
            'detailedWhereAmI': '[]'
        },
        'default': {
            'focused': '[]',
            'unfocused': 'roleName',
            'basicWhereAmI': '[]',
            'detailedWhereAmI': '[]'
        },
        pyatspi.ROLE_CANVAS: {
            'unfocused': 'roleName + positionInSet',
        },
        pyatspi.ROLE_CHECK_BOX: {
            'focused': 'checkedState',
            'unfocused': 'roleName + checkedState + required + invalid + availability',
        },
        pyatspi.ROLE_CHECK_MENU_ITEM: {
            'focused': 'checkedState',
            'unfocused': 'roleName + checkedState + availability + positionInSet',
        },
        pyatspi.ROLE_COMBO_BOX: {
            'focused': 'expandableState',
            'unfocused': 'roleName + positionInSet',
        },
        pyatspi.ROLE_DIAL: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage + required + invalid + availability',
        },
        pyatspi.ROLE_ENTRY: {
            'unfocused': 'roleName + readOnly + required + invalid + availability',
        },
        pyatspi.ROLE_HEADING: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState',
        },
        pyatspi.ROLE_ICON: {
            'unfocused': 'roleName + positionInSet',
        },
        pyatspi.ROLE_LINK: {
            'focused': 'expandableState',
            'unfocused': 'roleName + visitedState + expandableState',
        },
        pyatspi.ROLE_LIST: {
            'unfocused': 'roleName + multiselectableState',
        },
        pyatspi.ROLE_LIST_BOX: {
            'unfocused': 'roleName + multiselectableState',
        },
        pyatspi.ROLE_LIST_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState + positionInSet',
        },
        pyatspi.ROLE_MENU_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState + availability + positionInSet',
        },
        pyatspi.ROLE_PAGE_TAB: {
            'unfocused': 'roleName + positionInSet',
        },
        pyatspi.ROLE_PROGRESS_BAR: {
            'focused': 'progressBarValue',
            'unfocused': 'roleName + progressBarValue'
        },
        pyatspi.ROLE_PUSH_BUTTON: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState + availability',
        },
        pyatspi.ROLE_RADIO_BUTTON: {
            'focused': 'radioState',
            'unfocused': 'roleName + radioState + availability + positionInSet',
        },
        pyatspi.ROLE_RADIO_MENU_ITEM: {
            'focused': 'radioState',
            'unfocused': 'roleName + checkedState + availability + positionInSet',
        },
        pyatspi.ROLE_SCROLL_BAR: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage',
        },
        pyatspi.ROLE_SLIDER: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage + required + invalid + availability',
        },
        pyatspi.ROLE_SPIN_BUTTON: {
            'focused': 'percentage',
            'unfocused': 'roleName + availability + percentage + required + invalid',
        },
        pyatspi.ROLE_SPLIT_PANE: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage + availability',
        },
        'ROLE_SWITCH': {
            'focused': 'switchState',
            'unfocused': 'roleName + switchState + availability',
        },
        pyatspi.ROLE_TABLE_CELL: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState',
        },
        pyatspi.ROLE_TABLE_ROW: {
            'focused': 'expandableState',
        },
        pyatspi.ROLE_TEXT: {
            'unfocused': 'roleName + readOnly + required + invalid + availability',
        },
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'focused': 'expandableState or toggleState',
            'unfocused': 'roleName + (expandableState or toggleState) + availability',
        },
        pyatspi.ROLE_TREE_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState + positionInSet',
        },
    },
}

class Formatting(dict):

    def __init__(self, script):
        dict.__init__(self)
        self._script = script
        self.update(copy.deepcopy(formatting))

    def update(self, newDict):
        for key, val in newDict.items():
            if key in self:
                if isinstance(self[key], dict) and isinstance(val, dict):
                    self[key].update(val)
                elif isinstance(self[key], str) \
                     and isinstance(val, str):
                    self[key] = val
                else:
                    # exception or such like, we are trying to merge
                    # incompatible trees.
                    # throw an exception?
                    print("an error has occurred, cant merge dicts.")
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
            return self[args['mode']][args['role']][args['formatType']]
        except:
            pass

        if args.get('formatType') == 'detailedWhereAmI':
            try:
                return self[args['mode']][args['role']]['basicWhereAmI']
            except:
                pass

        try:
            return self[args['mode']][args['role']]['unfocused']
        except:
            pass


        try:
            return self[args['mode']]['default'][args['formatType']]
        except:
            pass

        try:
            return self[args['mode']]['default']['unfocused']
        except:
            return []
