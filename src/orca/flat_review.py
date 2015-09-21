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

"""Provides the default implementation for flat review for Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import re

from . import braille
from . import debug
from . import eventsynthesizer
from . import messages
from . import object_properties
from . import orca_state
from . import settings

# [[[WDW - HACK Regular expression to split strings on whitespace
# boundaries, which is what we'll use for word dividers instead of
# living at the whim of whomever decided to implement the AT-SPI
# interfaces for their toolkit or app.]]]
#
whitespace_re = re.compile(r'(\s+)', re.DOTALL | re.IGNORECASE | re.M)

EMBEDDED_OBJECT_CHARACTER = '\ufffc'

class Char:
    """Represents a single char of an Accessibility_Text object."""

    def __init__(self,
                 word,
                 index,
                 string,
                 x, y, width, height):
        """Creates a new char.

        Arguments:
        - word: the Word instance this belongs to
        - index: the index of this char in the word
        - string: the actual char
        - x, y, width, height: the extents of this Char on the screen
        """

        self.word = word
        self.string = string
        self.index = index
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Word:
    """Represents a single word of an Accessibility_Text object, or
    the entire name of an Image or Component if the associated object
    does not implement the Accessibility_Text interface.  As a rule of
    thumb, all words derived from an Accessibility_Text interface will
    start with the word and will end with all chars up to the
    beginning of the next word.  That is, whitespace and punctuation
    will usually be tacked on to the end of words."""

    def __init__(self,
                 zone,
                 index,
                 startOffset,
                 string,
                 x, y, width, height):
        """Creates a new Word.

        Arguments:
        - zone: the Zone instance this belongs to
        - index: the index of this word in the Zone
        - string: the actual string
        - x, y, width, height: the extents of this Char on the screen"""

        self.zone = zone
        self.index = index
        self.startOffset = startOffset
        self.string = string
        self.length = len(string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __getattr__(self, attr):
        """Used for lazily determining the chars of a word.  We do
        this to reduce the total number of round trip calls to the app,
        and to also spread the round trip calls out over the lifetime
        of a flat review context.

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """

        if attr == "chars":
            if isinstance(self.zone, TextZone):
                text = self.zone.accessible.queryText()

                # Pylint is confused and flags this warning:
                #
                # W0201:132:Word.__getattr__: Attribute 'chars' defined 
                # outside __init__
                #
                # So for now, we just disable this error in this method.
                #
                # pylint: disable-msg=W0201

                self.chars = []

                i = 0
                while i < self.length:
                    [char, startOffset, endOffset] = text.getTextAtOffset(
                        self.startOffset + i,
                        pyatspi.TEXT_BOUNDARY_CHAR)
                    # Sometimes we get more than a character's worth. See
                    # Bug #495303. We can try to correct this.
                    #
                    if len(char):
                        char[0]
                    [x, y, width, height] = text.getRangeExtents(
                        startOffset,
                        startOffset + 1,
                        0)
                    self.chars.append(Char(self,
                                           i,
                                           char,
                                           x, y, width, height))
                    i += 1
            else:
                self.chars = None
            return self.chars
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError(attr)
        else:
            return self.__dict__[attr]

class Zone:
    """Represents text that is a portion of a single horizontal line."""

    def __init__(self,
                 accessible,
                 string,
                 x, y,
                 width, height,
                 role=None):
        """Creates a new Zone, which is a horizontal region of text.

        Arguments:
        - accessible: the Accessible associated with this Zone
        - string: the string being displayed for this Zone
        - extents: x, y, width, height in screen coordinates
        - role: Role to override accesible's role.
        """

        self.accessible = accessible
        self.string = string
        self.length = len(string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.role = role or accessible.getRole()

    def __getattr__(self, attr):
        """Used for lazily determining the words in a Zone.

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """

        if attr == "words":

            # Pylint is confused and flags this warning:
            #
            # W0201:203:Zone.__getattr__: Attribute 'words' defined 
            # outside __init__
            #
            # So for now, we just disable this error in this method.
            #
            # pylint: disable-msg=W0201

            self.words = []

            return self.words
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError(attr)
        else:
            return self.__dict__[attr]

    def onSameLine(self, zone):
        """Returns True if this Zone is on the same horiztonal line as
        the given zone."""

        highestBottom = min(self.y + self.height, zone.y + zone.height)
        lowestTop     = max(self.y,               zone.y)

        # If we do overlap, lets see how much.  We'll require a 25% overlap
        # for now...
        #
        if lowestTop < highestBottom:
            overlapAmount = highestBottom - lowestTop
            shortestHeight = min(self.height, zone.height)
            return ((1.0 * overlapAmount) / shortestHeight) > 0.25
        else:
            return False

    def getWordAtOffset(self, charOffset):
        wordAtOffset = None
        offset = 0
        for word in self.words:
            nextOffset = offset + len(word.string)
            wordAtOffset = word
            if nextOffset > charOffset:
                return [wordAtOffset, charOffset - offset]
            else:
                offset = nextOffset

        return [wordAtOffset, offset]

class TextZone(Zone):
    """Represents Accessibility_Text that is a portion of a single
    horizontal line."""

    def __init__(self,
                 accessible,
                 startOffset,
                 string,
                 x, y,
                 width, height):
        """Creates a new Zone, which is a horizontal region of text.

        Arguments:
        - accessible: the Accessible associated with this Zone
        - startOffset: the index of the char in the Accessibility_Text
                       interface where this Zone starts
        - string: the string being displayed for this Zone
        - extents: x, y, width, height in screen coordinates
        """

        Zone.__init__(self, accessible, string, x, y, width, height)
        self.startOffset = startOffset

    def __getattr__(self, attr):
        """Used for lazily determining the words in a Zone.  The words
        will either be all whitespace (interword boundaries) or actual
        words.  To determine if a Word is whitespace, use
        word.string.isspace()

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """

        if attr == "words":
            text = self.accessible.queryText()

            # Pylint is confused and flags this warning:
            #
            # W0201:288:TextZone.__getattr__: Attribute 'words' defined
            # outside __init__
            #
            # So for now, we just disable this error in this method.
            #
            # pylint: disable-msg=W0201

            self.words = []

            wordIndex = 0
            offset = self.startOffset
            for string in whitespace_re.split(self.string):
                if len(string):
                    endOffset = offset + len(string)
                    [x, y, width, height] = text.getRangeExtents(
                        offset,
                        endOffset,
                        0)
                    word = Word(self,
                                wordIndex,
                                offset,
                                string,
                                x, y, width, height)
                    self.words.append(word)
                    wordIndex += 1
                    offset = endOffset

            return self.words

        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError(attr)
        else:
            return self.__dict__[attr]


class StateZone(Zone):
    """Represents a Zone for an accessible that shows a state using
    a graphical indicator, such as a checkbox or radio button."""

    def __init__(self,
                 accessible,
                 x, y,
                 width, height,
                 role=None):
        Zone.__init__(self, accessible, "", x, y, width, height, role)

        # Force the use of __getattr__ so we get the actual state
        # of the accessible each time we look at the 'string' field.
        #
        del self.string

    def __getattr__(self, attr):
        if attr in ["string", "length", "brailleString"]:
            # stateCount is used as a boolean and as an index
            stateset = self.accessible.getState()
            if stateset.contains(pyatspi.STATE_INDETERMINATE):
                stateCount = 2
            elif stateset.contains(pyatspi.STATE_CHECKED):
                stateCount = 1
            else:
                stateCount = 0
            if self.role in [pyatspi.ROLE_CHECK_BOX,
                             pyatspi.ROLE_CHECK_MENU_ITEM,
                             pyatspi.ROLE_TABLE_CELL]:
                if stateCount == 2:
                    speechState = object_properties.STATE_PARTIALLY_CHECKED
                elif stateCount == 1:
                    speechState = object_properties.STATE_CHECKED
                else:
                    speechState = object_properties.STATE_NOT_CHECKED
                brailleState = \
                    object_properties.CHECK_BOX_INDICATORS_BRAILLE[stateCount]
            elif self.role == pyatspi.ROLE_TOGGLE_BUTTON:
                if stateCount:
                    speechState = object_properties.STATE_PRESSED
                else:
                    speechState = object_properties.STATE_NOT_PRESSED
                brailleState = \
                    object_properties.RADIO_BUTTON_INDICATORS_BRAILLE[stateCount]
            else:
                if stateCount:
                    speechState = object_properties.STATE_SELECTED_RADIO_BUTTON
                else:
                    speechState = object_properties.STATE_UNSELECTED_RADIO_BUTTON
                brailleState = \
                    object_properties.RADIO_BUTTON_INDICATORS_BRAILLE[stateCount]

            if attr == "string":
                return speechState
            elif attr == "length":
                return len(speechState)
            elif attr == "brailleString":
                return brailleState
        else:
            return Zone.__getattr__(self, attr)

class ValueZone(Zone):
    """Represents a Zone for an accessible that shows a value using
    a graphical indicator, such as a progress bar or slider."""

    def __init__(self,
                 accessible,
                 x, y,
                 width, height,
                 role=None):
        Zone.__init__(self, accessible, "", x, y, width, height, role)

        # Force the use of __getattr__ so we get the actual state
        # of the accessible each time we look at the 'string' field.
        #
        del self.string

    def __getattr__(self, attr):
        if attr in ["string", "length", "brailleString"]:
            orientation = None
            if self.role in [pyatspi.ROLE_SLIDER,
                             pyatspi.ROLE_SCROLL_BAR]:
                stateset = self.accessible.getState()
                if stateset.contains(pyatspi.STATE_HORIZONTAL):
                    orientation = object_properties.STATE_HORIZONTAL
                elif stateset.contains(pyatspi.STATE_VERTICAL):
                    orientation = object_properties.STATE_VERTICAL
                        
            try:
                value = self.accessible.queryValue()
            except NotImplementedError:
                debug.println(debug.LEVEL_FINE,
                              'ValueZone does not implement Value interface')
            try:
                percentValue = int((value.currentValue /
                                    (value.maximumValue - value.minimumValue))
                                   * 100.0)
            except:
                percentValue = 0

            rolename = self.accessible.getLocalizedRoleName()
            if orientation:
                speechValue = orientation + " " + rolename
            else:
                speechValue = rolename

            speechValue = speechValue + " " + messages.percentage(percentValue)

            rolename = orca_state.activeScript.brailleGenerator.getLocalizedRoleName(
                self.accessible)
            if orientation:
                brailleValue = "%s %s %d%%" % (orientation,
                    rolename,
                    percentValue)
            else:
                brailleValue = "%s %d%%" % (rolename, percentValue)
            if attr == "string":
                return speechValue
            elif attr == "length":
                return len(speechValue)
            elif attr == "brailleString":
                return brailleValue
        else:
            return Zone.__getattr__(self, attr)


class Line:
    """A Line is a single line across a window and is composed of Zones."""

    def __init__(self,
                 index,
                 zones):
        """Creates a new Line, which is a horizontal region of text.

        Arguments:
        - index: the index of this Line in the window
        - zones: the Zones that make up this line
        """
        self.index = index
        self.zones = zones
        self.brailleRegions = None

    def __getattr__(self, attr):
        # We dynamically create the string each time to handle
        # StateZone and ValueZone zones.
        #
        if attr in ["string", "length", "x", "y", "width", "height"]:
            bounds = None
            string = ""
            for zone in self.zones:
                if not bounds:
                    bounds = [zone.x, zone.y,
                              zone.x + zone.width, zone.y + zone.height]
                else:
                    bounds[0] = min(bounds[0], zone.x)
                    bounds[1] = min(bounds[1], zone.y)
                    bounds[2] = max(bounds[2], zone.x + zone.width)
                    bounds[3] = max(bounds[3], zone.y + zone.height)
                if len(zone.string):
                    if len(string):
                        string += " "
                    string += zone.string

            if not bounds:
                bounds = [-1, -1, -1, -1]

            if attr == "string":
                return string
            elif attr == "length":
                return len(string)
            elif attr == "x":
                return bounds[0]
            elif attr == "y":
                return bounds[1]
            elif attr == "width":
                return bounds[2] - bounds[0]
            elif attr == "height":
                return bounds[3] - bounds[1]
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError(attr)
        else:
            return self.__dict__[attr]

    def getBrailleRegions(self):
        # [[[WDW - We'll always compute the braille regions.  This
        # allows us to handle StateZone and ValueZone zones whose
        # states might be changing on us.]]]
        #
        if True or not self.brailleRegions:
            self.brailleRegions = []
            brailleOffset = 0
            for zone in self.zones:
                # The 'isinstance(zone, TextZone)' test is a sanity check
                # to handle problems with Java text. See Bug 435553.
                if isinstance(zone, TextZone) and \
                   ((zone.accessible.getRole() in \
                         (pyatspi.ROLE_TEXT,  
                          pyatspi.ROLE_PASSWORD_TEXT,
                          pyatspi.ROLE_TERMINAL)) or \
                    # [[[TODO: Eitan - HACK: 
                    # This is just to get FF3 cursor key routing support.
                    # We really should not be determining all this stuff here,
                    # it should be in the scripts. 
                    # Same applies to roles above.]]]
                    (zone.accessible.getRole() in \
                         (pyatspi.ROLE_PARAGRAPH,
                          pyatspi.ROLE_HEADING,
                          pyatspi.ROLE_LINK))):
                    region = braille.ReviewText(zone.accessible,
                                                zone.string,
                                                zone.startOffset,
                                                zone)
                else:
                    try:
                        brailleString = zone.brailleString
                    except:
                        brailleString = zone.string
                    region = braille.ReviewComponent(zone.accessible,
                                                     brailleString,
                                                     0, # cursor offset
                                                     zone)
                if len(self.brailleRegions):
                    pad = braille.Region(" ")
                    pad.brailleOffset = brailleOffset
                    self.brailleRegions.append(pad)
                    brailleOffset += 1

                zone.brailleRegion = region
                region.brailleOffset = brailleOffset
                self.brailleRegions.append(region)

                regionString = region.string
                brailleOffset += len(regionString)

            if not settings.disableBrailleEOL:
                if len(self.brailleRegions):
                    pad = braille.Region(" ")
                    pad.brailleOffset = brailleOffset
                    self.brailleRegions.append(pad)
                    brailleOffset += 1
                eol = braille.Region("$l")
                eol.brailleOffset = brailleOffset
                self.brailleRegions.append(eol)

        return self.brailleRegions

class Context:
    """Information regarding where a user happens to be exploring
    right now.
    """

    ZONE   = 0
    CHAR   = 1
    WORD   = 2
    LINE   = 3 # includes all zones on same line
    WINDOW = 4

    WRAP_NONE       = 0
    WRAP_LINE       = 1 << 0
    WRAP_TOP_BOTTOM = 1 << 1
    WRAP_ALL        = (WRAP_LINE | WRAP_TOP_BOTTOM)

    def __init__(self, script):
        """Create a new Context that will be used for handling flat
        review mode.
        """
        self.script    = script

        if (not orca_state.locusOfFocus) \
            or (orca_state.locusOfFocus.getApplication() \
                != self.script.app):
            self.lines = []
        else:
            # We want to stop at the window or frame or equivalent level.
            #
            obj = script.utilities.topLevelObject(orca_state.locusOfFocus)
            if obj:
                self.lines = self.clusterZonesByLine(self.getShowingZones(obj))
            else:
                self.lines = []

        currentLineIndex = 0
        currentZoneIndex = 0
        currentWordIndex = 0
        currentCharIndex = 0

        try:
            role = orca_state.locusOfFocus.getRole()
        except:
            role = None

        if role == pyatspi.ROLE_TABLE_CELL:
            searchZone = self.script.\
                utilities.realActiveDescendant(orca_state.locusOfFocus)
        else:
            searchZone = orca_state.locusOfFocus

        foundZoneWithFocus = False
        while currentLineIndex < len(self.lines):
            line = self.lines[currentLineIndex]
            currentZoneIndex = 0
            while currentZoneIndex < len(line.zones):
                zone = line.zones[currentZoneIndex]
                if self.script.utilities.isSameObject(
                        zone.accessible, searchZone):
                    foundZoneWithFocus = True
                    break
                else:
                    currentZoneIndex += 1
            if foundZoneWithFocus:
                break
            else:
                currentLineIndex += 1

        # Fallback to the first Zone if we didn't find anything.
        #
        if not foundZoneWithFocus:
            currentLineIndex = 0
            currentZoneIndex = 0
        elif isinstance(zone, TextZone):
            # If we're on an accessible text object, try to set the
            # review cursor to the caret position of that object.
            #
            accessible  = zone.accessible
            lineIndex   = currentLineIndex
            zoneIndex   = currentZoneIndex
            try:
                caretOffset = zone.accessible.queryText().caretOffset
            except NotImplementedError:
                caretOffset = -1
            foundZoneWithCaret = False
            checkForEOF = False
            while lineIndex < len(self.lines):
                line = self.lines[lineIndex]
                while zoneIndex < len(line.zones):
                    zone = line.zones[zoneIndex]
                    if zone.accessible == accessible:
                        if (caretOffset >= zone.startOffset):
                            if (caretOffset \
                                    < (zone.startOffset + zone.length)):
                                foundZoneWithCaret = True
                                break
                            elif (caretOffset \
                                    == (zone.startOffset + zone.length)):
                                checkForEOF = True
                                lineToCheck = lineIndex
                                zoneToCheck = zoneIndex
                    zoneIndex += 1
                if foundZoneWithCaret:
                    currentLineIndex = lineIndex
                    currentZoneIndex = zoneIndex
                    currentWordIndex = 0
                    currentCharIndex = 0
                    offset = zone.startOffset
                    while currentWordIndex < len(zone.words):
                        word = zone.words[currentWordIndex]
                        if (word.length + offset) > caretOffset:
                            currentCharIndex = caretOffset - offset
                            break
                        else:
                            currentWordIndex += 1
                            offset += word.length
                    break
                else:
                    zoneIndex = 0
                    lineIndex += 1
            atEOF = not foundZoneWithCaret and checkForEOF
            if atEOF:
                line = self.lines[lineToCheck]
                zone = line.zones[zoneToCheck]
                currentLineIndex = lineToCheck
                currentZoneIndex = zoneToCheck
                if caretOffset and zone.words:
                    currentWordIndex = len(zone.words) - 1
                    currentCharIndex = \
                          zone.words[currentWordIndex].length - 1

        self.lineIndex = currentLineIndex
        self.zoneIndex = currentZoneIndex
        self.wordIndex = currentWordIndex
        self.charIndex = currentCharIndex

        # This is used to tell us where we should strive to move to
        # when going up and down lines to the closest character.
        # The targetChar is the character where we initially started
        # moving from, and does not change when one moves up or down
        # by line.
        #
        self.targetCharInfo = None

    def clip(self,
             ax, ay, awidth, aheight,
             bx, by, bwidth, bheight):
        """Clips region 'a' by region 'b' and returns the new region as
        a list: [x, y, width, height].
        """

        x = max(ax, bx)
        x2 = min(ax + awidth, bx + bwidth)
        width = x2 - x

        y = max(ay, by)
        y2 = min(ay + aheight, by + bheight)
        height = y2 - y

        return [x, y, width, height]

    def splitTextIntoZones(self, accessible, string, startOffset, cliprect):
        """Traverses the string, splitting it up into separate zones if the
        string contains the EMBEDDED_OBJECT_CHARACTER, which is used by apps
        such as Firefox to handle containment of things such as links in
        paragraphs.

        Arguments:
        - accessible: the accessible
        - string: a substring from the accessible's text specialization
        - startOffset: the starting character offset of the string
        - cliprect: the extents that the Zones must fit inside.

        Returns a list of Zones for the visible text or None if nothing is
        visible.
        """

        # We convert the string to unicode and walk through it.  While doing
        # this, we keep two sets of offsets:
        #
        # substring{Start,End}Offset: where in the accessible text 
        # implementation we are
        #
        # unicodeStartOffset: where we are in the unicodeString
        #
        anyVisible = False
        zones = []
        text = accessible.queryText()
        substringStartOffset = startOffset
        substringEndOffset   = startOffset
        unicodeStartOffset   = 0
        unicodeString = string
        #print "LOOKING AT '%s'" % unicodeString
        for i in range(0, len(unicodeString) + 1):
            if (i != len(unicodeString)) \
               and (unicodeString[i] != EMBEDDED_OBJECT_CHARACTER):
                substringEndOffset += 1
            elif (substringEndOffset == substringStartOffset):
                substringStartOffset += 1
                substringEndOffset   = substringStartOffset
                unicodeStartOffset   = i + 1
            else:
                [x, y, width, height] = text.getRangeExtents(
                        substringStartOffset, substringEndOffset, 0)
                if self.script.utilities.containsRegion(
                        x, y, width, height,
                        cliprect.x, cliprect.y,
                        cliprect.width, cliprect.height):

                    anyVisible = True

                    clipping = self.clip(x, y, width, height,
                                         cliprect.x, cliprect.y,
                                         cliprect.width, cliprect.height)

                    # [[[TODO: WDW - HACK it would be nice to clip the
                    # the text by what is really showing on the screen,
                    # but this seems to hang Orca and the client. Logged
                    # as bugzilla bug 319770.]]]
                    #
                    #ranges = text.getBoundedRanges(\
                    #    clipping[0],
                    #    clipping[1],
                    #    clipping[2],
                    #    clipping[3],
                    #    0,
                    #    pyatspi.TEXT_CLIP_BOTH,
                    #    pyatspi.TEXT_CLIP_BOTH)
                    #
                    #print
                    #print "HERE!"
                    #for range in ranges:
                    #    print range.startOffset
                    #    print range.endOffset
                    #    print range.content

                    substring = unicodeString[unicodeStartOffset:i]
                    #print " SUBSTRING '%s'" % substring
                    zones.append(TextZone(accessible,
                                          substringStartOffset,
                                          substring,
                                          clipping[0],
                                          clipping[1],
                                          clipping[2],
                                          clipping[3]))
                    substringStartOffset = substringEndOffset + 1
                    substringEndOffset   = substringStartOffset
                    unicodeStartOffset   = i + 1

        if anyVisible:
            return zones
        else:
            return None

    def getZonesFromText(self, accessible, cliprect):
        """Gets a list of Zones from an object that implements the
        AccessibleText specialization.

        Arguments:
        - accessible: the accessible
        - cliprect: the extents that the Zones must fit inside.

        Returns a list of Zones.
        """

        debug.println(debug.LEVEL_FINEST, "  looking at text:")

        try:
            text = accessible.queryText()
        except NotImplementedError:
            return []
        else:
            zones = []

        offset = 0
        lastEndOffset = -1
        upperMax = lowerMax = text.characterCount
        upperMid = lowerMid = int(upperMax / 2)
        upperMin = lowerMin = 0
        upperY = lowerY = 0
        oldMid = 0

        # performing binary search to locate first line inside clipped area
        while oldMid != upperMid:
            oldMid = upperMid
            [x, y, width, height] = text.getRangeExtents(upperMid,
                                                         upperMid+1,
                                                         0)
            upperY = y
            if y > cliprect.y:
                upperMax = upperMid
            else:
                upperMin = upperMid
            upperMid = int((upperMax - upperMin) / 2) + upperMin

        # performing binary search to locate last line inside clipped area
        oldMid = 0
        limit = cliprect.y+cliprect.height
        while oldMid != lowerMid:
            oldMid = lowerMid
            [x, y, width, height] = text.getRangeExtents(lowerMid,
                                                         lowerMid+1,
                                                         0)
            lowerY = y
            if y > limit:
                lowerMax = lowerMid
            else:
                lowerMin = lowerMid
            lowerMid = int((lowerMax - lowerMin) / 2) + lowerMin

        # finding out the zones
        offset = upperMin
        length = lowerMax
        while offset < length:

            [string, startOffset, endOffset] = text.getTextAtOffset(
                offset,
                pyatspi.TEXT_BOUNDARY_LINE_START)

            debug.println(debug.LEVEL_FINEST,
                          "    line at %d is (start=%d end=%d): '%s'" \
                          % (offset, startOffset, endOffset, string))

            # [[[WDW - HACK: well...gnome-terminal sometimes wants to
            # give us outrageous values back from getTextAtOffset
            # (see http://bugzilla.gnome.org/show_bug.cgi?id=343133),
            # so we try to handle it.  Evolution does similar things.]]]
            #
            if (startOffset < 0) \
               or (endOffset < 0) \
               or (startOffset > offset) \
               or (endOffset < offset) \
               or (startOffset > endOffset) \
               or (abs(endOffset - startOffset) > 666e3):
                debug.println(debug.LEVEL_WARNING,
                              "flat_review:getZonesFromText detected "\
                              "garbage from getTextAtOffset for accessible "\
                              "name='%s' role'='%s': offset used=%d, "\
                              "start/end offset returned=(%d,%d), string='%s'"\
                              % (accessible.name, accessible.getRoleName(),
                                 offset, startOffset, endOffset, string))
                break

            # [[[WDW - HACK: this is here because getTextAtOffset
            # tends not to be implemented consistently across toolkits.
            # Sometimes it behaves properly (i.e., giving us an endOffset
            # that is the beginning of the next line), sometimes it
            # doesn't (e.g., giving us an endOffset that is the end of
            # the current line).  So...we hack.  The whole 'max' deal
            # is to account for lines that might be a brazillion lines
            # long.]]]
            #
            if endOffset == lastEndOffset:
                offset = max(offset + 1, lastEndOffset + 1)
                lastEndOffset = endOffset
                continue
            else:
                offset = endOffset
                lastEndOffset = endOffset

            textZones = self.splitTextIntoZones(
                accessible, string, startOffset, cliprect)

            # We need to account for the fact that newlines at the end of 
            # text are treated as being on the same line when they in fact
            # are a whole separate blank line.  So, we check for this and
            # make up a new text zone for these cases.  See bug 434654.
            #
            if (endOffset == length) and (string[-1:] == "\n"):
                [x, y, width, height] = text.getRangeExtents(startOffset, 
                                                             endOffset,
                                                             0)
                if not textZones:
                    textZones = []
                textZones.append(TextZone(accessible,
                                          endOffset,
                                          "",
                                          x, y + height, 0, height))

            if textZones:
                zones.extend(textZones)
            elif len(zones):
                # We'll break out of searching all the text - the idea
                # here is that we'll at least try to optimize for when
                # we gone below the visible clipping area.
                #
                # [[[TODO: WDW - would be nice to optimize this better.
                # for example, perhaps we can assume the caret will always
                # be visible, and we can start our text search from there.
                # Logged as bugzilla bug 319771.]]]
                #
                break

        # We might have a zero length text area.  In that case, well,
        # lets hack if this is something whose sole purpose is to
        # act as a text entry area.
        #
        if len(zones) == 0:
            if (accessible.getRole() == pyatspi.ROLE_TEXT) \
               or ((accessible.getRole() == pyatspi.ROLE_ENTRY)) \
               or ((accessible.getRole() == pyatspi.ROLE_PASSWORD_TEXT)):
                extents = accessible.queryComponent().getExtents(0)
                zones.append(TextZone(accessible,
                                      0,
                                      "",
                                      extents.x, extents.y,
                                      extents.width, extents.height))

        return zones

    def _insertStateZone(self, zones, accessible, role=None):
        """If the accessible presents non-textual state, such as a
        checkbox or radio button, insert a StateZone representing
        that state."""

        zone = None
        stateOnLeft = True

        role = role or accessible.getRole()
        if role in [pyatspi.ROLE_CHECK_BOX,
                    pyatspi.ROLE_CHECK_MENU_ITEM,
                    pyatspi.ROLE_RADIO_BUTTON,
                    pyatspi.ROLE_RADIO_MENU_ITEM]:

            # Attempt to infer if the indicator is to the left or
            # right of the text.
            #
            extents = accessible.queryComponent().getExtents(0)
            stateX = extents.x
            stateY = extents.y
            stateWidth = 1
            stateHeight = extents.height

            try:
                text = accessible.queryText()
            except NotImplementedError:
                pass
            else:
                [x, y, width, height] = \
                    text.getRangeExtents( \
                        0, text.characterCount, 0)
                textToLeftEdge = x - extents.x
                textToRightEdge = (extents.x + extents.width) - (x + width)
                stateOnLeft = textToLeftEdge > 20
                if stateOnLeft:
                    stateWidth = textToLeftEdge
                else:
                    stateX = x + width
                    stateWidth = textToRightEdge

            zone = StateZone(accessible,
                             stateX, stateY, stateWidth, stateHeight)

        elif role ==  pyatspi.ROLE_TOGGLE_BUTTON:
            # [[[TODO: WDW - This is a major hack.  We make up an
            # indicator for a toggle button to let the user know
            # whether a toggle button is pressed or not.]]]
            #
            extents = accessible.queryComponent().getExtents(0)
            zone = StateZone(accessible,
                             extents.x, extents.y, 1, extents.height)

        elif role == pyatspi.ROLE_TABLE_CELL:
            # Handle table cells that act like check boxes.
            if self.script.utilities.hasMeaningfulToggleAction(accessible):
                self._insertStateZone(zones, accessible, pyatspi.ROLE_CHECK_BOX)

        if zone:
            if stateOnLeft:
                zones.insert(0, zone)
            else:
                zones.append(zone)

    def getZonesFromAccessible(self, accessible, cliprect):
        """Returns a list of Zones for the given accessible.

        Arguments:
        - accessible: the accessible
        - cliprect: the extents that the Zones must fit inside.
        """
        icomponent = accessible.queryComponent()
        if not icomponent:
            return []

        # Get the component extents in screen coordinates.
        #
        extents = icomponent.getExtents(0)

        if not self.script.utilities.containsRegion(
                extents.x, extents.y,
                extents.width, extents.height,
                cliprect.x, cliprect.y,
                cliprect.width, cliprect.height):
            return []

        debug.println(
            debug.LEVEL_FINEST,
            "flat_review.getZonesFromAccessible (name=%s role=%s)" \
            % (accessible.name, accessible.getRoleName()))

        # Now see if there is any accessible text.  If so, find new zones,
        # where each zone represents a line of this text object.  When
        # creating the zone, only keep track of the text that is actually
        # showing on the screen.
        #

        try:
            accessible.queryText()
        except NotImplementedError:
            zones = []
        else:
            zones = self.getZonesFromText(accessible, cliprect)

        # We really want the accessible text information.  But, if we have
        # an image, and it has a description, we can fall back on it.
        # First, try to get the image interface.
        try:
            iimage = accessible.queryImage()
        except NotImplementedError:
            iimage = None
        
        if (len(zones) == 0) and iimage:
            # Check for accessible.name, if it exists and has len > 0, use it
            # Otherwise, do the same for accessible.description
            # Otherwise, do the same for accessible.image.description
            imageName = ""
            if accessible.name and len(accessible.name):
                imageName = accessible.name
            elif accessible.description and len(accessible.description):
                imageName = accessible.description
            elif iimage.imageDescription and \
                     len(iimage.imageDescription):
                imageName = iimage.imageDescription

            [x, y] = iimage.getImagePosition(0)
            [width, height] = iimage.getImageSize()

            if width != 0 and height != 0 \
               and self.script.utilities.containsRegion(
                    x, y, width, height,
                    cliprect.x, cliprect.y,
                    cliprect.width, cliprect.height):

                clipping = self.clip(x, y, width, height,
                                     cliprect.x, cliprect.y,
                                     cliprect.width, cliprect.height)

                if (clipping[2] != 0) or (clipping[3] != 0):
                    zones.append(Zone(accessible,
                                      imageName,
                                      clipping[0],
                                      clipping[1],
                                      clipping[2],
                                      clipping[3]))

        # If the accessible is a parent, we really only looked at it for
        # its accessible text.  So...we'll skip the hacking here if that's
        # the case.  [[[TODO: WDW - HACK That is, except in the case of
        # combo boxes, which don't implement the accesible text
        # interface.  We also hack with MENU items for similar reasons.]]]
        #
        # Otherwise, even if we didn't get anything of use, we certainly
        # know there's something there.  If that's the case, we'll just
        # use the component extents and the name or description of the
        # accessible.
        #
        clipping = self.clip(extents.x, extents.y,
                             extents.width, extents.height,
                             cliprect.x, cliprect.y,
                             cliprect.width, cliprect.height)
        role = accessible.getRole()

        if (len(zones) == 0) \
            and role in [pyatspi.ROLE_SCROLL_BAR,
                         pyatspi.ROLE_SLIDER,
                         pyatspi.ROLE_PROGRESS_BAR]:
            zones.append(ValueZone(accessible,
                                   clipping[0],
                                   clipping[1],
                                   clipping[2],
                                   clipping[3]))
        elif (role != pyatspi.ROLE_COMBO_BOX) \
            and (role != pyatspi.ROLE_EMBEDDED) \
            and (role != pyatspi.ROLE_LABEL) \
            and (role != pyatspi.ROLE_MENU) \
            and (role != pyatspi.ROLE_PAGE_TAB) \
            and accessible.childCount > 0:
            pass
        elif len(zones) == 0:
            string = ""
            if role == pyatspi.ROLE_COMBO_BOX:
                try:
                    selection = accessible[0].querySelection()
                except:
                    string = self.script.utilities.displayedText(accessible[0])
                else:
                    item = selection.getSelectedChild(0)
                    if item:
                        string = item.name

            if not string and accessible.name and len(accessible.name):
                string = accessible.name
            elif accessible.description and len(accessible.description):
                string = accessible.description

            if not string and role == pyatspi.ROLE_ICON:
                string = self.script.utilities.displayedText(accessible)

            if (string == "") \
                and (role != pyatspi.ROLE_TABLE_CELL):
                string = accessible.getLocalizedRoleName()

            if len(string) and ((clipping[2] != 0) or (clipping[3] != 0)):
                zones.append(Zone(accessible,
                                  string,
                                  clipping[0],
                                  clipping[1],
                                  clipping[2],
                                  clipping[3]))

        self._insertStateZone(zones, accessible)

        return zones

    def getShowingZones(self, root):
        """Returns a list of all interesting, non-intersecting, regions
        that are drawn on the screen.  Each element of the list is the
        Accessible object associated with a given region.  The term
        'zone' here is inherited from OCR algorithms and techniques.

        The Zones are returned in no particular order.

        Arguments:
        - root: the Accessible object to traverse

        Returns: a list of Zones under the specified object
        """

        if not root:
            return []

        zones = []
        try:
            rootexts = root.queryComponent().getExtents(0)
        except:
            return []

        rootrole = root.getRole()

        # If we're at a leaf node, then we've got a good one on our hands.
        #
        try:
            childCount = root.childCount
        except (LookupError, RuntimeError):
            childCount = -1
        if root.childCount <= 0:
            return self.getZonesFromAccessible(root, rootexts)

        # Handle non-leaf Java JTree nodes. If the node is collapsed,
        # treat it as a leaf node. If it's expanded, add it to the
        # Zones list.
        #
        stateset = root.getState()
        if stateset.contains(pyatspi.STATE_EXPANDABLE):
            if stateset.contains(pyatspi.STATE_COLLAPSED):
                return self.getZonesFromAccessible(root, rootexts)
            elif stateset.contains(pyatspi.STATE_EXPANDED):
                treenode = self.getZonesFromAccessible(root, rootexts)
                if treenode:
                    zones.extend(treenode)

        # We'll stop at various objects because, while they do have
        # children, we logically think of them as one region on the
        # screen.  [[[TODO: WDW - HACK stopping at menu bars for now
        # because their menu items tell us they are showing even though
        # they are not showing.  Until I can figure out a reliable way to
        # get past these lies, I'm going to ignore them.]]]
        #
        if (root.parent and (root.parent.getRole() == pyatspi.ROLE_MENU_BAR)) \
           or (rootrole == pyatspi.ROLE_COMBO_BOX) \
           or (rootrole == pyatspi.ROLE_EMBEDDED) \
           or (rootrole == pyatspi.ROLE_TEXT) \
           or (rootrole == pyatspi.ROLE_SCROLL_BAR):
            return self.getZonesFromAccessible(root, rootexts)

        # If this is a status bar, only pursue its children if we cannot
        # get non-empty text information from the status bar.
        # See bug #506874 for more details.
        #
        if rootrole == pyatspi.ROLE_STATUS_BAR:
            zones = self.getZonesFromText(root, rootexts)
            if len(zones):
                return zones

        # Otherwise, dig deeper.
        #
        # We'll include page tabs: while they are parents, their extents do
        # not contain their children. [[[TODO: WDW - need to consider all
        # parents, especially those that implement accessible text.  Logged
        # as bugzilla bug 319773.]]]
        #
        if rootrole == pyatspi.ROLE_PAGE_TAB:
            zones.extend(self.getZonesFromAccessible(root, rootexts))

        try:
            root.queryText()
            if len(zones) == 0:
                zones = self.getZonesFromAccessible(root, rootexts)
        except NotImplementedError:
            pass

        showingDescendants = \
            self.script.utilities.showingDescendants(root)
        if len(showingDescendants):
            for child in showingDescendants:
                zones.extend(self.getShowingZones(child))
        else:
            for i in range(0, root.childCount):
                child = root.getChildAtIndex(i)
                if child == root:
                    debug.println(debug.LEVEL_WARNING,
                                  "flat_review.getShowingZones: " +
                                  "WARNING CHILD == PARENT!!!")
                    continue
                elif not child:
                    debug.println(debug.LEVEL_WARNING,
                                  "flat_review.getShowingZones: " +
                                  "WARNING CHILD IS NONE!!!")
                    continue
                elif child.parent != root:
                    debug.println(debug.LEVEL_WARNING,
                                  "flat_review.getShowingZones: " +
                                  "WARNING CHILD.PARENT != PARENT!!!")
                                  
                if self.script.utilities.pursueForFlatReview(child):
                    zones.extend(self.getShowingZones(child))

        return zones

    def clusterZonesByLine(self, zones):
        """Given a list of interesting accessible objects (the Zones),
        returns a list of lines in order from the top to bottom, where
        each line is a list of accessible objects in order from left
        to right.
        """

        if len(zones) == 0:
            return []

        # Sort the zones and also find the top most zone - we'll bias
        # the clustering to the top of the window.  That is, if an
        # object can be part of multiple clusters, for now it will
        # become a part of the top most cluster.
        #
        numZones = len(zones)
        for i in range(0, numZones):
            for j in range(0, numZones - 1 - i):
                a = zones[j]
                b = zones[j + 1]
                if b.y < a.y:
                    zones[j] = b
                    zones[j + 1] = a

        # Now we cluster the zones.  We create the clusters on the
        # fly, adding a zone to an existing cluster only if it's
        # rectangle horizontally overlaps all other zones in the
        # cluster.
        #
        lineClusters = []
        for clusterCandidate in zones:
            addedToCluster = False
            for lineCluster in lineClusters:
                inCluster = True
                for zone in lineCluster:
                    if not zone.onSameLine(clusterCandidate):
                        inCluster = False
                        break
                if inCluster:
                    # Add to cluster based on the x position.
                    #
                    i = 0
                    while i < len(lineCluster):
                        zone = lineCluster[i]
                        if clusterCandidate.x < zone.x:
                            break
                        else:
                            i += 1
                    lineCluster.insert(i, clusterCandidate)
                    addedToCluster = True
                    break
            if not addedToCluster:
                lineClusters.append([clusterCandidate])

        # Now, adjust all the indeces.
        #
        lines = []
        lineIndex = 0
        for lineCluster in lineClusters:
            lines.append(Line(lineIndex, lineCluster))
            zoneIndex = 0
            for zone in lineCluster:
                zone.line = lines[lineIndex]
                zone.index = zoneIndex
                zoneIndex += 1
            lineIndex += 1

        return lines

    def setCurrent(self, lineIndex, zoneIndex, wordIndex, charIndex):
        """Sets the current character of interest.

        Arguments:
        - lineIndex: index into lines
        - zoneIndex: index into lines[lineIndex].zones
        - wordIndex: index into lines[lineIndex].zones[zoneIndex].words
        - charIndex: index lines[lineIndex].zones[zoneIndex].words[wordIndex].chars
        """

        self.lineIndex = lineIndex
        self.zoneIndex = zoneIndex
        self.wordIndex = wordIndex
        self.charIndex = charIndex
        self.targetCharInfo = self.getCurrent(Context.CHAR)

        #print "Current line=%d zone=%d word=%d char=%d" \
        #      % (lineIndex, zoneIndex, wordIndex, charIndex)

    def routeToCurrent(self):
        """Routes the mouse pointer to the current accessible."""

        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return

        [string, x, y, width, height] = self.getCurrent(Context.CHAR)
        try:
            # We try to move to the left of center.  This is to
            # handle toolkits that will offset the caret position to
            # the right if you click dead on center of a character.
            #
            x = max(x, x + (width / 2) - 1)
            eventsynthesizer.routeToPoint(x, y + height / 2, "abs")
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def clickCurrent(self, button=1):
        """Performs a mouse click on the current accessible."""

        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return

        [string, x, y, width, height] = self.getCurrent(Context.CHAR)
        try:

            # We try to click to the left of center.  This is to
            # handle toolkits that will offset the caret position to
            # the right if you click dead on center of a character.
            #
            x = max(x, x + (width / 2) - 1)
            eventsynthesizer.clickPoint(x,
                                        y + height / 2,
                                        button)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def getCurrentAccessible(self):
        """Returns the accessible associated with the current locus of
        interest.
        """

        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return [None, -1, -1, -1, -1]

        zone = self.lines[self.lineIndex].zones[self.zoneIndex]

        return zone.accessible

    def getCurrent(self, flatReviewType=ZONE):
        """Gets the string, offset, and extent information for the
        current locus of interest.

        Arguments:
        - flatReviewType: one of ZONE, CHAR, WORD, LINE

        Returns: [string, x, y, width, height]
        """

        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return [None, -1, -1, -1, -1]

        zone = self.lines[self.lineIndex].zones[self.zoneIndex]

        if flatReviewType == Context.ZONE:
            return [zone.string,
                    zone.x,
                    zone.y,
                    zone.width,
                    zone.height]
        elif flatReviewType == Context.CHAR:
            if isinstance(zone, TextZone):
                words = zone.words
                if words:
                    chars = zone.words[self.wordIndex].chars
                    if chars:
                        char = chars[self.charIndex]
                        return [char.string,
                                char.x,
                                char.y,
                                char.width,
                                char.height]
                    else:
                        word = words[self.wordIndex]
                        return [word.string,
                                word.x,
                                word.y,
                                word.width,
                                word.height]
            return self.getCurrent(Context.ZONE)
        elif flatReviewType == Context.WORD:
            if isinstance(zone, TextZone):
                words = zone.words
                if words:
                    word = words[self.wordIndex]
                    return [word.string,
                            word.x,
                            word.y,
                            word.width,
                            word.height]
            return self.getCurrent(Context.ZONE)
        elif flatReviewType == Context.LINE:
            line = self.lines[self.lineIndex]
            return [line.string,
                    line.x,
                    line.y,
                    line.width,
                    line.height]
        else:
            raise Exception("Invalid type: %d" % flatReviewType)

    def getCurrentBrailleRegions(self):
        """Gets the braille for the entire current line.

        Returns [regions, regionWithFocus]
        """

        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return [None, None]

        regionWithFocus = None
        line = self.lines[self.lineIndex]
        regions = line.getBrailleRegions()

        # Now find the current region and the current character offset
        # into that region.
        #
        for zone in line.zones:
            if zone.index == self.zoneIndex:
                regionWithFocus = zone.brailleRegion
                regionWithFocus.cursorOffset = 0
                if zone.words:
                    for wordIndex in range(0, self.wordIndex):
                        regionWithFocus.cursorOffset += \
                            len(zone.words[wordIndex].string)
                regionWithFocus.cursorOffset += self.charIndex
                regionWithFocus.repositionCursor()
                break

        return [regions, regionWithFocus]

    def goBegin(self, flatReviewType=WINDOW):
        """Moves this context's locus of interest to the first char
        of the first relevant zone.

        Arguments:
        - flatReviewType: one of ZONE, LINE or WINDOW

        Returns True if the locus of interest actually changed.
        """

        if (flatReviewType == Context.LINE) or (flatReviewType == Context.ZONE):
            lineIndex = self.lineIndex
        elif flatReviewType == Context.WINDOW:
            lineIndex = 0
        else:
            raise Exception("Invalid type: %d" % flatReviewType)

        if flatReviewType == Context.ZONE:
            zoneIndex = self.zoneIndex
        else:
            zoneIndex = 0

        wordIndex = 0
        charIndex = 0

        moved = (self.lineIndex != lineIndex) \
                or (self.zoneIndex != zoneIndex) \
                or (self.wordIndex != wordIndex) \
                or (self.charIndex != charIndex) \

        if moved:
            self.lineIndex = lineIndex
            self.zoneIndex = zoneIndex
            self.wordIndex = wordIndex
            self.charIndex = charIndex
            self.targetCharInfo = self.getCurrent(Context.CHAR)

        return moved

    def goEnd(self, flatReviewType=WINDOW):
        """Moves this context's locus of interest to the last char
        of the last relevant zone.

        Arguments:
        - flatReviewType: one of ZONE, LINE, or WINDOW

        Returns True if the locus of interest actually changed.
        """

        if (flatReviewType == Context.LINE) or (flatReviewType == Context.ZONE):
            lineIndex = self.lineIndex
        elif flatReviewType == Context.WINDOW:
            lineIndex  = len(self.lines) - 1
        else:
            raise Exception("Invalid type: %d" % flatReviewType)

        if flatReviewType == Context.ZONE:
            zoneIndex = self.zoneIndex
        else:
            zoneIndex = len(self.lines[lineIndex].zones) - 1

        zone = self.lines[lineIndex].zones[zoneIndex]
        if zone.words:
            wordIndex = len(zone.words) - 1
            chars = zone.words[wordIndex].chars
            if chars:
                charIndex = len(chars) - 1
            else:
                charIndex = 0
        else:
            wordIndex = 0
            charIndex = 0

        moved = (self.lineIndex != lineIndex) \
                or (self.zoneIndex != zoneIndex) \
                or (self.wordIndex != wordIndex) \
                or (self.charIndex != charIndex) \

        if moved:
            self.lineIndex = lineIndex
            self.zoneIndex = zoneIndex
            self.wordIndex = wordIndex
            self.charIndex = charIndex
            self.targetCharInfo = self.getCurrent(Context.CHAR)

        return moved

    def goPrevious(self, flatReviewType=ZONE, 
                   wrap=WRAP_ALL, omitWhitespace=True):
        """Moves this context's locus of interest to the first char
        of the previous type.

        Arguments:
        - flatReviewType: one of ZONE, CHAR, WORD, LINE
        - wrap: if True, will cross boundaries, including top and
                bottom; if False, will stop on boundaries.

        Returns True if the locus of interest actually changed.
        """

        if not self.lines:
            debug.println(debug.LEVEL_FINE, 'goPrevious(): no lines in context')
            return False

        moved = False

        if flatReviewType == Context.ZONE:
            if self.zoneIndex > 0:
                self.zoneIndex -= 1
                self.wordIndex = 0
                self.charIndex = 0
                moved = True
            elif wrap & Context.WRAP_LINE:
                if self.lineIndex > 0:
                    self.lineIndex -= 1
                    self.zoneIndex = len(self.lines[self.lineIndex].zones) - 1
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif wrap & Context.WRAP_TOP_BOTTOM:
                    self.lineIndex = len(self.lines) - 1
                    self.zoneIndex = len(self.lines[self.lineIndex].zones) - 1
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
        elif flatReviewType == Context.CHAR:
            if self.charIndex > 0:
                self.charIndex -= 1
                moved = True
            else:
                moved = self.goPrevious(Context.WORD, wrap, False)
                if moved:
                    zone = self.lines[self.lineIndex].zones[self.zoneIndex]
                    if zone.words:
                        chars = zone.words[self.wordIndex].chars
                        if chars:
                            self.charIndex = len(chars) - 1
        elif flatReviewType == Context.WORD:
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            accessible = zone.accessible
            lineIndex = self.lineIndex
            zoneIndex = self.zoneIndex
            wordIndex = self.wordIndex
            charIndex = self.charIndex

            if self.wordIndex > 0:
                self.wordIndex -= 1
                self.charIndex = 0
                moved = True
            else:
                moved = self.goPrevious(Context.ZONE, wrap)
                if moved:
                    zone = self.lines[self.lineIndex].zones[self.zoneIndex]
                    if zone.words:
                        self.wordIndex = len(zone.words) - 1

            # If we landed on a whitespace word or something with no words,
            # we might need to move some more.
            #
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            if omitWhitespace \
               and moved \
               and ((len(zone.string) == 0) \
                    or (len(zone.words) \
                        and zone.words[self.wordIndex].string.isspace())):

                hasMoreText = False
                if self.lineIndex > 0 and isinstance(zone, TextZone):
                    prevZone = self.lines[self.lineIndex - 1].zones[-1]
                    if prevZone.accessible == zone.accessible:
                        hasMoreText = True

                # If we're on whitespace in the same zone, then let's
                # try to move on.  If not, we've definitely moved
                # across accessibles.  If that's the case, let's try
                # to find the first 'real' word in the accessible.
                # If we cannot, then we're just stuck on an accessible
                # with no words and we should do our best to announce
                # this to the user (e.g., "whitespace" or "blank").
                #
                if zone.accessible == accessible or hasMoreText:
                    moved = self.goPrevious(Context.WORD, wrap)
                else:
                    wordIndex = self.wordIndex - 1
                    while wordIndex >= 0:
                        if (not zone.words[wordIndex].string) \
                            or not len(zone.words[wordIndex].string) \
                            or zone.words[wordIndex].string.isspace():
                            wordIndex -= 1
                        else:
                            break
                    if wordIndex >= 0:
                        self.wordIndex = wordIndex

            if not moved:
                self.lineIndex = lineIndex
                self.zoneIndex = zoneIndex
                self.wordIndex = wordIndex
                self.charIndex = charIndex

        elif flatReviewType == Context.LINE:
            if wrap & Context.WRAP_LINE:
                if self.lineIndex > 0:
                    self.lineIndex -= 1
                    self.zoneIndex = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif (wrap & Context.WRAP_TOP_BOTTOM) \
                     and (len(self.lines) != 1):
                    self.lineIndex = len(self.lines) - 1
                    self.zoneIndex = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
        else:
            raise Exception("Invalid type: %d" % flatReviewType)

        if moved and (flatReviewType != Context.LINE):
            self.targetCharInfo = self.getCurrent(Context.CHAR)

        return moved

    def goNext(self, flatReviewType=ZONE, wrap=WRAP_ALL, omitWhitespace=True):
        """Moves this context's locus of interest to first char of
        the next type.

        Arguments:
        - flatReviewType: one of ZONE, CHAR, WORD, LINE
        - wrap: if True, will cross boundaries, including top and
                bottom; if False, will stop on boundaries.
        """

        if not self.lines:
            debug.println(debug.LEVEL_FINE, 'goNext(): no lines in context')
            return False

        moved = False

        if flatReviewType == Context.ZONE:
            if self.zoneIndex < (len(self.lines[self.lineIndex].zones) - 1):
                self.zoneIndex += 1
                self.wordIndex = 0
                self.charIndex = 0
                moved = True
            elif wrap & Context.WRAP_LINE:
                if self.lineIndex < (len(self.lines) - 1):
                    self.lineIndex += 1
                    self.zoneIndex  = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif wrap & Context.WRAP_TOP_BOTTOM:
                    self.lineIndex  = 0
                    self.zoneIndex  = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
        elif flatReviewType == Context.CHAR:
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            if zone.words:
                chars = zone.words[self.wordIndex].chars
                if chars:
                    if self.charIndex < (len(chars) - 1):
                        self.charIndex += 1
                        moved = True
                    else:
                        moved = self.goNext(Context.WORD, wrap, False)
                else:
                    moved = self.goNext(Context.WORD, wrap)
            else:
                moved = self.goNext(Context.ZONE, wrap)
        elif flatReviewType == Context.WORD:
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            accessible = zone.accessible
            lineIndex = self.lineIndex
            zoneIndex = self.zoneIndex
            wordIndex = self.wordIndex
            charIndex = self.charIndex

            if zone.words:
                if self.wordIndex < (len(zone.words) - 1):
                    self.wordIndex += 1
                    self.charIndex = 0
                    moved = True
                else:
                    moved = self.goNext(Context.ZONE, wrap)
            else:
                moved = self.goNext(Context.ZONE, wrap)

            # If we landed on a whitespace word or something with no words,
            # we might need to move some more.
            #
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            if omitWhitespace \
               and moved \
               and ((len(zone.string) == 0) \
                    or (len(zone.words) \
                        and zone.words[self.wordIndex].string.isspace())):

                # If we're on whitespace in the same zone, then let's
                # try to move on.  If not, we've definitely moved
                # across accessibles.  If that's the case, let's try
                # to find the first 'real' word in the accessible.
                # If we cannot, then we're just stuck on an accessible
                # with no words and we should do our best to announce
                # this to the user (e.g., "whitespace" or "blank").
                #
                if zone.accessible == accessible:
                    moved = self.goNext(Context.WORD, wrap)
                else:
                    wordIndex = self.wordIndex + 1
                    while wordIndex < len(zone.words):
                        if (not zone.words[wordIndex].string) \
                            or not len(zone.words[wordIndex].string) \
                            or zone.words[wordIndex].string.isspace():
                            wordIndex += 1
                        else:
                            break
                    if wordIndex < len(zone.words):
                        self.wordIndex = wordIndex

            if not moved:
                self.lineIndex = lineIndex
                self.zoneIndex = zoneIndex
                self.wordIndex = wordIndex
                self.charIndex = charIndex

        elif flatReviewType == Context.LINE:
            if wrap & Context.WRAP_LINE:
                if self.lineIndex < (len(self.lines) - 1):
                    self.lineIndex += 1
                    self.zoneIndex = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif (wrap & Context.WRAP_TOP_BOTTOM) \
                     and (self.lineIndex != 0):
                    self.lineIndex = 0
                    self.zoneIndex = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
        else:
            raise Exception("Invalid type: %d" % flatReviewType)

        if moved and (flatReviewType != Context.LINE):
            self.targetCharInfo = self.getCurrent(Context.CHAR)

        return moved

    def goAbove(self, flatReviewType=LINE, wrap=WRAP_ALL):
        """Moves this context's locus of interest to first char
        of the type that's closest to and above the current locus of
        interest.

        Arguments:
        - flatReviewType: LINE
        - wrap: if True, will cross top/bottom boundaries; if False, will
                stop on top/bottom boundaries.

        Returns: [string, startOffset, endOffset, x, y, width, height]
        """

        moved = False
        if flatReviewType == Context.CHAR:
            # We want to shoot for the closest character, which we've
            # saved away as self.targetCharInfo, which is the list
            # [string, x, y, width, height].
            #
            if not self.targetCharInfo:
                self.targetCharInfo = self.getCurrent(Context.CHAR)
            target = self.targetCharInfo

            [string, x, y, width, height] = target
            middleTargetX = x + (width / 2)

            moved = self.goPrevious(Context.LINE, wrap)
            if moved:
                while True:
                    [string, bx, by, bwidth, bheight] = \
                             self.getCurrent(Context.CHAR)
                    if (bx + width) >= middleTargetX:
                        break
                    elif not self.goNext(Context.CHAR, Context.WRAP_NONE):
                        break

            # Moving around might have reset the current targetCharInfo,
            # so we reset it to our saved value.
            #
            self.targetCharInfo = target
        elif flatReviewType == Context.LINE:
            return self.goPrevious(flatReviewType, wrap)
        else:
            raise Exception("Invalid type: %d" % flatReviewType)

        return moved

    def goBelow(self, flatReviewType=LINE, wrap=WRAP_ALL):
        """Moves this context's locus of interest to the first
        char of the type that's closest to and below the current
        locus of interest.

        Arguments:
        - flatReviewType: one of WORD, LINE
        - wrap: if True, will cross top/bottom boundaries; if False, will
                stop on top/bottom boundaries.

        Returns: [string, startOffset, endOffset, x, y, width, height]
        """

        moved = False
        if flatReviewType == Context.CHAR:
            # We want to shoot for the closest character, which we've
            # saved away as self.targetCharInfo, which is the list
            # [string, x, y, width, height].
            #
            if not self.targetCharInfo:
                self.targetCharInfo = self.getCurrent(Context.CHAR)
            target = self.targetCharInfo

            [string, x, y, width, height] = target
            middleTargetX = x + (width / 2)

            moved = self.goNext(Context.LINE, wrap)
            if moved:
                while True:
                    [string, bx, by, bwidth, bheight] = \
                             self.getCurrent(Context.CHAR)
                    if (bx + width) >= middleTargetX:
                        break
                    elif not self.goNext(Context.CHAR, Context.WRAP_NONE):
                        break

            # Moving around might have reset the current targetCharInfo,
            # so we reset it to our saved value.
            #
            self.targetCharInfo = target
        elif flatReviewType == Context.LINE:
            moved = self.goNext(flatReviewType, wrap)
        else:
            raise Exception("Invalid type: %d" % flatReviewType)

        return moved
