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

"""Bug reproducer for bug 340978.  This standalone module talks
directly with the AT-SPI Registry via its IDL interfaces.  No Orca
logic or code is stuck in the middle.

When moving between items in the inbox summary of messages, the information
obtained from the accessible table interface looks to be wrong/inconsistent.

Reproducible: Always

Steps to Reproduce:
1. Run the attached standalone test case in an xterm.
2. Open Thunderbird.
3. Use the keyboard to arrow between items in the message summary list
4. Examine the output of the standalone test case.

Actual Results:  
CHECKING TABLE CELL IMPLEMENTATION CONSISTENCY
  ORIGINAL CHILD INDEX CHECK OK
  COMPUTED CHILD (row=12, column=0) PARENT CHECK OK
  OOPS - COMPUTED CHILD INDEX MISMATCH (original index=37, computed index=212)
  OOPS - DID NOT GET THE SAME ROW (original=12, computed=70)
  OOPS - DID NOT GET THE SAME COLUMN (original=0, computed=1)
CHECKING TABLE CELL IMPLEMENTATION CONSISTENCY
  ORIGINAL CHILD INDEX CHECK OK
  COMPUTED CHILD (row=18, column=0) PARENT CHECK OK
  OOPS - COMPUTED CHILD INDEX MISMATCH (original index=55, computed index=320)
  OOPS - DID NOT GET THE SAME ROW (original=18, computed=106)
  OOPS - DID NOT GET THE SAME COLUMN (original=0, computed=1)


Expected Results:  
The test program performs a variety of checks on the consistency of what it is
being given.  Anything beginning with "OOPS" represents an inconsistency. 
There should be none of these.


I'm guessing there is at least something wrong with the computed row.  If I run
this test app and highlight the very first entry in the message summary and
then arrow to the 2nd item, you'll see that the row looks a bit odd (it jumps
from 0 to 6).  There also seems to be something broken with respect to
getAccessibleAt, which takes a row and column.  Perhaps the implementors got
this method confused with getAccessibleAtPoint?

CHECKING TABLE CELL IMPLEMENTATION CONSISTENCY
  ORIGINAL CHILD INDEX CHECK OK
  COMPUTED CHILD (row=0, column=0) PARENT CHECK OK
  OOPS - COMPUTED CHILD INDEX MISMATCH (original index=1, computed index=2640)
  OOPS - DID NOT GET THE SAME ROW (original=0, computed=879)
  OOPS - DID NOT GET THE SAME COLUMN (original=0, computed=2)
CHECKING TABLE CELL IMPLEMENTATION CONSISTENCY
  ORIGINAL CHILD INDEX CHECK OK
  COMPUTED CHILD (row=6, column=0) PARENT CHECK OK
  OOPS - COMPUTED CHILD INDEX MISMATCH (original index=19, computed index=104)
  OOPS - DID NOT GET THE SAME ROW (original=6, computed=34)
  OOPS - DID NOT GET THE SAME COLUMN (original=0, computed=1)
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

def getNameString(acc):
    if acc.name:
        return "'%s'" % acc.name
    else:
        return "None"

def getAccessibleString(acc):
    return "name=%s role='%s' state='%s'" \
           % (getNameString(acc), acc.getRoleName(), getStateString(acc))

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
##     "object:children-changed",
    "object:active-descendant-changed",
##     "object:visible-data-changed",
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
    # What we're doing here is checking to see if the table interface
    # is working properly.  We look upwards from the child to see
    # where it is in its parent and table, and then use that information
    # to get the table cell at that position.  The information for the
    # computed child had better be identical to the event.source
    #
    if event.source.getRoleName() == "table cell":
        print "CHECKING TABLE CELL IMPLEMENTATION CONSISTENCY"
        parent = event.source.parent

        # The parent had better implement the table interace.
        #
        table = parent.queryInterface("IDL:Accessibility/Table:1.0")
        if table:
            table = table._narrow(Accessibility.Table)
        else:
            print "  OOPS - PARENT DOES NOT SUPPORT THE TABLE INTERFACE"
            return

        # See if the parent/child relation is OK.  We do this to see
        # if the child is really indeed at its given index in the
        # parent.
        #
        index      = event.source.getIndexInParent()
        checkChild = parent.getChildAtIndex(index)
        checkIndex = checkChild.getIndexInParent()
        if checkIndex != index:
            print "  OOPS - ORIGINAL CHILD INDEX MISMATCH (original Index=%d, computed Index=%d)" \
                  % (index, checkIndex)
            return
        else:
            print "  ORIGINAL CHILD INDEX CHECK OK"

        # Use the table interface to get the computed child at what we
        # think is the right row and column.
        #
        row = table.getRowAtIndex(index)
        column = table.getColumnAtIndex(index)
        checkAcc = table.getAccessibleAt(row, column)
        checkParent = checkAcc.parent
        if checkParent != parent:
            print "  OOPS - DIDN'T GET THE SAME PARENT FOR COMPUTED CHILD"
            return
        else:
            print "  COMPUTED CHILD (row=%d, column=%d) PARENT CHECK OK" \
                  % (row, column)

        # Check again for parent/child relation based upon computed child.
        #
        checkIndex = checkAcc.getIndexInParent()
        if checkIndex != index:
            print "  OOPS - COMPUTED CHILD INDEX MISMATCH (original index=%d, computed index=%d)" \
                  % (index, checkIndex)
        else:
            print "  COMPUTED CHILD INDEX CHECK OK"

        # Let's see if we get the same table interface.
        #
        checkTable = checkParent.queryInterface("IDL:Accessibility/Table:1.0")
        if checkTable:
            checkTable = checkTable._narrow(Accessibility.Table)
        else:
            print "  OOPS - PARENT DOES NOT SUPPORT THE TABLE INTERFACE"
            return

        if checkTable != table:
            print "  OOPS - DIFFERENT TABLE INTERFACES"
            return
        
        checkRow = checkTable.getRowAtIndex(checkIndex)
        if checkRow != row:
            print "  OOPS - DID NOT GET THE SAME ROW (original=%d, computed=%d)" \
                  % (row, checkRow)
        else:
            print "  ROW CHECK OK"
            
        checkColumn = checkTable.getColumnAtIndex(checkIndex)
        if checkColumn != column:
            print "  OOPS - DID NOT GET THE SAME COLUMN (original=%d, computed=%d)" \
                  % (column, checkColumn)
        else:
            print "  COLUMN CHECK OK"
            
def notifyKeystroke(event):
    if event.event_string == "F12":
        shutdownAndExit()
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
