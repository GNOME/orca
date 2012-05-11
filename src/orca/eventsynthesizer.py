# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Provides support for synthesizing keyboard and mouse events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
from . import debug

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

def routeToCharacter(obj):
    """Moves the mouse pointer to the given character

    Arguments:
    - obj: the Accessible which implements the accessible text
      interface
    """
    text = obj.queryText()
    # We try to move to the left of center.  This is to
    # handle toolkits that will offset the caret position to
    # the right if you click dead on center of a character.
    #
    extents = text.getCharacterExtents(text.caretOffset,
                                       pyatspi.DESKTOP_COORDS)
    x = max(extents[0], extents[0] + (extents[2] / 2) - 1)
    y = extents[1] + extents[3] / 2
    routeToPoint(x, y, "abs")

def routeToObject(obj):
    """Moves the mouse pointer to the given Accessible.

    Arguments:
    - obj: the Accessible
    """
    extents = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
    x = extents.x + extents.width / 2
    y = extents.y + extents.height / 2
    routeToPoint(x, y, "abs")

def routeToPoint(x, y, eventName="abs"):
    """Moves the mouse pointer to the given point.

    Arguments:
    - x, y: the point
    - eventName: absolute("abs") or relative("rel")
    """
    generateMouseEvent(x, y, eventName)

def clickCharacter(obj, button):
    """Performs a button click on the current character

    Arguments:
    - obj: the Accessible which implements the accessible text
      interface
    - button: an integer representing the mouse button number
    """
    text = obj.queryText()
    # We try to click to the left of center.  This is to
    # handle toolkits that will offset the caret position to
    # the right if you click dead on center of a character.
    #
    extents = text.getCharacterExtents(text.caretOffset,
                                       pyatspi.DESKTOP_COORDS)
    x = max(extents[0], extents[0] + (extents[2] / 2) - 1)
    y = extents[1] + extents[3] / 2
    generateMouseEvent(x, y, "b%dc" % button)

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
