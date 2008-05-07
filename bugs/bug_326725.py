
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

"""Bug reproducer for bug 317475.  This standalone module talks
directly with the AT-SPI Registry via its IDL interfaces.  No Orca
logic or code is stuck in the middle.

To run this module, merely type 'python bug_326725.py'.

To reproduce bug 326725, follow these steps:

Steps to Reproduce:

1. Run Evolution. Bring up the Mail view.
2. Run the attached standalone python application in a terminal window.
3. Give focus to one of the offending components:
   - Mail Folder Tree
   - Mail Message list
   - Mail Compose Window - Message area
   In the terminal window where you started this script, you should see
   a hierarchical view of the ancestry of the component that currently
   has focus.
4. Press F7
   In the terminal window where you started this script, you should see
   the accessible hierarchy of all children in this application.

To terminate this application when you have finished testing, press F12.

"""

import time
import bonobo
import ORBit
import threading
import traceback
import sys

ORBit.load_typelib("Accessibility")
ORBit.CORBA.ORB_init()

import Accessibility
import Accessibility__POA

listeners = []
keystrokeListeners = []

registry = bonobo.get_object("OAFIID:Accessibility_Registry:1.0",
                             "Accessibility/Registry")

debug = False
locusOfFocus = None


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
        self.register()


    def ref(self): 
        pass


    def unref(self): 
        pass


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
        self.callback(event)


    def __del__(self):
        self.deregister()


