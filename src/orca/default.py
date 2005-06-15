# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""The default script for presenting information to the user using
both speech and Braille.

Provides a number of presenter functions that display Accessible object
information to the user based upon the object's role."""

import math

import a11y
import brl
import core
import debug
import kbd
import mag
import orca
import rolenames
import speech

from orca_i18n import _                          # for gettext support
from rolenames import getSpeechForRoleName       # localized role names
from rolenames import getShortBrailleForRoleName # localized role names

########################################################################
#                                                                      #
# INFORMATION GATHERING FUNCTIONS                                      #
#                                                                      #
# Functions that extract information from objects for the purposes of  #
# being spoken or presented on a Braille display.                      #
#                                                                      #
########################################################################

def getAcceleratorAndShortcut(obj):
    """Gets the accelerator string (and possibly shortcut) for the given
    object.

    Arguments:
    - obj: the Accessible object

    A list containing the accelerator and shortcut for the given object.
    """

    try:
        action = a11y.getAction(obj)
    except:
        action = None

    if action is None:
        return ["", ""]

    # [[[TODO: WDW - assumes the first keybinding is all that we care about.]]]
    #
    bindingStrings = action.getKeyBinding(0).split(';')

    debug.println(debug.LEVEL_FINEST,
                  "KEYBINDINGS: " + action.getKeyBinding(0))
                  
    # [[[TODO: WDW - assumes menu items have three bindings]]]
    #
    if len(bindingStrings) == 3:
        mnemonic       = bindingStrings[0]
        fullShortcut   = bindingStrings[1]
        accelerator    = bindingStrings[2]
    elif len(bindingStrings) > 0:
        fullShortcut   = bindingStrings[0]
        accelerator    = ""
    else:
        fullShortcut   = ""
        accelerator    = ""
        
    fullShortcut = fullShortcut.replace("<","")
    fullShortcut = fullShortcut.replace(">"," ")
    fullShortcut = fullShortcut.replace(":"," ")

    accelerator  = accelerator.replace("<","")
    accelerator  = accelerator.replace(">"," ")

    return [accelerator, fullShortcut]


def getSpeechForAvailability(obj):
    """Returns a string to be spoken that describes the availability
    of the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be spoken.
    """
    
    if obj.state.count(core.Accessibility.STATE_SENSITIVE):
        return _("available")
    else:
        return _("unavailable")

    
def getSpeechForAccelerator(obj):
    """Returns a string to be spoken that describes the keyboard
    accelerator (and possibly shortcut) for the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be spoken.
    """

    result = getAcceleratorAndShortcut(obj)

    accelerator = result[0]
    shortcut = result[1]

    text = ""
    if len(shortcut) > 0:
        text += _("shortcut") + " " + shortcut + ". "
    if len(accelerator) > 0:
        text += _("accelerator") + " " + accelerator + ". "
        
    return text;


def getBrailleForAccelerator(obj):
    """Returns a string to be displayed in Braille that describes the keyboard
    accelerator (and possibly shortcut) for the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be displayed in Braille.
    """

    result = getAcceleratorAndShortcut(obj)

    accelerator = result[0]
    shortcut = result[1]

    text = ""
    if len(shortcut) > 0:
        text += "(" + shortcut + ")"
    if len(accelerator) > 0:
        text +=  "(" + accelerator + ")"
        
    return text;


def getSpeech(obj, includeAvailability=False):
    """Gets text to be spoken for the current object's name, role, any
    accelerators, and availability.

    Arguments:
    - obj: an Accessible
    """

    if obj.role == rolenames.ROLE_TEAR_OFF_MENU_ITEM:
        text = _("tear off menu item") + "."
    else:
        label = None
        if obj.role == rolenames.ROLE_TERMINAL:
            frame = a11y.getFrame(obj)
            if frame:
                label = frame.name
        if label is None:
            label = a11y.getLabel(obj)
        text =  label + " " + getSpeechForRoleName(obj) + "."
        accel = getSpeechForAccelerator(obj)
        if len(accel) > 0:
            text = text + " " + accel

    if includeAvailability:
        text = text + " " + getSpeechForAvailability(obj) + "."
    
    text = text.replace("...", _(" dot dot dot"), 1)

    return text


def getTextLineAtCaret(obj):
    """Gets the line of text where the caret is.

    Argument:
    - obj: an Accessible object that implements the AccessibleText
           interface

    Returns the line of text where the caret is.
    """

    # Get the the AccessibleText interrface
    #
    text = a11y.getText(obj)

    if text is None:
        return ["", 0, 0]
    
    # Get the line containing the caret
    #
    offset = text.caretOffset
    line = text.getTextAtOffset(offset,
                                core.Accessibility.TEXT_BOUNDARY_LINE_START)

    # Line is actually a list of objects-- the first is the actual
    # text of the line, the second is the start offset, and the third
    # is the end offset.  Sometimes we get the trailing line-feed-- remove it
    #
    if line[0][-1:] == "\n":
        content = line[0][:-1]
    else:
        content = line[0]

    return [content, offset, line[1]]


########################################################################
#                                                                      #
# ACCESSIBLE TEXT OUTPUT FUNCTIONS                                     #
#                                                                      #
# Functions for handling output to speech and Braille.                 #
#                                                                      #
########################################################################

