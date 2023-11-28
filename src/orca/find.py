# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2022 Igalia, S.L.
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

"""Provides support for a flat review find."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc." \
                "Copyright (c) 2022 Igalia, S.L."
__license__   = "LGPL"


import copy
import re

from . import debug
from . import messages
from . import orca_state
from . import script_manager

from .flat_review import Context


class _SearchQueryMatch:
    """Represents a SearchQuery match."""

    def __init__(self, context, pattern):
        self._line = context.lineIndex
        self._zone = context.zoneIndex
        self._word = context.wordIndex
        self._char = context.charIndex
        self._pattern = pattern
        self._lineString = context.getCurrent(Context.LINE)[0]

    def __str__(self):
        return "SEARCH QUERY MATCH: '%s' (line %i, zone %i, word %i, char %i) for '%s'" % \
                (self._lineString, self._line, self._zone, self._word, self._char, self._pattern)

    def __eq__(self, other):
        if not other:
            return False

        return self._lineString == other._lineString and \
               self._line == other._line and \
               self._zone == other._zone and \
               self._word == other._word and \
               self._char == other._char

class SearchQuery:
    """Represents a search that the user wants to perform."""

    def __init__(self):
        """Creates a new SearchQuery. A searchQuery has the following
           properties:

           searchString     - the string to find
           searchBackwards  - if true, search upward for matches
           caseSensitive    - if true, case counts
           matchEntireWord  - if true, only match on the entire string
           startAtTop       - if true, begin the search from the top of
                              the window, rather than at the current
                              location
           windowWrap       - if true, when the top/bottom edge of the
                              window is reached wrap to the bottom/top
                              and continue searching
        """

        self.searchString = ""
        self.searchBackwards = False
        self.caseSensitive = False
        self.matchEntireWord = False
        self.windowWrap = False
        self.startAtTop = False
        self.debugLevel = debug.LEVEL_INFO
        self._contextLocation = [0, 0, 0, 0]
        self._match = None
        self._wrapped = False

    def __str__(self):
        string = f"FIND QUERY: '{self.searchString}'."
        options = []
        if self.searchBackwards:
            options.append("search backwards")
        if self.caseSensitive:
            options.append("case sensitive")
        if self.matchEntireWord:
            options.append("match entire word")
        if self.windowWrap:
            options.append("wrap")
        if self.startAtTop:
            options.append("start at top")
        if options:
            string += f" Options: {', '.join(options)}"
        if self._match:
            string += f" Last match: {self._match}"
        return string

    def previousMatch(self):
        if not orca_state.searchQuery:
            return None
        return orca_state.searchQuery._match

    def _saveContextLocation(self, context):
        self._contextLocation = [context.lineIndex,
                                 context.zoneIndex,
                                 context.wordIndex,
                                 context.charIndex]

    def _restoreContextLocation(self, context):
        context.setCurrent(*self._contextLocation)
        self._contextLocation = [0, 0, 0, 0]

    def _currentContextMatches(self, context, pattern, contextType):
        if contextType == Context.LINE:
            typeString = "LINE"
        elif contextType == Context.ZONE:
            typeString = "ZONE"
        elif contextType == Context.WORD:
            typeString = "WORD"
        else:
            return False

        string = context.getCurrent(contextType)[0]
        match = re.search(pattern, string)
        msg = "FIND: %s='%s'. Match: %s" % (typeString, string.replace("\n", "\\n"), match)
        debug.println(self.debugLevel, msg, True)
        return bool(match)

    def _move(self, context, contextType):
        if contextType == Context.WORD:
            if self.searchBackwards:
                return context.goPrevious(Context.WORD, Context.WRAP_LINE)
            return context.goNext(Context.WORD, Context.WRAP_LINE)

        if contextType == Context.ZONE:
            if self.searchBackwards:
                moved = context.goPrevious(Context.ZONE, Context.WRAP_LINE)
                context.goEnd(Context.ZONE)
                return moved
            return context.goNext(Context.ZONE, Context.WRAP_LINE)

        if contextType == Context.LINE:
            if self.searchBackwards:
                moved = context.goPrevious(Context.LINE, Context.WRAP_LINE)
                context.goEnd(Context.LINE)
            else:
                moved = context.goNext(Context.LINE, Context.WRAP_LINE)
            if moved:
                return True
            if not self.windowWrap or self._wrapped:
                return False
            self._wrapped = True
            script = script_manager.getManager().getActiveScript()
            if self.searchBackwards:
                script.presentMessage(messages.WRAPPING_TO_BOTTOM)
                moved = context.goPrevious(Context.LINE, Context.WRAP_ALL)
            else:
                script.presentMessage(messages.WRAPPING_TO_TOP)
                moved = context.goNext(Context.LINE, Context.WRAP_ALL)
            return moved

        return False

    def _findMatchIn(self, context, pattern, contextType):
        found = self._currentContextMatches(context, pattern, contextType)
        while not found:
            if not self._move(context, contextType):
                break
            found = self._currentContextMatches(context, pattern, contextType)

        return found

    def _findMatch(self, context, pattern):
        if not self._findMatchIn(context, pattern, Context.LINE):
            return False

        if not self._findMatchIn(context, pattern, Context.ZONE):
            return False

        if not self._findMatchIn(context, pattern, Context.WORD):
            return False

        if not self.previousMatch():
            return True

        candidateMatch = _SearchQueryMatch(context, pattern)
        if candidateMatch != self.previousMatch():
            return True

        if self._move(context, Context.WORD) \
            and self._findMatchIn(context, pattern, Context.WORD):
            return True

        if self._move(context, Context.ZONE) \
            and self._findMatchIn(context, pattern, Context.ZONE):
            return True

        if self._move(context, Context.LINE):
            return self._findMatch(context, pattern)

        return False

    def findQuery(self, context):
        """Performs a search on the string specified in searchQuery.

           Arguments:
           - context: The context from active script

           Returns:
           - The context of the match, if found
        """

        debug.println(self.debugLevel, str(self), True)
        flags = re.U
        if not self.caseSensitive:
            flags = flags | re.IGNORECASE
        if self.matchEntireWord:
            regexp = "\\b" + self.searchString + "\\b"
        else:
            regexp = self.searchString
        pattern = re.compile(regexp, flags)

        self._saveContextLocation(context)
        if self.startAtTop:
            context.goBegin(Context.WINDOW)

        location = None
        if self._findMatch(context, pattern):
            self._saveContextLocation(context)
            self._match = _SearchQueryMatch(context, pattern)
            self._wrapped = False
            location = copy.copy(context)
        else:
            self._restoreContextLocation(context)
        orca_state.searchQuery = copy.copy(self)
        return location

def getLastQuery():
    """Grabs the last search query performed from orca_state.

       Returns:
       - A copy of the last search query, if it exists
    """

    lastQuery = copy.copy(orca_state.searchQuery)
    return lastQuery
