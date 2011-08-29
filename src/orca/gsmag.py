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

"""Implements cursor and focus tracking for gnome-shell mag."""

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

# If True, the magnifier is active
#
_isActive = False

from gi.repository import Gdk
_display = Gdk.Display.get_default()
_screen = _display.get_default_screen()
_screenWidth = _screen.get_width()
_screenHeight = _screen.get_height()

# If True, this module has been initialized.
#
_initialized = False
_wasActiveOnInit = False

# The current region of interest as specified by the upper left corner.
#
_roi = None

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

def _setROICursorPush(x, y, width, height):
    """Nudges the ROI if the caret or control is not visible.

    Arguments:
    - x: integer in unzoomed system coordinates representing x component
    - y: integer in unzoomed system coordinates representing y component
    - width: integer in unzoomed system coordinates representing the width
    - height: integer in unzoomed system coordinates representing the height
    """

    # Determine if the accessible is partially to the left, right,
    # above, or below the current region of interest (ROI).
    # [[[WDW - probably should not make a D-Bus call each time.]]]
    #
    roiPushHandler = RoiHandler(x, y, width, height)
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
            # Orca no longer has settings related to magnification. For settings
            # not (or not yet) implemented by gnome-shell mag, we'll just do the
            # equivalent of Orca's default behavior.
            #
            # For tracking with respect to text/caret, Orca's default was push.
            # The default "edge margin" was 0, so we'll eliminate edge margin.
            _setROICursorPush(x, y, width, height)
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
        # Orca no longer has settings related to magnification. For settings
        # not (or not yet) implemented by gnome-shell mag, we'll just do the
        # equivalent of Orca's default behavior.
        #
        # For tracking with respect to controls/widgets, Orca's default was
        # push.
        _setROICursorPush(x, y, width, height)

########################################################################
#                                                                      #
# Methods for starting and stopping the magnifier                      #
#                                                                      #
########################################################################

def init():
    """Initializes the magnifier with respect to Orca so that Orca can
    handle caret and focus tracking.

    Returns True if the initialization procedure was run or False if this
    module has already been initialized.
    """
    global _initialized
    global _isActive
    global _wasActiveOnInit
    global _zoomer

    if _initialized:
        return False

    try:
        _initialized = True
        _wasActiveOnInit = _magnifier.isActive()

        zoomerPaths = _magnifier.getZoomRegions()
        if len(zoomerPaths) > 0:
            zoomProxy = _bus.get_object('org.gnome.Magnifier', zoomerPaths[0])
            _zoomer = dbus.Interface(
                zoomProxy, dbus_interface='org.gnome.Magnifier.ZoomRegion')

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

    _initialized = False
    return True
