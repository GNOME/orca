# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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

import core
import a11y
import orca

# Customized role pronunciations

from rolenames import getRoleName

# User settings

import settings

# Keyboard hooks

import kbd

# Speech support

import speech

# Braille support

import brl

# Orca i18n

from orca_i18n import _

# The following functions present various types of objects - all
# presentation functions handle both speech and Braille.  All
# functions take the object as the first parameter, and a boolean
# specifying whether the object had focus already or not


# Present menus - This function speaks the menu item which current is
# selected, an updates the Braille display to show all menu items with
# the cursor under the currently selected item.  The object passed as
# the first parameter is a menu item or a menu.

def menuPresenter (obj, already_focussed):
    menu = obj.parent
    selected = obj.index
    childCount = menu.childCount
    i = 0

    # Put the menu on the Braille display - Put each menu item in its
    # own region on the Braille display

    while i < childCount:
        name = a11y.getLabel (menu.child (i))
        brl.addRegion (name, len(name)+2, 0)
        i = i + 1

    # Put the Braille cursor under the selected item

    if selected >= 0:
        brl.setCursor (selected, 0)

    # Put the text on the Braille display

    brl.refresh ()

    # Speak the selected menu item

    if obj.role == "menu item":
        text = a11y.getLabel (obj)
    else:
        text = a11y.getLabel (obj) + " " + getRoleName(obj)
    speech.say ("default", text)

# Present a page tab list - This function displays the page tab list
# on the Braille display and speaks the currently selected page tab,
# and puts the Braille cursor under the currently selected page tab.
# the object passed to this function as the first parameter is the
# currently selected page tab.

def pageTabPresenter (obj, already_focussed):
    tablist = obj.parent
    selected = obj.index
    childCount = tablist.childCount

    # Put each page tab in its own region on the Braille display

    i = 0
    while i < childCount:
        name = a11y.getLabel (tablist.child (i))
        brl.addRegion (name, len(name)+2, 0)
        i = i + 1

    # Put the Braille cursor under the currently selected page tab

    if selected >= 0:
        brl.setCursor (selected, 0)

    # Put the text on the display

    brl.refresh ()

    # Speak the currently selected page tab

    text = a11y.getLabel (obj) + " " + getRoleName (obj)
    speech.say ("default", text)

# this function displays an object containing text on the Braille
# display - It takes the Accessible object and retrieves the
# AccessibleText interface, since it may also need access to the
# object's label

def brlUpdateText (obj):

    # If we're not using Braille, bail out now!

    # If this is the child of a combo box, use the combo boxe's label

    parent = obj.parent
    if parent.role == "combo box":
        label = a11y.getLabel (parent)
    else:
        label = a11y.getLabel (obj)

    # Get the the AccessibleText interrface

    text = a11y.getText (obj)
    offset = text.caretOffset
    display_size = brl.getDisplaySize ()

    # Get the line containing the caret

    line = text.getTextAtOffset (offset, core.Accessibility.TEXT_BOUNDARY_LINE_START)

    # Line is actually a list of objects-- the first is the actual
    # text of the line, the second is the start offset, and the third
    # is the end offset

    # Sometimes we get the trailing line-feed-- remove it

    if line[0][-1:] == "\n":
        content = line[0][:-1]
    else:
        content = line[0]

    # The label and text each get their own region - The label region
    # size is the length of the label's text + 1 or half the display
    # length, whidhever is less

    label_region_size = len(label)
    if label_region_size > display_size/2-1:
            label_region_size = display_size/2-1
    if label_region_size > 0:
        brl.addRegion (label, label_region_size+1, 0)

        # Subtract the space that is left for us to use on the display

        display_size = display_size - (label_region_size+1)
    text_region = brl.addRegion (content, display_size, 0)

    # Make the advance keys scroll the region containing the text

    brl.setScrollRegion (text_region)

    # Position the cursor at the caret position - Note that the region
    # containing the text can be longer than the physical display, and
    # tthat the cursor position is specified as an offset from the
    # beginning of the text

    brl.setCursor (text_region, offset-line[1])

    # Post the text to the display

    brl.refresh ()

# Speak the line of an AccessibleText object which contains the caret

