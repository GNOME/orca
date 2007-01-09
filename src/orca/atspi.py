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
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import signal
import time

import gobject
gobject.threads_init()

import bonobo
import ORBit

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
import rolenames
import settings

class Event:
    """Converts the source of an event to an Accessible object.  We
    need this since the event object we get from the atspi is
    read-only.  So, we create this dummy event object to contain a copy
    of all the event members with the source converted to an
    Accessible.  It is perfectly OK for event handlers to annotate this
    object with their own attributes.
    """

    def getAnyData(e):
        """Returns the any_data field, compensating for any
        differences between pre-1.7.0 and post-1.7.0 implementations
        of the AT-SPI."""

        # [[[TODO: WDW - HACK because AT-SPI 1.7.0 has
        # introduced a binary incompatibility where the
        # "any_data" of the event has changed from being a
        # real "any_data" to an EventDetails structure that
        # holds "any_data."  This check here helps us deal
        # with the case where we might be talking to a
        # pre-1.7.0 implementation or a 1.7.0+ implementation.
        # What we're doing is just checking the CORBA typecode
        # (as a string) to see if the type of the "any_data"
        # field is this new structure.  If it is, we pull the
        # "any_data" field from it.  If it isn't, we get the
        # "any_data" field as we normally would.]]]
        #
        if e.any_data and (e.any_data.typecode().name) == "EventDetails":
            return e.any_data.value().any_data
        else:
            return e.any_data

    getAnyData = staticmethod(getAnyData)

    def __init__(self, e=None):
        if e:
            self.source   = Accessible.makeAccessible(e.source)
            self.type     = e.type
            self.detail1  = e.detail1
            self.detail2  = e.detail2

            # If were talking to AT-SPI 1.7.0 or greater, we can get the
            # application information right away because it is tucked in
            # the EventDetails data new for 1.7.0.
            #
            if e.any_data and (e.any_data.typecode().name) == "EventDetails":
                details = e.any_data.value()
                self.any_data = details.any_data
                if self.source and details.host_application:
                    self.source.app = Accessible.makeAccessible(
                        details.host_application)
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
            self.registry = bonobo.get_object(
                "OAFIID:Accessibility_Registry:1.0",
                "Accessibility/Registry")
        if not self.__dict__.has_key("desktop"):
            self.desktop = self.registry.getDesktop(0)

    def __blockPreventor(self):
        """[[[TODO: HACK to attempt to prevent deadlocks.  We call time.sleep
        here as a means to sidestep the global interpreter lock (GIL).]]]
        """
        if settings.gilSleepTime:
            time.sleep(settings.gilSleepTime)
        return True

    def start(self):
        """Starts event notification with the AT-SPI Registry.  This method
        only returns after 'stop' has been called.
        """
        Accessible.init(self)

        # We'll try our own main loop to help debug things.  Code borrowed
        # "The Whole PyGtk FAQ": http://www.async.com.br/faq/pygtk/
        #
        if settings.useBonoboMain:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "atspi.start: using bonobo.main; "
                          + "gilSleepTime=%f" % settings.gilSleepTime)
            if settings.useBlockPreventor and settings.gilSleepTime:
                gobject.idle_add(self.__blockPreventor)
            bonobo.main()
        else:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "atspi.start: using our custom main loop; "
                          + "gilSleepTime=%f" % settings.gilSleepTime)
            self.running = True
            context = gobject.MainLoop().get_context()
            while self.running:
                if settings.gilSleepTime:
                    time.sleep(settings.gilSleepTime)
                context.iteration(False)

    def stop(self):
        """Unregisters any event or keystroke listeners registered with
        the AT-SPI Registry and then stops event notification with the
        AT-SPI Registry.
        """
        Accessible.shutdown(self)
        for listener in (self.__listeners + self.__keystrokeListeners):
            listener.deregister()
        if settings.useBonoboMain:
            bonobo.main_quit()
        else:
            self.running = False

    def registerEventListener(self, callback, eventType):
        """Registers the given eventType and callback with the Registry.

        Arguments:
        - callback: function to call with an AT-SPI event instance
        - eventType: string representing the type of event
        """
        listener = EventListener(self.registry, callback, eventType)
        self.__listeners.append(listener)

    def deregisterEventListener(self, callback, eventType):
        """Unregisters the given eventType and callback with the Registry.

        Arguments:
        - callback: function to call with an AT-SPI event instance
        - eventType: string representing the type of event
        """
        found = True
        while len(self.__listeners) and found:
            for i in range(0, len(self.__listeners)):
                if (self.__listeners[i].callback == callback) \
                   and (self.__listeners[i].eventType == eventType):
                    # The __del__ method of the listener will unregister it.
                    #
                    self.__listeners.pop(i)
                    found = True
                    break
                else:
                    found = False

    def registerKeystrokeListeners(self, callback):
        """Registers a single callback for all possible keystrokes.
        """
        for i in range(0, (1 << (Accessibility.MODIFIER_NUMLOCK + 1))):
            self.__keystrokeListeners.append(
                KeystrokeListener(self.registry,
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
# Event listener classes for global and keystroke events               #
#                                                                      #
########################################################################

class EventListener(Accessibility__POA.EventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given event type.  Most users of this module will not use this
    class directly, but will instead use the registerEventListener method
    of the Registry."""

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
        if settings.timeoutCallback and (settings.timeoutTime > 0):
            signal.signal(signal.SIGALRM, settings.timeoutCallback)
            signal.alarm(settings.timeoutTime)

        try:
            self.callback(event)
        except:
            debug.printException(debug.LEVEL_WARNING)

        if settings.timeoutCallback and (settings.timeoutTime > 0):
            signal.alarm(0)

    def __del__(self):
        self.deregister()

class KeystrokeListener(Accessibility__POA.DeviceEventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given keystroke.  Most users of this module will not use this
    class directly, but will instead use the registerKeystrokeListeners
    method of the Registry."""

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
        if settings.timeoutCallback and (settings.timeoutTime > 0):
            signal.signal(signal.SIGALRM, settings.timeoutCallback)
            signal.alarm(settings.timeoutTime)

        try:
            consumed = self.callback(event)
        except:
            debug.printException(debug.LEVEL_WARNING)
            consumed = False

        if settings.timeoutCallback and (settings.timeoutTime > 0):
            signal.alarm(0)

        return consumed

    def __del__(self):
        self.deregister()

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

    # The cache of the currently active accessible objects.  The key is
    # the AT-SPI Accessible, and the value is the Python Accessible.
    # [[[TODO: WDW - probably should look at the __new__ method as a means
    # to handle singletons.]]]
    #
    _cache = {}

    def init(registry):
        """Registers various event listeners with the Registry to keep
        the Accessible cache up to date.

        Arguments:
        - registry: an instance of Registry
        """
        registry.registerEventListener(
            Accessible._onNameChanged,
            "object:property-change:accessible-name")
        registry.registerEventListener(
            Accessible._onDescriptionChanged,
            "object:property-change:accessible-description")
        registry.registerEventListener(
            Accessible._onParentChanged,
            "object:property-change:accessible-parent")
        registry.registerEventListener(
            Accessible._onStateChanged,
            "object:state-changed:")
        registry.registerEventListener(
            Accessible._onChildrenChanged,
            "object:children-changed:")

    init = staticmethod(init)

    def shutdown(registry):
        """Unregisters the event listeners that were registered in the
        init method.

        Arguments:
        - registry: an instance of Registry
        """
        registry.deregisterEventListener(
            Accessible._onNameChanged,
            "object:property-change:accessible-name")
        registry.deregisterEventListener(
            Accessible._onDescriptionChanged,
            "object:property-change:accessible-description")
        registry.deregisterEventListener(
            Accessible._onParentChanged,
            "object:property-change:accessible-parent")
        registry.deregisterEventListener(
            Accessible._onStateChanged,
            "object:state-changed:")
        registry.deregisterEventListener(
            Accessible._onChildrenChanged,
            "object:children-changed:")

    shutdown = staticmethod(shutdown)

    def _onNameChanged(e):
        """Core module event listener called when an object's name
        changes.  Updates the cache accordingly.

        Arguments:
        - e: AT-SPI event from the AT-SPI registry
        """

        if Accessible._cache.has_key(e.source):
            obj = Accessible._cache[e.source]
            if obj.__dict__.has_key("name"):
                del obj.__dict__["name"]
            if obj.__dict__.has_key("label"):
                del obj.__dict__["label"]

    _onNameChanged = staticmethod(_onNameChanged)

    def _onDescriptionChanged(e):
        """Core module event listener called when an object's description
        changes.  Updates the cache accordingly.

        Arguments:
        - e: AT-SPI event from the AT-SPI registry
        """

        if Accessible._cache.has_key(e.source):
            obj = Accessible._cache[e.source]
            if obj.__dict__.has_key("description"):
                del obj.__dict__["description"]
            if obj.__dict__.has_key("label"):
                del obj.__dict__["label"]

    _onDescriptionChanged = staticmethod(_onDescriptionChanged)

    def _onParentChanged(e):
        """Core module event listener called when an object's parent
        changes.  Updates the cache accordingly.

        Arguments:
        - e: AT-SPI event from the AT-SPI registry
        """

        # [[[TODO: WDW - I put this in here for now.  The idea is that
        # we will probably get parent changed events for objects that
        # are or will soon be defunct, so let's just forget about the
        # object rather than try to keep the cache in sync.]]]
        #
        if Accessible._cache.has_key(e.source):
            Accessible.deleteAccessible(e.source)
        return

    _onParentChanged = staticmethod(_onParentChanged)

    def _onStateChanged(e):
        """Core module event listener called when an object's state
        changes.  Updates the cache accordingly.

        Arguments:
        - e: AT-SPI event from the AT-SPI registry
        """

        if Accessible._cache.has_key(e.source):
            # Let's get rid of defunct objects.  We hate them.
            #
            if e.type == "object:state-changed:defunct":
                Accessible.deleteAccessible(e.source)
            else:
                obj = Accessible._cache[e.source]
                if obj.__dict__.has_key("state"):
                    del obj.state

    _onStateChanged = staticmethod(_onStateChanged)

    def _onChildrenChanged(e):
        """Core module event listener called when an object's child count
        changes.  Updates the cache accordingly.

        Arguments:
        - e: AT-SPI event from the AT-SPI registry
        """

        if Accessible._cache.has_key(e.source):
            obj = Accessible._cache[e.source]
            if obj.__dict__.has_key("childCount"):
                del obj.childCount

    _onChildrenChanged = staticmethod(_onChildrenChanged)

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
        if not settings.cacheAccessibles:
            obj = Accessible(acc)
            return obj

        if Accessible._cache.has_key(acc):
            obj = Accessible._cache[acc]
            if not obj.valid:
                del Accessible._cache[acc]
                obj = None

        if not obj:
            obj = Accessible(acc)

        if obj.valid:
            Accessible._cache[acc] = obj
        else:
            obj = None

        return obj

    makeAccessible = staticmethod(makeAccessible)

    def deleteAccessible(acc):
        """Delete an Accessible from the cache if it exists.

        Arguments:
        - acc: the AT-SPI Accessibility_Accessible
        """

        if acc and Accessible._cache.has_key(acc):
            try:
                del Accessible._cache[acc]
            except:
                pass

    deleteAccessible = staticmethod(deleteAccessible)

    def __init__(self, acc):
        """Obtains, and creates if necessary, a Python Accessible from
        an AT-SPI Accessibility_Accessible.  Applications should not
        call this method, but should instead call makeAccessible.

        Arguments:
        - acc: the AT-SPI Accessibility_Accessible to back this object

        Returns the associated Python Accessible.
        """

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

        # [[[TODO: WDW - should do an assert here to make sure we're
        # getting a raw AT-SPI Accessible and not one of our own locally
        # cached Accessible instances. Logged as bugzilla bug 319673.]]]
        #
        assert (not Accessible._cache.has_key(acc)), \
               "Attempt to create an Accessible that's already been made."

        # See if we have an application. Via bridges such as the Java
        # access bridge, we might be getting a CORBA::Object, which is
        # of little use to us.  We need to narrow it down to something
        # we can use.  The first attempt is to see if we can get an
        # application out of it.  Then we go for an accessible.
        #
        self.accessible = None
        try:
            self.accessible = acc._narrow(Accessibility.Application)
            try:
                self.toolkitName = self.accessible.toolkitName
            except:
                self.toolkitName = None
            try:
                self.version = self.accessible.version
            except:
                self.version = None
        except:
            try:
                self.accessible = acc._narrow(Accessibility.Accessible)
            except:
                debug.printException(debug.LEVEL_SEVERE)
                debug.println(debug.LEVEL_SEVERE,
                              "atspi.py:Accessible.__init__" \
                              + " NOT GIVEN AN ACCESSIBLE!")
                self.accessible = None

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

        relations = self.relations
        relString = " "
        for relation in relations:
            if relation.getRelationType() == Accessibility.RELATION_LABEL_FOR:
                relString += "LABEL_FOR "
            if relation.getRelationType() == Accessibility.RELATION_LABELLED_BY:
                relString += "LABELLED_BY "
            if relation.getRelationType() == \
                                       Accessibility.RELATION_CONTROLLER_FOR:
                relString += "CONTROLLER_FOR "
            if relation.getRelationType() == \
                                       Accessibility.RELATION_CONTROLLED_BY:
                relString += "CONTROLLED_BY "
            if relation.getRelationType() == Accessibility.RELATION_MEMBER_OF:
                relString += "MEMBER_OF "
            if relation.getRelationType() == Accessibility.RELATION_TOOLTIP_FOR:
                relString += "TOOLTIP_FOR "
            if relation.getRelationType() == \
                                       Accessibility.RELATION_NODE_CHILD_OF:
                relString += "NODE_CHILD_OF "
            if relation.getRelationType() == Accessibility.RELATION_EXTENDED:
                relString += "RELATION_EXTENDED "
            if relation.getRelationType() == Accessibility.RELATION_FLOWS_TO:
                relString += "FLOWS_TO "
            if relation.getRelationType() == Accessibility.RELATION_FLOWS_FROM:
                relString += "FLOWS_FROM "
            if relation.getRelationType() == \
                                       Accessibility.RELATION_SUBWINDOW_OF:
                relString += "SUBWINDOW_OF "
            if relation.getRelationType() == Accessibility.RELATION_EMBEDS:
                relString += "EMBEDS "
            if relation.getRelationType() == Accessibility.RELATION_EMBEDDED_BY:
                relString += "EMBEDDED_BY "
            if relation.getRelationType() == Accessibility.RELATION_POPUP_FOR:
                relString += "POPUP_FOR "
            if relation.getRelationType() == \
                                       Accessibility.RELATION_PARENT_WINDOW_OF:
                relString += "WINDOW_OF "

        return relString.strip()

    def getStateString(self):
        """Returns a space-delimited string composed of the given object's
        Accessible state attribute.  This is for debug purposes.
        """

        stateSet = self.state
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
                self.accessible = None
                self._acc = None
            except:
                pass

    def __get_name(self):
        """Returns the object's accessible name as a string.
        """

        # Combo boxes don't seem to issue accessible-name changed
        # events, so we can't cache their names.  The main culprit
        # here seems to be the combo box in gaim's "Join Chat" window.
        #
        name = self.accessible.name

        if name and settings.cacheValues \
            and (self.role != rolenames.ROLE_COMBO_BOX):
            self.name = name

        return name

    def __get_description(self):
        """Returns the object's accessible description as a string.
        """

        description = self.accessible.description

        if description and settings.cacheValues:
            self.description = description

        return description

    def __get_parent(self):
        """Returns the object's parent as a Python Accessible.  If
        this object has no parent, None will be returned.
        """

        # We will never set self.parent if the backing accessible doesn't
        # have a parent.  The reason we do this is that we may sometimes
        # get events for objects without a parent, but then the object ends
        # up getting a parent later on.
        #
        accParent = self.accessible.parent

        if not accParent:
            return None
        else:
            parent = Accessible.makeAccessible(accParent);

            if settings.cacheValues:
                self.parent = parent

            return parent;

    def __get_child_count(self):
        """Returns the number of children for this object.
        """

        childCount = self.accessible.childCount

        # We don't want to cache this value because it's possible that it
        # will continually change.
        # if settings.cacheValues:
        #     self.childCount = childCount

        return childCount

    def __get_index(self):
        """Returns the index of this object in its parent's child list.
        """

        index = self.accessible.getIndexInParent()

        # We don't want to cache this value because it's possible that it
        # will continually change.
        # if settings.cacheValues:
        #     self.index = index

        return index

    def __get_role(self):
        """Returns the Accessible role name of this object as a string.
        This string is not localized and can be used for comparison.

        Note that this fudges the rolename of the object to match more closely
        what it is.  The only thing that is being fudged right now is to
        coalesce radio and check menu items that are also submenus; gtk-demo
        has an example of this in its menus demo.
        """

        role = self.accessible.getRoleName()

        # [[[TODO: WDW - HACK to handle the situation where some
        # things might not be quite lined up with the ATK and AT-SPI.
        # That is, some roles might have ids but no string yet.  See
        # http://bugzilla.gnome.org/show_bug.cgi?id=361757.
        #
        if not len(role):
            try:
                roleId = self.accessible.getRole()
                if roleId == Accessibility.ROLE_LINK:
                    role = rolenames.ROLE_LINK
                elif roleId == Accessibility.ROLE_INPUT_METHOD_WINDOW:
                    role = rolenames.ROLE_INPUT_METHOD_WINDOW
            except:
                pass

        # [[[TODO: HACK to coalesce menu items with children into
        # menus.  The menu demo in gtk-demo does this, and one
        # might view that as an edge case.  But, in
        # gnome-terminal, "Terminal" -> "Set Character Encoding"
        # is a menu item with children, but it behaves like a
        # menu.]]]
        #
        if (role == rolenames.ROLE_CHECK_MENU_ITEM) \
            and (self.childCount > 0):
                role = rolenames.ROLE_CHECK_MENU
        elif (role == rolenames.ROLE_RADIO_MENU_ITEM) \
            and (self.childCount > 0):
                role = rolenames.ROLE_RADIO_MENU
        elif (role == rolenames.ROLE_MENU_ITEM) \
            and (self.childCount > 0):
                role = rolenames.ROLE_MENU

        # [[[TODO: HACK because Java gives us radio button role and
        # check box role for menu item objects, instead of giving us
        # radio menu item role and check menu item role (see SwingSet
        # menus).]]]
        #
        if (self.parent) and (self.parent.role == rolenames.ROLE_MENU):
            if (role == rolenames.ROLE_RADIO_BUTTON):
                role = rolenames.ROLE_RADIO_MENU_ITEM
            elif (role == rolenames.ROLE_CHECK_BOX):
                role = rolenames.ROLE_CHECK_MENU_ITEM

        # [[[TODO: HACK because we sometimes get an object with an
        # unknown role but it's role changes later on and we are not
        # notified.  An example of this is gnome-terminal.  So...to
        # help with this, we will not cache the role if it is unknown.
        # See http://bugzilla.gnome.org/show_bug.cgi?id=344218 for
        # more info.]]]
        #
        if role and settings.cacheValues \
            and (role != rolenames.ROLE_UNKNOWN):
            self.role = role

        return role

    def __get_localized_rolename(self):
        """Returns the Accessible role name of this object as a
        localized string.  Most callers should use __get_role instead
        since it returns a non-localized string that can be used for
        comparison.
        """

        localizedRoleName = self.accessible.getLocalizedRoleName()

        if localizedRoleName and settings.cacheValues:
            self.localizedRoleName = localizedRoleName

        return localizedRoleName

    def __get_state(self):
        """Returns the Accessible StateSeq of this object, which is a
        sequence of Accessible StateTypes.
        """

        try:
            stateSet = self.accessible.getState()
        except:
            stateSet = None
        if stateSet:
            try:
                state = stateSet._narrow(Accessibility.StateSet).getStates()
            except:
                state = []
        else:
            state = []

        # [[[WDW - we don't seem to always get appropriate state changed
        # information, so we will not cache state information.]]]
        #
        #if state and settings.cacheValues:
        #    self.state = state

        return state

    def __get_relations(self):
        """Returns the Accessible RelationSet of this object as a list.
        """

        relations = []

        relationSet = self.accessible.getRelationSet()

        for relation in relationSet:
            try:
                relations.append(relation._narrow(Accessibility.Relation))
            except:
                pass

        return relations

    def __get_app(self):
        """Returns the AT-SPI Accessibility_Application associated with this
        object.  Returns None if the application cannot be found (usually
        the indication of an AT-SPI bug).
        """

        # [[[TODO: WDW - this code seems like it might break if this
        # object is an application to begin with. Logged as bugzilla
        # bug 319677.]]]
        #
        debug.println(debug.LEVEL_FINEST,
                      "Finding app for source.name=" \
                      + self.accessibleNameToString())
        obj = self
        while obj.parent and (obj != obj.parent):
            obj = obj.parent
            debug.println(debug.LEVEL_FINEST,
                          "--> parent.name=" + obj.accessibleNameToString())

        if (obj == obj.parent):
            debug.println(debug.LEVEL_SEVERE,
                          "ERROR in Accessible.__get_app: obj == obj.parent!")
            return None
        elif (obj.role != rolenames.ROLE_APPLICATION):
            debug.println(debug.LEVEL_FINEST,
                          "ERROR in Accessible.__get_app: top most parent " \
                          "(name='%s') is of role %s" % (obj.name, obj.role))

            # [[[TODO: We'll let this fall through for some cases.  It
            # seems as though we don't always end up with an
            # application, but we do end up with *something* that is
            # uniquely identifiable as the app.
            #
            if (obj.role != rolenames.ROLE_INVALID) \
               and (obj.role != rolenames.ROLE_FRAME):
                return None

        debug.println(debug.LEVEL_FINEST, "Accessible app for %s is %s" \
                      % (self.accessibleNameToString(), \
                         obj.accessibleNameToString()))

        if settings.cacheValues:
            self.app = obj

        return obj

    def __get_extents(self, coordinateType = 0):
        """Returns the object's accessible extents as an
        Accessibility.BoundingBox object, or None if the object doesn't
        implement the Accessibility Component interface.

        Arguments:
        - coordinateType: 0 = get the extents in screen coordinates,
                          1 = get the extents in window coordinates

        Returns:
        This object's accessible extents as an Accessibility.BoundingBox
        object, or None if the object doesn't implement the Accessibility
        Component interface.
        """

        component = self.component

        if not component:
            return None

        extents = component.getExtents(coordinateType)

        # [[[TODO: WDW - caching the extents is dangerous because
        # the object may move, resulting in the current extents
        # becoming way out of date.  Perhaps need to cache just
        # the component interface and suffer the hit for getting
        # the extents if we cannot figure out how to determine if
        # the cached extents is out of date. Logged as bugzilla
        # bug 319678.]]]
        #
        #if settings.cacheValues:
        #    self.extents = extents

        return extents

    def __get_action(self):
        """Returns an object that implements the Accessibility_Action
        interface for this object, or None if this object doesn't implement
        the Accessibility_Action interface.
        """

        action = self.accessible.queryInterface("IDL:Accessibility/Action:1.0")

        if action:
            try:
                action = action._narrow(Accessibility.Action)
            except:
                action = None

        if action and settings.cacheValues:
            self.action = action

        return action

    def __get_component(self):
        """Returns an object that implements the Accessibility_Component
        interface for this object, or None if this object doesn't implement
        the Accessibility_Component interface.
        """

        component = self.accessible.queryInterface(\
            "IDL:Accessibility/Component:1.0")

        if component:
            try:
                component = component._narrow(Accessibility.Component)
            except:
                component = None

        if component and settings.cacheValues:
            self.component = component

        return component

    def __get_hyperlink(self):
        """Returns an object that implements the Accessibility_Hyperlink
        interface for this object, or None if this object doesn't implement
        the Accessibility_Hyperlink interface.
        """

        hyperlink = self.accessible.queryInterface(\
            "IDL:Accessibility/Hyperlink:1.0")

        if hyperlink:
            try:
                hyperlink = hyperlink._narrow(Accessibility.Hyperlink)
            except:
                hyperlink = None

        if hyperlink and settings.cacheValues:
            self.hyperlink = hyperlink

        return hyperlink

    def __get_hypertext(self):
        """Returns an object that implements the Accessibility_Hypertext
        interface for this object, or None if this object doesn't implement
        the Accessibility_Hypertext interface.
        """

        hypertext = self.accessible.queryInterface(\
            "IDL:Accessibility/Hypertext:1.0")

        if hypertext:
            try:
                hypertext = hypertext._narrow(Accessibility.Hypertext)
            except:
                hypertext = None

        if hypertext and settings.cacheValues:
            self.hypertext = hypertext

        return hypertext

    def __get_image(self):
        """Returns an object that implements the Accessibility_Image
        interface for this object, or None if this object doesn't implement
        the Accessibility_Image interface.
        """

        image = self.accessible.queryInterface(\
            "IDL:Accessibility/Image:1.0")

        if image:
            try:
                image = image._narrow(Accessibility.Image)
            except:
                image = None

        if image and settings.cacheValues:
            self.image = image

        return image

    def __get_selection(self):
        """Returns an object that implements the Accessibility_Selection
        interface for this object, or None if this object doesn't implement
        the Accessibility_Selection interface.
        """

        selection = self.accessible.queryInterface(\
            "IDL:Accessibility/Selection:1.0")

        if selection:
            try:
                selection = selection._narrow(Accessibility.Selection)
            except:
                selection = None

        if selection and settings.cacheValues:
            self.selection = selection

        return selection

    def __get_table(self):
        """Returns an object that implements the Accessibility_Table
        interface for this object, or None if this object doesn't implement
        the Accessibility_Table interface.
        """

        table = self.accessible.queryInterface("IDL:Accessibility/Table:1.0")

        if table:
            try:
                table = table._narrow(Accessibility.Table)
            except:
                table = None

        if table and settings.cacheValues:
            self.table = table

        return table

    def __get_text(self):
        """Returns an object that implements the Accessibility_Text
        interface for this object, or None if this object doesn't implement
        the Accessibility_Text interface.
        """

        text = self.accessible.queryInterface("IDL:Accessibility/Text:1.0")

        if text:
            try:
                text = text._narrow(Accessibility.Text)
            except:
                text = None

        if text and settings.cacheValues:
            self.text = text

        return text

    def __get_value(self):
        """Returns an object that implements the Accessibility_Value
        interface for this object, or None if this object doesn't implement
        the Accessibility_Value interface.
        """

        value = self.accessible.queryInterface("IDL:Accessibility/Value:1.0")

        if value:
            try:
                value = value._narrow(Accessibility.Value)
            except:
                value = None

        if value and settings.cacheValues:
            self.value = value

        return value

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

        if attr == "name":
            return self.__get_name()
        elif attr == "description":
            return self.__get_description()
        elif attr == "parent":
            return self.__get_parent()
        elif attr == "childCount":
            return self.__get_child_count()
        elif attr == "index":
            return self.__get_index()
        elif attr == "role":
            return self.__get_role()
        elif attr == "localizedRoleName":
            return self.__get_localized_rolename()
        elif attr == "state":
            return self.__get_state()
        elif attr == "relations":
            return self.__get_relations()
        elif attr == "app":
            return self.__get_app()
        elif attr == "extents":
            return self.__get_extents()
        elif attr == "action":
            return self.__get_action()
        elif attr == "component":
            return self.__get_component()
        elif attr == "hyperlink":
            return self.__get_hyperlink()
        elif attr == "hypertext":
            return self.__get_hypertext()
        elif attr == "image":
            return self.__get_image()
        elif attr == "selection":
            return self.__get_selection()
        elif attr == "table":
            return self.__get_table()
        elif attr == "text":
            return self.__get_text()
        elif attr == "value":
            return self.__get_value()
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError, attr
        else:
            return self.__dict__[attr]

    def child(self, index):
        """Returns the specified child of this object.

        Arguments:
        - index: an integer specifying which child to obtain

        Returns the child at the given index or raise an exception if the
        index is out of bounds or the child is invalid.
        """

        # [[[TODO: WDW - the AT-SPI appears to give us a different accessible
        # when we repeatedly ask for the same child of a parent that manages
        # its descendants.  So...we probably shouldn't cache those kind of
        # children because we're likely to cause a memory leak.]]]
        #
        # Save away details we now know about this child
        #
        newChild = None
        if index >= 0 and index < self.accessible.childCount:
            accChild = self.accessible.getChildAtIndex(index)
            if accChild:
                newChild = Accessible.makeAccessible(accChild)
                newChild.index = index
                newChild.parent = self
                newChild.app = self.app

        if not newChild:
            # The problem with a child not existing is a bad one.
            # We want to issue a warning and we also want to know
            # where it happens.
            #
            debug.printStack(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_WARNING,
                          "Child at index %d is not an Accessible" % index)

        return newChild

    def toString(self, indent="", includeApp=True):

        """Returns a string, suitable for printing, that describes the
        given accessible.

        Arguments:
        - indent: A string to prefix the output with
        - includeApp: If True, include information about the app
                      for this accessible.
        """

        if includeApp:
            if self.app:
                string = indent + "app.name=%-20s " \
                         % self.app.accessibleNameToString()
            else:
                string = indent + "app=None "
        else:
            string = indent

        string += "name=%s role='%s' state='%s' relations='%s'" \
                  % (self.accessibleNameToString(),
                     self.role,
                     self.getStateString(),
                     self.getRelationString())

        return string

########################################################################
#                                                                      #
# Testing functions.                                                   #
#                                                                      #
########################################################################

def __printTopObject(child):
    parent = child
    while parent:
        if not parent.parent:
            print "RAW TOP:", parent.name, parent.role
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
        __printTopObject(event.source)
        if not event.source.parent:
            print "NO PARENT:", event.source.name, event.source.role

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

    __printDesktops()

    registry = Registry()
    for eventType in eventTypes:
        registry.registerEventListener(__notifyEvent, eventType)
    registry.registerKeystrokeListeners(__notifyKeystroke)
    registry.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, __shutdownAndExit)
    signal.signal(signal.SIGQUIT, __shutdownAndExit)
    __test()
