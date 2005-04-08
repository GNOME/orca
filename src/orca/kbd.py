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

"""Provides support for registering and handling keyboard events.
All keyboard events are chanelled through KeyStrokeListener instances.
These instances maintain a function pointer to call when their
notifyEvent method is called by the at-spi registry.  This function
is expected to handle the keyboard event and return True if they
have consumed the event.

For the purposes of orca, this module provides an onKeyEvent function
that serves as the sole function pointer for all KeyStrokeListener
instances.  This module also maintains a dictionary named
"keybindings" that provides a mapping from a keyboard event to a
function pointer.  Orca will replace the "keybindings" dictionary
with the keybindings from a script when the script becomes active.

This modules also maintains a "lastKey" attribute which is a string
that describes the last key event typed by the user.  This is sometimes
used by scripts to determine what keyboard actions may have caused an
at-spi event.
"""

import debug
import core
import a11y
import settings
import speech
import brl

# Dictionary representing the keybindings.  Orca is expected to replace
# this dictionary each time a new script is activated (using the keybindings
# defined in the script).  The keys to the dictionary represent the keystring
# that is assembled from a keyboard event, and the values represent function
# pointers to call when the matching keystring is received.
#
keybindings = {}

# A string representing the last key event that was received.  Scripts may
# use this as a "hint" to help determine why at-spi events have been received.
#
lastKey = None

# A boolean representing whether the insert key has been pressed or not.
# [[[TODO: WDW - Orca treats the insert key specially, but I'm not quite
# sure why.]]]
#
insertPressed = False

# A list of the various listeners we have registered with the at-spi
# registry.
#
listeners = None

# If True, this module has been initialized.
#
initialized = False


class KeystrokeListener (core.Accessibility__POA.DeviceEventListener):
    """Encapsulates all the information associated with at-spi key
    listeners.  [[[TODO: MM - Currently, under the covers, this class
    uses at-spi's toolkit listeners, but this could be changed if/when
    XEvIE becomes widely available.]]] [[[TODO: WDW - we definitely
    should consider moving to XEvIE when it's available.  The main reason
    is that it can help us when we come across inaccessible apps.  For
    example, assume I have some global keybindings set for orca and I
    give focus to a non-at-spi app such as emacs.  My key events will
    no longer be intercepted by GTK.  As a result, my global orca bindings
    will not be interpreted and I might end up inadvertently entering
    data into my emacs window.]]]
    """
    
    def __init__(self,  func, mask, preemptive, isGlobal):
        """Creates a new KeystrokeListener.

        Arguments:
        - func:       Function pointer to call when a keyboard event is
                      called. This function will be passed the event
                      directly, and is expected to return True if it has
                      consumed the event (and the preemptive flag is True).
        - mask:       Keyboard modifiers for filtering the events
        - preemptive: If True, the function will receive the key events
                      via synchronous calls from the at-spi registry and
                      is expected to return True if it has consumed the
                      event.
        - isGlobal:   [[[TODO: WDW - not quite sure.]]]
        """
        
        self.mask = mask
        self.keyset = []
        self.type = [core.Accessibility.KEY_PRESSED_EVENT,
                     core.Accessibility.KEY_RELEASED_EVENT]
        self.mode = core.Accessibility.EventListenerMode ()
        self.mode.preemptive = preemptive
        self.mode.synchronous = preemptive
        self.mode._global = isGlobal
        self.func = func


    def notifyEvent (self, event):
        """Called by the at-spi registry when a key is pressed or released.

        Arguments:
        - event: an at-spi DeviceEvent

        Returns True if the event has been consumed.
        """

        return self.func (event)


    def register (self):
        """Registers this listener with the at-spi registry.
        """
        
        global registry

        # [[[TODO: MM - This seems to always throw an exception, even
        # when it works, so we put it in a try catch block.  WDW - is
        # it possible that this happens because the keyset is empty?]]]
        # 
        try:
            d = core.registry.getDeviceEventController ()
            d.registerKeystrokeListener (self._this(), 
                                         self.keyset, 
                                         self.mask, 
                                         self.type, 
                                         self.mode)
        except:
            pass


    def deregister (self):
        """Deregisters this listener with the at-spi registry.
        """
        
        global registry

        # [[[TODO: MM - This seems to always throw an exception, even
        # when it works, so we put it in a try catch block.  WDW - is
        # it possible that this happens because the keyset is empty?]]]
        # 
        try:
            d = core.registry.getDeviceEventController ()
            d.deregisterKeystrokeListener (self._this(), 
                                           self.keyset, 
                                           self.mask, 
                                           self.type)
        except:
            pass


