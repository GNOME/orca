# Unit tests for ax_document.py methods.
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
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for ax_document.py methods."""

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
class TestAXDocument:
    """Test AXDocument class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_document dependencies."""

        additional_modules = [
            "orca.ax_collection",
            "orca.ax_object",
            "orca.ax_table",
            "orca.ax_utilities_role",
            "orca.ax_utilities_state",
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

        ax_table_mock = essential_modules["orca.ax_table"].AXTable
        ax_table_mock.is_layout_table = test_context.Mock(return_value=False)

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
        "method_name,expected_result",
        [
            ("did_page_change", False),
            ("get_page_count", 0),
            ("get_locale", ""),
        ],
    )
    def test_document_methods_when_not_document(
        self, test_context: OrcaTestContext, method_name: str, expected_result
    ) -> None:
        """Test AXDocument methods return defaults when object doesn't support document."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = False
        method = getattr(AXDocument, method_name)
        result = method(mock_accessible)
        assert result == expected_result
        ax_object_mock.supports_document.assert_called_once_with(mock_accessible)

    def test_did_page_change_false_when_page_unchanged(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument.did_page_change returns False when page hasn't changed."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        document_hash = hash(mock_accessible)
        AXDocument.LAST_KNOWN_PAGE[document_hash] = 3
        mock_get_page = test_context.Mock(return_value=3)
        test_context.patch_object(AXDocument, "_get_current_page", new=mock_get_page)
        result = AXDocument.did_page_change(mock_accessible)
        assert result is False
        mock_get_page.assert_called_once_with(mock_accessible)

    def test_did_page_change_true_when_page_changed(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument.did_page_change returns True when page has changed."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        document_hash = hash(mock_accessible)
        AXDocument.LAST_KNOWN_PAGE[document_hash] = 3
        mock_get_page = test_context.Mock(return_value=5)
        test_context.patch_object(AXDocument, "_get_current_page", new=mock_get_page)
        result = AXDocument.did_page_change(mock_accessible)
        assert result is True
        mock_get_page.assert_called_once_with(mock_accessible)

    def test_get_current_page_zero_when_not_document(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument._get_current_page returns 0 when object doesn't support document."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = False
        result = AXDocument._get_current_page(mock_accessible)
        assert result == 0
        ax_object_mock.supports_document.assert_called_once_with(mock_accessible)

    def test_get_current_page_success(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument._get_current_page returns page number on success."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        mock_get_page = test_context.Mock(return_value=7)
        test_context.patch(
            "gi.repository.Atspi.Document.get_current_page_number", new=mock_get_page
        )
        result = AXDocument._get_current_page(mock_accessible)
        assert result == 7
        mock_get_page.assert_called_once_with(mock_accessible)

    def test_get_current_page_exception_returns_zero(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument._get_current_page returns 0 on GLib.GError exception."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        mock_get_page = test_context.Mock(side_effect=GLib.GError("Test error"))
        test_context.patch(
            "gi.repository.Atspi.Document.get_current_page_number", new=mock_get_page
        )
        result = AXDocument._get_current_page(mock_accessible)
        assert result == 0
        mock_get_page.assert_called_once_with(mock_accessible)

    def test_get_current_page_public_method_caches_result(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXDocument.get_current_page caches the result in LAST_KNOWN_PAGE."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        mock_get_page = test_context.Mock(return_value=9)
        test_context.patch_object(AXDocument, "_get_current_page", new=mock_get_page)
        result = AXDocument.get_current_page(mock_accessible)
        assert result == 9
        document_hash = hash(mock_accessible)
        assert AXDocument.LAST_KNOWN_PAGE[document_hash] == 9

    def test_get_page_count_success(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument.get_page_count returns page count on success."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        mock_get_count = test_context.Mock(return_value=25)
        test_context.patch(
            "gi.repository.Atspi.Document.get_page_count", new=mock_get_count
        )
        result = AXDocument.get_page_count(mock_accessible)
        assert result == 25
        mock_get_count.assert_called_once_with(mock_accessible)

    def test_get_locale_success(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument.get_locale returns locale string on success."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        mock_get_locale = test_context.Mock(return_value="en_US")
        test_context.patch("gi.repository.Atspi.Document.get_locale", new=mock_get_locale)
        result = AXDocument.get_locale(mock_accessible)
        assert result == "en_US"
        mock_get_locale.assert_called_once_with(mock_accessible)

    def test_get_attributes_dict_empty_when_not_document(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXDocument._get_attributes_dict returns empty dict when object isn't a document."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = False
        result = AXDocument._get_attributes_dict(mock_accessible)
        assert result == {}
        ax_object_mock.supports_document.assert_called_once_with(mock_accessible)

    def test_get_attributes_dict_success(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument._get_attributes_dict returns attributes dict on success."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        test_attributes = {"DocURL": "http://example.com", "MimeType": "text/html"}
        mock_get_attrs = test_context.Mock(return_value=test_attributes)
        test_context.patch(
            "gi.repository.Atspi.Document.get_document_attributes", new=mock_get_attrs
        )
        result = AXDocument._get_attributes_dict(mock_accessible)
        assert result == test_attributes
        mock_get_attrs.assert_called_once_with(mock_accessible)

    @pytest.mark.parametrize(
        "attributes,expected_uri",
        [
            ({"DocURL": "http://example.com/doc", "URI": "fallback"}, "http://example.com/doc"),
            ({"URI": "http://example.com/fallback"}, "http://example.com/fallback"),
            ({}, ""),
        ],
    )
    def test_get_uri_handling(
        self, test_context: OrcaTestContext, attributes: dict, expected_uri: str
    ) -> None:
        """Test AXDocument.get_uri with different attribute scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_get_attrs = test_context.Mock(return_value=attributes)
        test_context.patch_object(AXDocument, "_get_attributes_dict", new=mock_get_attrs)
        result = AXDocument.get_uri(mock_accessible)
        assert result == expected_uri

    def test_get_mime_type_returns_mime_type(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument.get_mime_type returns MimeType from attributes."""

        self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_mime = "application/pdf"
        mock_get_attrs = test_context.Mock(return_value={"MimeType": test_mime})
        test_context.patch_object(AXDocument, "_get_attributes_dict", new=mock_get_attrs)
        result = AXDocument.get_mime_type(mock_accessible)
        assert result == test_mime

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
        self, test_context: OrcaTestContext, mime_type: str, expected: bool
    ) -> None:
        """Test AXDocument.is_plain_text with various mime types."""

        self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_get_mime = test_context.Mock(return_value=mime_type)
        test_context.patch_object(AXDocument, "get_mime_type", new=mock_get_mime)
        result = AXDocument.is_plain_text(mock_accessible)
        assert result is expected

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
        self, test_context: OrcaTestContext, mime_type: str, uri: str, expected: bool
    ) -> None:
        """Test AXDocument.is_pdf with various mime types and URIs."""

        self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_get_mime = test_context.Mock(return_value=mime_type)
        mock_get_uri = test_context.Mock(return_value=uri)
        test_context.patch_object(AXDocument, "get_mime_type", new=mock_get_mime)
        test_context.patch_object(AXDocument, "get_uri", new=mock_get_uri)
        result = AXDocument.is_pdf(mock_accessible)
        assert result is expected

    def test_get_document_uri_fragment_returns_fragment(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXDocument.get_document_uri_fragment returns fragment from parsed URI."""

        self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_get_uri = test_context.Mock(return_value="http://example.com/doc#section1")
        test_context.patch_object(AXDocument, "get_uri", new=mock_get_uri)
        result = AXDocument.get_document_uri_fragment(mock_accessible)
        assert result == "section1"

    def test_get_object_counts_returns_zero_counts_for_empty_document(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXDocument._get_object_counts returns zero counts when no objects found."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_collection_mock = essential_modules["orca.ax_collection"].AXCollection
        ax_collection_mock.get_all_matches.return_value = []
        result = AXDocument._get_object_counts(mock_accessible)
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
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXDocument._get_object_counts counts different object types correctly."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

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
        ax_utilities_role_mock.is_link.side_effect = lambda obj: obj in [
            visited_link,
            unvisited_link,
        ]
        ax_utilities_role_mock.is_landmark.side_effect = lambda obj: obj == landmark_obj

        ax_utilities_state_mock = essential_modules["orca.ax_utilities_state"].AXUtilitiesState
        ax_utilities_state_mock.is_visited.side_effect = lambda obj: obj == visited_link

        ax_table_mock = essential_modules["orca.ax_table"].AXTable
        ax_table_mock.is_layout_table.side_effect = lambda obj: obj == layout_table

        result = AXDocument._get_object_counts(mock_accessible)

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
        self, test_context: OrcaTestContext, object_counts: dict, expected_summary: str
    ) -> None:
        """Test AXDocument.get_document_summary with different object count scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

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
        test_context.patch_object(AXDocument, "_get_object_counts", new=mock_get_counts)
        result = AXDocument.get_document_summary(mock_accessible)
        assert result == expected_summary
