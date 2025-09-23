# Unit tests for flat_review_presenter.py methods.
#
# Copyright 2025 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=protected-access
# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for flat_review_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestFlatReviewPresenter:
    """Test FlatReviewPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for flat_review_presenter dependencies."""

        additional_modules = [
            "gi",
            "gi.repository",
            "gi.repository.Atspi",
            "gi.repository.Gtk",
            "gi.repository.GLib",
            "orca.flat_review",
            "orca.speech_and_verbosity_manager",
            "orca.ax_event_synthesizer",
            "orca.ax_text",
            "orca.braille_presenter",
            "orca.orca_platform",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        gi_repository_mock = essential_modules["gi.repository"]
        atspi_mock = essential_modules["gi.repository.Atspi"]
        gi_repository_mock.Atspi = atspi_mock

        gtk_mock = essential_modules["gi.repository.Gtk"]
        window_mock = test_context.Mock()
        gtk_mock.Window = test_context.Mock(return_value=window_mock)
        gtk_mock.VBox = test_context.Mock()
        gtk_mock.Label = test_context.Mock()
        gtk_mock.Button = test_context.Mock()

        glib_mock = essential_modules["gi.repository.GLib"]
        glib_error_mock = type("GError", (Exception,), {})
        glib_mock.GError = glib_error_mock

        flat_review_mock = essential_modules["orca.flat_review"]
        flat_review_context_mock = test_context.Mock()

        flat_review_context_mock.get_current_object = test_context.Mock(
            return_value=test_context.Mock()
        )
        flat_review_context_mock.get_current_word = test_context.Mock(return_value="test word")
        flat_review_context_mock.get_current_line = test_context.Mock(return_value="test line")
        flat_review_context_mock.get_current_line_string = test_context.Mock(
            return_value="test line"
        )
        flat_review_context_mock.get_current_char = test_context.Mock(return_value="t")
        flat_review_context_mock.get_current_character = test_context.Mock(return_value="t")
        flat_review_context_mock.get_current_item = test_context.Mock(return_value="test item")
        flat_review_context_mock.get_contents = test_context.Mock(return_value="test content")
        flat_review_context_mock.get_current_braille_regions = test_context.Mock(
            return_value=([], None)
        )

        flat_review_context_mock.go_next_line = test_context.Mock(return_value=True)
        flat_review_context_mock.go_previous_line = test_context.Mock(return_value=True)
        flat_review_context_mock.go_next_item = test_context.Mock(return_value=True)
        flat_review_context_mock.go_previous_item = test_context.Mock(return_value=True)
        flat_review_context_mock.go_next_character = test_context.Mock(return_value=True)
        flat_review_context_mock.go_previous_character = test_context.Mock(return_value=True)
        flat_review_context_mock.go_begin_line = test_context.Mock(return_value=True)
        flat_review_context_mock.go_end_line = test_context.Mock(return_value=True)
        flat_review_context_mock.go_top_left = test_context.Mock(return_value=True)
        flat_review_context_mock.go_bottom_right = test_context.Mock(return_value=True)
        flat_review_context_mock.go_bottom_left = test_context.Mock(return_value=True)
        flat_review_context_mock.go_to_start_of = test_context.Mock(return_value=True)
        flat_review_context_mock.go_to_end_of = test_context.Mock(return_value=True)

        context_class_mock = test_context.Mock(return_value=flat_review_context_mock)
        context_class_mock.WINDOW = "window"
        context_class_mock.LINE = "line"
        flat_review_mock.Context = context_class_mock

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_active_mode_and_object_of_interest = test_context.Mock(
            return_value=("focus_tracking", test_context.Mock())
        )
        focus_manager_instance.get_locus_of_focus = test_context.Mock(
            return_value=test_context.Mock()
        )
        focus_manager_instance.emit_region_changed = test_context.Mock()
        focus_manager_instance.FLAT_REVIEW = "flat_review"
        focus_manager_instance.FOCUS_TRACKING = "focus_tracking"
        focus_manager_mock.get_manager = test_context.Mock(return_value=focus_manager_instance)
        focus_manager_mock.FLAT_REVIEW = "flat_review"
        focus_manager_mock.FOCUS_TRACKING = "focus_tracking"

        script_manager_mock = essential_modules["orca.script_manager"]
        script_manager_instance = test_context.Mock()
        script_instance = test_context.Mock()
        script_instance.present_message = test_context.Mock()
        script_instance.present_object = test_context.Mock()
        script_instance.update_braille = test_context.Mock()
        script_instance.speak_message = test_context.Mock()

        speech_generator_mock = test_context.Mock()
        speech_generator_mock.voice = test_context.Mock(return_value="voice")
        script_instance.speech_generator = speech_generator_mock

        script_manager_instance.get_active_script = test_context.Mock(return_value=script_instance)
        script_manager_mock.get_manager = test_context.Mock(return_value=script_manager_instance)

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(return_value=controller_mock)
        dbus_service_mock.command = lambda func: func

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance.get_setting = test_context.Mock(return_value=False)
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

        settings_mock = essential_modules["orca.settings"]
        settings_mock.VERBOSITY_LEVEL_BRIEF = 0
        settings_mock.speechVerbosityLevel = 1

        keybindings_mock = essential_modules["orca.keybindings"]
        bindings_instance = test_context.Mock()
        bindings_instance.add = test_context.Mock()
        bindings_instance.remove = test_context.Mock()
        keybindings_mock.KeyBindings = test_context.Mock(return_value=bindings_instance)

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()
        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )
        input_event_mock.InputEvent = test_context.Mock()
        braille_event_mock = type("BrailleEvent", (), {})
        input_event_mock.BrailleEvent = braille_event_mock

        messages_mock = essential_modules["orca.messages"]
        messages_mock.FLAT_REVIEW_START = "Entering flat review."
        messages_mock.FLAT_REVIEW_STOP = "Leaving flat review."
        messages_mock.FLAT_REVIEW_HOME = "Top left."
        messages_mock.FLAT_REVIEW_END = "Bottom right."

        guilabels_mock = essential_modules["orca.guilabels"]
        guilabels_mock.FLAT_REVIEW = "Flat Review"

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.TOGGLE_FLAT_REVIEW = "toggleFlatReviewMode"
        cmdnames_mock.FLAT_REVIEW_HOME = "flatReviewHome"
        cmdnames_mock.FLAT_REVIEW_END = "flatReviewEnd"

        braille_mock = essential_modules["orca.braille"]
        braille_mock.refresh = test_context.Mock()
        braille_mock.present_line = test_context.Mock()
        braille_mock.present_item = test_context.Mock()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_event_synthesizer_mock = essential_modules["orca.ax_event_synthesizer"]
        ax_event_synthesizer_class_mock = test_context.Mock()
        ax_event_synthesizer_mock.AXEventSynthesizer = ax_event_synthesizer_class_mock

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.get_name = test_context.Mock(return_value="Test Object")
        ax_object_class_mock.is_dead = test_context.Mock(return_value=False)
        ax_object_mock.AXObject = ax_object_class_mock

        ax_text_mock = essential_modules["orca.ax_text"]
        ax_text_class_mock = test_context.Mock()
        ax_text_class_mock.get_text = test_context.Mock(return_value="test text")
        ax_text_mock.AXText = ax_text_class_mock

        speech_verbosity_mock = essential_modules["orca.speech_and_verbosity_manager"]
        speech_verbosity_instance = test_context.Mock()
        speech_verbosity_mock.get_manager = test_context.Mock(
            return_value=speech_verbosity_instance
        )

        braille_presenter_mock = essential_modules["orca.braille_presenter"]
        braille_presenter_instance = test_context.Mock()
        braille_presenter_instance.use_braille = test_context.Mock(return_value=True)
        braille_presenter_mock.get_presenter = test_context.Mock(
            return_value=braille_presenter_instance
        )

        platform_mock = essential_modules["orca.orca_platform"]
        platform_mock.tablesdir = "/usr/share/liblouis/tables"

        essential_modules["flat_review_context"] = flat_review_context_mock
        essential_modules["focus_manager_instance"] = focus_manager_instance
        essential_modules["script_manager_instance"] = script_manager_instance
        essential_modules["script_instance"] = script_instance
        essential_modules["controller"] = controller_mock
        essential_modules["window"] = window_mock
        essential_modules["settings_manager_instance"] = settings_manager_instance

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test FlatReviewPresenter.__init__."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        mock_controller = test_context.Mock()
        test_context.patch(
            "orca.flat_review_presenter.dbus_service.get_remote_controller",
            return_value=mock_controller
        )
        presenter = FlatReviewPresenter()

        assert presenter._context is None
        assert presenter._current_contents == ""
        assert isinstance(presenter._restrict, bool)
        assert presenter._handlers is not None
        assert presenter._desktop_bindings is not None
        assert presenter._laptop_bindings is not None
        assert presenter._gui is None

        mock_controller.register_decorated_module.assert_called_with(
            "FlatReviewPresenter", presenter
        )

    @pytest.mark.parametrize(
        "has_context,expected",
        [
            (False, False),
            (True, True),
        ],
    )
    def test_is_active(
        self, test_context: OrcaTestContext, has_context: bool, expected: bool
    ) -> None:
        """Test FlatReviewPresenter.is_active with various context states."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        presenter._context = test_context.Mock() if has_context else None
        result = presenter.is_active()
        assert result is expected

    def test_get_or_create_context_creates_new_unrestricted(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test FlatReviewPresenter.get_or_create_context creates context in unrestricted mode."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        presenter._context = None
        presenter._restrict = False
        script_mock = test_context.Mock()
        context = presenter.get_or_create_context(script_mock)

        assert context is not None
        assert presenter._context is not None
        essential_modules["orca.flat_review"].Context.assert_called_with(script_mock)
        essential_modules["focus_manager_instance"].emit_region_changed.assert_called_once()

    def test_get_or_create_context_creates_new_restricted(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test FlatReviewPresenter.get_or_create_context creates new context in restricted mode."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        presenter._context = None
        presenter._restrict = True
        script_mock = test_context.Mock()
        root_obj = test_context.Mock()
        essential_modules[
            "focus_manager_instance"
        ].get_active_mode_and_object_of_interest.return_value = ("focus_tracking", root_obj)
        context = presenter.get_or_create_context(script_mock)

        assert context is not None
        assert presenter._context is not None
        essential_modules["orca.flat_review"].Context.assert_called_with(script_mock, root=root_obj)

    def test_get_or_create_context_returns_existing(self, test_context: OrcaTestContext) -> None:
        """Test FlatReviewPresenter.get_or_create_context returns existing context."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        existing_context = test_context.Mock()
        presenter._context = existing_context
        presenter._restrict = False
        script_mock = test_context.Mock()
        context = presenter.get_or_create_context(script_mock)

        assert context is existing_context
        assert essential_modules["orca.flat_review"].Context.call_count == 0

    @pytest.mark.parametrize(
        "refresh,is_desktop,expects_setup_call",
        [
            pytest.param(False, True, False, id="no_refresh_desktop"),
            pytest.param(False, False, False, id="no_refresh_laptop"),
            pytest.param(True, True, True, id="refresh_desktop"),
        ],
    )
    def test_get_bindings(
        self,
        test_context: OrcaTestContext,
        refresh: bool,
        is_desktop: bool,
        expects_setup_call: bool,
    ) -> None:
        """Test FlatReviewPresenter.get_bindings with various refresh and desktop mode settings."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()

        if expects_setup_call:
            mock_setup = test_context.patch_object(presenter, "_setup_bindings")

        bindings = presenter.get_bindings(refresh=refresh, is_desktop=is_desktop)

        if is_desktop:
            assert bindings is presenter._desktop_bindings
        else:
            assert bindings is presenter._laptop_bindings

        if expects_setup_call:
            mock_setup.assert_called_once()

    def test_get_braille_bindings(self, test_context: OrcaTestContext) -> None:
        """Test FlatReviewPresenter.get_braille_bindings."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        braille_bindings = presenter.get_braille_bindings()
        assert isinstance(braille_bindings, dict)

    @pytest.mark.parametrize(
        "refresh",
        [
            pytest.param(False, id="cached"),
            pytest.param(True, id="refresh"),
        ],
    )
    def test_get_handlers(self, test_context: OrcaTestContext, refresh: bool) -> None:
        """Test FlatReviewPresenter.get_handlers with refresh parameter."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()

        if refresh:
            mock_setup = test_context.patch_object(presenter, "_setup_handlers")

        handlers = presenter.get_handlers(refresh=refresh)
        assert handlers is presenter._handlers

        if refresh:
            mock_setup.assert_called_once()

    @pytest.mark.parametrize(
        "has_context,provides_script,provides_event,verbose_mode",
        [
            (True, False, False, False),
            (False, True, False, False),
            (False, True, True, True),
        ],
    )
    def test_start_scenarios(
        self,
        test_context: OrcaTestContext,
        has_context: bool,
        provides_script: bool,
        provides_event: bool,
        verbose_mode: bool,
    ) -> None:
        """Test FlatReviewPresenter.start under different scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        presenter._context = test_context.Mock() if has_context else None
        script_mock = test_context.Mock() if provides_script else None
        event_mock = test_context.Mock() if provides_event else None
        if verbose_mode:
            settings_mock = essential_modules["orca.settings"]
            settings_mock.speechVerbosityLevel = 1
        presenter.start(script=script_mock, event=event_mock)
        if has_context:
            essential_modules["orca.flat_review"].Context.assert_not_called()
        else:
            assert presenter._context is not None
            essential_modules["orca.flat_review"].Context.assert_called_once()

    @pytest.mark.parametrize("is_active", [False, True])
    def test_quit_scenarios(self, test_context: OrcaTestContext, is_active: bool) -> None:
        """Test FlatReviewPresenter.quit when active or inactive."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        presenter._context = test_context.Mock() if is_active else None
        if is_active:
            focus_obj = test_context.Mock()
            essential_modules["focus_manager_instance"].get_locus_of_focus.return_value = focus_obj
        presenter.quit()
        if is_active:
            assert presenter._context is None
            essential_modules["focus_manager_instance"].emit_region_changed.assert_called_with(
                focus_obj, mode=essential_modules["focus_manager_instance"].FOCUS_TRACKING
            )
        else:
            essential_modules["focus_manager_instance"].emit_region_changed.assert_not_called()

    def test_toggle_flat_review_mode_enter(self, test_context: OrcaTestContext) -> None:
        """Test FlatReviewPresenter.toggle_flat_review_mode enters flat review."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        presenter._context = None
        script_mock = test_context.Mock()
        event_mock = test_context.Mock()
        mock_start = test_context.patch_object(presenter, "start")
        presenter.toggle_flat_review_mode(script_mock, event_mock)
        mock_start.assert_called_once_with(script_mock, event_mock)

    def test_toggle_flat_review_mode_exit(self, test_context: OrcaTestContext) -> None:
        """Test FlatReviewPresenter.toggle_flat_review_mode exits flat review."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        presenter._context = test_context.Mock()
        script_mock = test_context.Mock()
        event_mock = test_context.Mock()
        mock_quit = test_context.patch_object(presenter, "quit")
        presenter.toggle_flat_review_mode(script_mock, event_mock)
        mock_quit.assert_called_once_with(script_mock, event_mock)

    @pytest.mark.parametrize(
        "method_name,context_method,navigation_target",
        [
            ("go_home", "go_to_start_of", "WINDOW"),
            ("go_end", "go_to_end_of", "WINDOW"),
        ],
    )
    def test_navigation_methods(
        self,
        test_context: OrcaTestContext,
        method_name: str,
        context_method: str,
        navigation_target: str,
    ) -> None:
        """Test FlatReviewPresenter navigation methods (go_home, go_end)."""
        essential_modules = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        script_mock = test_context.Mock()
        event_mock = test_context.Mock()
        context_mock = test_context.Mock()
        presenter._context = context_mock
        mock_present_line = test_context.patch_object(presenter, "present_line")
        method = getattr(presenter, method_name)
        result = method(script_mock, event_mock)
        getattr(context_mock, context_method).assert_called_once_with(
            getattr(essential_modules["orca.flat_review"].Context, navigation_target)
        )
        mock_present_line.assert_called_once_with(script_mock, event_mock)
        assert result is True

    def test_go_bottom_left(self, test_context: OrcaTestContext) -> None:
        """Test FlatReviewPresenter.go_bottom_left."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        script_mock = test_context.Mock()
        event_mock = test_context.Mock()

        context_mock = test_context.Mock()
        presenter._context = context_mock
        mock_present_line = test_context.patch_object(presenter, "present_line")

        result = presenter.go_bottom_left(script_mock, event_mock)

        assert context_mock.go_to_end_of.call_count == 1
        context_mock.go_to_end_of.assert_called_with(
            essential_modules["orca.flat_review"].Context.WINDOW
        )
        context_mock.go_to_start_of.assert_called_once_with(
            essential_modules["orca.flat_review"].Context.LINE
        )
        mock_present_line.assert_called_once_with(script_mock, event_mock)
        assert result is True

    @pytest.mark.parametrize("navigation_succeeds", [True, False])
    def test_go_previous_line_scenarios(
        self, test_context: OrcaTestContext, navigation_succeeds: bool
    ) -> None:
        """Test FlatReviewPresenter.go_previous_line with success and failure."""
        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        script_mock = test_context.Mock()
        event_mock = test_context.Mock()
        context_mock = test_context.Mock()
        context_mock.go_previous_line.return_value = navigation_succeeds
        presenter._context = context_mock
        mock_present_line = test_context.patch_object(presenter, "present_line")
        result = presenter.go_previous_line(script_mock, event_mock)
        context_mock.go_previous_line.assert_called_once()
        if navigation_succeeds:
            mock_present_line.assert_called_once_with(script_mock, event_mock)
        else:
            mock_present_line.assert_not_called()
        assert result is True

    def test_get_presenter_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter function returns singleton instance."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import get_presenter

        presenter1 = get_presenter()
        presenter2 = get_presenter()
        assert presenter1 is presenter2
        assert presenter1 is not None

    def test_full_navigation_workflow(self, test_context: OrcaTestContext) -> None:
        """Test complete flat review navigation workflow."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        script_mock = test_context.Mock()
        event_mock = test_context.Mock()

        presenter.start(script_mock, event_mock)
        assert presenter.is_active()

        presenter.quit(script_mock, event_mock)
        assert not presenter.is_active()

    def test_restricted_vs_unrestricted_context_creation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test context creation in both restricted and unrestricted modes."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter_unrestricted = FlatReviewPresenter()
        presenter_unrestricted._restrict = False
        presenter_unrestricted._context = None
        script_mock = test_context.Mock()
        presenter_unrestricted.get_or_create_context(script_mock)
        essential_modules["orca.flat_review"].Context.assert_called_with(script_mock)

        presenter_restricted = FlatReviewPresenter()
        presenter_restricted._restrict = True
        presenter_restricted._context = None
        root_obj = test_context.Mock()
        essential_modules[
            "focus_manager_instance"
        ].get_active_mode_and_object_of_interest.return_value = ("focus_tracking", root_obj)
        presenter_restricted.get_or_create_context(script_mock)

        assert essential_modules["orca.flat_review"].Context.call_count >= 2

    def test_braille_integration(self, test_context: OrcaTestContext) -> None:
        """Test flat review integration with braille system."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        braille_bindings = presenter.get_braille_bindings()

        assert isinstance(braille_bindings, dict)

    def test_keyboard_bindings_setup(self, test_context: OrcaTestContext) -> None:
        """Test keyboard bindings setup for both desktop and laptop modes."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()

        desktop_bindings = presenter.get_bindings(refresh=False, is_desktop=True)
        assert desktop_bindings is presenter._desktop_bindings

        laptop_bindings = presenter.get_bindings(refresh=False, is_desktop=False)
        assert laptop_bindings is presenter._laptop_bindings

        assert desktop_bindings is not None
        assert laptop_bindings is not None

    def test_dbus_command_registration(self, test_context: OrcaTestContext) -> None:
        """Test D-Bus command registration during initialization."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        mock_controller = test_context.Mock()
        test_context.patch(
            "orca.flat_review_presenter.dbus_service.get_remote_controller",
            return_value=mock_controller
        )
        presenter = FlatReviewPresenter()

        mock_controller.register_decorated_module.assert_called_with(
            "FlatReviewPresenter", presenter
        )

    def test_focus_manager_integration(self, test_context: OrcaTestContext) -> None:
        """Test integration with focus manager for region changes."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        focus_manager_instance = essential_modules["focus_manager_instance"]

        script_mock = test_context.Mock()
        presenter.get_or_create_context(script_mock)
        focus_manager_instance.emit_region_changed.assert_called()

        presenter._context = test_context.Mock()
        focus_obj = test_context.Mock()
        focus_manager_instance.get_locus_of_focus.return_value = focus_obj
        presenter.quit()
        focus_manager_instance.emit_region_changed.assert_called_with(
            focus_obj, mode=focus_manager_instance.FOCUS_TRACKING
        )

    def test_error_handling_navigation_failure(self, test_context: OrcaTestContext) -> None:
        """Test error handling when navigation operations fail."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        context_mock = test_context.Mock()
        context_mock.go_next_line.return_value = False
        presenter._context = context_mock
        script_mock = test_context.Mock()
        event_mock = test_context.Mock()

        presenter.go_next_line(script_mock, event_mock)
        context_mock.go_next_line.assert_called_once()

    def test_gui_lifecycle_management(self, test_context: OrcaTestContext) -> None:
        """Test GUI-related methods exist."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()

        assert hasattr(presenter, "show_contents")
        assert callable(getattr(presenter, "show_contents", None))

    def test_context_caching_behavior(self, test_context: OrcaTestContext) -> None:
        """Test context caching and reuse behavior."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.flat_review_presenter import FlatReviewPresenter

        presenter = FlatReviewPresenter()
        script_mock = test_context.Mock()

        essential_modules["orca.flat_review"].Context.reset_mock()

        context1 = presenter.get_or_create_context(script_mock)
        assert context1 is not None

        context2 = presenter.get_or_create_context(script_mock)
        assert context1 is context2

        assert essential_modules["orca.flat_review"].Context.call_count == 1

        presenter._context = None
        context3 = presenter.get_or_create_context(script_mock)
        assert context3 is not None

        assert essential_modules["orca.flat_review"].Context.call_count == 2
