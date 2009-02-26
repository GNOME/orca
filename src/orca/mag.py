# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Manages the magnifier for orca.  [[[TODO: WDW - this is very very
early in development.  One might even say it is pre-prototype.]]]"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
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

import pyatspi
import debug
import eventsynthesizer
import settings
import speech
import orca_state

from orca_i18n import _  # for gettext support

_magnifierAvailable = False

try:
    import ORBit
    ORBit.load_typelib('GNOME_Magnifier')
    import GNOME.Magnifier
    _magnifierAvailable = True
except:
    pass

# If True, this module has been initialized.
#
_initialized = False

# The Magnifier and its property bag
#
_magnifier = None
_magnifierPBag = None

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

# The ZoomRegion we care about and its property bag.  We only use one
# ZoomRegion and we make it occupy the whole magnifier.
#
_zoomer = None
_zoomerPBag = None

# The time of the last mouse event.
#
_lastMouseEventTime = time.time()

# Whether or not the last mouse event was the result of our routing the
# pointer.
#
_lastMouseEventWasRoute = False

# If True, we're using gnome-mag >= 0.13.1 that allows us to control
# where to draw the cursor and crosswires.
#
_pollMouseDisabled = False

# Whether or not composite is being used.
#
_fullScreenCapable = True

# Whether or not we're in the process of making "live update" changes
# to the location of the magnifier.
#
_liveUpdatingMagnifier = False

# The original source display bounds.
#
_originalSourceDisplayBounds = None

# The current modes of tracking, for use with "live update" changes.
#
_mouseTracking = None
_controlTracking = None
_textTracking = None
_edgeMargin = None
_pointerFollowsZoomer = None
_pointerFollowsFocus = None

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

    #needNewROI = False
    newROI = GNOME.Magnifier.RectBounds(_roi.x1, _roi.y1, _roi.x2, _roi.y2)
    if x < _roi.x1:
        #needNewROI = True
        newROI.x1 = x
        newROI.x2 = x + _roiWidth
    elif x > _roi.x2:
        #needNewROI = True
        newROI.x2 = x
        newROI.x1 = x - _roiWidth
    if y < _roi.y1:
        #needNewROI = True
        newROI.y1 = y
        newROI.y2 = y + _roiHeight
    elif y > _roi.y2:
        #needNewROI = True
        newROI.y2 = y
        newROI.y1 = y - _roiHeight

    # Well...we'll always update the ROI so the new gnome-mag API
    # will redraw the crosswires for us.
    #
    #if needNewROI:
    if True:
        __setROI(newROI)

def __setROICursorPush(x, y, width, height, edgeMargin = 0):
    """Nudges the ROI if the caret or control is not visible.

    Arguments:
    - x: integer in unzoomed system coordinates representing x component
    - y: integer in unzoomed system coordinates representing y component
    - width: integer in unzoomed system coordinates representing the width
    - height: integer in unzoomed system coordinates representing the height
    - edgeMargin: a percentage representing how close to the edge we can get
                  before we need to push
    """

    # The edge margin should not exceed 50%. (50% is a centered alignment).
    #
    edgeMargin = min(edgeMargin, 50)/100.00
    edgeMarginX = edgeMargin * _sourceDisplayBounds.x2/settings.magZoomFactor
    edgeMarginY = edgeMargin * _sourceDisplayBounds.y2/settings.magZoomFactor

    # Determine if the accessible is partially to the left, right,
    # above, or below the current region of interest (ROI).
    #
    leftOfROI = (x - edgeMarginX) <= _roi.x1
    rightOfROI = (x + width + edgeMarginX) >= _roi.x2
    aboveROI = (y - edgeMarginY)  <= _roi.y1
    belowROI = (y + height + edgeMarginY) >= _roi.y2

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
        x1 = max(_sourceDisplayBounds.x1, x - edgeMarginX)
        x2 = x1 + _roiWidth
    elif rightOfROI:
        x = min(_sourceDisplayBounds.x2, x + edgeMarginX)
        if width > _roiWidth:
            x1 = x
            x2 = x1 + _roiWidth
        else:
            x2 = x + width
            x1 = x2 - _roiWidth

    if aboveROI:
        y1 = max(_sourceDisplayBounds.y1, y - edgeMarginY)
        y2 = y1 + _roiHeight
    elif belowROI:
        y = min(_sourceDisplayBounds.y2, y + edgeMarginY)
        if height > _roiHeight:
            y1 = y
            y2 = y1 + _roiHeight
        else:
            y2 = y + height
            y1 = y2 - _roiHeight

    __setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))

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
    global _lastMouseEventWasRoute

    isNewMouseMovement = (time.time() - _lastMouseEventTime > 1)
    _lastMouseEventTime = time.time()

    [x, y] = [e.detail1, e.detail2]

    if _pointerFollowsZoomer and isNewMouseMovement \
       and not _lastMouseEventWasRoute:
        mouseIsVisible = (_roi.x1 < x < _roi.x2) and (_roi.y1 < y < _roi.y2)
        if not mouseIsVisible and orca_state.locusOfFocus:
            if _mouseTracking == settings.MAG_TRACKING_MODE_CENTERED:
                x = (_roi.x1 + _roi.x2) / 2
                y = (_roi.y1 + _roi.y2) / 2
            elif _mouseTracking != settings.MAG_TRACKING_MODE_NONE:
                try:
                    extents = \
                        orca_state.locusOfFocus.queryComponent().getExtents(0)
                except:
                    extents = None
                if extents:
                    x = extents.x
                    y = extents.y + extents.height - 1

            eventsynthesizer.generateMouseEvent(x, y, "abs")
            _lastMouseEventWasRoute = True

    # If True, we're using gnome-mag >= 0.13.1 that allows us to
    # control where to draw the cursor and crosswires.
    #
    if _pollMouseDisabled:
        _zoomer.setPointerPos(x, y)

    if _lastMouseEventWasRoute:
        # If we just moved the mouse pointer to the menu item or control
        # with focus, we don't want to do anything.
        #
        _lastMouseEventWasRoute = False
        _zoomer.markDirty(_roi)
        return

    if _mouseTracking == settings.MAG_TRACKING_MODE_PUSH:
        __setROIPush(x, y)
    elif _mouseTracking == settings.MAG_TRACKING_MODE_PROPORTIONAL:
        __setROIProportional(x, y)
    elif _mouseTracking == settings.MAG_TRACKING_MODE_CENTERED:
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

