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

import time

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
from .ax_utilities_role import AXUtilitiesRole

class AXEventSynthesizer:
    """Provides support for synthesizing accessible input events."""

    _banner = None

    @staticmethod
    def _window_coordinates_to_screen_coordinates(x, y):
        # TODO - JD: This is a workaround to keep things working until we have something like
        # https://gitlab.gnome.org/GNOME/at-spi2-core/-/issues/158
        active_window = focus_manager.get_manager().get_active_window()
        if active_window is None:
            msg = "AXEventSynthesizer: Could not get active window to adjust coordinates"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return x, y

        try:
            point = Atspi.Component.get_position(active_window, Atspi.CoordType.SCREEN)
        except Exception as error:
            msg = f"AXEventSynthesizer: Exception in calling get_position: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return x, y

        msg = f"AXEventSynthesizer: Active window position: {point.x}, {point.y}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # Unfortunately, the position we get does not seem to include window decorations.
        # So we have to do more work to adjust. This is why we cannot have nice things.
        gdk_window = Gtk.Window().get_screen().get_active_window()
        frame_extents = gdk_window.get_frame_extents()
        title_bar_height = frame_extents.height - gdk_window.get_height()
        msg = f"AXEventSynthesizer: Title bar height believed to be: {title_bar_height}px"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        new_x = x + point.x
        new_y = y + point.y + title_bar_height

        msg = f"AXEventSynthesizer: x: {x}->{new_x}, y: {y}->{new_y}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return new_x, new_y

    @staticmethod
    def _get_mouse_coordinates():
        """Returns the current mouse coordinates."""

        root_window = Gtk.Window().get_screen().get_root_window()
        _window, x_coord, y_coord, _modifiers = root_window.get_pointer()
        tokens = ["AXEventSynthesizer: Mouse coordinates:", x_coord, ",", y_coord]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return x_coord, y_coord

    @staticmethod
    def _generate_mouse_event(x_coord, y_coord, event):
        """Synthesize a mouse event at a specific screen coordinate."""

        old_x, old_y = AXEventSynthesizer._get_mouse_coordinates()
        tokens = ["AXEventSynthesizer: Generating", event, "mouse event at", x_coord, ",", y_coord]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        screen_x, screen_y = AXEventSynthesizer._window_coordinates_to_screen_coordinates(
            x_coord, y_coord)

        try:
            success = Atspi.generate_mouse_event(screen_x, screen_y, event)
        except Exception as error:
            tokens = ["AXEventSynthesizer: Exception in _generate_mouse_event:", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            success = False
        else:
            tokens = ["AXEventSynthesizer: Atspi.generate_mouse_event returned", success]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        # There seems to be a timeout / lack of reply from this blocking call.
        # But often the mouse event is successful. Pause briefly before checking.
        time.sleep(1)

        new_x, new_y = AXEventSynthesizer._get_mouse_coordinates()
        if old_x == new_x and old_y == new_y and (old_x, old_y) != (screen_x, screen_y):
            msg = "AXEventSynthesizer: Mouse event possible failure. Pointer didn't move"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    @staticmethod
    def _mouse_event_on_character(obj, event):
        """Performs the specified mouse event on the current character in obj."""

        extents = AXText.get_character_rect(obj)
        if AXComponent.is_empty_rect(extents):
            return False

        rect = AXComponent.get_rect(obj)
        intersection = AXComponent.get_rect_intersection(extents, rect)
        if AXComponent.is_empty_rect(intersection):
            tokens = ["AXEventSynthesizer:", obj, "'s caret", extents, "not in obj", rect]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        x_coord = max(extents.x, extents.y + (extents.width / 2) - 1)
        y_coord = extents.y + extents.height / 2
        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, event)

    @staticmethod
    def _mouse_event_on_object(obj, event):
        """Performs the specified mouse event on obj."""

        x_coord, y_coord = AXComponent.get_center_point(obj)
        return AXEventSynthesizer._generate_mouse_event(x_coord, y_coord, event)

    @staticmethod
    def route_to_character(obj):
        """Routes the pointer to the current character in obj."""

        tokens = ["AXEventSynthesizer: Attempting to route to character in", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return AXEventSynthesizer._mouse_event_on_character(obj, "abs")

    @staticmethod
    def route_to_object(obj):
        """Moves the mouse pointer to the center of obj."""

        tokens = ["AXEventSynthesizer: Attempting to route to", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
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
    def _scroll_to_location(obj, location, start_offset=None, end_offset=None):
        """Attempts to scroll to the specified location."""

        before = AXComponent.get_position(obj)
        if not AXText.scroll_substring_to_location(obj, location, start_offset, end_offset):
            AXComponent.scroll_object_to_location(obj, location)

        after = AXComponent.get_position(obj)
        tokens = ["AXEventSynthesizer: Before scroll:", before, "After scroll:", after]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    @staticmethod
    def _scroll_to_point(obj, x_coord, y_coord, start_offset=None, end_offset=None):
        """Attempts to scroll obj to the specified point."""

        before = AXComponent.get_position(obj)
        if not AXText.scroll_substring_to_point(obj, x_coord, y_coord, start_offset, end_offset):
            AXComponent.scroll_object_to_point(obj, x_coord, y_coord)

        after = AXComponent.get_position(obj)
        tokens = ["AXEventSynthesizer: Before scroll:", before, "After scroll:", after]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    @staticmethod
    def scroll_into_view(obj, start_offset=None, end_offset=None):
        """Attempts to scroll obj into view."""

        AXEventSynthesizer._scroll_to_location(
            obj, Atspi.ScrollType.ANYWHERE, start_offset, end_offset)

    @staticmethod
    def _containing_document(obj):
        """Returns the document containing obj"""

        document = AXObject.find_ancestor(obj, AXUtilitiesRole.is_document)
        while document:
            ancestor = AXObject.find_ancestor(document, AXUtilitiesRole.is_document)
            if ancestor is None or ancestor == document:
                break
            document = ancestor

        return document

    @staticmethod
    def _get_obscuring_banner(obj):
        """"Returns the banner obscuring obj from view."""

        document = AXEventSynthesizer._containing_document(obj)
        if not document:
            tokens = ["AXEventSynthesizer: No obscuring banner found for", obj, ". No document."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        if not AXObject.supports_component(document):
            tokens = ["AXEventSynthesizer: No obscuring banner found for", obj, ". No doc iface."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        obj_rect = AXComponent.get_rect(obj)
        doc_rect = AXComponent.get_rect(document)
        left = AXComponent.get_descendant_at_point(document, doc_rect.x, obj_rect.y)
        right = AXComponent.get_descendant_at_point(
            document, doc_rect.x + doc_rect.width, obj_rect.y)
        if not (left and right and left == right != document):
            tokens = ["AXEventSynthesizer: No obscuring banner found for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        tokens = ["AXEventSynthesizer:", obj, "believed to be obscured by banner", left]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return left

    @staticmethod
    def _scroll_below_banner(obj, banner, start_offset, end_offset, margin=25):
        """Attempts to scroll obj below banner."""

        obj_rect = AXComponent.get_rect(obj)
        banner_rect = AXComponent.get_rect(banner)

        tokens = ["AXEventSynthesizer: Extents of banner: ", banner_rect]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        AXEventSynthesizer._scroll_to_point(
            obj, obj_rect.x, banner_rect.y + banner_rect.height + margin, start_offset, end_offset)

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

        actions = ["click", "press", "jump", "open", "activate"]
        for action in actions:
            if AXObject.do_named_action(obj, action):
                tokens = ["AXEventSynthesizer: '", action, "' on", obj, "performed successfully"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return True

        if debug.LEVEL_INFO < debug.debugLevel:
            return False

        tokens = ["AXEventSynthesizer: Actions on", obj, ":", AXObject.actions_as_string(obj)]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return False

_synthesizer = AXEventSynthesizer()
def get_synthesizer():
    """Returns the Event Synthesizer."""

    return _synthesizer
