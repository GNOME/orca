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

"""Provides the default implementation for bookmarks in Orca."""

import pickle
import os

import speech
import settings
import orca_state

from orca_i18n import _


class Bookmarks:
    """Represents a default bookmark handler."""
    def __init__(self, script):
        self._script = script
        self._bookmarks = {} 
        self._saveObservers = []
        self._loadObservers = []
        self._loadBookmarks() 
        self._currentbookmarkindex = None

    def addSaveObserver(self, observer):
        self._saveObservers.append(observer)

    def addLoadObserver(self, observer):
        self._loadObservers.append(observer)

    def goToBookmark(self, inputEvent, index=None):
        """ Go to the bookmark indexed by inputEvent.hw_code """
        # establish the _bookmarks index
        index = index or inputEvent.hw_code

        try:
            context = self._script.getFlatReviewContext()
            context_info = self._bookmarks[index]
            context.setCurrent(context_info['line'], context_info['zone'], \
                                context_info['word'], context_info['char'])
            self._bookmarks[index] = context_info
        except KeyError:
            self._script.systemBeep()
            return

        self._script.flatReviewContext = context
        self._script.reviewCurrentItem(inputEvent)

        # update the currentbookmark
        self._currentbookmarkindex = index

    def addBookmark(self, inputEvent):
        """ Add an in-page accessible object bookmark for this key. """
        context = self._script.getFlatReviewContext()
        self._bookmarks[inputEvent.hw_code] = self._contextToBookmark(context)
        
        # Translators: this announces that a bookmark has been entered.  
        # Orca allows users to tell it to remember a particular spot in an 
        # application window and provides keystrokes for the user to jump to 
        # those spots.  These spots are known as 'bookmarks'. 
        #
        utterances = [_('bookmark entered')]
        utterances.extend(self._script.speechGenerator.getSpeech( \
                          context.getCurrentAccessible(), False))
        speech.speakUtterances(utterances)

    def bookmarkCurrentWhereAmI(self, inputEvent):
        """ Report "Where am I" information for this bookmark relative to the 
        current pointer location."""
        try:
            context = self._bookmarkToContext( \
                          self._bookmarks[inputEvent.hw_code])
        except KeyError:
            self._script.systemBeep()
            return   

        obj = context.getCurrentAccessible()    
        cur_obj = orca_state.locusOfFocus

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
                speech.speak(_('shared ancestor %s') %p.role)
                return
            p = p.parent

        # Translators: This announces that a comparison between the bookmark
        # and the current object can not be determined.
        #
        speech.speak(_('comparison unknown'))

    def saveBookmarks(self, inputEvent):
        """ Save the bookmarks for this script. """        
        try:
            self.saveBookmarksToDisk(self._bookmarks)
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

        # get the hardware keys that have registered bookmarks
        hwkeys = self._bookmarks.keys()
        hwkeys.sort()

        # no bookmarks have been entered
        if len(hwkeys) == 0:
            self._script.systemBeep()
            return
        # only 1 bookmark or we are just starting out
        elif len(hwkeys) == 1 or self._currentbookmarkindex is None:
            self.goToBookmark(None, index=hwkeys[0])
            return

        # find current bookmark hw_code in our sorted list.  
        # Go to next one if possible
        try:
            index = hwkeys.index(self._currentbookmarkindex)
            self.goToBookmark(None, index=hwkeys[index+1])
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=hwkeys[0])

    def goToPrevBookmark(self, inputEvent):
        # get the hardware keys that have registered bookmarks
        hwkeys = self._bookmarks.keys()
        hwkeys.sort()

        # no bookmarks have been entered
        if len(hwkeys) == 0:
            self._script.systemBeep()
            return
        # only 1 bookmark or we are just starting out
        elif len(hwkeys) == 1 or self._currentbookmarkindex is None:
            self.goToBookmark(None, index=hwkeys[0])
            return

        # find current bookmark hw_code in our sorted list.  
        # Go to previous one if possible
        try:
            index = hwkeys.index(self._currentbookmarkindex)
            self.goToBookmark(None, index=hwkeys[index-1])
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=hwkeys[0])

    def _loadBookmarks(self):
        """ Load this scripts saved bookmarks."""
        self._bookmarks = self.readBookmarksFromDisk() or {}

        # notify the observers
        for o in self._loadObservers:
            o()

    def readBookmarksFromDisk(self, filename=None):
        """ Read saved bookmarks from disk.  Currently an unpickled object
        that represents a bookmark """
        filename = filename or self._script.name.split(' ')[0]
        orcaDir = settings.userPrefsDir
        orcaBookmarksDir = os.path.join(orcaDir, "bookmarks")
        try:
            inputFile = open( os.path.join( orcaBookmarksDir, \
                        '%s.pkl' %filename), "r")
            bookmarks = pickle.load(inputFile)
            inputFile.close()
            return bookmarks
        except (IOError, EOFError, OSError):
            return None

    def saveBookmarksToDisk(self, bookmarksObj, filename=None):
        """ Write bookmarks to disk.  bookmarksObj must be a pickleable 
        object. """
        filename = filename or self._script.name.split(' ')[0]
        orcaDir = settings.userPrefsDir
        orcaBookmarksDir = os.path.join(orcaDir, "bookmarks")
        # create directory if it does not exist.  correct place??
        try:
            os.stat(orcaBookmarksDir)
        except OSError:
            os.mkdir(orcaBookmarksDir)
        output = open( os.path.join( orcaBookmarksDir, \
                    '%s.pkl' %filename), "w", os.O_CREAT)
        pickle.dump(bookmarksObj, output)
        output.close()

    def _contextToBookmark(self, context):
        """Converts a flat_review.Context object into a bookmark."""
        context_info = {}
        context_info['zone'] = context.zoneIndex
        context_info['char'] = context.charIndex
        context_info['word'] = context.wordIndex
        context_info['line'] = context.lineIndex
        return context_info

    def _bookmarkToContext(self, bookmark):
        """Converts a bookmark into a flat_review.Context object."""
        context = self._script.getFlatReviewContext()
        context.setCurrent(bookmark['line'], bookmark['zone'], \
                           bookmark['word'], bookmark['char'])
        return context
