# Unit tests for ax_object.py methods.
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
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-order

"""Unit tests for ax_object.py methods."""

from __future__ import annotations

import sys
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
class TestAXObject:
    """Test AXObject class methods."""

    def _setup_soffice_collection_mocks(
        self, test_context, has_document_text=False, has_spreadsheet=False
    ):
        """Set up common mocks for soffice collection testing scenarios."""

        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_name", return_value="soffice")
        test_context.patch_object(Atspi.Accessible, "get_application", return_value=mock_app)
        test_context.patch_object(
            Atspi.Accessible, "get_collection_iface", side_effect=lambda obj: test_context.Mock()
        )

        if has_document_text:
            mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(
                AXObject,
                "find_ancestor_inclusive",
                side_effect=lambda obj, func: mock_ancestor if func(mock_ancestor) else None,
            )
            test_context.patch_object(
                AXObject,
                "get_role",
                side_effect=lambda obj: (
                    Atspi.Role.DOCUMENT_TEXT if obj == mock_ancestor else Atspi.Role.BUTTON
                ),
            )
        else:
            test_context.patch_object(
                AXObject, "find_ancestor_inclusive", return_value=None
            )
            if has_spreadsheet:
                test_context.patch_object(
                    AXObject, "_has_document_spreadsheet", return_value=True
                )
            else:
                test_context.patch_object(
                    AXObject, "_has_document_spreadsheet", return_value=False
                )

        return mock_accessible

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_object dependencies."""

        core_modules = [
            "orca.debug",
            "orca.messages",
            "orca.input_event",
            "orca.settings",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.settings_manager",
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
        keynames_mock = essential_modules["orca.keynames"]
        keynames_mock.KEY_BACKSPACE = "BackSpace"
        keynames_mock.KEY_DELETE = "Delete"
        keynames_mock.KEY_TAB = "Tab"
        keynames_mock.KEY_RETURN = "Return"
        keynames_mock.KEY_ESCAPE = "Escape"

        return essential_modules

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "gecko_section_hack",
                "test_type": "gecko_section_hack",
                "obj_role": Atspi.Role.SECTION,
                "parent_role": Atspi.Role.FRAME,
                "toolkit": "gecko",
                "expected_result": True,
            },
            {
                "id": "normal_object",
                "test_type": "normal_object",
                "obj_role": Atspi.Role.BUTTON,
                "parent_role": None,
                "toolkit": "gtk",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_bogus(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.is_bogus with various object types."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible) if case["parent_role"] else None

        if case["test_type"] == "gecko_section_hack":
            mock_get_role = test_context.Mock(
                side_effect=lambda obj: case["obj_role"]
                if obj == mock_accessible
                else case["parent_role"]
            )
        else:
            mock_get_role = test_context.Mock(return_value=case["obj_role"])

        mock_get_parent = test_context.Mock(return_value=mock_parent)
        mock_get_toolkit = test_context.Mock(return_value=case["toolkit"])
        test_context.patch_object(AXObject, "get_role", new=mock_get_role)
        test_context.patch_object(AXObject, "get_parent", new=mock_get_parent)
        test_context.patch_object(AXObject, "get_toolkit_name", new=mock_get_toolkit)

        result = AXObject.is_bogus(mock_accessible)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "qt_bug",
                "toolkit": "qt",
                "obj_type": "mock",
                "parent_role": "window",
                "has_grandparent": False,
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "good_qt_ancestry",
                "toolkit": "qt",
                "obj_type": "mock",
                "parent_role": "button",
                "has_grandparent": True,
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "non_qt",
                "toolkit": "gtk",
                "obj_type": "mock",
                "parent_role": "button",
                "has_grandparent": False,
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "none_object",
                "toolkit": "qt",
                "obj_type": "none",
                "parent_role": "button",
                "has_grandparent": False,
                "expected_result": False,
                "expects_debug": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_has_broken_ancestry(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.has_broken_ancestry with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        if case["obj_type"] == "none":
            result = AXObject.has_broken_ancestry(None)
            assert result is case["expected_result"]
            return

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "get_toolkit_name", side_effect=lambda obj: case["toolkit"]
        )

        if case["toolkit"] == "qt":
            mock_parent = test_context.Mock(spec=Atspi.Accessible)

            def mock_get_parent(obj) -> object:
                if obj == mock_accessible:
                    return mock_parent
                if case["has_grandparent"] and obj == mock_parent:
                    mock_app = test_context.Mock(spec=Atspi.Accessible)
                    return mock_app
                return None

            def mock_get_role(obj) -> object:
                if obj == mock_parent and case["parent_role"] == "window":
                    return Atspi.Role.WINDOW
                if case["has_grandparent"] and obj != mock_accessible and obj != mock_parent:
                    return Atspi.Role.APPLICATION
                return Atspi.Role.BUTTON

            test_context.patch_object(AXObject, "get_parent", new=mock_get_parent)
            test_context.patch_object(AXObject, "get_role", new=mock_get_role)

        result = AXObject.has_broken_ancestry(mock_accessible)
        assert result is case["expected_result"]

        if case["expects_debug"]:
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "successful",
                "toolkit_result": "GTK",
                "expects_error": False,
                "expected_result": "gtk",
                "expects_debug": False,
            },
            {
                "id": "glib_error",
                "toolkit_result": GLib.GError("Test error"),
                "expects_error": True,
                "expected_result": "",
                "expects_debug": True,
            },
            {
                "id": "none_result",
                "toolkit_result": None,
                "expects_error": False,
                "expected_result": "",
                "expects_debug": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_toolkit_name(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.get_toolkit_name with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(Atspi.Accessible, "get_application", return_value=mock_app)

        if case["expects_error"]:

            def raise_glib_error(app):
                raise case["toolkit_result"]

            test_context.patch_object(
                Atspi.Accessible, "get_toolkit_name", side_effect=raise_glib_error
            )
            from orca import debug

            test_context.patch_object(
                debug, "print_tokens", new=essential_modules["orca.debug"].print_tokens
            )
        else:
            test_context.patch_object(
                Atspi.Accessible, "get_toolkit_name", side_effect=lambda app: case["toolkit_result"]
            )

        result = AXObject.get_toolkit_name(mock_accessible)
        assert result == case["expected_result"]

        if case["expects_debug"]:
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "supports_action",
                "interface_type": "action",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_action_interface",
                "interface_type": "action",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "action_glib_error",
                "interface_type": "action",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_component",
                "interface_type": "component",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_component_interface",
                "interface_type": "component",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "component_glib_error",
                "interface_type": "component",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_document",
                "interface_type": "document",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_document_interface",
                "interface_type": "document",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "document_glib_error",
                "interface_type": "document",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_editable_text",
                "interface_type": "editable_text",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_editable_text_interface",
                "interface_type": "editable_text",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "editable_text_glib_error",
                "interface_type": "editable_text",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_hyperlink",
                "interface_type": "hyperlink",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_hyperlink_interface",
                "interface_type": "hyperlink",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "hyperlink_glib_error",
                "interface_type": "hyperlink",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_hypertext",
                "interface_type": "hypertext",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_hypertext_interface",
                "interface_type": "hypertext",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "hypertext_glib_error",
                "interface_type": "hypertext",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_image",
                "interface_type": "image",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_image_interface",
                "interface_type": "image",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "image_glib_error",
                "interface_type": "image",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_selection",
                "interface_type": "selection",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_selection_interface",
                "interface_type": "selection",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "selection_glib_error",
                "interface_type": "selection",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_table",
                "interface_type": "table",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_table_interface",
                "interface_type": "table",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "table_glib_error",
                "interface_type": "table",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_table_cell",
                "interface_type": "table_cell",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_table_cell_interface",
                "interface_type": "table_cell",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "table_cell_glib_error",
                "interface_type": "table_cell",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_text",
                "interface_type": "text",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_text_interface",
                "interface_type": "text",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "text_glib_error",
                "interface_type": "text",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
            {
                "id": "supports_value",
                "interface_type": "value",
                "interface_result": "mock_interface",
                "raises_error": False,
                "expected_result": True,
            },
            {
                "id": "no_value_interface",
                "interface_type": "value",
                "interface_result": None,
                "raises_error": False,
                "expected_result": False,
            },
            {
                "id": "value_glib_error",
                "interface_type": "value",
                "interface_result": None,
                "raises_error": True,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_supports_interface_parametrized(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.supports_* interface methods with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        interface_map = {
            "action": ("get_action_iface", AXObject.supports_action),
            "component": ("get_component_iface", AXObject.supports_component),
            "document": ("get_document_iface", AXObject.supports_document),
            "editable_text": ("get_editable_text_iface", AXObject.supports_editable_text),
            "hyperlink": ("get_hyperlink", AXObject.supports_hyperlink),
            "hypertext": ("get_hypertext_iface", AXObject.supports_hypertext),
            "image": ("get_image_iface", AXObject.supports_image),
            "selection": ("get_selection_iface", AXObject.supports_selection),
            "table": ("get_table_iface", AXObject.supports_table),
            "table_cell": ("get_table_cell", AXObject.supports_table_cell),
            "text": ("get_text_iface", AXObject.supports_text),
            "value": ("get_value_iface", AXObject.supports_value),
        }

        getter_name, support_method = interface_map[case["interface_type"]]

        if case["raises_error"]:

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test error")

            test_context.patch_object(Atspi.Accessible, getter_name, side_effect=raise_glib_error)
            handle_error_mock = test_context.Mock()
            test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        else:
            actual_interface_result = (
                test_context.Mock()
                if case["interface_result"] == "mock_interface"
                else case["interface_result"]
            )
            test_context.patch_object(
                Atspi.Accessible, getter_name, return_value=actual_interface_result
            )

        result = support_method(mock_accessible)
        assert result is case["expected_result"]

        if case["raises_error"]:
            handle_error_mock.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_reason",
                "reason": "test reason",
                "expected_message": "AXObject: Clearing local cache. Reason: test reason",
            },
            {
                "id": "without_reason",
                "reason": None,
                "expected_message": "AXObject: Clearing local cache.",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_clear_all_dictionaries(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXObject._clear_all_dictionaries with and without reason."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD[123] = True
        AXObject.OBJECT_ATTRIBUTES[456] = {"role": "button"}

        if case["reason"]:
            AXObject._clear_all_dictionaries(case["reason"])
        else:
            AXObject._clear_all_dictionaries()

        assert len(AXObject.KNOWN_DEAD) == 0
        assert len(AXObject.OBJECT_ATTRIBUTES) == 0
        essential_modules["orca.debug"].print_message.assert_called_with(
            essential_modules["orca.debug"].LEVEL_INFO, case["expected_message"], True
        )

    def test_clear_cache_now_calls_clear_all_dictionaries(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXObject.clear_cache_now calls _clear_all_dictionaries."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        clear_mock = test_context.Mock()
        test_context.patch_object(AXObject, "_clear_all_dictionaries", new=clear_mock)
        AXObject.clear_cache_now("test reason")
        clear_mock.assert_called_once_with("test reason")

    def test_start_cache_clearing_thread(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.start_cache_clearing_thread creates and starts thread."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_thread = test_context.Mock()
        thread_constructor_mock = test_context.Mock(return_value=mock_thread)
        test_context.patch("threading.Thread", new=thread_constructor_mock)
        AXObject.start_cache_clearing_thread()
        thread_constructor_mock.assert_called_once_with(target=AXObject._clear_stored_data)
        assert mock_thread.daemon is True
        mock_thread.start.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "scenario": "invalid_object",
                "app_name": "",
                "has_interface": False,
                "has_document_text": False,
                "has_spreadsheet": False,
                "raises_app_error": False,
                "raises_iface_error": False,
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "get_application_error",
                "scenario": "get_application_error",
                "app_name": "",
                "has_interface": False,
                "has_document_text": False,
                "has_spreadsheet": False,
                "raises_app_error": True,
                "raises_iface_error": False,
                "expected_result": False,
                "expects_debug": True,
            },
            {
                "id": "get_collection_iface_error",
                "scenario": "get_collection_iface_error",
                "app_name": "firefox",
                "has_interface": False,
                "has_document_text": False,
                "has_spreadsheet": False,
                "raises_app_error": False,
                "raises_iface_error": True,
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "non_soffice_with_interface",
                "scenario": "non_soffice_with_interface",
                "app_name": "firefox",
                "has_interface": True,
                "has_document_text": False,
                "has_spreadsheet": False,
                "raises_app_error": False,
                "raises_iface_error": False,
                "expected_result": True,
                "expects_debug": False,
            },
            {
                "id": "non_soffice_without_interface",
                "scenario": "non_soffice_without_interface",
                "app_name": "gedit",
                "has_interface": False,
                "has_document_text": False,
                "has_spreadsheet": False,
                "raises_app_error": False,
                "raises_iface_error": False,
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "soffice_with_document_text",
                "scenario": "soffice_with_document_text",
                "app_name": "soffice",
                "has_interface": True,
                "has_document_text": True,
                "has_spreadsheet": False,
                "raises_app_error": False,
                "raises_iface_error": False,
                "expected_result": True,
                "expects_debug": False,
            },
            {
                "id": "soffice_with_spreadsheet",
                "scenario": "soffice_with_spreadsheet",
                "app_name": "soffice",
                "has_interface": True,
                "has_document_text": False,
                "has_spreadsheet": True,
                "raises_app_error": False,
                "raises_iface_error": False,
                "expected_result": False,
                "expects_debug": True,
            },
            {
                "id": "soffice_without_text_or_spreadsheet",
                "scenario": "soffice_without_text_or_spreadsheet",
                "app_name": "soffice",
                "has_interface": True,
                "has_document_text": False,
                "has_spreadsheet": False,
                "raises_app_error": False,
                "raises_iface_error": False,
                "expected_result": True,
                "expects_debug": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_supports_collection(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.supports_collection with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        if case["scenario"] == "invalid_object":
            mock_accessible = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(AXObject, "is_valid", return_value=False)
        elif case["app_name"] == "soffice":
            mock_accessible = self._setup_soffice_collection_mocks(
                test_context,
                has_document_text=case["has_document_text"],
                has_spreadsheet=case["has_spreadsheet"],
            )
        else:
            mock_accessible = test_context.Mock(spec=Atspi.Accessible)
            mock_app = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(
                AXObject, "get_name", side_effect=lambda obj: case["app_name"]
            )

            if case["raises_app_error"]:

                def raise_app_error(_obj) -> None:
                    raise GLib.GError("Test application error")

                test_context.patch_object(
                    Atspi.Accessible, "get_application", side_effect=raise_app_error
                )
            elif case["raises_iface_error"]:

                def raise_iface_error(_obj) -> None:
                    raise GLib.GError("Test collection iface error")

                handle_error_mock = test_context.Mock()
                test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
                test_context.patch_object(
                    Atspi.Accessible, "get_application", return_value=mock_app
                )
                test_context.patch_object(
                    Atspi.Accessible, "get_collection_iface", side_effect=raise_iface_error
                )
            else:
                test_context.patch_object(
                    Atspi.Accessible, "get_application", return_value=mock_app
                )
                mock_iface = test_context.Mock() if case["has_interface"] else None
                test_context.patch_object(
                    Atspi.Accessible, "get_collection_iface", return_value=mock_iface
                )

        result = AXObject.supports_collection(mock_accessible)
        assert result is case["expected_result"]

        if case["expects_debug"]:
            essential_modules["orca.debug"].print_message.assert_called()
            if case["scenario"] == "get_application_error":
                calls = essential_modules["orca.debug"].print_message.call_args_list
                assert len(calls) == 1
                call_args = calls[0][0]
                assert call_args[0] == essential_modules["orca.debug"].LEVEL_INFO
                assert "AXObject: Exception in supports_collection:" in call_args[1]
                assert "Test application error" in call_args[1]
            elif case["scenario"] == "soffice_with_spreadsheet":
                essential_modules["orca.debug"].print_message.assert_called_with(
                    essential_modules["orca.debug"].LEVEL_INFO,
                    "AXObject: Treating soffice as not supporting collection due to spreadsheet.",
                    True,
                )

        if case["raises_iface_error"]:
            handle_error_mock.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "none_object", "obj_type": "none", "is_dead": False, "expected_result": False},
            {
                "id": "known_dead_object",
                "obj_type": "mock",
                "is_dead": True,
                "expected_result": False,
            },
            {"id": "valid_object", "obj_type": "mock", "is_dead": False, "expected_result": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_valid(self, test_context, case: dict) -> None:
        """Test AXObject.is_valid with different object scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        if case["obj_type"] == "none":
            test_obj = None
        else:
            test_obj = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(
                AXObject, "object_is_known_dead", side_effect=lambda obj: case["is_dead"]
            )

        result = AXObject.is_valid(test_obj)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "none_object", "use_none_object": True, "cache_status": None, "expected": False},
            {
                "id": "not_in_cache",
                "use_none_object": False,
                "cache_status": "clear",
                "expected": False,
            },
            {
                "id": "in_cache_as_dead",
                "use_none_object": False,
                "cache_status": True,
                "expected": True,
            },
            {
                "id": "in_cache_as_alive",
                "use_none_object": False,
                "cache_status": False,
                "expected": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_object_is_known_dead_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.object_is_known_dead with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        if case["use_none_object"]:
            test_obj = None
        else:
            test_obj = test_context.Mock(spec=Atspi.Accessible)
            if case["cache_status"] == "clear":
                AXObject.KNOWN_DEAD.clear()
            elif isinstance(case["cache_status"], bool):
                AXObject.KNOWN_DEAD[hash(test_obj)] = case["cache_status"]

        result = AXObject.object_is_known_dead(test_obj)
        assert result is case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "none_object",
                "use_none_object": True,
                "initial_status": None,
                "new_status": True,
                "expected_status": None,
                "expects_debug_call": False,
            },
            {
                "id": "same_status",
                "use_none_object": False,
                "initial_status": True,
                "new_status": True,
                "expected_status": True,
                "expects_debug_call": False,
            },
            {
                "id": "mark_as_dead",
                "use_none_object": False,
                "initial_status": "clear",
                "new_status": True,
                "expected_status": True,
                "expects_debug_call": "print_message",
            },
            {
                "id": "resurrect_object",
                "use_none_object": False,
                "initial_status": True,
                "new_status": False,
                "expected_status": False,
                "expects_debug_call": "print_tokens",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_set_known_dead_status_scenarios(  # pylint: disable=too-many-arguments
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject._set_known_dead_status with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        if case["use_none_object"]:
            test_obj = None
            AXObject._set_known_dead_status(test_obj, case["new_status"])
        else:
            test_obj = test_context.Mock(spec=Atspi.Accessible)
            if case["initial_status"] == "clear":
                AXObject.KNOWN_DEAD.clear()
            elif isinstance(case["initial_status"], bool):
                AXObject.KNOWN_DEAD[hash(test_obj)] = case["initial_status"]

            AXObject._set_known_dead_status(test_obj, case["new_status"])

            if case["expected_status"] is not None:
                assert AXObject.KNOWN_DEAD[hash(test_obj)] is case["expected_status"]

        if case["expects_debug_call"] == "print_message":
            essential_modules["orca.debug"].print_message.assert_called()
        elif case["expects_debug_call"] == "print_tokens":
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "object_not_exist",
                "error_string": "accessible/123 does not exist",
                "expected_msg_part": "object no longer exists",
            },
            {
                "id": "app_not_exist",
                "error_string": "The application no longer exists",
                "expected_msg_part": "app no longer exists",
            },
            {
                "id": "other_error",
                "error_string": "Some other error",
                "expected_msg_part": "Some other error",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_handle_error(self, test_context, case: dict) -> None:
        """Test AXObject.handle_error with different error types."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        error = Exception(case["error_string"])
        msg = f"AXObject: Error calling method: {case['error_string']}"
        AXObject.handle_error(mock_accessible, error, msg)
        essential_modules["orca.debug"].print_message.assert_called_once()
        call_args = essential_modules["orca.debug"].print_message.call_args[0]
        assert case["expected_msg_part"] in call_args[1]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "valid_object",
                "scenario": "valid_object",
                "expected_result": [1, 2],
                "should_call_handle_error": False,
            },
            {
                "id": "glib_error",
                "scenario": "glib_error",
                "expected_result": [],
                "should_call_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_path(self, test_context, case: dict) -> None:
        """Test AXObject.get_path with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "valid_object":
            mock_parent = test_context.Mock(spec=Atspi.Accessible)

            def mock_get_index(obj) -> int:
                if obj == mock_accessible:
                    return 2
                if obj == mock_parent:
                    return 1
                return 0

            test_context.patch_object(
                Atspi.Accessible, "get_index_in_parent", new=mock_get_index
            )

            def mock_get_parent_checked(obj) -> object:
                if obj == mock_accessible:
                    return mock_parent
                return None

            test_context.patch_object(
                AXObject, "get_parent_checked", new=mock_get_parent_checked
            )

        elif case["scenario"] == "glib_error":

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test path error")

            test_context.patch_object(
                Atspi.Accessible, "get_index_in_parent", side_effect=raise_glib_error
            )

        result = AXObject.get_path(mock_accessible)
        assert result == case["expected_result"]

        if case["should_call_handle_error"]:
            handle_error_mock.assert_called_once()
        else:
            handle_error_mock.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "valid_index",
                "scenario": "valid_index",
                "expected_result": 3,
                "should_call_handle_error": False,
            },
            {
                "id": "glib_error",
                "scenario": "glib_error",
                "expected_result": -1,
                "should_call_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_index_in_parent(self, test_context, case: dict) -> None:
        """Test AXObject.get_index_in_parent with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "valid_index":
            test_context.patch_object(Atspi.Accessible, "get_index_in_parent", return_value=3)
        elif case["scenario"] == "glib_error":

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test index error")

            test_context.patch_object(
                Atspi.Accessible, "get_index_in_parent", side_effect=raise_glib_error
            )

        result = AXObject.get_index_in_parent(mock_accessible)
        assert result == case["expected_result"]

        if case["should_call_handle_error"]:
            handle_error_mock.assert_called_once()
        else:
            handle_error_mock.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "valid_parent", "scenario": "valid_parent", "should_call_handle_error": False},
            {"id": "glib_error", "scenario": "glib_error", "should_call_handle_error": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_parent(self, test_context, case: dict) -> None:
        """Test AXObject.get_parent with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "valid_parent":
            mock_parent = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(
                Atspi.Accessible, "get_parent", return_value=mock_parent
            )
            result = AXObject.get_parent(mock_accessible)
            assert result == mock_parent
        elif case["scenario"] == "glib_error":

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test parent error")

            test_context.patch_object(Atspi.Accessible, "get_parent", side_effect=raise_glib_error)
            result = AXObject.get_parent(mock_accessible)
            assert result is None

        if case["should_call_handle_error"]:
            handle_error_mock.assert_called_once()
        else:
            handle_error_mock.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "valid_object",
                "scenario": "valid_object",
                "expected_result": Atspi.Role.BUTTON,
                "should_call_handle_error": False,
                "should_call_set_known_dead": True,
            },
            {
                "id": "invalid_object",
                "scenario": "invalid_object",
                "expected_result": Atspi.Role.INVALID,
                "should_call_handle_error": False,
                "should_call_set_known_dead": False,
            },
            {
                "id": "glib_error",
                "scenario": "glib_error",
                "expected_result": Atspi.Role.INVALID,
                "should_call_handle_error": True,
                "should_call_set_known_dead": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_role(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXObject.get_role with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        set_known_dead_status_mock = test_context.Mock()
        test_context.patch_object(
            AXObject, "_set_known_dead_status", new=set_known_dead_status_mock
        )

        if case["scenario"] == "valid_object":
            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(
                Atspi.Accessible, "get_role", return_value=Atspi.Role.BUTTON
            )
        elif case["scenario"] == "invalid_object":
            test_context.patch_object(AXObject, "is_valid", return_value=False)
        elif case["scenario"] == "glib_error":

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test role error")

            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(Atspi.Accessible, "get_role", side_effect=raise_glib_error)

        result = AXObject.get_role(mock_accessible)
        assert result == case["expected_result"]

        if case["should_call_handle_error"]:
            handle_error_mock.assert_called_once()
        else:
            handle_error_mock.assert_not_called()

        if case["should_call_set_known_dead"]:
            set_known_dead_status_mock.assert_called_once_with(mock_accessible, False)
        else:
            set_known_dead_status_mock.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "valid_not_localized",
                "scenario": "valid_not_localized",
                "localized": False,
                "expected_result": "button",
                "should_call_handle_error": False,
            },
            {
                "id": "valid_localized",
                "scenario": "valid_localized",
                "localized": True,
                "expected_result": "botón",
                "should_call_handle_error": False,
            },
            {
                "id": "invalid_object",
                "scenario": "invalid_object",
                "localized": None,
                "expected_result": "",
                "should_call_handle_error": False,
            },
            {
                "id": "glib_error",
                "scenario": "glib_error",
                "localized": None,
                "expected_result": "",
                "should_call_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_role_name(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXObject.get_role_name with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        result = ""

        if case["scenario"] == "valid_not_localized":
            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(
                Atspi.Accessible, "get_role_name", return_value="button"
            )
            result = AXObject.get_role_name(mock_accessible, localized=False)
        elif case["scenario"] == "valid_localized":
            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(
                Atspi.Accessible, "get_localized_role_name", return_value="botón"
            )
            result = AXObject.get_role_name(mock_accessible, localized=True)
        elif case["scenario"] == "invalid_object":
            test_context.patch_object(AXObject, "is_valid", return_value=False)
            result = AXObject.get_role_name(mock_accessible, localized=case["localized"])
        elif case["scenario"] == "glib_error":

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test role name error")

            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(
                Atspi.Accessible, "get_role_name", side_effect=raise_glib_error
            )
            result = AXObject.get_role_name(mock_accessible, localized=case["localized"])

        assert result == case["expected_result"]

        if case["should_call_handle_error"]:
            handle_error_mock.assert_called_once()
        else:
            handle_error_mock.assert_not_called()

    def test_get_role_description_with_invalid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_role_description with invalid object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.get_role_description(mock_accessible)
        assert result == ""

    def test_get_role_description_with_role_description(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXObject.get_role_description with role description attribute."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "get_attributes_dict", return_value={"roledescription": "custom button"}
        )
        result = AXObject.get_role_description(mock_accessible)
        assert result == "custom button"

    def test_get_role_description_with_braille_description(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXObject.get_role_description with braille role description."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject,
            "get_attributes_dict",
            return_value={"roledescription": "custom button", "brailleroledescription": "btn"},
        )
        result = AXObject.get_role_description(mock_accessible, is_braille=True)
        assert result == "btn"

    def test_get_role_description_braille_fallback(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_role_description braille falls back to regular description."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "get_attributes_dict", return_value={"roledescription": "custom button"}
        )
        result = AXObject.get_role_description(mock_accessible, is_braille=True)
        assert result == "custom button"

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "scenario": "invalid_object",
                "expected_result": "",
                "should_call_handle_error": False,
            },
            {
                "id": "valid_object",
                "scenario": "valid_object",
                "expected_result": "button-123",
                "should_call_handle_error": False,
            },
            {
                "id": "glib_error",
                "scenario": "glib_error",
                "expected_result": "",
                "should_call_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_accessible_id(self, test_context, case: dict) -> None:
        """Test AXObject.get_accessible_id with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "invalid_object":
            test_context.patch_object(AXObject, "is_valid", return_value=False)
        elif case["scenario"] == "valid_object":
            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(
                Atspi.Accessible, "get_accessible_id", return_value="button-123"
            )
        elif case["scenario"] == "glib_error":

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test accessible id error")

            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(
                Atspi.Accessible, "get_accessible_id", side_effect=raise_glib_error
            )

        result = AXObject.get_accessible_id(mock_accessible)
        assert result == case["expected_result"]

        if case["should_call_handle_error"]:
            handle_error_mock.assert_called_once()
        else:
            handle_error_mock.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "scenario": "invalid_object",
                "expected_result": "",
                "should_call_handle_error": False,
            },
            {
                "id": "valid_object",
                "scenario": "valid_object",
                "expected_result": "Submit",
                "should_call_handle_error": False,
            },
            {
                "id": "glib_error",
                "scenario": "glib_error",
                "expected_result": "",
                "should_call_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_name(self, test_context, case: dict) -> None:
        """Test AXObject.get_name with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "invalid_object":
            test_context.patch_object(AXObject, "is_valid", return_value=False)
        elif case["scenario"] == "valid_object":
            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(Atspi.Accessible, "get_name", return_value="Submit")
        elif case["scenario"] == "glib_error":

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test name error")

            test_context.patch_object(AXObject, "is_valid", return_value=True)
            test_context.patch_object(Atspi.Accessible, "get_name", side_effect=raise_glib_error)

        result = AXObject.get_name(mock_accessible)
        assert result == case["expected_result"]

        if case["should_call_handle_error"]:
            handle_error_mock.assert_called_once()
        else:
            handle_error_mock.assert_not_called()

    def test_has_same_non_empty_name_both_empty(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.has_same_non_empty_name with both objects having empty names."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_obj1 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "get_name", return_value="")
        result = AXObject.has_same_non_empty_name(mock_obj1, mock_obj2)
        assert result is False

    def test_has_same_non_empty_name_same_non_empty(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.has_same_non_empty_name with same non-empty names."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_obj1 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "get_name", return_value="Submit")
        result = AXObject.has_same_non_empty_name(mock_obj1, mock_obj2)
        assert result is True

    def test_has_same_non_empty_name_different_names(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.has_same_non_empty_name with different names."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_obj1 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)

        def mock_get_name(obj) -> str:
            if obj == mock_obj1:
                return "Submit"
            return "Cancel"

        test_context.patch_object(AXObject, "get_name", new=mock_get_name)
        result = AXObject.has_same_non_empty_name(mock_obj1, mock_obj2)
        assert result is False

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "invalid_object", "is_valid": False, "raises_glib_error": False},
            {"id": "valid_object", "is_valid": True, "raises_glib_error": False},
            {"id": "glib_error", "is_valid": True, "raises_glib_error": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_state_set(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.get_state_set with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", side_effect=lambda obj: case["is_valid"])

        if case["is_valid"] and not case["raises_glib_error"]:
            mock_state_set = test_context.Mock()
            test_context.patch_object(
                Atspi.Accessible, "get_state_set", return_value=mock_state_set
            )
            set_known_dead_status_mock = test_context.Mock()
            test_context.patch_object(
                AXObject, "_set_known_dead_status", new=set_known_dead_status_mock
            )

            result = AXObject.get_state_set(mock_accessible)
            assert result == mock_state_set
            set_known_dead_status_mock.assert_called_once_with(mock_accessible, False)
        elif case["raises_glib_error"]:

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test state set error")

            test_context.patch_object(
                Atspi.Accessible, "get_state_set", side_effect=raise_glib_error
            )
            handle_error_mock = test_context.Mock()
            test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

            result = AXObject.get_state_set(mock_accessible)
            assert isinstance(result, type(Atspi.StateSet()))
            handle_error_mock.assert_called_once()
        else:
            result = AXObject.get_state_set(mock_accessible)
            assert isinstance(result, type(Atspi.StateSet()))

    def test_has_state_with_invalid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.has_state with invalid object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.has_state(mock_accessible, Atspi.StateType.FOCUSED)
        assert result is False

    def test_has_state_with_valid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.has_state with valid object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_state_set = test_context.Mock()
        mock_state_set.contains.return_value = True
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_state_set", return_value=mock_state_set)
        result = AXObject.has_state(mock_accessible, Atspi.StateType.FOCUSED)
        assert result is True
        mock_state_set.contains.assert_called_once_with(Atspi.StateType.FOCUSED)

    def test_clear_cache_with_none_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.clear_cache with None object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        AXObject.clear_cache(None)

    def test_clear_cache_non_recursive(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.clear_cache non-recursive."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            Atspi.Accessible, "clear_cache_single", new=test_context.Mock()
        )
        AXObject.clear_cache(mock_accessible, recursive=False, reason="test")
        sys.modules["gi.repository"].Atspi.Accessible.clear_cache_single.assert_called_once_with(
            mock_accessible
        )
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_clear_cache_non_recursive_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.clear_cache non-recursive handles GLib.GError."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        def raise_glib_error(_obj) -> None:
            raise GLib.GError("Test clear cache error")

        test_context.patch_object(
            Atspi.Accessible, "clear_cache_single", side_effect=raise_glib_error
        )
        AXObject.clear_cache(mock_accessible, recursive=False)
        essential_modules["orca.debug"].print_message.assert_called()

    def test_clear_cache_recursive(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.clear_cache recursive."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_clear_cache = test_context.patch("gi.repository.Atspi.Accessible.clear_cache")
        AXObject.clear_cache(mock_accessible, recursive=True)
        mock_clear_cache.assert_called_once_with(mock_accessible)

    def test_clear_cache_recursive_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.clear_cache recursive handles GLib.GError."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        def raise_glib_error(_obj) -> None:
            raise GLib.GError("Test clear cache recursive error")

        test_context.patch_object(Atspi.Accessible, "clear_cache", side_effect=raise_glib_error)
        AXObject.clear_cache(mock_accessible, recursive=True)
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "is_valid": False,
                "use_cache": True,
                "cached_attrs": None,
                "get_attributes_result": None,
                "raises_error": False,
                "expected_result": {},
                "expects_cache_update": False,
                "expects_handle_error": False,
            },
            {
                "id": "cache_hit",
                "is_valid": True,
                "use_cache": True,
                "cached_attrs": {"id": "button1", "class": "primary"},
                "get_attributes_result": None,
                "raises_error": False,
                "expected_result": {"id": "button1", "class": "primary"},
                "expects_cache_update": False,
                "expects_handle_error": False,
            },
            {
                "id": "no_cache_valid_attributes",
                "is_valid": True,
                "use_cache": False,
                "cached_attrs": None,
                "get_attributes_result": {"id": "button2", "class": "secondary"},
                "raises_error": False,
                "expected_result": {"id": "button2", "class": "secondary"},
                "expects_cache_update": True,
                "expects_handle_error": False,
            },
            {
                "id": "glib_error",
                "is_valid": True,
                "use_cache": False,
                "cached_attrs": None,
                "get_attributes_result": None,
                "raises_error": True,
                "expected_result": {},
                "expects_cache_update": False,
                "expects_handle_error": True,
            },
            {
                "id": "none_attributes",
                "is_valid": True,
                "use_cache": False,
                "cached_attrs": None,
                "get_attributes_result": None,
                "raises_error": False,
                "expected_result": {},
                "expects_cache_update": False,
                "expects_handle_error": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_attributes_dict_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.get_attributes_dict with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", side_effect=lambda obj: case["is_valid"])

        if case["cached_attrs"]:
            AXObject.OBJECT_ATTRIBUTES[hash(mock_accessible)] = case["cached_attrs"]
        else:
            AXObject.OBJECT_ATTRIBUTES.clear()

        if case["raises_error"]:

            def raise_glib_error(_obj) -> None:
                raise GLib.GError("Test attributes error")

            test_context.patch_object(
                Atspi.Accessible, "get_attributes", side_effect=raise_glib_error
            )
            handle_error_mock = test_context.Mock()
            test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        elif case["get_attributes_result"] is not None:
            test_context.patch_object(
                Atspi.Accessible, "get_attributes", return_value=case["get_attributes_result"]
            )
        else:
            test_context.patch_object(Atspi.Accessible, "get_attributes", return_value=None)

        result = AXObject.get_attributes_dict(mock_accessible, use_cache=case["use_cache"])
        assert result == case["expected_result"]

        if case["expects_cache_update"] and case["get_attributes_result"]:
            assert (
                AXObject.OBJECT_ATTRIBUTES[hash(mock_accessible)] == case["get_attributes_result"]
            )

        if case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "is_valid": False,
                "attributes_dict": {},
                "attribute_name": "id",
                "expected_result": "",
            },
            {
                "id": "existing_attribute",
                "is_valid": True,
                "attributes_dict": {"id": "button1", "class": "primary"},
                "attribute_name": "id",
                "expected_result": "button1",
            },
            {
                "id": "missing_attribute",
                "is_valid": True,
                "attributes_dict": {"id": "button1"},
                "attribute_name": "class",
                "expected_result": "",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_attribute_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.get_attribute with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", side_effect=lambda obj: case["is_valid"])
        test_context.patch_object(
            AXObject,
            "get_attributes_dict",
            side_effect=lambda obj, use_cache: case["attributes_dict"],
        )
        result = AXObject.get_attribute(mock_accessible, case["attribute_name"])
        assert result == case["expected_result"]

    def test_get_n_actions_with_unsupported_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_n_actions with object that doesn't support actions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_action", return_value=False)
        result = AXObject.get_n_actions(mock_accessible)
        assert result == 0

    def test_get_n_actions_with_supported_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_n_actions with object that supports actions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_action", return_value=True)
        test_context.patch_object(Atspi.Action, "get_n_actions", return_value=3)
        result = AXObject.get_n_actions(mock_accessible)
        assert result == 3

    def test_get_n_actions_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_n_actions handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        def raise_glib_error(_obj) -> None:
            raise GLib.GError("Test n actions error")

        test_context.patch_object(AXObject, "supports_action", return_value=True)
        test_context.patch_object(Atspi.Action, "get_n_actions", side_effect=raise_glib_error)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        result = AXObject.get_n_actions(mock_accessible)
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
        """Test AXObject._normalize_action_name with various inputs."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        result = AXObject._normalize_action_name(case["action_name"])
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
        """Test AXObject.get_action_name with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "get_n_actions", side_effect=lambda obj: case["n_actions"]
        )
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "valid":
            test_context.patch_object(
                Atspi.Action, "get_action_name", return_value=case["atspi_result"]
            )
            test_context.patch_object(
                AXObject, "_normalize_action_name", return_value=case["normalize_result"]
            )
        elif case["scenario"] == "glib_error":
            test_context.patch_object(
                Atspi.Action,
                "get_action_name",
                side_effect=GLib.GError("Test error"),
            )

        result = AXObject.get_action_name(mock_accessible, case["test_index"])
        assert result == case["expected_result"]
        if case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    def test_get_action_names_no_actions(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_action_names with no actions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "get_n_actions", return_value=0)
        result = AXObject.get_action_names(mock_accessible)
        assert not result

    def test_get_action_names_with_actions(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_action_names with multiple actions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "get_n_actions", return_value=3)

        def mock_get_action_name(_obj, i) -> str:
            names = ["click", "", "press"]
            return names[i]

        test_context.patch_object(AXObject, "get_action_name", new=mock_get_action_name)
        result = AXObject.get_action_names(mock_accessible)
        assert result == ["click", "press"]

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
        """Test AXObject.get_action_description with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "get_n_actions", side_effect=lambda obj: case["n_actions"]
        )
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] == "valid":
            test_context.patch_object(
                Atspi.Action, "get_action_description", return_value=case["atspi_result"]
            )
        elif case["scenario"] == "glib_error":
            test_context.patch_object(
                Atspi.Action,
                "get_action_description",
                side_effect=GLib.GError("Test error"),
            )

        result = AXObject.get_action_description(mock_accessible, case["test_index"])
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
        """Test AXObject.get_action_key_binding with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "get_n_actions", side_effect=lambda obj: case["n_actions"]
        )
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        if case["scenario"] in ["valid", "void_symbol"]:
            test_context.patch_object(
                Atspi.Action, "get_key_binding", return_value=case["atspi_result"]
            )
        elif case["scenario"] == "glib_error":
            test_context.patch_object(
                Atspi.Action,
                "get_key_binding",
                side_effect=GLib.GError("Test error"),
            )

        result = AXObject.get_action_key_binding(mock_accessible, case["test_index"])
        assert result == case["expected_result"]
        if case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    def test_get_label_for_key_sequence_simple(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._get_label_for_key_sequence with empty string."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        result = AXObject._get_label_for_key_sequence("")
        assert result == ""

    def test_get_accelerator_with_invalid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_accelerator with invalid object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.get_accelerator(mock_accessible)
        assert result == ""

    def test_get_accelerator_invalid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_accelerator with invalid object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.get_accelerator(mock_accessible)
        assert result == ""

    def test_get_mnemonic_no_attributes(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_mnemonic with no keyshortcuts attribute."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXObject, "_find_first_action_with_keybinding", return_value=-1
        )
        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_single_letter_shortcut(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_mnemonic with single letter keyshortcut."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "get_attributes_dict", return_value={"keyshortcuts": "F"}
        )
        test_context.patch_object(AXObject, "_get_label_for_key_sequence", return_value="F")
        result = AXObject.get_mnemonic(mock_accessible)
        assert result == "F"

    def test_get_mnemonic_multiple_letter_shortcut(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_mnemonic with multi-letter keyshortcut."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "get_attributes_dict", return_value={"keyshortcuts": "Ctrl+F"}
        )
        test_context.patch_object(
            AXObject, "_get_label_for_key_sequence", return_value="Ctrl+F"
        )
        test_context.patch_object(
            AXObject, "_find_first_action_with_keybinding", return_value=-1
        )
        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_from_action_keybinding(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_mnemonic from action key binding."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXObject, "_find_first_action_with_keybinding", return_value=0
        )
        test_context.patch_object(
            AXObject, "get_action_key_binding", return_value="Alt+F;Alt+F"
        )
        test_context.patch_object(
            AXObject, "_get_label_for_key_sequence", return_value="Alt+F"
        )
        result = AXObject.get_mnemonic(mock_accessible)
        assert result == "Alt+F"

    def test_get_mnemonic_with_ctrl_in_result(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_mnemonic with Ctrl in result."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXObject, "_find_first_action_with_keybinding", return_value=0
        )
        test_context.patch_object(
            AXObject, "get_action_key_binding", return_value="Ctrl+F;Ctrl+F"
        )
        test_context.patch_object(
            AXObject, "_get_label_for_key_sequence", return_value="Ctrl+F"
        )
        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_with_space(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_mnemonic with space key."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXObject, "_find_first_action_with_keybinding", return_value=0
        )
        test_context.patch_object(
            AXObject, "get_action_key_binding", return_value="space;space"
        )
        test_context.patch_object(
            AXObject, "_get_label_for_key_sequence", return_value="space"
        )
        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_find_first_action_with_keybinding_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_first_action_with_keybinding found action."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_n_actions", return_value=2)

        def mock_get_action_key_binding(_obj, index) -> str:
            if index == 0:
                return ""
            return "Alt+F"

        test_context.patch_object(
            AXObject, "get_action_key_binding", new=mock_get_action_key_binding
        )
        result = AXObject._find_first_action_with_keybinding(mock_accessible)
        assert result == 1

    def test_find_first_action_with_keybinding_not_found(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXObject._find_first_action_with_keybinding not found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_n_actions", return_value=2)
        test_context.patch_object(AXObject, "get_action_key_binding", return_value="")
        result = AXObject._find_first_action_with_keybinding(mock_accessible)
        assert result == -1

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "valid_action", "action_index": 0, "expected": True},
            {"id": "invalid_action", "action_index": -1, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_has_action(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXObject.has_action with various action index values."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "get_action_index", side_effect=lambda obj, name: case["action_index"]
        )
        result = AXObject.has_action(mock_accessible, "click")
        assert result is case["expected"]

    def test_get_action_index_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_action_index found action."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "_normalize_action_name", side_effect=lambda name: name.lower()
        )
        test_context.patch_object(AXObject, "get_n_actions", return_value=2)

        def mock_get_action_name(_obj, index) -> str:
            if index == 0:
                return "press"
            return "click"

        test_context.patch_object(AXObject, "get_action_name", new=mock_get_action_name)
        result = AXObject.get_action_index(mock_accessible, "click")
        assert result == 1

    def test_get_action_index_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_action_index not found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "_normalize_action_name", side_effect=lambda name: name.lower()
        )
        test_context.patch_object(AXObject, "get_n_actions", return_value=2)
        test_context.patch_object(AXObject, "get_action_name", return_value="press")
        result = AXObject.get_action_index(mock_accessible, "click")
        assert result == -1

    def test_do_action_success(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.do_action success."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_n_actions", return_value=2)
        sys.modules["gi.repository"].Atspi.Action.do_action = test_context.Mock(return_value=True)
        result = AXObject.do_action(mock_accessible, 0)
        assert result is True

    def test_do_action_invalid_index(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.do_action invalid index."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_n_actions", return_value=2)
        result = AXObject.do_action(mock_accessible, 5)
        assert result is False

    def test_do_action_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.do_action handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_n_actions", return_value=2)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        sys.modules["gi.repository"].Atspi.Action.do_action = test_context.Mock(
            side_effect=sys.modules["gi.repository"].GLib.GError("Test error")
        )
        result = AXObject.do_action(mock_accessible, 0)
        assert result is False

    def test_do_named_action_success(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.do_named_action success."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_action_index", return_value=0)
        test_context.patch_object(AXObject, "do_action", return_value=True)
        result = AXObject.do_named_action(mock_accessible, "click")
        assert result is True

    def test_do_named_action_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.do_named_action action not found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_action_index", return_value=-1)
        debug_mock = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        sys.modules["orca.debug"] = debug_mock
        result = AXObject.do_named_action(mock_accessible, "click")
        assert result is False

    def test_grab_focus_no_component_support(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.grab_focus without component support."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "supports_component", return_value=False)
        result = AXObject.grab_focus(mock_accessible)
        assert result is False

    def test_grab_focus_basic_success(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.grab_focus basic success path."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "supports_component", return_value=True)
        test_context.patch_object(AXObject, "has_state", return_value=False)

        def mock_grab_focus(_obj) -> bool:
            from orca import debug

            debug.LEVEL_INFO = 800
            debug.debugLevel = 2
            return True

        test_context.patch(
            "orca.ax_object.Atspi.Component.grab_focus", new=mock_grab_focus
        )
        result = AXObject.grab_focus(mock_accessible)
        assert result is True

    def test_is_ancestor_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.is_ancestor with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "is_valid", side_effect=lambda obj: obj == mock_accessible
        )
        result = AXObject.is_ancestor(None, mock_accessible)
        assert result is False

    def test_is_ancestor_invalid_ancestor(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.is_ancestor with invalid ancestor."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "is_valid", side_effect=lambda obj: obj == mock_accessible
        )
        result = AXObject.is_ancestor(mock_accessible, None)
        assert result is False

    def test_is_ancestor_same_object_inclusive(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.is_ancestor with same object and inclusive=True."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        result = AXObject.is_ancestor(mock_accessible, mock_accessible, inclusive=True)
        assert result is True

    def test_is_ancestor_same_object_not_inclusive(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.is_ancestor with same object and inclusive=False."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "find_ancestor", return_value=None)
        result = AXObject.is_ancestor(mock_accessible, mock_accessible, inclusive=False)
        assert result is False

    def test_is_ancestor_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.is_ancestor when ancestor is found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "find_ancestor", return_value=mock_ancestor)
        result = AXObject.is_ancestor(mock_accessible, mock_ancestor)
        assert result is True

    def test_is_ancestor_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.is_ancestor when ancestor is not found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "find_ancestor", return_value=None)
        result = AXObject.is_ancestor(mock_accessible, mock_ancestor)
        assert result is False

    def test_get_child_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_child with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.get_child(mock_accessible, 0)
        assert result is None

    def test_get_child_no_children(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_child with no children."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=0)
        result = AXObject.get_child(mock_accessible, 0)
        assert result is None

    def test_get_child_negative_index(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_child with -1 index (last child)."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=3)

        def mock_get_child_at_index(_obj, index) -> object:
            if index == 2:
                return mock_child
            return None

        sys.modules["gi.repository"].Atspi.Accessible.get_child_at_index = mock_get_child_at_index
        result = AXObject.get_child(mock_accessible, -1)
        assert result == mock_child

    def test_get_child_valid_index(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_child with valid index."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=3)
        sys.modules["gi.repository"].Atspi.Accessible.get_child_at_index = (
            lambda obj, idx: mock_child if idx == 1 else None
        )
        result = AXObject.get_child(mock_accessible, 1)
        assert result == mock_child

    def test_find_descendant_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_descendant with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)

        def always_true(_obj) -> bool:
            return True

        result = AXObject._find_descendant(mock_accessible, always_true)
        assert result is None

    def test_find_descendant_no_children(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_descendant with no children."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=0)

        def always_true(_obj) -> bool:
            return True

        result = AXObject._find_descendant(mock_accessible, always_true)
        assert result is None

    def test_find_descendant_found_direct_child(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_descendant with direct child match."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=1)
        test_context.patch_object(AXObject, "get_child_checked", return_value=mock_child)

        def match_child(obj) -> bool:
            return obj == mock_child

        result = AXObject._find_descendant(mock_accessible, match_child)
        assert result == mock_child

    def test_find_descendant_found_in_grandchild(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_descendant with grandchild match."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        mock_grandchild = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 1
            if obj == mock_child:
                return 1
            return 0

        def mock_get_child_checked(obj, idx) -> object:
            if obj == mock_accessible and idx == 0:
                return mock_child
            if obj == mock_child and idx == 0:
                return mock_grandchild
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child_checked", new=mock_get_child_checked)

        def match_grandchild(obj) -> bool:
            return obj == mock_grandchild

        result = AXObject._find_descendant(mock_accessible, match_grandchild)
        assert result == mock_grandchild

    def test_find_descendant_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_descendant when predicate never matches."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=0)

        def never_match(_obj) -> bool:
            return False

        result = AXObject._find_descendant(mock_accessible, never_match)
        assert result is None

    def test_find_descendant_with_timing(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_descendant includes timing."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "_find_descendant", return_value=mock_child)
        debug_mock = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        sys.modules["orca.debug"] = debug_mock

        def always_true(_obj) -> bool:
            return True

        result = AXObject.find_descendant(mock_accessible, always_true)
        assert result == mock_child

    def test_find_deepest_descendant_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_deepest_descendant with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.find_deepest_descendant(mock_accessible)
        assert result is None

    def test_find_deepest_descendant_no_children(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_deepest_descendant with no children."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=0)
        test_context.patch_object(AXObject, "get_child", return_value=None)
        result = AXObject.find_deepest_descendant(mock_accessible)
        assert result == mock_accessible

    def test_find_deepest_descendant_with_children(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_deepest_descendant with nested children."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        mock_grandchild = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 2
            if obj == mock_child:
                return 1
            return 0

        def mock_get_child(obj, index) -> object:
            if obj == mock_accessible and index == 1:
                return mock_child
            if obj == mock_child and index == 0:
                return mock_grandchild
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child", new=mock_get_child)
        result = AXObject.find_deepest_descendant(mock_accessible)
        assert result == mock_grandchild

    def test_find_all_descendants_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_all_descendants with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        matches: list[Atspi.Accessible] = []
        AXObject._find_all_descendants(mock_accessible, None, None, matches)
        assert not matches

    def test_find_all_descendants_with_include_filter(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_all_descendants with include filter."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child1 = test_context.Mock(spec=Atspi.Accessible)
        mock_child2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 2
            return 0

        def mock_get_child(obj, idx) -> object:
            if obj == mock_accessible:
                if idx == 0:
                    return mock_child1
                if idx == 1:
                    return mock_child2
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child", new=mock_get_child)

        def include_child1(obj) -> bool:
            return obj == mock_child1

        matches: list[Atspi.Accessible] = []
        AXObject._find_all_descendants(mock_accessible, include_child1, None, matches)
        assert matches == [mock_child1]

    def test_find_all_descendants_with_exclude_filter(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._find_all_descendants with exclude filter."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child1 = test_context.Mock(spec=Atspi.Accessible)
        mock_child2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 2
            return 0

        def mock_get_child(obj, idx) -> object:
            if obj == mock_accessible:
                if idx == 0:
                    return mock_child1
                if idx == 1:
                    return mock_child2
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child", new=mock_get_child)

        def include_all(_obj) -> bool:
            return True

        def exclude_child1(obj) -> bool:
            return obj == mock_child1

        matches: list[Atspi.Accessible] = []
        AXObject._find_all_descendants(mock_accessible, include_all, exclude_child1, matches)
        assert matches == [mock_child2]

    def test_find_all_descendants_public_method(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_all_descendants public method."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject,
            "_find_all_descendants",
            side_effect=lambda root, incl, excl, matches: matches.append(mock_child),
        )
        debug_mock = test_context.Mock()
        debug_mock.print_message = test_context.Mock()
        sys.modules["orca.debug"] = debug_mock
        result = AXObject.find_all_descendants(mock_accessible)
        assert result == [mock_child]

    def test_get_role_name_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_role_name with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.get_role_name(mock_accessible)
        assert result == ""

    def test_get_role_name_non_localized(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_role_name non-localized."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        sys.modules["gi.repository"].Atspi.Accessible.get_role_name = test_context.Mock(
            return_value="button"
        )
        result = AXObject.get_role_name(mock_accessible, localized=False)
        assert result == "button"
        sys.modules["gi.repository"].Atspi.Accessible.get_localized_role_name = test_context.Mock(
            return_value="botón"
        )
        result = AXObject.get_role_name(mock_accessible, localized=True)
        assert result == "botón"

    def test_get_role_name_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_role_name handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
        sys.modules["gi.repository"].Atspi.Accessible.get_role_name = test_context.Mock(
            side_effect=GLib.GError("Test error")
        )
        result = AXObject.get_role_name(mock_accessible)
        assert result == ""

    def test_has_same_non_empty_name_empty_name1(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.has_same_non_empty_name with empty first name."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)

        def mock_get_name(obj) -> str:
            if obj == mock_accessible:
                return ""
            return "test"

        test_context.patch_object(AXObject, "get_name", new=mock_get_name)
        result = AXObject.has_same_non_empty_name(mock_accessible, mock_obj2)
        assert result is False

    def test_has_same_non_empty_name_same_names(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.has_same_non_empty_name with same names."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "get_name", return_value="test")
        result = AXObject.has_same_non_empty_name(mock_accessible, mock_obj2)
        assert result is True

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "desc_invalid_obj",
                "method_name": "get_description",
                "scenario": "invalid_obj",
                "is_valid": False,
                "atspi_method": "get_description",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "desc_success",
                "method_name": "get_description",
                "scenario": "success",
                "is_valid": True,
                "atspi_method": "get_description",
                "expected_result": "Test description",
                "expects_handle_error": False,
            },
            {
                "id": "desc_glib_error",
                "method_name": "get_description",
                "scenario": "glib_error",
                "is_valid": True,
                "atspi_method": "get_description",
                "expected_result": "",
                "expects_handle_error": True,
            },
            {
                "id": "child_count_invalid_obj",
                "method_name": "get_child_count",
                "scenario": "invalid_obj",
                "is_valid": False,
                "atspi_method": "get_child_count",
                "expected_result": 0,
                "expects_handle_error": False,
            },
            {
                "id": "child_count_success",
                "method_name": "get_child_count",
                "scenario": "success",
                "is_valid": True,
                "atspi_method": "get_child_count",
                "expected_result": 3,
                "expects_handle_error": False,
            },
            {
                "id": "child_count_glib_error",
                "method_name": "get_child_count",
                "scenario": "glib_error",
                "is_valid": True,
                "atspi_method": "get_child_count",
                "expected_result": 0,
                "expects_handle_error": True,
            },
            {
                "id": "img_desc_invalid_obj",
                "method_name": "get_image_description",
                "scenario": "invalid_obj",
                "is_valid": False,
                "atspi_method": "get_image_description",
                "expected_result": "",
                "expects_handle_error": False,
            },
            {
                "id": "img_desc_success",
                "method_name": "get_image_description",
                "scenario": "success",
                "is_valid": True,
                "atspi_method": "get_image_description",
                "expected_result": "Image description",
                "expects_handle_error": False,
            },
            {
                "id": "img_desc_glib_error",
                "method_name": "get_image_description",
                "scenario": "glib_error",
                "is_valid": True,
                "atspi_method": "get_image_description",
                "expected_result": "",
                "expects_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_getter_methods_with_error_handling_scenarios(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXObject getter methods with invalid_obj/success/glib_error scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", side_effect=lambda obj: case["is_valid"])

        if case["method_name"] == "get_image_description":
            if case["scenario"] == "invalid_obj":
                test_context.patch_object(AXObject, "supports_image", return_value=False)
            else:
                test_context.patch_object(AXObject, "supports_image", return_value=True)

        if case["scenario"] == "glib_error":
            handle_error_mock = test_context.Mock()
            test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)
            glib_error = GLib.GError("Test error")
            if case["method_name"] == "get_image_description":
                sys.modules["gi.repository"].Atspi.Image.get_image_description = test_context.Mock(
                    side_effect=glib_error
                )
            else:
                setattr(
                    sys.modules["gi.repository"].Atspi.Accessible,
                    case["atspi_method"],
                    test_context.Mock(side_effect=glib_error),
                )
        elif case["scenario"] == "success":
            if case["method_name"] == "get_image_description":
                sys.modules["gi.repository"].Atspi.Image.get_image_description = test_context.Mock(
                    return_value=case["expected_result"]
                )
            else:
                setattr(
                    sys.modules["gi.repository"].Atspi.Accessible,
                    case["atspi_method"],
                    test_context.Mock(return_value=case["expected_result"]),
                )

        method_to_test = getattr(AXObject, case["method_name"])
        result = method_to_test(mock_accessible)
        assert result == case["expected_result"]

        if case["scenario"] == "glib_error" and case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "action_invalid_obj",
                "interface_name": "action",
                "getter_method": "get_action_iface",
                "has_error": False,
                "expected_result": False,
                "expects_handle_error": False,
            },
            {
                "id": "component_invalid_obj",
                "interface_name": "component",
                "getter_method": "get_component_iface",
                "has_error": False,
                "expected_result": False,
                "expects_handle_error": False,
            },
            {
                "id": "component_glib_error",
                "interface_name": "component",
                "getter_method": "get_component_iface",
                "has_error": True,
                "expected_result": False,
                "expects_handle_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_supports_interface_error_paths(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.supports_* interface methods error paths."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        handle_error_mock = test_context.Mock()
        test_context.patch_object(AXObject, "handle_error", new=handle_error_mock)

        method = getattr(AXObject, f"supports_{case['interface_name']}")

        if case["has_error"]:
            test_context.patch_object(AXObject, "is_valid", return_value=True)
            setattr(
                sys.modules["gi.repository"].Atspi.Accessible,
                case["getter_method"],
                test_context.Mock(side_effect=GLib.GError("Test error")),
            )
        else:
            test_context.patch_object(AXObject, "is_valid", return_value=False)

        result = method(mock_accessible)
        assert result is case["expected_result"]
        if case["expects_handle_error"]:
            handle_error_mock.assert_called_once()

    def test_has_document_spreadsheet_import_path(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._has_document_spreadsheet import path."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_collection = test_context.Mock()
        mock_ax_collection.AXCollection = test_context.Mock()
        mock_ax_collection.AXCollection.create_match_rule = test_context.Mock(return_value=None)
        sys.modules["orca.ax_collection"] = mock_ax_collection
        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    def test_has_document_spreadsheet_no_frame_path(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._has_document_spreadsheet no frame path."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_collection = test_context.Mock()
        mock_ax_collection.AXCollection = test_context.Mock()
        mock_ax_collection.AXCollection.create_match_rule = test_context.Mock(
            return_value="mock_rule"
        )
        sys.modules["orca.ax_collection"] = mock_ax_collection
        test_context.patch_object(
            AXObject, "find_ancestor_inclusive", return_value=None
        )
        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    def test_has_document_spreadsheet_with_matches_path(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXObject._has_document_spreadsheet with matches path."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_frame = test_context.Mock(spec=Atspi.Accessible)
        mock_ax_collection = test_context.Mock()
        mock_ax_collection.AXCollection = test_context.Mock()
        mock_ax_collection.AXCollection.create_match_rule = test_context.Mock(
            return_value="mock_rule"
        )
        sys.modules["orca.ax_collection"] = mock_ax_collection
        test_context.patch_object(
            AXObject, "find_ancestor_inclusive", return_value=mock_frame
        )
        sys.modules["gi.repository"].Atspi.Collection.get_matches = test_context.Mock(
            return_value=["match1"]
        )
        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is True

    def test_get_common_ancestor_with_none_objects(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_common_ancestor with None objects."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        result = AXObject.get_common_ancestor(None, None)
        assert result is None

    def test_get_common_ancestor_same_objects(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_common_ancestor with same objects."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        result = AXObject.get_common_ancestor(mock_accessible, mock_accessible)
        assert result == mock_accessible

    def test_get_parent_checked_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_parent_checked with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject.get_parent_checked(mock_accessible)
        assert result is None

    def test_get_parent_checked_invalid_role(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.get_parent_checked with invalid role."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.INVALID)
        result = AXObject.get_parent_checked(mock_accessible)
        assert result is None

    def test_find_ancestor_found_grandparent(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_ancestor found in parent."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_parent_checked(obj) -> object:
            if obj == mock_accessible:
                return mock_parent
            return None

        test_context.patch_object(AXObject, "get_parent_checked", new=mock_get_parent_checked)

        def match_parent(obj) -> bool:
            return obj == mock_parent

        result = AXObject.find_ancestor(mock_accessible, match_parent)
        assert result == mock_parent

    def test_find_ancestor_found_in_grandparent(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_ancestor found in grandparent."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_grandparent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_parent_checked(obj) -> object:
            if obj == mock_accessible:
                return mock_parent
            if obj == mock_parent:
                return mock_grandparent
            return None

        test_context.patch_object(AXObject, "get_parent_checked", new=mock_get_parent_checked)

        def match_grandparent(obj) -> bool:
            return obj == mock_grandparent

        result = AXObject.find_ancestor(mock_accessible, match_grandparent)
        assert result == mock_grandparent

    def test_find_ancestor_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_ancestor not found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_parent_checked(obj) -> object:
            if obj == mock_accessible:
                return mock_parent
            return None

        test_context.patch_object(AXObject, "get_parent_checked", new=mock_get_parent_checked)

        def never_match(_obj) -> bool:
            return False

        result = AXObject.find_ancestor(mock_accessible, never_match)
        assert result is None

    def test_find_ancestor_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXObject.find_ancestor with no parent."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_parent_checked", return_value=None)

        def always_true(_obj) -> bool:
            return True

        result = AXObject.find_ancestor(mock_accessible, always_true)
        assert result is None

    def test_has_document_spreadsheet_with_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._has_document_spreadsheet with invalid object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    def test_has_document_spreadsheet_with_valid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._has_document_spreadsheet with valid object."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        mock_spreadsheet = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "find_ancestor_inclusive", return_value=mock_spreadsheet
        )
        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is True

    def test_has_document_spreadsheet_no_spreadsheet(self, test_context: OrcaTestContext) -> None:
        """Test AXObject._has_document_spreadsheet with no spreadsheet."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject, "find_ancestor_inclusive", return_value=None
        )
        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    @pytest.mark.parametrize(
        "interface_type,has_interface,expected",
        [
            ("document", True, True),
            ("document", False, False),
            ("editable_text", True, True),
            ("editable_text", False, False),
            ("hyperlink", True, True),
            ("hyperlink", False, False),
            ("image", True, True),
            ("image", False, False),
            ("selection", True, True),
            ("selection", False, False),
            ("table", True, True),
            ("table", False, False),
        ],
    )
    def test_supports_interface(
        self,
        test_context: OrcaTestContext,
        interface_type: str,
        has_interface: bool,
        expected: bool,
    ) -> None:
        """Test AXObject.supports_* interface methods with various interface types."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        interface_map = {
            "document": (
                "get_document_iface",
                AXObject.supports_document,
            ),
            "editable_text": (
                "get_editable_text_iface",
                AXObject.supports_editable_text,
            ),
            "hyperlink": (
                "get_hyperlink",
                AXObject.supports_hyperlink,
            ),
            "image": (
                "get_image_iface",
                AXObject.supports_image,
            ),
            "selection": (
                "get_selection_iface",
                AXObject.supports_selection,
            ),
            "table": (
                "get_table_iface",
                AXObject.supports_table,
            ),
        }

        getter_method, test_method = interface_map[interface_type]
        mock_iface = test_context.Mock() if has_interface else None
        setattr(
            sys.modules["gi.repository"].Atspi.Accessible,
            getter_method,
            test_context.Mock(return_value=mock_iface),
        )

        result = test_method(mock_accessible)
        assert result is expected

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "simple_sequence", "key_sequence": "Ctrl+c", "expected_output": "Ctrl+c"},
            {
                "id": "multiple_modifiers",
                "key_sequence": "Ctrl+Shift+s",
                "expected_output": "Ctrl+Shift+s",
            },
            {
                "id": "lowercase_modifiers",
                "key_sequence": "ctrl+alt+del",
                "expected_output": "ctrl+alt+del",
            },
            {"id": "primary_conversion", "key_sequence": "Primary+a", "expected_output": "Ctrl+A"},
            {
                "id": "primary_with_shift",
                "key_sequence": "Primary+Shift+z",
                "expected_output": "Ctrl+Shift+Z",
            },
            {
                "id": "angle_bracket_format",
                "key_sequence": "<Control><Shift>s",
                "expected_output": "Ctrl+Shift+S",
            },
            {"id": "single_character", "key_sequence": "a", "expected_output": "A"},
            {"id": "function_key", "key_sequence": "F1", "expected_output": "F1"},
            {"id": "empty_sequence", "key_sequence": "", "expected_output": ""},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_label_for_key_sequence_various_formats(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXObject._get_label_for_key_sequence with various key sequence formats."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        gtk_mock = test_context.Mock()
        gtk_mock.accelerator_parse.return_value = (65, 4)  # 'A' key with Ctrl modifier
        gtk_mock.accelerator_get_label.return_value = case["expected_output"]

        keynames_mock = essential_modules["orca.keynames"]
        keynames_mock.localize_key_sequence.return_value = case["expected_output"]

        test_context.patch("orca.ax_object.Gtk", new=gtk_mock)

        result = AXObject._get_label_for_key_sequence(case["key_sequence"])
        assert result == case["expected_output"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_sequence",
                "key_sequence": "invalid<>sequence",
                "gtk_error": True,
                "expected_fallback": "invalid sequence",
            },
            {
                "id": "broken_brackets",
                "key_sequence": "<Broken>key",
                "gtk_error": True,
                "expected_fallback": "Broken key",
            },
            {
                "id": "malformed_brackets",
                "key_sequence": "<<malformed",
                "gtk_error": True,
                "expected_fallback": "malformed",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_label_for_key_sequence_error_handling(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject._get_label_for_key_sequence error handling."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        gtk_mock = test_context.Mock()
        if case["gtk_error"]:
            gtk_mock.accelerator_parse.side_effect = GLib.GError("Invalid accelerator")

        keynames_mock = essential_modules["orca.keynames"]
        keynames_mock.localize_key_sequence.return_value = case["expected_fallback"]

        test_context.patch("orca.ax_object.Gtk", new=gtk_mock)

        result = AXObject._get_label_for_key_sequence(case["key_sequence"])
        assert result == case["expected_fallback"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "single_shortcut",
                "shortcut_string": "Ctrl+s",
                "expected_shortcuts": ["Ctrl+s"],
            },
            {
                "id": "multiple_shortcuts",
                "shortcut_string": "Ctrl+c Ctrl+v",
                "expected_shortcuts": ["Ctrl+c", "Ctrl+v"],
            },
            {"id": "empty_shortcuts", "shortcut_string": "", "expected_shortcuts": [""]},
            {
                "id": "function_keys",
                "shortcut_string": "F1 F2 F3",
                "expected_shortcuts": ["F1", "F2", "F3"],
            },
            {
                "id": "complex_shortcuts",
                "shortcut_string": "Alt+Tab Ctrl+Shift+Esc",
                "expected_shortcuts": ["Alt+Tab", "Ctrl+Shift+Esc"],
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_accelerator_shortcut_parsing(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXObject.get_accelerator shortcut parsing logic."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        attributes = {"keyshortcuts": case["shortcut_string"]} if case["shortcut_string"] else {}
        test_context.patch_object(AXObject, "get_attributes_dict", return_value=attributes)

        test_context.patch_object(
            AXObject, "_get_label_for_key_sequence", side_effect=lambda seq: seq
        )

        test_context.patch_object(
            AXObject, "_find_first_action_with_keybinding", return_value=-1
        )

        result = AXObject.get_accelerator(mock_accessible)

        if not case["shortcut_string"] or not case["shortcut_string"].strip():
            assert result == ""
        else:
            expected_result = " ".join(case["expected_shortcuts"]).strip()
            if len(expected_result) > 1:
                assert result == expected_result
            else:
                assert result in ("", expected_result)

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "valid_image_size", "image_support": True, "expected_result": (100, 200)},
            {"id": "no_image_support", "image_support": False, "expected_result": (0, 0)},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_image_size_various_conditions(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXObject.get_image_size with various conditions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch_object(
            AXObject, "supports_image", return_value=case["image_support"]
        )

        if case["image_support"]:
            mock_point = test_context.Mock()
            mock_point.x = case["expected_result"][0]
            mock_point.y = case["expected_result"][1]

            atspi_image_mock = test_context.Mock()
            atspi_image_mock.get_image_size.return_value = mock_point
            test_context.patch("orca.ax_object.Atspi.Image", new=atspi_image_mock)

        result = AXObject.get_image_size(mock_accessible)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "atspi_error_fallback", "atspi_error": True, "expected_result": (0, 0)},
            {"id": "successful_retrieval", "atspi_error": False, "expected_result": (150, 300)},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_image_size_error_handling(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXObject.get_image_size error handling."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch_object(AXObject, "supports_image", return_value=True)

        test_context.patch_object(AXObject, "handle_error", return_value=None)

        atspi_image_mock = test_context.Mock()
        if case["atspi_error"]:
            atspi_image_mock.get_image_size.side_effect = GLib.GError("Image error")
        else:
            mock_point = test_context.Mock()
            mock_point.x = case["expected_result"][0]
            mock_point.y = case["expected_result"][1]
            atspi_image_mock.get_image_size.return_value = mock_point

        test_context.patch("orca.ax_object.Atspi.Image", new=atspi_image_mock)

        result = AXObject.get_image_size(mock_accessible)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "atspi_help_text",
                "valid_obj": True,
                "atspi_error": False,
                "fallback_attr": None,
                "expected_result": "Official help text",
            },
            {
                "id": "fallback_to_attribute",
                "valid_obj": True,
                "atspi_error": True,
                "fallback_attr": "Fallback help",
                "expected_result": "Fallback help",
            },
            {
                "id": "no_help_available",
                "valid_obj": True,
                "atspi_error": True,
                "fallback_attr": None,
                "expected_result": "",
            },
            {
                "id": "invalid_object",
                "valid_obj": False,
                "atspi_error": False,
                "fallback_attr": None,
                "expected_result": "",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_help_text_various_conditions(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.get_help_text with various conditions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch_object(AXObject, "is_valid", side_effect=lambda obj: case["valid_obj"])

        if case["valid_obj"]:
            test_context.patch_object(
                AXObject,
                "get_attribute",
                side_effect=lambda obj, attr: case["fallback_attr"] if attr == "helptext" else None,
            )

            atspi_accessible_mock = test_context.Mock()
            if case["atspi_error"]:
                atspi_accessible_mock.get_help_text.side_effect = GLib.GError("Help text error")
            else:
                atspi_accessible_mock.get_help_text.return_value = case["expected_result"]

            test_context.patch(
                "orca.ax_object.Atspi.Accessible", new=atspi_accessible_mock
            )

        result = AXObject.get_help_text(mock_accessible)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "is_valid": False,
                "has_parent": True,
                "index": 1,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": None,
            },
            {
                "id": "no_parent",
                "is_valid": True,
                "has_parent": False,
                "index": 1,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": None,
            },
            {
                "id": "first_child_index_zero",
                "is_valid": True,
                "has_parent": True,
                "index": 0,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": None,
            },
            {
                "id": "invalid_negative_index",
                "is_valid": True,
                "has_parent": True,
                "index": -1,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": None,
            },
            {
                "id": "valid_previous_sibling",
                "is_valid": True,
                "has_parent": True,
                "index": 2,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": "sibling",
            },
            {
                "id": "self_referential_sibling",
                "is_valid": True,
                "has_parent": True,
                "index": 1,
                "has_sibling": True,
                "sibling_is_self": True,
                "expected_result": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_previous_sibling(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.get_previous_sibling with various conditions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible) if case["has_parent"] else None
        mock_sibling = (
            mock_obj if case["sibling_is_self"] else test_context.Mock(spec=Atspi.Accessible)
        )

        expected_result = case["expected_result"]
        if expected_result == "sibling" and not case["sibling_is_self"]:
            expected_result = mock_sibling

        test_context.patch_object(AXObject, "is_valid", side_effect=lambda obj: case["is_valid"])
        test_context.patch_object(AXObject, "get_parent", return_value=mock_parent)
        test_context.patch_object(
            AXObject, "get_index_in_parent", side_effect=lambda obj: case["index"]
        )
        test_context.patch_object(
            AXObject,
            "get_child",
            side_effect=lambda parent, idx: mock_sibling if case["has_sibling"] else None,
        )

        result = AXObject.get_previous_sibling(mock_obj)
        assert result == expected_result

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "is_valid": False,
                "has_parent": True,
                "index": 1,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": None,
            },
            {
                "id": "no_parent",
                "is_valid": True,
                "has_parent": False,
                "index": 1,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": None,
            },
            {
                "id": "invalid_negative_index",
                "is_valid": True,
                "has_parent": True,
                "index": -1,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": None,
            },
            {
                "id": "valid_next_sibling",
                "is_valid": True,
                "has_parent": True,
                "index": 1,
                "has_sibling": True,
                "sibling_is_self": False,
                "expected_result": "sibling",
            },
            {
                "id": "self_referential_sibling",
                "is_valid": True,
                "has_parent": True,
                "index": 1,
                "has_sibling": True,
                "sibling_is_self": True,
                "expected_result": None,
            },
            {
                "id": "no_next_sibling_available",
                "is_valid": True,
                "has_parent": True,
                "index": 1,
                "has_sibling": False,
                "sibling_is_self": False,
                "expected_result": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_next_sibling(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.get_next_sibling with various conditions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible) if case["has_parent"] else None
        mock_sibling = (
            mock_obj if case["sibling_is_self"] else test_context.Mock(spec=Atspi.Accessible)
        )

        expected_result = case["expected_result"]
        if expected_result == "sibling" and not case["sibling_is_self"]:
            expected_result = mock_sibling

        test_context.patch_object(AXObject, "is_valid", side_effect=lambda obj: case["is_valid"])
        test_context.patch_object(AXObject, "get_parent", return_value=mock_parent)
        test_context.patch_object(
            AXObject, "get_index_in_parent", side_effect=lambda obj: case["index"]
        )
        test_context.patch_object(
            AXObject,
            "get_child",
            side_effect=lambda parent, idx: mock_sibling if case["has_sibling"] else None,
        )

        result = AXObject.get_next_sibling(mock_obj)
        assert result == expected_result

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "is_valid": False,
                "child_count": 3,
                "children_valid": True,
                "becomes_invalid": False,
                "predicate_filter": None,
                "expected_count": 0,
                "warns_large": False,
            },
            {
                "id": "no_children",
                "is_valid": True,
                "child_count": 0,
                "children_valid": True,
                "becomes_invalid": False,
                "predicate_filter": None,
                "expected_count": 0,
                "warns_large": False,
            },
            {
                "id": "all_valid_children",
                "is_valid": True,
                "child_count": 3,
                "children_valid": True,
                "becomes_invalid": False,
                "predicate_filter": None,
                "expected_count": 3,
                "warns_large": False,
            },
            {
                "id": "becomes_invalid_during_iteration",
                "is_valid": True,
                "child_count": 3,
                "children_valid": True,
                "becomes_invalid": True,
                "predicate_filter": None,
                "expected_count": 1,
                "warns_large": False,
            },
            {
                "id": "with_predicate_filter",
                "is_valid": True,
                "child_count": 3,
                "children_valid": True,
                "becomes_invalid": False,
                "predicate_filter": "filter_odd",
                "expected_count": 2,
                "warns_large": False,
            },
            {
                "id": "large_child_count_warning",
                "is_valid": True,
                "child_count": 600,
                "children_valid": True,
                "becomes_invalid": False,
                "predicate_filter": None,
                "expected_count": 600,
                "warns_large": True,
            },
            {
                "id": "all_children_none",
                "is_valid": True,
                "child_count": 2,
                "children_valid": False,
                "becomes_invalid": False,
                "predicate_filter": None,
                "expected_count": 0,
                "warns_large": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_iter_children(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXObject.iter_children with various conditions."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        mock_children = []
        for i in range(case["child_count"]):
            child = test_context.Mock(spec=Atspi.Accessible) if case["children_valid"] else None
            if child:
                child.index = i
            mock_children.append(child)

        valid_calls = [0]

        def mock_is_valid(obj):
            if obj == mock_obj:
                if case["becomes_invalid"] and valid_calls[0] > 0:
                    return False
                valid_calls[0] += 1
                return case["is_valid"]
            return True

        child_calls = [0]

        def mock_get_child(parent, index):  # pylint: disable=unused-argument
            if case["becomes_invalid"] and child_calls[0] >= 1:
                return None
            child_calls[0] += 1
            if index < len(mock_children):
                return mock_children[index]
            return None

        test_context.patch_object(AXObject, "is_valid", new=mock_is_valid)
        test_context.patch_object(
            AXObject, "get_child_count", return_value=case["child_count"]
        )
        test_context.patch_object(AXObject, "get_child", new=mock_get_child)

        def pred_func(child):
            return child.index % 2 == 0

        predicate = pred_func if case["predicate_filter"] == "filter_odd" else None

        debug_calls = []
        debug_mock = test_context.Mock()
        debug_mock.LEVEL_INFO = 1
        debug_mock.print_tokens = test_context.Mock(
            side_effect=lambda *args: debug_calls.append(args)
        )
        test_context.patch("orca.ax_object.debug", new=debug_mock)

        results = list(AXObject.iter_children(mock_obj, predicate))

        assert len(results) == case["expected_count"]

        if case["warns_large"]:
            assert len(debug_calls) > 0
            warning_found = any("more than 500 children" in str(call) for call in debug_calls)
            assert warning_found
        else:
            large_warning_found = any("more than 500 children" in str(call) for call in debug_calls)
            assert not large_warning_found
