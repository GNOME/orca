# Unit tests for braille_presenter.py methods.
#
# Copyright 2025-2026 Igalia, S.L.
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
# pylint: disable=too-many-lines

"""Unit tests for braille_presenter.py methods."""

from __future__ import annotations

import unittest.mock

from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestBraillePresenter:
    """Test BraillePresenter methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for braille_presenter dependencies."""

        additional_modules = ["orca.braille", "orca.braille_monitor", "orca.orca_platform"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        platform_mock = essential_modules["orca.orca_platform"]
        platform_mock.tablesdir = "/usr/share/liblouis/tables"

        # Mock the settings constants to avoid enum issues
        settings_mock = essential_modules["orca.settings"]
        settings_mock.BRAILLE_UNDERLINE_NONE = 0x00
        settings_mock.BRAILLE_UNDERLINE_7 = 0x40
        settings_mock.BRAILLE_UNDERLINE_8 = 0x80
        settings_mock.BRAILLE_UNDERLINE_BOTH = 0xC0
        settings_mock.VERBOSITY_LEVEL_BRIEF = 0
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1

        test_context.patch(
            "orca.braille_presenter.BraillePresenter._get_table_files",
            return_value=[
                "en-us-g1.ctb",
                "en-us-g2.ctb",
                "en-us-comp8.ctb",
                "fr-bfu-g2.ctb",
                "de-g2.ctb",
            ],
        )

        return essential_modules

    def test_get_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test getting braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.enableBraille = True
        assert presenter.get_braille_is_enabled() is True

        settings_mock.enableBraille = False
        assert presenter.get_braille_is_enabled() is False

    def test_set_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test setting braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_braille_is_enabled(True)
        assert result is True
        assert settings_mock.enableBraille

        result = presenter.set_braille_is_enabled(False)
        assert result is True
        assert not settings_mock.enableBraille

    def test_get_contraction_table(self, test_context: OrcaTestContext):
        """Test getting contraction table."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleContractionTable = "/usr/share/liblouis/tables/en-us-g2.ctb"
        assert presenter.get_contraction_table() == "en-us-g2"

        settings_mock.brailleContractionTable = ""
        assert presenter.get_contraction_table() == ""

        settings_mock.brailleContractionTable = None
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
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_contraction_table("en-us-g2")
        assert result is True
        assert settings_mock.brailleContractionTable == "/usr/share/liblouis/tables/en-us-g2.ctb"

        result = presenter.set_contraction_table("en-us-g1.ctb")
        assert result is True
        assert settings_mock.brailleContractionTable == "/usr/share/liblouis/tables/en-us-g1.ctb"

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
        """Test setting empty contraction table returns False."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_contraction_table("")
        assert result is False

    def test_get_indicator_styles(self, test_context: OrcaTestContext):
        """Test getting indicator styles."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleSelectorIndicator = 0xC0
        assert presenter.get_selector_indicator() == "dots78"

        settings_mock.brailleLinkIndicator = 0x40
        assert presenter.get_link_indicator() == "dot7"

        settings_mock.textAttributesBrailleIndicator = 0x00
        assert presenter.get_text_attributes_indicator() == "none"

    def test_set_indicator_styles(self, test_context: OrcaTestContext):
        """Test setting indicator styles."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_selector_indicator("dots78")
        assert result is True
        assert settings_mock.brailleSelectorIndicator == 0xC0

        result = presenter.set_link_indicator("dot8")
        assert result is True
        assert settings_mock.brailleLinkIndicator == 0x80

        result = presenter.set_text_attributes_indicator("none")
        assert result is True
        assert settings_mock.textAttributesBrailleIndicator == 0x00

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
        settings_mock = essential_modules["orca.settings"]

        settings_mock.disableBrailleEOL = False
        assert presenter.get_end_of_line_indicator_is_enabled() is True

        settings_mock.disableBrailleEOL = True
        assert presenter.get_end_of_line_indicator_is_enabled() is False

        result = presenter.set_end_of_line_indicator_is_enabled(True)
        assert result is True
        assert not settings_mock.disableBrailleEOL

        result = presenter.set_end_of_line_indicator_is_enabled(False)
        assert result is True
        assert settings_mock.disableBrailleEOL

    def test_use_braille(self, test_context: OrcaTestContext):
        """Test use_braille method."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.enableBraille = True
        presenter.set_monitor_is_enabled(False)
        assert presenter.use_braille() is True

        settings_mock.enableBraille = False
        presenter.set_monitor_is_enabled(True)
        assert presenter.use_braille() is True

        settings_mock.enableBraille = False
        presenter.set_monitor_is_enabled(False)
        assert presenter.use_braille() is False

    def test_use_verbose_braille(self, test_context: OrcaTestContext):
        """Test use_verbose_braille method."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1

        settings_mock.brailleVerbosityLevel = 1
        assert presenter.use_verbose_braille() is True

        settings_mock.brailleVerbosityLevel = 0
        assert presenter.use_verbose_braille() is False

    def test_get_verbosity_level(self, test_context: OrcaTestContext):
        """Test getting verbosity level."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleVerbosityLevel = 0
        assert presenter.get_verbosity_level() == "brief"

        settings_mock.brailleVerbosityLevel = 1
        assert presenter.get_verbosity_level() == "verbose"

    def test_set_verbosity_level(self, test_context: OrcaTestContext):
        """Test setting verbosity level."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_verbosity_level("brief")
        assert result is True
        assert settings_mock.brailleVerbosityLevel == 0

        result = presenter.set_verbosity_level("verbose")
        assert result is True
        assert settings_mock.brailleVerbosityLevel == 1

        result = presenter.set_verbosity_level("invalid")
        assert result is False

    def test_use_full_rolenames(self, test_context: OrcaTestContext):
        """Test use_full_rolenames method."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1

        settings_mock.brailleRolenameStyle = 1
        assert presenter.use_full_rolenames() is True

        settings_mock.brailleRolenameStyle = 0
        assert presenter.use_full_rolenames() is False

    def test_get_rolename_style(self, test_context: OrcaTestContext):
        """Test getting rolename style."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleRolenameStyle = 0
        assert presenter.get_rolename_style() == "brief"

        settings_mock.brailleRolenameStyle = 1
        assert presenter.get_rolename_style() == "verbose"

    def test_set_rolename_style(self, test_context: OrcaTestContext):
        """Test setting rolename style."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_rolename_style("brief")
        assert result is True
        assert settings_mock.brailleRolenameStyle == 0

        result = presenter.set_rolename_style("verbose")
        assert result is True
        assert settings_mock.brailleRolenameStyle == 1

        result = presenter.set_rolename_style("invalid")
        assert result is False

    def test_get_display_ancestors(self, test_context: OrcaTestContext):
        """Test getting display ancestors setting."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.enableBrailleContext = True
        assert presenter.get_display_ancestors() is True

        settings_mock.enableBrailleContext = False
        assert presenter.get_display_ancestors() is False

    def test_set_display_ancestors(self, test_context: OrcaTestContext):
        """Test setting display ancestors."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_display_ancestors(True)
        assert result is True
        assert settings_mock.enableBrailleContext

        result = presenter.set_display_ancestors(False)
        assert result is True
        assert not settings_mock.enableBrailleContext

    def test_get_contracted_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test getting contracted braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.enableContractedBraille = True
        assert presenter.get_contracted_braille_is_enabled() is True

        settings_mock.enableContractedBraille = False
        assert presenter.get_contracted_braille_is_enabled() is False

    def test_set_contracted_braille_is_enabled(self, test_context: OrcaTestContext):
        """Test setting contracted braille enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_contracted_braille_is_enabled(True)
        assert result is True
        assert settings_mock.enableContractedBraille

        result = presenter.set_contracted_braille_is_enabled(False)
        assert result is True
        assert not settings_mock.enableContractedBraille

    def test_get_computer_braille_at_cursor_is_enabled(self, test_context: OrcaTestContext):
        """Test getting computer braille at cursor enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.enableComputerBrailleAtCursor = True
        assert presenter.get_computer_braille_at_cursor_is_enabled() is True

        settings_mock.enableComputerBrailleAtCursor = False
        assert presenter.get_computer_braille_at_cursor_is_enabled() is False

    def test_set_computer_braille_at_cursor_is_enabled(self, test_context: OrcaTestContext):
        """Test setting computer braille at cursor enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_computer_braille_at_cursor_is_enabled(True)
        assert result is True
        assert settings_mock.enableComputerBrailleAtCursor

        result = presenter.set_computer_braille_at_cursor_is_enabled(False)
        assert result is True
        assert not settings_mock.enableComputerBrailleAtCursor

    def test_get_word_wrap_is_enabled(self, test_context: OrcaTestContext):
        """Test getting word wrap enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.enableBrailleWordWrap = True
        assert presenter.get_word_wrap_is_enabled() is True

        settings_mock.enableBrailleWordWrap = False
        assert presenter.get_word_wrap_is_enabled() is False

    def test_set_word_wrap_is_enabled(self, test_context: OrcaTestContext):
        """Test setting word wrap enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_word_wrap_is_enabled(True)
        assert result is True
        assert settings_mock.enableBrailleWordWrap

        result = presenter.set_word_wrap_is_enabled(False)
        assert result is True
        assert not settings_mock.enableBrailleWordWrap

    def test_get_flash_messages_are_enabled(self, test_context: OrcaTestContext):
        """Test getting flash messages enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.enableFlashMessages = True
        assert presenter.get_flash_messages_are_enabled() is True

        settings_mock.enableFlashMessages = False
        assert presenter.get_flash_messages_are_enabled() is False

    def test_set_flash_messages_are_enabled(self, test_context: OrcaTestContext):
        """Test setting flash messages enabled status."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_flash_messages_are_enabled(True)
        assert result is True
        assert settings_mock.enableFlashMessages

        result = presenter.set_flash_messages_are_enabled(False)
        assert result is True
        assert not settings_mock.enableFlashMessages

    def test_get_flashtime_from_settings(self, test_context: OrcaTestContext):
        """Test getting flashtime from settings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.flashIsPersistent = True
        settings_mock.brailleFlashTime = 5000
        assert presenter.get_flashtime_from_settings() == -1

        settings_mock.flashIsPersistent = False
        settings_mock.brailleFlashTime = 3000
        assert presenter.get_flashtime_from_settings() == 3000

    def test_get_flash_message_duration(self, test_context: OrcaTestContext):
        """Test getting flash message duration."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleFlashTime = 2500
        assert presenter.get_flash_message_duration() == 2500

    def test_set_flash_message_duration(self, test_context: OrcaTestContext):
        """Test setting flash message duration."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_flash_message_duration(4000)
        assert result is True
        assert settings_mock.brailleFlashTime == 4000

    def test_get_flash_messages_are_persistent(self, test_context: OrcaTestContext):
        """Test getting flash messages persistent status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.flashIsPersistent = True
        assert presenter.get_flash_messages_are_persistent() is True

        settings_mock.flashIsPersistent = False
        assert presenter.get_flash_messages_are_persistent() is False

    def test_set_flash_messages_are_persistent(self, test_context: OrcaTestContext):
        """Test setting flash messages persistent status."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_flash_messages_are_persistent(True)
        assert result is True
        assert settings_mock.flashIsPersistent

        result = presenter.set_flash_messages_are_persistent(False)
        assert result is True
        assert not settings_mock.flashIsPersistent

    def test_get_flash_messages_are_detailed(self, test_context: OrcaTestContext):
        """Test getting flash messages detailed status."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.flashIsDetailed = True
        assert presenter.get_flash_messages_are_detailed() is True

        settings_mock.flashIsDetailed = False
        assert presenter.get_flash_messages_are_detailed() is False

    def test_set_flash_messages_are_detailed(self, test_context: OrcaTestContext):
        """Test setting flash messages detailed status."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_flash_messages_are_detailed(True)
        assert result is True
        assert settings_mock.flashIsDetailed

        result = presenter.set_flash_messages_are_detailed(False)
        assert result is True
        assert not settings_mock.flashIsDetailed

    def test_get_verbosity_is_detailed(self, test_context: OrcaTestContext):
        """Test _get_verbosity_is_detailed returns correct boolean."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleVerbosityLevel = settings_mock.VERBOSITY_LEVEL_VERBOSE
        assert presenter._get_verbosity_is_detailed() is True

        settings_mock.brailleVerbosityLevel = settings_mock.VERBOSITY_LEVEL_BRIEF
        assert presenter._get_verbosity_is_detailed() is False

    def test_set_verbosity_is_detailed(self, test_context: OrcaTestContext):
        """Test _set_verbosity_is_detailed sets verbosity level from boolean."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter._set_verbosity_is_detailed(True)
        assert result is True
        assert settings_mock.brailleVerbosityLevel == settings_mock.VERBOSITY_LEVEL_VERBOSE

        result = presenter._set_verbosity_is_detailed(False)
        assert result is True
        assert settings_mock.brailleVerbosityLevel == settings_mock.VERBOSITY_LEVEL_BRIEF

    def test_get_disable_eol(self, test_context: OrcaTestContext):
        """Test _get_disable_eol returns the disableBrailleEOL setting."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.disableBrailleEOL = True
        assert presenter._get_disable_eol() is True

        settings_mock.disableBrailleEOL = False
        assert presenter._get_disable_eol() is False

    def test_set_disable_eol(self, test_context: OrcaTestContext):
        """Test _set_disable_eol sets the disableBrailleEOL setting."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter._set_disable_eol(True)
        assert result is True
        assert settings_mock.disableBrailleEOL is True

        result = presenter._set_disable_eol(False)
        assert result is True
        assert settings_mock.disableBrailleEOL is False

    def test_get_use_abbreviated_rolenames(self, test_context: OrcaTestContext):
        """Test _get_use_abbreviated_rolenames returns True when brief style."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleRolenameStyle = settings_mock.VERBOSITY_LEVEL_BRIEF
        assert presenter._get_use_abbreviated_rolenames() is True

        settings_mock.brailleRolenameStyle = settings_mock.VERBOSITY_LEVEL_VERBOSE
        assert presenter._get_use_abbreviated_rolenames() is False

    def test_set_use_abbreviated_rolenames(self, test_context: OrcaTestContext):
        """Test _set_use_abbreviated_rolenames sets rolename style from boolean."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter._set_use_abbreviated_rolenames(True)
        assert result is True
        assert settings_mock.brailleRolenameStyle == settings_mock.VERBOSITY_LEVEL_BRIEF

        result = presenter._set_use_abbreviated_rolenames(False)
        assert result is True
        assert settings_mock.brailleRolenameStyle == settings_mock.VERBOSITY_LEVEL_VERBOSE

    def test_get_flash_duration_seconds(self, test_context: OrcaTestContext):
        """Test _get_flash_duration_seconds converts milliseconds to seconds."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.brailleFlashTime = 5000
        assert presenter._get_flash_duration_seconds() == 5

        settings_mock.brailleFlashTime = 2500
        assert presenter._get_flash_duration_seconds() == 2  # Integer division

        settings_mock.brailleFlashTime = 1000
        assert presenter._get_flash_duration_seconds() == 1

    def test_set_flash_duration_seconds(self, test_context: OrcaTestContext):
        """Test _set_flash_duration_seconds converts seconds to milliseconds."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        presenter._set_flash_duration_seconds(5)
        assert settings_mock.brailleFlashTime == 5000

        presenter._set_flash_duration_seconds(1)
        assert settings_mock.brailleFlashTime == 1000

        presenter._set_flash_duration_seconds(10)
        assert settings_mock.brailleFlashTime == 10000

    def test_get_present_mnemonics(self, test_context: OrcaTestContext):
        """Test getting present mnemonics setting."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock = essential_modules["orca.settings"]

        settings_mock.displayObjectMnemonic = True
        assert presenter.get_present_mnemonics() is True

        settings_mock.displayObjectMnemonic = False
        assert presenter.get_present_mnemonics() is False

    def test_set_present_mnemonics(self, test_context: OrcaTestContext):
        """Test setting present mnemonics."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_present_mnemonics(True)
        assert result is True
        assert settings_mock.displayObjectMnemonic is True

        result = presenter.set_present_mnemonics(False)
        assert result is True
        assert settings_mock.displayObjectMnemonic is False

    def test_get_set_monitor_is_enabled(self, test_context: OrcaTestContext):
        """Test getting and setting braille monitor enabled status."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_monitor_is_enabled(True)
        assert result is True
        assert presenter.get_monitor_is_enabled() is True

        result = presenter.set_monitor_is_enabled(False)
        assert result is True
        assert presenter.get_monitor_is_enabled() is False

    def test_set_braille_monitor_disabled_destroys_monitor(self, test_context: OrcaTestContext):
        """Test explicitly disabling braille monitor destroys the monitor widget."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        mock_monitor = test_context.Mock()
        presenter._monitor = mock_monitor

        presenter.set_monitor_is_enabled(False)

        mock_monitor.destroy.assert_called_once()
        assert presenter._monitor is None

    def test_init_braille_registers_monitor_callback(self, test_context: OrcaTestContext):
        """Test init_braille registers the monitor callback with braille."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        braille_mock = essential_modules["orca.braille"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        settings_mock.enableBraille = True

        presenter.init_braille()

        braille_mock.set_monitor_callback.assert_called_once_with(presenter.update_monitor)

    def test_update_monitor_creates_when_enabled(self, test_context: OrcaTestContext):
        """Test update_monitor creates monitor on demand when enabled."""

        essential_modules = self._setup_dependencies(test_context)
        braille_monitor_mock = essential_modules["orca.braille_monitor"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(True)
        presenter.set_monitor_cell_count(40)
        mock_monitor = test_context.Mock()
        braille_monitor_mock.BrailleMonitor.return_value = mock_monitor

        presenter.update_monitor(1, "hello", None, 40)

        braille_monitor_mock.BrailleMonitor.assert_called_once_with(
            40,
            on_close=unittest.mock.ANY,
        )
        mock_monitor.show_all.assert_called_once()
        mock_monitor.write_text.assert_called_once_with(1, "hello", None)

    def test_update_monitor_uses_cell_count_setting(self, test_context: OrcaTestContext):
        """Test update_monitor uses the configured cell count instead of display size."""

        essential_modules = self._setup_dependencies(test_context)
        braille_monitor_mock = essential_modules["orca.braille_monitor"]
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(True)
        presenter.set_monitor_cell_count(20)
        mock_monitor = test_context.Mock()
        braille_monitor_mock.BrailleMonitor.return_value = mock_monitor

        presenter.update_monitor(1, "hello", None, 40)

        braille_monitor_mock.BrailleMonitor.assert_called_once_with(
            20,
            on_close=unittest.mock.ANY,
        )

    def test_update_monitor_skips_when_disabled(self, test_context: OrcaTestContext):
        """Test update_monitor skips update when disabled without destroying."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(False)
        mock_monitor = test_context.Mock()
        presenter._monitor = mock_monitor

        presenter.update_monitor(1, "hello", None, 40)

        mock_monitor.write_text.assert_not_called()
        assert presenter._monitor is mock_monitor

    def test_destroy_monitor(self, test_context: OrcaTestContext):
        """Test destroy_monitor destroys existing monitor."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        mock_monitor = test_context.Mock()
        presenter._monitor = mock_monitor

        presenter.destroy_monitor()

        mock_monitor.destroy.assert_called_once()
        assert presenter._monitor is None

    def test_destroy_monitor_no_op_when_none(self, test_context: OrcaTestContext):
        """Test destroy_monitor does nothing when no monitor exists."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        assert presenter._monitor is None

        presenter.destroy_monitor()

        assert presenter._monitor is None

    def test_shutdown_braille_does_not_destroy_monitor(self, test_context: OrcaTestContext):
        """Test shutdown_braille does not destroy the monitor."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        mock_monitor = test_context.Mock()
        presenter._monitor = mock_monitor

        presenter.shutdown_braille()

        mock_monitor.destroy.assert_not_called()
        assert presenter._monitor is mock_monitor
        essential_modules["orca.braille"].shutdown.assert_called_once()

    def test_set_braille_disabled_keeps_monitor(self, test_context: OrcaTestContext):
        """Test disabling braille does not destroy the monitor."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import get_presenter

        presenter = get_presenter()
        mock_monitor = test_context.Mock()
        presenter._monitor = mock_monitor

        presenter.set_braille_is_enabled(False)

        mock_monitor.destroy.assert_not_called()
        assert presenter._monitor is mock_monitor


@pytest.mark.unit
class TestBraillePreferencesGridUI:
    """Test Braille preferences grid UI creation."""

    # pylint: disable-next=too-many-statements
    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for braille_presenter GUI dependencies."""

        additional_modules = ["orca.braille", "orca.braille_monitor", "orca.orca_platform"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        platform_mock = essential_modules["orca.orca_platform"]
        platform_mock.tablesdir = "/usr/share/liblouis/tables"

        settings_mock = essential_modules["orca.settings"]
        settings_mock.BRAILLE_UNDERLINE_NONE = 0x00
        settings_mock.BRAILLE_UNDERLINE_7 = 0x40
        settings_mock.BRAILLE_UNDERLINE_8 = 0x80
        settings_mock.BRAILLE_UNDERLINE_BOTH = 0xC0
        settings_mock.VERBOSITY_LEVEL_BRIEF = 0
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1
        settings_mock.PROGRESS_BAR_ALL = 0
        settings_mock.PROGRESS_BAR_APPLICATION = 1
        settings_mock.PROGRESS_BAR_WINDOW = 2
        settings_mock.brailleVerbosityLevel = 0
        settings_mock.brailleRolenameStyle = 0
        settings_mock.brailleShowContext = True
        settings_mock.enableContractedBraille = False
        settings_mock.enableComputerBrailleAtCursor = True
        settings_mock.disableBrailleEOL = False
        settings_mock.enableBrailleWordWrap = False
        settings_mock.brailleContractionTable = ""
        settings_mock.brailleLinkIndicator = 0x00
        settings_mock.brailleSelectorIndicator = 0x00
        settings_mock.textAttributesBrailleIndicator = 0x00

        test_context.patch(
            "orca.braille_presenter.BraillePresenter._get_table_files",
            return_value=[
                "en-us-g1.ctb",
                "en-us-g2.ctb",
            ],
        )
        settings_mock.enableFlashMessages = True
        settings_mock.flashIsPersistent = False
        settings_mock.flashVerbosityLevel = 1
        settings_mock.brailleFlashTime = 5000
        settings_mock.brailleProgressBarUpdates = True
        settings_mock.progressBarBrailleInterval = 10
        settings_mock.progressBarBrailleVerbosity = 0
        settings_mock.displayObjectMnemonic = True
        settings_mock.enableBrailleContext = True
        settings_mock.brailleMonitorCellCount = 32
        settings_mock.brailleMonitorShowDots = False
        settings_mock.brailleMonitorForeground = "#000000"
        settings_mock.brailleMonitorBackground = "#ffffff"

        guilabels_mock = essential_modules["orca.guilabels"]
        guilabels_mock.OBJECT_PRESENTATION_IS_DETAILED = "Detailed"
        guilabels_mock.BRAILLE_SHOW_CONTEXT = "Show context"
        guilabels_mock.BRAILLE_ABBREVIATED_ROLE_NAMES = "Abbreviated role names"
        guilabels_mock.PRESENT_OBJECT_MNEMONICS = "Present mnemonics"
        guilabels_mock.VERBOSITY = "Verbosity"
        guilabels_mock.BRAILLE_ENABLE_CONTRACTED_BRAILLE = "Enable contracted braille"
        guilabels_mock.BRAILLE_COMPUTER_BRAILLE_AT_CURSOR = "Expand word at cursor"
        guilabels_mock.BRAILLE_DISABLE_END_OF_LINE_SYMBOL = "Disable end of line symbol"
        guilabels_mock.BRAILLE_ENABLE_WORD_WRAP = "Enable word wrap"
        guilabels_mock.BRAILLE_CONTRACTION_TABLE = "Contraction table"
        guilabels_mock.BRAILLE_HYPERLINK_INDICATOR = "Hyperlink indicator"
        guilabels_mock.BRAILLE_DOT_NONE = "None"
        guilabels_mock.BRAILLE_DOT_7 = "Dot 7"
        guilabels_mock.BRAILLE_DOT_8 = "Dot 8"
        guilabels_mock.BRAILLE_DOT_7_8 = "Dots 7 and 8"
        guilabels_mock.BRAILLE_INDICATORS = "Indicators"
        guilabels_mock.BRAILLE_SELECTION_INDICATOR = "Selection indicator"
        guilabels_mock.BRAILLE_TEXT_ATTRIBUTES_INDICATOR = "Text attributes indicator"
        guilabels_mock.BRAILLE_DISPLAY_SETTINGS = "Display Settings"
        guilabels_mock.BRAILLE_MESSAGES_ARE_PERSISTENT = "Messages are persistent"
        guilabels_mock.BRAILLE_ENABLE_FLASH_MESSAGES = "Enable flash messages"
        guilabels_mock.BRAILLE_MESSAGES_ARE_DETAILED = "Messages are detailed"
        guilabels_mock.BRAILLE_DURATION_SECS = "Duration (secs)"
        guilabels_mock.BRAILLE_FLASH_MESSAGES = "Flash Messages"
        guilabels_mock.GENERAL_BRAILLE_UPDATES = "Braille updates"
        guilabels_mock.GENERAL_FREQUENCY_SECS = "Frequency (secs)"
        guilabels_mock.GENERAL_APPLIES_TO = "Applies to"
        guilabels_mock.PROGRESS_BAR_ALL = "All"
        guilabels_mock.PROGRESS_BAR_APPLICATION = "Application"
        guilabels_mock.PROGRESS_BAR_WINDOW = "Window"
        guilabels_mock.PROGRESS_BARS = "Progress Bars"
        guilabels_mock.BRAILLE = "Braille"
        guilabels_mock.BRAILLE_MONITOR = "On-screen braille"
        guilabels_mock.ON_SCREEN_DISPLAY = "On-Screen Display"
        guilabels_mock.BRAILLE_MONITOR_CELL_COUNT = "Cell count"
        guilabels_mock.BRAILLE_MONITOR_SHOW_DOTS = "Show braille dot patterns"
        guilabels_mock.BRAILLE_MONITOR_FOREGROUND = "Text color"
        guilabels_mock.BRAILLE_MONITOR_BACKGROUND = "Background color"
        guilabels_mock.BRAILLE_MONITOR_INFO = "On-screen braille info"

        return essential_modules

    def test_braille_verbosity_grid_creates_widgets(self, test_context: OrcaTestContext) -> None:
        """Test BrailleVerbosityPreferencesGrid creates correct widgets."""

        from gi.repository import Gtk

        self._setup_dependencies(test_context)
        from orca.braille_presenter import (
            BraillePresenter,
            BrailleVerbosityPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleVerbosityPreferencesGrid(presenter)

        assert isinstance(grid, Gtk.Grid)
        assert len(grid._widgets) == 4

    def test_braille_display_settings_grid_creates_widgets(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test BrailleDisplaySettingsPreferencesGrid creates correct widgets."""

        from gi.repository import Gtk

        self._setup_dependencies(test_context)
        from orca.braille_presenter import (
            BraillePresenter,
            BrailleDisplaySettingsPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleDisplaySettingsPreferencesGrid(presenter)

        assert isinstance(grid, Gtk.Grid)
        assert len(grid._widgets) == 8

    def test_braille_display_settings_grid_has_contracted_control(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test BrailleDisplaySettingsPreferencesGrid has contracted control."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import (
            BraillePresenter,
            BrailleDisplaySettingsPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleDisplaySettingsPreferencesGrid(presenter)

        contracted_switch = grid.get_widget(2)
        assert contracted_switch is not None

        computer_braille_at_cursor_switch = grid.get_widget(3)
        assert computer_braille_at_cursor_switch is not None

        contraction_table_combo = grid.get_widget(4)
        assert contraction_table_combo is not None

    def test_braille_flash_messages_grid_creates_widgets(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test BrailleFlashMessagesPreferencesGrid creates correct widgets."""

        from gi.repository import Gtk

        self._setup_dependencies(test_context)
        from orca.braille_presenter import (
            BraillePresenter,
            BrailleFlashMessagesPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleFlashMessagesPreferencesGrid(presenter)

        assert isinstance(grid, Gtk.Grid)
        assert len(grid._widgets) == 4

    def test_braille_flash_messages_grid_has_persistent_control(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test BrailleFlashMessagesPreferencesGrid has persistent control."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import (
            BraillePresenter,
            BrailleFlashMessagesPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleFlashMessagesPreferencesGrid(presenter)

        persistent_switch = grid.get_widget(2)
        assert persistent_switch is not None

        duration_spinbutton = grid.get_widget(3)
        assert duration_spinbutton is not None

    def test_braille_progress_bars_grid_creates_widgets(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test BrailleProgressBarsPreferencesGrid creates correct widgets."""

        from gi.repository import Gtk

        self._setup_dependencies(test_context)
        from orca.braille_presenter import (
            BraillePresenter,
            BrailleProgressBarsPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleProgressBarsPreferencesGrid(presenter)

        assert isinstance(grid, Gtk.Grid)
        assert len(grid._widgets) == 3

    def test_braille_preferences_grid_creates_multi_page_stack(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test BraillePreferencesGrid creates multi-page stack."""

        from gi.repository import Gtk

        self._setup_dependencies(test_context)
        from orca.braille_presenter import BraillePresenter, BraillePreferencesGrid

        presenter = BraillePresenter()
        grid = BraillePreferencesGrid(presenter)

        assert isinstance(grid, Gtk.Grid)
        assert grid._verbosity_grid is not None
        assert grid._display_settings_grid is not None
        assert grid._flash_messages_grid is not None
        assert grid._progress_bars_grid is not None

    def test_braille_preferences_grid_save_settings(self, test_context: OrcaTestContext) -> None:
        """Test BraillePreferencesGrid save_settings returns combined dict."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import BraillePresenter, BraillePreferencesGrid

        presenter = BraillePresenter()
        grid = BraillePreferencesGrid(presenter)

        result = grid.save_settings()

        assert isinstance(result, dict)
        assert "brailleVerbosityLevel" in result
        assert "disableBrailleEOL" in result
        assert "enableFlashMessages" in result
        assert "brailleProgressBarUpdates" in result

    def test_braille_preferences_grid_title_callback(self, test_context: OrcaTestContext) -> None:
        """Test BraillePreferencesGrid stores title change callback."""

        self._setup_dependencies(test_context)
        from orca.braille_presenter import BraillePresenter, BraillePreferencesGrid

        presenter = BraillePresenter()
        callback_calls: list[str] = []

        def title_callback(title: str) -> None:
            callback_calls.append(title)

        grid = BraillePreferencesGrid(presenter, title_change_callback=title_callback)

        assert grid._title_change_callback is title_callback

    def test_verbosity_grid_switch_reflects_initial_value(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test verbosity grid switch shows correct initial value."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        settings_mock.brailleVerbosityLevel = settings_mock.VERBOSITY_LEVEL_VERBOSE

        from orca.braille_presenter import (
            BraillePresenter,
            BrailleVerbosityPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleVerbosityPreferencesGrid(presenter)

        detailed_switch = grid.get_widget(0)
        assert detailed_switch is not None
        assert detailed_switch.get_active() is True

    def test_verbosity_grid_switch_toggle_updates_setting(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test toggling verbosity switch updates the setting."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        settings_mock.brailleVerbosityLevel = settings_mock.VERBOSITY_LEVEL_BRIEF

        from orca.braille_presenter import (
            BraillePresenter,
            BrailleVerbosityPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleVerbosityPreferencesGrid(presenter)

        detailed_switch = grid.get_widget(0)
        assert detailed_switch is not None
        assert detailed_switch.get_active() is False

        grid._initializing = False
        detailed_switch.set_active(True)

        result = grid.save_settings()
        assert result["brailleVerbosityLevel"] == settings_mock.VERBOSITY_LEVEL_VERBOSE

    def test_flash_messages_duration_initial_value(self, test_context: OrcaTestContext) -> None:
        """Test flash duration spinbutton shows correct initial value."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        settings_mock.brailleFlashTime = 3000

        from orca.braille_presenter import (
            BraillePresenter,
            BrailleFlashMessagesPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleFlashMessagesPreferencesGrid(presenter)

        duration_spinbutton = grid.get_widget(3)
        assert duration_spinbutton is not None
        assert duration_spinbutton.get_value() == 3

    def test_display_settings_combobox_initial_value(self, test_context: OrcaTestContext) -> None:
        """Test indicator combobox shows correct initial selection."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        settings_mock.brailleLinkIndicator = settings_mock.BRAILLE_UNDERLINE_7

        from orca.braille_presenter import (
            BraillePresenter,
            BrailleDisplaySettingsPreferencesGrid,
        )

        presenter = BraillePresenter()
        grid = BrailleDisplaySettingsPreferencesGrid(presenter)

        link_combo = grid.get_widget(5)
        assert link_combo is not None
        assert link_combo.get_active() == 1