def sayLine (obj):

    # Get the AccessibleText interface of the provided object

    text = a11y.getText (obj)
    offset = text.caretOffset
    line = text.getTextAtOffset (offset, core.Accessibility.TEXT_BOUNDARY_LINE_START)
    speech.say ("default", line[0])
    
# Spaek the word containing the caret

def sayWord (obj):
    text = a11y.getText (obj)
    offset = text.caretOffset
    word = text.getTextAtOffset (offset, core.Accessibility.TEXT_BOUNDARY_WORD_START)
    speech.say ("default", word[0])
    
# Speak the character under the caret

def sayCharacter (obj):
    text = a11y.getText (obj)
    offset = text.caretOffset
    character = text.getText (offset, offset+1)
    if character.isupper ():
        speech.say ("uppercase", character)
    else:
        speech.say ("default", character)
    
# Present a text object - This displays the line containing the caret
# on the Braille display, and speaks the line containing the caret
# with speech

def textPresenter (obj, already_focussed):

    # Update the Braille display

    brlUpdateText (obj)
    text = a11y.getLabel (obj) + " " + getRoleName (obj)
    speech.say ("default", text)
    sayLine (obj)


# Present a combo box in speech and Braille

def comboBoxPresenter (obj, already_focussed):
    has_text = False
    children = obj.childCount
    i = 0

    # See if this combo box  has a text object in it

    while i < children:
        child = obj.child (i)
        if child.role == "text":
            text = child
            has_text = True
        i = i + 1
        display_left = brl.getDisplaySize ()
    label = a11y.getLabel (obj)

    # Put the combo box's label, if any, in it's own region on the
    # Braille display

    if label is not None and len(label) > 0:

        # The region containing the label should be the length of the
        # label's text +1 or half the display length, whichever is
        # smaller

        label_region_size = len(label)+1
        if label_region_size > (display_left/2)-1:
            label_region_size = (display_left/2)-1
        brl.addRegion (label, label_region_size, 0)
        display_left = display_left - label_region_size
        speak_text = label
    else:
        speak_text = ""
    speak_text = speak_text + " " + getRoleName (obj)
    if has_text:

        # If the bomxo box has a text object, display it in the combo
        # box's content region of the Braille display

        txt = a11y.getText (text)
        contents = txt.getText (0, -1)
        region_num = brl.addRegion (contents, display_left, 0)
        brl.setCursor (region_num, txt.caretOffset)

        # Make the advance keys scroll the content region

        brl.setScrollRegion (region_num)
    else:

        # Otherwise, the combo box's name will contain it's value -
        # display that in the combo box's content region on the Braille
        # display

        contents = obj.name
        brl.addRegion (contents, display_left, 0)
        brl.refresh ()
        speak_text = speak_text + ", " + contents
    speech.say ("default", speak_text)
                                    

# Present a table object for speech and Braille - This function speaks
# and Brailles the name and role of the table, and then speaks and
# Brailles the selected items in the table

def tablePresenter (obj, already_focussed):

    # Only speak the table's name if it didn't already have focus

    if already_focussed == False:
        name = obj.name
        role = getRoleName (obj)
        speech.say ("default", name + " " + role)

    # Get the accessible table interface of the object

    table = a11y.getTable (obj)

    # Get the selected rows of the table

    rows = table.getSelectedRows ()
    cols = table.nColumns

    # Add the text of all the selected cells together

    text = ""
    for row in rows:
        col = 0
        while col < cols:
            acc = table.getAccessibleAt (row, col)
            acc = a11y.makeAccessible (acc)

            # If the cell has children, get a list of them

            if acc.childCount > 0:
                cells = a11y.getObjects(acc)

            # Otherwise, just make a list with the cell itelf as the
            # only member

            else:
                cells = [acc]

            # Add the text of all the cells to the text string to be
            # displayed/spoken

            for cell in cells:
                if cell.name and len(cell.name) > 0:
                    text = text + " " + cell.name

                    # Put each line of text in the cell in it's own
                    # region on the Braille display, so there is
                    #  tactile separation between them

                    for line in cell.name.splitlines ():
                        brl.addRegion (line, len(line)+2, 0)
            col = col+1

    # Put the text on the Braille display

    brl.refresh ()
    speech.say ("default", text)

