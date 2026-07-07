# Orca
#
# Copyright 2026 Igalia, S.L.
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

"""Hypertext and hyperlink utilities."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from . import debug
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities_role import AXUtilitiesRole

if TYPE_CHECKING:
    from collections.abc import Callable

    from gi.repository import Atspi

OBJECT_REPLACEMENT_CHARACTER = "\ufffc"
ZERO_WIDTH_NO_BREAK_SPACE = "\ufeff"


@dataclass(frozen=True)
class CaretPolicy:
    """The per-script decisions the caret-order walker delegates to."""

    can_have_caret_context: Callable[[Atspi.Accessible], bool]
    treat_as_text_object: Callable[[Atspi.Accessible], bool]
    treat_as_whole: Callable[[Atspi.Accessible, int | None], bool]
    in_document_content: Callable[[Atspi.Accessible], bool]
    is_boundary: Callable[[Atspi.Accessible], bool]
    is_text_block_element: Callable[[Atspi.Accessible], bool]


class AXUtilitiesHypertext:
    """Hypertext and hyperlink utilities."""

    @staticmethod
    def find_child_at_offset(obj: Atspi.Accessible, offset: int) -> Atspi.Accessible | None:
        """Returns the child at offset, indexed by the object-replacement characters before it."""

        text = AXText.get_all_text(obj)
        if not (0 <= offset < len(text)) or text[offset] != OBJECT_REPLACEMENT_CHARACTER:
            return None

        index = text[:offset].count(OBJECT_REPLACEMENT_CHARACTER)
        child = AXHypertext.get_child_at_link_index(obj, index)
        if child is not None and AXHypertext.get_character_offset_in_parent(child) == offset:
            return child

        tokens = [
            "AXUtilitiesHypertext: object-replacement count",
            index,
            "for offset",
            offset,
            "did not yield a child in",
            obj,
            "; got",
            child,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return None

    @staticmethod
    def is_valid_position(obj: Atspi.Accessible, offset: int, policy: CaretPolicy) -> bool:
        """Returns True if the caret can rest at obj, offset."""

        # A non-text object holds the caret as a whole; a text object holds it at a real
        # character (not the object-replacement char for an embedded child). An entry always
        # qualifies. An object-replacement-char offset is not a valid position: the caret
        # belongs in the child there, which is the signal to descend.
        if not policy.treat_as_text_object(obj):
            return policy.can_have_caret_context(obj)
        text = AXText.get_all_text(obj)
        if 0 <= offset < len(text) and text[offset] != OBJECT_REPLACEMENT_CHARACTER:
            return True
        return AXUtilitiesRole.is_entry(obj)

    @staticmethod
    def get_all_links_in_range(
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
    ) -> list[Atspi.Hyperlink]:
        """Returns all the hyperlinks in obj who started within the specified range."""

        links = []
        for i in range(AXHypertext.get_link_count(obj)):
            link = AXHypertext.get_link_at_index(obj, i)
            if link is None:
                continue
            if (
                start_offset <= AXHypertext.get_link_start_offset(link) < end_offset
                or start_offset < AXHypertext.get_link_end_offset(link) <= end_offset
            ):
                links.append(link)

        tokens = [
            f"AXUtilitiesHypertext: {len(links)} hyperlinks found in",
            obj,
            f"between start: {start_offset} and end: {end_offset}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return links

    @staticmethod
    def get_all_links(obj: Atspi.Accessible) -> list[Atspi.Hyperlink]:
        """Returns a list of all the hyperlinks in obj."""

        links = []
        for i in range(AXHypertext.get_link_count(obj)):
            link = AXHypertext.get_link_at_index(obj, i)
            if link is not None:
                links.append(link)

        tokens = [f"AXUtilitiesHypertext: {len(links)} hyperlinks found in", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return links

    @staticmethod
    def get_link_basename(
        obj: Atspi.Accessible,
        index: int = 0,
        remove_extension: bool = False,
    ) -> str:
        """Strip directory and suffix off of the URL associated with obj."""

        uri = AXHypertext.get_link_uri(obj, index)
        if not uri:
            return ""

        parsed_uri = urlparse(uri)
        basename = os.path.basename(parsed_uri.path)
        if remove_extension:
            basename = os.path.splitext(basename)[0]
            basename = re.sub(r"[-_]", " ", basename)

        tokens = ["AXUtilitiesHypertext: Basename for link", obj, f"is '{basename}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return basename

    @staticmethod
    def find_next_context(
        obj: Atspi.Accessible | None, offset: int, policy: CaretPolicy
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the next caret position in document order from obj at offset."""

        rv = AXUtilitiesHypertext._find_context(obj, offset, policy, previous=False)
        tokens = ["AXUtilitiesHypertext: Next context for", obj, offset, ":", rv[0], rv[1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rv

    @staticmethod
    def find_previous_context(
        obj: Atspi.Accessible | None, offset: int, policy: CaretPolicy
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the previous caret position in document order from obj at offset."""

        rv = AXUtilitiesHypertext._find_context(obj, offset, policy, previous=True)
        tokens = [
            "AXUtilitiesHypertext: Previous context for",
            obj,
            offset,
            ":",
            rv[0],
            rv[1],
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rv

    @staticmethod
    def search_for_caret_context(
        obj: Atspi.Accessible,
        policy: CaretPolicy,
        is_document: Callable[[Atspi.Accessible], bool],
    ) -> tuple[Atspi.Accessible, int]:
        """Returns the caret context found by descending into obj at its caret offset."""

        tokens = ["AXUtilitiesHypertext: Searching for caret context in", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        container = obj
        context_obj, context_offset = None, -1
        while obj:
            offset = AXText.get_caret_offset(obj)
            if offset < 0:
                break
            context_obj, context_offset = obj, offset
            if AXUtilitiesRole.is_math(obj):
                break
            child = AXUtilitiesHypertext.find_child_at_offset(obj, offset)
            if not child:
                break
            obj = child

        if context_obj:
            return AXUtilitiesHypertext.find_next_context(
                context_obj, max(-1, context_offset - 1), policy
            )

        if is_document(container):
            return container, 0

        return None, -1

    @staticmethod
    def _find_context(
        obj: Atspi.Accessible | None, offset: int, policy: CaretPolicy, previous: bool
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the next or previous caret position in document order from obj at offset."""

        if not obj or not policy.in_document_content(obj):
            return None, -1

        within = AXUtilitiesHypertext._context_within_object(obj, offset, policy, previous)
        if within is not None:
            return within

        if policy.is_boundary(obj):
            return None, -1

        return AXUtilitiesHypertext._context_in_ancestors(obj, policy, previous)

    @staticmethod
    def _context_within_object(
        obj: Atspi.Accessible, offset: int, policy: CaretPolicy, previous: bool
    ) -> tuple[Atspi.Accessible | None, int] | None:
        """Returns a caret position contained in obj, or None to walk up the tree instead."""

        if not policy.can_have_caret_context(obj):
            return None

        all_text = AXText.get_all_text(obj) if policy.treat_as_text_object(obj) else ""
        if all_text:
            for i in AXUtilitiesHypertext._scan_indices(offset, len(all_text), previous):
                stop = AXUtilitiesHypertext._context_at_offset(
                    obj, i, all_text[i], policy, previous
                )
                if stop is not None:
                    return stop
            return None

        if (count := AXObject.get_child_count(obj)) and not policy.treat_as_whole(obj, offset):
            return AXUtilitiesHypertext._find_context(
                AXObject.get_child(obj, count - 1 if previous else 0), -1, policy, previous
            )
        if offset < 0 and not policy.is_text_block_element(obj):
            return obj, 0
        return None

    @staticmethod
    def _scan_indices(offset: int, length: int, previous: bool) -> range:
        """Returns the offsets to scan within a text object of the given length."""

        if previous:
            if offset == -1 or offset > length:
                offset = length
            return range(offset - 1, -1, -1)
        return range(offset + 1, length)

    @staticmethod
    def _context_at_offset(
        obj: Atspi.Accessible, offset: int, char: str, policy: CaretPolicy, previous: bool
    ) -> tuple[Atspi.Accessible | None, int] | None:
        """Returns the caret stop at the given offset within obj, or None to keep scanning."""

        # Barring user-agent brokenness, an embedded child only sits at an object-replacement
        # char, so skip the lookup on plain text.
        child = (
            AXUtilitiesHypertext.find_child_at_offset(obj, offset)
            if char == OBJECT_REPLACEMENT_CHARACTER
            else None
        )
        if policy.can_have_caret_context(child):
            if policy.treat_as_whole(child, -1):
                return child, 0
            return AXUtilitiesHypertext._find_context(child, -1, policy, previous)
        if char not in (OBJECT_REPLACEMENT_CHARACTER, ZERO_WIDTH_NO_BREAK_SPACE):
            return obj, offset
        return None

    @staticmethod
    def _context_in_ancestors(
        obj: Atspi.Accessible, policy: CaretPolicy, previous: bool
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the next/previous caret position found by walking up from obj."""

        while obj and (parent := AXObject.get_parent(obj)):
            if not AXObject.is_valid(parent):
                debug.print_message(
                    debug.LEVEL_INFO, "AXUtilitiesHypertext: Parent is not valid.", True
                )
                break

            if policy.treat_as_text_object(parent):
                start = AXHypertext.get_link_start_offset(obj)
                end = AXHypertext.get_link_end_offset(obj)
                length = AXText.get_character_count(parent)
                if start + 1 == end and 0 <= start < end <= length:
                    return AXUtilitiesHypertext._find_context(parent, start, policy, previous)

            sibling = (
                AXObject.get_previous_sibling(obj) if previous else AXObject.get_next_sibling(obj)
            )
            if sibling:
                return AXUtilitiesHypertext._find_context(sibling, -1, policy, previous)
            obj = parent

        return None, -1
