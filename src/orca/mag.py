# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011 The Orca Team
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

# NOTE: This is an interim step in the plan for Orca to co-exist
# with various magnification solutions rather than to drive them.
# Orca should only fall back on this module if gnome-shell mag is
# unavailable. And in a GNOME 3 environment, there are no other
# magnification solutions. Hence the lack of functionality. ;-)

def applySettings():
    pass

def magnifyAccessible(event, obj, extents=None):
    pass

def init():
    return False

def shutdown():
    return False

def setupMagnifier(position, left=None, top=None, right=None, bottom=None,
                   restore=None):
    pass

def setMagnifierCursor(enabled, customEnabled, size, updateScreen=True):
    pass

def setMagnifierCrossHair(enabled, updateScreen=True):
    pass

def setMagnifierCrossHairClip(enabled, updateScreen=True):
    pass

def setZoomerColorInversion(enabled, updateScreen=True):
    pass

def setZoomerBrightness(red=0, green=0, blue=0, updateScreen=True):
    pass

def setZoomerContrast(red=0, green=0, blue=0, updateScreen=True):
    pass

def setMagnifierObjectSize(magProperty, size, updateScreen=True):
    pass

def setZoomerObjectSize(magProperty, size, updateScreen=True):
    pass

def setZoomerObjectColor(magProperty, colorSetting, updateScreen=True):
    pass

def setMagnifierObjectColor(magProperty, colorSetting, updateScreen=True):
    pass

def setZoomerMagFactor(x, y, updateScreen=True):
    pass

def setZoomerSmoothingType(smoothingType, updateScreen=True):
    pass

def setZoomerColorFilter(colorFilter, updateScreen=True):
    pass

def hideSystemPointer(hidePointer):
    pass

def isFullScreenCapable():
    return False

def isFilteringCapable():
    return False

def updateMouseTracking(newMode):
    pass

def updateControlTracking(newMode):
    pass

def updateTextTracking(newMode):
    pass

def updateEdgeMargin(amount):
    pass

def updatePointerFollowsFocus(enabled):
    pass

def updatePointerFollowsZoomer(enabled):
    pass

def finishLiveUpdating():
    pass

def toggleColorEnhancements(script=None, inputEvent=None):
    pass

def toggleMouseEnhancements(script=None, inputEvent=None):
    pass

def increaseMagnification(script=None, inputEvent=None):
    pass

def decreaseMagnification(script=None, inputEvent=None):
    pass

def toggleMagnifier(script=None, inputEvent=None):
    pass

def cycleZoomerType(script=None, inputEvent=None):
    pass
