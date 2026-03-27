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

"""Utilities for reconstructing MathML from the accessibility tree."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, ClassVar

from . import debug
from .ax_object import AXObject
from .ax_utilities_role import AXUtilitiesRole

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class AXUtilitiesMath:
    """Utilities for reconstructing MathML from accessible math objects."""

    _MATHML_ATTRIBUTES: ClassVar[dict[str, list[str]]] = {
        "menclose": ["notation"],
        "mfenced": ["open", "close", "separators"],
        "mfrac": ["linethickness"],
        "mo": ["form", "stretchy", "fence", "separator", "largeop", "movablelimits", "accent"],
        "mspace": ["width", "height", "depth"],
        "mstyle": ["mathvariant", "mathsize", "mathcolor", "mathbackground"],
        "mpadded": ["width", "height", "depth", "lspace", "voffset"],
        "mtable": ["align", "columnalign", "rowalign"],
        "mtr": ["columnalign", "rowalign"],
        "mtd": ["columnalign", "rowalign", "columnspan", "rowspan"],
        "mi": ["mathvariant"],
        "mn": ["mathvariant"],
        "ms": ["lquote", "rquote"],
    }

    _TOKEN_TAGS: ClassVar[set[str]] = {"mi", "mn", "mo", "mtext", "ms", "mspace"}

    @staticmethod
    def get_mathml(obj: Atspi.Accessible) -> str:
        """Returns a MathML string reconstructed from the accessible tree rooted at obj."""

        math_root = AXUtilitiesMath.find_math_root(obj)
        if math_root is None:
            return ""

        parts: list[str] = []
        AXUtilitiesMath._serialize(math_root, parts)
        result = "".join(parts)
        msg = f"AXUtilitiesMath: Reconstructed MathML: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @staticmethod
    def find_math_root(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Walks up the tree to find the top-level math element."""

        if not AXObject.is_valid(obj):
            return None

        if AXUtilitiesRole.is_math(obj):
            return obj

        candidate = obj
        while AXObject.is_valid(candidate):
            if AXUtilitiesRole.is_math(candidate):
                return candidate
            parent = AXObject.get_parent(candidate)
            if parent is None or parent == candidate:
                break
            candidate = parent

        if AXUtilitiesRole.is_math_related(obj):
            tokens = ["AXUtilitiesMath: Could not find math root from", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return None

    @staticmethod
    def _get_tag(obj: Atspi.Accessible) -> str:
        """Returns the MathML tag for an accessible object."""

        return AXObject.get_attribute(obj, "tag")

    @staticmethod
    def _get_text_content(obj: Atspi.Accessible) -> str:
        """Returns the text content for a MathML token element."""

        name = AXObject.get_name(obj)
        if name:
            return name

        # Some token elements might have children that contain the text.
        parts: list[str] = []
        for child in AXObject.iter_children(obj):
            child_name = AXObject.get_name(child)
            if child_name:
                parts.append(child_name)
        return "".join(parts)

    @staticmethod
    def _serialize(obj: Atspi.Accessible, parts: list[str]) -> None:
        """Recursively serializes an accessible math object into MathML parts."""

        tag = AXUtilitiesMath._get_tag(obj)
        if not tag:
            tokens = ["AXUtilitiesMath: No tag found for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            text = AXObject.get_name(obj)
            if text:
                parts.append(escape(text))
            return

        # Build the opening tag with attributes.
        parts.append(f"<{tag}")
        attrs = AXObject.get_attributes_dict(obj)
        attr_names = AXUtilitiesMath._MATHML_ATTRIBUTES.get(tag, [])
        for attr_name in attr_names:
            value = attrs.get(attr_name)
            if value:
                parts.append(f' {attr_name}="{escape(value, quote=True)}"')
        parts.append(">")

        if tag in AXUtilitiesMath._TOKEN_TAGS:
            text = AXUtilitiesMath._get_text_content(obj)
            parts.append(escape(text))
        else:
            for child in AXObject.iter_children(obj):
                AXUtilitiesMath._serialize(child, parts)

        parts.append(f"</{tag}>")
