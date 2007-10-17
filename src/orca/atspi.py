# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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

"""Provides the interface to the AT-SPI Registry."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import signal
import time

import gobject
gobject.threads_init()

import ORBit
import traceback
import settings

ORBit.load_typelib("Accessibility")

# We will pass "orbit-io-thread" to initialize the ORB in threaded mode.
# This should hopefully help address bug 319652:
#
#   http://bugzilla.gnome.org/show_bug.cgi?id=319652
#
# See also:
#
#   http://bugzilla.gnome.org/show_bug.cgi?id=342614
#   http://mail.gnome.org/archives/orbit-list/2005-December/msg00001.html
#
ORBit.CORBA.ORB_init(orb_id="orbit-io-thread")

import Accessibility
import Accessibility__POA

import debug

try:
  import pyatspi
except ImportError, e:
  import sys
  print sys.path
  raise e

pyatspi.ROLE_CHECK_MENU = -1 # For backward compatability
pyatspi.ROLE_RADIO_MENU = -2 # For backward compatability

#if True:
#    pyatspi.setCacheLevel(pyatspi.CACHE_INTERFACES)
  
class Event:
    """Converts the source of an event to an Accessible object.  We
    need this since the event object we get from the atspi is
    read-only.  So, we create this dummy event object to contain a copy
    of all the event members with the source converted to an
    Accessible.  It is perfectly OK for event handlers to annotate this
    object with their own attributes.
    """

    def __init__(self, e=None):
        if e:
            self.source   = Accessible.makeAccessible(e.source)
            self.type     = e.type
            self.detail1  = e.detail1
            self.detail2  = e.detail2
            if isinstance(e.any_data, Accessibility.Accessible):
                self.any_data = Accessible.makeAccessible(e.any_data)
            else:
                self.any_data = e.any_data
        else:
            self.source   = None
            self.type     = None
            self.detail1  = None
            self.detail2  = None
            self.any_data = None

class Registry:
    """Delegates to the actual AT-SPI Regisitry.
    """

    # The "Borg" singleton model - ensures we're really
    # only connecting to the registry once.
    #
    __sharedState = {}
    __instanceCount = 0

    __listeners=[]
    __keystrokeListeners=[]

    def __init__(self):

        # The "Borg" singleton model - ensures we're really
        # only connecting to the registry once.
        #
        self.__dict__ = self.__sharedState
        self.__instanceCount += 1
        if not self.__dict__.has_key("registry"):
            self.registry = pyatspi.Registry
        if not self.__dict__.has_key("desktop"):
            self.desktop = self.registry.getDesktop(0)

    def start(self):
        """Starts event notification with the AT-SPI Registry.  This method
        only returns after 'stop' has been called.
        """

        self.registry.start()

    def stop(self):
        """Unregisters any event or keystroke listeners registered with
        the AT-SPI Registry and then stops event notification with the
        AT-SPI Registry.
        """
        self.registry.stop()

    def registerEventListener(self, callback, eventType):
        """Registers the given eventType and callback with the Registry.

        Arguments:
        - callback: function to call with an AT-SPI event instance
        - eventType: string representing the type of event
        """
        self.registry.registerEventListener(callback, eventType)

    def deregisterEventListener(self, callback, eventType):
        """Unregisters the given eventType and callback with the Registry.

        Arguments:
        - callback: function to call with an AT-SPI event instance
        - eventType: string representing the type of event
        """
        self.registry.deregisterEventListener(callback, eventType)

    def registerKeystrokeListeners(self, callback):
        """Registers a single callback for all possible keystrokes.
        """
        masks = []
        mask = 0
        while mask <= (1 << pyatspi.MODIFIER_NUMLOCK):
            masks.append(mask)
            mask += 1
        pyatspi.Registry.registerKeystrokeListener(
            callback,
            mask=masks,
            kind=(pyatspi.KEY_PRESSED_EVENT, pyatspi.KEY_RELEASED_EVENT))


class KeystrokeListener(Accessibility__POA.DeviceEventListener):
    """Placeholder for API compatability."""

    def keyEventToString(event):
        return ("KEYEVENT: type=%d\n" % event.type) \
               + ("          hw_code=%d\n" % event.hw_code) \
               + ("          modifiers=%d\n" % event.modifiers) \
               + ("          event_string=(%s)\n" % event.event_string) \
               + ("          is_text=%s\n" % event.is_text) \
               + ("          time=%f" % time.time())

    keyEventToString = staticmethod(keyEventToString)


########################################################################
#                                                                      #
# The Accessible class.                                                #
#                                                                      #
########################################################################

class Accessible:
    """Wraps AT-SPI Accessible objects and caches properties such as
    name, description, and parent.

    It also adds some properties to the AT-SPI Accessible including
    the Application to which the object belongs.

    For efficiency purposes, this class also maintains a cache of all
    Accessible objects obtained so far, and will return an element
    from that cache instead of creating a duplicate object.
    """
    _cache = {}
    _legacyAttributes = {'index': 'getIndexInParent', 
                         'role': 'getRoleName',
                         'localizedRoleName': 'getLocalizedRoleName',
                         'state': 'getState',
                         'relations': 'getRelationSet',
                         'app': 'getApplication',
                         'attributes': 'getAttributes'}

    _legacyIfaceAccess = {'action': 'queryAction',
                          'component': 'queryComponent',
                          'hyperlink': 'queryHyperlink',
                          'hypertext': 'queryHypertext',
                          'image': 'queryImage',
                          'selection': 'querySelection',
                          'table': 'queryTable',
                          'text': 'queryText',
                          'value': 'queryValue',
                          'document': 'queryDocument'}

    _legacyProxyAttribs = {'extents': '_get_extents'}

    _legacyWritableAttribs = ['lastRow', 'lastColumn', 'role', 
                              'lastCursorPosition', 'lastSelections',
                              'characterOffsetInParent', 'childrenIndices',
                              'unicodeText']

    class _CrackDict(dict):
        """This is here to allow some good old-fashioned direct __dict__ access.
        It's crack.
        """
        def __init__(self, container):
            self._container = container
        
        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                try:
                    d = self._container.accessible.user_data
                except AttributeError:
                    d = {} 
                return d[key]

        def has_key(self, key):
            try:
                d = self._container.accessible.user_data
            except AttributeError:
                d = {} 
            return dict.has_key(self, key) or d.has_key(key)

    def makeAccessible(acc):
        """Make an Accessible.  This is used instead of a simple calls to
        Accessible's constructor because the object may already be in the
        cache.

        Arguments:
        - acc: the AT-SPI Accessibility_Accessible

        Returns a Python Accessible.
        """
        obj = None

        if not acc:
            return obj

        if isinstance(acc, Accessible):
            debug.println(
                debug.LEVEL_WARNING,
                "WARNING: atspi.Accessible.makeAccessible:\n"
                "         Parameter acc passed in is a\n" \
                "         Python Accessible instead of an\n" \
                "         AT-SPI Accessible.\n"
                "         Returning Python Accessible.")
            return acc

        # [[[TODO: WDW - the AT-SPI appears to give us a different
        # accessible when we repeatedly ask for the same child of a
        # parent that manages its descendants.  So...we probably
        # shouldn't cache those kind of children because we're likely
        # to cause a memory leak. Logged as bugzilla bug 319675.]]]
        #
        obj = Accessible(acc)

        return obj

    makeAccessible = staticmethod(makeAccessible)

    def deleteAccessible(acc):
        """Delete an Accessible from the cache if it exists.

        Arguments:
        - acc: the AT-SPI Accessibility_Accessible
        """

        pass

    deleteAccessible = staticmethod(deleteAccessible)

    def relationToString(acc):
        """Returns a space-delimited string composed of the given object's
        Accessible relations attribute.  This is for debug purposes.
        """

        relations = acc.getRelationSet()
        relation_strings = []

        for relation in relations:
            rel_string = repr(relation.getRelationType())
            rel_string = rel_string.replace('RELATION_','')
            relation_strings.append(rel_string)

        return ' '.join(relation_strings)

    relationToString = staticmethod(relationToString)
    
    def stateToString(acc):
        """Returns a space-delimited string composed of the given object's
        Accessible state attribute.  This is for debug purposes.
        """

        stateSet = acc.getState()
        states = stateSet.getStates()
        state_strings = []

        for state in states:
            state_string = repr(state)
            state_string = state_string.replace('STATE_','')
            state_strings.append(state_string)

        return ' '.join(state_strings)

    stateToString = staticmethod(stateToString)

    def __init__(self, acc):
        """Obtains, and creates if necessary, a Python Accessible from
        an AT-SPI Accessibility_Accessible.  Applications should not
        call this method, but should instead call makeAccessible.

        Arguments:
        - acc: the AT-SPI Accessibility_Accessible to back this object

        Returns the associated Python Accessible.
        """

        # Crack!
        self.__dict__ = Accessible._CrackDict(self)
        # The setting of self._acc to None here is to help with manual
        # and unit testing of this module.  Furthermore, it helps us
        # determine if this particular instance is really backed by an
        # object or not.
        #
        self._acc = None

        # We'll also keep track of whether this object is any good to
        # us or not.  This object will be deleted when a defunct event
        # is received for it, but anything could happen prior to that
        # event, so we keep this extra field around to help us.
        #
        self.valid = False

        # See if we have an application. Via bridges such as the Java
        # access bridge, we might be getting a CORBA::Object, which is
        # of little use to us.  We need to narrow it down to something
        # we can use.  The first attempt is to see if we can get an
        # application out of it.  Then we go for an accessible.
        #
        if isinstance(acc, Accessibility.Accessible):
            self.accessible = acc            
            if isinstance(self.accessible, Accessibility.Application):
                try:
                    self.toolkitName = self.accessible.toolkitName
                except:
                    self.toolkitName = None
                try:
                    self.version = self.accessible.version
                except:
                    self.version = None
        else:
            debug.println(debug.LEVEL_WARNING,
                          "atspi.py:Accessible.__init__" \
                              + " NOT GIVEN AN ACCESSIBLE!")
            self.accessible = acc
            
        # Save a reference to the AT-SPI object.
        #
        if self.accessible:
            try:
                self.accessible.ref()
                self._acc = acc
                self.valid = True
            except:
                debug.printException(debug.LEVEL_SEVERE)

    def getRelationString(self):
        """Returns a space-delimited string composed of the given object's
        Accessible relations attribute.  This is for debug purposes.
        """

        return Accessible.relationToString(self)

    def getStateString(self):
        """Returns a space-delimited string composed of the given object's
        Accessible state attribute.  This is for debug purposes.
        """
        
        return Accessible.stateToString(self)

    def accessibleNameToString(self):
        """Returns the accessible's name in single quotes or
        the string None if the accessible does not have a name.
        """

        if self.name:
            return "'" + self.name + "'"
        else:
            return "None"

    def __del__(self):
        """Unrefs the AT-SPI Accessible associated with this object.
        """

        if self.accessible:
            try:
                self.accessible.unref()
            except:
                pass

            try:
                Accessible.deleteAccessible(self._acc)
            except:
                pass

            self.accessible = None
            self._acc = None
            self.app = None

    def _get_extents(self, coordinateType = 0):
        """
        This should probably go away.
        """
        component = self.accessible.queryComponent()

        extents = component.getExtents(coordinateType)

        return extents

    def __setattr__(self, attr, value):
        """Traditionally we were able to simply write attributes to the 
        accessible object and access them across the board, this is not 
        possible any more, but we still have a user_data attribute we could 
        use to tack on stuff.
        """
        if attr in self._legacyWritableAttribs:
            _deprecatedMessage(
              msg="Don't write attributes to accessible objects!")
            try:
                user_data = self.accessible.user_data
            except AttributeError:
                user_data = {}
            user_data[attr] = value
            self.accessible.user_data = user_data
        else:
            self.__dict__[attr] = value

    def __getattr__(self, attr):
        """Created virtual attributes for the Accessible object to make
        the syntax a bit nicer (e.g., acc.name rather than acc.name()).
        This method is also called if and only if the given attribute
        does not exist in the object.  Thus, we're effectively lazily
        building a cache to the remote object attributes here.

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """
        if self._legacyAttributes.has_key(attr):
            method_name = self._legacyAttributes[attr]
            _deprecatedMessage(attr, '%s()' % method_name)
            method = getattr(self.accessible, method_name)
            try:
                rv = method()
            except LookupError:
                if attr in ('state', 'relations'):
                    rv = []
                else:
                    rv = None
        elif self._legacyIfaceAccess.has_key(attr):
            method_name = self._legacyIfaceAccess[attr]
            _deprecatedMessage(attr, '%s()' % method_name)
            method = getattr(self.accessible, method_name)
            try:
              rv =  method()
            except:
              rv = None
        elif self._legacyProxyAttribs.has_key(attr):
            method_name = self._legacyProxyAttribs[attr]
            method = getattr(self, method_name)
            _deprecatedMessage(attr, 'something else')
            try:
              rv =  method()
            except Exception, e:
              rv = None
        elif attr in self._legacyWritableAttribs:
          try:
            rv = self.accessible.user_data[attr]
          except:
            raise AttributeError
        else:
            try:
                rv = getattr(self.accessible, attr)
            except AttributeError, e:
                raise e
            except:
                rv = None

        if isinstance(rv, Accessibility.Accessible):
            return Accessible.makeAccessible(rv)
        elif isinstance(rv, Accessibility.StateSet):
            return rv.getStates()
        else:
            return rv

    def child(self, index):
        """Returns the specified child of this object.

        Arguments:
        - index: an integer specifying which child to obtain

        Returns the child at the given index or raise an exception if the
        index is out of bounds or the child is invalid.
        """
        _deprecatedMessage('accessible.child(i)', 'accessible[i]')

        # [[[TODO: WDW - the AT-SPI appears to give us a different accessible
        # when we repeatedly ask for the same child of a parent that manages
        # its descendants.  So...we probably shouldn't cache those kind of
        # children because we're likely to cause a memory leak.]]]
        #
        # Save away details we now know about this child
        #
        
        newChild = None
        try:
            accChild = self.accessible[index]
            if accChild:
                newChild = Accessible.makeAccessible(accChild)
        except IndexError:
            # The problem with a child not existing is a bad one.
            # We want to issue a warning and we also want to know
            # where it happens.
            debug.printStack(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_WARNING,
                          "Child at index %d is not an Accessible" % index)
            
        return newChild

    def __iter__(self):
        '''
        A temporary copy/paste from pyatspi.accessible._AccessibleMixin
        We will use this for emulating pyatspi's container 
        interface for accessibles.
        '''
        for i in xrange(self.accessible.childCount):
            try:
                yield Accessible.makeAccessible(
                  self.accessible.getChildAtIndex(i))
            except LookupError:
                yield None

    def __getitem__(self, index):
        '''
        Proxy pyatspi.accessible._AccessibleMixin
        We will use this for emulating pyatspi's container 
        interface for accessibles.
        '''
        newChild = None
        accChild = self.accessible[index]
        if accChild:
            newChild = Accessible.makeAccessible(accChild)
        
        return newChild


    def __len__(self):
        '''
        Proxy pyatspi.accessible._AccessibleMixin
        We will use this for emulating pyatspi's container 
        interface for accessibles.
        '''
        return len(self.accessible)

    def __str__(self):
      return '%s (Legacy)' % self.accessible

    def __cmp__(self, other):
       if self.accessible.__class__ == other.__class__:
         return cmp(self.accessible, other)
       else:
         return cmp(self.accessible, getattr(other, 'accessible', None))

    def toString(self, indent="", includeApp=True):

        """Returns a string, suitable for printing, that describes the
        given accessible.

        Arguments:
        - indent: A string to prefix the output with
        - includeApp: If True, include information about the app
                      for this accessible.
        """

        if includeApp:
            app = self.accessible.getApplication()
            if app:
                string = indent + "app.name=%-20s " \
                         % "'"+app.name+"'"
            else:
                string = indent + "app=None "
        else:
            string = indent

        string += "name=%s role='%s' state='%s' relations='%s'" \
                  % (self.accessibleNameToString(),
                     self.getRoleName(),
                     self.getStateString(),
                     self.getRelationString())

        return string

########################################################################
#                                                                      #
# Deprecated message                                                   #
#                                                                      #
########################################################################

def _deprecatedMessage(legacy_attrib=None, new_attrib=None, msg=None):
    if not settings.deprecatedMessages:
        return
    stack = traceback.extract_stack(limit=3)
    if len(stack) > 0:
        frame = stack[0]
        try:
            fname = frame[0][frame[0].index('/orca/')+1:]
        except ValueError:
            fname = frame[0]
        context = '%s:%s (%s)' % (fname, frame[1], frame[2])
    else:
        context = 'UNKNOWN'
    if msg:
        dep_msg = 'DEPRECATED: %s %s' % (context, msg)
    else:
        dep_msg = 'DEPRECATED: %s Instead of %s, use %s' % \
            (context, legacy_attrib, new_attrib)
    debug.println(debug.LEVEL_WARNING, dep_msg)


########################################################################
#                                                                      #
# Testing functions.                                                   #
#                                                                      #
########################################################################

def __printTopObject(child):
    parent = child
    while parent:
        if not parent.parent:
            print "RAW TOP:", parent.name, parent.role, \
                parent.state.count(Accessibility.STATE_DEFUNCT)
        parent = parent.parent
    if (child.parent):
        accessible = Accessible.makeAccessible(child)
        app = accessible.app
        print "ACC TOP:", app.name, app.role

def __printDesktops():
    registry = Registry().registry
    print "There are %d desktops" % registry.getDesktopCount()
    for i in range(0,registry.getDesktopCount()):
        desktop = registry.getDesktop(i)
        print "  Desktop %d (name=%s) has %d apps" \
              % (i, desktop.name, desktop.childCount)
        for j in range(0, desktop.childCount):
            app = desktop.getChildAtIndex(j)
            print "    App %d: name=%s role=%s" \
                  % (j, app.name, app.getRoleName())

def __notifyEvent(event):
        print event.type, event.source.name, \
              event.detail1, event.detail2,  \
              event.any_data
        source = Accessible.makeAccessible(event.source)
        __printTopObject(source)
        if not source.parent:
            print "NO PARENT:", source.name, source.role

def __notifyKeystroke(event):
    print "keystroke type=%d hw_code=%d modifiers=%d event_string=(%s) " \
          "is_text=%s" \
          % (event.type, event.hw_code, event.modifiers, event.event_string,
             event.is_text)
    if event.event_string == "F12":
        __shutdownAndExit(None, None)
    return False

def __shutdownAndExit(signum, frame):
    Registry().stop()
    print "Goodbye."

def __test():
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
        "object:children-changed",
        "object:active-descendant-changed",
        "object:visible-data-changed",
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

    __printDesktops()

    registry = Registry()
    for eventType in eventTypes:
        registry.registerEventListener(__notifyEvent, eventType)
    registry.registerKeystrokeListeners(__notifyKeystroke)
    registry.start()

if __name__ == "__main__":
    debug.debugLevel = debug.LEVEL_INFO
    signal.signal(signal.SIGINT, __shutdownAndExit)
    signal.signal(signal.SIGQUIT, __shutdownAndExit)
    __test()