def __setupMagnifier(position, left=None, top=None, right=None, bottom=None,
                     restore=None):
    """Creates the magnifier in the position specified.

    Arguments:
    - position: the position/type of zoomer (full, left half, etc.)
    - left:     the left edge of the zoomer (only applicable for custom)
    - top:      the top edge of the zoomer (only applicable for custom)
    - right:    the right edge of the zoomer (only applicable for custom)
    - bottom:   the top edge of the zoomer (only applicable for custom)
    - restore:  a dictionary of all of the settings which should be restored
    """

    global _fullScreenCapable
    global _magnifierPBag
    global _originalSourceDisplayBounds

    _magnifier.clearAllZoomRegions()

    if not restore:
        restore = {}

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

    # Find out if we're using composite.
    #
    try:
        _fullScreenCapable = _magnifier.fullScreenCapable()
    except:
        debug.printException(debug.LEVEL_WARNING)

    # If we are running in full screen mode, try to hide the original cursor
    # (assuming the user wants to). See bug #533095 for more details.
    # Depends upon new functionality in gnome-mag, so just catch the 
    # exception if this functionality isn't there.
    #
    hideCursor = restore.get('magHideCursor', settings.magHideCursor)
    if hideCursor \
       and _fullScreenCapable \
       and _magnifier.SourceDisplay == _magnifier.TargetDisplay \
       and position == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
        hideSystemPointer(True)
    else:
        hideSystemPointer(False)

    _magnifierPBag = _magnifier.getProperties()
    sdb = _magnifierPBag.getValue("source-display-bounds").value()
    if not _originalSourceDisplayBounds:
        _originalSourceDisplayBounds = sdb
    elif _liveUpdatingMagnifier:
        sdb = _originalSourceDisplayBounds

    # Find out where the user wants to place the target display.
    #
    if _fullScreenCapable and \
       position == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
        prefLeft = 0
        prefTop = 0
        prefRight = sdb.x2
        prefBottom = sdb.y2
    elif position == settings.MAG_ZOOMER_TYPE_TOP_HALF:
        prefLeft = 0
        prefTop = 0
        prefRight = sdb.x2
        prefBottom = sdb.y2 / 2
    elif position == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
        prefLeft = 0
        prefTop = sdb.y2 / 2
        prefRight = sdb.x2
        prefBottom = sdb.y2
    elif position == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
        prefLeft = 0
        prefTop = 0
        prefRight = sdb.x2 / 2
        prefBottom = sdb.y2
    elif position == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
        prefLeft = sdb.x2 / 2
        prefTop = 0
        prefRight = sdb.x2
        prefBottom = sdb.y2
    else:
        prefLeft   = left or settings.magZoomerLeft
        prefTop    = top or settings.magZoomerTop
        prefRight  = right or settings.magZoomerRight
        prefBottom = bottom or settings.magZoomerBottom
    orca_state.zoomerType = position
    updateTarget = True

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
        tdb = _magnifierPBag.getValue("target-display-bounds").value()
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
            elif sdb.y2 > 0:
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
        tdb = _magnifierPBag.getValue("target-display-bounds").value()
        _magnifierPBag.setValue(
            "target-display-bounds",
            ORBit.CORBA.Any(
                ORBit.CORBA.TypeCode(
                    tdb.__typecode__.repo_id),
                GNOME.Magnifier.RectBounds(prefLeft,
                                           prefTop,
                                           prefRight,
                                           prefBottom)))

    bonobo.pbclient_set_string(_magnifierPBag, "cursor-set", "default")

    enableCursor = restore.get('enableMagCursor', settings.enableMagCursor)
    explicitSize = restore.get('enableMagCursorExplicitSize',
                               settings.enableMagCursorExplicitSize)
    size = restore.get('magCursorSize', settings.magCursorSize)
    setMagnifierCursor(enableCursor, explicitSize, size, False)

    value = restore.get('magCursorColor', settings.magCursorColor)
    setMagnifierObjectColor("cursor-color", value, False)

    value = restore.get('magCrossHairColor', settings.magCrossHairColor)
    setMagnifierObjectColor("crosswire-color", value, False)

    enableCrossHair = restore.get('enableMagCrossHair',
                                  settings.enableMagCrossHair)
    setMagnifierCrossHair(enableCrossHair, False)

    value = restore.get('enableMagCrossHairClip',
                        settings.enableMagCrossHairClip)
    setMagnifierCrossHairClip(value, False)

    orca_state.mouseEnhancementsEnabled = enableCursor or enableCrossHair

