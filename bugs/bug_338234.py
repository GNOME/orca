# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

"""Bug reproducer for bug x.  This standalone module talks
directly with the AT-SPI Registry via its IDL interfaces.  No Orca
logic or code is stuck in the middle.

To run this module, merely type 'python preferences_tabs.py'.

To reproduce bug x, follow these steps:

1) Run this module in an xterm
2) Start Firefox, open the preferences dialog.
3) Arrow between 'General' 'Privacy' 'Advanced' etc.
4) In the output of this module, you will see that the
   item that used to have focus issues a 'focus:' event.

The item with focus should be the last one to issue a 'focus' event.
"""

import time

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

def getRelations(acc):
    relations = []
    relationSet = acc.getRelationSet()
    for relation in relationSet:
        relations.append(relation._narrow(Accessibility.Relation))
    return relations

def getAccessibleTextString(acc):
    if not acc:
        return "text=None"
    text = acc.queryInterface("IDL:Accessibility/Text:1.0")
    if text:
        text = text._narrow(Accessibility.Text)
        return "text(len=%d)='%s'" % (text.characterCount, text.getText(0, -1))
    else:
        return "text=None"
    
def getNameString(acc):
    if acc.name:
        return "'%s'" % acc.name
    else:
        return "None"

def getAccessibleString(acc):
    if not acc:
        return "None"
    try:
        toolkitName = acc.toolkitName
        version     = acc.version
        return "name=%s role='%s' state='%s' toolkit='%s' version='%s'" \
               % (getNameString(acc),
                  acc.getRoleName(),
                  getStateString(acc),
                  toolkitName,
                  version)
    except:
        return "name=%s role='%s' state='%s'" \
               % (getNameString(acc), acc.getRoleName(), getStateString(acc))

def getLabeller(acc):
    relations = getRelations(acc)
    for relation in relations:
        if relation.getRelationType() \
               == Accessibility.RELATION_LABELLED_BY:
            target = relation.getTarget(0)
            return target
    return None

def printAncestry(child):
   """Prints a hierarchical view of a child's ancestry."""
   
   if not child:
       return
   
   objects = [child]
   parent = child.parent
   while parent and (parent.parent != parent):
       objects.insert(0, parent)
       parent = parent.parent

   indent = ""
   for object in objects:
       print indent + "+-" + getAccessibleString(object)
       indent += "  "

def printHierarchy(root,
                   ooi=None,
                   indent="",
                   onlyShowing=True,
                   omitManaged=True):
    """Prints the accessible hierarchy of all children

    Arguments:
    -indent:      Indentation string
    -root:        Accessible where to start
    -ooi:         Accessible object of interest
    -onlyShowing: If True, only show children painted on the screen
    -omitManaged: If True, omit children that are managed descendants
    """

    if not root:
        return

    if root == ooi:
        print indent + "(*)" + getAccessibleString(root)
    else:
        print indent + "+-" + getAccessibleString(root)
       
    s = root.getState()
    s = s._narrow(Accessibility.StateSet)
    stateSet = s.getStates()
    rootManagesDescendants = stateSet.count(\
        Accessibility.STATE_MANAGES_DESCENDANTS)
    
    for i in range(0, root.childCount):
        child = root.getChildAtIndex(i)
        if child == root:
            print indent + "  " + "WARNING CHILD == PARENT!!!"
        elif not child:
            print indent + "  " + "WARNING CHILD IS NONE!!!"
        elif child.parent != root:
            print indent + "  " + "WARNING CHILD.PARENT != PARENT!!!"
        else:
            s = child.getState()
            s = s._narrow(Accessibility.StateSet)
            stateSet = s.getStates()
            paint = (not onlyShowing) \
                    or (onlyShowing \
                        and stateSet.count(Accessibility.STATE_SHOWING))
            paint = paint \
                    and ((not omitManaged) \
                         or (omitManaged and not rootManagesDescendants))

            if paint:
               printHierarchy(child,
                              ooi,
                              indent + "  ",
                              onlyShowing,
                              omitManaged)

def printTopObject(child):
    parent = child
    while parent:
	if not parent.parent:
            print "TOP OBJECT:", parent.name, parent.getRoleName()
            #if parent.getRole() != Accessibility.ROLE_APPLICATION:
            #    print "ERROR: TOP OBJECT NOT AN APPLICATION."
            #    shutdownAndExit()
        parent = parent.parent
	
def printDesktops():
    print "There are %d desktops" % registry.getDesktopCount()
    for i in range(0,registry.getDesktopCount()):
        desktop = registry.getDesktop(i)
        print "  Desktop %d (name=%s) has %d apps" \
              % (i, desktop.name, desktop.childCount)
        for j in range(0, desktop.childCount):
            app = desktop.getChildAtIndex(j)
            print "    App %d: name=%s role=%s" \
		  % (j, app.name, app.getRoleName())
            for k in range(0, app.childCount):
                child = app.getChildAtIndex(k)
                print "      Child %d: name=%s role=%s" \
                      % (k, child.name, child.getRoleName())
               
def findActiveWindow():
    desktop = registry.getDesktop(0)
    window = None
    for j in range(0, desktop.childCount):
        app = desktop.getChildAtIndex(j)
        for k in range(0, app.childCount):
            child = app.getChildAtIndex(k)
            s = child.getState()
            s = s._narrow(Accessibility.StateSet)
            state = s.getStates()            
            if (state.count(Accessibility.STATE_ACTIVE) > 0) \
               or (state.count(Accessibility.STATE_FOCUSED) > 0):
                window = child
		break
        if window:
           break
    return window
 
def findAllText(root):
    if not root:
        return
    text = root.queryInterface("IDL:Accessibility/Text:1.0")
    if text:
        text = text._narrow(Accessibility.Text)
        print "Text (len=%d): %s" % (text.characterCount, text.getText(0, -1))
    for i in range(0, root.childCount):
        findAllText(root.getChildAtIndex(i))

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

def notifyEvent(event):
    print event.type, event.detail1, event.detail2, event.any_data
    obj = None
    try:
        obj = event.source._narrow(Accessibility.Application)
    except:
        try:
            obj = event.source._narrow(Accessibility.Accessible)
        except:
            pass
    if obj:
        print "  " + getAccessibleString(obj) \
              + " " + getAccessibleTextString(obj)
        labeller = getLabeller(obj)
        print "  LABELLED BY:" + getAccessibleString(labeller) \
              + " " + getAccessibleTextString(labeller)

def notifyKeystroke(event):
    print "keystroke type=%d hw_code=%d modifiers=%d event_string=(%s) " \
          "is_text=%s" \
          % (event.type, event.hw_code, event.modifiers, event.event_string,
             event.is_text)
    if event.event_string == "F12":
        shutdownAndExit()
        return True
    return False

def shutdownAndExit(signum=None, frame=None):
    stop()
    print "Goodbye."

def test():
    print "Press F12 to Exit."
    for eventType in eventTypes:
        registerEventListener(notifyEvent, eventType)
    registerKeystrokeListeners(notifyKeystroke)
    start()

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    test()
