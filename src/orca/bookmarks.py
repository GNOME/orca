# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Provides the default implementation for bookmarks in Orca."""

import pickle
import os
import urllib.parse

from . import cmdnames
from . import keybindings
from . import input_event
from . import messages
from . import settings_manager
from .ax_object import AXObject

_settingsManager = settings_manager.getManager()

class Bookmarks:
    """Represents a default bookmark handler."""
    def __init__(self, script):
        self._script = script
        self._bookmarks = {} 
        self._saveObservers = []
        self._loadObservers = []
        self._loadBookmarks() 
        self._currentbookmarkindex = None
        self._handlers = self._setup_handlers()
        self._bindings = self._setup_bindings()

    def get_bindings(self):
        """Returns the bookmark keybindings."""

        return self._bindings

    def get_handlers(self):
        """Returns the bookmark handlers."""

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the bookmark input event handlers."""

        handlers = {}

        handlers["goToPrevBookmark"] = \
            input_event.InputEventHandler(
                self.goToPrevBookmark,
                cmdnames.BOOKMARK_GO_TO_PREVIOUS)

        handlers["goToNextBookmark"] = \
            input_event.InputEventHandler(
                self.goToNextBookmark,
                cmdnames.BOOKMARK_GO_TO_NEXT)

        handlers["goToBookmark"] = \
            input_event.InputEventHandler(
                self.goToBookmark,
                cmdnames.BOOKMARK_GO_TO)

        handlers["addBookmark"] = \
            input_event.InputEventHandler(
                self.addBookmark,
                cmdnames.BOOKMARK_ADD)

        handlers["saveBookmarks"] = \
            input_event.InputEventHandler(
                self.saveBookmarks,
                cmdnames.BOOKMARK_SAVE)

        return handlers

    def _setup_bindings(self):
        """Sets up and returns the date-and-time-presenter key bindings."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("goToNextBookmark")))

        bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("goToPrevBookmark")))

        bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.defaultModifierMask,
                keybindings.ORCA_ALT_MODIFIER_MASK,
                self._handlers.get("saveBookmarks")))

        for i in range(6):
            bindings.add(
                keybindings.KeyBinding(
                    str(i + 1),
                    keybindings.defaultModifierMask,
                    keybindings.ORCA_MODIFIER_MASK,
                    self._handlers.get("goToBookmark")))

            bindings.add(
                keybindings.KeyBinding(
                    str(i + 1),
                    keybindings.defaultModifierMask,
                    keybindings.ORCA_ALT_MODIFIER_MASK,
                    self._handlers.get("addBookmark")))

        return bindings

    def addSaveObserver(self, observer):
        self._saveObservers.append(observer)

    def addLoadObserver(self, observer):
        self._loadObservers.append(observer)

    def goToBookmark(self, script, inputEvent, index=None):
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
            self._script.presentMessage(messages.BOOKMARK_NOT_FOUND)
            return

        self._script.flatReviewPresenter.present_item(script, inputEvent)

        # update the currentbookmark
        self._currentbookmarkindex = index

    def addBookmark(self, script, inputEvent):
        """ Add an in-page accessible object bookmark for this key. """
        context = self._script.getFlatReviewContext()
        self._bookmarks[inputEvent.hw_code] = self._contextToBookmark(context)
        self._script.presentMessage(messages.BOOKMARK_ENTERED)

    def saveBookmarks(self, script, inputEvent):
        """ Save the bookmarks for this script. """
        try:
            self.saveBookmarksToDisk(self._bookmarks)
            self._script.presentMessage(messages.BOOKMARKS_SAVED)
        except IOError:
            self._script.presentMessage(messages.BOOKMARKS_SAVED_FAILURE)

        # Notify the observers
        for o in self._saveObservers:
            o()

    def goToNextBookmark(self, script, inputEvent):
        """ Go to the next bookmark location.  If no bookmark has yet to be
        selected, the first bookmark will be used.  """

        # get the hardware keys that have registered bookmarks
        hwkeys = sorted(self._bookmarks.keys())

        # no bookmarks have been entered
        if len(hwkeys) == 0:
            self._script.presentMessage(messages.BOOKMARKS_NOT_FOUND)
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

    def goToPrevBookmark(self, script, inputEvent):
        # get the hardware keys that have registered bookmarks
        hwkeys = sorted(self._bookmarks.keys())

        # no bookmarks have been entered
        if len(hwkeys) == 0:
            self._script.presentMessage(messages.BOOKMARKS_NOT_FOUND)
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
        orcaDir = _settingsManager.getPrefsDir()
        if not orcaDir:
            return

        orcaBookmarksDir = os.path.join(orcaDir, "bookmarks")
        try:
            inputFile = open( os.path.join( orcaBookmarksDir, \
                        f'{filename}.pkl'), "r")
            bookmarks = pickle.load(inputFile.buffer)
            inputFile.close()
            return bookmarks
        except (IOError, EOFError, OSError):
            return None

    def saveBookmarksToDisk(self, bookmarksObj, filename=None):
        """ Write bookmarks to disk.  bookmarksObj must be a pickleable 
        object. """
        filename = filename or self._script.name.split(' ')[0]
        orcaDir = _settingsManager.getPrefsDir()
        orcaBookmarksDir = os.path.join(orcaDir, "bookmarks")
        # create directory if it does not exist.  correct place??
        try:
            os.stat(orcaBookmarksDir)
        except OSError:
            os.mkdir(orcaBookmarksDir)
        output = open( os.path.join( orcaBookmarksDir, \
                    f'{filename}.pkl'), "w", os.O_CREAT)
        pickle.dump(bookmarksObj, output.buffer)
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

    def getURIKey(self):
        """Returns the URI key for a given page as a URI stripped of
        parameters?query#fragment as seen in urlparse."""
        uri = self._script.utilities.documentFrameURI()
        if uri:
            parsed_uri = urllib.parse.urlparse(uri)
            return ''.join(parsed_uri[0:3])
        else:
            return None

    def pathToObj(self, path):
        """Return the object with the given path (relative to the
        document frame). """
        returnobj = self._script.utilities.documentFrame()
        for childnumber in path:
            returnobj = AXObject.get_child(returnobj, childnumber)
            if not returnobj:
                break

        return returnobj

    def _objToPath(self, start_obj=None):
        """Given an object, return it's path from the root accessible.  If obj
        is not provided, the current caret context is used. """
        if not start_obj:
            [start_obj, characterOffset] = self._script.utilities.getCaretContext()

        if not start_obj:
            return []

        if self._script.utilities.isDocument(start_obj):
            return []

        path = []
        path.append(AXObject.get_index_in_parent(start_obj))
        p = AXObject.get_parent(start_obj)
        while p:
            if self._script.utilities.isDocument(p):
                path.reverse()
                return path
            path.append(AXObject.get_index_in_parent(p))
            p = AXObject.get_parent(p)

        return []
