# Unit tests for event_manager.py EventManager class methods.
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
# pylint: disable=too-many-locals
# pylint: disable=too-few-public-methods

"""Unit tests for event_manager.py EventManager class methods."""

from __future__ import annotations

import itertools
import queue
import sys
from unittest.mock import Mock, patch, call

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi


@pytest.mark.unit
class TestEventManager:
    """Test EventManager class methods."""

    @pytest.fixture
    def mock_event_manager_deps(self, monkeypatch, mock_orca_dependencies):
        """Mock all dependencies needed for event_manager imports."""

        from .conftest import clean_module_cache

        modules_to_clean = [
            "orca.event_manager",
            "orca.braille",
            "orca.focus_manager",
            "orca.input_event",
            "orca.input_event_manager",
            "orca.script_manager",
            "orca.ax_utilities_debugging",
        ]
        for module in modules_to_clean:
            clean_module_cache(module)

        debug_mock = mock_orca_dependencies.debug
        debug_mock.LEVEL_WARNING = 2
        debug_mock.LEVEL_SEVERE = 3
        debug_mock.debugLevel = 0

        braille_mock = Mock()
        braille_mock.disableBraille = Mock()
        monkeypatch.setitem(sys.modules, "orca.braille", braille_mock)

        focus_manager_mock = Mock()
        focus_mgr_instance = Mock()
        focus_mgr_instance.get_locus_of_focus = Mock()
        focus_mgr_instance.get_active_window = Mock()
        focus_mgr_instance.focus_and_window_are_unknown = Mock(return_value=False)
        focus_mgr_instance.clear_state = Mock()
        focus_manager_mock.get_manager = Mock(return_value=focus_mgr_instance)
        monkeypatch.setitem(sys.modules, "orca.focus_manager", focus_manager_mock)

        input_event_mock = Mock()

        class MockKeyboardEvent:
            """Mock KeyboardEvent for testing."""

        class MockBrailleEvent:
            """Mock BrailleEvent for testing."""

        class MockMouseButtonEvent:
            """Mock MouseButtonEvent for testing."""

        input_event_mock.KeyboardEvent = MockKeyboardEvent
        input_event_mock.BrailleEvent = MockBrailleEvent
        input_event_mock.MouseButtonEvent = MockMouseButtonEvent
        monkeypatch.setitem(sys.modules, "orca.input_event", input_event_mock)

        input_event_manager_mock = Mock()
        input_mgr_instance = Mock()
        input_mgr_instance.start_key_watcher = Mock()
        input_mgr_instance.stop_key_watcher = Mock()
        input_event_manager_mock.get_manager = Mock(return_value=input_mgr_instance)
        monkeypatch.setitem(sys.modules, "orca.input_event_manager", input_event_manager_mock)

        script_manager_mock = Mock()
        script_mgr_instance = Mock()
        script_instance = Mock()
        script_instance.app = Mock()
        script_instance.event_cache = {}
        script_instance.listeners = {}
        script_instance.is_activatable_event = Mock(return_value=True)
        script_instance.force_script_activation = Mock(return_value=False)
        script_instance.present_if_inactive = False
        script_mgr_instance.get_active_script = Mock(return_value=script_instance)
        script_mgr_instance.get_script = Mock(return_value=script_instance)
        script_mgr_instance.set_active_script = Mock()
        script_mgr_instance.get_default_script = Mock(return_value=script_instance)
        script_mgr_instance.reclaim_scripts = Mock()
        script_manager_mock.get_manager = Mock(return_value=script_mgr_instance)
        monkeypatch.setitem(sys.modules, "orca.script_manager", script_manager_mock)

        settings_mock = mock_orca_dependencies.settings
        settings_mock.progressBarVerbosity = 1
        settings_mock.PROGRESS_BAR_ALL = 2

        ax_utils_debugging_mock = Mock()
        ax_utils_debugging_mock.object_event_details_as_string = Mock(return_value="mock details")
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_debugging", ax_utils_debugging_mock)

        glib_mock = Mock()
        glib_mock.idle_add = Mock(return_value=123)
        glib_mock.timeout_add = Mock()
        monkeypatch.setattr("gi.repository.GLib", glib_mock)

        ax_object_mock = mock_orca_dependencies.ax_object
        ax_object_mock.get_name = Mock()
        ax_object_mock.get_parent = Mock()
        ax_object_mock.get_role = Mock()
        ax_object_mock.get_attribute = Mock()
        ax_object_mock.is_dead = Mock(return_value=False)
        ax_object_mock.has_state = Mock(return_value=False)

        ax_utilities_mock = mock_orca_dependencies.ax_utilities
        ax_utilities_mock.is_frame = Mock(return_value=False)
        ax_utilities_mock.is_dialog_or_alert = Mock(return_value=False)
        ax_utilities_mock.is_window = Mock(return_value=False)
        ax_utilities_mock.is_text = Mock(return_value=False)
        ax_utilities_mock.is_notification = Mock(return_value=False)
        ax_utilities_mock.is_alert = Mock(return_value=False)
        ax_utilities_mock.is_selected = Mock(return_value=False)
        ax_utilities_mock.is_focused = Mock(return_value=False)
        ax_utilities_mock.manages_descendants = Mock(return_value=False)
        ax_utilities_mock.is_section = Mock(return_value=False)
        ax_utilities_mock.get_application = Mock()
        ax_utilities_mock.get_desktop = Mock()
        ax_utilities_mock.is_invalid_role = Mock(return_value=False)
        ax_utilities_mock.is_menu_related = Mock(return_value=False)
        ax_utilities_mock.is_image = Mock(return_value=False)
        ax_utilities_mock.is_showing = Mock(return_value=True)
        ax_utilities_mock.is_selectable = Mock(return_value=False)
        ax_utilities_mock.is_menu = Mock(return_value=False)
        ax_utilities_mock.is_focusable = Mock(return_value=False)
        ax_utilities_mock.is_panel = Mock(return_value=False)
        ax_utilities_mock.is_modal = Mock(return_value=False)
        ax_utilities_mock.is_progress_bar = Mock(return_value=False)
        ax_utilities_mock.is_defunct = Mock(return_value=False)
        ax_utilities_mock.is_application_in_desktop = Mock(return_value=True)
        ax_utilities_mock.is_iconified = Mock(return_value=False)

        return {
            "debug": debug_mock,
            "braille": braille_mock,
            "focus_manager": focus_mgr_instance,
            "input_event_manager": input_mgr_instance,
            "script_manager": script_mgr_instance,
            "script": script_instance,
            "settings": settings_mock,
            "glib": glib_mock,
            "ax_utils_debugging": ax_utils_debugging_mock,
            "ax_object": ax_object_mock,
            "ax_utilities": ax_utilities_mock,
        }

    def test_init(self, mock_event_manager_deps):
        """Test EventManager.__init__."""

        from orca.event_manager import EventManager

        manager = EventManager()

        assert not manager._script_listener_counts
        assert manager._active is False
        assert manager._paused is False
        assert isinstance(manager._counter, itertools.count)
        assert isinstance(manager._event_queue, queue.PriorityQueue)
        assert manager._gidle_id == 0
        assert not manager._event_history

    def test_activate(self, mock_event_manager_deps):
        """Test EventManager.activate."""

        from orca.event_manager import EventManager

        manager = EventManager()
        input_mgr = mock_event_manager_deps["input_event_manager"]

        # Scenario: Activate when not already active
        manager.activate()
        assert manager._active is True
        input_mgr.start_key_watcher.assert_called_once()

        # Scenario: Activate when already active
        input_mgr.start_key_watcher.reset_mock()
        manager.activate()
        input_mgr.start_key_watcher.assert_not_called()

    def test_deactivate(self, mock_event_manager_deps):
        """Test EventManager.deactivate."""

        from orca.event_manager import EventManager

        manager = EventManager()
        input_mgr = mock_event_manager_deps["input_event_manager"]
        manager._active = True
        manager._script_listener_counts = {"test": 1}

        # Scenario: Deactivate when active
        manager.deactivate()
        assert manager._active is False
        assert not manager._script_listener_counts
        input_mgr.stop_key_watcher.assert_called_once()

        # Scenario: Deactivate when already inactive
        input_mgr.stop_key_watcher.reset_mock()
        manager.deactivate()
        input_mgr.stop_key_watcher.assert_not_called()

    @pytest.mark.parametrize(
        "pause, clear_queue, reason",
        [
            pytest.param(True, False, "", id="pause_only"),
            pytest.param(False, False, "test reason", id="unpause_with_reason"),
            pytest.param(True, True, "clear and pause", id="pause_and_clear"),
        ],
    )
    def test_pause_queuing(self, mock_event_manager_deps, pause, clear_queue, reason):
        """Test EventManager.pause_queuing."""

        from orca.event_manager import EventManager

        manager = EventManager()
        original_queue = manager._event_queue

        manager.pause_queuing(pause, clear_queue, reason)

        assert manager._paused == pause
        if clear_queue:
            assert manager._event_queue is not original_queue
        else:
            assert manager._event_queue is original_queue

    @pytest.mark.parametrize(
        "event_type, expected_priority",
        [
            pytest.param("window:activate", 2, id="window_event"),
            pytest.param("object:state-changed:focused", 3, id="focus_changed"),
            pytest.param("object:active-descendant-changed", 3, id="active_descendant"),
            pytest.param("object:announcement", 4, id="announcement_normal"),
            pytest.param("object:state-changed:invalid-entry", 5, id="invalid_entry"),
            pytest.param("object:children-changed:add", 6, id="children_changed"),
            pytest.param("object:text-changed:insert", 4, id="other_event"),
        ],
    )
    def test_get_priority(self, mock_event_manager_deps, event_type, expected_priority):
        """Test EventManager._get_priority."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = event_type
        mock_event.source = Mock()
        mock_event.detail1 = 0

        ax_utilities = mock_event_manager_deps["ax_utilities"]
        if event_type == "object:state-changed:active":
            ax_utilities.is_frame.return_value = True
        elif event_type == "object:announcement":
            mock_event.detail1 = Atspi.Live.POLITE if expected_priority == 3 else 0

        priority = manager._get_priority(mock_event)
        assert priority == expected_priority

    def test_get_priority_announcement_levels(self, mock_event_manager_deps):
        """Test EventManager._get_priority for announcement event levels."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:announcement"
        mock_event.source = Mock()

        # Scenario: Assertive announcement
        mock_event.detail1 = Atspi.Live.ASSERTIVE
        priority = manager._get_priority(mock_event)
        assert priority == 2  # PRIORITY_IMPORTANT

        # Scenario: Polite announcement
        mock_event.detail1 = Atspi.Live.POLITE
        priority = manager._get_priority(mock_event)
        assert priority == 3  # PRIORITY_HIGH

        # Scenario: Other announcement level
        mock_event.detail1 = 999
        priority = manager._get_priority(mock_event)
        assert priority == 4  # PRIORITY_NORMAL

    def test_is_obsoleted_by_same_event(self, mock_event_manager_deps):
        """Test EventManager._is_obsoleted_by detects duplicate events."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = Mock()
        mock_event.detail1 = 5
        mock_event.detail2 = 10
        mock_event.any_data = "test"

        existing_event = Mock(spec=Atspi.Event)
        existing_event.type = "object:text-changed:insert"
        existing_event.source = mock_event.source
        existing_event.detail1 = 5
        existing_event.detail2 = 10
        existing_event.any_data = "test"

        manager._event_queue.put((4, 1, existing_event))
        result = manager._is_obsoleted_by(mock_event)
        assert result == existing_event

    def test_is_obsoleted_by_window_event(self, mock_event_manager_deps):
        """Test EventManager._is_obsoleted_by for window events."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "window:activate"
        mock_event.source = Mock()

        existing_event = Mock(spec=Atspi.Event)
        existing_event.type = "window:deactivate"
        existing_event.source = mock_event.source
        manager._event_queue.put((2, 1, existing_event))

        result = manager._is_obsoleted_by(mock_event)
        assert result == existing_event

    def test_is_obsoleted_by_no_obsolescence(self, mock_event_manager_deps):
        """Test EventManager._is_obsoleted_by when no obsolescence exists."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = Mock()

        result = manager._is_obsoleted_by(mock_event)
        assert result is None

    def test_ignore_inactive_manager(self, mock_event_manager_deps):
        """Test EventManager._ignore when manager is inactive."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"

        # Scenario: Manager not active
        manager._active = False
        assert manager._ignore(mock_event) is True

        # Scenario: Manager paused
        manager._active = True
        manager._paused = True
        assert manager._ignore(mock_event) is True

    def test_ignore_window_events(self, mock_event_manager_deps):
        """Test EventManager._ignore for window and mouse events."""

        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False

        # Scenario: Window event should not be ignored
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "window:activate"
        assert manager._ignore(mock_event) is False

        # Scenario: Mouse button event should not be ignored
        mock_event.type = "mouse:button:1p"
        assert manager._ignore(mock_event) is False

    def test_ignore_focused_window(self, mock_event_manager_deps):
        """Test EventManager._ignore for focused window events."""

        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False

        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:state-changed:focused"
        mock_event.source = Mock()

        ax_utilities = mock_event_manager_deps["ax_utilities"]
        ax_utilities.is_window.return_value = True

        assert manager._ignore(mock_event) is True

    def test_queue_println(self, mock_event_manager_deps):
        """Test EventManager._queue_println."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "test:event"

        debug_mock = mock_event_manager_deps["debug"]
        debug_mock.debugLevel = 10  # Higher than LEVEL_INFO to cause early return

        # Should not crash
        manager._queue_println(mock_event)
        manager._queue_println(mock_event, is_enqueue=False)

    def test_enqueue_object_event_ignored(self, mock_event_manager_deps):
        """Test EventManager._enqueue_object_event for ignored events."""

        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = False  # Will cause event to be ignored

        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"

        manager._enqueue_object_event(mock_event)
        assert manager._event_queue.empty()

    def test_on_no_focus(self, mock_event_manager_deps):
        """Test EventManager._on_no_focus."""

        from orca.event_manager import EventManager

        manager = EventManager()
        focus_mgr = mock_event_manager_deps["focus_manager"]
        script_mgr = mock_event_manager_deps["script_manager"]
        braille_mock = mock_event_manager_deps["braille"]

        # Scenario: Focus and window are unknown
        focus_mgr.focus_and_window_are_unknown.return_value = True
        result = manager._on_no_focus()
        assert result is False

        # Scenario: No active script
        focus_mgr.focus_and_window_are_unknown.return_value = False
        script_mgr.get_active_script.return_value = None
        result = manager._on_no_focus()
        assert result is False
        script_mgr.set_active_script.assert_called_once()
        braille_mock.disableBraille.assert_called_once()

    def test_dequeue_object_event_empty_queue(self, mock_event_manager_deps):
        """Test EventManager._dequeue_object_event with empty queue."""

        from orca.event_manager import EventManager

        manager = EventManager()
        result = manager._dequeue_object_event()

        # Should stop processing (return False)
        assert result is False
        assert manager._gidle_id == 0

    def test_register_listener(self, mock_event_manager_deps):
        """Test EventManager.register_listener."""

        from orca.event_manager import EventManager

        manager = EventManager()
        manager._listener = Mock()

        # Scenario: First registration for event type
        manager.register_listener("object:text-changed:insert")
        assert manager._script_listener_counts["object:text-changed:insert"] == 1
        manager._listener.register.assert_called_once_with("object:text-changed:insert")

        # Scenario: Second registration for same event type
        manager._listener.register.reset_mock()
        manager.register_listener("object:text-changed:insert")
        assert manager._script_listener_counts["object:text-changed:insert"] == 2
        manager._listener.register.assert_not_called()

    def test_deregister_listener(self, mock_event_manager_deps):
        """Test EventManager.deregister_listener."""

        from orca.event_manager import EventManager

        manager = EventManager()
        manager._listener = Mock()
        event_type = "object:text-changed:insert"
        manager._script_listener_counts[event_type] = 2

        # Scenario: Decrement but don't remove
        manager.deregister_listener(event_type)
        assert manager._script_listener_counts[event_type] == 1
        manager._listener.deregister.assert_not_called()

        # Scenario: Decrement to zero and remove
        manager.deregister_listener(event_type)
        assert event_type not in manager._script_listener_counts
        manager._listener.deregister.assert_called_once_with(event_type)

        # Scenario: Deregister non-existent event type
        manager.deregister_listener("non:existent")
        # Should not crash

    def test_register_script_listeners(self, mock_event_manager_deps):
        """Test EventManager.register_script_listeners."""

        from orca.event_manager import EventManager

        manager = EventManager()
        manager.register_listener = Mock()

        mock_script = Mock()
        mock_script.listeners = {
            "object:text-changed:insert": Mock(),
            "object:state-changed:focused": Mock(),
        }

        manager.register_script_listeners(mock_script)

        # Should register all listener event types
        expected_calls = [
            call("object:text-changed:insert"),
            call("object:state-changed:focused"),
        ]
        manager.register_listener.assert_has_calls(expected_calls, any_order=True)

    def test_deregister_script_listeners(self, mock_event_manager_deps):
        """Test EventManager.deregister_script_listeners."""

        from orca.event_manager import EventManager

        manager = EventManager()
        manager.deregister_listener = Mock()

        mock_script = Mock()
        mock_script.listeners = {
            "object:text-changed:insert": Mock(),
            "object:state-changed:focused": Mock(),
        }

        manager.deregister_script_listeners(mock_script)

        # Should deregister all listener event types
        expected_calls = [
            call("object:text-changed:insert"),
            call("object:state-changed:focused"),
        ]
        manager.deregister_listener.assert_has_calls(expected_calls, any_order=True)

    def test_get_script_for_event_focus(self, mock_event_manager_deps):
        """Test EventManager._get_script_for_event for focused events."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.source = Mock()
        mock_event.type = "object:state-changed:focused"

        focus_mgr = mock_event_manager_deps["focus_manager"]
        script_mgr = mock_event_manager_deps["script_manager"]
        active_script = Mock()

        focus_mgr.get_locus_of_focus.return_value = mock_event.source

        result = manager._get_script_for_event(mock_event, active_script)
        assert result == active_script

    def test_get_script_for_event_mouse(self, mock_event_manager_deps):
        """Test EventManager._get_script_for_event for mouse events."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "mouse:button:1p"
        mock_event.source = Mock()

        script_mgr = mock_event_manager_deps["script_manager"]
        expected_script = Mock()
        script_mgr.get_script.return_value = expected_script

        mock_mouse_event = Mock()
        mock_mouse_event.app = Mock()
        mock_mouse_event.window = Mock()

        with patch("orca.input_event.MouseButtonEvent", return_value=mock_mouse_event):
            result = manager._get_script_for_event(mock_event)

        assert result == expected_script

    def test_get_script_for_event_defunct_app(self, mock_event_manager_deps):
        """Test EventManager._get_script_for_event with defunct application."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = Mock()
        mock_app = Mock()

        ax_utilities = mock_event_manager_deps["ax_utilities"]
        ax_utilities.get_application.return_value = mock_app
        ax_utilities.is_defunct.return_value = True

        result = manager._get_script_for_event(mock_event)
        assert result is None

    @pytest.mark.parametrize(
        "event_type, detail1, expected, reason_contains",
        [
            pytest.param(
                "object:state-changed:focused", 1, True, "claimed focus", id="focus_claimed"
            ),
            pytest.param(
                "object:state-changed:selected", 1, True, "Selection change", id="menu_selection"
            ),
            pytest.param("object:state-changed:showing", 0, True, "Modal panel", id="modal_panel"),
            pytest.param("object:text-changed:insert", 0, False, "No reason", id="no_activation"),
        ],
    )
    def test_is_activatable_event(
        self, mock_event_manager_deps, event_type, detail1, expected, reason_contains
    ):
        """Test EventManager._is_activatable_event."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = event_type
        mock_event.detail1 = detail1
        mock_event.source = Mock()

        mock_script = Mock()
        mock_script.is_activatable_event.return_value = True
        mock_script.force_script_activation.return_value = False

        ax_utilities = mock_event_manager_deps["ax_utilities"]
        if event_type == "object:state-changed:selected":
            ax_utilities.is_menu.return_value = True
            ax_utilities.is_focusable.return_value = True
        elif event_type == "object:state-changed:showing":
            ax_utilities.is_panel.return_value = True
            ax_utilities.is_modal.return_value = True
        else:
            ax_utilities.is_frame.return_value = event_type == "object:state-changed:active"

        focus_mgr = mock_event_manager_deps["focus_manager"]
        if event_type == "window:activate":
            focus_mgr.get_active_window.return_value = mock_event.source
        else:
            focus_mgr.get_active_window.return_value = Mock()

        result, reason = manager._is_activatable_event(mock_event, mock_script)
        assert result == expected
        assert reason_contains.lower() in reason.lower()

    def test_is_activatable_event_no_source(self, mock_event_manager_deps):
        """Test EventManager._is_activatable_event with no event source."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.source = None

        result, reason = manager._is_activatable_event(mock_event)
        assert result is False
        assert "event.source" in reason

    def test_is_activatable_event_script_forces(self, mock_event_manager_deps):
        """Test EventManager._is_activatable_event when script forces activation."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = Mock()

        mock_script = Mock()
        mock_script.is_activatable_event.return_value = True
        mock_script.force_script_activation.return_value = True

        result, reason = manager._is_activatable_event(mock_event, mock_script)
        assert result is True
        assert "insists" in reason

    @pytest.mark.parametrize(
        "event_script_is_active, present_if_inactive, is_progress_bar, verbosity_all, expected",
        [
            pytest.param(True, False, False, False, True, id="active_script"),
            pytest.param(False, True, False, False, True, id="inactive_but_presents"),
            pytest.param(False, False, True, True, True, id="progress_bar_all"),
            pytest.param(False, False, False, False, False, id="no_reason_to_process"),
        ],
    )
    def test_should_process_event(
        self,
        mock_event_manager_deps,
        event_script_is_active,
        present_if_inactive,
        is_progress_bar,
        verbosity_all,
        expected,
    ):
        """Test EventManager._should_process_event."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "test:event"
        mock_event.source = Mock()

        event_script = Mock()
        event_script.present_if_inactive = present_if_inactive

        if event_script_is_active:
            active_script = event_script
        else:
            active_script = Mock()

        settings = mock_event_manager_deps["settings"]
        if verbosity_all:
            settings.progressBarVerbosity = settings.PROGRESS_BAR_ALL
        else:
            settings.progressBarVerbosity = 1

        ax_utilities = mock_event_manager_deps["ax_utilities"]
        ax_utilities.is_progress_bar.return_value = is_progress_bar

        result = manager._should_process_event(mock_event, event_script, active_script)
        assert result == expected

    def test_process_object_event_obsoleted(self, mock_event_manager_deps):
        """Test EventManager._process_object_event with obsoleted event."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)

        manager._is_obsoleted_by = Mock(return_value=Mock())

        manager._process_object_event(mock_event)
        # Should return early without processing

    def test_process_object_event_dead_source(self, mock_event_manager_deps):
        """Test EventManager._process_object_event with dead event source."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "window:deactivate"
        mock_event.source = Mock()

        manager._is_obsoleted_by = Mock(return_value=None)
        ax_object = mock_event_manager_deps["ax_object"]
        ax_utilities = mock_event_manager_deps["ax_utilities"]
        ax_object.is_dead.return_value = True
        ax_utilities.is_defunct.return_value = False

        focus_mgr = mock_event_manager_deps["focus_manager"]
        script_mgr = mock_event_manager_deps["script_manager"]
        focus_mgr.get_active_window.return_value = mock_event.source

        manager._process_object_event(mock_event)

        # Should clear focus and script when active window is dead
        focus_mgr.clear_state.assert_called_once()
        script_mgr.set_active_script.assert_called_once_with(
            None, "Active window is dead or defunct"
        )

    def test_process_object_event_no_listener(self, mock_event_manager_deps):
        """Test EventManager._process_object_event with no matching listener."""

        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "object:unknown-event"
        mock_event.source = Mock()

        manager._is_obsoleted_by = Mock(return_value=None)
        ax_object = mock_event_manager_deps["ax_object"]
        ax_utilities = mock_event_manager_deps["ax_utilities"]
        ax_object.is_dead.return_value = False
        ax_utilities.is_defunct.return_value = False
        ax_utilities.is_iconified.return_value = False

        mock_script = Mock()
        mock_script.listeners = {}

        script_mgr = mock_event_manager_deps["script_manager"]
        script_mgr.get_active_script.return_value = mock_script

        manager._get_script_for_event = Mock(return_value=mock_script)
        manager._is_activatable_event = Mock(return_value=(False, "test"))
        manager._should_process_event = Mock(return_value=True)

        manager._process_object_event(mock_event)
        # Should complete without error

    def test_get_manager(self, mock_event_manager_deps):
        """Test event_manager.get_manager."""

        from orca import event_manager

        manager1 = event_manager.get_manager()
        manager2 = event_manager.get_manager()

        # Should return the same singleton instance
        assert manager1 is manager2
        assert isinstance(manager1, event_manager.EventManager)
