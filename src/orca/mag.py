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

"""Manages the magnifier for orca.  [[[TODO: WDW - this is very very early
in development.  One might even say it is pre-prototype.]]]
"""

import core
from core import bonobo
import CORBA
import GNOME
import time

# If True, this module has been initialized.
#
initialized = False

# The Magnifier
#
magnifier = None

# The GNOME.Magnifier.RectBounds, in unzoomed system coordinates, of the
# display that is being magnified.
#
sourceDisplayBounds = None

# The width and height, in unzoomed system coordinates of the rectangle that,
# when magnified, will fill the viewport of the magnifier - this needs to be
# sync'd with the magnification factors of the zoom area.
#
roiWidth = 0
roiHeight = 0

# Minimum values for the center of the ROI
#
minROIX = 0
maxROIX = 0
minROIY = 0
maxROIY = 0

# The current region of interest.
#
roi = None

# The ZoomRegion we care about [[[TODO: WDW - we should be more careful about
# just what we're doing here.  The Magnifier allows more than one ZoomRegion
# and we're just picking up the first one.]]]
#
zoomer = None

# The time of the last mouse event.
#
lastMouseEventTime = time.time()


def magnifyAccessible(acc):
    """Sets the region of interest to the upper left of the given
    accessible, if it implements the Component interface.  Otherwise,
    does nothing.

    Arguments:
    - acc: the accessible
    """

    global initialized
    global roi
    global lastMouseEventTime
    
    if not initialized:
        return

    extents = acc.extents
    if extents is None:
        return

    # Avoid jerking the display around if the mouse is what ended up causing
    # this event.  We guess this by seeing if this request has come in within
    # a close period of time.  [[[TODO: WDW - this is a hack and really
    # doesn't belong here.  Plus, the delta probably should be adjustable.]]]
    #
    currentTime = time.time()
    if (currentTime - lastMouseEventTime) < 0.2: # 200 milliseconds
        return
    
    # Determine if the accessible is partially to the left, right,
    # above, or below the current region of interest (ROI).
    #
    left = extents.x < roi.x1
    right = (extents.x + extents.width) > roi.x2
    above = extents.y < roi.y1
    below = (extents.y + extents.height) > roi.y2

    # If it is already completely showing, do nothing.
    #
    visibleX = not (left or right)
    visibleY = not (above or below)

    if visibleX and visibleY:
        return
    
    # The algorithm is devised to move the ROI as little as possible, yet
    # favor the top left side of the object [[[TODO: WDW - the left/right
    # top/bottom favoring should probably depend upon the locale.  Also,
    # I had the notion of including a floating point snap factor between
    # 0.0 and 1.0 that would determine how to position the object in the
    # window relative to the ROI edges.  A snap factor of -1 would mean to
    # snap to the closest edge.  A snap factor of 0.0 would snap to the
    # left most or top most edge, a snap factor of 1.0 would snap to the
    # right most or bottom most edge.  Any number in between would divide
    # the two.]]]
    #
    x1 = roi.x1
    x2 = roi.x2 
    y1 = roi.y1
    y2 = roi.y2
    
    if left:
        x1 = extents.x
        x2 = x1 + roiWidth
    elif right:
        if extents.width > roiWidth:
            x1 = extents.x
            x2 = x1 + roiWidth
        else:
            x2 = extents.x + extents.width
            x1 = x2 - roiWidth
        
    if above:
        y1 = extents.y
        y2 = y1 + roiHeight
    elif below:
        if extents.height > roiHeight:
            y1 = extents.y
            y2 = y1 + roiHeight
        else:
            y2 = extents.y + extents.height
            y1 = y2 - roiHeight
        
    setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))

    
def setROICenter(x, y):
    """Centers the region of interest around the given point.

    Arguments:
    - x: integer in unzoomed system coordinates representing x component
    - y: integer in unzoomed system coordinates representing y component
    """

    if not initialized:
        return

    if x < minROIX:
        x = minROIX
    elif x > maxROIX:
        x = maxROIX
        
    if y < minROIY:
        y = minROIY
    elif y > maxROIY:
        y = maxROIY

    x1 = x - (roiWidth / 2)
    y1 = y - (roiHeight / 2)

    x2 = x1 + roiWidth
    y2 = y1 + roiHeight

    setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))


