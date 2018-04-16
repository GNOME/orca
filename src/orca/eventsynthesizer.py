# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2018 Igalia, S.L.
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

import pyatspi
from . import debug

def _generateMouseEvent(x, y, event):
    """Synthesize a mouse event at a specific screen coordinate."""

    msg = "EVENT SYNTHESIZER: Generating %s mouse event at %d,%d" % (event, x, y)
    debug.println(debug.LEVEL_INFO, msg, True)
    pyatspi.Registry.generateMouseEvent(x, y, event)

def _mouseEventOnCharacter(obj, event):
    """Performs the specified mouse event on the current character in obj."""

    text = obj.queryText()
    extents = text.getCharacterExtents(text.caretOffset, pyatspi.DESKTOP_COORDS)
    x = max(extents[0], extents[0] + (extents[2] / 2) - 1)
    y = extents[1] + extents[3] / 2
    _generateMouseEvent(x, y, event)

def _mouseEventOnObject(obj, event):
    """Performs the specified mouse event on obj."""

    extents = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
    x = extents.x + extents.width/2
    y = extents.y + extents.height/2
    _generateMouseEvent(x, y, event)

def routeToCharacter(obj):
    """Routes the pointer to the current character in obj."""

    _mouseEventOnCharacter(obj, "abs")

def routeToObject(obj):
    """Moves the mouse pointer to the center of obj."""

    _mouseEventOnObject(obj, "abs")

def routeToPoint(x, y):
    """Routes the pointer to the specified coordinates."""

    _generateMouseEvent(x, y, "abs")

def clickCharacter(obj, button=1):
    """Single click on the current character in obj using the specified button."""

    _mouseEventOnCharacter(obj, "b%dc" % button)

def clickObject(obj, button=1):
    """Single click on obj using the specified button."""

    _mouseEventOnObject(obj, "b%dc" % button)

def clickPoint(x, y, button=1):
    """Single click on the given point using the specified button."""

    _generateMouseEvent(x, y, "b%dc" % button)

def doubleClickCharacter(obj, button=1):
    """Double click on the current character in obj using the specified button."""

    _mouseEventOnCharacter(obj, "b%dd" % button)

def doubleClickObject(obj, button=1):
    """Double click on obj using the specified button."""

    _mouseEventOnObject(obj, "b%dd" % button)

def doubleClickPoint(x, y, button=1):
    """Double click on the given point using the specified button."""

    _generateMouseEvent(x, y, "b%dd" % button)

def pressAtCharacter(obj, button=1):
    """Performs a press on the current character in obj using the specified button."""

    _mouseEventOnCharacter(obj, "b%dp" % button)

def pressAtObject(obj, button=1):
    """Performs a press on obj using the specified button."""

    _mouseEventOnObject(obj, "b%dp" % button)

def pressAtPoint(x, y, button=1):
    """Performs a press on the given point using the specified button."""

    _generateMouseEvent(x, y, "b%dp" % button)

def releaseAtCharacter(obj, button=1):
    """Performs a release on the current character in obj using the specified button."""

    _mouseEventOnCharacter(obj, "b%dr" % button)

def releaseAtObject(obj, button=1):
    """Performs a release on obj using the specified button."""

    _mouseEventOnObject(obj, "b%dr" % button)

def releaseAtPoint(x, y, button=1):
    """Performs a release on the given point using the specified button."""

    _generateMouseEvent(x, y, "b%dr" % button)


