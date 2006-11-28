# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Speaks information about the current object of interest."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import string

import atspi
import chnames
import debug
import default
import input_event
import orca_prefs
import orca_state
import rolenames
import settings
import speech
import speechserver
import Accessibility
import math
import util


from orca_i18n import _ # for gettext support

_debugLevel = debug.LEVEL_FINEST


def whereAmI(obj, doubleClick):
    """
    Speaks information about the current object of interest, including
    the object itself, which window it is in, which application, which
    workspace, etc.

    The object of interest can vary depending upon the mode the user
    is using at the time. For example, in focus tracking mode, the
    object of interest is the object with keyboard focus. In review
    mode, the object of interest is the object currently being visited,
    whether it has keyboard focus or not.
    """

    parent = obj.parent
    role = obj.role
    utterances = []

    debug.println(_debugLevel,
        "whereAmI: label=%s name=%s, role=%s state=%s, mnemonics=%s" % \
        (_getObjLabel(obj),
         _getObjName(obj),
         rolenames.getSpeechForRoleName(obj),
         obj.getStateString(),
         util.getAcceleratorAndShortcut(obj)))


    if role == rolenames.ROLE_CHECK_BOX:
        """Checkboxes present the following information
        (an example is 'Enable speech, checkbox checked, Alt E'):
        1. label
        2. role
        3. state
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _getObjLabelAndName(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        if obj.state.count(atspi.Accessibility.STATE_CHECKED):
            text = _("checked")
        else:
            text = _("not checked")
        utterances.append(text)

        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "check box utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)


    elif role == rolenames.ROLE_RADIO_BUTTON:
        """
        Radio Buttons present the following information (an example is
        'Punctuation Level, Some, Radio button, selected, item 2 of 4, Alt M'):
        1. group name
        2. label
        3. role
        4. state
        5. relative position
        6. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % _getGroupLabel(obj)
        utterances.append(text)

        if doubleClick:
            text = _("%s") % _getPositionInGroup(obj)
            utterances.append(text)

        text = _("%s") % _getObjLabelAndName(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        if obj.state.count(atspi.Accessibility.STATE_CHECKED):
            text = _("checked")
        else:
            text = _("not checked")
        utterances.append(text)

        if not doubleClick:
            text = _("%s") % _getPositionInGroup(obj)
            utterances.append(text)

        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "radio button utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)


    elif role == rolenames.ROLE_COMBO_BOX:
        """
        Comboboxes present the following information (an example is
        'Speech system: combo box, GNOME Speech Services, item 1 of 1,
        Alt S'):
        1. label
        2. role
        3. current value
        4. relative position
        5. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % _getObjLabel(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        if doubleClick:
            # child(0) is the popup list
            name = _("%s") % _getObjName(obj)
            text = _("%s") % _getPositionInList(obj.child(0), name)
            utterances.append(text)

            utterances.append(name)
        else:
            name = _("%s") % _getObjName(obj)
            utterances.append(name)
            
            # child(0) is the popup list
            text = _("%s") % _getPositionInList(obj.child(0), name)
            utterances.append(text)

        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "combo box utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)
        

    elif role == rolenames.ROLE_SPIN_BUTTON:
        """
        Spin Buttons present the following information (an example is
        'Scale factor: spin button, 4.00, Alt F'):
        
        1. label
        2. role
        3. current value
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % _getObjLabelAndName(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        value = obj.value
        if value: 
            text = "%.1f" % value.currentValue
            utterances.append(text)

        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "spin button utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)


    elif role == rolenames.ROLE_PUSH_BUTTON:
        """
        Push Buttons present the following information (an example is
        'Apply button, Alt A'):
        
        1. label
        2. role
        3. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % _getObjLabelAndName(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "push button utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    elif role == rolenames.ROLE_SLIDER:
        """
        Sliders present the following information (examples include
        'Pitch slider, 5.0, 56%'; 'Volume slider, 9.0, 100%'):
        
        1. label
        2. role
        3. value
        4. percentage (if possible)
        5. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % _getObjLabel(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        values = _getSliderValues(obj)
        utterances.append(_("%s") % values[0])
        utterances.append(_("%s percent") % values[1])

        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "slider utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)
        

    elif role == rolenames.ROLE_MENU or \
         role == rolenames.ROLE_MENU_ITEM or \
         role == rolenames.ROLE_CHECK_MENU or \
         role == rolenames.ROLE_CHECK_MENU_ITEM:
        """
        Menu items present the following information (examples include
        'File menu, Open..., Control + O, item 2 of 20, O', 'File menu,
        Wizards Menu, item 4 of 20, W'):
        
        1. Name of the menu containing the item, followed by its role
        2. item name, followed by its role (if a menu) followed by its
        accelerator key, if any
        3. relative position
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % _getObjLabelAndName(obj.parent)
        utterances.append(text)

        if doubleClick:
            # parent is the page tab list
            name = _("%s") % _getObjName(obj)
            text = _("%s") % _getPositionInList(obj.parent, name)
            utterances.append(text)

        text = _("%s") % _getObjLabelAndName(obj)
        utterances.append(text)

        text = _("%s") % _getObjAccelerator(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        if not doubleClick:
            # parent is the page tab list
            name = _("%s") % _getObjName(obj)
            text = _("%s") % _getPositionInList(obj.parent, name)
            utterances.append(text)

        text = _("%s") % _getObjShortcut(obj)
        utterances.append(text)

        debug.println(_debugLevel, "menu item utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    elif role == rolenames.ROLE_PAGE_TAB:
        """
        Tabs in a Tab List present the following information (an example
        is 'Tab list, braille page, item 2 of 5'):
        
        1. role
        2. label + 'page'
        3. relative position
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        if doubleClick:
            text = _("%s page") % _getObjLabelAndName(obj)
            utterances.append(text)
            
            name = _("%s") % _getObjName(obj)
            text = _("%s") % _getPositionInList(obj.parent, name)
            utterances.append(text)
        else:
            name = _("%s") % _getObjName(obj)
            text = _("%s") % _getPositionInList(obj.parent, name)
            utterances.append(text)
            
            text = _("%s page") % _getObjLabelAndName(obj)
            utterances.append(text)
            
        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "page utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)
        

    elif role == rolenames.ROLE_TEXT or role == rolenames.ROLE_TERMINAL:
        """
        Text boxes present the following information (an example is
        'Source display: text, blank, Alt O'):
        
        1. label, if any
        2. role
        3. contents
            A. if no text on the current line is selected, the current line
            B. if text is selected on the current line, that text, followed
            by 'selected'
            C. if the current line is blank/empty, 'blank'
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """
        text = _("%s") % _getObjLabel(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        [textContents, selected] = _getTextContents(obj)
        text = _("%s") % textContents
        utterances.append(text)
        if selected:
            text = _("%s") % "selected"
            utterances.append(text)

        text = _("%s") % _getObjMnemonic(obj)
        utterances.append(text)

        debug.println(_debugLevel, "text utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)


    elif role == rolenames.ROLE_TABLE_CELL:
        """
        Tree Tables present the following information (an example is
        'Tree table, Mike Pedersen, item 8 of 10, tree level 2'):
        
        1. label, if any
        2. role
        3. current row (regardless of speak cell/row setting)
        4. relative position
        5. if expandable/collapsible: expanded/collapsed
        6. if applicable, the level
        """
        # Speak the first two items (and possibly the position)
        text = _("%s") % _getObjLabel(obj)
        utterances.append(text)

        text = _("%s") % rolenames.getSpeechForRoleName(obj)
        utterances.append(text)
        debug.println(_debugLevel, "table cell utterances 1=%s" % \
                      utterances)

        if doubleClick:
            table = parent.table
            row = table.getRowAtIndex(orca_state.locusOfFocus.index)
            text = _("row %d of %d") % ((row+1), parent.table.nRows)
            utterances.append(text)

        speech.speakUtterances(utterances)

        # Speak the current row
        utterances = _getTableRow(obj)
        debug.println(_debugLevel, "table cell utterances 2=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

        # Speak the remaining items.
        utterances = []

        if not doubleClick:
            table = parent.table
            row = table.getRowAtIndex(orca_state.locusOfFocus.index)
            text = _("row %d of %d") % ((row+1), parent.table.nRows)
            utterances.append(text)

        if obj.state.count(atspi.Accessibility.STATE_EXPANDABLE):
            if obj.state.count(atspi.Accessibility.STATE_EXPANDED):
                text = _("expanded")
            else:
                text = _("collapsed")
            utterances.append(text)

        level = util.getNodeLevel(orca_state.locusOfFocus)
        if level >= 0:
            utterances.append(_("tree level %d") % (level + 1))

        debug.println(_debugLevel, "table cell utterances 3=%s" % \
                      utterances)
        speech.speakUtterances(utterances)
        

    # OpenOffice Calc
        """
        Given the nature of OpenOffice Calc, Orca should override the
        default KP_Enter behavior when the item with focus is a cell
        within Calc. In this instance, the following information should
        be spoken/displayed:
        
        1. 'Cell'
        2. the cell coordinates
        3. the cell contents:
        A. if the cell is empty, 'blank'
        B. if the cell is being edited AND if some text within the
        cell is selected, the selected text followed by 'selected'
        C. otherwise, the full contents of the cell
        """

    return True


def _getObjName(obj):
    """
    Returns the name to speak for an object. This code is
    adapted from speechgenerator.py
    """
    text = ""
    name = util.getDisplayedText(obj)
    if not name:
        name = obj.description

    if name and name != "None":
        text = _("%s") % name
    debug.println(_debugLevel, "%s name=<%s>" % (obj.role, text))
    return text


def _getObjLabel(obj):
    """
    Returns the label to speak for an object. This code is
    adapted from speechgenerator.py
    """
    text = ""
    label = util.getDisplayedLabel(obj)
    
    if label and label != "None":
        text = _("%s") % label
    debug.println(_debugLevel, "%s label=<%s>" % (obj.role, text))
    return text


def _getObjLabelAndName(obj):

    name = _getObjName(obj)
    label = _getObjLabel(obj)
    if name != label:
        text = _("%s %s") % (label, name)
    else:
        text = _("%s") % label


    if obj.text:
        [string, startOffset, endOffset] = obj.text.getTextAtOffset(0,
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)

        debug.println(_debugLevel, "%s text=<%s>" % (obj.role, string))

    return text


def _getGroupLabel(obj):
    """
    Returns the label for a group of components.
    """

    text = ""
    labelledBy = None

    relations = obj.relations
    for relation in relations:
        if relation.getRelationType() ==  \
               atspi.Accessibility.RELATION_LABELLED_BY:
            labelledBy = atspi.Accessible.makeAccessible(relation.getTarget(0))
            break

    if labelledBy:
        text = _getObjLabelAndName(labelledBy)

    else:
        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent.role == rolenames.ROLE_PANEL:
                label = _getObjLabelAndName(parent)
                if label and label != "":
                    text = label
                    break
            parent = parent.parent

    return text


def _getPositionInGroup(obj):
    """
    Returns the relative position of an object in a group.
    """

    text = ""
    position = -1
    total = -1
    
    relations = obj.relations
    for relation in relations:
        if relation.getRelationType() == Accessibility.RELATION_MEMBER_OF:
            total = relation.getNTargets()
            for i in range(0, total):
                target = atspi.Accessible.makeAccessible(relation.getTarget(i))
                if target == obj:
                    position = total - i
                    break
    
    if position >= 0:
        text += _("item %d of %d") % (position, total)

    return text


def _getPositionInComboBox(obj, name):
    """
    Returns the relative position of an object in a combo box.
    """

    # The only child of a combo box is the popup menu
    return _getPositionInList(obj.child(0), name)

    

def _getPositionInList(obj, name):
    """
    Returns the relative position of an object in a list.
    """

    text = ""
    position = -1

    total = obj.childCount
    debug.println(_debugLevel, "obj=%s, count=%d, name=%s" % \
                  (obj.role, obj.childCount, name))
    for i in range(0, total):
        next = _getObjName(obj.child(i))
        debug.println(_debugLevel, "next=%s" % next)

        if next == name:
            position = i
            break

    if position >= 0:
        text = _("item %d of %d") % (position + 1, total)

    return text


def _getObjMnemonic(obj):
    """
    Returns the accellerator and/or shortcut for the object,
    if either exists.
    """

    list = util.getAcceleratorAndShortcut(obj)

    text = ""
    if not list[1]:
        text = _("%s") % list[0]
    else:
        text = _("%s %s") % (list[0], list[1])

    return text


def _getObjAccelerator(obj):
    """
    Returns the accelerator for the object, if it exists.
    """

    list = util.getAcceleratorAndShortcut(obj)

    text = ""
    if list[0]:
        text = _("%s") % list[0]

    return text

def _getObjShortcut(obj):
    """
    Returns the shortcut for the object, if it exists.
    """

    list = util.getAcceleratorAndShortcut(obj)

    text = ""
    if list[1]:
        text = _("%s") % list[1]

    return text


def _getSliderValues(obj):
    """
    Returns the slider's current value and percentage.
    """
    value = obj.value

    currentValue = "%.1f" % value.currentValue
    percent = value.currentValue / value.maximumValue * 100
    rounded = "%d" % round(percent, 5)

    debug.println(_debugLevel,
        "_getSliderValues: min=%f, cur=%f, max=%f, str=%s, percent=%s" % \
        (value.minimumValue, value.currentValue, value.maximumValue, \
         currentValue, rounded))
    
    return [currentValue, rounded]


def _getTableRow(obj):
    """Get the speech for a table cell row or a single table cell
    if settings.readTableCellRow is False.
    
    Arguments:
    - obj: the table
    - already_focused: False if object just received focus
    
    Returns a list of utterances to be spoken for the object.
    """
    
    _utterances = []
    
    parent = obj.parent
    row = parent.table.getRowAtIndex(obj.index)
    column = parent.table.getColumnAtIndex(obj.index)
    
    for i in range(0, parent.table.nColumns):
        accRow = parent.table.getAccessibleAt(row, i)
        cell = atspi.Accessible.makeAccessible(accRow)
        _utterances.extend(_getTableCell(cell))

    debug.println(_debugLevel, "row=<%s>" % _utterances)
    return _utterances


def _getTableCell(obj):
    """
    Get the speech utterances for a single table cell
    """

    _utterances = []

    action = obj.action
    if action:
        for i in range(0, action.nActions):
            if action.getName(i) == "toggle":
                obj.role = rolenames.ROLE_CHECK_BOX
                _utterances.append(_getCheckBox(obj))
                obj.role = rolenames.ROLE_TABLE_CELL
                break

    descendant = util.getRealActiveDescendant(obj)
    text = util.getDisplayedText(descendant)
    _utterances.append(text)
            
    return _utterances


def _getCheckBox(obj):
    """
    Returns utterences for a check box.
    """

    _utterances = []

    text = _getObjLabelAndName(obj)
    _utterances.append(text)
    
    text = _("%s") % rolenames.getSpeechForRoleName(obj)
    _utterances.append(text)
    
    if obj.state.count(atspi.Accessibility.STATE_CHECKED):
        text = _("checked")
    else:
        text = _("not checked")
    _utterances.append(text)

    text = _("%s") % _getObjMnemonic(obj)
    _utterances.append(text)

    return _utterances


def _getTextContents(obj):
    """
    Returns utterences for text.

    A. if no text on the current line is selected, the current line
    B. if text is selected on the current line, that text, followed
    by 'selected'
    C. if the current line is blank/empty, 'blank'
    """

    textObj = obj.text
    caretOffset = textObj.caretOffset
    textContents = ""
    selected = False

    nSelections = textObj.getNSelections()
    debug.println(_debugLevel,
        "_getTextContents: caretOffset=%d, nSelections=%d" % \
        (caretOffset, nSelections))

    if nSelections:
        selected = True
        for i in range(0, nSelections):
            [startSelOffset, endSelOffset] = textObj.getSelection(i)
            
            debug.println(_debugLevel,
                "_getTextContents: selection start=%d, end=%d" % \
                (startSelOffset, endSelOffset))
            
            selectedText = textObj.getText(startSelOffset, endSelOffset)
            debug.println(_debugLevel,
                "_getTextContents: selected text=<%s>" % selectedText)

            if i > 0:
                textContents += " "
            textContents += selectedText

    else:
        [line, caretOffset, startOffset] = util.getTextLineAtCaret(obj)
        debug.println(_debugLevel, \
            "_getTextContents: len=%d, start=%d, caret=%d, line=<%s>" % \
            (len(line), startOffset, caretOffset, line))

        if len(line):
            line = util.adjustForRepeats(line)
            textContents = line

        else:
            char = textObj.getTextAtOffset(caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_CHAR)
            debug.println(_debugLevel,
                "_getTextContents: character=<%s>, start=%d, end=%d" % \
                (char[0], char[1], char[2]))
            
            if char[0] == "\n" and startOffset == caretOffset \
                   and settings.speakBlankLines:
                textContents = (_("blank"))

    return [textContents, selected]
