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
    _gtk3_terminal_flatrev,
    _gtk3_terminal_nano,
    _gtk3_terminal_pager,
    _gtk3_terminal_shell,
    _gtk3_terminal_vim,
    _gtk3_terminal_wide_pager,
    _gtk3_text_view,
    _gtk3_text_view_emoji,
    _gtk3_toolbar,
    _gtk3_tree_view,
    _gtk3_two_entries,
    _gtk3_two_windows,
    _gtk3_widget_notebook,
    _orca,
    _web_alert,
    _web_aria_spinbutton,
    _web_attribute_mask,
    _web_autocomplete,
    _web_basic,
    _web_block_context,
    _web_caret_context,
    _web_contracted_braille,
    _web_cssed_brokenness,
    _web_custom_wrappers,
    _web_dialogs,
    _web_dynamic_content,
    _web_editable_embedded,
    _web_editing,
    _web_emoji_links,
    _web_emoji_offset_skew,
    _web_field_states,
    _web_flat_review,
    _web_flat_review_shrink,
    _web_focus_mutations,
    _web_form_fields,
    _web_headings,
    _web_image_link,
    _web_inline_landmarks,
    _web_inline_list,
    _web_inline_list_wrap,
    _web_label_inference,
    _web_landmarks,
    _web_languages,
    _web_line_breaks,
    _web_lists,
    _web_live_regions,
    _web_long_line,
    _web_math,
    _web_missing_cells,
    _web_mixed_line_heights,
    _web_nested_headings,
    _web_offscreen_labels,
    _web_option_removal,
    _web_page_up_down,
    _web_pain_slider,
    _web_pain_slider_no_valuenow,
    _web_plain_text,
    _web_redundant_content,
    _web_removed_child_recovery,
    _web_sister_projects,
    _web_sliders,
    _web_sortable_table,
    _web_structural_navigation,
    _web_tables,
    _web_text_attributes,
    _web_tree,
    _web_useless_images,
    _web_weird_headings,
    _web_wrapped_link,
    _web_wrapping_text,
)

if TYPE_CHECKING:
    import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""

    config.addinivalue_line("markers", "dbus: marks tests as D-Bus specific tests")
    config.addinivalue_line("markers", "gsettings: marks tests as GSettings integration tests")
    config.addinivalue_line(
        "markers", "native_app: marks tests that drive a native GUI app via AT-SPI"
    )
