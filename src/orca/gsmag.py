# Orca
#
# Copyright 2009 Sun Microsystems Inc.
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

"""Manages the GNOME Shell magnifier interface for orca.  [[[TODO: WDW
- this is very very early in development.  One might even say it is
pre-prototype.]]]"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2009 Sun Microsystems Inc."
__license__   = "LGPL"

import dbus
_bus = dbus.SessionBus()
_proxy_obj = _bus.get_object("org.gnome.Shell", "/org/gnome/Shell/Magnifier")
_magnifier = dbus.Interface(_proxy_obj, "org.gnome.Shell.Magnifier")

import eventsynthesizer
import settings
import speech

# If True, the magnifier is active
#
_isActive = False

# Whether or not we're in the process of making "live update" changes
# to the location of the magnifier.
#
_liveUpdatingMagnifier = False

# The current modes of tracking, for use with "live update" changes.
#
_controlTracking = None
_edgeMargin = None
_mouseTracking = None
_pointerFollowsZoomer = None
_pointerFollowsFocus = None
_textTracking = None

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
    _magnifier.shiftContentsTo(x, y)

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
    (screenWidth, screenHeight) = _magnifier.getScreenSize()
    edgeMargin = min(edgeMargin, 50)/100.00
    edgeMarginX = edgeMargin * screenWidth/settings.magZoomFactor
    edgeMarginY = edgeMargin * screenHeight/settings.magZoomFactor

    # Determine if the accessible is partially to the left, right,
    # above, or below the current region of interest (ROI).
    # [[[WDW - probably should not make a D-Bus call each time.]]]
    #
    (roiLeft, roiTop, roiWidth, roiHeight) = _magnifier.getROI()
    leftOfROI = (x - edgeMarginX) <= roiLeft
    rightOfROI = (x + width + edgeMarginX) >= (roiLeft + roiWidth)
    aboveROI = (y - edgeMarginY)  <= roiTop
    belowROI = (y + height + edgeMarginY) >= (roiTop + roiHeight)

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
        x1 = max(0, x - edgeMarginX)
        x2 = x1 + roiWidth
    elif rightOfROI:
        x = min(screenWidth - 1, x + edgeMarginX)
        if width > roiWidth:
            x1 = x
            x2 = x1 + roiWidth
        else:
            x2 = x + width
            x1 = x2 - roiWidth

    if aboveROI:
        y1 = max(0, y - edgeMarginY)
        y2 = y1 + roiHeight
    elif belowROI:
        y = min(screenHeight - 1, y + edgeMarginY)
        if height > roiHeight:
            y1 = y
            y2 = y1 + roiHeight
        else:
            y2 = y + height
            y1 = y2 - roiHeight

    _setROICenter((x1 + x2) / 2, (y1 + y2) / 2)

def magnifyAccessible(event, obj, extents=None):
    """Sets the region of interest to the upper left of the given
    accessible, if it implements the Component interface.  Otherwise,
    does nothing.

    Arguments:
    - event: the Event that caused this to be called
    - obj: the accessible
    """
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
            #
            if width > _roiWidth:
                centerX = x
            if height > _roiHeight:
                centerY = y

            _setROICenter(centerX, centerY)
        elif _controlTracking == settings.MAG_TRACKING_MODE_PUSH:
            _setROICursorPush(x, y, width, height)

########################################################################
#                                                                      #
# Methods for updating live tracking settings                          #
#                                                                      #
########################################################################

def updateControlTracking(newMode):
    """Updates the control tracking mode.

    Arguments:
    -newMode: The new mode to use.
    """
    global _controlTracking
    _controlTracking = newMode
    
def updateEdgeMargin(amount):
    """Updates the edge margin

    Arguments:
    -amount: The new margin to use, in pixels.
    """
    global _edgeMargin
    _edgeMargin = amount

def updateMouseTracking(newMode):
    """Updates the mouse tracking mode.

    Arguments:
    -newMode: The new mode to use.
    """
    global _mouseTracking
    _mouseTracking = newMode

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

def updateTextTracking(newMode):
    """Updates the text tracking mode.

    Arguments:
    -newMode: The new mode to use.
    """
    global _textTracking
    _textTracking = newMode

def finishLiveUpdating():
    """Restores things that were altered via a live update."""

    global _liveUpdatingMagnifier
    global _controlTracking
    global _edgeMargin
    global _mouseTracking
    global _pointerFollowsFocus
    global _pointerFollowsZoomer
    global _textTracking

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

########################################################################
#                                                                      #
# Methods for updating appearance settings                             #
#                                                                      #
########################################################################

def _setScreenPosition(position):
    if position == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
        positionString = "Full Screen"
    elif position == settings.MAG_ZOOMER_TYPE_TOP_HALF:
        positionString = "Top Half"
    elif position == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
        positionString = "Bottom Half"
    elif position == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
        positionString = "Left Half"
    elif position == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
        positionString = "Right Half"
    else:
        positionString = "Full Screen"
    _magnifier.setScreenPosition(positionString)
    
def applySettings():
    """Looks at the user settings and applies them to the magnifier."""
    global _mouseTracking
    global _controlTracking
    global _textTracking
    global _edgeMargin
    global _pointerFollowsZoomer
    global _pointerFollowsFocus

    _magnifier.setMagFactor(settings.magZoomFactor, settings.magZoomFactor)
    _setScreenPosition(settings.magZoomerType)
  
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
    # [[[WDW - To be implemented]]]
    pass

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
    # [[[WDW - To be implemented]]]
    global _liveUpdatingMagnifier
    _liveUpdatingMagnifier = True

def setMagnifierCursor(enabled, customEnabled, size, updateScreen=True):
    """Sets the cursor.

    Arguments:
    - enabled:        Whether or not the cursor should be enabled
    - customEnabled:  Whether or not a custom size has been enabled
    - size:           The size it should be set to
    - updateScreen:   Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setMagnifierCrossHair(enabled, updateScreen=True):
    """Sets the cross-hair.

    Arguments:
    - enabled: Whether or not the cross-hair should be enabled
    - updateScreen:  Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setMagnifierCrossHairClip(enabled, updateScreen=True):
    """Sets the cross-hair clip.

    Arguments:
    - enabled: Whether or not the cross-hair clip should be enabled
    - updateScreen:   Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setMagnifierObjectColor(magProperty, colorSetting, updateScreen=True):
    """Sets the specified magnifier property to the specified color.

    Arguments:
    - magProperty:  The property to set (as a string)
    - colorSetting: The Orca color setting to apply
    - updateScreen:  Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setMagnifierObjectSize(magProperty, size, updateScreen=True):
    """Sets the specified magnifier property to the specified size.

    Arguments:
    - magProperty:   The property to set (as a string)
    - size:          The size to apply
    - updateScreen:  Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

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
    # [[[WDW - To be implemented]]]
    pass

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
    # [[[WDW - To be implemented]]]
    pass

