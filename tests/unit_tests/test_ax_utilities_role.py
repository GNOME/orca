# Unit tests for ax_utilities_role.py methods.
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

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for ax_utilities_role.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestAXUtilitiesRole:
    """Test AXUtilitiesRole class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_role dependencies."""

        additional_modules = ["orca.object_properties", "orca.ax_utilities_state"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        object_props_mock = essential_modules["orca.object_properties"]
        object_props_mock.ROLE_SLIDER_HORIZONTAL = "slider horizontal"
        object_props_mock.ROLE_SLIDER_VERTICAL = "slider vertical"
        object_props_mock.ROLE_SCROLL_BAR_HORIZONTAL = "scroll bar horizontal"
        object_props_mock.ROLE_SCROLL_BAR_VERTICAL = "scroll bar vertical"
        object_props_mock.ROLE_SPLITTER_HORIZONTAL = "splitter horizontal"
        object_props_mock.ROLE_SPLITTER_VERTICAL = "splitter vertical"
        object_props_mock.ROLE_CONTENT_SUGGESTION = "content suggestion"
        object_props_mock.ROLE_FEED = "feed"
        object_props_mock.ROLE_FIGURE = "figure"
        object_props_mock.ROLE_SWITCH = "switch"
        object_props_mock.ROLE_ACKNOWLEDGMENTS = "acknowledgments"
        object_props_mock.ROLE_ABSTRACT = "abstract"
        object_props_mock.ROLE_BIBLIOENTRY = "biblioentry"
        object_props_mock.ROLE_LANDMARK_BANNER = "banner"
        object_props_mock.ROLE_LANDMARK_COMPLEMENTARY = "complementary"
        object_props_mock.ROLE_LANDMARK_CONTENTINFO = "contentinfo"
        object_props_mock.ROLE_LANDMARK_MAIN = "main"
        object_props_mock.ROLE_LANDMARK_NAVIGATION = "navigation"
        object_props_mock.ROLE_LANDMARK_REGION = "region"
        object_props_mock.ROLE_LANDMARK_SEARCH = "search"

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.get_role = test_context.Mock(return_value=Atspi.Role.UNKNOWN)
        ax_object_class_mock.get_role_name = test_context.Mock(return_value="unknown")
        ax_object_class_mock.get_attributes_dict = test_context.Mock(return_value={})
        ax_object_class_mock.has_state = test_context.Mock(return_value=False)
        ax_object_class_mock.find_ancestor = test_context.Mock(return_value=None)
        ax_object_class_mock.find_descendant = test_context.Mock(return_value=None)
        ax_object_class_mock.supports_value = test_context.Mock(return_value=False)
        ax_object_class_mock.get_attribute = test_context.Mock(return_value=None)
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        state_class_mock = test_context.Mock()
        state_class_mock.has_popup = test_context.Mock(return_value=False)
        state_class_mock.is_editable = test_context.Mock(return_value=False)
        state_class_mock.is_single_line = test_context.Mock(return_value=False)
        state_class_mock.supports_autocompletion = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_state"].AXUtilitiesState = state_class_mock

        return essential_modules

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "color_chooser_role",
                "method_name": "is_color_chooser",
                "matching_role": Atspi.Role.COLOR_CHOOSER,
                "non_matching_role": Atspi.Role.BUTTON,
            },
            {
                "id": "column_header_role",
                "method_name": "is_column_header",
                "matching_role": Atspi.Role.COLUMN_HEADER,
                "non_matching_role": Atspi.Role.ROW_HEADER,
            },
            {
                "id": "alert_role",
                "method_name": "is_alert",
                "matching_role": Atspi.Role.ALERT,
                "non_matching_role": Atspi.Role.DIALOG,
            },
            {
                "id": "animation_role",
                "method_name": "is_animation",
                "matching_role": Atspi.Role.ANIMATION,
                "non_matching_role": Atspi.Role.IMAGE,
            },
            {
                "id": "application_role",
                "method_name": "is_application",
                "matching_role": Atspi.Role.APPLICATION,
                "non_matching_role": Atspi.Role.FRAME,
            },
            {
                "id": "arrow_role",
                "method_name": "is_arrow",
                "matching_role": Atspi.Role.ARROW,
                "non_matching_role": Atspi.Role.BUTTON,
            },
            {
                "id": "article_role",
                "method_name": "is_article",
                "matching_role": Atspi.Role.ARTICLE,
                "non_matching_role": Atspi.Role.SECTION,
            },
            {
                "id": "audio_role",
                "method_name": "is_audio",
                "matching_role": Atspi.Role.AUDIO,
                "non_matching_role": Atspi.Role.VIDEO,
            },
            {
                "id": "block_quote_role",
                "method_name": "is_block_quote",
                "matching_role": Atspi.Role.BLOCK_QUOTE,
                "non_matching_role": Atspi.Role.PARAGRAPH,
            },
            {
                "id": "calendar_role",
                "method_name": "is_calendar",
                "matching_role": Atspi.Role.CALENDAR,
                "non_matching_role": Atspi.Role.DATE_EDITOR,
            },
            {
                "id": "canvas_role",
                "method_name": "is_canvas",
                "matching_role": Atspi.Role.CANVAS,
                "non_matching_role": Atspi.Role.IMAGE,
            },
            {
                "id": "caption_role",
                "method_name": "is_caption",
                "matching_role": Atspi.Role.CAPTION,
                "non_matching_role": Atspi.Role.LABEL,
            },
            {
                "id": "chart_role",
                "method_name": "is_chart",
                "matching_role": Atspi.Role.CHART,
                "non_matching_role": Atspi.Role.IMAGE,
            },
            {
                "id": "check_box_role",
                "method_name": "is_check_box",
                "matching_role": Atspi.Role.CHECK_BOX,
                "non_matching_role": Atspi.Role.RADIO_BUTTON,
            },
            {
                "id": "check_menu_item_role",
                "method_name": "is_check_menu_item",
                "matching_role": Atspi.Role.CHECK_MENU_ITEM,
                "non_matching_role": Atspi.Role.MENU_ITEM,
            },
            {
                "id": "combo_box_role",
                "method_name": "is_combo_box",
                "matching_role": Atspi.Role.COMBO_BOX,
                "non_matching_role": Atspi.Role.LIST_BOX,
            },
            {
                "id": "date_editor_role",
                "method_name": "is_date_editor",
                "matching_role": Atspi.Role.DATE_EDITOR,
                "non_matching_role": Atspi.Role.SPIN_BUTTON,
            },
            {
                "id": "definition_role",
                "method_name": "is_definition",
                "matching_role": Atspi.Role.DEFINITION,
                "non_matching_role": Atspi.Role.DESCRIPTION_VALUE,
            },
            {
                "id": "description_list_role",
                "method_name": "is_description_list",
                "matching_role": Atspi.Role.DESCRIPTION_LIST,
                "non_matching_role": Atspi.Role.LIST,
            },
            {
                "id": "description_term_role",
                "method_name": "is_description_term",
                "matching_role": Atspi.Role.DESCRIPTION_TERM,
                "non_matching_role": Atspi.Role.DESCRIPTION_VALUE,
            },
            {
                "id": "description_value_role",
                "method_name": "is_description_value",
                "matching_role": Atspi.Role.DESCRIPTION_VALUE,
                "non_matching_role": Atspi.Role.DESCRIPTION_TERM,
            },
            {
                "id": "desktop_icon_role",
                "method_name": "is_desktop_icon",
                "matching_role": Atspi.Role.DESKTOP_ICON,
                "non_matching_role": Atspi.Role.ICON,
            },
            {
                "id": "dial_role",
                "method_name": "is_dial",
                "matching_role": Atspi.Role.DIAL,
                "non_matching_role": Atspi.Role.SLIDER,
            },
            {
                "id": "dialog_role",
                "method_name": "is_dialog",
                "matching_role": Atspi.Role.DIALOG,
                "non_matching_role": Atspi.Role.FRAME,
            },
            {
                "id": "directory_pane_role",
                "method_name": "is_directory_pane",
                "matching_role": Atspi.Role.DIRECTORY_PANE,
                "non_matching_role": Atspi.Role.TREE,
            },
            {
                "id": "document_email_role",
                "method_name": "is_document_email",
                "matching_role": Atspi.Role.DOCUMENT_EMAIL,
                "non_matching_role": Atspi.Role.DOCUMENT_TEXT,
            },
            {
                "id": "document_frame_role",
                "method_name": "is_document_frame",
                "matching_role": Atspi.Role.DOCUMENT_FRAME,
                "non_matching_role": Atspi.Role.FRAME,
            },
            {
                "id": "document_presentation_role",
                "method_name": "is_document_presentation",
                "matching_role": Atspi.Role.DOCUMENT_PRESENTATION,
                "non_matching_role": Atspi.Role.DOCUMENT_TEXT,
            },
            {
                "id": "document_spreadsheet_role",
                "method_name": "is_document_spreadsheet",
                "matching_role": Atspi.Role.DOCUMENT_SPREADSHEET,
                "non_matching_role": Atspi.Role.DOCUMENT_TEXT,
            },
            {
                "id": "document_text_role",
                "method_name": "is_document_text",
                "matching_role": Atspi.Role.DOCUMENT_TEXT,
                "non_matching_role": Atspi.Role.TEXT,
            },
            {
                "id": "document_web_role",
                "method_name": "is_document_web",
                "matching_role": Atspi.Role.DOCUMENT_WEB,
                "non_matching_role": Atspi.Role.DOCUMENT_TEXT,
            },
            {
                "id": "drawing_area_role",
                "method_name": "is_drawing_area",
                "matching_role": Atspi.Role.DRAWING_AREA,
                "non_matching_role": Atspi.Role.CANVAS,
            },
            {
                "id": "editbar_role",
                "method_name": "is_editbar",
                "matching_role": Atspi.Role.EDITBAR,
                "non_matching_role": Atspi.Role.TOOL_BAR,
            },
            {
                "id": "embedded_role",
                "method_name": "is_embedded",
                "matching_role": Atspi.Role.EMBEDDED,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "entry_role",
                "method_name": "is_entry",
                "matching_role": Atspi.Role.ENTRY,
                "non_matching_role": Atspi.Role.TEXT,
            },
            {
                "id": "extended_role",
                "method_name": "is_extended",
                "matching_role": Atspi.Role.EXTENDED,
                "non_matching_role": Atspi.Role.UNKNOWN,
            },
            {
                "id": "file_chooser_role",
                "method_name": "is_file_chooser",
                "matching_role": Atspi.Role.FILE_CHOOSER,
                "non_matching_role": Atspi.Role.DIALOG,
            },
            {
                "id": "filler_role",
                "method_name": "is_filler",
                "matching_role": Atspi.Role.FILLER,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "focus_traversable_role",
                "method_name": "is_focus_traversable",
                "matching_role": Atspi.Role.FOCUS_TRAVERSABLE,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "font_chooser_role",
                "method_name": "is_font_chooser",
                "matching_role": Atspi.Role.FONT_CHOOSER,
                "non_matching_role": Atspi.Role.COLOR_CHOOSER,
            },
            {
                "id": "footer_role",
                "method_name": "is_footer",
                "matching_role": Atspi.Role.FOOTER,
                "non_matching_role": Atspi.Role.HEADER,
            },
            {
                "id": "footnote_role",
                "method_name": "is_footnote",
                "matching_role": Atspi.Role.FOOTNOTE,
                "non_matching_role": Atspi.Role.STATIC,
            },
            {
                "id": "form_role",
                "method_name": "is_form",
                "matching_role": Atspi.Role.FORM,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "frame_role",
                "method_name": "is_frame",
                "matching_role": Atspi.Role.FRAME,
                "non_matching_role": Atspi.Role.WINDOW,
            },
            {
                "id": "glass_pane_role",
                "method_name": "is_glass_pane",
                "matching_role": Atspi.Role.GLASS_PANE,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "header_role",
                "method_name": "is_header",
                "matching_role": Atspi.Role.HEADER,
                "non_matching_role": Atspi.Role.FOOTER,
            },
            {
                "id": "heading_role",
                "method_name": "is_heading",
                "matching_role": Atspi.Role.HEADING,
                "non_matching_role": Atspi.Role.LABEL,
            },
            {
                "id": "html_container_role",
                "method_name": "is_html_container",
                "matching_role": Atspi.Role.HTML_CONTAINER,
                "non_matching_role": Atspi.Role.SECTION,
            },
            {
                "id": "icon_role",
                "method_name": "is_icon",
                "matching_role": Atspi.Role.ICON,
                "non_matching_role": Atspi.Role.IMAGE,
            },
            {
                "id": "image_role",
                "method_name": "is_image",
                "matching_role": Atspi.Role.IMAGE,
                "non_matching_role": Atspi.Role.ICON,
            },
            {
                "id": "image_map_role",
                "method_name": "is_image_map",
                "matching_role": Atspi.Role.IMAGE_MAP,
                "non_matching_role": Atspi.Role.IMAGE,
            },
            {
                "id": "info_bar_role",
                "method_name": "is_info_bar",
                "matching_role": Atspi.Role.INFO_BAR,
                "non_matching_role": Atspi.Role.TOOL_BAR,
            },
            {
                "id": "input_method_window_role",
                "method_name": "is_input_method_window",
                "matching_role": Atspi.Role.INPUT_METHOD_WINDOW,
                "non_matching_role": Atspi.Role.WINDOW,
            },
            {
                "id": "internal_frame_role",
                "method_name": "is_internal_frame",
                "matching_role": Atspi.Role.INTERNAL_FRAME,
                "non_matching_role": Atspi.Role.FRAME,
            },
            {
                "id": "invalid_role",
                "method_name": "is_invalid_role",
                "matching_role": Atspi.Role.INVALID,
                "non_matching_role": Atspi.Role.UNKNOWN,
            },
            {
                "id": "label_role",
                "method_name": "is_label",
                "matching_role": Atspi.Role.LABEL,
                "non_matching_role": Atspi.Role.STATIC,
            },
            {
                "id": "landmark_role",
                "method_name": "is_landmark",
                "matching_role": Atspi.Role.LANDMARK,
                "non_matching_role": Atspi.Role.SECTION,
            },
            {
                "id": "layered_pane_role",
                "method_name": "is_layered_pane",
                "matching_role": Atspi.Role.LAYERED_PANE,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "level_bar_role",
                "method_name": "is_level_bar",
                "matching_role": Atspi.Role.LEVEL_BAR,
                "non_matching_role": Atspi.Role.PROGRESS_BAR,
            },
            {
                "id": "link_role",
                "method_name": "is_link",
                "matching_role": Atspi.Role.LINK,
                "non_matching_role": Atspi.Role.TEXT,
            },
            {
                "id": "list_role",
                "method_name": "is_list",
                "matching_role": Atspi.Role.LIST,
                "non_matching_role": Atspi.Role.LIST_BOX,
            },
            {
                "id": "list_box_role",
                "method_name": "is_list_box",
                "matching_role": Atspi.Role.LIST_BOX,
                "non_matching_role": Atspi.Role.LIST,
            },
            {
                "id": "list_item_role",
                "method_name": "is_list_item",
                "matching_role": Atspi.Role.LIST_ITEM,
                "non_matching_role": Atspi.Role.LIST,
            },
            {
                "id": "log_role",
                "method_name": "is_log",
                "matching_role": Atspi.Role.LOG,
                "non_matching_role": Atspi.Role.TEXT,
            },
            {
                "id": "marquee_role",
                "method_name": "is_marquee",
                "matching_role": Atspi.Role.MARQUEE,
                "non_matching_role": Atspi.Role.ANIMATION,
            },
            {
                "id": "math_role",
                "method_name": "is_math",
                "matching_role": Atspi.Role.MATH,
                "non_matching_role": Atspi.Role.STATIC,
            },
            {
                "id": "math_fraction_role",
                "method_name": "is_math_fraction",
                "matching_role": Atspi.Role.MATH_FRACTION,
                "non_matching_role": Atspi.Role.MATH,
            },
            {
                "id": "math_root_role",
                "method_name": "is_math_root",
                "matching_role": Atspi.Role.MATH_ROOT,
                "non_matching_role": Atspi.Role.MATH,
            },
            {
                "id": "menu_role",
                "method_name": "is_menu",
                "matching_role": Atspi.Role.MENU,
                "non_matching_role": Atspi.Role.MENU_BAR,
            },
            {
                "id": "menu_bar_role",
                "method_name": "is_menu_bar",
                "matching_role": Atspi.Role.MENU_BAR,
                "non_matching_role": Atspi.Role.MENU,
            },
            {
                "id": "menu_item_role",
                "method_name": "is_menu_item",
                "matching_role": Atspi.Role.MENU_ITEM,
                "non_matching_role": Atspi.Role.CHECK_MENU_ITEM,
            },
            {
                "id": "notification_role",
                "method_name": "is_notification",
                "matching_role": Atspi.Role.NOTIFICATION,
                "non_matching_role": Atspi.Role.ALERT,
            },
            {
                "id": "option_pane_role",
                "method_name": "is_option_pane",
                "matching_role": Atspi.Role.OPTION_PANE,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "page_role",
                "method_name": "is_page",
                "matching_role": Atspi.Role.PAGE,
                "non_matching_role": Atspi.Role.SECTION,
            },
            {
                "id": "page_tab_role",
                "method_name": "is_page_tab",
                "matching_role": Atspi.Role.PAGE_TAB,
                "non_matching_role": Atspi.Role.PAGE_TAB_LIST,
            },
            {
                "id": "page_tab_list_role",
                "method_name": "is_page_tab_list",
                "matching_role": Atspi.Role.PAGE_TAB_LIST,
                "non_matching_role": Atspi.Role.PAGE_TAB,
            },
            {
                "id": "panel_role",
                "method_name": "is_panel",
                "matching_role": Atspi.Role.PANEL,
                "non_matching_role": Atspi.Role.FILLER,
            },
            {
                "id": "paragraph_role",
                "method_name": "is_paragraph",
                "matching_role": Atspi.Role.PARAGRAPH,
                "non_matching_role": Atspi.Role.TEXT,
            },
            {
                "id": "password_text_role",
                "method_name": "is_password_text",
                "matching_role": Atspi.Role.PASSWORD_TEXT,
                "non_matching_role": Atspi.Role.TEXT,
            },
            {
                "id": "popup_menu_role",
                "method_name": "is_popup_menu",
                "matching_role": Atspi.Role.POPUP_MENU,
                "non_matching_role": Atspi.Role.MENU,
            },
            {
                "id": "progress_bar_role",
                "method_name": "is_progress_bar",
                "matching_role": Atspi.Role.PROGRESS_BAR,
                "non_matching_role": Atspi.Role.LEVEL_BAR,
            },
            {
                "id": "push_button_role",
                "method_name": "is_push_button",
                "matching_role": Atspi.Role.BUTTON,
                "non_matching_role": Atspi.Role.TOGGLE_BUTTON,
            },
            {
                "id": "push_button_menu_role",
                "method_name": "is_push_button_menu",
                "matching_role": Atspi.Role.PUSH_BUTTON_MENU,
                "non_matching_role": Atspi.Role.BUTTON,
            },
            {
                "id": "radio_button_role",
                "method_name": "is_radio_button",
                "matching_role": Atspi.Role.RADIO_BUTTON,
                "non_matching_role": Atspi.Role.CHECK_BOX,
            },
            {
                "id": "radio_menu_item_role",
                "method_name": "is_radio_menu_item",
                "matching_role": Atspi.Role.RADIO_MENU_ITEM,
                "non_matching_role": Atspi.Role.CHECK_MENU_ITEM,
            },
            {
                "id": "rating_role",
                "method_name": "is_rating",
                "matching_role": Atspi.Role.RATING,
                "non_matching_role": Atspi.Role.SLIDER,
            },
            {
                "id": "redundant_object_role",
                "method_name": "is_redundant_object_role",
                "matching_role": Atspi.Role.REDUNDANT_OBJECT,
                "non_matching_role": Atspi.Role.UNKNOWN,
            },
            {
                "id": "root_pane_role",
                "method_name": "is_root_pane",
                "matching_role": Atspi.Role.ROOT_PANE,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "row_header_role",
                "method_name": "is_row_header",
                "matching_role": Atspi.Role.ROW_HEADER,
                "non_matching_role": Atspi.Role.COLUMN_HEADER,
            },
            {
                "id": "ruler_role",
                "method_name": "is_ruler",
                "matching_role": Atspi.Role.RULER,
                "non_matching_role": Atspi.Role.SEPARATOR,
            },
            {
                "id": "scroll_bar_role",
                "method_name": "is_scroll_bar",
                "matching_role": Atspi.Role.SCROLL_BAR,
                "non_matching_role": Atspi.Role.SLIDER,
            },
            {
                "id": "scroll_pane_role",
                "method_name": "is_scroll_pane",
                "matching_role": Atspi.Role.SCROLL_PANE,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "section_role",
                "method_name": "is_section",
                "matching_role": Atspi.Role.SECTION,
                "non_matching_role": Atspi.Role.ARTICLE,
            },
            {
                "id": "separator_role",
                "method_name": "is_separator",
                "matching_role": Atspi.Role.SEPARATOR,
                "non_matching_role": Atspi.Role.RULER,
            },
            {
                "id": "slider_role",
                "method_name": "is_slider",
                "matching_role": Atspi.Role.SLIDER,
                "non_matching_role": Atspi.Role.SCROLL_BAR,
            },
            {
                "id": "spin_button_role",
                "method_name": "is_spin_button",
                "matching_role": Atspi.Role.SPIN_BUTTON,
                "non_matching_role": Atspi.Role.ENTRY,
            },
            {
                "id": "split_pane_role",
                "method_name": "is_split_pane",
                "matching_role": Atspi.Role.SPLIT_PANE,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "static_role",
                "method_name": "is_static",
                "matching_role": Atspi.Role.STATIC,
                "non_matching_role": Atspi.Role.LABEL,
            },
            {
                "id": "status_bar_role",
                "method_name": "is_status_bar",
                "matching_role": Atspi.Role.STATUS_BAR,
                "non_matching_role": Atspi.Role.TOOL_BAR,
            },
            {
                "id": "subscript_role",
                "method_name": "is_subscript",
                "matching_role": Atspi.Role.SUBSCRIPT,
                "non_matching_role": Atspi.Role.SUPERSCRIPT,
            },
            {
                "id": "superscript_role",
                "method_name": "is_superscript",
                "matching_role": Atspi.Role.SUPERSCRIPT,
                "non_matching_role": Atspi.Role.SUBSCRIPT,
            },
            {
                "id": "table_role",
                "method_name": "is_table",
                "matching_role": Atspi.Role.TABLE,
                "non_matching_role": Atspi.Role.TREE_TABLE,
            },
            {
                "id": "table_cell_role",
                "method_name": "is_table_cell",
                "matching_role": Atspi.Role.TABLE_CELL,
                "non_matching_role": Atspi.Role.COLUMN_HEADER,
            },
            {
                "id": "terminal_role",
                "method_name": "is_terminal",
                "matching_role": Atspi.Role.TERMINAL,
                "non_matching_role": Atspi.Role.TEXT,
            },
            {
                "id": "text_role",
                "method_name": "is_text",
                "matching_role": Atspi.Role.TEXT,
                "non_matching_role": Atspi.Role.LABEL,
            },
            {
                "id": "timer_role",
                "method_name": "is_timer",
                "matching_role": Atspi.Role.TIMER,
                "non_matching_role": Atspi.Role.STATIC,
            },
            {
                "id": "title_bar_role",
                "method_name": "is_title_bar",
                "matching_role": Atspi.Role.TITLE_BAR,
                "non_matching_role": Atspi.Role.TOOL_BAR,
            },
            {
                "id": "toggle_button_role",
                "method_name": "is_toggle_button",
                "matching_role": Atspi.Role.TOGGLE_BUTTON,
                "non_matching_role": Atspi.Role.BUTTON,
            },
            {
                "id": "tool_bar_role",
                "method_name": "is_tool_bar",
                "matching_role": Atspi.Role.TOOL_BAR,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "tool_tip_role",
                "method_name": "is_tool_tip",
                "matching_role": Atspi.Role.TOOL_TIP,
                "non_matching_role": Atspi.Role.LABEL,
            },
            {
                "id": "tree_role",
                "method_name": "is_tree",
                "matching_role": Atspi.Role.TREE,
                "non_matching_role": Atspi.Role.TREE_TABLE,
            },
            {
                "id": "tree_item_role",
                "method_name": "is_tree_item",
                "matching_role": Atspi.Role.TREE_ITEM,
                "non_matching_role": Atspi.Role.LIST_ITEM,
            },
            {
                "id": "tree_table_role",
                "method_name": "is_tree_table",
                "matching_role": Atspi.Role.TREE_TABLE,
                "non_matching_role": Atspi.Role.TABLE,
            },
            {
                "id": "unknown_role",
                "method_name": "is_unknown",
                "matching_role": Atspi.Role.UNKNOWN,
                "non_matching_role": Atspi.Role.INVALID,
            },
            {
                "id": "video_role",
                "method_name": "is_video",
                "matching_role": Atspi.Role.VIDEO,
                "non_matching_role": Atspi.Role.AUDIO,
            },
            {
                "id": "viewport_role",
                "method_name": "is_viewport",
                "matching_role": Atspi.Role.VIEWPORT,
                "non_matching_role": Atspi.Role.PANEL,
            },
            {
                "id": "window_role",
                "method_name": "is_window",
                "matching_role": Atspi.Role.WINDOW,
                "non_matching_role": Atspi.Role.FRAME,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_simple_role_methods(self, test_context, case: dict) -> None:
        """Test AXUtilitiesRole simple role methods."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_role = test_context.Mock(return_value=case["matching_role"])
        from orca.ax_utilities_role import AXUtilitiesRole

        method = getattr(AXUtilitiesRole, case["method_name"])
        assert method(mock_obj)
        mock_ax_object_class.get_role = test_context.Mock(return_value=case["non_matching_role"])

        method = getattr(AXUtilitiesRole, case["method_name"])
        assert not method(mock_obj)

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "push_button_true", "role": Atspi.Role.BUTTON, "expected": True},
            {"id": "toggle_button_true", "role": Atspi.Role.TOGGLE_BUTTON, "expected": True},
            {"id": "label_false", "role": Atspi.Role.LABEL, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_button(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRole.is_button with various roles."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_role = test_context.Mock(return_value=case["role"])
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilitiesRole.is_button(mock_obj)
        assert result is case["expected"]

    def test_children_are_presentational(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.children_are_presentational."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.BUTTON)
        from orca.ax_utilities_role import AXUtilitiesRole

        assert AXUtilitiesRole.children_are_presentational(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.SWITCH)
        assert AXUtilitiesRole.children_are_presentational(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.LABEL)
        assert not AXUtilitiesRole.children_are_presentational(mock_obj)

    def test_get_localized_role_name_with_atspi_role(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_localized_role_name with standard Atspi.Role."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )
        if hasattr(Atspi, "role_get_localized_name"):
            test_context.patch_object(
                Atspi, "role_get_localized_name", return_value="LocalizedRole"
            )
        else:
            test_context.patch_object(Atspi, "role_get_name", return_value="LocalizedRole")
        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.BUTTON)
            == "LocalizedRole"
        )

    def test_get_localized_role_name_with_non_atspi_role(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name with non-Atspi.Role value."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.get_role_name = test_context.Mock(return_value="role_name")
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        assert AXUtilitiesRole.get_localized_role_name(mock_obj, "not_a_role") == "role_name"

    def test_get_localized_role_name_with_dpub_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_localized_role_name for DPUB roles."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=True)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=True
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_dpub_acknowledgments", return_value=True
        )
        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.LANDMARK)
            == object_properties.ROLE_ACKNOWLEDGMENTS
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_dpub_abstract", return_value=True
        )
        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, "ROLE_DPUB_SECTION")
            == object_properties.ROLE_ABSTRACT
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_list_item", return_value=True
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_dpub_biblioref", return_value=True
        )
        assert (
            AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.LIST_ITEM)
            == object_properties.ROLE_BIBLIOENTRY
        )

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "horizontal_slider",
                "supports_value": True,
                "role_check_method": "is_horizontal_slider",
                "role": Atspi.Role.SLIDER,
                "expected_result": "object_properties.ROLE_SLIDER_HORIZONTAL",
            },
            {
                "id": "vertical_slider",
                "supports_value": True,
                "role_check_method": "is_vertical_slider",
                "role": Atspi.Role.SLIDER,
                "expected_result": "object_properties.ROLE_SLIDER_VERTICAL",
            },
            {
                "id": "horizontal_scrollbar",
                "supports_value": True,
                "role_check_method": "is_horizontal_scrollbar",
                "role": Atspi.Role.SCROLL_BAR,
                "expected_result": "object_properties.ROLE_SCROLL_BAR_HORIZONTAL",
            },
            {
                "id": "vertical_scrollbar",
                "supports_value": True,
                "role_check_method": "is_vertical_scrollbar",
                "role": Atspi.Role.SCROLL_BAR,
                "expected_result": "object_properties.ROLE_SCROLL_BAR_VERTICAL",
            },
            {
                "id": "horizontal_separator",
                "supports_value": True,
                "role_check_method": "is_horizontal_separator",
                "role": Atspi.Role.SEPARATOR,
                "expected_result": "object_properties.ROLE_SPLITTER_HORIZONTAL",
            },
            {
                "id": "vertical_separator",
                "supports_value": True,
                "role_check_method": "is_vertical_separator",
                "role": Atspi.Role.SEPARATOR,
                "expected_result": "object_properties.ROLE_SPLITTER_VERTICAL",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_localized_role_name_value_based_roles(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name for value-based roles."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=case["supports_value"])
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        role_methods = [
            "is_horizontal_slider",
            "is_vertical_slider",
            "is_horizontal_scrollbar",
            "is_vertical_scrollbar",
            "is_horizontal_separator",
            "is_vertical_separator",
            "is_split_pane",
        ]
        for method in role_methods:
            test_context.patch_object(
                AXUtilitiesRole,
                method,
                side_effect=lambda obj, role=None, m=method: m == case["role_check_method"],
            )

        test_context.patch_object(
            AXUtilitiesRole, "is_suggestion", return_value=False
        )
        test_context.patch_object(AXUtilitiesRole, "is_feed", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_figure", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_switch", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj, case["role"])
        expected = getattr(object_properties, case["expected_result"].split(".")[1])
        assert result == expected

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "horizontal_state",
                "has_horizontal_state": True,
                "has_vertical_state": False,
                "expected_result": "object_properties.ROLE_SPLITTER_VERTICAL",
            },
            {
                "id": "vertical_state",
                "has_horizontal_state": False,
                "has_vertical_state": True,
                "expected_result": "object_properties.ROLE_SPLITTER_HORIZONTAL",
            },
            {
                "id": "no_orientation",
                "has_horizontal_state": False,
                "has_vertical_state": False,
                "expected_result": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_localized_role_name_split_pane_orientation(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name for split pane orientation."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=True)
        mock_ax_object_class.has_state = test_context.Mock(
            side_effect=lambda obj, state: (
                state == Atspi.StateType.HORIZONTAL
                and case["has_horizontal_state"]
                or state == Atspi.StateType.VERTICAL
                and case["has_vertical_state"]
            )
        )
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_split_pane", return_value=True
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_horizontal_slider", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_vertical_slider", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_horizontal_scrollbar", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_vertical_scrollbar", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_horizontal_separator", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_vertical_separator", return_value=False
        )

        test_context.patch_object(
            AXUtilitiesRole, "is_suggestion", return_value=False
        )
        test_context.patch_object(AXUtilitiesRole, "is_feed", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_figure", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_switch", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )
        test_context.patch_object(
            Atspi, "role_get_localized_name", return_value="fallback_role"
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.SPLIT_PANE)
        if case["expected_result"]:
            expected = getattr(object_properties, case["expected_result"].split(".")[1])
            assert result == expected
        else:
            assert result == "fallback_role"

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "suggestion",
                "role_check_method": "is_suggestion",
                "expected_result": "object_properties.ROLE_CONTENT_SUGGESTION",
            },
            {
                "id": "feed",
                "role_check_method": "is_feed",
                "expected_result": "object_properties.ROLE_FEED",
            },
            {
                "id": "figure",
                "role_check_method": "is_figure",
                "expected_result": "object_properties.ROLE_FIGURE",
            },
            {
                "id": "switch",
                "role_check_method": "is_switch",
                "expected_result": "object_properties.ROLE_SWITCH",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_localized_role_name_simple_roles(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name for simple role mappings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        simple_methods = ["is_suggestion", "is_feed", "is_figure", "is_switch"]
        for method in simple_methods:
            test_context.patch_object(
                AXUtilitiesRole,
                method,
                side_effect=lambda obj, role=None, m=method: m == case["role_check_method"],
            )

        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.UNKNOWN)
        expected = getattr(object_properties, case["expected_result"].split(".")[1])
        assert result == expected

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "landmark_banner",
                "role_check_method": "is_landmark_banner",
                "expected_result": "object_properties.ROLE_LANDMARK_BANNER",
            },
            {
                "id": "landmark_complementary",
                "role_check_method": "is_landmark_complementary",
                "expected_result": "object_properties.ROLE_LANDMARK_COMPLEMENTARY",
            },
            {
                "id": "landmark_contentinfo",
                "role_check_method": "is_landmark_contentinfo",
                "expected_result": "object_properties.ROLE_LANDMARK_CONTENTINFO",
            },
            {
                "id": "landmark_main",
                "role_check_method": "is_landmark_main",
                "expected_result": "object_properties.ROLE_LANDMARK_MAIN",
            },
            {
                "id": "landmark_navigation",
                "role_check_method": "is_landmark_navigation",
                "expected_result": "object_properties.ROLE_LANDMARK_NAVIGATION",
            },
            {
                "id": "landmark_region",
                "role_check_method": "is_landmark_region",
                "expected_result": "object_properties.ROLE_LANDMARK_REGION",
            },
            {
                "id": "landmark_search",
                "role_check_method": "is_landmark_search",
                "expected_result": "object_properties.ROLE_LANDMARK_SEARCH",
            },
            {
                "id": "landmark_without_type",
                "role_check_method": "is_landmark_without_type",
                "expected_result": "",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_localized_role_name_landmark_roles(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name for landmark roles."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=True
        )

        landmark_methods = [
            "is_landmark_without_type",
            "is_landmark_banner",
            "is_landmark_complementary",
            "is_landmark_contentinfo",
            "is_landmark_main",
            "is_landmark_navigation",
            "is_landmark_region",
            "is_landmark_search",
            "is_landmark_form",
        ]
        for method in landmark_methods:
            test_context.patch_object(
                AXUtilitiesRole,
                method,
                side_effect=lambda obj, role=None, m=method: m == case["role_check_method"],
            )

        test_context.patch_object(
            AXUtilitiesRole, "is_suggestion", return_value=False
        )
        test_context.patch_object(AXUtilitiesRole, "is_feed", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_figure", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_switch", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.LANDMARK)
        if case["expected_result"]:
            if case["expected_result"] == "":
                assert result == ""
            else:
                expected = getattr(object_properties, case["expected_result"].split(".")[1])
                assert result == expected

    def test_get_localized_role_name_landmark_form_fallback(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name landmark form fallback to FORM role."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=True
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_form", return_value=True
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_without_type", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_banner", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_complementary", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_contentinfo", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_main", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_navigation", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_region", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark_search", return_value=False
        )

        test_context.patch_object(
            AXUtilitiesRole, "is_suggestion", return_value=False
        )
        test_context.patch_object(AXUtilitiesRole, "is_feed", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_figure", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_switch", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )
        test_context.patch_object(
            Atspi, "role_get_localized_name", return_value="form_localized"
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.LANDMARK)
        assert result == "form_localized"

    def test_get_localized_role_name_comment_fallback(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_localized_role_name comment fallback to COMMENT role."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesRole, "is_comment", return_value=True)
        test_context.patch_object(
            AXUtilitiesRole, "is_suggestion", return_value=False
        )
        test_context.patch_object(AXUtilitiesRole, "is_feed", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_figure", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_switch", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        test_context.patch_object(
            Atspi, "role_get_localized_name", return_value="comment_localized"
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj, Atspi.Role.SECTION)
        assert result == "comment_localized"

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "dpub_acknowledgments",
                "dpub_method": "is_dpub_acknowledgments",
                "expected_result": "object_properties.ROLE_ACKNOWLEDGMENTS",
                "role_context": "landmark",
            },
            {
                "id": "dpub_afterword",
                "dpub_method": "is_dpub_afterword",
                "expected_result": "object_properties.ROLE_AFTERWORD",
                "role_context": "landmark",
            },
            {
                "id": "dpub_appendix",
                "dpub_method": "is_dpub_appendix",
                "expected_result": "object_properties.ROLE_APPENDIX",
                "role_context": "landmark",
            },
            {
                "id": "dpub_bibliography",
                "dpub_method": "is_dpub_bibliography",
                "expected_result": "object_properties.ROLE_BIBLIOGRAPHY",
                "role_context": "landmark",
            },
            {
                "id": "dpub_chapter",
                "dpub_method": "is_dpub_chapter",
                "expected_result": "object_properties.ROLE_CHAPTER",
                "role_context": "landmark",
            },
            {
                "id": "dpub_conclusion",
                "dpub_method": "is_dpub_conclusion",
                "expected_result": "object_properties.ROLE_CONCLUSION",
                "role_context": "landmark",
            },
            {
                "id": "dpub_credits",
                "dpub_method": "is_dpub_credits",
                "expected_result": "object_properties.ROLE_CREDITS",
                "role_context": "landmark",
            },
            {
                "id": "dpub_endnotes",
                "dpub_method": "is_dpub_endnotes",
                "expected_result": "object_properties.ROLE_ENDNOTES",
                "role_context": "landmark",
            },
            {
                "id": "dpub_epilogue",
                "dpub_method": "is_dpub_epilogue",
                "expected_result": "object_properties.ROLE_EPILOGUE",
                "role_context": "landmark",
            },
            {
                "id": "dpub_errata",
                "dpub_method": "is_dpub_errata",
                "expected_result": "object_properties.ROLE_ERRATA",
                "role_context": "landmark",
            },
            {
                "id": "dpub_foreword",
                "dpub_method": "is_dpub_foreword",
                "expected_result": "object_properties.ROLE_FOREWORD",
                "role_context": "landmark",
            },
            {
                "id": "dpub_glossary",
                "dpub_method": "is_dpub_glossary",
                "expected_result": "object_properties.ROLE_GLOSSARY",
                "role_context": "landmark",
            },
            {
                "id": "dpub_index",
                "dpub_method": "is_dpub_index",
                "expected_result": "object_properties.ROLE_INDEX",
                "role_context": "landmark",
            },
            {
                "id": "dpub_introduction",
                "dpub_method": "is_dpub_introduction",
                "expected_result": "object_properties.ROLE_INTRODUCTION",
                "role_context": "landmark",
            },
            {
                "id": "dpub_pagelist",
                "dpub_method": "is_dpub_pagelist",
                "expected_result": "object_properties.ROLE_PAGELIST",
                "role_context": "landmark",
            },
            {
                "id": "dpub_part",
                "dpub_method": "is_dpub_part",
                "expected_result": "object_properties.ROLE_PART",
                "role_context": "landmark",
            },
            {
                "id": "dpub_preface",
                "dpub_method": "is_dpub_preface",
                "expected_result": "object_properties.ROLE_PREFACE",
                "role_context": "landmark",
            },
            {
                "id": "dpub_prologue",
                "dpub_method": "is_dpub_prologue",
                "expected_result": "object_properties.ROLE_PROLOGUE",
                "role_context": "landmark",
            },
            {
                "id": "dpub_toc",
                "dpub_method": "is_dpub_toc",
                "expected_result": "object_properties.ROLE_TOC",
                "role_context": "landmark",
            },
            {
                "id": "dpub_abstract",
                "dpub_method": "is_dpub_abstract",
                "expected_result": "object_properties.ROLE_ABSTRACT",
                "role_context": "section",
            },
            {
                "id": "dpub_colophon",
                "dpub_method": "is_dpub_colophon",
                "expected_result": "object_properties.ROLE_COLOPHON",
                "role_context": "section",
            },
            {
                "id": "dpub_credit",
                "dpub_method": "is_dpub_credit",
                "expected_result": "object_properties.ROLE_CREDIT",
                "role_context": "section",
            },
            {
                "id": "dpub_dedication",
                "dpub_method": "is_dpub_dedication",
                "expected_result": "object_properties.ROLE_DEDICATION",
                "role_context": "section",
            },
            {
                "id": "dpub_epigraph",
                "dpub_method": "is_dpub_epigraph",
                "expected_result": "object_properties.ROLE_EPIGRAPH",
                "role_context": "section",
            },
            {
                "id": "dpub_example",
                "dpub_method": "is_dpub_example",
                "expected_result": "object_properties.ROLE_EXAMPLE",
                "role_context": "section",
            },
            {
                "id": "dpub_pullquote",
                "dpub_method": "is_dpub_pullquote",
                "expected_result": "object_properties.ROLE_PULLQUOTE",
                "role_context": "section",
            },
            {
                "id": "dpub_qna",
                "dpub_method": "is_dpub_qna",
                "expected_result": "object_properties.ROLE_QNA",
                "role_context": "section",
            },
            {
                "id": "dpub_biblioref",
                "dpub_method": "is_dpub_biblioref",
                "expected_result": "object_properties.ROLE_BIBLIOENTRY",
                "role_context": "list_item",
            },
            {
                "id": "dpub_endnote",
                "dpub_method": "is_dpub_endnote",
                "expected_result": "object_properties.ROLE_ENDNOTE",
                "role_context": "list_item",
            },
            {
                "id": "dpub_cover",
                "dpub_method": "is_dpub_cover",
                "expected_result": "object_properties.ROLE_COVER",
                "role_context": "other",
            },
            {
                "id": "dpub_pagebreak",
                "dpub_method": "is_dpub_pagebreak",
                "expected_result": "object_properties.ROLE_PAGEBREAK",
                "role_context": "other",
            },
            {
                "id": "dpub_subtitle",
                "dpub_method": "is_dpub_subtitle",
                "expected_result": "object_properties.ROLE_SUBTITLE",
                "role_context": "other",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_localized_role_name_dpub_roles_comprehensive(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name for all DPUB role types."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=True)
        if case["role_context"] == "landmark":
            test_context.patch_object(
                AXUtilitiesRole, "is_landmark", return_value=True
            )
            test_context.patch_object(
                AXUtilitiesRole, "is_list_item", return_value=False
            )
            role_param = Atspi.Role.LANDMARK
        elif case["role_context"] == "section":
            test_context.patch_object(
                AXUtilitiesRole, "is_landmark", return_value=False
            )
            test_context.patch_object(
                AXUtilitiesRole, "is_list_item", return_value=False
            )
            role_param = "ROLE_DPUB_SECTION"
        elif case["role_context"] == "list_item":
            test_context.patch_object(
                AXUtilitiesRole, "is_landmark", return_value=False
            )
            test_context.patch_object(
                AXUtilitiesRole, "is_list_item", return_value=True
            )
            role_param = Atspi.Role.LIST_ITEM
        else:
            test_context.patch_object(
                AXUtilitiesRole, "is_landmark", return_value=False
            )
            test_context.patch_object(
                AXUtilitiesRole, "is_list_item", return_value=False
            )
            role_param = Atspi.Role.UNKNOWN

        dpub_methods = [
            "is_dpub_acknowledgments",
            "is_dpub_afterword",
            "is_dpub_appendix",
            "is_dpub_bibliography",
            "is_dpub_chapter",
            "is_dpub_conclusion",
            "is_dpub_credits",
            "is_dpub_endnotes",
            "is_dpub_epilogue",
            "is_dpub_errata",
            "is_dpub_foreword",
            "is_dpub_glossary",
            "is_dpub_index",
            "is_dpub_introduction",
            "is_dpub_pagelist",
            "is_dpub_part",
            "is_dpub_preface",
            "is_dpub_prologue",
            "is_dpub_toc",
            "is_dpub_abstract",
            "is_dpub_colophon",
            "is_dpub_credit",
            "is_dpub_dedication",
            "is_dpub_epigraph",
            "is_dpub_example",
            "is_dpub_pullquote",
            "is_dpub_qna",
            "is_dpub_biblioref",
            "is_dpub_endnote",
            "is_dpub_cover",
            "is_dpub_pagebreak",
            "is_dpub_subtitle",
        ]
        for method in dpub_methods:
            test_context.patch_object(
                AXUtilitiesRole,
                method,
                side_effect=lambda obj, role=None, m=method: m == case["dpub_method"],
            )

        test_context.patch_object(
            AXUtilitiesRole, "is_suggestion", return_value=False
        )
        test_context.patch_object(AXUtilitiesRole, "is_feed", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_figure", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_switch", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj, role_param)
        expected = getattr(object_properties, case["expected_result"].split(".")[1])
        assert result == expected

    def test_get_localized_role_name_no_role_provided_uses_ax_object_get_role(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilitiesRole.get_localized_role_name without role parameter."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        mock_ax_object_class.supports_value = test_context.Mock(return_value=False)
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.BUTTON)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_suggestion", return_value=False
        )
        test_context.patch_object(AXUtilitiesRole, "is_feed", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_figure", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_switch", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_dpub", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_comment", return_value=False
        )
        test_context.patch_object(
            Atspi, "role_get_localized_name", return_value="button_localized"
        )

        result = AXUtilitiesRole.get_localized_role_name(mock_obj)
        assert result == "button_localized"
        mock_ax_object_class.get_role.assert_called_once_with(mock_obj)

    def test_is_grid(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_grid."""

        self._setup_dependencies(test_context)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        from orca.ax_utilities_role import AXUtilitiesRole

        test_context.patch_object(AXUtilitiesRole, "is_table", return_value=False)
        assert not AXUtilitiesRole.is_grid(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "is_table", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "_get_xml_roles", return_value=[])
        assert not AXUtilitiesRole.is_grid(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "_get_xml_roles", return_value=["grid"])
        assert AXUtilitiesRole.is_grid(mock_obj)

    def test_is_grid_cell(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_grid_cell."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=None)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_table_cell", return_value=False
        )
        assert not AXUtilitiesRole.is_grid_cell(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_table_cell", return_value=True
        )
        test_context.patch_object(
            AXUtilitiesRole, "_get_xml_roles", return_value=["gridcell"]
        )
        assert AXUtilitiesRole.is_grid_cell(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "_get_xml_roles", return_value=["cell"])
        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=test_context.Mock())
        assert AXUtilitiesRole.is_grid_cell(mock_obj)

        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=None)
        assert not AXUtilitiesRole.is_grid_cell(mock_obj)

    def test_is_editable_combo_box(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_editable_combo_box."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.LABEL)
        mock_ax_object_class.find_descendant = test_context.Mock(return_value=None)
        mock_utilities_state_class = essential_modules["orca.ax_utilities_state"].AXUtilitiesState
        mock_utilities_state_class.is_editable = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.LABEL)
        assert not AXUtilitiesRole.is_editable_combo_box(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.COMBO_BOX)
        mock_utilities_state_class.is_editable = test_context.Mock(return_value=True)
        assert AXUtilitiesRole.is_editable_combo_box(mock_obj)

        mock_utilities_state_class.is_editable = test_context.Mock(return_value=False)
        mock_ax_object_class.find_descendant = test_context.Mock(return_value=test_context.Mock())
        assert AXUtilitiesRole.is_editable_combo_box(mock_obj)

        mock_ax_object_class.find_descendant = test_context.Mock(return_value=None)
        assert not AXUtilitiesRole.is_editable_combo_box(mock_obj)

    def test_is_feed_article(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_feed_article."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=None)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_article", return_value=False
        )
        assert not AXUtilitiesRole.is_feed_article(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "is_article", return_value=True)
        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=None)
        assert not AXUtilitiesRole.is_feed_article(mock_obj)

        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=test_context.Mock())
        assert AXUtilitiesRole.is_feed_article(mock_obj)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "internal_frame",
                "method_name": "is_inline_internal_frame",
                "base_method_name": "is_internal_frame",
            },
            {
                "id": "list_item",
                "method_name": "is_inline_list_item",
                "base_method_name": "is_list_item",
            },
            {
                "id": "suggestion",
                "method_name": "is_inline_suggestion",
                "base_method_name": "is_suggestion",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_inline_methods(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test is_inline_* methods for base role check and display style."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        method_to_test = getattr(AXUtilitiesRole, case["method_name"])
        test_context.patch_object(
            AXUtilitiesRole, case["base_method_name"], return_value=False
        )
        assert not method_to_test(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, case["base_method_name"], return_value=True
        )
        test_context.patch_object(AXUtilitiesRole, "_get_display_style", return_value="block")
        assert not method_to_test(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "_get_display_style", return_value="inline"
        )
        assert method_to_test(mock_obj)

    def test_is_list_box_item(self, test_context: OrcaTestContext) -> None:
        """Test is_list_box_item for list item and list box ancestor."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=None)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_list_item", return_value=False
        )
        assert not AXUtilitiesRole.is_list_box_item(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_list_item", return_value=True
        )
        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=None)
        assert not AXUtilitiesRole.is_list_box_item(mock_obj)

        mock_ax_object_class.find_ancestor = test_context.Mock(return_value=test_context.Mock())
        assert AXUtilitiesRole.is_list_box_item(mock_obj)

    def test_is_math_fraction_without_bar(self, test_context: OrcaTestContext) -> None:
        """Test is_math_fraction_without_bar for math fraction and linethickness."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attribute = test_context.Mock(return_value=None)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_math_fraction", return_value=False
        )
        assert not AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_math_fraction", return_value=True
        )
        mock_ax_object_class.get_attribute = test_context.Mock(return_value=None)
        assert not AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

        mock_ax_object_class.get_attribute = test_context.Mock(return_value="2")
        assert not AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

        mock_ax_object_class.get_attribute = test_context.Mock(return_value="00")
        assert AXUtilitiesRole.is_math_fraction_without_bar(mock_obj)

    def test_is_modal_dialog(self, test_context: OrcaTestContext) -> None:
        """Test is_modal_dialog for dialog/alert roles and modal state."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.has_state = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_dialog_or_alert", return_value=False
        )
        assert not AXUtilitiesRole.is_modal_dialog(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_dialog_or_alert", return_value=True
        )
        mock_ax_object_class.has_state = test_context.Mock(return_value=False)
        assert not AXUtilitiesRole.is_modal_dialog(mock_obj)

        mock_ax_object_class.has_state = test_context.Mock(return_value=True)
        assert AXUtilitiesRole.is_modal_dialog(mock_obj)

    def test_is_multi_line_entry(self, test_context: OrcaTestContext) -> None:
        """Test is_multi_line_entry for entry role and multiline state."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.has_state = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesRole, "is_entry", return_value=False)
        assert not AXUtilitiesRole.is_multi_line_entry(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "is_entry", return_value=True)
        mock_ax_object_class.has_state = test_context.Mock(return_value=False)
        assert not AXUtilitiesRole.is_multi_line_entry(mock_obj)

        mock_ax_object_class.has_state = test_context.Mock(return_value=True)
        assert AXUtilitiesRole.is_multi_line_entry(mock_obj)

    def test_is_docked_frame(self, test_context: OrcaTestContext) -> None:
        """Test is_docked_frame for frame role and docked attribute."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesRole, "is_frame", return_value=False)
        assert not AXUtilitiesRole.is_docked_frame(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "is_frame", return_value=True)
        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"window-type": "normal"}
        )
        assert not AXUtilitiesRole.is_docked_frame(mock_obj)

        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"window-type": "dock"}
        )
        assert AXUtilitiesRole.is_docked_frame(mock_obj)

    def test_is_desktop_frame(self, test_context: OrcaTestContext) -> None:
        """Test is_desktop_frame for desktop frame and is-desktop attribute."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.LABEL)
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.DESKTOP_FRAME)
        assert AXUtilitiesRole.is_desktop_frame(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.FRAME)
        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"is-desktop": "true"}
        )
        assert AXUtilitiesRole.is_desktop_frame(mock_obj)

        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"is-desktop": "false"}
        )
        assert not AXUtilitiesRole.is_desktop_frame(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.LABEL)
        assert not AXUtilitiesRole.is_desktop_frame(mock_obj)

    def test_is_live_region(self, test_context: OrcaTestContext) -> None:
        """Test is_live_region for container-live attribute."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={"foo": "bar"})
        assert not AXUtilitiesRole.is_live_region(mock_obj)

        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"container-live": "polite"}
        )
        assert AXUtilitiesRole.is_live_region(mock_obj)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_code_xml_role",
                "xml_roles": ["code"],
                "tag": None,
                "expected_result": True,
            },
            {"id": "with_code_tag", "xml_roles": [], "tag": "code", "expected_result": True},
            {"id": "with_pre_tag", "xml_roles": [], "tag": "pre", "expected_result": True},
            {
                "id": "with_no_code_indicators",
                "xml_roles": ["text"],
                "tag": "p",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_code(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRole.is_code in various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "_get_xml_roles", side_effect=lambda obj: case["xml_roles"]
        )
        if case["tag"] is not None:
            test_context.patch_object(
                AXUtilitiesRole, "_get_tag", side_effect=lambda obj: case["tag"]
            )

        result = AXUtilitiesRole.is_code(mock_obj)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "push_button_with_popup",
                "role": Atspi.Role.BUTTON,
                "has_popup": True,
                "expected": True,
            },
            {
                "id": "push_button_without_popup",
                "role": Atspi.Role.BUTTON,
                "has_popup": False,
                "expected": False,
            },
            {
                "id": "label_with_popup",
                "role": Atspi.Role.LABEL,
                "has_popup": True,
                "expected": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_button_with_popup(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRole.is_button_with_popup with various combinations."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_utilities_state_mock = essential_modules["orca.ax_utilities_state"].AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock.get_role.return_value = case["role"]
        ax_utilities_state_mock.has_popup.return_value = case["has_popup"]

        result = AXUtilitiesRole.is_button_with_popup(mock_obj)
        assert result is case["expected"]

    def test_is_landmark_without_type(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_landmark_without_type."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=False
        )
        assert not AXUtilitiesRole.is_landmark_without_type(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=True
        )
        test_context.patch_object(AXUtilitiesRole, "_get_xml_roles", return_value=[])
        assert AXUtilitiesRole.is_landmark_without_type(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_landmark", return_value=True
        )
        test_context.patch_object(
            AXUtilitiesRole, "_get_xml_roles", return_value=["navigation"]
        )
        assert not AXUtilitiesRole.is_landmark_without_type(mock_obj)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "dialog_roles",
                "method_name": "get_dialog_roles",
                "expected_roles": [
                    Atspi.Role.COLOR_CHOOSER,
                    Atspi.Role.DIALOG,
                    Atspi.Role.FILE_CHOOSER,
                    Atspi.Role.ALERT,
                ],
                "test_params": [{}, {"include_alert_as_dialog": False}],
            },
            {
                "id": "document_roles",
                "method_name": "get_document_roles",
                "expected_roles": [
                    Atspi.Role.DOCUMENT_EMAIL,
                    Atspi.Role.DOCUMENT_FRAME,
                    Atspi.Role.DOCUMENT_PRESENTATION,
                    Atspi.Role.DOCUMENT_SPREADSHEET,
                    Atspi.Role.DOCUMENT_TEXT,
                    Atspi.Role.DOCUMENT_WEB,
                ],
                "test_params": [{}],
            },
            {
                "id": "form_field_roles",
                "method_name": "get_form_field_roles",
                "expected_roles": [
                    Atspi.Role.BUTTON,
                    Atspi.Role.CHECK_BOX,
                    Atspi.Role.RADIO_BUTTON,
                    Atspi.Role.COMBO_BOX,
                    Atspi.Role.DOCUMENT_FRAME,
                    Atspi.Role.TEXT,
                    Atspi.Role.LIST_BOX,
                    Atspi.Role.ENTRY,
                    Atspi.Role.PASSWORD_TEXT,
                    Atspi.Role.SPIN_BUTTON,
                    Atspi.Role.TOGGLE_BUTTON,
                ],
                "test_params": [{}],
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_role_collections(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRole get_*_roles methods."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        method_to_test = getattr(AXUtilitiesRole, case["method_name"])

        for params in case["test_params"]:
            roles = method_to_test(**params)
            if case["method_name"] == "get_dialog_roles" and "include_alert_as_dialog" in params:
                expected = [r for r in case["expected_roles"] if r != Atspi.Role.ALERT]
                assert roles == expected
            else:
                assert roles == case["expected_roles"]

    def test_get_menu_item_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_menu_item_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_menu_item_roles()
        expected = [
            Atspi.Role.MENU_ITEM,
            Atspi.Role.CHECK_MENU_ITEM,
            Atspi.Role.RADIO_MENU_ITEM,
            Atspi.Role.TEAROFF_MENU_ITEM,
        ]
        assert roles == expected

    def test_get_menu_related_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_menu_related_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_menu_related_roles()
        expected = [
            Atspi.Role.MENU,
            Atspi.Role.MENU_BAR,
            Atspi.Role.POPUP_MENU,
            Atspi.Role.MENU_ITEM,
            Atspi.Role.CHECK_MENU_ITEM,
            Atspi.Role.RADIO_MENU_ITEM,
            Atspi.Role.TEAROFF_MENU_ITEM,
        ]
        assert roles == expected

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "table_cell_roles",
                "method_name": "get_table_cell_roles",
                "expected_roles": [
                    Atspi.Role.TABLE_CELL,
                    Atspi.Role.TABLE_COLUMN_HEADER,
                    Atspi.Role.TABLE_ROW_HEADER,
                    Atspi.Role.COLUMN_HEADER,
                    Atspi.Role.ROW_HEADER,
                ],
                "test_params": [{}, {"include_headers": False}],
            },
            {
                "id": "table_header_roles",
                "method_name": "get_table_header_roles",
                "expected_roles": [
                    Atspi.Role.TABLE_COLUMN_HEADER,
                    Atspi.Role.TABLE_ROW_HEADER,
                    Atspi.Role.COLUMN_HEADER,
                    Atspi.Role.ROW_HEADER,
                ],
                "test_params": [{}],
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_table_role_collections(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRole get_table_*_roles methods."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        method_to_test = getattr(AXUtilitiesRole, case["method_name"])

        for params in case["test_params"]:
            roles = method_to_test(**params)
            if case["method_name"] == "get_table_cell_roles" and "include_headers" in params:
                expected = [Atspi.Role.TABLE_CELL]
                assert roles == expected
            else:
                assert roles == case["expected_roles"]

    def test_get_table_related_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_table_related_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_table_related_roles()
        expected = [
            Atspi.Role.TABLE,
            Atspi.Role.TABLE_CELL,
            Atspi.Role.TABLE_COLUMN_HEADER,
            Atspi.Role.TABLE_ROW_HEADER,
            Atspi.Role.COLUMN_HEADER,
            Atspi.Role.ROW_HEADER,
        ]
        assert roles == expected

        roles = AXUtilitiesRole.get_table_related_roles(include_caption=True)
        expected = [
            Atspi.Role.TABLE,
            Atspi.Role.TABLE_CELL,
            Atspi.Role.TABLE_COLUMN_HEADER,
            Atspi.Role.TABLE_ROW_HEADER,
            Atspi.Role.COLUMN_HEADER,
            Atspi.Role.ROW_HEADER,
            Atspi.Role.CAPTION,
        ]
        assert roles == expected

    def test_have_same_role(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.have_same_role."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj1 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.BUTTON)
        assert AXUtilitiesRole.have_same_role(mock_obj1, mock_obj2)

        def mock_get_role(obj):
            if obj == mock_obj1:
                return Atspi.Role.BUTTON
            return Atspi.Role.LABEL

        mock_ax_object_class.get_role = mock_get_role
        assert not AXUtilitiesRole.have_same_role(mock_obj1, mock_obj2)

    def test_has_role_from_aria(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.has_role_from_aria."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"xml-roles": "button"}
        )
        assert AXUtilitiesRole.has_role_from_aria(mock_obj)

        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={})
        assert not AXUtilitiesRole.has_role_from_aria(mock_obj)

        mock_ax_object_class.get_attributes_dict = test_context.Mock(return_value={"xml-roles": ""})
        assert not AXUtilitiesRole.has_role_from_aria(mock_obj)

    def test_is_aria_alert(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_aria_alert."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"xml-roles": "button"}
        )
        assert not AXUtilitiesRole.is_aria_alert(mock_obj)

        mock_ax_object_class.get_attributes_dict = test_context.Mock(
            return_value={"xml-roles": "alert"}
        )
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.NOTIFICATION)
        assert AXUtilitiesRole.is_aria_alert(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.ALERT)
        assert AXUtilitiesRole.is_aria_alert(mock_obj)

    def test_is_autocomplete(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_autocomplete."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.AUTOCOMPLETE)
        assert AXUtilitiesRole.is_autocomplete(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.BUTTON)
        assert not AXUtilitiesRole.is_autocomplete(mock_obj)
        assert AXUtilitiesRole.is_autocomplete(mock_obj, Atspi.Role.AUTOCOMPLETE)
        assert not AXUtilitiesRole.is_autocomplete(mock_obj, Atspi.Role.BUTTON)

    def test_is_default_button(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_default_button."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        mock_ax_object_class.has_state = test_context.Mock(return_value=False)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_push_button", return_value=False
        )
        assert not AXUtilitiesRole.is_default_button(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_push_button", return_value=True
        )
        mock_ax_object_class.has_state = test_context.Mock(return_value=False)
        assert not AXUtilitiesRole.is_default_button(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_push_button", return_value=True
        )
        mock_ax_object_class.has_state = test_context.Mock(return_value=True)
        assert AXUtilitiesRole.is_default_button(mock_obj)

    def test_is_single_line_autocomplete_entry(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_single_line_autocomplete_entry."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_utilities_state_class = essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_single_line_entry", return_value=False
        )
        assert not AXUtilitiesRole.is_single_line_autocomplete_entry(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_single_line_entry", return_value=True
        )
        mock_ax_utilities_state_class.supports_autocompletion = test_context.Mock(
            return_value=False
        )
        assert not AXUtilitiesRole.is_single_line_autocomplete_entry(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "is_single_line_entry", return_value=True
        )
        mock_ax_utilities_state_class.supports_autocompletion = test_context.Mock(return_value=True)
        assert AXUtilitiesRole.is_single_line_autocomplete_entry(mock_obj)

    def test_is_single_line_entry(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_single_line_entry."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_utilities_state_class = essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_utilities_state_class.is_single_line = test_context.Mock(return_value=False)
        assert not AXUtilitiesRole.is_single_line_entry(mock_obj)

        mock_ax_utilities_state_class.is_single_line = test_context.Mock(return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_entry", return_value=True)
        assert AXUtilitiesRole.is_single_line_entry(mock_obj)

        mock_ax_utilities_state_class.is_single_line = test_context.Mock(return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_entry", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_text", return_value=True)
        mock_ax_utilities_state_class.is_editable = test_context.Mock(return_value=True)
        assert AXUtilitiesRole.is_single_line_entry(mock_obj)

        mock_ax_utilities_state_class.is_editable = test_context.Mock(return_value=False)
        assert not AXUtilitiesRole.is_single_line_entry(mock_obj)

    def test_is_dialog_or_alert(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_dialog_or_alert."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.DIALOG)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.ALERT)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.COLOR_CHOOSER)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.FILE_CHOOSER)
        assert AXUtilitiesRole.is_dialog_or_alert(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.BUTTON)
        assert not AXUtilitiesRole.is_dialog_or_alert(mock_obj)

    def test_is_dialog_or_window(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_dialog_or_window."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.DIALOG)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.FRAME)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.WINDOW)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.COLOR_CHOOSER)
        assert AXUtilitiesRole.is_dialog_or_window(mock_obj)

        mock_ax_object_class.get_role = test_context.Mock(return_value=Atspi.Role.BUTTON)
        assert not AXUtilitiesRole.is_dialog_or_window(mock_obj)

    def test_get_widget_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_widget_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_widget_roles()
        assert len(roles) > 10
        assert Atspi.Role.BUTTON in roles
        assert Atspi.Role.CHECK_BOX in roles
        assert Atspi.Role.ENTRY in roles
        assert Atspi.Role.COMBO_BOX in roles

    def test_get_text_ui_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_text_ui_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_text_ui_roles()
        expected = [
            Atspi.Role.INFO_BAR,
            Atspi.Role.LABEL,
            Atspi.Role.PAGE_TAB,
            Atspi.Role.STATUS_BAR,
        ]
        assert roles == expected

    def test_get_tree_related_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_tree_related_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_tree_related_roles()
        expected = [Atspi.Role.TREE, Atspi.Role.TREE_ITEM, Atspi.Role.TREE_TABLE]
        assert roles == expected

    def test_get_set_container_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_set_container_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_set_container_roles()
        expected = [
            Atspi.Role.LIST,
            Atspi.Role.MENU,
            Atspi.Role.PAGE_TAB_LIST,
            Atspi.Role.TABLE,
            Atspi.Role.TREE,
            Atspi.Role.TREE_TABLE,
        ]
        assert roles == expected

    def test_get_layout_only_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_layout_only_roles."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        roles = AXUtilitiesRole.get_layout_only_roles()
        expected = [
            Atspi.Role.AUTOCOMPLETE,
            Atspi.Role.FILLER,
            Atspi.Role.REDUNDANT_OBJECT,
            Atspi.Role.UNKNOWN,
            Atspi.Role.SCROLL_PANE,
            Atspi.Role.TEAROFF_MENU_ITEM,
        ]
        assert roles == expected

    def test_get_large_container_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_large_container_roles."""

        self._setup_dependencies(test_context)
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
            Atspi.Role.TREE_TABLE,
        ]
        assert roles == expected

    def test_get_roles_to_exclude_from_clickables_list(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.get_roles_to_exclude_from_clickables_list."""

        self._setup_dependencies(test_context)
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
            Atspi.Role.TREE,
        ]
        assert roles == expected

    def test_is_dpub(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole.is_dpub."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "_get_xml_roles", return_value=["doc-abstract"]
        )
        assert AXUtilitiesRole.is_dpub(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "_get_xml_roles", return_value=["button"])
        assert not AXUtilitiesRole.is_dpub(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "_get_xml_roles", return_value=[])
        assert not AXUtilitiesRole.is_dpub(mock_obj)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "dpub_abstract",
                "method_name": "is_dpub_abstract",
                "expected_xml_role": "doc-abstract",
            },
            {
                "id": "dpub_acknowledgments",
                "method_name": "is_dpub_acknowledgments",
                "expected_xml_role": "doc-acknowledgments",
            },
            {
                "id": "dpub_afterword",
                "method_name": "is_dpub_afterword",
                "expected_xml_role": "doc-afterword",
            },
            {
                "id": "dpub_appendix",
                "method_name": "is_dpub_appendix",
                "expected_xml_role": "doc-appendix",
            },
            {
                "id": "dpub_backlink",
                "method_name": "is_dpub_backlink",
                "expected_xml_role": "doc-backlink",
            },
            {
                "id": "dpub_biblioref",
                "method_name": "is_dpub_biblioref",
                "expected_xml_role": "doc-biblioref",
            },
            {
                "id": "dpub_bibliography",
                "method_name": "is_dpub_bibliography",
                "expected_xml_role": "doc-bibliography",
            },
            {
                "id": "dpub_chapter",
                "method_name": "is_dpub_chapter",
                "expected_xml_role": "doc-chapter",
            },
            {
                "id": "dpub_colophon",
                "method_name": "is_dpub_colophon",
                "expected_xml_role": "doc-colophon",
            },
            {
                "id": "dpub_conclusion",
                "method_name": "is_dpub_conclusion",
                "expected_xml_role": "doc-conclusion",
            },
            {"id": "dpub_cover", "method_name": "is_dpub_cover", "expected_xml_role": "doc-cover"},
            {
                "id": "dpub_credit",
                "method_name": "is_dpub_credit",
                "expected_xml_role": "doc-credit",
            },
            {
                "id": "dpub_credits",
                "method_name": "is_dpub_credits",
                "expected_xml_role": "doc-credits",
            },
            {
                "id": "dpub_dedication",
                "method_name": "is_dpub_dedication",
                "expected_xml_role": "doc-dedication",
            },
            {
                "id": "dpub_endnote",
                "method_name": "is_dpub_endnote",
                "expected_xml_role": "doc-endnote",
            },
            {
                "id": "dpub_endnotes",
                "method_name": "is_dpub_endnotes",
                "expected_xml_role": "doc-endnotes",
            },
            {
                "id": "dpub_epigraph",
                "method_name": "is_dpub_epigraph",
                "expected_xml_role": "doc-epigraph",
            },
            {
                "id": "dpub_epilogue",
                "method_name": "is_dpub_epilogue",
                "expected_xml_role": "doc-epilogue",
            },
            {
                "id": "dpub_errata",
                "method_name": "is_dpub_errata",
                "expected_xml_role": "doc-errata",
            },
            {
                "id": "dpub_example",
                "method_name": "is_dpub_example",
                "expected_xml_role": "doc-example",
            },
            {
                "id": "dpub_footnote",
                "method_name": "is_dpub_footnote",
                "expected_xml_role": "doc-footnote",
            },
            {
                "id": "dpub_foreword",
                "method_name": "is_dpub_foreword",
                "expected_xml_role": "doc-foreword",
            },
            {
                "id": "dpub_glossary",
                "method_name": "is_dpub_glossary",
                "expected_xml_role": "doc-glossary",
            },
            {
                "id": "dpub_glossref",
                "method_name": "is_dpub_glossref",
                "expected_xml_role": "doc-glossref",
            },
            {"id": "dpub_index", "method_name": "is_dpub_index", "expected_xml_role": "doc-index"},
            {
                "id": "dpub_introduction",
                "method_name": "is_dpub_introduction",
                "expected_xml_role": "doc-introduction",
            },
            {
                "id": "dpub_noteref",
                "method_name": "is_dpub_noteref",
                "expected_xml_role": "doc-noteref",
            },
            {
                "id": "dpub_pagelist",
                "method_name": "is_dpub_pagelist",
                "expected_xml_role": "doc-pagelist",
            },
            {
                "id": "dpub_pagebreak",
                "method_name": "is_dpub_pagebreak",
                "expected_xml_role": "doc-pagebreak",
            },
            {"id": "dpub_part", "method_name": "is_dpub_part", "expected_xml_role": "doc-part"},
            {
                "id": "dpub_preface",
                "method_name": "is_dpub_preface",
                "expected_xml_role": "doc-preface",
            },
            {
                "id": "dpub_prologue",
                "method_name": "is_dpub_prologue",
                "expected_xml_role": "doc-prologue",
            },
            {
                "id": "dpub_pullquote",
                "method_name": "is_dpub_pullquote",
                "expected_xml_role": "doc-pullquote",
            },
            {"id": "dpub_qna", "method_name": "is_dpub_qna", "expected_xml_role": "doc-qna"},
            {
                "id": "dpub_subtitle",
                "method_name": "is_dpub_subtitle",
                "expected_xml_role": "doc-subtitle",
            },
            {"id": "dpub_toc", "method_name": "is_dpub_toc", "expected_xml_role": "doc-toc"},
        ],
        ids=lambda case: case["id"],
    )
    def test_dpub_methods(self, test_context, case: dict) -> None:
        """Test AXUtilitiesRole DPUB methods."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilitiesRole, case["method_name"])
        test_context.patch_object(
            AXUtilitiesRole, "_get_xml_roles", side_effect=lambda obj: [case["expected_xml_role"]]
        )
        assert method(mock_obj)

        test_context.patch_object(
            AXUtilitiesRole, "_get_xml_roles", return_value=["doc-other"]
        )
        assert not method(mock_obj)

        test_context.patch_object(AXUtilitiesRole, "_get_xml_roles", return_value=[])
        assert not method(mock_obj)

    def test_get_display_style(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole._get_display_style method."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import ax_utilities_role

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            ax_utilities_role.AXObject, "get_attributes_dict", return_value={"display": "inline"}
        )
        result = AXUtilitiesRole._get_display_style(mock_obj)  # pylint: disable=protected-access
        assert result == "inline"

    def test_get_display_style_missing(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole._get_display_style when display attribute is missing."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import ax_utilities_role

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            ax_utilities_role.AXObject, "get_attributes_dict", return_value={}
        )
        result = AXUtilitiesRole._get_display_style(mock_obj)  # pylint: disable=protected-access
        assert result == ""

    def test_get_tag(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole._get_tag method."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import ax_utilities_role

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            ax_utilities_role.AXObject, "get_attributes_dict", return_value={"tag": "button"}
        )
        result = AXUtilitiesRole._get_tag(mock_obj)  # pylint: disable=protected-access
        assert result == "button"

    def test_get_tag_missing(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole._get_tag when tag attribute is missing."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import ax_utilities_role

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            ax_utilities_role.AXObject, "get_attributes_dict", return_value={}
        )
        result = AXUtilitiesRole._get_tag(mock_obj)  # pylint: disable=protected-access
        assert result is None

    def test_get_xml_roles(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole._get_xml_roles method."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import ax_utilities_role

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            ax_utilities_role.AXObject,
            "get_attributes_dict",
            return_value={"xml-roles": "doc-part doc-chapter"},
        )
        result = AXUtilitiesRole._get_xml_roles(mock_obj)  # pylint: disable=protected-access
        assert result == ["doc-part", "doc-chapter"]

    def test_get_xml_roles_empty(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesRole._get_xml_roles when xml-roles is empty."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import ax_utilities_role

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            ax_utilities_role.AXObject, "get_attributes_dict", return_value={"xml-roles": ""}
        )
        result = AXUtilitiesRole._get_xml_roles(mock_obj)  # pylint: disable=protected-access
        assert result == []
