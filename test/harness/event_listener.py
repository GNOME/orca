# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Listens for events and spits them out.
"""

import time

import gobject
import Queue
import CORBA

import bonobo
import ORBit

ORBit.load_typelib("Accessibility")
ORBit.CORBA.ORB_init()

import Accessibility
import Accessibility__POA

listeners = []
keystrokeListeners = []

registry = bonobo.get_object("OAFIID:Accessibility_Registry:1.0",
                             "Accessibility/Registry")

gidleId = 0
queue   = Queue.Queue(0)

########################################################################
#                                                                      #
# Event listener classes for global and keystroke events               #
#                                                                      #
########################################################################

class EventListener(Accessibility__POA.EventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given event type.  Most users of this module will not use this
    class directly, but will instead use the addEventListener method.
    """

    def __init__(self, registry, callback, eventType):
        self.registry  = registry
        self.callback  = callback
        self.eventType = eventType
        self.count     = 0
        self.register()

    def ref(self): pass

    def unref(self): pass

    def queryInterface(self, repo_id):
	thiz = None
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            thiz = self._this()
	return thiz

    def register(self):
        self._default_POA().the_POAManager.activate()
        self.registry.registerGlobalEventListener(self._this(),
                                                  self.eventType)
        self.__registered = True
        return self.__registered

    def deregister(self):
        if not self.__registered:
            return
        self.registry.deregisterGlobalEventListener(self._this(),
                                                    self.eventType)
        self.__registered = False

    def notifyEvent(self, event):
        global queue
        global gidleId

        if event.source:
            event.source.ref()

        queue.put(event)
        if not gidleId:
            gidleId = gobject.idle_add(notifyObjectEvent)
        
    def __del__(self):
        self.deregister()

