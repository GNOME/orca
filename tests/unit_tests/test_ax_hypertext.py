# Unit tests for ax_hypertext.py methods.
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
# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_hypertext.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestAXHypertext:
    """Test AXHypertext class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_hypertext dependencies."""

        essential_modules = test_context.setup_shared_dependencies([])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.supports_hypertext = test_context.Mock(return_value=True)
        ax_object_class_mock.supports_text = test_context.Mock(return_value=True)
        ax_object_class_mock.get_parent = test_context.Mock(return_value=None)
        ax_object_class_mock.get_name = test_context.Mock(return_value="test-object")
        ax_object_class_mock.is_dead = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        return essential_modules

    def test_get_link_count_with_hypertext_support(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext._get_link_count with hypertext support."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=True
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hypertext.get_n_links", return_value=3
        )
        result = AXHypertext._get_link_count(mock_accessible)
        assert result == 3

    def test_get_link_count_without_hypertext_support(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext._get_link_count without hypertext support."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=False
        )
        result = AXHypertext._get_link_count(mock_accessible)
        assert result == 0

    def test_get_link_count_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext._get_link_count handles GLib.GError."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        def raise_glib_error(self) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=True
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hypertext.get_n_links", side_effect=raise_glib_error
        )
        test_context.patch(
            "orca.ax_hypertext.debug.print_message",
            new=essential_modules["orca.debug"].print_message,
        )
        result = AXHypertext._get_link_count(mock_accessible)
        assert result == 0
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "has_hypertext_support,raises_glib_error,should_return_link",
        [
            (True, False, True),  # Valid index
            (False, False, False),  # Without hypertext support
            (True, True, False),  # With GLib error
        ],
    )
    def test_get_link_at_index_scenarios(
        self,
        test_context: OrcaTestContext,
        has_hypertext_support: bool,
        raises_glib_error: bool,
        should_return_link: bool,
    ) -> None:
        """Test AXHypertext._get_link_at_index under different scenarios."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=has_hypertext_support
        )
        if raises_glib_error:

            def raise_glib_error(self, index) -> None:
                raise GLib.GError("Test error")

            test_context.patch(
                "orca.ax_hypertext.Atspi.Hypertext.get_link", side_effect=raise_glib_error
            )
            test_context.patch(
                "orca.ax_hypertext.debug.print_message",
                new=essential_modules["orca.debug"].print_message,
            )
        else:
            test_context.patch(
                "orca.ax_hypertext.Atspi.Hypertext.get_link",
                return_value=mock_hyperlink,
            )
        result = AXHypertext._get_link_at_index(mock_accessible, 0)
        if should_return_link:
            assert result == mock_hyperlink
        else:
            assert result is None
        if raises_glib_error:
            essential_modules["orca.debug"].print_message.assert_called()

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
    def test_get_all_links_in_range(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        start_offset,
        end_offset,
        link_ranges,
        expected_count,
        test_context,
    ) -> None:
        """Test AXHypertext.get_all_links_in_range."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        mock_links = [test_context.Mock(spec=Atspi.Hyperlink) for _ in link_ranges]

        def get_offset(link, is_start=True) -> int:
            for i, mock_link in enumerate(mock_links):
                if link == mock_link:
                    return link_ranges[i][0 if is_start else 1]
            return -1

        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_count", return_value=len(mock_links)
        )
        def mock_get_link_at_index(_obj, index):
            return mock_links[index] if index < len(mock_links) else None
        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_at_index",
            side_effect=mock_get_link_at_index,
        )
        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_start_offset",
            side_effect=lambda link: get_offset(link, True),
        )
        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_end_offset",
            side_effect=lambda link: get_offset(link, False),
        )
        result = AXHypertext.get_all_links_in_range(mock_accessible, start_offset, end_offset)
        assert len(result) == expected_count

    def test_get_all_links_empty_object(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_all_links with object containing no links."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_count", return_value=0
        )
        result = AXHypertext.get_all_links(mock_accessible)
        assert not result

    def test_get_all_links_with_valid_links(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_all_links with multiple valid links."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        mock_link1 = test_context.Mock(spec=Atspi.Hyperlink)
        mock_link2 = test_context.Mock(spec=Atspi.Hyperlink)
        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_count", return_value=2
        )
        def mock_get_link_by_index(_obj, index):
            return mock_link1 if index == 0 else mock_link2
        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_at_index",
            side_effect=mock_get_link_by_index,
        )
        result = AXHypertext.get_all_links(mock_accessible)
        assert len(result) == 2
        assert result[0] == mock_link1
        assert result[1] == mock_link2

    def test_get_all_links_filters_none_values(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_all_links filters out None values."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        mock_link = test_context.Mock(spec=Atspi.Hyperlink)
        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_count", return_value=3
        )
        def mock_get_specific_link(_obj, index):
            return mock_link if index == 1 else None
        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_at_index",
            side_effect=mock_get_specific_link,
        )
        result = AXHypertext.get_all_links(mock_accessible)
        assert len(result) == 1
        assert result[0] == mock_link

    def test_get_link_uri_with_valid_hyperlink(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_link_uri with valid hyperlink."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.Atspi.Accessible.get_hyperlink",
            return_value=mock_hyperlink,
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_uri",
            return_value="https://example.com",
        )
        result = AXHypertext.get_link_uri(mock_accessible, 0)
        assert result == "https://example.com"

    def test_get_link_uri_with_no_hyperlink(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_link_uri with no hyperlink."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        def raise_glib_error(obj) -> None:
            raise GLib.GError("No hyperlink")

        test_context.patch(
            "orca.ax_hypertext.Atspi.Accessible.get_hyperlink", side_effect=raise_glib_error
        )
        test_context.patch(
            "orca.ax_hypertext.debug.print_message",
            new=essential_modules["orca.debug"].print_message,
        )
        result = AXHypertext.get_link_uri(mock_accessible, 0)
        assert result == ""
        essential_modules["orca.debug"].print_message.assert_called()

    def test_get_link_uri_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_link_uri handles GLib.GError."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        def raise_glib_error(link, index) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "orca.ax_hypertext.Atspi.Accessible.get_hyperlink",
            return_value=mock_hyperlink,
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_uri", side_effect=raise_glib_error
        )
        test_context.patch(
            "orca.ax_hypertext.debug.print_message",
            new=essential_modules["orca.debug"].print_message,
        )
        result = AXHypertext.get_link_uri(mock_accessible, 0)
        assert result == ""
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "input_type, expected_offset",
        [
            pytest.param("accessible", 5, id="accessible_input"),
            pytest.param("hyperlink", 10, id="hyperlink_input"),
        ],
    )
    def test_get_link_start_offset(
        self,
        input_type,
        expected_offset,
        test_context,
    ) -> None:
        """Test AXHypertext.get_link_start_offset."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        if input_type == "accessible":
            test_context.patch(
                "orca.ax_hypertext.Atspi.Accessible.get_hyperlink",
                return_value=mock_hyperlink,
            )
            input_obj = mock_accessible
        else:
            test_context.patch(
                "orca.ax_hypertext.Atspi.Hyperlink.get_object",
                return_value=mock_accessible,
            )
            input_obj = mock_hyperlink
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_start_index",
            return_value=expected_offset,
        )
        result = AXHypertext.get_link_start_offset(input_obj)
        assert result == expected_offset

    def test_get_link_start_offset_no_hyperlink(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_link_start_offset with no hyperlink."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.Atspi.Accessible.get_hyperlink", return_value=None
        )
        result = AXHypertext.get_link_start_offset(mock_accessible)
        assert result == -1

    def test_get_link_start_offset_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_link_start_offset handles GLib.GError."""

        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        def raise_glib_error(link) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_object",
            return_value=mock_hyperlink,
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_start_index", side_effect=raise_glib_error
        )
        test_context.patch(
            "orca.ax_hypertext.debug.print_message",
            new=essential_modules["orca.debug"].print_message,
        )
        result = AXHypertext.get_link_start_offset(mock_hyperlink)
        assert result == -1
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "input_type, expected_offset",
        [
            pytest.param("accessible", 15, id="accessible_input"),
            pytest.param("hyperlink", 20, id="hyperlink_input"),
        ],
    )
    def test_get_link_end_offset(
        self,
        input_type,
        expected_offset,
        test_context,
    ) -> None:
        """Test AXHypertext.get_link_end_offset."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        if input_type == "accessible":
            test_context.patch(
                "orca.ax_hypertext.Atspi.Accessible.get_hyperlink",
                return_value=mock_hyperlink,
            )
            input_obj = mock_accessible
        else:
            test_context.patch(
                "orca.ax_hypertext.Atspi.Hyperlink.get_object",
                return_value=mock_accessible,
            )
            input_obj = mock_hyperlink
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_end_index",
            return_value=expected_offset,
        )
        result = AXHypertext.get_link_end_offset(input_obj)
        assert result == expected_offset

    def test_get_link_end_offset_no_hyperlink(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_link_end_offset with no hyperlink."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.Atspi.Accessible.get_hyperlink", return_value=None
        )
        result = AXHypertext.get_link_end_offset(mock_accessible)
        assert result == -1

    def test_get_link_end_offset_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_link_end_offset handles GLib.GError."""

        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        def raise_glib_error(link) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_object",
            return_value=mock_hyperlink,
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_end_index", side_effect=raise_glib_error
        )
        test_context.patch(
            "orca.ax_hypertext.debug.print_message",
            new=essential_modules["orca.debug"].print_message,
        )
        result = AXHypertext.get_link_end_offset(mock_hyperlink)
        assert result == -1
        essential_modules["orca.debug"].print_message.assert_called()

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
            pytest.param("file:///home/user/document.pdf", False, "document.pdf", id="file_uri"),
            pytest.param(
                "file:///home/user/document.pdf", True, "document", id="file_uri_extension_removed"
            ),
        ],
    )
    def test_get_link_basename(
        self,
        uri,
        remove_extension,
        expected_result,
        test_context,
    ) -> None:
        """Test AXHypertext.get_link_basename."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_uri", return_value=uri
        )
        result = AXHypertext.get_link_basename(mock_accessible, 0, remove_extension)
        assert result == expected_result

    def test_get_child_at_offset_with_valid_link(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_child_at_offset with valid link."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=True
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hypertext.get_link_index", return_value=0
        )
        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_at_index",
            return_value=mock_hyperlink,
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_object",
            return_value=mock_child,
        )
        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result == mock_child

    def test_get_child_at_offset_without_hypertext_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXHypertext.get_child_at_offset without hypertext support."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=False
        )
        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None

    def test_get_child_at_offset_no_link_at_index(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_child_at_offset with no link at index."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=True
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hypertext.get_link_index", return_value=-1
        )
        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None

    def test_get_child_at_offset_with_glib_error_get_link_index(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXHypertext.get_child_at_offset handles GLib.GError in get_link_index."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        def raise_glib_error(obj, offset) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=True
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hypertext.get_link_index", side_effect=raise_glib_error
        )
        test_context.patch(
            "orca.ax_hypertext.debug.print_message",
            new=essential_modules["orca.debug"].print_message,
        )
        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None
        essential_modules["orca.debug"].print_message.assert_called()

    def test_get_child_at_offset_with_glib_error_get_object(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXHypertext.get_child_at_offset handles GLib.GError in get_object."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_hyperlink = test_context.Mock(spec=Atspi.Hyperlink)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        def raise_glib_error(link, index) -> None:
            raise GLib.GError("Test error")

        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_hypertext", return_value=True
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hypertext.get_link_index", return_value=0
        )
        test_context.patch(
            "orca.ax_hypertext.AXHypertext._get_link_at_index",
            return_value=mock_hyperlink,
        )
        test_context.patch(
            "orca.ax_hypertext.Atspi.Hyperlink.get_object", side_effect=raise_glib_error
        )
        test_context.patch(
            "orca.ax_hypertext.debug.print_message",
            new=essential_modules["orca.debug"].print_message,
        )
        result = AXHypertext.get_child_at_offset(mock_accessible, 5)
        assert result is None
        essential_modules["orca.debug"].print_message.assert_called()

    def test_get_character_offset_in_parent_with_text_parent(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXHypertext.get_character_offset_in_parent with text-supporting parent."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.ax_hypertext.AXObject.get_parent", return_value=mock_parent
        )
        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_text", return_value=True
        )
        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_start_offset", return_value=10
        )
        result = AXHypertext.get_character_offset_in_parent(mock_accessible)
        assert result == 10

    def test_get_character_offset_in_parent_without_text_parent(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXHypertext.get_character_offset_in_parent without text-supporting parent."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.ax_hypertext.AXObject.get_parent", return_value=mock_parent
        )
        test_context.patch(
            "orca.ax_hypertext.AXObject.supports_text", return_value=False
        )
        result = AXHypertext.get_character_offset_in_parent(mock_accessible)
        assert result == -1

    def test_get_character_offset_in_parent_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXHypertext.get_character_offset_in_parent with no parent."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_hypertext import AXHypertext

        test_context.patch("orca.ax_hypertext.AXObject.get_parent", return_value=None)
        test_context.patch(
            "orca.ax_hypertext.Atspi.Accessible.get_hyperlink", return_value=None
        )
        result = AXHypertext.get_character_offset_in_parent(mock_accessible)
        assert result == -1
