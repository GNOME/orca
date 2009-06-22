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

"""Custom script for Gecko toolkit.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import urlparse

import orca.speech as speech
import orca.bookmarks as bookmarks

from orca.orca_i18n import _

####################################################################
#                                                                  #
# Custom bookmarks class                                           #
#                                                                  #
####################################################################
class GeckoBookmarks(bookmarks.Bookmarks):
    def __init__(self, script):
        bookmarks.Bookmarks.__init__(self, script)
        self._currentbookmarkindex = {}
        
        
    def addBookmark(self, inputEvent):
        """ Add an in-page accessible object bookmark for this key and
        webpage URI. """ 
        # form bookmark dictionary key
        index = (inputEvent.hw_code, self.getURIKey())
        # convert the current object to a path and bookmark it
        obj, characterOffset = self._script.getCaretContext()
        path = self._objToPath()
        self._bookmarks[index] = path, characterOffset
        # Translators: this announces that a bookmark has been entered
        #
        utterances = [(_('entered bookmark'))]
        utterances.extend(self._script.speechGenerator.generateSpeech(obj))
        speech.speak(utterances)
        
    def goToBookmark(self, inputEvent, index=None):
        """ Go to the bookmark indexed at this key and this page's URI """
        index = index or (inputEvent.hw_code, self.getURIKey())
        
        try:
            path, characterOffset = self._bookmarks[index]
        except KeyError:
            self._script.systemBeep()
            return
        # convert our path to an object
        obj = self.pathToObj(path)
       
        if obj:
            # restore the location
            self._script.setCaretPosition(obj, characterOffset)
            self._script.updateBraille(obj)
            self._script.speakContents( \
                self._script.getObjectContentsAtOffset(obj, characterOffset))
            # update the currentbookmark
            self._currentbookmarkindex[index[1]] = index[0]
        else:
            self._script.systemBeep()
        
    def bookmarkCurrentWhereAmI(self, inputEvent):
        """ Report "Where am I" information for this bookmark relative to the 
        current pointer location."""
        index = (inputEvent.hw_code, self.getURIKey())
        try:
            path, characterOffset = self._bookmarks[index]
            obj = self.pathToObj(path)
        except KeyError:
            self._script.systemBeep()
            return
            
        [cur_obj, cur_characterOffset] = self._script.getCaretContext()
        
        # Are they the same object?
        if self._script.isSameObject(cur_obj, obj):
            # Translators: this announces that the current object is the same
            # object pointed to by the bookmark.
            #
            speech.speak(_('bookmark is current object'))
            return
        # Are their parents the same?
        elif self._script.isSameObject(cur_obj.parent, obj.parent):
            # Translators: this announces that the current object's parent and 
            # the parent of the object pointed to by the bookmark are the same.
            #
            speech.speak(_('bookmark and current object have same parent'))
            return
        
        # Do they share a common ancestor?
        # bookmark's ancestors
        bookmark_ancestors = []
        p = obj.parent
        while p:
            bookmark_ancestors.append(p)
            p = p.parent
        # look at current object's ancestors to compare to bookmark's ancestors
        p = cur_obj.parent
        while p:
            if bookmark_ancestors.count(p) > 0:
                # Translators: this announces that the bookmark and the current
                # object share a common ancestor
                #
                speech.speak(_('shared ancestor %s') %p.getRole())
                return
            p = p.parent
        
        # Translators: This announces that a comparison between the bookmark
        # and the current object can not be determined.
        #
        speech.speak(_('comparison unknown'))
        
    def saveBookmarks(self, inputEvent):
        """ Save the bookmarks for this script. """
        saved = {}
         
        # save obj as a path instead of an accessible
        for index, bookmark in self._bookmarks.iteritems():
            saved[index] = bookmark[0], bookmark[1]
            
        try:
            self.saveBookmarksToDisk(saved)
            # Translators: this announces that a bookmark has been saved to 
            # disk
            #
            speech.speak(_('bookmarks saved'))
        except IOError:
            # Translators: this announces that a bookmark could not be saved to 
            # disk
            #
            speech.speak(_('bookmarks could not be saved'))

        # Notify the observers
        for o in self._saveObservers:
            o()
            
    def goToNextBookmark(self, inputEvent):
        """ Go to the next bookmark location.  If no bookmark has yet to be
        selected, the first bookmark will be used.  """
        # The convenience of using a dictionary to add/goto a bookmark is 
        # offset by the difficulty in finding the next bookmark.  We will 
        # need to sort our keys to determine the next bookmark on a page by 
        # page basis.
        bm_keys = self._bookmarks.keys()
        current_uri = self.getURIKey()
        
        # mine out the hardware keys for this page and sort them
        thispage_hwkeys = []
        for bm_key in bm_keys:
            if bm_key[1] == current_uri:
                thispage_hwkeys.append(bm_key[0])
        thispage_hwkeys.sort()
        
        # no bookmarks for this page
        if len(thispage_hwkeys) == 0:
            self._script.systemBeep()
            return
        # only 1 bookmark or we are just starting out
        elif len(thispage_hwkeys) == 1 or \
                         current_uri not in self._currentbookmarkindex:
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            return
        
        # find current bookmark hw_code in our sorted list.  
        # Go to next one if possible
        try:
            index = thispage_hwkeys.index( \
                                 self._currentbookmarkindex[current_uri])
            self.goToBookmark(None, index=( \
                                 thispage_hwkeys[index+1], current_uri))
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            
    def goToPrevBookmark(self, inputEvent):
        """ Go to the previous bookmark location.  If no bookmark has yet to be
        selected, the first bookmark will be used.  """
        bm_keys = self._bookmarks.keys()
        current_uri = self.getURIKey()
        
        # mine out the hardware keys for this page and sort them
        thispage_hwkeys = []
        for bm_key in bm_keys:
            if bm_key[1] == current_uri:
                thispage_hwkeys.append(bm_key[0])
        thispage_hwkeys.sort()
        
        # no bookmarks for this page
        if len(thispage_hwkeys) == 0:
            self._script.systemBeep()
            return
        # only 1 bookmark or we are just starting out
        elif len(thispage_hwkeys) == 1 or \
                         current_uri not in self._currentbookmarkindex:
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            return
        
        # find current bookmark hw_code in our sorted list.  
        # Go to next one if possible
        try:
            index = thispage_hwkeys.index( \
                            self._currentbookmarkindex[current_uri])
            self.goToBookmark(None, 
                              index=(thispage_hwkeys[index-1], current_uri))
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))    
            
    def _objToPickle(self, obj=None):
        """Given an object, return it's saving (pickleable) format.  In this 
        case, the obj path is determined relative to the document frame and is 
        returned as a list.  If obj is not provided, the current caret context
        is used.  """
        return self._objToPath(start_obj=obj)
                               
    def _objToPath(self, start_obj=None):
        """Given an object, return it's path from the root accessible.  If obj 
        is not provided, the current caret context is used. """
        if not start_obj:
            [start_obj, characterOffset] = self._script.getCaretContext()    
            
        if start_obj is None \
                     or start_obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            return []
        else:
            path = []
            path.append(start_obj.getIndexInParent())
            p = start_obj.parent
            while p:
                if p.getRole()  == pyatspi.ROLE_DOCUMENT_FRAME:
                    path.reverse()
                    return path
                path.append(p.getIndexInParent())
                p = p.parent
            
            return []
            
    def _pickleToObj(self, obj):
        """Return the s with the given path (relative to the
        document frame). """
        
        # could test for different obj types.  We'll just assume it is
        # list that represents a path for now.
        return self.pathToObj(obj)
            
    def pathToObj(self, path):
        """Return the object with the given path (relative to the
        document frame). """
        returnobj = self._script.getDocumentFrame()
        for childnumber in path:
            try:
                returnobj = returnobj[childnumber]
            except IndexError:
                return None
            
        return returnobj
            
    def getURIKey(self):
        """Returns the URI key for a given page as a URI stripped of 
        parameters?query#fragment as seen in urlparse."""
        uri = self._script.getDocumentFrameURI()
        if uri:
            parsed_uri = urlparse.urlparse(uri)
            return ''.join(parsed_uri[0:3])
        else:
            return None
