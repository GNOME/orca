import bisect
import copy
import pyatspi
import time
from gi.repository import GLib

from . import cmdnames
from . import chnames
from . import keybindings
from . import messages
from . import input_event
from . import orca_state
from . import settings_manager

_settingsManager = settings_manager.getManager()

# define 'live' property types
LIVE_OFF       = -1
LIVE_NONE      = 0
LIVE_POLITE    = 1
LIVE_ASSERTIVE = 2
LIVE_RUDE      = 3

# Seconds a message is held in the queue before it is discarded
MSG_KEEPALIVE_TIME = 45  # in seconds

# The number of messages that are cached and can later be reviewed via 
# LiveRegionManager.reviewLiveAnnouncement.
CACHE_SIZE = 9  # corresponds to one of nine key bindings

class PriorityQueue:
    """ This class represents a thread **UNSAFE** priority queue where priority
    is determined by the given integer priority.  The entries are also   
    maintained in chronological order. 

    TODO: experiment with Queue.Queue to make thread safe
    """
    def __init__(self):
        self.queue = []

    def enqueue(self, data, priority, obj):
        """ Add a new element to the queue according to 1) priority and
        2) timestamp. """
        bisect.insort_left(self.queue, (priority, time.time(), data, obj))
       
    def dequeue(self):
        """get the highest priority element from the queue.  """
        return self.queue.pop(0)

    def clear(self):
        """ Clear the queue """
        self.queue = []

    def purgeByKeepAlive(self):
        """ Purge items from the queue that are older than the keepalive 
        time """
        currenttime = time.time()
        myfilter = lambda item: item[1] + MSG_KEEPALIVE_TIME > currenttime
        self.queue = list(filter(myfilter, self.queue))

    def purgeByPriority(self, priority):
        """ Purge items from the queue that have a lower than or equal priority
        than the given argument """
        myfilter = lambda item: item[0] > priority
        self.queue = list(filter(myfilter, self.queue))

    def __len__(self):
        """ Return the length of the queue """
        return len(self.queue)