class KeystrokeListener(Accessibility__POA.DeviceEventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given keystroke.  Most users of this module will not use this
    class directly, but will instead use the registerKeystrokeListeners
    method."""

    def keyEventToString(event):
        return ("KEYEVENT: type=%d\n" % event.type) \
               + ("          hw_code=%d\n" % event.hw_code) \
               + ("          modifiers=%d\n" % event.modifiers) \
               + ("          event_string=(%s)\n" % event.event_string) \
               + ("          is_text=%s\n" % event.is_text) \
               + ("          time=%f" % time.time())


    keyEventToString = staticmethod(keyEventToString)


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


    def ref(self): 
        pass


    def unref(self):
        pass


    def queryInterface(self, repo_id):
        thiz = None
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            thiz = self._this()

        return thiz


    def register(self):
        d = self.registry.getDeviceEventController()
        if d.registerKeystrokeListener(self._this(), self.keyset,
                                       self.mask, self.type, self.mode):
            self.__registered = True
        else:
            self.__registered = False

        return self.__registered


    def deregister(self):
        if not self.__registered:
            return
        d = self.registry.getDeviceEventController()
        d.deregisterKeystrokeListener(self._this(), self.keyset,
                                      self.mask, self.type)
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

def getApp(acc, indent=""):
    """Returns the AT-SPI Accessibility_Application associated with this
    object.  Returns None if the application cannot be found (usually
    the indication of an AT-SPI bug).

    Arguments:
    - acc: the accessible object
    - indent: A string to prefix the output with

    """

    global debug

    if debug:
        print indent + "Finding app for source.name=" + getNameString(acc)
    obj = acc
    while obj.parent:
        obj = obj.parent
        if debug:
            print indent + "--> parent.name=" + getNameString(obj)

    if (obj == obj.parent):
        print indent + "ERROR in getApp(): obj == obj.parent!"
        return None
    elif (obj.getRoleName() != "application"):

        print indent + "ERROR in getApp(): top most parent " \
                  "(name='%s') is of role %s" % (obj.name, obj.getRoleName())

        if (obj.getRoleName() != "invalid") and (obj.getRoleName() != "frame"):
            return None

    if debug:
        print indent + "Accessible app for %s is %s" \
              % (getNameString(acc), getNameString(obj))

    return obj


def getStateString(acc):
    """Returns a space-delimited string composed of the given object's
    Accessible state attribute.  This is for debug purposes.
    """

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

    return stateString.strip()


def toString(acc, indent="", includeApp=True):

    """Returns a string, suitable for printing, that describes the
    given accessible.

    Arguments:
    - acc: the accessible object
    - indent: A string to prefix the output with
    - includeApp: If True, include information about the app
                  for this accessible.
    """

    if includeApp:
        if getApp(acc, indent):
            string = indent + "app.name=%-20s " % \
                getNameString(getApp(acc, indent))
        else:
            string = indent + "app=None"
    else:
        string = indent

    string += "name=%s role='%s' state='%s'" \
              % (getNameString(acc), acc.getRoleName(), getStateString(acc))

    return string


def getNameString(acc):
    """Return the name string for the given accessible object.

    Arguments:
    - acc: the accessible object

    Returns the name of this accessible object (or "None" if not set).
    """

    if acc.name:
        return "'%s'" % acc.name
    else:
        return "None"


def getAccessibleString(acc):
    return "name=%s role='%s' state='%s'" \
           % (getNameString(acc), acc.getRoleName(), getStateString(acc))


# List of event types that we are interested in.

eventTypes = [
     "focus:",
##     "mouse:rel",
##     "mouse:button",
##     "mouse:abs",
##     "keyboard:modifiers",
##     "object:property-change",
##     "object:property-change:accessible-name",
##     "object:property-change:accessible-description",
##     "object:property-change:accessible-parent",
##     "object:state-changed",
##     "object:state-changed:focused",
##     "object:selection-changed",
##     "object:children-changed"
##     "object:active-descendant-changed"
##     "object:visible-data-changed"
##     "object:text-selection-changed",
##     "object:text-caret-moved",
##     "object:text-changed",
##    "object:text-changed:insert",
##     "object:column-inserted",
##     "object:row-inserted",
##     "object:column-reordered",
##     "object:row-reordered",
##     "object:column-deleted",
##     "object:row-deleted",
##     "object:model-changed",
##     "object:link-selected",
##     "object:bounds-changed",
##     "window:minimize",
##     "window:maximize",
##     "window:restore",
##     "window:activate",
##     "window:create",
##     "window:deactivate",
##     "window:close",
##     "window:lower",
##     "window:raise",
##     "window:resize",
##     "window:shade",
##     "window:unshade",
##     "object:property-change:accessible-table-summary",
##     "object:property-change:accessible-table-row-header",
##     "object:property-change:accessible-table-column-header",
##     "object:property-change:accessible-table-summary",
##     "object:property-change:accessible-table-row-description",
##     "object:property-change:accessible-table-column-description",
##     "object:test",
##     "window:restyle",
##     "window:desktop-create",
##     "window:desktop-destroy"
]


def printAncestry(child):
    """Prints a hierarchical view of a child's ancestry."""

    if not child:
        return

    print "===========================================================\n\n"
    objects = [child]
    parent = child.parent
    while parent and (parent.parent != parent):
        objects.insert(0, parent)
        parent = parent.parent

    indent = ""
    for object in objects:
        print toString(object, indent + "+-", False)
        indent += "  "
    print "===========================================================\n\n"


def printHierarchy(root, ooi, indent=""):
    """Prints the accessible hierarchy of all children

    Arguments:
    -indent:      Indentation string
    -root:        Accessible where to start
    -ooi:         Accessible object of interest
    """

    if not root:
        return

    if root == ooi:
       print toString(root, indent + "(*)", False)
    else:
       print toString(root, indent + "+-", False)

    for i in range(0, root.childCount):
        child = root.getChildAtIndex(i)
        if child == root:
            print indent + "  " + "WARNING CHILD == PARENT!!!"
        elif not child:
            print indent + "  " + "WARNING CHILD IS NONE!!!"
        elif child.parent != root:
            print indent + "  " + "WARNING CHILD.PARENT != PARENT!!!"
        else:
            printHierarchy(child, ooi, indent + "  ")


def notifyEvent(event):
    global debug, locusOfFocus

    if event.type == "focus:":
        if event.source == None:
            if debug:
                print "notifyEvent: event.source is NONE."
        else:
            if debug:
                print "notifyEvent: event.source", event.source
            try:
                if locusOfFocus:
                    locusOfFocus.unref()
                locusOfFocus = event.source
                if locusOfFocus:
                    locusOfFocus.ref()
            except:
                traceback.print_stack(None, 100)
            printAncestry(locusOfFocus)


def notifyKeystroke(event):
    """Process keyboard events.

    Arguments:
    - event: the keyboard event to process
    """

    global debug, locusOfFocus

    # print KeystrokeListener.keyEventToString(event)

    if (event.event_string == "F7") and (event.type == 0):
        if debug:
            print "notifyKeystroke: LOCUSOFFOCUS: ", locusOfFocus
        if locusOfFocus != None:
            app = getApp(locusOfFocus, "")

            if app != None:
                if debug:
                    print "Starting to print Hierarchy."
                printHierarchy(getApp(locusOfFocus, ""), locusOfFocus)
                if debug:
                    print "Finishing printing Hierarchy."

    if (event.event_string == "F12") or (event.event_string == "SunF37"):
        shutdownAndExit()

    return False


def shutdownAndExit(signum=None, frame=None):
    stop()


def test():
    for eventType in eventTypes:
        registerEventListener(notifyEvent, eventType)
    registerKeystrokeListeners(notifyKeystroke)
    start()


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    test()
