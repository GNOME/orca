# Unit tests for ax_action.py methods.
#
# Copyright 2026 Igalia, S.L.
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

# pylint: disable=import-outside-toplevel

"""Unit tests for ax_action.py methods."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXAction:
    """Test AXAction class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_action dependencies."""

        core_modules = [
            "orca.debug",
            "orca.messages",
            "orca.input_event",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.dbus_service",
            "orca.script_manager",
            "orca.orca_i18n",
            "orca.guilabels",
            "orca.text_attribute_names",
            "orca.focus_manager",
            "orca.braille",
            "orca.keynames",
        ]

        essential_modules = {}
        for module_name in core_modules:
            mock_module = test_context.Mock()
            test_context.patch_module(module_name, mock_module)
            essential_modules[module_name] = mock_module

        test_context.configure_shared_module_behaviors(essential_modules)

        return essential_modules

    def test_get_n_actions_with_unsupported_object(self, test_context: OrcaTestContext) -> None:
        """Test AXAction.get_n_actions with object that doesn't support actions."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_action", return_value=False)
        result = AXAction.get_n_actions(mock_accessible)
        assert result == 0

    def test_get_n_actions_with_supported_object(self, test_context: OrcaTestContext) -> None:
        """Test AXAction.get_n_actions with object that supports actions."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_action", return_value=True)
        test_context.patch_object(Atspi.Action, "get_n_actions", return_value=3)
        result = AXAction.get_n_actions(mock_accessible)
        assert result == 3

    def test_get_n_actions_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXAction.get_n_actions handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        def raise_glib_error(_obj) -> None:
            raise GLib.GError("Test n actions error")

        test_context.patch_object(AXObject, "supports_action", return_value=True)
        test_context.patch_object(Atspi.Action, "get_n_actions", side_effect=raise_glib_error)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        result = AXAction.get_n_actions(mock_accessible)
        assert result == 0
        handle_error_mock.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "empty_string", "action_name": "", "expected_result": ""},
            {"id": "simple_name", "action_name": "click", "expected_result": "click"},
            {"id": "camel_case", "action_name": "clickButton", "expected_result": "click-button"},
            {"id": "mixed_case", "action_name": "onClick", "expected_result": "on-click"},
            {
                "id": "with_punctuation",
                "action_name": "click!button",
                "expected_result": "click-button",
            },
            {
                "id": "with_underscore",
                "action_name": "click_button",
                "expected_result": "click-button",
            },
            {"id": "uppercase", "action_name": "CLICK", "expected_result": "click"},
        ],
        ids=lambda case: case["id"],
    )
    def test_normalize_action_name(self, case: dict, test_context) -> None:
        """Test AXAction.normalize_action_name with various inputs."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction

        result = AXAction.normalize_action_name(case["action_name"])
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_negative",
                "test_index": -1,
                "n_actions": 2,
                "atspi_result": None,
                "normalize_result": None,
                "scenario": "invalid_negative",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "invalid_too_high",
                "test_index": 2,
                "n_actions": 2,
                "atspi_result": None,
                "normalize_result": None,
                "scenario": "invalid_too_high",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "valid_index",
                "test_index": 1,
                "n_actions": 2,
                "atspi_result": "clickButton",
                "normalize_result": "click-button",
                "scenario": "valid",
                "expected_result": "click-button",
                "expects_handle_error": False,
            },
            {
                "id": "glib_error",
                "test_index": 0,
                "n_actions": 2,
                "atspi_result": None,
                "normalize_result": None,
                "scenario": "glib_error",
                "expected_result": "",
                "expects_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_action_name(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXAction.get_action_name with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXAction,
            "get_n_actions",
            side_effect=lambda obj: case["n_actions"],
        )
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "valid":
            test_context.patch_object(
                Atspi.Action,
                "get_action_name",
                return_value=case["atspi_result"],
            )
            test_context.patch_object(
                AXAction,
                "normalize_action_name",
                return_value=case["normalize_result"],
            )
        elif case["scenario"] == "glib_error":
            test_context.patch_object(
                Atspi.Action,
                "get_action_name",
                side_effect=GLib.GError("Test error"),
            )

        result = AXAction.get_action_name(mock_accessible, case["test_index"])
        assert result == case["expected_result"]
        if case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "desc_invalid_negative",
                "test_index": -1,
                "n_actions": 2,
                "atspi_result": None,
                "scenario": "invalid_negative",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "desc_invalid_too_high",
                "test_index": 3,
                "n_actions": 2,
                "atspi_result": None,
                "scenario": "invalid_too_high",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "desc_valid_index",
                "test_index": 0,
                "n_actions": 2,
                "atspi_result": "Clicks the button",
                "scenario": "valid",
                "expected_result": "Clicks the button",
                "expects_handle_error": False,
            },
            {
                "id": "desc_glib_error",
                "test_index": 1,
                "n_actions": 2,
                "atspi_result": None,
                "scenario": "glib_error",
                "expected_result": "",
                "expects_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_action_description(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXAction.get_action_description with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXAction,
            "get_n_actions",
            side_effect=lambda obj: case["n_actions"],
        )
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "valid":
            test_context.patch_object(
                Atspi.Action,
                "get_action_description",
                return_value=case["atspi_result"],
            )
        elif case["scenario"] == "glib_error":
            test_context.patch_object(
                Atspi.Action,
                "get_action_description",
                side_effect=GLib.GError("Test error"),
            )

        result = AXAction.get_action_description(mock_accessible, case["test_index"])
        assert result == case["expected_result"]
        if case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "key_binding_invalid_negative",
                "test_index": -1,
                "n_actions": 2,
                "atspi_result": None,
                "scenario": "invalid_negative",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "key_binding_invalid_too_high",
                "test_index": 2,
                "n_actions": 2,
                "atspi_result": None,
                "scenario": "invalid_too_high",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "key_binding_valid_index",
                "test_index": 0,
                "n_actions": 2,
                "atspi_result": "Ctrl+Enter",
                "scenario": "valid",
                "expected_result": "Ctrl+Enter",
                "expects_handle_error": False,
            },
            {
                "id": "key_binding_void_symbol",
                "test_index": 0,
                "n_actions": 2,
                "atspi_result": "<VoidSymbol>",
                "scenario": "void_symbol",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "key_binding_glib_error",
                "test_index": 1,
                "n_actions": 2,
                "atspi_result": None,
                "scenario": "glib_error",
                "expected_result": "",
                "expects_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_action_key_binding(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXAction.get_action_key_binding with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXAction,
            "get_n_actions",
            side_effect=lambda obj: case["n_actions"],
        )
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] in ["valid", "void_symbol"]:
            test_context.patch_object(
                Atspi.Action,
                "get_key_binding",
                return_value=case["atspi_result"],
            )
        elif case["scenario"] == "glib_error":
            test_context.patch_object(
                Atspi.Action,
                "get_key_binding",
                side_effect=GLib.GError("Test error"),
            )

        result = AXAction.get_action_key_binding(mock_accessible, case["test_index"])
        assert result == case["expected_result"]
        if case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    def test_do_action_success(self, test_context: OrcaTestContext) -> None:
        """Test AXAction.do_action success."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXAction, "get_n_actions", return_value=2)
        sys.modules["gi.repository"].Atspi.Action.do_action = test_context.Mock(return_value=True)
        result = AXAction.do_action(mock_accessible, 0)
        assert result is True

    def test_do_action_invalid_index(self, test_context: OrcaTestContext) -> None:
        """Test AXAction.do_action invalid index."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXAction, "get_n_actions", return_value=2)
        result = AXAction.do_action(mock_accessible, 5)
        assert result is False

    def test_do_action_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXAction.do_action handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXAction, "get_n_actions", return_value=2)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        sys.modules["gi.repository"].Atspi.Action.do_action = test_context.Mock(
            side_effect=sys.modules["gi.repository"].GLib.GError("Test error"),
        )
        result = AXAction.do_action(mock_accessible, 0)
        assert result is False
