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
from orca_i18n import _ # for gettext support

_debugLevel = debug.LEVEL_FINEST
_appName = None
_statusBar = None
_lastAttributeString = ""

def whereAmI(obj, context, doubleClick, orcaKey):
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

    if (not obj) or (not context):
        return False

    debug.println(_debugLevel,
        "whereAmI: \
       \n  context= %s \
       \n  label=%s \
       \n  name=%s \
       \n  role=%s \
       \n  mnemonics=%s \
       \n  parent label= %s \
       \n  parent name=%s \
       \n  parent role=%s \
       \n  double-click=%s \
       \n  orca-key=%s" % \
        (context,
         _getObjLabel(obj),
         _getObjName(obj),
         obj.role,
         orca_state.activeScript.getAcceleratorAndShortcut(obj),
         _getObjLabel(obj.parent),
         _getObjName(obj.parent),
         obj.parent.role,
         doubleClick,
         orcaKey))

    global _appName
    _appName = context[0]
    role = obj.role

    if orcaKey:
        # Handle the Orca modifier key being pressed.
        if _getAppName() == "soffice.bin":
            top = orca_state.activeScript.getTopLevel(obj)
            if top and top.name.endswith(" Calc"):
                _handleCalcOrcaKey(obj, doubleClick)
            else:
                _handleOrcaKey(obj, doubleClick)
        else:
            _handleOrcaKey(obj, doubleClick)


    elif role == rolenames.ROLE_CHECK_BOX:
        _speakCheckBox(obj, doubleClick)


    elif role == rolenames.ROLE_RADIO_BUTTON:
        _speakRadioButton(obj, doubleClick)


    elif role == rolenames.ROLE_COMBO_BOX:
        _speakComboBox(obj, doubleClick)
        

    elif role == rolenames.ROLE_SPIN_BUTTON:
        _speakSpinButton(obj, doubleClick)
        

    elif role == rolenames.ROLE_PUSH_BUTTON:
        _speakPushButton(obj, doubleClick)


    elif role == rolenames.ROLE_SLIDER:
        _speakSlider(obj, doubleClick)
        

    elif role == rolenames.ROLE_MENU or \
         role == rolenames.ROLE_MENU_ITEM or \
         role == rolenames.ROLE_CHECK_MENU or \
         role == rolenames.ROLE_CHECK_MENU_ITEM or \
         role == rolenames.ROLE_RADIO_MENU or \
         role == rolenames.ROLE_RADIO_MENU_ITEM:
        _speakMenuItem(obj, doubleClick)


    elif role == rolenames.ROLE_PAGE_TAB:
        _speakPageTab(obj, doubleClick)
        

    elif role == rolenames.ROLE_TEXT or \
         role == rolenames.ROLE_TERMINAL:
        _speakText(obj, doubleClick)


    elif role == rolenames.ROLE_TABLE_CELL:
        if _getAppName() == "soffice.bin":
            _speakCalcTableCell(obj, doubleClick)
        else:
            _speakTableCell(obj, doubleClick)
            

    elif role == rolenames.ROLE_PARAGRAPH:
        _speakParagraph(obj, doubleClick)

    return True


def _getAppName():
    """
    Returns the application name.
    """
    global _appName
    return _appName


def _speakCheckBox(obj, doubleClick):
    """Checkboxes present the following information
    (an example is 'Enable speech, checkbox checked, Alt E'):
    1. label
    2. role
    3. state
    4. mnemonic (i.e. Alt plus the underlined letter), if any
    """    
    utterances = []
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


def _speakRadioButton(obj, doubleClick):
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
    utterances = []
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


def _speakComboBox(obj, doubleClick):
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
    utterances = []
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


def _speakSpinButton(obj, doubleClick):
    """
    Spin Buttons present the following information (an example is
    'Scale factor: spin button, 4.00, Alt F'):
    
    1. label
    2. role
    3. current value
    4. mnemonic (i.e. Alt plus the underlined letter), if any
    """
    utterances = []
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


