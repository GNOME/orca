# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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

"""Manages the magnifier for orca.  [[[TODO: WDW - this is very very
early in development.  One might even say it is pre-prototype.]]]"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import bonobo
try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk
except:
    pass
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

# The width and height, in unzoomed system coordinates of the rectangle that,
# when magnified, will fill the viewport of the magnifier - this needs to be
# sync'd with the magnification factors of the zoom area.
#
_roiWidth = 0
_roiHeight = 0

# Minimum/maximum values for the center of the ROI
# in source screen coordinates.
#
_minROIX = 0
_maxROIX = 0
_minROIY = 0
_maxROIY = 0

# The current region of interest.
#
# A GNOME.Magnifier.RectBounds object which consists of x1, y1, x2, y2 values
# that are in source screen coordinates.
#
_roi = None

# The area of the source display that is not covered by the magnifier.
#
# A GNOME.Magnifier.RectBounds object which consists of x1, y1, x2, y2 values
# that are in source screen coordinates.  If the COMPOSITE support is enabled
# in gnome-mag, then this typically becomes the entire source screen.  If it
# it not enabled, however, and the target and source displays are the same,
# this ends up becoming the portion of the screen that is not covered by the
# magnifier.
#
_sourceDisplayBounds = None

# The area on the target display where we are placing the magnifier.
#
# A GNOME.Magnifier.RectBounds object which consists of x1, y1, x2, y2 values
# that are in target screen coordinates.
#
_targetDisplayBounds = None

# The ZoomRegion we care about.  We only use one ZoomRegion and we
# make it occupy the whole magnifier.
#
_zoomer = None

# The time of the last mouse event.
#
_lastMouseEventTime = time.time()

# If True, we're using gnome-mag >= 0.13.1 that allows us to control
# where to draw the cursor and crosswires.
#
_pollMouseDisabled = False

# Whether or not composite is being used.
#
_fullScreenCapable = True

def __setROI(rect):
    """Sets the region of interest.

    Arguments:
    - rect: A GNOME.Magnifier.RectBounds object.
    """

    global _roi

    debug.println(debug.LEVEL_ALL, "mag.py:__setROI: (%d, %d), (%d, %d)" \
                  % (rect.x1, rect.y1, rect.x2, rect.y2))

    _roi = rect

    _zoomer.setROI(_roi)
    _zoomer.markDirty(_roi)  # [[[TODO: WDW - for some reason, this seems
                             # necessary.]]]
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

def __setROIPush(x, y):
    """Nudges the ROI if the pointer bumps into the edge of it.  The point
    given is assumed to be the point where the mouse pointer is.

    Arguments:
    - x: integer in unzoomed system coordinates representing x component
    - y: integer in unzoomed system coordinates representing y component
    """

    needNewROI = False
    newROI = GNOME.Magnifier.RectBounds(_roi.x1, _roi.y1, _roi.x2, _roi.y2)
    if x < _roi.x1:
        needNewROI = True
        newROI.x1 = x
        newROI.x2 = x + _roiWidth
    elif x > _roi.x2:
        needNewROI = True
        newROI.x2 = x
        newROI.x1 = x - _roiWidth
    if y < _roi.y1:
        needNewROI = True
        newROI.y1 = y
        newROI.y2 = y + _roiHeight
    elif y > _roi.y2:
        needNewROI = True
        newROI.y2 = y
        newROI.y1 = y - _roiHeight

    # Well...we'll always update the ROI so the new gnome-mag API
    # will redraw the crosswires for us.
    #
    #if needNewROI:
    if True:
        __setROI(newROI)

def __setROIProportional(x, y):
    """Positions the ROI proportionally to where the pointer is on the screen.

    Arguments:
    - x: integer in unzoomed system coordinates representing x component
    - y: integer in unzoomed system coordinates representing y component
    """

    if not _initialized:
        return

    if not _sourceDisplayBounds:
        __setROICenter(x, y)
    else:
        halfScreenWidth  = (_sourceDisplayBounds.x2 \
                            - _sourceDisplayBounds.x1) / 2.0
        halfScreenHeight = (_sourceDisplayBounds.y2 \
                            - _sourceDisplayBounds.y1) / 2.0

        proportionX = (halfScreenWidth  - x) / halfScreenWidth
        proportionY = (halfScreenHeight - y) / halfScreenHeight

        centerX = x + int(proportionX * _roiWidth  / 2.0)
        centerY = y + int(proportionY * _roiHeight / 2.0)

        __setROICenter(centerX, centerY)

# Used for tracking the pointer.
#
def __onMouseEvent(e):
    """
    Arguments:
    - e: at-spi event from the at-api registry
    """

    global _lastMouseEventTime

    _lastMouseEventTime = time.time()

    [x, y] = [e.detail1, e.detail2]

    # If True, we're using gnome-mag >= 0.13.1 that allows us to
    # control where to draw the cursor and crosswires.
    #
    if _pollMouseDisabled:
        _zoomer.setPointerPos(x, y)

    if settings.magMouseTrackingMode == settings.MAG_MOUSE_TRACKING_MODE_PUSH:
        __setROIPush(x, y)
    elif settings.magMouseTrackingMode == settings.MAG_MOUSE_TRACKING_MODE_PROPORTIONAL:
        __setROIProportional(x, y)
    elif settings.magMouseTrackingMode == settings.MAG_MOUSE_TRACKING_MODE_CENTERED:
        __setROICenter(x, y)

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
        # These crash the magnifier since it doesn't know how to marshall
        # them to us.
        #
        if slot in ["cursor-set", "smoothing-type"]:
            continue
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

    global _sourceDisplayBounds
    global _targetDisplayBounds
    global _zoomer
    global _roiWidth
    global _roiHeight
    global _minROIX
    global _minROIY
    global _maxROIX
    global _maxROIY
    global _pollMouseDisabled
    global _fullScreenCapable

    ########################################################################
    #                                                                      #
    # First set up the magnifier properties.                               #
    #                                                                      #
    ########################################################################

    _magnifier.clearAllZoomRegions()

    # Define where the magnifier will live.
    #
    try:
        _magnifier.TargetDisplay = settings.magTargetDisplay
    except:
        pass

    # Define what will be magnified.
    #
    try:
        _magnifier.SourceDisplay = settings.magSourceDisplay
    except:
        pass

    # Find out where the user wants to place the target display.
    #
    prefLeft   = settings.magZoomerLeft
    prefTop    = settings.magZoomerTop
    prefRight  = settings.magZoomerRight
    prefBottom = settings.magZoomerBottom
    updateTarget = True

    # Find out if we're using composite.
    #
    try:
        _fullScreenCapable = _magnifier.fullScreenCapable()
    except:
        debug.printException(debug.LEVEL_WARNING)

    magnifierPBag = _magnifier.getProperties()
    
    # If we're not using composite, bad things will happen if we allow the
    # target display to occupy more than 50% of the full screen.  Also, if
    # it occupies the same space as something that should be magnified (e.g.
    # the Applications menu), that item will not be magnified. Therefore,
    # we're going to prefer the right half of the screen for the target
    # display -- unless gnome-mag is already running and not in "full screen"
    # mode.
    #
    if not _fullScreenCapable \
       and _magnifier.SourceDisplay == _magnifier.TargetDisplay:
        # At this point, the target display bounds have not been set. if they
        # are all 0, then we know that gnome-mag isn't already running.
        #
        magAlreadyRunning = False
        tdb = magnifierPBag.getValue("target-display-bounds").value()
        if tdb.x1 or tdb.x2 or tdb.y1 or tdb.y2:
            magAlreadyRunning = True

        # At this point, because we haven't set the target display bounds,
        # gnome-mag has not modified the source display bounds. Therefore,
        # we can use the current source display bounds to get the
        # dimensions of the full screen -- assuming gnome-mag has not
        # already been launched with a split screen. Comparing the values
        # of the source and target display bounds lets us know if gnome-mag
        # has been started in "full screen" mode.
        #
        sdb = magnifierPBag.getValue("source-display-bounds").value()
        magFullScreen = magAlreadyRunning \
                        and (tdb.x1 == sdb.x1) and (tdb.x2 == sdb.x2) \
                        and (tdb.y1 == sdb.y1) and (tdb.y2 == sdb.y2)

        sourceArea = (sdb.x2 - sdb.x1) * (sdb.y2 - sdb.y1)
        prefArea = (prefRight - prefLeft) * (prefBottom - prefTop)
        if prefArea > sourceArea/2:
            debug.println(
                debug.LEVEL_WARNING,
                "Composite is not being used. The preferred target area is\n"\
                "greater than 50% of the source area.  These settings can\n"\
                "render the contents of the screen inaccessible.")
            if not magAlreadyRunning or magFullScreen:
                debug.println(
                    debug.LEVEL_WARNING,
                    "Setting the target display to the screen's right half.")
                prefRight  = sdb.x2
                prefLeft   = sdb.x2/2
                prefTop    = sdb.y1
                prefBottom = sdb.y2
            else:
                updateTarget = False
                debug.println(
                    debug.LEVEL_WARNING,
                    "Gnome-mag is already running.  Using those settings.")

    # Now, tell the magnifier where we want it to live on the target display.
    # The coordinates are in screen coordinates of the target display.
    # This will have the side effect of setting up other stuff for us, such
    # as source-display-bouinds.
    #
    if updateTarget:
        tdb = magnifierPBag.getValue("target-display-bounds").value()
        magnifierPBag.setValue(
            "target-display-bounds",
            atspi.ORBit.CORBA.Any(
                atspi.ORBit.CORBA.TypeCode(
                    tdb.__typecode__.repo_id),
                GNOME.Magnifier.RectBounds(prefLeft,
                                           prefTop,
                                           prefRight,
                                           prefBottom)))

    # Set a bunch of other magnifier properties...
    #
    if settings.enableMagCursor:
        bonobo.pbclient_set_float(
            magnifierPBag, "cursor-scale-factor", 1.0 * settings.magZoomFactor)
    else:
        bonobo.pbclient_set_float(
            magnifierPBag, "cursor-scale-factor", 0.0)

    if settings.enableMagCursorExplicitSize:
        bonobo.pbclient_set_long(
            magnifierPBag, "cursor-size", settings.magCursorSize)
    else:
        bonobo.pbclient_set_long(
            magnifierPBag, "cursor-size", 0)

    bonobo.pbclient_set_string(magnifierPBag, "cursor-set", "default")

    # Convert the colorPreference string to something we can use.
    # The main issue here is that the color preferences are saved
    # as 4 byte values per color.  We only need 2 bytes, so we
    # get rid of the bottom 8 bits.
    #
    colorPreference = gtk.gdk.color_parse(settings.magCursorColor)
    colorPreference.red   = colorPreference.red   >> 8
    colorPreference.blue  = colorPreference.blue  >> 8
    colorPreference.green = colorPreference.green >> 8
    colorString = "0x%02X%02X%02X" \
                  % (colorPreference.red,
                     colorPreference.green,
                     colorPreference.blue)

    color = magnifierPBag.getValue("cursor-color")
    magnifierPBag.setValue(
        "cursor-color",
        atspi.ORBit.CORBA.Any(
            color.typecode(),
            long(colorString, 0)))

    color = magnifierPBag.getValue("crosswire-color")
    magnifierPBag.setValue(
        "crosswire-color",
        atspi.ORBit.CORBA.Any(
            color.typecode(),
            long(colorString, 0)))

    if settings.enableMagCrossHair:
        bonobo.pbclient_set_long(
            magnifierPBag, "crosswire-size", settings.magCrossHairSize)
    else:
        bonobo.pbclient_set_long(
            magnifierPBag, "crosswire-size", 0)

    bonobo.pbclient_set_boolean(
        magnifierPBag, "crosswire-clip", settings.enableMagCrossHairClip)

    ########################################################################
    #                                                                      #
    # Now set up the zoomer properties.                                    #
    #                                                                      #
    ########################################################################

    # We set the target-display-bounds above, but let's ask gnome-mag for
    # what it really set it to.  Hopefully, it was the same thing.
    #
    _targetDisplayBounds = magnifierPBag.getValue(
        "target-display-bounds").value()

    debug.println(debug.LEVEL_ALL,
                  "Magnifier target bounds preferences: (%d, %d), (%d, %d)" \
                  % (settings.magZoomerLeft, settings.magZoomerTop, \
                     settings.magZoomerRight, settings.magZoomerBottom))

    debug.println(debug.LEVEL_ALL,
                  "Magnifier target bounds actual: (%d, %d), (%d, %d)" \
                  % (_targetDisplayBounds.x1, _targetDisplayBounds.y1, \
                     _targetDisplayBounds.x2, _targetDisplayBounds.y2))

    # If the COMPOSITE support is not enabled in gnome-mag, then the
    # source-display-bounds will be adjusted to accomodate portion of the
    # display not being covered by the magnifier (assuming there is only
    # one display).  Otherwise, the source-display-bounds will be the
    # entire source screen.
    #
    _sourceDisplayBounds = magnifierPBag.getValue(
        "source-display-bounds").value()

    debug.println(debug.LEVEL_ALL,
                  "Magnifier source bounds actual: (%d, %d), (%d, %d)" \
                  % (_sourceDisplayBounds.x1, _sourceDisplayBounds.y1, \
                     _sourceDisplayBounds.x2, _sourceDisplayBounds.y2))

    # If there is nothing we can possibly magnify, then abort our mission.
    #
    if ((_sourceDisplayBounds.x2 - _sourceDisplayBounds.x1) == 0) \
        or ((_sourceDisplayBounds.y2 - _sourceDisplayBounds.y1) == 0):
        debug.println(
            debug.LEVEL_SEVERE,
            "There is nothing to magnify.  This is usually caused\n" \
            "by a preferences setting that tries to take up the\n" \
            "full screen for magnification, but the underlying\n"
            "system does not support full screen magnification.\n"
            "The causes of that are generally that COMPOSITE\n" \
            "support has not been enabled in gnome-mag or the\n" \
            "X Window System Server.  As a result of this issue\n" \
            "Magnification will not be used.\n")
        raise RuntimeError, "Nothing can be magnified"

    # Now, we create a zoom region to occupy the whole magnifier (i.e.,
    # the viewport is in target region coordinates and we make the
    # viewport be the whole target region).  Note, since we're starting
    # at (0, 0), the viewportWidth and viewportHeight are the same as
    # the x2, y2 values for a rectangular region.
    #
    viewportWidth = _targetDisplayBounds.x2 - _targetDisplayBounds.x1
    viewportHeight = _targetDisplayBounds.y2 - _targetDisplayBounds.y1

    debug.println(debug.LEVEL_ALL,
                  "Magnifier zoomer viewport desired: (0, 0), (%d, %d)" \
                  % (viewportWidth, viewportHeight))

    # Now, let's see what the ROI looks like.
    #
    debug.println(debug.LEVEL_ALL,
                  "Magnifier source width: %d (viewport can show %d)" \
                  % (_sourceDisplayBounds.x2 - _sourceDisplayBounds.x1,
                   viewportWidth / settings.magZoomFactor))
    debug.println(debug.LEVEL_ALL,
                  "Magnifier source height: %d (viewport can show %d)" \
                  % (_sourceDisplayBounds.y2 - _sourceDisplayBounds.y1,
                   viewportHeight / settings.magZoomFactor))

    # Adjust the ROI in the event the source window is too small for the
    # target window.  This usually happens when someone expects COMPOSITE
    # to be enabled, but it isn't.  As a result, they usually have a very
    # big grey magnifier on their screen.
    #
    _roiWidth  = min(_sourceDisplayBounds.x2 - _sourceDisplayBounds.x1,
                     viewportWidth / settings.magZoomFactor)
    _roiHeight = min(_sourceDisplayBounds.y2 - _sourceDisplayBounds.y1,
                     viewportHeight / settings.magZoomFactor)

    debug.println(debug.LEVEL_ALL,
                  "Magnifier zoomer ROI size desired: width=%d, height=%d)" \
                  % (_roiWidth, _roiHeight))

    # Create the zoomer with a magnification factor, an initial ROI, and
    # where in magnifier we want it to be (we want it to be in the whole
    # magnifier).
    #
    _zoomer = _magnifier.createZoomRegion(
        settings.magZoomFactor, settings.magZoomFactor,
        GNOME.Magnifier.RectBounds(0, 0, _roiWidth, _roiHeight),
        GNOME.Magnifier.RectBounds(0, 0, viewportWidth, viewportHeight))

    zoomerPBag = _zoomer.getProperties()
    bonobo.pbclient_set_boolean(zoomerPBag, "is-managed", True)

    # Try to use gnome-mag >= 0.13.1 to allow us to control where to
    # draw the cursor and crosswires.
    #
    try:
        bonobo.pbclient_set_boolean(zoomerPBag, "poll-mouse", False)
        _pollMouseDisabled = True
    except:
        _pollMouseDisabled = False

    _zoomer.setMagFactor(settings.magZoomFactor, settings.magZoomFactor)

    bonobo.pbclient_set_boolean(
        zoomerPBag, "inverse-video", settings.enableMagZoomerColorInversion)

    if settings.magSmoothingMode == settings.MAG_SMOOTHING_MODE_BILINEAR:
        try:
            bonobo.pbclient_set_string(
                zoomerPBag, "smoothing-type", "bilinear")
        except:
            pass

    viewport = zoomerPBag.getValue("viewport").value()

    debug.println(debug.LEVEL_ALL,
                  "Magnifier viewport actual: (%d, %d), (%d, %d)" \
                  % (viewport.x1, viewport.y1, viewport.x2, viewport.y2))

    magx = zoomerPBag.getValue("mag-factor-x").value()
    magy = zoomerPBag.getValue("mag-factor-y").value()

    _roiWidth  = min(_sourceDisplayBounds.x2 - _sourceDisplayBounds.x1,
                     (viewport.x2 - viewport.x1) / magx)
    _roiHeight = min(_sourceDisplayBounds.y2 - _sourceDisplayBounds.y1,
                     (viewport.y2 - viewport.y1) / magy)

    debug.println(debug.LEVEL_ALL,
                  "Magnifier zoomer ROI size actual: width=%d, height=%d)" \
                  % (_roiWidth, _roiHeight))

    _minROIX = _sourceDisplayBounds.x1 + (_roiWidth / 2)
    _minROIY = _sourceDisplayBounds.y1 + (_roiHeight / 2)

    _maxROIX = _sourceDisplayBounds.x2 - (_roiWidth / 2)
    _maxROIY = _sourceDisplayBounds.y2 - (_roiHeight / 2)

    debug.println(debug.LEVEL_ALL,
                  "Magnifier ROI min/max center: (%d, %d), (%d, %d)" \
                  % (_minROIX, _minROIY, _maxROIX, _maxROIY))

    _magnifier.addZoomRegion(_zoomer)

    #print "MAGNIFIER PROPERTIES:", _magnifier
    #__dumpPropertyBag(_magnifier)
    #print "ZOOMER PROPERTIES:", _zoomer
    #__dumpPropertyBag(_zoomer)

def magnifyAccessible(event, obj, extents=None):
    """Sets the region of interest to the upper left of the given
    accessible, if it implements the Component interface.  Otherwise,
    does nothing.

    Arguments:
    - event: the Event that caused this to be called
    - obj: the accessible
    """

    if not _initialized:
        return

    if extents:
        [x, y, width, height] = extents
    elif event and event.type.startswith("object:text-caret-moved") \
       and obj.text and (obj.text.caretOffset >= 0):
        offset = obj.text.caretOffset
        [x, y, width, height] = obj.text.getCharacterExtents(offset,
                                                             0) # coord type screen
    elif obj.extents:
        extents = obj.extents
        [x, y, width, height] = [extents.x, extents.y, extents.width, extents.height]
    else:
        return

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
    leftOfROI = x < _roi.x1
    rightOfROI = (x + width) > _roi.x2
    aboveROI = y < _roi.y1
    belowROI = (y + height) > _roi.y2

    # If it is already completely showing, do nothing.
    #
    visibleX = not(leftOfROI or rightOfROI)
    visibleY = not(aboveROI or belowROI)

    if visibleX and visibleY:
        _zoomer.markDirty(_roi)

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

    if leftOfROI:
        x1 = x
        x2 = x1 + _roiWidth
    elif rightOfROI:
        if width > _roiWidth:
            x1 = x
            x2 = x1 + _roiWidth
        else:
            x2 = x + width
            x1 = x2 - _roiWidth

    if aboveROI:
        y1 = y
        y2 = y1 + _roiHeight
    elif belowROI:
        if height > _roiHeight:
            y1 = y
            y2 = y1 + _roiHeight
        else:
            y2 = y + height
            y1 = y2 - _roiHeight

    __setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))

def init():
    """Initializes the magnifier, bringing the magnifier up on the
    display.

    Returns True if the initialization procedure was run or False if this
    module has already been initialized.
    """

    global _initialized
    global _magnifier

    if not _magnifierAvailable:
        return False

    if _initialized:
        return False

    _magnifier = bonobo.get_object("OAFIID:GNOME_Magnifier_Magnifier:0.9",
                                   "GNOME/Magnifier/Magnifier")

    try:
        applySettings()
        atspi.Registry().registerEventListener(__onMouseEvent, "mouse:abs")

        _initialized = True

        # Zoom to the upper left corner of the display for now.
        #
        __setROICenter(0, 0)

        return True
    except:
        _magnifier.dispose()
        raise

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

    atspi.Registry().deregisterEventListener(__onMouseEvent,"mouse:abs")

    # Someone might have killed the magnifier on us.  They shouldn't
    # have done so, but we need to be able to recover if they did.
    # See http://bugzilla.gnome.org/show_bug.cgi?id=375396.
    #
    try:
        _magnifier.clearAllZoomRegions()
        _magnifier.dispose()
    except:
        debug.printException(debug.LEVEL_WARNING)

    _magnifier = None

    _initialized = False

    return True
