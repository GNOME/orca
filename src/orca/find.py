# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"


import copy
import re

from . import debug
from . import flat_review
from . import messages
from . import orca_state

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

        self.debugLevel = debug.LEVEL_FINEST

    def debugContext(self, context, string):
        """Prints out the context and the string to find to debug.out"""
        debug.println(self.debugLevel, \
            "------------------------------------------------------------")
        debug.println(self.debugLevel, \
                      "findQuery: %s line=%d zone=%d word=%d char=%d" \
                      % (string, context.lineIndex, context.zoneIndex, \
                                 context.wordIndex, context.charIndex))

        debug.println(self.debugLevel, \
                      "Number of lines: %d" % len(context.lines))
        debug.println(self.debugLevel, \
                      "Number of zones in current line: %d" % \
                      len(context.lines[context.lineIndex].zones))
        debug.println(self.debugLevel, \
                      "Number of words in current zone: %d" % \
           len(context.lines[context.lineIndex].zones[context.zoneIndex].words))

        debug.println(self.debugLevel, \
            "==========================================================\n\n")

    def dumpContext(self, context):
        """Debug utility which prints out the context."""
        print("DUMP")
        for i in range(0, len(context.lines)):
            print("  Line %d" % i)
            for j in range(0, len(context.lines[i].zones)):
                print("    Zone: %d" % j)
                for k in range(0, len(context.lines[i].zones[j].words)):
                    print("      Word %d = `%s` len(word): %d" % \
                        (k, context.lines[i].zones[j].words[k].string, \
                         len(context.lines[i].zones[j].words[k].string)))

    def findQuery(self, context, justEnteredFlatReview):
        """Performs a search on the string specified in searchQuery.

           Arguments:
           - context: The context from active script
           - justEnteredFlatReview: If true, we began the search in focus
             tracking mode.

           Returns:
           - The context of the match, if found
        """

        # Get the starting context so that we can restore it at the end.
        #
        originalLineIndex = context.lineIndex
        originalZoneIndex = context.zoneIndex
        originalWordIndex = context.wordIndex
        originalCharIndex = context.charIndex

        debug.println(self.debugLevel, \
            "findQuery: original context line=%d zone=%d word=%d char=%d" \
                % (originalLineIndex, originalZoneIndex, \
                   originalWordIndex, originalCharIndex))
        # self.dumpContext(context)

        flags = re.LOCALE
        if not self.caseSensitive:
            flags = flags | re.IGNORECASE
        if self.matchEntireWord:
            regexp = "\\b" + self.searchString + "\\b"
        else:
            regexp = self.searchString
        pattern = re.compile(regexp, flags)

        debug.println(self.debugLevel, \
            "findQuery: startAtTop: %d  regexp: `%s`" \
                % (self.startAtTop, regexp))

        if self.startAtTop:
            context.goBegin(flat_review.Context.WINDOW)
            self.debugContext(context, "go begin")

        location = None
        found = False
        wrappedYet = False

        doneWithLine = False
        while not found:
            # Check the current line for the string.
            #
            [currentLine, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.LINE)
            debug.println(self.debugLevel, \
                "findQuery: current line=`%s` x=%d y=%d width=%d height=%d" \
                    % (currentLine, x, y, width, height))

            if re.search(pattern, currentLine) and not doneWithLine:
                # It's on this line. Check the current zone for the string.
                #
                while not found:
                    [currentZone, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.ZONE)
                    debug.println(self.debugLevel, \
                        "findQuery: current zone=`%s` x=%d y=%d " % \
                        (currentZone, x, y))
                    debug.println(self.debugLevel, \
                        "width=%d height=%d" % (width, height))

                    if re.search(pattern, currentZone):
                        # It's in this zone at least once.
                        #
                        theZone = context.lines[context.lineIndex] \
                                         .zones[context.zoneIndex]
                        startedInThisZone = \
                              (originalLineIndex == context.lineIndex) and \
                              (originalZoneIndex == context.zoneIndex)
                        try:
                            theZone.accessible.queryText()
                        except:
                            pass
                        else:
                            # Make a list of the character offsets for the
                            # matches in this zone.
                            #
                            allMatches = re.finditer(pattern, currentZone)
                            offsets = []
                            for m in allMatches:
                                offsets.append(m.start(0))
                            if self.searchBackwards:
                                offsets.reverse()

                            i = 0
                            while not found and (i < len(offsets)):
                                [nextInstance, offset] = \
                                   theZone.getWordAtOffset(offsets[i])
                                if nextInstance:
                                    offsetDiff = \
                                        nextInstance.index - context.wordIndex
                                    if self.searchBackwards \
                                       and (offsetDiff < 0) \
                                       or (not self.searchBackwards \
                                           and offsetDiff > 0):
                                        context.wordIndex = nextInstance.index
                                        context.charIndex = 0
                                        found = True
                                    elif not offsetDiff and \
                                        (not startedInThisZone or \
                                         justEnteredFlatReview):
                                        # We landed on a match by happenstance.
                                        # This can occur when the nextInstance
                                        # is the first thing we come across.
                                        #
                                        found = True
                                    else:
                                        i += 1
                                else:
                                    break
                    if not found:
                        # Locate the next zone to try again.
                        #
                        if self.searchBackwards:
                            moved = context.goPrevious( \
                                        flat_review.Context.ZONE, \
                                        flat_review.Context.WRAP_LINE)
                            self.debugContext(context, "[1] go previous")
                            context.goEnd(flat_review.Context.ZONE)
                            self.debugContext(context, "[1] go end")
                        else:
                            moved = context.goNext( \
                                        flat_review.Context.ZONE, \
                                        flat_review.Context.WRAP_LINE)
                            self.debugContext(context, "[1] go next")
                        if not moved:
                            doneWithLine = True
                            break
            else:
                # Locate the next line to try again.
                #
                if self.searchBackwards:
                    moved = context.goPrevious(flat_review.Context.LINE, \
                                               flat_review.Context.WRAP_LINE)
                    self.debugContext(context, "[2] go previous")
                else:
                    moved = context.goNext(flat_review.Context.LINE, \
                                           flat_review.Context.WRAP_LINE)
                    self.debugContext(context, "[2] go next")
                if moved:
                    if self.searchBackwards:
                        moved = context.goEnd(flat_review.Context.LINE)
                        self.debugContext(context, "[2] go end")
                else:
                    # Then we're at the screen's edge.
                    #
                    if self.windowWrap and not wrappedYet:
                        script = orca_state.activeScript
                        doneWithLine = False
                        wrappedYet = True
                        if self.searchBackwards:
                            script.presentMessage(messages.WRAPPING_TO_BOTTOM)
                            moved = context.goPrevious( \
                                    flat_review.Context.LINE, \
                                    flat_review.Context.WRAP_ALL)
                            self.debugContext(context, "[3] go previous")
                        else:
                            script.presentMessage(messages.WRAPPING_TO_TOP)
                            moved = context.goNext( \
                                    flat_review.Context.LINE, \
                                    flat_review.Context.WRAP_ALL)
                            self.debugContext(context, "[3] go next")
                        if not moved:
                            debug.println(self.debugLevel, \
                                          "findQuery: cannot wrap")
                            break
                    else:
                        break
        if found:
            location = copy.copy(context)

        self.debugContext(context, "before setting original")
        context.setCurrent(originalLineIndex, originalZoneIndex, \
                           originalWordIndex, originalCharIndex)
        self.debugContext(context, "after setting original")

        if location:
            debug.println(self.debugLevel, \
                "findQuery: returning line=%d zone=%d word=%d char=%d" \
                    % (location.lineIndex, location.zoneIndex, \
                       location.wordIndex, location.charIndex))

        return location

def getLastQuery():
    """Grabs the last search query performed from orca_state.

       Returns:
       - A copy of the last search query, if it exists
    """

    lastQuery = copy.copy(orca_state.searchQuery)
    return lastQuery
