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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-branches

"""Unit tests for ax_utilities_state.py accessibility state utilities."""

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
class TestAXUtilitiesState:
    """Test AXUtilitiesState class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_state dependencies."""

        essential_modules = test_context.setup_shared_dependencies([])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        messages_mock = essential_modules["orca.messages"]
        messages_mock.CURRENT_DATE = "current date"
        messages_mock.CURRENT_TIME = "current time"
        messages_mock.CURRENT_LOCATION = "current location"
        messages_mock.CURRENT_PAGE = "current page"
        messages_mock.CURRENT_STEP = "current step"
        messages_mock.CURRENT_ITEM = "current item"

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.has_state = test_context.Mock(return_value=False)
        ax_object_class_mock.get_state_set = test_context.Mock()

        def mock_get_attribute(obj, attr, default=None):  # pylint: disable=unused-argument
            return default

        ax_object_class_mock.get_attribute = test_context.Mock(side_effect=mock_get_attribute)
        ax_object_class_mock.get_role = test_context.Mock(return_value=Atspi.Role.UNKNOWN)
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        return essential_modules

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "enabled", "method_name": "is_enabled", "state_type": Atspi.StateType.ENABLED},
            {
                "id": "editable",
                "method_name": "is_editable",
                "state_type": Atspi.StateType.EDITABLE,
            },
            {
                "id": "selected",
                "method_name": "is_selected",
                "state_type": Atspi.StateType.SELECTED,
            },
            {"id": "visible", "method_name": "is_visible", "state_type": Atspi.StateType.VISIBLE},
            {"id": "pressed", "method_name": "is_pressed", "state_type": Atspi.StateType.PRESSED},
        ],
        ids=lambda case: case["id"],
    )
    def test_common_state_methods(self, test_context, case: dict) -> None:
        """Test AXUtilitiesState common state methods."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_state import AXUtilitiesState

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilitiesState, case["method_name"])
        mock_ax_object_class.has_state = test_context.Mock(
            side_effect=lambda obj, state: state == case["state_type"]
        )
        assert method(mock_obj)
        mock_ax_object_class.has_state = test_context.Mock(
            side_effect=lambda obj, state: state != case["state_type"]
        )
        assert not method(mock_obj)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "not_active",
                "is_active": False,
                "attribute_value": None,
                "expected_result": "",
            },
            {
                "id": "active_no_attribute",
                "is_active": True,
                "attribute_value": None,
                "expected_result": "",
            },
            {
                "id": "date_attribute",
                "is_active": True,
                "attribute_value": "date",
                "expected_result": "current date",
            },
            {
                "id": "time_attribute",
                "is_active": True,
                "attribute_value": "time",
                "expected_result": "current time",
            },
            {
                "id": "location_attribute",
                "is_active": True,
                "attribute_value": "location",
                "expected_result": "current location",
            },
            {
                "id": "page_attribute",
                "is_active": True,
                "attribute_value": "page",
                "expected_result": "current page",
            },
            {
                "id": "step_attribute",
                "is_active": True,
                "attribute_value": "step",
                "expected_result": "current step",
            },
            {
                "id": "unknown_attribute",
                "is_active": True,
                "attribute_value": "unknown",
                "expected_result": "current item",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_current_item_status_string(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXUtilitiesState.get_current_item_status_string."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_state import AXUtilitiesState

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesState, "is_active", return_value=case["is_active"]
        )
        mock_ax_object_class.get_attribute = test_context.Mock(return_value=case["attribute_value"])
        result = AXUtilitiesState.get_current_item_status_string(mock_obj)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "empty_state_set", "is_empty": True, "expected_result": True},
            {"id": "non_empty_state_set", "is_empty": False, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_has_no_state(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesState.has_no_state."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_state import AXUtilitiesState

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_state_set = test_context.Mock(
            return_value=test_context.Mock(
                is_empty=test_context.Mock(return_value=case["is_empty"])
            )
        )
        assert AXUtilitiesState.has_no_state(mock_obj) == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "has_checkable_state", "state_scenario": "checkable", "expected_result": True},
            {"id": "has_checked_state", "state_scenario": "checked", "expected_result": True},
            {"id": "no_relevant_state", "state_scenario": "none", "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_checkable(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesState.is_checkable."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_state import AXUtilitiesState

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        if case["state_scenario"] == "checkable":
            mock_ax_object_class.has_state = test_context.Mock(
                side_effect=lambda obj, state: state == Atspi.StateType.CHECKABLE
            )
        elif case["state_scenario"] == "checked":
            mock_ax_object_class.has_state = test_context.Mock(
                side_effect=lambda obj, state: state == Atspi.StateType.CHECKED
            )
        else:
            mock_ax_object_class.has_state = test_context.Mock(return_value=False)

        assert AXUtilitiesState.is_checkable(mock_obj) == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "checked_both_states",
                "method_name": "is_checked",
                "state_scenario": "both_states",
                "expected_result": True,
                "expects_debug": False,
            },
            {
                "id": "checked_checked_only",
                "method_name": "is_checked",
                "state_scenario": "checked_only",
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "checked_none",
                "method_name": "is_checked",
                "state_scenario": "none",
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "expandable_expandable",
                "method_name": "is_expandable",
                "state_scenario": "expandable",
                "expected_result": True,
                "expects_debug": False,
            },
            {
                "id": "expandable_expanded",
                "method_name": "is_expandable",
                "state_scenario": "expanded",
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "expandable_none",
                "method_name": "is_expandable",
                "state_scenario": "none",
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "expanded_both_states",
                "method_name": "is_expanded",
                "state_scenario": "both_states",
                "expected_result": True,
                "expects_debug": False,
            },
            {
                "id": "expanded_expanded_only",
                "method_name": "is_expanded",
                "state_scenario": "expanded_only",
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "expanded_none",
                "method_name": "is_expanded",
                "state_scenario": "none",
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "focusable_focusable",
                "method_name": "is_focusable",
                "state_scenario": "focusable",
                "expected_result": True,
                "expects_debug": False,
            },
            {
                "id": "focusable_focused",
                "method_name": "is_focusable",
                "state_scenario": "focused",
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "focusable_none",
                "method_name": "is_focusable",
                "state_scenario": "none",
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "focused_both_states",
                "method_name": "is_focused",
                "state_scenario": "both_states",
                "expected_result": True,
                "expects_debug": False,
            },
            {
                "id": "focused_focused_only",
                "method_name": "is_focused",
                "state_scenario": "focused_only",
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "focused_none",
                "method_name": "is_focused",
                "state_scenario": "none",
                "expected_result": False,
                "expects_debug": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_state_methods_with_debug(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesState methods that can trigger debug output."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import debug

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        if case["method_name"] == "is_checked":
            if case["state_scenario"] == "both_states":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state
                    in (Atspi.StateType.CHECKED, Atspi.StateType.CHECKABLE),
                )
            elif case["state_scenario"] == "checked_only":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state == Atspi.StateType.CHECKED,
                )
        elif case["method_name"] == "is_expandable":
            if case["state_scenario"] == "expandable":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state == Atspi.StateType.EXPANDABLE,
                )
            elif case["state_scenario"] == "expanded":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state == Atspi.StateType.EXPANDED,
                )
        elif case["method_name"] == "is_expanded":
            if case["state_scenario"] == "both_states":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state
                    in (Atspi.StateType.EXPANDED, Atspi.StateType.EXPANDABLE),
                )
            elif case["state_scenario"] == "expanded_only":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state == Atspi.StateType.EXPANDED,
                )
        elif case["method_name"] == "is_focusable":
            if case["state_scenario"] == "focusable":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state == Atspi.StateType.FOCUSABLE,
                )
            elif case["state_scenario"] == "focused":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state == Atspi.StateType.FOCUSED,
                )
        elif case["method_name"] == "is_focused":
            if case["state_scenario"] == "both_states":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state
                    in (Atspi.StateType.FOCUSED, Atspi.StateType.FOCUSABLE),
                )
            elif case["state_scenario"] == "focused_only":
                test_context.patch_object(
                    AXObject,
                    "has_state",
                    side_effect=lambda obj, state: state == Atspi.StateType.FOCUSED,
                )

        if case["state_scenario"] == "none":
            test_context.patch_object(AXObject, "has_state", return_value=False)

        if case["expects_debug"]:
            test_context.patch_object(
                debug, "print_tokens", new=essential_modules["orca.debug"].print_tokens
            )

        method = getattr(AXUtilitiesState, case["method_name"])
        assert method(mock_obj) == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "hidden_true", "hidden_value": "true", "expected_result": True},
            {"id": "hidden_false", "hidden_value": "false", "expected_result": False},
            {"id": "hidden_none", "hidden_value": None, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_hidden(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesState.is_hidden."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_ax_object_class = essential_modules["orca.ax_object"].AXObject
        from orca.ax_utilities_state import AXUtilitiesState

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_object_class.get_attribute = test_context.Mock(
            side_effect=lambda obj, attr, default=None: case["hidden_value"]
            if attr == "hidden"
            else default
        )
        assert AXUtilitiesState.is_hidden(mock_obj) == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "has_read_only_state",
                "read_only_scenario": "has_read_only_state",
                "expected_result": True,
            },
            {"id": "is_editable", "read_only_scenario": "editable", "expected_result": False},
            {
                "id": "text_role_not_editable",
                "read_only_scenario": "text_role_not_editable",
                "expected_result": True,
            },
            {
                "id": "label_role_not_editable",
                "read_only_scenario": "label_role_not_editable",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_read_only(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesState.is_read_only."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        if case["read_only_scenario"] == "has_read_only_state":
            test_context.patch_object(
                AXObject,
                "has_state",
                side_effect=lambda obj, state: state == Atspi.StateType.READ_ONLY,
            )
        elif case["read_only_scenario"] == "editable":
            test_context.patch_object(AXObject, "has_state", return_value=False)
            test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        elif case["read_only_scenario"] == "text_role_not_editable":
            test_context.patch_object(AXObject, "has_state", return_value=False)
            test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
            test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        elif case["read_only_scenario"] == "label_role_not_editable":
            test_context.patch_object(AXObject, "has_state", return_value=False)
            test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
            test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.LABEL)

        assert AXUtilitiesState.is_read_only(mock_obj) == case["expected_result"]
