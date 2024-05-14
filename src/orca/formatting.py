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

# If we were to adhere to the line-length requirements of 100 characters,
# this file would be even more cumbersome to look at than it already is.
# We shall respect the line-length requirements for all files that are not
# formatting.py.
# ruff: noqa: E501

import copy

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import object_properties

BRAILLE_TEXT = '[Text(obj, asString(labelOrName or placeholderText), asString(eol), startOffset, endOffset, caretOffset)]\
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
    # Formatting for braille.                                          #
    #                                                                  #
    ####################################################################

    'braille': {
        'prefix': {
# TODO - JD: Figure out why we are globally getting table and radio button group properties.
#
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
            'unfocused': '((substring and ' + BRAILLE_TEXT + ') \
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
        except Exception:
            pass

        if args.get('formatType') == 'ancestor':
            try:
                return self[args['mode']][args['role']]['focused']
            except Exception:
                pass

        if args.get('formatType') == 'detailedWhereAmI':
            try:
                return self[args['mode']][args['role']]['basicWhereAmI']
            except Exception:
                pass

        try:
            return self[args['mode']][args['role']]['unfocused']
        except Exception:
            pass


        try:
            return self[args['mode']]['default'][args['formatType']]
        except Exception:
            pass

        try:
            return self[args['mode']]['default']['unfocused']
        except Exception:
            return []
