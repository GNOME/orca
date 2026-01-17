# Unit tests for text_attribute_manager.py methods.
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

# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=no-member

"""Unit tests for text_attribute_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestTextAttributeManager:
    """Test TextAttributeManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for text_attribute_manager module testing."""

        additional_modules: list[str] = []
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        settings_mock = essential_modules["orca.settings"]
        settings_mock.textAttributesToSpeak = []
        settings_mock.textAttributesToBraille = []

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test TextAttributeManager initialization."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        assert manager is not None

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller = dbus_service_mock.get_remote_controller.return_value
        controller.register_decorated_module.assert_called_with(
            "TextAttributeManager", manager
        )

    def test_get_attributes_to_speak_empty(self, test_context: OrcaTestContext) -> None:
        """Test get_attributes_to_speak returns empty list by default."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].textAttributesToSpeak = []
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        result = manager.get_attributes_to_speak()
        assert result == []

    def test_get_attributes_to_speak_with_values(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_attributes_to_speak returns configured attributes."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        expected = ["bold", "italic", "underline"]
        essential_modules["orca.settings"].textAttributesToSpeak = expected
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        result = manager.get_attributes_to_speak()
        assert result == expected

    def test_set_attributes_to_speak(self, test_context: OrcaTestContext) -> None:
        """Test set_attributes_to_speak updates settings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].textAttributesToSpeak = []
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        new_value = ["bold", "italic"]
        result = manager.set_attributes_to_speak(new_value)

        assert result is True
        assert essential_modules["orca.settings"].textAttributesToSpeak == new_value
        essential_modules["orca.debug"].print_message.assert_called()

    def test_set_attributes_to_speak_same_value(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_attributes_to_speak returns early when value unchanged."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        existing = ["bold", "italic"]
        essential_modules["orca.settings"].textAttributesToSpeak = existing
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        essential_modules["orca.debug"].print_message.reset_mock()

        result = manager.set_attributes_to_speak(existing)
        assert result is True
        # Debug message for the setting change should NOT be called
        # (only the init message was called before reset)
        calls = essential_modules["orca.debug"].print_message.call_args_list
        setting_calls = [c for c in calls if "Setting attributes to speak" in str(c)]
        assert len(setting_calls) == 0

    def test_get_attributes_to_braille_empty(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_attributes_to_braille returns empty list by default."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].textAttributesToBraille = []
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        result = manager.get_attributes_to_braille()
        assert result == []

    def test_get_attributes_to_braille_with_values(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_attributes_to_braille returns configured attributes."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        expected = ["bold", "strikethrough"]
        essential_modules["orca.settings"].textAttributesToBraille = expected
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        result = manager.get_attributes_to_braille()
        assert result == expected

    def test_set_attributes_to_braille(self, test_context: OrcaTestContext) -> None:
        """Test set_attributes_to_braille updates settings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].textAttributesToBraille = []
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        new_value = ["bold", "underline"]
        result = manager.set_attributes_to_braille(new_value)

        assert result is True
        assert essential_modules["orca.settings"].textAttributesToBraille == new_value
        essential_modules["orca.debug"].print_message.assert_called()

    def test_set_attributes_to_braille_same_value(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_attributes_to_braille returns early when value unchanged."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        existing = ["bold"]
        essential_modules["orca.settings"].textAttributesToBraille = existing
        from orca.text_attribute_manager import TextAttributeManager

        manager = TextAttributeManager()
        essential_modules["orca.debug"].print_message.reset_mock()

        result = manager.set_attributes_to_braille(existing)
        assert result is True
        # Debug message for the setting change should NOT be called
        calls = essential_modules["orca.debug"].print_message.call_args_list
        setting_calls = [c for c in calls if "Setting attributes to braille" in str(c)]
        assert len(setting_calls) == 0
