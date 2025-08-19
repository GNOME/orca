# Unit tests for ax_value.py methods.
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
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_value.py methods."""

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
class TestAXValue:
    """Test AXValue class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for ax_value module testing."""

        additional_modules = ["orca.ax_utilities", "orca.ax_utilities_state"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.supports_value = test_context.Mock(return_value=True)
        ax_object_class_mock.get_attribute = test_context.Mock(return_value="")
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        ax_utilities_class_mock = test_context.Mock()
        ax_utilities_class_mock.is_indeterminate = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities"].AXUtilities = ax_utilities_class_mock

        ax_utilities_state_class_mock = test_context.Mock()
        ax_utilities_state_class_mock.is_indeterminate = test_context.Mock(
            return_value=False
        )
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState = ax_utilities_state_class_mock

        return essential_modules

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_value_support",
                "supports_value": False,
                "current_value": None,
                "last_known_value": None,
                "expected_result": False,
                "setup_last_known": False,
            },
            {
                "id": "first_time_value",
                "supports_value": True,
                "current_value": 50.0,
                "last_known_value": None,
                "expected_result": True,
                "setup_last_known": False,
            },
            {
                "id": "same_value",
                "supports_value": True,
                "current_value": 50.0,
                "last_known_value": 50.0,
                "expected_result": False,
                "setup_last_known": True,
            },
            {
                "id": "value_changed",
                "supports_value": True,
                "current_value": 75.0,
                "last_known_value": 50.0,
                "expected_result": True,
                "setup_last_known": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_did_value_change(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXValue.did_value_change."""

        self._setup_dependencies(test_context)
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "supports_value", side_effect=lambda obj: case["supports_value"]
        )

        if case["current_value"] is not None:
            test_context.patch_object(
                AXValue, "_get_current_value", side_effect=lambda obj: case["current_value"]
            )

        if case["setup_last_known"]:
            AXValue.LAST_KNOWN_VALUE[hash(mock_accessible)] = case["last_known_value"]
        else:
            AXValue.LAST_KNOWN_VALUE.clear()

        result = AXValue.did_value_change(mock_accessible)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_value_support",
                "supports_value": False,
                "atspi_return_value": None,
                "should_raise_error": False,
                "expected_result": 0.0,
            },
            {
                "id": "success_case",
                "supports_value": True,
                "atspi_return_value": 42.5,
                "should_raise_error": False,
                "expected_result": 42.5,
            },
            {
                "id": "glib_error",
                "supports_value": True,
                "atspi_return_value": None,
                "should_raise_error": True,
                "expected_result": 0.0,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_current_value_private(
        self,
        test_context,
        case: dict,
    ):
        """Test AXValue._get_current_value."""

        self._setup_dependencies(test_context)
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "supports_value", side_effect=lambda obj: case["supports_value"]
        )

        if case["should_raise_error"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Value, "get_current_value", side_effect=raise_glib_error
            )
        elif case["atspi_return_value"] is not None:
            test_context.patch_object(
                Atspi.Value, "get_current_value", side_effect=lambda obj: case["atspi_return_value"]
            )
        else:
            test_context.patch_object(Atspi.Value, "get_current_value", return_value=0.0)

        result = AXValue._get_current_value(mock_obj)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_value_support",
                "supports_value": False,
                "get_current_return": 0.0,
                "expected_result": 0.0,
                "stores_value": False,
            },
            {
                "id": "stores_value",
                "supports_value": True,
                "get_current_return": 75.0,
                "expected_result": 75.0,
                "stores_value": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_current_value(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXValue.get_current_value with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "supports_value", side_effect=lambda obj: case["supports_value"]
        )
        if case["supports_value"]:
            test_context.patch_object(
                AXValue, "_get_current_value", side_effect=lambda obj: case["get_current_return"]
            )
        else:
            test_context.patch_object(
                Atspi.Value, "get_current_value", side_effect=lambda obj: case["get_current_return"]
            )

        AXValue.LAST_KNOWN_VALUE.clear()
        result = AXValue.get_current_value(mock_obj)
        assert result == case["expected_result"]

        if case["stores_value"]:
            assert AXValue.LAST_KNOWN_VALUE[hash(mock_obj)] == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "valuetext_attribute",
                "supports_value": True,
                "valuetext_attr": "75%",
                "atspi_text": "",
                "should_raise_error": False,
                "current_value": 0.0,
                "expected_result": "75%",
            },
            {
                "id": "no_value_support",
                "supports_value": False,
                "valuetext_attr": "",
                "atspi_text": "",
                "should_raise_error": False,
                "current_value": 0.0,
                "expected_result": "",
            },
            {
                "id": "from_atspi",
                "supports_value": True,
                "valuetext_attr": "",
                "atspi_text": "50 percent",
                "should_raise_error": False,
                "current_value": 0.0,
                "expected_result": "50 percent",
            },
            {
                "id": "glib_error",
                "supports_value": True,
                "valuetext_attr": "",
                "atspi_text": "",
                "should_raise_error": True,
                "current_value": 42.0,
                "expected_result": "42",
            },
            {
                "id": "decimal_places",
                "supports_value": True,
                "valuetext_attr": "",
                "atspi_text": "",
                "should_raise_error": False,
                "current_value": 0.125,
                "expected_result": "0.125",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_current_value_text(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXValue.get_current_value_text with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        def mock_get_attribute(obj, name, check_computed=True):  # pylint: disable=unused-argument
            if name == "valuetext":
                return case["valuetext_attr"]
            return ""

        essential_modules["orca.ax_object"].AXObject.get_attribute = mock_get_attribute
        essential_modules["orca.ax_object"].AXObject.supports_value = test_context.Mock(
            return_value=case["supports_value"]
        )

        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        AXValue.LAST_KNOWN_VALUE.clear()

        test_context.patch_object(AXObject, "get_attribute", side_effect=mock_get_attribute)
        test_context.patch_object(
            AXObject, "supports_value", side_effect=lambda obj: case["supports_value"]
        )

        if case["should_raise_error"]:

            def raise_glib_error(self):
                raise GLib.GError("Test error")

            test_context.patch_object(Atspi.Value, "get_text", side_effect=raise_glib_error)
            test_context.patch_object(
                AXValue, "get_current_value", side_effect=lambda obj: case["current_value"]
            )
        else:
            test_context.patch_object(
                Atspi.Value, "get_text", side_effect=lambda self: case["atspi_text"]
            )
            if case["current_value"] != 0.0:
                test_context.patch_object(
                    AXValue, "get_current_value", side_effect=lambda obj: case["current_value"]
                )

        test_context.patch_object(Atspi.Value, "get_current_value", return_value=0.0)

        result = AXValue.get_current_value_text(mock_obj)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_value_support",
                "supports_value": False,
                "current_value": None,
                "is_indeterminate": False,
                "min_val": None,
                "max_val": None,
                "expected_result": None,
            },
            {
                "id": "indeterminate_state",
                "supports_value": True,
                "current_value": 0.0,
                "is_indeterminate": True,
                "min_val": None,
                "max_val": None,
                "expected_result": None,
            },
            {
                "id": "min_equals_max",
                "supports_value": True,
                "current_value": 50.0,
                "is_indeterminate": False,
                "min_val": 100.0,
                "max_val": 100.0,
                "expected_result": None,
            },
            {
                "id": "normal_calculation",
                "supports_value": True,
                "current_value": 75.0,
                "is_indeterminate": False,
                "min_val": 0.0,
                "max_val": 100.0,
                "expected_result": 75,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_value_as_percent(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXValue.get_value_as_percent."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        supports_value_mock = test_context.Mock(return_value=case["supports_value"])
        is_indeterminate_mock = test_context.Mock(return_value=case["is_indeterminate"])
        essential_modules["orca.ax_object"].AXObject.supports_value = supports_value_mock
        essential_modules["orca.ax_utilities"].AXUtilities.is_indeterminate = is_indeterminate_mock

        from orca.ax_value import AXValue
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        AXValue.LAST_KNOWN_VALUE.clear()

        test_context.patch_object(
            AXObject, "supports_value", side_effect=lambda obj: case["supports_value"]
        )

        current_val = case["current_value"] if case["current_value"] is not None else 0.0
        min_val_default = case["min_val"] if case["min_val"] is not None else 0.0
        max_val_default = case["max_val"] if case["max_val"] is not None else 100.0

        test_context.patch_object(
            Atspi.Value, "get_current_value", side_effect=lambda obj: current_val
        )
        test_context.patch_object(
            Atspi.Value, "get_minimum_value", side_effect=lambda obj: min_val_default
        )
        test_context.patch_object(
            Atspi.Value, "get_maximum_value", side_effect=lambda obj: max_val_default
        )

        test_context.patch_object(
            AXUtilities, "is_indeterminate", side_effect=lambda obj: case["is_indeterminate"]
        )

        if case["current_value"] is not None:
            test_context.patch_object(
                AXValue, "get_current_value", side_effect=lambda obj: case["current_value"]
            )
        if case["min_val"] is not None:
            test_context.patch_object(
                AXValue, "get_minimum_value", side_effect=lambda obj: case["min_val"]
            )
        if case["max_val"] is not None:
            test_context.patch_object(
                AXValue, "get_maximum_value", side_effect=lambda obj: case["max_val"]
            )

        result = AXValue.get_value_as_percent(mock_obj)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_value_support",
                "supports_value": False,
                "current_value": None,
                "cached_value": None,
                "expected_result": False,
                "expects_debug_call": False,
                "cache_should_exist": False,
            },
            {
                "id": "cached_value_changed",
                "supports_value": True,
                "current_value": 75.0,
                "cached_value": 50.0,
                "expected_result": True,
                "expects_debug_call": True,
                "cache_should_exist": True,
            },
            {
                "id": "cached_value_unchanged",
                "supports_value": True,
                "current_value": 50.0,
                "cached_value": 50.0,
                "expected_result": False,
                "expects_debug_call": False,
                "cache_should_exist": True,
            },
            {
                "id": "no_cached_value",
                "supports_value": True,
                "current_value": 25.0,
                "cached_value": None,
                "expected_result": True,
                "expects_debug_call": True,
                "cache_should_exist": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_did_value_change_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXValue.did_value_change with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "supports_value", side_effect=lambda obj: case["supports_value"]
        )

        if case["current_value"] is not None:
            test_context.patch_object(
                AXValue, "_get_current_value", side_effect=lambda obj: case["current_value"]
            )

        AXValue.LAST_KNOWN_VALUE.clear()
        if case["cached_value"] is not None:
            AXValue.LAST_KNOWN_VALUE[hash(mock_obj)] = case["cached_value"]

        result = AXValue.did_value_change(mock_obj)
        assert result is case["expected_result"]

        if case["expects_debug_call"]:
            essential_modules["orca.debug"].print_tokens.assert_called()

        if case["cache_should_exist"] and case["cached_value"] is not None:
            assert AXValue.LAST_KNOWN_VALUE[hash(mock_obj)] == case["cached_value"]
        elif not case["cache_should_exist"]:
            assert hash(mock_obj) not in AXValue.LAST_KNOWN_VALUE

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "min_no_value_support",
                "method_name": "get_minimum_value",
                "supports_value": False,
                "atspi_return_value": None,
                "should_raise_error": False,
                "expected_result": 0.0,
            },
            {
                "id": "min_success_case",
                "method_name": "get_minimum_value",
                "supports_value": True,
                "atspi_return_value": 10.0,
                "should_raise_error": False,
                "expected_result": 10.0,
            },
            {
                "id": "min_glib_error",
                "method_name": "get_minimum_value",
                "supports_value": True,
                "atspi_return_value": None,
                "should_raise_error": True,
                "expected_result": 0.0,
            },
            {
                "id": "min_negative_values",
                "method_name": "get_minimum_value",
                "supports_value": True,
                "atspi_return_value": -50.5,
                "should_raise_error": False,
                "expected_result": -50.5,
            },
            {
                "id": "max_no_value_support",
                "method_name": "get_maximum_value",
                "supports_value": False,
                "atspi_return_value": None,
                "should_raise_error": False,
                "expected_result": 0.0,
            },
            {
                "id": "max_success_case",
                "method_name": "get_maximum_value",
                "supports_value": True,
                "atspi_return_value": 100.0,
                "should_raise_error": False,
                "expected_result": 100.0,
            },
            {
                "id": "max_glib_error",
                "method_name": "get_maximum_value",
                "supports_value": True,
                "atspi_return_value": None,
                "should_raise_error": True,
                "expected_result": 0.0,
            },
            {
                "id": "max_large_values",
                "method_name": "get_maximum_value",
                "supports_value": True,
                "atspi_return_value": 99999.99,
                "should_raise_error": False,
                "expected_result": 99999.99,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_minimum_maximum_value(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXValue.get_minimum_value and get_maximum_value with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "supports_value", side_effect=lambda obj: case["supports_value"]
        )

        if case["should_raise_error"]:

            def raise_glib_error(obj):  # pylint: disable=unused-argument
                error_type = "minimum" if "minimum" in case["method_name"] else "maximum"
                raise GLib.GError(f"Test {error_type} value error")

            test_context.patch_object(
                Atspi.Value, case["method_name"], side_effect=raise_glib_error
            )
        elif case["atspi_return_value"] is not None:
            test_context.patch_object(
                Atspi.Value, case["method_name"], side_effect=lambda obj: case["atspi_return_value"]
            )
        else:
            test_context.patch_object(Atspi.Value, case["method_name"], return_value=0.0)

        result = getattr(AXValue, case["method_name"])(mock_obj)
        assert result == case["expected_result"]

        if case["supports_value"]:
            if case["should_raise_error"]:
                essential_modules["orca.debug"].print_message.assert_called()
            else:
                essential_modules["orca.debug"].print_tokens.assert_called()
