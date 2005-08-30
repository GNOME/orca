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

ZONE_TYPE_COMPONENT = 0
ZONE_TYPE_TEXT      = 1
ZONE_TYPE_IMAGE     = 2

class Zone:
    """Represents text that is a portion of a single horizontal line."""

    def __init__(self, 
                 accessible,
                 type,
                 string, 
                 x, y, 
                 width, height, 
                 startOffset, endOffset):
        """Creates a new Zone, which is a horizontal region of text.

        Arguments:
        - accessible: the Accessible associated with this Zone
        - string: the string being displayed for this Zone
        - type: one of ZONE_TYPE_COMPONENT, ZONE_TYPE_TEXT, etc.
        - extents: x, y, width, height: if the accessible implements
                   Accessibility_Text, these will be the range extents
                   for startOffset and endOffset.  If the accessible
                   does not implement Accessibility_Text, then these will
                   be the extents of the Accessibility_Component.
        - startOffset: index into Accessibility_Text for start of line
        - endOffset: index into Accessibility_Text for end of line
        """
        
        self.accessible = accessible
        self.type = type
        self.string = string
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.startOffset = startOffset
        self.endOffset = endOffset

        
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
                                  ZONE_TYPE_TEXT,
                                  string, 
                                  clipping[0],
                                  clipping[1],
                                  clipping[2],
                                  clipping[3],
                                  startOffset, endOffset))
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
                              ZONE_TYPE_TEXT,
                              "",
                              extents.x, extents.y,
                              extents.width, extents.height,
                              0, 0))

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
                              ZONE_TYPE_IMAGE,
                              accessible.image.imageDescription, 
                              clipping[0],
                              clipping[1],
                              clipping[2],
                              clipping[3],
                              0, len(accessible.image.imageDescription)))

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
                          ZONE_TYPE_COMPONENT,
                          accessible.name,
                          clipping[0],
                          clipping[1],
                          clipping[2],
                          clipping[3],
                          0,
                          len(accessible.name)))
    
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
