# Unit tests for ax_utilities_role.py accessibility role utilities.
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
# pylint: disable=unused-argument
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for ax_utilities_role.py accessibility role utilities."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi



@pytest.mark.unit
class TestAXUtilitiesRole:
    """Test role identification methods."""

    @pytest.mark.parametrize(
        "method_name, matching_role, non_matching_role",
        [
            ("is_color_chooser", Atspi.Role.COLOR_CHOOSER, Atspi.Role.PUSH_BUTTON),
            ("is_column_header", Atspi.Role.COLUMN_HEADER, Atspi.Role.ROW_HEADER),
        ],
    )
    def test_simple_role_methods(
        self, monkeypatch, method_name, matching_role, non_matching_role, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole simple role methods."""

        mock_obj = Mock(spec=Atspi.Accessible)

        # Test with matching role
        # Create a mock AXObject class with the get_role method
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=matching_role)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole
        method = getattr(AXUtilitiesRole, method_name)
        assert method(mock_obj)

        # Test with non-matching role
        # Update the mock to return non-matching role
        mock_ax_object_class.get_role = Mock(return_value=non_matching_role)

        # No need to re-import, just use the existing AXUtilitiesRole class
        method = getattr(AXUtilitiesRole, method_name)
        assert not method(mock_obj)

    def test_is_button_with_push_button_role(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.is_button with push button role."""

        # Create a mock AXObject class with the get_role method
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.PUSH_BUTTON)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.is_button(mock_obj)

    def test_is_button_with_toggle_button_role(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.is_button with toggle button role."""

        # Create a mock AXObject class with the get_role method
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.TOGGLE_BUTTON)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.is_button(mock_obj)

    def test_is_button_with_non_button_role(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.is_button with non-button roles."""

        # Create a mock AXObject class with the get_role method
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert not AXUtilitiesRole.is_button(mock_obj)


    def test_children_are_presentational(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.children_are_presentational."""

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Role is inherently presentational
        # Create a mock AXObject class with the get_role method
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.PUSH_BUTTON)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole
        monkeypatch.setattr(AXUtilitiesRole, "is_switch", lambda obj, role=None: False)
        assert AXUtilitiesRole.children_are_presentational(mock_obj)

        # Scenario: Role is not presentational
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        monkeypatch.setattr(AXUtilitiesRole, "is_switch", lambda obj, role=None: False)
        assert not AXUtilitiesRole.children_are_presentational(mock_obj)

        # Scenario: Role becomes presentational via is_switch
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        monkeypatch.setattr(AXUtilitiesRole, "is_switch", lambda obj, role=None: True)
        assert AXUtilitiesRole.children_are_presentational(mock_obj)

    def test_get_localized_role_name_with_atspi_role(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.get_localized_role_name with standard Atspi.Role."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
        mock_ax_object_class.supports_value = Mock(return_value=False)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRole, "is_dpub", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_landmark", lambda obj, role=None: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_comment", lambda obj, role=None: False)

        if hasattr(Atspi, "role_get_localized_name"):
            monkeypatch.setattr(Atspi, "role_get_localized_name", lambda role: "LocalizedRole")
        else:
            monkeypatch.setattr(Atspi, "role_get_name", lambda role: "LocalizedRole")

        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.PUSH_BUTTON)
            == "LocalizedRole"
        )

    def test_get_localized_role_name_with_non_atspi_role(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.get_localized_role_name with non-Atspi.Role value."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
        mock_ax_object_class.get_role_name = Mock(return_value="role_name")
        mock_ax_object_class.supports_value = Mock(return_value=False)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.get_localized_role_name(mock_obj, "not_a_role") == "role_name"

    def test_get_localized_role_name_with_dpub_roles(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.get_localized_role_name for DPUB roles."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
        mock_ax_object_class.supports_value = Mock(return_value=False)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRole, "is_dpub", lambda obj: True)

        # Scenario: DPUB landmark role (acknowledgments)
        monkeypatch.setattr(AXUtilitiesRole, "is_landmark", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_dpub_acknowledgments", lambda obj, role=None: True)
        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.LANDMARK)
            == object_properties.ROLE_ACKNOWLEDGMENTS
        )

        # Scenario: DPUB section role (abstract)
        monkeypatch.setattr(AXUtilitiesRole, "is_landmark", lambda obj, role=None: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_dpub_abstract", lambda obj, role=None: True)
        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, "ROLE_DPUB_SECTION")
            == object_properties.ROLE_ABSTRACT
        )

        # Scenario: DPUB list item role (biblioref)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_item", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_dpub_biblioref", lambda obj, role=None: True)
        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.LIST_ITEM)
            == object_properties.ROLE_BIBLIOENTRY
        )

    def test_is_grid(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_grid."""

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object is not a table
        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_grid(mock_obj)

        # Scenario: Object is a table but has no grid xml-role
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: [])
        assert not AXUtilitiesRole.is_grid(mock_obj)

        # Scenario: Object is a table with grid xml-role
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["grid"])
        assert AXUtilitiesRole.is_grid(mock_obj)

    def test_is_grid_cell(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_grid_cell."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.find_ancestor = Mock(return_value=None)  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object is not a table cell
        monkeypatch.setattr(AXUtilitiesRole, "is_table_cell", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_grid_cell(mock_obj)

        # Scenario: Table cell with gridcell xml-role
        monkeypatch.setattr(AXUtilitiesRole, "is_table_cell", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["gridcell"])
        assert AXUtilitiesRole.is_grid_cell(mock_obj)

        # Scenario: Table cell with cell xml-role and grid ancestor
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["cell"])
        mock_ax_object_class.find_ancestor = Mock(return_value=Mock())  # Mock ancestor found
        assert AXUtilitiesRole.is_grid_cell(mock_obj)

        # Scenario: Table cell with cell xml-role but no grid ancestor
        mock_ax_object_class.find_ancestor = Mock(return_value=None)  # No ancestor found
        assert not AXUtilitiesRole.is_grid_cell(mock_obj)

    def test_is_editable_combo_box(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_editable_combo_box."""

        # Create mock classes with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)  # Default
        mock_ax_object_class.find_descendant = Mock(return_value=None)  # Default
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        mock_utilities_state_class = Mock()
        mock_utilities_state_class.is_editable = Mock(return_value=False)  # Default
        mock_orca_dependencies["ax_utilities_state"].AXUtilitiesState = mock_utilities_state_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not a combo box
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        assert not AXUtilitiesRole.is_editable_combo_box(mock_obj)

        # Scenario: Combo box, editable
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.COMBO_BOX)
        mock_utilities_state_class.is_editable = Mock(return_value=True)
        assert AXUtilitiesRole.is_editable_combo_box(mock_obj)

        # Scenario: Combo box, not editable, has text input descendant
        mock_utilities_state_class.is_editable = Mock(return_value=False)
        mock_ax_object_class.find_descendant = Mock(return_value=Mock())  # Mock descendant found
        assert AXUtilitiesRole.is_editable_combo_box(mock_obj)

        # Scenario: Combo box, not editable, no text input descendant
        mock_ax_object_class.find_descendant = Mock(return_value=None)  # No descendant found
        assert not AXUtilitiesRole.is_editable_combo_box(mock_obj)

    def test_is_feed_article(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_feed_article."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.find_ancestor = Mock(return_value=None)  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not an article
        monkeypatch.setattr(AXUtilitiesRole, "is_article", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_feed_article(mock_obj)

        # Scenario: Article, no feed ancestor
        monkeypatch.setattr(AXUtilitiesRole, "is_article", lambda obj, role=None: True)
        mock_ax_object_class.find_ancestor = Mock(return_value=None)
        assert not AXUtilitiesRole.is_feed_article(mock_obj)

        # Scenario: Article, has feed ancestor
        mock_ax_object_class.find_ancestor = Mock(return_value=Mock())  # Mock ancestor found
        assert AXUtilitiesRole.is_feed_article(mock_obj)

    def test_is_inline_internal_frame(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_inline_internal_frame for internal frame and display style."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not internal frame
        monkeypatch.setattr(AXUtilitiesRole, "is_internal_frame", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_inline_internal_frame(mock_obj)

        # Scenario: Internal frame, not inline
        monkeypatch.setattr(AXUtilitiesRole, "is_internal_frame", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "_get_display_style", lambda obj: "block")
        assert not AXUtilitiesRole.is_inline_internal_frame(mock_obj)

        # Scenario: Internal frame, inline
        monkeypatch.setattr(AXUtilitiesRole, "_get_display_style", lambda obj: "inline")
        assert AXUtilitiesRole.is_inline_internal_frame(mock_obj)

    def test_is_inline_list_item(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_inline_list_item for list item and display style."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not list item
        monkeypatch.setattr(AXUtilitiesRole, "is_list_item", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_inline_list_item(mock_obj)

        # Scenario: List item, not inline
        monkeypatch.setattr(AXUtilitiesRole, "is_list_item", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "_get_display_style", lambda obj: "block")
        assert not AXUtilitiesRole.is_inline_list_item(mock_obj)

        # Scenario: List item, inline
        monkeypatch.setattr(AXUtilitiesRole, "_get_display_style", lambda obj: "inline")
        assert AXUtilitiesRole.is_inline_list_item(mock_obj)

    def test_is_inline_suggestion(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_inline_suggestion for suggestion and display style."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not suggestion
        monkeypatch.setattr(AXUtilitiesRole, "is_suggestion", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_inline_suggestion(mock_obj)

        # Scenario: Suggestion, not inline
        monkeypatch.setattr(AXUtilitiesRole, "is_suggestion", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "_get_display_style", lambda obj: "block")
        assert not AXUtilitiesRole.is_inline_suggestion(mock_obj)

        # Scenario: Suggestion, inline
        monkeypatch.setattr(AXUtilitiesRole, "_get_display_style", lambda obj: "inline")
        assert AXUtilitiesRole.is_inline_suggestion(mock_obj)

    def test_is_list_box_item(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_list_box_item for list item and list box ancestor."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.find_ancestor = Mock(return_value=None)  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not list item
        monkeypatch.setattr(AXUtilitiesRole, "is_list_item", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_list_box_item(mock_obj)

        # Scenario: List item, no list box ancestor
        monkeypatch.setattr(AXUtilitiesRole, "is_list_item", lambda obj, role=None: True)
        mock_ax_object_class.find_ancestor = Mock(return_value=None)
        assert not AXUtilitiesRole.is_list_box_item(mock_obj)

        # Scenario: List item, has list box ancestor
        mock_ax_object_class.find_ancestor = Mock(return_value=Mock())  # Mock ancestor found
        assert AXUtilitiesRole.is_list_box_item(mock_obj)

    def test_is_math_fraction_without_bar(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_math_fraction_without_bar for math fraction and linethickness."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attribute = Mock(return_value=None)  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not math fraction
        monkeypatch.setattr(AXUtilitiesRole, "is_math_fraction", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

        # Scenario: Math fraction, no linethickness
        monkeypatch.setattr(AXUtilitiesRole, "is_math_fraction", lambda obj, role=None: True)
        mock_ax_object_class.get_attribute = Mock(return_value=None)
        assert not AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

        # Scenario: Math fraction, linethickness with nonzero
        mock_ax_object_class.get_attribute = Mock(return_value="2")
        assert not AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

        # Scenario: Math fraction, linethickness all zero
        mock_ax_object_class.get_attribute = Mock(return_value="00")
        assert AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

    def test_is_modal_dialog(self, monkeypatch, mock_orca_dependencies):
        """Test is_modal_dialog for dialog/alert roles and modal state."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.has_state = Mock(return_value=False)  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not dialog or alert
        monkeypatch.setattr(AXUtilitiesRole, "is_dialog_or_alert", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_modal_dialog(mock_obj)

        # Scenario: Dialog or alert, not modal
        monkeypatch.setattr(AXUtilitiesRole, "is_dialog_or_alert", lambda obj, role=None: True)
        mock_ax_object_class.has_state = Mock(return_value=False)
        assert not AXUtilitiesRole.is_modal_dialog(mock_obj)

        # Scenario: Dialog or alert, modal
        mock_ax_object_class.has_state = Mock(return_value=True)
        assert AXUtilitiesRole.is_modal_dialog(mock_obj)

    def test_is_multi_line_entry(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_multi_line_entry for entry role and multiline state."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.has_state = Mock(return_value=False)  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not entry
        monkeypatch.setattr(AXUtilitiesRole, "is_entry", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_multi_line_entry(mock_obj)

        # Scenario: Entry, not multiline
        monkeypatch.setattr(AXUtilitiesRole, "is_entry", lambda obj, role=None: True)
        mock_ax_object_class.has_state = Mock(return_value=False)
        assert not AXUtilitiesRole.is_multi_line_entry(mock_obj)

        # Scenario: Entry, multiline
        mock_ax_object_class.has_state = Mock(return_value=True)
        assert AXUtilitiesRole.is_multi_line_entry(mock_obj)

    def test_is_docked_frame(self, monkeypatch, mock_orca_dependencies):
        """Test is_docked_frame for frame role and docked attribute."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not frame
        monkeypatch.setattr(AXUtilitiesRole, "is_frame", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_docked_frame(mock_obj)

        # Scenario: Frame, not docked
        monkeypatch.setattr(AXUtilitiesRole, "is_frame", lambda obj, role=None: True)
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"window-type": "normal"})
        assert not AXUtilitiesRole.is_docked_frame(mock_obj)

        # Scenario: Frame, docked
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"window-type": "dock"})
        assert AXUtilitiesRole.is_docked_frame(mock_obj)

    def test_is_desktop_frame(self, monkeypatch, mock_orca_dependencies):
        """Test is_desktop_frame for desktop frame and is-desktop attribute."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)  # Default case
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Role is DESKTOP_FRAME
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.DESKTOP_FRAME)
        assert AXUtilitiesRole.is_desktop_frame(mock_obj)

        # Scenario: Role is FRAME, is-desktop true
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.FRAME)
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"is-desktop": "true"})
        assert AXUtilitiesRole.is_desktop_frame(mock_obj)

        # Scenario: Role is FRAME, is-desktop false
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"is-desktop": "false"})
        assert not AXUtilitiesRole.is_desktop_frame(mock_obj)

        # Scenario: Role is not DESKTOP_FRAME or FRAME
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        assert not AXUtilitiesRole.is_desktop_frame(mock_obj)

    def test_is_live_region(self, monkeypatch, mock_orca_dependencies):
        """Test is_live_region for container-live attribute."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})  # Default case
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: No container-live
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"foo": "bar"})
        assert not AXUtilitiesRole.is_live_region(mock_obj)

        # Scenario: Has container-live
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"container-live": "polite"})
        assert AXUtilitiesRole.is_live_region(mock_obj)

    def test_is_code_with_code_xml_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_code with code xml-role."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["code"])
        assert AXUtilitiesRole.is_code(mock_obj)

    def test_is_code_with_code_tag(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_code with code HTML tag."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: [])
        monkeypatch.setattr(AXUtilitiesRole, "_get_tag", lambda obj: "code")
        assert AXUtilitiesRole.is_code(mock_obj)

    def test_is_code_with_pre_tag(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_code with pre HTML tag."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: [])
        monkeypatch.setattr(AXUtilitiesRole, "_get_tag", lambda obj: "pre")
        assert AXUtilitiesRole.is_code(mock_obj)

    def test_is_code_with_no_code_indicators(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_code with no code indicators."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["text"])
        monkeypatch.setattr(AXUtilitiesRole, "_get_tag", lambda obj: "p")
        assert not AXUtilitiesRole.is_code(mock_obj)

    def test_is_button_with_popup_true(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.is_button_with_popup for button with popup."""

        # Create mock classes with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.PUSH_BUTTON)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        mock_utilities_state_class = Mock()
        mock_utilities_state_class.has_popup = Mock(return_value=True)
        mock_orca_dependencies["ax_utilities_state"].AXUtilitiesState = mock_utilities_state_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.is_button_with_popup(mock_obj)

    def test_is_button_with_popup_false_no_popup(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.is_button_with_popup for button without popup."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "get_role", lambda obj: Atspi.Role.PUSH_BUTTON
        )
        monkeypatch.setattr(
            mock_orca_dependencies["ax_utilities_state"], "has_popup", lambda obj: False
        )
        assert not AXUtilitiesRole.is_button_with_popup(mock_obj)

    def test_is_button_with_popup_false_not_button(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.is_button_with_popup for non-button with popup."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "get_role", lambda obj: Atspi.Role.LABEL
        )
        monkeypatch.setattr(
            mock_orca_dependencies["ax_utilities_state"], "has_popup", lambda obj: True
        )
        assert not AXUtilitiesRole.is_button_with_popup(mock_obj)

    def test_is_landmark_without_type(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole.is_landmark_without_type."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario 1: Role is not a landmark
        monkeypatch.setattr(AXUtilitiesRole, "is_landmark", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_landmark_without_type(mock_obj)

        # Scenario 2: Role is a landmark and there are no xml-roles
        monkeypatch.setattr(AXUtilitiesRole, "is_landmark", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: [])
        assert AXUtilitiesRole.is_landmark_without_type(mock_obj)

        # Scenario 3: Role is a landmark and there are xml-roles
        monkeypatch.setattr(AXUtilitiesRole, "is_landmark", lambda obj, role=None: True)
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["navigation"])
        assert not AXUtilitiesRole.is_landmark_without_type(mock_obj)
