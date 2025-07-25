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
            pytest.param(
                "BG_COLOR", "5px", "5 pixels", id="pixel_value_int"
            ),
            pytest.param(
                "BG_COLOR", "5.5px", "5 pixels", id="pixel_value_float"
            ),
            pytest.param(
                "BG_COLOR", "#ff0000", "red", id="color_value_with_color_names"
            ),
            pytest.param(
                "SIZE", "bold-moz", "Bold", id="moz_prefix_removal"
            ),
            pytest.param(
                "JUSTIFICATION", "justify", "fill", id="justify_to_fill_replacement"
            ),
            pytest.param(
                "FAMILY_NAME", '"Arial", sans-serif', "Arial", id="family_name_cleanup"
            ),
            pytest.param(
                "SIZE", "normal", "normal", id="regular_value"
            ),
            pytest.param(
                "SIZE", None, "", id="none_value"
            ),
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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_tokens", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_message", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_tokens", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_message", Mock()
        )

        result = AXText.get_character_count(mock_accessible)
        assert result == 0
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_substring_successful(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXText.get_substring successful case."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(Atspi.Text, "get_text", lambda obj, start, end: "substring")
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_tokens", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_message", Mock()
        )

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

        monkeypatch.setattr(
            AXText, "get_character_at_offset", lambda obj, offset: ("\ufffc", 5, 6)
        )

        result = AXText.character_at_offset_is_eoc(mock_accessible, 5)
        assert result is True

    def test_character_at_offset_is_eoc_without_eoc(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXText.character_at_offset_is_eoc without embedded object character."""

        clean_module_cache("orca.ax_text")
        from orca.ax_text import AXText

        monkeypatch.setattr(
            AXText, "get_character_at_offset", lambda obj, offset: ("a", 5, 6)
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_tokens", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_message", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_tokens", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_message", Mock()
        )

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

        monkeypatch.setattr(
            Atspi.Text, "get_offset_at_point", lambda obj, x, y, coord_type: 25
        )
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_tokens", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_message", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_tokens", Mock()
        )

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
        monkeypatch.setattr(
            mock_orca_dependencies["debug"], "print_message", Mock()
        )

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
                id="fully_contained"
            ),
            pytest.param(
                Mock(x=0, y=0, width=20, height=20),
                Mock(x=5, y=5, width=10, height=10),
                False,
                id="not_contained"
            ),
            pytest.param(
                Mock(x=10, y=10, width=20, height=20),
                Mock(x=10, y=10, width=20, height=20),
                True,
                id="exactly_same"
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
            pytest.param(
                Mock(y=10, height=10),
                Mock(y=5, height=30),
                0,
                id="line_inside_clip"
            ),
            pytest.param(
                Mock(y=0, height=10),
                Mock(y=15, height=20),
                -1,
                id="line_above_clip"
            ),
            pytest.param(
                Mock(y=40, height=10),
                Mock(y=5, height=20),
                1,
                id="line_below_clip"
            ),
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