def __setupZoomer(restore=None):
    """Creates a zoomer in the magnifier
    Arguments:
    - restore:  a dictionary of all of the settings which should be restored
    """

    global _sourceDisplayBounds
    global _targetDisplayBounds
    global _zoomer
    global _roiWidth
    global _roiHeight
    global _pollMouseDisabled
    global _zoomerPBag
    global _fullScreenCapable

    if not restore:
        restore = {}

    _targetDisplayBounds = _magnifierPBag.getValue(
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
    _sourceDisplayBounds = _magnifierPBag.getValue(
        "source-display-bounds").value()

    debug.println(debug.LEVEL_ALL,
                  "Magnifier source bounds actual: (%d, %d), (%d, %d)" \
                  % (_sourceDisplayBounds.x1, _sourceDisplayBounds.y1, \
                     _sourceDisplayBounds.x2, _sourceDisplayBounds.y2))

    # If there is nothing we can possibly magnify, switch to the right half.
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
            "X Window System Server.  As a result of this issue,\n" \
            "defaulting to the right half of the screen.\n")
        _fullScreenCapable = False
        __setupMagnifier(settings.MAG_ZOOMER_TYPE_CUSTOM,
                         _targetDisplayBounds.x1/2,
                         _targetDisplayBounds.y1,
                         _targetDisplayBounds.x2,
                         _targetDisplayBounds.y2)
        _sourceDisplayBounds = _magnifierPBag.getValue(
            "source-display-bounds").value()
        _targetDisplayBounds = _magnifierPBag.getValue(
            "target-display-bounds").value()

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
    # magnifier). Initially set the viewport so that it does not appear.
    # After we set all of the color properties, reset the viewport to
    # the correct position.  This will prevent the user from seeing the
    # individual property changes (e.g. brightness, contrast) upon load.
    #
    _zoomer = _magnifier.createZoomRegion(
        settings.magZoomFactor, settings.magZoomFactor,
        GNOME.Magnifier.RectBounds(0, 0, _roiWidth, _roiHeight),
        GNOME.Magnifier.RectBounds(0, 0, 1, 1))

    _zoomerPBag = _zoomer.getProperties()
    bonobo.pbclient_set_boolean(_zoomerPBag, "is-managed", True)

    value = restore.get('magZoomFactor', settings.magZoomFactor)
    setZoomerMagFactor(value, value, False)

    value = restore.get('enableMagZoomerColorInversion',
                        settings.enableMagZoomerColorInversion)
    setZoomerColorInversion(value, False)

    brightness = restore.get('magBrightnessLevel', settings.magBrightnessLevel)
    r = brightness + \
        restore.get('magBrightnessLevelRed',
                    settings.magBrightnessLevelRed)
    g = brightness + \
        restore.get('magBrightnessLevelGreen',
                    settings.magBrightnessLevelGreen)
    b = brightness + \
        restore.get('magBrightnessLevelBlue',
                    settings.magBrightnessLevelBlue)
    setZoomerBrightness(r, g, b, False)

    contrast = restore.get('magContrastLevel', settings.magContrastLevel)
    r = contrast + \
        restore.get('magContrastLevelRed',
                    settings.magContrastLevelRed)
    g = contrast + \
        restore.get('magContrastLevelGreen',
                    settings.magContrastLevelGreen)
    b = contrast + \
        restore.get('magContrastLevelBlue',
                    settings.magContrastLevelBlue)
    setZoomerContrast(r, g, b, False)

    value = restore.get('magColorFilteringMode',
                        settings.magColorFilteringMode)
    setZoomerColorFilter(value, False)

    value = restore.get('magZoomerType', settings.magZoomerType)
    if value == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
        size = 0
    else:
        size = restore.get('magZoomerBorderSize', settings.magZoomerBorderSize)
    color = restore.get('magZoomerBorderColor', settings.magZoomerBorderColor)
    setZoomerObjectSize("border-size", size, False)
    setZoomerObjectColor("border-color", color, False)

    value = restore.get('magSmoothingMode', settings.magSmoothingMode)
    setZoomerSmoothingType(value, False)

    # Now it's safe to display the viewport.
    #
    bounds = GNOME.Magnifier.RectBounds(0, 0, viewportWidth, viewportHeight)
    _zoomer.moveResize(bounds)

    # Try to use gnome-mag >= 0.13.1 to allow us to control where to
    # draw the cursor and crosswires.
    #
    try:
        bonobo.pbclient_set_boolean(_zoomerPBag, "poll-mouse", False)
        _pollMouseDisabled = True
    except:
        _pollMouseDisabled = False

    __updateROIDimensions()
    _magnifier.addZoomRegion(_zoomer)

