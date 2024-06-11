# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position

"""
Utilities for obtaining position-related information about accessible objects.
These utilities are app-type- and toolkit-agnostic. Utilities that might have
different implementations or results depending on the type of app (e.g. terminal,
chat, web) or toolkit (e.g. Qt, Gtk) should be in script_utilities.py file(s).

N.B. There are currently utilities that should never have custom implementations
that live in script_utilities.py files. These will be moved over time.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import functools

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject
from .ax_utilities_role import AXUtilitiesRole


class AXComponent:
    """Utilities for obtaining position-related information about accessible objects."""

    @staticmethod
    def get_center_point(obj):
        """Returns the center point of obj with respect to its window."""

        rect = AXComponent.get_rect(obj)
        return rect.x + rect.width / 2, rect.y + rect.height / 2

    @staticmethod
    def get_position(obj):
        """Returns the x, y position tuple of obj with respect to its window."""

        if not AXObject.supports_component(obj):
            return -1, -1

        try:
            point = Atspi.Component.get_position(obj, Atspi.CoordType.WINDOW)
        except Exception as error:
            msg = f"AXComponent: Exception in get_position: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return -1, -1

        return point.x, point.y

    @staticmethod
    def get_rect(obj):
        """Returns the Atspi rect of obj with respect to its window."""

        if not AXObject.supports_component(obj):
            return Atspi.Rect()

        try:
            rect = Atspi.Component.get_extents(obj, Atspi.CoordType.WINDOW)
        except Exception as error:
            msg = f"AXComponent: Exception in get_rect: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return Atspi.Rect()

        return rect

    @staticmethod
    def get_rect_intersection(rect1, rect2):
        """Returns a rect representing the intersection of rect1 and rect2."""

        result = Atspi.Rect()

        x_points1 = range(rect1.x, rect1.x + rect1.width + 1)
        x_points2 = range(rect2.x, rect2.x + rect2.width + 1)
        x_intersection = sorted(set(x_points1).intersection(set(x_points2)))

        y_points1 = range(rect1.y, rect1.y + rect1.height + 1)
        y_points2 = range(rect2.y, rect2.y + rect2.height + 1)
        y_intersection = sorted(set(y_points1).intersection(set(y_points2)))

        if x_intersection and y_intersection:
            result.x = x_intersection[0]
            result.y = y_intersection[0]
            result.width = x_intersection[-1] - result.x
            result.height = y_intersection[-1] - result.y

        tokens = ["AXComponent: The intersection of", rect1, "and", rect2, "is:", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_size(obj):
        """Returns the width, height tuple of obj with respect to its window."""

        if not AXObject.supports_component(obj):
            return -1, -1

        try:
            point = Atspi.Component.get_size(obj, Atspi.CoordType.WINDOW)
        except Exception as error:
            msg = f"AXComponent: Exception in get_position: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return -1, -1

        # An Atspi.Point object stores width in x and height in y.
        return point.x, point.y

    @staticmethod
    def has_no_size(obj):
        """Returns True if obj has a width and height of 0."""

        rect = AXComponent.get_rect(obj)
        return not(rect.width or rect.height)

    @staticmethod
    def has_no_size_or_invalid_rect(obj):
        """Returns True if the rect associated with obj is sizeless or invalid."""

        rect = AXComponent.get_rect(obj)
        if not (rect.width or rect.height):
            return True

        if rect.x == rect.y == rect.width == rect.height == -1:
            return True

        if (rect.width < -1 or rect.height < -1):
            tokens = ["WARNING: ", obj, "has a broken rect:", rect]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            AXObject.clear_cache(obj)
            rect = AXComponent.get_rect(obj)
            if (rect.width < -1 or rect.height < -1):
                msg = "AXComponent: Clearing cache did not fix the rect"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

        return False

    @staticmethod
    def is_empty_rect(rect):
        """Returns True if rect's x, y, width, and height are all 0."""

        return rect.x == 0 and rect.y == 0 and rect.width == 0 and rect.height == 0

    @staticmethod
    def is_same_rect(rect1, rect2):
        """Returns True if rect1 and rect2 represent the same bounding box."""

        return rect1.x == rect2.x \
            and rect1.y == rect2.y \
            and rect1.width == rect2.width \
            and rect1.height == rect2.height

    @staticmethod
    def object_contains_point(obj, x, y):
        """Returns True if obj's rect contains the specified point."""

        if not AXObject.supports_component(obj):
            return False

        if AXObject.is_bogus(obj):
            return False

        try:
            result = Atspi.Component.contains(obj, x, y, Atspi.CoordType.WINDOW)
        except Exception as error:
            msg = f"AXComponent: Exception in object_contains_point: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXComponent: ", obj, f"contains point {x}, {y}: {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def object_intersects_rect(obj, rect):
        """Returns True if the Atspi.Rect associated with obj intersects rect."""

        intersection = AXComponent.get_rect_intersection(AXComponent.get_rect(obj), rect)
        return not AXComponent.is_empty_rect(intersection)

    @staticmethod
    def object_is_off_screen(obj):
        """Returns True if the rect associated with obj is off-screen"""

        rect = AXComponent.get_rect(obj)
        if abs(rect.x) > 10000 or abs(rect.y) > 10000:
            tokens = ["AXComponent: Treating", obj, "as offscreen due to position"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if rect.width == 0 or rect.height == 0:
            if not AXObject.get_child_count(obj):
                tokens = ["AXComponent: Treating", obj, "as offscreen due to size and no children"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return True
            if AXUtilitiesRole.is_menu(obj):
                tokens = ["AXComponent: Treating", obj, "as offscreen due to size and role"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return True
            tokens = ["AXComponent: Treating sizeless", obj, "as onscreen"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        result = rect.x + rect.width < 0 and rect.y + rect.height < 0
        tokens = ["AXComponent:", obj, f"is off-screen: {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def objects_have_same_rect(obj1, obj2):
        """Returns True if obj1 and obj2 have the same rect."""

        return AXComponent.is_same_rect(AXComponent.get_rect(obj1),AXComponent.get_rect(obj2))

    @staticmethod
    def objects_overlap(obj1, obj2):
        """Returns True if the rects associated with obj1 and obj2 overlap."""

        intersection = AXComponent.get_rect_intersection(
            AXComponent.get_rect(obj1), AXComponent.get_rect(obj2))
        return not AXComponent.is_empty_rect(intersection)

    @staticmethod
    def on_same_line(obj1, obj2, delta=0):
        """Returns True if obj1 and obj2 are on the same line based on the center points."""

        y1_center = AXComponent.get_center_point(obj1)[1]
        y2_center = AXComponent.get_center_point(obj2)[1]
        return abs(y1_center - y2_center) <= delta

    @staticmethod
    def _object_bounds_includes_children(obj):
        """Returns True if obj's rect is expected to include the rects of its children."""

        if AXUtilitiesRole.is_menu(obj) or AXUtilitiesRole.is_page_tab(obj):
            return False

        rect = AXComponent.get_rect(obj)
        return rect.width > 0 and rect.height > 0

    @staticmethod
    def _find_descendant_at_point(obj, x, y):
        """Checks each child to see if it has a descendant at the specified point."""

        for child in AXObject.iter_children(obj):
            if AXComponent._object_bounds_includes_children(child):
                continue
            for descendant in AXObject.iter_children(child):
                if AXComponent.object_contains_point(descendant, x, y):
                    return descendant
        return None

    @staticmethod
    def _get_object_at_point(obj, x, y):
        """Returns the child (or descendant?) of obj at the specified point."""

        if not AXObject.supports_component(obj):
            return None

        try:
            result = Atspi.Component.get_accessible_at_point(obj, x, y, Atspi.CoordType.WINDOW)
        except Exception as error:
            msg = f"AXComponent: Exception in get_child_at_point: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return None

        tokens = ["AXComponent: Child of", obj, f"at {x}, {y} is", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def _get_descendant_at_point(obj, x, y):
        """Returns the deepest descendant of obj at the specified point."""

        child = AXComponent._get_object_at_point(obj, x, y)
        if child is None and AXComponent.object_contains_point(obj, x, y):
            descendant = AXComponent._find_descendant_at_point(obj, x, y)
            if descendant is None:
                return obj
            child = descendant

        if child == obj or not AXObject.get_child_count(child):
            return child

        return AXComponent._get_descendant_at_point(child, x, y)

    @staticmethod
    def get_descendant_at_point(obj, x, y):
        """Returns the deepest descendant of obj at the specified point."""

        result = AXComponent._get_descendant_at_point(obj, x, y)
        tokens = ["AXComponent: Descendant of", obj, f"at {x}, {y} is", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def scroll_object_to_point(obj, x, y):
        """Attempts to scroll obj to the specified point."""

        if not AXObject.supports_component(obj):
            return False

        try:
            result = Atspi.Component.scroll_to_point(obj, Atspi.CoordType.WINDOW, x, y)
        except Exception as error:
            msg = f"AXComponent: Exception in scroll_object_to_point: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXComponent: Scrolled", obj, f"to {x}, {y}:", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def scroll_object_to_location(obj, location):
        """Attempts to scroll obj to the specified Atspi.ScrollType location."""

        if not AXObject.supports_component(obj):
            return False

        try:
            result = Atspi.Component.scroll_to(obj, location)
        except Exception as error:
            msg = f"AXComponent: Exception in scroll_object_to_location: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXComponent: Scrolled", obj, "to", location, f": {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def sort_objects_by_size(objects):
        """Returns objects sorted from smallest to largest."""

        def _size_comparison(obj1, obj2):
            rect1 = AXComponent.get_rect(obj1)
            rect2 = AXComponent.get_rect(obj2)
            return (rect1.width * rect1.height) - (rect2.width * rect2.height)

        return sorted(objects, key=functools.cmp_to_key(_size_comparison))

    @staticmethod
    def sort_objects_by_position(objects):
        """Returns objects sorted from top-left to bottom-right."""

        def _spatial_comparison(obj1, obj2):
            rect1 = AXComponent.get_rect(obj1)
            rect2 = AXComponent.get_rect(obj2)
            rv = rect1.y - rect2.y or rect1.x - rect2.x

            # If the objects claim to have the same coordinates and the same parent,
            # we probably have bogus coordinates from the implementation.
            if not rv and AXObject.get_parent(obj1) == AXObject.get_parent(obj2):
                rv = AXObject.get_index_in_parent(obj1) - AXObject.get_index_in_parent(obj2)

            rv = max(rv, -1)
            rv = min(rv, 1)
            return rv

        return sorted(objects, key=functools.cmp_to_key(_spatial_comparison))
