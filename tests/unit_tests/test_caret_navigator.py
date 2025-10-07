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
            "orca.script_manager",
        ]

        for module_name in additional_modules:
            if module_name not in essential_modules:
                essential_modules[module_name] = test_context.Mock()

        return essential_modules

    @pytest.mark.parametrize(
        "direction,event_provided,context_available,expected_result",
        [
            pytest.param("next", False, True, True, id="next_char_no_event_returns_true"),
            pytest.param("next", True, False, False, id="next_char_no_context_returns_false"),
            pytest.param("next", True, True, True, id="next_char_valid_navigation_succeeds"),
            pytest.param("previous", False, True, True, id="prev_char_no_event_returns_true"),
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

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject.supports_text.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_valid.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_ancestor.side_effect = (
            lambda obj, root, same: obj is not None and root is not None
        )

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_get_root_object", return_value=None)
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

        navigation_method = getattr(navigator, f"{direction}_character")
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

        navigation_method = getattr(navigator, f"{direction}_word")
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
        "test_method,expected_result",
        [
            pytest.param("suspend_commands", True, id="suspend_commands"),
            pytest.param("toggle_enabled", True, id="toggle_enabled"),
        ],
    )
    def test_navigator_control_methods(
        self,
        test_context: OrcaTestContext,
        test_method: str,
        expected_result: bool,
    ) -> None:
        """Test CaretNavigator control methods."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        if test_method == "suspend_commands":
            mock_script.key_bindings = test_context.Mock()
            mock_script.key_bindings.remove = test_context.Mock()
            mock_script.key_bindings.add = test_context.Mock()
            test_context.patch_object(navigator, "refresh_bindings_and_grabs")
            test_context.patch_object(navigator, "_is_active_script", return_value=True)
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
            mock_script.utilities.get_caret_context.return_value = ("obj", 5)
            mock_script.utilities.get_previous_line_contents.return_value = next_prev_contents

        mock_script.utilities.set_caret_position = test_context.Mock()
        mock_script.interrupt_presentation = test_context.Mock()
        mock_script.speak_contents = test_context.Mock()
        mock_script.display_contents = test_context.Mock()

        navigation_method = getattr(navigator, f"{navigation_type}")
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

        navigation_method = getattr(navigator, f"{navigation_type}")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        if expected_result:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            mock_script.interrupt_presentation.assert_called_once()
            mock_script.say_character.assert_called_once()
            mock_script.display_contents.assert_called_once()

    @pytest.mark.parametrize(
        "script_is_active,expected_result",
        [
            pytest.param(True, True, id="script_is_active"),
            pytest.param(False, False, id="script_is_not_active"),
        ],
    )
    def test_is_active_script(
        self,
        test_context: OrcaTestContext,
        script_is_active: bool,
        expected_result: bool,
    ) -> None:
        """Test _is_active_script method with active and non-active scripts."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_active_script = test_context.Mock() if script_is_active else test_context.Mock()

        script_manager_mock = essential_modules["orca.script_manager"]
        manager_instance = test_context.Mock()
        script_manager_mock.get_manager.return_value = manager_instance

        if script_is_active:
            manager_instance.get_active_script.return_value = mock_script
        else:
            manager_instance.get_active_script.return_value = mock_active_script

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_tokens = test_context.Mock()

        result = navigator._is_active_script(mock_script)
        assert result == expected_result

        if not script_is_active:
            debug_mock.print_tokens.assert_called_once()

    @pytest.mark.parametrize(
        "script_is_active,suspended,debug_level",
        [
            pytest.param(True, False, 0, id="active_script_not_suspended_debug_on"),
            pytest.param(True, True, 0, id="active_script_suspended_debug_on"),
            pytest.param(False, False, 0, id="non_active_script_debug_on"),
            pytest.param(True, False, 1000, id="active_script_debug_off"),
        ],
    )
    def test_add_bindings(
        self,
        test_context: OrcaTestContext,
        script_is_active: bool,
        suspended: bool,
        debug_level: int,
    ) -> None:
        """Test add_bindings method with various script states."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_script.key_bindings = test_context.Mock()
        mock_script.key_bindings.add = test_context.Mock()
        mock_script.key_bindings.get_bindings_with_grabs_for_debugging = test_context.Mock(
            return_value=[1, 2, 3]
        )

        navigator._suspended = suspended

        script_manager_mock = essential_modules["orca.script_manager"]
        manager_instance = test_context.Mock()
        script_manager_mock.get_manager.return_value = manager_instance

        if script_is_active:
            manager_instance.get_active_script.return_value = mock_script
        else:
            manager_instance.get_active_script.return_value = test_context.Mock()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.debugLevel = debug_level
        debug_mock.print_tokens = test_context.Mock()

        mock_bindings = test_context.Mock()
        mock_bindings.key_bindings = [test_context.Mock(), test_context.Mock()]
        test_context.patch_object(navigator, "get_handlers", return_value={})
        test_context.patch_object(navigator, "get_bindings", return_value=mock_bindings)

        navigator.add_bindings(mock_script, "test reason")

        if script_is_active:
            assert debug_mock.print_tokens.call_count >= 1
            assert mock_script.key_bindings.add.call_count == len(mock_bindings.key_bindings)
            if debug_level <= 800:
                grabs_call_count = 2
                grabs_method = mock_script.key_bindings.get_bindings_with_grabs_for_debugging
                actual_grabs_call_count = grabs_method.call_count
                assert actual_grabs_call_count == grabs_call_count
        else:
            assert mock_script.key_bindings.add.call_count == 0

    @pytest.mark.parametrize(
        "script_is_active,debug_level",
        [
            pytest.param(True, 0, id="active_script_debug_on"),
            pytest.param(False, 0, id="non_active_script_debug_on"),
            pytest.param(True, 1000, id="active_script_debug_off"),
        ],
    )
    def test_remove_bindings(
        self,
        test_context: OrcaTestContext,
        script_is_active: bool,
        debug_level: int,
    ) -> None:
        """Test remove_bindings method with various script states."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_script.key_bindings = test_context.Mock()
        mock_script.key_bindings.remove = test_context.Mock()
        mock_script.key_bindings.get_bindings_with_grabs_for_debugging = test_context.Mock(
            return_value=[1, 2, 3]
        )

        mock_bindings = test_context.Mock()
        mock_bindings.key_bindings = [test_context.Mock(), test_context.Mock()]
        navigator._bindings = mock_bindings

        script_manager_mock = essential_modules["orca.script_manager"]
        manager_instance = test_context.Mock()
        script_manager_mock.get_manager.return_value = manager_instance

        if script_is_active:
            manager_instance.get_active_script.return_value = mock_script
        else:
            manager_instance.get_active_script.return_value = test_context.Mock()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.debugLevel = debug_level
        debug_mock.print_tokens = test_context.Mock()

        navigator.remove_bindings(mock_script, "test reason")

        if script_is_active:
            assert debug_mock.print_tokens.call_count >= 1
            assert mock_script.key_bindings.remove.call_count == len(mock_bindings.key_bindings)
            if debug_level <= 800:
                grabs_call_count = 2
                grabs_method = mock_script.key_bindings.get_bindings_with_grabs_for_debugging
                actual_grabs_call_count = grabs_method.call_count
                assert actual_grabs_call_count == grabs_call_count
        else:
            assert mock_script.key_bindings.remove.call_count == 0

    def test_refresh_bindings_updates_script_bindings(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test refresh_bindings_and_grabs properly updates script key bindings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_script.key_bindings = test_context.Mock()
        mock_script.key_bindings.remove = test_context.Mock()
        mock_script.key_bindings.add = test_context.Mock()
        mock_script.key_bindings.get_bindings_with_grabs_for_debugging = test_context.Mock(
            return_value=[1, 2, 3]
        )

        script_manager_mock = essential_modules["orca.script_manager"]
        manager_instance = test_context.Mock()
        script_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_active_script.return_value = mock_script

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.debugLevel = 0
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()

        old_bindings = test_context.Mock()
        old_bindings.key_bindings = [test_context.Mock()]
        navigator._bindings = old_bindings

        new_bindings = test_context.Mock()
        new_bindings.key_bindings = [test_context.Mock(), test_context.Mock()]
        test_context.patch_object(navigator, "get_handlers", return_value={})
        test_context.patch_object(navigator, "get_bindings", return_value=new_bindings)

        navigator.refresh_bindings_and_grabs(mock_script, "test reason")

        assert mock_script.key_bindings.remove.call_count == len(old_bindings.key_bindings)
        assert mock_script.key_bindings.add.call_count == len(new_bindings.key_bindings)
        assert navigator._handlers == {}
        assert navigator._bindings == new_bindings
        debug_mock.print_message.assert_called_once()

    def test_get_is_enabled(self, test_context: OrcaTestContext) -> None:
        """Test get_is_enabled returns setting value."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = True
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.get_is_enabled()
        assert result is True
        settings_mock.get_setting.assert_called_with("caretNavigationEnabled")

    def test_set_is_enabled_no_change(self, test_context: OrcaTestContext) -> None:
        """Test set_is_enabled returns early if value unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = True
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.set_is_enabled(True)
        assert result is True
        settings_mock.set_setting.assert_not_called()

    def test_set_is_enabled_updates_setting(self, test_context: OrcaTestContext) -> None:
        """Test set_is_enabled updates setting and refreshes bindings."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = False
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_refresh = test_context.Mock()
        test_context.patch_object(navigator, "refresh_bindings_and_grabs", new=mock_refresh)

        result = navigator.set_is_enabled(True)
        assert result is True
        settings_mock.set_setting.assert_called_with("caretNavigationEnabled", True)
        assert navigator._last_input_event is None
        mock_refresh.assert_called_once()

    def test_set_is_enabled_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test set_is_enabled returns early if no active script."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = False
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = None
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_refresh = test_context.Mock()
        test_context.patch_object(navigator, "refresh_bindings_and_grabs", new=mock_refresh)

        result = navigator.set_is_enabled(True)
        assert result is True
        mock_refresh.assert_not_called()

    def test_get_triggers_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test get_triggers_focus_mode returns setting value."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = False
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.get_triggers_focus_mode()
        assert result is False
        settings_mock.get_setting.assert_called_with("caretNavTriggersFocusMode")

    def test_set_triggers_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test set_triggers_focus_mode updates setting."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = True
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.set_triggers_focus_mode(False)
        assert result is True
        settings_mock.set_setting.assert_called_with("caretNavTriggersFocusMode", False)

    def test_set_triggers_focus_mode_no_change(self, test_context: OrcaTestContext) -> None:
        """Test set_triggers_focus_mode returns early if unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = True
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.set_triggers_focus_mode(True)
        assert result is True
        settings_mock.set_setting.assert_not_called()

    def test_get_enabled_for_script(self, test_context: OrcaTestContext) -> None:
        """Test get_enabled_for_script returns script-specific state."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        navigator._enabled_for_script[mock_script] = True
        result = navigator.get_enabled_for_script(mock_script)
        assert result is True

    def test_get_enabled_for_script_default(self, test_context: OrcaTestContext) -> None:
        """Test get_enabled_for_script returns False by default."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.get_enabled_for_script(mock_script)
        assert result is False

    def test_set_enabled_for_script(self, test_context: OrcaTestContext) -> None:
        """Test set_enabled_for_script updates script-specific state."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = False
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_refresh = test_context.Mock()
        test_context.patch_object(navigator, "refresh_bindings_and_grabs", new=mock_refresh)
        test_context.patch_object(navigator, "_is_active_script", return_value=True)

        navigator.set_enabled_for_script(mock_script, True)
        assert navigator._enabled_for_script[mock_script] is True

    def test_set_enabled_for_script_inactive_script(self, test_context: OrcaTestContext) -> None:
        """Test set_enabled_for_script doesn't call set_is_enabled for inactive script."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_is_active_script", return_value=False)
        mock_set_is_enabled = test_context.Mock()
        test_context.patch_object(navigator, "set_is_enabled", new=mock_set_is_enabled)

        navigator.set_enabled_for_script(mock_script, True)
        assert navigator._enabled_for_script[mock_script] is True
        mock_set_is_enabled.assert_not_called()

    def test_last_command_prevents_focus_mode_true(self, test_context: OrcaTestContext) -> None:
        """Test last_command_prevents_focus_mode returns True."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = False
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_event = test_context.Mock()
        navigator._last_input_event = mock_event
        test_context.patch_object(
            navigator, "last_input_event_was_navigation_command", return_value=True
        )
        result = navigator.last_command_prevents_focus_mode()
        assert result is True

    def test_last_command_prevents_focus_mode_false_no_event(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test last_command_prevents_focus_mode returns False if no event."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        navigator._last_input_event = None
        result = navigator.last_command_prevents_focus_mode()
        assert result is False

    def test_last_command_prevents_focus_mode_false_setting_true(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test last_command_prevents_focus_mode returns False if setting True."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = test_context.Mock()
        settings_mock.get_setting.return_value = True
        essential_modules["orca.settings_manager"].get_manager.return_value = settings_mock
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_event = test_context.Mock()
        navigator._last_input_event = mock_event
        test_context.patch_object(
            navigator, "last_input_event_was_navigation_command", return_value=True
        )
        result = navigator.last_command_prevents_focus_mode()
        assert result is False