# Present a checkbox - This function displays ( ) and the object's
# name on the display.  An x between the ( and ) indicates that the
# checkbox is checked.  It also sppeaks the name of the object and
# whether it is checked or unchecked

def checkBoxPresenter (obj, already_focussed):
    label = a11y.getLabel (obj)
    role = getRoleName (obj)
    text = ""
    brltext = ""

    # Get the state of the checkbox

    set = obj.state

    # If the checkbox is checked, indicate this in speech and Braille

    if set.count (core.Accessibility.STATE_CHECKED):

        # If it's not already focused, say it's name

        if already_focussed == False:
            text = label + " " + role
        text = text + " checked"
        brltext = "(*) " + label
    else:
        if already_focussed == False:
            text = label + " " + role
        text = text + " not checked"
        if settings.useBraille:
            brltext = "( ) " + label
    brl.writeMessage (brltext)
    brl.refresh ()
    speech.say ("default", text)

# Present a radio button - This function is essentially the same as
# the checkbox presenter, except that it attempts to find the
# radio button's group

def radioButtonPresenter (obj, already_focussed):

    # Find group

    group = a11y.getGroup (obj)
    groupName = a11y.getLabel (group)

    label = a11y.getLabel (obj)
    role = getRoleName (obj)
    text = ""
    brltext = ""
    states = obj.state
    if states.count (core.Accessibility.STATE_CHECKED):
        if already_focussed == False:
            text = groupName + " " + label + " " + role
        text = text + " checked"
        brltext = "(*) " + label
    else:
        if already_focussed == False:
            text = groupName + " " + label + " " + role
        text = text + " not checked"
        brltext = "( ) " + label

    # Put the group name and the radio button's label each in their
    # own region

    brl.addRegion (groupName, len(groupName)+1, 0)
    buttonRegion = brl.addRegion (brltext, len(brltext), 0)

    # If the radio button's label is too long to fit in it's region,
    # make the advance keys scroll that radio button name region

    brl.setScrollRegion (buttonRegion)
    brl.refresh ()
    speech.say ("default", text)


# Present a button - Displays the button name on the Braille display
# and speaks it

def buttonPresenter (obj, already_focussed):
    name = a11y.getLabel (obj)
    brl.writeMessage (name)
    text = name + " " + getRoleName (obj)
    speech.say ("default", text)

# Presenter which is used if we don't have a role specific one

def defaultPresenter (obj, has_focus):

    # Speak and Braille the object's label and role

    text = a11y.getLabel (obj) + " " + getRoleName (obj)
    brl.writeMessage (text)
    speech.say ("default", text)
    
# Present a dialog box - This function displays the name of the dialog
# on the Braille display.  It speaks the title of the dialog.  It
# then searches the dialog for labels which are not associated
# with any other objects, and reads their contents

def dialogPresenter (dlg, already_focussed):
    text = a11y.getLabel (dlg)
    text = text + " " + getRoleName (dlg)

    # Find all the labels in the dialog

    labels = a11y.findByRole (dlg, "label")

    # Add the names of only those labels which are not associated with
    # other objects (I.E., do empty relation setss)

    for label in labels:
        set = label.relations
        if len(set) == 0:
            text = text + " " + label.name
    brl.writeMessage (text)
    brl.refresh ()
    speech.say ("default", text)

# This hash table maps role names to the above presenter functions

presenters = {}

presenters["menu"] = menuPresenter
presenters["menu item"] = menuPresenter
presenters["page tab"] = pageTabPresenter
presenters["text"] = textPresenter
presenters["password text"] = textPresenter
presenters["check box"] = checkBoxPresenter
presenters["tree table"] = tablePresenter
presenters["tree"] = tablePresenter
presenters["table"] = tablePresenter
presenters["combo box"] = comboBoxPresenter
presenters["dialog"] = dialogPresenter
presenters["alert"] = dialogPresenter
presenters["radio button"] = radioButtonPresenter
presenters["push button"] = buttonPresenter

# This function gets called whenever an object gets focus

def onFocus (event):
    global presenters

    roleName = event.source.role

    # Do we have a role specific presenter for this type of object

    try:
        p = presenters[roleName]

    # Nope, use the default

    except:
        defaultPresenter (event.source, False)
        return
    p (event.source, False)

