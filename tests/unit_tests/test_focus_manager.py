# Unit tests for focus_manager.py methods.
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

"""Unit tests for focus_manager.py methods."""

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
class TestFocusManager:
    """Test FocusManager class methods."""

    def _setup_locus_of_focus_ax_mocks(
        self, test_context, mock_app=None, is_dead=False, cell_coords=(-1, -1), caret_offset=-1
    ):
        """Set up common AX object mocks for set_locus_of_focus testing scenarios.

        Returns:
            tuple: (mock_get_cell_coordinates, mock_get_caret_offset, mock_update_cached_text)
        """

        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_table import AXTable
        from orca.ax_text import AXText

        test_context.patch_object(AXObject, "clear_cache", new=test_context.Mock())
        test_context.patch_object(
            AXObject, "is_dead", return_value=is_dead
        )
        test_context.patch_object(
            AXObject, "is_valid", side_effect=lambda obj: obj is not None
        )

        if mock_app is not None:
            test_context.patch_object(
                AXUtilities, "get_application", return_value=mock_app
            )
        else:
            test_context.patch_object(AXUtilities, "get_application", new=test_context.Mock())

        test_context.patch_object(
            AXUtilities, "save_object_info_for_events", new=test_context.Mock()
        )

        mock_get_cell_coordinates = test_context.Mock(return_value=cell_coords)
        test_context.patch_object(AXTable, "get_cell_coordinates", new=mock_get_cell_coordinates)

        mock_get_caret_offset = test_context.Mock(return_value=caret_offset)
        test_context.patch_object(AXText, "get_caret_offset", new=mock_get_caret_offset)

        mock_update_cached_text = test_context.Mock()
        test_context.patch_object(
            AXText, "update_cached_selected_text", new=mock_update_cached_text
        )

        return mock_get_cell_coordinates, mock_get_caret_offset, mock_update_cached_text

    def _setup_dependencies(self, test_context) -> dict[str, MagicMock]:
        """Set up mocks for focus_manager dependencies."""

        all_modules = [
            "orca.debug",
            "orca.messages",
            "orca.input_event",
            "orca.settings",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.ax_object",
            "orca.settings_manager",
            "orca.dbus_service",
            "orca.script_manager",
            "orca.orca_i18n",
            "orca.guilabels",
            "orca.text_attribute_names",
            "orca.braille",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities",
        ]
        essential_modules = test_context._setup_essential_modules(all_modules)

        i18n_mock = essential_modules["orca.orca_i18n"]
        i18n_mock._ = lambda x: x  # Identity function for translations
        i18n_mock.C_ = lambda c, x: x  # Context-aware translations
        i18n_mock.ngettext = lambda s, p, n: s if n == 1 else p  # Plural forms

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_FINEST = 2
        debug_mock.LEVEL_SEVERE = 0
        debug_mock.print_message = test_context.Mock()
        debug_mock.println = test_context.Mock()

        keybindings_mock = essential_modules["orca.keybindings"]
        bindings_instance = test_context.Mock()
        bindings_instance.is_empty = test_context.Mock(return_value=True)
        bindings_instance.add = test_context.Mock()
        keybindings_mock.KeyBindings = test_context.Mock(return_value=bindings_instance)
        keybindings_mock.KeyBinding = test_context.Mock(
            return_value=test_context.Mock()
        )

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = test_context.Mock()
        manager_instance.get_setting = test_context.Mock(return_value=True)
        manager_instance.set_setting = test_context.Mock(return_value=True)
        settings_manager_mock.get_manager = test_context.Mock(return_value=manager_instance)

        braille_mock = essential_modules["orca.braille"]
        braille_mock.setBrlapiPriority = test_context.Mock()
        braille_mock.BRLAPI_PRIORITY_HIGH = 1

        script_manager_mock = essential_modules["orca.script_manager"]
        script_mgr_instance = test_context.Mock()
        script_instance = test_context.Mock()
        script_instance.locus_of_focus_changed = test_context.Mock()
        script_mgr_instance.get_active_script = test_context.Mock(
            return_value=script_instance
        )
        script_mgr_instance.get_script = test_context.Mock(return_value=script_instance)
        script_mgr_instance.set_active_script = test_context.Mock()
        script_manager_mock.get_manager = test_context.Mock(return_value=script_mgr_instance)

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject = test_context.Mock()
        ax_object_mock.AXObject.is_dead = test_context.Mock(return_value=False)
        ax_object_mock.AXObject.is_valid = test_context.Mock(return_value=True)
        ax_object_mock.AXObject.clear_cache = test_context.Mock()
        ax_object_mock.AXObject.is_ancestor = test_context.Mock(return_value=False)
        ax_object_mock.AXObject.has_broken_ancestry = test_context.Mock(return_value=False)

        ax_table_mock = essential_modules["orca.ax_table"]
        ax_table_mock.AXTable = test_context.Mock()
        ax_table_mock.AXTable.get_cell_coordinates = test_context.Mock(return_value=(-1, -1))

        ax_text_mock = essential_modules["orca.ax_text"]
        ax_text_mock.AXText = test_context.Mock()
        ax_text_mock.AXText.get_caret_offset = test_context.Mock(return_value=-1)
        ax_text_mock.AXText.update_cached_selected_text = test_context.Mock()

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.AXUtilities = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_table_cell = test_context.Mock(return_value=False)
        ax_utilities_mock.AXUtilities.get_application = test_context.Mock()
        ax_utilities_mock.AXUtilities.save_object_info_for_events = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_active = test_context.Mock(return_value=True)
        ax_utilities_mock.AXUtilities.get_focused_object = test_context.Mock()

        return essential_modules

    def test_init(self, test_context) -> None:
        """Test FocusManager.__init__."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        assert manager._focus is None
        assert manager._window is None
        assert manager._object_of_interest is None
        assert manager._active_mode is None

    def test_clear_state(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.clear_state."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        test_context.patch_object(
            manager, "_focus", new=test_context.Mock(spec=Atspi.Accessible)
        )
        test_context.patch_object(
            manager, "_window", new=test_context.Mock(spec=Atspi.Accessible)
        )
        test_context.patch_object(
            manager, "_object_of_interest", new=test_context.Mock(spec=Atspi.Accessible)
        )
        manager._active_mode = "focus-tracking"

        manager.clear_state()
        assert manager._focus is None
        assert manager._window is None
        assert manager._object_of_interest is None
        assert manager._active_mode is None
        test_context.patch_object(
            manager, "_focus", new=test_context.Mock(spec=Atspi.Accessible)
        )
        manager.clear_state("test reason")
        assert manager._focus is None

    def test_find_focused_object(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.find_focused_object."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager
        from orca.ax_utilities import AXUtilities

        manager = FocusManager()
        mock_window = test_context.Mock(spec=Atspi.Accessible)
        mock_focused = test_context.Mock(spec=Atspi.Accessible)
        manager._window = mock_window
        mock_get_focused = test_context.Mock(return_value=mock_focused)
        test_context.patch_object(AXUtilities, "get_focused_object", new=mock_get_focused)
        result = manager.find_focused_object()
        assert result == mock_focused
        mock_get_focused.assert_called_once_with(mock_window)

    @pytest.mark.parametrize(
        "focus, window, expected",
        [
            pytest.param(None, None, True, id="both_none"),
            pytest.param(None, "window", False, id="focus_none_window_set"),
            pytest.param("focus", None, False, id="focus_set_window_none"),
            pytest.param("focus", "window", False, id="both_set"),
        ],
    )
    def test_focus_and_window_are_unknown(self, test_context, focus, window, expected) -> None:
        """Test FocusManager.focus_and_window_are_unknown."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        focus_obj = test_context.Mock(spec=Atspi.Accessible) if focus else None
        window_obj = test_context.Mock(spec=Atspi.Accessible) if window else None
        test_context.patch_object(manager, "_focus", new=focus_obj)
        test_context.patch_object(manager, "_window", new=window_obj)
        result = manager.focus_and_window_are_unknown()
        assert result == expected

    @pytest.mark.parametrize(
        "focus_obj,focus_is_dead,expected",
        [
            pytest.param("mock_focus", True, True, id="focus_is_dead"),
            pytest.param("mock_focus", False, False, id="focus_is_alive"),
            pytest.param(None, False, False, id="no_focus_set"),
        ],
    )
    def test_focus_is_dead(self, test_context, focus_obj, focus_is_dead, expected) -> None:
        """Test FocusManager.focus_is_dead with various focus states."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()

        if focus_obj == "mock_focus":
            mock_focus = test_context.Mock(spec=Atspi.Accessible)
            manager._focus = mock_focus
            expected_call_arg = mock_focus
        else:
            manager._focus = None
            expected_call_arg = None

        from orca.ax_object import AXObject

        mock_is_dead = test_context.Mock(return_value=focus_is_dead)
        test_context.patch_object(AXObject, "is_dead", new=mock_is_dead)

        result = manager.focus_is_dead()
        assert result == expected
        mock_is_dead.assert_called_once_with(expected_call_arg)

    @pytest.mark.parametrize(
        "focus, window, expected",
        [
            pytest.param(None, "window", False, id="no_focus"),
            pytest.param("same_obj", "same_obj", True, id="focus_equals_window"),
            pytest.param("focus_obj", "window_obj", False, id="focus_not_window"),
        ],
    )
    def test_focus_is_active_window(self, test_context, focus, window, expected) -> None:
        """Test FocusManager.focus_is_active_window."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        if focus == "same_obj" and window == "same_obj":
            same_obj = test_context.Mock(spec=Atspi.Accessible)
            manager._focus = same_obj
            manager._window = same_obj
        else:
            focus_obj = test_context.Mock(spec=Atspi.Accessible) if focus else None
            window_obj = test_context.Mock(spec=Atspi.Accessible) if window else None
            test_context.patch_object(manager, "_focus", new=focus_obj)
            test_context.patch_object(manager, "_window", new=window_obj)
        result = manager.focus_is_active_window()
        assert result == expected

    @pytest.mark.parametrize(
        "focus, window, is_ancestor, expected",
        [
            pytest.param(None, "window", False, False, id="no_focus"),
            pytest.param("focus", "window", True, True, id="focus_in_window"),
            pytest.param("focus", "window", False, False, id="focus_not_in_window"),
        ],
    )
    def test_focus_is_in_active_window(
        self, test_context, focus, window, is_ancestor, expected
    ) -> None:
        """Test FocusManager.focus_is_in_active_window."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        focus_obj = test_context.Mock(spec=Atspi.Accessible) if focus else None
        window_obj = test_context.Mock(spec=Atspi.Accessible) if window else None
        test_context.patch_object(manager, "_focus", new=focus_obj)
        test_context.patch_object(manager, "_window", new=window_obj)
        from orca.ax_object import AXObject

        mock_is_ancestor = test_context.Mock(return_value=is_ancestor)
        test_context.patch_object(AXObject, "is_ancestor", new=mock_is_ancestor)
        result = manager.focus_is_in_active_window()
        assert result == expected
        if focus and window:
            mock_is_ancestor.assert_called_once_with(manager._focus, manager._window)

    @pytest.mark.parametrize(
        "start_offset, end_offset, mode, use_null_object",
        [
            pytest.param(None, None, None, False, id="all_defaults"),
            pytest.param(5, None, None, False, id="start_only"),
            pytest.param(5, 10, None, False, id="start_and_end"),
            pytest.param(5, 10, "caret-tracking", False, id="all_specified"),
            pytest.param(None, None, None, True, id="null_object"),
        ],
    )
    def test_emit_region_changed_scenarios(  # pylint: disable=too-many-arguments
        self, test_context, start_offset, end_offset, mode, use_null_object
    ) -> None:
        """Test FocusManager.emit_region_changed with various scenarios."""
        essential_modules = self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager, FOCUS_TRACKING, FLAT_REVIEW

        manager = FocusManager()

        if use_null_object:
            manager.emit_region_changed(None)
            assert manager._object_of_interest is None
        else:
            mock_obj = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(mock_obj, "emit", new=test_context.Mock())
            expected_start = start_offset if start_offset is not None else 0
            expected_end = end_offset if end_offset is not None else expected_start
            expected_mode = mode if mode is not None else FOCUS_TRACKING

            manager.emit_region_changed(mock_obj, start_offset, end_offset, mode)
            mock_obj.emit.assert_any_call("mode-changed::" + expected_mode, 1, "")
            mock_obj.emit.assert_any_call("region-changed", expected_start, expected_end)
            assert manager._active_mode == expected_mode
            assert manager._object_of_interest == mock_obj

            manager.emit_region_changed(mock_obj, mode=FLAT_REVIEW)
            braille_mock = essential_modules["orca.braille"]
            braille_mock.setBrlapiPriority.assert_called_with(braille_mock.BRLAPI_PRIORITY_HIGH)

            manager.emit_region_changed(mock_obj, mode=FOCUS_TRACKING)
            braille_mock.setBrlapiPriority.assert_called_with()

    @pytest.mark.parametrize(
        "active_mode, expected",
        [
            pytest.param("say-all", True, id="in_say_all"),
            pytest.param("focus-tracking", False, id="not_in_say_all"),
            pytest.param(None, False, id="no_mode"),
        ],
    )
    def test_in_say_all(self, test_context, active_mode, expected) -> None:
        """Test FocusManager.in_say_all."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        manager._active_mode = active_mode
        result = manager.in_say_all()
        assert result == expected

    def test_get_active_mode_and_object_of_interest(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.get_active_mode_and_object_of_interest."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mode = "caret-tracking"
        manager._active_mode = mode
        manager._object_of_interest = mock_obj
        result_mode, result_obj = manager.get_active_mode_and_object_of_interest()
        assert result_mode == mode
        assert result_obj == mock_obj

    def test_get_locus_of_focus(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.get_locus_of_focus."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        manager._focus = mock_focus
        result = manager.get_locus_of_focus()
        assert result == mock_focus

    @pytest.mark.parametrize(
        "force, obj_equals_current_focus, notify_script",
        [
            pytest.param(True, True, True, id="force_same_object"),
            pytest.param(False, True, True, id="no_force_same_object"),
            pytest.param(False, False, True, id="different_object"),
            pytest.param(False, False, False, id="different_object_no_notify"),
        ],
    )
    def test_set_locus_of_focus(
        self, test_context, force, obj_equals_current_focus, notify_script
    ) -> None:
        """Test FocusManager.set_locus_of_focus."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        if obj_equals_current_focus:
            manager._focus = mock_obj
        else:
            test_context.patch_object(
                manager, "_focus", new=test_context.Mock(spec=Atspi.Accessible)
            )
        script_manager_mock = essential_modules["orca.script_manager"]
        manager_instance = script_manager_mock.get_manager.return_value
        script_instance = manager_instance.get_active_script.return_value
        self._setup_locus_of_focus_ax_mocks(test_context, mock_app=mock_app)
        mock_emit = test_context.Mock()
        test_context.patch_object(manager, "emit_region_changed", new=mock_emit)
        manager.set_locus_of_focus(mock_event, mock_obj, notify_script, force)
        if not force and obj_equals_current_focus:
            mock_emit.assert_not_called()
        else:
            assert manager._focus == mock_obj
            mock_emit.assert_called_once()
            if notify_script:
                script_instance.locus_of_focus_changed.assert_called_once()

    def test_set_locus_of_focus_null_object(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.set_locus_of_focus with null object."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager
        from orca.ax_object import AXObject

        test_context.patch_object(
            AXObject, "is_valid", side_effect=lambda obj: obj is not None
        )
        manager = FocusManager()
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        manager._focus = mock_focus
        manager.set_locus_of_focus(None, None)
        assert manager._focus is None

    def test_set_locus_of_focus_dead_object(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.set_locus_of_focus with dead object."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        self._setup_locus_of_focus_ax_mocks(test_context, is_dead=True)
        manager = FocusManager()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        old_focus = test_context.Mock(spec=Atspi.Accessible)
        manager._focus = old_focus
        manager.set_locus_of_focus(None, mock_obj)

        # Focus should not change since object is dead
        assert manager._focus == old_focus

    def test_active_window_is_active(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.active_window_is_active."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_window = test_context.Mock(spec=Atspi.Accessible)
        manager._window = mock_window
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_clear = test_context.Mock()
        test_context.patch_object(AXObject, "clear_cache", new=mock_clear)
        mock_is_active = test_context.Mock(return_value=True)
        test_context.patch_object(AXUtilities, "is_active", new=mock_is_active)
        result = manager.active_window_is_active()
        assert result is True
        mock_clear.assert_called_once_with(
            mock_window, False, "Ensuring the active window is really active."
        )
        mock_is_active.assert_called_once_with(mock_window)

    def test_get_active_window(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.get_active_window."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_window = test_context.Mock(spec=Atspi.Accessible)
        manager._window = mock_window
        result = manager.get_active_window()
        assert result == mock_window

    @pytest.mark.parametrize(
        "frame_equals_current, set_window_as_focus, focus_is_in_window, has_broken_ancestry",
        [
            pytest.param(True, False, True, False, id="same_window"),
            pytest.param(False, True, False, False, id="set_as_focus"),
            pytest.param(False, False, False, False, id="focus_not_in_window"),
            pytest.param(False, False, False, True, id="focus_has_broken_ancestry"),
        ],
    )
    def test_set_active_window(
        self,
        test_context,
        frame_equals_current,
        set_window_as_focus,
        focus_is_in_window,
        has_broken_ancestry,
    ) -> None:
        """Test FocusManager.set_active_window."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_frame = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        if frame_equals_current:
            manager._window = mock_frame
        else:
            test_context.patch_object(
                manager, "_window", new=test_context.Mock(spec=Atspi.Accessible)
            )
        manager._focus = mock_focus
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_set_focus = test_context.Mock()
        test_context.patch_object(manager, "set_locus_of_focus", new=mock_set_focus)
        test_context.patch_object(
            manager, "focus_is_active_window", return_value=focus_is_in_window
        )
        test_context.patch_object(
            manager, "focus_is_in_active_window", return_value=focus_is_in_window
        )
        test_context.patch_object(
            AXObject, "has_broken_ancestry", return_value=has_broken_ancestry
        )
        test_context.patch_object(
            AXUtilities, "get_application", return_value=mock_app
        )
        manager.set_active_window(mock_frame, mock_app, set_window_as_focus, False)
        if not frame_equals_current:
            assert manager._window == mock_frame
        if set_window_as_focus:
            mock_set_focus.assert_called_with(None, mock_frame, False)
        elif not focus_is_in_window and not has_broken_ancestry:
            mock_set_focus.assert_called_with(None, mock_frame, notify_script=True)

    def test_set_active_window_null_frame(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.set_active_window with null frame."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        manager._focus = mock_focus
        manager.set_active_window(None)
        assert manager._window is None

    def test_get_manager(self, test_context: OrcaTestContext) -> None:
        """Test focus_manager.get_manager."""

        self._setup_dependencies(test_context)
        from orca import focus_manager

        manager1 = focus_manager.get_manager()
        manager2 = focus_manager.get_manager()
        assert manager1 is manager2
        assert isinstance(manager1, focus_manager.FocusManager)

    def test_set_locus_of_focus_table_cell_coordinates(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.set_locus_of_focus saves table cell coordinates."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        mock_get_cell_coordinates = self._setup_locus_of_focus_ax_mocks(
            test_context, cell_coords=(5, 3)
        )[0]
        manager = FocusManager()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        manager.set_locus_of_focus(None, mock_obj)

        mock_get_cell_coordinates.assert_called_once_with(mock_obj, find_cell=True)
        assert manager.get_last_cell_coordinates() == (5, 3)

    def test_set_locus_of_focus_text_cursor_position(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.set_locus_of_focus saves text cursor position."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        mocks = self._setup_locus_of_focus_ax_mocks(test_context, caret_offset=42)
        mock_get_caret_offset = mocks[1]
        mock_update_cached_text = mocks[2]
        manager = FocusManager()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        manager.set_locus_of_focus(None, mock_obj)

        mock_get_caret_offset.assert_called_once_with(mock_obj)
        mock_update_cached_text.assert_called_once_with(mock_obj)
        obj, offset = manager.get_last_cursor_position()
        assert obj == mock_obj
        assert offset == 42

    def test_set_locus_of_focus_none_object_coordinates(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test FocusManager.set_locus_of_focus handles None object coordinates properly."""

        self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager
        from orca.ax_table import AXTable
        from orca.ax_text import AXText
        from orca.ax_object import AXObject

        test_context.patch_object(
            AXObject, "is_valid", side_effect=lambda obj: obj is not None
        )
        manager = FocusManager()

        mock_get_cell_coordinates = test_context.Mock()
        test_context.patch_object(AXTable, "get_cell_coordinates", new=mock_get_cell_coordinates)
        mock_get_caret_offset = test_context.Mock()
        test_context.patch_object(AXText, "get_caret_offset", new=mock_get_caret_offset)
        mock_update_cached_selected_text = test_context.Mock()
        test_context.patch_object(
            AXText, "update_cached_selected_text", new=mock_update_cached_selected_text
        )
        manager.set_locus_of_focus(None, None)

        mock_get_cell_coordinates.assert_not_called()
        mock_get_caret_offset.assert_not_called()
        mock_update_cached_selected_text.assert_not_called()

        assert manager.get_last_cell_coordinates() == (-1, -1)

    @pytest.mark.parametrize(
        "method_name,attribute_name,test_offset",
        [
            pytest.param(
                "get_penultimate_cursor_position",
                "_penultimate_cursor_position",
                42,
                id="penultimate",
            ),
            pytest.param("get_last_cursor_position", "_last_cursor_position", 123, id="last"),
        ],
    )
    def test_cursor_position_debug_logging(
        self, test_context: OrcaTestContext, method_name, attribute_name, test_offset
    ) -> None:
        """Test cursor position methods log debug information."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        focus_manager = FocusManager()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        setattr(focus_manager, attribute_name, (mock_obj, test_offset))

        method = getattr(focus_manager, method_name)
        obj, offset = method()

        assert obj is mock_obj
        assert offset == test_offset
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_set_locus_of_focus_null_object_with_debug(self, test_context: OrcaTestContext) -> None:
        """Test FocusManager.set_locus_of_focus with null object logs debug message."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        focus_manager = FocusManager()
        initial_focus = test_context.Mock(spec=Atspi.Accessible)
        focus_manager._focus = initial_focus
        focus_manager.set_locus_of_focus(None, None)

        assert focus_manager._focus is None
        essential_modules["orca.debug"].print_message.assert_called()

    def test_set_locus_of_focus_with_event_and_force_flag(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test FocusManager.set_locus_of_focus with event and force flag."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.focus_manager import FocusManager

        focus_manager = FocusManager()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event = test_context.Mock()
        focus_manager.set_locus_of_focus(mock_event, mock_obj, force=True)
        essential_modules["orca.debug"].print_tokens.assert_called()
