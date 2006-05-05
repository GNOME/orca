# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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
in development.  One might even say it is pre-prototype.  Magnification
has also been disabled for now - logged as bugzilla bug 319643.]]]
"""

import bonobo
import time

import atspi
import debug
import settings

_magnifierAvailable = False

try:
    atspi.ORBit.load_typelib('GNOME_Magnifier')
    import GNOME.Magnifier
    _magnifierAvailable = True
except:
    pass

import time

# If True, this module has been initialized.
#
_initialized = False

# The Magnifier
#
_magnifier = None

# The GNOME.Magnifier.RectBounds, in unzoomed system coordinates, of the
# display that is being magnified.
#
_sourceDisplayBounds = None

# The width and height, in unzoomed system coordinates of the rectangle that,
# when magnified, will fill the viewport of the magnifier - this needs to be
# sync'd with the magnification factors of the zoom area.
#
_roiWidth = 0
_roiHeight = 0

# Minimum values for the center of the ROI
#
_minROIX = 0
_maxROIX = 0
_minROIY = 0
_maxROIY = 0

# The current region of interest.
#
_roi = None

# The ZoomRegion we care about [[[TODO: WDW - we should be more careful about
# just what we're doing here.  The Magnifier allows more than one ZoomRegion
# and we're just picking up the first one.]]]
#
_zoomer = None

# The time of the last mouse event.
#
_lastMouseEventTime = time.time()

def magnifyAccessible(acc):
    """Sets the region of interest to the upper left of the given
    accessible, if it implements the Component interface.  Otherwise,
    does nothing.

    Arguments:
    - acc: the accessible
    """

    if not _initialized:
        return

    extents = acc.extents
    if not extents:
        return

    [x, y, width, height] = [extents.x, extents.y, extents.width, extents.height]
    
    if acc.text:
        offset = acc.text.caretOffset
        if offset >= 0:
            [x, y, width, height] = acc.text.getCharacterExtents(offset,
                                                                 0) # coord type screen
            
    # Avoid jerking the display around if the mouse is what ended up causing
    # this event.  We guess this by seeing if this request has come in within
    # a close period of time.  [[[TODO: WDW - this is a hack and really
    # doesn't belong here.  Plus, the delta probably should be adjustable.]]]
    #
    currentTime = time.time()
    if (currentTime - _lastMouseEventTime) < 0.2: # 200 milliseconds
        return

    # Determine if the accessible is partially to the left, right,
    # above, or below the current region of interest (ROI).
    #
    left = x < _roi.x1
    right = (x + width) > _roi.x2
    above = y < _roi.y1
    below = (y + height) > _roi.y2

    # If it is already completely showing, do nothing.
    #
    visibleX = not(left or right)
    visibleY = not(above or below)

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
    x1 = _roi.x1
    x2 = _roi.x2
    y1 = _roi.y1
    y2 = _roi.y2

    if left:
        x1 = x
        x2 = x1 + _roiWidth
    elif right:
        if width > _roiWidth:
            x1 = x
            x2 = x1 + _roiWidth
        else:
            x2 = x + width
            x1 = x2 - _roiWidth

    if above:
        y1 = y
        y2 = y1 + _roiHeight
    elif below:
        if height > _roiHeight:
            y1 = y
            y2 = y1 + _roiHeight
        else:
            y2 = y + height
            y1 = y2 - _roiHeight

    __setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))

def __setROICenter(x, y):
    """Centers the region of interest around the given point.

    Arguments:
    - x: integer in unzoomed system coordinates representing x component
    - y: integer in unzoomed system coordinates representing y component
    """

    if not _initialized:
        return

    if x < _minROIX:
        x = _minROIX
    elif x > _maxROIX:
        x = _maxROIX

    if y < _minROIY:
        y = _minROIY
    elif y > _maxROIY:
        y = _maxROIY

    x1 = x - (_roiWidth / 2)
    y1 = y - (_roiHeight / 2)

    x2 = x1 + _roiWidth
    y2 = y1 + _roiHeight

    __setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))

def __setROI(rect):
    """Sets the region of interest.

    Arguments:
    - rect: A GNOME.Magnifier.RectBounds object.
    """

    global _roi

    _roi = rect
    _zoomer.setROI(_roi)
    _zoomer.markDirty(_roi)  # [[[TODO: WDW - for some reason, this seems
                             # necessary.]]]

# Used for tracking the pointer.
#
def onMouseEvent(e):
    """
    Arguments:
    - e: at-spi event from the at-api registry
    """

    global _lastMouseEventTime

    _lastMouseEventTime = time.time()
    __setROICenter(e.detail1, e.detail2)

def __getValueText(slot, value):
    valueText = ""
    if slot == "cursor-hotspot":
        valueText = "(%d, %d)" % (value.x, value.y)
    elif slot == "source-display-bounds":
        valueText = "(%d, %d),(%d, %d)" \
                    % (value.x1, value.y1, value.x2, value.y2)
    elif slot == "target-display-bounds":
        valueText = "(%d, %d),(%d, %d)" \
                    % (value.x1, value.y1, value.x2, value.y2)
    elif slot == "viewport":
        valueText = "(%d, %d),(%d, %d)" \
                    % (value.x1, value.y1, value.x2, value.y2)
    return valueText

def __dumpPropertyBag(obj):
    pbag = obj.getProperties()
    slots = pbag.getKeys("")
    print "  Available slots: ", pbag.getKeys("")
    for slot in slots:
        print
        print "    About '%s':" % slot
        print "    Doc Title:", pbag.getDocTitle(slot)
        print "    Type:", pbag.getType(slot)
        value = pbag.getDefault(slot).value()
        print "    Default value:", value, __getValueText(slot, value)
        value = pbag.getValue(slot).value()
        print "    Current value:", value, __getValueText(slot, value)
        print

def applySettings():
    """Looks at the user settings and applies them to the magnifier."""

    global _roiWidth
    global _roiHeight
    global _minROIX
    global _minROIY
    global _maxROIX
    global _maxROIY

    #bonobo.pbclient_set_string
    #bonobo.pbclient_set_short
    #bonobo.pbclient_set_ushort
    #bonobo.pbclient_set_long
    #bonobo.pbclient_set_ulong
    #bonobo.pbclient_set_float
    #bonobo.pbclient_set_double
    #bonobo.pbclient_set_boolean
    #bonobo.pbclient_set_char
    #bonobo.pbclient_set_value
    
    magnifierPBag = _magnifier.getProperties()
    zoomerPBag = _zoomer.getProperties()

    #try:
    #    tdb = magnifierPBag.getValue("target-display-bounds").value()
    #    magnifierPBag.setValue(
    #        "target-display-bounds",
    #        atspi.ORBit.CORBA.Any(
    #            atspi.ORBit.CORBA.TypeCode(
    #                tdb.__typecode__.repo_id),
    #            GNOME.Magnifier.RectBounds(0, 0, 512, 768)))
    #
    #     sdb = magnifier.getValue("source-display-bounds").value()
    #    magnifier.setValue(
    #        "source-display-bounds",
    #        atspi.ORBit.CORBA.Any(
    #            atspi.ORBit.CORBA.TypeCode(
    #                sdb.__typecode__.repo_id),
    #            GNOME.Magnifier.RectBounds(512,0,1024,768)))
    #
    #    viewport = zoomerPBag.getValue("viewport").value()
    #    zoomerPBag.setValue(
    #        "viewport",
    #        atspi.ORBit.CORBA.Any(
    #            atspi.ORBit.CORBA.TypeCode(
    #                viewport.__typecode__.repo_id),
    #            GNOME.Magnifier.RectBounds(0, 0, 512, 768)))
    #except:
    #    debug.printException(debug.LEVEL_OFF)
    #

    if settings.enableMagCursorExplicitSize:
        bonobo.pbclient_set_long(
            magnifierPBag, "cursor-size", settings.magCursorSize)
    else:
        bonobo.pbclient_set_long(
            magnifierPBag, "cursor-size", 0)

    color = long(settings.magCursorColor.replace("#", "0x", 1), 0)

    bonobo.pbclient_set_long(
        magnifierPBag, "cursor-color", color)

    bonobo.pbclient_set_long(
        magnifierPBag, "crosswire-color", color)
        
    if settings.enableMagCrossHair:
        bonobo.pbclient_set_long(
            magnifierPBag, "crosswire-size", settings.magCrossHairSize)
    else:
        bonobo.pbclient_set_long(
            magnifierPBag, "crosswire-size", 0)
        
    bonobo.pbclient_set_boolean(
        magnifierPBag, "crosswire-clip", settings.enableMagCrossHairClip)

    _zoomer.setMagFactor(settings.magZoomFactor, settings.magZoomFactor)
    
    bonobo.pbclient_set_boolean(
        zoomerPBag, "inverse-video", settings.enableMagZoomerColorInversion)

    # "smoothing-type"

    bonobo.pbclient_set_boolean(zoomerPBag, "is-managed", True)
    viewport = zoomerPBag.getValue("viewport").value()
    
    magx = zoomerPBag.getValue("mag-factor-x").value()
    magy = zoomerPBag.getValue("mag-factor-y").value()

    _roiWidth = (viewport.x2 - viewport.x1) / magx
    _roiHeight = (viewport.y2 - viewport.y1) / magy

    _minROIX = _sourceDisplayBounds.x1 + (_roiWidth / 2)
    _minROIY = _sourceDisplayBounds.y1 + (_roiHeight / 2)

    _maxROIX = _sourceDisplayBounds.x2 - (_roiWidth / 2)
    _maxROIY = _sourceDisplayBounds.y2 - (_roiHeight / 2)

def init():
    """Initializes the magnifier, bringing the magnifier up on the
    display.

    Returns True if the initialization procedure was run or False if this
    module has already been initialized.
    """

    global _initialized
    global _magnifier
    global _sourceDisplayBounds
    global _zoomer

    if not _magnifierAvailable:
        return False
    
    if _initialized:
        return False

    _magnifier = bonobo.get_object("OAFIID:GNOME_Magnifier_Magnifier:0.9",
                                   "GNOME/Magnifier/Magnifier")

    magnifierPBag = _magnifier.getProperties()
    _sourceDisplayBounds = magnifierPBag.getValue(
        "source-display-bounds").value()
    _magnifier.clearAllZoomRegions()
    _zoomer = _magnifier.createZoomRegion(
        settings.magZoomFactor, settings.magZoomFactor,
        GNOME.Magnifier.RectBounds(0,                              # x1
                                   0,                              # y1
                                   -1,                             # x2
                                   -1),                            # y2
        GNOME.Magnifier.RectBounds(0,                              # x1
                                   0,                              # y1
                                   _sourceDisplayBounds.x2,        # x2
                                   _sourceDisplayBounds.y2))       # y2

    applySettings()
    
    #print "MAGNIFIER PROPERTIES:", _magnifier
    #__dumpPropertyBag(_magnifier)
    #print "ZOOMER PROPERTIES:", _zoomer
    #__dumpPropertyBag(_zoomer)

    atspi.Registry().registerEventListener(onMouseEvent, "mouse:abs")
    
    _initialized = True

    # Zoom to the upper left corner of the display for now.
    #
    __setROICenter(0, 0)

    return True

def shutdown():
    """Shuts down the magnifier module.
    Returns True if the shutdown procedure was run or False if this
    module has not been initialized.
    """

    global _initialized
    global _magnifier

    if not _magnifierAvailable:
        return False
    
    if not _initialized:
        return False

    atspi.Registry().deregisterEventListener(onMouseEvent,"mouse:abs")
    
    _magnifier.clearAllZoomRegions()
    _magnifier.dispose()
    _magnifier = None

    _initialized = False

    return True