# This function is called whenever a toplevel window is activated

def onWindowActivated (event):
    p = None

    # Do we have a role specific presenter for this type of object?
    
    try:
        p = presenters[event.source.role]

    except:
        pass
    if p is not None:
        p (event.source, False)
    else:
        defaultPresenter (event.source, False)

# This hash table defines which presenters should be used if an
# object's selection changes

selection_changed_handlers = {}

selection_changed_handlers["table"] = tablePresenter
selection_changed_handlers["tree table"] = tablePresenter

# This function is called if an object's selection changes

def onSelectionChanged (event):

    # See if we have an object specific presente registered to be
    # called when this type of object's selection changes

    try:
        p = selection_changed_handlers[event.source.role]

    # Don't do anything if we don't have a role-specific presenter

    except:
        return
    p (event.source, True)
    

# This hash table defines the presenters which should be called when
# various states change for various types of objects.  The only
# current example is that this table defines that the
# checkBoxPresenter function should be called when the CHECKED state
# changes on an object of role "checkbox"

state_change_notifiers = {}
state_change_notifiers["check box"] = ("checked")

# This function is called whenever an object's state changes - Note
# that currently, state changes for non-focused objects are ignored

def onStateChanged (event):
    global presenters
    global state_change_notifiers
    
    # Don't notify for state changes for non-focussed objects

    if event.source != a11y.focussedObject:
        return
    
    # Should we re-present the object?

    try:
        notifiers = state_change_notifiers[event.source.role]
    except:
        return

    # WE found a notifier - is the state that just changed in our
    # list?

    found = False
    for state in notifiers:
        if event.type.find (state) != -1:
            found = True
            break

    if found == False:
        return

    # We're supposed to notify the user about this state change - do
    # we have a presenter for this type of object
    
    try:
        p = presenters[event.source.role]
    except:
        defaultPresenter (event.source, True)
        return
    p (event.source, True)

# This function is called whenever the caret moves

def onCaretMoved (event):

    # Update the Braille display

    brlUpdateText (event.source)

    # If this move is in response to an up or down arrow, read the line

    if kbd.lastKey == "Up" or kbd.lastKey == "Down":
        sayLine (event.source)

    # Control-left and control-right arrows speak the word under the
    # caret

    if kbd.lastKey == "control+Right" or kbd.lastKey == "control+Left":
        sayWord (event.source)

    # Right and left arrows speak the character under the cursor

    if kbd.lastKey == "Right" or kbd.lastKey == "Left":
        sayCharacter (event.source)
 

# This function is called whenever text is inserted into an object

def onTextInserted (event):

    # Ignore text insertions to non-focused objects, unless the
    # currently focused object is the parent of the object to which
    # text was inserted
    
    if event.source != a11y.focussedObject and \
           event.source.parent != a11y.focussedObject:
        return
    brlUpdateText (event.source)

# This function is called whenever text is deleted from an object

def onTextDeleted (event):

    # Ignore text deletions from non-focused objects, unless the
    # currently focused object is the parent of the object from which
    # text was deleted
    
    if event.source != a11y.focussedObject and \
           event.source.parent != a11y.focussedObject:
        return
    if settings.useBraille == True:
        brlUpdateText (event.source)

    # The any_data member of the event object has the deleted text in
    # it - If the last key pressed was a backspace or delete key,
    # speak the deleted text

    text = event.any_data
    if kbd.lastKey != "BackSpace" and kbd.lastKey != "Delete":
        return
    if text.isupper ():
        speech.say ("uppercase", text)
    else:
        speech.say ("default", text)

# Quit the screen reader

def quit ():
    orca.shutdown ()
    
# The following functions handle Braille key presses from the display
# - These functions receive an object to which the keypress was
# directed, the region number which generated the key press, and the
# offset of the key within the region

# Handle Braille key presses directed at menus

def menuBrlKeyHandler (obj, region, position):

    # Each menu item/menu displayed is in its own region - so the
    # region_num will indicate which menu/menu item to select

    menu = obj.parent
    child = menu.child (region)

    # Get the AccessibleAction interface and do the first one

    a = a11y.getAction (child)
    a.doAction (0)