def _speakPushButton(obj, doubleClick):
    """
    Push Buttons present the following information (an example is
    'Apply button, Alt A'):
    
    1. label
    2. role
    3. mnemonic (i.e. Alt plus the underlined letter), if any
    """
    utterances = []
    text = _("%s") % _getObjLabelAndName(obj)
    utterances.append(text)
    
    text = _("%s") % rolenames.getSpeechForRoleName(obj)
    utterances.append(text)
    
    text = _("%s") % _getObjMnemonic(obj)
    utterances.append(text)
    
    debug.println(_debugLevel, "push button utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)


def _speakSlider(obj, doubleClick):
    """
    Sliders present the following information (examples include
    'Pitch slider, 5.0, 56%'; 'Volume slider, 9.0, 100%'):
    
    1. label
    2. role
    3. value
    4. percentage (if possible)
    5. mnemonic (i.e. Alt plus the underlined letter), if any
    """
    utterances = []
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


def _speakMenuItem(obj, doubleClick):
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
    utterances = []
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


def _speakPageTab(obj, doubleClick):
    """
    Tabs in a Tab List present the following information (an example
    is 'Tab list, braille page, item 2 of 5'):
    
    1. role
    2. label + 'page'
    3. relative position
    4. mnemonic (i.e. Alt plus the underlined letter), if any
    """
    utterances = []
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


def _speakText(obj, doubleClick):
    """
    Text boxes present the following information (an example is
    'Source display: text, blank, Alt O'):
    
    1. label, if any
    2. role
    3. contents
        A. if no text on the current line is selected, the current line
        B. if text is selected on the current line, that text, followed
        attibute information before  (bold "text")
        by 'selected' (single press) 
        C. if the current line is blank/empty, 'blank'
    4. mnemonic (i.e. Alt plus the underlined letter), if any

    Gaim, gedit, OpenOffice Writer and Terminal
    """
    utterances = []
    text = _("%s") % _getObjLabel(obj)
    utterances.append(text)
    
    text = _("%s") % rolenames.getSpeechForRoleName(obj)
    utterances.append(text)

    [textContents, startOffset, endOffset, selected] = \
                   _getTextContents(obj, doubleClick)
    if doubleClick:
        # Speak character attributes.
        textContents = \
            _insertAttributes(obj, startOffset, endOffset, textContents)
        savedStyle = settings.verbalizePunctuationStyle
        settings.verbalizePunctuationStyle = settings.PUNCTUATION_STYLE_SOME
    
    text = _("%s") % textContents
    utterances.append(text)
    debug.println(_debugLevel, "first text utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)

    if doubleClick:
        verbalizePunctuationStyle = savedStyle
    
    utterances = []
    if selected:
        text = _("%s") % "selected"
        utterances.append(text)

    text = _("%s") % _getObjMnemonic(obj)
    utterances.append(text)
    
    debug.println(_debugLevel, "text utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)


def _speakCalcTableCell(obj, doubleClick):
    """
    Given the nature of OpenOffice Calc, Orca should override the
    default KP_Enter behavior when the item with focus is a cell
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
    
    utterances = []
    utterances.append(_("Cell"))
    
    table = obj.parent.table
    text = _("column %d") % (table.getColumnAtIndex(obj.index) + 1)
    utterances.append(text)
    text = _("row %d") % (table.getRowAtIndex(obj.index) + 1)
    utterances.append(text)
    
    text = obj.text.getText(0, -1)
    utterances.append(text)

    debug.println(_debugLevel, "calc table cell utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)
        

def _speakTableCell(obj, doubleClick):
    """
    Tree Tables present the following information (an example is
    'Tree table, Mike Pedersen, item 8 of 10, tree level 2'):
    
    1. label, if any
    2. role
    3. current row (regardless of speak cell/row setting)
    4. relative position
    5. if expandable/collapsible: expanded/collapsed
    6. if applicable, the level
    
    Nautilus and Gaim
    """
    
    # Speak the first two items (and possibly the position)
    utterances = []
    if obj.parent.role == rolenames.ROLE_TABLE_CELL:
        obj = obj.parent
    parent = obj.parent
        
    text = _("%s") % _getObjLabel(obj)
    utterances.append(text)
    
    text = _("%s") % rolenames.getSpeechForRoleName(obj)
    utterances.append(text)
    debug.println(_debugLevel, "first table cell utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)
    
    utterances = []
    if doubleClick:
        table = parent.table
        row = table.getRowAtIndex(orca_state.locusOfFocus.index)
        text = _("row %d of %d") % ((row+1), parent.table.nRows)
        utterances.append(text)
        speech.speakUtterances(utterances)
        
    # Speak the current row
    utterances = _getTableRow(obj)
    debug.println(_debugLevel, "second table cell utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)
    
    # Speak the remaining items.
    utterances = []
    
    if not doubleClick:
        table = parent.table
        if not table:
            debug.println(_debugLevel, "??? parent=%s" % parent.role)
            return

        row = table.getRowAtIndex(orca_state.locusOfFocus.index)
        text = _("row %d of %d") % ((row+1), parent.table.nRows)
        utterances.append(text)

    if obj.state.count(atspi.Accessibility.STATE_EXPANDABLE):
        if obj.state.count(atspi.Accessibility.STATE_EXPANDED):
            text = _("expanded")
        else:
            text = _("collapsed")
            utterances.append(text)
            
    level = orca_state.activeScript.getNodeLevel(orca_state.locusOfFocus)
    if level >= 0:
        utterances.append(_("tree level %d") % (level + 1))

    debug.println(_debugLevel, "third table cell utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)


def _speakParagraph(obj, doubleClick):
    """
    OpenOffice Calc cells have the role "paragraph" when
    they are being edited.
    """
    if _getAppName() == "soffice.bin":
        top = orca_state.activeScript.getTopLevel(obj)
        if top and top.name.endswith(" Calc"):
            _speakCalc(obj, doubleClick)

        elif top and top.name.endswith(" Writer"):
            _speakText(obj, doubleClick)



def _speakCalc(obj, doubleClick):
    """
    Speak a OpenOffice Calc cell.
    """
    utterances = []
    utterances.append(_("Cell"))
    
    # No way to get cell coordinates?
    
    [textContents, startOffset, endOffset, selected] = \
        _getTextContents(obj, doubleClick)
    text = _("%s") % textContents
    utterances.append(text)
    if selected:
        text = _("%s") % "selected"
        utterances.append(text)
        
    debug.println(_debugLevel, "editable table cell utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)
            

def _getObjName(obj):
    """
    Returns the name to speak for an object.
    """
    text = ""
    name = orca_state.activeScript.getDisplayedText(obj)
    if not name:
        name = obj.description

    if name and name != "None":
        text = _("%s") % name
    # debug.println(_debugLevel, "%s name=<%s>" % (obj.role, text))
    return text


def _getObjLabel(obj):
    """
    Returns the label to speak for an object.
    """
    text = ""
    label = orca_state.activeScript.getDisplayedLabel(obj)
    
    if label and label != "None":
        text = _("%s") % label
    # debug.println(_debugLevel, "%s label=<%s>" % (obj.role, text))
    return text


def _getObjLabelAndName(obj):
    """
    Returns the object label plus the object name.
    """
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
    index = 0
    total = 0

    debug.println(_debugLevel, "obj=%s, count=%d, name=%s" % \
                  (obj.role, obj.childCount, name))
    
    for i in range(0, obj.childCount):
        next = _getObjName(obj.child(i))
        if next == "" or next == "Empty" or next == "separator":
            continue
        
        index += 1
        total += 1

        if next == name:
            position = index


    if position >= 0:
        text = _("item %d of %d") % (position, total)

    return text


def _getObjMnemonic(obj):
    """
    Returns the accellerator and/or shortcut for the object,
    if either exists.
    """
    list = orca_state.activeScript.getAcceleratorAndShortcut(obj)

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
    list = orca_state.activeScript.getAcceleratorAndShortcut(obj)

    text = ""
    if list[0]:
        text = _("%s") % list[0]

    return text


def _getObjShortcut(obj):
    """
    Returns the shortcut for the object, if it exists.
    """
    list = orca_state.activeScript.getAcceleratorAndShortcut(obj)

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
    utterances = []
    
    parent = obj.parent
    table = parent.table
    if not table:
        debug.println(_debugLevel, "??? parent=%s" % parent.role)
        return []
    
    row = parent.table.getRowAtIndex(obj.index)
    
    for i in range(0, parent.table.nColumns):
        cell = parent.table.getAccessibleAt(row, i)
        acc = atspi.Accessible.makeAccessible(cell)
        utterances.append(_getTableCell(acc))

    debug.println(_debugLevel, "row=<%s>" % utterances)
    return utterances


def _getTableCell(obj):
    """
    Get the speech utterances for a single table cell. 
    """

    # Don't speak check box cells that area not checked.
    notChecked = False
    action = obj.action
    if action:
        for i in range(0, action.nActions):
            if action.getName(i) == "toggle":
                obj.role = rolenames.ROLE_CHECK_BOX
                if not obj.state.count(atspi.Accessibility.STATE_CHECKED):
                    notChecked = True
                obj.role = rolenames.ROLE_TABLE_CELL
                break

    if notChecked:
        return ""
    
    descendant = orca_state.activeScript.getRealActiveDescendant(obj)
    text = orca_state.activeScript.getDisplayedText(descendant)

    # For Evolution mail header list.
    if _getAppName().startswith("evolution") and text == "Status":
        text = _("Read")
        
    debug.println(_debugLevel, "cell=<%s>" % text)
    return text


def _getCheckBox(obj):
    """
    Returns utterences for a check box.
    """
    utterances = []

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

    return utterances


def _getTextContents(obj, doubleClick):
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
    startSelOffset = -1
    endSelOffset = -1

    nSelections = textObj.getNSelections()
    debug.println(_debugLevel,
        "_getTextContents: caretOffset=%d, nSelections=%d" % \
        (caretOffset, nSelections))

    if nSelections:
        selected = True
        for i in range(0, nSelections):
            [startOffset, endOffset] = textObj.getSelection(i)
            
            debug.println(_debugLevel,
                "_getTextContents: selection start=%d, end=%d" % \
                (startOffset, endOffset))
            
            selectedText = textObj.getText(startOffset, endOffset)
            debug.println(_debugLevel,
                "_getTextContents: selected text=<%s>" % selectedText)

            if i > 0:
                textContents += " "
            textContents += selectedText

    else:
        # Get the line containing the caret
        #
        [line, startOffset, endOffset] = textObj.getTextAtOffset(
            textObj.caretOffset, atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
        debug.println(_debugLevel, \
            "_getTextContents: len=%d, start=%d, end=%d, line=<%s>" % \
            (len(line), startOffset, endOffset, line))

        if len(line):
            line = orca_state.activeScript.adjustForRepeats(line)
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

    return [textContents, startOffset, endOffset, selected]


def _insertAttributes(obj, startOffset, endOffset, line):
    """
    Adjust line to include attribute information.
    """
    text = obj.text
    if not text:
        return ""
    
    newLine = ""
    textOffset = startOffset

    for i in range(0, len(line)):
        attribs =_getAttributesForChar(text, textOffset, line, i)
        debug.println(_debugLevel,
                      "line attribs <%s>" % (attribs))
        if attribs:
            newLine += " ; "
            newLine += attribs
            newLine += " "

        newLine += line[i]
        textOffset += 1

    debug.println(_debugLevel, "newLine: <%s>" % (newLine))
    return newLine


def _getAttributesForChar(text, textOffset, line, lineIndex):

    global _lastAttributeString
    keys = [ "style", "weight", "underline" ]

    attribStr = ""

    charAttributes = text.getAttributes(textOffset)
    
    if charAttributes[0]:
        charDict = _stringToDictionary(charAttributes[0])
        debug.println(_debugLevel,
                      "charDict: %s" % (charDict))

        for key in keys:
            if charDict.has_key(key):
                attribute = charDict[key]
                if attribute:
                    # If it's the 'weight' attribute and greater than 400, just
                    # speak it as bold, otherwise speak the weight.
                    #
                    if key == "weight" and int(attribute) > 400:
                        attribStr += " "
                        attribStr += _("bold")
                        
                    elif key == "underline":
                        if attribute != "none":
                            attribStr += " "
                            attribStr += key
                        
                    elif key == "style":
                        if attribute != "normal":
                            attribStr += " "
                            attribStr += attribute
                    else:
                        attribStr += " "
                        attribStr += (key + " " + attribute)

        debug.println(_debugLevel,
                      "char <%s>: %s" % (line[lineIndex], attribStr))

    # Only return attributes for the beginning of an attribute run.
    if attribStr != _lastAttributeString:
        _lastAttributeString = attribStr
        return attribStr
    else:
        return ""


def _stringToDictionary(str):
    """
    Converts a string of text attribute tokens of the form
    <key>:<value>; into a dictionary of keys and values.
    Text before the colon is the key and text afterwards is the
    value. If there is a final semi-colon, then it's ignored.
    """
    dictionary = {}
    allTokens = str.split(";")
    for token in allTokens:
        item = token.split(":")
        if len(item) == 2:
            item[0] = _removeLeadingSpaces(item[0])
            item[1] = _removeLeadingSpaces(item[1])
            dictionary[item[0]] = item[1]
            
    return dictionary


def _removeLeadingSpaces(str):
    """
    Returns a string with the leading space characters removed.
    """
    newStr = ""
    leadingSpaces = True
    for i in range(0, len(str)):
        if str[i] == " ":
            if leadingSpaces:
                continue
        else:
            leadingSpaces = False

        newStr += str[i]

    return newStr

def _handleOrcaKey(obj, doubleClick):
    """
    Handle the Orca modifier key being pressed.

    When Insert + KP_Enter is pressed a single time, Orca will speak
    and display the following information:
    
    1. The contents of the title bar of the application main window
    2. If in a dialog box within an application, the contents of the
    title bar of the dialog box.
    3. Orca will pause briefly between these two pieces of information
    so that the speech user can distinguish each.
    """
    global _statusBar
    utterances = []

    list = _getFrameAndDialog(obj)
    if doubleClick:
        if list[0]:
            _statusBar = None
            _getStatusBar(list[0])
            if _statusBar:
                _speakStatusBar()
    else:
        if list[0]:
            text = _("%s") % _getObjLabelAndName(list[0])
            utterances.append(text)
        if list[1]:
            text = _("%s") % _getObjLabelAndName(list[1])
            utterances.append(text)
            
        debug.println(_debugLevel, "titlebar utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)


def _handleCalcOrcaKey(obj, doubleClick):
    """
    Handle the Orca modifier key being pressed.

    Calc-Specific Handling: If Insert+KP_Enter is pressed a single time
    while focus is on a cell within OpenOffice Calc, Orca will speak the
    following information:

    1. The contents of the title bar of the application main window
    2. The title of the current worksheet

    Note that if the application with focus is Calc, but a cell does not
    have focus, the default behavior should be used.
    """
    global _statusBar
    utterances = []

    list = _getCalcFrameAndSheet(obj)
    if doubleClick:
        if list[0]:
            _statusBar = None
            _getStatusBar(list[0])
            if _statusBar:
                _speakCalcStatusBar()
    else:
        if list[0]:
            text = _("%s") % _getObjLabelAndName(list[0])
            utterances.append(text)
        if list[1]:
            text = _("%s") % _getObjLabelAndName(list[1])
            utterances.append(text)
            
        debug.println(_debugLevel, "Calc titlebar and sheet utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)


def _getFrameAndDialog(obj):
    """
    Returns the frame and (possibly) the dialog containing
    the object.
    """
    list = [None, None]

    parent = obj.parent
    while parent and (parent.parent != parent):
        #debug.println(_debugLevel, "_getFrameAndDialog: parent=%s, %s" % \
        #             (parent.role, _getObjLabelAndName(parent)))
        if parent.role == rolenames.ROLE_FRAME:
            list[0] = parent
        if parent.role == rolenames.ROLE_DIALOG:
            list[1] = parent
        parent = parent.parent

    return list


def _getCalcFrameAndSheet(obj):
    """
    Returns the Calc frame and sheet
    """
    list = [None, None]

    parent = obj.parent
    while parent and (parent.parent != parent):
        # debug.println(_debugLevel, "_getCalcFrameAndSheet: parent=%s, %s" % \
        #               (parent.role, _getObjLabelAndName(parent)))
        if parent.role == rolenames.ROLE_FRAME:
            list[0] = parent
        if parent.role == rolenames.ROLE_TABLE:
            list[1] = parent
        parent = parent.parent

    return list


def _getStatusBar(obj):
    """
    Gets the status bar.
    """
    global _statusBar
    if _statusBar:
        return

    # debug.println(_debugLevel, "_findStatusBar: ROOT=%s, %s" % \
    #               (obj.role, _getObjLabelAndName(obj)))
    
    managesDescendants = obj.state.count(\
        atspi.Accessibility.STATE_MANAGES_DESCENDANTS)
    if managesDescendants:
        return

    for i in range(0, obj.childCount):
        child = obj.child(i)
        # debug.println(_debugLevel, "_findStatusBar: child=%s, %s" % \
        #               (child.role, _getObjLabelAndName(child)))
        if child.role == rolenames.ROLE_STATUSBAR:
            _statusBar = child
            return
            
        if child.childCount > 0:
            _getStatusBar(child)
            

def _speakStatusBar():
    """
    Speaks the status bar.
    """
    global _statusBar
    if not _statusBar:
        return

    utterances = []

    if _statusBar.childCount == 0:
        text = _("%s") % _getObjName(_statusBar)
        utterances.append(text)
    else:
        for i in range(0, _statusBar.childCount):
            child = _statusBar.child(i)
            text = _("%s") % _getObjName(child)
            utterances.append(text)

    debug.println(_debugLevel, "statusbar utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)
    
    
def _speakCalcStatusBar():
    """
    Speaks the OpenOffice Calc statusbar.
    """
    global _statusBar
    if not _statusBar:
        return
    
    utterances = []
    for i in range(0, _statusBar.childCount):
        child = _statusBar.child(i)
        text = _("%s") % _getObjName(child)
        utterances.append(text)

    debug.println(_debugLevel, "Calc statusbar utterances=%s" % \
                  utterances)
    speech.speakUtterances(utterances)



