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

# Accessibility support

import core
import a11y

# User settings

import settings

# Speech support

import speech

# Braille support

import brl

# KeystrokeListener class - This class encapsulates all the information associated with at-spi key listeners.  Currently, under the covers, this class uses at-spi's toolkit listeners, but this could be changed if/when XEvIE becomes widely available.

class KeystrokeListener (core.Accessibility__POA.DeviceEventListener):

    # KeystrokeListener constructor

    def __init__(self,  func, mask, preemptive, isGlobal):
        self.mask = mask
        self.keyset = []
        self.type = [core.Accessibility.KEY_PRESSED_EVENT, core.Accessibility.KEY_RELEASED_EVENT]

        # Initialize mode manually since one of its member is named
        # 'global' and that's a keyword

        self.mode = core.Accessibility.EventListenerMode ()
        self.mode.preemptive = preemptive
        self.mode.synchronous = preemptive
        self.mode._global = isGlobal
        self.func = func

    # This function is called by the at-spi registry when a key is
    # presed

    def notifyEvent (self, event):
        return self.func (event)

    # Register the listener with at-spi

    def register (self):
        global registry

        # This seems to always throw an exception, even when it works,
        # so we put it in a try catch block

        try:
            d = core.registry.getDeviceEventController ()
            d.registerKeystrokeListener (self._this(), \
                                         self.keyset, \
                                         self.mask, \
                                         self.type, \
                                         self.mode)
        except:
            pass

    # deregister the event listener with at-spi

    def deregister (self):
        global registry

        # This seems to always throw an exception, even when it works,
        # so we put it in a try catch block

        try:
            d = core.registry.getDeviceEventController ()
            d.deregisterKeystrokeListener (self._this(), \
                                           self.keyset, \
                                           self.mask, \
                                           self.type)
        except:
            pass

# Track the state of the numpad insert key

insertPressed = False

# This function converts modifier states into a text string so
# defining hotkeys is easier

def getModifierString (modifier):
    s = ""
    l = []

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

# This function is called whnever a key is pressed - It is passed as
# it's only argument a string representation of the key which was pressed

def keyEcho (key):
    if not settings.keyEcho:
        return
    if key.isupper ():
        speech.say ("uppercase", key)
    else:
        speech.say ("default", key)

# The active key bindings

keybindings = {}

# Maintain a record of the last key pressed

lastKey = None

# This function is called whenever a key is pressed - It is called by
# our event listener which is listening to at-spi key events

def onKeyEvent (event):
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

            if speech.sayAllEnabled:
                speech.stopSayAll ()
            else:
                speech.stop ("default")

            # Key presses clear the Braille display

            if settings.useBraille:
                brl.clear ()
    else:
        if event.event_string == "KP_Insert":
            insertPressed = False
    if keystring:
        lastKey = keystring
        keyEcho (keystring)

        # Execute a key binding if we have one

        try:
            func = keybindings[keystring]
        except:
            func = None
        if func:
            return func ()
    return False

# In order to intercept all keys, we have to register tons and tons
# and tons of listeners

listeners = None

# Keyboard support initialized

initialized = False

def init ():
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

# Shutdown the keyboard hooks

def shutdown ():
    global initialized
    global insertPressed
    global listeners

    if not initialized:
        return False

    # Reset the insertPressed flag

    insertPressed = False

    for l in listeners:
        l.deregister ()
    del listeners
    initialized = False
    return True
