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

# pylint: disable=wrong-import-position

"""Utilities for obtaining information about accessible hypertext and hyperlinks."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L."
__license__   = "LGPL"

import os
import re
from urllib.parse import urlparse

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from .ax_object import AXObject

class AXHypertext:
    """Utilities for obtaining information about accessible hypertext and hyperlinks."""

    @staticmethod
    def _get_link_count(obj: Atspi.Accessible) -> int:
        """Returns the number of hyperlinks in obj."""

        if not AXObject.supports_hypertext(obj):
            return 0

        try:
            count = Atspi.Hypertext.get_n_links(obj)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in _get_link_count: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXHypertext:", obj, f"reports {count} hyperlinks"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def _get_link_at_index(obj: Atspi.Accessible, index: int) -> Atspi.Hyperlink | None:
        """Returns the hyperlink object at the specified index."""

        if not AXObject.supports_hypertext(obj):
            return None

        try:
            link = Atspi.Hypertext.get_link(obj, index)
        except GLib.GError as error:
            msg = f"AXHypertext: Exception in _get_link_at_index: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        return link

    @staticmethod
    def get_all_links_in_range(
        obj: Atspi.Accessible, start_offset: int, end_offset: int
    ) -> list[Atspi.Hyperlink]:
        """Returns all the hyperlinks in obj who started within the specified range."""

        links = []
        for i in range(AXHypertext._get_link_count(obj)):
            link = AXHypertext._get_link_at_index(obj, i)
            if start_offset <= AXHypertext.get_link_start_offset(link) < end_offset \
               or start_offset < AXHypertext.get_link_end_offset(link) <= end_offset:
                links.append(link)

        tokens = [f"AXHypertext: {len(links)} hyperlinks found in", obj,
                  f"between start: {start_offset} and end: {end_offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return links

    @staticmethod
    def get_all_links(obj: Atspi.Accessible) -> list[Atspi.Hyperlink]:
        """Returns a list of all the hyperlinks in obj."""

        links = []
        for i in range(AXHypertext._get_link_count(obj)):
            link = AXHypertext._get_link_at_index(obj, i)
            if link is not None:
                links.append(link)

        tokens = [f"AXHypertext: {len(links)} hyperlinks found in", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return links

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
    def get_link_basename(
        obj: Atspi.Accessible, index: int = 0, remove_extension: bool = False
    ) -> str:
        """Strip directory and suffix off of the URL associated with obj."""

        uri = AXHypertext.get_link_uri(obj, index)
        if not uri:
            return ""

        parsed_uri = urlparse(uri)
        basename =  os.path.basename(parsed_uri.path)
        if remove_extension:
            basename = os.path.splitext(basename)[0]
            basename = re.sub(r"[-_]", " ", basename)

        tokens = ["AXHypertext: Basename for link", obj, f"is '{basename}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return basename

    @staticmethod
    def find_child_at_offset(obj: Atspi.Accessible, offset: int) -> Atspi.Accessible | None:
        """Attempts to correct for off-by-one brokenness in implementations"""

        if child := AXHypertext.get_child_at_offset(obj, offset):
            return child

        if child_before := AXHypertext.get_child_at_offset(obj, offset - 1):
            offset_in_parent = AXHypertext.get_character_offset_in_parent(child_before)
            if offset_in_parent == offset:
                tokens = [f"AXHypertext: Corrected child at offset {offset} in", obj, "is",
                          child_before, f"at offset {offset - 1}"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return child_before

        if child_after := AXHypertext.get_child_at_offset(obj, offset + 1):
            offset_in_parent = AXHypertext.get_character_offset_in_parent(child_after)
            if offset_in_parent == offset:
                tokens = [f"AXHypertext: Corrected child at offset {offset} in", obj, "is",
                          child_after, f"at offset {offset + 1}"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return child_after

        return None

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

        link = AXHypertext._get_link_at_index(obj, index)
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
    def get_character_offset_in_parent(obj: Atspi.Accessible) -> int:
        """Returns the offset of the embedded-object obj in the text of its parent."""

        if not AXObject.supports_text(AXObject.get_parent(obj)):
            return -1

        return AXHypertext.get_link_start_offset(obj)