def brailleUpdateText(obj):
    """Displays an object containing text on the Braille display.

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """

    label = None
    
    if obj.role == rolenames.ROLE_TERMINAL:
        frame = a11y.getFrame(obj)
        if frame:
            label = frame.name

    # Treat the beastly combo box specially.
    #
    comboBox = None
    if (obj.role == rolenames.ROLE_COMBO_BOX):
        comboBox = obj
    else:
        parent = obj.parent
        if parent and (parent.role == rolenames.ROLE_COMBO_BOX):
            comboBox = parent
    if comboBox:
        comboBoxPresenter(comboBox, True, False)
        return
        
    if label is None:
        label = a11y.getLabel(obj)

    brltext = getShortBrailleForRoleName(obj) + " "
    beginningOfText = len(brltext)

    result = getTextLineAtCaret(obj)
    line = result[0]    
    caretOffset = result[1]
    lineOffset = result[2]
    
    brltext = brltext + line
    brl.writeMessage(brltext)

    # Empty lines seem to wreak havoc on the offsets returned by
    # getTextLineAtCaret, so we trap for this.
    #
    cursor = beginningOfText + caretOffset - lineOffset
    if cursor >= beginningOfText:
        brl.setCursor(0, cursor)
        brl.refresh()


def sayLine(obj):
    """Speaks the line of an AccessibleText object that contains the
    caret. [[[TODO: WDW - what if the line is empty?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    # Get the AccessibleText interface of the provided object
    #
    result = getTextLineAtCaret(obj)
    speech.say("default", result[0])
    

def sayWord(obj):
    """Speaks the word at the caret.  [[[TODO: WDW - what if there is no
    word at the caret?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    text = a11y.getText(obj)
    offset = text.caretOffset
    word = text.getTextAtOffset(offset,
                                core.Accessibility.TEXT_BOUNDARY_WORD_START)
    speech.say("default", word[0])
    

def sayCharacter(obj):
    """Speak the character under the caret.  [[[TODO: WDW - isn't the
    caret between characters?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    text = a11y.getText(obj)
    offset = text.caretOffset
    character = text.getText(offset, offset+1)
    if character.isupper():
        speech.say("uppercase", character)
    else:
        speech.say("default", character)


########################################################################
#                                                                      #
# PRESENTATION FUNCTIONS                                               #
#                                                                      #
# The following functions present various types of objects via speech  #
# and Braille.  All the functions take the object as the first         #
# parameter, and a boolean specifying whether the object had focus     #
# already or not.                                                      #
#                                                                      #
# [[[TODO: WDW - don't really get the Braille region stuff yet.  This  #
# was an experiment of Marc's that we talked about in Hawaii, but I'm  #
# still not fully grasping the concept.]]]                             #
#                                                                      #
# [[[TODO: WDW - the order of presentation should be configurable by   #
# the user.]]]                                                         #
#                                                                      #
# [[[TODO: WDW - much i18n to be done here.]]]                         #
#                                                                      #
# [[[TODO: WDW - need to think about impact on magnification.]]]       #
#                                                                      #
########################################################################

def debugPresenter(presenterName, obj, already_focused):
    """Prints debug.LEVEL_FINER information regarding the presenter.

    Arguments:
    - presenterName: the name of the presenter
    - obj: the object being presented
    - already_focused: boolean staing if object just received focus
    """

    debug.println(debug.LEVEL_FINER,
                  "PRESENTER: %s" % presenterName)
    debug.println(debug.LEVEL_FINER,
                  "           obj             = %s" % obj.name)
    debug.println(debug.LEVEL_FINER,
                  "           role            = %s" % obj.role)
    debug.println(debug.LEVEL_FINER,
                  "           already_focused = %s" % already_focused)
    

def defaultPresenter(obj, already_focused):
    """Default presenter that just speaks and Brailles an object's
    label, role name, and accelerator (if it exists).

    Arguments:
    - obj: the Accessible component
    - already_focused: if False, the obj just received focus
    """

    debugPresenter("default.defaultPresenter", obj, already_focused)
    
    brailleText = getShortBrailleForRoleName(obj) + " " \
                  + a11y.getLabel(obj) + " " \
                  + getBrailleForAccelerator(obj)    
    brl.writeMessage(brailleText)
    brl.setCursor(0, 4)
    brl.refresh()
    
    speech.say("default", getSpeech(obj))
    

def pushButtonPresenter(obj, already_focused):
    """Speaks a button and displays it on the Braille display.
    
    Arguments:
    - obj: the Accessible button
    - already_focused: if False, the obj just received focus
    """

    debugPresenter("default.pushButtonPresenter", obj, already_focused)
    
    brailleText = getShortBrailleForRoleName(obj) + " " \
                  + a11y.getLabel(obj) + " " \
                  + getBrailleForAccelerator(obj)
    brl.writeMessage(brailleText)
    brl.setCursor(0, 4)
    brl.refresh()
    
    speech.say("default", getSpeech(obj))
    

def toggleButtonPresenter(obj, already_focused):
    """Speaks the name and state of the obj and also displays it in
    Braille.  An \"=\" in Braille indicates the checkbox is checked whereas
    a \"-\" indicates it is unchecked.

    Arguments:
    - obj: the Accessible check box
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.toggleButtonPresenter", obj, already_focused)
    
    # If the checkbox is checked, indicate this in speech and Braille
    #
    set = obj.state
    if set.count(core.Accessibility.STATE_CHECKED):
        # If it's not already focused, say it's name
        #
        if already_focused == False:
            text = a11y.getLabel(obj) + " " \
                   + getSpeechForRoleName(obj) + ". " \
                   + _("checked") + ". " \
                   + getSpeechForAccelerator(obj)
        else:
            text = _("checked") + "."
        brltext = getShortBrailleForRoleName(obj) + " " + "=" + " " \
                  + a11y.getLabel(obj)
    else:
        if already_focused == False:
            text = a11y.getLabel(obj) + " " \
                   + getSpeechForRoleName(obj) + ". " \
                   + _("not checked") + "." \
                   + getSpeechForAccelerator(obj)
        else:
            text = _("not checked") + "."
        brltext = getShortBrailleForRoleName(obj) + " " + "-" + " " \
                  + a11y.getLabel(obj)

    brl.writeMessage(brltext + " " + getBrailleForAccelerator(obj))
    brl.setCursor(0, 6)
    brl.refresh()
    
    speech.say("default", text)


def radioButtonPresenter(obj, already_focused):
    """Speaks the name and state of the obj and also displays it in
    Braille.  A \"7 \" in Braille indicates the radio button is checked whereas
    a \"' \" indicates it is unchecked.  [[[TODO: WDW - this also appears
    to attempt to show the radio button group name as well as all the
    other buttons in the group on the Braille display.  Not quite sure
    that's really working yet.]]]

    Arguments:
    - obj: the Accessible radio button
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.radioButtonPresenter", obj, already_focused)

    selected = obj.index
    label = a11y.getLabel(obj)
    role = getSpeechForRoleName(obj)
    text = ""
    brltext = getShortBrailleForRoleName(obj) + " "
    cursor = -1
    
    # If the radio button is in a group, we handle it differently (i.e.,
    # we say the group name and also display as much as we can in Braille).
    # [[[TODO: WDW - this is way broken for now, so we just skip it.]]]
    #group = a11y.getGroup (obj)
    group = None
    if group:
        groupName = a11y.getLabel(group)
        if (len(groupName) > 0):
            text = text + groupName + ". "
            brltext = brltext + groupName + " "
        
    states = obj.state
    if states.count(core.Accessibility.STATE_CHECKED):
        if already_focused == False:
            text = text + label + " " + role + ". " \
                   + _("checked") + "."
        else:
            text = _("checked") + "."
    else:
        if already_focused == False:
            text = text + label + " " + role + ". " \
                   + _("not checked") + "."
        else:
            text = _("not checked") + "."

    # If we're in a group, put the group name and the radio button's
    # label each in their own region
    #
    if group:
        children = group.childCount
        i = 0
        while i < children:
            child = group.child(i)
            if child.role != rolenames.ROLE_RADIO_BUTTON:
                debug.println(debug.LEVEL_SEVERE,
                              "ERROR: Found " + child.role + \
                              " in a radio button group!")
            else:
                if i == selected:
                    cursor = len(brltext) + 1
                set = child.state
                if set.count(core.Accessibility.STATE_CHECKED):
                    brltext = brltext + "(7 " + a11y.getLabel(child) + ")"
                else:
                    brltext = brltext + "(' " + a11y.getLabel(child) + ")"
            i = i + 1
    else:
        cursor = len(brltext) + 2
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            brltext = brltext + "7" + " " + a11y.getLabel(obj)
        else:
            brltext = brltext + "'" + " " + a11y.getLabel(obj)
        brltext = brltext + " " + getBrailleForAccelerator(obj)
 
    brl.writeMessage(brltext)
    if cursor < 0:
        debug.println(debug.LEVEL_SEVERE,
                      "ERROR: Did not find self (" + a11y.getLabel(obj) + \
                      ") in its own radio button group!")
    else:
        brl.setCursor(0, cursor)
        brl.refresh()
        
    speech.say("default", text)


def menuBarPresenter(obj, already_focused):
    """Speaks the menu bar that is currently selected and updates
    the Braille display to show all menu items, with the cursor under
    the currently selected item.

    Arguments:
    - obj: the Accessible menu bar
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.menuBarPresenter", obj, already_focused)
    
    # Put the menu on the Braille display - Put each menu item in its
    # own region on the Braille display
    #
    text = getSpeechForRoleName(obj) + "."
    brltext = getShortBrailleForRoleName(obj) + " "

    cursor = -1
    selection = a11y.getSelection(obj)            
    childCount = obj.childCount
    i = 0
    while i < childCount:
        label = ally.getLabel(obj.child(i))
        text = text + ", " + label
        if selection and selection.isChildSelected(i):
            cursor = len(brltext) + 1
        brltext = brltext + "(" + label + ")"
        i = i + 1
        
    brl.writeMessage(brltext)
    if cursor >= 0:
        brl.setCursor(0, cursor)
        brl.refresh()
        
    speech.say("default", text)

    
def menuPresenter(obj, already_focused):
    """Speaks the menu item that is currently selected and updates
    the Braille display to show all menu items, with the cursor under
    the currently selected item.

    Arguments:
    - obj: the Accessible menu item or a menu
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.menuPresenter", obj, already_focused)

    # Put the menu on the Braille display - Put each menu item in its
    # own region on the Braille display
    #
    if obj.role == rolenames.ROLE_MENU:
        menu = obj
    else:
        menu = obj.parent

    if menu is None:
        debug.println(debug.LEVEL_SEVERE, "No menu found for " \
                      + a11y.getLabel(obj))
        return
    
    brltext = getShortBrailleForRoleName(menu) + " " \
              + a11y.getLabel(menu) + " "

    cursor = -1    
    selection = a11y.getSelection(menu)
    childCount = menu.childCount
    i = 0
    while i < childCount:
        child = menu.child(i)
        if child.role != rolenames.ROLE_SEPARATOR \
            and child.state.count(core.Accessibility.STATE_SENSITIVE):
            if selection and selection.isChildSelected(i):
                cursor = len(brltext) + 1
            checked = child.state.count(core.Accessibility.STATE_CHECKED)
            name = a11y.getLabel(child)
            if child.role == rolenames.ROLE_CHECK_MENU_ITEM:
                if checked != 0:
                    name = "= " + name
                else:
                    name = "- " + name
            elif child.role == rolenames.ROLE_RADIO_MENU_ITEM:
                if checked != 0:
                    name = "7 " + name
                else:
                    name = "' " + name
            elif child.role == rolenames.ROLE_TEAR_OFF_MENU_ITEM:
                name = _("___")
            elif child.role == rolenames.ROLE_MENU:
                name = "o " + name
            brltext = brltext + "(" + name + ")"
        i = i + 1

    brl.writeMessage(brltext)
    if cursor >= 0:
        brl.setCursor(0, cursor)
        brl.refresh()
        
    # Now do the speech.
    #
    text = getSpeech(obj)
    if obj.role == rolenames.ROLE_MENU:
        i = 0
        itemCount = 0
        while i < obj.childCount:
            child = obj.child(i)
            if child.role != rolenames.ROLE_SEPARATOR:
                itemCount += 1
            i += 1
                
        if itemCount == 1:
            text += " " + _("one item") + "."
        else:
            text += (" %d " % itemCount) + _("items") + "."
    speech.say("default", text)

    
def sliderPresenter(obj, already_focused):
    """Speaks the given slider and displays it on the Braille display,
    with the cursor under the current value

    Arguments:
    - obj: the Accessible slider
    - already_focused: if False, the obj just received focus
    """

    debugPresenter("default.sliderPresenter", obj, already_focused)

    value = a11y.getValue(obj)

    # OK, this craziness is all about trying to figure out the most
    # meaningful formatting string for the floating point values.
    # The number of places to the right of the decimal point should
    # be set by the minimumIncrement, but the minimumIncrement isn't
    # always set.  So...we'll default the minimumIncrement to 1/100
    # of the range.  But, if max == min, then we'll just go for showing
    # them off to two meaningful digits.
    #
    try:
        minimumIncrement = value.minimumIncrement
    except:
        minimumIncrement = (value.maximumValue - value.minimumValue) / 100.0

    try:
        decimalPlaces = max(0, -math.log10(minimumIncrement))
    except:
        try:
            decimalPlaces = max(0, -math.log10(minimumValue))
        except:
            try:
                decimalPlaces = max(0, -math.log10(maximumValue))
            except:
                decimalPlaces = 0

    formatter = "%%.%df" % decimalPlaces
    valueString = formatter % value.currentValue
    minString   = formatter % value.minimumValue
    maxString   = formatter % value.maximumValue

    if already_focused:
        text = valueString
    else:
        text = a11y.getLabel(obj) + " " + getSpeechForRoleName(obj) + ". " \
               + _("Value: %s") % valueString + ". " \
               + _("Minimum value: %s") % minString + ". " \
               + _("Maximum value: %s") % maxString + ". " \
               + getSpeechForAccelerator(obj)

    brltext = getShortBrailleForRoleName(obj) + " " + a11y.getLabel(obj) \
              + " " + "(%s %s %s)" % (minString, valueString, maxString)

    brl.writeMessage(brltext + " " + getBrailleForAccelerator(obj))
    
    speech.say("default", text)


def pageTabPresenter(obj, already_focused):
    """Speaks the currently selected page tab and displays the page
    tab list on the Braille display, with the cursor under the currently
    selected page tab.

    Arguments:
    - obj: the currently selected Accessible page tab or page tab list
    - already_focused: if False, the obj just received focus
    """
   
    debugPresenter("default.pageTabPresenter", obj, already_focused)
    
    # Put the menu on the Braille display - Put each menu item in its
    # own region on the Braille display
    #
    if obj.role == rolenames.ROLE_PAGE_TAB_LIST:
        tablist = obj
    else:
        tablist = obj.parent

    brltext = getShortBrailleForRoleName(tablist) + " "

    cursor = -1
    selected = obj.index
    childCount = tablist.childCount    
    i = 0
    while i < childCount:
        if i == selected:
            cursor = len(brltext) + 1
        name = a11y.getLabel(tablist.child(i))
        brltext = brltext + "(" + name + ")"
        i = i + 1

    brl.writeMessage(brltext)
    if cursor >= 0:
        brl.setCursor(0, cursor)
        brl.refresh()
    
    # Now do the speech.
    #
    if obj.role == rolenames.ROLE_PAGE_TAB:
        text = getSpeech(obj)
    else:
        text = getSpeechForRoleName(tablist) + "."
        if tablist.childCount == 1:
            text += " " + _("one tab") + "."
        else:
            text += (" %d " % tablist.childCount) + _("tabs") + "."
    speech.say("default", text)


def textPresenter(obj, already_focused):
    """Speaks line the containing the caret and displays the line containing
    the caret on the Braille display.

    Arguments:
    - obj: an Accessible object that implements the AccessibleText interface
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.textPresenter", obj, already_focused)
    
    brailleUpdateText(obj)

    text = getSpeech(obj)
    result = getTextLineAtCaret(obj)
    text = text + " " + result[0]
    speech.say("default", text)


def comboBoxPresenter(obj, already_focused, speak=True):
    """Speaks line the containing the caret and displays the line containing
    the caret on the Braille display.  [[[TODO: WDW - this presenter seems
    to be a bit broken.]]]

    Arguments:
    - obj: the Accessible combo box
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.comboBoxPresenter", obj, already_focused)
    
    label = a11y.getLabel(obj)
    brltext = getShortBrailleForRoleName(obj) + " "
    text = ""
    
    if (label is not None) and (len(label) > 0):
        brltext = brltext + label + " "
        text = label + " "

    text = text + getSpeechForRoleName(obj) + ". "    

    # Find the text displayed in the combo box.  This is either:
    #
    # 1) The last text object that's a child of the combo box
    # 2) The selected child of the combo box.
    # 3) The contents of the text of the combo box itself when
    #    treated as a text object.
    #
    # Preference is given to #1, if it exists.
    #
    # [[[TODO: WDW - Combo boxes are complex beasts.  This algorithm
    # needs serious work.]]]
    #
    selectedItem = None
    comboSelection = a11y.getSelection(obj)
    if comboSelection and comboSelection.nSelectedChildren > 0:
        selectedItem = a11y.makeAccessible(comboSelection.getSelectedChild(0))

    result = getTextLineAtCaret(obj)
    selectedText = result[0]
    
    cursor = -1
    textObj = None
    children = obj.childCount
    i = 0
    while i < children:
        child = obj.child(i)
        if child.role == rolenames.ROLE_TEXT:
            textObj = child
        elif child.role == rolenames.ROLE_MENU:
            menuItemCount = child.childCount
            j = 0
            while j < menuItemCount:
                item = child.child(j)
                label = a11y.getLabel(item)
                if item == selectedItem \
                       or label == selectedText:
                    cursor = len(brltext) + 1
                brltext = brltext + "(" + label + ")"
                j = j + 1
        i = i + 1

    if already_focused:
        text = ""

    if textObj:
        result = getTextLineAtCaret(textObj)
        line = result[0]    
        caretOffset = result[1]
        lineOffset = result[2]
        brltext = brltext + "("
        beginningOfText = len(brltext)
        brltext = brltext + line
        brltext = brltext + " )"
        cursor = beginningOfText+caretOffset-lineOffset
        text = text + line + "."
    elif selectedItem:
        text = text + a11y.getLabel(selectedItem) + "."
    elif len(selectedText) > 0:
        text = text + selectedText + "."
    else:
        debug.println(debug.LEVEL_SEVERE,
                      "ERROR: Could not find selected item for combo box.")

    brl.writeMessage(brltext)
    if cursor >= 0:
        brl.setCursor(0, cursor)
        brl.refresh()
        
    if speak:
        speech.say("default", text)
                                    

def tablePresenter(obj, already_focused):
    """Speaks the name and role of the table as well as the selected items
    in the table.  Also does the same via Braille.

    Arguments:
    - obj: the Accessible that implements the AccessibleTable interface
    - already_focused: if False, the obj just received focus
    """
        
    debugPresenter("default.tablePresenter", obj, already_focused)
    
    # Only speak the table's name if it didn't already have focus
    #
    if already_focused == False:
        speech.say("default",
                   a11y.getLabel(obj) + " " + getSpeechForRoleName(obj) \
                   + ". ")

    # Get the selected rows of the table
    #
    table = a11y.getTable(obj)
    rows = table.getSelectedRows()
    cols = table.nColumns

    # Add the text of all the selected cells together
    #
    text = ""
    for row in rows:
        col = 0
        while col < cols:
            acc = table.getAccessibleAt(row, col)
            acc = a11y.makeAccessible(acc)

            # If the cell has children, get a list of them; otherwise,
            # just make a list with the cell itelf as the only member
            #
            if acc.childCount > 0:
                cells = a11y.getObjects(acc)
            else:
                cells = [acc]

            # Add the text of all the cells to the text string to be
            # displayed/spoken
            #
            for cell in cells:
                if cell.name and len(cell.name) > 0:
                    text = text + " " + cell.name

                    # Put each line of text in the cell in it's own
                    # region on the Braille display, so there is
                    #  tactile separation between them
                    #
                    for line in cell.name.splitlines():
                        brl.addRegion(line, len(line)+2, 0)
            col = col+1

    # Put the text on the Braille display
    #
    brl.refresh()
    speech.say("default", text)


# Present a dialog box - This function displays the name of the dialog
# on the Braille display.  It speaks the title of the dialog.  It
# then searches the dialog for labels which are not associated
# with any other objects, and reads their contents

def dialogPresenter(obj, already_focused):
    """Speaks the title of the dialog and displays it on the Braille display.
    Also reads the contents of labels inside the dialog that are not
    associated with any other objects.

    Arguments:
    - obj: the Accessible dialog
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.dialogPresenter", obj, already_focused)
    
    text = a11y.getLabel(obj)
    text = text + " " + getSpeechForRoleName(obj)

    # Find all the labels in the dialog
    #
    labels = a11y.findByRole(obj, "label")

    # Add the names of only those labels which are not associated with
    # other objects (i.e., do empty relation setss)
    #
    for label in labels:
        set = label.relations
        if len(set) == 0:
            text = text + " " + label.name
            
    brl.writeMessage(text)
    
    speech.say("default", text)


# Dictionary that maps role names to the above presenter functions
#
presenters = {}
presenters["alert"]              = dialogPresenter
presenters["check box"]          = toggleButtonPresenter
presenters["check menu item"]    = menuPresenter
presenters["combo box"]          = comboBoxPresenter
presenters["dialog"]             = dialogPresenter
presenters["menu"]               = menuPresenter
presenters["menu bar"]           = menuBarPresenter
presenters["menu item"]          = menuPresenter
presenters["multi line text"]    = textPresenter
presenters["page tab"]           = pageTabPresenter
presenters["page tab list"]      = pageTabPresenter
presenters["password text"]      = textPresenter
presenters["push button"]        = pushButtonPresenter
presenters["radio button"]       = radioButtonPresenter
presenters["radio menu item"]    = menuPresenter
presenters["single line text"]   = textPresenter
presenters["slider"]             = sliderPresenter
presenters["spin button"]        = textPresenter
presenters["table"]              = tablePresenter
presenters["tear off menu item"] = menuPresenter
presenters["terminal"]           = textPresenter
presenters["text"]               = textPresenter
presenters["toggle button"]      = toggleButtonPresenter
presenters["tree"]               = tablePresenter
presenters["tree table"]         = tablePresenter


########################################################################
#                                                                      #
# AT-SPI EVENT HANDLERS                                                #
#                                                                      #
# The following functions represent the listeners for this script, and #
# are named after the keys in the a11y.dispatcher dictionary.          #
#                                                                      #
########################################################################


def onWindowActivated(event):
    """Called whenever a toplevel window is activated.

    Arguments:
    - event: the Event
    """

    global presenters

    if presenters.has_key(event.source.role):
        p = presenters[event.source.role]
        try:
            p(event.source, False)
        except:
            debug.printException(debug.LEVEL_SEVERE)
    else:
        defaultPresenter(event.source, False)


def onFocus(event):
    """Called whenever an object gets focus.

    Arguments:
    - event: the Event
    """
    
    global presenters

    # Magnify the object.  [[[TODO: WDW - this is a hack for now.  The
    # individual presenters should probably know what to do.  This raises the
    # possible issue, however, that we might need different presenters for
    # different modes (e.g., braille presenters, speech presenters,
    # magnification presentaters).]]]
    #
    mag.magnifyAccessible(event.source)
    
    if presenters.has_key(event.source.role):
        p = presenters[event.source.role]
        try:
            p(event.source, False)
        except:
            debug.printException(debug.LEVEL_SEVERE)
    else:
        defaultPresenter(event.source, False)


# This dictionary defines the presenters which should be called when
# various states change for various types of objects.  The key
# represents the role and the value represents a list of states that
# we care about.
#
state_change_notifiers = {}
state_change_notifiers["check box"] = ("checked", None)
state_change_notifiers["toggle button"] = ("checked", None)

def onStateChanged(event):
    """Called whenever an object's state changes.  Currently, the
    state changes for non-focused objects are ignored.

    Arguments:
    - event: the Event
    """
    
    global presenters
    global state_change_notifiers

    if event.source != orca.focusedObject:
        return

    # Should we re-present the object?
    #
    if state_change_notifiers.has_key(event.source.role):
        notifiers = state_change_notifiers[event.source.role]
        found = False
        for state in notifiers:
            if state and event.type.endswith(state):
                found = True
                break
        if found:
            if presenters.has_key(event.source.role):
                p = presenters[event.source.role]
                try:
                    p(event.source, True)
                except:
                    debug.printException(debug.LEVEL_SEVERE)
                    defaultPresenter(event.source, True)
            else:
                defaultPresenter(event.source, True)


def onValueChanged(event):
    """Called whenever an object's value changes.  Currently, the
    value changes for non-focused objects are ignored.

    Arguments:
    - event: the Event
    """
    
    global presenters
    global state_change_notifiers
        
    if event.source != orca.focusedObject:
        return

    if presenters.has_key(event.source.role):
        p = presenters[event.source.role]
        try:
            p(event.source, True)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            defaultPresenter(event.source, True)
        else:
            defaultPresenter(event.source, True)


# This dictionary defines which presenters should be used if an
# object's selection changes.  The key represents the role and
# the value represents the presenter function.
#
selection_changed_handlers = {}
selection_changed_handlers["combo box"] = comboBoxPresenter
selection_changed_handlers["table"] = tablePresenter
selection_changed_handlers["tree table"] = tablePresenter


def onSelectionChanged(event):
    """Called when an object's selection changes.

    Arguments:
    - event: the Event
    """
    
    # Do we care?
    #
    if selection_changed_handlers.has_key(event.source.role):
        p = selection_changed_handlers[event.source.role]
        try:
            p(event.source, True)
        except:
            debug.printException(debug.LEVEL_SEVERE)
    

def onCaretMoved(event):
    """Called whenever the caret moves.

    Arguments:
    - event: the Event
    """

    # Magnify the object.  [[[TODO: WDW - this is a hack for now.]]]
    #
    mag.magnifyAccessible(event.source)

    # Update the Braille display
    #
    brailleUpdateText(event.source)

    # If this move is in response to an up or down arrow, read the line.
    # [[[TODO: WDW - this motion assumes arrow key events.  In an editor
    # such as vi, line up and down is done via other actions such as
    # "i" or "j".  We may need to think about this a little harder.]]]
    #
    if orca.lastKey == "Up" or orca.lastKey == "Down":
        sayLine(event.source)

    # Control-left and control-right arrows speak the word under the
    # caret.  [[[TODO: WDW - need to make sure the actions work as
    # expected.  For example, will the caret always end up at the
    # end of a word, or will it end up at the beginning of a word.
    # There seems to be some confusion in gedit about this.  That is,
    # when moving forward, it ends up at the end of the word and
    # when moving backward, it ends up at the beginning of the word.]]]
    #
    if orca.lastKey == "control+Right" or orca.lastKey == "control+Left":
        sayWord(event.source)

    # Right and left arrows speak the character under the cursor
    #
    if orca.lastKey == "Right" or orca.lastKey == "Left":
        sayCharacter(event.source)
 

def onTextInserted(event):
    """Called whenever text is inserted into an object.

    Arguments:
    - event: the Event
    """

    # Ignore text insertions to non-focused objects, unless the
    # currently focused object is the parent of the object to which
    # text was inserted
    #
    if (event.source != orca.focusedObject) \
           and (event.source.parent != orca.focusedObject):
        pass
    else:
        brailleUpdateText(event.source)
        text = event.any_data
        if text.isupper():
            speech.say("uppercase", text)
        else:
            speech.say("default", text)


def onTextDeleted(event):
    """Called whenever text is deleted from an object.

    Arguments:
    - event: the Event
    """
    
    # Ignore text deletions from non-focused objects, unless the
    # currently focused object is the parent of the object from which
    # text was deleted
    #
    if (event.source != orca.focusedObject) \
            and (event.source.parent != orca.focusedObject):
        pass
    else:
        brailleUpdateText(event.source)

    # The any_data member of the event object has the deleted text in
    # it - If the last key pressed was a backspace or delete key,
    # speak the deleted text.  [[[TODO: WDW - again, need to think
    # about the ramifications of this when it comes to editors such
    # as vi or emacs.
    #
    text = event.any_data
    if (orca.lastKey == "BackSpace") or (orca.lastKey == "Delete"):
        if text.isupper():
            speech.say("uppercase", text)
        else:
            speech.say("default", text)


def onActiveDescendantChanged(event):
    """Called when an object who manages its own descendants detects a
    change in one of its children.

    Arguments:
    - event: the Event
    """

    print "*** HERE:", event.source, event.source.name, event.source.role
    child = a11y.makeAccessible(event.any_data)
    print "*** HERE:", child.name, child.role, child.childCount
    print "*** HERE:", event.detail1, event.detail2
    index = event.detail1
    table = a11y.getTable(event.source)
    rowDesc = table.getRowDescription(index)
    colDesc = table.getColumnDescription(index)
    print "*** HERE:", rowDesc, colDesc

    row = a11y.makeAccessible(table.getRowHeader(index))
    print "*** HERE:", row
    rowDesc = ""
    if row:
        rowDesc = row.name
    col = a11y.makeAccessible(table.getColumnHeader(index))
    print "*** HERE:", col
    colDesc = ""
    if col:
        colDesc = col.name
    print "*** HERE:", rowDesc, colDesc
    print
    

########################################################################
#                                                                      #
# BRAILLE KEY EVENT HANDLERS                                           #    
#                                                                      #
# The following functions handle Braille key presses from the display. #
# These functions receive an object to which the keypress was          #
# directed, the region number which generated the key press, and the   #
# offset of the key within the region.                                 #
#                                                                      #
########################################################################

# Handle Braille key presses directed at menus

def menuBrlKeyHandler(obj, region, position):
    """Handles Braille key presses directed at menus.

    Arguments:
    - obj: the Accessible menu item
    - region: the Braille region which generated the press
    - position: the offset within the region
    """
    
    # Each menu item/menu displayed is in its own region - so the
    # region_num will indicate which menu/menu item to select
    #
    menu = obj.parent
    child = menu.child(region)

    # Get the AccessibleAction interface and do the first one
    #
    a = a11y.getAction(child)
    a.doAction(0)


def pageTabBrlKeyHandler(obj, region, position):
    """Handles Braille key presses directed at page tabs.

    Arguments:
    - obj: the Accessible page tag
    - region: the Braille region which generated the press
    - position: the offset within the region
    """

    # Each page tab will be displayed in its own region of the Braille
    # display - so the region number will indicate the page tab to
    # select
    #
    tablist = obj.parent
    
    # Select the clicked page tab
    #
    sel = a11y.getSelection(tablist)
    sel.selectChild(region)


def textBrlKeyHandler(obj, region, position):
    """Handles Braille key presses directed at text objects.

    Arguments:
    - obj: the Accessible text object
    - region: the Braille region which generated the press
    - position: the offset within the region
    """

    # The line containing the caret is displayed on the display - so
    # the content region of the Braille display that generated the
    # keypress contains that line.  Therefore, the absolute offset to
    # move the caret to can be derived by the offset of the key plus the
    # offset of the beginning of the line containing the caret
    #
    text = a11y.getText(obj)
    line = text.getTextAtOffset(text.caretOffset,
                                core.Accessibility.TEXT_BOUNDARY_LINE_START)
    cursor_position = position+line[1]
    text.setCaretOffset(cursor_position)

# This dictionary defines the Braille key handlers for the various types
# of objects.  The key represents the role name and the value represents
# the function.
#
brl_key_handlers = {}
brl_key_handlers["menu"] = menuBrlKeyHandler
brl_key_handlers["menu item"] = menuBrlKeyHandler
brl_key_handlers["page tab"] = pageTabBrlKeyHandler
brl_key_handlers["text"] = textBrlKeyHandler

# This function is called whenever a cursor key is pressed on the
# Braille display

def onBrlKey(region, position):
    """Called whenever a cursor key is pressed on the Braille display.

    Arguments:
    - region: the Braille region which generated the press
    - position: the offset within the region
    """

    if orca.focusedObject is None:
        return
    
    # Clear the Braille display memory (does not clear the physical
    # display)
    #
    brl.clear()

    # Do we have a Braille key handler for the role of the focused
    # object?
    #
    try:
       h = brl_key_handlers[orca.focusedObject.role]
       h(orca.focusedObject, region, position)
    except:
        debug.printException(debug.LEVEL_SEVERE)
        # We don't have a specific handler - see if the focused object
        # has an AccessibleAction interface, and if so, do the first
        # action it lists
        #
        a = a11y.getAction(orca.focusedObject)
        if a is None:
            pass
        else:
            a.doAction(0)


########################################################################
#                                                                      #
# SAYALL SUPPORT                                                       #    
#                                                                      #
# The following functions related to the sayAll system.  This system   #
# is designed to be pluggable such that sayAll commands could be       #
# implemented for various types of objects.  The current               #
# implementation only works for reading the text of single text        #
# objects.  This implementation will need to be extended to support    #
# reading of more complex documents such as web pages in Yelp/Mozilla, #
# and documents within StarOffice.                                     #
#                                                                      #
# [[[TODO: WDW - need to think about updating magnifier roi.]]]        #
#                                                                      #
########################################################################

def sayAgain():
    speech.sayAgain()

    
# sayAllText contains the AccessibleText object of the document
# currently being read
#
sayAllText = None

# sayAllPosition is the current position within sayAllText
#
sayAllPosition = 0

def sayAllGetChunk():
    """Speaks the next chunk of text.

    Returns True if there is still more text to be spoken.
    """
    
    global sayAllText
    global sayAllPosition

    # Get the next line of text to read
    #
    line = sayAllText.getTextAfterOffset(
        sayAllPosition,
        core.Accessibility.TEXT_BOUNDARY_LINE_START)

    # If the line is empty (which only happens at the end of the
    # document [[[TODO: WDW - is this true?]]]), quit.  Note that
    # blank lines are returned as lines of length 1 character which is
    # the newline character
    #
    if line[1] == line[2]:
        return False

    # Speak the line
    #
    speech.say("default", line[0])

    # Set the say all position to the beginning of the line being read
    #
    sayAllPosition = line[1]

    # Return true to continue reading

    return True


def sayAllStopped(position):
    """Called when sayAll mode is interrupted.

    Arguments:
    - position: the position within the current chunk where speech
                was interrupted.
    """
    
    global sayAllText
    global sayAllPosition

    sayAllText.setCaretOffset(sayAllPosition + position)

# This function initiates say all mode

def sayAll():
    """Initiates sayAll mode and attempts to say all the text of the
    currently focused Accessible text object.
    """
    
    global sayAllText
    global sayAllPosition

    # If the focused object isn't text, we don't know how to read it
    #
    txt = None
    try:
        txt = a11y.getText(orca.focusedObject)
    except:
        pass
    
    if txt is None:
        speech.say("default", _("Not a document."))
        return
    
    sayAllText = txt
    sayAllPosition = txt.caretOffset

    # Initialize sayAll mode with the speech subsystem - providing the
    # sayAllGetChunk and sayAllStopped callbacks.  Once we call sayLine,
    # the sayAll mode will begin executing when it receives the associated
    # speech callback.
    #
    speech.startSayAll("default", sayAllGetChunk, sayAllStopped)
    sayLine(orca.focusedObject)
