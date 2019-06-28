# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2018-2019 Igalia, S.L.
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

"""Provides support for synthesizing accessible input events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2018 Igalia, S.L."
__license__   = "LGPL"

import gi
import pyatspi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import debug

try:
    _canScrollTo = pyatspi.Component.scrollTo is not None
except:
    _canScrollTo = False

def _getMouseCoordinates():
    """Returns the current mouse coordinates."""

    rootWindow = Gtk.Window().get_screen().get_root_window()
    window, x, y, modifiers = rootWindow.get_pointer()
    msg = "EVENT SYNTHESIZER: Mouse coordinates: %d,%d" % (x, y)
    debug.println(debug.LEVEL_INFO, msg, True)
    return x, y

def _generateMouseEvent(x, y, event):
    """Synthesize a mouse event at a specific screen coordinate."""

    oldX, oldY = _getMouseCoordinates()

    msg = "EVENT SYNTHESIZER: Generating %s mouse event at %d,%d" % (event, x, y)
    debug.println(debug.LEVEL_INFO, msg, True)
    pyatspi.Registry.generateMouseEvent(x, y, event)

    newX, newY = _getMouseCoordinates()
    if oldX == newX and oldY == newY and (oldX, oldY) != (x, y):
        msg = "EVENT SYNTHESIZER: Mouse event possible failure. Pointer didn't move"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    return True

def _mouseEventOnCharacter(obj, event):
    """Performs the specified mouse event on the current character in obj."""

    text = obj.queryText()
    extents = text.getCharacterExtents(text.caretOffset, pyatspi.DESKTOP_COORDS)
    x = max(extents[0], extents[0] + (extents[2] / 2) - 1)
    y = extents[1] + extents[3] / 2
    return _generateMouseEvent(x, y, event)

def _mouseEventOnObject(obj, event):
    """Performs the specified mouse event on obj."""

    extents = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
    x = extents.x + extents.width/2
    y = extents.y + extents.height/2
    return _generateMouseEvent(x, y, event)

def routeToCharacter(obj):
    """Routes the pointer to the current character in obj."""

    return _mouseEventOnCharacter(obj, "abs")

def routeToObject(obj):
    """Moves the mouse pointer to the center of obj."""

    return _mouseEventOnObject(obj, "abs")

def routeToPoint(x, y):
    """Routes the pointer to the specified coordinates."""

    return _generateMouseEvent(x, y, "abs")

def clickCharacter(obj, button=1):
    """Single click on the current character in obj using the specified button."""

    return _mouseEventOnCharacter(obj, "b%dc" % button)

def clickObject(obj, button=1):
    """Single click on obj using the specified button."""

    return _mouseEventOnObject(obj, "b%dc" % button)

def clickPoint(x, y, button=1):
    """Single click on the given point using the specified button."""

    return _generateMouseEvent(x, y, "b%dc" % button)

def doubleClickCharacter(obj, button=1):
    """Double click on the current character in obj using the specified button."""

    return _mouseEventOnCharacter(obj, "b%dd" % button)

def doubleClickObject(obj, button=1):
    """Double click on obj using the specified button."""

    return _mouseEventOnObject(obj, "b%dd" % button)

def doubleClickPoint(x, y, button=1):
    """Double click on the given point using the specified button."""

    return _generateMouseEvent(x, y, "b%dd" % button)

def pressAtCharacter(obj, button=1):
    """Performs a press on the current character in obj using the specified button."""

    return _mouseEventOnCharacter(obj, "b%dp" % button)

def pressAtObject(obj, button=1):
    """Performs a press on obj using the specified button."""

    return _mouseEventOnObject(obj, "b%dp" % button)

def pressAtPoint(x, y, button=1):
    """Performs a press on the given point using the specified button."""

    return _generateMouseEvent(x, y, "b%dp" % button)

def releaseAtCharacter(obj, button=1):
    """Performs a release on the current character in obj using the specified button."""

    return _mouseEventOnCharacter(obj, "b%dr" % button)

def releaseAtObject(obj, button=1):
    """Performs a release on obj using the specified button."""

    return _mouseEventOnObject(obj, "b%dr" % button)

def releaseAtPoint(x, y, button=1):
    """Performs a release on the given point using the specified button."""

    return _generateMouseEvent(x, y, "b%dr" % button)

def scrollToPoint(obj, x, y):
    """Attemps to scroll obj to the specified point."""

    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    try:
        component = obj.queryComponent()
    except:
        msg = "ERROR: Exception querying component of %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    before = component.getExtents(pyatspi.WINDOW_COORDS)
    try:
        component.scrollToPoint(pyatspi.WINDOW_COORDS, x, y)
    except:
        msg = "ERROR: Exception scrolling %s to %i,%i." % (obj, x, y)
        debug.println(debug.LEVEL_INFO, msg, True)
    else:
        msg = "INFO: Attemped to scroll %s to %i,%i" % (obj, x, y)
        debug.println(debug.LEVEL_INFO, msg, True)

    after = component.getExtents(pyatspi.WINDOW_COORDS)
    msg = "EVENT SYNTHESIZER: Before scroll: %i,%i. After scroll: %i,%i." % \
          (before[0], before[1], after[0], after[1])
    debug.println(debug.LEVEL_INFO, msg, True)

def _scrollToLocation(obj, location):
    """Attemps to scroll obj to the specified location."""

    try:
        component = obj.queryComponent()
    except:
        msg = "ERROR: Exception querying component of %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    before = component.getExtents(pyatspi.WINDOW_COORDS)
    try:
        component.scrollTo(location)
    except:
        msg = "ERROR: Exception scrolling %s to %s." % (obj, location)
        debug.println(debug.LEVEL_INFO, msg, True)
    else:
        msg = "INFO: Attemped to scroll %s to %s" % (obj, location)
        debug.println(debug.LEVEL_INFO, msg, True)

    after = component.getExtents(pyatspi.WINDOW_COORDS)
    msg = "EVENT SYNTHESIZER: Before scroll: %i,%i. After scroll: %i,%i." % \
          (before[0], before[1], after[0], after[1])
    debug.println(debug.LEVEL_INFO, msg, True)

def scrollIntoView(obj):
    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    _scrollToLocation(obj, pyatspi.SCROLL_ANYWHERE)

def scrollToTopEdge(obj):
    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    _scrollToLocation(obj, pyatspi.SCROLL_TOP_EDGE)

def scrollToTopLeft(obj):
    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    _scrollToLocation(obj, pyatspi.SCROLL_TOP_LEFT)

def scrollToLeftEdge(obj):
    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    _scrollToLocation(obj, pyatspi.SCROLL_LEFT_EDGE)

def scrollToBottomEdge(obj):
    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    _scrollToLocation(obj, pyatspi.SCROLL_BOTTOM_EDGE)

def scrollToBottomRight(obj):
    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    _scrollToLocation(obj, pyatspi.SCROLL_BOTTOM_RIGHT)

def scrollToRightEdge(obj):
    if not _canScrollTo:
        msg = "INFO: Installed version of AT-SPI2 doesn't support scrolling."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    _scrollToLocation(obj, pyatspi.SCROLL_RIGHT_EDGE)
