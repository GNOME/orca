# Orca
#
# Copyright 2023-2026 Igalia, S.L.
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

"""Utilities for obtaining information about accessible objects."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class AXUtilitiesObject:
    """Utilities for obtaining information about accessible objects."""

    @staticmethod
    def _iter_ancestors(obj: Atspi.Accessible) -> Iterator[Atspi.Accessible]:
        """Yields the ancestors of obj, starting with its parent."""

        if not AXObject.is_valid(obj):
            return

        seen = {obj}
        parent = AXObject.get_parent(obj)
        while parent:
            if parent in seen:
                tokens = [
                    "AXUtilitiesObject: Circular tree suspected while walking ancestors.",
                    parent,
                    "already seen in:",
                    list(seen),
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return

            yield parent
            seen.add(parent)
            parent = AXObject.get_parent(parent)

    @staticmethod
    def _get_ancestors(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of the ancestors of obj, starting with its parent."""

        ancestors = list(AXUtilitiesObject._iter_ancestors(obj))
        ancestors.reverse()
        return ancestors

    @staticmethod
    def get_common_ancestor(
        obj1: Atspi.Accessible,
        obj2: Atspi.Accessible,
    ) -> Atspi.Accessible | None:
        """Returns the common ancestor of obj1 and obj2."""

        tokens = ["AXUtilitiesObject: Looking for common ancestor of", obj1, "and", obj2]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not (obj1 and obj2):
            return None

        if obj1 == obj2:
            return obj1

        obj1_ancestors = [*AXUtilitiesObject._get_ancestors(obj1), obj1]
        obj2_ancestors = [*AXUtilitiesObject._get_ancestors(obj2), obj2]
        result = None
        for a1, a2 in zip(obj1_ancestors, obj2_ancestors, strict=False):
            if a1 == a2:
                result = a1
            else:
                break

        tokens = ["AXUtilitiesObject: Common ancestor of", obj1, "and", obj2, "is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def find_ancestor_inclusive(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool],
    ) -> Atspi.Accessible | None:
        """Returns obj, or the ancestor of obj, for which the function pred is true"""

        if pred(obj):
            return obj

        return AXUtilitiesObject.find_ancestor(obj, pred)

    @staticmethod
    def find_outermost_ancestor_inclusive(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool],
    ) -> Atspi.Accessible | None:
        """Returns the outermost object, including obj, for which pred is true."""

        if not AXObject.is_valid(obj):
            return None

        for ancestor in AXUtilitiesObject._get_ancestors(obj):
            if pred(ancestor):
                return ancestor

        return obj if pred(obj) else None

    @staticmethod
    def find_ancestor(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool],
    ) -> Atspi.Accessible | None:
        """Returns the ancestor of obj if the function pred is true"""

        for ancestor in AXUtilitiesObject._iter_ancestors(obj):
            if pred(ancestor):
                return ancestor
            if AXObject.get_role(ancestor) in (Atspi.Role.INVALID, Atspi.Role.APPLICATION):
                break

        return None

    @staticmethod
    def is_ancestor(
        obj: Atspi.Accessible,
        ancestor: Atspi.Accessible,
        inclusive: bool = False,
    ) -> bool:
        """Returns true if ancestor is an ancestor of obj or, if inclusive, obj is ancestor."""

        if not AXObject.is_valid(obj):
            return False

        if not AXObject.is_valid(ancestor):
            return False

        if obj == ancestor and inclusive:
            return True

        return AXUtilitiesObject.find_ancestor(obj, lambda x: x == ancestor) is not None

    @staticmethod
    def label_is_ancestor_of_labelled(
        label: Atspi.Accessible, labelled_objects: list[Atspi.Accessible]
    ) -> bool:
        """Returns True if label is an ancestor of an object it is the label for."""

        return any(AXUtilitiesObject.is_ancestor(labelled, label) for labelled in labelled_objects)

    @staticmethod
    def _find_descendant(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool],
    ) -> Atspi.Accessible | None:
        """Returns the descendant of obj if the function pred is true"""

        if not AXObject.is_valid(obj):
            return None

        for i in range(AXObject.get_child_count(obj)):
            child = AXObject.get_child_checked(obj, i)
            if child is None:
                continue
            if pred(child):
                return child
            child = AXUtilitiesObject._find_descendant(child, pred)
            if child:
                return child

        return None

    @staticmethod
    def find_descendant(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool],
    ) -> Atspi.Accessible | None:
        """Returns the descendant of obj if the function pred is true"""

        start = time.time()
        result = AXUtilitiesObject._find_descendant(obj, pred)
        tokens = [
            "AXUtilitiesObject: find_descendant: found",
            result,
            "in",
            round(time.time() - start, 4),
            "s",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def find_deepest_descendant(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the deepest descendant of obj"""

        if not AXObject.is_valid(obj):
            return None

        child_count = AXObject.get_child_count(obj)
        last_child = AXObject.get_child(obj, child_count - 1, child_count)
        if last_child is None:
            return obj

        return AXUtilitiesObject.find_deepest_descendant(last_child)

    @staticmethod
    def _find_all_descendants(
        obj: Atspi.Accessible,
        include_if: Callable[[Atspi.Accessible], bool] | None,
        exclude_if: Callable[[Atspi.Accessible], bool] | None,
        matches: list[Atspi.Accessible],
    ) -> None:
        """Returns all descendants which match the specified inclusion and exclusion"""

        if not AXObject.is_valid(obj):
            return

        child_count = AXObject.get_child_count(obj)
        for i in range(child_count):
            child = AXObject.get_child(obj, i, child_count)
            if exclude_if and exclude_if(child):
                continue
            if include_if and include_if(child):
                matches.append(child)
            AXUtilitiesObject._find_all_descendants(child, include_if, exclude_if, matches)

    @staticmethod
    def find_all_descendants(
        root: Atspi.Accessible,
        include_if: Callable[[Atspi.Accessible], bool] | None = None,
        exclude_if: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants which match the specified inclusion and exclusion"""

        start = time.time()
        matches: list[Atspi.Accessible] = []
        AXUtilitiesObject._find_all_descendants(root, include_if, exclude_if, matches)
        tokens = [
            "AXUtilitiesObject: find_all_descendants:",
            len(matches),
            "matches found in",
            round(time.time() - start, 4),
            "s",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return matches

    @staticmethod
    def path_comparison(path1: list[int], path2: list[int]) -> int:
        """Returns -1, 0, or 1 to indicate if path1 is before, the same, or after path2."""

        if path1 == path2:
            return 0

        size = max(len(path1), len(path2))
        path1 = (path1 + [-1] * size)[:size]
        path2 = (path2 + [-1] * size)[:size]

        for x in range(min(len(path1), len(path2))):
            if path1[x] < path2[x]:
                return -1
            if path1[x] > path2[x]:
                return 1

        return 0