# This function is called when Braille keys are directed at page tabs

def pageTabBrlKeyHandler (obj, region, position):

    # Each page tab will be displayed in its own region of the Braille
    # display - so the region number will indicate the page tab to
    # select

    tablist = obj.parent
    
    # Select the clicked page tab

    sel = a11y.getSelection (tablist)
    sel.selectChild (region)

# This function is called when Braille keypresses are directed at text
# objects
def textBrlKeyHandler (obj, region, position):

    # The line containing the caret is displayed on the display - so
    # the content region of the Braille display that generated the
    # keypress contains that line.  Therefore, the absolute offset to
    # move the caret to can be derived by the offset of the key plus the
    # offset of the beginning of the line containing the caret

    text = a11y.getText (obj)
    line = text.getTextAtOffset (text.caretOffset, core.Accessibility.TEXT_BOUNDARY_LINE_START)
    cursor_position = position+line[1]
    text.setCaretOffset (cursor_position)

# This hash table defines the Braille key handlers for the various types
# of objects

brl_key_handlers = {}

brl_key_handlers["menu"] = menuBrlKeyHandler
brl_key_handlers["menu item"] = menuBrlKeyHandler
brl_key_handlers["page tab"] = pageTabBrlKeyHandler
brl_key_handlers["text"] = textBrlKeyHandler

# This function is called whenever a cursor key is pressed on the
# Braille display

def onBrlKey (region, position):

    # Clear the Braille display memory (does not clear the physical
    # disply)

    brl.clear ()

    # Do we have a Braille key handler for the role of the focused
    # object?

    try:
        h = brl_key_handlers[a11y.focussedObject.getRoleName ()]
    except:
        h = None
    if h:
        h (a11y.focussedObject, region, position)
    else:

        # We don't have a specific handler - see if the focused object
        # has an AccessibleAction interface, and if so, do the first
        # action it lists
        
        a = a11y.getAction (a11y.focussedObject)
        if a is None:
            pass
        else:
            a.doAction (0)

# The following functions related to the sayAll system - This system
# is designed to be pluggable such that sayAll commands could be
# implemented for various types of objects.  The current
# implementation only works for reading the text of single text
# objects.  This implementation will need to be extended to support
# reading of more complex documents such as web pages in Yelp/Mozilla,
# and documents within StarOffice

# sayAllText contains the AccessibleText object of the document
# currently being read

sayAllText = None

# sayAllPosition is the current position within sayAllText

sayAllPosition = 0

def sayAllGetChunk ():
    global sayAllText
    global sayAllPosition

    # Get the next line of text to read

    line = sayAllText.getTextAfterOffset (sayAllPosition, core.Accessibility.TEXT_BOUNDARY_LINE_START)

    # If the line is empty (which only happens at the end of the
    # document), quit.  Note that blank lines are returned as lines
    # of length 1 character which is the newline character

    if line[1] == line[2]:
        return False

    # Speak the line

    speech.say ("default", line[0])

    # Set the say all position to the beginning of the line being read

    sayAllPosition = line[1]

    # Return true to continue reading

    return True

# This function is called when sayAll mode is interrupted - the only
# parameter is the position within the current chunk where speech
# was interrupted

def sayAllStopped (position):
    global sayAllText
    global sayAllPosition

    # Move the caret to the position where speech was interrupted

    sayAllText.setCaretOffset (sayAllPosition+position)

# This function initiates say all mode

def sayAll ():
    global sayAllText
    global sayAllPosition

    # If the focused object isn't text, we don't know how to read it

    txt = a11y.getText (a11y.focussedObject)
    if txt is None:
        speech.say ("default", _("Not a document."))
        return

    # Setup say all mode

    sayAllText = txt

    # Start reading at the caret offset

    sayAllPosition = txt.caretOffset

    # Start say all by speaking the current line - the end of speech
    # marker which occurs when this call to say is finished will cause
    # the say all process to continue

    sayLine (txt)

    # Initiate say all mode with the speech subsystem - providing the
    # sayAllGetChunk and sayAllStopped callbacks

    speech.startSayAll ("default", sayAllGetChunk, sayAllStopped)
