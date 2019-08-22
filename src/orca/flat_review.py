# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import re

from . import braille
from . import debug
from . import eventsynthesizer
from . import messages
from . import orca_state
from . import settings

EMBEDDED_OBJECT_CHARACTER = '\ufffc'

class Char:
    """A character's worth of presentable information."""

    def __init__(self, word, index, startOffset, string, x, y, width, height):
        """Creates a new char.

        Arguments:
        - word: the Word instance this belongs to
        - startOffset: the start offset with respect to the accessible
        - string: the actual char
        - x, y, width, height: the extents of this Char on the screen
        """

        self.word = word
        self.index = index
        self.startOffset = startOffset
        self.endOffset = startOffset + 1
        self.string = string
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Word:
    """A single chunk (word or object) of presentable information."""

    def __init__(self, zone, index, startOffset, string, x, y, width, height):
        """Creates a new Word.

        Arguments:
        - zone: the Zone instance this belongs to
        - index: the index of this Word in the Zone
        - startOffset: the start offset with respect to the accessible
        - string: the actual string
        - x, y, width, height: the extents of this Word on the screen
        """

        self.zone = zone
        self.index = index
        self.startOffset = startOffset
        self.string = string
        self.length = len(string)
        self.endOffset = self.startOffset + len(string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.chars = []

    def __getattribute__(self, attr):
        if attr != "chars":
            return super().__getattribute__(attr)

        # TODO - JD: For now, don't fake character and word extents.
        # The main goal is to improve reviewability.
        extents = self.x, self.y, self.width, self.height

        try:
            text = self.zone.accessible.queryText()
        except:
            text = None

        chars = []
        for i, char in enumerate(self.string):
            start = i + self.startOffset
            if text:
                extents = text.getRangeExtents(start, start+1, pyatspi.DESKTOP_COORDS)
            chars.append(Char(self, i, start, char, *extents))

        return chars

    def getRelativeOffset(self, offset):
        """Returns the char offset with respect to this word or -1."""

        if self.startOffset <= offset < self.startOffset + len(self.string):
            return offset - self.startOffset

        return -1


class Zone:
    """Represents text that is a portion of a single horizontal line."""

    WORDS_RE = re.compile(r"(\S+\s*)", re.UNICODE)

    def __init__(self, accessible, string, x, y, width, height, role=None):
        """Creates a new Zone.

        Arguments:
        - accessible: the Accessible associated with this Zone
        - string: the string being displayed for this Zone
        - extents: x, y, width, height in screen coordinates
        - role: Role to override accessible's role.
        """

        self.accessible = accessible
        self.startOffset = 0
        self._string = string
        self.length = len(string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.role = role or accessible.getRole()
        self._words = []

    def __getattribute__(self, attr):
        """To ensure we update the content."""

        if attr not in ["words", "string"]:
            return super().__getattribute__(attr)

        if attr == "string":
            return self._string

        if not self._shouldFakeText():
            return self._words

        # TODO - JD: For now, don't fake character and word extents.
        # The main goal is to improve reviewability.
        extents = self.x, self.y, self.width, self.height

        words = []
        for i, word in enumerate(re.finditer(self.WORDS_RE, self._string)):
            words.append(Word(self, i, word.start(), word.group(), *extents))

        self._words = words
        return words

    def _shouldFakeText(self):
        """Returns True if we should try to fake the text interface"""

        textRoles = [pyatspi.ROLE_LABEL,
                     pyatspi.ROLE_MENU,
                     pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM,
                     pyatspi.ROLE_PAGE_TAB,
                     pyatspi.ROLE_PUSH_BUTTON,
                     pyatspi.ROLE_TABLE_CELL]

        if self.role in textRoles:
            return True

        return False

    def _extentsAreOnSameLine(self, zone, pixelDelta=5):
        """Returns True if this Zone is physically on the same line as zone."""

        if self.width == 0 and self.height == 0:
            return zone.y <= self.y <= zone.y + zone.height

        if zone.width == 0 and self.height == 0:
            return self.y <= zone.y <= self.y + self.height

        highestBottom = min(self.y + self.height, zone.y + zone.height)
        lowestTop = max(self.y, zone.y)
        if lowestTop >= highestBottom:
            return False

        middle = self.y + self.height / 2
        zoneMiddle = zone.y + zone.height / 2
        if abs(middle - zoneMiddle) > pixelDelta:
            return False

        return True

    def onSameLine(self, zone):
        """Returns True if we treat this Zone and zone as being on one line."""

        if pyatspi.ROLE_SCROLL_BAR in [self.role, zone.role]:
            return self.accessible == zone.accessible

        try:
            thisParentRole = self.accessible.parent.getRole()
            zoneParentRole = zone.accessible.parent.getRole()
        except:
            pass
        else:
            if pyatspi.ROLE_MENU_BAR in [thisParentRole, zoneParentRole]:
                return self.accessible.parent == zone.accessible.parent

        return self._extentsAreOnSameLine(zone)

    def getWordAtOffset(self, charOffset):
        for word in self.words:
            offset = word.getRelativeOffset(charOffset)
            if offset >= 0:
                return word, offset

        if self.length == charOffset and self.words:
            lastWord = self.words[-1]
            return lastWord, lastWord.length

        return None, -1

    def hasCaret(self):
        """Returns True if this Zone contains the caret."""

        return False

    def wordWithCaret(self):
        """Returns the Word and relative offset with the caret."""

        return None, -1

class TextZone(Zone):
    """A Zone whose purpose is to display text of an object."""

    def __init__(self, accessible, startOffset, string, x, y, width, height, role=None):
        super().__init__(accessible, string, x, y, width, height, role)

        self.startOffset = startOffset
        self.endOffset = self.startOffset + len(string)
        self._itext = self.accessible.queryText()

    def __getattribute__(self, attr):
        """To ensure we update the content."""

        if not attr in ["words", "string"]:
            return super().__getattribute__(attr)

        string = self._itext.getText(self.startOffset, self.endOffset)
        words = []
        for i, word in enumerate(re.finditer(self.WORDS_RE, string)):
            start, end = map(lambda x: x + self.startOffset, word.span())
            extents = self._itext.getRangeExtents(start, end, pyatspi.DESKTOP_COORDS)
            words.append(Word(self, i, start, word.group(), *extents))

        self._string = string
        self._words = words
        return super().__getattribute__(attr)

    def hasCaret(self):
        """Returns True if this Zone contains the caret."""

        offset = self._itext.caretOffset
        if self.startOffset <= offset < self.endOffset:
            return True

        return self.endOffset == self._itext.characterCount

    def wordWithCaret(self):
        """Returns the Word and relative offset with the caret."""

        if not self.hasCaret():
            return None, -1

        return self.getWordAtOffset(self._itext.caretOffset)


class StateZone(Zone):
    """A Zone whose purpose is to display the state of an object."""

    def __init__(self, accessible, x, y, width, height, role=None):
        super().__init__(accessible, "", x, y, width, height, role)

    def __getattribute__(self, attr):
        """To ensure we update the state."""

        if attr not in ["string", "brailleString"]:
            return super().__getattribute__(attr)

        if attr == "string":
            generator = orca_state.activeScript.speechGenerator
        else:
            generator = orca_state.activeScript.brailleGenerator

        result = generator.getStateIndicator(self.accessible, role=self.role)
        if result:
            return result[0]

        return ""


class ValueZone(Zone):
    """A Zone whose purpose is to display the value of an object."""

    def __init__(self, accessible, x, y, width, height, role=None):
        super().__init__(accessible, "", x, y, width, height, role)

    def __getattribute__(self, attr):
        """To ensure we update the value."""

        if attr not in ["string", "brailleString"]:
            return super().__getattribute__(attr)

        if attr == "string":
            generator = orca_state.activeScript.speechGenerator
        else:
            generator = orca_state.activeScript.brailleGenerator

        result = ""

        # TODO - JD: This cobbling together beats what we had, but the
        # generators should also be doing the assembly.
        rolename = generator.getLocalizedRoleName(self.accessible)
        value = generator.getValue(self.accessible)
        if rolename and value:
            result = "%s %s" % (rolename, value[0])

        return result


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

    def __getattribute__(self, attr):
        if attr == "string":
            return " ".join([zone.string for zone in self.zones])

        if attr == "x":
            return min([zone.x for zone in self.zones])

        if attr == "y":
            return min([zone.y for zone in self.zones])

        if attr == "width":
            return sum([zone.width for zone in self.zones])

        if attr == "height":
            return max([zone.height for zone in self.zones])

        return super().__getattribute__(attr)

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
    """Contains the flat review regions for the current top-level object."""

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
        """Create a new Context for script."""

        self.script = script
        self.zones = []
        self.lines = []
        self.lineIndex = 0
        self.zoneIndex = 0
        self.wordIndex = 0
        self.charIndex = 0
        self.targetCharInfo = None
        self.focusZone = None
        self.container = None
        self.focusObj = orca_state.locusOfFocus
        self.topLevel = script.utilities.topLevelObject(self.focusObj)
        self.bounds = 0, 0, 0, 0

        try:
            component = self.topLevel.queryComponent()
            self.bounds = component.getExtents(pyatspi.DESKTOP_COORDS)
        except:
            msg = "ERROR: Exception getting extents of %s" % self.topLevel
            debug.println(debug.LEVEL_INFO, msg, True)

        containerRoles = [pyatspi.ROLE_MENU]
        isContainer = lambda x: x and x.getRole() in containerRoles
        container = pyatspi.findAncestor(self.focusObj, isContainer)
        if not container and isContainer(self.focusObj):
            container = self.focusObj

        self.container = container or self.topLevel

        self.zones, self.focusZone = self.getShowingZones(self.container)
        self.lines = self.clusterZonesByLine(self.zones)
        if not (self.lines and self.focusZone):
            return

        for i, line in enumerate(self.lines):
            if self.focusZone in line.zones:
                self.lineIndex = i
                self.zoneIndex = line.zones.index(self.focusZone)
                word, offset = self.focusZone.wordWithCaret()
                if word:
                    self.wordIndex = word.index
                    self.charIndex = offset
                break

        msg = "FLAT REVIEW: On line %i, zone %i, word %i, char %i" % \
              (self.lineIndex, self.zoneIndex, self.wordIndex, self.charIndex)
        debug.println(debug.LEVEL_INFO, msg, True)

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
                extents = text.getRangeExtents(
                    substringStartOffset, substringEndOffset, 0)
                if self.script.utilities.containsRegion(extents, cliprect):
                    anyVisible = True
                    clipping = self.script.utilities.intersection(extents, cliprect)


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

        try:
            text = accessible.queryText()
        except NotImplementedError:
            return []
        else:
            zones = []

        # TODO - JD: This is here temporarily whilst I sort out the rest
        # of the text-related mess.
        if not re.search("[^\ufffc]", text.getText(0, -1)):
            return []

        # TODO - JD: Ditto.
        if "EditableText" in pyatspi.listInterfaces(accessible) \
           and accessible.getState().contains(pyatspi.STATE_SINGLE_LINE):
            extents = accessible.queryComponent().getExtents(0)
            return [TextZone(accessible, 0, text.getText(0, -1), *extents)]

        debug.println(debug.LEVEL_FINEST, "  looking at text:")

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

        return zones

    def _insertStateZone(self, zones, accessible, extents):
        """If the accessible presents non-textual state, such as a
        checkbox or radio button, insert a StateZone representing
        that state."""

        # TODO - JD: This whole thing is pretty hacky. Either do it
        # right or nuke it.

        indicatorExtents = [extents.x, extents.y, 1, extents.height]
        role = accessible.getRole()
        if role == pyatspi.ROLE_TOGGLE_BUTTON:
            zone = StateZone(accessible, *indicatorExtents, role=role)
            if zone:
                zones.insert(0, zone)
            return

        if role == pyatspi.ROLE_TABLE_CELL \
           and self.script.utilities.hasMeaningfulToggleAction(accessible):
            role = pyatspi.ROLE_CHECK_BOX

        if role not in [pyatspi.ROLE_CHECK_BOX,
                        pyatspi.ROLE_CHECK_MENU_ITEM,
                        pyatspi.ROLE_RADIO_BUTTON,
                        pyatspi.ROLE_RADIO_MENU_ITEM]:
            return

        zone = None
        stateOnLeft = True

        if len(zones) == 1 and isinstance(zones[0], TextZone):
            textZone = zones[0]
            textToLeftEdge = textZone.x - extents.x
            textToRightEdge = (extents.x + extents.width) - (textZone.x + textZone.width)
            stateOnLeft = textToLeftEdge > 20
            if stateOnLeft:
                indicatorExtents[2] = textToLeftEdge
            else:
                indicatorExtents[0] = textZone.x + textZone.width
                indicatorExtents[2] = textToRightEdge

        zone = StateZone(accessible, *indicatorExtents, role=role)
        if zone:
            if stateOnLeft:
                zones.insert(0, zone)
            else:
                zones.append(zone)

    def getZonesFromAccessible(self, accessible, cliprect):
        """Returns a list of Zones for the given accessible."""

        try:
            component = accessible.queryComponent()
            extents = component.getExtents(pyatspi.DESKTOP_COORDS)
        except:
            return []

        try:
            role = accessible.getRole()
        except:
            return []

        zones = self.getZonesFromText(accessible, cliprect)
        if not zones and role in [pyatspi.ROLE_SCROLL_BAR,
                                  pyatspi.ROLE_SLIDER,
                                  pyatspi.ROLE_PROGRESS_BAR]:
            zones.append(ValueZone(accessible, *extents))
        elif not zones:
            string = ""
            redundant = [pyatspi.ROLE_TABLE_ROW]
            if role not in redundant:
                string = self.script.speechGenerator.getName(accessible)

            useless = [pyatspi.ROLE_TABLE_CELL, pyatspi.ROLE_LABEL]
            if not string and role not in useless:
                string = self.script.speechGenerator.getRoleName(accessible)
            if string:
                zones.append(Zone(accessible, string, *extents))

        self._insertStateZone(zones, accessible, extents)

        return zones

    def _isOrIsIn(self, child, parent):
        if not (child and parent):
            return False

        if child == parent:
            return True

        return pyatspi.findAncestor(child, lambda x: x == parent)

    def getShowingZones(self, root, boundingbox=None):
        """Returns an unsorted list of all the zones under root and the focusZone."""

        if boundingbox is None:
            boundingbox = self.bounds

        objs = self.script.utilities.getOnScreenObjects(root, boundingbox)
        msg = "FLAT REVIEW: %i on-screen objects found for %s" % (len(objs), root)
        debug.println(debug.LEVEL_INFO, msg, True)

        allZones, focusZone = [], None
        for o in objs:
            zones = self.getZonesFromAccessible(o, boundingbox)
            if not zones:
                descendant = self.script.utilities.realActiveDescendant(o)
                if descendant:
                    zones = self.getZonesFromAccessible(descendant, boundingbox)

            if not zones:
                continue

            allZones.extend(zones)
            if not focusZone and zones and self.focusObj and self._isOrIsIn(o, self.focusObj):
                zones = list(filter(lambda z: z.hasCaret(), zones)) or zones
                focusZone = zones[0]

        msg = "FLAT REVIEW: %i zones found for %s" % (len(allZones), root)
        debug.println(debug.LEVEL_INFO, msg, True)
        return allZones, focusZone

    def clusterZonesByLine(self, zones):
        """Returns a sorted list of Line clusters containing sorted Zones."""

        if not zones:
            return []

        lineClusters = []
        sortedZones = sorted(zones, key=lambda z: z.y)
        newCluster = [sortedZones.pop(0)]
        for zone in sortedZones:
            if zone.onSameLine(newCluster[-1]):
                newCluster.append(zone)
            else:
                lineClusters.append(sorted(newCluster, key=lambda z: z.x))
                newCluster = [zone]

        if newCluster:
            lineClusters.append(sorted(newCluster, key=lambda z: z.x))

        lines = []
        for lineIndex, lineCluster in enumerate(lineClusters):
            lines.append(Line(lineIndex, lineCluster))
            for zoneIndex, zone in enumerate(lineCluster):
                zone.line = lines[lineIndex]
                zone.index = zoneIndex

        msg = "FLAT REVIEW: Zones clustered into %i lines" % len(lines)
        debug.println(debug.LEVEL_INFO, msg, True)
        return lines

    def getCurrent(self, flatReviewType=ZONE):
        """Returns the current string, offset, and extent information."""

        # TODO - JD: This method has not (yet) been renamed. But we have a
        # getter and setter which do totally different things....

        zone = self._getCurrentZone()
        if not zone:
            return None, -1, -1, -1, -1

        current = zone
        if flatReviewType == Context.LINE:
            current = zone.line
        elif zone.words:
            current = zone.words[self.wordIndex]
            if flatReviewType == Context.CHAR and current.chars:
                try:
                    current = current.chars[self.charIndex]
                except:
                    return None, -1, -1, -1, -1

        return current.string, current.x, current.y, current.width, current.height

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

    def _getClickPoint(self):
        string, x, y, width, height = self.getCurrent(Context.CHAR)
        if (x < 0 and y < 0) or (width <= 0 and height <=0):
            return -1, -1

        # Click left of center to position the caret there.
        x = int(max(x, x + (width / 2) - 1))
        y = int(y + height / 2)

        return x, y

    def routeToCurrent(self):
        """Routes the mouse pointer to the current accessible."""

        x, y = self._getClickPoint()
        if x < 0 or y < 0:
            return False

        return eventsynthesizer.routeToPoint(x, y)

    def clickCurrent(self, button=1):
        """Performs a mouse click on the current accessible."""

        x, y = self._getClickPoint()
        if x >= 0 and y >= 0 and eventsynthesizer.clickPoint(x, y, button):
            return True

        if eventsynthesizer.clickObject(self.getCurrentAccessible(), button):
            return True

        return False

    def _getCurrentZone(self):
        if not (self.lines and 0 <= self.lineIndex < len(self.lines)):
            return None

        line = self.lines[self.lineIndex]
        if not (line and 0 <= self.zoneIndex < len(line.zones)):
            return None

        return line.zones[self.zoneIndex]

    def getCurrentAccessible(self):
        """Returns the current accessible."""

        zone = self._getCurrentZone()
        if not zone:
            return None

        return zone.accessible

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
