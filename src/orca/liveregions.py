import bisect
import gobject
import time
import pyatspi
import speech

from orca_i18n import _

# define 'live' property types
LIVE_OFF       = -1
LIVE_NONE      = 0
LIVE_POLITE    = 1
LIVE_ASSERTIVE = 2
LIVE_RUDE      = 3

# Seconds a message is held in the queue before it is discarded
MSG_KEEPALIVE_TIME = 5  # in seconds

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

    def enqueue(self, utts, priority, obj):
        """ Add a new element to the queue according to 1) priority and
        2) timestamp. """
        bisect.insort_left(self.queue, (priority, time.time(), utts, obj))
       
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
        self.queue = filter(myfilter, self.queue)

    def purgeByPriority(self, priority):
        """ Purge items from the queue that have a lower than or equal priority
        than the given argument """
        myfilter = lambda item: item[0] > priority
        self.queue = filter(myfilter, self.queue)

    def __len__(self):
        """ Return the length of the queue """
        return len(self.queue)


class LiveRegionManager:
    def __init__(self, script):
        self._script = script
        # message priority queue
        self.msg_queue = PriorityQueue()

        # Message cache.  Used to store up to 9 previous messages so user can
        # review if desired.
        self.msg_cache = []

        # User overrides for politeness settings.
        self._politenessOverrides = None

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

    def bookmarkSaveHandler(self):
        self._script.bookmarks.saveBookmarksToDisk(self._politenessOverrides,
                                                    filename='politeness')

    def bookmarkLoadHandler(self):
        # readBookmarksFromDisk() returns None on error. Just initialize to an
        # empty dictionary if this is the case.
        self._politenessOverrides = \
        self._script.bookmarks.readBookmarksFromDisk(filename='politeness') \
        or {}

    def handleEvent(self, event):

        livetype = self._getLiveType(event.source)
        # Purge our queue of messages based on priority of incoming event and
        # age of queued message.
        if livetype == LIVE_NONE:
            # 1) we won't do anything for bad markup right now.
            # 2) we won't waste processing power if live type is lower
            #    than user define.
            return

        # Add a callback if the queue is empty because we are about to add 
        # something to it.
        if len(self.msg_queue) == 0:
            gobject.idle_add(self.pumpMessages)

        if livetype == LIVE_POLITE:
            # Nothing to do for now
            pass
        elif livetype ==  LIVE_ASSERTIVE:
            self.msg_queue.purgeByPriority(LIVE_POLITE)
        elif livetype == LIVE_RUDE:
            self.msg_queue.purgeByPriority(LIVE_ASSERTIVE)

        utterance = self._getUtterances(event)
        if utterance:
            self.msg_queue.enqueue(utterance, livetype, event.source)

    def pumpMessages(self):
        """ Main gobject callback for live region support.  Handles both 
        purging the message queue and outputting any queued messages that
        were queued up in the handleEvent() method.
        """
        # House cleaning on the message queue.  No purging is
        # performed in handleEvent().
        self.msg_queue.purgeByKeepAlive()

        # If there are messages in the queue and we are not currently 
        # speaking then speak queued message.
        if len(self.msg_queue) > 0 and not speech.isSpeaking():
            politeness, timestamp, utts, obj = self.msg_queue.dequeue()
            speech.speakUtterances(utts)
            # set the last live obj to be announced
            self.lastliveobj = obj
            # cache our message
            self._cacheMessage(utts)

        # See you again soon, stay in event loop if we still have messages.
        if len(self.msg_queue) > 0:
            return True 
        else:
            return False

    def advancePoliteness(self, obj):
        utterances = []
        attrs = self._getAttrDictionary(obj)

        # Should probably never see this situation because ids are used by
        # web developers to identify the live region.  If we do, the user is
        # out of luck and cannot override politeness level
        if not attrs.has_key('id'):
            # Translators: Objects within webpages sometimes do not have ids.
            # In this rare case, the live politeness property cannot be 
            # overriden. 
            #
            utterances.append(_('object does not have id'))
            utterances.append(_('cannot override live priority'))
            speech.speakUtterances(utterances)
            return

        uri = self._script.bookmarks.getURIKey()

        try:
            # The current priority is either a previous override or the
            # live property.  If an exception is thrown, an override for 
            # this object has never occurred and the object does not have
            # live markup.  In either case, set the override to LIVE_NONE.
            if self._politenessOverrides.has_key((uri, attrs['id'])):
                cur_priority = self._politenessOverrides[(uri, attrs['id'])] 
            else:
                cur_priority = self._liveStringToType(obj, attributes=attrs)
        except KeyError:
            cur_priority = LIVE_NONE

        if cur_priority == LIVE_OFF or cur_priority == LIVE_NONE:
            self._politenessOverrides[(uri, attrs['id'])] = LIVE_POLITE
            # Translators:  sets the live region politeness level to polite
            #
            utterances.append(_('setting live region to polite'))
        elif cur_priority == LIVE_POLITE:
            self._politenessOverrides[(uri, attrs['id'])] = LIVE_ASSERTIVE
            # Translators:  sets the live region politeness level to assertive
            #
            utterances.append(_('setting live region to assertive'))
        elif cur_priority == LIVE_ASSERTIVE:
            self._politenessOverrides[(uri, attrs['id'])] = LIVE_RUDE
            # Translators:  sets the live region politeness level to rude
            #
            utterances.append(_('setting live region to rude'))
        elif cur_priority == LIVE_RUDE:
            self._politenessOverrides[(uri, attrs['id'])] = LIVE_OFF
            # Translators:  sets the live region politeness level to off
            #
            utterances.append(_('setting live region to off'))

        speech.speakUtterances(utterances)

    def goLastLiveRegion(self):
        if self.lastliveobj:
            self._script.setCaretPosition(self.lastliveobj, 0)
            self._script.outlineAccessible(self.lastliveobj)
            self._script.speakContents(self._script.getObjectContentsAtOffset(\
                                       self.lastliveobj,0))

    def reviewLiveAnnouncement(self, msgnum):
        if msgnum > len(self.msg_cache):
            # Tranlators: this tells the user that a cached message
            # is not available.
            #
            speech.speak(_('no live message saved'))
        else:
            speech.speakUtterances(self.msg_cache[-msgnum])

    def monitorLiveRegions(self):
        # start at the document frame
        obj = self._script.getDocumentFrame()
        # get the URI of the page.  It is used as a partial key.
        uri = self._script.bookmarks.getURIKey()

        # The user is currently monitoring live regions but now wants to 
        # change all live region politeness on page to LIVE_OFF
        if self.monitoring:
            # look through all the objects on the page and set/add to
            # politeness overrides.
            # TODO: use Collection
            matches = pyatspi.findAllDescendants(obj, self._livePred)
            for match in matches:
                attrs = self._getAttrDictionary(match)
                self._politenessOverrides[(uri, attrs['id'])] = LIVE_OFF

            # Translators: This lets the user know that all live regions
            # have been turned off.
            speech.speak(_("All live regions set to off"))

            # Toggle our flag
            self.monitoring = False

        # The user wants to restore politeness levels
        else:
            # Get the politeness bookmarks
            oldpoliteness = \
                self._script.bookmarks.readBookmarksFromDisk( \
                filename='politeness') or {}

            # look through all the objects on the page.
            # TODO: use Collection
            matches = pyatspi.findAllDescendants(obj, self._livePred)
            for match in matches:
                attrs = self._getAttrDictionary(match)
                # Restore the bookmarked politeness or the markup politeness
                try:
                    self._politenessOverrides[(uri, attrs['id'])] = \
                                oldpoliteness[(uri, attrs['id'])]
                except KeyError:
                    self._politenessOverrides[(uri, attrs['id'])] = \
                            self._liveStringToType(obj, attributes=attrs)

            # Translators: This lets the user know that all live regions
            # have been restored to their original politeness level.
            speech.speak(_("live regions politeness levels restored"))

            # Toggle our flag
            self.monitoring = True  

    def outputLiveRegionDescription(self, obj):
        attrs = self._getAttrDictionary(obj)
        uri = self._script.bookmarks.getURIKey()

        utterances = []

        # get the description if there is one.
        for relation in obj.getRelationSet():
            relationtype = relation.getRelationType()
            if relationtype == pyatspi.RELATION_DESCRIBED_BY:
                targetobj = relation.getTarget(0)
                try:
                    utterances.append(targetobj.queryText().getText(0, -1))
                except NotImplemented:
                    pass

        # get the politeness level as a string
        try:
            livepriority = self._politenessOverrides[(uri, attrs['id'])]
            liveprioritystr = self._liveTypeToString(livepriority)
        except KeyError:
            if attrs.has_key('live'):
                liveprioritystr = attrs['live']
            else:
                liveprioritystr = 'unknown'

        # Translators: output the politeness level
        #
        utterances.append(_('politeness level %s') %liveprioritystr)
        speech.speakUtterances(utterances)

    def _livePred(self, obj):
        attrs = self._getAttrDictionary(obj)
        return (attrs.has_key('container-live') and attrs.has_key('id'))

    def _getUtterances(self, event):

        attrs = self._getAttrDictionary(event.source)
        # TODO: handle relevant property here

        # Get the message content for the event.  First the relations.
        utterances = []

        if event.type.startswith('object:children-changed:add'):
            # Get a handle to the Text interface for the target.
            try:
                targetitext = event.any_data.queryText()
            except NotImplementedError:
                return [] 

            # Get the text based on the atomic property
            try:
                if attrs['container-atomic'] == 'true':
                    utterances.append(self._script.expandEOCs(event.source))
                else:
                    utterances.append(targetitext.getText(0, -1))
            except (KeyError, TypeError):
                utterances.append(targetitext.getText(0, -1))

        else: #object:text-changed:insert
            # Get a handle to the Text interface for the source.
            # Serious problems if this fails.
            #
            try:
                sourceitext = event.source.queryText()
            except NotImplementedError:
                # TODO: output warning
                return None

            # We found an embed character.  We can expect a children-changed
            # event, which we will act on, so just return.
            content = sourceitext.getText(0, -1)
            if content.find(self._script.EMBEDDED_OBJECT_CHARACTER) == 0:
                return None

            # Get labeling information
            utterances.extend(self._getLabelsAsUtterances(event.source))

            # Get the text based on the atomic property
            try:
                if attrs['container-atomic'] == 'true':
                    utterances.append(content)
                else:
                    utterances.append(content[event.detail1:]) 
            except KeyError:
                utterances.append(content[event.detail1:])
 
        return utterances 

    def _cacheMessage(self, utts):
        self.msg_cache.append(utts)
        if len(self.msg_cache) > CACHE_SIZE:
            self.msg_cache.pop(0)

    def _getLabelsAsUtterances(self, obj):
        utterances = []
        for relation in obj.getRelationSet():
            relationtype = relation.getRelationType()
            if relationtype == pyatspi.RELATION_LABELLED_BY:
                labelobj = relation.getTarget(0)
                try:
                    utterances.append(labelobj.queryText().getText(0, -1))
                except NotImplemented:
                    pass
        return utterances

    def _getLiveType(self, obj):
        attrs = self._getAttrDictionary(obj)
        uri = self._script.bookmarks.getURIKey()

        # look to see if there is a user politeness override
        try:
            return self._politenessOverrides[(uri, attrs['id'])]
        except (KeyError, TypeError):
            # exception could be thrown due to no override, no 'id' or 
            # attrs being None (unlikely).  In any case, just pass to logic 
            # below.
            return self._liveStringToType(obj, attributes=attrs)

    def _liveStringToType(self, obj, attributes=None):
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
        return dict([attr.split(':', 1) for attr in obj.getAttributes()])