class KeystrokeListener(Accessibility__POA.DeviceEventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given keystroke.  Most users of this module will not use this
    class directly, but will instead use the registerKeystrokeListeners
    method."""

    def __init__(self, registry, callback,
                 keyset, mask, type, synchronous, preemptive, isGlobal):
        self._default_POA().the_POAManager.activate()

        self.registry         = registry
        self.callback         = callback
        self.keyset           = keyset
        self.mask             = mask
        self.type             = type
        self.mode             = Accessibility.EventListenerMode()
        self.mode.synchronous = synchronous
        self.mode.preemptive  = preemptive
        self.mode._global     = isGlobal
        self.register()

    def ref(self): pass

    def unref(self): pass

    def queryInterface(self, repo_id):
	thiz = None
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            thiz = self._this()
	return thiz

    def register(self):
        d = self.registry.getDeviceEventController()
        if d.registerKeystrokeListener(self._this(),
                                       self.keyset,
                                       self.mask,
                                       self.type,
                                       self.mode):
            self.__registered = True
        else:
            self.__registered = False
        return self.__registered

    def deregister(self):
        if not self.__registered:
            return
        d = self.registry.getDeviceEventController()
        d.deregisterKeystrokeListener(self._this(),
                                      self.keyset,
                                      self.mask,
                                      self.type)
        self.__registered = False

    def notifyEvent(self, event):
        """Called by the at-spi registry when a key is pressed or released.

        Arguments:
        - event: an at-spi DeviceEvent

        Returns True if the event has been consumed.
        """
        return self.callback(event)

    def __del__(self):
        self.deregister()

########################################################################
#                                                                      #
# Testing functions.                                                   #
#                                                                      #
########################################################################

def start():
    """Starts event notification with the AT-SPI Registry.  This method
    only returns after 'stop' has been called.
    """
    bonobo.main()

def stop():
    """Unregisters any event or keystroke listeners registered with
    the AT-SPI Registry and then stops event notification with the
    AT-SPI Registry.
    """
    for listener in (listeners + keystrokeListeners):
        listener.deregister()
    bonobo.main_quit()

def registerEventListener(callback, eventType):
    global listeners
    listener = EventListener(registry, callback, eventType)
    listeners.append(listener)

def registerKeystrokeListeners(callback):
    """Registers a single callback for all possible keystrokes.
    """
    global keystrokeListeners
    for i in range(0, (1 << (Accessibility.MODIFIER_NUMLOCK + 1))):
        keystrokeListeners.append(
            KeystrokeListener(registry,
                              callback, # callback
                              [],       # keyset
                              i,        # modifier mask
                              [Accessibility.KEY_PRESSED_EVENT,
                               Accessibility.KEY_RELEASED_EVENT],
                              True,     # synchronous
                              True,     # preemptive
                              False))   # global

########################################################################
#                                                                      #
# Helper utilities.                                                    #
#                                                                      #
########################################################################

def getStateString(acc):
    """Returns a space-delimited string composed of the given object's
    Accessible state attribute.  This is for debug purposes.
    """

    if not acc:
        return "None"
    
    s = acc.getState()
    s = s._narrow(Accessibility.StateSet)
    stateSet = s.getStates()
    
    stateString = " "
    if stateSet.count(Accessibility.STATE_INVALID):
        stateString += "INVALID "
    if stateSet.count(Accessibility.STATE_ACTIVE):
        stateString += "ACTIVE "
    if stateSet.count(Accessibility.STATE_ARMED):
        stateString += "ARMED "
    if stateSet.count(Accessibility.STATE_BUSY):
        stateString += "BUSY "
    if stateSet.count(Accessibility.STATE_CHECKED):
        stateString += "CHECKED "
    if stateSet.count(Accessibility.STATE_COLLAPSED):
        stateString += "COLLAPSED "
    if stateSet.count(Accessibility.STATE_DEFUNCT):
        stateString += "DEFUNCT "
    if stateSet.count(Accessibility.STATE_EDITABLE):
        stateString += "EDITABLE "
    if stateSet.count(Accessibility.STATE_ENABLED):
        stateString += "ENABLED "
    if stateSet.count(Accessibility.STATE_EXPANDABLE):
        stateString += "EXPANDABLE "
    if stateSet.count(Accessibility.STATE_EXPANDED):
        stateString += "EXPANDED "
    if stateSet.count(Accessibility.STATE_FOCUSABLE):
        stateString += "FOCUSABLE "
    if stateSet.count(Accessibility.STATE_FOCUSED):
        stateString += "FOCUSED "
    if stateSet.count(Accessibility.STATE_HAS_TOOLTIP):
        stateString += "HAS_TOOLTIP "
    if stateSet.count(Accessibility.STATE_HORIZONTAL):
        stateString += "HORIZONTAL "
    if stateSet.count(Accessibility.STATE_ICONIFIED):
        stateString += "ICONIFIED "
    if stateSet.count(Accessibility.STATE_MODAL):
        stateString += "MODAL "
    if stateSet.count(Accessibility.STATE_MULTI_LINE):
        stateString += "MULTI_LINE "
    if stateSet.count(Accessibility.STATE_MULTISELECTABLE):
        stateString += "MULTISELECTABLE "
    if stateSet.count(Accessibility.STATE_OPAQUE):
        stateString += "OPAQUE "
    if stateSet.count(Accessibility.STATE_PRESSED):
        stateString += "PRESSED "
    if stateSet.count(Accessibility.STATE_RESIZABLE):
        stateString += "RESIZABLE "
    if stateSet.count(Accessibility.STATE_SELECTABLE):
        stateString += "SELECTABLE "
    if stateSet.count(Accessibility.STATE_SELECTED):
        stateString += "SELECTED "
    if stateSet.count(Accessibility.STATE_SENSITIVE):
        stateString += "SENSITIVE "
    if stateSet.count(Accessibility.STATE_SHOWING):
        stateString += "SHOWING "
    if stateSet.count(Accessibility.STATE_SINGLE_LINE):
        stateString += "SINGLE_LINE "
    if stateSet.count(Accessibility.STATE_STALE):
        stateString += "STALE "
    if stateSet.count(Accessibility.STATE_TRANSIENT):
        stateString += "TRANSIENT "
    if stateSet.count(Accessibility.STATE_VERTICAL):
        stateString += "VERTICAL "
    if stateSet.count(Accessibility.STATE_VISIBLE):
        stateString += "VISIBLE "
    if stateSet.count(Accessibility.STATE_MANAGES_DESCENDANTS):
        stateString += "MANAGES_DESCENDANTS "
    if stateSet.count(Accessibility.STATE_INDETERMINATE):
        stateString += "INDETERMINATE "

    return "'%s'" % stateString.strip()

def getName(acc):
    if acc and acc.name:
        return "'%s'" % acc.name
    else:
        return "None"

def getRoleName(acc):
    if acc:
        return "'%s'" % acc.getRoleName()
    else:
        return "None"

def getAppName(acc):
    try:
        parent = acc
        while parent.parent and (parent != parent.parent):
            parent = parent.parent
        return "'%s'" % parent.name
    except:
        return "None"
    
def toString(acc):
    return "app=%s name=%s role=%s state=%s" \
           % (getAppName(acc), \
              getName(acc), \
              getRoleName(acc), \
              getStateString(acc))

eventTypes = [
    "focus:",
    "window:",
    "object:property-change",
    "object:state-changed",
    "object:selection-changed",
    "object:children-changed"
    "object:active-descendant-changed"
    "object:visible-data-changed"
    "object:text-selection-changed",
    "object:text-caret-moved",
    "object:text-changed",
    "object:column-inserted",
    "object:row-inserted",
    "object:column-reordered",
    "object:row-reordered",
    "object:column-deleted",
    "object:row-deleted",
    "object:model-changed",
    "object:link-selected",
    "object:bounds-changed",
]

def notifyObjectEvent():
    global queue
    global gidleId
    
    event = queue.get()
    
    try:
        print event.type, event.detail1, event.detail2, toString(event.source)
    except CORBA.COMM_FAILURE:
        pass
    
    try:    
        if event.source:
            event.source.unref()
    except CORBA.COMM_FAILURE:
        pass
    
    if queue.empty():
        gidleId = 0
        return False
    else:
        return True

def notifyKeystroke(event):
    print "keystroke type=%d hw_code=%d modifiers=%d event_string=(%s) " \
          "is_text=%s" \
          % (event.type, event.hw_code, event.modifiers, event.event_string,
             event.is_text)
    if event.event_string == "F12": 
        shutdownAndExit()
    return False

def shutdownAndExit(signum=None, frame=None):
    stop()

def test():
    for eventType in eventTypes:
        registerEventListener(notifyObjectEvent, eventType)
    registerKeystrokeListeners(notifyKeystroke)
    start()

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    test()
