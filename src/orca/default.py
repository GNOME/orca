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

import core
import a11y
import orca
import settings                                  # user settings
import kbd
import speech
import brl
import mag
import debug

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
        pass

    if action is None:
        return ["", ""]

    # [[[TODO: WDW - assumes the first keybinding is all that we care about.]]]
    #
    bindingStrings = action.getKeyBinding (0).split (';')

    #debug.println ("KEYBINDINGS: " + action.getKeyBinding (0))
                  
    # [[[TODO: WDW - assumes menu items have three bindings]]]
    #
    if len (bindingStrings) == 3:
        mnemonic       = bindingStrings[0]
        fullShortcut   = bindingStrings[1]
        accelerator    = bindingStrings[2]
    elif len (bindingStrings) > 0:
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


def getSpeechForAvailability (obj):
    """Returns a string to be spoken that describes the availability
    of the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be spoken.
    """
    
    if obj.state.count (core.Accessibility.STATE_SENSITIVE):
        return _("available") + ". "
    else:
        return _("unavailable") + ". "

    
def getSpeechForNameAndRole (obj):
    """Returns a string to be spoken that describes the name and role
    of the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be spoken.
    """

    text = a11y.getLabel (obj) + " " + getSpeechForRoleName (obj) + ". "
    return text;


def getSpeechForAccelerator (obj):
    """Returns a string to be spoken that describes the keyboard
    accelerator (and possibly shortcut) for the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be spoken.
    """

    result = getAcceleratorAndShortcut (obj)

    accelerator = result[0]
    shortcut = result[1]

    text = ""
    if len (shortcut) > 0:
        text += _("shortcut") + " " + shortcut + ". "
    if len (accelerator) > 0:
        text += _("accelerator") + " " + accelerator + ". "
        
    return text;


def getBrailleForNameAndRole (obj):
    """Returns a string to be displayed in Braille that describes the name and
    role of the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be displayed in Braille.
    """

    text = getShortBrailleForRoleName (obj) + " " + a11y.getLabel (obj)
    return text;


def getBrailleForAccelerator (obj):
    """Returns a string to be displayed in Braille that describes the keyboard
    accelerator (and possibly shortcut) for the given object.

    Arguments:
    - obj: the Accessible object

    Returns a string to be displayed in Braille.
    """

    result = getAcceleratorAndShortcut (obj)

    accelerator = result[0]
    shortcut = result[1]

    text = ""
    if len (shortcut) > 0:
        text += "(" + shortcut + ")"
    if len (accelerator) > 0:
        text +=  "(" + accelerator + ")"
        
    return text;


def getSpeech (obj, includeAvailability=False):
    """Gets text to be spoken for the current object's name, role, any
    accelerators, and availability.

    Arguments:
    - obj: an Accessible
    """

    text = getSpeechForNameAndRole (obj) \
           + getSpeechForAccelerator (obj)

    if includeAvailability:
        text += getSpeechForAvailability (obj)
    
    text = text.replace ("...", _(" dot dot dot"), 1)

    return text


def getBraille (obj):
    """Gets Braille to be displayed for object's name, role, and accelerators.

    Arguments:
    - obj: an Accessible
    """

    text = getBrailleForNameAndRole (obj) \
           + " " + getBrailleForAccelerator (obj)
    
    return text


