# Unit tests for caret_navigator.py methods.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Unit tests for caret_navigator.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext

@pytest.mark.unit
class TestCaretNavigator:
    """Test CaretNavigator class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Any]:
        """Set up mocks for caret_navigator dependencies."""

        essential_modules = test_context.setup_shared_dependencies()
        additional_modules = [
            "orca.input_event_manager",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.guilabels",
            "orca.debug",
            "orca.ax_object",
            "orca.ax_text",
        ]

        for module_name in additional_modules:
            if module_name not in essential_modules:
                essential_modules[module_name] = test_context.Mock()

        return essential_modules

    @pytest.mark.parametrize(
        "direction,event_provided,context_available,expected_result",
        [
            pytest.param("next", False, True, False, id="next_char_no_event_returns_false"),
            pytest.param("next", True, False, False, id="next_char_no_context_returns_false"),
            pytest.param("next", True, True, True, id="next_char_valid_navigation_succeeds"),
            pytest.param("previous", False, True, False, id="prev_char_no_event_returns_false"),
            pytest.param("previous", True, False, False, id="prev_char_no_context_returns_false"),
            pytest.param("previous", True, True, True, id="prev_char_valid_navigation_succeeds"),
        ],
    )
    def test_character_navigation(
        self,
        test_context: OrcaTestContext,
        direction: str,
        event_provided: bool,
        context_available: bool,
        expected_result: bool,
    ) -> None:
        """Test character navigation (next/previous) with various conditions."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock() if event_provided else None

        if context_available:
            mock_obj = test_context.Mock()
            if direction == "next":
                mock_script.utilities.next_context.return_value = (mock_obj, 10)
            else:
                mock_script.utilities.previous_context.return_value = (mock_obj, 5)
        else:
            if direction == "next":
                mock_script.utilities.next_context.return_value = (None, 0)
            else:
                mock_script.utilities.previous_context.return_value = (None, 0)

        navigation_method = getattr(navigator, f"_{direction}_character")
        result = navigation_method(mock_script, mock_event)
        assert result == expected_result

        if expected_result:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called_once()
            mock_script.interrupt_presentation.assert_called_once()
            mock_script.update_braille.assert_called_once()
            mock_script.say_character.assert_called_once()

    @pytest.mark.parametrize(
        "direction,context_result,word_contents,expected_result",
        [
            pytest.param("next", (None, 0), None, False, id="next_word_no_context"),
            pytest.param("next", ("obj", 20), [], False, id="next_word_no_contents"),
            pytest.param(
                "next", ("obj", 20), [("obj", 20, 25, "word")], True, id="next_word_success"
            ),
            pytest.param("previous", (None, 0), None, False, id="previous_word_no_context"),
            pytest.param("previous", ("obj", 15), [], False, id="previous_word_no_contents"),
            pytest.param(
                "previous", ("obj", 15), [("obj", 10, 15, "word")], True, id="previous_word_success"
            ),
        ],
    )
    def test_word_navigation(
        self,
        test_context: OrcaTestContext,
        direction: str,
        context_result: tuple,
        word_contents: list | None,
        expected_result: bool,
    ) -> None:
        """Test word navigation (next/previous) with various error conditions."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        if direction == "next":
            mock_script.utilities.next_context.return_value = context_result
        else:
            mock_script.utilities.previous_context.return_value = context_result

        mock_script.utilities.get_word_contents_at_offset.return_value = word_contents or []

        mock_script.utilities.set_caret_position = test_context.Mock()
        mock_script.interrupt_presentation = test_context.Mock()
        mock_script.update_braille = test_context.Mock()
        mock_script.say_word = test_context.Mock()

        navigation_method = getattr(navigator, f"_{direction}_word")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        if expected_result:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            mock_script.interrupt_presentation.assert_called_once()
            mock_script.update_braille.assert_called_once()
            mock_script.say_word.assert_called_once()
        else:
            mock_script.utilities.set_caret_position.assert_not_called()
            mock_script.interrupt_presentation.assert_not_called()

    @pytest.mark.parametrize(
        "test_method,scenario,expected_result",
        [
            pytest.param("handles_navigation", "external_handler", False, id="external_handler"),
            pytest.param("handles_navigation", "nav_handler", True, id="nav_handler"),
            pytest.param("suspend_commands", "suspend_true", True, id="suspend_commands"),
            pytest.param("toggle_enabled", "toggle_test", True, id="toggle_enabled"),
        ],
    )
    def test_navigator_control_methods(
        self,
        test_context: OrcaTestContext,
        test_method: str,
        scenario: str,
        expected_result: bool,
    ) -> None:
        """Test CaretNavigator control methods."""
        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        if test_method == "handles_navigation":
            if scenario == "external_handler":
                external_handler = test_context.Mock()
                external_handler.function = test_context.Mock()
                result = navigator.handles_navigation(external_handler)
                assert result == expected_result
            elif scenario == "nav_handler":
                nav_handler = navigator._handlers.get("next_character")
                if nav_handler:
                    result = navigator.handles_navigation(nav_handler)
                    assert result == expected_result

        elif test_method == "suspend_commands":
            mock_script.key_bindings = test_context.Mock()
            mock_script.key_bindings.remove = test_context.Mock()
            mock_script.key_bindings.add = test_context.Mock()
            test_context.patch_object(navigator, "refresh_bindings_and_grabs")
            navigator._suspended = False
            navigator.suspend_commands(mock_script, True, "test reason")
            assert navigator._suspended == expected_result

        elif test_method == "toggle_enabled":
            mock_script.key_bindings = test_context.Mock()
            mock_script.key_bindings.remove = test_context.Mock()
            mock_script.key_bindings.add = test_context.Mock()

            settings_manager_mock = essential_modules["orca.settings_manager"]
            manager_instance = test_context.Mock()
            settings_manager_mock.get_manager.return_value = manager_instance

            guilabels_mock = essential_modules["orca.guilabels"]
            guilabels_mock.CARET_NAVIGATION_ENABLED = "Caret navigation enabled"
            guilabels_mock.CARET_NAVIGATION_DISABLED = "Caret navigation disabled"

            test_context.patch_object(navigator, "refresh_bindings_and_grabs")

            result = navigator.toggle_enabled(mock_script, mock_event)
            assert result == expected_result

    @pytest.mark.parametrize(
        "test_method,param_data,expected_checks",
        [
            pytest.param(
                "initialization",
                {},
                ["_handlers", "_bindings", "_last_input_event", "_suspended"],
                id="initialization",
            ),
            pytest.param(
                "get_handlers",
                {"refresh": True, "expected_type": dict},
                ["isinstance_dict"],
                id="get_handlers_refresh",
            ),
            pytest.param(
                "get_handlers",
                {"refresh": False, "expected_type": dict},
                ["isinstance_dict"],
                id="get_handlers_cached",
            ),
            pytest.param(
                "get_bindings",
                {"is_desktop": True, "refresh": True},
                ["not_none"],
                id="get_bindings_desktop",
            ),
            pytest.param(
                "get_bindings",
                {"is_desktop": False, "refresh": True},
                ["not_none"],
                id="get_bindings_laptop",
            ),
        ],
    )
    def test_navigator_setup_and_getter_methods(
        self,
        test_context: OrcaTestContext,
        test_method: str,
        param_data: dict,
        expected_checks: list[str],
    ) -> None:
        """Test CaretNavigator setup and getter methods."""
        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()

        if test_method == "initialization":
            for attr in expected_checks:
                assert hasattr(navigator, attr)
            assert navigator._handlers is not None
            assert navigator._bindings is not None
            assert navigator._last_input_event is None
            assert navigator._suspended is False

        elif test_method == "get_handlers":
            handlers = navigator.get_handlers(refresh=param_data["refresh"])
            if "isinstance_dict" in expected_checks:
                assert isinstance(handlers, param_data["expected_type"])

        elif test_method == "get_bindings":
            keybindings_mock = essential_modules["orca.keybindings"]
            mock_bindings = test_context.Mock()
            keybindings_mock.KeyBindings = test_context.Mock(return_value=mock_bindings)

            result = navigator.get_bindings(
                refresh=param_data["refresh"], is_desktop=param_data["is_desktop"]
            )
            if "not_none" in expected_checks:
                assert result is not None

    @pytest.mark.parametrize(
        "navigation_type,in_say_all,current_line,next_prev_contents,expected_result",
        [
            pytest.param(
                "next_line", True, [("obj", 0, 10, "text")], [], True, id="next_line_in_say_all"
            ),
            pytest.param("next_line", False, [], [], False, id="next_line_no_current_line"),
            pytest.param(
                "next_line",
                False,
                [("obj", 0, 10, "text")],
                [],
                False,
                id="next_line_no_next_contents",
            ),
            pytest.param(
                "next_line",
                False,
                [("obj", 0, 10, "text")],
                [("obj2", 11, 21, "next")],
                True,
                id="next_line_success",
            ),
            pytest.param("previous_line", True, None, [], True, id="previous_line_in_say_all"),
            pytest.param("previous_line", False, None, [], False, id="previous_line_no_contents"),
            pytest.param(
                "previous_line",
                False,
                None,
                [("obj", 0, 10, "prev")],
                True,
                id="previous_line_success",
            ),
        ],
    )
    def test_line_navigation(
        self,
        test_context: OrcaTestContext,
        navigation_type: str,
        in_say_all: bool,
        current_line: list | None,
        next_prev_contents: list,
        expected_result: bool,
    ) -> None:
        """Test line navigation including say-all mode handling."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        manager_instance.in_say_all.return_value = in_say_all

        if in_say_all:
            settings_manager_mock = essential_modules["orca.settings_manager"]
            settings_instance = test_context.Mock()
            settings_manager_mock.get_manager.return_value = settings_instance
            settings_instance.get_setting.return_value = True

        if navigation_type == "next_line" and not in_say_all:
            mock_script.utilities.get_caret_context.return_value = ("obj", 5)
            mock_script.utilities.get_line_contents_at_offset.return_value = current_line
            mock_script.utilities.get_next_line_contents.return_value = next_prev_contents
        elif navigation_type == "previous_line" and not in_say_all:
            mock_script.utilities.get_previous_line_contents.return_value = next_prev_contents

        mock_script.utilities.set_caret_position = test_context.Mock()
        mock_script.interrupt_presentation = test_context.Mock()
        mock_script.speak_contents = test_context.Mock()
        mock_script.display_contents = test_context.Mock()

        navigation_method = getattr(navigator, f"_{navigation_type}")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        if expected_result and not in_say_all:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            mock_script.interrupt_presentation.assert_called_once()
            mock_script.speak_contents.assert_called_once()
            mock_script.display_contents.assert_called_once()
        elif in_say_all:
            assert navigator._last_input_event != mock_event

    @pytest.mark.parametrize(
        "navigation_type,line_contents,expected_result",
        [
            pytest.param("start_of_line", [], False, id="start_of_line_no_line"),
            pytest.param(
                "start_of_line", [("obj", 5, 15, "text")], True, id="start_of_line_success"
            ),
            pytest.param("end_of_line", [], False, id="end_of_line_no_line"),
            pytest.param(
                "end_of_line", [("obj", 5, 15, "text ")], True, id="end_of_line_with_space"
            ),
            pytest.param("end_of_line", [("obj", 5, 15, "text")], True, id="end_of_line_no_space"),
        ],
    )
    def test_line_boundary_navigation(
        self,
        test_context: OrcaTestContext,
        navigation_type: str,
        line_contents: list,
        expected_result: bool,
    ) -> None:
        """Test start/end of line navigation."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        mock_script.utilities.get_caret_context.return_value = ("obj", 10)
        mock_script.utilities.get_line_contents_at_offset.return_value = line_contents

        mock_script.utilities.set_caret_position = test_context.Mock()
        mock_script.interrupt_presentation = test_context.Mock()
        mock_script.say_character = test_context.Mock()
        mock_script.display_contents = test_context.Mock()

        navigation_method = getattr(navigator, f"_{navigation_type}")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        if expected_result:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            mock_script.interrupt_presentation.assert_called_once()
            mock_script.say_character.assert_called_once()
            mock_script.display_contents.assert_called_once()
