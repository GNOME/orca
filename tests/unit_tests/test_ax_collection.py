# Unit tests for ax_collection.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_collection.py methods."""

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
class TestAXCollection:
    """Test AXCollection class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_collection dependencies."""

        essential_modules = test_context.setup_shared_dependencies([])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.supports_collection = test_context.Mock(return_value=True)
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock
        return essential_modules

    def test_create_match_rule_with_colon_values(self, test_context: OrcaTestContext) -> None:
        """Test create_match_rule with attributes that contain colons in values."""

        self._setup_dependencies(test_context)
        from orca.ax_collection import AXCollection

        mock_rule = test_context.Mock(spec=Atspi.MatchRule)
        mock_match_rule_new = test_context.patch(
            "gi.repository.Atspi.MatchRule.new", return_value=mock_rule
        )

        attributes = ["url:http://example.com:8080"]
        result = AXCollection.create_match_rule(attributes=attributes)

        expected_attrs = {"url": r"http\://example.com\:8080"}
        mock_match_rule_new.assert_called_once()
        args = mock_match_rule_new.call_args[0]
        assert args[2] == expected_attrs
        assert result == mock_rule

    def test_create_match_rule_with_duplicate_keys(self, test_context: OrcaTestContext) -> None:
        """Test create_match_rule with duplicate attribute keys."""

        self._setup_dependencies(test_context)
        from orca.ax_collection import AXCollection

        mock_rule = test_context.Mock(spec=Atspi.MatchRule)
        mock_match_rule_new = test_context.patch(
            "gi.repository.Atspi.MatchRule.new", return_value=mock_rule
        )

        attributes = ["class:button", "class:primary"]
        result = AXCollection.create_match_rule(attributes=attributes)

        expected_attrs = {"class": "button:primary"}
        mock_match_rule_new.assert_called_once()
        args = mock_match_rule_new.call_args[0]
        assert args[2] == expected_attrs
        assert result == mock_rule

    def test_create_match_rule_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test create_match_rule when Atspi.MatchRule.new raises GLib.GError."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_collection import AXCollection

        test_context.patch(
            "gi.repository.Atspi.MatchRule.new", side_effect=GLib.GError("Test error")
        )
        result = AXCollection.create_match_rule()

        essential_modules["orca.debug"].print_tokens.assert_called_once()
        args = essential_modules["orca.debug"].print_tokens.call_args[0]
        assert "AXCollection: Exception in create_match_rule:" in args[1][0]
        assert result is None

    def test_get_all_matches_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test get_all_matches when Atspi.Collection.get_matches raises GLib.GError."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_collection import AXCollection

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules["orca.ax_object"].AXObject.supports_collection.return_value = True
        test_context.patch(
            "gi.repository.Atspi.Collection.get_matches",
            side_effect=GLib.GError("Collection error")
        )
        mock_rule = test_context.Mock(spec=Atspi.MatchRule)
        result = AXCollection.get_all_matches(mock_accessible, mock_rule)

        essential_modules["orca.debug"].print_tokens.assert_called_once()
        args = essential_modules["orca.debug"].print_tokens.call_args[0]
        assert "AXCollection: Exception in get_all_matches:" in args[1][0]
        assert result == []

    def test_get_first_match_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test get_first_match when Atspi.Collection.get_matches raises GLib.GError."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_collection import AXCollection

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules["orca.ax_object"].AXObject.supports_collection.return_value = True
        test_context.patch(
            "gi.repository.Atspi.Collection.get_matches",
            side_effect=GLib.GError("First match error")
        )
        mock_rule = test_context.Mock(spec=Atspi.MatchRule)
        result = AXCollection.get_first_match(mock_accessible, mock_rule)

        essential_modules["orca.debug"].print_tokens.assert_called_once()
        args = essential_modules["orca.debug"].print_tokens.call_args[0]
        assert "AXCollection: Exception in get_first_match:" in args[1][0]
        assert result is None

    def test_create_match_rule_with_states(self, test_context: OrcaTestContext) -> None:
        """Test create_match_rule with states parameter uses real StateSet."""

        self._setup_dependencies(test_context)
        from orca.ax_collection import AXCollection

        mock_rule = test_context.Mock(spec=Atspi.MatchRule)
        mock_match_rule_new = test_context.patch(
            "gi.repository.Atspi.MatchRule.new", return_value=mock_rule
        )

        states = [Atspi.StateType.FOCUSED, Atspi.StateType.SELECTED]
        result = AXCollection.create_match_rule(states=states)

        mock_match_rule_new.assert_called_once()
        args = mock_match_rule_new.call_args[0]
        state_set = args[0]  # First argument should be the StateSet
        assert isinstance(state_set, Atspi.StateSet)
        assert result == mock_rule