def getTextLineAtCaret (obj):
    """Gets the line of text where the caret is.

    Argument:
    - obj: an Accessible object that implements the AccessibleText
           interface

    Returns the line of text where the caret is.
    """

    # Get the the AccessibleText interrface
    #
    text = a11y.getText (obj)

    if text is None:
        return ["", 0, 0]
    
    # Get the line containing the caret
    #
    offset = text.caretOffset
    line = text.getTextAtOffset (offset,
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

def brailleUpdateText (obj):
    """Displays an object containing text on the Braille display.

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """

    parent = obj.parent
    if parent and (parent.role == "combo box"):
        label = a11y.getLabel (parent)
    else:
        label = a11y.getLabel (obj)


    # The label and text each get their own region - The label region
    # size is the length of the label's text + 1 or half the display
    # length, whidhever is less
    #
    display_size = brl.getDisplaySize ()
    label_region_size = len(label)
    if label_region_size > display_size/2-1:
            label_region_size = display_size/2-1
    if label_region_size > 0:
        brl.addRegion (label, label_region_size+1, 0)

        # Subtract the space that is left for us to use on the display
        #
        display_size = display_size - (label_region_size+1)

    # Get the line containing the caret
    #
    result = getTextLineAtCaret (obj)
    line = result[0]
    caretOffset = result[1]
    lineOffset = result[2]
    
    text_region = brl.addRegion (line, display_size, 0)

    # Make the advance keys scroll the region containing the text
    #
    brl.setScrollRegion (text_region)

    # Position the cursor at the caret position - Note that the region
    # containing the text can be longer than the physical display, and
    # that the cursor position is specified as an offset from the
    # beginning of the text
    #
    brl.setCursor (text_region, caretOffset-lineOffset)

    # Post the text to the display
    #
    brl.refresh ()


def sayLine (obj):
    """Speaks the line of an AccessibleText object that contains the
    caret. [[[TODO: WDW - what if the line is empty?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    # Get the AccessibleText interface of the provided object
    #
    result = getTextLineAtCaret (obj)
    speech.say ("default", result[0])
    

def sayWord (obj):
    """Speaks the word at the caret.  [[[TODO: WDW - what if there is no
    word at the caret?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    text = a11y.getText (obj)
    offset = text.caretOffset
    word = text.getTextAtOffset (offset,
                                 core.Accessibility.TEXT_BOUNDARY_WORD_START)
    speech.say ("default", word[0])
    

def sayCharacter (obj):
    """Speak the character under the caret.  [[[TODO: WDW - isn't the
    caret between characters?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    text = a11y.getText (obj)
    offset = text.caretOffset
    character = text.getText (offset, offset+1)
    if character.isupper ():
        speech.say ("uppercase", character)
    else:
        speech.say ("default", character)


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

    
def menuPresenter (obj, already_focused):
    """Speaks the menu item that is currently selected and updates
    the Braille display to show all menu items, with the cursor under
    the currently selected item.

    Arguments:
    - obj: the Accessible menu item or a menu
    - already_focused: if False, the obj just received focus
    """
    
    # Put the menu on the Braille display - Put each menu item in its
    # own region on the Braille display
    #
    name = "MNU" # [[[TODO: WDW - should get this from rolenames.py]]]
    brl.addRegion (name, len(name)+2, 0)

    menu = obj.parent
    selected = obj.index
    childCount = menu.childCount

    i = 0
    while i < childCount:
        name = a11y.getLabel (menu.child (i))
        brl.addRegion (name, len(name)+2, 0)
        i = i + 1

    # Put the Braille cursor under the selected item
    #
    if selected >= 0:
        brl.setCursor (selected, 0)

    # Put the text on the Braille display
    #
    brl.refresh ()

    # Now speak it...
    #
    text = getSpeech (obj)

    i = 0
    itemCount = 0
    while i < obj.childCount:
        child = obj.child (i)
        if child.role != "separator":
            itemCount += 1
        i += 1
        
    if itemCount == 1:
        text += " " + _("one item") + "."
    else:
        text += (" %d " % itemCount) + _("items") + "."

    speech.say ("default", text)

    
def pageTabPresenter (obj, already_focused):
    """Speaks the currently selected page tab and displays the page
    tab list on the Braille display, with the cursor under the currently
    selected page tab.

    Arguments:
    - obj: the currently selected Accessible page tab
    - already_focused: if False, the obj just received focus
    """
   
    # Put each page tab in its own region on the Braille display
    #
    name = "PTL" # [[[TODO: WDW - should get this from rolenames.py]]]
    brl.addRegion (name, len(name)+2, 0)

    tablist = obj.parent
    selected = obj.index
    childCount = tablist.childCount

    i = 0
    while i < childCount:
        name = a11y.getLabel (tablist.child (i))
        brl.addRegion (name, len(name)+2, 0)
        i = i + 1

    # Put the Braille cursor under the currently selected page tab
    #
    if selected >= 0:
        brl.setCursor (selected, 0)

    # Put the text on the display
    #
    brl.refresh ()

    # Now speak it...
    #
    text = getSpeech (obj)
    speech.say ("default", text)


def textPresenter (obj, already_focused):
    """Speaks line the containing the caret and displays the line containing
    the caret on the Braille display.

    Arguments:
    - obj: an Accessible object that implements the AccessibleText interface
    - already_focused: if False, the obj just received focus
    """
    
    brailleUpdateText (obj)

    text = getSpeech (obj)
    speech.say ("default", text)
    sayLine (obj)


def comboBoxPresenter (obj, already_focused):
    """Speaks line the containing the caret and displays the line containing
    the caret on the Braille display.  [[[TODO: WDW - this presenter seems
    to be a bit broken.]]]

    Arguments:
    - obj: the Accessible combo box
    - already_focused: if False, the obj just received focus
    """
    
    # Put the combo box's label, if any, in it's own region on the
    # Braille display
    #
    display_left = brl.getDisplaySize ()
    label = a11y.getLabel (obj)

    if (label is not None) and (len (label) > 0):
        # The region containing the label should be the length of the
        # label's text +1 or half the display length, whichever is
        # smaller
        #
        label_region_size = len(label)+1
        if label_region_size > (display_left/2)-1:
            label_region_size = (display_left/2)-1
        brl.addRegion (label, label_region_size, 0)
        display_left = display_left - label_region_size
        
    speak_text = getSpeechForNameAndRole (obj)

    # Find the last (if any) element of the combo box that contains text.
    #
    text = None
    children = obj.childCount
    i = 0
    while i < children:
        child = obj.child (i)
        if child.role == "text":
            text = child
        i = i + 1
        
    # If the combo box has a text object, display it in the combo
    # box's content region of the Braille display.  Otherwise, the
    # combo box's name will contain it's value - display that in the
    # combo box's content region on the Braille display.
    #
    # [[[TODO: WDW - something seems broken here.  I'm guessing what
    # is supposed to be happening is that each of the combo box's
    # items is to be displayed on the Braille display, much like a
    # menu.]]]
    #
    if text:
        txt = a11y.getText (text)
        contents = txt.getText (0, -1)
        region_num = brl.addRegion (contents, display_left, 0)
        brl.setCursor (region_num, txt.caretOffset)
        brl.setScrollRegion (region_num)
    else:
        contents = obj.name
        brl.addRegion (contents, display_left, 0)
        brl.refresh ()
        speak_text = speak_text + ", " + contents

    speech.say ("default", speak_text)
                                    

def tablePresenter (obj, already_focused):
    """Speaks the name and role of the table as well as the selected items
    in the table.  Also does the same via Braille.

    Arguments:
    - obj: the Accessible that implements the AccessibleTable interface
    - already_focused: if False, the obj just received focus
    """
        
    # Only speak the table's name if it didn't already have focus
    #
    if already_focused == False:
        speech.say ("default", getSpeechForNameAndRole (obj))

    # Get the selected rows of the table
    #
    table = a11y.getTable (obj)
    rows = table.getSelectedRows ()
    cols = table.nColumns

    # Add the text of all the selected cells together
    #
    text = ""
    for row in rows:
        col = 0
        while col < cols:
            acc = table.getAccessibleAt (row, col)
            acc = a11y.makeAccessible (acc)

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
                    for line in cell.name.splitlines ():
                        brl.addRegion (line, len(line)+2, 0)
            col = col+1

    # Put the text on the Braille display
    #
    brl.refresh ()
    speech.say ("default", text)


def checkBoxPresenter (obj, already_focused):
    """Speaks the name and state of the obj and also displays it in
    Braille.  An "(x)" in Braille indicates the checkbox is checked whereas
    a "( )" indicates it is unchecked.

    Arguments:
    - obj: the Accessible check box
    - already_focused: if False, the obj just received focus
    """
    
    # If the checkbox is checked, indicate this in speech and Braille
    #
    set = obj.state
    if set.count (core.Accessibility.STATE_CHECKED):
        # If it's not already focused, say it's name
        #
        if already_focused == False:
            text = getSpeech (obj) + " " + _("checked") + "."
        else:
            text = _("checked") + "."
        brltext = getShortBrailleForRoleName (obj) + " (x) " \
                  + a11y.getLabel (obj)
    else:
        if already_focused == False:
            text = getSpeech (obj) + " " + _("not checked") + "."
        else:
            text = _("not checked") + "."
        brltext = getShortBrailleForRoleName (obj) + " ( ) " \
                  + a11y.getLabel (obj)

    brl.writeMessage (brltext)
    brl.refresh ()
    speech.say ("default", text)


def radioButtonPresenter (obj, already_focused):
    """Speaks the name and state of the obj and also displays it in
    Braille.  A"(x)" in Braille indicates the checkbox is checked whereas
    a "( )" indicates it is unchecked.  [[[TODO: WDW - this also appears
    to attempt to show the radio button group name as well as all the
    other buttons in the group on the Braille display.  Not quite sure
    that's really working yet.]]]

    Arguments:
    - obj: the Accessible radio button
    - already_focused: if False, the obj just received focus
    """
    
    label = a11y.getLabel (obj)
    role = getSpeechForRoleName (obj)
    group = a11y.getGroup (obj)
    groupName = a11y.getLabel (group)

    text = ""
    brltext = ""
    states = obj.state
    if states.count (core.Accessibility.STATE_CHECKED):
        if already_focused == False:
            text = groupName + " " + label + " " + role
        text = text + " checked"
        brltext = "(x) " + label
    else:
        if already_focused == False:
            text = groupName + " " + label + " " + role
        text = text + " not checked"
        brltext = "( ) " + label

    # Put the group name and the radio button's label each in their
    # own region
    #
    brl.addRegion (groupName, len(groupName)+1, 0)
    buttonRegion = brl.addRegion (brltext, len(brltext), 0)

    # If the radio button's label is too long to fit in it's region,
    # make the advance keys scroll that radio button name region
    #
    brl.setScrollRegion (buttonRegion)
    brl.refresh ()
    
    speech.say ("default", text)


def buttonPresenter (obj, already_focused):
    """Speaks a button and displays it on the Braille display.
    
    Arguments:
    - obj: the Accessible button
    - already_focused: if False, the obj just received focus
    """

    brl.writeMessage (getBraille (obj))
    brl.refresh ()
    speech.say ("default", getSpeech (obj, True))
    

def defaultPresenter (obj, has_focus):
    """Default presenter that just speaks and Brailles and object's
    label, role name, and accelerator (if it exists).

    Arguments:
    - obj: the Accessible component
    - already_focused: if False, the obj just received focus
    """

    #debug.println ("Using default presenter.")

    speech.say ("default", getSpeech (obj))
    brl.writeMessage (getBraille (obj))
    

# Present a dialog box - This function displays the name of the dialog
# on the Braille display.  It speaks the title of the dialog.  It
# then searches the dialog for labels which are not associated
# with any other objects, and reads their contents

def dialogPresenter (obj, already_focused):
    """Speaks the title of the dialog and displays it on the Braille display.
    Also reads the contents of labels inside the dialog that are not
    associated with any other objects.

    Arguments:
    - obj: the Accessible dialog
    - already_focused: if False, the obj just received focus
    """
    
    text = a11y.getLabel (obj)
    text = text + " " + getSpeechForRoleName (obj)

    # Find all the labels in the dialog
    #
    labels = a11y.findByRole (obj, "label")

    # Add the names of only those labels which are not associated with
    # other objects (i.e., do empty relation setss)
    #
    for label in labels:
        set = label.relations
        if len(set) == 0:
            text = text + " " + label.name
            
    brl.writeMessage (text)
    brl.refresh ()
    
    speech.say ("default", text)

# Dictionary that maps role names to the above presenter functions
#
presenters = {}
#presenters["menu"] = menuPresenter
#presenters["menu item"] = menuPresenter
presenters["page tab"] = pageTabPresenter
presenters["text"] = textPresenter
presenters["password text"] = textPresenter
presenters["check box"] = checkBoxPresenter
presenters["check menu item"] = checkBoxPresenter
presenters["tree table"] = tablePresenter
presenters["tree"] = tablePresenter
presenters["table"] = tablePresenter
presenters["combo box"] = comboBoxPresenter
presenters["dialog"] = dialogPresenter
presenters["alert"] = dialogPresenter
presenters["radio button"] = checkBoxPresenter
presenters["radio menu item"] = checkBoxPresenter
presenters["push button"] = buttonPresenter
presenters["button"] = buttonPresenter


########################################################################
#                                                                      #
# AT-SPI EVENT HANDLERS                                                #
#                                                                      #
# The following functions represent the listeners for this script, and #
# are named after the keys in the a11y.dispatcher dictionary.          #
#                                                                      #
########################################################################


def onWindowActivated (event):
    """Called whenever a toplevel window is activated.

    Arguments:
    - event: the Event
    """

    global presenters

    if presenters.has_key (event.source.role):
        p = presenters[event.source.role]
        try:
            p (event.source, False)
        except:
            debug.printException ()
    else:
        defaultPresenter (event.source, False)


def onFocus (event):
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
    mag.magnifyAccessible (event.source)
    
    if presenters.has_key (event.source.role):
        p = presenters[event.source.role]
        try:
            p (event.source, False)
        except:
            debug.printException ()
    else:
        defaultPresenter (event.source, False)


# This dictionary defines the presenters which should be called when
# various states change for various types of objects.  The key
# represents the role and the value represents a list of states that
# we care about. The only current example that this table defines that
# the checkBoxPresenter function should be called when the CHECKED
# state changes on an object of role "checkbox"
#
state_change_notifiers = {}
state_change_notifiers["check box"] = ("checked")


def onStateChanged (event):
    """Called whenever an object's state changes.  Currently, the
    state changes for non-focused objects are ignored.

    Arguments:
    - event: the Event
    """
    
    global presenters
    global state_change_notifiers
    
    if event.source != a11y.focusedObject:
        return
    
    # Should we re-present the object?
    #
    if state_change_notifiers.has_key (event.source.role):
        notifiers = state_change_notifiers[event.source.role]
        found = False
        for state in notifiers:
            if event.type.find (state) != -1:
                found = True
                break
        if found:
            if presenters.has_key (event.source.role):
                p = presenters[event.source.role]
                try:
                    p (event.source, True)
                except:
                    debug.printException ()
                    defaultPresenter (event.source, True)
            else:
                defaultPresenter (event.source, True)


# This dictionary defines which presenters should be used if an
# object's selection changes.  The key represents the role and
# the value represents the presenter function.
#
selection_changed_handlers = {}
selection_changed_handlers["table"] = tablePresenter
selection_changed_handlers["tree table"] = tablePresenter


def onSelectionChanged (event):
    """Called when an object's selection changes.

    Arguments:
    - event: the Event
    """
    
    # Do we care?
    #
    if selection_changed_handlers.has_key (event.source.role):
        p = selection_changed_handlers[event.source.role]
        try:
            p (event.source, True)
        except:
            debug.printException ()
    

def onCaretMoved (event):
    """Called whenever the caret moves.

    Arguments:
    - event: the Event
    """

    # Magnify the object.  [[[TODO: WDW - this is a hack for now.]]]
    #
    mag.magnifyAccessible (event.source)

    # Update the Braille display
    #
    brailleUpdateText (event.source)

    # If this move is in response to an up or down arrow, read the line.
    # [[[TODO: WDW - this motion assumes arrow key events.  In an editor
    # such as vi, line up and down is done via other actions such as
    # "i" or "j".  We may need to think about this a little harder.]]]
    #
    if kbd.lastKey == "Up" or kbd.lastKey == "Down":
        sayLine (event.source)

    # Control-left and control-right arrows speak the word under the
    # caret.  [[[TODO: WDW - need to make sure the actions work as
    # expected.  For example, will the caret always end up at the
    # end of a word, or will it end up at the beginning of a word.
    # There seems to be some confusion in gedit about this.  That is,
    # when moving forward, it ends up at the end of the word and
    # when moving backward, it ends up at the beginning of the word.]]]
    #
    if kbd.lastKey == "control+Right" or kbd.lastKey == "control+Left":
        sayWord (event.source)

    # Right and left arrows speak the character under the cursor
    #
    if kbd.lastKey == "Right" or kbd.lastKey == "Left":
        sayCharacter (event.source)
 

def onTextInserted (event):
    """Called whenever text is inserted into an object.

    Arguments:
    - event: the Event
    """

    # Ignore text insertions to non-focused objects, unless the
    # currently focused object is the parent of the object to which
    # text was inserted
    #
    if (event.source != a11y.focusedObject) \
           and (event.source.parent != a11y.focusedObject):
        pass
    else:
        braillelUpdateText (event.source)


def onTextDeleted (event):
    """Called whenever text is deleted from an object.

    Arguments:
    - event: the Event
    """
    
    # Ignore text deletions from non-focused objects, unless the
    # currently focused object is the parent of the object from which
    # text was deleted
    #
    if (event.source != a11y.focusedObject) \
            and (event.source.parent != a11y.focusedObject):
        pass
    else:
        braillelUpdateText (event.source)

    # The any_data member of the event object has the deleted text in
    # it - If the last key pressed was a backspace or delete key,
    # speak the deleted text.  [[[TODO: WDW - again, need to think
    # about the ramifications of this when it comes to editors such
    # as vi or emacs.
    #
    text = event.any_data
    if (kbd.lastKey == "BackSpace") or (kbd.lastKey != "Delete"):
        if text.isupper ():
            speech.say ("uppercase", text)
        else:
            speech.say ("default", text)


# Quit the screen reader

def quit ():
    """Quits the screen reader.

    [[[TODO: WDW - so...I think this is bad because quit will typically
    be invoked from a keyboard event.  All keyboard events in orca are
    handled via synchronous methods.  orca.shutdown kills everything, so
    when this method returns, it is going to to cause some major issues
    because the event handler is going to want to return a value to the
    at-spi registry, but we just shut everything down.  I believe this
    is what is causing the segmentation fault when you quit orca.  I'm
    not quite sure of reliable ways to quit, I guess it may involve
    something like deregistering all listeners (keyboard and event) and
    placing a sentinel on the core event queue.]]]
    """
    
    orca.shutdown ()


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

def menuBrlKeyHandler (obj, region, position):
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
    child = menu.child (region)

    # Get the AccessibleAction interface and do the first one
    #
    a = a11y.getAction (child)
    a.doAction (0)


def pageTabBrlKeyHandler (obj, region, position):
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
    sel = a11y.getSelection (tablist)
    sel.selectChild (region)


def textBrlKeyHandler (obj, region, position):
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
    text = a11y.getText (obj)
    line = text.getTextAtOffset (text.caretOffset,
                                 core.Accessibility.TEXT_BOUNDARY_LINE_START)
    cursor_position = position+line[1]
    text.setCaretOffset (cursor_position)

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

def onBrlKey (region, position):
    """Called whenever a cursor key is pressed on the Braille display.

    Arguments:
    - region: the Braille region which generated the press
    - position: the offset within the region
    """
    
    # Clear the Braille display memory (does not clear the physical
    # display)
    #
    brl.clear ()

    # Do we have a Braille key handler for the role of the focused
    # object?
    #
    try:
        h = brl_key_handlers[a11y.focusedObject.role]
        h (a11y.focusedObject, region, position)
    except:
        debug.printException ()
        # We don't have a specific handler - see if the focused object
        # has an AccessibleAction interface, and if so, do the first
        # action it lists
        #
        a = a11y.getAction (a11y.focusedObject)
        if a is None:
            pass
        else:
            a.doAction (0)


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

def sayAgain ():
    speech.sayAgain ()

    
# sayAllText contains the AccessibleText object of the document
# currently being read
#
sayAllText = None

# sayAllPosition is the current position within sayAllText
#
sayAllPosition = 0

def sayAllGetChunk ():
    """Speaks the next chunk of text.

    Returns True if there is still more text to be spoken.
    """
    
    global sayAllText
    global sayAllPosition

    # Get the next line of text to read
    #
    line = sayAllText.getTextAfterOffset (
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
    speech.say ("default", line[0])

    # Set the say all position to the beginning of the line being read
    #
    sayAllPosition = line[1]

    # Return true to continue reading

    return True


def sayAllStopped (position):
    """Called when sayAll mode is interrupted.

    Arguments:
    - position: the position within the current chunk where speech
                was interrupted.
    """
    
    global sayAllText
    global sayAllPosition

    sayAllText.setCaretOffset (sayAllPosition + position)

# This function initiates say all mode

def sayAll ():
    """Initiates sayAll mode and attempts to say all the text of the
    currently focused Accessible text object.
    """
    
    global sayAllText
    global sayAllPosition

    # If the focused object isn't text, we don't know how to read it
    #
    txt = None
    try:
        txt = a11y.getText (a11y.focusedObject)
    except:
        pass
    
    if txt is None:
        speech.say ("default", _("Not a document."))
        return
    
    sayAllText = txt
    sayAllPosition = txt.caretOffset

    # Initialize sayAll mode with the speech subsystem - providing the
    # sayAllGetChunk and sayAllStopped callbacks.  Once we call sayLine,
    # the sayAll mode will begin executing when it receives the associated
    # speech callback.
    #
    speech.startSayAll ("default", sayAllGetChunk, sayAllStopped)
    sayLine (a11y.focusedObject)
    

########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################

def debugListApps ():
    """Prints a list of all known applications to stdout if the
    settings.debug flag is enabled."""

    debug.listApps ()
    return True 

def debugListActiveApp ():
    """Prints details about the currently active application."""

    debug.listActiveApp ()
    return True 
