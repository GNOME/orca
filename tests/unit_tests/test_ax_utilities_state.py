# Unit tests for ax_utils_state.py accessibility state utilities.
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
# pylint: disable=too-many-lines
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-argument
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for ax_utilities_state.py accessibility state utilities."""


from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi



@pytest.mark.unit
class TestAXUtilitiesState:
    """Test state identification methods."""


    @pytest.mark.parametrize(
        "method_name, state_type",
        [
            pytest.param("has_popup", Atspi.StateType.HAS_POPUP, id="popup"),
            pytest.param("has_tooltip", Atspi.StateType.HAS_TOOLTIP, id="tooltip"),
            pytest.param("is_active", Atspi.StateType.ACTIVE, id="active"),
            pytest.param("is_animated", Atspi.StateType.ANIMATED, id="animated"),
            pytest.param("is_armed", Atspi.StateType.ARMED, id="armed"),
            pytest.param("is_busy", Atspi.StateType.BUSY, id="busy"),
            pytest.param("is_collapsed", Atspi.StateType.COLLAPSED, id="collapsed"),
            pytest.param("is_default", Atspi.StateType.IS_DEFAULT, id="default"),
            pytest.param("is_defunct", Atspi.StateType.DEFUNCT, id="defunct"),
            pytest.param("is_editable", Atspi.StateType.EDITABLE, id="editable"),
            pytest.param("is_enabled", Atspi.StateType.ENABLED, id="enabled"),
            pytest.param("is_horizontal", Atspi.StateType.HORIZONTAL, id="horizontal"),
            pytest.param("is_iconified", Atspi.StateType.ICONIFIED, id="iconified"),
            pytest.param("is_indeterminate", Atspi.StateType.INDETERMINATE, id="indeterminate"),
            pytest.param("is_invalid_state", Atspi.StateType.INVALID, id="invalid_state"),
            pytest.param("is_invalid_entry", Atspi.StateType.INVALID_ENTRY, id="invalid_entry"),
            pytest.param("is_modal", Atspi.StateType.MODAL, id="modal"),
            pytest.param("is_multi_line", Atspi.StateType.MULTI_LINE, id="multi_line"),
            pytest.param(
                "is_multiselectable", Atspi.StateType.MULTISELECTABLE, id="multiselectable"
            ),
            pytest.param("is_opaque", Atspi.StateType.OPAQUE, id="opaque"),
            pytest.param("is_pressed", Atspi.StateType.PRESSED, id="pressed"),
            pytest.param("is_required", Atspi.StateType.REQUIRED, id="required"),
            pytest.param("is_resizable", Atspi.StateType.RESIZABLE, id="resizable"),
            pytest.param("is_selectable", Atspi.StateType.SELECTABLE, id="selectable"),
            pytest.param(
                "is_selectable_text", Atspi.StateType.SELECTABLE_TEXT, id="selectable_text"
            ),
            pytest.param("is_selected", Atspi.StateType.SELECTED, id="selected"),
            pytest.param("is_sensitive", Atspi.StateType.SENSITIVE, id="sensitive"),
            pytest.param("is_showing", Atspi.StateType.SHOWING, id="showing"),
            pytest.param("is_single_line", Atspi.StateType.SINGLE_LINE, id="single_line"),
            pytest.param("is_stale", Atspi.StateType.STALE, id="stale"),
            pytest.param("is_transient", Atspi.StateType.TRANSIENT, id="transient"),
            pytest.param("is_truncated", Atspi.StateType.TRUNCATED, id="truncated"),
            pytest.param("is_vertical", Atspi.StateType.VERTICAL, id="vertical"),
            pytest.param("is_visible", Atspi.StateType.VISIBLE, id="visible"),
            pytest.param("is_visited", Atspi.StateType.VISITED, id="visited"),
            pytest.param(
                "manages_descendants", Atspi.StateType.MANAGES_DESCENDANTS, id="manages_descendants"
            ),
            pytest.param(
                "supports_autocompletion",
                Atspi.StateType.SUPPORTS_AUTOCOMPLETION,
                id="supports_autocompletion"
            ),
        ],
    )
    def test_simple_state_methods(
        self, monkeypatch, method_name, state_type, mock_orca_dependencies
    ):
        """Test AXUtilitiesState simple state methods."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilitiesState, method_name)

        monkeypatch.setattr(
            AXObject, "has_state", lambda obj, state: state == state_type
        )
        assert method(mock_obj)

        monkeypatch.setattr(
            AXObject, "has_state", lambda obj, state: state != state_type
        )
        assert not method(mock_obj)

    def test_get_current_item_status_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.get_current_item_status_string."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import messages

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object is not active
        monkeypatch.setattr(AXUtilitiesState, "is_active", lambda obj: False)
        assert AXUtilitiesState.get_current_item_status_string(mock_obj) == ""

        # Scenario: Object is active but has no attribute
        monkeypatch.setattr(AXUtilitiesState, "is_active", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: None)
        assert AXUtilitiesState.get_current_item_status_string(mock_obj) == ""

        # Scenario: Object has "date" attribute
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: "date")
        assert AXUtilitiesState.get_current_item_status_string(mock_obj) == messages.CURRENT_DATE

        # Scenario: Object has "time" attribute
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: "time")
        assert AXUtilitiesState.get_current_item_status_string(mock_obj) == messages.CURRENT_TIME

        # Scenario: Object has "location" attribute
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: "location")
        assert (
            AXUtilitiesState.get_current_item_status_string(mock_obj) == messages.CURRENT_LOCATION
        )

        # Scenario: Object has "page" attribute
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: "page")
        assert AXUtilitiesState.get_current_item_status_string(mock_obj) == messages.CURRENT_PAGE

        # Scenario: Object has "step" attribute
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: "step")
        assert AXUtilitiesState.get_current_item_status_string(mock_obj) == messages.CURRENT_STEP

        # Scenario: Object has unknown attribute type
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: "unknown")
        assert AXUtilitiesState.get_current_item_status_string(mock_obj) == messages.CURRENT_ITEM

    def test_has_no_state(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.has_no_state."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: State set is empty
        monkeypatch.setattr(
            AXObject, "get_state_set", lambda obj: Mock(is_empty=lambda: True)
        )
        assert AXUtilitiesState.has_no_state(mock_obj)

        # Scenario: State set is not empty
        monkeypatch.setattr(
            AXObject, "get_state_set", lambda obj: Mock(is_empty=lambda: False)
        )
        assert not AXUtilitiesState.has_no_state(mock_obj)

    def test_is_checkable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_checkable."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object has CHECKABLE state
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state == Atspi.StateType.CHECKABLE,
        )
        assert AXUtilitiesState.is_checkable(mock_obj)

        # Scenario: Object has CHECKED state but not CHECKABLE
        monkeypatch.setattr(
            AXObject, "has_state", lambda obj, state: state == Atspi.StateType.CHECKED
        )
        from orca import debug
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)
        assert AXUtilitiesState.is_checkable(mock_obj)

        # Scenario: Object has no relevant states
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        assert not AXUtilitiesState.is_checkable(mock_obj)

    def test_is_checked(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_checked."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object has both CHECKED and CHECKABLE states
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state in (Atspi.StateType.CHECKED, Atspi.StateType.CHECKABLE),
        )
        assert AXUtilitiesState.is_checked(mock_obj)

        # Scenario: Object has only CHECKED state
        monkeypatch.setattr(
            AXObject, "has_state", lambda obj, state: state == Atspi.StateType.CHECKED
        )
        from orca import debug
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)
        assert AXUtilitiesState.is_checked(mock_obj)

        # Scenario: Object has no relevant states
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        assert not AXUtilitiesState.is_checked(mock_obj)


    def test_is_expandable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_expandable."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object has EXPANDABLE state
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state == Atspi.StateType.EXPANDABLE,
        )
        assert AXUtilitiesState.is_expandable(mock_obj)

        # Scenario: Object has EXPANDED state but not EXPANDABLE
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state == Atspi.StateType.EXPANDED,
        )
        from orca import debug
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)
        assert AXUtilitiesState.is_expandable(mock_obj)

        # Scenario: Object has no relevant states
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        assert not AXUtilitiesState.is_expandable(mock_obj)

    def test_is_expanded(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_expanded."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object has both EXPANDED and EXPANDABLE states
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state in (Atspi.StateType.EXPANDED, Atspi.StateType.EXPANDABLE),
        )
        assert AXUtilitiesState.is_expanded(mock_obj)

        # Scenario: Object has only EXPANDED state
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state == Atspi.StateType.EXPANDED,
        )
        from orca import debug
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)
        assert AXUtilitiesState.is_expanded(mock_obj)

        # Scenario: Object has no relevant states
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        assert not AXUtilitiesState.is_expanded(mock_obj)

    def test_is_focusable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_focusable."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object has FOCUSABLE state
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state == Atspi.StateType.FOCUSABLE,
        )
        assert AXUtilitiesState.is_focusable(mock_obj)

        # Scenario: Object has FOCUSED state but not FOCUSABLE
        monkeypatch.setattr(
            AXObject, "has_state", lambda obj, state: state == Atspi.StateType.FOCUSED
        )
        from orca import debug
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)
        assert AXUtilitiesState.is_focusable(mock_obj)

        # Scenario: Object has no relevant states
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        assert not AXUtilitiesState.is_focusable(mock_obj)

    def test_is_focused(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_focused."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object has both FOCUSED and FOCUSABLE states
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state in (Atspi.StateType.FOCUSED, Atspi.StateType.FOCUSABLE),
        )
        assert AXUtilitiesState.is_focused(mock_obj)

        # Scenario: Object has only FOCUSED state
        monkeypatch.setattr(
            AXObject, "has_state", lambda obj, state: state == Atspi.StateType.FOCUSED
        )
        from orca import debug
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)
        assert AXUtilitiesState.is_focused(mock_obj)

        # Scenario: Object has no relevant states
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        assert not AXUtilitiesState.is_focused(mock_obj)

    def test_is_hidden(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_hidden."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario 1: Object has "hidden" attribute set to "true"
        monkeypatch.setattr(
            AXObject, "get_attribute",
            lambda obj, attr, default: "true" if attr == "hidden" else default,
        )
        assert AXUtilitiesState.is_hidden(mock_obj)

        # Scenario 2: Object has "hidden" attribute set to "false"
        monkeypatch.setattr(
            AXObject, "get_attribute",
            lambda obj, attr, default: "false" if attr == "hidden" else default,
        )
        assert not AXUtilitiesState.is_hidden(mock_obj)

        # Scenario 3: Object does not have "hidden" attribute
        monkeypatch.setattr(
            AXObject, "get_attribute", lambda obj, attr, default: default
        )
        assert not AXUtilitiesState.is_hidden(mock_obj)


    def test_is_read_only(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesState.is_read_only."""

        clean_module_cache("orca.ax_utilities_state")
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario 1: Object has READ_ONLY state
        monkeypatch.setattr(
            AXObject, "has_state",
            lambda obj, state: state == Atspi.StateType.READ_ONLY,
        )
        assert AXUtilitiesState.is_read_only(mock_obj)

        # Scenario 2: Object does not have READ_ONLY state but is editable
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        monkeypatch.setattr(
            AXUtilitiesState, "is_editable", lambda obj: True
        )
        assert not AXUtilitiesState.is_read_only(mock_obj)

        # Scenario 3: Object does not have READ_ONLY state and is not editable, but is TEXT role
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        monkeypatch.setattr(
            AXUtilitiesState, "is_editable", lambda obj: False
        )
        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        assert AXUtilitiesState.is_read_only(mock_obj)

        # Scenario 4: Object does not have READ_ONLY state, is not editable, and is not TEXT role
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        monkeypatch.setattr(
            AXUtilitiesState, "is_editable", lambda obj: False
        )
        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.LABEL)
        assert not AXUtilitiesState.is_read_only(mock_obj)
