# Unit tests for ax_utilities_action.py methods.
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
# pylint: disable=protected-access

"""Unit tests for ax_utilities_action.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXUtilitiesAction:
    """Test AXUtilitiesAction class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_action dependencies."""

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
        keynames_mock = essential_modules["orca.keynames"]
        keynames_mock.KEY_BACKSPACE = "BackSpace"
        keynames_mock.KEY_DELETE = "Delete"
        keynames_mock.KEY_TAB = "Tab"
        keynames_mock.KEY_RETURN = "Return"
        keynames_mock.KEY_ESCAPE = "Escape"

        return essential_modules

    def test_get_action_names_no_actions(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_action_names with no actions."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXAction, "get_n_actions", return_value=0)
        result = AXUtilitiesAction.get_action_names(mock_accessible)
        assert not result

    def test_get_action_names_with_actions(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_action_names with multiple actions."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXAction, "get_n_actions", return_value=3)

        def mock_get_action_name(_obj, i) -> str:
            names = ["click", "", "press"]
            return names[i]

        test_context.patch_object(AXAction, "get_action_name", new=mock_get_action_name)
        result = AXUtilitiesAction.get_action_names(mock_accessible)
        assert result == ["click", "press"]

    def test_get_action_index_found(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_action_index found action."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXAction,
            "normalize_action_name",
            side_effect=lambda name: name.lower(),
        )
        test_context.patch_object(AXAction, "get_n_actions", return_value=2)

        def mock_get_action_name(_obj, index) -> str:
            if index == 0:
                return "press"
            return "click"

        test_context.patch_object(AXAction, "get_action_name", new=mock_get_action_name)
        result = AXUtilitiesAction.get_action_index(mock_accessible, "click")
        assert result == 1

    def test_get_action_index_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_action_index not found."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXAction,
            "normalize_action_name",
            side_effect=lambda name: name.lower(),
        )
        test_context.patch_object(AXAction, "get_n_actions", return_value=2)
        test_context.patch_object(AXAction, "get_action_name", return_value="press")
        result = AXUtilitiesAction.get_action_index(mock_accessible, "click")
        assert result == -1

    def test_do_named_action_success(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.do_named_action success."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesAction, "get_action_index", return_value=0)
        test_context.patch_object(AXAction, "do_action", return_value=True)
        result = AXUtilitiesAction.do_named_action(mock_accessible, "click")
        assert result is True

    def test_do_named_action_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.do_named_action action not found."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesAction, "get_action_index", return_value=-1)
        result = AXUtilitiesAction.do_named_action(mock_accessible, "click")
        assert result is False

    def test_find_first_action_with_keybinding_found(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesAction._find_first_action_with_keybinding found action."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXAction, "get_n_actions", return_value=2)

        def mock_get_action_key_binding(_obj, index) -> str:
            if index == 0:
                return ""
            return "Alt+F"

        test_context.patch_object(
            AXAction,
            "get_action_key_binding",
            new=mock_get_action_key_binding,
        )
        result = AXUtilitiesAction._find_first_action_with_keybinding(mock_accessible)
        assert result == 1

    def test_find_first_action_with_keybinding_not_found(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesAction._find_first_action_with_keybinding not found."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXAction, "get_n_actions", return_value=2)
        test_context.patch_object(AXAction, "get_action_key_binding", return_value="")
        result = AXUtilitiesAction._find_first_action_with_keybinding(mock_accessible)
        assert result == -1

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "empty_string",
                "sequence": "",
                "gtk_result": None,
                "localized": None,
                "expected": "",
            },
            {
                "id": "normalizes_plus_separated",
                "sequence": "Ctrl+F",
                "gtk_result": "Ctrl+F",
                "localized": "Ctrl+F",
                "expected": "Ctrl+F",
            },
            {
                "id": "already_angle_bracket",
                "sequence": "<Primary>F",
                "gtk_result": "Ctrl+F",
                "localized": "Ctrl+F",
                "expected": "Ctrl+F",
            },
            {
                "id": "gtk_returns_trailing_plus",
                "sequence": "Alt+F",
                "gtk_result": "Alt+",
                "localized": "<Alt>F",
                "expected": "<Alt>F",
            },
            {
                "id": "single_char_skips_normalization",
                "sequence": "F",
                "gtk_result": "F",
                "localized": "F",
                "expected": "F",
            },
            {
                "id": "comma_separated_skips_normalization",
                "sequence": "Ctrl+F,Ctrl+G",
                "gtk_result": "",
                "localized": "Ctrl+F,Ctrl+G",
                "expected": "Ctrl+F,Ctrl+G",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_label_for_key_sequence(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXUtilitiesAction._get_label_for_key_sequence normalization and Gtk parsing."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_action import AXUtilitiesAction

        if case["sequence"]:
            gi_repo = test_context.patch("orca.ax_utilities_action.Gtk")
            gi_repo.accelerator_parse.return_value = (0, 0)
            gi_repo.accelerator_get_label.return_value = case["gtk_result"]

            keynames_mock = essential_modules["orca.keynames"]
            keynames_mock.localize_key_sequence.side_effect = lambda s: s

        result = AXUtilitiesAction._get_label_for_key_sequence(case["sequence"])

        if not case["sequence"]:
            assert result == ""
        elif case["gtk_result"] and not case["gtk_result"].endswith("+"):
            assert result == case["gtk_result"]
        else:
            assert result == case["localized"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "from_keyshortcuts_attribute",
                "attributes": {"keyshortcuts": "Ctrl+F"},
                "label_result": "Ctrl+F",
                "keybinding_index": -1,
                "expected": "Ctrl+F",
            },
            {
                "id": "single_char_shortcut_not_accelerator",
                "attributes": {"keyshortcuts": "F"},
                "label_result": "F",
                "keybinding_index": -1,
                "expected": "",
            },
            {
                "id": "from_action_keybinding_three_parts",
                "attributes": {},
                "label_result": "Ctrl+F",
                "keybinding_index": 0,
                "keybinding_string": "F;Alt+F;Ctrl+F",
                "expected": "Ctrl+F",
            },
            {
                "id": "from_action_keybinding_ctrl_in_last",
                "attributes": {},
                "label_result": "Ctrl+F",
                "keybinding_index": 0,
                "keybinding_string": "Ctrl+F",
                "expected": "Ctrl+F",
            },
            {
                "id": "from_action_keybinding_no_ctrl",
                "attributes": {},
                "label_result": "Alt+F",
                "keybinding_index": 0,
                "keybinding_string": "Alt+F",
                "expected": "",
            },
            {
                "id": "no_shortcuts_no_keybinding",
                "attributes": {},
                "label_result": "",
                "keybinding_index": -1,
                "expected": "",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_accelerator(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXUtilitiesAction.get_accelerator parsing paths."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value=case["attributes"])
        test_context.patch_object(
            AXUtilitiesAction,
            "_get_label_for_key_sequence",
            side_effect=lambda seq: case["label_result"] if seq else "",
        )
        test_context.patch_object(
            AXUtilitiesAction,
            "_find_first_action_with_keybinding",
            return_value=case["keybinding_index"],
        )
        if case["keybinding_index"] >= 0:
            test_context.patch_object(
                AXAction,
                "get_action_key_binding",
                return_value=case.get("keybinding_string", ""),
            )

        result = AXUtilitiesAction.get_accelerator(mock_accessible)
        assert result == case["expected"]

    def test_get_mnemonic_no_attributes(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_mnemonic with no keyshortcuts attribute."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXUtilitiesAction, "_find_first_action_with_keybinding", return_value=-1
        )
        result = AXUtilitiesAction.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_single_letter_shortcut(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_mnemonic with single letter keyshortcut."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject,
            "get_attributes_dict",
            return_value={"keyshortcuts": "F"},
        )
        test_context.patch_object(
            AXUtilitiesAction, "_get_label_for_key_sequence", return_value="F"
        )
        result = AXUtilitiesAction.get_mnemonic(mock_accessible)
        assert result == "F"

    def test_get_mnemonic_multiple_letter_shortcut(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_mnemonic with multi-letter keyshortcut."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject,
            "get_attributes_dict",
            return_value={"keyshortcuts": "Ctrl+F"},
        )
        test_context.patch_object(
            AXUtilitiesAction, "_get_label_for_key_sequence", return_value="Ctrl+F"
        )
        test_context.patch_object(
            AXUtilitiesAction, "_find_first_action_with_keybinding", return_value=-1
        )
        result = AXUtilitiesAction.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_from_action_keybinding(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_mnemonic from action key binding."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXUtilitiesAction, "_find_first_action_with_keybinding", return_value=0
        )
        test_context.patch_object(AXAction, "get_action_key_binding", return_value="Alt+F;Alt+F")
        test_context.patch_object(
            AXUtilitiesAction, "_get_label_for_key_sequence", return_value="Alt+F"
        )
        result = AXUtilitiesAction.get_mnemonic(mock_accessible)
        assert result == "Alt+F"

    def test_get_mnemonic_with_ctrl_in_result(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_mnemonic with Ctrl in result."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXUtilitiesAction, "_find_first_action_with_keybinding", return_value=0
        )
        test_context.patch_object(AXAction, "get_action_key_binding", return_value="Ctrl+F;Ctrl+F")
        test_context.patch_object(
            AXUtilitiesAction, "_get_label_for_key_sequence", return_value="Ctrl+F"
        )
        result = AXUtilitiesAction.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_with_space(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesAction.get_mnemonic with space key."""

        self._setup_dependencies(test_context)
        from orca.ax_action import AXAction
        from orca.ax_object import AXObject
        from orca.ax_utilities_action import AXUtilitiesAction

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(
            AXUtilitiesAction, "_find_first_action_with_keybinding", return_value=0
        )
        test_context.patch_object(AXAction, "get_action_key_binding", return_value="space;space")
        test_context.patch_object(
            AXUtilitiesAction, "_get_label_for_key_sequence", return_value="space"
        )
        result = AXUtilitiesAction.get_mnemonic(mock_accessible)
        assert result == ""
