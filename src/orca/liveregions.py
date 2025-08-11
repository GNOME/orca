import bisect
import copy
import time
from gi.repository import GLib

from . import cmdnames
from . import debug
from . import focus_manager
from . import keybindings
from . import messages
from . import input_event
from . import settings_manager
from .ax_collection import AXCollection
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

LIVE_OFF       = -1
LIVE_NONE      = 0
LIVE_POLITE    = 1
LIVE_ASSERTIVE = 2

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
        """ Purge items from the queue that are older than the keepalive time """
        currenttime = time.time()

        def myfilter(item):
            return item and item[1] + MSG_KEEPALIVE_TIME > currenttime

        self.queue = list(filter(myfilter, self.queue))

    def purgeByPriority(self, priority):
        """ Purge items from the queue that have a lower than or equal priority
        than the given argument """

        def myfilter(item):
            return item and item[0] > priority

        self.queue = list(filter(myfilter, self.queue))

    def __len__(self):
        """ Return the length of the queue """
        return len(self.queue)


class LiveRegionManager:
    def __init__(self, script):
        self._script = script
        # message priority queue
        self.msg_queue = PriorityQueue()

        # To make it possible for focus mode to suspend commands without changing
        # the user's preferred setting.
        self._suspended = False

        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

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

        self._last_presented_timestamp = None
        self._last_presented_message = ""

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

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the live-region-manager keybindings."""

        if refresh:
            msg = "LIVE REGION MANAGER: Refreshing bindings."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("LIVE REGION MANAGER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the live-region-manager handlers."""

        if refresh:
            msg = "LIVE REGION MANAGER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up the live-region-manager input event handlers."""

        self._handlers = {}

        self._handlers["advanceLivePoliteness"] = \
            input_event.InputEventHandler(
                self.advancePoliteness,
                cmdnames.LIVE_REGIONS_ADVANCE_POLITENESS,
                enabled = not self._suspended)

        self._handlers["setLivePolitenessOff"] = \
            input_event.InputEventHandler(
                self.setLivePolitenessOff,
                cmdnames.LIVE_REGIONS_SET_POLITENESS_OFF,
                enabled = not self._suspended)

        self._handlers["monitorLiveRegions"] = \
            input_event.InputEventHandler(
                self.toggleMonitoring,
                cmdnames.LIVE_REGIONS_MONITOR,
                enabled = not self._suspended)

        self._handlers["reviewLiveAnnouncement"] = \
            input_event.InputEventHandler(
                self.reviewLiveAnnouncement,
                cmdnames.LIVE_REGIONS_REVIEW,
                enabled = not self._suspended)

        msg = f"LIVE REGION MANAGER: Handlers set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the live-region-manager key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "backslash",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("advanceLivePoliteness"),
                1,
                not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "backslash",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers.get("setLivePolitenessOff"),
                1,
                not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "backslash",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("monitorLiveRegions"),
                1,
                not self._suspended))

        for key in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            self._bindings.add(
                keybindings.KeyBinding(
                    key,
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.ORCA_MODIFIER_MASK,
                    self._handlers.get("reviewLiveAnnouncement"),
                    1,
                    not self._suspended))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.get_manager().override_key_bindings(
            self._handlers, self._bindings, False)

        msg = f"LIVE REGION MANAGER: Bindings set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def refresh_bindings_and_grabs(self, script, reason=""):
        """Refreshes live region bindings and grabs for script."""

        msg = "LIVE REGION MANAGER: Refreshing bindings and grabs"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.remove(binding, include_grabs=True)

        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.add(binding, include_grabs=not self._suspended)

    def suspend_commands(self, script, suspended, reason=""):
        """Suspends live region commands independent of the enabled setting."""

        if suspended == self._suspended:
            return

        msg = f"LIVE REGION MANAGER: Commands suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._suspended = suspended
        self.refresh_bindings_and_grabs(script, f"Suspended changed to {suspended}")

    def reset(self):
        # First we will purge our politeness override dictionary of LIVE_NONE
        # objects that are not registered for this page
        newpoliteness = {}
        currenturi = self._script.bookmarks.getURIKey()
        for key, value in self._politenessOverrides.items():
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

    def _is_duplicate_message(self, message):
        msg = f"LIVE REGION MANAGER: Message ({message}) is duplicate: "
        if self._last_presented_timestamp is None:
            msg += "False, no previous message"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        if message != self._last_presented_message:
            msg += f"False, message is different (last message: {self._last_presented_message})"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        delta = time.time() - self._last_presented_timestamp
        if delta > 1:
            msg += f"False, last message content is same, but was {delta:.4f}s ago"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        msg += f"True, last message content is same and was {delta:.4f}s ago"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def handleEvent(self, event):
        """Main live region event handler"""
        politeness = self._getLivevent_type(event.source)
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

        message = self._getMessage(event)
        if message and not self._is_duplicate_message(message):
            self._last_presented_message = message
            self._last_presented_timestamp = time.time()

            if len(self.msg_queue) == 0:
                GLib.timeout_add(100, self.pumpMessages)
            self.msg_queue.enqueue(message, politeness, event.source)

    def pumpMessages(self):
        """ Main gobject callback for live region support.  Handles both
        purging the message queue and outputting any queued messages that
        were queued up in the handleEvent() method.
        """

        if len(self.msg_queue) > 0:
            debug.print_message(debug.LEVEL_INFO, "\nvvvvv PRESENT LIVE REGION MESSAGE vvvvv")
            self.msg_queue.purgeByKeepAlive()
            politeness, timestamp, message, obj = self.msg_queue.dequeue()
            # Form output message.  No need to repeat labels and content.
            # TODO: really needs to be tested in real life cases.  Perhaps
            # a verbosity setting?
            if message['labels'] == message['content']:
                utts = message['content']
            else:
                utts = message['labels'] + message['content']

            if self.monitoring:
                if isinstance(utts, list):
                    utts = " ".join(utts)
                self._script.present_message(utts)
            else:
                msg = "INFO: Not presenting message because monitoring is off"
                debug.print_message(debug.LEVEL_INFO, msg, True)

            # set the last live obj to be announced
            self.lastliveobj = obj

            # cache our message
            self._cacheMessage(utts)

        # We still want to maintain our queue if we are not monitoring
        if not self.monitoring:
            self.msg_queue.purgeByKeepAlive()

        msg = f'LIVE REGIONS: messages in queue: {len(self.msg_queue)}'
        debug.print_message(debug.LEVEL_INFO, msg, True)
        debug.print_message(debug.LEVEL_INFO, "^^^^^ PRESENT LIVE REGION MESSAGE ^^^^^\n")

        # See you again soon, stay in event loop if we still have messages.
        return len(self.msg_queue) > 0

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

        if not settings_manager.get_manager().get_setting('inferLiveRegions'):
            self._script.present_message(messages.LIVE_REGIONS_OFF)
            return

        obj = focus_manager.get_manager().get_locus_of_focus()
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
            self._script.present_message(messages.LIVE_REGIONS_LEVEL_POLITE)
        elif cur_priority == LIVE_POLITE:
            self._politenessOverrides[(uri, objectid)] = LIVE_ASSERTIVE
            self._script.present_message(messages.LIVE_REGIONS_LEVEL_ASSERTIVE)
        elif cur_priority == LIVE_ASSERTIVE:
            self._politenessOverrides[(uri, objectid)] = LIVE_OFF
            self._script.present_message(messages.LIVE_REGIONS_LEVEL_OFF)

    def goLastLiveRegion(self):
        """Move the caret to the last announced live region and speak the
        contents of that object"""
        if self.lastliveobj:
            self._script.utilities.set_caret_position(self.lastliveobj, 0)
            self._script.speak_contents(self._script.utilities.get_object_contents_at_offset(
                                       self.lastliveobj, 0))

    def reviewLiveAnnouncement(self, script, inputEvent):
        """Speak the given number cached message"""

        msgnum = int(inputEvent.keyval_name[1:])
        if not settings_manager.get_manager().get_setting('inferLiveRegions'):
            self._script.present_message(messages.LIVE_REGIONS_OFF)
            return

        if msgnum > len(self.msg_cache):
            self._script.present_message(messages.LIVE_REGIONS_NO_MESSAGE)
        else:
            self._script.present_message(self.msg_cache[-msgnum])

    def setLivePolitenessOff(self, script, inputEvent):
        """User toggle to set all live regions to LIVE_OFF or back to their
        original politeness."""

        if not settings_manager.get_manager().get_setting('inferLiveRegions'):
            self._script.present_message(messages.LIVE_REGIONS_OFF)
            return

        # start at the document frame
        docframe = self._script.utilities.active_document()
        # get the URI of the page.  It is used as a partial key.
        uri = self._script.bookmarks.getURIKey()

        # The user is currently monitoring live regions but now wants to
        # change all live region politeness on page to LIVE_OFF
        if self.monitoring:
            self._script.present_message(messages.LIVE_REGIONS_ALL_OFF)
            self.msg_queue.clear()

            # First we'll save off a copy for quick restoration
            self._restoreOverrides = copy.copy(self._politenessOverrides)

            # Set all politeness overrides to LIVE_OFF.
            for override in self._politenessOverrides.keys():
                self._politenessOverrides[override] = LIVE_OFF

            # look through all the objects on the page and set/add to
            # politeness overrides.  This only adds live regions with good
            # markup.
            matches = self.getAllLiveRegions(docframe)
            for match in matches:
                objectid = self._getObjectId(match)
                self._politenessOverrides[(uri, objectid)] = LIVE_OFF

            # Toggle our flag
            self.monitoring = False

        # The user wants to restore politeness levels
        else:
            for key, value in self._restoreOverrides.items():
                self._politenessOverrides[key] = value
            self._script.present_message(messages.LIVE_REGIONS_ALL_RESTORED)
            # Toggle our flag
            self.monitoring = True

    def getAllLiveRegions(self, document):
        attrs = []
        levels = ["off", "polite", "assertive"]
        for level in levels:
            attrs.append('container-live:' + level)

        rule = AXCollection.create_match_rule(attributes=attrs)
        result = AXCollection.get_all_matches(document, rule)

        msg = f'LIVE REGIONS: {len(result)} regions found'
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def generateLiveRegionDescription(self, obj, **args):
        """Used in conjunction with whereAmI to output description and
        politeness of the given live region object"""
        objectid = self._getObjectId(obj)
        uri = self._script.bookmarks.getURIKey()

        results = []

        # get the description if there is one.
        targetobj = None
        targets = AXUtilities.get_is_described_by(obj)
        if targets:
            targetobj = targets[0]
            # We will add on descriptions if they don't duplicate
            # what's already in the object's description.
            # See http://bugzilla.gnome.org/show_bug.cgi?id=568467
            # for more information.
            description = AXText.get_all_text(targetobj)
            if description.strip() != AXObject.get_description(obj).strip():
                results.append(description)

        # get the politeness level as a string
        try:
            livepriority = self._politenessOverrides[(uri, objectid)]
            liveprioritystr = self._livevent_typeToString(livepriority)
        except KeyError:
            liveprioritystr = 'none'

        # We will only output useful information
        #
        if results or liveprioritystr != 'none':
            results.append(messages.LIVE_REGIONS_LEVEL % liveprioritystr)

        return results

    def _findContainer(self, obj):
        def isContainer(x):
            return self._getAttrDictionary(x).get('atomic')

        if isContainer(obj):
            return obj

        return AXObject.find_ancestor(obj, isContainer)

    def _getMessage(self, event):
        """Gets the message associated with a given live event."""
        attrs = self._getAttrDictionary(event.source)
        content = ""
        labels = ""

        # A message is divided into two parts: labels and content.  We
        # will first try to get the content.  If there is None,
        # assume it is an invalid message and return None
        if event.type.startswith('object:text-changed:insert'):
            if attrs.get('container-atomic') != 'true':
                if "\ufffc" not in event.any_data:
                    content = event.any_data
                else:
                    content = self._script.utilities.expand_eocs(
                        event.source, event.detail1, event.detail1 + event.detail2)
            else:
                container = self._findContainer(event.source)
                content = self._script.utilities.expand_eocs(container)

        if not content:
            return None

        content = content.strip()

        # Proper live regions typically come with proper aria labels. These
        # labels are typically exposed as names. Failing that, descriptions.
        # Looking for actual labels seems a non-performant waste of time.
        name = (AXObject.get_name(event.source) or AXObject.get_description(event.source)).strip()
        if name and name != content:
            labels = name

        # instantly send out notify messages
        if attrs.get('channel') == 'notify':
            utts = labels + content
            self._script.interrupt_presentation()
            self._script.present_message(utts)
            return None

        return {'content':[content], 'labels':[labels]}

    def flushMessages(self):
        self.msg_queue.clear()

        # This function is called as part of presentation interrupt. One of the times we interrupt
        # presentation is in response to a key press. The motivation for clearing the last message
        # details is to prevent concluding incorrectly that a live region message is duplicate.
        # For instance, if the same live region message results from two different back-to-back key
        # presses, both of those messages should be presented.
        self._last_presented_message = ""
        self._last_presented_timestamp = None

    def _cacheMessage(self, utts):
        """Cache a message in our cache list of length CACHE_SIZE"""
        self.msg_cache.append(utts)
        if len(self.msg_cache) > CACHE_SIZE:
            self.msg_cache.pop(0)

    def _getLivevent_type(self, obj):
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
            else:
                return LIVE_NONE
        except KeyError:
            return LIVE_NONE

    def _livevent_typeToString(self, politeness):
        """Returns the politeness level as a string given a politeness enum"""
        if politeness == LIVE_OFF:
            return 'off'
        elif politeness == LIVE_POLITE:
            return 'polite'
        elif politeness == LIVE_ASSERTIVE:
            return 'assertive'
        elif politeness == LIVE_NONE:
            return 'none'
        else:
            return 'unknown'

    def _getAttrDictionary(self, obj):
        return AXObject.get_attributes_dict(obj)

    def _getPath(self, obj):
        """ Returns, as a tuple of integers, the path from the given object
        to the document frame."""
        docframe = self._script.utilities.active_document()
        path = []
        while True:
            if obj == docframe or AXObject.get_parent(obj) is None:
                path.reverse()
                return tuple(path)
            path.append(AXObject.get_index_in_parent(obj))
            obj = AXObject.get_parent(obj)

    def toggleMonitoring(self, script, inputEvent):
        if not settings_manager.get_manager().get_setting('inferLiveRegions'):
            settings_manager.get_manager().set_setting('inferLiveRegions', True)
            self._script.present_message(messages.LIVE_REGIONS_MONITORING_ON)
        else:
            settings_manager.get_manager().set_setting('inferLiveRegions', False)
            self.flushMessages()
            self._script.present_message(messages.LIVE_REGIONS_MONITORING_OFF)
