# Unit tests for ax_hypertext.py hypertext-related methods.
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

"""Unit tests for ax_hypertext.py hypertext-related methods."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache  # pylint: disable=import-error

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib



@pytest.mark.unit
class TestAXHypertext:
    """Test hypertext-related methods."""

    @pytest.fixture
    def mock_accessible(self):
        """Create a mock Atspi.Accessible object."""

        return Mock(spec=Atspi.Accessible)

    @pytest.fixture
    def mock_hyperlink(self):
        """Create a mock Atspi.Hyperlink object."""

        return Mock(spec=Atspi.Hyperlink)

    def test_get_link_count_with_hypertext_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext._get_link_count with hypertext support."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(Atspi.Hypertext, "get_n_links", lambda self: 3)

        result = AXHypertext._get_link_count(mock_accessible)
        assert result == 3

    def test_get_link_count_without_hypertext_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext._get_link_count without hypertext support."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: False)

        result = AXHypertext._get_link_count(mock_accessible)
        assert result == 0

    def test_get_link_count_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext._get_link_count handles GLib.GError."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(self):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(Atspi.Hypertext, "get_n_links", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext._get_link_count(mock_accessible)
        assert result == 0
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_link_at_index_with_valid_index(
        self, monkeypatch, mock_accessible, mock_hyperlink, mock_orca_dependencies
    ):
        """Test AXHypertext._get_link_at_index with valid index."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(Atspi.Hypertext, "get_link", lambda self, index: mock_hyperlink)

        result = AXHypertext._get_link_at_index(mock_accessible, 0)
        assert result == mock_hyperlink

    def test_get_link_at_index_without_hypertext_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext._get_link_at_index without hypertext support."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: False)

        result = AXHypertext._get_link_at_index(mock_accessible, 0)
        assert result is None

    def test_get_link_at_index_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext._get_link_at_index handles GLib.GError."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(self, index):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(Atspi.Hypertext, "get_link", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext._get_link_at_index(mock_accessible, 0)
        assert result is None
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "start_offset, end_offset, link_ranges, expected_count",
        [
            pytest.param(0, 10, [], 0, id="no_links"),
            pytest.param(0, 10, [(5, 8)], 1, id="link_within_range"),
            pytest.param(0, 10, [(12, 15)], 0, id="link_outside_range"),
            pytest.param(0, 10, [(0, 5), (8, 10)], 2, id="multiple_links_in_range"),
            pytest.param(5, 15, [(0, 6), (10, 20)], 2, id="links_partially_overlapping"),
            pytest.param(10, 15, [(10, 12)], 1, id="link_start_matches_range_start"),
        ],
    )
    def test_get_all_links_in_range(
        self,
        monkeypatch,
        mock_accessible,
        start_offset,
        end_offset,
        link_ranges,
        expected_count,
        mock_orca_dependencies,
    ):
        """Test AXHypertext.get_all_links_in_range."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        mock_links = []
        for _ in link_ranges:
            mock_link = Mock(spec=Atspi.Hyperlink)
            mock_links.append(mock_link)

        monkeypatch.setattr(AXHypertext, "_get_link_count", lambda obj: len(mock_links))
        def get_link_at_index(obj, index):
            return mock_links[index] if index < len(mock_links) else None
        monkeypatch.setattr(AXHypertext, "_get_link_at_index", get_link_at_index)

        def mock_get_start_offset(link):
            for i, mock_link in enumerate(mock_links):
                if link == mock_link:
                    return link_ranges[i][0]
            return -1

        def mock_get_end_offset(link):
            for i, mock_link in enumerate(mock_links):
                if link == mock_link:
                    return link_ranges[i][1]
            return -1

        monkeypatch.setattr(AXHypertext, "get_link_start_offset", mock_get_start_offset)
        monkeypatch.setattr(AXHypertext, "get_link_end_offset", mock_get_end_offset)

        result = AXHypertext.get_all_links_in_range(mock_accessible, start_offset, end_offset)
        assert len(result) == expected_count

    def test_get_all_links_empty_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_all_links with object containing no links."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        monkeypatch.setattr(AXHypertext, "_get_link_count", lambda obj: 0)

        result = AXHypertext.get_all_links(mock_accessible)
        assert not result

    def test_get_all_links_with_valid_links(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_all_links with multiple valid links."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        mock_link1 = Mock(spec=Atspi.Hyperlink)
        mock_link2 = Mock(spec=Atspi.Hyperlink)

        monkeypatch.setattr(AXHypertext, "_get_link_count", lambda obj: 2)
        monkeypatch.setattr(
            AXHypertext,
            "_get_link_at_index",
            lambda obj, index: mock_link1 if index == 0 else mock_link2,
        )

        result = AXHypertext.get_all_links(mock_accessible)
        assert len(result) == 2
        assert result[0] == mock_link1
        assert result[1] == mock_link2

    def test_get_all_links_filters_none_values(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_all_links filters out None values."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        mock_link = Mock(spec=Atspi.Hyperlink)

        monkeypatch.setattr(AXHypertext, "_get_link_count", lambda obj: 3)
        monkeypatch.setattr(
            AXHypertext,
            "_get_link_at_index",
            lambda obj, index: mock_link if index == 1 else None,
        )

        result = AXHypertext.get_all_links(mock_accessible)
        assert len(result) == 1
        assert result[0] == mock_link

    def test_get_link_uri_with_valid_hyperlink(
        self, monkeypatch, mock_accessible, mock_hyperlink, mock_orca_dependencies
    ):
        """Test AXHypertext.get_link_uri with valid hyperlink."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        monkeypatch.setattr(Atspi.Accessible, "get_hyperlink", lambda obj: mock_hyperlink)
        monkeypatch.setattr(Atspi.Hyperlink, "get_uri", lambda link, index: "https://example.com")

        result = AXHypertext.get_link_uri(mock_accessible, 0)
        assert result == "https://example.com"

    def test_get_link_uri_with_no_hyperlink(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_link_uri with no hyperlink."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("No hyperlink")

        monkeypatch.setattr(Atspi.Accessible, "get_hyperlink", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext.get_link_uri(mock_accessible, 0)
        assert result == ""
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_link_uri_with_glib_error(
        self, monkeypatch, mock_accessible, mock_hyperlink, mock_orca_dependencies
    ):
        """Test AXHypertext.get_link_uri handles GLib.GError."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca import debug

        def raise_glib_error(link, index):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Accessible, "get_hyperlink", lambda obj: mock_hyperlink)
        monkeypatch.setattr(Atspi.Hyperlink, "get_uri", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext.get_link_uri(mock_accessible, 0)
        assert result == ""
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "input_type, expected_offset",
        [
            pytest.param("accessible", 5, id="accessible_input"),
            pytest.param("hyperlink", 10, id="hyperlink_input"),
        ],
    )
    def test_get_link_start_offset(
        self,
        monkeypatch,
        mock_accessible,
        mock_hyperlink,
        input_type,
        expected_offset,
        mock_orca_dependencies,
    ):
        """Test AXHypertext.get_link_start_offset."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        if input_type == "accessible":
            monkeypatch.setattr(
                Atspi.Accessible, "get_hyperlink", lambda obj: mock_hyperlink
            )
            input_obj = mock_accessible
        else:
            monkeypatch.setattr(
                Atspi.Hyperlink, "get_object", lambda link, index: mock_accessible
            )
            input_obj = mock_hyperlink

        monkeypatch.setattr(
            Atspi.Hyperlink, "get_start_index", lambda link: expected_offset
        )

        result = AXHypertext.get_link_start_offset(input_obj)
        assert result == expected_offset

    def test_get_link_start_offset_no_hyperlink(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_link_start_offset with no hyperlink."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        monkeypatch.setattr(Atspi.Accessible, "get_hyperlink", lambda obj: None)

        result = AXHypertext.get_link_start_offset(mock_accessible)
        assert result == -1

    def test_get_link_start_offset_with_glib_error(
        self, monkeypatch, mock_hyperlink, mock_orca_dependencies
    ):
        """Test AXHypertext.get_link_start_offset handles GLib.GError."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca import debug

        def raise_glib_error(link):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Hyperlink, "get_object", lambda link, index: mock_hyperlink)
        monkeypatch.setattr(Atspi.Hyperlink, "get_start_index", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext.get_link_start_offset(mock_hyperlink)
        assert result == -1
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "input_type, expected_offset",
        [
            pytest.param("accessible", 15, id="accessible_input"),
            pytest.param("hyperlink", 20, id="hyperlink_input"),
        ],
    )
    def test_get_link_end_offset(
        self,
        monkeypatch,
        mock_accessible,
        mock_hyperlink,
        input_type,
        expected_offset,
        mock_orca_dependencies,
    ):
        """Test AXHypertext.get_link_end_offset."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        if input_type == "accessible":
            monkeypatch.setattr(
                Atspi.Accessible, "get_hyperlink", lambda obj: mock_hyperlink
            )
            input_obj = mock_accessible
        else:
            monkeypatch.setattr(
                Atspi.Hyperlink, "get_object", lambda link, index: mock_accessible
            )
            input_obj = mock_hyperlink

        monkeypatch.setattr(
            Atspi.Hyperlink, "get_end_index", lambda link: expected_offset
        )

        result = AXHypertext.get_link_end_offset(input_obj)
        assert result == expected_offset

    def test_get_link_end_offset_no_hyperlink(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_link_end_offset with no hyperlink."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        monkeypatch.setattr(Atspi.Accessible, "get_hyperlink", lambda obj: None)

        result = AXHypertext.get_link_end_offset(mock_accessible)
        assert result == -1

    def test_get_link_end_offset_with_glib_error(
        self, monkeypatch, mock_hyperlink, mock_orca_dependencies
    ):
        """Test AXHypertext.get_link_end_offset handles GLib.GError."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca import debug

        def raise_glib_error(link):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Hyperlink, "get_object", lambda link, index: mock_hyperlink)
        monkeypatch.setattr(Atspi.Hyperlink, "get_end_index", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext.get_link_end_offset(mock_hyperlink)
        assert result == -1
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "uri, remove_extension, expected_result",
        [
            pytest.param(
                "https://example.com/path/file.html", False, "file.html", id="path_with_extension"
            ),
            pytest.param(
                "https://example.com/path/file.html", True, "file", id="path_with_extension_removed"
            ),
            pytest.param("https://example.com/", False, "", id="no_path_component"),
            pytest.param("", False, "", id="empty_uri"),
            pytest.param("https://example.com/simple", False, "simple", id="path_no_extension"),
            pytest.param(
                "https://example.com/simple", True, "simple", id="path_no_extension_capitalized"
            ),
            pytest.param(
                "file:///home/user/document.pdf", False, "document.pdf", id="file_uri"
            ),
            pytest.param(
                "file:///home/user/document.pdf", True, "document", id="file_uri_extension_removed"
            ),
        ],
    )
    def test_get_link_basename(
        self,
        monkeypatch,
        mock_accessible,
        uri,
        remove_extension,
        expected_result,
        mock_orca_dependencies,
    ):
        """Test AXHypertext.get_link_basename."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext

        monkeypatch.setattr(
            AXHypertext, "get_link_uri", lambda obj, index: uri
        )

        result = AXHypertext.get_link_basename(
            mock_accessible, 0, remove_extension
        )
        assert result == expected_result

    def test_get_child_at_offset_with_valid_link(
        self, monkeypatch, mock_accessible, mock_hyperlink, mock_orca_dependencies
    ):
        """Test AXHypertext.get_child_at_offset with valid link."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(Atspi.Hypertext, "get_link_index", lambda self, offset: 0)
        monkeypatch.setattr(
            AXHypertext, "_get_link_at_index", lambda obj, index: mock_hyperlink
        )
        monkeypatch.setattr(
            Atspi.Hyperlink, "get_object", lambda link, index: mock_child
        )

        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result == mock_child

    def test_get_child_at_offset_without_hypertext_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_child_at_offset without hypertext support."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: False)

        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None

    def test_get_child_at_offset_no_link_at_index(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_child_at_offset with no link at index."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(
            Atspi.Hypertext, "get_link_index", lambda self, offset: -1
        )

        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None

    def test_get_child_at_offset_with_glib_error_get_link_index(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_child_at_offset handles GLib.GError in get_link_index."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj, offset):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(Atspi.Hypertext, "get_link_index", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_child_at_offset_with_glib_error_get_object(
        self, monkeypatch, mock_accessible, mock_hyperlink, mock_orca_dependencies
    ):
        """Test AXHypertext.get_child_at_offset handles GLib.GError in get_object."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(link, index):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_hypertext", lambda obj: True)
        monkeypatch.setattr(Atspi.Hypertext, "get_link_index", lambda obj, offset: 0)
        monkeypatch.setattr(
            AXHypertext, "_get_link_at_index", lambda obj, index: mock_hyperlink
        )
        monkeypatch.setattr(Atspi.Hyperlink, "get_object", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_character_offset_in_parent_with_text_parent(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_character_offset_in_parent with text-supporting parent."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "get_parent", lambda obj: mock_parent)
        monkeypatch.setattr(AXObject, "supports_text", lambda obj: True)
        monkeypatch.setattr(AXHypertext, "get_link_start_offset", lambda obj: 10)

        result = AXHypertext.get_character_offset_in_parent(mock_accessible)
        assert result == 10

    def test_get_character_offset_in_parent_without_text_parent(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_character_offset_in_parent without text-supporting parent."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "get_parent", lambda obj: mock_parent)
        monkeypatch.setattr(AXObject, "supports_text", lambda obj: False)

        result = AXHypertext.get_character_offset_in_parent(mock_accessible)
        assert result == -1

    def test_get_character_offset_in_parent_no_parent(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXHypertext.get_character_offset_in_parent with no parent."""

        clean_module_cache("orca.ax_hypertext")
        from orca.ax_hypertext import AXHypertext
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_parent", lambda obj: None)
        monkeypatch.setattr(Atspi.Accessible, "get_hyperlink", lambda obj: None)

        result = AXHypertext.get_character_offset_in_parent(mock_accessible)
        assert result == -1
