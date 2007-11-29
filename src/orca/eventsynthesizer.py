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

"""Provides support for synthesizing keyboard and mouse events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import debug

def generateMouseEvent(x, y, eventName):
    """Synthesize a mouse event at a specific screen coordinate.
    Most AT clients should use the #AccessibleAction interface when
    tempted to generate mouse events, rather than this method.

    Event names: b1p = button 1 press; b2r = button 2 release;
                 b3c = button 3 click; b2d = button 2 double-click;
                 abs = absolute motion; rel = relative motion.

    Arguments:
    - x: the x screen coordinate
    - y: the y screen coordinate
    - eventName: the event name string (as described above)
    """

    debug.println(debug.LEVEL_FINER,
                  "SYNTHESIZING MOUSE EVENT: (%d, %d) %s"\
                  % (x, y, eventName))

    pyatspi.Registry.generateMouseEvent(x, y, eventName)

def clickObject(obj, button):
    """Performs a button click on the given Accessible.

    Arguments:
    - obj: the Accessible
    - button: an integer representing the mouse button number
    """
    extents = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
    x = extents.x + extents.width/2
    y = extents.y + extents.height/2
    generateMouseEvent(x, y, "b%dc" % button)

def clickPoint(x, y, button):
    """Performs a button click on the given point.

    Arguments:
    - obj: the Accessible
    - x, y: the point
    - button: an integer representing the mouse button number
    """

    generateMouseEvent(x, y, "b%dc" % button)

def generateKeyboardEvent(keycode, keystring, eventType):
    """Generates a keyboard event.

    Arguments:
    - keyval: a long integer indicating the keycode or keysym of the key event
              being synthesized.
    - keystring: an (optional) UTF-8 string which, if keyval is NULL,
              indicates a 'composed' keyboard input string which is
              being synthesized; this type of keyboard event synthesis does
              not emulate hardware keypresses but injects the string
              as though a composing input method (such as XIM) were used.
    - eventType: an AccessibleKeySynthType flag indicating whether keyval
              is to be interpreted as a keysym rather than a keycode
              (pyatspi.KEY_SYM), or whether to synthesize
              KEY_PRESS, KEY_RELEASE, or both (KEY_PRESSRELEASE).
    """

    pyatspi.Registry.generateKeyboardEvent(keycode, keystring, eventType)
