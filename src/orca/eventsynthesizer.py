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
import time

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import debug
from .ax_object import AXObject
from .ax_utilities import AXUtilities

_banner = None

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

    try:
        success = Atspi.generate_mouse_event(x, y, event)
    except Exception as e:
        msg = "EVENT SYNTHESIZER: Exception in _generateMouseEvent: %s" % e
        debug.println(debug.LEVEL_INFO, msg, True)
        success = False
    else:
        msg = "EVENT SYNTHESIZER: Atspi.generate_mouse_event returned %s" % success
        debug.println(debug.LEVEL_INFO, msg, True)

    # There seems to be a timeout / lack of reply from this blocking call.
    # But often the mouse event is successful. Pause briefly before checking.
    time.sleep(0.5)

    newX, newY = _getMouseCoordinates()
    if oldX == newX and oldY == newY and (oldX, oldY) != (x, y):
        msg = "EVENT SYNTHESIZER: Mouse event possible failure. Pointer didn't move"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    return True

def _intersection(extents1, extents2):
    """Returns the bounding box containing the intersection of the two boxes."""

    x1, y1, width1, height1 = extents1
    x2, y2, width2, height2 = extents2

    xPoints1 = range(x1, x1 + width1 + 1)
    xPoints2 = range(x2, x2 + width2 + 1)
    xIntersection = sorted(set(xPoints1).intersection(set(xPoints2)))

    yPoints1 = range(y1, y1 + height1 + 1)
    yPoints2 = range(y2, y2 + height2 + 1)
    yIntersection = sorted(set(yPoints1).intersection(set(yPoints2)))

    if not (xIntersection and yIntersection):
        return 0, 0, 0, 0

    x = xIntersection[0]
    y = yIntersection[0]
    width = xIntersection[-1] - x
    height = yIntersection[-1] - y
    return x, y, width, height

def _extentsAtCaret(obj):
    """Returns the character extents of obj at the current caret offset."""

    try:
        text = obj.queryText()
        extents = text.getCharacterExtents(text.caretOffset, Atspi.CoordType.SCREEN)
    except Exception:
        msg = "ERROR: Exception getting character extents for %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return 0, 0, 0, 0

    return extents

def _objectExtents(obj):
    """Returns the bounding box associated with obj."""

    try:
        extents = obj.queryComponent().getExtents(Atspi.CoordType.SCREEN)
    except Exception:
        msg = "ERROR: Exception getting extents for %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return 0, 0, 0, 0

    return extents

def _mouseEventOnCharacter(obj, event):
    """Performs the specified mouse event on the current character in obj."""

    extents = _extentsAtCaret(obj)
    if extents == (0, 0, 0, 0):
        return False

    objExtents = _objectExtents(obj)
    intersection = _intersection(extents, objExtents)
    if intersection == (0, 0, 0, 0):
        msg = "EVENT SYNTHESIZER: %s's caret %s not in obj %s" % (obj, extents, objExtents)
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    x = max(extents[0], extents[0] + (extents[2] / 2) - 1)
    y = extents[1] + extents[3] / 2
    return _generateMouseEvent(x, y, event)

def _mouseEventOnObject(obj, event):
    """Performs the specified mouse event on obj."""

    extents = _objectExtents(obj)
    if extents == (0, 0, 0, 0):
        return False

    x = extents.x + extents.width/2
    y = extents.y + extents.height/2
    return _generateMouseEvent(x, y, event)

def routeToCharacter(obj):
    """Routes the pointer to the current character in obj."""

    msg = "EVENT SYNTHESIZER: Attempting to route to character in %s" % obj
    debug.println(debug.LEVEL_INFO, msg, True)
    return _mouseEventOnCharacter(obj, "abs")

def routeToObject(obj):
    """Moves the mouse pointer to the center of obj."""

    msg = "EVENT SYNTHESIZER: Attempting to route to %s" % obj
    debug.println(debug.LEVEL_INFO, msg, True)
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

def _scrollSubstringToLocation(obj, location, startOffset, endOffset):
    """Attempts to scroll the given substring to the specified location."""

    try:
        text = obj.queryText()
        if not text.characterCount:
            return False
        if startOffset is None:
            startOffset = 0
        if endOffset is None:
            endOffset = text.characterCount - 1
        result = text.scrollSubstringTo(startOffset, endOffset, location)
    except NotImplementedError:
        msg = "ERROR: Text interface not implemented for %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False
    except Exception:
        msg = "ERROR: Exception scrolling %s (%s,%s) to %s." % \
            (obj, startOffset, endOffset, location)
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    msg = "EVENT SYNTHESIZER: scrolled %s (%i,%i) to %s: %s" % \
        (obj, startOffset, endOffset, location, result)
    debug.println(debug.LEVEL_INFO, msg, True)
    return result

