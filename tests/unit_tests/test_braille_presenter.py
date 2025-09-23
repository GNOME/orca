# Unit tests for braille_presenter.py methods.
#
# Copyright 2025 Igalia, S.L.
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
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods

"""Unit tests for braille_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestBraillePresenter:
    """Test BraillePresenter methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for braille_presenter dependencies."""

        additional_modules = ["orca.braille", "orca.orca_platform"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        braille_mock = essential_modules["orca.braille"]
        braille_mock.get_table_files.return_value = [
            "en-us-g1.ctb",
            "en-us-g2.ctb",
            "en-us-comp8.ctb",
            "fr-bfu-g2.ctb",
            "de-g2.ctb"
        ]

        platform_mock = essential_modules["orca.orca_platform"]
        platform_mock.tablesdir = "/usr/share/liblouis/tables"

        # Mock the settings constants to avoid enum issues
        settings_mock = essential_modules["orca.settings"]
        settings_mock.BRAILLE_UNDERLINE_NONE = 0x00
        settings_mock.BRAILLE_UNDERLINE_7 = 0x40
        settings_mock.BRAILLE_UNDERLINE_8 = 0x80
        settings_mock.BRAILLE_UNDERLINE_BOTH = 0xc0
        settings_mock.VERBOSITY_LEVEL_BRIEF = 0
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1
        settings_mock.BRAILLE_ROLENAME_STYLE_SHORT = 0
        settings_mock.BRAILLE_ROLENAME_STYLE_LONG = 1

        return essential_modules

    def test_get_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test getting braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = True
        assert presenter.get_braille_is_enabled() is True
        manager_mock.get_setting.assert_called_with("enableBraille")

        manager_mock.get_setting.return_value = False
        assert presenter.get_braille_is_enabled() is False

    def test_set_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test setting braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_braille_is_enabled(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableBraille", True)

        result = presenter.set_braille_is_enabled(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableBraille", False)

    def test_get_contraction_table(self, test_context: OrcaTestContext):
        """Test getting contraction table."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = "/usr/share/liblouis/tables/en-us-g2.ctb"
        assert presenter.get_contraction_table() == "en-us-g2"

        manager_mock.get_setting.return_value = ""
        assert presenter.get_contraction_table() == ""

        manager_mock.get_setting.return_value = None
        assert presenter.get_contraction_table() == ""

    def test_get_available_contraction_tables(self, test_context: OrcaTestContext):
        """Test getting available contraction tables."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        tables = presenter.get_available_contraction_tables()
        expected = ["en-us-g1", "en-us-g2", "en-us-comp8", "fr-bfu-g2", "de-g2"]
        assert tables == expected

    def test_set_contraction_table_valid(self, test_context: OrcaTestContext):
        """Test setting valid contraction table."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_contraction_table("en-us-g2")
        assert result is True
        manager_mock.set_setting.assert_called_with(
            "brailleContractionTable", "/usr/share/liblouis/tables/en-us-g2.ctb"
        )

        result = presenter.set_contraction_table("en-us-g1.ctb")
        assert result is True
        manager_mock.set_setting.assert_called_with(
            "brailleContractionTable", "/usr/share/liblouis/tables/en-us-g1.ctb"
        )

    def test_set_contraction_table_invalid(self, test_context: OrcaTestContext):
        """Test setting invalid contraction table."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_contraction_table("nonexistent")
        assert result is False

        result = presenter.set_contraction_table("nonexistent.ctb")
        assert result is False

    def test_set_contraction_table_empty_string(self, test_context: OrcaTestContext):
        """Test setting empty string contraction table returns false and doesn't update setting."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_contraction_table("")
        assert result is False
        manager_mock.set_setting.assert_not_called()

    def test_get_indicator_styles(self, test_context: OrcaTestContext):
        """Test getting indicator styles."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = 0xc0
        assert presenter.get_selector_indicator() == "dots78"

        manager_mock.get_setting.return_value = 0x40
        assert presenter.get_link_indicator() == "dot7"

        manager_mock.get_setting.return_value = 0x00
        assert presenter.get_text_attributes_indicator() == "none"

    def test_set_indicator_styles(self, test_context: OrcaTestContext):
        """Test setting indicator styles."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_selector_indicator("dots78")
        assert result is True
        manager_mock.set_setting.assert_called_with("brailleSelectorIndicator", 0xc0)

        result = presenter.set_link_indicator("dot8")
        assert result is True
        manager_mock.set_setting.assert_called_with("brailleLinkIndicator", 0x80)

        result = presenter.set_text_attributes_indicator("none")
        assert result is True
        manager_mock.set_setting.assert_called_with("textAttributesBrailleIndicator", 0x00)

        result = presenter.set_selector_indicator("invalid")
        assert result is False

        result = presenter.set_link_indicator("invalid")
        assert result is False

        result = presenter.set_text_attributes_indicator("invalid")
        assert result is False

    def test_end_of_line_indicator(self, test_context: OrcaTestContext):
        """Test end of line indicator settings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = False
        assert presenter.get_end_of_line_indicator_is_enabled() is True

        manager_mock.get_setting.return_value = True
        assert presenter.get_end_of_line_indicator_is_enabled() is False

        result = presenter.set_end_of_line_indicator_is_enabled(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("disableBrailleEOL", False)

        result = presenter.set_end_of_line_indicator_is_enabled(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("disableBrailleEOL", True)

    def test_use_braille(self, test_context: OrcaTestContext):
        """Test use_braille method."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.side_effect = lambda setting: {
            "enableBraille": True,
            "enableBrailleMonitor": False
        }.get(setting, False)
        assert presenter.use_braille() is True

        manager_mock.get_setting.side_effect = lambda setting: {
            "enableBraille": False,
            "enableBrailleMonitor": True
        }.get(setting, False)
        assert presenter.use_braille() is True

        manager_mock.get_setting.side_effect = lambda setting: False
        assert presenter.use_braille() is False

    def test_use_verbose_braille(self, test_context: OrcaTestContext):
        """Test use_verbose_braille method."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value
        settings_mock = essential_modules["orca.settings"]
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1

        manager_mock.get_setting.return_value = 1
        assert presenter.use_verbose_braille() is True

        manager_mock.get_setting.return_value = 0
        assert presenter.use_verbose_braille() is False

    def test_get_verbosity_level(self, test_context: OrcaTestContext):
        """Test getting verbosity level."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = 0
        assert presenter.get_verbosity_level() == "brief"

        manager_mock.get_setting.return_value = 1
        assert presenter.get_verbosity_level() == "verbose"

    def test_set_verbosity_level(self, test_context: OrcaTestContext):
        """Test setting verbosity level."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_verbosity_level("brief")
        assert result is True
        manager_mock.set_setting.assert_called_with("brailleVerbosityLevel", 0)

        result = presenter.set_verbosity_level("verbose")
        assert result is True
        manager_mock.set_setting.assert_called_with("brailleVerbosityLevel", 1)

        result = presenter.set_verbosity_level("invalid")
        assert result is False

    def test_use_full_rolenames(self, test_context: OrcaTestContext):
        """Test use_full_rolenames method."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value
        settings_mock = essential_modules["orca.settings"]
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1

        manager_mock.get_setting.return_value = 1
        assert presenter.use_full_rolenames() is True

        manager_mock.get_setting.return_value = 0
        assert presenter.use_full_rolenames() is False

    def test_get_rolename_style(self, test_context: OrcaTestContext):
        """Test getting rolename style."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = 0
        assert presenter.get_rolename_style() == "short"

        manager_mock.get_setting.return_value = 1
        assert presenter.get_rolename_style() == "long"

    def test_set_rolename_style(self, test_context: OrcaTestContext):
        """Test setting rolename style."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_rolename_style("short")
        assert result is True
        manager_mock.set_setting.assert_called_with("brailleRolenameStyle", 0)

        result = presenter.set_rolename_style("long")
        assert result is True
        manager_mock.set_setting.assert_called_with("brailleRolenameStyle", 1)

        result = presenter.set_rolename_style("invalid")
        assert result is False

    def test_get_display_ancestors(self, test_context: OrcaTestContext):
        """Test getting display ancestors setting."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = True
        assert presenter.get_display_ancestors() is True
        manager_mock.get_setting.assert_called_with("enableBrailleContext")

        manager_mock.get_setting.return_value = False
        assert presenter.get_display_ancestors() is False

    def test_set_display_ancestors(self, test_context: OrcaTestContext):
        """Test setting display ancestors."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_display_ancestors(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableBrailleContext", True)

        result = presenter.set_display_ancestors(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableBrailleContext", False)

    def test_get_contracted_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test getting contracted braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = True
        assert presenter.get_contracted_braille_is_enabled() is True
        manager_mock.get_setting.assert_called_with("enableContractedBraille")

        manager_mock.get_setting.return_value = False
        assert presenter.get_contracted_braille_is_enabled() is False

    def test_set_contracted_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test setting contracted braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_contracted_braille_is_enabled(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableContractedBraille", True)

        result = presenter.set_contracted_braille_is_enabled(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableContractedBraille", False)

    def test_get_word_wrap_is_enabled(self, test_context: OrcaTestContext):
        """Test getting word wrap enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = True
        assert presenter.get_word_wrap_is_enabled() is True
        manager_mock.get_setting.assert_called_with("enableBrailleWordWrap")

        manager_mock.get_setting.return_value = False
        assert presenter.get_word_wrap_is_enabled() is False

    def test_set_word_wrap_is_enabled(self, test_context: OrcaTestContext):
        """Test setting word wrap enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_word_wrap_is_enabled(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableBrailleWordWrap", True)

        result = presenter.set_word_wrap_is_enabled(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableBrailleWordWrap", False)

    def test_get_flash_messages_are_enabled(self, test_context: OrcaTestContext):
        """Test getting flash messages enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = True
        assert presenter.get_flash_messages_are_enabled() is True
        manager_mock.get_setting.assert_called_with("enableFlashMessages")

        manager_mock.get_setting.return_value = False
        assert presenter.get_flash_messages_are_enabled() is False

    def test_set_flash_messages_are_enabled(self, test_context: OrcaTestContext):
        """Test setting flash messages enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_flash_messages_are_enabled(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableFlashMessages", True)

        result = presenter.set_flash_messages_are_enabled(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("enableFlashMessages", False)

    def test_get_flashtime_from_settings(self, test_context: OrcaTestContext):
        """Test getting flashtime from settings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.side_effect = lambda setting: {
            "flashIsPersistent": True,
            "brailleFlashTime": 5000
        }.get(setting, False)
        assert presenter.get_flashtime_from_settings() == -1

        manager_mock.get_setting.side_effect = lambda setting: {
            "flashIsPersistent": False,
            "brailleFlashTime": 3000
        }.get(setting, False)
        assert presenter.get_flashtime_from_settings() == 3000

    def test_get_flash_message_duration(self, test_context: OrcaTestContext):
        """Test getting flash message duration."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = 2500
        assert presenter.get_flash_message_duration() == 2500
        manager_mock.get_setting.assert_called_with("brailleFlashTime")

    def test_set_flash_message_duration(self, test_context: OrcaTestContext):
        """Test setting flash message duration."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_flash_message_duration(4000)
        assert result is True
        manager_mock.set_setting.assert_called_with("brailleFlashTime", 4000)

    def test_get_flash_messages_are_persistent(self, test_context: OrcaTestContext):
        """Test getting flash messages persistent status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = True
        assert presenter.get_flash_messages_are_persistent() is True
        manager_mock.get_setting.assert_called_with("flashIsPersistent")

        manager_mock.get_setting.return_value = False
        assert presenter.get_flash_messages_are_persistent() is False

    def test_set_flash_messages_are_persistent(self, test_context: OrcaTestContext):
        """Test setting flash messages persistent status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_flash_messages_are_persistent(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("flashIsPersistent", True)

        result = presenter.set_flash_messages_are_persistent(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("flashIsPersistent", False)

    def test_get_flash_messages_are_detailed(self, test_context: OrcaTestContext):
        """Test getting flash messages detailed status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        manager_mock.get_setting.return_value = True
        assert presenter.get_flash_messages_are_detailed() is True
        manager_mock.get_setting.assert_called_with("flashIsDetailed")

        manager_mock.get_setting.return_value = False
        assert presenter.get_flash_messages_are_detailed() is False

    def test_set_flash_messages_are_detailed(self, test_context: OrcaTestContext):
        """Test setting flash messages detailed status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        manager_mock = essential_modules["orca.settings_manager"].get_manager.return_value

        result = presenter.set_flash_messages_are_detailed(True)
        assert result is True
        manager_mock.set_setting.assert_called_with("flashIsDetailed", True)

        result = presenter.set_flash_messages_are_detailed(False)
        assert result is True
        manager_mock.set_setting.assert_called_with("flashIsDetailed", False)
