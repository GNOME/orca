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

"""Declarative preferences for user extensions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class ExtensionPreferenceKind(Enum):
    """Supported user-extension preference control kinds."""

    BOOLEAN = "boolean"
    STRING = "string"
    PATH = "path"
    COLOR = "color"
    INTEGER = "integer"
    FLOAT = "float"
    ENUM = "enum"
    STRING_LIST = "string-list"
    DICTIONARY = "dictionary"


@dataclass(frozen=True)
class ExtensionPreference:
    """Declarative description of one user-extension preference."""

    key: str
    label: str
    default: Any
    kind: ExtensionPreferenceKind
    minimum: int | float | None = None
    maximum: int | float | None = None
    options: tuple[tuple[Any, str], ...] = ()
    item_validator: Callable[[str], bool] | None = None
    item_error: str = ""
    directory: bool = False

    @classmethod
    def boolean(cls, key: str, label: str, default: bool = False) -> ExtensionPreference:
        """Return a boolean preference."""

        return cls(key, label, default, ExtensionPreferenceKind.BOOLEAN)

    @classmethod
    def string(cls, key: str, label: str, default: str = "") -> ExtensionPreference:
        """Return a string preference."""

        return cls(key, label, default, ExtensionPreferenceKind.STRING)

    @classmethod
    def path(
        cls,
        key: str,
        label: str,
        default: str = "",
        *,
        directory: bool = False,
    ) -> ExtensionPreference:
        """Return a file or directory path preference."""

        return cls(key, label, default, ExtensionPreferenceKind.PATH, directory=directory)

    @classmethod
    def color(cls, key: str, label: str, default: str = "#000000") -> ExtensionPreference:
        """Return a color preference stored as a hex string."""

        return cls(key, label, default, ExtensionPreferenceKind.COLOR)

    @classmethod
    def integer(
        cls,
        key: str,
        label: str,
        default: int = 0,
        minimum: int = 0,
        maximum: int = 100,
    ) -> ExtensionPreference:
        """Return an integer preference."""

        return cls(key, label, default, ExtensionPreferenceKind.INTEGER, minimum, maximum)

    @classmethod
    def floating(
        cls,
        key: str,
        label: str,
        default: float = 0.0,
        minimum: float = 0.0,
        maximum: float = 1.0,
    ) -> ExtensionPreference:
        """Return a floating-point preference."""

        return cls(key, label, default, ExtensionPreferenceKind.FLOAT, minimum, maximum)

    @classmethod
    def enum(
        cls,
        key: str,
        label: str,
        options: tuple[tuple[Any, str], ...],
        default: Any,
    ) -> ExtensionPreference:
        """Return an enumerated preference."""

        return cls(key, label, default, ExtensionPreferenceKind.ENUM, options=options)

    @classmethod
    def string_list(
        cls,
        key: str,
        label: str,
        default: list[str] | None = None,
        item_validator: Callable[[str], bool] | None = None,
        item_error: str = "",
    ) -> ExtensionPreference:
        """Return a string-list preference."""

        return cls(
            key,
            label,
            default or [],
            ExtensionPreferenceKind.STRING_LIST,
            item_validator=item_validator,
            item_error=item_error,
        )

    @classmethod
    def dictionary(
        cls,
        key: str,
        label: str,
        default: dict[str, bool | int | float | str] | None = None,
    ) -> ExtensionPreference:
        """Return a dictionary preference."""

        return cls(key, label, default or {}, ExtensionPreferenceKind.DICTIONARY)


GENERATED_DIALOG_KINDS = {
    ExtensionPreferenceKind.BOOLEAN,
    ExtensionPreferenceKind.STRING,
    ExtensionPreferenceKind.PATH,
    ExtensionPreferenceKind.COLOR,
    ExtensionPreferenceKind.INTEGER,
    ExtensionPreferenceKind.FLOAT,
    ExtensionPreferenceKind.ENUM,
    ExtensionPreferenceKind.STRING_LIST,
}


def is_supported_in_generated_dialog(preference: ExtensionPreference) -> bool:
    """Return True if Orca's generated dialog can display preference."""

    return preference.kind in GENERATED_DIALOG_KINDS
