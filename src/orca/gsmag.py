# Orca
#
# Copyright 2009 Sun Microsystems Inc.
# Copyright 2010 Willie Walker
#  * Contributor: Willie Walker <walker.willie@gmail.com>
#  * Contributor: Joseph Scheuhammer <clown@alum.mit.edu>
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

"""Manages the GNOME Shell magnifier interface for orca.  [[[TODO: WDW
- this is very very early in development.  One might even say it is
pre-prototype.]]]"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2009 Sun Microsystems Inc."
__license__   = "LGPL"

import dbus
from dbus.mainloop.glib import DBusGMainLoop
_dbusLoop = DBusGMainLoop()
_bus = dbus.SessionBus(mainloop=_dbusLoop)

_proxy_obj = _bus.get_object("org.gnome.Magnifier",
                             "/org/gnome/Magnifier")
_magnifier = dbus.Interface(_proxy_obj, "org.gnome.Magnifier")
_zoomer = None

import debug
import eventsynthesizer
import settings
import orca_state

# If True, the magnifier is active
#
_isActive = False

# The current modes of tracking, for use with "live update" changes.
#
_controlTracking = None
_edgeMargin = None
_mouseTracking = None
_pointerFollowsZoomer = None
_pointerFollowsFocus = None
_textTracking = None

import gtk
_display = gtk.gdk.display_get_default()
_screen = _display.get_default_screen()
_screenWidth = _screen.get_width()
_screenHeight = _screen.get_height()

# If True, this module has been initialized.
#
_initialized = False
_fullScreenCapable = False
_wasActiveOnInit = False

# The width and height, in unzoomed system coordinates of the rectangle that,
# when magnified, will fill the viewport of the magnifier - this needs to be
# sync'd with the magnification factors of the zoom area.
#
_roiWidth = 0
_roiHeight = 0

# The current region of interest as specified by the upper left corner.
#
_roi = None

# Minimum/maximum values for the center of the ROI
# in source screen coordinates.
#
_minROIX = 0
_maxROIX = 0
_minROIY = 0
_maxROIY = 0


########################################################################
#                                                                      #
# D-Bus callbacks                                                      #
#                                                                      #
########################################################################

class RoiHandler:
    """For handling D-Bus calls to zoomRegion.getRoi() asynchronously
    """
    def __init__(self, left=0, top=0, width=0, height=0, centerX=0, centerY=0,
                 edgeMarginX=0, edgeMarginY=0):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.centerX = centerX
        self.centerY = centerY
        self.edgeMarginX = edgeMarginX
        self.edgeMarginY = edgeMarginY

    def setRoiCenter(self, reply):
        """Given a region of interest, put that at the center of the magnifier.

        Arguments:
        - reply:  an array defining a rectangle [left, top, right, bottom]
        """
        roiWidth = reply[2] - reply[0]
        roiHeight = reply[3] - reply[1]
        if self.width > roiWidth:
            self.centerX = self.left
        if self.height > roiHeight:
            self.centerY = self.top
        _setROICenter(self.centerX, self.centerY)

    def setRoiCursorPush(self, reply):
        """Given a region of interest, nudge it if the caret or control is not
        visible.

        Arguments:
        - reply:  an array defining a rectangle [left, top, right, bottom]
        """
        # Determine if the accessible is partially to the left, right,
        # above, or below the current region of interest (ROI).
        #
        roiLeft = reply[0]
        roiTop = reply[1]
        roiWidth = reply[2] - roiLeft
        roiHeight = reply[3] - roiTop
        leftOfROI = (self.left - self.edgeMarginX) <= roiLeft
        rightOfROI = \
            (self.left + self.width + self.edgeMarginX) >= (roiLeft + roiWidth)
        aboveROI = (self.top - self.edgeMarginY)  <= roiTop
        belowROI = \
            (self.top + self.height + self.edgeMarginY) >= (roiTop + roiHeight)

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
        x1 = roiLeft
        x2 = roiLeft + roiWidth
        y1 = roiTop
        y2 = roiTop + roiHeight

        if leftOfROI:
            x1 = max(0, self.left - self.edgeMarginX)
            x2 = x1 + roiWidth
        elif rightOfROI:
            self.left = min(_screenWidth, self.left + self.edgeMarginX)
            if self.width > roiWidth:
                x1 = self.left
                x2 = x1 + roiWidth
            else:
                x2 = self.left + self.width
                x1 = x2 - roiWidth

        if aboveROI:
            y1 = max(0, self.top - self.edgeMarginY)
            y2 = y1 + roiHeight
        elif belowROI:
            self.top = min(_screenHeight, self.top + self.edgeMarginY)
            if self.height > roiHeight:
                y1 = self.top
                y2 = y1 + roiHeight
            else:
                y2 = self.top + self.height
                y1 = y2 - roiHeight

        _setROICenter((x1 + x2) / 2, (y1 + y2) / 2)

    def setRoiCenterErr(self, error):
        _dbusCallbackError('_setROICenter()', error)

    def setRoiCursorPushErr(self, error):
        _dbusCallbackError('_setROICursorPush()', error)

    def magnifyAccessibleErr(self, error):
        _dbusCallbackError('magnifyAccessible()', error)

def _dbusCallbackError(funcName, error):
    """Log D-Bus errors

    Arguments:
    - funcName: The name of the gsmag function that made the D-Bus call.
    - error: The error that D-Bus returned.
    """
    logLine = funcName + ' failed: ' + str(error)
    debug.println(debug.LEVEL_WARNING, logLine)

########################################################################
#                                                                      #
# Methods for magnifying objects                                       #
#                                                                      #
########################################################################

def _setROICenter(x, y):
    """Centers the region of interest around the given point.

    Arguments:
    - x: integer in unzoomed system coordinates representing x component
    - y: integer in unzoomed system coordinates representing y component
    """
    _zoomer.shiftContentsTo(x, y, ignore_reply=True)

def _setROICursorPush(x, y, width, height, edgeMargin = 0):
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
    # [[[WDW - probably should not make a D-Bus call each time.]]]
    #
    edgeMargin = min(edgeMargin, 50)/100.00
    edgeMarginX = edgeMargin * _screenWidth/settings.magZoomFactor
    edgeMarginY = edgeMargin * _screenHeight/settings.magZoomFactor

    # Determine if the accessible is partially to the left, right,
    # above, or below the current region of interest (ROI).
    # [[[WDW - probably should not make a D-Bus call each time.]]]
    #
    roiPushHandler = RoiHandler(x, y, width, height,
                                edgeMarginX=edgeMarginX,
                                edgeMarginY=edgeMarginY)
    _zoomer.getRoi(reply_handler=roiPushHandler.setRoiCursorPush,
                   error_handler=roiPushHandler.setRoiCursorPushErr)

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
                _setROICenter(x, y)
            elif _textTracking == settings.MAG_TRACKING_MODE_PUSH:
                _setROICursorPush(x, y, width, height, _edgeMargin)
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
            # [[[WDW - probably should not make a getRoi call each time]]]
            #
            roiCenterHandler = RoiHandler(x, y, width, height, centerX, centerY)
            _zoomer.getRoi(reply_handler=roiCenterHandler.setRoiCenter,
                           error_handler=roiCenterHandler.magnifyAccessibleErr)

        elif _controlTracking == settings.MAG_TRACKING_MODE_PUSH:
            _setROICursorPush(x, y, width, height)

########################################################################
#                                                                      #
# Methods for updating appearance settings                             #
#                                                                      #
########################################################################

def applySettings():
    """Looks at the user settings and applies them to the magnifier."""
    global _mouseTracking
    global _controlTracking
    global _textTracking
    global _edgeMargin
    global _pointerFollowsZoomer
    global _pointerFollowsFocus

    __setupMagnifier(settings.magZoomerType)
    __setupZoomer(settings.magZoomerType)

    _mouseTracking = settings.magMouseTrackingMode
    _controlTracking = settings.magControlTrackingMode
    _textTracking = settings.magTextTrackingMode
    _edgeMargin = settings.magEdgeMargin
    _pointerFollowsZoomer = settings.magPointerFollowsZoomer
    _pointerFollowsFocus = settings.magPointerFollowsFocus

def hideSystemPointer(hidePointer):
    """Hide or show the system pointer.

    Arguments:
    -hidePointer: If True, hide the system pointer, otherwise show it.
    """
    try:
        if hidePointer:
            _magnifier.hideCursor(ignore_reply=True)
        else:
            _magnifier.showCursor(ignore_reply=True)
    except:
        debug.printException(debug.LEVEL_FINEST)

def __setupMagnifier(position, restore=None):
    """Creates the magnifier in the position specified.

    Arguments:
    - position: the position/type of zoomer (full, left half, etc.)
    - restore:  a dictionary of all of the settings which should be restored
    """

    global _fullScreenCapable

    if not restore:
        restore = {}

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
       and position == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
        hideSystemPointer(True)
    else:
        hideSystemPointer(False)

    orca_state.zoomerType = position
    updateTarget = True

    enableCrossHair = restore.get('enableMagCrossHair',
                                  settings.enableMagCrossHair)

    orca_state.mouseEnhancementsEnabled = enableCrossHair

def __setupZoomer(position, left=None, top=None, right=None, bottom=None,
                  restore=None):
    """Creates a zoomer in the magnifier.
    The position of the zoomer onscreen is based on the given arguments.  If
    none are supplied, defaults to the settings for the given zoomer position.

    Arguments:
    - position: position of the zoomer view port (top half, left half, custom)
    - left:     left edge of zoomer's viewport (for custom -- optional)
    - top:      top edge of zoomer's viewport (for custom -- optional)
    - right:    right edge of zoomer's viewport (for custom -- optional)
    - bottom:   bottom edge of zoomer's viewport (for custom -- optional)
    - restore:  dictionary of the settings; used for zoom factor (optional)
    """

    global _zoomer
    global _roiWidth
    global _roiHeight

    if not restore:
        restore = {}

    # full screen is the default.
    #
    prefLeft = 0
    prefTop = 0
    prefRight = prefLeft + _screenWidth
    prefBottom = prefTop + _screenHeight

    if position == settings.MAG_ZOOMER_TYPE_TOP_HALF:
        prefBottom = prefTop + _screenHeight/2
    elif position == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
        prefTop = _screenHeight/2
        prefBottom = prefTop + _screenHeight/2
    elif position == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
        prefRight = prefLeft + _screenWidth/2
    elif position == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
        prefLeft = _screenWidth/2
        prefRight = prefLeft + _screenWidth/2
    elif position == settings.MAG_ZOOMER_TYPE_CUSTOM:
        prefLeft = settings.magZoomerLeft if left == None else left
        prefTop = settings.magZoomerTop if top == None else top
        prefRight = settings.magZoomerRight if right == None else right
        prefBottom = settings.magZoomerBottom if bottom == None else bottom

    magFactor = restore.get('magZoomFactor', settings.magZoomFactor)
    viewWidth = prefRight - prefLeft
    viewHeight = prefBottom - prefTop
    _roiWidth = viewWidth / magFactor
    _roiHeight = viewHeight / magFactor

    debug.println(debug.LEVEL_ALL,
                  "Magnifier zoomer ROI size desired: width=%d, height=%d)" \
                  % (_roiWidth, _roiHeight))

    # If there are zoom regions, use the first one; otherwise create one.
    #
    zoomerPaths = _magnifier.getZoomRegions()
    if len(zoomerPaths) > 0:
        zoomProxy = _bus.get_object('org.gnome.Magnifier', zoomerPaths[0])
        _zoomer = dbus.Interface(zoomProxy,
                                dbus_interface='org.gnome.Magnifier.ZoomRegion')
        _zoomer.setMagFactor(magFactor, magFactor)
        _zoomer.moveResize([prefLeft, prefTop, prefRight, prefBottom])
    else:
        zoomerPath = _magnifier.createZoomRegion(
            magFactor, magFactor,
	        [0, 0, _roiWidth, _roiHeight],
	        [prefLeft, prefTop, prefRight, prefBottom])
        zoomProxy = _bus.get_object('org.gnome.Magnifier', zoomerPath)
        _zoomer = dbus.Interface(zoomProxy,
                                dbus_interface='org.gnome.Magnifier.ZoomRegion')
        _magnifier.addZoomRegion(zoomerPath)

    __updateROIDimensions()

def __updateROIDimensions():
    """Updates the ROI width, height, and maximum and minimum values.
    """
    global _roiWidth
    global _roiHeight
    global _minROIX
    global _minROIY
    global _maxROIX
    global _maxROIY

    roi = _zoomer.getRoi()
    _roiWidth = roi[2] - roi[0]
    _roiHeight = roi[3] - roi[1]

    _minROIX = _roiWidth / 2
    _minROIY = _roiHeight / 2

    _maxROIX = _screenWidth - (_roiWidth / 2)
    _maxROIY = _screenHeight - (_roiHeight / 2)

    debug.println(debug.LEVEL_ALL,
                  "Magnifier ROI min/max center: (%d, %d), (%d, %d)" \
                  % (_minROIX, _minROIY, _maxROIX, _maxROIY))

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

    __setupMagnifier(position, restore)
    __setupZoomer(position, left, top, right, bottom, restore)

########################################################################
#                                                                      #
# Methods for obtaining magnifier capabilities                         #
#                                                                      #
########################################################################

def isFilteringCapable():
    """Returns True if we're able to take advantage of libcolorblind's color
    filtering.
    """
    # [[[WDW - To be implemented]]]
    return False

def isFullScreenCapable():
    """Returns True if we are capable of doing full screen (i.e. whether
    composite is being used.
    """
    return True

########################################################################
#                                                                      #
# Methods for starting and stopping the magnifier                      #
#                                                                      #
########################################################################

def init():
    """Initializes the magnifier, bringing the magnifier up on the
    display.

    Returns True if the initialization procedure was run or False if this
    module has already been initialized.
    """
    global _initialized
    global _isActive
    global _wasActiveOnInit

    if _initialized:
        return False

    try:
        _initialized = True
        _wasActiveOnInit = _magnifier.isActive()
        applySettings()
        _magnifier.setActive(True)
        _isActive = _magnifier.isActive()
        return True

    except:
        _initialized = False
        raise
    
def shutdown():
    """Shuts down the magnifier module.
    Returns True if the shutdown procedure was run or False if this
    module has not been initialized.
    """

    global _initialized
    global _isActive

    if not _initialized:
        return False

    _magnifier.setActive(_wasActiveOnInit)
    _isActive = _magnifier.isActive()
    if not _isActive:
        hideSystemPointer(False)

    _initialized = False
    return True
