# Orca
#
# Copyright 2025 Valve Corporation
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

"""Shared fixtures and configuration for integration tests."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

os.environ["GSETTINGS_BACKEND"] = "memory"

from .apps import browser, gtk, terminal
from .dbus_fixtures import (  # noqa: F401
    _bus,
    _dbus_service_proxy,
    _module_proxy_factory,
    dbus_timeout_fixture,
    run_with_timeout,
)
from .gsettings_fixtures import (  # noqa: F401
    _gsettings_handle,
    _gsettings_profile,
    _gsettings_registry,
)
from .orca_fixtures import (  # noqa: F401
    _atril,
    _gtk_announcement,
    _gtk_buttons,
    _gtk_drop_down,
    _gtk_multi_select_list,
    _gtk_redundant_names,
    _gtk_text_view,
    _gtk_text_view_blank_line,
    _gtk_text_view_emoji,
    _gtk_text_view_repeated_symbols,
    _gtk_text_view_selection,
    _gtk_text_view_word_boundaries,
    _gtk_toolbar,
    _gtk_tree_view,
    _gtk_tri_state_checkbox,
    _gtk_two_entries,
    _gtk_two_windows,
    _gtk_widget_notebook,
    _notification_daemon,
    _orca,
    _terminal_flatrev,
    _terminal_focus,
    _terminal_nano,
    _terminal_pager,
    _terminal_review_update,
    _terminal_shell,
    _terminal_trailing_deletion,
    _terminal_updates,
    _terminal_vim,
    _terminal_vim_bottom,
    _terminal_vim_pages,
    _terminal_vim_scroll,
    _terminal_wide_pager,
    _web_accordion,
    _web_alert,
    _web_app_nested_documents,
    _web_aria_application,
    _web_aria_document,
    _web_aria_spinbutton,
    _web_article_headers,
    _web_attribute_mask,
    _web_autocomplete,
    _web_basic,
    _web_block_context,
    _web_blockquote_line_breaks,
    _web_canvas_fallback,
    _web_caret_context,
    _web_click_actions,
    _web_code_block,
    _web_code_block_multiline,
    _web_colored_blocks,
    _web_contenteditable_replacement,
    _web_contenteditable_replacement_button,
    _web_contracted_braille,
    _web_cssed_brokenness,
    _web_custom_wrappers,
    _web_data_grid,
    _web_dialogs,
    _web_disclosure,
    _web_dynamic_content,
    _web_editable_boundaries,
    _web_editable_embedded,
    _web_editable_embedded_selection,
    _web_editable_focus,
    _web_editing,
    _web_emoji_links,
    _web_emoji_offset_skew,
    _web_feed,
    _web_field_states,
    _web_flat_review,
    _web_flat_review_shrink,
    _web_flex_header,
    _web_focus_mutations,
    _web_form_fields,
    _web_form_label,
    _web_grid_named_cells,
    _web_grid_selection,
    _web_headings,
    _web_iframes,
    _web_image_descendants,
    _web_image_link,
    _web_inline_code,
    _web_inline_code_wrapped,
    _web_inline_landmarks,
    _web_inline_list,
    _web_inline_list_wrap,
    _web_label_inference,
    _web_landmarks,
    _web_languages,
    _web_line_breaks,
    _web_link_starts_line,
    _web_list_replacement,
    _web_listbox,
    _web_lists,
    _web_live_regions,
    _web_long_line,
    _web_math,
    _web_menu_button,
    _web_menubar,
    _web_missing_cells,
    _web_mixed_line_heights,
    _web_mixed_lists,
    _web_multi_line_content,
    _web_multithumb_slider,
    _web_native_text_selection,
    _web_nested_blockquotes,
    _web_nested_headings,
    _web_nested_link_text,
    _web_offscreen_labels,
    _web_option_removal,
    _web_page_up_down,
    _web_pain_slider,
    _web_pain_slider_no_valuenow,
    _web_plain_text,
    _web_preformatted_blank_lines,
    _web_radio_button_lines,
    _web_range_widgets,
    _web_redundant_content,
    _web_region_headings,
    _web_removed_child_recovery,
    _web_selection,
    _web_sister_projects,
    _web_sister_projects_2,
    _web_sortable_table,
    _web_structural_navigation,
    _web_switch,
    _web_table_block_cells,
    _web_table_label_inference,
    _web_tables,
    _web_tabs,
    _web_temporary_aria_hidden,
    _web_text_attributes,
    _web_toolbar,
    _web_tree,
    _web_treegrid,
    _web_tri_state_checkbox,
    _web_useless_images,
    _web_weird_headings,
    _web_widget_boundaries,
    _web_window_splitter,
    _web_word_boundaries,
    _web_wrapped_link,
    _web_wrapping_text,
)

if TYPE_CHECKING:
    import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))


def pytest_addoption(parser: pytest.Parser) -> None:
    """Registers the application choices supplied by the Meson suite."""

    parser.addoption("--user-agent", choices=tuple(browser.USER_AGENTS))
    parser.addoption("--terminal-toolkit", choices=tuple(terminal.TOOLKITS))
    parser.addoption("--gtk-toolkit", choices=tuple(gtk.TOOLKITS))


def pytest_configure(config: pytest.Config) -> None:
    """Configures the suite's applications and registers custom markers."""

    browser.configure(config.getoption("user_agent"))
    terminal.configure(config.getoption("terminal_toolkit"))
    gtk.configure(config.getoption("gtk_toolkit"))

    config.addinivalue_line("markers", "dbus: marks tests as D-Bus specific tests")
    config.addinivalue_line("markers", "gsettings: marks tests as GSettings integration tests")
    config.addinivalue_line(
        "markers", "native_app: marks tests that drive a native GUI app via AT-SPI"
    )
