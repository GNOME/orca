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

"""The Default Script for presenting information to the user using
both speech and Braille.

This module also provides a number of presenter functions that display
Accessible object information to the user based upon the object's role."""

import math

import a11y
import braille
import core
import debug
import kbd
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.]]]
import orca
import rolenames
import speech

from input_event import InputEventHandler

from orca_i18n import _                          # for gettext support
from rolenames import getShortBrailleForRoleName # localized role names
from rolenames import getSpeechForRoleName       # localized role names

from script import Script

########################################################################
#                                                                      #
# The factory method for this module.  All Scripts are expected to     #
# have this method, and it is the sole way that instances of scripts   #
# should be created.                                                   #
#                                                                      #
########################################################################

def getScript(app):
    """Factory method to create a new Default script for the given
    application.  This method should be used for creating all
    instances of this script class.

    Arguments:
    - app: the application to create a script for
    """
    
    return Default(app)


########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Default(Script):
    
    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.
        
        Arguments:
        - app: the application to create a script for.
        """
        
        Script.__init__(self, app)

        # [[[TODO: WDW - right now, cannot easily refer to instance methods.]]]
        #
        self.keybindings["F9"] = InputEventHandler(
            sayAgain,
            _("Repeats last utterance sent to speech."))
        self.keybindings["F11"] = InputEventHandler(
            sayAll,
            _("Speaks entire document."))
            
        #self.listeners["object:property-change:accessible-name"] = \
        #    self.onNameChanged 
        #self.listeners["object:text-selection-changed"]          = \
        #    self.onTextSelectionChanged 
        self.listeners["object:text-changed:insert"]             = \
            self.onTextInserted 
        self.listeners["object:text-changed:delete"]             = \
            self.onTextDeleted
        self.listeners["object:state-changed:"]                  = \
            self.onStateChanged
        self.listeners["object:property-change:accessible-value"] = \
            self.onValueChanged
        self.listeners["object:value-changed:"]                  = \
            self.onValueChanged
        self.listeners["object:selection-changed"]               = \
            self.onSelectionChanged
        self.listeners["object:text-caret-moved"]                = \
            self.onCaretMoved
        #self.listeners["object:link-selected"]                   = \
        #    self.onLinkSelected
        #self.listeners["object:property-change:"]                = \
        #    self.onPropertyChanged
        self.listeners["object:active-descendant-changed"]       = \
            self.onActiveDescendantChanged
        #self.listeners["object:visible-changed"]                 = \
        #    self.onVisibleDataChanged
        #self.listeners["object:children-changed:"]               = \
        #    self.onChildrenChanged
        self.listeners["window:activate"]                        = \
            self.onWindowActivated
        #self.listeners["window:create"]                          = \
        #    self.onWindowCreated
        #self.listeners["window:destroy"]                         = \
        #    self.onWindowDestroyed
        #self.listeners["window:deactivated"]                     = \
        #    self.onWindowDeactivated
        #self.listeners["window:maximize"]                        = \
        #    self.onWindowMaximized
        #self.listeners["window:minimize"]                        = \
        #    self.onWindowMinimized
        #self.listeners["window:rename"]                          = \
        #    self.onWindowRenamed
        #self.listeners["window:restore"]                         = \
        #    self.onWindowRestored
        #self.listeners["window:switch"]                          = \
        #    self.onWindowSwitched
        #self.listeners["window:titlelize"]                       = \
        #    self.onWindowTitlelized
        self.listeners["focus:"]                                 = \
            self.onFocus
        

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # Ignore text insertions to non-focused objects, unless the
        # currently focused object is the parent of the object to which
        # text was inserted
        #
        if (event.source == orca.focusedObject) \
               or (event.source.parent == orca.focusedObject):
            brailleUpdateText(event.source)
            text = event.any_data
            if text.isupper():
                speech.say("uppercase", text)
            else:
                speech.say("default", text)


    def onTextDeleted(self, event):
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


    def onStateChanged(self, event):
        """Called whenever an object's state changes.  Currently, the
        state changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """
    
        global presenters
        global state_change_notifiers

        if event.source != orca.focusedObject:
            return

        # Should we present the object again?
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


    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """
    
        global presenters

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


    def onSelectionChanged(self, event):
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


    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # Magnify the object.  [[[TODO: WDW - this is a hack for now.]]]
        #
        #mag.magnifyAccessible(event.source)

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


    def onPropertyChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """
        pass


    def onActiveDescendantChanged(self, event):
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
        table = event.source.table
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


    def onWindowActivated(self, event):
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


    def onFocus(self, event):
        """Called whenever an object gets focus.
        
        Arguments:
        - event: the Event
        """
    
        global presenters

        # Magnify the object.  [[[TODO: WDW - this is a hack for now.  The
        # individual presenters should probably know what to do.  This raises
        # the possible issue, however, that we might need different presenters
        # for different modes (e.g., braille presenters, speech presenters,
        # magnification presentaters).]]]
        #
        #mag.magnifyAccessible(event.source)
    
        if presenters.has_key(event.source.role):
            p = presenters[event.source.role]
            try:
                p(event.source, False)
            except:
                debug.printException(debug.LEVEL_SEVERE)
        else:
            defaultPresenter(event.source, False)


########################################################################
#                                                                      #
# INFORMATION GATHERING UTILITIES                                      #
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

    action = obj.action

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
            label = obj.label
        text =  label + " " + getSpeechForRoleName(obj) + "."
        accel = getSpeechForAccelerator(obj)
        if len(accel) > 0:
            text = text + " " + accel

    if includeAvailability:
        text = text + " " + getSpeechForAvailability(obj) + "."
    
    text = text.replace("...", _(" dot dot dot"), 1)

    return text


########################################################################
#                                                                      #
# ACCESSIBLE TEXT OUTPUT FUNCTIONS                                     #
#                                                                      #
# Functions for handling output of AccessibleText objects to speech    #
# and Braille.                                                         #
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
        label = obj.label

    line = braille.Line()

    brltext = getShortBrailleForRoleName(obj) + " "
    line.addRegion(braille.Region(brltext))

    beginningOfText = len(brltext)
    result = a11y.getTextLineAtCaret(obj)
    brltext = result[0]    
    caretOffset = result[1]
    lineOffset = result[2]

    line.addRegion(braille.Text(obj, brltext, lineOffset, caretOffset))

    # Empty lines seem to wreak havoc on the offsets returned by
    # a11y.getTextLineAtCaret, so we trap for this.
    #
    braille.clear()
    braille.addLine(line)

    cursor = beginningOfText + caretOffset - lineOffset
    if cursor >= beginningOfText:
        braille.setCursor(cursor, 0)
    else:
        braille.setCursor(-1, -1)

    braille.refresh()
    

def sayLine(obj):
    """Speaks the line of an AccessibleText object that contains the
    caret. [[[TODO: WDW - what if the line is empty?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    # Get the AccessibleText interface of the provided object
    #
    result = a11y.getTextLineAtCaret(obj)
    speech.say("default", result[0])
    

def sayWord(obj):
    """Speaks the word at the caret.  [[[TODO: WDW - what if there is no
    word at the caret?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    text = obj.text
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
    
    text = obj.text
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

    line = braille.Line()
    line.addRegion(braille.Region(getShortBrailleForRoleName(obj) + " "))
    componentRegion = braille.Component(obj)
    line.addRegion(componentRegion)
    line.addRegion(braille.Region(" " + getBrailleForAccelerator(obj)))
    
    braille.clear()
    braille.addLine(line)
    braille.setFocus(componentRegion)
    braille.refresh()    
    
    speech.say("default", getSpeech(obj))


def pushButtonPresenter(obj, already_focused):
    """Speaks a button and displays it on the Braille display.
    
    Arguments:
    - obj: the Accessible button
    - already_focused: if False, the obj just received focus
    """

    debugPresenter("default.pushButtonPresenter", obj, already_focused)
    
    line = braille.Line()
    line.addRegion(braille.Region(getShortBrailleForRoleName(obj) + " "))
    buttonRegion = braille.Component(obj)
    line.addRegion(buttonRegion)
    line.addRegion(braille.Region(" " + getBrailleForAccelerator(obj)))

    braille.clear()
    braille.addLine(line)
    braille.setFocus(buttonRegion)
    braille.refresh()
    
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

    line = braille.Line()
    
    # If the checkbox is checked, indicate this in speech and Braille
    #
    set = obj.state
    if set.count(core.Accessibility.STATE_CHECKED):
        # If it's not already focused, say it's name
        #
        if already_focused == False:
            text = obj.label + " " \
                   + getSpeechForRoleName(obj) + ". " \
                   + _("checked") + ". " \
                   + getSpeechForAccelerator(obj)
        else:
            text = _("checked") + "."
    else:
        if already_focused == False:
            text = obj.label + " " \
                   + getSpeechForRoleName(obj) + ". " \
                   + _("not checked") + "." \
                   + getSpeechForAccelerator(obj)
        else:
            text = _("not checked") + "."

    line.addRegion(braille.Region(getShortBrailleForRoleName(obj) + " "))
    toggleRegion = braille.ToggleButton(obj)
    line.addRegion(toggleRegion)
    line.addRegion(braille.Region(" " + getBrailleForAccelerator(obj)))
    
    braille.clear()
    braille.addLine(line)
    braille.setFocus(toggleRegion)
    braille.refresh()
    
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
    label = obj.label
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
        groupName = group.label
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
                    brltext = brltext + "(7 " + child.label + ")"
                else:
                    brltext = brltext + "(' " + child.label + ")"
            i = i + 1
    else:
        cursor = len(brltext) + 2
        set = obj.state
        if set.count(core.Accessibility.STATE_CHECKED):
            brltext = brltext + "7" + " " + obj.label
        else:
            brltext = brltext + "'" + " " + obj.label
        brltext = brltext + " " + getBrailleForAccelerator(obj)
 
    if cursor == -1:
        debug.println(debug.LEVEL_SEVERE,
                      "ERROR: Did not find self (" + obj.label + \
                      ") in its own radio button group!")
        
    braille.displayMessage(brltext, cursor)
        
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

    line = braille.Line()
    line.addRegion(braille.Region(getShortBrailleForRoleName(obj) + " "))

    selectedMenu = None
    selection = obj.selection
    childCount = obj.childCount
    i = 0
    while i < childCount:
        label = obj.child(i).label
        text = text + ", " + label
        menuRegion = braille.Component(obj.child(i))
        line.addRegion(menuRegion)
        if i < (childCount - 1):
            line.addRegion(braille.Region(" _ "))
        if selection and selection.isChildSelected(i):
            selectedMenu = menuRegion
        i = i + 1
        
    braille.clear()
    braille.addLine(line)
    braille.setFocus(selectedMenu)
    braille.refresh()
    
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
    # own region on the Braille display.  NOTE: we will only display
    # the contents of a submenu if the submenu is actually showing; we
    # do this by determining if any items in the submenu are selected
    # [[[WDW - this is a little hacky, I think.]]]
    #
    if obj.role == rolenames.ROLE_MENU:
        menu = obj
        selection = menu.selection
        if not selection or (selection and selection.nSelectedChildren == 0):
            menu = obj.parent
    else:
        menu = obj.parent

    if menu is None:
        debug.println(debug.LEVEL_SEVERE, "No menu found for " \
                      + obj.label)
        return
    
    line = braille.Line()
    line.addRegion(braille.Region(getShortBrailleForRoleName(menu) + " "
                                  + menu.label + " "))

    selectedItem = None
    selection = menu.selection
    childCount = menu.childCount
    i = 0
    while i < childCount:
        child = menu.child(i)
        if child.role != rolenames.ROLE_SEPARATOR \
            and child.state.count(core.Accessibility.STATE_SENSITIVE):
            
            if child.role == rolenames.ROLE_CHECK_MENU_ITEM:
                region = braille.ToggleButton(child)
            elif child.role == rolenames.ROLE_RADIO_MENU_ITEM:
                region = braille.RadioButton(child)
            elif child.role == rolenames.ROLE_TEAR_OFF_MENU_ITEM:
                region = braille.Component(child, _("___"))
            elif child.role == rolenames.ROLE_MENU:
                region = braille.Component(
                    child, "o " + child.label)
            else:
                region = braille.Component(child)

            line.addRegion(region)
            if i < (childCount - 1):
                line.addRegion(braille.Region(" _ "))

            if selection and selection.isChildSelected(i):
                selectedItem = region
                
        i = i + 1

    braille.clear()
    braille.addLine(line)
    braille.setFocus(selectedItem)
    braille.refresh()
    
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

    value = obj.value

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
        text = obj.label + " " + getSpeechForRoleName(obj) + ". " \
               + _("Value: %s") % valueString + ". " \
               + _("Minimum value: %s") % minString + ". " \
               + _("Maximum value: %s") % maxString + ". " \
               + getSpeechForAccelerator(obj)

    brltext = getShortBrailleForRoleName(obj) + " " + obj.label \
              + " " + "(%s %s %s)" % (minString, valueString, maxString)

    braille.displayMessage(brltext + " " + getBrailleForAccelerator(obj))
    
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

    line = braille.Line()
    line.addRegion(braille.Region(getShortBrailleForRoleName(tablist) + " "))
    
    selected = obj.index
    selectedTab = None
    childCount = tablist.childCount    
    i = 0
    while i < childCount:
        tabRegion = braille.Component(tablist.child(i))
        line.addRegion(tabRegion)
        if i < (childCount - 1):
            line.addRegion(braille.Region(" _ "))
        if i == selected:
            selectedTab = tabRegion
        i = i + 1

    braille.clear()
    braille.addLine(line)
    braille.setFocus(selectedTab)
    braille.refresh()
    
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
    result = a11y.getTextLineAtCaret(obj)
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
    
    label = obj.label
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
    comboSelection = obj.selection
    if comboSelection and comboSelection.nSelectedChildren > 0:
        selectedItem = a11y.makeAccessible(comboSelection.getSelectedChild(0))

    result = a11y.getTextLineAtCaret(obj)
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
                label = item.label
                if item == selectedItem \
                       or label == selectedText:
                    cursor = len(brltext) + 2
                brltext = brltext + "(" + label + ")"
                j = j + 1
        i = i + 1

    if already_focused:
        text = ""

    if textObj:
        result = a11y.getTextLineAtCaret(textObj)
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
        text = text + selectedItem.label + "."
    elif len(selectedText) > 0:
        text = text + selectedText + "."
    else:
        debug.println(debug.LEVEL_SEVERE,
                      "ERROR: Could not find selected item for combo box.")

    braille.displayMessage(brltext, cursor)
    
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
                   obj.label + " " + getSpeechForRoleName(obj) \
                   + ". ")

    # Get the selected rows of the table
    #
    table = obj.table
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
                    #for line in cell.name.splitlines():
                    #    brl.addRegion(line, len(line)+2, 0)
            col = col+1

    # Put the text on the Braille display
    #
    braille.displayMessage(text)
    speech.say("default", text)


def dialogPresenter(obj, already_focused):
    """Speaks the title of the dialog and displays it on the Braille display.
    Also reads the contents of labels inside the dialog that are not
    associated with any other objects.

    Arguments:
    - obj: the Accessible dialog
    - already_focused: if False, the obj just received focus
    """
    
    debugPresenter("default.dialogPresenter", obj, already_focused)
    
    text = obj.label
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
            
    braille.displayMessage(text)
    
    speech.say("default", text)


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

def sayAgain(inputEvent):
    """Tells speech to repeat what was last spoken.
        
    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """
    
    speech.sayAgain()
    
    return True
    
    
def sayAll(inputEvent):
    """Initiates sayAll mode and attempts to say all the text of the
    currently focused Accessible text object.  [[[TODO: WDW - the entire
    sayAll mechanism is likely to be severely broken.]]]
    
    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """
    
    global sayAllText
    global sayAllPosition

    # If the focused object isn't text, we don't know how to read it
    #
    txt = None
    try:
        txt = orca.focusedObject.text
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

    return True


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


########################################################################
#                                                                      #
# VARIOUS DICTIONARIES TO HELP DRIVE THINGS.                           #
#                                                                      #
########################################################################

# Dictionary that maps role names to the presenter functions for those roles.
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


# Dictionary that defines the presenters which should be called when various
# states change for various types of objects.  The key represents the role and
# the value represents a list of states that we care about.
#
state_change_notifiers = {}
state_change_notifiers["check box"] = ("checked", None)
state_change_notifiers["toggle button"] = ("checked", None)


# Dictionary that defines which presenters should be used if an object's
# selection changes.  The key represents the role and the value represents the
# presenter function.
#
selection_changed_handlers = {}
selection_changed_handlers["combo box"]  = comboBoxPresenter
selection_changed_handlers["table"]      = tablePresenter
selection_changed_handlers["tree table"] = tablePresenter
