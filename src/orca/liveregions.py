import bisect
import gobject
import orca_state
import pyatspi
import speech
import copy
import time

from orca_i18n import _

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
        self.queue = filter(myfilter, self.queue)

    def purgeByPriority(self, priority):
        """ Purge items from the queue that have a lower than or equal priority
        than the given argument """
        myfilter = lambda item: item[0] > priority
        self.queue = filter(myfilter, self.queue)

    def clumpContents(self):
        """ Combines messages with the same 'label' by appending newer  
        'content' and removing the newer message.  This operation is only
        applied to the next dequeued message for performance reasons and is
        often applied in conjunction with filterContents() """
        if len(self.queue):
            newqueue = []
            newqueue.append(self.queue[0])
            targetlabels = newqueue[0][2]['labels']
            targetcontent = newqueue[0][2]['content']
            for i in range(1, len(self.queue)):
                if self.queue[i][2]['labels'] == targetlabels:
                    newqueue[0][2]['content'].extend \
                                   (self.queue[i][2]['content'])
                else:
                    newqueue.append(self.queue[i]) 

            self.queue = newqueue

    def filterContents(self):
        """ Combines utterances by eliminating repeated utterances and
        utterances that are part of other utterances. """
        if len(self.queue[0][2]['content']) > 1:
            oldcontent = self.queue[0][2]['content']
            newcontent = [oldcontent[0]]

            for i in range(1, len(oldcontent)):
                found = False
                for j in range(len(newcontent)):
                    if oldcontent[i].find(newcontent[j]) != -1 \
                        or newcontent[j].find(oldcontent[i]) != -1: 
                        if len(oldcontent[i]) > len(newcontent[j]):
                            newcontent[j] = oldcontent[i]
                        found = True
                        break

                if not found:
                    newcontent.append(oldcontent[i])

            self.queue[0][2]['content'] = newcontent
 
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

    def reset(self):
        # First we will purge our politeness override dictionary of LIVE_NONE
        # objects that are not registered for this page
        newpoliteness = {}
        currenturi = self._script.bookmarks.getURIKey()
        for key, value in self._politenessOverrides.iteritems():
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
                gobject.timeout_add(100, self.pumpMessages)
            self.msg_queue.enqueue(message, politeness, event.source)

    def pumpMessages(self):
        """ Main gobject callback for live region support.  Handles both 
        purging the message queue and outputting any queued messages that
        were queued up in the handleEvent() method.
        """
        # If there are messages in the queue, we are monitoring, and we are not
        # currently speaking then speak queued message.
        # Note: Do all additional work within if statement to prevent
        # it from being done for each event loop callback
        # Note: isSpeaking() returns False way too early.  A strategy using
        # a message length (in secs) could be used but don't forget many 
        # parameters such as rate,expanded text and others must be considered.
        if len(self.msg_queue) > 0 \
                  and not speech.isSpeaking() \
                  and time.time() - orca_state.lastInputEvent.time > 1:
            # House cleaning on the message queue.  
            # First we will purge the queue of old messages
            self.msg_queue.purgeByKeepAlive()
            # Next, we will filter the messages
            self.msg_queue.clumpContents()
            self.msg_queue.filterContents()
            # Let's get our queued information
            politeness, timestamp, message, obj = self.msg_queue.dequeue()
            # Form output message.  No need to repeat labels and content.
            # TODO: really needs to be tested in real life cases.  Perhaps
            # a verbosity setting?
            if message['labels'] == message['content']:
                utts = message['content']
            else:
                utts = message['labels'] + message['content']
            speech.speakUtterances(utts)

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

    def advancePoliteness(self, obj):
        """Advance the politeness level of the given object"""
        utterances = []
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
            # Translators:  sets the live region politeness level to polite
            #
            utterances.append(_('setting live region to polite'))
        elif cur_priority == LIVE_POLITE:
            self._politenessOverrides[(uri, objectid)] = LIVE_ASSERTIVE
            # Translators:  sets the live region politeness level to assertive
            #
            utterances.append(_('setting live region to assertive'))
        elif cur_priority == LIVE_ASSERTIVE:
            self._politenessOverrides[(uri, objectid)] = LIVE_RUDE
            # Translators:  sets the live region politeness level to rude
            #
            utterances.append(_('setting live region to rude'))
        elif cur_priority == LIVE_RUDE:
            self._politenessOverrides[(uri, objectid)] = LIVE_OFF
            # Translators:  sets the live region politeness level to off
            #
            utterances.append(_('setting live region to off'))

        speech.speakUtterances(utterances)

    def goLastLiveRegion(self):
        """Move the caret to the last announced live region and speak the 
        contents of that object"""
        if self.lastliveobj:
            self._script.setCaretPosition(self.lastliveobj, 0)
            self._script.outlineAccessible(self.lastliveobj)
            self._script.speakContents(self._script.getObjectContentsAtOffset(\
                                       self.lastliveobj,0))

    def reviewLiveAnnouncement(self, msgnum):
        """Speak the given number cached message"""
        if msgnum > len(self.msg_cache):
            # Tranlators: this tells the user that a cached message
            # is not available.
            #
            speech.speak(_('no live message saved'))
        else:
            speech.speakUtterances(self.msg_cache[-msgnum])

    def setLivePolitenessOff(self):
        """User toggle to set all live regions to LIVE_OFF or back to their
        original politeness."""
        # start at the document frame
        docframe = self._script.getDocumentFrame()
        # get the URI of the page.  It is used as a partial key.
        uri = self._script.bookmarks.getURIKey()

        # The user is currently monitoring live regions but now wants to 
        # change all live region politeness on page to LIVE_OFF
        if self.monitoring:
            # Translators: This lets the user know that all live regions
            # have been turned off.
            speech.speak(_("All live regions set to off"))

            self.msg_queue.clear()
            
            # First we'll save off a copy for quick restoration
            self._restoreOverrides = copy.copy(self._politenessOverrides)

            # Set all politeness overrides to LIVE_OFF.
            for override in self._politenessOverrides.keys():
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
            for key, value in self._restoreOverrides.iteritems():
                self._politenessOverrides[key] = value
            # Translators: This lets the user know that all live regions
            # have been restored to their original politeness level.
            speech.speak(_("live regions politeness levels restored"))

            # Toggle our flag
            self.monitoring = True  

    def outputLiveRegionDescription(self, obj):
        """Used in conjuction with whereAmI to output description and 
        politeness of the given live region object"""
        objectid = self._getObjectId(obj)
        uri = self._script.bookmarks.getURIKey()

        utterances = []

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
                        utterances.append(description)
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
        if utterances or liveprioritystr != 'none':
            # Translators: output the politeness level
            #
            utterances.append(_('politeness level %s') %liveprioritystr)
            speech.speakUtterances(utterances)

    def matchLiveRegion(self, obj):
        """Predicate used to find a live region"""
        attrs = self._getAttrDictionary(obj)
        return 'container-live' in attrs

    def _getMessage(self, event):
        """Gets the message associated with a given live event."""
        attrs = self._getAttrDictionary(event.source)
        content = [] 
        labels = []
        
        # A message is divided into two parts: labels and content.  We
        # will first try to get the content.  If there is None, 
        # assume it is an invalid message and return None
        if event.type.startswith('object:children-changed:add'):
            # Get the text based on the atomic property
            try:
                if attrs['container-atomic'] == 'true':
                    # expand the source if atomic is true
                    newcontent = self._script.expandEOCs(event.source)
                else:
                    # expand the target if atomic is false
                    newcontent = self._script.expandEOCs(event.any_data)
            except (KeyError, TypeError):
                # expand the target if there is no ARIA markup
                newcontent = self._script.expandEOCs(event.any_data)

            # add our content to the returned message or return None if no
            # content
            if newcontent:
                content.append(newcontent)
            else:
                return None

        else: #object:text-changed:insert
            # Get a handle to the Text interface for the source.
            # Serious problems if this fails.
            #
            try:
                sourceitext = event.source.queryText()
            except NotImplementedError:
                return None

            # We found an embed character.  We can expect a children-changed
            # event, which we will act on, so just return.
            txt = sourceitext.getText(0, -1)
            if txt.count(self._script.EMBEDDED_OBJECT_CHARACTER) > 0:
                return None

            # Get the text based on the atomic property
            try:
                if attrs['container-atomic'] == 'true':
                    newcontent = txt
                else:
                    newcontent = txt[event.detail1:event.detail1+event.detail2]
            except KeyError:
                newcontent = txt[event.detail1:event.detail1+event.detail2]

            # add our content to the returned message or return None if no
            # content
            if len(newcontent) > 0:
                content.append(newcontent)
            else:
                return None

        # Get the labeling information now that we have good content.
        labels = self._getLabelsAsUtterances(event.source)

        # instantly send out notify messages
        if 'channel' in attrs and attrs['channel'] == 'notify':
            utts = labels + content
            speech.stop()
            # Note: we would like to use a different ACSS for alerts.  This work
            # should be done as part of bug #412656.
            speech.speakUtterances(utts)
            return None
        else:
            return {'content':content, 'labels':labels}

    def flushMessages(self):
        self.msg_queue.clear()

    def _cacheMessage(self, utts):
        """Cache a message in our cache list of length CACHE_SIZE"""
        self.msg_cache.append(utts)
        if len(self.msg_cache) > CACHE_SIZE:
            self.msg_cache.pop(0)

    def _getLabelsAsUtterances(self, obj):
        """Get the labels for a given object"""
        # try the Gecko label getter first
        uttstring = self._script.getDisplayedLabel(obj)
        if uttstring:
            return [uttstring.strip()]
        # often we see a table cell.  I'll implement my own label getter
        elif obj.getRole() == pyatspi.ROLE_TABLE_CELL \
                           and obj.parent.childCount > 1:
            # We will try the table interface first for it's parent
            try:
                itable = obj.parent.queryTable()
                # I'm in a table, now what row are we in?  Look in the first 
                # columm of that row.
                #
                # Note: getRowHeader() fails for most markup.  We will use the
                # relation when the markup is good (when getRowHeader() works) 
                # so we won't see this code in those cases.  
                index = self._script.getCellIndex(obj)
                row = itable.getRowAtIndex(index)
                header = itable.getAccessibleAt(row, 0)
                # expand the header
                return [self._script.expandEOCs(header).strip()]
            except NotImplementedError:
                pass

            # Last ditch effort is to see if our parent is a table row <tr> 
            # element.
            parentattrs = self._getAttrDictionary(obj.parent) 
            if 'tag' in parentattrs and parentattrs['tag'] == 'TR':
                return [self._script.expandEOCs( \
                                  obj.parent.getChildAtIndex(0)).strip()]

        # Sorry, no valid labels found
        return []

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
        docframe = self._script.getDocumentFrame()
        path = []
        while 1:
            if obj.parent is None or obj == docframe:
                path.reverse()
                return tuple(path)
            try:
                path.append(obj.getIndexInParent())
            except Exception:
                raise LookupError
            obj = obj.parent
