# Unit tests for say_all_presenter.py methods.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Unit tests for say_all_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext

@pytest.mark.unit
class TestSayAllPresenter:
    """Test SayAllPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Any]:
        """Set up mocks for say_all_presenter dependencies."""

        essential_modules = test_context.setup_shared_dependencies()
        additional_modules = [
            "orca.speechserver",
            "orca.input_event",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.guilabels",
            "orca.speech",
            "orca.ax_object",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.messages",
            "orca.input_event_manager",
        ]

        for module_name in additional_modules:
            if module_name not in essential_modules:
                essential_modules[module_name] = test_context.Mock()

        return essential_modules

    def test_say_all_should_skip_content(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter._say_all_should_skip_content empty content handling."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        content = (mock_obj, 0, 0, "test text")
        result = presenter._say_all_should_skip_content(content, [])
        assert result is True

    def test_parse_utterances(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter._parse_utterances with various input formats."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speech  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()

        mock_acss = test_context.Mock(spec=speech.ACSS)

        elements, voices = presenter._parse_utterances([])
        assert len(elements) == 0
        assert len(voices) == 0

        elements, voices = presenter._parse_utterances(["Hello world"])
        assert len(elements) == 1
        assert elements[0] == "Hello world"

        elements, voices = presenter._parse_utterances([["Hello"], ["world"]])
        assert len(elements) == 2
        assert elements[0] == "Hello"
        assert elements[1] == "world"

        elements, voices = presenter._parse_utterances(["Hello", mock_acss])
        assert len(elements) == 1
        assert len(voices) == 1
        assert elements[0] == "Hello"
        assert voices[0] == mock_acss

    def test_get_presenter_singleton(self, test_context: OrcaTestContext) -> None:
        """Test that get_presenter returns a singleton instance."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import get_presenter  # pylint: disable=import-outside-toplevel

        presenter1 = get_presenter()
        presenter2 = get_presenter()
        assert presenter1 is presenter2
        assert presenter1 is not None

    def test_say_all_presenter_initialization(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter initialization sets up required attributes."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        assert presenter is not None
        assert hasattr(presenter, "get_handlers")
        assert hasattr(presenter, "get_bindings")

    @pytest.mark.parametrize(
        "refresh,expected_setup_calls",
        [
            pytest.param(True, 1, id="refresh_true_calls_setup"),
            pytest.param(False, 0, id="refresh_false_uses_cache"),
        ],
    )
    def test_get_handlers(
        self,
        test_context: OrcaTestContext,
        refresh: bool,
        expected_setup_calls: int,
    ) -> None:
        """Test SayAllPresenter.get_handlers with refresh parameter."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        original_setup = presenter._setup_handlers
        setup_calls = [0]

        def mock_setup():
            setup_calls[0] += 1
            return original_setup()

        test_context.patch_object(presenter, "_setup_handlers", side_effect=mock_setup)
        handlers = presenter.get_handlers(refresh=refresh)
        assert isinstance(handlers, dict)
        assert setup_calls[0] == expected_setup_calls

    @pytest.mark.parametrize(
        "is_desktop",
        [
            pytest.param(True, id="desktop_bindings"),
            pytest.param(False, id="laptop_bindings"),
        ],
    )
    def test_get_bindings(
        self,
        test_context: OrcaTestContext,
        is_desktop: bool,
    ) -> None:
        """Test SayAllPresenter.get_bindings with different keyboard layouts."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_bindings = test_context.Mock()
        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBindings = test_context.Mock(return_value=mock_bindings)

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = test_context.Mock()
        settings_manager_mock.get_manager.return_value = manager_instance
        manager_instance.is_desktop_keyboard_layout.return_value = is_desktop

        result = presenter.get_bindings(refresh=True)
        assert result is not None
        keybindings_mock.KeyBindings.assert_called()

    def test_say_all_no_object_scenario(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter.say_all with no focus object scenario."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_locus_of_focus.return_value = None

        messages_mock = essential_modules["orca.messages"]
        messages_mock.LOCATION_NOT_FOUND_FULL = "Location not found"

        result = presenter.say_all(mock_script, obj=None)
        assert result is True

        mock_script.interrupt_presentation.assert_called_once()
        mock_script.present_message.assert_called_once_with("Location not found")

    @pytest.mark.parametrize(
        "direction,enabled,contents_available,obj_valid,expected_result",
        [
            pytest.param("rewind", False, True, True, False, id="rewind_disabled"),
            pytest.param("rewind", True, False, True, True, id="rewind_no_contents_valid_context"),
            pytest.param(
                "rewind", True, False, False, False, id="rewind_no_contents_invalid_context_obj"
            ),
            pytest.param("rewind", True, True, True, True, id="rewind_success"),
            pytest.param("fast_forward", False, True, True, False, id="fast_forward_disabled"),
            pytest.param(
                "fast_forward", True, False, True, True, id="fast_forward_no_contents_valid_context"
            ),
            pytest.param(
                "fast_forward",
                True,
                False,
                False,
                False,
                id="fast_forward_no_contents_invalid_context_obj",
            ),
            pytest.param("fast_forward", True, True, True, True, id="fast_forward_success"),
        ],
    )
    def test_navigation_controls(
        self,
        test_context: OrcaTestContext,
        direction: str,
        enabled: bool,
        contents_available: bool,
        obj_valid: bool,
        expected_result: bool,
    ) -> None:
        """Test _rewind and _fast_forward navigation controls with various conditions."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        presenter._script = mock_script

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = test_context.Mock()
        settings_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_setting.return_value = enabled

        mock_context = test_context.Mock(spec=speechserver.SayAllContext)
        mock_context.obj = "context_obj" if obj_valid else None

        if direction == "rewind":
            mock_context.start_offset = 15
        else:
            mock_context.end_offset = 25

        if contents_available:
            if direction == "rewind":
                presenter._contents = [("content_obj", 5, 10, "text")]
            else:
                presenter._contents = [("first_obj", 0, 5, "first"), ("last_obj", 20, 30, "last")]
        else:
            presenter._contents = []

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = focus_instance

        mock_script.utilities.set_caret_context = test_context.Mock()

        if direction == "rewind":
            mock_script.utilities.previous_context.return_value = ("prev_obj", 8)
        else:
            mock_script.utilities.next_context.return_value = ("next_obj", 35)

        presenter.say_all = test_context.Mock(return_value=True)
        navigation_method = getattr(presenter, f"_{direction}")
        result = navigation_method(mock_context)
        assert result == expected_result

        if expected_result:
            focus_instance.set_locus_of_focus.assert_called()
            mock_script.utilities.set_caret_context.assert_called()
            if direction == "rewind":
                mock_script.utilities.previous_context.assert_called()
            else:
                mock_script.utilities.next_context.assert_called()
            presenter.say_all.assert_called_once()

    @pytest.mark.parametrize(
        "command_method",
        [
            pytest.param("rewind", id="rewind_command"),
            pytest.param("fast_forward", id="fast_forward_command"),
        ],
    )
    def test_dbus_navigation_commands(
        self,
        test_context: OrcaTestContext,
        command_method: str,
    ) -> None:
        """Test D-Bus navigation commands delegate to private methods."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_tokens = test_context.Mock()

        private_method_name = f"_{command_method}"
        test_context.patch_object(presenter, private_method_name, return_value=True)

        command = getattr(presenter, command_method)
        result = command(mock_script, mock_event, notify_user=True)

        assert result is True
        debug_mock.print_tokens.assert_called_once()
        private_method = getattr(presenter, private_method_name)
        private_method.assert_called_once_with(None, True)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "rewind_setting_disabled_no_override",
                "direction": "rewind",
                "override_setting": False,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": False,
            },
            {
                "id": "rewind_setting_disabled_with_override",
                "direction": "rewind",
                "override_setting": True,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "rewind_setting_enabled_no_override",
                "direction": "rewind",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "rewind_setting_enabled_with_override",
                "direction": "rewind",
                "override_setting": True,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "rewind_with_provided_context",
                "direction": "rewind",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": True,
                "expected_result": True,
            },
            {
                "id": "fast_forward_setting_disabled_no_override",
                "direction": "fast_forward",
                "override_setting": False,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": False,
            },
            {
                "id": "fast_forward_setting_disabled_with_override",
                "direction": "fast_forward",
                "override_setting": True,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "fast_forward_setting_enabled_no_override",
                "direction": "fast_forward",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "fast_forward_setting_enabled_with_override",
                "direction": "fast_forward",
                "override_setting": True,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "fast_forward_with_provided_context",
                "direction": "fast_forward",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": True,
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_navigation_methods_with_parameters(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test _rewind and _fast_forward methods with override_setting parameter."""

        direction = case["direction"]
        override_setting = case["override_setting"]
        setting_enabled = case["setting_enabled"]
        context_provided = case["context_provided"]
        expected_result = case["expected_result"]

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        presenter._script = mock_script

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = test_context.Mock()
        settings_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_setting.return_value = setting_enabled

        mock_context = (test_context.Mock(spec=speechserver.SayAllContext)
                        if context_provided else None)
        if context_provided and mock_context is not None:
            mock_context.obj = "provided_obj"
            if direction == "rewind":
                mock_context.start_offset = 10
            else:
                mock_context.end_offset = 20

        current_context = test_context.Mock(spec=speechserver.SayAllContext)
        current_context.obj = "current_obj"
        if direction == "rewind":
            current_context.start_offset = 5
        else:
            current_context.end_offset = 15
        presenter._current_context = current_context

        if direction == "rewind":
            presenter._contents = [("content_obj", 0, 10, "text")]
        else:
            presenter._contents = [("first_obj", 0, 5, "first"),
                                   ("last_obj", 10, 20, "last")]

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = focus_instance

        mock_script.utilities.set_caret_context = test_context.Mock()
        if direction == "rewind":
            mock_script.utilities.previous_context.return_value = ("prev_obj", 3)
        else:
            mock_script.utilities.next_context.return_value = ("next_obj", 25)

        presenter.say_all = test_context.Mock(return_value=True)

        navigation_method = getattr(presenter, f"_{direction}")
        result = navigation_method(mock_context, override_setting)

        assert result == expected_result

        if expected_result:
            focus_instance.set_locus_of_focus.assert_called()
            mock_script.utilities.set_caret_context.assert_called()
            presenter.say_all.assert_called_once()

    def test_say_all_initialization_clears_state(self, test_context: OrcaTestContext) -> None:
        """Test say_all method clears contexts, contents, and current_context at start."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()

        presenter._contexts = [test_context.Mock(spec=speechserver.SayAllContext)]
        presenter._contents = [("old_obj", 0, 5, "old")]
        presenter._current_context = test_context.Mock(spec=speechserver.SayAllContext)

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_locus_of_focus.return_value = "focus_obj"

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_tokens = test_context.Mock()

        speech_mock = essential_modules["orca.speech"]
        speech_mock.say_all = test_context.Mock()

        mock_script.utilities.get_caret_context.return_value = ("obj", 10)

        result = presenter.say_all(mock_script, None)
        assert result is True

        assert not presenter._contexts
        assert not presenter._contents
        assert presenter._current_context is None

    def test_progress_callback_sets_current_context(self, test_context: OrcaTestContext) -> None:
        """Test that _progress_callback sets the current context."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()

        mock_context = test_context.Mock(spec=speechserver.SayAllContext)
        assert presenter._current_context is None

        presenter._current_context = mock_context
        assert presenter._current_context is mock_context