def getModifierString (modifier):
    """Converts a set of modifer states into a text string

    Arguments:
    - modifer: the modifiers field from an at-spi DeviceEvent

    Returns a string consisting of modifier names separated by "+"'s.
    """
    
    s = ""
    l = []

    # [[[TODO: WDW - need to consider all modifiers: SHIFT, SHIFTLOCK,
    # NUMLOCK, META, META2, META3.  Some of these may be handled via the
    # actual key symbol (e.g., upper or lower case), but others may not.]]]
    #
    if insertPressed:
        l.append ("insert")
    if modifier & (1<<core.Accessibility.MODIFIER_CONTROL):
        l.append ("control")
    if modifier & (1<<core.Accessibility.MODIFIER_ALT):
        l.append ("alt")
    for mod in l:
        if s == "":
            s = mod
        else:
            s = s + "+" + mod
    return s


def keyEcho (key):
    """If the keyEcho setting is enabled, echoes the key via speech.
    Uppercase keys will be spoken using the "uppercase" voice style,
    whereas lowercase keys will be spoken using the "default" voice style.

    Arguments:
    - key: a string representing the key name to echo.
    """
    
    if not getattr (settings, "keyEcho", False):
        return
    if key.isupper ():
        speech.say ("uppercase", key)
    else:
        speech.say ("default", key)



# This function is called whenever a key is pressed - It is called by
# our event listener which is listening to at-spi key events

def onKeyEvent (event):
    """The primary key event handler for orca.  Keeps track of various
    attributes, such as the lastKey and insertPressed.  Also calls
    keyEcho as well as any function that may exist in the keybindings
    dictionary for the key event.  This method is called synchronously
    from the at-spi registry and should be performant.  In addition, it
    must return True if it has consumed the event (and False if not).
    
    Arguments:
    - event: an at-spi DeviceEvent

    Returns True if the event should be consumed.
    """
    
    global lastKey
    global insertPressed
    global keybindings

    keystring = ""

    if event.type == core.Accessibility.KEY_PRESSED_EVENT:
        if event.event_string == "KP_Insert":
            insertPressed = True
        else:
            mods = getModifierString (event.modifiers)
            if mods:
                keystring = mods + "+" + event.event_string
            else:
                keystring = event.event_string

            # Key presses always interrupt speech - If say all mode is
            # enabled, a key press stops it
            #
            if speech.sayAllEnabled:
                speech.stopSayAll ()
            else:
                speech.stop ("default")

            # Key presses clear the Braille display
            # [[[TODO:  WDW - is this what we want?]]]
            #
            if getattr (settings, "useBraille", False):
                brl.clear ()
    else:
        if event.event_string == "KP_Insert":
            insertPressed = False
            
    if keystring:
        lastKey = keystring
        debug.println (debug.LEVEL_INFO, "Key Event: " + keystring)
        keyEcho (keystring)

        # Execute a key binding if we have one
        #
        if keybindings.has_key (keystring):
            func = keybindings[keystring]
            try:
                return func ()
            except:
                debug.printException (debug.LEVEL_SEVERE)
                
        return False


def init ():
    """Initializes this module and registers keystroke listeners for
    a complete set of keyboard events from the at-spi.

    Returns True if the intialization procedure was run or False if the
    module has already been initialized.
    """
    
    global initialized
    global listeners

    if initialized:
        return False
    
    listeners = []
    i = 0
    while i <= (1<<core.Accessibility.MODIFIER_NUMLOCK):
        kl = KeystrokeListener (onKeyEvent, i, True, False)
        kl.register ()
        listeners.append (kl)
        i = i+1
        
    initialized = True
    return True


def shutdown ():
    """Unregisters all event listeners from the at-spi registry and
    resets the initialized state to False.

    Returns True if the shutdown procedure has run or False if this
    module has not yet been initialized.
    """
    
    global initialized
    global insertPressed
    global listeners

    if not initialized:
        return False

    for l in listeners:
        l.deregister ()
    del listeners

    insertPressed = False
    initialized = False

    return True
