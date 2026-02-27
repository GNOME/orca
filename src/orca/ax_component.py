# Orca
#
# Copyright 2024-2026 Igalia, S.L.
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

"""Utilities for obtaining position-related information about accessible objects."""

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import debug
from .ax_object import AXObject


class AXComponent:
    """Utilities for obtaining position-related information about accessible objects."""

    @staticmethod
    def get_position(obj: Atspi.Accessible) -> tuple[int, int]:
        """Returns the x, y position tuple of obj with respect to its window."""

        if not AXObject.supports_component(obj):
            return -1, -1

        try:
            point = Atspi.Component.get_position(obj, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXComponent: Exception in get_position: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1, -1

        if point is None:
            tokens = ["AXComponent: get_position failed for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return -1, -1

        return point.x, point.y

    @staticmethod
    def get_rect(obj: Atspi.Accessible) -> Atspi.Rect:
        """Returns the Atspi rect of obj with respect to its window."""

        if not AXObject.supports_component(obj):
            return Atspi.Rect()

        try:
            rect = Atspi.Component.get_extents(obj, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXComponent: Exception in get_rect: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return Atspi.Rect()

        return rect

    @staticmethod
    def get_size(obj: Atspi.Accessible) -> tuple[int, int]:
        """Returns the width, height tuple of obj with respect to its window."""

        if not AXObject.supports_component(obj):
            return -1, -1

        try:
            point = Atspi.Component.get_size(obj, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXComponent: Exception in get_position: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1, -1

        if point is None:
            tokens = ["AXComponent: get_size failed for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return -1, -1

        # An Atspi.Point object stores width in x and height in y.
        return point.x, point.y

    @staticmethod
    def object_contains_point(obj: Atspi.Accessible, x: int, y: int) -> bool:
        """Returns True if obj's rect contains the specified point."""

        if not AXObject.supports_component(obj):
            return False

        if AXObject.is_bogus(obj):
            return False

        try:
            result = Atspi.Component.contains(obj, x, y, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXComponent: Exception in object_contains_point: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXComponent: ", obj, f"contains point {x}, {y}: {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_object_at_point(obj: Atspi.Accessible, x: int, y: int) -> Atspi.Accessible | None:
        """Returns the child (or descendant?) of obj at the specified point."""

        if not AXObject.supports_component(obj):
            return None

        try:
            result = Atspi.Component.get_accessible_at_point(obj, x, y, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXComponent: Exception in get_child_at_point: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        tokens = ["AXComponent: Child of", obj, f"at {x}, {y} is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def scroll_object_to_point(obj: Atspi.Accessible, x: int, y: int) -> bool:
        """Attempts to scroll obj to the specified point."""

        if not AXObject.supports_component(obj):
            return False

        try:
            result = Atspi.Component.scroll_to_point(obj, Atspi.CoordType.WINDOW, x, y)
        except GLib.GError as error:
            msg = f"AXComponent: Exception in scroll_object_to_point: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXComponent: Scrolled", obj, f"to {x}, {y}:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def scroll_object_to_location(obj: Atspi.Accessible, location: Atspi.ScrollType) -> bool:
        """Attempts to scroll obj to the specified Atspi.ScrollType location."""

        if not AXObject.supports_component(obj):
            return False

        try:
            result = Atspi.Component.scroll_to(obj, location)
        except GLib.GError as error:
            msg = f"AXComponent: Exception in scroll_object_to_location: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXComponent: Scrolled", obj, "to", location, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result
