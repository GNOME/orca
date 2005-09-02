# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import a11y
import core
import rolenames

# [[[TODO: WDW - this whole thing is a bit shaky right now.  I think
# it's because I wrote half the code late at night.  I tried to do
# the right thing, but I think "tried" got reformed as "tired."]]]

class Zone:
    """Represents text that is a portion of a single horizontal line."""

    COMPONENT = 0
    TEXT      = 1
    IMAGE     = 2

    def __init__(self, 
                 accessible,
                 type,
                 string, 
                 x, y, 
                 width, height, 
                 startOffset):
        """Creates a new Zone, which is a horizontal region of text.

        Arguments:
        - accessible: the Accessible associated with this Zone
        - string: the string being displayed for this Zone
        - type: one of COMPONENT, TEXT, etc.
        - extents: x, y, width, height: if the accessible implements
                   Accessibility_Text, these will be the range extents
                   for startOffset and endOffset.  If the accessible
                   does not implement Accessibility_Text, then these will
                   be the extents of the Accessibility_Component.
        - startOffset: index into Accessibility_Text for start of line
        """
        
        self.accessible = accessible
        self.type = type
        self.string = string
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.startOffset = startOffset
        self.length = len(string)

        
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
                        

class Context:
    """Information regarding where a user happens to be exploring
    right now.
    """

    ZONE      = 0
    CHARACTER = 1
    WORD      = 2
    LINE      = 3 # includes all zones on same line
    WINDOW    = 4

    WRAP_LINE       = 1 << 0
    WRAP_TOP_BOTTOM = 1 << 1
    WRAP_ALL        = (WRAP_LINE | WRAP_TOP_BOTTOM)
    
    def __init__(self, lines, lineIndex, zoneIndex, textOffset):
        """Create a new Context that will be used for handling flat
        review mode.

        Arguments:
        - lines:      an array of arrays of Zones (see clusterZonesByLine)
        - lineIndex:  index pointing into lines
        - zoneIndex:  index pointing into lines[lineIndex]
        - textOffset: character index into the string of the
                      current zone.
        """

        self.lines      = lines
        self.lineIndex  = lineIndex
        self.zoneIndex  = zoneIndex
        self.textOffset = textOffset


    def _debugWhatHappened(self, moved):
        zone = self.lines[self.lineIndex][self.zoneIndex]

        print "line=%d, zone=%d" % (self.lineIndex, self.zoneIndex)
        print "  zone.startOffset   = %d" % zone.startOffset
        print "  self.textOffset    = %d" % self.textOffset
        print "  zone.length        = %d" % zone.length
        print "  zone.string        = '%s'" % zone.string
        print "  moved              =", moved

        
    def getCurrent(self, type=ZONE):
        """Gets the string, offset, and extent information for the
        current locus of interest.

        Arguments:
        - type: one of ZONE, CHARACTER, WORD, LINE

        Returns: [string, x, y, width, height]
        """
        
        zone = self.lines[self.lineIndex][self.zoneIndex]
            
        if type == Context.ZONE:
            return [zone.string,
                    zone.x, zone.y,
                    zone.width, zone.height]
        elif type == Context.CHARACTER:
            text = zone.accessible.text
            if text:
                [string, startOffset, endOffset] = text.getTextAtOffset(
                    zone.startOffset + self.textOffset,
                    core.Accessibility.TEXT_BOUNDARY_CHAR)
                string = string.strip()
                endOffset = startOffset + len(string)
                [x, y, width, height] = text.getRangeExtents(startOffset, 
                                                             endOffset, 
                                                             0)
                return [string,
                        x, y, width, height]
            else:
                return self.getCurrent(Context.ZONE)
        elif type == Context.WORD:
            text = zone.accessible.text
            if text:
                [string, startOffset, endOffset] = text.getTextAtOffset(
                    zone.startOffset + self.textOffset,
                    core.Accessibility.TEXT_BOUNDARY_WORD_START)
                string = string.strip()
                endOffset = min(startOffset + len(string),
                                zone.startOffset + zone.length)
                startOffset = max(startOffset, zone.startOffset)
                string = text.getText(startOffset, endOffset)
                [x, y, width, height] = text.getRangeExtents(startOffset, 
                                                             endOffset, 
                                                             0)
                return [string,
                        x, y, width, height]
            else:
                return self.getCurrent(Context.ZONE)
        elif type == Context.LINE:
            line = self.lines[self.lineIndex]
            bounds = None
            string = ""
            for zone in line:
                if bounds is None:
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
            if bounds is None:
                bounds = [-1, -1, -2, -2]
            return [string,
                    bounds[0], bounds[1],
                    bounds[2] - bounds[0],
                    bounds[3] - bounds[1]]
        else:
            raise Error, "Invalid type: %d" % type

            
    def goBegin(self, type=WINDOW):
        """Moves this context's locus of interest to the first character
        of the first relevant zone.

        Arguments:
        - type: one of LINE or WINDOW
        
        Returns True if the locus of interest actually changed.
        """

        if type == Context.LINE:
            lineIndex  = self.lineIndex
            zoneIndex  = 0
            textOffset = 0
        elif type == Context.WINDOW:
            lineIndex  = 0
            zoneIndex  = 0
            textOffset = 0
        else:
            raise Error, "Invalid type: %d" % type
            
        moved = (self.lineIndex != lineIndex) \
                or (self.zoneIndex != zoneIndex) \
                or (self.textOffset != textOffset)

        self.lineIndex  = lineIndex
        self.zoneIndex  = zoneIndex
        self.textOffset = textOffset

        return moved

    
    def goEnd(self, type=WINDOW):
        """Moves this context's locus of interest to the last character
        of the last relevant zone.

        Arguments:
        - type: one of LINE or WINDOW
        
        Returns True if the locus of interest actually changed.
        """

        if type == Context.LINE:
            lineIndex  = self.lineIndex
            zoneIndex  = len(self.lines[lineIndex]) - 1
            zone       = self.lines[lineIndex][zoneIndex]
            textOffset = max(0, zone.length - 1)
        elif type == Context.WINDOW:
            lineIndex  = len(self.lines) - 1
            zoneIndex  = len(self.lines[lineIndex]) - 1
            zone       = self.lines[lineIndex][zoneIndex]
            textOffset = max(0, zone.length - 1)
        else:
            raise Error, "Invalid type: %d" % type

        moved = (self.lineIndex != lineIndex) \
                or (self.zoneIndex != zoneIndex) \
                or (self.textOffset != textOffset)

        self.lineIndex  = lineIndex
        self.zoneIndex  = zoneIndex
        self.textOffset = textOffset

        return moved

        
    def goPrevious(self, type=ZONE, wrap=WRAP_ALL):
        """Moves this context's locus of interest to the first character
        of the previous type.

        Arguments:
        - type: one of ZONE, CHARACTER, WORD, LINE
        - wrap: if True, will cross boundaries, including top and
                bottom; if False, will stop on boundaries.                

        Returns True if the locus of interest actually changed.
        """

        moved = False

        if type == Context.ZONE:
            if self.zoneIndex > 0:
                self.zoneIndex -= 1
                self.textOffset = 0
                moved = True
            elif wrap & Context.WRAP_LINE:
                if self.lineIndex > 0:
                    self.lineIndex -= 1
                    self.zoneIndex  = len(self.lines[self.lineIndex]) - 1
                    self.textOffset = 0
                    moved = True
                elif wrap & Context.WRAP_TOP_BOTTOM:
                    self.lineIndex  = len(self.lines) - 1
                    self.zoneIndex  = len(self.lines[self.lineIndex]) - 1
                    self.textOffset = 0
                    moved = True
        elif type == Context.CHARACTER:
            # We can only do WORD and CHARACTER traversal with
            # Accessible_Text objects for now.  For all other
            # objects, we'll treat it like a Zone traversal.
            #
            zone = self.lines[self.lineIndex][self.zoneIndex]
            if zone.type == Zone.TEXT:
                if self.textOffset > 0:
                    self.textOffset -= 1
                    text = zone.accessible.text
                    [string, startOffset, endOffset] = text.getTextAtOffset(
                        zone.startOffset + self.textOffset,
                        core.Accessibility.TEXT_BOUNDARY_CHAR)
                    moved = True
                else:
                    moved = self.goPrevious(Context.ZONE, wrap)
                    if moved:
                        zone = self.lines[self.lineIndex][self.zoneIndex]
                        if zone.type == Zone.TEXT:
                            self.textOffset = max(0, zone.length - 1)
                        if len(zone.string) == 0:
                            self.goPrevious(type, wrap)
            else:
                moved = self.goPrevious(Context.ZONE, wrap)
                if moved:
                    zone = self.lines[self.lineIndex][self.zoneIndex]
                    if zone.type == Zone.TEXT:
                        self.textOffset = max(0, zone.length - 1)
                    if len(zone.string) == 0:
                        self.goPrevious(type, wrap)
        elif type == Context.WORD:
            # We can only do WORD and CHARACTER traversal with
            # Accessible_Text objects for now.  For all other
            # objects, we'll treat it like a Zone traversal.
            #
            zone = self.lines[self.lineIndex][self.zoneIndex]
            if zone.type != Zone.TEXT:
                moved = self.goPrevious(Context.ZONE, wrap)
                if moved:
                    zone = self.lines[self.lineIndex][self.zoneIndex]
                    if zone.type == Zone.TEXT:
                        self.textOffset = zone.length
                        self.goPrevious(type, wrap)
                    [string, x, y, width, height] = \
                             self.getCurrent(Context.WORD)
                    if len(string.strip()) == 0:
                        self.goPrevious(type, wrap)
                return moved

            # We first think about working within the current Zone
            # if we can...
            #
            text = zone.accessible.text
            if self.textOffset > 0:
                # We'll move the text offset to the beginning of the
                # previous word in the current zone if possible.
                #
                [string, startOffset, endOffset] = text.getTextAtOffset(
                    zone.startOffset + self.textOffset - 1,
                    core.Accessibility.TEXT_BOUNDARY_WORD_START)

                # We may have ended up with a starting offset not in
                # this Zone, but in the same text area.  So...we'll
                # keep trodding backwards until we hit the zone where
                # the word really is.  We'll also stop if we hit the
                # beginning or we leave the current accessible text
                # object (remember that a single text area can be
                # represented by multiple zones).
                #
                recalcOffset = True
                while (endOffset == 0) or (startOffset < zone.startOffset):
                    oldZone = zone
                    moved = self.goPrevious(Context.ZONE, wrap)
                    if moved:
                        zone = self.lines[self.lineIndex][self.zoneIndex]
                        if zone.accessible != oldZone.accessible:
                            if zone.type == Zone.TEXT:
                                self.textOffset = max(0, zone.length - 1)
                            recalcOffset = False
                            break
                    else:
                        break
                if recalcOffset:
                    newOffset = startOffset - zone.startOffset
                    if not moved:
                        moved = newOffset != self.textOffset
                    self.textOffset = newOffset

                # Now check to see if we ended up on something empty.
                # If we did, then move on to the next word.
                #
                if moved:
                    [string, x, y, width, height] = \
                             self.getCurrent(Context.WORD)
                    if len(string.strip()) == 0:
                        self.goPrevious(type, wrap)
            else:
                # Othewise, we're currently at the beginning of the
                # current zone and we need to try the previous zone.
                #
                moved = self.goPrevious(Context.ZONE, wrap)
                if moved:
                    zone = self.lines[self.lineIndex][self.zoneIndex]
                    if zone.type == Zone.TEXT:
                        self.textOffset = zone.length
                        self.goPrevious(type, wrap)
                    [string, x, y, width, height] = \
                             self.getCurrent(Context.WORD)
                    if len(string.strip()) == 0:
                        self.goPrevious(type, wrap)            
        elif type == Context.LINE:
            if wrap & Context.WRAP_LINE:
                if self.lineIndex > 0:
                    self.lineIndex -= 1
                    self.zoneIndex  = 0
                    self.textOffset = 0
                    moved = True
                elif (wrap & Context.WRAP_TOP_BOTTOM) \
                     and (len(lines) != 1):
                    self.lineIndex  = len(self.lines) - 1
                    self.zoneIndex  = 0
                    self.textOffset = 0
                    moved = True
        else:
            raise Error, "Invalid type: %d" % type

        return moved


    def goNext(self, type=ZONE, wrap=True):
        """Moves this context's locus of interest to first character of
        the next type.

        Arguments:
        - type: one of ZONE, CHARACTER, WORD, LINE
        - wrap: if True, will cross boundaries, including top and
                bottom; if False, will stop on boundaries.
        """

        moved = False
        
        if type == Context.ZONE:
            if self.zoneIndex < (len(self.lines[self.lineIndex]) - 1):
                self.zoneIndex += 1
                self.textOffset = 0
                moved = True
            elif wrap & Context.WRAP_LINE:
                if self.lineIndex < (len(self.lines) - 1):
                    self.lineIndex += 1
                    self.zoneIndex  = 0
                    self.textOffset = 0
                    moved = True
                elif wrap & Context.WRAP_TOP_BOTTOM:
                    self.lineIndex  = 0
                    self.zoneIndex  = 0
                    self.textOffset = 0
                    moved = True
        elif type == Context.CHARACTER:
            # We can only do WORD and CHARACTER traversal with
            # Accessible_Text objects for now.  For all other
            # objects, we'll treat it like a Zone traversal.
            #
            zone = self.lines[self.lineIndex][self.zoneIndex]
            if zone.type != Zone.TEXT:
                moved = self.goNext(Context.ZONE, wrap)
                if moved:
                    zone = self.lines[self.lineIndex][self.zoneIndex]
                    if zone.length == 0:
                        self.goNext(type, wrap)
            else:
                if self.textOffset < max(0, zone.length - 1):
                    self.textOffset += 1
                    text = zone.accessible.text
                    [string, startOffset, endOffset] = text.getTextAtOffset(
                        zone.startOffset + self.textOffset,
                        core.Accessibility.TEXT_BOUNDARY_CHAR)
                    moved = True
                else:
                    moved = self.goNext(Context.ZONE, wrap)
                    if moved:
                        zone = self.lines[self.lineIndex][self.zoneIndex]
                        if zone.length == 0:
                            self.goNext(type, wrap)
        elif type == Context.WORD:
            # We can only do WORD and CHARACTER traversal with
            # Accessible_Text objects for now.  For all other
            # objects, we'll treat it like a Zone traversal.
            #
            # So...if we're on a non-text object, we jump to
            # the next object.  If it isn't a word, then we
            # go on from there...
            #
            zone = self.lines[self.lineIndex][self.zoneIndex]            
            if zone.type != Zone.TEXT:
                moved = self.goNext(Context.ZONE, wrap)
                if moved:                    
                    # We might move to a zone that begins with white
                    # space.  In this case, the
                    # TEXT_BOUNDARY_WORD_START will end up prior to
                    # this zone.  So...we need to take that into
                    # account. [[[TODO: WDW - I'm not really sure this
                    # is exactly what is going on there.  This algorithm
                    # is sloppy and could use some tightening.]]]
                    #
                    zone = self.lines[self.lineIndex][self.zoneIndex]
                    if zone.type == Zone.TEXT:   
                        text = zone.accessible.text
                        [string, startOffset, endOffset] = \
                                 text.getTextAtOffset(
                            zone.startOffset + self.textOffset,
                            core.Accessibility.TEXT_BOUNDARY_WORD_START)
                        if startOffset < zone.startOffset:
                            self.goNext(type, wrap)
                    [string, x, y, width, height] = \
                             self.getCurrent(Context.WORD)
                    if len(string.strip()) == 0:
                        self.goNext(type, wrap)
                return moved
            
            # We'll move the text offset to the beginning of the next
            # word.  We do this by getting the end offset of the
            # current word and setting our new offset to that.
            #
            text = zone.accessible.text
            [string, startOffset, endOffset] = text.getTextAtOffset(
                zone.startOffset + self.textOffset,
                core.Accessibility.TEXT_BOUNDARY_WORD_START)

            # We may have ended up with an offset not in this Zone,
            # but in the same text area.  So...we'll Keep on trodding
            # across zones until we get to where the end of the word
            # really is.  We'll also stop if we hit the end or we
            # leave the current accessible text object (remember that
            # a single text area can be represented by multiple
            # zones).
            #
            recalcOffset = True
            while endOffset >= (zone.startOffset + zone.length):
                oldZone = zone
                moved = self.goNext(Context.ZONE, wrap)
                if moved:
                    zone = self.lines[self.lineIndex][self.zoneIndex]
                    if zone.accessible != oldZone.accessible:
                        recalcOffset = False
                        break
                else:
                    break

            # If we are still in the same accessible text object then
            # we set our new textOffset to the appropriate value without
            # going beyond the end of the text object.
            #
            if recalcOffset:
                newOffset = endOffset - zone.startOffset
                if (newOffset != self.textOffset) \
                   and (newOffset < zone.length):
                    self.textOffset = newOffset
                    moved = True

            # Now check to see if we ended up on something empty.
            # If we did, then move on to the next word.
            #
            if moved:
                [string, x, y, width, height] = self.getCurrent(Context.WORD)
                if len(string.strip()) == 0:
                    self.goNext(type, wrap)
        elif type == Context.LINE:
            if wrap & Context.WRAP_LINE:
                if self.lineIndex < (len(self.lines) - 1):
                    self.lineIndex += 1
                    self.zoneIndex  = 0
                    self.textOffset = 0
                    moved = True
                elif (wrap & Context.WRAP_TOP_BOTTOM) \
                     and (self.lineIndex != 0):
                        self.lineIndex  = 0
                        self.zoneIndex  = 0
                        self.textOffset = 0
                        moved = True
        else:
            raise Error, "Invalid type: %d" % type

        return moved
    

    def goAbove(self, type=ZONE, wrap=True):
        """Moves this context's locus of interest to first character
        of the type that's closest to and above the current locus of
        interest.

        Arguments:
        - type: one of ZONE, CHARACTER, WORD, LINE
        - wrap: if True, will cross top/bottom boundaries; if False, will
                stop on top/bottom boundaries.

        Returns: [string, startOffset, endOffset, x, y, width, height]
        """

        if type == Context.LINE:
            return goPrevious(type, wrap)
        else:
            raise Error, "Invalid type: %d" % type


    def getBelow(self, type=ZONE, wrap=True):
        """Moves this context's locus of interest to the first
        character of the type that's closest to and below the current
        locus of interest.

        Arguments:
        - type: one of ZONE, CHARACTER, WORD, LINE
        - wrap: if True, will cross top/bottom boundaries; if False, will
                stop on top/bottom boundaries.

        Returns: [string, startOffset, endOffset, x, y, width, height]
        """

        if type == Context.LINE:
            return goNext(type, wrap)
        else:
            raise Error, "Invalid type: %d" % type

        
