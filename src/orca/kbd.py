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
"""

import core

# A list of the various listeners we have registered with the at-spi
# registry.
#
listeners = None

# If True, this module has been initialized.
#
initialized = False


class KeystrokeListener(core.Accessibility__POA.DeviceEventListener):
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
        self.mode = core.Accessibility.EventListenerMode()
        self.mode.preemptive = preemptive
        self.mode.synchronous = preemptive
        self.mode._global = isGlobal
        self.func = func


    def ref(self): pass
    

    def unref(self): pass
    

    def queryInterface(self, repo_id):
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            return self._this()
        else:
            return None


    def notifyEvent(self, event):
        """Called by the at-spi registry when a key is pressed or released.

        Arguments:
        - event: an at-spi DeviceEvent

        Returns True if the event has been consumed.
        """

        return self.func(event)


    def register(self):
        """Registers this listener with the at-spi registry.
        """
        
        global registry

        self._default_POA().the_POAManager.activate()
        d = core.registry.getDeviceEventController()
        d.registerKeystrokeListener(self._this(), 
                                    self.keyset, 
                                    self.mask, 
                                    self.type, 
                                    self.mode)


    def deregister(self):
        """Deregisters this listener with the at-spi registry.
        """
        
        global registry

        d = core.registry.getDeviceEventController()
        d.deregisterKeystrokeListener(self._this(), 
                                      self.keyset, 
                                      self.mask, 
                                      self.type)


def init(onKeyEvent):
    """Initializes this module and registers keystroke listeners for
    a complete set of keyboard events from the at-spi.

    Arguments:
    - onKeyEvent: function to call on keyboard events

    Returns True if the intialization procedure was run or False if the
    module has already been initialized.
    """
    
    global initialized
    global listeners

    if initialized:
        return False
    
    listeners = []
    i = 0
    while i <= (1 << core.Accessibility.MODIFIER_NUMLOCK):
        kl = KeystrokeListener(onKeyEvent, i, True, False)
        kl.register()
        listeners.append(kl)
        i = i + 1
        
    initialized = True
    return True


def shutdown():
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
        l.deregister()
    del listeners

    insertPressed = False
    initialized = False

    return True
