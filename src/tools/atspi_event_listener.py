# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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

"""Bare bones direct access to the AT-SPI Registry.  Registers for
keyboard events and global events, printing them out when it sees
them.  Press F12 to quit."""

import sys
import bonobo
import ORBit

ORBit.load_typelib("Accessibility")
ORBit.CORBA.ORB_init()

import Accessibility
import Accessibility__POA

__registry=None
__listeners=[]
__keystrokeListeners=[]

def getRegistry():
    global __registry
    if __registry is None:
        __registry = bonobo.get_object("OAFIID:Accessibility_Registry:1.0",
                                       "Accessibility/Registry")
    return __registry

def printAncestors(child):
    parent = child.parent
    while parent:
        print "   ", parent.name, parent.getRoleName()
        parent = parent.parent
        
def listApps():
    registry = getRegistry()
    print "There are %d desktops" % registry.getDesktopCount()
    for i in range(0,registry.getDesktopCount()):
        desktop = registry.getDesktop(i)
        print "  Desktop %d (name=%s) has %d apps" \
              % (i, desktop.name, desktop.childCount)
        for j in range(0, desktop.childCount):
            app = desktop.getChildAtIndex(j)
            print "    App %d: name=%s role=%s" % (j, app.name, app.getRole())

def keyEventToString(event):
    return "keystroke type=%d hw_code=%d modifiers=%d event_string=(%s) " \
           "is_text=%s" \
           % (event.type, event.hw_code, event.modifiers, event.event_string,
              event.is_text)

class EventListener(Accessibility__POA.EventListener):
    def __init__(self, eventType):
        self._default_POA().the_POAManager.activate()
        registry = getRegistry()
        registry.registerGlobalEventListener(self._this(), eventType)
        self.eventType = eventType
        self.__registered = True
        
    def ref(self): pass
    
    def unref(self): pass
    
    def queryInterface(self, repo_id):
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            return self._this()
        else:
            return None

    def deregister(self):
        if not self.__registered:
            return
        registry = getRegistry()
        registry.deregisterGlobalEventListener(self._this(), self.eventType)
        self.__registered = False
        
    def notifyEvent(self, event):
        print event.type, event.source.name, \
              event.detail1, event.detail2,  \
              event.any_data
        #if event.source:
        #    printAncestors(event.source)

class KeystrokeListener(Accessibility__POA.DeviceEventListener):
    def __init__(self, keyset, mask, type, synchronous, preemptive, isGlobal):
        self._default_POA().the_POAManager.activate()

        mode = Accessibility.EventListenerMode()
        mode.synchronous = synchronous
        mode.preemptive = preemptive
        mode._global = isGlobal

        registry = getRegistry()
        d = registry.getDeviceEventController()
        if d.registerKeystrokeListener(self._this(), 
                                       keyset, 
                                       mask,
                                       type,
                                       mode):
            self.keyset = keyset
            self.mask = mask
            self.type = type
            self.synchronous = synchronous
            self.preemptive = preemptive
            self.isGlobal = isGlobal
            self.__registered = True
        else:
            self.__registered = False

    def ref(self): pass
    
    def unref(self): pass
    
    def queryInterface(self, repo_id):
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            return self._this()
        else:
            return None

    def deregister(self):
        if not self.__registered:
            return
        
        registry = getRegistry()
        d = registry.getDeviceEventController()
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
        print keyEventToString(event)
        if event.event_string == "F12":
            shutdownAndExit(None, None)
            
def registerListeners():
    global __listeners
    eventTypes = [
        "focus:",
        "mouse:rel",
        "mouse:button",
        "mouse:abs",
        "keyboard:modifiers",
        "object:property-change",
        "object:property-change:accessible-name",
        "object:property-change:accessible-description",
        "object:property-change:accessible-parent",
        "object:state-changed",
        "object:state-changed:focused",
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
        "window:minimize",
        "window:maximize",
        "window:restore",
        "window:activate",
        "window:create",
        "window:deactivate",
        "window:close",
        "window:lower",
        "window:raise",
        "window:resize",
        "window:shade",
        "window:unshade",
        "object:property-change:accessible-table-summary",
        "object:property-change:accessible-table-row-header",
        "object:property-change:accessible-table-column-header",
        "object:property-change:accessible-table-summary",
        "object:property-change:accessible-table-row-description",
        "object:property-change:accessible-table-column-description",
        "object:test",
        "window:restyle",
        "window:desktop-create",
        "window:desktop-destroy"
    ]        

    for eventType in eventTypes:
        __listeners.append(EventListener(eventType))
        
def registerKeystrokeListeners():
    global __keystrokeListeners

    for i in range(0, (1 << (Accessibility.MODIFIER_NUMLOCK + 1))):
        __keystrokeListeners.append(
            KeystrokeListener([],     # keyset
                              i,      # modifier mask
                              [Accessibility.KEY_PRESSED_EVENT,
                               Accessibility.KEY_RELEASED_EVENT], 
                              True,   # synchronous
                              True,   # preemptive
                              False)) # global
    
def main():
    listApps()
    registerListeners()
    registerKeystrokeListeners()
    bonobo.main()

def shutdownAndExit(signum, frame):
    print "Goodbye."
    for listener in (__keystrokeListeners + __listeners):
        listener.deregister()
        
    bonobo.main_quit()
    sys.exit()
    
if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    main()