def __updateROIDimensions():
    """Updates the ROI width, height, and maximum and minimum values.
    """

    global _roiWidth
    global _roiHeight
    global _minROIX
    global _minROIY
    global _maxROIX
    global _maxROIY

    viewport = _zoomerPBag.getValue("viewport").value()

    debug.println(debug.LEVEL_ALL,
                  "Magnifier viewport actual: (%d, %d), (%d, %d)" \
                  % (viewport.x1, viewport.y1, viewport.x2, viewport.y2))

    magx = _zoomerPBag.getValue("mag-factor-x").value()
    magy = _zoomerPBag.getValue("mag-factor-y").value()

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

def applySettings():
    """Looks at the user settings and applies them to the magnifier."""

    global _mouseTracking
    global _controlTracking
    global _textTracking
    global _edgeMargin
    global _pointerFollowsZoomer
    global _pointerFollowsFocus

    __setupMagnifier(settings.magZoomerType)
    __setupZoomer()
  
    _mouseTracking = settings.magMouseTrackingMode
    _controlTracking = settings.magControlTrackingMode
    _textTracking = settings.magTextTrackingMode
    _edgeMargin = settings.magEdgeMargin
    _pointerFollowsZoomer = settings.magPointerFollowsZoomer
    _pointerFollowsFocus = settings.magPointerFollowsFocus

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

    global _lastMouseEventWasRoute

    if not _initialized:
        return

    # Avoid jerking the display around if the mouse is what ended up causing
    # this event.  We guess this by seeing if this request has come in within
    # a close period of time.  [[[TODO: WDW - this is a hack and really
    # doesn't belong here.  Plus, the delta probably should be adjustable.]]]
    #
    currentTime = time.time()
    if (currentTime - _lastMouseEventTime) < 0.2: # 200 milliseconds
        return

    haveSomethingToMagnify = False

    if extents:
        [x, y, width, height] = extents
        haveSomethingToMagnify = True
    elif event and event.type.startswith("object:text-caret-moved"):
        try:
            text = obj.queryText()
            if text and (text.caretOffset >= 0):
                offset = text.caretOffset
                if offset == text.characterCount:
                    offset -= 1
                [x, y, width, height] = \
                    text.getCharacterExtents(offset, 0)
                haveSomethingToMagnify = (width + height > 0)
                    
        except:
            haveSomethingToMagnify = False

        if haveSomethingToMagnify:
            if _textTracking == settings.MAG_TRACKING_MODE_CENTERED:
                __setROICenter(x, y)
            elif _textTracking == settings.MAG_TRACKING_MODE_PUSH:
                __setROICursorPush(x, y, width, height, _edgeMargin)
            return

    if not haveSomethingToMagnify:
        try:
            extents = obj.queryComponent().getExtents(0)
            [x, y, width, height] = \
                [extents.x, extents.y, extents.width, extents.height]
            haveSomethingToMagnify = True
        except:
            haveSomethingToMagnify = False

    if haveSomethingToMagnify:
        if _pointerFollowsFocus:
            _lastMouseEventWasRoute = True
            eventsynthesizer.generateMouseEvent(x, y + height - 1, "abs")

        if _controlTracking == settings.MAG_TRACKING_MODE_CENTERED:
            centerX = x + width/2
            centerY = y + height/2

            # Be sure that the upper-left corner of the object will still
            # be visible on the screen.
            #
            if width > _roiWidth:
                centerX = x
            if height > _roiHeight:
                centerY = y

            __setROICenter(centerX, centerY)
        elif _controlTracking == settings.MAG_TRACKING_MODE_PUSH:
            __setROICursorPush(x, y, width, height)

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
        _initialized = True
        applySettings()
        pyatspi.Registry.registerEventListener(__onMouseEvent, "mouse:abs")

        # Zoom to the upper left corner of the display for now.
        #
        __setROICenter(0, 0)

        return True
    except:
        _initialized = False
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

    pyatspi.Registry.deregisterEventListener(__onMouseEvent,"mouse:abs")

    # Someone might have killed the magnifier on us.  They shouldn't
    # have done so, but we need to be able to recover if they did.
    # See http://bugzilla.gnome.org/show_bug.cgi?id=375396.
    #
    try:
        hideSystemPointer(False)
        _magnifier.clearAllZoomRegions()
        _magnifier.dispose()
    except:
        debug.printException(debug.LEVEL_WARNING)

    _magnifier = None

    _initialized = False

    return True

######################################################################
#                                                                    #
#              Convenience functions for "live" changes              #
#                                                                    #
######################################################################

def setupMagnifier(position, left=None, top=None, right=None, bottom=None,
                   restore=None):
    """Creates the magnifier in the position specified.

    Arguments:
    - position: the position/type of zoomer (full, left half, etc.)
    - left:     the left edge of the zoomer (only applicable for custom)
    - top:      the top edge of the zoomer (only applicable for custom)
    - right:    the right edge of the zoomer (only applicable for custom)
    - bottom:   the top edge of the zoomer (only applicable for custom)
    - restore:  a dictionary of all of the settings that should be restored
    """

    if not _initialized:
        return

    global _liveUpdatingMagnifier

    _liveUpdatingMagnifier = True
    __setupMagnifier(position, left, top, right, bottom, restore)
    __setupZoomer(restore)

