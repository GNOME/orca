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

"""Settings keys and values for Say All."""

from __future__ import annotations

from enum import Enum

from . import gsettings_registry


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.SayAllStyle",
    values={"line": 0, "sentence": 1},
)
class SayAllStyle(Enum):
    """Style enumeration with int values from settings."""

    SENTENCE = 1
    LINE = 0

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


class SayAllSettings:
    """The Say All settings keys."""

    KEY_ANNOUNCE_ARTICLE = "announce-article"
    KEY_ANNOUNCE_BLOCKQUOTE = "announce-blockquote"
    KEY_ANNOUNCE_CODE_BLOCK = "announce-code-block"
    KEY_ANNOUNCE_DOCUMENT = "announce-document"
    KEY_ANNOUNCE_FORM = "announce-form"
    KEY_ANNOUNCE_GROUPING = "announce-grouping"
    KEY_ANNOUNCE_HEADER_AND_FOOTER = "announce-header-and-footer"
    KEY_ANNOUNCE_INLINE_CODE = "announce-inline-code"
    KEY_ANNOUNCE_LANDMARK = "announce-landmark"
    KEY_ANNOUNCE_LIST = "announce-list"
    KEY_ANNOUNCE_TABLE = "announce-table"
    KEY_ANNOUNCE_TRACKED_CHANGES = "announce-tracked-changes"
    KEY_ONLY_SPEAK_DISPLAYED_TEXT = "only-speak-displayed-text"
    KEY_REWIND_AND_FAST_FORWARD = "rewind-and-fast-forward"
    KEY_STRUCTURAL_NAVIGATION = "structural-navigation"
    KEY_STYLE = "style"
    KEY_TEXT_ATTRIBUTE_CHANGE_MODE = "text-attribute-change-mode"