def _scrollObjectToLocation(obj, location):
    """Attempts to scroll obj to the specified location."""

    try:
        result = obj.queryComponent().scrollTo(location)
    except NotImplementedError:
        msg = "ERROR: Component interface not implemented for %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False
    except Exception:
        msg = "ERROR: Exception scrolling %s to %s." % (obj, location)
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    msg = "EVENT SYNTHESIZER: scrolled %s to %s: %s" % (obj, location, result)
    debug.println(debug.LEVEL_INFO, msg, True)
    return result

def _scrollToLocation(obj, location, startOffset=None, endOffset=None):
    """Attempts to scroll to the specified location."""

    try:
        component = obj.queryComponent()
    except Exception:
        msg = "ERROR: Exception querying component of %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    before = component.getExtents(Atspi.CoordType.SCREEN)

    if not _scrollSubstringToLocation(obj, location, startOffset, endOffset):
        _scrollObjectToLocation(obj, location)

    after = component.getExtents(Atspi.CoordType.SCREEN)
    msg = "EVENT SYNTHESIZER: Before scroll: %i,%i. After scroll: %i,%i." % \
          (before[0], before[1], after[0], after[1])
    debug.println(debug.LEVEL_INFO, msg, True)

def _scrollSubstringToPoint(obj, x, y, startOffset, endOffset):
    """Attempts to scroll the given substring to the specified location."""

    try:
        text = obj.queryText()
        if not text.characterCount:
            return False
        if startOffset is None:
            startOffset = 0
        if endOffset is None:
            endOffset = text.characterCount - 1
        result = text.scrollSubstringToPoint(startOffset, endOffset, Atspi.CoordType.SCREEN, x, y)
    except NotImplementedError:
        msg = "ERROR: Text interface not implemented for %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False
    except Exception:
        msg = "ERROR: Exception scrolling %s (%i,%i) to %i,%i." % \
            (obj, startOffset, endOffset, x, y)
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    msg = "EVENT SYNTHESIZER: scrolled %s (%i,%i) to %i,%i: %s" % \
        (obj, startOffset, endOffset, x, y, result)
    debug.println(debug.LEVEL_INFO, msg, True)
    return result

def _scrollObjectToPoint(obj, x, y):
    """Attempts to scroll obj to the specified point."""

    try:
        result = obj.queryComponent().scrollToPoint(Atspi.CoordType.SCREEN, x, y)
    except NotImplementedError:
        msg = "ERROR: Component interface not implemented for %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False
    except Exception:
        msg = "ERROR: Exception scrolling %s to %i,%i." % (obj, x, y)
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    msg = "EVENT SYNTHESIZER: scrolled %s to %i,%i: %s" % (obj, x, y, result)
    debug.println(debug.LEVEL_INFO, msg, True)
    return result

def _scrollToPoint(obj, x, y, startOffset=None, endOffset=None):
    """Attempts to scroll obj to the specified point."""

    try:
        component = obj.queryComponent()
    except Exception:
        msg = "ERROR: Exception querying component of %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    before = component.getExtents(Atspi.CoordType.SCREEN)

    if not _scrollSubstringToPoint(obj, x, y, startOffset, endOffset):
        _scrollObjectToPoint(obj, x, y)

    after = component.getExtents(Atspi.CoordType.SCREEN)
    msg = "EVENT SYNTHESIZER: Before scroll: %i,%i. After scroll: %i,%i." % \
          (before[0], before[1], after[0], after[1])
    debug.println(debug.LEVEL_INFO, msg, True)

def scrollIntoView(obj, startOffset=None, endOffset=None):
    _scrollToLocation(obj, Atspi.ScrollType.ANYWHERE, startOffset, endOffset)

def _containingDocument(obj):
    document = AXObject.find_ancestor(obj, AXUtilities.is_document)
    while document:
        ancestor = AXObject.find_ancestor(document, AXUtilities.is_document)
        if ancestor is None or ancestor == document:
            break
        document = ancestor

    return document