def setMagnifierCursor(enabled, customEnabled, size, updateScreen=True):
    """Sets the cursor.

    Arguments:
    - enabled:        Whether or not the cursor should be enabled
    - customEnabled:  Whether or not a custom size has been enabled
    - size:           The size it should be set to
    - updateScreen:   Whether or not to update the screen
    """

    if not _initialized:
        return
    try:
        mag = _zoomerPBag.getValue("mag-factor-x").value()
    except:
        mag = settings.magZoomFactor

    if enabled:
        scale = 1.0 * mag
    else:
        scale = 0.0

    if not (enabled and customEnabled):
        size = 0

    bonobo.pbclient_set_float(_magnifierPBag, "cursor-scale-factor", scale)
    bonobo.pbclient_set_long(_magnifierPBag, "cursor-size", size)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setMagnifierCrossHair(enabled, updateScreen=True):
    """Sets the cross-hair.

    Arguments:
    - enabled: Whether or not the cross-hair should be enabled
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized:
        return

    size = 0
    if enabled:
        size = settings.magCrossHairSize

    bonobo.pbclient_set_long(_magnifierPBag, "crosswire-size", size)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setMagnifierCrossHairClip(enabled, updateScreen=True):
    """Sets the cross-hair clip.

    Arguments:
    - enabled: Whether or not the cross-hair clip should be enabled
    - updateScreen:   Whether or not to update the screen
    """

    if not _initialized:
        return

    bonobo.pbclient_set_boolean(_magnifierPBag, "crosswire-clip", enabled)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setZoomerColorInversion(enabled, updateScreen=True):
    """Sets the color inversion.

    Arguments:
    - enabled: Whether or not color inversion should be enabled
    - updateScreen:   Whether or not to update the screen
    """

    if not _initialized:
        return

    bonobo.pbclient_set_boolean(_zoomerPBag, "inverse-video", enabled)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setZoomerBrightness(red=0, green=0, blue=0, updateScreen=True):
    """Increases/Decreases the brightness level by the specified
    increments.  Increments are floats ranging from -1 (black/no
    brightenss) to 1 (white/100% brightness).  0 means no change.

    Arguments:
    - red:    The amount to alter the red brightness level
    - green:  The amount to alter the green brightness level
    - blue:   The amount to alter the blue brightness level
    - updateScreen:   Whether or not to update the screen
    """

    if not _initialized:
        return

    _zoomer.setBrightness(red, green, blue)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setZoomerContrast(red=0, green=0, blue=0, updateScreen=True):
    """Increases/Decreases the contrast level by the specified
    increments.  Increments are floats ranging from -1 (grey/no
    contrast) to 1 (white/back/100% contrast).  0 means no change.

    Arguments:
    - red:    The amount to alter the red contrast level
    - green:  The amount to alter the green contrast level
    - blue:   The amount to alter the blue contrast level
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized:
        return

    _zoomer.setContrast(red, green, blue)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setMagnifierObjectSize(magProperty, size, updateScreen=True):
    """Sets the specified magnifier property to the specified size.

    Arguments:
    - magProperty:   The property to set (as a string)
    - size:          The size to apply
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized:
        return

    bonobo.pbclient_set_long(_magnifierPBag, magProperty, size)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setZoomerObjectSize(magProperty, size, updateScreen=True):
    """Sets the specified zoomer property to the specified size.

    Arguments:
    - magProperty:   The property to set (as a string)
    - size:          The size to apply
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized:
        return

    if magProperty == "border-size":
        try:
            left = right = top = bottom = 0
            if orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
                left = size
            elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
                right = size
            elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_TOP_HALF:
                bottom = size
            elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
                top = size
            elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_CUSTOM:
                if _targetDisplayBounds.x1 > _sourceDisplayBounds.x1:
                    left = size
                if _targetDisplayBounds.x2 < _sourceDisplayBounds.x2:
                    right = size
                if _targetDisplayBounds.y1 > _sourceDisplayBounds.y1:
                    top = size
                if _targetDisplayBounds.y2 < _sourceDisplayBounds.y2:
                    bottom = size
                
            bonobo.pbclient_set_long(_zoomerPBag, "border-size-left", left)
            bonobo.pbclient_set_long(_zoomerPBag, "border-size-top", top)
            bonobo.pbclient_set_long(_zoomerPBag, "border-size-right", right)
            bonobo.pbclient_set_long(_zoomerPBag, "border-size-bottom", bottom)
        except:
            bonobo.pbclient_set_long(_zoomerPBag, "border-size", size)
    else:
        bonobo.pbclient_set_long(_zoomerPBag, magProperty, size)

    if updateScreen:
        _zoomer.markDirty(_roi)

