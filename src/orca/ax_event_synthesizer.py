# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2018-2023 Igalia, S.L.
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
                "Copyright (c) 2018-2023 Igalia, S.L."
__license__   = "LGPL"

import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import debug
from .ax_object import AXObject
from .ax_utilities import AXUtilities

class AXEventSynthesizer:
    """Provides support for synthesizing accessible input events."""

    _banner = None

    @staticmethod
    def _get_mouse_coordinates():
        """Returns the current mouse coordinates."""

        root_window = Gtk.Window().get_screen().get_root_window()
        window, x_coord, y_coord, modifiers = root_window.get_pointer()
        msg = f"AXEventSynthesizer: Mouse coordinates: {x_coord}, {y_coord}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return x_coord, y_coord

    @staticmethod
    def _generate_mouse_event(x_coord, y_coord, event):
        """Synthesize a mouse event at a specific screen coordinate."""

        old_x, old_y = AXEventSynthesizer._get_mouse_coordinates()
        msg = f"AXEventSynthesizer: Generating {event} mouse event at {x_coord}, {y_coord}"
        debug.println(debug.LEVEL_INFO, msg, True)

        try:
            success = Atspi.generate_mouse_event(x_coord, y_coord, event)
        except Exception as error:
            msg = f"AXEventSynthesizer: Exception in _generate_mouse_event: {error}"
            debug.println(debug.LEVEL_INFO, msg, True)
            success = False
        else:
            msg = f"AXEventSynthesizer: Atspi.generate_mouse_event returned {success}"
            debug.println(debug.LEVEL_INFO, msg, True)

        # There seems to be a timeout / lack of reply from this blocking call.
        # But often the mouse event is successful. Pause briefly before checking.
        time.sleep(1)

        new_x, new_y = AXEventSynthesizer._get_mouse_coordinates()
        if old_x == new_x and old_y == new_y and (old_x, old_y) != (x_coord, y_coord):
            msg = "AXEventSynthesizer: Mouse event possible failure. Pointer didn't move"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    @staticmethod
    def _intersection(extents1, extents2):
        """Returns the bounding box containing the intersection of the two boxes."""

        x_coord1, y_coord1, width1, height1 = extents1
        x_coord2, y_coord2, width2, height2 = extents2

        x_points1 = range(x_coord1, x_coord1 + width1 + 1)
        x_points2 = range(x_coord2, x_coord2 + width2 + 1)
        x_intersection = sorted(set(x_points1).intersection(set(x_points2)))

        y_points1 = range(y_coord1, y_coord1 + height1 + 1)
        y_points2 = range(y_coord2, y_coord2 + height2 + 1)
        y_intersection = sorted(set(y_points1).intersection(set(y_points2)))

        if not (x_intersection and y_intersection):
            return 0, 0, 0, 0

        x_coord = x_intersection[0]
        y_coord = y_intersection[0]
        width = x_intersection[-1] - x_coord
        height = y_intersection[-1] - y_coord
        return x_coord, y_coord, width, height

    @staticmethod
    def _extents_at_caret(obj):
        """Returns the character extents of obj at the current caret offset."""

        try:
            text = obj.queryText()
            extents = text.getCharacterExtents(text.caretOffset, Atspi.CoordType.SCREEN)
        except Exception:
            msg = f"ERROR: Exception getting character extents for {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0, 0, 0, 0

        return extents

    @staticmethod
    def _object_extents(obj):
        """Returns the bounding box associated with obj."""

        try:
            extents = obj.queryComponent().getExtents(Atspi.CoordType.SCREEN)
        except Exception:
            msg = f"ERROR: Exception getting extents for {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0, 0, 0, 0

        return extents

    @staticmethod
    def _mouse_event_on_character(obj, event):
        """Performs the specified mouse event on the current character in obj."""

        extents = AXEventSynthesizer._extents_at_caret(obj)
        if extents == (0, 0, 0, 0):
            return False

        obj_extents = AXEventSynthesizer._object_extents(obj)
        intersection = AXEventSynthesizer._intersection(extents, obj_extents)
        if intersection == (0, 0, 0, 0):
            msg = f"AXEventSynthesizer: {obj}'s caret {extents} not in obj {obj_extents}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        x_coord = max(extents[0], extents[0] + (extents[2] / 2) - 1)
        y_coord = extents[1] + extents[3] / 2
        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, event)

    @staticmethod
    def _mouse_event_on_object(obj, event):
        """Performs the specified mouse event on obj."""

        extents = AXEventSynthesizer._object_extents(obj)
        if extents == (0, 0, 0, 0):
            return False

        x_coord = extents.x + extents.width/2
        y_coord = extents.y + extents.height/2
        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, event)

    @staticmethod
    def route_to_character(obj):
        """Routes the pointer to the current character in obj."""

        msg = f"AXEventSynthesizer: Attempting to route to character in {obj}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return AXEventSynthesizer._mouse_event_on_character(obj, "abs")

    @staticmethod
    def route_to_object(obj):
        """Moves the mouse pointer to the center of obj."""

        msg = f"AXEventSynthesizer: Attempting to route to {obj}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return AXEventSynthesizer._mouse_event_on_object(obj, "abs")

    @staticmethod
    def route_to_point(x_coord, y_coord):
        """Routes the pointer to the specified coordinates."""

        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, "abs")

    @staticmethod
    def click_character(obj, button=1):
        """Single click on the current character in obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_character(obj, f"b{button}c")

    @staticmethod
    def click_object(obj, button=1):
        """Single click on obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_object(obj, f"b{button}c")

    @staticmethod
    def click_point(x_coord, y_coord, button=1):
        """Single click on the given point using the specified button."""

        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, f"b{button}c")

    @staticmethod
    def double_click_character(obj, button=1):
        """Double click on the current character in obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_character(obj, f"b{button}d")

    @staticmethod
    def double_click_object(obj, button=1):
        """Double click on obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_object(obj, f"b{button}d")

    @staticmethod
    def double_click_point(x_coord, y_coord, button=1):
        """Double click on the given point using the specified button."""

        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, f"b{button}d")

    @staticmethod
    def press_at_character(obj, button=1):
        """Performs a press on the current character in obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_character(obj, f"b{button}p")

    @staticmethod
    def press_at_object(obj, button=1):
        """Performs a press on obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_object(obj, f"b{button}p")

    @staticmethod
    def press_at_point(x_coord, y_coord, button=1):
        """Performs a press on the given point using the specified button."""

        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, f"b{button}p")

    @staticmethod
    def release_at_character(obj, button=1):
        """Performs a release on the current character in obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_character(obj, f"b{button}r")

    @staticmethod
    def release_at_object(obj, button=1):
        """Performs a release on obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_object(obj, f"b{button}r")

    @staticmethod
    def release_at_point(x_coord, y_coord, button=1):
        """Performs a release on the given point using the specified button."""

        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, f"b{button}r")

    @staticmethod
    def _scroll_substring_to_location(obj, location, start_offset, end_offset):
        """Attempts to scroll the given substring to the specified location."""

        try:
            text = obj.queryText()
            if not text.characterCount:
                return False
            if start_offset is None:
                start_offset = 0
            if end_offset is None:
                end_offset = text.characterCount - 1
            result = text.scrollSubstringTo(start_offset, end_offset, location)
        except NotImplementedError:
            msg = f"AXEventSynthesizer: Text interface not implemented for {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        except Exception:
            msg = (
                f"AXEventSynthesizer: Exception scrolling {obj} ({start_offset}, {end_offset}) "
                f"to {location.value_name}."
            )
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = (
            f"AXEventSynthesizer: scrolled {obj} substring ({start_offset}, {end_offset}) "
            f"to {location.value_name}: {result}"
        )
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    @staticmethod
    def _scroll_object_to_location(obj, location):
        """Attempts to scroll obj to the specified location."""

        try:
            result = obj.queryComponent().scrollTo(location)
        except NotImplementedError:
            msg = f"AXEventSynthesizer: Component interface not implemented for {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        except Exception:
            msg = f"AXEventSynthesizer: Exception scrolling {obj} to {location.value_name}."
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = f"AXEventSynthesizer: scrolled {obj} to {location.value_name}: {result}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    @staticmethod
    def _scroll_to_location(obj, location, start_offset=None, end_offset=None):
        """Attempts to scroll to the specified location."""

        try:
            component = obj.queryComponent()
        except Exception:
            msg = f"AXEventSynthesizer: Exception querying component of {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        before = component.getExtents(Atspi.CoordType.SCREEN)

        if not AXEventSynthesizer._scroll_substring_to_location(
           obj, location, start_offset, end_offset):
            AXEventSynthesizer._scroll_object_to_location(obj, location)

        after = component.getExtents(Atspi.CoordType.SCREEN)
        msg = (
            f"AXEventSynthesizer: Before scroll: {before[0]}, {before[1]}. "
            f"After scroll: {after[0]}, {after[1]}."
        )
        debug.println(debug.LEVEL_INFO, msg, True)

    @staticmethod
    def _scroll_substring_to_point(obj, x_coord, y_coord, start_offset, end_offset):
        """Attempts to scroll the given substring to the specified location."""

        try:
            text = obj.queryText()
            if not text.characterCount:
                return False
            if start_offset is None:
                start_offset = 0
            if end_offset is None:
                end_offset = text.characterCount - 1
            result = text.scrollSubstringToPoint(
                start_offset, end_offset, Atspi.CoordType.SCREEN, x_coord, y_coord)
        except NotImplementedError:
            msg = f"AXEventSynthesizer: Text interface not implemented for {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        except Exception:
            msg = (
                f"AXEventSynthesizer: Exception scrolling {obj} ({start_offset}, {end_offset}) "
                f"to {x_coord}, {y_coord}"
            )
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXEventSynthesizer: scrolled %s (%i, %i) to %i, %i: %s" % \
            (obj, start_offset, end_offset, x_coord, y_coord, result)
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    @staticmethod
    def _scroll_object_to_point(obj, x_coord, y_coord):
        """Attempts to scroll obj to the specified point."""

        try:
            result = obj.queryComponent().scrollToPoint(Atspi.CoordType.SCREEN, x_coord, y_coord)
        except NotImplementedError:
            msg = f"AXEventSynthesizer: Component interface not implemented for {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        except Exception:
            msg = f"AXEventSynthesizer: Exception scrolling {obj} to {x_coord}, {y_coord}."
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = f"AXEventSynthesizer: scrolled {obj} to {x_coord}, {y_coord}: {result}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    @staticmethod
    def _scroll_to_point(obj, x_coord, y_coord, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the specified point."""

        try:
            component = obj.queryComponent()
        except Exception:
            msg = f"AXEventSynthesizer: Exception querying component of {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        before = component.getExtents(Atspi.CoordType.SCREEN)

        if not AXEventSynthesizer._scroll_substring_to_point(
           obj, x_coord, y_coord, start_offset, end_offset):
            AXEventSynthesizer._scroll_object_to_point(obj, x_coord, y_coord)

        after = component.getExtents(Atspi.CoordType.SCREEN)
        msg = (
            f"AXEventSynthesizer: Before scroll: {before[0]}, {before[1]}. "
            f"After scroll: {after[0]}, {after[1]}."
        )
        debug.println(debug.LEVEL_INFO, msg, True)

    @staticmethod
    def scroll_into_view(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj into view."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.ANYWHERE, start_offset, end_offset)

    @staticmethod
    def _containing_document(obj):
        """Returns the document containing obj"""

        document = AXObject.find_ancestor(obj, AXUtilities.is_document)
        while document:
            ancestor = AXObject.find_ancestor(document, AXUtilities.is_document)
            if ancestor is None or ancestor == document:
                break
            document = ancestor

        return document

    @staticmethod
    def _get_accessible_at_point(root, x_coord, y_coord):
        """"Returns the accessible in root at the specified point."""

        try:
            result = root.queryComponent().getAccessibleAtPoint(
                x_coord, y_coord, Atspi.CoordType.SCREEN)
        except NotImplementedError:
            msg = f"AXEventSynthesizer: Component interface not implemented for {root}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return None
        except Exception:
            msg = (
                f"AXEventSynthesizer: Exception getting accessible at "
                f"{x_coord}, {y_coord} for {root}"
            )
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        msg = f"AXEventSynthesizer: Accessible at {x_coord}, {y_coord} in {root}: {result}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    @staticmethod
    def _get_obscuring_banner(obj):
        """"Returns the banner obscuring obj from view."""

        document = AXEventSynthesizer._containing_document(obj)
        if not document:
            msg = f"AXEventSynthesizer: No obscuring banner found for {obj}. No document."
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if not AXObject.supports_component(document):
            msg = f"AXEventSynthesizer: No obscuring banner found for {obj}. No doc iface."
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        obj_x, obj_y, obj_width, obj_height = AXEventSynthesizer._object_extents(obj)
        doc_x, doc_y, doc_width, doc_height = AXEventSynthesizer._object_extents(document)

        left = AXEventSynthesizer._get_accessible_at_point(document, doc_x, obj_y)
        right = AXEventSynthesizer._get_accessible_at_point(document, doc_x + doc_width, obj_y)
        if not (left and right and left == right != document):
            msg = f"AXEventSynthesizer: No obscuring banner found for {obj}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        msg = f"AXEventSynthesizer: {obj} believed to be obscured by banner {left}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return left

    @staticmethod
    def _scroll_below_banner(obj, banner, start_offset, end_offset, margin=25):
        """Attempts to scroll obj below banner."""

        obj_x, obj_y, obj_width, obj_height = AXEventSynthesizer._object_extents(obj)
        banner_x, banner_y, banner_width, banner_height = AXEventSynthesizer._object_extents(banner)
        msg = (
            f"AXEventSynthesizer: Extents of banner: "
            f"({banner_x}, {banner_y}, {banner_width}, {banner_height})"
        )
        debug.println(debug.LEVEL_INFO, msg, True)
        AXEventSynthesizer._scroll_to_point(
            obj, obj_x, banner_y + banner_height + margin, start_offset, end_offset)

    @staticmethod
    def scroll_to_top_edge(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the top edge."""

        if AXEventSynthesizer._banner and not AXObject.is_dead(AXEventSynthesizer._banner):
            msg = (
                f"AXEventSynthesizer: Suspected existing banner found: "
                f"{AXEventSynthesizer._banner}"
            )
            debug.println(debug.LEVEL_INFO, msg, True)
            AXEventSynthesizer._scroll_below_banner(
                obj, AXEventSynthesizer._banner, start_offset, end_offset)
            return

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.TOP_EDGE, start_offset, end_offset)

        AXEventSynthesizer._banner = AXEventSynthesizer._get_obscuring_banner(obj)
        if AXEventSynthesizer._banner:
            msg = f"AXEventSynthesizer: Re-scrolling {obj} due to banner"
            AXEventSynthesizer._scroll_below_banner(
                obj, AXEventSynthesizer._banner, start_offset, end_offset)
            debug.println(debug.LEVEL_INFO, msg, True)

    @staticmethod
    def scroll_to_top_left(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the top left."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.TOP_LEFT, start_offset, end_offset)

    @staticmethod
    def scroll_to_left_edge(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the left edge."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.LEFT_EDGE, start_offset, end_offset)

    @staticmethod
    def scroll_to_bottom_edge(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the bottom edge."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.BOTTOM_EDGE, start_offset, end_offset)

    @staticmethod
    def scroll_to_bottom_right(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the bottom right."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.BOTTOM_RIGHT, start_offset, end_offset)

    @staticmethod
    def scroll_to_right_edge(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the right edge."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.RIGHT_EDGE, start_offset, end_offset)

    @staticmethod
    def try_all_clickable_actions(obj):
        """Attempts to perform a click-like action if one is available."""

        actions = ["click", "press", "jump", "open"]
        for action in actions:
            if AXObject.do_named_action(obj, action):
                msg = f"AXEventSynthesizer: '{action}' on {obj} performed successfully"
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        if debug.LEVEL_INFO < debug.debugLevel:
            return False

        msg = f"AXEventSynthesizer: Actions on {obj}: {AXObject.actions_as_string(obj)}"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

_synthesizer = AXEventSynthesizer()
def getSynthesizer():
    return _synthesizer
