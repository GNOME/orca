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
from . import debug
from . import flat_review_presenter
from . import keybindings
from . import input_event
from . import messages
from . import settings_manager
from .ax_document import AXDocument
from .ax_object import AXObject


class Bookmarks:
    """Represents a default bookmark handler."""
    def __init__(self, script):
        self._script = script
        self._bookmarks = {} 
        self._saveObservers = []
        self._loadObservers = []
        self._loadBookmarks() 
        self._currentbookmarkindex = None
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the bookmark keybindings."""

        if refresh:
            msg = "BOOKMARKS: Refreshing bindings."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("BOOKMARKS: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the bookmark handlers."""

        if refresh:
            msg = "BOOKMARKS: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up the bookmark input event handlers."""

        self._handlers = {}

        self._handlers["goToPrevBookmark"] = \
            input_event.InputEventHandler(
                self.goToPrevBookmark,
                cmdnames.BOOKMARK_GO_TO_PREVIOUS)

        self._handlers["goToNextBookmark"] = \
            input_event.InputEventHandler(
                self.goToNextBookmark,
                cmdnames.BOOKMARK_GO_TO_NEXT)

        self._handlers["goToBookmark"] = \
            input_event.InputEventHandler(
                self.goToBookmark,
                cmdnames.BOOKMARK_GO_TO)

        self._handlers["addBookmark"] = \
            input_event.InputEventHandler(
                self.addBookmark,
                cmdnames.BOOKMARK_ADD)

        self._handlers["saveBookmarks"] = \
            input_event.InputEventHandler(
                self.saveBookmarks,
                cmdnames.BOOKMARK_SAVE)

        msg = "BOOKMARKS: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the bookmark key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("goToNextBookmark")))

        self._bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("goToPrevBookmark")))

        self._bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_ALT_MODIFIER_MASK,
                self._handlers.get("saveBookmarks")))

        for i in range(6):
            self._bindings.add(
                keybindings.KeyBinding(
                    str(i + 1),
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.ORCA_MODIFIER_MASK,
                    self._handlers.get("goToBookmark")))

            self._bindings.add(
                keybindings.KeyBinding(
                    str(i + 1),
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.ORCA_ALT_MODIFIER_MASK,
                    self._handlers.get("addBookmark")))

        msg = "BOOKMARKS: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def addSaveObserver(self, observer):
        self._saveObservers.append(observer)

    def addLoadObserver(self, observer):
        self._loadObservers.append(observer)

    def goToBookmark(self, script, inputEvent, index=None):
        """ Go to the bookmark indexed by inputEvent.hw_code """
        # establish the _bookmarks index
        index = index or inputEvent.hw_code

        context = self._get_context()
        try:
            context_info = self._bookmarks[index]
            context.setCurrent(context_info['line'], context_info['zone'], \
                                context_info['word'], context_info['char'])
            self._bookmarks[index] = context_info
        except KeyError:
            self._script.present_message(messages.BOOKMARK_NOT_FOUND)
            return

        flat_review_presenter.get_presenter().present_item(script, inputEvent)

        # update the currentbookmark
        self._currentbookmarkindex = index

    def addBookmark(self, script, inputEvent):
        """ Add an in-page accessible object bookmark for this key. """
        self._bookmarks[inputEvent.hw_code] = self._contextToBookmark(self._get_context())
        self._script.present_message(messages.BOOKMARK_ENTERED)

    def saveBookmarks(self, script, inputEvent):
        """ Save the bookmarks for this script. """
        try:
            self.saveBookmarksToDisk(self._bookmarks)
            self._script.present_message(messages.BOOKMARKS_SAVED)
        except IOError:
            self._script.present_message(messages.BOOKMARKS_SAVED_FAILURE)

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
            self._script.present_message(messages.BOOKMARKS_NOT_FOUND)
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
            self._script.present_message(messages.BOOKMARKS_NOT_FOUND)
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
        orca_dir = settings_manager.get_manager().get_prefs_dir()
        if not orca_dir:
            return

        orca_bookmarks_dir = os.path.join(orca_dir, "bookmarks")
        try:
            inputFile = open( os.path.join( orca_bookmarks_dir, \
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
        orca_dir = settings_manager.get_manager().get_prefs_dir()
        orca_bookmarks_dir = os.path.join(orca_dir, "bookmarks")
        # create directory if it does not exist.  correct place??
        try:
            os.stat(orca_bookmarks_dir)
        except OSError:
            os.mkdir(orca_bookmarks_dir)
        output = open( os.path.join( orca_bookmarks_dir, \
                    f'{filename}.pkl'), "w", os.O_CREAT)
        pickle.dump(bookmarksObj, output.buffer)
        output.close()

    def _contextToBookmark(self, context):
        """Converts a flat_review.Context object into a bookmark."""
        context_info = {}
        line, zone, word, char = context.getCurrent()
        context_info['zone'] = zone
        context_info['char'] = char
        context_info['word'] = word
        context_info['line'] = line
        return context_info

    def _get_context(self):
        return flat_review_presenter.get_presenter().get_or_create_context(self._script)

    def _bookmarkToContext(self, bookmark):
        """Converts a bookmark into a flat_review.Context object."""
        context = self._get_context()
        location = bookmark['line'], bookmark['zone'], bookmark['word'], bookmark['char']
        context.set_current_location(location)
        return context

    def getURIKey(self):
        """Returns the URI key for a given page as a URI stripped of
        parameters?query#fragment as seen in urlparse."""
        uri = AXDocument.get_uri(self._script.utilities.active_document())
        if uri:
            parsed_uri = urllib.parse.urlparse(uri)
            return ''.join(parsed_uri[0:3])
        else:
            return None

    def pathToObj(self, path):
        """Return the object with the given path (relative to the
        document frame). """
        returnobj = self._script.utilities.active_document()
        for childnumber in path:
            returnobj = AXObject.get_child(returnobj, childnumber)
            if not returnobj:
                break

        return returnobj

    def _objToPath(self, start_obj=None):
        """Given an object, return it's path from the root accessible.  If obj
        is not provided, the current caret context is used. """
        if not start_obj:
            [start_obj, _characterOffset] = self._script.utilities.get_caret_context()

        if not start_obj:
            return []

        if self._script.utilities.is_document(start_obj):
            return []

        path = []
        path.append(AXObject.get_index_in_parent(start_obj))
        p = AXObject.get_parent(start_obj)
        while p:
            if self._script.utilities.is_document(p):
                path.reverse()
                return path
            path.append(AXObject.get_index_in_parent(p))
            p = AXObject.get_parent(p)

        return []
