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

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXDocument:
    """Test AXDocument class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_document dependencies."""

        additional_modules = [
            "orca.ax_collection",
            "orca.ax_object",
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
        "method_name,expected_result",
        [
            ("get_page_count", 0),
            ("get_locale", ""),
        ],
    )
    def test_document_methods_when_not_document(
        self,
        test_context: OrcaTestContext,
        method_name: str,
        expected_result,
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

    def test_get_page_count_success(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument.get_page_count returns page count on success."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        mock_get_count = test_context.Mock(return_value=25)
        test_context.patch("gi.repository.Atspi.Document.get_page_count", new=mock_get_count)
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
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXDocument.get_attributes_dict returns empty dict when object isn't a document."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = False
        result = AXDocument.get_attributes_dict(mock_accessible)
        assert result == {}
        ax_object_mock.supports_document.assert_called_once_with(mock_accessible)

    def test_get_attributes_dict_success(self, test_context: OrcaTestContext) -> None:
        """Test AXDocument.get_attributes_dict returns attributes dict on success."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_document import AXDocument

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.supports_document.return_value = True
        test_attributes = {"DocURL": "http://example.com", "MimeType": "text/html"}
        mock_get_attrs = test_context.Mock(return_value=test_attributes)
        test_context.patch(
            "gi.repository.Atspi.Document.get_document_attributes",
            new=mock_get_attrs,
        )
        result = AXDocument.get_attributes_dict(mock_accessible)
        assert result == test_attributes
        mock_get_attrs.assert_called_once_with(mock_accessible)