def setZoomerObjectColor(magProperty, colorSetting, updateScreen=True):
    """Sets the specified zoomer property to the specified color.

    Arguments:
    - magProperty:  The property to set (as a string)
    - colorSetting: The Orca color setting to apply
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized:
        return

    colorPreference = gtk.gdk.color_parse(colorSetting)

    # Convert the colorPreference string to something we can use.
    # The main issue here is that the color preferences are saved
    # as 4 byte values per color.  We only need 2 bytes, so we
    # get rid of the bottom 8 bits.
    #
    colorPreference.red   = colorPreference.red   >> 8
    colorPreference.blue  = colorPreference.blue  >> 8
    colorPreference.green = colorPreference.green >> 8
    colorString = "0x%02X%02X%02X" \
                  % (colorPreference.red,
                     colorPreference.green,
                     colorPreference.blue)

    toChange = _zoomerPBag.getValue(magProperty)
    _zoomerPBag.setValue(magProperty,
                         ORBit.CORBA.Any(toChange.typecode(),
                                         long(colorString, 0)))
    if updateScreen:
        _zoomer.markDirty(_roi)

def setMagnifierObjectColor(magProperty, colorSetting, updateScreen=True):
    """Sets the specified magnifier property to the specified color.

    Arguments:
    - magProperty:  The property to set (as a string)
    - colorSetting: The Orca color setting to apply
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized:
        return

    colorPreference = gtk.gdk.color_parse(colorSetting)

    # Convert the colorPreference string to something we can use.
    # The main issue here is that the color preferences are saved
    # as 4 byte values per color.  We only need 2 bytes, so we
    # get rid of the bottom 8 bits.
    #
    colorPreference.red   = colorPreference.red   >> 8
    colorPreference.blue  = colorPreference.blue  >> 8
    colorPreference.green = colorPreference.green >> 8
    colorString = "0x%02X%02X%02X" \
                  % (colorPreference.red,
                     colorPreference.green,
                     colorPreference.blue)

    toChange = _magnifierPBag.getValue(magProperty)
    _magnifierPBag.setValue(magProperty,
                            ORBit.CORBA.Any(toChange.typecode(),
                                            long(colorString, 0)))
    if updateScreen:
        _zoomer.markDirty(_roi)

def setZoomerMagFactor(x, y, updateScreen=True):
    """Sets the magnification level.

    Arguments:
    - x: The horizontal magnification level
    - y: The vertical magnification level
    - updateScreen:  Whether or not to update the screen
    """

    global _minROIX
    global _minROIY

    if not _initialized:
        return

    [oldX, oldY] = _zoomer.getMagFactor()

    _zoomer.setMagFactor(x, y)

    if updateScreen:
        __updateROIDimensions()
        if (oldX > x) and (x < 1.5):
            _minROIX = _sourceDisplayBounds.x1
            _minROIY = _sourceDisplayBounds.y1
            __setROI(GNOME.Magnifier.RectBounds(_minROIX,
                                                _minROIY,
                                                _minROIX + _roiWidth,
                                                _minROIY + _roiHeight))
        else:
            extents = orca_state.locusOfFocus.queryComponent().getExtents(0)
            __setROICenter(extents.x, extents.y)

