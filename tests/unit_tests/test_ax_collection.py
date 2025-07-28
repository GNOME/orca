# Unit tests for ax_collection.py collection-related methods.
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

"""Unit tests for ax_collection.py collection-related methods."""

from __future__ import annotations

# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-locals

from unittest.mock import Mock, patch

import gi
import pytest

from conftest import clean_module_cache  # pylint: disable=import-error

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib


@pytest.mark.unit
class TestAXCollection:
    """Test collection-related methods."""

    @pytest.fixture
    def mock_accessible(self) -> Mock:
        """Create a mock Atspi.Accessible object."""
        return Mock(spec=Atspi.Accessible)


    def test_create_match_rule_with_default_parameters(self, mock_orca_dependencies):
        """Test create_match_rule with all default parameters."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_rule = Mock()
            mock_match_rule_new.return_value = mock_rule

            result = AXCollection.create_match_rule()

            # Verify StateSet was created and no states were added
            mock_state_set_class.assert_called_once()
            mock_state_set.add.assert_not_called()

            # Verify MatchRule.new was called with correct defaults
            mock_match_rule_new.assert_called_once_with(
                mock_state_set,
                Atspi.CollectionMatchType.ALL,
                {},
                Atspi.CollectionMatchType.ANY,
                [],
                Atspi.CollectionMatchType.ANY,
                [],
                Atspi.CollectionMatchType.ALL,
                False
            )

            assert result == mock_rule

    def test_create_match_rule_with_states(self, mock_orca_dependencies):
        """Test create_match_rule with states provided."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_rule = Mock()
            mock_match_rule_new.return_value = mock_rule

            states = ["FOCUSED", "ENABLED"]
            result = AXCollection.create_match_rule(states=states)

            # Verify states were added to StateSet
            assert mock_state_set.add.call_count == 2
            mock_state_set.add.assert_any_call("FOCUSED")
            mock_state_set.add.assert_any_call("ENABLED")

            assert result == mock_rule

    def test_create_match_rule_with_attributes(self, mock_orca_dependencies):
        """Test create_match_rule with attributes provided."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_rule = Mock()
            mock_match_rule_new.return_value = mock_rule

            attributes = ["class:button", "name:submit"]
            result = AXCollection.create_match_rule(attributes=attributes)

            # Verify attributes dictionary was created correctly
            expected_attrs = {"class": "button", "name": "submit"}
            mock_match_rule_new.assert_called_once()
            args = mock_match_rule_new.call_args[0]
            assert args[2] == expected_attrs  # attributes_dict argument

            assert result == mock_rule

    def test_create_match_rule_with_colon_values(self, mock_orca_dependencies):
        """Test create_match_rule with attributes that contain colons in values."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_rule = Mock()
            mock_match_rule_new.return_value = mock_rule

            # Attribute value contains colons that should be escaped
            attributes = ["url:http://example.com:8080"]
            result = AXCollection.create_match_rule(attributes=attributes)

            # Verify colons in value are escaped with backslash
            expected_attrs = {"url": r"http\://example.com\:8080"}
            mock_match_rule_new.assert_called_once()
            args = mock_match_rule_new.call_args[0]
            assert args[2] == expected_attrs  # attributes_dict argument

            assert result == mock_rule

    def test_create_match_rule_with_duplicate_keys(self, mock_orca_dependencies):
        """Test create_match_rule with duplicate attribute keys."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_rule = Mock()
            mock_match_rule_new.return_value = mock_rule

            # Same key appears multiple times - should be combined with colons
            attributes = ["class:button", "class:primary"]
            result = AXCollection.create_match_rule(attributes=attributes)

            # Verify duplicate keys are combined with colon separator
            expected_attrs = {"class": "button:primary"}
            mock_match_rule_new.assert_called_once()
            args = mock_match_rule_new.call_args[0]
            assert args[2] == expected_attrs  # attributes_dict argument

            assert result == mock_rule

    def test_create_match_rule_with_roles_and_interfaces(self, mock_orca_dependencies):
        """Test create_match_rule with roles and interfaces provided."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_rule = Mock()
            mock_match_rule_new.return_value = mock_rule

            roles = ["BUTTON", "LINK"]
            interfaces = ["ACTION", "COMPONENT"]
            result = AXCollection.create_match_rule(roles=roles, interfaces=interfaces)

            # Verify roles and interfaces are passed correctly
            mock_match_rule_new.assert_called_once()
            args = mock_match_rule_new.call_args[0]
            assert args[4] == roles      # roles argument
            assert args[6] == interfaces # interfaces argument

            assert result == mock_rule

    def test_create_match_rule_with_match_types_and_invert(self, mock_orca_dependencies):
        """Test create_match_rule with custom match types and invert flag."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_rule = Mock()
            mock_match_rule_new.return_value = mock_rule

            result = AXCollection.create_match_rule(
                state_match_type=Atspi.CollectionMatchType.ANY,
                attribute_match_type=Atspi.CollectionMatchType.ALL,
                role_match_type=Atspi.CollectionMatchType.ALL,
                interface_match_type=Atspi.CollectionMatchType.ANY,
                invert=True
            )

            # Verify match types and invert flag are passed correctly
            mock_match_rule_new.assert_called_once()
            args = mock_match_rule_new.call_args[0]
            assert args[1] == Atspi.CollectionMatchType.ANY  # state_match_type
            assert args[3] == Atspi.CollectionMatchType.ALL  # attribute_match_type
            assert args[5] == Atspi.CollectionMatchType.ALL  # role_match_type
            assert args[7] == Atspi.CollectionMatchType.ANY  # interface_match_type
            assert args[8] is True  # invert

            assert result == mock_rule

    def test_create_match_rule_with_glib_error(self, mock_orca_dependencies):
        """Test create_match_rule when Atspi.MatchRule.new raises GLib.GError."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        with patch('gi.repository.Atspi.StateSet') as mock_state_set_class, \
             patch('gi.repository.Atspi.MatchRule.new') as mock_match_rule_new:

            mock_state_set = Mock()
            mock_state_set_class.return_value = mock_state_set
            mock_match_rule_new.side_effect = GLib.GError("Test error")

            result = AXCollection.create_match_rule()

            # Verify error was handled and debug message was printed
            mock_orca_dependencies.debug.print_tokens.assert_called_once()
            args = mock_orca_dependencies.debug.print_tokens.call_args[0]
            assert "AXCollection: Exception in create_match_rule:" in args[1][0]

            assert result is None

    def test_get_all_matches_no_collection_support(
        self, mock_orca_dependencies, mock_accessible
    ):
        """Test get_all_matches when object does not support collection interface."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return False
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = False

        mock_rule = Mock()
        result = AXCollection.get_all_matches(mock_accessible, mock_rule)

        # Verify debug message was printed and empty list returned
        mock_orca_dependencies.debug.print_tokens.assert_called_once()
        args = mock_orca_dependencies.debug.print_tokens.call_args[0]
        assert "does not implement this interface" in args[1][2]

        assert result == []

    def test_get_all_matches_with_none_rule(self, mock_orca_dependencies, mock_accessible):
        """Test get_all_matches with None rule."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        result = AXCollection.get_all_matches(mock_accessible, None)

        assert result == []

    def test_get_all_matches_success(self, mock_orca_dependencies, mock_accessible):
        """Test get_all_matches successful execution."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        with patch('gi.repository.Atspi.Collection.get_matches') as mock_get_matches, \
             patch('time.time') as mock_time:

            # Mock time progression
            mock_time.side_effect = [1000.0, 1000.1234]  # 0.1234 second elapsed

            # Mock collection results
            mock_match1 = Mock()
            mock_match2 = Mock()
            mock_matches = [mock_match1, mock_match2]
            mock_get_matches.return_value = mock_matches

            mock_rule = Mock()
            result = AXCollection.get_all_matches(mock_accessible, mock_rule)

            # Verify collection interface was called correctly
            mock_get_matches.assert_called_once_with(
                mock_accessible,
                mock_rule,
                Atspi.CollectionSortOrder.CANONICAL,
                0,    # no limit
                True  # traverse
            )

            # Verify debug message with timing was printed
            mock_orca_dependencies.debug.print_message.assert_called_once()
            args = mock_orca_dependencies.debug.print_message.call_args[0]
            assert "2 match(es) found in 0.1234s" in args[1]

            assert result == mock_matches

    def test_get_all_matches_with_custom_sort_order(self, mock_orca_dependencies, mock_accessible):
        """Test get_all_matches with custom sort order."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        with patch('gi.repository.Atspi.Collection.get_matches') as mock_get_matches, \
             patch('time.time') as mock_time:

            mock_time.side_effect = [1000.0, 1000.0]  # no time elapsed
            mock_get_matches.return_value = []

            mock_rule = Mock()
            result = AXCollection.get_all_matches(
                mock_accessible,
                mock_rule,
                Atspi.CollectionSortOrder.REVERSE_CANONICAL
            )

            # Verify custom sort order was used
            mock_get_matches.assert_called_once_with(
                mock_accessible,
                mock_rule,
                Atspi.CollectionSortOrder.REVERSE_CANONICAL,
                0,
                True
            )

            assert result == []

    def test_get_all_matches_with_glib_error(self, mock_orca_dependencies, mock_accessible):
        """Test get_all_matches when Atspi.Collection.get_matches raises GLib.GError."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        with patch('gi.repository.Atspi.Collection.get_matches') as mock_get_matches:
            mock_get_matches.side_effect = GLib.GError("Collection error")

            mock_rule = Mock()
            result = AXCollection.get_all_matches(mock_accessible, mock_rule)

            # Verify error was handled and debug message was printed
            mock_orca_dependencies.debug.print_tokens.assert_called_once()
            args = mock_orca_dependencies.debug.print_tokens.call_args[0]
            assert "AXCollection: Exception in get_all_matches:" in args[1][0]

            assert result == []

    def test_get_first_match_object_does_not_support_collection(
        self, mock_orca_dependencies, mock_accessible
    ):
        """Test get_first_match when object does not support collection interface."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return False
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = False

        mock_rule = Mock()
        result = AXCollection.get_first_match(mock_accessible, mock_rule)

        # Verify debug message was printed and None returned
        mock_orca_dependencies.debug.print_tokens.assert_called_once()
        args = mock_orca_dependencies.debug.print_tokens.call_args[0]
        assert "does not implement this interface" in args[1][2]

        assert result is None

    def test_get_first_match_with_none_rule(self, mock_orca_dependencies, mock_accessible):
        """Test get_first_match with None rule."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        result = AXCollection.get_first_match(mock_accessible, None)

        assert result is None

    def test_get_first_match_success_with_results(self, mock_orca_dependencies, mock_accessible):
        """Test get_first_match successful execution with results."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        with patch('gi.repository.Atspi.Collection.get_matches') as mock_get_matches, \
             patch('time.time') as mock_time:

            # Mock time progression
            mock_time.side_effect = [2000.0, 2000.0567]  # 0.0567 second elapsed

            # Mock collection results
            mock_match = Mock()
            mock_matches = [mock_match]
            mock_get_matches.return_value = mock_matches

            mock_rule = Mock()
            result = AXCollection.get_first_match(mock_accessible, mock_rule)

            # Verify collection interface was called correctly with limit 1
            mock_get_matches.assert_called_once_with(
                mock_accessible,
                mock_rule,
                Atspi.CollectionSortOrder.CANONICAL,
                1,    # limit to 1 result
                True  # traverse
            )

            # Verify debug message with timing was printed
            mock_orca_dependencies.debug.print_tokens.assert_called_once()
            args = mock_orca_dependencies.debug.print_tokens.call_args[0]
            assert "AXCollection: found" == args[1][0]
            assert mock_match == args[1][1]
            assert "0.0567s" in args[1][2]

            assert result == mock_match

    def test_get_first_match_success_with_no_results(self, mock_orca_dependencies, mock_accessible):
        """Test get_first_match successful execution with no results."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        with patch('gi.repository.Atspi.Collection.get_matches') as mock_get_matches, \
             patch('time.time') as mock_time:

            mock_time.side_effect = [3000.0, 3000.1]  # 0.1 second elapsed
            mock_get_matches.return_value = []  # no matches

            mock_rule = Mock()
            result = AXCollection.get_first_match(mock_accessible, mock_rule)

            # Verify debug message shows None was found
            mock_orca_dependencies.debug.print_tokens.assert_called_once()
            args = mock_orca_dependencies.debug.print_tokens.call_args[0]
            assert "AXCollection: found" == args[1][0]
            assert args[1][1] is None
            assert "0.1000s" in args[1][2]

            assert result is None

    def test_get_first_match_with_custom_sort_order(self, mock_orca_dependencies, mock_accessible):
        """Test get_first_match with custom sort order."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        with patch('gi.repository.Atspi.Collection.get_matches') as mock_get_matches, \
             patch('time.time') as mock_time:

            mock_time.side_effect = [4000.0, 4000.0]  # no time elapsed
            mock_get_matches.return_value = []

            mock_rule = Mock()
            result = AXCollection.get_first_match(
                mock_accessible,
                mock_rule,
                Atspi.CollectionSortOrder.REVERSE_CANONICAL
            )

            # Verify custom sort order was used
            mock_get_matches.assert_called_once_with(
                mock_accessible,
                mock_rule,
                Atspi.CollectionSortOrder.REVERSE_CANONICAL,
                1,
                True
            )

            assert result is None

    def test_get_first_match_with_glib_error(self, mock_orca_dependencies, mock_accessible):
        """Test get_first_match when Atspi.Collection.get_matches raises GLib.GError."""
        clean_module_cache("orca.ax_collection")
        from orca.ax_collection import AXCollection

        # Mock AXObject.supports_collection to return True
        mock_orca_dependencies.ax_object.AXObject.supports_collection.return_value = True

        with patch('gi.repository.Atspi.Collection.get_matches') as mock_get_matches:
            mock_get_matches.side_effect = GLib.GError("First match error")

            mock_rule = Mock()
            result = AXCollection.get_first_match(mock_accessible, mock_rule)

            # Verify error was handled and debug message was printed
            mock_orca_dependencies.debug.print_tokens.assert_called_once()
            args = mock_orca_dependencies.debug.print_tokens.call_args[0]
            assert "AXCollection: Exception in get_first_match:" in args[1][0]

            assert result is None
