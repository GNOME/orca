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
# pylint: disable=too-many-lines

"""Unit tests for ax_utilities_role.py accessibility role utilities."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache  # pylint: disable=import-error

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
            ("is_alert", Atspi.Role.ALERT, Atspi.Role.DIALOG),
            ("is_animation", Atspi.Role.ANIMATION, Atspi.Role.IMAGE),
            ("is_application", Atspi.Role.APPLICATION, Atspi.Role.FRAME),
            ("is_arrow", Atspi.Role.ARROW, Atspi.Role.PUSH_BUTTON),
            ("is_article", Atspi.Role.ARTICLE, Atspi.Role.SECTION),
            ("is_audio", Atspi.Role.AUDIO, Atspi.Role.VIDEO),
            ("is_block_quote", Atspi.Role.BLOCK_QUOTE, Atspi.Role.PARAGRAPH),
            ("is_calendar", Atspi.Role.CALENDAR, Atspi.Role.DATE_EDITOR),
            ("is_canvas", Atspi.Role.CANVAS, Atspi.Role.IMAGE),
            ("is_caption", Atspi.Role.CAPTION, Atspi.Role.LABEL),
            ("is_chart", Atspi.Role.CHART, Atspi.Role.IMAGE),
            ("is_check_box", Atspi.Role.CHECK_BOX, Atspi.Role.RADIO_BUTTON),
            ("is_check_menu_item", Atspi.Role.CHECK_MENU_ITEM, Atspi.Role.MENU_ITEM),
            ("is_combo_box", Atspi.Role.COMBO_BOX, Atspi.Role.LIST_BOX),
            ("is_date_editor", Atspi.Role.DATE_EDITOR, Atspi.Role.SPIN_BUTTON),
            ("is_definition", Atspi.Role.DEFINITION, Atspi.Role.DESCRIPTION_VALUE),
            ("is_description_list", Atspi.Role.DESCRIPTION_LIST, Atspi.Role.LIST),
            ("is_description_term", Atspi.Role.DESCRIPTION_TERM, Atspi.Role.DESCRIPTION_VALUE),
            ("is_description_value", Atspi.Role.DESCRIPTION_VALUE, Atspi.Role.DESCRIPTION_TERM),
            ("is_desktop_icon", Atspi.Role.DESKTOP_ICON, Atspi.Role.ICON),
            ("is_dial", Atspi.Role.DIAL, Atspi.Role.SLIDER),
            ("is_dialog", Atspi.Role.DIALOG, Atspi.Role.FRAME),
            ("is_directory_pane", Atspi.Role.DIRECTORY_PANE, Atspi.Role.TREE),
            ("is_document_email", Atspi.Role.DOCUMENT_EMAIL, Atspi.Role.DOCUMENT_TEXT),
            ("is_document_frame", Atspi.Role.DOCUMENT_FRAME, Atspi.Role.FRAME),
            (
                "is_document_presentation",
                Atspi.Role.DOCUMENT_PRESENTATION,
                Atspi.Role.DOCUMENT_TEXT
            ),
            (
                "is_document_spreadsheet",
                Atspi.Role.DOCUMENT_SPREADSHEET,
                Atspi.Role.DOCUMENT_TEXT
            ),
            ("is_document_text", Atspi.Role.DOCUMENT_TEXT, Atspi.Role.TEXT),
            ("is_document_web", Atspi.Role.DOCUMENT_WEB, Atspi.Role.DOCUMENT_TEXT),
            ("is_drawing_area", Atspi.Role.DRAWING_AREA, Atspi.Role.CANVAS),
            ("is_editbar", Atspi.Role.EDITBAR, Atspi.Role.TOOL_BAR),
            ("is_embedded", Atspi.Role.EMBEDDED, Atspi.Role.PANEL),
            ("is_entry", Atspi.Role.ENTRY, Atspi.Role.TEXT),
            ("is_extended", Atspi.Role.EXTENDED, Atspi.Role.UNKNOWN),
            ("is_file_chooser", Atspi.Role.FILE_CHOOSER, Atspi.Role.DIALOG),
            ("is_filler", Atspi.Role.FILLER, Atspi.Role.PANEL),
            ("is_focus_traversable", Atspi.Role.FOCUS_TRAVERSABLE, Atspi.Role.PANEL),
            ("is_font_chooser", Atspi.Role.FONT_CHOOSER, Atspi.Role.COLOR_CHOOSER),
            ("is_footer", Atspi.Role.FOOTER, Atspi.Role.HEADER),
            ("is_footnote", Atspi.Role.FOOTNOTE, Atspi.Role.STATIC),
            ("is_form", Atspi.Role.FORM, Atspi.Role.PANEL),
            ("is_frame", Atspi.Role.FRAME, Atspi.Role.WINDOW),
            ("is_glass_pane", Atspi.Role.GLASS_PANE, Atspi.Role.PANEL),
            ("is_header", Atspi.Role.HEADER, Atspi.Role.FOOTER),
            ("is_heading", Atspi.Role.HEADING, Atspi.Role.LABEL),
            ("is_html_container", Atspi.Role.HTML_CONTAINER, Atspi.Role.SECTION),
            ("is_icon", Atspi.Role.ICON, Atspi.Role.IMAGE),
            ("is_image", Atspi.Role.IMAGE, Atspi.Role.ICON),
            ("is_image_map", Atspi.Role.IMAGE_MAP, Atspi.Role.IMAGE),
            ("is_info_bar", Atspi.Role.INFO_BAR, Atspi.Role.TOOL_BAR),
            ("is_input_method_window", Atspi.Role.INPUT_METHOD_WINDOW, Atspi.Role.WINDOW),
            ("is_internal_frame", Atspi.Role.INTERNAL_FRAME, Atspi.Role.FRAME),
            ("is_invalid_role", Atspi.Role.INVALID, Atspi.Role.UNKNOWN),
            ("is_label", Atspi.Role.LABEL, Atspi.Role.STATIC),
            ("is_landmark", Atspi.Role.LANDMARK, Atspi.Role.SECTION),
            ("is_layered_pane", Atspi.Role.LAYERED_PANE, Atspi.Role.PANEL),
            ("is_level_bar", Atspi.Role.LEVEL_BAR, Atspi.Role.PROGRESS_BAR),
            ("is_link", Atspi.Role.LINK, Atspi.Role.TEXT),
            ("is_list", Atspi.Role.LIST, Atspi.Role.LIST_BOX),
            ("is_list_box", Atspi.Role.LIST_BOX, Atspi.Role.LIST),
            ("is_list_item", Atspi.Role.LIST_ITEM, Atspi.Role.LIST),
            ("is_log", Atspi.Role.LOG, Atspi.Role.TEXT),
            ("is_marquee", Atspi.Role.MARQUEE, Atspi.Role.ANIMATION),
            ("is_math", Atspi.Role.MATH, Atspi.Role.STATIC),
            ("is_math_fraction", Atspi.Role.MATH_FRACTION, Atspi.Role.MATH),
            ("is_math_root", Atspi.Role.MATH_ROOT, Atspi.Role.MATH),
            ("is_menu", Atspi.Role.MENU, Atspi.Role.MENU_BAR),
            ("is_menu_bar", Atspi.Role.MENU_BAR, Atspi.Role.MENU),
            ("is_menu_item", Atspi.Role.MENU_ITEM, Atspi.Role.CHECK_MENU_ITEM),
            ("is_notification", Atspi.Role.NOTIFICATION, Atspi.Role.ALERT),
            ("is_option_pane", Atspi.Role.OPTION_PANE, Atspi.Role.PANEL),
            ("is_page", Atspi.Role.PAGE, Atspi.Role.SECTION),
            ("is_page_tab", Atspi.Role.PAGE_TAB, Atspi.Role.PAGE_TAB_LIST),
            ("is_page_tab_list", Atspi.Role.PAGE_TAB_LIST, Atspi.Role.PAGE_TAB),
            ("is_panel", Atspi.Role.PANEL, Atspi.Role.FILLER),
            ("is_paragraph", Atspi.Role.PARAGRAPH, Atspi.Role.TEXT),
            ("is_password_text", Atspi.Role.PASSWORD_TEXT, Atspi.Role.TEXT),
            ("is_popup_menu", Atspi.Role.POPUP_MENU, Atspi.Role.MENU),
            ("is_progress_bar", Atspi.Role.PROGRESS_BAR, Atspi.Role.LEVEL_BAR),
            ("is_push_button", Atspi.Role.PUSH_BUTTON, Atspi.Role.TOGGLE_BUTTON),
            ("is_push_button_menu", Atspi.Role.PUSH_BUTTON_MENU, Atspi.Role.PUSH_BUTTON),
            ("is_radio_button", Atspi.Role.RADIO_BUTTON, Atspi.Role.CHECK_BOX),
            ("is_radio_menu_item", Atspi.Role.RADIO_MENU_ITEM, Atspi.Role.CHECK_MENU_ITEM),
            ("is_rating", Atspi.Role.RATING, Atspi.Role.SLIDER),
            ("is_redundant_object_role", Atspi.Role.REDUNDANT_OBJECT, Atspi.Role.UNKNOWN),
            ("is_root_pane", Atspi.Role.ROOT_PANE, Atspi.Role.PANEL),
            ("is_row_header", Atspi.Role.ROW_HEADER, Atspi.Role.COLUMN_HEADER),
            ("is_ruler", Atspi.Role.RULER, Atspi.Role.SEPARATOR),
            ("is_scroll_bar", Atspi.Role.SCROLL_BAR, Atspi.Role.SLIDER),
            ("is_scroll_pane", Atspi.Role.SCROLL_PANE, Atspi.Role.PANEL),
            ("is_section", Atspi.Role.SECTION, Atspi.Role.ARTICLE),
            ("is_separator", Atspi.Role.SEPARATOR, Atspi.Role.RULER),
            ("is_slider", Atspi.Role.SLIDER, Atspi.Role.SCROLL_BAR),
            ("is_spin_button", Atspi.Role.SPIN_BUTTON, Atspi.Role.ENTRY),
            ("is_split_pane", Atspi.Role.SPLIT_PANE, Atspi.Role.PANEL),
            ("is_static", Atspi.Role.STATIC, Atspi.Role.LABEL),
            ("is_status_bar", Atspi.Role.STATUS_BAR, Atspi.Role.TOOL_BAR),
            ("is_subscript", Atspi.Role.SUBSCRIPT, Atspi.Role.SUPERSCRIPT),
            ("is_superscript", Atspi.Role.SUPERSCRIPT, Atspi.Role.SUBSCRIPT),
            ("is_table", Atspi.Role.TABLE, Atspi.Role.TREE_TABLE),
            ("is_table_cell", Atspi.Role.TABLE_CELL, Atspi.Role.COLUMN_HEADER),
            ("is_terminal", Atspi.Role.TERMINAL, Atspi.Role.TEXT),
            ("is_text", Atspi.Role.TEXT, Atspi.Role.LABEL),
            ("is_timer", Atspi.Role.TIMER, Atspi.Role.STATIC),
            ("is_title_bar", Atspi.Role.TITLE_BAR, Atspi.Role.TOOL_BAR),
            ("is_toggle_button", Atspi.Role.TOGGLE_BUTTON, Atspi.Role.PUSH_BUTTON),
            ("is_tool_bar", Atspi.Role.TOOL_BAR, Atspi.Role.PANEL),
            ("is_tool_tip", Atspi.Role.TOOL_TIP, Atspi.Role.LABEL),
            ("is_tree", Atspi.Role.TREE, Atspi.Role.TREE_TABLE),
            ("is_tree_item", Atspi.Role.TREE_ITEM, Atspi.Role.LIST_ITEM),
            ("is_tree_table", Atspi.Role.TREE_TABLE, Atspi.Role.TABLE),
            ("is_unknown", Atspi.Role.UNKNOWN, Atspi.Role.INVALID),
            ("is_video", Atspi.Role.VIDEO, Atspi.Role.AUDIO),
            ("is_viewport", Atspi.Role.VIEWPORT, Atspi.Role.PANEL),
            ("is_window", Atspi.Role.WINDOW, Atspi.Role.FRAME),
        ],
    )
    def test_simple_role_methods(
        self, monkeypatch, method_name, matching_role, non_matching_role, mock_orca_dependencies
    ):
        """Test AXUtilitiesRole simple role methods."""

        mock_obj = Mock(spec=Atspi.Accessible)

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=matching_role)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        method = getattr(AXUtilitiesRole, method_name)
        assert method(mock_obj)

        mock_ax_object_class.get_role = Mock(return_value=non_matching_role)

        # No need to re-import, just use the existing AXUtilitiesRole class
        method = getattr(AXUtilitiesRole, method_name)
        assert not method(mock_obj)

    def test_is_button_with_push_button_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_button with push button role."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.PUSH_BUTTON)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.is_button(mock_obj)

    def test_is_button_with_toggle_button_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_button with toggle button role."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.TOGGLE_BUTTON)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.is_button(mock_obj)

    def test_is_button_with_non_button_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_button with non-button roles."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert not AXUtilitiesRole.is_button(mock_obj)

    def test_children_are_presentational(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.children_are_presentational."""

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Role is inherently presentational
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

    def test_get_localized_role_name_with_atspi_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_localized_role_name with standard Atspi.Role."""

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

    def test_get_localized_role_name_with_non_atspi_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_localized_role_name with non-Atspi.Role value."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
        mock_ax_object_class.get_role_name = Mock(return_value="role_name")
        mock_ax_object_class.supports_value = Mock(return_value=False)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.get_localized_role_name(mock_obj, "not_a_role") == "role_name"

    def test_get_localized_role_name_with_dpub_roles(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_localized_role_name for DPUB roles."""

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

        mock_ax_object_class = Mock()
        mock_ax_object_class.find_ancestor = Mock(return_value=None)
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
        mock_ax_object_class.find_ancestor = Mock(return_value=Mock())
        assert AXUtilitiesRole.is_grid_cell(mock_obj)

        # Scenario: Table cell with cell xml-role but no grid ancestor
        mock_ax_object_class.find_ancestor = Mock(return_value=None)  # No ancestor found
        assert not AXUtilitiesRole.is_grid_cell(mock_obj)

    def test_is_editable_combo_box(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_editable_combo_box."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        mock_ax_object_class.find_descendant = Mock(return_value=None)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        mock_utilities_state_class = Mock()
        mock_utilities_state_class.is_editable = Mock(return_value=False)
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
        mock_ax_object_class.find_descendant = Mock(return_value=Mock())
        assert AXUtilitiesRole.is_editable_combo_box(mock_obj)

        # Scenario: Combo box, not editable, no text input descendant
        mock_ax_object_class.find_descendant = Mock(return_value=None)  # No descendant found
        assert not AXUtilitiesRole.is_editable_combo_box(mock_obj)

    def test_is_feed_article(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_feed_article."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.find_ancestor = Mock(return_value=None)
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
        mock_ax_object_class.find_ancestor = Mock(return_value=Mock())
        assert AXUtilitiesRole.is_feed_article(mock_obj)

    def test_is_inline_internal_frame(self, monkeypatch, mock_orca_dependencies):
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

    def test_is_inline_list_item(self, monkeypatch, mock_orca_dependencies):
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

    def test_is_inline_suggestion(self, monkeypatch, mock_orca_dependencies):
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

    def test_is_list_box_item(self, monkeypatch, mock_orca_dependencies):
        """Test is_list_box_item for list item and list box ancestor."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.find_ancestor = Mock(return_value=None)
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
        mock_ax_object_class.find_ancestor = Mock(return_value=Mock())
        assert AXUtilitiesRole.is_list_box_item(mock_obj)

    def test_is_math_fraction_without_bar(self, monkeypatch, mock_orca_dependencies):
        """Test is_math_fraction_without_bar for math fraction and linethickness."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attribute = Mock(return_value=None)
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

        mock_ax_object_class = Mock()
        mock_ax_object_class.has_state = Mock(return_value=False)
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

    def test_is_multi_line_entry(self, monkeypatch, mock_orca_dependencies):
        """Test is_multi_line_entry for entry role and multiline state."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.has_state = Mock(return_value=False)
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

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
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

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.LABEL)
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
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

        mock_ax_object_class = Mock()
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
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

    def test_is_button_with_popup_true(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_button_with_popup for button with popup."""

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

    def test_is_button_with_popup_false_no_popup(self, monkeypatch, mock_orca_dependencies):
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

    def test_is_button_with_popup_false_not_button(self, monkeypatch, mock_orca_dependencies):
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

    def test_is_landmark_without_type(self, monkeypatch, mock_orca_dependencies):
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

    def test_get_dialog_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_dialog_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        # Scenario: Include alert as dialog (default)
        roles = AXUtilitiesRole.get_dialog_roles()
        expected = [
            Atspi.Role.COLOR_CHOOSER,
            Atspi.Role.DIALOG,
            Atspi.Role.FILE_CHOOSER,
            Atspi.Role.ALERT
        ]
        assert roles == expected

        # Scenario: Exclude alert as dialog
        roles = AXUtilitiesRole.get_dialog_roles(include_alert_as_dialog=False)
        expected = [Atspi.Role.COLOR_CHOOSER, Atspi.Role.DIALOG, Atspi.Role.FILE_CHOOSER]
        assert roles == expected

    def test_get_document_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_document_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_document_roles()
        expected = [
            Atspi.Role.DOCUMENT_EMAIL,
            Atspi.Role.DOCUMENT_FRAME,
            Atspi.Role.DOCUMENT_PRESENTATION,
            Atspi.Role.DOCUMENT_SPREADSHEET,
            Atspi.Role.DOCUMENT_TEXT,
            Atspi.Role.DOCUMENT_WEB
        ]
        assert roles == expected

    def test_get_form_field_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_form_field_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_form_field_roles()
        expected = [
            Atspi.Role.CHECK_BOX,
            Atspi.Role.RADIO_BUTTON,
            Atspi.Role.COMBO_BOX,
            Atspi.Role.DOCUMENT_FRAME,
            Atspi.Role.TEXT,
            Atspi.Role.LIST_BOX,
            Atspi.Role.ENTRY,
            Atspi.Role.PASSWORD_TEXT,
            Atspi.Role.PUSH_BUTTON,
            Atspi.Role.SPIN_BUTTON,
            Atspi.Role.TOGGLE_BUTTON
        ]
        assert roles == expected

    def test_get_menu_item_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_menu_item_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_menu_item_roles()
        expected = [
            Atspi.Role.MENU_ITEM,
            Atspi.Role.CHECK_MENU_ITEM,
            Atspi.Role.RADIO_MENU_ITEM,
            Atspi.Role.TEAROFF_MENU_ITEM
        ]
        assert roles == expected

    def test_get_menu_related_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_menu_related_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_menu_related_roles()
        expected = [
            Atspi.Role.MENU,
            Atspi.Role.MENU_BAR,
            Atspi.Role.POPUP_MENU,
            Atspi.Role.MENU_ITEM,
            Atspi.Role.CHECK_MENU_ITEM,
            Atspi.Role.RADIO_MENU_ITEM,
            Atspi.Role.TEAROFF_MENU_ITEM
        ]
        assert roles == expected

    def test_get_table_cell_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_table_cell_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        # Scenario: Include headers (default)
        roles = AXUtilitiesRole.get_table_cell_roles()
        expected = [
            Atspi.Role.TABLE_CELL, Atspi.Role.TABLE_COLUMN_HEADER,
            Atspi.Role.TABLE_ROW_HEADER, Atspi.Role.COLUMN_HEADER, Atspi.Role.ROW_HEADER
        ]
        assert roles == expected

        # Scenario: Exclude headers
        roles = AXUtilitiesRole.get_table_cell_roles(include_headers=False)
        expected = [Atspi.Role.TABLE_CELL]
        assert roles == expected

    def test_get_table_header_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_table_header_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_table_header_roles()
        expected = [
            Atspi.Role.TABLE_COLUMN_HEADER, Atspi.Role.TABLE_ROW_HEADER,
            Atspi.Role.COLUMN_HEADER, Atspi.Role.ROW_HEADER
        ]
        assert roles == expected

    def test_get_table_related_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_table_related_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        # Scenario: Exclude caption (default)
        roles = AXUtilitiesRole.get_table_related_roles()
        expected = [
            Atspi.Role.TABLE,
            Atspi.Role.TABLE_CELL,
            Atspi.Role.TABLE_COLUMN_HEADER,
            Atspi.Role.TABLE_ROW_HEADER,
            Atspi.Role.COLUMN_HEADER,
            Atspi.Role.ROW_HEADER
        ]
        assert roles == expected

        # Scenario: Include caption
        roles = AXUtilitiesRole.get_table_related_roles(include_caption=True)
        expected = [
            Atspi.Role.TABLE,
            Atspi.Role.TABLE_CELL,
            Atspi.Role.TABLE_COLUMN_HEADER,
            Atspi.Role.TABLE_ROW_HEADER,
            Atspi.Role.COLUMN_HEADER,
            Atspi.Role.ROW_HEADER,
            Atspi.Role.CAPTION
        ]
        assert roles == expected

    def test_have_same_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.have_same_role."""

        mock_ax_object_class = Mock()
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj1 = Mock(spec=Atspi.Accessible)
        mock_obj2 = Mock(spec=Atspi.Accessible)

        # Scenario: Same roles
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.PUSH_BUTTON)
        assert AXUtilitiesRole.have_same_role(mock_obj1, mock_obj2)

        # Scenario: Different roles
        def mock_get_role(obj):
            if obj == mock_obj1:
                return Atspi.Role.PUSH_BUTTON
            return Atspi.Role.LABEL

        mock_ax_object_class.get_role = mock_get_role
        assert not AXUtilitiesRole.have_same_role(mock_obj1, mock_obj2)

    def test_has_role_from_aria(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.has_role_from_aria."""

        mock_ax_object_class = Mock()
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Has xml-roles attribute
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"xml-roles": "button"})
        assert AXUtilitiesRole.has_role_from_aria(mock_obj)

        # Scenario: No xml-roles attribute
        mock_ax_object_class.get_attributes_dict = Mock(return_value={})
        assert not AXUtilitiesRole.has_role_from_aria(mock_obj)

        # Scenario: Empty xml-roles attribute
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"xml-roles": ""})
        assert not AXUtilitiesRole.has_role_from_aria(mock_obj)

    def test_is_aria_alert(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_aria_alert."""

        mock_ax_object_class = Mock()
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not an ARIA alert (no xml-roles with "alert")
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"xml-roles": "button"})
        assert not AXUtilitiesRole.is_aria_alert(mock_obj)

        # Scenario: ARIA alert with notification role
        mock_ax_object_class.get_attributes_dict = Mock(return_value={"xml-roles": "alert"})
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.NOTIFICATION)
        assert AXUtilitiesRole.is_aria_alert(mock_obj)

        # Scenario: ARIA alert with wrong role (still returns True but logs debug message)
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.ALERT)
        assert AXUtilitiesRole.is_aria_alert(mock_obj)

    def test_is_autocomplete(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_autocomplete."""

        mock_ax_object_class = Mock()
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Has autocomplete role
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.AUTOCOMPLETE)
        assert AXUtilitiesRole.is_autocomplete(mock_obj)

        # Scenario: Different role
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.BUTTON)
        assert not AXUtilitiesRole.is_autocomplete(mock_obj)

        # Scenario: With explicit role parameter
        assert AXUtilitiesRole.is_autocomplete(mock_obj, Atspi.Role.AUTOCOMPLETE)
        assert not AXUtilitiesRole.is_autocomplete(mock_obj, Atspi.Role.BUTTON)

    def test_is_default_button(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_default_button."""

        mock_ax_object_class = Mock()
        mock_ax_object_class.has_state = Mock(return_value=False)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not a push button
        monkeypatch.setattr(AXUtilitiesRole, "is_push_button", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_default_button(mock_obj)

        # Scenario: Push button, not default
        monkeypatch.setattr(AXUtilitiesRole, "is_push_button", lambda obj, role=None: True)
        mock_ax_object_class.has_state = Mock(return_value=False)
        assert not AXUtilitiesRole.is_default_button(mock_obj)

        # Scenario: Push button, is default
        monkeypatch.setattr(AXUtilitiesRole, "is_push_button", lambda obj, role=None: True)
        mock_ax_object_class.has_state = Mock(return_value=True)
        assert AXUtilitiesRole.is_default_button(mock_obj)

    def test_is_single_line_autocomplete_entry(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_single_line_autocomplete_entry."""

        mock_ax_utilities_state_class = Mock()
        mock_orca_dependencies["ax_utilities_state"].AXUtilitiesState = (
            mock_ax_utilities_state_class
        )

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not single line entry
        monkeypatch.setattr(AXUtilitiesRole, "is_single_line_entry", lambda obj, role=None: False)
        assert not AXUtilitiesRole.is_single_line_autocomplete_entry(mock_obj)

        # Scenario: Single line entry, not autocomplete
        monkeypatch.setattr(AXUtilitiesRole, "is_single_line_entry", lambda obj, role=None: True)
        mock_ax_utilities_state_class.supports_autocompletion = Mock(return_value=False)
        assert not AXUtilitiesRole.is_single_line_autocomplete_entry(mock_obj)

        # Scenario: Single line entry, autocomplete
        monkeypatch.setattr(AXUtilitiesRole, "is_single_line_entry", lambda obj, role=None: True)
        mock_ax_utilities_state_class.supports_autocompletion = Mock(return_value=True)
        assert AXUtilitiesRole.is_single_line_autocomplete_entry(mock_obj)

    def test_is_single_line_entry(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_single_line_entry."""

        mock_ax_utilities_state_class = Mock()
        mock_orca_dependencies["ax_utilities_state"].AXUtilitiesState = (
            mock_ax_utilities_state_class
        )

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Not single line
        mock_ax_utilities_state_class.is_single_line = Mock(return_value=False)
        assert not AXUtilitiesRole.is_single_line_entry(mock_obj)

        # Scenario: Single line entry
        mock_ax_utilities_state_class.is_single_line = Mock(return_value=True)
        monkeypatch.setattr(AXUtilitiesRole, "is_entry", lambda obj, role=None: True)
        assert AXUtilitiesRole.is_single_line_entry(mock_obj)

        # Scenario: Single line text, editable
        mock_ax_utilities_state_class.is_single_line = Mock(return_value=True)
        monkeypatch.setattr(AXUtilitiesRole, "is_entry", lambda obj, role=None: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_text", lambda obj, role=None: True)
        mock_ax_utilities_state_class.is_editable = Mock(return_value=True)
        assert AXUtilitiesRole.is_single_line_entry(mock_obj)

        # Scenario: Single line text, not editable
        mock_ax_utilities_state_class.is_editable = Mock(return_value=False)
        assert not AXUtilitiesRole.is_single_line_entry(mock_obj)

    def test_is_dialog_or_alert(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_dialog_or_alert."""

        mock_ax_object_class = Mock()
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Is dialog role
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.DIALOG)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        # Scenario: Is alert role
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.ALERT)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        # Scenario: Is color chooser role (in dialog roles)
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.COLOR_CHOOSER)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        # Scenario: Is file chooser role (in dialog roles)
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.FILE_CHOOSER)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        # Scenario: Neither dialog nor alert
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.BUTTON)
        assert not AXUtilitiesRole.is_dialog_or_alert(mock_obj)

    def test_is_dialog_or_window(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_dialog_or_window."""

        mock_ax_object_class = Mock()
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Is dialog role
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.DIALOG)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        # Scenario: Is frame role
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.FRAME)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        # Scenario: Is window role
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.WINDOW)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        # Scenario: Is color chooser role (in dialog roles, exclude_alert=False)
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.COLOR_CHOOSER)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        # Scenario: Neither dialog nor window
        mock_ax_object_class.get_role = Mock(return_value=Atspi.Role.BUTTON)
        assert not AXUtilitiesRole.is_dialog_or_window(mock_obj)

    def test_get_widget_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_widget_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_widget_roles()
        assert len(roles) > 10
        assert Atspi.Role.PUSH_BUTTON in roles
        assert Atspi.Role.CHECK_BOX in roles
        assert Atspi.Role.ENTRY in roles
        assert Atspi.Role.COMBO_BOX in roles

    def test_get_text_ui_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_text_ui_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_text_ui_roles()
        expected = [
            Atspi.Role.INFO_BAR,
            Atspi.Role.LABEL,
            Atspi.Role.PAGE_TAB,
            Atspi.Role.STATUS_BAR
        ]
        assert roles == expected

    def test_get_tree_related_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_tree_related_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_tree_related_roles()
        expected = [Atspi.Role.TREE, Atspi.Role.TREE_ITEM, Atspi.Role.TREE_TABLE]
        assert roles == expected

    def test_get_set_container_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_set_container_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_set_container_roles()
        expected = [
            Atspi.Role.LIST,
            Atspi.Role.MENU,
            Atspi.Role.PAGE_TAB_LIST,
            Atspi.Role.TABLE,
            Atspi.Role.TREE,
            Atspi.Role.TREE_TABLE
        ]
        assert roles == expected

    def test_get_layout_only_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_layout_only_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_layout_only_roles()
        expected = [
            Atspi.Role.AUTOCOMPLETE,
            Atspi.Role.FILLER,
            Atspi.Role.REDUNDANT_OBJECT,
            Atspi.Role.UNKNOWN,
            Atspi.Role.SCROLL_PANE,
            Atspi.Role.TEAROFF_MENU_ITEM
        ]
        assert roles == expected

    def test_get_large_container_roles(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_large_container_roles."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_large_container_roles()
        expected = [
            Atspi.Role.ARTICLE,
            Atspi.Role.BLOCK_QUOTE,
            Atspi.Role.DESCRIPTION_LIST,
            Atspi.Role.FORM,
            Atspi.Role.FOOTER,
            Atspi.Role.GROUPING,
            Atspi.Role.HEADER,
            Atspi.Role.HTML_CONTAINER,
            Atspi.Role.LANDMARK,
            Atspi.Role.LOG,
            Atspi.Role.LIST,
            Atspi.Role.MARQUEE,
            Atspi.Role.PANEL,
            Atspi.Role.TABLE,
            Atspi.Role.TREE,
            Atspi.Role.TREE_TABLE
        ]
        assert roles == expected

    def test_get_roles_to_exclude_from_clickables_list(self, mock_orca_dependencies):
        """Test AXUtilitiesRole.get_roles_to_exclude_from_clickables_list."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_roles_to_exclude_from_clickables_list()
        expected = [
            Atspi.Role.COMBO_BOX,
            Atspi.Role.ENTRY,
            Atspi.Role.LIST_BOX,
            Atspi.Role.MENU,
            Atspi.Role.MENU_ITEM,
            Atspi.Role.CHECK_MENU_ITEM,
            Atspi.Role.RADIO_MENU_ITEM,
            Atspi.Role.PAGE_TAB,
            Atspi.Role.PAGE_TAB_LIST,
            Atspi.Role.PASSWORD_TEXT,
            Atspi.Role.PROGRESS_BAR,
            Atspi.Role.SLIDER,
            Atspi.Role.SPIN_BUTTON,
            Atspi.Role.TOOL_BAR,
            Atspi.Role.TREE_ITEM,
            Atspi.Role.TREE_TABLE,
            Atspi.Role.TREE
        ]
        assert roles == expected

    def test_is_dpub(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRole.is_dpub."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Has DPUB xml-role
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["doc-abstract"])
        assert AXUtilitiesRole.is_dpub(mock_obj)

        # Scenario: No DPUB xml-role
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["button"])
        assert not AXUtilitiesRole.is_dpub(mock_obj)

        # Scenario: No xml-roles
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: [])
        assert not AXUtilitiesRole.is_dpub(mock_obj)

    @pytest.mark.parametrize(
        "method_name, expected_xml_role",
        [
            ("is_dpub_abstract", "doc-abstract"),
            ("is_dpub_acknowledgments", "doc-acknowledgments"),
            ("is_dpub_afterword", "doc-afterword"),
            ("is_dpub_appendix", "doc-appendix"),
            ("is_dpub_backlink", "doc-backlink"),
            ("is_dpub_biblioref", "doc-biblioref"),
            ("is_dpub_bibliography", "doc-bibliography"),
            ("is_dpub_chapter", "doc-chapter"),
            ("is_dpub_colophon", "doc-colophon"),
            ("is_dpub_conclusion", "doc-conclusion"),
            ("is_dpub_cover", "doc-cover"),
            ("is_dpub_credit", "doc-credit"),
            ("is_dpub_credits", "doc-credits"),
            ("is_dpub_dedication", "doc-dedication"),
            ("is_dpub_endnote", "doc-endnote"),
            ("is_dpub_endnotes", "doc-endnotes"),
            ("is_dpub_epigraph", "doc-epigraph"),
            ("is_dpub_epilogue", "doc-epilogue"),
            ("is_dpub_errata", "doc-errata"),
            ("is_dpub_example", "doc-example"),
            ("is_dpub_footnote", "doc-footnote"),
            ("is_dpub_foreword", "doc-foreword"),
            ("is_dpub_glossary", "doc-glossary"),
            ("is_dpub_glossref", "doc-glossref"),
            ("is_dpub_index", "doc-index"),
            ("is_dpub_introduction", "doc-introduction"),
            ("is_dpub_noteref", "doc-noteref"),
            ("is_dpub_pagelist", "doc-pagelist"),
            ("is_dpub_pagebreak", "doc-pagebreak"),
            ("is_dpub_part", "doc-part"),
            ("is_dpub_preface", "doc-preface"),
            ("is_dpub_prologue", "doc-prologue"),
            ("is_dpub_pullquote", "doc-pullquote"),
            ("is_dpub_qna", "doc-qna"),
            ("is_dpub_subtitle", "doc-subtitle"),
            ("is_dpub_toc", "doc-toc"),
        ],
    )
    def test_dpub_methods(
        self, monkeypatch, mock_orca_dependencies, method_name, expected_xml_role
    ):
        """Test AXUtilitiesRole DPUB methods."""

        clean_module_cache("orca.ax_utilities_role")
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilitiesRole, method_name)

        # Scenario: Has expected DPUB xml-role
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: [expected_xml_role])
        assert method(mock_obj)

        # Scenario: Different DPUB xml-role
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: ["doc-other"])
        assert not method(mock_obj)

        # Scenario: No xml-roles
        monkeypatch.setattr(AXUtilitiesRole, "_get_xml_roles", lambda obj: [])
        assert not method(mock_obj)
