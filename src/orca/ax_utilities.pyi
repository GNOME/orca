# Stub file that should contain all public methods of AXUtilities
#
# Copyright 2023 Igalia, S.L.
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

# pylint: disable=missing-function-docstring
# pylint: disable=unused-argument
# pylint: disable=too-many-lines
# pylint: disable=missing-class-docstring
# pylint: disable=wrong-import-position
# pylint: disable=too-many-public-methods

"""
Stub file that contains all public methods of AXUtilities, including
those which are added dynamically at runtime. This is needed for type
checkers, linters, and IDEs.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

from typing import Callable

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .ax_utilities_event import TextEventReason

class AXUtilities:

    # From ax_utilities.py
    @staticmethod
    def clear_all_cache_now(obj: Atspi.Accessible | None = None, reason: str = "") -> None: ...

    @staticmethod
    def can_be_active_window(window: Atspi.Accessible) -> bool: ...

    @staticmethod
    def find_active_window() -> Atspi.Accessible | None: ...

    @staticmethod
    def is_unfocused_alert_or_dialog(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def get_unfocused_alerts_and_dialogs(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_all_widgets(
        obj: Atspi.Accessible,
        must_be_showing_and_visible: bool = True,
        exclude_push_button: bool = False
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_default_button(obj: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def get_focused_object(obj: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def get_info_bar(obj: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def get_status_bar(obj: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def is_layout_only(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_message_dialog(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_redundant_object(obj1: Atspi.Accessible, obj2: Atspi.Accessible) -> bool: ...

    @staticmethod
    def get_set_members(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_set_size(obj: Atspi.Accessible) -> int: ...

    @staticmethod
    def get_set_size_is_unknown(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def get_position_in_set(obj: Atspi.Accessible) -> int: ...

    @staticmethod
    def has_explicit_name(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def has_visible_caption(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def get_displayed_label(obj: Atspi.Accessible) -> str: ...

    @staticmethod
    def get_displayed_description(obj: Atspi.Accessible) -> str: ...

    @staticmethod
    def get_heading_level(obj: Atspi.Accessible) -> int: ...

    @staticmethod
    def get_nesting_level(obj: Atspi.Accessible) -> int: ...

    @staticmethod
    def get_next_object(obj: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def get_previous_object(obj: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def is_on_screen(obj: Atspi.Accessible, bounding_box: Atspi.Rect | None = None) -> bool: ...

    @staticmethod
    def treat_as_leaf_node(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def get_on_screen_objects(
        root: Atspi.Accessible,
        bounding_box: Atspi.Rect | None = None
    ) -> list: ...

    # From ax_utilities_application.py
    @staticmethod
    def application_as_string(obj: Atspi.Accessible) -> str: ...

    @staticmethod
    def get_all_applications(
        must_have_window: bool = False,
        exclude_unresponsive: bool = False,
        is_debug: bool = False
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_application_with_pid(pid: int) -> Atspi.Accessible | None: ...

    @staticmethod
    def get_application(obj: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def get_application_toolkit_name(obj: Atspi.Accessible) -> str: ...

    @staticmethod
    def get_application_toolkit_version(obj: Atspi.Accessible) -> str: ...

    @staticmethod
    def get_desktop() -> Atspi.Accessible: ...

    @staticmethod
    def get_process_id(obj: Atspi.Accessible) -> int: ...

    @staticmethod
    def is_application_in_desktop(app: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_application_unresponsive(app: Atspi.Accessible) -> bool: ...

    # From ax_utilities_event.py
    @staticmethod
    def save_object_info_for_events(obj: Atspi.Accessible) -> None: ...

    @staticmethod
    def get_text_event_reason(event: Atspi.Event) -> TextEventReason: ...

    @staticmethod
    def is_presentable_active_descendant_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_checked_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_description_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_expanded_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_indeterminate_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_invalid_entry_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_name_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_pressed_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_selected_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_text_attributes_change(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_text_deletion(event: Atspi.Event) -> bool: ...

    @staticmethod
    def is_presentable_text_insertion(event: Atspi.Event) -> bool: ...

    # From ax_utilities_role.py
    @staticmethod
    def _get_display_style(obj: Atspi.Accessible) -> str: ...

    @staticmethod
    def _get_tag(obj: Atspi.Accessible) -> str | None: ...

    @staticmethod
    def _get_xml_roles(obj: Atspi.Accessible) -> list[str]: ...

    @staticmethod
    def children_are_presentational(
        obj: Atspi.Accessible,
        role: Atspi.Role | None = None
    ) -> bool: ...

    @staticmethod
    def get_dialog_roles(include_alert_as_dialog: bool = True) -> list[Atspi.Role]: ...

    @staticmethod
    def get_document_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_form_field_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_large_container_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_layout_only_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_menu_item_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_menu_related_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_roles_to_exclude_from_clickables_list() -> list[Atspi.Role]: ...

    @staticmethod
    def get_set_container_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_table_cell_roles(include_headers: bool = True) -> list[Atspi.Role]: ...

    @staticmethod
    def get_table_header_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_table_related_roles(include_caption: bool = False) -> list[Atspi.Role]: ...

    @staticmethod
    def get_text_ui_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_tree_related_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_widget_roles() -> list[Atspi.Role]: ...

    @staticmethod
    def get_localized_role_name(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> str: ...

    @staticmethod
    def has_role_from_aria(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def have_same_role(obj1: Atspi.Accessible, obj2: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_accelerator_label(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_alert(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_aria_alert(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_animation(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_application(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_arrow(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_article(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_audio(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_autocomplete(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_block_quote(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_button(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_button_with_popup(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_calendar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_canvas(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_caption(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_chart(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_check_box(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_check_menu_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_code(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_color_chooser(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_column_header(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_combo_box(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_comment(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_content_deletion(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_content_insertion(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_default_button(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_date_editor(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_definition(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_description_list(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_description_term(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_description_value(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_desktop_frame(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_desktop_icon(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dial(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dialog(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dialog_or_alert(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dialog_or_window(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_directory_pane(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_docked_frame(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_document(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_document_email(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_document_frame(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_document_presentation(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_document_spreadsheet(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_document_text(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_document_web(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_abstract(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_acknowledgments(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_afterword(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_appendix(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_backlink(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_biblioref(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_bibliography(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_chapter(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_colophon(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_conclusion(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_cover(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_credit(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_credits(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_dedication(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_endnote(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_endnotes(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_epigraph(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_epilogue(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_errata(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_example(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_footnote(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_foreword(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_glossary(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_glossref(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_index(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_introduction(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_noteref(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_pagelist(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_pagebreak(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_part(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_preface(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_prologue(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_pullquote(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_qna(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_subtitle(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_dpub_toc(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_drawing_area(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_editable_combo_box(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_editbar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_embedded(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_entry(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_extended(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_feed(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_feed_article(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_figure(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_file_chooser(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_filler(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_focus_traversable(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_font_chooser(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_footer(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_footnote(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_form(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_frame(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_glass_pane(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_gui_list(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_grid(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_grid_cell(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_group(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_grouping(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_header(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_heading(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_html_container(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_horizontal_scrollbar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_horizontal_separator(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_horizontal_slider(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_icon(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_icon_or_canvas(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_image(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_image_or_canvas(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_image_map(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_info_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_inline_internal_frame(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_inline_list_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_inline_suggestion(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_input_method_window(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_internal_frame(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_invalid_role(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_label(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_label_or_caption(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_banner(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_complementary(
        obj: Atspi.Accessible,
        _role: Atspi.Role | None = None
    ) -> bool: ...

    @staticmethod
    def is_landmark_contentinfo(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_form(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_main(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_navigation(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_region(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_search(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_landmark_without_type(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_large_container(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_layered_pane(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_level_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_link(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_list(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_list_box(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_list_box_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_list_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_log(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_live_region(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_mark(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_marquee(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_math(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_math_enclose(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_fenced(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_fraction(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_math_fraction_without_bar(
        obj: Atspi.Accessible, role: Atspi.Role | None = None
    ) -> bool: ...

    @staticmethod
    def is_math_layout_only(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_multi_script(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_related(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_math_root(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_math_square_root(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_sub_or_super_script(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_table(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_table_row(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_token(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_math_under_or_over_script(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_menu(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_menu_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_menu_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_menu_item_of_any_kind(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_menu_related(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_modal_dialog(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_multi_line_entry(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_notification(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_option_pane(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_page(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_page_tab(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_page_tab_list(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_page_tab_list_related(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_panel(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_paragraph(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_password_text(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_popup_menu(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_progress_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_push_button(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_push_button_menu(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_radio_button(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_radio_menu_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_rating(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_redundant_object_role(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_root_pane(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_row_header(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_ruler(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_scroll_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_scroll_pane(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_section(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_separator(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_single_line_autocomplete_entry(
        obj: Atspi.Accessible, role: Atspi.Role | None = None
    ) -> bool: ...

    @staticmethod
    def is_single_line_entry(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_slider(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_spin_button(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_split_pane(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_static(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_status_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_subscript(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_subscript_or_superscript(
        obj: Atspi.Accessible, role: Atspi.Role | None = None
    ) -> bool: ...

    @staticmethod
    def is_subscript_or_superscript_text(
        obj: Atspi.Accessible, role: Atspi.Role | None = None
    ) -> bool: ...

    @staticmethod
    def is_suggestion(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_superscript(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_svg(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_switch(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_table(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_table_cell(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_table_cell_or_header(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_table_column_header(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_table_header(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_table_related(
        obj: Atspi.Accessible,
        role: Atspi.Role | None = None,
        include_caption: bool = False
    ) -> bool: ...

    @staticmethod
    def is_table_row(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_table_row_header(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tearoff_menu_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_terminal(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_date(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_email(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_number(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_search(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_telephone(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_time(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_url(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_text_input_week(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_time(obj: Atspi.Accessible, _role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_timer(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_title_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_toggle_button(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tool_bar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tool_tip(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tree(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tree_or_tree_table(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tree_related(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tree_item(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_tree_table(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_unknown(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_unknown_or_redundant(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_vertical_scrollbar(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_vertical_separator(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_vertical_slider(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_video(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_viewport(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_widget(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    @staticmethod
    def is_widget_controlled_by_line_navigation(
        obj: Atspi.Accessible, role: Atspi.Role | None = None
    ) -> bool: ...

    @staticmethod
    def is_web_element(obj: Atspi.Accessible, exclude_pseudo_elements: bool = True) -> bool: ...

    @staticmethod
    def is_web_element_custom(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_window(obj: Atspi.Accessible, role: Atspi.Role | None = None) -> bool: ...

    # From ax_utilities_state.py
    @staticmethod
    def get_current_item_status_string(obj: Atspi.Accessible) -> str: ...

    @staticmethod
    def has_no_state(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def has_popup(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def has_tooltip(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_active(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_animated(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_armed(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_busy(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_checkable(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_checked(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_collapsed(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_default(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_defunct(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_editable(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_enabled(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_expandable(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_expanded(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_focusable(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_focused(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_hidden(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_horizontal(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_iconified(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_indeterminate(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_invalid_state(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_invalid_entry(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_modal(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_multi_line(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_multiselectable(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_opaque(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_pressed(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_read_only(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_required(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_resizable(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_selectable(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_selectable_text(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_selected(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_sensitive(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_showing(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_single_line(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_stale(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_transient(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_truncated(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_vertical(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_visible(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def is_visited(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def manages_descendants(obj: Atspi.Accessible) -> bool: ...

    @staticmethod
    def supports_autocompletion(obj: Atspi.Accessible) -> bool: ...

    # From ax_utilities_collection.py
    @staticmethod
    def find_all_with_interfaces(
        root: Atspi.Accessible,
        interface_list: list[str],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_with_role(
        root: Atspi.Accessible,
        roles_list: list[Atspi.Role],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_without_roles(
        root: Atspi.Accessible,
        roles_list: list[Atspi.Role],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_with_role_and_all_states(
        root: Atspi.Accessible,
        roles_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_with_role_and_any_state(
        root: Atspi.Accessible,
        roles_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_with_role_without_states(
        root: Atspi.Accessible,
        roles_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_with_states(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_with_any_state(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_without_states(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_accelerator_labels(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_alerts(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_animations(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_arrows(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_articles(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_audios(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_autocompletes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_block_quotes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_buttons(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_calendars(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_canvases(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_captions(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_charts(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_check_boxes(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_check_menu_items(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_clickables(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_color_choosers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_column_headers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_combo_boxes(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_comments(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_content_deletions(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_content_insertions(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_date_editors(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_definitions(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_description_lists(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_description_terms(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_description_values(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_desktop_frames(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_desktop_icons(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_dials(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_dialogs(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_dialogs_and_alerts(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_directory_panes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_documents(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_document_emails(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_document_frames(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_document_presentations(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_document_spreadsheets(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_document_texts(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_document_webs(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_drawing_areas(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_editable_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_editbars(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_embeddeds(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_entries(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_extendeds(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_file_choosers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_fillers(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_focus_traversables(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_focusable_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_focusable_objects_with_click_ancestor(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_focused_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_font_choosers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_footers(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_footnotes(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_forms(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_form_fields(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_frames(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_glass_panes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_grids(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_grid_cells(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_groupings(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_headers(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_headings(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_headings_at_level(
        root: Atspi.Accessible,
        level: int,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_html_containers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_horizontal_scrollbars(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_horizontal_separators(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_horizontal_sliders(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_icons(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_icons_and_canvases(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_images(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_images_and_canvases(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_images_and_image_maps(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_image_maps(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_info_bars(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_input_method_windows(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_internal_frames(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_labels(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_labels_and_captions(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_landmarks(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_large_containers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_layered_panes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_level_bars(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_lists(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
        include_description_lists: bool = False,
        include_tab_lists: bool = False
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_list_boxes(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_list_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
        include_description_terms: bool = False,
        include_tabs: bool = False
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_live_regions(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_logs(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_marks(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_marquees(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_maths(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_math_fractions(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_math_roots(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_menus(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_menu_bars(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_menu_items(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_menu_items_of_any_kind(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_menu_related_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_modal_dialogs(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_multi_line_entries(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_notifications(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_option_panes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_pages(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_page_tabs(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_page_tab_lists(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_page_tab_list_related_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_panels(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_paragraphs(
        root: Atspi.Accessible,
        treat_headings_as_paragraphs: bool = False,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_password_texts(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_popup_menus(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_progress_bars(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_push_buttons(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_push_button_menus(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_radio_buttons(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_radio_menu_items(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_ratings(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_root_panes(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_row_headers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_rulers(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_scroll_bars(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_scroll_panes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_sections(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_selectable_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_selected_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_separators(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_set_containers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_showing_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_showing_and_visible_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_showing_or_visible_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_single_line_entries(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_sliders(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_spin_buttons(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_split_panes(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_statics(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_status_bars(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_subscripts(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_subscripts_and_superscripts(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_suggestions(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_superscripts(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_action(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_document(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_editable_text(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_hypertext(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_hyperlink(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_selection(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_table(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_table_cell(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_text(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_supports_value(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_tables(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_table_cells(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_table_cells_and_headers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_table_column_headers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_table_headers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_table_related_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None,
        include_caption: bool = False
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_table_rows(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_table_row_headers(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_tearoff_menu_items(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_terminals(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_texts(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_text_inputs(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_timers(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_title_bars(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_toggle_buttons(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_tool_bars(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_tool_tips(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_trees(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_trees_and_tree_tables(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_tree_related_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_tree_items(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_tree_tables(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_unrelated_labels(
        root: Atspi.Accessible,
        must_be_showing: bool = True,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_unvisited_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_vertical_scrollbars(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_vertical_separators(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_vertical_sliders(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_videos(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_viewports(
        root: Atspi.Accessible, pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_visible_objects(
        root: Atspi.Accessible,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_all_visited_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable | None = None
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def find_default_button(root: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def find_focused_object(root: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def find_info_bar(root: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def find_status_bar(root: Atspi.Accessible) -> Atspi.Accessible | None: ...

    @staticmethod
    def has_combo_box_or_list_box(root: Atspi.Accessible) -> bool: ...

    @staticmethod
    def has_editable_object(root: Atspi.Accessible) -> bool: ...

    @staticmethod
    def has_scroll_pane(root: Atspi.Accessible) -> bool: ...

    @staticmethod
    def has_split_pane(root: Atspi.Accessible) -> bool: ...

    @staticmethod
    def has_tree_or_tree_table(root: Atspi.Accessible) -> bool: ...

    # From ax_utilities.relation.py
    @staticmethod
    def _get_relation_targets(
        obj: Atspi.Accessible,
        relation_type: Atspi.ReleationType
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_relation_targets_for_debugging(
        obj: Atspi.Accessible,
        relation_type: Atspi.ReleationType
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_controlled_by(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_controller_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_described_by(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_description_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_details(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_details_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_embedded_by(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_embeds(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_error_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_error_message(obj: Atspi.Accessible) -> str | None: ...

    @staticmethod
    def get_flows_from(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_flows_to(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_label_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_labelled_by(
        obj: Atspi.Accessible,
        exclude_ancestors: bool = True
    ) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_member_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_node_child_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_node_parent_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_parent_window_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_popup_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_subwindow_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def get_is_tooltip_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]: ...

    @staticmethod
    def object_is_controlled_by(obj1: Atspi.Accessible, obj2: Atspi.Accessible) -> bool: ...

    @staticmethod
    def object_is_unrelated(obj: Atspi.Accessible) -> bool: ...
