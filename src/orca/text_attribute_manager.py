# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Manager for text attribute presentation preferences."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any

from . import dbus_service, debug, gsettings_registry
from .ax_text import AXTextAttribute

if TYPE_CHECKING:
    from .text_attribute_manager_preferences_grid import TextAttributePreferencesGrid


class PresentationMode(enum.IntEnum):
    """How a text attribute should be presented."""

    NONE = 0
    SPEAK = 1
    BRAILLE = 2
    SPEAK_AND_BRAILLE = 3


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.TextAttributeChangeMode",
    values={"off": 0, "editable-only": 1, "always": 2},
)
class TextAttributeChangeMode(enum.Enum):
    """When to announce text attribute changes during navigation."""

    OFF = 0
    EDITABLE_ONLY = 1
    ALWAYS = 2


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.TextAttributes",
    name="text-attributes",
)
class TextAttributeManager:
    """Manager for text attribute presentation settings."""

    _SCHEMA = "text-attributes"
    KEY_ATTRIBUTES_TO_SPEAK = "attributes-to-speak"
    KEY_ATTRIBUTES_TO_BRAILLE = "attributes-to-braille"

    def _get_setting(self, key: str, gtype: str, default: Any) -> Any:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            gtype,
            default=default,
        )

    def __init__(self) -> None:
        msg = "TEXT ATTRIBUTE MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("TextAttributeManager", self)

    def create_preferences_grid(self) -> TextAttributePreferencesGrid:
        """Create and return a preferences grid for text attributes."""

        # pylint: disable-next=import-outside-toplevel
        from .text_attribute_manager_preferences_grid import TextAttributePreferencesGrid

        return TextAttributePreferencesGrid()

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ATTRIBUTES_TO_SPEAK,
        schema="text-attributes",
        gtype="as",
        default=[],
        summary="Text attributes to speak",
        migration_key="textAttributesToSpeak",
    )
    @dbus_service.getter
    def get_attributes_to_speak(self) -> list[str]:
        """Returns the list of text attributes to speak."""

        return self._get_setting(self.KEY_ATTRIBUTES_TO_SPEAK, "as", [])

    def get_resolved_attributes_to_speak(self) -> list[AXTextAttribute]:
        """Returns the resolved list of attributes to speak, falling back to defaults."""

        result = list(
            filter(None, map(AXTextAttribute.from_string, self.get_attributes_to_speak()))
        )
        if not result:
            result = [a for a in AXTextAttribute if a.should_present_by_default()]
        return result

    @dbus_service.setter
    def set_attributes_to_speak(self, value: list[str]) -> bool:
        """Sets the list of text attributes to speak."""

        if self.get_attributes_to_speak() == value:
            return True

        msg = f"TEXT ATTRIBUTE MANAGER: Setting attributes to speak to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ATTRIBUTES_TO_SPEAK,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ATTRIBUTES_TO_BRAILLE,
        schema="text-attributes",
        gtype="as",
        default=[],
        summary="Text attributes to mark in braille",
        migration_key="textAttributesToBraille",
    )
    @dbus_service.getter
    def get_attributes_to_braille(self) -> list[str]:
        """Returns the list of text attributes to mark in braille."""

        return self._get_setting(self.KEY_ATTRIBUTES_TO_BRAILLE, "as", [])

    @dbus_service.setter
    def set_attributes_to_braille(self, value: list[str]) -> bool:
        """Sets the list of text attributes to mark in braille."""

        if self.get_attributes_to_braille() == value:
            return True

        msg = f"TEXT ATTRIBUTE MANAGER: Setting attributes to braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ATTRIBUTES_TO_BRAILLE,
            value,
        )
        return True


_manager = TextAttributeManager()


def get_manager() -> TextAttributeManager:
    """Return the singleton TextAttributeManager instance."""

    return _manager
