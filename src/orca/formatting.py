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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

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
            'groupindextotalunknown':object_properties.GROUP_INDEX_TOTAL_UNKNOWN_SPEECH,
            'clickable': object_properties.STATE_CLICKABLE,
            'haslongdesc': object_properties.STATE_HAS_LONGDESC,
            'hasdetails': object_properties.RELATION_HAS_DETAILS,
            'detailsfor': object_properties.RELATION_DETAILS_FOR
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
            'ancestor': '[]',
            'focused': 'detailsFor',
            'unfocused': 'oldAncestors + newAncestors',
            'basicWhereAmI': 'toolbar',
            'detailedWhereAmI' : '[]'
            },
        'suffix': {
            'ancestor': '[]',
            'focused': '[]',
            'unfocused': 'newNodeLevel + unselectedCell + clickable + pause + hasLongDesc + hasDetails + detailsFor +' + TUTORIAL + ' + description + pause + hasPopup',
            'basicWhereAmI': TUTORIAL + ' + clickable + hasLongDesc + description + pause + hasPopup + pause + detailsFor + pause + allDetails',
            'detailedWhereAmI': TUTORIAL + ' + clickable + hasLongDesc + description + pause + hasPopup + detailsFor + pause + allDetails'
            },
        'default': {
            'ancestor': '[]',
            'focused': '[]',
            'unfocused': 'labelOrName + roleName + availability + ' + MNEMONIC + ' + accelerator + childWidget',
            'basicWhereAmI': 'labelOrName + roleName',
            'detailedWhereAmI' : 'pageSummary'
            },
        Atspi.Role.ALERT: {
            'unfocused': 'roleName + labelOrName + pause + alertText'
            },
        Atspi.Role.ANIMATION: {
            'unfocused': 'labelAndName'
            },
        Atspi.Role.ARTICLE: {
            'focused': 'labelOrName + roleName',
            'unfocused': 'labelOrName + roleName + pause + currentLineText + allTextSelection',
            },
        'ROLE_ARTICLE_IN_FEED' : {
            'unfocused': '(labelOrName or currentLineText or roleName) + pause + positionInList',
            },
        Atspi.Role.BLOCK_QUOTE: {
            'focused' : 'leaving or (roleName + pause + nestingLevel)',
            'unfocused': 'roleName + pause + nestingLevel + pause + displayedText',
            },
        Atspi.Role.CANVAS: {
            'focused': 'labelAndName + (imageDescription or roleName) + pause + positionInList',
            'unfocused': 'labelAndName + (imageDescription or roleName) + pause + positionInList',
            'basicWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause',
            'detailedWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause + selectedItems + pause'
            },
        Atspi.Role.CAPTION: {
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName'
            },
        Atspi.Role.CHECK_BOX: {
            'focused': 'checkedState',
            'unfocused': 'labelOrName + readOnly + roleName + checkedState + required + pause + invalid + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'namedContainingPanel + labelOrName + readOnly + roleName + checkedState + ' + MNEMONIC + ' + accelerator + required + pause + invalid'
            },
        Atspi.Role.CHECK_MENU_ITEM: {
            'focused': 'checkedState',
            'unfocused': 'labelOrName + roleName + checkedState + required + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList',
            'basicWhereAmI': 'ancestors + pause + labelOrName + roleName + checkedState + pause + accelerator + pause + positionInList + ' + MNEMONIC
            },
        Atspi.Role.COLOR_CHOOSER: {
            'focused': 'value',
            'unfocused': 'label + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'label + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        Atspi.Role.COLUMN_HEADER: {
            'focused': 'labelAndName + roleName + pause + sortOrder',
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName + pause + sortOrder'
            },
        Atspi.Role.COMBO_BOX: {
            'focused': 'labelOrName + roleName + expandableState',
            'unfocused': 'labelOrName + roleName + pause + value + pause + positionInList + ' + MNEMONIC + ' + accelerator',
            },
        Atspi.Role.COMMENT: {
            'focused': 'labelOrName + roleName',
            'unfocused': 'labelOrName + roleName + pause + currentLineText + allTextSelection',
            },
        # TODO - JD: When we bump dependencies to 2.34, remove this fake role and use the real one.
        'ROLE_CONTENT_DELETION': {
            'focused': 'leaving or deletionStart',
            'unfocused': 'deletionStart + pause + displayedText + pause + deletionEnd',
            },
        'ROLE_CONTENT_ERROR': {
            'unfocused': 'displayedText + pause + invalid',
            },
        # TODO - JD: When we bump dependencies to 2.34, remove this fake role and use the real one.
        'ROLE_CONTENT_INSERTION': {
            'focused': 'leaving or insertionStart',
            'unfocused': 'insertionStart + pause + displayedText + pause + insertionEnd',
            },
        # TODO - JD: When we bump dependencies to 2.36, remove this fake role and use the real one.
        'ROLE_CONTENT_MARK': {
            'focused': 'leaving or markStart',
            'unfocused': 'markStart + pause + displayedText + pause + markEnd',
            },
        # TODO - JD: When we bump dependencies to 2.36, remove this fake role and use the real one.
        'ROLE_CONTENT_SUGGESTION': {
            'focused': 'leaving or roleName',
            },
        Atspi.Role.DESCRIPTION_LIST: {
            'focused' : 'leaving or (labelOrName + pause + (numberOfChildren or roleName) + pause + nestingLevel)',
            'unfocused': 'labelOrName + pause + focusedItem + pause + multiselectableState + (numberOfChildren or roleName) + pause'
            },
        Atspi.Role.DESCRIPTION_TERM: {
            'unfocused': '(labelOrName or (displayedText + allTextSelection)) + roleName + pause + termValueCount + pause + positionInList',
            },
        Atspi.Role.DESCRIPTION_VALUE: {
            'unfocused': '(labelOrName or (displayedText + allTextSelection)) + roleName + pause + positionInList',
            },
        Atspi.Role.DIAL: {
            'focused': 'value',
            'unfocused': 'labelOrName + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        Atspi.Role.DIALOG: {
            'focused': 'labelOrName + roleName + (unrelatedLabelsOrDescription)',
            'unfocused': '(expandedEOCs or (labelOrName + roleName + (unrelatedLabelsOrDescription)))'
            },
        Atspi.Role.DOCUMENT_FRAME: {
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + anyTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'labelOrName + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        Atspi.Role.DOCUMENT_WEB: {
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + anyTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'labelorName + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        'ROLE_DPUB_LANDMARK': {
            'focused': 'leaving or labelOrName',
            'unfocused': 'labelOrName + currentLineText + allTextSelection'
            },
        'ROLE_DPUB_SECTION': {
            'focused': 'leaving or (labelOrName + roleName)',
            'unfocused': 'labelOrName + currentLineText + allTextSelection'
            },
        Atspi.Role.EMBEDDED: {
            'focused': 'labelOrName + roleName + availability',
            'unfocused': '(expandedEOCs or (labelOrName + unrelatedLabels)) + roleName + availability'
            },
        Atspi.Role.ENTRY: {
            'focused': 'labelOrName + readOnly + textRole + (currentLineText or placeholderText) + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + (currentLineText or placeholderText) + allTextSelection + required + pause + invalid + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + readOnly + textRole + (textContent or placeholderText) + anyTextSelection + required + pause + invalid + ' + MNEMONIC,
            'detailedWhereAmI': 'labelOrName + readOnly + textRole + (textContentWithAttributes or placeholderText) + anyTextSelection + required + pause + invalid + ' + MNEMONIC,
            },
        'ROLE_FEED': {
            'focused': 'leaving or (labelOrName + pause + (numberOfChildren or roleName))',
            'unfocused': 'labelOrName + pause + (numberOfChildren or roleName)',
            },
        Atspi.Role.FOOTNOTE: {
            'unfocused': 'labelOrName + roleName + pause + currentLineText + allTextSelection',
            },
        Atspi.Role.FOOTER: {
            'unfocused': '(displayedText or name) + roleName',
        },
        Atspi.Role.FORM: {
            'focused': 'leaving or (labelAndName + roleName)',
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName'
            },
        Atspi.Role.FRAME: {
            'focused': 'labelOrName',
            'unfocused': 'labelOrName + roleName + unfocusedDialogCount + availability'
            },
        Atspi.Role.HEADER: {
            'unfocused': '(displayedText or name) + roleName',
        },
        Atspi.Role.HEADING: {
            'focused': 'displayedText + roleName + expandableState',
            'unfocused': 'displayedText + roleName + expandableState',
            'basicWhereAmI': 'label + readOnly + textRole + pause + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + pause + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        Atspi.Role.ICON: {
            'focused': 'labelAndName + (imageDescription or roleName) + pause + positionInList',
            'unfocused': 'labelAndName + (imageDescription or roleName) + pause + positionInList',
            'basicWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause',
            'detailedWhereAmI': 'parentRoleName + pause + labelAndName + pause + selectedItemCount + pause + selectedItems + pause'
            },
        Atspi.Role.IMAGE: {
            'unfocused': 'labelAndName + roleName'
            },
        Atspi.Role.INFO_BAR: {
            'unfocused': 'labelAndName + unrelatedLabels'
            },
        Atspi.Role.LABEL: {
            'unfocused': 'label + ((displayedText + allTextSelection) or name) + roleName',
            },
        Atspi.Role.LANDMARK: {
            'focused': 'leaving or (roleName + labelAndName)',
            'unfocused': 'roleName + (labelAndName or (substring and currentLineText)) + pause + unrelatedLabels'
            },
        Atspi.Role.LAYERED_PANE: {
            'focused': '(labelAndName or roleName) + availability + noShowingChildren',
            'unfocused': '(labelAndName or roleName) + availability + noShowingChildren',
            'basicWhereAmI': '(labelAndName or roleName) + pause + selectedItemCount + pause',
            'detailedWhereAmI': '(labelAndName or roleName) + pause + roleName + pause + selectedItemCount + pause + selectedItems + pause'
            },
        Atspi.Role.LINK: {
            'unfocused': '(name or displayedText) + roleName + pause + expandableState + availability + ' + MNEMONIC,
            'basicWhereAmI': 'linkInfo + pause + siteDescription + pause + fileSize + pause + ' + MNEMONIC
            },
        Atspi.Role.LIST: {
            'focused' : 'leaving or (labelOrName + pause + (numberOfChildren or roleName) + pause + nestingLevel)',
            'unfocused': 'labelOrName + pause + focusedItem + pause + multiselectableState + (numberOfChildren or roleName) + pause'
            },
        Atspi.Role.LIST_BOX: {
            'focused': 'labelOrName + multiselectableState + (numberOfChildren or roleName)',
            'unfocused': 'labelOrName + pause + focusedItem + pause + multiselectableState + (numberOfChildren or roleName) + pause'
            },
        Atspi.Role.LIST_ITEM: {
            'focused': 'checkedStateIfCheckable + pause + expandableState',
            'unfocused': '(labelOrName or (displayedText + allTextSelection)) + checkedStateIfCheckable + pause + unselectedStateIfSelectable + pause + expandableState + pause + positionInList + pause + listBoxItemWidgets',
            'basicWhereAmI': 'label + roleName + pause + (name or displayedText) + checkedStateIfCheckable + pause + unselectedStateIfSelectable + pause + positionInList + pause + expandableState + (nodeLevel or nestingLevel) + pause'
            },
        Atspi.Role.MATH: {
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
        Atspi.Role.MATH_FRACTION: {
            'unfocused': 'fractionStart + pause + fractionNumerator + fractionLine + fractionDenominator + pause + fractionEnd + pause',
        },
        Atspi.Role.MATH_ROOT: {
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
        Atspi.Role.MENU: {
            'focused': 'labelOrName + roleName',
            'unfocused': 'labelOrName + roleName + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList',
            'basicWhereAmI': '(ancestors or parentRoleName) + pause + labelOrName + roleName + pause + positionInList + ' + MNEMONIC
            },
        Atspi.Role.MENU_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'labelOrName + checkedStateIfCheckable + expandableState + availability + ' + MNEMONIC + ' + accelerator + pause + positionInList',
            'basicWhereAmI': 'ancestors + pause + labelOrName + checkedStateIfCheckable + pause + accelerator + pause + positionInList + ' + MNEMONIC
            },
        Atspi.Role.NOTIFICATION: {
            'unfocused': 'roleName + labelOrName + pause + (expandedEOCs or unrelatedLabelsOrDescription)'
            },
        Atspi.Role.PAGE: {
            'focused': 'label + readOnly + currentLineText + anyTextSelection',
            'unfocused': 'label + readOnly + currentLineText + anyTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        Atspi.Role.PAGE_TAB: {
            'focused': 'labelOrName + roleName + availability + pause + positionInList + ' + MNEMONIC + ' + accelerator',
            'unfocused': 'labelOrName + roleName + availability + pause + positionInList + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'parentRoleName + pause + labelOrName + roleName + availability + pause + positionInList + ' + MNEMONIC + ' + accelerator'
            },
        Atspi.Role.PANEL: {
            'focused': 'leaving or (labelAndName + roleName + availability + pause + unrelatedLabels)',
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName + availability + pause + unrelatedLabels'
            },
        Atspi.Role.PARAGRAPH: {
            'focused': 'labelOrName + readOnly + textRole + textIndentation + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + textIndentation + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        Atspi.Role.PASSWORD_TEXT: {
            'focused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + currentLineText + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        Atspi.Role.PROGRESS_BAR: {
            'focused': 'progressBarIndex + (progressBarValue or roleName)',
            'unfocused': 'progressBarIndex + labelAndName + (progressBarValue or roleName)'
            },
        Atspi.Role.PUSH_BUTTON: {
            'focused': 'expandableState',
            'unfocused': 'labelAndName + expandableState + roleName + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelAndName + expandableState + roleName + ' + MNEMONIC + ' + accelerator'
            },
        Atspi.Role.RADIO_BUTTON: {
            'focused': 'radioState',
            'unfocused': 'newRadioButtonGroup + pause + (name or label) + pause + radioState + roleName + availability + lineBreak + ' + MNEMONIC + ' + accelerator + pause + positionInList + pause',
            'basicWhereAmI': 'radioButtonGroup + pause + (name or label) + roleName + pause + radioState + pause + positionInGroup + ' + MNEMONIC + ' + accelerator'
            },
        Atspi.Role.RADIO_MENU_ITEM: {
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
        'ROLE_REGION': {
            'focused': 'leaving or (roleName + labelOrName)',
            'unfocused': 'labelOrName + roleName + currentLineText + allTextSelection'
            },
        Atspi.Role.ROW_HEADER: {
            'focused': 'labelAndName + roleName + pause + sortOrder',
            'unfocused': '((substring and currentLineText) or labelAndName) + roleName + pause + sortOrder'
            },
        Atspi.Role.SCROLL_BAR: {
            'focused': 'value',
            'unfocused': 'labelOrName + roleName + value + required + availability + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required'
            },
        Atspi.Role.SCROLL_PANE: {
            'unfocused': '(currentLineText + allTextSelection) or (labelOrName + roleName)',
            },
        Atspi.Role.SECTION: {
            'focused': '(labelOrName or (currentLineText + allTextSelection)) + roleName',
            'unfocused': '(labelOrName or (currentLineText + allTextSelection)) + roleName + ' + MNEMONIC,
            },
        Atspi.Role.SLIDER: {
            'focused': 'value',
            'unfocused': 'labelOrName + roleName + value + required + pause + invalid + availability + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + roleName + value + percentage + ' + MNEMONIC + ' + accelerator + required + pause + invalid'
            },
        Atspi.Role.SPIN_BUTTON: {
            'focused': '(displayedText or value)',
            'unfocused': 'labelAndName + (displayedText or value) + roleName + required + pause + invalid + availability + ' + MNEMONIC,
            'basicWhereAmI': 'label + roleName + name + (displayedText or value) + ' + MNEMONIC + ' + accelerator + required + pause + invalid'
            },
        Atspi.Role.SEPARATOR: {
            'focused': 'roleName + availability',
            'unfocused': 'roleName + availability + (labelOrName or displayedText or value) + ' + MNEMONIC,
            },
        Atspi.Role.SPLIT_PANE: {
            'focused': 'value',
            'unfocused': 'labelAndName + roleName + value + availability + ' + MNEMONIC,
            'basicWhereAmI' : 'labelAndName + roleName + value'
            },
        Atspi.Role.STATIC: {
            'unfocused': '(displayedText or name) + roleName',
            },
        Atspi.Role.STATUS_BAR: {
            'focused': 'labelAndName + roleName',
            'unfocused': 'labelAndName + roleName + pause + statusBar',
            },
        Atspi.Role.SUBSCRIPT: {
            'unfocused': 'roleName + currentLineText + allTextSelection',
            },
        Atspi.Role.SUPERSCRIPT: {
            'unfocused': 'roleName + currentLineText + allTextSelection',
            },
        'ROLE_SWITCH': {
            'focused': 'switchState',
            'unfocused': 'labelOrName + roleName + switchState + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelOrName + roleName + switchState'
            },
        Atspi.Role.TABLE: {
            'focused': 'leaving or (labelAndName + pause + table)',
            'unfocused': 'labelAndName + pause + table',
            'basicWhereAmI': 'labelAndName + pause + table'
            },
        Atspi.Role.TABLE_CELL: {
            'ancestor': 'newRowHeader + newColumnHeader + pause + newRow + pause + newColumn',
            'focused': '((tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState) + pause + (expandableState and (expandableState + pause + numberOfChildren + pause))',
            'unfocused': 'tableCellRow + pause',
            'basicWhereAmI': 'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + expandableState + pause + nodeLevel + pause',
            'detailedWhereAmI': 'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + tableCellRow + pause + expandableState + pause + nodeLevel + pause',
            },
        'REAL_ROLE_TABLE_CELL': {
            # the real cell information
            # note that Atspi.Role.TABLE_CELL is used to work out if we need to
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
        Atspi.Role.TABLE_ROW: {
            'focused': 'expandableState',
            'unfocused': '(labelOrName or displayedText) + pause + expandableState + pause + positionInList',
            'basicWhereAmI': '(labelOrName or displayedText) + roleName + pause + positionInList + pause + expandableState + (nodeLevel or nestingLevel)'
            },
        Atspi.Role.TEAROFF_MENU_ITEM: {
            'focused': '[]',
            'unfocused': 'labelOrName + roleName + availability '
            },
        Atspi.Role.TERMINAL: {
            'focused': 'textContent',
            'unfocused': 'textContent',
            'basicWhereAmI': 'label + readOnly + pause + textRole + pause + textContent + anyTextSelection + ' + MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + pause + textRole + pause + textContentWithAttributes + anyTextSelection + ' + MNEMONIC
            },
        Atspi.Role.TEXT: {
            'focused': 'labelOrName + readOnly + textRole + pause + textIndentation + (currentLineText or placeholderText) + allTextSelection',
            'unfocused': 'labelOrName + readOnly + textRole + pause + textIndentation + (currentLineText or placeholderText) + allTextSelection + ' + MNEMONIC,
            'basicWhereAmI': 'labelOrName + readOnly + textRole + pause + (textContent or placeholderText) + anyTextSelection + pause + ' + MNEMONIC,
            'detailedWhereAmI': 'labelOrName + readOnly + textRole + pause + (textContentWithAttributes or placeholderText) + anyTextSelection + pause + ' + MNEMONIC
            },
        Atspi.Role.TOGGLE_BUTTON: {
            'focused': 'expandableState or toggleState',
            'unfocused': 'labelOrName + roleName + (expandableState or toggleState) + availability + ' + MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelOrName + roleName + (expandableState or toggleState)'
            },
        Atspi.Role.TOOL_BAR: {
            'focused': 'labelAndName + roleName',
            'unfocused': 'labelAndName + roleName',
            },
        Atspi.Role.TOOL_TIP: {
            'focused': 'leaving or roleName',
            'unfocused': 'roleName + labelAndName',
            'basicWhereAmI': 'roleName + labelAndName'
            },
        Atspi.Role.TREE: {
            'focused': 'labelAndName + roleName',
            'unfocused': 'labelAndName + roleName',
            },
        Atspi.Role.TREE_ITEM: {
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
        Atspi.Role.ALERT: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]))'
            },
        Atspi.Role.ANIMATION: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName + (description and space(": ") + description)))]',
            },
        Atspi.Role.APPLICATION: {
            'focused':   '[Component(obj, asString(name + roleName))]',
            'unfocused': '[Component(obj, asString(name + roleName))]',
            },
        Atspi.Role.ARTICLE: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]\
                             + (childWidget and ([Region(" ")] + childWidget))))'
            },
        'ROLE_ARTICLE_IN_FEED': {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelOrName + roleName))]))'
            },
        #Atspi.Role.ARROW: 'default'
        Atspi.Role.BLOCK_QUOTE: {
            'unfocused': BRAILLE_TEXT + ' + (roleName and [Region(" " + asString(roleName + nestingLevel))])',
            },
        Atspi.Role.CANVAS: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText + imageDescription) or name) + roleName))]'
            },
        Atspi.Role.CHECK_BOX: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName),\
                                     indicator=asString(checkedState))]'
            },
        Atspi.Role.CHECK_MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(label + displayedText + roleName + availability) + asString(accelerator),\
                                     indicator=asString(checkedState))]'
            },
        Atspi.Role.COLUMN_HEADER: {
            'unfocused': '[Component(obj,\
                                     asString(((substring and currentLineText) or labelAndName) + roleName + sortOrder))]',
            },
        Atspi.Role.COMBO_BOX: {
            'unfocused': '[Component(obj, asString(labelOrName + value + roleName), \
                                     labelOrName and (len(asString(labelOrName)) + 1) or 0)]'
            },
        Atspi.Role.DESCRIPTION_TERM: {
            'unfocused': BRAILLE_TEXT + ' + ([Region(" " + asString(termValueCount))])',
            },
        #Atspi.Role.DESKTOP_ICON: 'default'
        Atspi.Role.DIAL: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + value + roleName + required))]'
            },
        Atspi.Role.DIALOG: {
            'unfocused': '[Component(obj, asString(labelOrName + roleName + (unrelatedLabelsOrDescription)))]'
            },
        #Atspi.Role.DIRECTORY_PANE: 'default'
        Atspi.Role.DOCUMENT_FRAME: {
            'focused': '[Text(obj, asString(placeholderText), asString(eol), startOffset, endOffset)]\
                          + (required and [Region(" " + asString(required))])\
                          + (readOnly and [Region(" " + asString(readOnly))])',
            'unfocused': BRAILLE_TEXT
            },
        Atspi.Role.DOCUMENT_WEB: {
            'focused': '[Text(obj, asString(placeholderText), asString(eol), startOffset, endOffset)]\
                          + (required and [Region(" " + asString(required))])\
                          + (readOnly and [Region(" " + asString(readOnly))])',
            'unfocused': BRAILLE_TEXT
            },
        Atspi.Role.ENTRY: {
            'unfocused': BRAILLE_TEXT
            },
        Atspi.Role.FORM: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]))'
            },
        Atspi.Role.FRAME: {
            'focused':   '[Component(obj,\
                                     asString(labelOrName + roleName + alertAndDialogCount))]',
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName + alertAndDialogCount))]',
            },
        Atspi.Role.HEADING: {
            'unfocused': '[Text(obj, asString(placeholderText), "", startOffset, endOffset)]\
                          + [Region(" " + asString(roleName))]'
            },
        #Atspi.Role.HTML_CONTAINER: 'default'
        Atspi.Role.ICON: {
            'unfocused': '[Component(obj,\
                                     asString(((label + displayedText + imageDescription) or name) + roleName))]'
            },
        Atspi.Role.IMAGE: {
            'focused':   '[Component(obj,\
                                     asString(labelAndName + value + roleName + required))]',
            'unfocused': '[Component(obj,\
                                     asString(labelAndName + value + roleName + required))]',
            },
        Atspi.Role.LABEL: {
            'unfocused': BRAILLE_TEXT
            },
        Atspi.Role.LINK: {
            'unfocused': '[Link(obj, asString(name or displayedText))] \
                        + (roleName and [Region(" " + asString(roleName))])',
        },
        Atspi.Role.LIST: {
            'unfocused': '[Component(obj,\
                                     asString(label + focusedItem + roleName),\
                                     asString(label) and (len(asString(label)) + 1) or 0)]'
        },
        Atspi.Role.LIST_BOX: {
            'unfocused': '[Component(obj,\
                                     asString(label + focusedItem + roleName),\
                                     asString(label) and (len(asString(label)) + 1) or 0)]'
        },
        Atspi.Role.LIST_ITEM: {
            'focused':   '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj,\
                                     asString(label + displayedText + expandableState + roleName + availability) + asString(accelerator), indicator=asString(checkedStateIfCheckable))] \
                          + (nestingLevel and [Region(" " + asString(nestingLevel))])\
                          + (listBoxItemWidgets and ([Region(" ")] + listBoxItemWidgets))))',
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelOrName + expandableState))]\
                              + (nestingLevel and [Region(" " + asString(nestingLevel))])\
                              + (listBoxItemWidgets and ([Region(" ")] + listBoxItemWidgets))))',
            },
        Atspi.Role.MENU: {
            'focused':   '[Component(obj,\
                                     asString(labelOrName + roleName + availability) + asString(accelerator))]',
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName))]',
            },
        #Atspi.Role.MENU_BAR: 'default'
        Atspi.Role.MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + expandableState + availability) + asString(accelerator),\
                                     indicator=asString(checkedStateIfCheckable))]'
            },
        Atspi.Role.NOTIFICATION: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]))'
            },
        Atspi.Role.PAGE: {
            'unfocused': BRAILLE_TEXT
            },
        #Atspi.Role.OPTION_PANE: 'default'
        Atspi.Role.PAGE_TAB: {
            'focused':   '[Component(obj,\
                                     asString(labelOrName + roleName + availability) + asString(accelerator))]',
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName))]'
            },
        #Atspi.Role.PAGE_TAB_LIST: 'default'
        Atspi.Role.PANEL: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelAndName + roleName))]\
                             + (childWidget and ([Region(" ")] + childWidget))))'
            },
        Atspi.Role.PARAGRAPH: {
            'unfocused': BRAILLE_TEXT
            },
        Atspi.Role.PASSWORD_TEXT: {
            'unfocused': BRAILLE_TEXT
            },
        Atspi.Role.PROGRESS_BAR: {
            'unfocused': '(progressBarValue and \
                           [Component(obj, asString(labelAndName + progressBarValue + roleName + progressBarIndex))]) \
                           or []'
            },
        Atspi.Role.PUSH_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString((labelAndName or description) + expandableState + roleName))]'
            },
        Atspi.Role.RADIO_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString((labelOrName or description) + roleName),\
                                     indicator=asString(radioState))]'
            },
        Atspi.Role.RADIO_MENU_ITEM: {
            'focused':   '[Component(obj,\
                                     asString((labelOrName or description) + roleName + availability)\
                                     + asString(accelerator),\
                                     indicator=asString(radioState))]',
            'unfocused': '[Component(obj,\
                                     asString(labelOrName or description)\
                                     + asString(accelerator),\
                                     indicator=asString(radioState))]'
            },
        Atspi.Role.ROW_HEADER: {
            'unfocused': '[Component(obj,\
                                     asString(((substring and currentLineText) or labelAndName) + roleName + sortOrder))]',
            },
        Atspi.Role.SCROLL_BAR: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + value + roleName + required))]'
            },
        Atspi.Role.SCROLL_PANE: {
            'unfocused': 'asPageTabOrScrollPane'
            },
        Atspi.Role.SECTION: {
            'unfocused': BRAILLE_TEXT
            },
        #'REAL_ROLE_SCROLL_PANE': 'default'
        Atspi.Role.SLIDER: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + value + roleName + required + invalid))]'
            },
        Atspi.Role.SPIN_BUTTON: {
            'unfocused': '[Text(obj, asString(label), asString(eol))]\
                          + (required and [Region(" " + asString(required))] or [])\
                          + (readOnly and [Region(" " + asString(readOnly))] or [])'
            },
        Atspi.Role.STATUS_BAR: {
            'unfocused': '[Component(obj, asString(labelOrName + roleName))]\
                              + [Region(" ")] + statusBar',
            },
        'ROLE_SWITCH' : {
            'unfocused': '[Component(obj,\
                                     asString((labelOrName or description) + roleName),\
                                     indicator=asString(switchState))]'
            },
        #Atspi.Role.SPLIT_PANE: 'default'
        #Atspi.Role.TABLE: 'default'
        Atspi.Role.TABLE_CELL: {
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
        #Atspi.Role.TABLE_COLUMN_HEADER: 'default'
        #Atspi.Role.TABLE_ROW_HEADER: 'default'
        Atspi.Role.TEAROFF_MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(roleName))]'
            },
        Atspi.Role.TERMINAL: {
            'unfocused': '[Text(obj)]'
            },
        Atspi.Role.TEXT: {
            'unfocused': BRAILLE_TEXT
            },
        Atspi.Role.TOGGLE_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString((labelOrName or description) + expandableState + roleName),\
                                     indicator=asString(toggleState))]'
            },
        Atspi.Role.TOOL_BAR: {
            'unfocused': '[Component(obj, asString(labelOrName + roleName))]',
            },
        Atspi.Role.TREE: {
            'unfocused': '[Component(obj, asString(labelOrName + roleName))]',
            },
        Atspi.Role.TREE_ITEM: {
            'unfocused': '((substring and ' + BRAILLE_TEXT + ')\
                          or ([Component(obj, asString(labelOrName + expandableState))]\
                              + (nodeLevel and [Region(" " + asString(nodeLevel))])))',
            },
        #Atspi.Role.TREE: 'default'
        #Atspi.Role.TREE_TABLE: 'default'
        #Atspi.Role.WINDOW: 'default'
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
        Atspi.Role.CANVAS: {
            'unfocused': 'roleName + positionInSet',
        },
        Atspi.Role.CHECK_BOX: {
            'focused': 'checkedState',
            'unfocused': 'roleName + checkedState + required + invalid + availability',
        },
        Atspi.Role.CHECK_MENU_ITEM: {
            'focused': 'checkedState',
            'unfocused': 'roleName + checkedState + availability + positionInSet',
        },
        Atspi.Role.COMBO_BOX: {
            'focused': 'expandableState',
            'unfocused': 'roleName + positionInSet',
        },
        Atspi.Role.DIAL: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage + required + invalid + availability',
        },
        Atspi.Role.ENTRY: {
            'unfocused': 'roleName + readOnly + required + invalid + availability',
        },
        Atspi.Role.HEADING: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState',
        },
        Atspi.Role.ICON: {
            'unfocused': 'roleName + positionInSet',
        },
        Atspi.Role.LINK: {
            'focused': 'expandableState',
            'unfocused': 'roleName + visitedState + expandableState',
        },
        Atspi.Role.LIST: {
            'unfocused': 'roleName + multiselectableState',
        },
        Atspi.Role.LIST_BOX: {
            'unfocused': 'roleName + multiselectableState',
        },
        Atspi.Role.LIST_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState + positionInSet',
        },
        Atspi.Role.MENU_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState + availability + positionInSet',
        },
        Atspi.Role.PAGE_TAB: {
            'unfocused': 'roleName + positionInSet',
        },
        Atspi.Role.PROGRESS_BAR: {
            'focused': 'progressBarValue',
            'unfocused': 'roleName + progressBarValue'
        },
        Atspi.Role.PUSH_BUTTON: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState + availability',
        },
        Atspi.Role.RADIO_BUTTON: {
            'focused': 'radioState',
            'unfocused': 'roleName + radioState + availability + positionInSet',
        },
        Atspi.Role.RADIO_MENU_ITEM: {
            'focused': 'radioState',
            'unfocused': 'roleName + checkedState + availability + positionInSet',
        },
        Atspi.Role.SCROLL_BAR: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage',
        },
        Atspi.Role.SLIDER: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage + required + invalid + availability',
        },
        Atspi.Role.SPIN_BUTTON: {
            'focused': 'percentage',
            'unfocused': 'roleName + availability + percentage + required + invalid',
        },
        Atspi.Role.SPLIT_PANE: {
            'focused': 'percentage',
            'unfocused': 'roleName + percentage + availability',
        },
        'ROLE_SWITCH': {
            'focused': 'switchState',
            'unfocused': 'roleName + switchState + availability',
        },
        Atspi.Role.TABLE_CELL: {
            'focused': 'expandableState',
            'unfocused': 'roleName + expandableState',
        },
        Atspi.Role.TABLE_ROW: {
            'focused': 'expandableState',
        },
        Atspi.Role.TEXT: {
            'unfocused': 'roleName + readOnly + required + invalid + availability',
        },
        Atspi.Role.TOGGLE_BUTTON: {
            'focused': 'expandableState or toggleState',
            'unfocused': 'roleName + (expandableState or toggleState) + availability',
        },
        Atspi.Role.TREE_ITEM: {
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
        - role: the role, such as Atspi.Role.TEXT
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
        - role: the role, such as Atspi.Role.TEXT
        - formatType: the type of formatting, such as
          'focused', 'basicWhereAmI', etc.
        """
        try:
            return self[args['mode']][args['role']][args['formatType']]
        except:
            pass

        if args.get('formatType') == 'ancestor':
            try:
                return self[args['mode']][args['role']]['focused']
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