def _getAccessibleAtPoint(root, x, y):
    try:
        result = root.queryComponent().getAccessibleAtPoint(x, y, Atspi.CoordType.SCREEN)
    except NotImplementedError:
        msg = "ERROR: Component interface not implemented for %s" % root
        debug.println(debug.LEVEL_INFO, msg, True)
        return None
    except Exception:
        msg = "ERROR: Exception getting accessible at (%i, %i) for %s" % (x, y, root)
        debug.println(debug.LEVEL_INFO, msg, True)
        return None

    msg = "EVENT SYNTHESIZER: Accessible at (%i, %i) in %s: %s" % (x, y, root, result)
    debug.println(debug.LEVEL_INFO, msg, True)
    return result

def _obscuringBanner(obj):
    document = _containingDocument(obj)
    if not document:
        msg = "EVENT SYNTHESIZER: No obscuring banner found for %s. No document." % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return None

    if not AXObject.supports_component(document):
        msg = "EVENT SYNTHESIZER: No obscuring banner found for %s. No doc iface." % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return None

    objX, objY, objWidth, objHeight = _objectExtents(obj)
    docX, docY, docWidth, docHeight = _objectExtents(document)

    left = _getAccessibleAtPoint(document, docX, objY)
    right = _getAccessibleAtPoint(document, docX + docWidth, objY)
    if not (left and right and left == right != document):
        msg = "EVENT SYNTHESIZER: No obscuring banner found for %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return None

    msg = "EVENT SYNTHESIZER: %s believed to be obscured by banner %s" % (obj, left)
    debug.println(debug.LEVEL_INFO, msg, True)
    return left

def _scrollBelowBanner(obj, banner, startOffset, endOffset, margin=25):
    objX, objY, objWidth, objHeight = _objectExtents(obj)
    bannerX, bannerY, bannerWidth, bannerHeight = _objectExtents(banner)
    msg = "EVENT SYNTHESIZER: Extents of banner: (%i, %i, %i, %i)" % \
        (bannerX, bannerY, bannerWidth, bannerHeight)
    debug.println(debug.LEVEL_INFO, msg, True)
    _scrollToPoint(obj, objX, bannerY + bannerHeight + margin, startOffset, endOffset)

def scrollToTopEdge(obj, startOffset=None, endOffset=None):
    global _banner
    if _banner and not AXObject.is_dead(_banner):
        msg = "EVENT SYNTHESIZER: Suspected existing banner found: %s" % _banner
        debug.println(debug.LEVEL_INFO, msg, True)
        _scrollBelowBanner(obj, _banner, startOffset, endOffset)
        return

    _scrollToLocation(obj, Atspi.ScrollType.TOP_EDGE, startOffset, endOffset)

    _banner = _obscuringBanner(obj)
    if _banner:
        msg = "EVENT SYNTHESIZER: Rescrolling %s due to banner" % obj
        _scrollBelowBanner(obj, _banner, startOffset, endOffset)
        debug.println(debug.LEVEL_INFO, msg, True)

def scrollToTopLeft(obj, startOffset=None, endOffset=None):
    _scrollToLocation(obj, Atspi.ScrollType.TOP_LEFT, startOffset, endOffset)

def scrollToLeftEdge(obj, startOffset=None, endOffset=None):
    _scrollToLocation(obj, Atspi.ScrollType.LEFT_EDGE, startOffset, endOffset)

def scrollToBottomEdge(obj, startOffset=None, endOffset=None):
    _scrollToLocation(obj, Atspi.ScrollType.BOTTOM_EDGE, startOffset, endOffset)

def scrollToBottomRight(obj, startOffset=None, endOffset=None):
    _scrollToLocation(obj, Atspi.ScrollType.BOTTOM_RIGHT, startOffset, endOffset)

def scrollToRightEdge(obj, startOffset=None, endOffset=None):
    _scrollToLocation(obj, Atspi.ScrollType.RIGHT_EDGE, startOffset, endOffset)

def tryAllClickableActions(obj):
    actions = ["click", "press", "jump", "open"]
    for a in actions:
        if AXObject.do_named_action(obj, a):
            msg = "INFO: '%s' on %s performed successfully" % (a, obj)
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

    if debug.LEVEL_INFO < debug.debugLevel:
        return False

    msg = "INFO: Actions on %s: %s" % (obj, AXObject.actions_as_string(obj))
    debug.println(debug.LEVEL_INFO, msg, True)
    return False

def grabFocusOn(obj):
    try:
        component = obj.queryComponent()
    except Exception:
        msg = "ERROR: Exception querying component of %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    return component.grabFocus()
