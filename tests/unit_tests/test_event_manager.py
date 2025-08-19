# Unit tests for event_manager.py methods.
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
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines

"""Unit tests for event_manager.py methods."""

from __future__ import annotations

import itertools
import queue
from typing import TYPE_CHECKING
from unittest.mock import call

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestEventManager:
    """Test EventManager class methods."""

    def _setup_ignore_event_ax_utilities_mocks(self, test_context, mock_time=5000.0, is_text=True):
        """Set up common AXUtilities mocks for event ignore testing scenarios."""

        test_context.patch("time.time", return_value=mock_time)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=is_text
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for event_manager module testing."""

        additional_modules = [
            "orca.input_event_manager",
            "orca.ax_utilities_debugging",
            "orca.ax_utilities",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_WARNING = 2
        debug_mock.LEVEL_SEVERE = 3
        debug_mock.debugLevel = 0

        braille_mock = essential_modules["orca.braille"]
        braille_mock.disableBraille = test_context.Mock()

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_mgr_instance = test_context.Mock()
        focus_mgr_instance.get_locus_of_focus = test_context.Mock()
        focus_mgr_instance.get_active_window = test_context.Mock()
        focus_mgr_instance.focus_and_window_are_unknown = test_context.Mock(
            return_value=False
        )
        focus_mgr_instance.clear_state = test_context.Mock()
        focus_manager_mock.get_manager = test_context.Mock(return_value=focus_mgr_instance)

        input_event_mock = essential_modules["orca.input_event"]

        class MockKeyboardEvent:
            """Mock KeyboardEvent for testing."""

        class MockBrailleEvent:
            """Mock BrailleEvent for testing."""

        class MockMouseButtonEvent:
            """Mock MouseButtonEvent for testing."""

        input_event_mock.KeyboardEvent = MockKeyboardEvent
        input_event_mock.BrailleEvent = MockBrailleEvent
        input_event_mock.MouseButtonEvent = MockMouseButtonEvent

        input_event_manager_mock = essential_modules["orca.input_event_manager"]
        input_mgr_instance = test_context.Mock()
        input_mgr_instance.start_key_watcher = test_context.Mock()
        input_mgr_instance.stop_key_watcher = test_context.Mock()
        input_event_manager_mock.get_manager = test_context.Mock(
            return_value=input_mgr_instance
        )

        script_manager_mock = essential_modules["orca.script_manager"]
        script_mgr_instance = test_context.Mock()
        script_instance = test_context.Mock()
        script_instance.app = test_context.Mock()
        script_instance.event_cache = {}
        script_instance.listeners = {}
        script_instance.is_activatable_event = test_context.Mock(return_value=True)
        script_instance.force_script_activation = test_context.Mock(return_value=False)
        script_instance.present_if_inactive = False
        script_mgr_instance.get_active_script = test_context.Mock(
            return_value=script_instance
        )
        script_mgr_instance.get_script = test_context.Mock(return_value=script_instance)
        script_mgr_instance.set_active_script = test_context.Mock()
        script_mgr_instance.get_default_script = test_context.Mock(
            return_value=script_instance
        )
        script_mgr_instance.reclaim_scripts = test_context.Mock()
        script_manager_mock.get_manager = test_context.Mock(return_value=script_mgr_instance)

        settings_mock = essential_modules["orca.settings"]
        settings_mock.progressBarVerbosity = 1
        settings_mock.PROGRESS_BAR_ALL = 2

        ax_utils_debugging_mock = essential_modules["orca.ax_utilities_debugging"]
        ax_utils_debugging_mock.object_event_details_as_string = test_context.Mock(
            return_value="mock details"
        )

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.get_name = test_context.Mock()
        ax_object_mock.get_parent = test_context.Mock()
        ax_object_mock.get_role = test_context.Mock()
        ax_object_mock.get_attribute = test_context.Mock()
        ax_object_mock.is_dead = test_context.Mock(return_value=False)
        ax_object_mock.has_state = test_context.Mock(return_value=False)

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.is_frame = test_context.Mock(return_value=False)
        ax_utilities_mock.is_dialog_or_alert = test_context.Mock(return_value=False)
        ax_utilities_mock.is_window = test_context.Mock(return_value=False)
        ax_utilities_mock.is_text = test_context.Mock(return_value=False)
        ax_utilities_mock.is_notification = test_context.Mock(return_value=False)
        ax_utilities_mock.is_alert = test_context.Mock(return_value=False)
        ax_utilities_mock.is_selected = test_context.Mock(return_value=False)
        ax_utilities_mock.is_focused = test_context.Mock(return_value=False)
        ax_utilities_mock.manages_descendants = test_context.Mock(return_value=False)
        ax_utilities_mock.is_section = test_context.Mock(return_value=False)
        ax_utilities_mock.get_application = test_context.Mock()
        ax_utilities_mock.get_desktop = test_context.Mock()
        ax_utilities_mock.is_invalid_role = test_context.Mock(return_value=False)
        ax_utilities_mock.is_menu_related = test_context.Mock(return_value=False)
        ax_utilities_mock.is_image = test_context.Mock(return_value=False)
        ax_utilities_mock.is_showing = test_context.Mock(return_value=True)
        ax_utilities_mock.is_selectable = test_context.Mock(return_value=False)
        ax_utilities_mock.is_menu = test_context.Mock(return_value=False)
        ax_utilities_mock.is_focusable = test_context.Mock(return_value=False)
        ax_utilities_mock.is_panel = test_context.Mock(return_value=False)
        ax_utilities_mock.is_modal = test_context.Mock(return_value=False)
        ax_utilities_mock.is_progress_bar = test_context.Mock(return_value=False)
        ax_utilities_mock.is_defunct = test_context.Mock(return_value=False)
        ax_utilities_mock.is_application_in_desktop = test_context.Mock(return_value=True)
        ax_utilities_mock.is_iconified = test_context.Mock(return_value=False)

        glib_mock = test_context.Mock()
        glib_mock.idle_add = test_context.Mock(return_value=123)
        glib_mock.timeout_add = test_context.Mock()
        test_context.patch("gi.repository.GLib", new=glib_mock)

        essential_modules["focus_manager_instance"] = focus_mgr_instance
        essential_modules["input_event_manager_instance"] = input_mgr_instance
        essential_modules["script_manager_instance"] = script_mgr_instance
        essential_modules["script_instance"] = script_instance
        essential_modules["glib"] = glib_mock

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test EventManager.__init__."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        assert not manager._script_listener_counts
        assert manager._active is False
        assert manager._paused is False
        assert isinstance(manager._counter, itertools.count)
        assert isinstance(manager._event_queue, queue.PriorityQueue)
        assert manager._gidle_id == 0
        assert not manager._event_history

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "activate_manager",
                "operation": "activate",
                "initial_active": False,
                "initial_counts": {},
                "expected_active": True,
                "watcher_method": "start_key_watcher",
            },
            {
                "id": "deactivate_manager",
                "operation": "deactivate",
                "initial_active": True,
                "initial_counts": {"test": 1},
                "expected_active": False,
                "watcher_method": "stop_key_watcher",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_activation_operations(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager activate/deactivate operations."""
        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        mock_get_input_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.input_event_manager.get_manager", new=mock_get_input_mgr
        )
        mock_input_mgr = test_context.Mock()
        mock_get_input_mgr.return_value = mock_input_mgr
        manager = EventManager()
        manager._active = case["initial_active"]
        manager._script_listener_counts = case["initial_counts"].copy()

        getattr(manager, case["operation"])()
        assert manager._active is case["expected_active"]

        if case["operation"] == "deactivate":
            assert not manager._script_listener_counts

        getattr(mock_input_mgr, case["watcher_method"]).assert_called_once()

        getattr(mock_input_mgr, case["watcher_method"]).reset_mock()
        getattr(manager, case["operation"])()
        getattr(mock_input_mgr, case["watcher_method"]).assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "pause_only", "pause": True, "clear_queue": False, "reason": ""},
            {
                "id": "unpause_with_reason",
                "pause": False,
                "clear_queue": False,
                "reason": "test reason",
            },
            {
                "id": "pause_and_clear",
                "pause": True,
                "clear_queue": True,
                "reason": "clear and pause",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_pause_queuing(self, test_context, case: dict) -> None:
        """Test EventManager.pause_queuing."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        original_queue = manager._event_queue
        manager.pause_queuing(case["pause"], case["clear_queue"], case["reason"])
        assert manager._paused == case["pause"]
        if case["clear_queue"]:
            assert manager._event_queue is not original_queue
        else:
            assert manager._event_queue is original_queue

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "window_event", "event_type": "window:activate", "expected_priority": 2},
            {
                "id": "focus_changed",
                "event_type": "object:state-changed:focused",
                "expected_priority": 3,
            },
            {
                "id": "active_descendant",
                "event_type": "object:active-descendant-changed",
                "expected_priority": 3,
            },
            {
                "id": "announcement_normal",
                "event_type": "object:announcement",
                "expected_priority": 4,
            },
            {
                "id": "invalid_entry",
                "event_type": "object:state-changed:invalid-entry",
                "expected_priority": 5,
            },
            {
                "id": "children_changed",
                "event_type": "object:children-changed:add",
                "expected_priority": 6,
            },
            {
                "id": "other_event",
                "event_type": "object:text-changed:insert",
                "expected_priority": 4,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_priority(self, test_context, case: dict) -> None:
        """Test EventManager._get_priority."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["event_type"]
        mock_event.source = test_context.Mock()
        mock_event.detail1 = 0
        ax_utilities = essential_modules["orca.ax_utilities"]
        if case["event_type"] == "object:state-changed:active":
            ax_utilities.is_frame.return_value = True
        elif case["event_type"] == "object:announcement":
            mock_event.detail1 = Atspi.Live.POLITE if case["expected_priority"] == 3 else 0
        priority = manager._get_priority(mock_event)
        assert priority == case["expected_priority"]

    def test_get_priority_announcement_levels(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._get_priority for announcement event levels."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:announcement"
        mock_event.source = test_context.Mock()

        mock_event.detail1 = Atspi.Live.ASSERTIVE
        priority = manager._get_priority(mock_event)
        assert priority == 2  # PRIORITY_IMPORTANT

        mock_event.detail1 = Atspi.Live.POLITE
        priority = manager._get_priority(mock_event)
        assert priority == 3  # PRIORITY_HIGH

        mock_event.detail1 = 999
        priority = manager._get_priority(mock_event)
        assert priority == 4  # PRIORITY_NORMAL

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "duplicate_events",
                "new_type": "object:text-changed:insert",
                "new_detail1": 5,
                "new_detail2": 10,
                "new_data": "test",
                "existing_type": "object:text-changed:insert",
                "existing_detail1": 5,
                "existing_detail2": 10,
                "existing_data": "test",
                "priority": 4,
                "should_obsolete": True,
            },
            {
                "id": "window_events",
                "new_type": "window:activate",
                "new_detail1": 0,
                "new_detail2": 0,
                "new_data": None,
                "existing_type": "window:deactivate",
                "existing_detail1": 0,
                "existing_detail2": 0,
                "existing_data": None,
                "priority": 2,
                "should_obsolete": True,
            },
            {
                "id": "no_obsolescence",
                "new_type": "object:text-changed:insert",
                "new_detail1": 0,
                "new_detail2": 0,
                "new_data": None,
                "existing_type": None,
                "existing_detail1": None,
                "existing_detail2": None,
                "existing_data": None,
                "priority": None,
                "should_obsolete": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_obsoleted_by_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager._is_obsoleted_by for various obsolescence scenarios."""
        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["new_type"]
        mock_event.source = test_context.Mock()
        mock_event.detail1 = case["new_detail1"]
        mock_event.detail2 = case["new_detail2"]
        mock_event.any_data = case["new_data"]

        if case["existing_type"] is not None and case["priority"] is not None:
            existing_event = test_context.Mock(spec=Atspi.Event)
            existing_event.type = case["existing_type"]
            existing_event.source = mock_event.source
            existing_event.detail1 = case["existing_detail1"]
            existing_event.detail2 = case["existing_detail2"]
            existing_event.any_data = case["existing_data"]
            manager._event_queue.put((case["priority"], 1, existing_event))

        result = manager._is_obsoleted_by(mock_event)
        if case["should_obsolete"]:
            assert result is not None
        else:
            assert result is None

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "inactive_manager", "active": False, "paused": False, "expected": True},
            {"id": "paused_manager", "active": True, "paused": True, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_ignore_inactive_or_paused_manager(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test EventManager._ignore when manager is inactive or paused."""
        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"

        manager._active = case["active"]
        manager._paused = case["paused"]
        assert manager._ignore(mock_event) is case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "window_activate_event",
                "event_type": "window:activate",
                "event_config": {},
                "expected_result": False,
            },
            {
                "id": "mouse_button_event",
                "event_type": "mouse:button:1p",
                "event_config": {},
                "expected_result": False,
            },
            {
                "id": "focused_window_event",
                "event_type": "object:state-changed:focused",
                "event_config": {"is_window": True},
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_ignore_window_and_mouse_events(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager._ignore for window, mouse, and focused window events."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["event_type"]
        mock_event.source = test_context.Mock()

        if "is_window" in case["event_config"]:
            ax_utilities = essential_modules["orca.ax_utilities"]
            ax_utilities.is_window.return_value = case["event_config"]["is_window"]

        assert manager._ignore(mock_event) is case["expected_result"]

    def test_ignore_frame_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore for frame events."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.source = test_context.Mock()
        mock_event.any_data = test_context.Mock()
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        ax_utilities = essential_modules["orca.ax_utilities"]
        focus_mgr = essential_modules["focus_manager_instance"]

        focus_mgr.get_locus_of_focus.return_value = None
        ax_utilities.is_window.return_value = False
        test_context.patch("time.time", return_value=1000.0)
        manager._event_history = {}

        mock_app = test_context.Mock()
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=True
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="mutter-x11-frames"
        )
        assert manager._ignore(mock_event) is True

        regular_app = test_context.Mock()
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=True
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=regular_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )
        assert manager._ignore(mock_event) is False

    def test_ignore_text_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore for text-related events."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.source = test_context.Mock()
        mock_event.detail2 = 5001  # Large text insertion
        mock_event.any_data = test_context.Mock()
        mock_event.detail1 = 0
        ax_utilities = essential_modules["orca.ax_utilities"]
        focus_mgr = essential_modules["focus_manager_instance"]
        focus_mgr.get_locus_of_focus.return_value = None
        ax_utilities.is_window.return_value = False
        ax_utilities.is_frame.return_value = False
        ax_utilities.is_text.return_value = True  # This triggers text logic
        ax_utilities.is_notification.return_value = False
        ax_utilities.is_alert.return_value = False
        ax_utilities.is_selected.return_value = False
        ax_utilities.is_focused.return_value = False
        ax_utilities.is_section.return_value = False

        self._setup_ignore_event_ax_utilities_mocks(test_context, mock_time=5000.0, is_text=True)
        manager._event_history = {}

        mock_event.type = "object:text-changed:insert"
        result = manager._ignore(mock_event)
        assert result is True, f"Expected True but got {result}"

        mock_event.detail2 = 100
        assert manager._ignore(mock_event) is False

        mock_event.type = "object:text-changed:delete"
        assert manager._ignore(mock_event) is False

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "notification_event",
                "utility_method": "is_notification",
                "utility_value": True,
                "expected_result": False,
            },
            {
                "id": "alert_event",
                "utility_method": "is_alert",
                "utility_value": True,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_ignore_notification_and_alert_events(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager._ignore for notification and alert events."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.source = test_context.Mock()
        ax_utilities = essential_modules["orca.ax_utilities"]

        ax_utilities.is_notification.return_value = False
        ax_utilities.is_alert.return_value = False
        getattr(ax_utilities, case["utility_method"]).return_value = case["utility_value"]

        assert manager._ignore(mock_event) is case["expected_result"]

    def test_ignore_focus_and_selection_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore for focus and selection events."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.source = test_context.Mock()
        mock_event.any_data = test_context.Mock()
        ax_utilities = essential_modules["orca.ax_utilities"]
        focus_mgr = essential_modules["focus_manager_instance"]

        focus_mgr.get_locus_of_focus.return_value = mock_event.source
        assert manager._ignore(mock_event) is False

        focus_mgr.get_locus_of_focus.return_value = mock_event.any_data
        assert manager._ignore(mock_event) is False

        focus_mgr.get_locus_of_focus.return_value = test_context.Mock()
        ax_utilities.is_selected.return_value = True
        assert manager._ignore(mock_event) is False

    def test_ignore_focused_source_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore for events from focused sources."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.source = test_context.Mock()
        mock_event.detail1 = 1
        mock_event.detail2 = 0
        mock_event.any_data = test_context.Mock()
        focus_mgr = essential_modules["focus_manager_instance"]

        focus_mgr.get_locus_of_focus.return_value = None
        test_context.patch("time.time", return_value=3000.0)
        manager._event_history = {}

        mock_event.type = "object:test-event"
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=True
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        assert manager._ignore(mock_event) is False

        # - should not be ignored
        mock_event.type = "object:state-changed:focused"
        mock_event.detail1 = 1
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=True
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=True
        )
        assert manager._ignore(mock_event) is False

    def test_ignore_live_region_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore for live region events."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = test_context.Mock()
        mock_event.detail2 = 100
        ax_utilities = essential_modules["orca.ax_utilities"]
        ax_object = essential_modules["orca.ax_object"]
        focus_mgr = essential_modules["focus_manager_instance"]

        focus_mgr.get_locus_of_focus.return_value = test_context.Mock()
        ax_utilities.is_selected.return_value = False
        ax_utilities.is_focused.return_value = False
        ax_utilities.is_section.return_value = True

        ax_object.get_attribute.return_value = "polite"
        assert manager._ignore(mock_event) is False

        ax_object.get_attribute.return_value = "off"
        mock_app = test_context.Mock()
        ax_utilities.get_application.return_value = mock_app
        manager._event_history = {}
        assert manager._ignore(mock_event) is False

    def test_ignore_spam_filtering(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore spam filtering mechanism."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.source = test_context.Mock()
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.any_data = test_context.Mock()
        mock_app = test_context.Mock()
        original_hash = hash

        def mock_hash(obj):
            if obj is mock_app:
                return 12345
            return original_hash(obj)

        test_context.patch("builtins.hash", new=mock_hash)
        focus_mgr = essential_modules["focus_manager_instance"]
        focus_mgr.get_locus_of_focus.return_value = None

        manager._event_history = {}
        test_context.patch("time.time", return_value=100.0)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_attribute", return_value=None
        )
        test_context.patch(
            "orca.event_manager.focus_manager.get_manager", return_value=focus_mgr
        )
        assert manager._ignore(mock_event) is False

        test_context.patch("time.time", return_value=100.05)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_attribute", return_value=None
        )
        test_context.patch(
            "orca.event_manager.focus_manager.get_manager", return_value=focus_mgr
        )
        assert manager._ignore(mock_event) is True

        test_context.patch("time.time", return_value=100.2)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_attribute", return_value=None
        )
        test_context.patch(
            "orca.event_manager.focus_manager.get_manager", return_value=focus_mgr
        )
        assert manager._ignore(mock_event) is False

    def test_ignore_mutter_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore for mutter-x11-frames events."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.source = test_context.Mock()
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.any_data = test_context.Mock()
        mock_app = test_context.Mock()
        original_hash = hash

        def mock_hash(obj):
            if obj is mock_app:
                return 12345
            return original_hash(obj)

        test_context.patch("builtins.hash", new=mock_hash)
        focus_mgr = essential_modules["focus_manager_instance"]
        focus_mgr.get_locus_of_focus.return_value = None

        test_context.patch("time.time", return_value=100.0)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="mutter-x11-frames"
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_attribute", return_value=None
        )
        test_context.patch(
            "orca.event_manager.focus_manager.get_manager", return_value=focus_mgr
        )
        manager._event_history = {}
        assert manager._ignore(mock_event) is True

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "window_event",
                "event_type": "window:activate",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 0,
                "expected_priority": 2,
            },
            {
                "id": "active_frame",
                "event_type": "object:state-changed:active",
                "is_frame": True,
                "is_dialog_or_alert": False,
                "detail1": 0,
                "expected_priority": 2,
            },
            {
                "id": "active_dialog",
                "event_type": "object:state-changed:active",
                "is_frame": False,
                "is_dialog_or_alert": True,
                "detail1": 0,
                "expected_priority": 2,
            },
            {
                "id": "focused_event",
                "event_type": "object:state-changed:focused",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 0,
                "expected_priority": 3,
            },
            {
                "id": "active_descendant",
                "event_type": "object:active-descendant-changed",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 0,
                "expected_priority": 3,
            },
            {
                "id": "assertive_announcement",
                "event_type": "object:announcement",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 2,
                "expected_priority": 2,
            },
            {
                "id": "polite_announcement",
                "event_type": "object:announcement",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 1,
                "expected_priority": 3,
            },
            {
                "id": "other_announcement",
                "event_type": "object:announcement",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 3,
                "expected_priority": 4,
            },
            {
                "id": "invalid_entry",
                "event_type": "object:state-changed:invalid-entry",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 0,
                "expected_priority": 5,
            },
            {
                "id": "children_changed",
                "event_type": "object:children-changed:add",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 0,
                "expected_priority": 6,
            },
            {
                "id": "default_normal",
                "event_type": "object:text-changed:insert",
                "is_frame": False,
                "is_dialog_or_alert": False,
                "detail1": 0,
                "expected_priority": 4,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_priority_various_event_types(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager._get_priority with various event types and conditions."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["event_type"]
        mock_event.detail1 = case["detail1"]
        mock_event.source = test_context.Mock()

        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=case["is_frame"]
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_dialog_or_alert",
            return_value=case["is_dialog_or_alert"],
        )

        result = manager._get_priority(mock_event)
        assert result == case["expected_priority"]
        essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "notification_not_ignored",
                "source_role": "notification",
                "event_type": "object:text-changed:insert",
                "source_is_focused": False,
                "manages_descendants": False,
                "detail1": 0,
                "expected_ignore": False,
            },
            {
                "id": "alert_not_ignored",
                "source_role": "alert",
                "event_type": "object:text-changed:insert",
                "source_is_focused": False,
                "manages_descendants": False,
                "detail1": 0,
                "expected_ignore": False,
            },
            {
                "id": "large_text_insertion_ignored",
                "source_role": "text",
                "event_type": "object:text-changed:insert",
                "source_is_focused": False,
                "manages_descendants": False,
                "detail1": 5001,
                "expected_ignore": True,
            },
            {
                "id": "small_text_insertion_not_ignored",
                "source_role": "text",
                "event_type": "object:text-changed:insert",
                "source_is_focused": False,
                "manages_descendants": False,
                "detail1": 4999,
                "expected_ignore": False,
            },
            {
                "id": "focused_source_not_ignored",
                "source_role": "push_button",
                "event_type": "object:state-changed:focused",
                "source_is_focused": True,
                "manages_descendants": False,
                "detail1": 0,
                "expected_ignore": False,
            },
            {
                "id": "focused_managing_descendants_with_detail1",
                "source_role": "push_button",
                "event_type": "object:state-changed:focused",
                "source_is_focused": True,
                "manages_descendants": True,
                "detail1": 1,
                "expected_ignore": False,
            },
            {
                "id": "window_focused_event_ignored",
                "source_role": "window",
                "event_type": "object:state-changed:focused",
                "source_is_focused": False,
                "manages_descendants": False,
                "detail1": 0,
                "expected_ignore": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_ignore_event_conditions(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager._ignore with various event conditions."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        manager._event_history = {}

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["event_type"]
        mock_event.detail1 = case["detail1"]
        mock_event.detail2 = (
            0 if case["event_type"] != "object:text-changed:insert" else case["detail1"]
        )
        mock_event.source = test_context.Mock()
        mock_event.any_data = test_context.Mock()

        mock_app = test_context.Mock()
        focus_mgr = essential_modules["focus_manager_instance"]
        focus_mgr.get_locus_of_focus.return_value = None

        test_context.patch("time.time", return_value=100.0)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window",
            side_effect=lambda obj: (
                case["source_role"] == "window" if obj == mock_event.source else False
            ),
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text",
            side_effect=lambda obj: (
                case["source_role"] == "text" if obj == mock_event.source else False
            ),
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification",
            side_effect=lambda obj: case["source_role"] == "notification"
            if obj == mock_event.source
            else False,
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert",
            side_effect=lambda obj: (
                case["source_role"] == "alert" if obj == mock_event.source else False
            ),
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused",
            side_effect=lambda obj: (
                case["source_is_focused"] if obj == mock_event.source else False
            ),
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants",
            side_effect=lambda obj: (
                case["manages_descendants"] if obj == mock_event.source else False
            ),
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )

        result = manager._ignore(mock_event)
        assert result is case["expected_ignore"]

    def test_ignore_live_region_text_insertion(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore for live region text insertions."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        manager._event_history = {}

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.detail1 = 0
        mock_event.detail2 = 100
        mock_event.source = test_context.Mock()
        mock_event.any_data = test_context.Mock()

        mock_app = test_context.Mock()
        focus_mgr = essential_modules["focus_manager_instance"]
        focus_mgr.get_locus_of_focus.return_value = None

        test_context.patch("time.time", return_value=100.0)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=True
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_attribute",
            side_effect=lambda obj, attr: "polite" if attr == "live" else None,
        )

        result = manager._ignore(mock_event)
        assert result is False

    def test_ignore_event_history_filtering(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore with event history spam filtering."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        manager._event_history = {}

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.source = test_context.Mock()
        mock_event.any_data = test_context.Mock()

        mock_app = test_context.Mock()
        focus_mgr = essential_modules["focus_manager_instance"]
        focus_mgr.get_locus_of_focus.return_value = None

        original_hash = hash

        def mock_hash(obj):
            if obj is mock_app:
                return 12345
            return original_hash(obj)

        test_context.patch("builtins.hash", new=mock_hash)
        test_context.patch("time.time", return_value=100.0)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_attribute", return_value=None
        )

        # First call should not be ignored
        result1 = manager._ignore(mock_event)
        assert result1 is False
        assert manager._event_history["object:test-event"] == (12345, 100.0)

        # Second call within 0.1s should be ignored
        test_context.patch("time.time", return_value=100.05)
        result2 = manager._ignore(mock_event)
        assert result2 is True

    def test_is_obsoleted_by_identical_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._is_obsoleted_by with identical events in queue."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.source = test_context.Mock()
        mock_event.detail1 = 1
        mock_event.detail2 = 2
        mock_event.any_data = "test_data"

        identical_event = test_context.Mock(spec=Atspi.Event)
        identical_event.type = "object:test-event"
        identical_event.source = mock_event.source
        identical_event.detail1 = 1
        identical_event.detail2 = 2
        identical_event.any_data = "test_data"

        queue_data = [(4, 1, identical_event)]
        with manager._event_queue.mutex:
            manager._event_queue.queue = queue_data

        result = manager._is_obsoleted_by(mock_event)
        assert result == identical_event

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "active_descendant_obsoletes",
                "existing_type": "object:active-descendant-changed",
                "existing_source_same": True,
                "new_type": "object:active-descendant-changed",
                "should_obsolete": True,
            },
            {
                "id": "state_changed_obsoletes",
                "existing_type": "object:state-changed:focused",
                "existing_source_same": True,
                "new_type": "object:state-changed:focused",
                "should_obsolete": True,
            },
            {
                "id": "caret_moved_obsoletes",
                "existing_type": "object:text-caret-moved",
                "existing_source_same": True,
                "new_type": "object:text-caret-moved",
                "should_obsolete": True,
            },
            {
                "id": "window_activate_obsoletes",
                "existing_type": "window:activate",
                "existing_source_same": True,
                "new_type": "window:activate",
                "should_obsolete": True,
            },
            {
                "id": "non_skippable_does_not_obsolete",
                "existing_type": "object:other-event",
                "existing_source_same": True,
                "new_type": "object:other-event",
                "should_obsolete": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_obsoleted_by_same_type_and_object(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager._is_obsoleted_by with same type and object conditions."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_source = test_context.Mock()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["new_type"]
        mock_event.source = mock_source
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.any_data = None

        existing_event = test_context.Mock(spec=Atspi.Event)
        existing_event.type = case["existing_type"]
        existing_event.source = mock_source if case["existing_source_same"] else test_context.Mock()
        existing_event.detail1 = (
            0 if case["should_obsolete"] else 1
        )  # Make it different for non-obsoleting case
        existing_event.detail2 = 0
        existing_event.any_data = None

        queue_data = [(4, 1, existing_event)]
        with manager._event_queue.mutex:
            manager._event_queue.queue = queue_data

        result = manager._is_obsoleted_by(mock_event)
        if case["should_obsolete"]:
            assert result == existing_event
        else:
            assert result is None

    def test_is_obsoleted_by_sibling_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._is_obsoleted_by with sibling event conditions."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        parent_mock = test_context.Mock()
        mock_source = test_context.Mock()
        sibling_source = test_context.Mock()

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:state-changed:focused"
        mock_event.source = mock_source
        mock_event.detail1 = 1
        mock_event.detail2 = 2
        mock_event.any_data = "test_data"

        sibling_event = test_context.Mock(spec=Atspi.Event)
        sibling_event.type = "object:state-changed:focused"
        sibling_event.source = sibling_source
        sibling_event.detail1 = 1
        sibling_event.detail2 = 2
        sibling_event.any_data = "test_data"

        test_context.patch(
            "orca.event_manager.AXObject.get_parent",
            side_effect=lambda obj: parent_mock
            if obj in [mock_source, sibling_source]
            else test_context.Mock(),
        )

        queue_data = [(4, 1, sibling_event)]
        with manager._event_queue.mutex:
            manager._event_queue.queue = queue_data

        result = manager._is_obsoleted_by(mock_event)
        assert result == sibling_event

    def test_is_obsoleted_by_window_events(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._is_obsoleted_by with window event conditions."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_source = test_context.Mock()

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "window:activate"
        mock_event.source = mock_source
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.any_data = None

        existing_event = test_context.Mock(spec=Atspi.Event)
        existing_event.type = "window:activate"
        existing_event.source = mock_source
        existing_event.detail1 = 0
        existing_event.detail2 = 0
        existing_event.any_data = None

        queue_data = [(4, 1, existing_event)]
        with manager._event_queue.mutex:
            manager._event_queue.queue = queue_data

        result = manager._is_obsoleted_by(mock_event)
        assert result == existing_event

    def test_focus_conditions_in_ignore(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore focus-related conditions."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        manager._event_history = {}

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.source = test_context.Mock()
        mock_event.any_data = test_context.Mock()

        focus_mgr = essential_modules["focus_manager_instance"]

        focus_mgr.get_locus_of_focus.return_value = mock_event.source
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )

        result = manager._ignore(mock_event)
        assert result is False

        focus_mgr.get_locus_of_focus.return_value = mock_event.any_data
        result = manager._ignore(mock_event)
        assert result is False

    def test_ignore_selected_source_not_ignored(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._ignore does not ignore events from selected sources."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        manager._event_history = {}

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:test-event"
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.source = test_context.Mock()
        mock_event.any_data = test_context.Mock()

        mock_app = test_context.Mock()
        focus_mgr = essential_modules["focus_manager_instance"]
        focus_mgr.get_locus_of_focus.return_value = None

        test_context.patch("time.time", return_value=100.0)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_window", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_frame", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_text", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_notification", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_alert", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_selected",
            return_value=True,  # Selected source should not be ignored
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_focused", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.is_section", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.manages_descendants", return_value=False
        )
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_name", return_value="regular-app"
        )
        test_context.patch(
            "orca.event_manager.AXObject.get_attribute", return_value=None
        )

        result = manager._ignore(mock_event)
        assert result is False

    def test_queue_println(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._queue_println."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "test:event"
        debug_mock = essential_modules["orca.debug"]
        debug_mock.debugLevel = 10
        manager._queue_println(mock_event)
        manager._queue_println(mock_event, is_enqueue=False)

    def test_enqueue_object_event_ignored(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._enqueue_object_event for ignored events."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = False
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        manager._enqueue_object_event(mock_event)
        assert manager._event_queue.empty()

    def test_on_no_focus(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._on_no_focus."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_get_focus_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.focus_manager.get_manager", new=mock_get_focus_mgr
        )
        mock_get_script_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.script_manager.get_manager", new=mock_get_script_mgr
        )
        mock_braille = test_context.Mock()
        test_context.patch("orca.event_manager.braille", new=mock_braille)
        mock_focus_mgr = test_context.Mock()
        mock_script_mgr = test_context.Mock()
        mock_get_focus_mgr.return_value = mock_focus_mgr
        mock_get_script_mgr.return_value = mock_script_mgr

        mock_focus_mgr.focus_and_window_are_unknown.return_value = True
        result = manager._on_no_focus()
        assert result is False

        mock_focus_mgr.focus_and_window_are_unknown.return_value = False
        mock_script_mgr.get_active_script.return_value = None
        result = manager._on_no_focus()
        assert result is False
        mock_script_mgr.set_active_script.assert_called_once()
        mock_braille.disableBraille.assert_called_once()

    def test_dequeue_object_event_empty_queue(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._dequeue_object_event with empty queue."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        result = manager._dequeue_object_event()
        assert result is False
        assert manager._gidle_id == 0

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "first_registration",
                "operation": "register",
                "initial_count": 0,
                "expected_count": 1,
                "should_call_listener": True,
            },
            {
                "id": "duplicate_registration",
                "operation": "register",
                "initial_count": 1,
                "expected_count": 2,
                "should_call_listener": False,
            },
            {
                "id": "partial_deregistration",
                "operation": "deregister",
                "initial_count": 2,
                "expected_count": 1,
                "should_call_listener": False,
            },
            {
                "id": "final_deregistration",
                "operation": "deregister",
                "initial_count": 1,
                "expected_count": 0,
                "should_call_listener": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_listener_registration(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager register/deregister listener operations."""
        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._listener = test_context.Mock()
        event_type = "object:text-changed:insert"

        if case["initial_count"] > 0:
            manager._script_listener_counts[event_type] = case["initial_count"]

        if case["operation"] == "register":
            manager.register_listener(event_type)
            if case["should_call_listener"]:
                manager._listener.register.assert_called_once_with(event_type)
            else:
                manager._listener.register.assert_not_called()
        else:  # deregister
            manager.deregister_listener(event_type)
            if case["should_call_listener"]:
                manager._listener.deregister.assert_called_once_with(event_type)
            else:
                manager._listener.deregister.assert_not_called()

        if case["expected_count"] == 0:
            assert event_type not in manager._script_listener_counts
        else:
            assert manager._script_listener_counts[event_type] == case["expected_count"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "register_script_listeners", "operation": "register"},
            {"id": "deregister_script_listeners", "operation": "deregister"},
        ],
        ids=lambda case: case["id"],
    )
    def test_script_listeners_operations(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test EventManager register/deregister script listeners operations."""
        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_listener_method = test_context.Mock()
        method_name = f"{case['operation']}_listener"
        test_context.patch_object(manager, method_name, new=mock_listener_method)

        mock_script = test_context.Mock()
        mock_script.listeners = {
            "object:text-changed:insert": test_context.Mock(),
            "object:state-changed:focused": test_context.Mock(),
        }

        getattr(manager, f"{case['operation']}_script_listeners")(mock_script)

        expected_calls = [
            call("object:text-changed:insert"),
            call("object:state-changed:focused"),
        ]
        mock_listener_method.assert_has_calls(expected_calls, any_order=True)

    def test_get_script_for_event_focus(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._get_script_for_event for focused events."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.source = test_context.Mock()
        mock_event.type = "object:state-changed:focused"
        active_script = test_context.Mock()
        mock_get_focus_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.focus_manager.get_manager", new=mock_get_focus_mgr
        )
        mock_focus_mgr = test_context.Mock()
        mock_get_focus_mgr.return_value = mock_focus_mgr
        mock_focus_mgr.get_locus_of_focus.return_value = mock_event.source
        result = manager._get_script_for_event(mock_event, active_script)
        assert result == active_script

    def test_get_script_for_event_mouse(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._get_script_for_event for mouse events."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "mouse:button:1p"
        mock_event.source = test_context.Mock()
        expected_script = test_context.Mock()
        mock_mouse_event = test_context.Mock()
        mock_mouse_event.app = test_context.Mock()
        mock_mouse_event.window = test_context.Mock()
        mock_get_script_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.script_manager.get_manager", new=mock_get_script_mgr
        )
        test_context.patch(
            "orca.event_manager.input_event.MouseButtonEvent", return_value=mock_mouse_event
        )
        mock_script_mgr = test_context.Mock()
        mock_get_script_mgr.return_value = mock_script_mgr
        mock_script_mgr.get_script.return_value = expected_script
        result = manager._get_script_for_event(mock_event)
        assert result == expected_script

    def test_get_script_for_event_defunct_app(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._get_script_for_event with defunct application."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = test_context.Mock()
        mock_app = test_context.Mock()
        ax_utilities = essential_modules["orca.ax_utilities"]
        ax_utilities.get_application.return_value = mock_app
        ax_utilities.is_defunct.return_value = True
        result = manager._get_script_for_event(mock_event)
        assert result is None

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "focus_claimed",
                "event_type": "object:state-changed:focused",
                "detail1": 1,
                "expected": True,
                "reason_contains": "claimed focus",
            },
            {
                "id": "menu_selection",
                "event_type": "object:state-changed:selected",
                "detail1": 1,
                "expected": True,
                "reason_contains": "Selection change",
            },
            {
                "id": "modal_panel",
                "event_type": "object:state-changed:showing",
                "detail1": 0,
                "expected": True,
                "reason_contains": "Modal panel",
            },
            {
                "id": "no_activation",
                "event_type": "object:text-changed:insert",
                "detail1": 0,
                "expected": False,
                "reason_contains": "No reason",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_activatable_event(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test EventManager._is_activatable_event."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["event_type"]
        mock_event.detail1 = case["detail1"]
        mock_event.source = test_context.Mock()
        mock_script = test_context.Mock()
        mock_script.is_activatable_event.return_value = True
        mock_script.force_script_activation.return_value = False
        ax_utilities = essential_modules["orca.ax_utilities"]
        if case["event_type"] == "object:state-changed:selected":
            ax_utilities.is_menu.return_value = True
            ax_utilities.is_focusable.return_value = True
        elif case["event_type"] == "object:state-changed:showing":
            ax_utilities.is_panel.return_value = True
            ax_utilities.is_modal.return_value = True
        else:
            ax_utilities.is_frame.return_value = case["event_type"] == "object:state-changed:active"
        focus_mgr = essential_modules["focus_manager_instance"]
        if case["event_type"] == "window:activate":
            focus_mgr.get_active_window.return_value = mock_event.source
        else:
            focus_mgr.get_active_window.return_value = test_context.Mock()
        result, reason = manager._is_activatable_event(mock_event, mock_script)
        assert result == case["expected"]
        assert case["reason_contains"].lower() in reason.lower()

    def test_is_activatable_event_no_source(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._is_activatable_event with no event source."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.source = None
        result, reason = manager._is_activatable_event(mock_event)
        assert result is False
        assert "event.source" in reason

    def test_is_activatable_event_script_forces(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._is_activatable_event when script forces activation."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = test_context.Mock()
        mock_script = test_context.Mock()
        mock_script.is_activatable_event.return_value = True
        mock_script.force_script_activation.return_value = True
        result, reason = manager._is_activatable_event(mock_event, mock_script)
        assert result is True
        assert "insists" in reason

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "active_script",
                "event_script_is_active": True,
                "present_if_inactive": False,
                "is_progress_bar": False,
                "verbosity_all": False,
                "expected": True,
            },
            {
                "id": "inactive_but_presents",
                "event_script_is_active": False,
                "present_if_inactive": True,
                "is_progress_bar": False,
                "verbosity_all": False,
                "expected": True,
            },
            {
                "id": "progress_bar_all",
                "event_script_is_active": False,
                "present_if_inactive": False,
                "is_progress_bar": True,
                "verbosity_all": True,
                "expected": True,
            },
            {
                "id": "no_reason_to_process",
                "event_script_is_active": False,
                "present_if_inactive": False,
                "is_progress_bar": False,
                "verbosity_all": False,
                "expected": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_should_process_event(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test EventManager._should_process_event."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "test:event"
        mock_event.source = test_context.Mock()
        event_script = test_context.Mock()
        event_script.present_if_inactive = case["present_if_inactive"]
        if case["event_script_is_active"]:
            active_script = event_script
        else:
            active_script = test_context.Mock()
        mock_settings = test_context.Mock()
        test_context.patch("orca.event_manager.settings", new=mock_settings)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_progress_bar", return_value=case["is_progress_bar"]
        )
        if case["verbosity_all"]:
            mock_settings.progressBarVerbosity = mock_settings.PROGRESS_BAR_ALL
        else:
            mock_settings.progressBarVerbosity = 1
        result = manager._should_process_event(mock_event, event_script, active_script)
        assert result == case["expected"]

    def test_process_object_event_obsoleted(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._process_object_event with obsoleted event."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_is_obsoleted = test_context.Mock(return_value=test_context.Mock())
        test_context.patch_object(manager, "_is_obsoleted_by", new=mock_is_obsoleted)
        manager._process_object_event(mock_event)

    def test_process_object_event_dead_source(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._process_object_event with dead event source."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "window:deactivate"
        mock_event.source = test_context.Mock()
        mock_is_obsoleted = test_context.Mock(return_value=None)
        test_context.patch_object(manager, "_is_obsoleted_by", new=mock_is_obsoleted)
        test_context.patch("orca.event_manager.AXObject.is_dead", return_value=True)
        test_context.patch(
            "orca.event_manager.AXUtilities.is_defunct", return_value=False
        )
        mock_get_focus_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.focus_manager.get_manager", new=mock_get_focus_mgr
        )
        mock_get_script_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.script_manager.get_manager", new=mock_get_script_mgr
        )
        mock_focus_mgr = test_context.Mock()
        mock_script_mgr = test_context.Mock()
        mock_get_focus_mgr.return_value = mock_focus_mgr
        mock_get_script_mgr.return_value = mock_script_mgr
        mock_focus_mgr.get_active_window.return_value = mock_event.source
        manager._process_object_event(mock_event)

        mock_focus_mgr.clear_state.assert_called_once()
        mock_script_mgr.set_active_script.assert_called_once_with(
            None, "Active window is dead or defunct"
        )

    def test_process_object_event_no_listener(self, test_context: OrcaTestContext) -> None:
        """Test EventManager._process_object_event with no matching listener."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:unknown-event"
        mock_event.source = test_context.Mock()
        mock_is_obsoleted = test_context.Mock(return_value=None)
        test_context.patch_object(manager, "_is_obsoleted_by", new=mock_is_obsoleted)
        ax_object = essential_modules["orca.ax_object"]
        ax_utilities = essential_modules["orca.ax_utilities"]
        ax_object.is_dead.return_value = False
        ax_utilities.is_defunct.return_value = False
        ax_utilities.is_iconified.return_value = False
        mock_script = test_context.Mock()
        mock_script.listeners = {}
        script_mgr = essential_modules["script_manager_instance"]
        script_mgr.get_active_script.return_value = mock_script
        mock_get_script = test_context.Mock(return_value=mock_script)
        mock_is_activatable = test_context.Mock(return_value=(False, "test"))
        mock_should_process = test_context.Mock(return_value=True)
        test_context.patch_object(manager, "_get_script_for_event", new=mock_get_script)
        test_context.patch_object(manager, "_is_activatable_event", new=mock_is_activatable)
        test_context.patch_object(manager, "_should_process_event", new=mock_should_process)
        manager._process_object_event(mock_event)

    def test_get_manager(self, test_context: OrcaTestContext) -> None:
        """Test event_manager.get_manager."""

        self._setup_dependencies(test_context)
        from orca import event_manager

        manager1 = event_manager.get_manager()
        manager2 = event_manager.get_manager()

        assert manager1 is manager2
        assert isinstance(manager1, event_manager.EventManager)

    def test_enqueue_with_comprehensive_gidle_management(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test EventManager._enqueue_object_event with comprehensive GLib idle management."""

        self._setup_dependencies(test_context)
        from orca.event_manager import EventManager

        manager = EventManager()
        manager._active = True
        manager._paused = False
        manager._gidle_id = 0  # No existing idle handler
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "object:text-changed:insert"
        mock_event.source = test_context.Mock()
        mock_app = test_context.Mock()
        mock_script = test_context.Mock()
        mock_script.event_cache = {}

        mock_ignore = test_context.Mock(return_value=False)
        test_context.patch_object(manager, "_ignore", new=mock_ignore)
        test_context.patch(
            "orca.event_manager.AXUtilities.get_application", return_value=mock_app
        )
        mock_get_script_mgr = test_context.Mock()
        test_context.patch(
            "orca.event_manager.script_manager.get_manager", new=mock_get_script_mgr
        )
        mock_idle_add = test_context.Mock(return_value=456)
        test_context.patch("orca.event_manager.GLib.idle_add", new=mock_idle_add)
        test_context.patch("time.time", return_value=200.0)
        mock_script_mgr = test_context.Mock()
        mock_get_script_mgr.return_value = mock_script_mgr
        mock_script_mgr.get_script.return_value = mock_script
        manager._enqueue_object_event(mock_event)

        assert not manager._event_queue.empty()
        assert mock_event.type in mock_script.event_cache
        mock_idle_add.assert_called_once_with(manager._dequeue_object_event)
        assert manager._gidle_id == 456

        mock_idle_add.reset_mock()
        manager._gidle_id = 456
        test_context.patch("time.time", return_value=200.1)
        manager._enqueue_object_event(mock_event)

        mock_idle_add.assert_not_called()
        assert manager._gidle_id == 456
