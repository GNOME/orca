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
import braillegenerator
import core
import debug
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.]]]
import orca
import rolenames
import speech
import speechgenerator

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
        
        self.brailleGenerator = braillegenerator.BrailleGenerator()
        self.speechGenerator = speechgenerator.SpeechGenerator()


    def updateBraille(self, obj):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        """

        braille.clear()

        line = braille.Line()
        
        line.addRegions(self.brailleGenerator.getBrailleContext(obj))
        
        result = self.brailleGenerator.getBrailleRegions(obj)
        line.addRegions(result[0])
        
        braille.addLine(line)
        
        braille.setFocus(result[1])

        braille.refresh()    
    
        
    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

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
            self.updateBraille(event.source)
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
            self.updateBraille(event.source)

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
    
        global state_change_notifiers

        if event.source != orca.focusedObject:
            return

        self.updateBraille(event.source)
        
        # Should we speak the object again?
        #
        if state_change_notifiers.has_key(event.source.role):
            notifiers = state_change_notifiers[event.source.role]
            found = False
            for state in notifiers:
                if state and event.type.endswith(state):
                    found = True
                    break
            if found:
                speech.say("default",
                           self.speechGenerator.getSpeech(event.source, True))

        
    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """
    
        if event.source != orca.focusedObject:
            return

        self.updateBraille(event.source)
        speech.say("default",
                   self.speechGenerator.getSpeech(event.source, True))
            

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """
    
        # Do we care?
        #
        if selection_changed_handlers.has_key(event.source.role):
            self.updateBraille(event.source)
            speech.say("default",
                       self.speechGenerator.getSpeech(event.source, True))


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
        self.updateBraille(event.source)

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

        self.updateBraille(event.source)
        speech.say("default",
                   self.speechGenerator.getSpeech(event.source, True))
            

    def onFocus(self, event):
        """Called whenever an object gets focus.
        
        Arguments:
        - event: the Event
        """
    
        self.updateBraille(event.source)
        speech.say("default",
                   self.speechGenerator.getSpeech(event.source, True))


########################################################################
#                                                                      #
# ACCESSIBLE TEXT OUTPUT FUNCTIONS                                     #
#                                                                      #
# Functions for handling output of AccessibleText objects to speech.   #
#                                                                      #
########################################################################

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


# Dictionary that defines the state changes we care about for various
# objects.  The key represents the role and the value represents a list
# of states that we care about.
#
state_change_notifiers = {}
state_change_notifiers["check box"] = ("checked", None)
state_change_notifiers["toggle button"] = ("checked", None)


# Dictionary that defines which objects we care about if an object's
# selection changes.
#
selection_changed_handlers = {}
selection_changed_handlers["combo box"]  = True
selection_changed_handlers["table"]      = True
selection_changed_handlers["tree table"] = True
