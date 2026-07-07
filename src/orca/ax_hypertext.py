# Orca
#
# Copyright 2024 Igalia, S.L.
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

"""Wrapper for the Atspi.Hypertext and Hyperlink interfaces."""

from __future__ import annotations

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import debug
from .ax_object import AXObject


class AXHypertext:
    """Wrapper for the Atspi.Hypertext and Hyperlink interfaces."""

    @staticmethod
    def get_link_count(obj: Atspi.Accessible) -> int:
        """Returns the number of hyperlinks in obj."""

        if not AXObject.supports_hypertext(obj):
            return 0

        try:
            count = Atspi.Hypertext.get_n_links(obj)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_link_count: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXHypertext:", obj, f"reports {count} hyperlinks"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def get_link_at_index(obj: Atspi.Accessible, index: int) -> Atspi.Hyperlink | None:
        """Returns the hyperlink object at the specified index."""

        if not AXObject.supports_hypertext(obj):
            return None

        try:
            link = Atspi.Hypertext.get_link(obj, index)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_link_at_index: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        return link

    @staticmethod
    def get_link_uri(obj: Atspi.Accessible, index: int = 0) -> str:
        """Returns the URI associated with obj at the specified index."""

        try:
            link = Atspi.Accessible.get_hyperlink(obj)
            uri = Atspi.Hyperlink.get_uri(link, index)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_link_uri: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        tokens = ["AXHypertext: URI of", obj, f"at index {index} is {uri}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return uri

    @staticmethod
    def get_link_start_offset(obj: Atspi.Accessible) -> int:
        """Returns the start offset of obj in the associated text."""

        if isinstance(obj, Atspi.Hyperlink):
            link = obj
            if debug.debugLevel <= debug.LEVEL_INFO:
                obj = Atspi.Hyperlink.get_object(link, 0)
        else:
            link = Atspi.Accessible.get_hyperlink(obj)

        if link is None:
            tokens = ["AXHypertext: Couldn't get hyperlink for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return -1

        try:
            offset = Atspi.Hyperlink.get_start_index(link)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_link_start_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXHypertext: Start offset of", obj, f"is {offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return offset

    @staticmethod
    def get_link_end_offset(obj: Atspi.Accessible) -> int:
        """Returns the end offset of obj in the associated text."""

        if isinstance(obj, Atspi.Hyperlink):
            link = obj
            if debug.debugLevel <= debug.LEVEL_INFO:
                obj = Atspi.Hyperlink.get_object(link, 0)
        else:
            link = Atspi.Accessible.get_hyperlink(obj)

        if link is None:
            tokens = ["AXHypertext: Couldn't get hyperlink for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return -1

        try:
            offset = Atspi.Hyperlink.get_end_index(link)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_link_end_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXHypertext: End offset of", obj, f"is {offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return offset

    @staticmethod
    def get_child_at_offset(obj: Atspi.Accessible, offset: int) -> Atspi.Accessible | None:
        """Returns the embedded-object child of obj at the specified offset."""

        if not AXObject.supports_hypertext(obj):
            return None

        try:
            index = Atspi.Hypertext.get_link_index(obj, offset)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_child_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        if index < 0:
            return None

        link = AXHypertext.get_link_at_index(obj, index)
        if link is None:
            return None

        try:
            child = Atspi.Hyperlink.get_object(link, 0)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_child_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        tokens = [f"AXHypertext: Child at offset {offset} in", obj, "is", child]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return child

    @staticmethod
    def get_child_at_link_index(obj: Atspi.Accessible, index: int) -> Atspi.Accessible | None:
        """Returns the embedded-object child of obj for the hyperlink at the specified index."""

        link = AXHypertext.get_link_at_index(obj, index)
        if link is None:
            return None

        try:
            child = Atspi.Hyperlink.get_object(link, 0)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in get_child_at_link_index: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        tokens = [f"AXHypertext: Child for link index {index} in", obj, "is", child]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return child

    @staticmethod
    def get_character_offset_in_parent(obj: Atspi.Accessible) -> int:
        """Returns the offset of the embedded-object obj in the text of its parent."""

        if not AXObject.supports_text(AXObject.get_parent(obj)):
            return -1

        return AXHypertext.get_link_start_offset(obj)
