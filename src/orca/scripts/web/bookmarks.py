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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from orca import bookmarks
from orca import messages


class Bookmarks(bookmarks.Bookmarks):

    def __init__(self, script):
        super().__init__(script)
        self._currentbookmarkindex = {}

    def addBookmark(self, script, inputEvent):
        """Add an in-page accessible object bookmark for this key and URI."""

        index = (inputEvent.hw_code, self.getURIKey())
        obj, characterOffset = self._script.utilities.get_caret_context()
        path = self._objToPath()
        self._bookmarks[index] = path, characterOffset
        self._script.present_message(messages.BOOKMARK_ENTERED)

    def goToBookmark(self, script, inputEvent, index=None):
        """Go to the bookmark indexed at this key and this page's URI."""

        index = index or (inputEvent.hw_code, self.getURIKey())
        try:
            path, offset = self._bookmarks[index]
        except KeyError:
            return

        obj = self.pathToObj(path)
        if not obj:
            return

        self._script.utilities.set_caret_position(obj, offset)
        contents = self._script.utilities.get_object_contents_at_offset(obj, offset)
        self._script.speak_contents(contents)
        self._script.display_contents(contents)
        self._currentbookmarkindex[index[1]] = index[0]

    def saveBookmarks(self, script, inputEvent):
        """Save the bookmarks for this script."""

        saved = {}
        for index, bookmark in self._bookmarks.items():
            saved[index] = bookmark[0], bookmark[1]

        try:
            self.saveBookmarksToDisk(saved)
            self._script.present_message(messages.BOOKMARKS_SAVED)
        except IOError:
            self._script.present_message(messages.BOOKMARKS_SAVED_FAILURE)

        for o in self._saveObservers:
            o()

    def goToNextBookmark(self, script, inputEvent):
        """Go to the next bookmark location."""

        # The convenience of using a dictionary to add/goto a bookmark is offset
        # by the difficulty in finding the next bookmark. We will need to sort
        # our keys to determine the next bookmark on a page-by-page basis.
        bm_keys = list(self._bookmarks.keys())
        current_uri = self.getURIKey()

        # mine out the hardware keys for this page and sort them
        thispage_hwkeys = []
        for bm_key in bm_keys:
            if bm_key[1] == current_uri:
                thispage_hwkeys.append(bm_key[0])
        thispage_hwkeys.sort()

        if len(thispage_hwkeys) == 0:
            return

        if len(thispage_hwkeys) == 1 or current_uri not in self._currentbookmarkindex:
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            return

        try:
            index = thispage_hwkeys.index(self._currentbookmarkindex[current_uri])
            self.goToBookmark(None, index=(thispage_hwkeys[index+1], current_uri))
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))

    def goToPrevBookmark(self, script, inputEvent):
        """Go to the previous bookmark location."""

        bm_keys = list(self._bookmarks.keys())
        current_uri = self.getURIKey()

        # mine out the hardware keys for this page and sort them
        thispage_hwkeys = []
        for bm_key in bm_keys:
            if bm_key[1] == current_uri:
                thispage_hwkeys.append(bm_key[0])
        thispage_hwkeys.sort()

        if len(thispage_hwkeys) == 0:
            return

        if len(thispage_hwkeys) == 1 or current_uri not in self._currentbookmarkindex:
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
            return

        try:
            index = thispage_hwkeys.index(self._currentbookmarkindex[current_uri])
            self.goToBookmark(None, index=(thispage_hwkeys[index-1], current_uri))
        except (ValueError, KeyError, IndexError):
            self.goToBookmark(None, index=(thispage_hwkeys[0], current_uri))