def setZoomerColorFilter(colorFilter, updateScreen=True):
    """Sets the zoomer's color filter.

    Arguments:
    - colorFilter: The color filter to apply
    - updateScreen:  Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setZoomerColorInversion(enabled, updateScreen=True):
    """Sets the color inversion.

    Arguments:
    - enabled: Whether or not color inversion should be enabled
    - updateScreen:   Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setZoomerMagFactor(x, y, updateScreen=True):
    """Sets the magnification level.

    Arguments:
    - x: The horizontal magnification level
    - y: The vertical magnification level
    - updateScreen:  Whether or not to update the screen
    """
    _magnifier.setMagFactor(x, y)

def setZoomerObjectColor(magProperty, colorSetting, updateScreen=True):
    """Sets the specified zoomer property to the specified color.

    Arguments:
    - magProperty:  The property to set (as a string)
    - colorSetting: The Orca color setting to apply
    - updateScreen:  Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setZoomerObjectSize(magProperty, size, updateScreen=True):
    """Sets the specified zoomer property to the specified size.

    Arguments:
    - magProperty:   The property to set (as a string)
    - size:          The size to apply
    - updateScreen:  Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

def setZoomerSmoothingType(smoothingType, updateScreen=True):
    """Sets the zoomer's smoothing type.

    Arguments:
    - smoothingType: The type of smoothing to use
    - updateScreen:  Whether or not to update the screen
    """
    # [[[WDW - To be implemented]]]
    pass

########################################################################
#                                                                      #
# Methods for changing settings via keyboard/mouse events              #
#                                                                      #
########################################################################

def cycleZoomerType(script=None, inputEvent=None):
    """Allows the user to cycle through the available zoomer types."""
    # [[[WDW - To be implemented]]]
    pass

def decreaseMagnification(script=None, inputEvent=None):
    """Decreases the magnification level."""
    # [[[WDW - To be implemented]]]
    pass

def increaseMagnification(script=None, inputEvent=None):
    """Increases the magnification level."""
    # [[[WDW - To be implemented]]]
    pass

def toggleColorEnhancements(script=None, inputEvent=None):
    """Toggles the color enhancements on/off."""
    # [[[WDW - To be implemented]]]
    pass

def toggleMouseEnhancements(script=None, inputEvent=None):
    """Toggles the mouse enhancements on/off."""
    # [[[WDW - To be implemented]]]
    pass

def toggleMagnifier(script=None, inputEvent=None):
    """Toggles the magnifier."""
    if not _magnifier.isActive():
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
    global _isActive
    _magnifier.setActive(True)
    applySettings()
    _isActive = _magnifier.isActive()
    
def shutdown():
    global _isActive
    _magnifier.setActive(False)
    _isActive = _magnifier.isActive()
