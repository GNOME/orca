# Unit tests for focus_manager.py FocusManager class methods.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=unused-argument
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-statements
# pylint: disable=unused-variable

"""Unit tests for focus_manager.py FocusManager class methods."""

from __future__ import annotations

import sys
from unittest.mock import Mock, patch

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi


@pytest.mark.unit
class TestFocusManager:
    """Test FocusManager class methods."""

    @pytest.fixture
    def mock_focus_manager_deps(self, monkeypatch):
        """Mock all dependencies needed for focus_manager imports."""

        from .conftest import clean_module_cache

        modules_to_clean = [
            "orca.focus_manager",
            "orca.braille",
            "orca.script_manager",
            "orca.ax_object",
            "orca.ax_utilities",
            "orca.debugging_tools_manager",
            "orca.orca",
            "orca.scripts",
            "orca.scripts.default",
            "orca.scripts.apps",
            "orca.scripts.sleepmode",
            "orca.scripts.toolkits",
            "orca.keynames",
            "orca.orca_i18n",
        ]
        for module in modules_to_clean:
            clean_module_cache(module)

        debug_mock = Mock()
        debug_mock.print_message = Mock()
        debug_mock.print_tokens = Mock()
        debug_mock.LEVEL_INFO = 1
        debug_mock.debugFile = None

        braille_mock = Mock()
        braille_mock.setBrlapiPriority = Mock()
        braille_mock.BRLAPI_PRIORITY_HIGH = 1

        script_manager_mock = Mock()
        manager_instance = Mock()
        script_instance = Mock()
        script_instance.app = True
        script_instance.locus_of_focus_changed = Mock()
        manager_instance.get_active_script = Mock(return_value=script_instance)
        manager_instance.get_script = Mock(return_value=script_instance)
        manager_instance.set_active_script = Mock()
        script_manager_mock.get_manager = Mock(return_value=manager_instance)

        monkeypatch.setitem(sys.modules, "orca.debug", debug_mock)
        monkeypatch.setitem(sys.modules, "orca.braille", braille_mock)
        monkeypatch.setitem(sys.modules, "orca.script_manager", script_manager_mock)

        monkeypatch.setitem(sys.modules, "orca.debugging_tools_manager", Mock())
        monkeypatch.setitem(sys.modules, "orca.orca", Mock())
        monkeypatch.setitem(sys.modules, "orca.scripts", Mock())
        monkeypatch.setitem(sys.modules, "orca.scripts.default", Mock())
        monkeypatch.setitem(sys.modules, "orca.scripts.apps", Mock())
        monkeypatch.setitem(sys.modules, "orca.scripts.sleepmode", Mock())
        monkeypatch.setitem(sys.modules, "orca.scripts.toolkits", Mock())
        monkeypatch.setitem(sys.modules, "orca.keynames", Mock())
        monkeypatch.setitem(sys.modules, "orca.orca_i18n", Mock())
        monkeypatch.setitem(sys.modules, "orca.orca_platform", Mock())
        monkeypatch.setitem(sys.modules, "orca.messages", Mock())
        monkeypatch.setitem(sys.modules, "orca.ax_component", Mock())
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_role", Mock())
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_state", Mock())
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_application", Mock())
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_relation", Mock())
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_event", Mock())

        from orca.ax_utilities import AXUtilities
        from orca.ax_object import AXObject

        AXUtilities.get_focused_object = Mock()
        AXUtilities.is_table_cell = Mock(return_value=False)
        AXUtilities.get_application = Mock()
        AXUtilities.is_active = Mock(return_value=True)

        AXObject.clear_cache = Mock()
        AXObject.is_dead = Mock(return_value=False)
        AXObject.is_valid = Mock(side_effect=lambda obj: obj is not None)
        AXObject.is_ancestor = Mock(return_value=False)
        AXObject.has_broken_ancestry = Mock(return_value=False)
        AXObject._get_toolkit_name = Mock(return_value="gtk")

        # Mock functions that can't handle Mock objects being passed to GObject methods
        from orca.ax_table import AXTable
        from orca.ax_text import AXText

        AXTable.get_cell_coordinates = Mock(return_value=(-1, -1))
        AXText.get_caret_offset = Mock(return_value=-1)
        AXText.update_cached_selected_text = Mock()
        AXUtilities.save_object_info_for_events = Mock()

        return {
            "debug": debug_mock,
            "braille": braille_mock,
            "script_manager": script_manager_mock,
            "manager_instance": manager_instance,
            "script_instance": script_instance,
        }

    @pytest.mark.parametrize(
        "focus, window, object_of_interest, active_mode",
        [
            pytest.param(None, None, None, None, id="all_none"),
            pytest.param("focus_obj", "window_obj", "interest_obj", "caret-tracking", id="all_set"),
        ],
    )
    def test_init(self, mock_focus_manager_deps, focus, window, object_of_interest, active_mode):
        """Test FocusManager.__init__."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        assert manager._focus is None
        assert manager._window is None
        assert manager._object_of_interest is None
        assert manager._active_mode is None

    def test_clear_state(self, mock_focus_manager_deps):
        """Test FocusManager.clear_state."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()

        manager._focus = Mock(spec=Atspi.Accessible)
        manager._window = Mock(spec=Atspi.Accessible)
        manager._object_of_interest = Mock(spec=Atspi.Accessible)
        manager._active_mode = "focus-tracking"

        # Scenario: Clear state without reason
        manager.clear_state()
        assert manager._focus is None
        assert manager._window is None
        assert manager._object_of_interest is None
        assert manager._active_mode is None

        # Scenario: Clear state with reason
        manager._focus = Mock(spec=Atspi.Accessible)
        manager.clear_state("test reason")
        assert manager._focus is None

    def test_find_focused_object(self, mock_focus_manager_deps, monkeypatch):
        """Test FocusManager.find_focused_object."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_window = Mock(spec=Atspi.Accessible)
        mock_focused = Mock(spec=Atspi.Accessible)
        manager._window = mock_window

        with patch(
            "orca.ax_utilities.AXUtilities.get_focused_object", return_value=mock_focused
        ) as mock_get_focused:
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
    def test_focus_and_window_are_unknown(self, mock_focus_manager_deps, focus, window, expected):
        """Test FocusManager.focus_and_window_are_unknown."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        manager._focus = Mock(spec=Atspi.Accessible) if focus else None
        manager._window = Mock(spec=Atspi.Accessible) if window else None

        result = manager.focus_and_window_are_unknown()
        assert result == expected

    @pytest.mark.parametrize(
        "focus_is_dead, expected",
        [
            pytest.param(True, True, id="focus_is_dead"),
            pytest.param(False, False, id="focus_is_alive"),
        ],
    )
    def test_focus_is_dead(self, mock_focus_manager_deps, focus_is_dead, expected):
        """Test FocusManager.focus_is_dead."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_focus = Mock(spec=Atspi.Accessible)
        manager._focus = mock_focus

        with patch("orca.ax_object.AXObject.is_dead", return_value=focus_is_dead) as mock_is_dead:
            result = manager.focus_is_dead()
            assert result == expected
            mock_is_dead.assert_called_once_with(mock_focus)

    def test_focus_is_dead_no_focus(self, mock_focus_manager_deps):
        """Test FocusManager.focus_is_dead with no focus set."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        manager._focus = None

        with patch("orca.ax_object.AXObject.is_dead", return_value=False):
            result = manager.focus_is_dead()
            assert result is False

    @pytest.mark.parametrize(
        "focus, window, expected",
        [
            pytest.param(None, "window", False, id="no_focus"),
            pytest.param("same_obj", "same_obj", True, id="focus_equals_window"),
            pytest.param("focus_obj", "window_obj", False, id="focus_not_window"),
        ],
    )
    def test_focus_is_active_window(self, mock_focus_manager_deps, focus, window, expected):
        """Test FocusManager.focus_is_active_window."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()

        if focus == "same_obj" and window == "same_obj":
            same_obj = Mock(spec=Atspi.Accessible)
            manager._focus = same_obj
            manager._window = same_obj
        else:
            manager._focus = Mock(spec=Atspi.Accessible) if focus else None
            manager._window = Mock(spec=Atspi.Accessible) if window else None

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
        self, mock_focus_manager_deps, focus, window, is_ancestor, expected
    ):
        """Test FocusManager.focus_is_in_active_window."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        manager._focus = Mock(spec=Atspi.Accessible) if focus else None
        manager._window = Mock(spec=Atspi.Accessible) if window else None

        with patch(
            "orca.ax_object.AXObject.is_ancestor", return_value=is_ancestor
        ) as mock_is_ancestor:
            result = manager.focus_is_in_active_window()
            assert result == expected

            if focus and window:
                mock_is_ancestor.assert_called_once_with(manager._focus, manager._window)

    @pytest.mark.parametrize(
        "start_offset, end_offset, mode",
        [
            pytest.param(None, None, None, id="all_defaults"),
            pytest.param(5, None, None, id="start_only"),
            pytest.param(5, 10, None, id="start_and_end"),
            pytest.param(5, 10, "caret-tracking", id="all_specified"),
        ],
    )
    def test_emit_region_changed(self, mock_focus_manager_deps, start_offset, end_offset, mode):
        """Test FocusManager.emit_region_changed."""

        from orca.focus_manager import FocusManager, FOCUS_TRACKING, FLAT_REVIEW

        manager = FocusManager()
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_obj.emit = Mock()

        expected_start = start_offset if start_offset is not None else 0
        expected_end = end_offset if end_offset is not None else expected_start
        expected_mode = mode if mode is not None else FOCUS_TRACKING

        # Scenario: Regular mode change
        manager.emit_region_changed(mock_obj, start_offset, end_offset, mode)

        mock_obj.emit.assert_any_call("mode-changed::" + expected_mode, 1, "")
        mock_obj.emit.assert_any_call("region-changed", expected_start, expected_end)

        assert manager._active_mode == expected_mode
        assert manager._object_of_interest == mock_obj

        # Scenario: Mode change to FLAT_REVIEW
        manager.emit_region_changed(mock_obj, mode=FLAT_REVIEW)
        braille_mock = mock_focus_manager_deps["braille"]
        braille_mock.setBrlapiPriority.assert_called_with(braille_mock.BRLAPI_PRIORITY_HIGH)

        # Scenario: Mode change from FLAT_REVIEW to normal mode
        manager.emit_region_changed(mock_obj, mode=FOCUS_TRACKING)
        braille_mock.setBrlapiPriority.assert_called_with()

    def test_emit_region_changed_null_object(self, mock_focus_manager_deps):
        """Test FocusManager.emit_region_changed with null object."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()

        manager.emit_region_changed(None)
        assert manager._object_of_interest is None

    @pytest.mark.parametrize(
        "active_mode, expected",
        [
            pytest.param("say-all", True, id="in_say_all"),
            pytest.param("focus-tracking", False, id="not_in_say_all"),
            pytest.param(None, False, id="no_mode"),
        ],
    )
    def test_in_say_all(self, mock_focus_manager_deps, active_mode, expected):
        """Test FocusManager.in_say_all."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        manager._active_mode = active_mode

        result = manager.in_say_all()
        assert result == expected

    def test_get_active_mode_and_object_of_interest(self, mock_focus_manager_deps):
        """Test FocusManager.get_active_mode_and_object_of_interest."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_obj = Mock(spec=Atspi.Accessible)
        mode = "caret-tracking"

        manager._active_mode = mode
        manager._object_of_interest = mock_obj

        result_mode, result_obj = manager.get_active_mode_and_object_of_interest()
        assert result_mode == mode
        assert result_obj == mock_obj

    def test_get_locus_of_focus(self, mock_focus_manager_deps):
        """Test FocusManager.get_locus_of_focus."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_focus = Mock(spec=Atspi.Accessible)
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
        self, mock_focus_manager_deps, monkeypatch, force, obj_equals_current_focus, notify_script
    ):
        """Test FocusManager.set_locus_of_focus."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_app = Mock(spec=Atspi.Accessible)

        if obj_equals_current_focus:
            manager._focus = mock_obj
        else:
            manager._focus = Mock(spec=Atspi.Accessible)

        script_instance = mock_focus_manager_deps["script_instance"]

        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        AXObject.clear_cache = Mock()
        AXObject.is_dead = Mock(return_value=False)
        AXObject.is_valid = Mock(side_effect=lambda obj: obj is not None)
        AXUtilities.is_table_cell = Mock(return_value=False)
        AXUtilities.get_application = Mock(return_value=mock_app)

        mock_emit = Mock()
        manager.emit_region_changed = mock_emit

        manager.set_locus_of_focus(mock_event, mock_obj, notify_script, force)

        if not force and obj_equals_current_focus:
            mock_emit.assert_not_called()
        else:
            assert manager._focus == mock_obj
            mock_emit.assert_called_once()

            if notify_script:
                script_instance.locus_of_focus_changed.assert_called_once()

    def test_set_locus_of_focus_null_object(self, mock_focus_manager_deps):
        """Test FocusManager.set_locus_of_focus with null object."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_focus = Mock(spec=Atspi.Accessible)
        manager._focus = mock_focus

        manager.set_locus_of_focus(None, None)
        assert manager._focus is None

    def test_set_locus_of_focus_dead_object(self, mock_focus_manager_deps):
        """Test FocusManager.set_locus_of_focus with dead object."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_obj = Mock(spec=Atspi.Accessible)
        old_focus = Mock(spec=Atspi.Accessible)
        manager._focus = old_focus

        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        AXObject.clear_cache = Mock()
        AXObject.is_dead = Mock(return_value=True)
        AXUtilities.is_table_cell = Mock(return_value=False)

        manager.set_locus_of_focus(None, mock_obj)

        # Focus should not change since object is dead
        assert manager._focus == old_focus

    def test_active_window_is_active(self, mock_focus_manager_deps):
        """Test FocusManager.active_window_is_active."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_window = Mock(spec=Atspi.Accessible)
        manager._window = mock_window

        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_clear = Mock()
        mock_is_active = Mock(return_value=True)
        AXObject.clear_cache = mock_clear
        AXUtilities.is_active = mock_is_active

        result = manager.active_window_is_active()
        assert result is True

        mock_clear.assert_called_once_with(
            mock_window, False, "Ensuring the active window is really active."
        )
        mock_is_active.assert_called_once_with(mock_window)

    def test_get_active_window(self, mock_focus_manager_deps):
        """Test FocusManager.get_active_window."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_window = Mock(spec=Atspi.Accessible)
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
        mock_focus_manager_deps,
        frame_equals_current,
        set_window_as_focus,
        focus_is_in_window,
        has_broken_ancestry,
    ):
        """Test FocusManager.set_active_window."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_frame = Mock(spec=Atspi.Accessible)
        mock_app = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)

        if frame_equals_current:
            manager._window = mock_frame
        else:
            manager._window = Mock(spec=Atspi.Accessible)

        manager._focus = mock_focus

        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_set_focus = Mock()
        manager.set_locus_of_focus = mock_set_focus
        manager.focus_is_active_window = Mock(return_value=focus_is_in_window)
        manager.focus_is_in_active_window = Mock(return_value=focus_is_in_window)
        AXObject.has_broken_ancestry = Mock(return_value=has_broken_ancestry)
        AXUtilities.get_application = Mock(return_value=mock_app)

        manager.set_active_window(mock_frame, mock_app, set_window_as_focus, False)

        if not frame_equals_current:
            assert manager._window == mock_frame

        if set_window_as_focus:
            mock_set_focus.assert_called_with(None, mock_frame, False)
        elif not focus_is_in_window and not has_broken_ancestry:
            mock_set_focus.assert_called_with(None, mock_frame, notify_script=True)

    def test_set_active_window_null_frame(self, mock_focus_manager_deps):
        """Test FocusManager.set_active_window with null frame."""

        from orca.focus_manager import FocusManager

        manager = FocusManager()
        mock_focus = Mock(spec=Atspi.Accessible)
        manager._focus = mock_focus

        manager.set_active_window(None)
        assert manager._window is None

    def test_get_manager(self, mock_focus_manager_deps):
        """Test focus_manager.get_manager."""

        from orca import focus_manager

        manager1 = focus_manager.get_manager()
        manager2 = focus_manager.get_manager()

        assert manager1 is manager2
        assert isinstance(manager1, focus_manager.FocusManager)

    def test_set_locus_of_focus_table_cell_coordinates(self, mock_focus_manager_deps):
        """Test FocusManager.set_locus_of_focus saves table cell coordinates."""

        from orca.focus_manager import FocusManager
        from orca.ax_table import AXTable

        manager = FocusManager()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Mock table coordinates
        AXTable.get_cell_coordinates = Mock(return_value=(5, 3))

        manager.set_locus_of_focus(None, mock_obj)

        # Verify cell coordinates were retrieved and saved
        AXTable.get_cell_coordinates.assert_called_once_with(mock_obj, find_cell=True)
        assert manager.get_last_cell_coordinates() == (5, 3)

    def test_set_locus_of_focus_text_cursor_position(self, mock_focus_manager_deps):
        """Test FocusManager.set_locus_of_focus saves text cursor position."""

        from orca.focus_manager import FocusManager
        from orca.ax_text import AXText

        manager = FocusManager()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Mock text cursor offset
        AXText.get_caret_offset = Mock(return_value=42)

        manager.set_locus_of_focus(None, mock_obj)

        # Verify cursor position was retrieved and saved
        AXText.get_caret_offset.assert_called_once_with(mock_obj)
        AXText.update_cached_selected_text.assert_called_once_with(mock_obj)
        obj, offset = manager.get_last_cursor_position()
        assert obj == mock_obj
        assert offset == 42

    def test_set_locus_of_focus_none_object_coordinates(self, mock_focus_manager_deps):
        """Test FocusManager.set_locus_of_focus handles None object coordinates properly."""

        from orca.focus_manager import FocusManager
        from orca.ax_table import AXTable
        from orca.ax_text import AXText

        manager = FocusManager()

        # Mock functions should not be called for None object
        AXTable.get_cell_coordinates = Mock()
        AXText.get_caret_offset = Mock()
        AXText.update_cached_selected_text = Mock()

        manager.set_locus_of_focus(None, None)

        # Verify functions were not called for None object
        AXTable.get_cell_coordinates.assert_not_called()
        AXText.get_caret_offset.assert_not_called()
        AXText.update_cached_selected_text.assert_not_called()

        # Verify default coordinates were set
        assert manager.get_last_cell_coordinates() == (-1, -1)