def setROI(rect):
    """Sets the region of interest.

    Arguments:
    - rect: A GNOME.Magnifier.RectBounds object.
    """
    
    global roi
    roi = rect
    zoomer.setROI(roi)
    zoomer.markDirty(roi)  # [[[TODO: WDW - for some reason, this seems
                           # necessary.]]]


# Used for tracking the pointer.
#
def onMouseEvent(e):
    """
    Arguments:
    - e: at-spi event from the at-api registry
    """
    global lastMouseEventTime
    lastMouseEventTime = time.time()
    setROICenter(e.detail1, e.detail2)

    
def init():
    """Initializes the magnifier, bringing the magnifier up on the
    display.
    
    Returns True if the initialization procedure was run or False if this
    module has already been initialized.
    """
    
    global initialized
    global magnifier
    global zoomer
    global sourceDisplayBounds
    global roiWidth
    global roiHeight
    global minROIX
    global minROIY
    global maxROIX
    global maxROIY
    
    if initialized:
        return False

    magnifier = bonobo.get_object("OAFIID:GNOME_Magnifier_Magnifier:0.9",
                                  "GNOME/Magnifier/Magnifier")

    pbag = magnifier.getProperties()
    sourceDisplayBounds = pbag.getValue("source-display-bounds").value()

    #print "MAGNIFIER PROPERTIES:"
    #pbag = magnifier.getProperties ()
    #slots = pbag.getKeys ("")
    #print "Available slots: ", pbag.getKeys("")
    #for slot in slots:
    #    print
    #    print "About '%(slot)s':" %vars()
    #    print "Doc Title:", pbag.getDocTitle(slot)
    #    print "Type:", pbag.getType(slot)
    #    print "Default value:", pbag.getDefault(slot).value()
    #    print "Current value:", pbag.getValue(slot).value()

    #print
    #print "ZOOMER PROPERTIES:"
    #zoomers = magnifier.getZoomRegions ()    
    #for zoomer in zoomers:
    #    print zoomer
    #    pbag = zoomer.getProperties ()
    #    slots = pbag.getKeys ("")
    #    print "Available slots: ", pbag.getKeys("")
    #    for slot in slots:
    #        print
    #        print "About '%(slot)s':" %vars()
    #        print "Doc Title:", pbag.getDocTitle(slot)
    #        print "Type:", pbag.getType(slot)
    #        print "Default value:", pbag.getDefault(slot).value()
    #        print "Current value:", pbag.getValue(slot).value()
    #    print
    #    bonobo.pbclient_set_boolean(pbag, "is-managed", True)
    #    managed = pbag.getValue("is-managed").value()
    #    print "Managed:  ", managed

    zoomers =  magnifier.getZoomRegions()
    zoomer = zoomers[0]

    pbag = zoomer.getProperties()
    viewport = pbag.getValue("viewport").value()
    magx = pbag.getValue("mag-factor-x").value()
    magy = pbag.getValue("mag-factor-y").value()

    roiWidth = (viewport.x2 - viewport.x1) / magx
    roiHeight = (viewport.y2 - viewport.y1) / magy

    minROIX = sourceDisplayBounds.x1 + (roiWidth / 2)
    minROIY = sourceDisplayBounds.y1 + (roiHeight / 2)

    maxROIX = sourceDisplayBounds.x2 - (roiWidth / 2)
    maxROIY = sourceDisplayBounds.y2 - (roiHeight / 2)

    #pbag.setValue("viewport", CORBA.Any(CORBA.TypeCode(viewport.typecode().repo_id),GNOME.Magnifier.RectBounds(0,0,512,780)))
    #zoomer.moveResize(GNOME.Magnifier.RectBounds(256,256,600,600))
    #zoomer.setMagFactor(1.0, 1.0)

    core.registerEventListener(onMouseEvent, "mouse:abs")
    
    initialized = True

    # Zoom to the upper left corner of the display for now.
    #
    setROICenter(0, 0)

    return True


def shutdown():
    """Shuts down the magnifier module.
    Returns True if the shutdown procedure was run or False if this
    module has not been initialized.
    """
    
    global initialized
    global magnifier

    if not initialized:
        return False

    magnifier.clearAllZoomRegions()
    magnifier.dispose()
    magnifier = None
    
    initialized = False
    
    return True