def setZoomerSmoothingType(smoothingType, updateScreen=True):
    """Sets the zoomer's smoothing type.

    Arguments:
    - smoothingType: The type of smoothing to use
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized:
        return

    if smoothingType == settings.MAG_SMOOTHING_MODE_BILINEAR:
        string = "bilinear"
    else:
        string = "None"

    try:
        bonobo.pbclient_set_string(_zoomerPBag, "smoothing-type", string)
    except:
        pass

    if updateScreen:
        _zoomer.markDirty(_roi)

def setZoomerColorFilter(colorFilter, updateScreen=True):
    """Sets the zoomer's color filter.

    Arguments:
    - colorFilter: The color filter to apply
    - updateScreen:  Whether or not to update the screen
    """

    if not _initialized or not isFilteringCapable():
        return

    if colorFilter == settings.MAG_COLOR_FILTERING_MODE_SATURATE_RED:
        toApply = _zoomer.COLORBLIND_FILTER_T_SELECTIVE_SATURATE_RED
    elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_SATURATE_GREEN:
        toApply = _zoomer.COLORBLIND_FILTER_T_SELECTIVE_SATURATE_GREEN
    elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_SATURATE_BLUE:
        toApply = _zoomer.COLORBLIND_FILTER_T_SELECTIVE_SATURATE_BLUE
    elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_RED:
        toApply = _zoomer.COLORBLIND_FILTER_T_SELECTIVE_DESSATURATE_RED
    elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_GREEN:
        toApply = _zoomer.COLORBLIND_FILTER_T_SELECTIVE_DESSATURATE_GREEN
    elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_BLUE:
        toApply = _zoomer.COLORBLIND_FILTER_T_SELECTIVE_DESSATURATE_BLUE
    elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_NEGATIVE_HUE_SHIFT:
        toApply = _zoomer.COLORBLIND_FILTER_T_HUE_SHIFT_NEGATIVE
    elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_POSITIVE_HUE_SHIFT:
        toApply = _zoomer.COLORBLIND_FILTER_T_HUE_SHIFT_POSITIVE
    else:
        toApply = _zoomer.COLORBLIND_FILTER_T_NO_FILTER

    colorFilter = _zoomerPBag.getValue("color-blind-filter")
    _zoomerPBag.setValue(
         "color-blind-filter",
         ORBit.CORBA.Any(
             colorFilter.typecode(),
             toApply))

    if updateScreen:
        _zoomer.markDirty(_roi)

def hideSystemPointer(hidePointer):
    """Hide or show the system pointer.

    Arguments:
    -hidePointer: If True, hide the system pointer, otherwise show it.
    """

    # Depends upon new functionality in gnome-mag, so just catch the
    # exception if this functionality isn't there.
    #
    try:
        if hidePointer:
            _magnifier.hideCursor()
        else:
            _magnifier.showCursor()
    except:
        debug.printException(debug.LEVEL_FINEST)

def isFullScreenCapable():
    """Returns True if we are capable of doing full screen (i.e. whether
    composite is being used.
    """

    try:
        capable = _magnifier.fullScreenCapable()
    except:
        capable = False

    return capable

def isFilteringCapable():
    """Returns True if we're able to take advantage of libcolorblind's color
    filtering.
    """

    try:
        capable = _magnifier.supportColorblindFilters()
    except:
        capable = False

    return capable

def updateMouseTracking(newMode):
    """Updates the mouse tracking mode.

    Arguments:
    -newMode: The new mode to use.
    """

    global _mouseTracking
    _mouseTracking = newMode

def updateControlTracking(newMode):
    """Updates the control tracking mode.

    Arguments:
    -newMode: The new mode to use.
    """

    global _controlTracking
    _controlTracking = newMode

def updateTextTracking(newMode):
    """Updates the text tracking mode.

    Arguments:
    -newMode: The new mode to use.
    """

    global _textTracking
    _textTracking = newMode

def updateEdgeMargin(amount):
    """Updates the edge margin

    Arguments:
    -amount: The new margin to use, in pixels.
    """

    global _edgeMargin
    _edgeMargin = amount

def updatePointerFollowsFocus(enabled):
    """Updates the pointer follows focus setting.

    Arguments:
    -enabled: whether or not pointer follows focus should be enabled.
    """

    global _pointerFollowsFocus
    _pointerFollowsFocus = enabled

def updatePointerFollowsZoomer(enabled):
    """Updates the pointer follows zoomer setting.

    Arguments:
    -enabled: whether or not pointer follows zoomer should be enabled.
    """

    global _pointerFollowsZoomer
    _pointerFollowsZoomer = enabled

def finishLiveUpdating():
    """Restores things that were altered via a live update."""

    global _liveUpdatingMagnifier
    global _mouseTracking
    global _controlTracking
    global _textTracking
    global _edgeMargin
    global _pointerFollowsFocus
    global _pointerFollowsZoomer

    _liveUpdatingMagnifier = False
    _mouseTracking = settings.magMouseTrackingMode
    _controlTracking = settings.magControlTrackingMode
    _textTracking = settings.magTextTrackingMode
    _edgeMargin = settings.magEdgeMargin
    _pointerFollowsFocus = settings.magPointerFollowsFocus
    _pointerFollowsZoomer = settings.magPointerFollowsZoomer

    if settings.enableMagnifier:
        setupMagnifier(settings.magZoomerType)
        init()
    else:
        shutdown()

######################################################################
#                                                                    #
#                        Input Event Handlers                        #
#                                                                    #
######################################################################

def toggleColorEnhancements(script=None, inputEvent=None):
    """Toggles the color enhancements on/off."""

    if not _initialized:
        return

    # We don't want to stomp on a command-altered magnification level.
    #
    [levelX, levelY] = _zoomer.getMagFactor()
    
    normal = {'enableMagZoomerColorInversion': False,
              'magBrightnessLevelRed': 0,
              'magBrightnessLevelGreen': 0,
              'magBrightnessLevelBlue': 0,
              'magContrastLevelRed': 0,
              'magContrastLevelGreen': 0,
              'magContrastLevelBlue': 0,
              'magColorFilteringMode': settings.MAG_COLOR_FILTERING_MODE_NONE,
              'magSmoothingMode': settings.MAG_SMOOTHING_MODE_BILINEAR,
              'magZoomerBorderColor': '#000000',
              'magZoomFactor': levelX}

    if orca_state.colorEnhancementsEnabled:
        __setupZoomer(restore = normal)
        # Translators: "color enhancements" are changes users can
        # make to the appearance of the screen to make things easier
        # to see, such as inverting the colors or applying a tint.
        #
        speech.speak(_("Color enhancements disabled."))
    else:
        toRestore = {'magZoomFactor': levelX}
        __setupZoomer(restore = toRestore)
        # Translators: "color enhancements" are changes users can
        # make to the appearance of the screen to make things easier
        # to see, such as inverting the colors or applying a tint.
        #
        speech.speak(_("Color enhancements enabled."))

    orca_state.colorEnhancementsEnabled = \
                                    not orca_state.colorEnhancementsEnabled

    return True

def toggleMouseEnhancements(script=None, inputEvent=None):
    """Toggles the mouse enhancements on/off."""

    if not _initialized:
        return

    if orca_state.mouseEnhancementsEnabled:
        setMagnifierCrossHair(False, False)
        setMagnifierObjectColor("cursor-color", "#000000", False)
        setMagnifierCursor(True, False, 0)
        # Translators: "mouse enhancements" are changes users can
        # make to the appearance of the mouse pointer to make it
        # easier to see, such as increasing its size, changing its
        # color, and surrounding it with crosshairs.
        #
        speech.speak(_("Mouse enhancements disabled."))
    else:
        # We normally toggle "on" what the user has enabled by default.
        # However, if the user's default settings are to disable all mouse
        # enhancements "on" and "off" are the same thing.  If that is the
        # case and this command is being used, the user probably expects
        # to see *something* change. We don't know what, so enable both
        # the cursor and the cross-hairs.
        #
        cursorEnable = settings.enableMagCursor
        crossHairEnable = settings.enableMagCrossHair
        if not (cursorEnable or crossHairEnable):
            cursorEnable = True
            crossHairEnable = True

        setMagnifierCursor(cursorEnable,
                           settings.enableMagCursorExplicitSize,
                           settings.magCursorSize,
                           False)
        setMagnifierObjectColor("cursor-color",
                                settings.magCursorColor,
                                False)
        setMagnifierObjectColor("crosswire-color",
                                settings.magCrossHairColor,
                                False)
        setMagnifierCrossHairClip(settings.enableMagCrossHairClip,
                                  False)
        setMagnifierCrossHair(crossHairEnable)
        # Translators: "mouse enhancements" are changes users can
        # make to the appearance of the mouse pointer to make it
        # easier to see, such as increasing its size, changing its
        # color, and surrounding it with crosshairs.
        #
        speech.speak(_("Mouse enhancements enabled."))

    orca_state.mouseEnhancementsEnabled = \
                                    not orca_state.mouseEnhancementsEnabled
    return True

def increaseMagnification(script=None, inputEvent=None):
    """Increases the magnification level."""

    if not _initialized:
        return

    [levelX, levelY] = _zoomer.getMagFactor()

    # Move in increments that are sensible based on the current level of
    # magnification.
    #
    if 1 <= levelX < 4:
        increment = 0.25
    elif 4 <= levelX < 7:
        increment = 0.5
    else:
        increment = 1

    newLevel = levelX + increment
    if newLevel <= 16:
        setZoomerMagFactor(newLevel, newLevel)
        speech.speak(str(newLevel))

    return True

def decreaseMagnification(script=None, inputEvent=None):
    """Decreases the magnification level."""

    if not _initialized:
        return

    [levelX, levelY] = _zoomer.getMagFactor()

    # Move in increments that are sensible based on the current level of
    # magnification.
    #
    if 1 <= levelX < 4:
        increment = 0.25
    elif 4 <= levelX < 7:
        increment = 0.5
    else:
        increment = 1

    newLevel = levelX - increment
    if newLevel >= 1:
        setZoomerMagFactor(newLevel, newLevel)
        speech.speak(str(newLevel))

    return True

def toggleMagnifier(script=None, inputEvent=None):
    """Toggles the magnifier."""

    if not _initialized:
        init()
        # Translators: this is the message spoken when a user enables the
        # magnifier.  In addition to screen magnification, the user's
        # preferred colors and mouse customizations are loaded.
        #
        speech.speak(_("Magnifier enabled."))
    else:
        shutdown()
        # Translators: this is the message spoken when a user disables the
        # magnifier, restoring the screen contents to their normal colors
        # and sizes.
        #
        speech.speak(_("Magnifier disabled."))

    return True

def cycleZoomerType(script=None, inputEvent=None):
    """Allows the user to cycle through the available zoomer types."""

    if not _initialized:
        return

    # There are 6 possible zoomer types
    #
    orca_state.zoomerType += 1

    if orca_state.zoomerType >= 6:
        orca_state.zoomerType = 0

    if orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_FULL_SCREEN \
       and not _fullScreenCapable:
        orca_state.zoomerType += 1

    # We don't want to stomp on any command-altered settings
    #
    toRestore = {}

    [levelX, levelY] = _zoomer.getMagFactor()
    if levelX != settings.magZoomFactor:
        toRestore['magZoomFactor'] = levelX

    if not orca_state.colorEnhancementsEnabled:
        toRestore.update(\
            {'enableMagZoomerColorInversion': False,
             'magBrightnessLevelRed': 0,
             'magBrightnessLevelGreen': 0,
             'magBrightnessLevelBlue': 0,
             'magContrastLevelRed': 0,
             'magContrastLevelGreen': 0,
             'magContrastLevelBlue': 0,
             'magColorFilteringMode': settings.MAG_COLOR_FILTERING_MODE_NONE,
             'magSmoothingMode': settings.MAG_SMOOTHING_MODE_BILINEAR,
             'magZoomerBorderColor': '#000000'})

    setupMagnifier(orca_state.zoomerType, restore = toRestore)

    if not orca_state.mouseEnhancementsEnabled:
        setMagnifierCrossHair(False)
        setMagnifierObjectColor("cursor-color",
                                settings.magCursorColor,
                                False)
        setMagnifierCursor(False, False, 0)

    if orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
        if _fullScreenCapable:
            # Translators: magnification will use the full screen.
            #
            zoomerType = _("Full Screen")
        else:
            # Translators: the user attempted to switch to full screen
            # magnification, but his/her system doesn't support it.
            #
            zoomerType = _("Full Screen mode unavailable")
    elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_TOP_HALF:
        # Translators: magnification will use the top half of the screen.
        #
        zoomerType = _("Top Half")
    elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
        # Translators: magnification will use the bottom half of the screen.
        #
        zoomerType = _("Bottom Half")
    elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
        # Translators: magnification will use the left half of the screen.
        #
        zoomerType = _("Left Half")
    elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
        # Translators: magnification will use the right half of the screen.
        #
        zoomerType = _("Right Half")
    elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_CUSTOM:
        # Translators: the user has selected a custom area of the screen
        # to use for magnification.
        #
        zoomerType = _("Custom")
    else:
        # This shouldn't happen, but just in case....
        zoomerType = ""

    speech.speak(zoomerType)

    return True