class LiveRegionManager:
    def __init__(self, script):
        self._script = script
        # message priority queue
        self.msg_queue = PriorityQueue()

        self.inputEventHandlers = self._getInputEventHandlers()
        self.keyBindings = self._getKeyBindings()

        # This is temporary.
        self.functions = [self.advancePoliteness,
                          self.setLivePolitenessOff,
                          self.toggleMonitoring,
                          self.reviewLiveAnnouncement]

        # Message cache.  Used to store up to 9 previous messages so user can
        # review if desired.
        self.msg_cache = []

        # User overrides for politeness settings.
        self._politenessOverrides = None
        self._restoreOverrides = None

        # last live obj to be announced
        self.lastliveobj = None

        # Used to track whether a user wants to monitor all live regions
        # Not to be confused with the global Gecko.liveRegionsOn which 
        # completely turns off live region support.  This one is based on
        # a user control by changing politeness levels to LIVE_OFF or back
        # to the bookmark or markup politeness value.
        self.monitoring = True

        # Set up politeness level overrides and subscribe to bookmarks
        # for load and save user events.
        # We are initialized after bookmarks so call the load handler once
        # to get initialized.
        #
        self.bookmarkLoadHandler()
        script.bookmarks.addSaveObserver(self.bookmarkSaveHandler)
        script.bookmarks.addLoadObserver(self.bookmarkLoadHandler)

    def _getInputEventHandlers(self):
        handlers = {}

        handlers["advanceLivePoliteness"] = \
            input_event.InputEventHandler(
                self.advancePoliteness,
                cmdnames.LIVE_REGIONS_ADVANCE_POLITENESS)

        handlers["setLivePolitenessOff"] = \
            input_event.InputEventHandler(
                self.setLivePolitenessOff,
                cmdnames.LIVE_REGIONS_SET_POLITENESS_OFF)

        handlers["monitorLiveRegions"] = \
            input_event.InputEventHandler(
                self.toggleMonitoring,
                cmdnames.LIVE_REGIONS_MONITOR)

        handlers["reviewLiveAnnouncement"] = \
            input_event.InputEventHandler(
                self.reviewLiveAnnouncement,
                cmdnames.LIVE_REGIONS_REVIEW)

        return handlers

    def _getKeyBindings(self):
        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.inputEventHandlers.get("advanceLivePoliteness")))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_MODIFIER_MASK,
                self.inputEventHandlers.get("setLivePolitenessOff")))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self.inputEventHandlers.get("monitorLiveRegions")))

        for key in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            keyBindings.add(
                keybindings.KeyBinding(
                    key,
                    keybindings.defaultModifierMask,
                    keybindings.ORCA_MODIFIER_MASK,
                    self.inputEventHandlers.get("reviewLiveAnnouncement")))

        return keyBindings

    def reset(self):
        # First we will purge our politeness override dictionary of LIVE_NONE
        # objects that are not registered for this page
        newpoliteness = {}
        currenturi = self._script.bookmarks.getURIKey()
        for key, value in list(self._politenessOverrides.items()):
            if key[0] == currenturi or value != LIVE_NONE:
                newpoliteness[key] = value
        self._politenessOverrides = newpoliteness

    def bookmarkSaveHandler(self):
        """Bookmark save callback"""
        self._script.bookmarks.saveBookmarksToDisk(self._politenessOverrides,
                                                    filename='politeness')

    def bookmarkLoadHandler(self):
        """Bookmark load callback"""
        # readBookmarksFromDisk() returns None on error. Just initialize to an
        # empty dictionary if this is the case.
        self._politenessOverrides = \
        self._script.bookmarks.readBookmarksFromDisk(filename='politeness') \
        or {}

    def handleEvent(self, event):
        """Main live region event handler"""
        politeness = self._getLiveType(event.source)
        if politeness == LIVE_OFF:
            return
        if politeness == LIVE_NONE:
            # All the 'registered' LIVE_NONE objects will be set to off
            # if not monitoring.  We will ignore LIVE_NONE objects that 
            # arrive after the user switches off monitoring.
            if not self.monitoring:
                return
        elif politeness == LIVE_POLITE:
            # Nothing to do for now
            pass
        elif politeness ==  LIVE_ASSERTIVE:
            self.msg_queue.purgeByPriority(LIVE_POLITE)
        elif politeness == LIVE_RUDE:
            self.msg_queue.purgeByPriority(LIVE_ASSERTIVE)

        message = self._getMessage(event)
        if message:
            if len(self.msg_queue) == 0:
                GLib.timeout_add(100, self.pumpMessages)
            self.msg_queue.enqueue(message, politeness, event.source)

    def pumpMessages(self):
        """ Main gobject callback for live region support.  Handles both 
        purging the message queue and outputting any queued messages that
        were queued up in the handleEvent() method.
        """

        if len(self.msg_queue) > 0:
            self.msg_queue.purgeByKeepAlive()
            politeness, timestamp, message, obj = self.msg_queue.dequeue()
            # Form output message.  No need to repeat labels and content.
            # TODO: really needs to be tested in real life cases.  Perhaps
            # a verbosity setting?
            if message['labels'] == message['content']:
                utts = message['content']
            else:
                utts = message['labels'] + message['content']
            self._script.presentMessage(utts)

            # set the last live obj to be announced
            self.lastliveobj = obj

            # cache our message
            self._cacheMessage(utts)

        # We still want to maintain our queue if we are not monitoring
        if not self.monitoring:
            self.msg_queue.purgeByKeepAlive()

        # See you again soon, stay in event loop if we still have messages.
        if len(self.msg_queue) > 0:
            return True 
        else:
            return False
        
    def getLiveNoneObjects(self):
        """Return the live objects that are registered and have a politeness
        of LIVE_NONE. """
        retval = []
        currenturi = self._script.bookmarks.getURIKey()
        for uri, objectid in self._politenessOverrides:
            if uri == currenturi and isinstance(objectid, tuple):
                retval.append(self._script.bookmarks.pathToObj(objectid))
        return retval

    def advancePoliteness(self, script, inputEvent):
        """Advance the politeness level of the given object"""

        if not _settingsManager.getSetting('inferLiveRegions'):
            self._script.presentMessage(messages.LIVE_REGIONS_OFF)
            return

        obj = orca_state.locusOfFocus
        objectid = self._getObjectId(obj)
        uri = self._script.bookmarks.getURIKey()

        try:
            # The current priority is either a previous override or the
            # live property.  If an exception is thrown, an override for 
            # this object has never occurred and the object does not have
            # live markup.  In either case, set the override to LIVE_NONE.
            cur_priority = self._politenessOverrides[(uri, objectid)] 
        except KeyError:
            cur_priority = self._liveStringToType(obj)

        if cur_priority == LIVE_OFF or cur_priority == LIVE_NONE:
            self._politenessOverrides[(uri, objectid)] = LIVE_POLITE
            self._script.presentMessage(messages.LIVE_REGIONS_LEVEL_POLITE)
        elif cur_priority == LIVE_POLITE:
            self._politenessOverrides[(uri, objectid)] = LIVE_ASSERTIVE
            self._script.presentMessage(messages.LIVE_REGIONS_LEVEL_ASSERTIVE)
        elif cur_priority == LIVE_ASSERTIVE:
            self._politenessOverrides[(uri, objectid)] = LIVE_RUDE
            self._script.presentMessage(messages.LIVE_REGIONS_LEVEL_RUDE)
        elif cur_priority == LIVE_RUDE:
            self._politenessOverrides[(uri, objectid)] = LIVE_OFF
            self._script.presentMessage(messages.LIVE_REGIONS_LEVEL_OFF)


    def goLastLiveRegion(self):
        """Move the caret to the last announced live region and speak the 
        contents of that object"""
        if self.lastliveobj:
            self._script.utilities.setCaretPosition(self.lastliveobj, 0)
            self._script.speakContents(self._script.utilities.getObjectContentsAtOffset(
                                       self.lastliveobj, 0))

    def reviewLiveAnnouncement(self, script, inputEvent):
        """Speak the given number cached message"""

        msgnum = int(inputEvent.event_string[1:])
        if not _settingsManager.getSetting('inferLiveRegions'):
            self._script.presentMessage(messages.LIVE_REGIONS_OFF)
            return

        if msgnum > len(self.msg_cache):
            self._script.presentMessage(messages.LIVE_REGIONS_NO_MESSAGE)
        else:
            self._script.presentMessage(self.msg_cache[-msgnum])

    def setLivePolitenessOff(self, script, inputEvent):
        """User toggle to set all live regions to LIVE_OFF or back to their
        original politeness."""

        if not _settingsManager.getSetting('inferLiveRegions'):
            self._script.presentMessage(messages.LIVE_REGIONS_OFF)
            return

        # start at the document frame
        docframe = self._script.utilities.documentFrame()
        # get the URI of the page.  It is used as a partial key.
        uri = self._script.bookmarks.getURIKey()

        # The user is currently monitoring live regions but now wants to 
        # change all live region politeness on page to LIVE_OFF
        if self.monitoring:
            self._script.presentMessage(messages.LIVE_REGIONS_ALL_OFF)
            self.msg_queue.clear()
            
            # First we'll save off a copy for quick restoration
            self._restoreOverrides = copy.copy(self._politenessOverrides)

            # Set all politeness overrides to LIVE_OFF.
            for override in list(self._politenessOverrides.keys()):
                self._politenessOverrides[override] = LIVE_OFF

            # look through all the objects on the page and set/add to
            # politeness overrides.  This only adds live regions with good
            # markup.
            matches = pyatspi.findAllDescendants(docframe, self.matchLiveRegion)
            for match in matches:
                objectid = self._getObjectId(match)
                self._politenessOverrides[(uri, objectid)] = LIVE_OFF

            # Toggle our flag
            self.monitoring = False

        # The user wants to restore politeness levels
        else:
            for key, value in list(self._restoreOverrides.items()):
                self._politenessOverrides[key] = value
            self._script.presentMessage(messages.LIVE_REGIONS_ALL_RESTORED)
            # Toggle our flag
            self.monitoring = True  

    def generateLiveRegionDescription(self, obj, **args):
        """Used in conjuction with whereAmI to output description and 
        politeness of the given live region object"""
        objectid = self._getObjectId(obj)
        uri = self._script.bookmarks.getURIKey()

        results = []

        # get the description if there is one.
        for relation in obj.getRelationSet():
            relationtype = relation.getRelationType()
            if relationtype == pyatspi.RELATION_DESCRIBED_BY:
                targetobj = relation.getTarget(0)
                try:
                    # We will add on descriptions if they don't duplicate
                    # what's already in the object's description.
                    # See http://bugzilla.gnome.org/show_bug.cgi?id=568467
                    # for more information.
                    #
                    description = targetobj.queryText().getText(0, -1)
                    if description.strip() != obj.description.strip():
                        results.append(description)
                except NotImplemented:
                    pass

        # get the politeness level as a string
        try:
            livepriority = self._politenessOverrides[(uri, objectid)]
            liveprioritystr = self._liveTypeToString(livepriority)
        except KeyError:
            liveprioritystr = 'none'

        # We will only output useful information
        # 
        if results or liveprioritystr != 'none':
            results.append(messages.LIVE_REGIONS_LEVEL % liveprioritystr)

        return results

    def matchLiveRegion(self, obj):
        """Predicate used to find a live region"""
        attrs = self._getAttrDictionary(obj)
        return 'container-live' in attrs

    def _getMessage(self, event):
        """Gets the message associated with a given live event."""
        attrs = self._getAttrDictionary(event.source)
        content = ""
        labels = ""
        
        # A message is divided into two parts: labels and content.  We
        # will first try to get the content.  If there is None, 
        # assume it is an invalid message and return None
        if event.type.startswith('object:children-changed:add'):
            if attrs.get('container-atomic') == 'true':
                content = self._script.utilities.expandEOCs(event.source)
            else:
                content = self._script.utilities.expandEOCs(event.any_data)

        elif event.type.startswith('object:text-changed:insert'):
            if attrs.get('container-atomic') != 'true':
                content = event.any_data
            else:
                text = self._script.utilities.queryNonEmptyText(event.source)
                if text:
                    content = text.getText(0, -1)

        if not content:
            return None

        content = content.strip()
        if len(content) == 1:
            content = chnames.getCharacterName(content)

        # Proper live regions typically come with proper aria labels. These
        # labels are typically exposed as names. Failing that, descriptions.
        # Looking for actual labels seems a non-performant waste of time.
        name = (event.source.name or event.source.description).strip()
        if name and name != content:
            labels = name

        # instantly send out notify messages
        if attrs.get('channel') == 'notify':
            utts = labels + content
            self._script.presentationInterrupt()
            self._script.presentMessage(utts)
            return None

        return {'content':[content], 'labels':[labels]}

    def flushMessages(self):
        self.msg_queue.clear()

    def _cacheMessage(self, utts):
        """Cache a message in our cache list of length CACHE_SIZE"""
        self.msg_cache.append(utts)
        if len(self.msg_cache) > CACHE_SIZE:
            self.msg_cache.pop(0)

    def _getLiveType(self, obj):
        """Returns the live politeness setting for a given object. Also,
        registers LIVE_NONE objects in politeness overrides when monitoring."""
        objectid = self._getObjectId(obj)
        uri = self._script.bookmarks.getURIKey()
        if (uri, objectid) in self._politenessOverrides:
            # look to see if there is a user politeness override
            return self._politenessOverrides[(uri, objectid)]
        else:
            livetype = self._liveStringToType(obj)
            # We'll save off a reference to LIVE_NONE if we are monitoring
            # to give the user a chance to change the politeness level.  It
            # is done here for performance sake (objectid, uri are expensive)
            if livetype == LIVE_NONE and self.monitoring:
                self._politenessOverrides[(uri, objectid)] = livetype
            return livetype

    def _getObjectId(self, obj):
        """Returns the HTML 'id' or a path to the object is an HTML id is
        unavailable"""
        attrs = self._getAttrDictionary(obj)
        if attrs is None:
            return self._getPath(obj)
        try:
            return attrs['id']
        except KeyError:
            return self._getPath(obj)

    def _liveStringToType(self, obj, attributes=None):
        """Returns the politeness enum for a given object"""
        attrs = attributes or self._getAttrDictionary(obj)
        try:
            if attrs['container-live'] == 'off': 
                return LIVE_OFF
            elif attrs['container-live'] == 'polite':  
                return LIVE_POLITE
            elif attrs['container-live'] == 'assertive': 
                return LIVE_ASSERTIVE
            elif attrs['container-live'] == 'rude': 
                return LIVE_RUDE
            else: return LIVE_NONE
        except KeyError:
            return LIVE_NONE

    def _liveTypeToString(self, politeness):
        """Returns the politeness level as a string given a politeness enum"""
        if politeness == LIVE_OFF: 
            return 'off'
        elif politeness == LIVE_POLITE: 
            return 'polite'
        elif politeness == LIVE_ASSERTIVE: 
            return 'assertive'
        elif politeness == LIVE_RUDE: 
            return 'rude'
        elif politeness == LIVE_NONE: 
            return 'none'
        else: return 'unknown'

    def _getAttrDictionary(self, obj):
        try:
            return dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return {}
    
    def _getPath(self, obj):
        """ Returns, as a tuple of integers, the path from the given object 
        to the document frame."""
        docframe = self._script.utilities.documentFrame()
        path = []
        while True:
            if obj.parent is None or obj == docframe:
                path.reverse()
                return tuple(path)
            try:
                path.append(obj.getIndexInParent())
            except Exception:
                raise LookupError
            obj = obj.parent

    def toggleMonitoring(self, script, inputEvent):
        if not _settingsManager.getSetting('inferLiveRegions'):
            _settingsManager.setSetting('inferLiveRegions', True)
            self._script.presentMessage(messages.LIVE_REGIONS_MONITORING_ON)
        else:
            _settingsManager.setSetting('inferLiveRegions', False)
            self.flushMessages()
            self._script.presentMessage(messages.LIVE_REGIONS_MONITORING_OFF)
