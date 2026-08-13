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
from .ax_utilities_object import AXUtilitiesObject
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
    def _is_separate_text_element(obj: Atspi.Accessible) -> bool:
        return any(
            predicate(obj)
            for predicate in (
                AXUtilitiesRole.is_block_quote,
                AXUtilitiesRole.is_combo_box,
                AXUtilitiesRole.is_heading,
                AXUtilitiesRole.is_list,
                AXUtilitiesRole.is_list_box,
                AXUtilitiesRole.is_list_item,
                AXUtilitiesRole.is_menu_item_of_any_kind,
                AXUtilitiesRole.is_paragraph,
                AXUtilitiesRole.is_section,
                AXUtilitiesRole.is_table,
                AXUtilitiesRole.is_table_cell,
                AXUtilitiesRole.is_table_row,
            )
        )

    @staticmethod
    def _join_expanded_parts(parts: list[tuple[str, bool]]) -> str:
        result: list[str] = []
        previous_requires_separator = False
        for string, requires_separator in parts:
            if not string:
                continue
            part = string
            stripped = part.lstrip()
            if (
                result
                and (previous_requires_separator or requires_separator)
                and stripped
                and stripped[0].isalnum()
            ):
                result[-1] = result[-1].rstrip()
                part = stripped
                result.append(" ")
            result.append(part)
            previous_requires_separator = requires_separator
        return "".join(result)

    @staticmethod
    def _expand_eocs_in_subtree(
        root: Atspi.Accessible,
        start: tuple[Atspi.Accessible, int] | None,
        end: tuple[Atspi.Accessible, int] | None,
        include_start: bool,
        include_end: bool,
    ) -> str:
        """Expands a subtree, trimming it at optional text boundaries."""

        start_obj = start[0] if start is not None else None
        end_obj = end[0] if end is not None else None
        start_child = (
            AXUtilitiesHypertext._direct_descendant(start_obj, root)
            if start_obj is not None and start_obj != root
            else None
        )
        end_child = (
            AXUtilitiesHypertext._direct_descendant(end_obj, root)
            if end_obj is not None and end_obj != root
            else None
        )

        if not AXObject.supports_text(root):
            first = AXObject.get_index_in_parent(start_child) if start_child is not None else 0
            last = (
                AXObject.get_index_in_parent(end_child)
                if end_child is not None
                else AXObject.get_child_count(root) - 1
            )
            return AXUtilitiesHypertext._join_expanded_parts(
                [
                    (
                        AXUtilitiesHypertext._expand_eocs_in_subtree(
                            child,
                            start if child == start_child else None,
                            end if child == end_child else None,
                            include_start if child == start_child else True,
                            include_end if child == end_child else True,
                        ),
                        True,
                    )
                    for index in range(first, last + 1)
                    if (child := AXObject.get_child(root, index)) is not None
                ]
            )

        count = AXText.get_character_count(root)
        lower = start[1] + int(not include_start) if start is not None and start_obj == root else 0
        upper = end[1] + int(include_end) if end is not None and end_obj == root else count
        if start_child is not None:
            lower = AXHypertext.get_character_offset_in_parent(start_child)
        if end_child is not None:
            upper = AXHypertext.get_character_offset_in_parent(end_child) + 1
        lower = max(0, min(lower, count))
        upper = max(0, min(upper, count))

        boundaries = [child for child in (start_child, end_child) if child is not None]
        if len(boundaries) == 2 and boundaries[0] == boundaries[1]:
            boundaries.pop()
        parts = []
        cursor = lower
        for child in sorted(boundaries, key=AXHypertext.get_character_offset_in_parent):
            offset = AXHypertext.get_character_offset_in_parent(child)
            if not lower <= offset < upper:
                continue
            if cursor < offset:
                parts.append((AXUtilitiesHypertext.expand_eocs(root, cursor, offset), False))
            parts.append(
                (
                    AXUtilitiesHypertext._expand_eocs_in_subtree(
                        child,
                        start if child == start_child else None,
                        end if child == end_child else None,
                        include_start if child == start_child else True,
                        include_end if child == end_child else True,
                    ),
                    AXUtilitiesHypertext._is_separate_text_element(child),
                )
            )
            cursor = offset + 1
        if cursor < upper:
            parts.append((AXUtilitiesHypertext.expand_eocs(root, cursor, upper), False))
        return AXUtilitiesHypertext._join_expanded_parts(parts)

    @staticmethod
    def expand_eocs_in_range(
        start_obj: Atspi.Accessible,
        start_offset: int,
        end_obj: Atspi.Accessible | None,
        end_offset: int,
        *,
        include_start: bool = True,
        include_end: bool = True,
    ) -> str:
        """Expands embedded objects between two accessible text positions."""

        end_obj = end_obj or start_obj
        if end_offset < 0:
            end_offset = AXText.get_character_count(end_obj) - 1
        if end_offset < 0:
            return ""

        comparison = AXUtilitiesHypertext.compare_text_positions(
            start_obj,
            start_offset,
            end_obj,
            end_offset,
        )
        if comparison > 0:
            start_obj, end_obj = end_obj, start_obj
            start_offset, end_offset = end_offset, start_offset
            include_start, include_end = include_end, include_start

        root = AXUtilitiesObject.get_common_ancestor(start_obj, end_obj)
        if root is None:
            tokens = [
                "AXUtilitiesHypertext: No common ancestor for text endpoints",
                start_obj,
                start_offset,
                end_obj,
                end_offset,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        result = AXUtilitiesHypertext._expand_eocs_in_subtree(
            root,
            (start_obj, start_offset),
            (end_obj, end_offset),
            include_start,
            include_end,
        )
        tokens = [
            "AXUtilitiesHypertext: Expanded EOCs between",
            start_obj,
            start_offset,
            "and",
            end_obj,
            end_offset,
            f"with endpoint inclusion {include_start}, {include_end}: '{result}'",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def expand_eocs(
        obj: Atspi.Accessible,
        start_offset: int = 0,
        end_offset: int = -1,
    ) -> str:
        """Replaces embedded object characters in a text range with their text."""

        if AXUtilitiesRole.is_math(obj):
            if not AXObject.get_child_count(obj):
                return ""
            # pylint: disable-next=import-outside-toplevel
            from . import math_presenter

            return math_presenter.get_presenter().expand_embedded_math(obj)

        if not AXUtilitiesHypertext.can_expand_embedded_object_as_text(obj):
            return ""

        if AXUtilitiesRole.is_grid(obj) or AXUtilitiesObject.find_descendant(
            obj, AXUtilitiesRole.is_grid
        ):
            tokens = ["AXUtilitiesHypertext: Not expanding EOCs in", obj, "which contains a grid."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        text = AXText.get_substring(obj, start_offset, end_offset)
        if OBJECT_REPLACEMENT_CHARACTER not in text:
            return text

        to_build = list(text)
        for index, char in enumerate(to_build):
            if char != OBJECT_REPLACEMENT_CHARACTER:
                continue
            child = AXUtilitiesHypertext.find_child_at_offset(obj, index + start_offset)
            result = AXUtilitiesHypertext.expand_eocs(child) if child is not None else ""
            if (
                result
                and not result[-1].isspace()
                and child is not None
                and AXUtilitiesHypertext._is_separate_text_element(child)
            ):
                result += " "
            to_build[index] = result

        result = "".join(to_build)
        tokens = [
            "AXUtilitiesHypertext: Expanded EOCs for",
            obj,
            f"range {start_offset}:{end_offset}: '{result}'",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if OBJECT_REPLACEMENT_CHARACTER in result:
            msg = "AXUtilitiesHypertext: Unable to expand EOCs"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""
        return result

    @staticmethod
    def can_expand_embedded_object_as_text(obj: Atspi.Accessible | None) -> bool:
        """Returns True if an embedded object can contribute text to its parent."""

        if not AXObject.supports_text(obj) or not AXText.get_character_count(obj):
            return False
        return not any(
            predicate(obj)
            for predicate in (
                AXUtilitiesRole.is_button,
                AXUtilitiesRole.is_embedded,
                AXUtilitiesRole.is_list_box,
                AXUtilitiesRole.is_table,
                AXUtilitiesRole.is_table_row,
            )
        )

    @staticmethod
    def _direct_descendant(
        descendant: Atspi.Accessible,
        ancestor: Atspi.Accessible,
    ) -> Atspi.Accessible | None:
        """Returns the child of ancestor which contains descendant."""

        child = descendant
        parent = AXObject.get_parent(child)
        while parent is not None and parent != ancestor:
            child = parent
            parent = AXObject.get_parent(child)
        return child if parent == ancestor else None

    @staticmethod
    def compare_text_positions(
        obj1: Atspi.Accessible,
        offset1: int,
        obj2: Atspi.Accessible,
        offset2: int,
    ) -> int:
        """Returns the relative document order of two accessible text positions."""

        if obj1 == obj2:
            return (offset1 > offset2) - (offset1 < offset2)

        if AXUtilitiesObject.is_ancestor(obj2, obj1):
            child = AXUtilitiesHypertext._direct_descendant(obj2, obj1)
            if child is not None:
                child_offset = AXHypertext.get_character_offset_in_parent(child)
                if child_offset >= 0:
                    if offset1 != child_offset:
                        return (offset1 > child_offset) - (offset1 < child_offset)
                    return 0 if offset2 == 0 else -1

        if AXUtilitiesObject.is_ancestor(obj1, obj2):
            return -AXUtilitiesHypertext.compare_text_positions(obj2, offset2, obj1, offset1)

        return AXUtilitiesObject.path_comparison(
            AXObject.get_path(obj1),
            AXObject.get_path(obj2),
        )

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
