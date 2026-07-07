# Unit tests for ax_utilities_hypertext.py methods.
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

# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_utilities_hypertext.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXUtilitiesHypertext:
    """Test AXUtilitiesHypertext class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_hypertext dependencies."""

        additional_modules = ["orca.ax_text", "orca.ax_utilities_role"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800
        debug_mock.debugLevel = 1000

        return essential_modules

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
        """Test AXUtilitiesHypertext.get_all_links_in_range."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import AXUtilitiesHypertext

        mock_links = [test_context.Mock(spec=Atspi.Hyperlink) for _ in link_ranges]

        def get_offset(link, is_start=True) -> int:
            for i, mock_link in enumerate(mock_links):
                if link == mock_link:
                    return link_ranges[i][0 if is_start else 1]
            return -1

        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_count",
            return_value=len(mock_links),
        )

        def mock_get_link_at_index(_obj, index):
            return mock_links[index] if index < len(mock_links) else None

        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_at_index",
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
        result = AXUtilitiesHypertext.get_all_links_in_range(
            mock_accessible, start_offset, end_offset
        )
        assert len(result) == expected_count

    @pytest.mark.parametrize(
        "uri, remove_extension, expected_result",
        [
            pytest.param(
                "https://example.com/path/file.html",
                False,
                "file.html",
                id="path_with_extension",
            ),
            pytest.param(
                "https://example.com/path/file.html",
                True,
                "file",
                id="path_with_extension_removed",
            ),
            pytest.param("https://example.com/", False, "", id="no_path_component"),
            pytest.param("", False, "", id="empty_uri"),
            pytest.param("https://example.com/simple", False, "simple", id="path_no_extension"),
            pytest.param(
                "https://example.com/simple",
                True,
                "simple",
                id="path_no_extension_capitalized",
            ),
            pytest.param("file:///home/user/document.pdf", False, "document.pdf", id="file_uri"),
            pytest.param(
                "file:///home/user/document.pdf",
                True,
                "document",
                id="file_uri_extension_removed",
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
        """Test AXUtilitiesHypertext.get_link_basename."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import AXUtilitiesHypertext

        test_context.patch("orca.ax_hypertext.AXHypertext.get_link_uri", return_value=uri)
        result = AXUtilitiesHypertext.get_link_basename(mock_accessible, 0, remove_extension)
        assert result == expected_result
