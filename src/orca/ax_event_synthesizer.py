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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=too-many-public-methods

"""Provides support for synthesizing accessible input events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2018-2023 Igalia, S.L."
__license__   = "LGPL"


import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi
from gi.repository import Gtk

from . import debug
from . import focus_manager
from .ax_component import AXComponent
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities_debugging import AXUtilitiesDebugging
from .ax_utilities_role import AXUtilitiesRole

class AXEventSynthesizer:
    """Provides support for synthesizing accessible input events."""

    @staticmethod
    def _window_coordinates_to_screen_coordinates(x, y):
        # TODO - JD: Remove this when we bump dependencies to AT-SPI 2.52.
        active_window = focus_manager.get_manager().get_active_window()
        if active_window is None:
            msg = "AXEventSynthesizer: Could not get active window to adjust coordinates"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return x, y

        try:
            point = Atspi.Component.get_position(active_window, Atspi.CoordType.SCREEN)
        except Exception as error:
            msg = f"AXEventSynthesizer: Exception in calling get_position: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return x, y

        msg = f"AXEventSynthesizer: Active window position: {point.x}, {point.y}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # Unfortunately, the position we get does not seem to include window decorations.
        # So we have to do more work to adjust. This is why we cannot have nice things.
        gdk_window = Gtk.Window().get_screen().get_active_window()
        frame_extents = gdk_window.get_frame_extents()
        title_bar_height = frame_extents.height - gdk_window.get_height()
        msg = f"AXEventSynthesizer: Title bar height believed to be: {title_bar_height}px"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        new_x = x + point.x
        new_y = y + point.y + title_bar_height

        msg = f"AXEventSynthesizer: x: {x}->{new_x}, y: {y}->{new_y}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return new_x, new_y

    @staticmethod
    def _highest_ancestor(obj):
        """Returns the highest obtainable ancestor of obj, stopping before the application."""
        parent = AXObject.get_parent(obj)
        return parent is None or AXUtilitiesRole.is_application(parent)

    @staticmethod
    def _is_scrolled_off_screen(obj, offset=None, ancestor=None):
        """Returns true if obj, or the caret offset therein, is scrolled off-screen."""

        tokens = ["AXEventSynthesizer: Checking if", obj, "is scrolled offscreen"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rect = AXComponent.get_rect(obj)
        ancestor = ancestor or AXObject.find_ancestor(obj, AXEventSynthesizer._highest_ancestor)
        if ancestor is None:
            tokens = ["AXEventSynthesizer: Could not get ancestor of", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        ancestor_rect = AXComponent.get_rect(ancestor)
        intersection = AXComponent.get_rect_intersection(ancestor_rect, rect)
        if AXComponent.is_empty_rect(intersection):
            tokens = ["AXEventSynthesizer:", obj, "is outside of", ancestor, ancestor_rect]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if offset is None:
            tokens = ["AXEventSynthesizer:", obj, "is not scrolled offscreen"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        extents = AXText.get_character_rect(obj, offset)
        if AXComponent.is_empty_rect(extents):
            tokens = ["AXEventSynthesizer: Could not get character rect of", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        intersection = AXComponent.get_rect_intersection(extents, rect)
        if AXComponent.is_empty_rect(intersection):
            tokens = ["AXEventSynthesizer:", obj, "'s caret", extents, "not in obj", rect]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def _generate_mouse_event_new(obj, relative_x, relative_y, event):
        tokens = ["AXEventSynthesizer: Attempting to generate new mouse event on", obj,
                  f"at relative coordinates {relative_x},{relative_y}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        try:
            device = Atspi.Device.new()
            Atspi.Device.generate_mouse_event(device, obj, relative_x, relative_y, event)
        except AttributeError:
            message = "AXEventSynthesizer: Atspi.Device.generate_mouse_event requires v2.52."
            debug.print_message(debug.LEVEL_INFO, message, True)
            return False
        except Exception as error:
            message = f"AXEventSynthesizer: Exception in _generate_mouse_event_new: {error}"
            debug.print_message(debug.LEVEL_INFO, message, True)
            return False
        return True

    @staticmethod
    def _generate_mouse_event_legacy(obj, screen_x, screen_y, event):
        # TODO - JD: Remove this when we bump dependencies to AT-SPI 2.52.
        tokens = ["AXEventSynthesizer: Attempting to generate legacy mouse event on", obj,
                  f"at screen coordinates {screen_x},{screen_y}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        try:
            success = Atspi.generate_mouse_event(screen_x, screen_y, event)
        except Exception as error:
            message = f"AXEventSynthesizer: Exception in _generate_mouse_event_legacy: {error}"
            debug.print_message(debug.LEVEL_INFO, message, True)
            return False
        return success

    @staticmethod
    def _generate_mouse_event(obj, relative_x, relative_y, event):
        """Synthesize a mouse event at a specific screen coordinate."""

        if not AXEventSynthesizer._generate_mouse_event_new(obj, relative_x, relative_y, event):
            rect = AXComponent.get_rect(obj)
            screen_x, screen_y = AXEventSynthesizer._window_coordinates_to_screen_coordinates(
                rect.x + relative_x, rect.y + relative_y)
            AXEventSynthesizer._generate_mouse_event_legacy(obj, screen_x, screen_y, event)
        return True

    @staticmethod
    def _mouse_event_on_character(obj, offset, event):
        """Performs the specified mouse event on the current character in obj."""

        if offset is None:
            offset = max(AXText.get_caret_offset(obj), 0)

        if AXEventSynthesizer._is_scrolled_off_screen(obj, offset):
            AXEventSynthesizer.scroll_into_view(obj, offset)
            if AXEventSynthesizer._is_scrolled_off_screen(obj, offset):
                tokens = ["AXEventSynthesizer:", obj, "is still offscreen. Setting caret."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                AXText.set_caret_offset(obj, offset)

        extents = AXText.get_character_rect(obj, offset)
        if AXComponent.is_empty_rect(extents):
            return False

        rect = AXComponent.get_rect(obj)
        intersection = AXComponent.get_rect_intersection(extents, rect)
        if AXComponent.is_empty_rect(intersection):
            tokens = ["AXEventSynthesizer:", obj, "'s caret", extents, "not in obj", rect]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        relative_x = (extents.x - rect.x) + extents.width / 2
        relative_y = (extents.y - rect.y) + extents.height / 2
        return AXEventSynthesizer._generate_mouse_event(obj, relative_x, relative_y, event)

    @staticmethod
    def _mouse_event_on_object(obj, event):
        """Performs the specified mouse event on obj."""

        if AXEventSynthesizer._is_scrolled_off_screen(obj):
            AXEventSynthesizer.scroll_into_view(obj)
            if AXEventSynthesizer._is_scrolled_off_screen(obj):
                tokens = ["AXEventSynthesizer:", obj, "is still offscreen. Grabbing focus."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                AXObject.grab_focus(obj)

        rect = AXComponent.get_rect(obj)
        relative_x = rect.width / 2
        relative_y = rect.height / 2
        return AXEventSynthesizer._generate_mouse_event(obj, relative_x, relative_y, event)

    @staticmethod
    def route_to_character(obj, offset=None):
        """Routes the pointer to the current character in obj."""

        tokens = [f"AXEventSynthesizer: Attempting to route to offset {offset} in", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return AXEventSynthesizer._mouse_event_on_character(obj, offset, "abs")

    @staticmethod
    def route_to_object(obj):
        """Moves the mouse pointer to the center of obj."""

        tokens = ["AXEventSynthesizer: Attempting to route to", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return AXEventSynthesizer._mouse_event_on_object(obj, "abs")

    @staticmethod
    def click_character(obj, offset=None, button=1):
        """Single click on the current character in obj using the specified button."""

        tokens = [f"AXEventSynthesizer: Attempting to click at offset {offset} in", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return AXEventSynthesizer._mouse_event_on_character(obj, offset, f"b{button}c")

    @staticmethod
    def click_object(obj, button=1):
        """Single click on obj using the specified button."""

        return AXEventSynthesizer._mouse_event_on_object(obj, f"b{button}c")

    @staticmethod
    def _scroll_to_location(obj, location, start_offset=None, end_offset=None):
        """Attempts to scroll to the specified location."""

        before = AXComponent.get_position(obj)
        AXText.scroll_substring_to_location(obj, location, start_offset, end_offset)
        AXObject.clear_cache(obj, False, "To obtain updated location after scroll.")
        after = AXComponent.get_position(obj)
        tokens = ["AXEventSynthesizer: Text scroll, before:", before, "after:", after]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if before != after:
            return

        AXComponent.scroll_object_to_location(obj, location)
        AXObject.clear_cache(obj, False, "To obtain updated location after scroll.")
        after = AXComponent.get_position(obj)
        tokens = ["AXEventSynthesizer: Object scroll, before:", before, "after:", after]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    @staticmethod
    def _scroll_to_point(obj, x_coord, y_coord, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the specified point."""

        before = AXComponent.get_position(obj)
        AXText.scroll_substring_to_point(obj, x_coord, y_coord, start_offset, end_offset)
        AXObject.clear_cache(obj, False, "To obtain updated location after scroll.")
        after = AXComponent.get_position(obj)
        tokens = ["AXEventSynthesizer: Text scroll, before:", before, "after:", after]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if before != after:
            return

        AXComponent.scroll_object_to_point(obj, x_coord, y_coord)
        AXObject.clear_cache(obj, False, "To obtain updated location after scroll.")
        after = AXComponent.get_position(obj)
        tokens = ["AXEventSynthesizer: Object scroll, before:", before, "after:", after]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    @staticmethod
    def scroll_into_view(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj into view."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.ANYWHERE, start_offset, end_offset)

    @staticmethod
    def scroll_to_center(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the center of its window."""

        ancestor = AXObject.find_ancestor(obj, AXEventSynthesizer._highest_ancestor)
        if ancestor is None:
            tokens = ["AXEventSynthesizer: Could not get ancestor of", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        ancestor_rect = AXComponent.get_rect(ancestor)
        x_coord = ancestor_rect.x + ancestor_rect.width / 2
        y_coord = ancestor_rect.y + ancestor_rect.height / 2
        AXEventSynthesizer._scroll_to_point(obj, x_coord, y_coord, start_offset, end_offset)

    @staticmethod
    def scroll_to_top_edge(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the top edge."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.TOP_EDGE, start_offset, end_offset)

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

        actions = ["click", "press", "jump", "open", "activate"]
        for action in actions:
            if AXObject.do_named_action(obj, action):
                tokens = ["AXEventSynthesizer: '", action, "' on", obj, "performed successfully"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

        if debug.LEVEL_INFO < debug.debugLevel:
            return False

        tokens = ["AXEventSynthesizer: Actions on", obj, ":",
                  AXUtilitiesDebugging.actions_as_string(obj)]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

_synthesizer = AXEventSynthesizer()
def get_synthesizer():
    """Returns the Event Synthesizer."""

    return _synthesizer
