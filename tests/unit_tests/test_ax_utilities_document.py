# Unit tests for ax_utilities_document.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for ax_utilities_document.py methods."""

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
class TestAXUtilitiesDocument:
    """Test AXUtilitiesDocument class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_document dependencies."""

        additional_modules = [
            "orca.ax_collection",
            "orca.ax_document",
            "orca.ax_utilities_role",
            "orca.ax_utilities_state",
            "orca.ax_utilities_table",
            "orca.messages",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        messages_mock = essential_modules["orca.messages"]
        messages_mock.landmark_count = test_context.Mock(return_value="")
        messages_mock.heading_count = test_context.Mock(return_value="")
        messages_mock.form_count = test_context.Mock(return_value="")
        messages_mock.table_count = test_context.Mock(return_value="")
        messages_mock.visited_link_count = test_context.Mock(return_value="")
        messages_mock.unvisited_link_count = test_context.Mock(return_value="")
        messages_mock.PAGE_SUMMARY_PREFIX = "Page has %s"

        ax_collection_mock = essential_modules["orca.ax_collection"].AXCollection
        ax_collection_mock.create_match_rule = test_context.Mock(return_value={})
        ax_collection_mock.get_all_matches = test_context.Mock(return_value=[])

        ax_document_mock = essential_modules["orca.ax_document"].AXDocument
        ax_document_mock.get_attributes_dict = test_context.Mock(return_value={})

        ax_utilities_table_mock = essential_modules["orca.ax_utilities_table"].AXUtilitiesTable
        ax_utilities_table_mock.is_layout_table = test_context.Mock(return_value=False)

        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"].AXUtilitiesRole
        ax_utilities_role_mock.is_heading = test_context.Mock(return_value=False)
        ax_utilities_role_mock.is_form = test_context.Mock(return_value=False)
        ax_utilities_role_mock.is_table = test_context.Mock(return_value=False)
        ax_utilities_role_mock.is_link = test_context.Mock(return_value=False)
        ax_utilities_role_mock.is_landmark = test_context.Mock(return_value=False)

        ax_utilities_state_mock = essential_modules["orca.ax_utilities_state"].AXUtilitiesState
        ax_utilities_state_mock.is_visited = test_context.Mock(return_value=False)

        return essential_modules

    @pytest.mark.parametrize(
        "mime_type,expected",
        [
            ("text/plain", True),
            ("text/html", False),
            ("application/pdf", False),
            ("", False),
        ],
    )
    def test_is_plain_text(
        self,
        test_context: OrcaTestContext,
        mime_type: str,
        expected: bool,
    ) -> None:
        """Test AXUtilitiesDocument.is_plain_text with various mime types."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        essential_modules["orca.ax_document"].AXDocument.get_attributes_dict.return_value = {
            "MimeType": mime_type,
        }
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        assert AXUtilitiesDocument.is_plain_text(mock_accessible) is expected

    @pytest.mark.parametrize(
        "mime_type,uri,expected",
        [
            ("application/pdf", "http://example.com/document", True),
            ("text/html", "http://example.com/document.pdf", True),
            ("text/html", "http://example.com/document.html", False),
            ("text/plain", "http://example.com/document.pdf", False),
            ("", "http://example.com/document.pdf", False),
        ],
    )
    def test_is_pdf(
        self,
        test_context: OrcaTestContext,
        mime_type: str,
        uri: str,
        expected: bool,
    ) -> None:
        """Test AXUtilitiesDocument.is_pdf with various mime types and URIs."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        essential_modules["orca.ax_document"].AXDocument.get_attributes_dict.return_value = {
            "MimeType": mime_type,
            "DocURL": uri,
        }
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        assert AXUtilitiesDocument.is_pdf(mock_accessible) is expected

    @pytest.mark.parametrize(
        "attributes,expected_uri",
        [
            ({"DocURL": "http://example.com/doc", "URI": "fallback"}, "http://example.com/doc"),
            ({"URI": "http://example.com/fallback"}, "http://example.com/fallback"),
            ({}, ""),
        ],
    )
    def test_get_uri(
        self,
        test_context: OrcaTestContext,
        attributes: dict,
        expected_uri: str,
    ) -> None:
        """Test AXUtilitiesDocument.get_uri with different attribute scenarios."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        essential_modules[
            "orca.ax_document"
        ].AXDocument.get_attributes_dict.return_value = attributes
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        assert AXUtilitiesDocument.get_uri(mock_accessible) == expected_uri

    def test_get_mime_type(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDocument.get_mime_type returns MimeType from attributes."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        essential_modules["orca.ax_document"].AXDocument.get_attributes_dict.return_value = {
            "MimeType": "application/pdf",
        }
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        assert AXUtilitiesDocument.get_mime_type(mock_accessible) == "application/pdf"

    def test_get_document_uri_fragment(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDocument.get_document_uri_fragment returns the parsed URI fragment."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        essential_modules["orca.ax_document"].AXDocument.get_attributes_dict.return_value = {
            "DocURL": "http://example.com/doc#section1",
        }
        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        assert AXUtilitiesDocument.get_document_uri_fragment(mock_accessible) == "section1"

    def test_get_object_counts_returns_zero_counts_for_empty_document(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesDocument._get_object_counts returns zeros when no objects found."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_collection_mock = essential_modules["orca.ax_collection"].AXCollection
        ax_collection_mock.get_all_matches.return_value = []
        result = AXUtilitiesDocument._get_object_counts(mock_accessible)
        expected = {
            "forms": 0,
            "landmarks": 0,
            "headings": 0,
            "tables": 0,
            "unvisited_links": 0,
            "visited_links": 0,
        }
        assert result == expected

    def test_get_object_counts_with_various_objects(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesDocument._get_object_counts counts different object types correctly."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        heading1 = test_context.Mock(spec=Atspi.Accessible)
        heading2 = test_context.Mock(spec=Atspi.Accessible)
        form_obj = test_context.Mock(spec=Atspi.Accessible)
        table_obj = test_context.Mock(spec=Atspi.Accessible)
        visited_link = test_context.Mock(spec=Atspi.Accessible)
        unvisited_link = test_context.Mock(spec=Atspi.Accessible)
        landmark_obj = test_context.Mock(spec=Atspi.Accessible)
        layout_table = test_context.Mock(spec=Atspi.Accessible)

        mock_objects = [
            heading1,
            heading2,
            form_obj,
            table_obj,
            visited_link,
            unvisited_link,
            landmark_obj,
            layout_table,
        ]
        ax_collection_mock = essential_modules["orca.ax_collection"].AXCollection
        ax_collection_mock.get_all_matches.return_value = mock_objects

        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"].AXUtilitiesRole
        ax_utilities_role_mock.is_heading.side_effect = lambda obj: obj in [heading1, heading2]
        ax_utilities_role_mock.is_form.side_effect = lambda obj: obj == form_obj
        ax_utilities_role_mock.is_table.side_effect = lambda obj: obj in [table_obj, layout_table]
        ax_utilities_role_mock.is_link.side_effect = lambda obj: (
            obj
            in [
                visited_link,
                unvisited_link,
            ]
        )
        ax_utilities_role_mock.is_landmark.side_effect = lambda obj: obj == landmark_obj

        ax_utilities_state_mock = essential_modules["orca.ax_utilities_state"].AXUtilitiesState
        ax_utilities_state_mock.is_visited.side_effect = lambda obj: obj == visited_link

        ax_utilities_table_mock = essential_modules["orca.ax_utilities_table"].AXUtilitiesTable
        ax_utilities_table_mock.is_layout_table.side_effect = lambda obj: obj == layout_table

        result = AXUtilitiesDocument._get_object_counts(mock_accessible)

        expected = {
            "forms": 1,
            "landmarks": 1,
            "headings": 2,
            "tables": 1,
            "unvisited_links": 1,
            "visited_links": 1,
        }
        assert result == expected

        ax_collection_mock.create_match_rule.assert_called_once()
        call_args = ax_collection_mock.create_match_rule.call_args
        roles_used = call_args.kwargs["roles"]
        assert Atspi.Role.HEADING in roles_used
        assert Atspi.Role.LINK in roles_used
        assert Atspi.Role.TABLE in roles_used
        assert Atspi.Role.FORM in roles_used
        assert Atspi.Role.LANDMARK in roles_used

    @pytest.mark.parametrize(
        "object_counts,expected_summary",
        [
            (
                {
                    "forms": 0,
                    "landmarks": 0,
                    "headings": 0,
                    "tables": 0,
                    "unvisited_links": 0,
                    "visited_links": 0,
                },
                "",
            ),
            (
                {
                    "forms": 2,
                    "landmarks": 1,
                    "headings": 3,
                    "tables": 1,
                    "unvisited_links": 5,
                    "visited_links": 2,
                },
                (
                    "Page has 1 landmark, 3 headings, 2 forms, 1 table, "
                    "2 visited links, 5 unvisited links"
                ),
            ),
        ],
    )
    def test_get_document_summary(
        self,
        test_context: OrcaTestContext,
        object_counts: dict,
        expected_summary: str,
    ) -> None:
        """Test AXUtilitiesDocument.get_document_summary with different object count scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_utilities_document import AXUtilitiesDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        if expected_summary:
            messages_mock = essential_modules["orca.messages"]
            messages_mock.landmark_count.return_value = "1 landmark"
            messages_mock.heading_count.return_value = "3 headings"
            messages_mock.form_count.return_value = "2 forms"
            messages_mock.table_count.return_value = "1 table"
            messages_mock.visited_link_count.return_value = "2 visited links"
            messages_mock.unvisited_link_count.return_value = "5 unvisited links"
        mock_get_counts = test_context.Mock(return_value=object_counts)
        test_context.patch_object(AXUtilitiesDocument, "_get_object_counts", new=mock_get_counts)
        result = AXUtilitiesDocument.get_document_summary(mock_accessible)
        assert result == expected_summary