def visible(ax, ay, awidth, aheight,
            bx, by, bwidth, bheight):
    """Returns true if any portion of region 'a' is in region 'b'
    """
    highestBottom = min(ay + aheight, by + bheight)    
    lowestTop = max(ay, by)

    leftMostRightEdge = min(ax + awidth, bx + bwidth)
    rightMostLeftEdge = max(ax, bx)

    if (lowestTop < highestBottom) \
       and (rightMostLeftEdge < leftMostRightEdge):
        return True
    elif (aheight == 0):
        if (awidth == 0):
            return (lowestTop == highestBottom) \
                   and (leftMostRightEdge == rightMostLeftEdge)
        else:
            return leftMostRightEdge < rightMostLeftEdge
    elif (awidth == 0):
        return (lowestTop < highestBottom)

        
def clip(ax, ay, awidth, aheight,
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


def getZonesFromAccessible(accessible, cliprect):
    """Returns a list of Zones for the given accessible.

    Arguments:
    - accessible: the accessible
    - cliprect: the extents that the Zones must fit inside.    
    """

    # Get the component extents in screen coordinates.
    #
    extents = accessible.component.getExtents(0)
    
    if not visible(extents.x, extents.y, 
                   extents.width, extents.height,
                   cliprect.x, cliprect.y,
                   cliprect.width, cliprect.height):
        return []
    
    zones = []
    
    if accessible.text:
        text = accessible.text
        length = text.characterCount

        offset = 0
        while offset < length:
            
            [string, startOffset, endOffset] = text.getTextAtOffset(
                offset,
                core.Accessibility.TEXT_BOUNDARY_LINE_START)

            [x, y, width, height] = text.getRangeExtents(startOffset, 
                                                         endOffset, 
                                                         0)

            # Sometimes we get the trailing line-feed -- remove it
            #
            if string[-1:] == "\n":
                string = string[:-1]
                offset = endOffset
            else:
                offset = endOffset + 1
            
            if visible(x, y, width, height, 
                       cliprect.x, cliprect.y, 
                       cliprect.width, cliprect.height):
                   
                clipping = clip(x, y, width, height,
                                cliprect.x, cliprect.y,
                                cliprect.width, cliprect.height)
                
                zones.append(Zone(accessible,
                                  Zone.TEXT,
                                  string, 
                                  clipping[0],
                                  clipping[1],
                                  clipping[2],
                                  clipping[3],
                                  startOffset))
                
            elif len(zones):
                # We'll break out of searching all the text - the idea
                # here is that we'll at least try to optimize for when
                # we gone below the visible clipping area.
                #
                # [[[TODO: WDW - would be nice to optimize this better.
                # for example, perhaps we can assume the caret will always
                # be visible, and we can start our text search from there.]]]
                #
                break
        
        # We might have a zero length text area.
        #
        if len(zones) == 0:
            zones.append(Zone(accessible,
                              Zone.TEXT,
                              "",
                              extents.x, extents.y,
                              extents.width, extents.height,
                              0))

    # We really want the accessible text information.  But, if we have
    # and image, and it has a description, we can fall back on it.
    #
    if (len(zones) == 0) \
           and accessible.image \
           and accessible.image.imageDescription \
           and len(accessible.image.imageDescription):
        
        [x, y] = accessible.image.getImagePosition(0)
        [width, height] = accessible.image.getImageSize()
        
        if (width != 0) and (height != 0) \
               and visible(x, y, width, height,
                           cliprect.x, cliprect.y, 
                           cliprect.width, cliprect.height):
                   
            clipping = clip(x, y, width, height,
                            cliprect.x, cliprect.y,
                            cliprect.width, cliprect.height)
                
            zones.append(Zone(accessible, 
                              Zone.IMAGE,
                              accessible.image.imageDescription, 
                              clipping[0],
                              clipping[1],
                              clipping[2],
                              clipping[3],
                              0))

    # Well...darn.  Maybe we didn't get anything of use, but we certainly
    # know there's something there.  If that's the case, we'll just use
    # the component extents and the name of the accessible.
    #
    if len(zones) == 0:
        clipping = clip(extents.x, extents.y,
                        extents.width, extents.height,
                        cliprect.x, cliprect.y,
                        cliprect.width, cliprect.height)
        zones.append(Zone(accessible,
                          Zone.COMPONENT,
                          accessible.name,
                          clipping[0],
                          clipping[1],
                          clipping[2],
                          clipping[3],
                          0))
    
    return zones


def getShowingZones(root):
    """Returns a list of all interesting, non-intersecting, regions
    that are drawn on the screen.  Each element of the list is the
    Accessible object associated with a given region.  The term
    'zone' here is inherited from OCR algorithms and techniques.
    
    The objects are returned in no particular order.

    Arguments:
    - root: the Accessible object to traverse

    Returns: a list of objects under the specified object
    """

    if root is None:
        return []
    
    # If we're at a leaf node, then we've got a good one on our hands.
    #
    if root.childCount <= 0:
        return getZonesFromAccessible(root, root.extents)

    # We'll stop at various objects because, while they do have
    # children, we logically think of them as one region on the
    # screen.  [[[TODO: WDW - HACK stopping at menu bars for now
    # because their menu items tell us they are showing even though
    # they are not showing.  Until I can figure out a reliable way to
    # get past these lies, I'm going to ignore them.]]]
    #
    if (root.parent and (root.parent.role == rolenames.ROLE_MENU_BAR)) \
       or (root.role == rolenames.ROLE_COMBO_BOX):
        return getZonesFromAccessible(root, root.extents)
    
    # Otherwise, dig deeper.
    #
    objlist = []

    # We'll include page tabs: while they are parents, their extents do
    # not contain their children.
    #
    if root.role == rolenames.ROLE_PAGE_TAB:
        objlist.extend(getZonesFromAccessible(root, root.extents))
        
    # [[[TODO: WDW - probably want to do something a little smarter
    # for parents that manage gazillions of descendants.]]]
    #
    i = 0
    while i < root.childCount:
        child = root.child(i)
        if child == root:
            debug.println(debug.LEVEL_SEVERE,
                          indent + "  " + "WARNING CHILD == PARENT!!!")
        elif child is None:
            debug.println(debug.LEVEL_SEVERE,
                          indent + "  " + "WARNING CHILD IS NONE!!!")
        elif child.parent != root:
            debug.println(debug.LEVEL_SEVERE,
                          indent + "  " + "WARNING CHILD.PARENT != PARENT!!!")
        elif child.state.count(core.Accessibility.STATE_SHOWING):    
            objlist.extend(getShowingZones(child))
        i += 1
        
    return objlist


def clusterZonesByLine(zones):
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
    i = 0
    while i < numZones:
        j = 0
        while j < (numZones - 1 - i):
            a = zones[j]
            b = zones[j + 1]
            if b.y < a.y:
                zones[j] = b
                zones[j + 1] = a
            j += 1
        i += 1

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
                    i += 1
                lineCluster.insert(i, clusterCandidate)
                addedToCluster = True
                break                
        if not addedToCluster:
            lineClusters.append([clusterCandidate])

    return lineClusters
