# Unit tests for ax_text.py methods.
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

# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals

"""Unit tests for ax_text.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

class MockRect:  # pylint: disable=too-few-public-methods
    """Mock rectangle class for testing."""

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height


@pytest.mark.unit
class TestAXTextAttribute:
    """Test AXTextAttribute enum methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_text dependencies."""

        additional_modules = [
            "locale",
            "orca.colornames",
            "orca.ax_utilities_role",
            "orca.ax_utilities_state",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        locale_mock = essential_modules["locale"]
        locale_mock.localeconv = test_context.Mock(return_value={"decimal_point": "."})

        colornames_mock = essential_modules["orca.colornames"]
        colornames_mock.COLOR_NAMES = {"#ff0000": "red", "#00ff00": "green"}
        colornames_mock.rgb_string_to_color_name = test_context.Mock(
            side_effect=lambda color: colornames_mock.COLOR_NAMES.get(color, color)
        )
        colornames_mock.normalize_rgb_string = test_context.Mock(side_effect=lambda color: color)
        colornames_mock.get_presentable_color_name = test_context.Mock(
            side_effect=lambda color: colornames_mock.COLOR_NAMES.get(color, color)
        )

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.debugLevel = 0
        debug_mock.debug = test_context.Mock()
        debug_mock.print_message = test_context.Mock()

        messages_mock = essential_modules["orca.messages"]
        messages_mock.TEXT_ATTRIBUTE_NAMES = {
            "bg-color": "Background Color",
            "size": "size",
            "language": "Language",
            "weight": "Weight",
            "family-name": "Family Name",
        }
        messages_mock.pixel_count = test_context.Mock(
            side_effect=lambda count: f"{count} pixel{'s' if count != 1.0 else ''}"
        )

        settings_mock = essential_modules["orca.settings"]
        settings_mock.speakTextAttributes = True
        settings_mock.useColorNames = True

        text_attribute_names_mock = essential_modules["orca.text_attribute_names"]
        text_attribute_names_mock.attribute_names = {
            "bg-color": "Background Color",
            "size": "size",
            "language": "Language",
            "weight": "Weight",
            "family-name": "Family Name",
        }
        text_attribute_names_mock.attribute_values = test_context.Mock()
        text_attribute_names_mock.attribute_values.get = test_context.Mock(
            side_effect=lambda value, default: default
        )

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.supports_text = test_context.Mock(return_value=True)
        ax_object_mock.AXObject = ax_object_class_mock

        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"]
        role_class_mock = test_context.Mock()
        ax_utilities_role_mock.AXUtilitiesRole = role_class_mock

        ax_utilities_state_mock = essential_modules["orca.ax_utilities_state"]
        state_class_mock = test_context.Mock()
        ax_utilities_state_mock.AXUtilitiesState = state_class_mock

        return essential_modules

    def test_from_string_with_valid_attribute(self, test_context: OrcaTestContext) -> None:
        """Test AXTextAttribute.from_string with valid attribute name."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_string("bg-color")
        assert result == AXTextAttribute.BG_COLOR

    def test_from_string_with_invalid_attribute(self, test_context: OrcaTestContext) -> None:
        """Test AXTextAttribute.from_string with invalid attribute name."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_string("invalid-attribute")
        assert result is None

    def test_from_localized_string_with_valid_attribute(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTextAttribute.from_localized_string with valid localized name."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_localized_string("Background Color")
        assert result == AXTextAttribute.BG_COLOR

    def test_from_localized_string_with_invalid_attribute(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTextAttribute.from_localized_string with invalid localized name."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_localized_string("Invalid Localized")
        assert result is None

    def test_get_attribute_name(self, test_context: OrcaTestContext) -> None:
        """Test AXTextAttribute.get_attribute_name."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.BG_COLOR.get_attribute_name()
        assert result == "bg-color"

    def test_get_localized_name_with_translation(self, test_context: OrcaTestContext) -> None:
        """Test AXTextAttribute.get_localized_name with available translation."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.BG_COLOR.get_localized_name()
        assert result == "Background Color"

    def test_get_localized_name_without_translation(self, test_context: OrcaTestContext) -> None:
        """Test AXTextAttribute.get_localized_name without available translation."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.INDENT.get_localized_name()
        assert result == "indent"

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "pixel_int_multiple",
                "attribute_name": "INDENT",
                "input_value": "12px",
                "expected_result": "12 pixels",
            },
            {
                "id": "pixel_int_singular",
                "attribute_name": "INDENT",
                "input_value": "1px",
                "expected_result": "1 pixel",
            },
            {
                "id": "pixel_int_zero",
                "attribute_name": "INDENT",
                "input_value": "0px",
                "expected_result": "0 pixels",
            },
            {
                "id": "pixel_float_multiple",
                "attribute_name": "INDENT",
                "input_value": "12.5px",
                "expected_result": "12.5 pixels",
            },
            {
                "id": "pixel_float_singular",
                "attribute_name": "INDENT",
                "input_value": "1.0px",
                "expected_result": "1.0 pixel",
            },
            {
                "id": "pixel_float_zero",
                "attribute_name": "INDENT",
                "input_value": "0.0px",
                "expected_result": "0.0 pixels",
            },
            {
                "id": "color_red",
                "attribute_name": "BG_COLOR",
                "input_value": "#ff0000",
                "expected_result": "red",
            },
            {
                "id": "moz_prefix_removal",
                "attribute_name": "JUSTIFICATION",
                "input_value": "left-moz",
                "expected_result": "left",
            },
            {
                "id": "justify_to_fill",
                "attribute_name": "JUSTIFICATION",
                "input_value": "justify",
                "expected_result": "fill",
            },
            {
                "id": "family_name_cleanup",
                "attribute_name": "FAMILY_NAME",
                "input_value": "Arial, sans-serif",
                "expected_result": "Arial",
            },
            {
                "id": "regular_value",
                "attribute_name": "LANGUAGE",
                "input_value": "en-US",
                "expected_result": "en-US",
            },
            {
                "id": "none_value",
                "attribute_name": "LANGUAGE",
                "input_value": None,
                "expected_result": "",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_localized_value_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTextAttribute.get_localized_value with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        attribute = getattr(AXTextAttribute, case["attribute_name"])
        result = attribute.get_localized_value(case["input_value"])
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "bg_color_true", "attribute": "BG_COLOR", "expected": True},
            {"id": "bg_full_height_false", "attribute": "BG_FULL_HEIGHT", "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_should_present_by_default(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXTextAttribute.should_present_by_default."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        attr = getattr(AXTextAttribute, case["attribute"])
        result = attr.should_present_by_default()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "bg_color_zero", "attribute": "BG_COLOR", "value": "0", "expected": True},
            {"id": "bg_color_zero_px", "attribute": "BG_COLOR", "value": "0px", "expected": True},
            {"id": "bg_color_none", "attribute": "BG_COLOR", "value": "none", "expected": True},
            {"id": "bg_color_empty", "attribute": "BG_COLOR", "value": "", "expected": True},
            {"id": "bg_color_null", "attribute": "BG_COLOR", "value": None, "expected": True},
            {"id": "scale_one", "attribute": "SCALE", "value": "1.0", "expected": True},
            {
                "id": "text_position_baseline",
                "attribute": "TEXT_POSITION",
                "value": "baseline",
                "expected": True,
            },
            {"id": "weight_400", "attribute": "WEIGHT", "value": "400", "expected": True},
            {
                "id": "bg_color_bold_false",
                "attribute": "BG_COLOR",
                "value": "bold",
                "expected": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_value_is_default(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXTextAttribute.value_is_default."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        attr = getattr(AXTextAttribute, case["attribute"])
        result = attr.value_is_default(case["value"])
        assert result == case["expected"]


@pytest.mark.unit
class TestAXText:
    """Test AXText class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_text dependencies."""

        additional_modules = [
            "locale",
            "orca.colornames",
            "orca.ax_utilities_role",
            "orca.ax_utilities_state",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        locale_mock = essential_modules["locale"]
        locale_mock.localeconv = test_context.Mock(return_value={"decimal_point": "."})

        colornames_mock = essential_modules["orca.colornames"]
        colornames_mock.COLOR_NAMES = {"#ff0000": "red", "#00ff00": "green"}
        colornames_mock.rgb_string_to_color_name = test_context.Mock(
            side_effect=lambda color: colornames_mock.COLOR_NAMES.get(color, color)
        )
        colornames_mock.normalize_rgb_string = test_context.Mock(side_effect=lambda color: color)
        colornames_mock.get_presentable_color_name = test_context.Mock(
            side_effect=lambda color: colornames_mock.COLOR_NAMES.get(color, color)
        )

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.debugLevel = 0
        debug_mock.debug = test_context.Mock()
        debug_mock.print_message = test_context.Mock()

        messages_mock = essential_modules["orca.messages"]
        messages_mock.TEXT_ATTRIBUTE_NAMES = {
            "bg-color": "Background Color",
            "size": "size",
            "language": "Language",
            "weight": "Weight",
            "family-name": "Family Name",
        }
        messages_mock.pixel_count = test_context.Mock(
            side_effect=lambda count: f"{count} pixel{'s' if count != 1.0 else ''}"
        )

        settings_mock = essential_modules["orca.settings"]
        settings_mock.speakTextAttributes = True
        settings_mock.useColorNames = True

        text_attribute_names_mock = essential_modules["orca.text_attribute_names"]
        text_attribute_names_mock.attribute_names = {
            "bg-color": "Background Color",
            "size": "size",
            "language": "Language",
            "weight": "Weight",
            "family-name": "Family Name",
        }
        text_attribute_names_mock.attribute_values = test_context.Mock()
        text_attribute_names_mock.attribute_values.get = test_context.Mock(
            side_effect=lambda value, default: default
        )

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.supports_text = test_context.Mock(return_value=True)
        ax_object_mock.AXObject = ax_object_class_mock

        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"]
        role_class_mock = test_context.Mock()
        ax_utilities_role_mock.AXUtilitiesRole = role_class_mock

        ax_utilities_state_mock = essential_modules["orca.ax_utilities_state"]
        state_class_mock = test_context.Mock()
        ax_utilities_state_mock.AXUtilitiesState = state_class_mock

        return essential_modules

    def test_is_eoc_with_embedded_object_character(self, test_context: OrcaTestContext) -> None:
        """Test AXText.is_eoc with embedded object character."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        result = AXText.is_eoc("\ufffc")
        assert result is True

    def test_is_eoc_with_regular_character(self, test_context: OrcaTestContext) -> None:
        """Test AXText.is_eoc with regular character."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        result = AXText.is_eoc("a")
        assert result is False

    def test_character_at_offset_is_eoc_with_eoc(self, test_context: OrcaTestContext) -> None:
        """Test AXText.character_at_offset_is_eoc with embedded object character."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText, "get_character_at_offset", return_value=("\ufffc", 5, 6)
        )
        result = AXText.character_at_offset_is_eoc(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is True

    def test_character_at_offset_is_eoc_without_eoc(self, test_context: OrcaTestContext) -> None:
        """Test AXText.character_at_offset_is_eoc without embedded object character."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText, "get_character_at_offset", return_value=("a", 5, 6)
        )
        result = AXText.character_at_offset_is_eoc(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is False

    def test_is_whitespace_or_empty_with_whitespace(self, test_context: OrcaTestContext) -> None:
        """Test AXText.is_whitespace_or_empty with whitespace text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_all_text", return_value="   \t\n  ")
        result = AXText.is_whitespace_or_empty(test_context.Mock(spec=Atspi.Accessible))
        assert result is True

    def test_is_whitespace_or_empty_with_content(self, test_context: OrcaTestContext) -> None:
        """Test AXText.is_whitespace_or_empty with actual content."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_all_text", return_value="Hello world")
        result = AXText.is_whitespace_or_empty(test_context.Mock(spec=Atspi.Accessible))
        assert result is False

    def test_has_presentable_text_with_word_characters(self, test_context: OrcaTestContext) -> None:
        """Test AXText.has_presentable_text with word characters."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_all_text", return_value="Hello123")
        result = AXText.has_presentable_text(test_context.Mock(spec=Atspi.Accessible))
        assert result is True

    def test_has_presentable_text_without_word_characters(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.has_presentable_text without word characters."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_all_text", return_value="!@#$%^&*()")
        result = AXText.has_presentable_text(test_context.Mock(spec=Atspi.Accessible))
        assert result is False

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "successful",
                "should_raise_error": False,
                "expected_result": 50,
                "expected_debug_method": "print_tokens",
            },
            {
                "id": "glib_error",
                "should_raise_error": True,
                "expected_result": -1,
                "expected_debug_method": "print_message",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_caret_offset(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText.get_caret_offset successful case and GLib.GError handling."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        if case["should_raise_error"]:

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test error")

            test_context.patch_object(Atspi.Text, "get_caret_offset", new=raise_glib_error)
        else:
            test_context.patch_object(Atspi.Text, "get_caret_offset", return_value=50)

        essential_modules["orca.debug"].print_tokens = test_context.Mock()
        essential_modules["orca.debug"].print_message = test_context.Mock()
        result = AXText.get_caret_offset(test_context.Mock(spec=Atspi.Accessible))
        assert result == case["expected_result"]
        getattr(essential_modules["orca.debug"], case["expected_debug_method"]).assert_called()

    def test_set_caret_offset_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.set_caret_offset successful case."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(Atspi.Text, "set_caret_offset", return_value=True)
        essential_modules["orca.debug"].print_tokens = test_context.Mock()
        result = AXText.set_caret_offset(test_context.Mock(spec=Atspi.Accessible), 25)
        assert result is True
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_set_caret_offset_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.set_caret_offset handles GLib.GError."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        def raise_glib_error(_obj, _offset) -> None:
            raise GLib.GError("Test error")

        test_context.patch_object(Atspi.Text, "set_caret_offset", new=raise_glib_error)
        essential_modules["orca.debug"].print_message = test_context.Mock()
        result = AXText.set_caret_offset(test_context.Mock(spec=Atspi.Accessible), 25)
        assert result is False
        essential_modules["orca.debug"].print_message.assert_called()

    def test_set_caret_offset_to_start(self, test_context: OrcaTestContext) -> None:
        """Test AXText.set_caret_offset_to_start."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "set_caret_offset", return_value=True)
        result = AXText.set_caret_offset_to_start(test_context.Mock(spec=Atspi.Accessible))
        assert result is True

    def test_set_caret_offset_to_end(self, test_context: OrcaTestContext) -> None:
        """Test AXText.set_caret_offset_to_end."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=100)
        test_context.patch_object(AXText, "set_caret_offset", return_value=True)
        result = AXText.set_caret_offset_to_end(test_context.Mock(spec=Atspi.Accessible))
        assert result is True

    def test_has_selected_text_without_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText.has_selected_text without text selection."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "_get_n_selections", return_value=0)
        result = AXText.has_selected_text(test_context.Mock(spec=Atspi.Accessible))
        assert result is False

    def test_get_n_selections_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText._get_n_selections successful case."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(Atspi.Text, "get_n_selections", return_value=2)
        essential_modules["orca.debug"].print_tokens = test_context.Mock()
        result = AXText._get_n_selections(test_context.Mock(spec=Atspi.Accessible))
        assert result == 2
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_get_n_selections_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText._get_n_selections handles GLib.GError."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        def raise_glib_error(_obj) -> None:
            raise GLib.GError("Test error")

        test_context.patch_object(Atspi.Text, "get_n_selections", new=raise_glib_error)
        essential_modules["orca.debug"].print_message = test_context.Mock()
        result = AXText._get_n_selections(test_context.Mock(spec=Atspi.Accessible))
        assert result == 0
        essential_modules["orca.debug"].print_message.assert_called()

    def test_get_cached_selected_text_without_cache(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_cached_selected_text without cached data."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.Mock(spec=Atspi.Accessible).hash = test_context.Mock(return_value=54321)
        AXText.CACHED_TEXT_SELECTION.clear()
        result = AXText.get_cached_selected_text(test_context.Mock(spec=Atspi.Accessible))
        assert result == ("", 0, 0)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "fully_contained",
                "rect1": MockRect(x=10, y=10, width=20, height=20),
                "rect2": MockRect(x=5, y=5, width=30, height=30),
                "expected": True,
            },
            {
                "id": "not_contained",
                "rect1": MockRect(x=0, y=0, width=20, height=20),
                "rect2": MockRect(x=5, y=5, width=10, height=10),
                "expected": False,
            },
            {
                "id": "exactly_same",
                "rect1": MockRect(x=10, y=10, width=20, height=20),
                "rect2": MockRect(x=10, y=10, width=20, height=20),
                "expected": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_rect_is_fully_contained_in(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXText._rect_is_fully_contained_in."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        result = AXText._rect_is_fully_contained_in(case["rect1"], case["rect2"])
        assert result is case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "line_inside_clip",
                "line_rect": MockRect(y=10, height=10),
                "clip_rect": MockRect(y=5, height=30),
                "expected": 0,
            },
            {
                "id": "line_above_clip",
                "line_rect": MockRect(y=0, height=10),
                "clip_rect": MockRect(y=15, height=20),
                "expected": -1,
            },
            {
                "id": "line_below_clip",
                "line_rect": MockRect(y=40, height=10),
                "clip_rect": MockRect(y=5, height=20),
                "expected": 1,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_line_comparison(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXText._line_comparison."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        result = AXText._line_comparison(case["line_rect"], case["clip_rect"])
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "successful", "should_raise_error": False, "expected_result": ("hello", 5, 10)},
            {"id": "glib_error", "should_raise_error": True, "expected_result": ("", 0, 0)},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_word_at_offset(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText.get_word_at_offset successful case and GLib.GError handling."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch_object(AXText, "get_caret_offset", return_value=7)

        if case["should_raise_error"]:

            def mock_get_string_at_offset(_obj, _offset, _granularity) -> None:
                raise GLib.GError("Test error")

            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset", new=mock_get_string_at_offset
            )
        else:
            mock_result = test_context.Mock()
            mock_result.content = "hello"
            mock_result.start_offset = 5
            mock_result.end_offset = 10
            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset",
                side_effect=lambda obj, offset, granularity: mock_result,
            )

        result = AXText.get_word_at_offset(test_context.Mock(spec=Atspi.Accessible))
        assert result == case["expected_result"]

    def test_get_all_text_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_all_text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=25)
        test_context.patch(
            "gi.repository.Atspi.Text.get_text", return_value="This is some test text"
        )
        result = AXText.get_all_text(test_context.Mock(spec=Atspi.Accessible))
        assert result == "This is some test text"

    def test_get_all_text_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_all_text handles GLib.GError exceptions."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=25)

        def mock_get_text(_obj, _start, _end) -> None:
            raise GLib.GError("Test error")

        test_context.patch("gi.repository.Atspi.Text.get_text", new=mock_get_text)
        result = AXText.get_all_text(test_context.Mock(spec=Atspi.Accessible))
        assert result == ""

    def test_get_selected_text_with_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_selected_text with text selected."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText, "get_selected_ranges", return_value=[(5, 10), (15, 20)]
        )
        test_context.patch_object(
            AXText, "get_substring", side_effect=lambda obj, start, end: f"text{start}-{end}"
        )
        result = AXText.get_selected_text(test_context.Mock(spec=Atspi.Accessible))
        assert result == ("text5-10 text15-20", 5, 20)

    def test_get_selected_text_without_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_selected_text without text selected."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_selected_ranges", return_value=[])
        result = AXText.get_selected_text(test_context.Mock(spec=Atspi.Accessible))
        assert result == ("", 0, 0)

    def test_get_text_attributes_at_offset_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_text_attributes_at_offset."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_caret_offset", return_value=5)
        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"font-family": "Arial", "font-size": "12pt"}, 0, 10),
        )
        result = AXText.get_text_attributes_at_offset(test_context.Mock(spec=Atspi.Accessible))
        assert result == ({"font-family": "Arial", "font-size": "12pt"}, 0, 10)

    def test_get_text_attributes_at_offset_with_glib_error(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.get_text_attributes_at_offset handles GLib.GError exceptions."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_caret_offset", return_value=5)
        test_context.patch_object(AXText, "get_character_count", return_value=20)

        def mock_get_attribute_run(_obj, _offset, include_defaults=True) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.get_attribute_run", new=mock_get_attribute_run
        )
        result = AXText.get_text_attributes_at_offset(test_context.Mock(spec=Atspi.Accessible))
        assert result == ({}, 0, 20)

    def test_get_all_text_attributes_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_all_text_attributes."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_character_count", return_value=20)

        def mock_get_text_attributes_at_offset(_obj, offset) -> tuple[dict[str, str], int, int]:
            if offset < 10:
                return ({"font-weight": "bold"}, 0, 10)
            return ({"font-style": "italic"}, 10, 20)

        test_context.patch_object(
            AXText, "get_text_attributes_at_offset", new=mock_get_text_attributes_at_offset
        )
        result = AXText.get_all_text_attributes(test_context.Mock(spec=Atspi.Accessible))
        assert len(result) == 2
        assert result[0] == (0, 10, {"font-weight": "bold"})
        assert result[1] == (10, 20, {"font-style": "italic"})

    def test_supports_paragraph_iteration_true(self, test_context: OrcaTestContext) -> None:
        """Test AXText.supports_paragraph_iteration returns True."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText, "get_paragraph_at_offset", return_value=("This is a paragraph.", 0, 20)
        )
        result = AXText.supports_paragraph_iteration(test_context.Mock(spec=Atspi.Accessible))
        assert result is True

    def test_iter_character_with_valid_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.iter_character with valid text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)
        test_context.patch_object(AXText, "get_character_count", return_value=3)

        def mock_get_character_at_offset(_obj, offset) -> tuple[str, int, int]:
            chars = [("a", 0, 1), ("b", 1, 2), ("c", 2, 3)]
            if 0 <= offset < 3:
                return chars[offset]
            return ("", 0, 0)

        test_context.patch_object(
            AXText, "get_character_at_offset", new=mock_get_character_at_offset
        )
        result = list(AXText.iter_character(test_context.Mock(spec=Atspi.Accessible)))
        assert result == [("a", 0, 1), ("b", 1, 2), ("c", 2, 3)]

    def test_iter_character_with_empty_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.iter_character with empty text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)
        test_context.patch_object(AXText, "get_character_count", return_value=0)
        result = list(AXText.iter_character(test_context.Mock(spec=Atspi.Accessible)))
        assert not result

    def test_iter_word_with_valid_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.iter_word with valid text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)
        test_context.patch_object(AXText, "get_character_count", return_value=11)

        def mock_get_word_at_offset(_obj, offset) -> tuple[str, int, int]:
            if offset is None:
                offset = 0
            if 0 <= offset < 5:
                return ("hello", 0, 5)
            if 5 <= offset < 11:
                return (" world", 5, 11)
            return ("", 0, 0)

        test_context.patch_object(AXText, "get_word_at_offset", new=mock_get_word_at_offset)
        result = list(AXText.iter_word(test_context.Mock(spec=Atspi.Accessible)))
        assert result == [("hello", 0, 5), (" world", 5, 11)]

    def test_iter_line_with_valid_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.iter_line with valid text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)
        test_context.patch_object(AXText, "get_character_count", return_value=20)

        def mock_get_line_at_offset(_obj, offset) -> tuple[str, int, int]:
            if offset is None:
                offset = 0
            if 0 <= offset < 10:
                return ("First line", 0, 10)
            if 10 <= offset < 20:
                return ("Second line", 10, 20)
            return ("", 0, 0)

        test_context.patch_object(AXText, "get_line_at_offset", new=mock_get_line_at_offset)
        result = list(AXText.iter_line(test_context.Mock(spec=Atspi.Accessible)))
        assert result == [("First line", 0, 10), ("Second line", 10, 20)]

    def test_iter_line_prevents_infinite_loop_when_get_next_line_returns_same_position(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that iter_line prevents infinite loops when get_next_line doesn't advance."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)

        def mock_get_line_at_offset(_obj, offset) -> tuple[str, int, int]:
            if offset is None:
                offset = 0
            return ("Test line", 0, 10)

        def mock_get_next_line(_obj, _offset) -> tuple[str, int, int]:
            return ("Next line", 0, 10)

        test_context.patch_object(AXText, "get_line_at_offset", new=mock_get_line_at_offset)
        test_context.patch_object(AXText, "get_next_line", new=mock_get_next_line)

        result = list(AXText.iter_line(test_context.Mock(spec=Atspi.Accessible)))
        assert result == [("Test line", 0, 10)]

    def test_iter_line_skips_duplicate_when_offset_at_end(
        self, test_context: OrcaTestContext
    ) -> None:
        """Ensure iter_line doesn't yield the same line when starting at its end offset."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        # get_line_at_offset returns the same first line even when called at end
        test_context.patch_object(
            AXText,
            "get_line_at_offset",
            new=lambda _obj, _offset: ("First line", 0, 10),
        )

        # get_next_line advances to a distinct second line only once
        def mock_get_next_line(_obj, offset) -> tuple[str, int, int]:
            if offset == 0:
                return ("Second line", 10, 20)
            return ("", 0, 0)

        test_context.patch_object(AXText, "get_next_line", new=mock_get_next_line)

        result = list(AXText.iter_line(test_context.Mock(spec=Atspi.Accessible), 10))
        assert result == [("Second line", 10, 20)]

    def test_iter_sentence_prevents_infinite_loop_when_get_next_sentence_returns_same_position(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that iter_sentence prevents infinite loops if get_next_sentence doesn't advance."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)

        def mock_get_sentence_at_offset(_obj, offset) -> tuple[str, int, int]:
            if offset is None:
                offset = 0
            return ("Test sentence", 0, 15)

        def mock_get_next_sentence(_obj, _offset) -> tuple[str, int, int]:
            return ("Next sentence", 0, 15)

        test_context.patch_object(AXText, "get_sentence_at_offset", new=mock_get_sentence_at_offset)
        test_context.patch_object(AXText, "get_next_sentence", new=mock_get_next_sentence)

        result = list(AXText.iter_sentence(test_context.Mock(spec=Atspi.Accessible)))
        assert result == [("Test sentence", 0, 15)]

    def test_iter_sentence_skips_duplicate_when_offset_at_end(
        self, test_context: OrcaTestContext
    ) -> None:
        """Ensure iter_sentence doesn't yield the same sentence when starting at its end."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        # get_sentence_at_offset returns the same first sentence even at its end
        test_context.patch_object(
            AXText,
            "get_sentence_at_offset",
            new=lambda _obj, _offset: ("First sentence.", 0, 12),
        )

        # get_next_sentence advances to a distinct second sentence only once
        def mock_get_next_sentence(_obj, offset) -> tuple[str, int, int]:
            if offset == 0:
                return ("Second sentence.", 12, 25)
            return ("", 0, 0)

        test_context.patch_object(AXText, "get_next_sentence", new=mock_get_next_sentence)

        result = list(AXText.iter_sentence(test_context.Mock(spec=Atspi.Accessible), 12))
        assert result == [("Second sentence.", 12, 25)]

    def test_iter_sentence_with_valid_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.iter_sentence with valid text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)
        test_context.patch_object(AXText, "get_character_count", return_value=25)

        def mock_get_sentence_at_offset(_obj, offset) -> tuple[str, int, int]:
            if offset is None:
                offset = 0
            if 0 <= offset < 12:
                return ("First sentence.", 0, 12)
            if 12 <= offset < 25:
                return ("Second sentence.", 12, 25)
            return ("", 0, 0)

        test_context.patch_object(
            AXText, "get_sentence_at_offset", new=mock_get_sentence_at_offset
        )
        result = list(AXText.iter_sentence(test_context.Mock(spec=Atspi.Accessible)))
        assert result == [("First sentence.", 0, 12), ("Second sentence.", 12, 25)]

    def test_iter_paragraph_with_valid_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.iter_paragraph with valid text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_caret_offset", return_value=0)
        test_context.patch_object(AXText, "get_character_count", return_value=30)

        def mock_get_paragraph_at_offset(_obj, offset) -> tuple[str, int, int]:
            if offset is None:
                offset = 0
            if 0 <= offset < 15:
                return ("First paragraph.", 0, 15)
            if 15 <= offset < 30:
                return ("Second paragraph.", 15, 30)
            return ("", 0, 0)

        test_context.patch_object(
            AXText, "get_paragraph_at_offset", new=mock_get_paragraph_at_offset
        )
        result = list(AXText.iter_paragraph(test_context.Mock(spec=Atspi.Accessible)))
        assert result == [("First paragraph.", 0, 15), ("Second paragraph.", 15, 30)]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "offset_successful",
                "method_type": "offset",
                "offset_result": 25,
                "char_count": 30,
                "expected_result": 25,
                "should_raise_error": False,
                "debug_method": "print_tokens",
                "x_coord": 100,
                "y_coord": 200,
            },
            {
                "id": "offset_glib_error",
                "method_type": "offset",
                "offset_result": -1,
                "char_count": 30,
                "expected_result": -1,
                "should_raise_error": True,
                "debug_method": "print_message",
                "x_coord": 100,
                "y_coord": 200,
            },
            {
                "id": "character_valid",
                "method_type": "character",
                "offset_result": 5,
                "char_count": 10,
                "expected_result": ("a", 5, 6),
                "should_raise_error": False,
                "debug_method": None,
                "x_coord": 100,
                "y_coord": 200,
            },
            {
                "id": "character_invalid_offset",
                "method_type": "character",
                "offset_result": -1,
                "char_count": 10,
                "expected_result": ("", 0, 0),
                "should_raise_error": False,
                "debug_method": None,
                "x_coord": 100,
                "y_coord": 200,
            },
            {
                "id": "word_valid",
                "method_type": "word",
                "offset_result": 5,
                "char_count": 10,
                "expected_result": ("hello", 3, 8),
                "should_raise_error": False,
                "debug_method": None,
                "x_coord": 100,
                "y_coord": 200,
            },
            {
                "id": "line_valid",
                "method_type": "line",
                "offset_result": 5,
                "char_count": 20,
                "expected_result": ("This is a line", 0, 14),
                "should_raise_error": False,
                "debug_method": None,
                "x_coord": 100,
                "y_coord": 200,
            },
            {
                "id": "sentence_valid",
                "method_type": "sentence",
                "offset_result": 5,
                "char_count": 20,
                "expected_result": ("This is a sentence.", 0, 19),
                "should_raise_error": False,
                "debug_method": None,
                "x_coord": 100,
                "y_coord": 200,
            },
            {
                "id": "paragraph_valid",
                "method_type": "paragraph",
                "offset_result": 5,
                "char_count": 25,
                "expected_result": ("This is a paragraph.", 0, 20),
                "should_raise_error": False,
                "debug_method": None,
                "x_coord": 100,
                "y_coord": 200,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_at_point_methods_scenarios(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText get_*_at_point methods with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result: int | tuple[str, int, int] | None = None

        if case["method_type"] == "offset":
            if case["should_raise_error"]:

                def raise_glib_error(_obj, _x, _y, _coord_type) -> None:
                    raise GLib.GError("Test error")

                test_context.patch_object(
                    Atspi.Text, "get_offset_at_point", new=raise_glib_error
                )
            else:
                test_context.patch_object(
                    Atspi.Text,
                    "get_offset_at_point",
                    side_effect=lambda obj, x, y, coord_type: case["offset_result"],
                )
            essential_modules["orca.debug"].print_tokens = test_context.Mock()
            essential_modules["orca.debug"].print_message = test_context.Mock()
            result = AXText.get_offset_at_point(mock_obj, case["x_coord"], case["y_coord"])
            if case["debug_method"]:
                getattr(essential_modules["orca.debug"], case["debug_method"]).assert_called()
        else:
            test_context.patch_object(
                AXText, "get_offset_at_point", side_effect=lambda obj, x, y: case["offset_result"]
            )
            test_context.patch_object(
                AXText, "get_character_count", side_effect=lambda obj: case["char_count"]
            )

            if case["method_type"] == "character":
                if case["offset_result"] == -1:
                    result = AXText.get_character_at_point(
                        mock_obj, case["x_coord"], case["y_coord"]
                    )
                else:
                    test_context.patch_object(
                        AXText,
                        "get_character_at_offset",
                        side_effect=lambda obj, offset: case["expected_result"],
                    )
                    result = AXText.get_character_at_point(
                        mock_obj, case["x_coord"], case["y_coord"]
                    )
            elif case["method_type"] == "word":
                test_context.patch_object(
                    AXText,
                    "get_word_at_offset",
                    side_effect=lambda obj, offset: case["expected_result"]
                )
                result = AXText.get_word_at_point(mock_obj, case["x_coord"], case["y_coord"])
            elif case["method_type"] == "line":
                test_context.patch_object(
                    AXText,
                    "get_line_at_offset",
                    side_effect=lambda obj, offset: case["expected_result"]
                )
                result = AXText.get_line_at_point(mock_obj, case["x_coord"], case["y_coord"])
            elif case["method_type"] == "sentence":
                test_context.patch_object(
                    AXText,
                    "get_sentence_at_offset",
                    side_effect=lambda obj, offset: case["expected_result"]
                )
                result = AXText.get_sentence_at_point(mock_obj, case["x_coord"], case["y_coord"])
            elif case["method_type"] == "paragraph":
                test_context.patch_object(
                    AXText,
                    "get_paragraph_at_offset",
                    side_effect=lambda obj, offset: case["expected_result"]
                )
                result = AXText.get_paragraph_at_point(mock_obj, case["x_coord"], case["y_coord"])

        assert result == case["expected_result"]

    def test_string_has_spelling_error_with_invalid_spelling(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.string_has_spelling_error with spelling error."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"invalid": "spelling"}, 0, 10),
        )
        result = AXText.string_has_spelling_error(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is True

    def test_string_has_spelling_error_with_text_spelling(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.string_has_spelling_error with text-spelling misspelled."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"text-spelling": "misspelled"}, 0, 10),
        )
        result = AXText.string_has_spelling_error(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is True

    def test_string_has_spelling_error_with_underline_error(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.string_has_spelling_error with underline error."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"underline": "spelling"}, 0, 10),
        )
        result = AXText.string_has_spelling_error(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is True

    def test_string_has_spelling_error_without_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.string_has_spelling_error without spelling error."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"font-size": "12pt"}, 0, 10),
        )
        result = AXText.string_has_spelling_error(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is False

    def test_string_has_grammar_error_with_invalid_grammar(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.string_has_grammar_error with grammar error."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"invalid": "grammar"}, 0, 10),
        )
        result = AXText.string_has_grammar_error(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is True

    def test_string_has_grammar_error_with_underline_grammar(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.string_has_grammar_error with underline grammar."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"underline": "grammar"}, 0, 10),
        )
        result = AXText.string_has_grammar_error(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is True

    def test_string_has_grammar_error_without_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.string_has_grammar_error without grammar error."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText,
            "get_text_attributes_at_offset",
            return_value=({"font-size": "12pt"}, 0, 10),
        )
        result = AXText.string_has_grammar_error(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result is False

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "start_with_selection",
                "method_name": "get_selection_start_offset",
                "has_selection": True,
                "expected_result": 5,
            },
            {
                "id": "start_without_selection",
                "method_name": "get_selection_start_offset",
                "has_selection": False,
                "expected_result": -1,
            },
            {
                "id": "end_with_selection",
                "method_name": "get_selection_end_offset",
                "has_selection": True,
                "expected_result": 20,
            },
            {
                "id": "end_without_selection",
                "method_name": "get_selection_end_offset",
                "has_selection": False,
                "expected_result": -1,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_selection_offset_methods(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText selection offset methods with and without selection."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        selected_ranges = [(5, 10), (15, 20)] if case["has_selection"] else []
        test_context.patch_object(AXText, "get_selected_ranges", return_value=selected_ranges)

        method = getattr(AXText, case["method_name"])
        result = method(test_context.Mock(spec=Atspi.Accessible))
        assert result == case["expected_result"]

    def test_is_all_text_selected_with_full_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText.is_all_text_selected with full text selected."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch_object(AXText, "get_selected_ranges", return_value=[(0, 20)])
        result = AXText.is_all_text_selected(test_context.Mock(spec=Atspi.Accessible))
        assert result is True

    def test_is_all_text_selected_with_partial_selection(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.is_all_text_selected with partial selection."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch_object(AXText, "get_selected_ranges", return_value=[(5, 15)])
        result = AXText.is_all_text_selected(test_context.Mock(spec=Atspi.Accessible))
        assert result is False

    def test_is_all_text_selected_without_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText.is_all_text_selected without selection."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch_object(AXText, "get_selected_ranges", return_value=[])
        result = AXText.is_all_text_selected(test_context.Mock(spec=Atspi.Accessible))
        assert result is False

    def test_clear_all_selected_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.clear_all_selected_text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        removed_selections = []

        def mock_remove_selection(_obj, selection_number) -> None:
            removed_selections.append(selection_number)

        test_context.patch_object(AXText, "_get_n_selections", return_value=3)
        test_context.patch_object(AXText, "_remove_selection", new=mock_remove_selection)
        AXText.clear_all_selected_text(test_context.Mock(spec=Atspi.Accessible))
        assert removed_selections == [0, 1, 2]

    def test_remove_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText._remove_selection."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        mock_remove_selection = test_context.Mock()
        test_context.patch(
            "gi.repository.Atspi.Text.remove_selection", new=mock_remove_selection
        )
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        AXText._remove_selection(mock_accessible, 0)
        mock_remove_selection.assert_called_once_with(mock_accessible, 0)

    def test_remove_selection_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText._remove_selection handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)

        def mock_remove_selection(obj, selection_number) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.remove_selection", new=mock_remove_selection
        )

        AXText._remove_selection(test_context.Mock(spec=Atspi.Accessible), 0)

    def test_get_selected_ranges_with_valid_selections(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_selected_ranges with valid selections."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "_get_n_selections", return_value=2)

        def mock_get_selection(_obj, selection_num) -> None:
            results = [
                test_context.Mock(start_offset=5, end_offset=10),
                test_context.Mock(start_offset=15, end_offset=20),
            ]
            return results[selection_num]

        test_context.patch(
            "gi.repository.Atspi.Text.get_selection", new=mock_get_selection
        )
        result = AXText.get_selected_ranges(test_context.Mock(spec=Atspi.Accessible))
        assert result == [(5, 10), (15, 20)]

    def test_get_selected_ranges_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_selected_ranges handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "_get_n_selections", return_value=1)

        def mock_get_selection(obj, selection_num) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.get_selection", new=mock_get_selection
        )
        result = AXText.get_selected_ranges(test_context.Mock(spec=Atspi.Accessible))
        assert not result

    def test_add_new_selection_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText._add_new_selection successful case."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch(
            "gi.repository.Atspi.Text.add_selection", return_value=True
        )
        result = AXText._add_new_selection(test_context.Mock(spec=Atspi.Accessible), 5, 10)
        assert result is True

    def test_add_new_selection_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText._add_new_selection handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)

        def mock_add_selection(obj, start, end) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.add_selection", new=mock_add_selection
        )
        result = AXText._add_new_selection(test_context.Mock(spec=Atspi.Accessible), 5, 10)
        assert result is False

    def test_update_existing_selection_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText._update_existing_selection successful case."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch(
            "gi.repository.Atspi.Text.set_selection", return_value=True
        )
        result = AXText._update_existing_selection(
            test_context.Mock(spec=Atspi.Accessible), 5, 10, 0
        )
        assert result is True

    def test_update_existing_selection_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText._update_existing_selection handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)

        def mock_set_selection(obj, num, start, end) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.set_selection", new=mock_set_selection
        )
        result = AXText._update_existing_selection(
            test_context.Mock(spec=Atspi.Accessible), 5, 10, 0
        )
        assert result is False

    def test_set_selected_text_with_existing_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText.set_selected_text with existing selection."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "_get_n_selections", return_value=1)
        test_context.patch_object(
            AXText, "_update_existing_selection", return_value=True
        )
        test_context.patch_object(AXText, "get_substring", return_value="test")
        test_context.patch_object(AXText, "get_selected_text", return_value=("test", 5, 10))
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.debug"].debugLevel = 0
        result = AXText.set_selected_text(test_context.Mock(spec=Atspi.Accessible), 5, 10)
        assert result is True

    def test_set_selected_text_with_new_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXText.set_selected_text with new selection."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "_get_n_selections", return_value=0)
        test_context.patch_object(AXText, "_add_new_selection", return_value=True)
        test_context.patch_object(AXText, "get_substring", return_value="test")
        test_context.patch_object(AXText, "get_selected_text", return_value=("test", 5, 10))
        essential_modules["orca.debug"].debugLevel = 0
        result = AXText.set_selected_text(test_context.Mock(spec=Atspi.Accessible), 5, 10)
        assert result is True

    def test_update_cached_selected_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.update_cached_selected_text."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(
            AXText, "get_selected_text", return_value=("cached text", 5, 15)
        )
        AXText.CACHED_TEXT_SELECTION.clear()
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        AXText.update_cached_selected_text(mock_accessible)
        mock_hash = hash(mock_accessible)
        assert mock_hash in AXText.CACHED_TEXT_SELECTION
        assert AXText.CACHED_TEXT_SELECTION[mock_hash] == ("cached text", 5, 15)

    def test_get_character_rect_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_character_rect successful case."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_caret_offset", return_value=5)
        mock_rect = test_context.Mock(x=10, y=20, width=5, height=12)
        test_context.patch(
            "gi.repository.Atspi.Text.get_character_extents",
            side_effect=lambda obj, offset, coord_type: mock_rect,
        )
        result = AXText.get_character_rect(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result == mock_rect

    def test_get_character_rect_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_character_rect handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_caret_offset", return_value=5)

        def mock_get_character_extents(obj, offset, coord_type) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.get_character_extents", new=mock_get_character_extents
        )
        result = AXText.get_character_rect(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result.x == 0 and result.y == 0

    def test_get_range_rect_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_range_rect successful case."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)
        mock_rect = test_context.Mock(x=10, y=20, width=50, height=12)
        test_context.patch(
            "gi.repository.Atspi.Text.get_range_extents",
            side_effect=lambda obj, start, end, coord_type: mock_rect,
        )
        result = AXText.get_range_rect(test_context.Mock(spec=Atspi.Accessible), 5, 15)
        assert result == mock_rect

    def test_get_range_rect_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_range_rect handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=True)

        def mock_get_range_extents(obj, start, end, coord_type) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.get_range_extents", new=mock_get_range_extents
        )
        result = AXText.get_range_rect(test_context.Mock(spec=Atspi.Accessible), 5, 15)
        assert result.x == 0 and result.y == 0

    def test_scroll_substring_to_point_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.scroll_substring_to_point successful case."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch(
            "gi.repository.Atspi.Text.scroll_substring_to_point",
            return_value=True,
        )
        result = AXText.scroll_substring_to_point(
            test_context.Mock(spec=Atspi.Accessible), 100, 200, 5, 15
        )
        assert result is True

    def test_scroll_substring_to_point_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.scroll_substring_to_point handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)

        def mock_scroll_substring_to_point(obj, start, end, coord_type, x, y) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.scroll_substring_to_point", new=mock_scroll_substring_to_point
        )
        result = AXText.scroll_substring_to_point(
            test_context.Mock(spec=Atspi.Accessible), 100, 200, 5, 15
        )
        assert result is False

    def test_scroll_substring_to_location_successful(self, test_context: OrcaTestContext) -> None:
        """Test AXText.scroll_substring_to_location successful case."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        mock_scroll_type = test_context.Mock()

        def mock_scroll_success(_obj, _start, _end, _location) -> bool:
            return True

        test_context.patch(
            "gi.repository.Atspi.Text.scroll_substring_to", new=mock_scroll_success
        )
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        result = AXText.scroll_substring_to_location(mock_accessible, mock_scroll_type, 5, 15)
        assert result is True

    def test_scroll_substring_to_location_with_glib_error(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.scroll_substring_to_location handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)

        def mock_scroll_substring_to(obj, start, end, location) -> None:
            raise GLib.GError("Test error")

        mock_scroll_type = test_context.Mock()
        scroll_attr = "gi.repository.Atspi.Text.scroll_substring_to"
        test_context.patch(scroll_attr, new=mock_scroll_substring_to)
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        result = AXText.scroll_substring_to_location(mock_accessible, mock_scroll_type, 5, 15)
        assert result is False

    def test_get_visible_lines(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_visible_lines."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        clip_rect = test_context.Mock(x=0, y=0, width=100, height=50)
        test_context.patch_object(
            AXText, "find_first_visible_line", return_value=("First line", 0, 10)
        )

        def mock_iter_line(_obj, _offset) -> Generator[tuple[str, int, int], None, None]:
            lines = [("Second line", 10, 20), ("Third line", 20, 30)]
            yield from lines

        test_context.patch_object(AXText, "iter_line", new=mock_iter_line)
        test_context.patch_object(
            AXText,
            "get_range_rect",
            side_effect=lambda obj, start, end: test_context.Mock(x=0, y=10, width=50, height=10),
        )
        test_context.patch_object(AXText, "_line_comparison", return_value=0)
        result = AXText.get_visible_lines(test_context.Mock(spec=Atspi.Accessible), clip_rect)
        assert len(result) >= 1
        assert result[0] == ("First line", 0, 10)

    def test_find_first_visible_line_at_start(self, test_context: OrcaTestContext) -> None:
        """Test AXText.find_first_visible_line when first line is at start."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        clip_rect = test_context.Mock(x=0, y=0, width=100, height=50)
        test_context.patch_object(AXText, "get_character_count", return_value=100)
        test_context.patch_object(
            AXText, "get_line_at_offset", return_value=("First line", 0, 10)
        )
        result = AXText.find_first_visible_line(test_context.Mock(spec=Atspi.Accessible), clip_rect)
        assert result == ("First line", 0, 10)

    def test_find_last_visible_line_at_end(self, test_context: OrcaTestContext) -> None:
        """Test AXText.find_last_visible_line when last line is at end."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        clip_rect = test_context.Mock(x=0, y=0, width=100, height=50)
        test_context.patch_object(AXText, "get_character_count", return_value=100)
        test_context.patch_object(
            AXText, "get_line_at_offset", return_value=("Last line", 90, 100)
        )
        result = AXText.find_last_visible_line(test_context.Mock(spec=Atspi.Accessible), clip_rect)
        assert result == ("Last line", 90, 100)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "successful",
                "should_raise_error": False,
                "expected_result": ("This is a line", 0, 14),
            },
            {"id": "glib_error", "should_raise_error": True, "expected_result": ("", 0, 0)},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_line_at_offset(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText.get_line_at_offset successful case and GLib.GError handling."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch_object(AXText, "get_caret_offset", return_value=7)

        if case["should_raise_error"]:

            def mock_get_string_at_offset(_obj, _offset, _granularity) -> None:
                raise GLib.GError("Test error")

            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset", new=mock_get_string_at_offset
            )
        else:
            mock_result = test_context.Mock()
            mock_result.content = "This is a line"
            mock_result.start_offset = 0
            mock_result.end_offset = 14
            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset",
                side_effect=lambda obj, offset, granularity: mock_result,
            )

        result = AXText.get_line_at_offset(test_context.Mock(spec=Atspi.Accessible))
        assert result == case["expected_result"]

    def test_get_line_at_offset_chromium_fallback(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_line_at_offset with Chromium fallback for invalid result."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch_object(AXText, "get_caret_offset", return_value=20)
        call_count = 0

        def mock_get_string_at_offset(_obj, _offset, _granularity):
            nonlocal call_count
            call_count += 1
            mock_result = test_context.Mock()
            if call_count == 1:
                mock_result.content = ""
                mock_result.start_offset = -1
                mock_result.end_offset = -1
            else:
                mock_result.content = "Valid line"
                mock_result.start_offset = 10
                mock_result.end_offset = 20
            return mock_result

        test_context.patch(
            "gi.repository.Atspi.Text.get_string_at_offset", new=mock_get_string_at_offset
        )
        result = AXText.get_line_at_offset(test_context.Mock(spec=Atspi.Accessible), 20)
        assert result == ("Valid line", 10, 20)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "successful",
                "should_raise_error": False,
                "expected_result": ("This is a sentence.", 0, 19),
            },
            {"id": "glib_error", "should_raise_error": True, "expected_result": ("", 0, 0)},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_sentence_at_offset(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText.get_sentence_at_offset successful case and GLib.GError handling."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=25)
        test_context.patch_object(AXText, "get_caret_offset", return_value=7)

        if case["should_raise_error"]:

            def mock_get_string_at_offset(_obj, _offset, _granularity) -> None:
                raise GLib.GError("Test error")

            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset", new=mock_get_string_at_offset
            )
            test_context.patch(
                "gi.repository.Atspi.Text.get_text", return_value=""
            )
        else:
            mock_result = test_context.Mock()
            mock_result.content = "This is a sentence."
            mock_result.start_offset = 0
            mock_result.end_offset = 19
            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset",
                side_effect=lambda obj, offset, granularity: mock_result,
            )

        result = AXText.get_sentence_at_offset(test_context.Mock(spec=Atspi.Accessible))
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "successful",
                "should_raise_error": False,
                "expected_result": ("This is a paragraph.", 0, 20),
            },
            {"id": "glib_error", "should_raise_error": True, "expected_result": ("", 0, 0)},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_paragraph_at_offset(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText.get_paragraph_at_offset successful case and GLib.GError handling."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=25)
        test_context.patch_object(AXText, "get_caret_offset", return_value=7)

        if case["should_raise_error"]:

            def mock_get_string_at_offset(_obj, _offset, _granularity) -> None:
                raise GLib.GError("Test error")

            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset", new=mock_get_string_at_offset
            )
        else:
            mock_result = test_context.Mock()
            mock_result.content = "This is a paragraph."
            mock_result.start_offset = 0
            mock_result.end_offset = 20
            test_context.patch(
                "gi.repository.Atspi.Text.get_string_at_offset",
                side_effect=lambda obj, offset, granularity: mock_result,
            )

        result = AXText.get_paragraph_at_offset(test_context.Mock(spec=Atspi.Accessible))
        assert result == case["expected_result"]

    def test_get_character_at_offset_invalid_offset(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_character_at_offset with invalid offset."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        essential_modules["orca.debug"].print_message = test_context.Mock()
        test_context.patch(
            "gi.repository.Atspi.Text.get_character_count", return_value=10
        )
        result = AXText.get_character_at_offset(test_context.Mock(spec=Atspi.Accessible), 15)
        assert result == ("", 0, 0)
        essential_modules["orca.debug"].print_message.assert_called()

    def test_get_substring_with_end_offset_minus_one(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_substring with end_offset=-1."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_character_count", return_value=20)
        test_context.patch_object(
            Atspi.Text, "get_text", return_value="substring"
        )
        essential_modules["orca.debug"].print_tokens = test_context.Mock()
        result = AXText.get_substring(test_context.Mock(spec=Atspi.Accessible), 5, -1)
        assert result == "substring"

    def test_supports_paragraph_iteration_false(self, test_context: OrcaTestContext) -> None:
        """Test AXText.supports_paragraph_iteration returns False."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=False)
        result = AXText.supports_paragraph_iteration(test_context.Mock(spec=Atspi.Accessible))
        assert result is False

    def test_is_whitespace_or_empty_no_text_support(self, test_context: OrcaTestContext) -> None:
        """Test AXText.is_whitespace_or_empty with no text support."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_text", return_value=False)
        result = AXText.is_whitespace_or_empty(test_context.Mock(spec=Atspi.Accessible))
        assert result is True

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "matching_locale", "attribute_value": "en", "expected": True},
            {"id": "non_matching_locale", "attribute_value": "fr", "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_value_is_default_language_attribute(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXTextAttribute.value_is_default for LANGUAGE attribute."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXTextAttribute

        test_context.patch("locale.getlocale", return_value=("en_US", "UTF-8"))
        result = AXTextAttribute.LANGUAGE.value_is_default(case["attribute_value"])
        assert result is case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "next_character_successful",
                "direction": "next",
                "unit_type": "character",
                "setup_params": {
                    "caret_offset": 0,
                    "count": 5,
                    "data": {"0": ("a", 0, 1), "1": ("b", 1, 2), "2": ("c", 2, 3)},
                },
                "method_params": {},
                "expected": ("b", 1, 2),
            },
            {
                "id": "next_character_with_offset",
                "direction": "next",
                "unit_type": "character",
                "setup_params": {"count": 5, "data": {"1": ("b", 1, 2), "2": ("c", 2, 3)}},
                "method_params": {"offset": 1},
                "expected": ("c", 2, 3),
            },
            {
                "id": "next_character_no_current",
                "direction": "next",
                "unit_type": "character",
                "setup_params": {"caret_offset": 5, "data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_character_at_end",
                "direction": "next",
                "unit_type": "character",
                "setup_params": {"caret_offset": 4, "count": 5, "data": {"4": ("z", 4, 5)}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_word_successful",
                "direction": "next",
                "unit_type": "word",
                "setup_params": {
                    "caret_offset": 0,
                    "count": 15,
                    "word_data": {"0-5": ("first", 0, 5), "6-11": ("second", 6, 11)},
                },
                "method_params": {},
                "expected": ("second", 6, 11),
            },
            {
                "id": "next_word_with_offset",
                "direction": "next",
                "unit_type": "word",
                "setup_params": {
                    "count": 15,
                    "word_data": {"0-5": ("first", 0, 5), "6-11": ("second", 6, 11)},
                },
                "method_params": {"offset": 2},
                "expected": ("second", 6, 11),
            },
            {
                "id": "next_word_no_current",
                "direction": "next",
                "unit_type": "word",
                "setup_params": {"caret_offset": 5, "word_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_word_at_end",
                "direction": "next",
                "unit_type": "word",
                "setup_params": {
                    "caret_offset": 10,
                    "count": 15,
                    "word_data": {"10-15": ("last", 10, 15)},
                },
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_line_successful",
                "direction": "next",
                "unit_type": "line",
                "setup_params": {
                    "caret_offset": 0,
                    "count": 25,
                    "line_data": {"0-10": ("First line", 0, 10), "11-20": ("Second line", 11, 20)},
                },
                "method_params": {},
                "expected": ("Second line", 11, 20),
            },
            {
                "id": "next_line_with_offset",
                "direction": "next",
                "unit_type": "line",
                "setup_params": {
                    "count": 25,
                    "line_data": {"0-10": ("First line", 0, 10), "11-20": ("Second line", 11, 20)},
                },
                "method_params": {"offset": 5},
                "expected": ("Second line", 11, 20),
            },
            {
                "id": "next_line_no_current",
                "direction": "next",
                "unit_type": "line",
                "setup_params": {"caret_offset": 5, "line_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_line_at_end",
                "direction": "next",
                "unit_type": "line",
                "setup_params": {
                    "caret_offset": 15,
                    "count": 25,
                    "line_data": {"15-25": ("Last line", 15, 25)},
                },
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_sentence_successful",
                "direction": "next",
                "unit_type": "sentence",
                "setup_params": {
                    "caret_offset": 0,
                    "count": 30,
                    "sentence_data": {
                        "0-10": ("First sentence.", 0, 10),
                        "11-25": ("Second sentence.", 11, 25),
                    },
                },
                "method_params": {},
                "expected": ("Second sentence.", 11, 25),
            },
            {
                "id": "next_sentence_with_offset",
                "direction": "next",
                "unit_type": "sentence",
                "setup_params": {
                    "count": 30,
                    "sentence_data": {
                        "0-10": ("First sentence.", 0, 10),
                        "11-25": ("Second sentence.", 11, 25),
                    },
                },
                "method_params": {"offset": 5},
                "expected": ("Second sentence.", 11, 25),
            },
            {
                "id": "next_sentence_no_current",
                "direction": "next",
                "unit_type": "sentence",
                "setup_params": {"caret_offset": 5, "sentence_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_sentence_at_end",
                "direction": "next",
                "unit_type": "sentence",
                "setup_params": {
                    "caret_offset": 20,
                    "count": 30,
                    "sentence_data": {"20-30": ("Last sentence.", 20, 30)},
                },
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_paragraph_successful",
                "direction": "next",
                "unit_type": "paragraph",
                "setup_params": {
                    "caret_offset": 0,
                    "count": 40,
                    "paragraph_data": {
                        "0-15": ("First paragraph.", 0, 15),
                        "16-30": ("Second paragraph.", 16, 30),
                    },
                },
                "method_params": {},
                "expected": ("Second paragraph.", 16, 30),
            },
            {
                "id": "next_paragraph_with_offset",
                "direction": "next",
                "unit_type": "paragraph",
                "setup_params": {
                    "count": 40,
                    "paragraph_data": {
                        "0-15": ("First paragraph.", 0, 15),
                        "16-30": ("Second paragraph.", 16, 30),
                    },
                },
                "method_params": {"offset": 8},
                "expected": ("Second paragraph.", 16, 30),
            },
            {
                "id": "next_paragraph_no_current",
                "direction": "next",
                "unit_type": "paragraph",
                "setup_params": {"caret_offset": 5, "paragraph_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "next_paragraph_at_end",
                "direction": "next",
                "unit_type": "paragraph",
                "setup_params": {
                    "caret_offset": 25,
                    "count": 40,
                    "paragraph_data": {"25-40": ("Last paragraph.", 25, 40)},
                },
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_character_successful",
                "direction": "previous",
                "unit_type": "character",
                "setup_params": {"caret_offset": 2, "data": {"1": ("a", 1, 2), "2": ("b", 2, 3)}},
                "method_params": {},
                "expected": ("a", 1, 2),
            },
            {
                "id": "previous_character_with_offset",
                "direction": "previous",
                "unit_type": "character",
                "setup_params": {"data": {"0": ("a", 0, 1), "1": ("b", 1, 2)}},
                "method_params": {"offset": 1},
                "expected": ("a", 0, 1),
            },
            {
                "id": "previous_character_no_current",
                "direction": "previous",
                "unit_type": "character",
                "setup_params": {"caret_offset": 5, "data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_character_at_start",
                "direction": "previous",
                "unit_type": "character",
                "setup_params": {"caret_offset": 0, "data": {"0": ("a", 0, 1)}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_word_successful",
                "direction": "previous",
                "unit_type": "word",
                "setup_params": {
                    "caret_offset": 8,
                    "word_data": {"0-4": ("first", 0, 4), "5-11": ("second", 5, 11)},
                },
                "method_params": {},
                "expected": ("first", 0, 4),
            },
            {
                "id": "previous_word_with_offset",
                "direction": "previous",
                "unit_type": "word",
                "setup_params": {"word_data": {"0-4": ("first", 0, 4), "5-11": ("second", 5, 11)}},
                "method_params": {"offset": 8},
                "expected": ("first", 0, 4),
            },
            {
                "id": "previous_word_no_current",
                "direction": "previous",
                "unit_type": "word",
                "setup_params": {"caret_offset": 5, "word_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_word_at_start",
                "direction": "previous",
                "unit_type": "word",
                "setup_params": {"caret_offset": 0, "word_data": {"0-4": ("first", 0, 4)}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_line_successful",
                "direction": "previous",
                "unit_type": "line",
                "setup_params": {
                    "caret_offset": 15,
                    "line_data": {"0-10": ("First line", 0, 10), "11-20": ("Second line", 11, 20)},
                },
                "method_params": {},
                "expected": ("First line", 0, 10),
            },
            {
                "id": "previous_line_with_offset",
                "direction": "previous",
                "unit_type": "line",
                "setup_params": {
                    "line_data": {"0-10": ("First line", 0, 10), "11-20": ("Second line", 11, 20)}
                },
                "method_params": {"offset": 15},
                "expected": ("First line", 0, 10),
            },
            {
                "id": "previous_line_no_current",
                "direction": "previous",
                "unit_type": "line",
                "setup_params": {"caret_offset": 5, "count": 10, "line_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_line_at_start",
                "direction": "previous",
                "unit_type": "line",
                "setup_params": {"caret_offset": 0, "line_data": {"0-10": ("First line", 0, 10)}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_sentence_successful",
                "direction": "previous",
                "unit_type": "sentence",
                "setup_params": {
                    "caret_offset": 20,
                    "sentence_data": {
                        "0-15": ("First sentence.", 0, 15),
                        "16-30": ("Second sentence.", 16, 30),
                    },
                },
                "method_params": {},
                "expected": ("First sentence.", 0, 15),
            },
            {
                "id": "previous_sentence_with_offset",
                "direction": "previous",
                "unit_type": "sentence",
                "setup_params": {
                    "sentence_data": {
                        "0-15": ("First sentence.", 0, 15),
                        "16-30": ("Second sentence.", 16, 30),
                    }
                },
                "method_params": {"offset": 20},
                "expected": ("First sentence.", 0, 15),
            },
            {
                "id": "previous_sentence_no_current",
                "direction": "previous",
                "unit_type": "sentence",
                "setup_params": {"caret_offset": 5, "sentence_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_sentence_at_start",
                "direction": "previous",
                "unit_type": "sentence",
                "setup_params": {
                    "caret_offset": 0,
                    "sentence_data": {"0-15": ("First sentence.", 0, 15)},
                },
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_paragraph_successful",
                "direction": "previous",
                "unit_type": "paragraph",
                "setup_params": {
                    "caret_offset": 20,
                    "paragraph_data": {
                        "0-15": ("First paragraph.", 0, 15),
                        "16-30": ("Second paragraph.", 16, 30),
                    },
                },
                "method_params": {},
                "expected": ("First paragraph.", 0, 15),
            },
            {
                "id": "previous_paragraph_with_offset",
                "direction": "previous",
                "unit_type": "paragraph",
                "setup_params": {
                    "paragraph_data": {
                        "0-15": ("First paragraph.", 0, 15),
                        "16-30": ("Second paragraph.", 16, 30),
                    }
                },
                "method_params": {"offset": 20},
                "expected": ("First paragraph.", 0, 15),
            },
            {
                "id": "previous_paragraph_no_current",
                "direction": "previous",
                "unit_type": "paragraph",
                "setup_params": {"caret_offset": 5, "paragraph_data": {}},
                "method_params": {},
                "expected": ("", 0, 0),
            },
            {
                "id": "previous_paragraph_at_start",
                "direction": "previous",
                "unit_type": "paragraph",
                "setup_params": {
                    "caret_offset": 0,
                    "paragraph_data": {"0-15": ("First paragraph.", 0, 15)},
                },
                "method_params": {},
                "expected": ("", 0, 0),
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_next_text_unit_scenarios(  # pylint: disable=too-many-branches,too-many-statements
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXText.get_next_* and get_previous_* methods with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        setup_params = case["setup_params"]
        method_params = case["method_params"]
        direction = case["direction"]
        unit_type = case["unit_type"]
        expected = case["expected"]

        if "caret_offset" in setup_params:
            test_context.patch_object(
                AXText, "get_caret_offset", side_effect=lambda obj: setup_params["caret_offset"]
            )
        if "count" in setup_params:
            test_context.patch_object(
                AXText, "get_character_count", side_effect=lambda obj: setup_params["count"]
            )

        if unit_type == "character":

            def mock_get_character_at_offset(_obj, offset) -> tuple[str, int, int]:
                return setup_params["data"].get(str(offset), ("", 0, 0))

            test_context.patch_object(
                AXText, "get_character_at_offset", new=mock_get_character_at_offset
            )

            mock_obj = test_context.Mock(spec=Atspi.Accessible)
            if direction == "next":
                if method_params:
                    result = AXText.get_next_character(mock_obj, **method_params)
                else:
                    result = AXText.get_next_character(mock_obj)
            else:
                if method_params:
                    result = AXText.get_previous_character(mock_obj, **method_params)
                else:
                    result = AXText.get_previous_character(mock_obj)
        elif unit_type == "word":

            def mock_get_word_at_offset(_obj, offset) -> tuple[str, int, int]:
                for range_key, data in setup_params.get("word_data", {}).items():
                    if "-" in range_key:
                        start, end = map(int, range_key.split("-"))
                        if start <= offset <= end:
                            return data
                return ("", 0, 0)

            test_context.patch_object(AXText, "get_word_at_offset", new=mock_get_word_at_offset)

            mock_obj = test_context.Mock(spec=Atspi.Accessible)
            if direction == "next":
                if method_params:
                    result = AXText.get_next_word(mock_obj, **method_params)
                else:
                    result = AXText.get_next_word(mock_obj)
            else:
                if method_params:
                    result = AXText.get_previous_word(mock_obj, **method_params)
                else:
                    result = AXText.get_previous_word(mock_obj)
        elif unit_type == "line":

            def mock_get_line_at_offset(_obj, offset) -> tuple[str, int, int]:
                for range_key, data in setup_params.get("line_data", {}).items():
                    if "-" in range_key:
                        start, end = map(int, range_key.split("-"))
                        if start <= offset <= end:
                            return data
                return ("", 0, 0)

            test_context.patch_object(AXText, "get_line_at_offset", new=mock_get_line_at_offset)

            mock_obj = test_context.Mock(spec=Atspi.Accessible)
            if direction == "next":
                if method_params:
                    result = AXText.get_next_line(mock_obj, **method_params)
                else:
                    result = AXText.get_next_line(mock_obj)
            else:
                if method_params:
                    result = AXText.get_previous_line(mock_obj, **method_params)
                else:
                    result = AXText.get_previous_line(mock_obj)
        elif unit_type == "sentence":

            def mock_get_sentence_at_offset(_obj, offset) -> tuple[str, int, int]:
                for range_key, data in setup_params.get("sentence_data", {}).items():
                    if "-" in range_key:
                        start, end = map(int, range_key.split("-"))
                        if start <= offset <= end:
                            return data
                return ("", 0, 0)

            test_context.patch_object(
                AXText, "get_sentence_at_offset", new=mock_get_sentence_at_offset
            )

            mock_obj = test_context.Mock(spec=Atspi.Accessible)
            if direction == "next":
                if method_params:
                    result = AXText.get_next_sentence(mock_obj, **method_params)
                else:
                    result = AXText.get_next_sentence(mock_obj)
            else:
                if method_params:
                    result = AXText.get_previous_sentence(mock_obj, **method_params)
                else:
                    result = AXText.get_previous_sentence(mock_obj)
        elif unit_type == "paragraph":

            def mock_get_paragraph_at_offset(_obj, offset) -> tuple[str, int, int]:
                for range_key, data in setup_params.get("paragraph_data", {}).items():
                    if "-" in range_key:
                        start, end = map(int, range_key.split("-"))
                        if start <= offset <= end:
                            return data
                return ("", 0, 0)

            test_context.patch_object(
                AXText, "get_paragraph_at_offset", new=mock_get_paragraph_at_offset
            )

            mock_obj = test_context.Mock(spec=Atspi.Accessible)
            if direction == "next":
                if method_params:
                    result = AXText.get_next_paragraph(mock_obj, **method_params)
                else:
                    result = AXText.get_next_paragraph(mock_obj)
            else:
                if method_params:
                    result = AXText.get_previous_paragraph(mock_obj, **method_params)
                else:
                    result = AXText.get_previous_paragraph(mock_obj)
        else:
            result = ("", 0, 0)

        assert result == expected

    def test_get_character_at_offset_with_empty_text(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_character_at_offset when text is empty."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        test_context.patch(
            "gi.repository.Atspi.Text.get_character_count", return_value=0
        )
        result = AXText.get_character_at_offset(test_context.Mock(spec=Atspi.Accessible), 0)
        assert result == ("", 0, 0)

    def test_get_character_at_offset_with_none_offset(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_character_at_offset when offset is None."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "gi.repository.Atspi.Text.get_character_count", return_value=10
        )
        test_context.patch_object(AXText, "get_caret_offset", return_value=5)

        mock_result = test_context.Mock()
        mock_result.content = "a"
        mock_result.start_offset = 5
        mock_result.end_offset = 6
        test_context.patch(
            "gi.repository.Atspi.Text.get_string_at_offset",
            side_effect=lambda obj, offset, granularity: mock_result,
        )

        result = AXText.get_character_at_offset(mock_obj, None)
        assert result == ("a", 5, 6)

    def test_get_character_at_offset_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXText.get_character_at_offset when GLib.GError occurs."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        def raise_glib_error(_obj, _offset, _granularity):
            raise GLib.GError("Test error")

        test_context.patch(
            "gi.repository.Atspi.Text.get_character_count", return_value=10
        )
        test_context.patch(
            "gi.repository.Atspi.Text.get_string_at_offset", new=raise_glib_error
        )

        result = AXText.get_character_at_offset(test_context.Mock(spec=Atspi.Accessible), 5)
        assert result == ("", 0, 0)

    def test_get_previous_line_at_end_with_newline_sets_correct_start(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.get_previous_line sets start when fallback line ends with newline."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        # Mock get_character_count to return 12 (end of text)
        test_context.patch_object(AXText, "get_character_count", return_value=12)

        # Mock get_line_at_offset for the sequence
        def mock_get_line_at_offset(_obj, offset):
            if offset == 12:  # At end of text - empty line
                return ("", 12, 12)
            if offset == 11:  # One character back - line ending with newline
                return ("Hello World\n", 0, 12)
            if offset == 10:  # Previous line search from (offset-1)-1 = 10
                return ("Previous Line", 0, 11)
            return ("", 0, 0)

        test_context.patch_object(AXText, "get_line_at_offset", new=mock_get_line_at_offset)

        # Test: when at end with empty line and fallback has newline
        result = AXText.get_previous_line(mock_obj, 12)

        # The current line becomes "Hello World\n" with start=11
        assert result == ("Previous Line", 0, 11)

    def test_get_previous_line_at_end_of_text_fallback_to_normal_behavior(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.get_previous_line at end when fallback doesn't end with newline."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        # Mock get_character_count to return 11 (end of text)
        test_context.patch_object(AXText, "get_character_count", return_value=11)

        # Mock get_line_at_offset scenarios
        def mock_get_line_at_offset(_obj, offset):
            if offset == 11:  # At end of text
                return ("", 11, 11)
            if offset == 10:  # One character back - no newline
                return ("Hello World", 5, 15)  # start > 0 so it continues
            if offset == 4:  # Previous line lookup from start-1 = 4
                return ("Previous Line", 0, 5)
            return ("", 0, 0)

        test_context.patch_object(AXText, "get_line_at_offset", new=mock_get_line_at_offset)

        # Test: should use normal behavior when fallback line doesn't end with newline
        result = AXText.get_previous_line(mock_obj, 11)
        assert result == ("Previous Line", 0, 5)

    def test_get_previous_line_empty_current_line_returns_empty(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXText.get_previous_line returns empty when current_line is empty."""

        self._setup_dependencies(test_context)
        from orca.ax_text import AXText

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        # Mock get_character_count to return 5 (not at end)
        test_context.patch_object(AXText, "get_character_count", return_value=5)

        # Mock get_line_at_offset to return empty line not at end of text
        def mock_get_line_at_offset(_obj, _offset):
            return ("", 3, 3)

        test_context.patch_object(AXText, "get_line_at_offset", new=mock_get_line_at_offset)

        # Test: when current_line is empty (and not at end), should return empty
        result = AXText.get_previous_line(mock_obj, 3)
        assert result == ("", 0, 0)
