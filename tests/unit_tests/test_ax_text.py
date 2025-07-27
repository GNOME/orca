# Unit tests for ax_text.py text-related methods.
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
# pylint: disable=unused-argument
# pylint: disable=too-many-lines

"""Unit tests for ax_text.py text-related methods."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache  # pylint: disable=import-error

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib


@pytest.mark.unit
class TestAXTextAttribute:
    """Test AXTextAttribute enum methods."""

    def test_from_string_with_valid_attribute(self, monkeypatch, mock_orca_dependencies):
        """Test AXTextAttribute.from_string with valid attribute name."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_string("bg-color")
        assert result == AXTextAttribute.BG_COLOR

    def test_from_string_with_invalid_attribute(self, monkeypatch, mock_orca_dependencies):
        """Test AXTextAttribute.from_string with invalid attribute name."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_string("invalid-attribute")
        assert result is None

    def test_from_localized_string_with_valid_attribute(self, monkeypatch, mock_orca_dependencies):
        """Test AXTextAttribute.from_localized_string with valid localized name."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_localized_string("Background Color")
        assert result == AXTextAttribute.BG_COLOR

    def test_from_localized_string_with_invalid_attribute(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXTextAttribute.from_localized_string with invalid localized name."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.from_localized_string("Invalid Localized")
        assert result is None

    def test_get_attribute_name(self, monkeypatch, mock_orca_dependencies):
        """Test AXTextAttribute.get_attribute_name."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.BG_COLOR.get_attribute_name()
        assert result == "bg-color"

    def test_get_localized_name_with_translation(self, monkeypatch, mock_orca_dependencies):
        """Test AXTextAttribute.get_localized_name with translation available."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.BG_COLOR.get_localized_name()
        assert result == "Background Color"

    def test_get_localized_name_without_translation(self, monkeypatch, mock_orca_dependencies):
        """Test AXTextAttribute.get_localized_name without translation available."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        result = AXTextAttribute.SIZE.get_localized_name()
        assert result == "size"

    @pytest.mark.parametrize(
        "attribute, value, expected",
        [
            pytest.param("BG_COLOR", "5px", "5 pixels", id="pixel_value_int"),
            pytest.param("BG_COLOR", "5.5px", "5 pixels", id="pixel_value_float"),
            pytest.param("BG_COLOR", "#ff0000", "red", id="color_value_with_color_names"),
            pytest.param("SIZE", "bold-moz", "Bold", id="moz_prefix_removal"),
            pytest.param("JUSTIFICATION", "justify", "fill", id="justify_to_fill_replacement"),
            pytest.param("FAMILY_NAME", '"Arial", sans-serif', "Arial", id="family_name_cleanup"),
            pytest.param("SIZE", "normal", "normal", id="regular_value"),
            pytest.param("SIZE", None, "", id="none_value"),
        ],
    )
    def test_get_localized_value(
        self, monkeypatch, attribute, value, expected, mock_orca_dependencies
    ):
        """Test AXTextAttribute.get_localized_value."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        attr = getattr(AXTextAttribute, attribute)
        result = attr.get_localized_value(value)
        assert result == expected

    @pytest.mark.parametrize(
        "attribute, expected",
        [
            pytest.param("BG_COLOR", True, id="default_true"),
            pytest.param("BG_FULL_HEIGHT", False, id="default_false"),
        ],
    )
    def test_should_present_by_default(
        self, monkeypatch, attribute, expected, mock_orca_dependencies
    ):
        """Test AXTextAttribute.should_present_by_default."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        attr = getattr(AXTextAttribute, attribute)
        result = attr.should_present_by_default()
        assert result is expected

    @pytest.mark.parametrize(
        "attribute, value, expected",
        [
            pytest.param("SIZE", "0", True, id="zero_string"),
            pytest.param("SIZE", "0px", True, id="zero_pixels"),
            pytest.param("SIZE", "none", True, id="none_string"),
            pytest.param("SIZE", "", True, id="empty_string"),
            pytest.param("SIZE", None, True, id="none_value"),
            pytest.param("SCALE", "1.0", True, id="scale_default"),
            pytest.param("TEXT_POSITION", "baseline", True, id="text_position_default"),
            pytest.param("WEIGHT", "400", True, id="weight_default"),
            pytest.param("SIZE", "12px", False, id="non_default_value"),
        ],
    )
    def test_value_is_default(
        self, monkeypatch, attribute, value, expected, mock_orca_dependencies
    ):
        """Test AXTextAttribute.value_is_default."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        attr = getattr(AXTextAttribute, attribute)
        result = attr.value_is_default(value)
        assert result is expected


@pytest.mark.unit
class TestAXText:
    """Test AXText utility methods."""

    @pytest.fixture
    def mock_accessible(self):
        """Create a mock Atspi.Accessible object."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_obj.hash = Mock(return_value=12345)
        return mock_obj

    def test_get_character_at_offset_with_valid_offset(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_at_offset with valid offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def mock_get_string_at_offset(obj, offset, granularity):
            result = Mock()
            result.content = "a"
            result.start_offset = 5
            result.end_offset = 6
            return result

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 10)
        monkeypatch.setattr(Atspi.Text, "get_caret_offset", lambda obj: 5)
        monkeypatch.setattr(Atspi.Text, "get_string_at_offset", mock_get_string_at_offset)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText.get_character_at_offset(mock_accessible, 5)
        assert result == ("a", 5, 6)
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_character_at_offset_with_no_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_at_offset with no text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 0)

        result = AXText.get_character_at_offset(mock_accessible)
        assert result == ("", 0, 0)

    def test_get_character_at_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_at_offset handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def raise_glib_error(obj, offset, granularity):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 10)
        monkeypatch.setattr(Atspi.Text, "get_caret_offset", lambda obj: 5)
        monkeypatch.setattr(Atspi.Text, "get_string_at_offset", raise_glib_error)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText.get_character_at_offset(mock_accessible, 5)
        assert result == ("", 0, 0)
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_character_count_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_count successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(Atspi.Text, "get_character_count", lambda obj: 100)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText.get_character_count(mock_accessible)
        assert result == 100
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_character_count_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_count handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Text, "get_character_count", raise_glib_error)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText.get_character_count(mock_accessible)
        assert result == 0
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_substring_successful(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXText.get_substring successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(Atspi.Text, "get_text", lambda obj, start, end: "substring")
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText.get_substring(mock_accessible, 5, 15)
        assert result == "substring"
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_substring_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_substring handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def raise_glib_error(obj, start, end):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Text, "get_text", raise_glib_error)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText.get_substring(mock_accessible, 5, 15)
        assert result == ""
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_all_supported_text_attributes(self, monkeypatch, mock_orca_dependencies):
        """Test AXText.get_all_supported_text_attributes."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText, AXTextAttribute

        result = AXText.get_all_supported_text_attributes()
        assert isinstance(result, list)
        assert AXTextAttribute.BG_COLOR in result
        assert AXTextAttribute.SIZE in result

    def test_is_eoc_with_embedded_object_character(self, monkeypatch, mock_orca_dependencies):
        """Test AXText.is_eoc with embedded object character."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        result = AXText.is_eoc("\ufffc")
        assert result is True

    def test_is_eoc_with_regular_character(self, monkeypatch, mock_orca_dependencies):
        """Test AXText.is_eoc with regular character."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        result = AXText.is_eoc("a")
        assert result is False

    def test_character_at_offset_is_eoc_with_eoc(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.character_at_offset_is_eoc with embedded object character."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_at_offset", lambda obj, offset: ("\ufffc", 5, 6))

        result = AXText.character_at_offset_is_eoc(mock_accessible, 5)
        assert result is True

    def test_character_at_offset_is_eoc_without_eoc(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.character_at_offset_is_eoc without embedded object character."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_at_offset", lambda obj, offset: ("a", 5, 6))

        result = AXText.character_at_offset_is_eoc(mock_accessible, 5)
        assert result is False

    def test_is_whitespace_or_empty_with_whitespace(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.is_whitespace_or_empty with whitespace text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_all_text", lambda obj: "   \t\n  ")

        result = AXText.is_whitespace_or_empty(mock_accessible)
        assert result is True

    def test_is_whitespace_or_empty_with_content(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.is_whitespace_or_empty with actual content."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_all_text", lambda obj: "Hello world")

        result = AXText.is_whitespace_or_empty(mock_accessible)
        assert result is False

    def test_has_presentable_text_with_word_characters(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.has_presentable_text with word characters."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_all_text", lambda obj: "Hello123")

        result = AXText.has_presentable_text(mock_accessible)
        assert result is True

    def test_has_presentable_text_without_word_characters(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.has_presentable_text without word characters."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_all_text", lambda obj: "!@#$%^&*()")

        result = AXText.has_presentable_text(mock_accessible)
        assert result is False

    def test_get_caret_offset_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_caret_offset successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(Atspi.Text, "get_caret_offset", lambda obj: 50)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText.get_caret_offset(mock_accessible)
        assert result == 50
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_caret_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_caret_offset handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Text, "get_caret_offset", raise_glib_error)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText.get_caret_offset(mock_accessible)
        assert result == -1
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_set_caret_offset_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.set_caret_offset successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(Atspi.Text, "set_caret_offset", lambda obj, offset: True)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText.set_caret_offset(mock_accessible, 25)
        assert result is True
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_set_caret_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.set_caret_offset handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def raise_glib_error(obj, offset):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Text, "set_caret_offset", raise_glib_error)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText.set_caret_offset(mock_accessible, 25)
        assert result is False
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_set_caret_offset_to_start(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXText.set_caret_offset_to_start."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "set_caret_offset", lambda obj, offset: True)

        result = AXText.set_caret_offset_to_start(mock_accessible)
        assert result is True

    def test_set_caret_offset_to_end(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXText.set_caret_offset_to_end."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 100)
        monkeypatch.setattr(AXText, "set_caret_offset", lambda obj, offset: True)

        result = AXText.set_caret_offset_to_end(mock_accessible)
        assert result is True

    def test_get_offset_at_point_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_offset_at_point successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(Atspi.Text, "get_offset_at_point", lambda obj, x, y, coord_type: 25)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText.get_offset_at_point(mock_accessible, 100, 200)
        assert result == 25
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_offset_at_point_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_offset_at_point handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def raise_glib_error(obj, x, y, coord_type):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Text, "get_offset_at_point", raise_glib_error)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText.get_offset_at_point(mock_accessible, 100, 200)
        assert result == -1
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_has_selected_text_without_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.has_selected_text without text selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "_get_n_selections", lambda obj: 0)

        result = AXText.has_selected_text(mock_accessible)
        assert result is False

    def test_get_n_selections_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._get_n_selections successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(Atspi.Text, "get_n_selections", lambda obj: 2)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText._get_n_selections(mock_accessible)
        assert result == 2
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_n_selections_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._get_n_selections handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Text, "get_n_selections", raise_glib_error)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText._get_n_selections(mock_accessible)
        assert result == 0
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_cached_selected_text_without_cache(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_cached_selected_text without cached data."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        mock_accessible.hash = Mock(return_value=54321)
        AXText.CACHED_TEXT_SELECTION.clear()

        result = AXText.get_cached_selected_text(mock_accessible)
        assert result == ("", 0, 0)

    @pytest.mark.parametrize(
        "rect1, rect2, expected",
        [
            pytest.param(
                Mock(x=10, y=10, width=20, height=20),
                Mock(x=5, y=5, width=30, height=30),
                True,
                id="fully_contained",
            ),
            pytest.param(
                Mock(x=0, y=0, width=20, height=20),
                Mock(x=5, y=5, width=10, height=10),
                False,
                id="not_contained",
            ),
            pytest.param(
                Mock(x=10, y=10, width=20, height=20),
                Mock(x=10, y=10, width=20, height=20),
                True,
                id="exactly_same",
            ),
        ],
    )
    def test_rect_is_fully_contained_in(
        self, monkeypatch, rect1, rect2, expected, mock_orca_dependencies
    ):
        """Test AXText._rect_is_fully_contained_in."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        result = AXText._rect_is_fully_contained_in(rect1, rect2)
        assert result is expected

    @pytest.mark.parametrize(
        "line_rect, clip_rect, expected",
        [
            pytest.param(Mock(y=10, height=10), Mock(y=5, height=30), 0, id="line_inside_clip"),
            pytest.param(Mock(y=0, height=10), Mock(y=15, height=20), -1, id="line_above_clip"),
            pytest.param(Mock(y=40, height=10), Mock(y=5, height=20), 1, id="line_below_clip"),
        ],
    )
    def test_line_comparison(
        self, monkeypatch, line_rect, clip_rect, expected, mock_orca_dependencies
    ):
        """Test AXText._line_comparison."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        result = AXText._line_comparison(line_rect, clip_rect)
        assert result == expected

    def test_get_word_at_offset_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_word_at_offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        mock_result = Mock()
        mock_result.content = "hello"
        mock_result.start_offset = 5
        mock_result.end_offset = 10
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset",
            lambda obj, offset, granularity: mock_result,
        )

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        result = AXText.get_word_at_offset(mock_accessible)
        assert result == ("hello", 5, 10)

    def test_get_word_at_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_word_at_offset handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        def mock_get_string_at_offset(obj, offset, granularity):
            raise GLib.GError("Test error")

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset", mock_get_string_at_offset
        )

        result = AXText.get_word_at_offset(mock_accessible)
        assert result == ("", 0, 0)


    def test_get_all_text_successful(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXText.get_all_text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_text", lambda obj, start, end: "This is some test text"
        )

        result = AXText.get_all_text(mock_accessible)
        assert result == "This is some test text"

    def test_get_all_text_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_all_text handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)

        def mock_get_text(obj, start, end):
            raise GLib.GError("Test error")

        monkeypatch.setattr("gi.repository.Atspi.Text.get_text", mock_get_text)

        result = AXText.get_all_text(mock_accessible)
        assert result == ""

    def test_get_selected_text_with_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selected_text with text selected."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [(5, 10), (15, 20)])
        monkeypatch.setattr(AXText, "get_substring", lambda obj, start, end: f"text{start}-{end}")

        result = AXText.get_selected_text(mock_accessible)
        assert result == ("text5-10 text15-20", 5, 20)

    def test_get_selected_text_without_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selected_text without text selected."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [])

        result = AXText.get_selected_text(mock_accessible)
        assert result == ("", 0, 0)

    def test_get_text_attributes_at_offset_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_text_attributes_at_offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 5)

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset=None: ({"font-family": "Arial", "font-size": "12pt"}, 0, 10),
        )

        result = AXText.get_text_attributes_at_offset(mock_accessible)
        assert result == ({"font-family": "Arial", "font-size": "12pt"}, 0, 10)

    def test_get_text_attributes_at_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_text_attributes_at_offset handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 5)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)

        def mock_get_attribute_run(obj, offset, include_defaults=True):
            raise GLib.GError("Test error")

        monkeypatch.setattr("gi.repository.Atspi.Text.get_attribute_run", mock_get_attribute_run)

        result = AXText.get_text_attributes_at_offset(mock_accessible)
        assert result == ({}, 0, 20)

    def test_get_all_text_attributes_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_all_text_attributes."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)

        def mock_get_text_attributes_at_offset(obj, offset):
            if offset < 10:
                return ({"font-weight": "bold"}, 0, 10)
            return ({"font-style": "italic"}, 10, 20)

        monkeypatch.setattr(
            AXText, "get_text_attributes_at_offset", mock_get_text_attributes_at_offset
        )

        result = AXText.get_all_text_attributes(mock_accessible)
        assert len(result) == 2
        assert result[0] == (0, 10, {"font-weight": "bold"})
        assert result[1] == (10, 20, {"font-style": "italic"})

    def test_supports_sentence_iteration_true(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.supports_sentence_iteration returns True."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText, "get_sentence_at_offset", lambda obj, offset: ("This is a sentence.", 0, 19)
        )

        result = AXText.supports_sentence_iteration(mock_accessible)
        assert result is True

    def test_supports_paragraph_iteration_true(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.supports_paragraph_iteration returns True."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText, "get_paragraph_at_offset", lambda obj, offset: ("This is a paragraph.", 0, 20)
        )

        result = AXText.supports_paragraph_iteration(mock_accessible)
        assert result is True

    def test_iter_character_with_valid_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.iter_character with valid text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 0)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 3)

        def mock_get_character_at_offset(obj, offset):
            chars = [("a", 0, 1), ("b", 1, 2), ("c", 2, 3)]
            if 0 <= offset < 3:
                return chars[offset]
            return ("", 0, 0)

        monkeypatch.setattr(AXText, "get_character_at_offset", mock_get_character_at_offset)

        result = list(AXText.iter_character(mock_accessible))
        assert result == [("a", 0, 1), ("b", 1, 2), ("c", 2, 3)]

    def test_iter_character_with_empty_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.iter_character with empty text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 0)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 0)

        result = list(AXText.iter_character(mock_accessible))
        assert not result

    def test_iter_word_with_valid_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.iter_word with valid text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 0)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 11)

        def mock_get_word_at_offset(obj, offset):
            if 0 <= offset < 5:
                return ("hello", 0, 5)
            if 5 <= offset < 11:
                return (" world", 5, 11)
            return ("", 0, 0)

        monkeypatch.setattr(AXText, "get_word_at_offset", mock_get_word_at_offset)

        result = list(AXText.iter_word(mock_accessible))
        assert result == [("hello", 0, 5), (" world", 5, 11)]

    def test_iter_line_with_valid_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.iter_line with valid text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 0)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)

        def mock_get_line_at_offset(obj, offset):
            if 0 <= offset < 10:
                return ("First line", 0, 10)
            if 10 <= offset < 20:
                return ("Second line", 10, 20)
            return ("", 0, 0)

        monkeypatch.setattr(AXText, "get_line_at_offset", mock_get_line_at_offset)

        result = list(AXText.iter_line(mock_accessible))
        assert result == [("First line", 0, 10), ("Second line", 10, 20)]

    def test_iter_sentence_with_valid_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.iter_sentence with valid text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 0)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)

        def mock_get_sentence_at_offset(obj, offset):
            if 0 <= offset < 12:
                return ("First sentence.", 0, 12)
            if 12 <= offset < 25:
                return ("Second sentence.", 12, 25)
            return ("", 0, 0)

        monkeypatch.setattr(AXText, "get_sentence_at_offset", mock_get_sentence_at_offset)

        result = list(AXText.iter_sentence(mock_accessible))
        assert result == [("First sentence.", 0, 12), ("Second sentence.", 12, 25)]

    def test_iter_paragraph_with_valid_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.iter_paragraph with valid text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 0)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 30)

        def mock_get_paragraph_at_offset(obj, offset):
            if 0 <= offset < 15:
                return ("First paragraph.", 0, 15)
            if 15 <= offset < 30:
                return ("Second paragraph.", 15, 30)
            return ("", 0, 0)

        monkeypatch.setattr(AXText, "get_paragraph_at_offset", mock_get_paragraph_at_offset)

        result = list(AXText.iter_paragraph(mock_accessible))
        assert result == [("First paragraph.", 0, 15), ("Second paragraph.", 15, 30)]

    def test_get_character_at_point(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_at_point."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_offset_at_point", lambda obj, x, y: 5)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 10)
        monkeypatch.setattr(AXText, "get_character_at_offset", lambda obj, offset: ("a", 5, 6))

        result = AXText.get_character_at_point(mock_accessible, 100, 200)
        assert result == ("a", 5, 6)

    def test_get_character_at_point_invalid_offset(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_at_point with invalid offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_offset_at_point", lambda obj, x, y: -1)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 10)

        result = AXText.get_character_at_point(mock_accessible, 100, 200)
        assert result == ("", 0, 0)

    def test_get_word_at_point(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_word_at_point."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_offset_at_point", lambda obj, x, y: 5)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 10)
        monkeypatch.setattr(AXText, "get_word_at_offset", lambda obj, offset: ("hello", 3, 8))

        result = AXText.get_word_at_point(mock_accessible, 100, 200)
        assert result == ("hello", 3, 8)

    def test_get_line_at_point(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_line_at_point."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_offset_at_point", lambda obj, x, y: 5)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(
            AXText, "get_line_at_offset", lambda obj, offset: ("This is a line", 0, 14)
        )

        result = AXText.get_line_at_point(mock_accessible, 100, 200)
        assert result == ("This is a line", 0, 14)

    def test_get_sentence_at_point(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_sentence_at_point."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_offset_at_point", lambda obj, x, y: 5)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(
            AXText, "get_sentence_at_offset", lambda obj, offset: ("This is a sentence.", 0, 19)
        )

        result = AXText.get_sentence_at_point(mock_accessible, 100, 200)
        assert result == ("This is a sentence.", 0, 19)

    def test_get_paragraph_at_point(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_paragraph_at_point."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_offset_at_point", lambda obj, x, y: 5)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)
        monkeypatch.setattr(
            AXText, "get_paragraph_at_offset", lambda obj, offset: ("This is a paragraph.", 0, 20)
        )

        result = AXText.get_paragraph_at_point(mock_accessible, 100, 200)
        assert result == ("This is a paragraph.", 0, 20)

    def test_string_has_spelling_error_with_invalid_spelling(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.string_has_spelling_error with spelling error."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset: ({"invalid": "spelling"}, 0, 10),
        )

        result = AXText.string_has_spelling_error(mock_accessible, 5)
        assert result is True

    def test_string_has_spelling_error_with_text_spelling(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.string_has_spelling_error with text-spelling misspelled."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset: ({"text-spelling": "misspelled"}, 0, 10),
        )

        result = AXText.string_has_spelling_error(mock_accessible, 5)
        assert result is True

    def test_string_has_spelling_error_with_underline_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.string_has_spelling_error with underline error."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset: ({"underline": "spelling"}, 0, 10),
        )

        result = AXText.string_has_spelling_error(mock_accessible, 5)
        assert result is True

    def test_string_has_spelling_error_without_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.string_has_spelling_error without spelling error."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset: ({"font-size": "12pt"}, 0, 10),
        )

        result = AXText.string_has_spelling_error(mock_accessible, 5)
        assert result is False

    def test_string_has_grammar_error_with_invalid_grammar(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.string_has_grammar_error with grammar error."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset: ({"invalid": "grammar"}, 0, 10),
        )

        result = AXText.string_has_grammar_error(mock_accessible, 5)
        assert result is True

    def test_string_has_grammar_error_with_underline_grammar(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.string_has_grammar_error with underline grammar."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset: ({"underline": "grammar"}, 0, 10),
        )

        result = AXText.string_has_grammar_error(mock_accessible, 5)
        assert result is True

    def test_string_has_grammar_error_without_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.string_has_grammar_error without grammar error."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText,
            "get_text_attributes_at_offset",
            lambda obj, offset: ({"font-size": "12pt"}, 0, 10),
        )

        result = AXText.string_has_grammar_error(mock_accessible, 5)
        assert result is False

    def test_get_selection_start_offset_with_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selection_start_offset with selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [(5, 10), (15, 20)])

        result = AXText.get_selection_start_offset(mock_accessible)
        assert result == 5

    def test_get_selection_start_offset_without_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selection_start_offset without selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [])

        result = AXText.get_selection_start_offset(mock_accessible)
        assert result == -1

    def test_get_selection_end_offset_with_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selection_end_offset with selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [(5, 10), (15, 20)])

        result = AXText.get_selection_end_offset(mock_accessible)
        assert result == 20

    def test_get_selection_end_offset_without_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selection_end_offset without selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [])

        result = AXText.get_selection_end_offset(mock_accessible)
        assert result == -1

    def test_is_all_text_selected_with_full_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.is_all_text_selected with full text selected."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [(0, 20)])

        result = AXText.is_all_text_selected(mock_accessible)
        assert result is True

    def test_is_all_text_selected_with_partial_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.is_all_text_selected with partial selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [(5, 15)])

        result = AXText.is_all_text_selected(mock_accessible)
        assert result is False

    def test_is_all_text_selected_without_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.is_all_text_selected without selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_selected_ranges", lambda obj: [])

        result = AXText.is_all_text_selected(mock_accessible)
        assert result is False

    def test_clear_all_selected_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.clear_all_selected_text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        removed_selections = []
        def mock_remove_selection(obj, selection_number):
            removed_selections.append(selection_number)

        monkeypatch.setattr(AXText, "_get_n_selections", lambda obj: 3)
        monkeypatch.setattr(AXText, "_remove_selection", mock_remove_selection)

        AXText.clear_all_selected_text(mock_accessible)
        assert removed_selections == [0, 1, 2]

    def test_remove_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._remove_selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)

        mock_remove_selection = Mock()
        monkeypatch.setattr("gi.repository.Atspi.Text.remove_selection", mock_remove_selection)

        AXText._remove_selection(mock_accessible, 0)
        mock_remove_selection.assert_called_once_with(mock_accessible, 0)

    def test_remove_selection_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._remove_selection handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)

        def mock_remove_selection(obj, selection_number):
            raise GLib.GError("Test error")

        monkeypatch.setattr("gi.repository.Atspi.Text.remove_selection", mock_remove_selection)

        # Should not raise exception
        AXText._remove_selection(mock_accessible, 0)

    def test_get_selected_ranges_with_valid_selections(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selected_ranges with valid selections."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "_get_n_selections", lambda obj: 2)

        def mock_get_selection(obj, selection_num):
            results = [
                Mock(start_offset=5, end_offset=10),
                Mock(start_offset=15, end_offset=20)
            ]
            return results[selection_num]

        monkeypatch.setattr("gi.repository.Atspi.Text.get_selection", mock_get_selection)

        result = AXText.get_selected_ranges(mock_accessible)
        assert result == [(5, 10), (15, 20)]

    def test_get_selected_ranges_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_selected_ranges handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "_get_n_selections", lambda obj: 1)

        def mock_get_selection(obj, selection_num):
            raise GLib.GError("Test error")

        monkeypatch.setattr("gi.repository.Atspi.Text.get_selection", mock_get_selection)

        result = AXText.get_selected_ranges(mock_accessible)
        assert not result

    def test_add_new_selection_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._add_new_selection successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr("gi.repository.Atspi.Text.add_selection", lambda obj, start, end: True)

        result = AXText._add_new_selection(mock_accessible, 5, 10)
        assert result is True

    def test_add_new_selection_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._add_new_selection handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)

        def mock_add_selection(obj, start, end):
            raise GLib.GError("Test error")

        monkeypatch.setattr("gi.repository.Atspi.Text.add_selection", mock_add_selection)

        result = AXText._add_new_selection(mock_accessible, 5, 10)
        assert result is False

    def test_update_existing_selection_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._update_existing_selection successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.set_selection", lambda obj, num, start, end: True
        )

        result = AXText._update_existing_selection(mock_accessible, 5, 10, 0)
        assert result is True

    def test_update_existing_selection_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText._update_existing_selection handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)

        def mock_set_selection(obj, num, start, end):
            raise GLib.GError("Test error")

        monkeypatch.setattr("gi.repository.Atspi.Text.set_selection", mock_set_selection)

        result = AXText._update_existing_selection(mock_accessible, 5, 10, 0)
        assert result is False

    def test_set_selected_text_with_existing_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.set_selected_text with existing selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "_get_n_selections", lambda obj: 1)
        monkeypatch.setattr(AXText, "_update_existing_selection", lambda obj, start, end: True)
        monkeypatch.setattr(AXText, "get_substring", lambda obj, start, end: "test")
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("test", 5, 10))
        monkeypatch.setattr(mock_orca_dependencies["debug"], "debugLevel", 0)

        result = AXText.set_selected_text(mock_accessible, 5, 10)
        assert result is True

    def test_set_selected_text_with_new_selection(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.set_selected_text with new selection."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "_get_n_selections", lambda obj: 0)
        monkeypatch.setattr(AXText, "_add_new_selection", lambda obj, start, end: True)
        monkeypatch.setattr(AXText, "get_substring", lambda obj, start, end: "test")
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("test", 5, 10))
        monkeypatch.setattr(mock_orca_dependencies["debug"], "debugLevel", 0)

        result = AXText.set_selected_text(mock_accessible, 5, 10)
        assert result is True

    def test_update_cached_selected_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.update_cached_selected_text."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("cached text", 5, 15))

        AXText.CACHED_TEXT_SELECTION.clear()

        AXText.update_cached_selected_text(mock_accessible)
        assert hash(mock_accessible) in AXText.CACHED_TEXT_SELECTION
        assert AXText.CACHED_TEXT_SELECTION[hash(mock_accessible)] == ("cached text", 5, 15)

    def test_get_character_rect_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_rect successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 5)

        mock_rect = Mock(x=10, y=20, width=5, height=12)
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_character_extents",
            lambda obj, offset, coord_type: mock_rect
        )

        result = AXText.get_character_rect(mock_accessible, 5)
        assert result == mock_rect

    def test_get_character_rect_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_rect handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 5)

        def mock_get_character_extents(obj, offset, coord_type):
            raise GLib.GError("Test error")

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_character_extents", mock_get_character_extents
        )

        result = AXText.get_character_rect(mock_accessible, 5)
        assert result.x == 0 and result.y == 0

    def test_get_range_rect_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_range_rect successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        mock_rect = Mock(x=10, y=20, width=50, height=12)
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_range_extents",
            lambda obj, start, end, coord_type: mock_rect
        )

        result = AXText.get_range_rect(mock_accessible, 5, 15)
        assert result == mock_rect

    def test_get_range_rect_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_range_rect handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)

        def mock_get_range_extents(obj, start, end, coord_type):
            raise GLib.GError("Test error")

        monkeypatch.setattr("gi.repository.Atspi.Text.get_range_extents", mock_get_range_extents)

        result = AXText.get_range_rect(mock_accessible, 5, 15)
        assert result.x == 0 and result.y == 0

    def test_scroll_substring_to_point_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.scroll_substring_to_point successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.scroll_substring_to_point",
            lambda obj, start, end, coord_type, x, y: True
        )

        result = AXText.scroll_substring_to_point(mock_accessible, 100, 200, 5, 15)
        assert result is True

    def test_scroll_substring_to_point_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.scroll_substring_to_point handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)

        def mock_scroll_substring_to_point(obj, start, end, coord_type, x, y):
            raise GLib.GError("Test error")

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.scroll_substring_to_point", mock_scroll_substring_to_point
        )

        result = AXText.scroll_substring_to_point(mock_accessible, 100, 200, 5, 15)
        assert result is False

    def test_scroll_substring_to_location_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.scroll_substring_to_location successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        mock_scroll_type = Mock()
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.scroll_substring_to",
            lambda obj, start, end, location: True
        )

        result = AXText.scroll_substring_to_location(mock_accessible, mock_scroll_type, 5, 15)
        assert result is True

    def test_scroll_substring_to_location_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.scroll_substring_to_location handles GLib.GError."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)

        def mock_scroll_substring_to(obj, start, end, location):
            raise GLib.GError("Test error")

        mock_scroll_type = Mock()
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.scroll_substring_to", mock_scroll_substring_to
        )

        result = AXText.scroll_substring_to_location(mock_accessible, mock_scroll_type, 5, 15)
        assert result is False

    def test_get_visible_lines(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_visible_lines."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        clip_rect = Mock(x=0, y=0, width=100, height=50)
        monkeypatch.setattr(
            AXText, "find_first_visible_line", lambda obj, rect: ("First line", 0, 10)
        )

        def mock_iter_line(obj, offset):
            lines = [("Second line", 10, 20), ("Third line", 20, 30)]
            yield from lines

        monkeypatch.setattr(AXText, "iter_line", mock_iter_line)

        monkeypatch.setattr(
            AXText, "get_range_rect", lambda obj, start, end: Mock(x=0, y=10, width=50, height=10)
        )
        monkeypatch.setattr(AXText, "_line_comparison", lambda line_rect, clip_rect: 0)

        result = AXText.get_visible_lines(mock_accessible, clip_rect)
        assert len(result) >= 1
        assert result[0] == ("First line", 0, 10)

    def test_find_first_visible_line_at_start(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.find_first_visible_line when first line is at start."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        clip_rect = Mock(x=0, y=0, width=100, height=50)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 100)

        monkeypatch.setattr(
            AXText, "get_line_at_offset", lambda obj, offset: ("First line", 0, 10)
        )

        result = AXText.find_first_visible_line(mock_accessible, clip_rect)
        assert result == ("First line", 0, 10)

    def test_find_last_visible_line_at_end(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.find_last_visible_line when last line is at end."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        clip_rect = Mock(x=0, y=0, width=100, height=50)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 100)

        monkeypatch.setattr(
            AXText, "get_line_at_offset", lambda obj, offset: ("Last line", 90, 100)
        )

        result = AXText.find_last_visible_line(mock_accessible, clip_rect)
        assert result == ("Last line", 90, 100)

    def test_get_line_at_offset_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_line_at_offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        mock_result = Mock()
        mock_result.content = "This is a line"
        mock_result.start_offset = 0
        mock_result.end_offset = 14
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset",
            lambda obj, offset, granularity: mock_result,
        )

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        result = AXText.get_line_at_offset(mock_accessible)
        assert result == ("This is a line", 0, 14)

    def test_get_line_at_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_line_at_offset handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        def mock_get_string_at_offset(obj, offset, granularity):
            raise GLib.GError("Test error")

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset", mock_get_string_at_offset
        )

        result = AXText.get_line_at_offset(mock_accessible)
        assert result == ("", 0, 0)

    def test_get_line_at_offset_chromium_fallback(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_line_at_offset with Chromium fallback for invalid result."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 20)

        call_count = 0
        def mock_get_string_at_offset(obj, offset, granularity):
            nonlocal call_count
            call_count += 1
            mock_result = Mock()
            if call_count == 1:
                mock_result.content = ""
                mock_result.start_offset = -1
                mock_result.end_offset = -1
            else:
                mock_result.content = "Valid line"
                mock_result.start_offset = 10
                mock_result.end_offset = 20
            return mock_result

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset", mock_get_string_at_offset
        )

        result = AXText.get_line_at_offset(mock_accessible, 20)
        assert result == ("Valid line", 10, 20)

    def test_get_sentence_at_offset_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_sentence_at_offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        mock_result = Mock()
        mock_result.content = "This is a sentence."
        mock_result.start_offset = 0
        mock_result.end_offset = 19
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset",
            lambda obj, offset, granularity: mock_result,
        )

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        result = AXText.get_sentence_at_offset(mock_accessible)
        assert result == ("This is a sentence.", 0, 19)

    def test_get_sentence_at_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_sentence_at_offset handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        def mock_get_string_at_offset(obj, offset, granularity):
            raise GLib.GError("Test error")

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset", mock_get_string_at_offset
        )

        result = AXText.get_sentence_at_offset(mock_accessible)
        assert result == ("", 0, 0)

    def test_get_paragraph_at_offset_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_paragraph_at_offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        mock_result = Mock()
        mock_result.content = "This is a paragraph."
        mock_result.start_offset = 0
        mock_result.end_offset = 20
        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset",
            lambda obj, offset, granularity: mock_result,
        )

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        result = AXText.get_paragraph_at_offset(mock_accessible)
        assert result == ("This is a paragraph.", 0, 20)

    def test_get_paragraph_at_offset_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_paragraph_at_offset handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 25)
        monkeypatch.setattr(AXText, "get_caret_offset", lambda obj: 7)

        def mock_get_string_at_offset(obj, offset, granularity):
            raise GLib.GError("Test error")

        monkeypatch.setattr(
            "gi.repository.Atspi.Text.get_string_at_offset", mock_get_string_at_offset
        )

        result = AXText.get_paragraph_at_offset(mock_accessible)
        assert result == ("", 0, 0)

    def test_get_character_at_offset_invalid_offset(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_character_at_offset with invalid offset."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 10)
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_message", Mock())

        result = AXText.get_character_at_offset(mock_accessible, 15)
        assert result == ("", 0, 0)
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_substring_with_end_offset_minus_one(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.get_substring with end_offset=-1."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 20)
        monkeypatch.setattr(Atspi.Text, "get_text", lambda obj, start, end: "substring")
        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        result = AXText.get_substring(mock_accessible, 5, -1)
        assert result == "substring"

    def test_supports_sentence_iteration_false(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.supports_sentence_iteration returns False."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: False)

        result = AXText.supports_sentence_iteration(mock_accessible)
        assert result is False

    def test_supports_paragraph_iteration_false(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.supports_paragraph_iteration returns False."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: False)

        result = AXText.supports_paragraph_iteration(mock_accessible)
        assert result is False

    def test_is_whitespace_or_empty_no_text_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.is_whitespace_or_empty with no text support."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_text", lambda obj: False)

        result = AXText.is_whitespace_or_empty(mock_accessible)
        assert result is True

    @pytest.mark.parametrize(
        "attribute_value, expected",
        [
            pytest.param("en", True, id="matching_locale"),
            pytest.param("fr", False, id="non_matching_locale"),
        ],
    )
    def test_value_is_default_language_attribute(
        self, monkeypatch, attribute_value, expected, mock_orca_dependencies
    ):
        """Test AXTextAttribute.value_is_default for LANGUAGE attribute."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXTextAttribute

        monkeypatch.setattr("locale.getlocale", lambda: ("en_US", "UTF-8"))

        result = AXTextAttribute.LANGUAGE.value_is_default(attribute_value)
        assert result is expected
