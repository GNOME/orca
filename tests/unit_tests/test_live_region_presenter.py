# Unit tests for live_region_presenter.py methods.
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

"""Unit tests for live_region_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestLivePoliteness:
    """Test LivePoliteness enum."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Set up dependencies for live_region_presenter module testing."""

        additional_modules = ["gi", "gi.repository", "gi.repository.GLib"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        glib_mock = essential_modules["gi.repository.GLib"]
        glib_mock.timeout_add = test_context.Mock(return_value=1)

        return essential_modules

    def test_politeness_values(self, test_context: OrcaTestContext) -> None:
        """Test LivePoliteness enum values and properties."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LivePoliteness

        assert LivePoliteness.ASSERTIVE.priority == 0
        assert LivePoliteness.ASSERTIVE.name_str == "assertive"
        assert LivePoliteness.POLITE.priority == 1
        assert LivePoliteness.POLITE.name_str == "polite"
        assert LivePoliteness.OFF.priority == 2
        assert LivePoliteness.OFF.name_str == "off"

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            pytest.param("assertive", "ASSERTIVE", id="assertive"),
            pytest.param("polite", "POLITE", id="polite"),
            pytest.param("off", "OFF", id="off"),
            pytest.param("invalid", "OFF", id="invalid_defaults_to_off"),
            pytest.param(None, "OFF", id="none_defaults_to_off"),
        ],
    )
    def test_from_string(self, test_context: OrcaTestContext, input_str, expected) -> None:
        """Test LivePoliteness.from_string conversion."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LivePoliteness

        result = LivePoliteness.OFF.from_string(input_str)
        assert result.name == expected

    @pytest.mark.parametrize(
        "politeness,expected_str",
        [
            pytest.param("ASSERTIVE", "assertive", id="assertive"),
            pytest.param("POLITE", "polite", id="polite"),
            pytest.param("OFF", "off", id="off"),
        ],
    )
    def test_to_string(self, test_context: OrcaTestContext, politeness, expected_str) -> None:
        """Test LivePoliteness.to_string conversion."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LivePoliteness

        politeness_enum = getattr(LivePoliteness, politeness)
        assert politeness_enum.to_string() == expected_str


@pytest.mark.unit
class TestLiveRegionMessage:
    """Test LiveRegionMessage class."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Set up dependencies for live_region_presenter module testing."""

        additional_modules = ["gi", "gi.repository", "gi.repository.GLib"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        glib_mock = essential_modules["gi.repository.GLib"]
        glib_mock.timeout_add = test_context.Mock(return_value=1)

        return essential_modules

    def test_message_creation(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionMessage creation."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionMessage, LivePoliteness

        mock_obj = test_context.Mock()
        test_context.patch("time.time", return_value=1234567890.0)

        message = LiveRegionMessage(
            text="Test message", politeness=LivePoliteness.POLITE, obj=mock_obj
        )

        assert message.text == "Test message"
        assert message.politeness == LivePoliteness.POLITE
        assert message.obj == mock_obj
        assert message.timestamp == 1234567890.0

    def test_message_with_explicit_timestamp(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionMessage with explicit timestamp."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionMessage, LivePoliteness

        mock_obj = test_context.Mock()
        message = LiveRegionMessage(
            text="Test", politeness=LivePoliteness.ASSERTIVE, obj=mock_obj, timestamp=999.0
        )

        assert message.timestamp == 999.0

    @pytest.mark.parametrize(
        "politeness1,politeness2,timestamp1,timestamp2,expected_less_than",
        [
            pytest.param("ASSERTIVE", "POLITE", 100.0, 100.0, True, id="assertive_before_polite"),
            pytest.param("POLITE", "ASSERTIVE", 100.0, 100.0, False, id="polite_after_assertive"),
            pytest.param("POLITE", "POLITE", 100.0, 200.0, True, id="older_before_newer"),
            pytest.param("POLITE", "POLITE", 200.0, 100.0, False, id="newer_after_older"),
        ],
    )
    def test_message_comparison(
        self,
        test_context: OrcaTestContext,
        politeness1,
        politeness2,
        timestamp1,
        timestamp2,
        expected_less_than,
    ) -> None:
        """Test LiveRegionMessage comparison for priority queue ordering."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionMessage, LivePoliteness

        mock_obj = test_context.Mock()
        msg1 = LiveRegionMessage(
            text="Message 1",
            politeness=getattr(LivePoliteness, politeness1),
            obj=mock_obj,
            timestamp=timestamp1,
        )
        msg2 = LiveRegionMessage(
            text="Message 2",
            politeness=getattr(LivePoliteness, politeness2),
            obj=mock_obj,
            timestamp=timestamp2,
        )

        assert (msg1 < msg2) == expected_less_than

    @pytest.mark.parametrize(
        "text1,text2,time_diff,expected_duplicate",
        [
            pytest.param("Same", "Same", 0.1, True, id="duplicate_within_window"),
            pytest.param("Same", "Same", 0.25, True, id="duplicate_at_boundary"),
            pytest.param("Same", "Same", 0.26, False, id="not_duplicate_outside_window"),
            pytest.param("Different", "Text", 0.1, False, id="different_text"),
        ],
    )
    def test_is_duplicate_of(
        self, test_context: OrcaTestContext, text1, text2, time_diff, expected_duplicate
    ) -> None:
        """Test LiveRegionMessage.is_duplicate_of."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionMessage, LivePoliteness

        mock_obj = test_context.Mock()
        base_time = 1000.0

        msg1 = LiveRegionMessage(
            text=text1, politeness=LivePoliteness.POLITE, obj=mock_obj, timestamp=base_time
        )
        msg2 = LiveRegionMessage(
            text=text2,
            politeness=LivePoliteness.POLITE,
            obj=mock_obj,
            timestamp=base_time + time_diff,
        )

        assert msg2.is_duplicate_of(msg1) == expected_duplicate

    def test_is_duplicate_of_none(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionMessage.is_duplicate_of with None."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionMessage, LivePoliteness

        mock_obj = test_context.Mock()
        message = LiveRegionMessage(text="Test", politeness=LivePoliteness.POLITE, obj=mock_obj)

        assert message.is_duplicate_of(None) is False


@pytest.mark.unit
class TestLiveRegionMessageQueue:
    """Test LiveRegionMessageQueue class."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Set up dependencies for live_region_presenter module testing."""

        additional_modules = ["gi", "gi.repository", "gi.repository.GLib"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        glib_mock = essential_modules["gi.repository.GLib"]
        glib_mock.timeout_add = test_context.Mock(return_value=1)

        return essential_modules

    def test_queue_creation(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionMessageQueue creation."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionMessageQueue

        queue = LiveRegionMessageQueue(max_size=5)
        assert len(queue) == 0

    def test_enqueue_dequeue(self, test_context: OrcaTestContext) -> None:
        """Test basic enqueue and dequeue operations."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import (
            LiveRegionMessageQueue,
            LiveRegionMessage,
            LivePoliteness,
        )

        queue = LiveRegionMessageQueue(max_size=5)
        mock_obj = test_context.Mock()

        msg = LiveRegionMessage("Test", LivePoliteness.POLITE, mock_obj, timestamp=100.0)
        queue.enqueue(msg)

        assert len(queue) == 1
        dequeued = queue.dequeue()
        assert dequeued == msg
        assert len(queue) == 0

    def test_priority_ordering(self, test_context: OrcaTestContext) -> None:
        """Test messages are dequeued in priority order."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import (
            LiveRegionMessageQueue,
            LiveRegionMessage,
            LivePoliteness,
        )

        queue = LiveRegionMessageQueue(max_size=5)
        mock_obj = test_context.Mock()

        polite_msg = LiveRegionMessage("Polite", LivePoliteness.POLITE, mock_obj, timestamp=100.0)
        assertive_msg = LiveRegionMessage(
            "Assertive", LivePoliteness.ASSERTIVE, mock_obj, timestamp=200.0
        )

        queue.enqueue(polite_msg)
        queue.enqueue(assertive_msg)

        # Assertive should come out first
        first = queue.dequeue()
        assert first.text == "Assertive"
        second = queue.dequeue()
        assert second.text == "Polite"

    def test_max_size_enforcement(self, test_context: OrcaTestContext) -> None:
        """Test queue enforces max size limit."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import (
            LiveRegionMessageQueue,
            LiveRegionMessage,
            LivePoliteness,
        )

        queue = LiveRegionMessageQueue(max_size=3)
        mock_obj = test_context.Mock()

        for i in range(5):
            msg = LiveRegionMessage(
                f"Message {i}", LivePoliteness.POLITE, mock_obj, timestamp=float(i)
            )
            queue.enqueue(msg)

        assert len(queue) == 3

    def test_clear(self, test_context: OrcaTestContext) -> None:
        """Test queue clear operation."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import (
            LiveRegionMessageQueue,
            LiveRegionMessage,
            LivePoliteness,
        )

        queue = LiveRegionMessageQueue(max_size=5)
        mock_obj = test_context.Mock()

        for i in range(3):
            msg = LiveRegionMessage(f"Message {i}", LivePoliteness.POLITE, mock_obj)
            queue.enqueue(msg)

        assert len(queue) == 3
        queue.clear()
        assert len(queue) == 0

    def test_dequeue_empty_returns_none(self, test_context: OrcaTestContext) -> None:
        """Test dequeue on empty queue returns None."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionMessageQueue

        queue = LiveRegionMessageQueue(max_size=5)
        assert queue.dequeue() is None

    def test_purge_by_keep_alive(self, test_context: OrcaTestContext) -> None:
        """Test purge_by_keep_alive removes old messages."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import (
            LiveRegionMessageQueue,
            LiveRegionMessage,
            LivePoliteness,
        )

        queue = LiveRegionMessageQueue(max_size=10)
        mock_obj = test_context.Mock()

        current_time = 1000.0
        test_context.patch("time.time", return_value=current_time)

        # Add old message (older than MSG_KEEPALIVE_TIME)
        old_msg = LiveRegionMessage(
            "Old", LivePoliteness.POLITE, mock_obj, timestamp=current_time - 50
        )
        queue.enqueue(old_msg)

        # Add recent message
        new_msg = LiveRegionMessage(
            "New", LivePoliteness.POLITE, mock_obj, timestamp=current_time - 10
        )
        queue.enqueue(new_msg)

        assert len(queue) == 2
        queue.purge_by_keep_alive()
        assert len(queue) == 1

        remaining = queue.dequeue()
        assert remaining.text == "New"

    def test_purge_by_priority(self, test_context: OrcaTestContext) -> None:
        """Test purge_by_priority removes lower priority messages."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import (
            LiveRegionMessageQueue,
            LiveRegionMessage,
            LivePoliteness,
        )

        queue = LiveRegionMessageQueue(max_size=10)
        mock_obj = test_context.Mock()

        assertive_msg = LiveRegionMessage(
            "Assertive", LivePoliteness.ASSERTIVE, mock_obj, timestamp=100.0
        )
        polite_msg = LiveRegionMessage("Polite", LivePoliteness.POLITE, mock_obj, timestamp=200.0)
        off_msg = LiveRegionMessage("Off", LivePoliteness.OFF, mock_obj, timestamp=300.0)

        queue.enqueue(assertive_msg)
        queue.enqueue(polite_msg)
        queue.enqueue(off_msg)

        assert len(queue) == 3

        # Purge messages with priority >= POLITE (removes POLITE and OFF, keeps ASSERTIVE)
        queue.purge_by_priority(LivePoliteness.POLITE)
        assert len(queue) == 1

        remaining = queue.dequeue()
        assert remaining.text == "Assertive"


@pytest.mark.unit
class TestLiveRegionPresenter:
    """Test LiveRegionPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Set up dependencies for LiveRegionPresenter testing."""

        additional_modules = [
            "gi",
            "gi.repository",
            "gi.repository.GLib",
            "orca.cmdnames",
            "orca.dbus_service",
            "orca.debug",
            "orca.focus_manager",
            "orca.input_event",
            "orca.keybindings",
            "orca.messages",
            "orca.script_manager",
            "orca.settings_manager",
            "orca.AXObject",
            "orca.AXUtilities",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        glib_mock = essential_modules["gi.repository.GLib"]
        glib_mock.timeout_add = test_context.Mock(return_value=1)

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.LIVE_REGIONS_MONITOR = "toggleLiveRegionMonitoring"
        cmdnames_mock.LIVE_REGIONS_PREVIOUS = "presentPreviousLiveRegionMessage"
        cmdnames_mock.LIVE_REGIONS_ADVANCE_POLITENESS = "advanceLivePoliteness"
        cmdnames_mock.LIVE_REGIONS_ARE_ANNOUNCED = "toggleLiveRegionPresentation"
        cmdnames_mock.LIVE_REGIONS_NEXT = "presentNextLiveRegionMessage"

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(return_value=controller_mock)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_class = test_context.Mock()
        input_event_handler_instance = test_context.Mock()
        input_event_handler_class.return_value = input_event_handler_instance
        input_event_mock.InputEventHandler = input_event_handler_class

        keybindings_mock = essential_modules["orca.keybindings"]

        def create_keybindings_instance():
            instance = test_context.Mock()
            instance.is_empty = test_context.Mock(return_value=True)
            instance.remove_key_grabs = test_context.Mock()
            instance.add = test_context.Mock()
            instance.remove = test_context.Mock()
            instance.key_bindings = []
            return instance

        keybindings_mock.KeyBindings = test_context.Mock(side_effect=create_keybindings_instance)
        keybinding_instance = test_context.Mock()
        keybindings_mock.KeyBinding = test_context.Mock(return_value=keybinding_instance)
        keybindings_mock.DEFAULT_MODIFIER_MASK = 1
        keybindings_mock.NO_MODIFIER_MASK = 0
        keybindings_mock.ORCA_MODIFIER_MASK = 8

        messages_mock = essential_modules["orca.messages"]
        messages_mock.LIVE_REGIONS_SUPPORT_DISABLED = "Live regions support disabled"
        messages_mock.LIVE_REGIONS_LEVEL_POLITE = "Live regions set to polite"
        messages_mock.LIVE_REGIONS_LEVEL_ASSERTIVE = "Live regions set to assertive"
        messages_mock.LIVE_REGIONS_LEVEL_OFF = "Live regions set to off"
        messages_mock.LIVE_REGIONS_NO_MESSAGES = "No live region messages"
        messages_mock.LIVE_REGIONS_LIST_TOP = "Top of live region list"
        messages_mock.LIVE_REGIONS_LIST_BOTTOM = "Bottom of live region list"
        messages_mock.LIVE_REGIONS_ENABLED = "Live regions monitoring enabled"
        messages_mock.LIVE_REGIONS_DISABLED = "Live regions monitoring disabled"
        messages_mock.LIVE_REGIONS_ALL_OFF = "Live regions all off"
        messages_mock.LIVE_REGIONS_ALL_RESTORED = "Live regions restored"

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_instance = test_context.Mock()
        settings_instance.set_setting = test_context.Mock()
        settings_instance.override_key_bindings = test_context.Mock(
            side_effect=lambda handlers, bindings, is_desktop: bindings
        )
        settings_manager_mock.get_manager = test_context.Mock(return_value=settings_instance)

        # Set live region settings
        settings_mock = essential_modules["orca.settings"]
        settings_mock.inferLiveRegions = True
        settings_mock.presentLiveRegionFromInactiveTab = True

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_instance.get_locus_of_focus = test_context.Mock(return_value=None)
        focus_manager_mock.get_manager = test_context.Mock(return_value=focus_instance)

        script_manager_mock = essential_modules["orca.script_manager"]
        script_instance = test_context.Mock()
        script_instance.present_message = test_context.Mock()
        script_instance.utilities = test_context.Mock()
        script_manager_mock.get_manager = test_context.Mock()
        script_manager_mock.get_manager.return_value.get_active_script = test_context.Mock(
            return_value=script_instance
        )

        axobject_mock = essential_modules["orca.AXObject"]
        axobject_mock.get_attributes_dict = test_context.Mock(return_value={})
        axobject_mock.get_name = test_context.Mock(return_value="")
        axobject_mock.find_ancestor = test_context.Mock(return_value=None)
        axobject_mock.find_ancestor_inclusive = test_context.Mock(return_value=None)

        axutilities_mock = essential_modules["orca.AXUtilities"]
        axutilities_mock.is_live_region = test_context.Mock(return_value=True)
        axutilities_mock.is_aria_alert = test_context.Mock(return_value=False)
        axutilities_mock.get_focused_object = test_context.Mock(return_value=None)
        axutilities_mock.find_all_live_regions = test_context.Mock(return_value=[])

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.__init__."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()

        assert presenter.msg_queue is not None
        assert len(presenter.msg_queue) == 0
        assert presenter._suspended is False
        assert isinstance(presenter._handlers, dict)
        assert len(presenter.msg_cache) == 0
        assert presenter._monitoring is True
        assert presenter._current_index == 9  # QUEUE_SIZE

    @pytest.mark.parametrize(
        "refresh",
        [
            pytest.param(True, id="refresh_true"),
            pytest.param(False, id="empty_bindings"),
        ],
    )
    def test_get_bindings(self, test_context: OrcaTestContext, refresh: bool) -> None:
        """Test LiveRegionPresenter.get_bindings."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        bindings = presenter.get_bindings(refresh=refresh, is_desktop=True)
        assert bindings is not None

    @pytest.mark.parametrize(
        "refresh,check_handler_names",
        [
            pytest.param(True, True, id="refresh_true"),
            pytest.param(False, False, id="no_refresh"),
        ],
    )
    def test_get_handlers(
        self, test_context: OrcaTestContext, refresh: bool, check_handler_names: bool
    ) -> None:
        """Test LiveRegionPresenter.get_handlers."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        handlers = presenter.get_handlers(refresh=refresh)

        assert isinstance(handlers, dict)
        assert len(handlers) == 5

        if check_handler_names:
            expected_handlers = [
                "toggle_live_region_support",
                "present_previous_live_region_message",
                "advance_live_politeness",
                "toggle_live_region_presentation",
                "present_next_live_region_message",
            ]
            for handler_name in expected_handlers:
                assert handler_name in handlers

    def test_suspend_commands(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.suspend_commands."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_script.key_bindings = test_context.Mock()
        mock_script.key_bindings.remove = test_context.Mock()
        mock_script.key_bindings.add = test_context.Mock()

        assert presenter._suspended is False
        presenter.suspend_commands(mock_script, True, "Test suspend")
        assert presenter._suspended is True

    def test_reset(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.reset."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        presenter._politeness_overrides = {123: "test"}
        presenter.reset()
        assert not presenter._politeness_overrides

    def test_get_is_enabled(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.get_is_enabled."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        essential_modules["orca.settings"].enableLiveRegions = True

        presenter = LiveRegionPresenter()
        assert presenter.get_is_enabled() is True

    def test_set_is_enabled(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.set_is_enabled."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.live_region_presenter import LiveRegionPresenter

        essential_modules["orca.settings"].enableLiveRegions = False
        essential_modules["orca.settings_manager"].get_manager.return_value

        presenter = LiveRegionPresenter()
        result = presenter.set_is_enabled(True)

        assert result is True
        assert settings_mock.enableLiveRegions

    def test_toggle_monitoring_enable(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.toggle_monitoring enables monitoring."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        essential_modules["orca.settings"].enableLiveRegions = False

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        mock_event = test_context.Mock()

        result = presenter.toggle_monitoring(mock_script, mock_event)

        assert result is True
        mock_script.present_message.assert_called_with("Live regions monitoring enabled")

    def test_toggle_monitoring_disable(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.toggle_monitoring disables monitoring."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        essential_modules["orca.settings"].enableLiveRegions = True

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        mock_event = test_context.Mock()

        result = presenter.toggle_monitoring(mock_script, mock_event)

        assert result is True
        mock_script.present_message.assert_called_with("Live regions monitoring disabled")

    def test_flush_messages(self, test_context: OrcaTestContext) -> None:
        """Test LiveRegionPresenter.flush_messages."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import (
            LiveRegionPresenter,
            LiveRegionMessage,
            LivePoliteness,
        )

        presenter = LiveRegionPresenter()
        mock_obj = test_context.Mock()
        msg = LiveRegionMessage("Test", LivePoliteness.POLITE, mock_obj)
        presenter.msg_queue.enqueue(msg)

        assert len(presenter.msg_queue) > 0
        presenter.flush_messages()
        assert len(presenter.msg_queue) == 0

    def test_present_previous_live_region_message_no_messages(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test present_previous_live_region_message with no messages."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()

        result = presenter.present_previous_live_region_message(mock_script, None)

        assert result is True
        mock_script.present_message.assert_called_with("No live region messages")

    def test_present_previous_live_region_message_disabled(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test present_previous_live_region_message when disabled."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        essential_modules["orca.settings"].enableLiveRegions = False

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()

        result = presenter.present_previous_live_region_message(mock_script, None)

        assert result is False
        mock_script.present_message.assert_called_with("Live regions support disabled")

    def test_present_next_live_region_message_no_messages(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test present_next_live_region_message with no messages."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()

        result = presenter.present_next_live_region_message(mock_script, None)

        assert result is True
        mock_script.present_message.assert_called_with("No live region messages")

    def test_go_last_live_region_no_message(self, test_context: OrcaTestContext) -> None:
        """Test go_last_live_region with no last message."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()

        result = presenter.go_last_live_region(mock_script, None)
        assert result is False

    def test_is_presentable_live_region_event_wrong_type(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test is_presentable_live_region_event with wrong event type."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_event.type = "object:state-changed:focused"
        mock_event.source = test_context.Mock()

        result = presenter.is_presentable_live_region_event(mock_script, mock_event)
        assert result is False

    def test_is_presentable_live_region_event_disabled(self, test_context: OrcaTestContext) -> None:
        """Test is_presentable_live_region_event when presenter is disabled."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter

        essential_modules["orca.settings"].enableLiveRegions = False

        presenter = LiveRegionPresenter()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_event.type = "object:text-changed:insert"
        mock_event.source = test_context.Mock()

        result = presenter.is_presentable_live_region_event(mock_script, mock_event)
        assert result is False

    def test_is_presentable_live_region_event_not_live_region(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test is_presentable_live_region_event when source is not a live region."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import LiveRegionPresenter
        from orca import ax_utilities

        presenter = LiveRegionPresenter()
        test_context.patch_object(ax_utilities.AXUtilities, "is_live_region", return_value=False)

        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_event.type = "object:text-changed:insert"
        mock_event.source = test_context.Mock()

        result = presenter.is_presentable_live_region_event(mock_script, mock_event)
        assert result is False


@pytest.mark.unit
class TestLiveRegionPresenterModule:
    """Test module-level functions."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Set up dependencies for live_region_presenter module testing."""

        additional_modules = [
            "gi",
            "gi.repository",
            "gi.repository.GLib",
            "orca.cmdnames",
            "orca.dbus_service",
            "orca.debug",
            "orca.focus_manager",
            "orca.input_event",
            "orca.keybindings",
            "orca.messages",
            "orca.script_manager",
            "orca.settings_manager",
            "orca.AXObject",
            "orca.AXUtilities",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        glib_mock = essential_modules["gi.repository.GLib"]
        glib_mock.timeout_add = test_context.Mock(return_value=1)

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(return_value=controller_mock)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        essential_modules["orca.cmdnames"].LIVE_REGIONS_MONITOR = "test"
        essential_modules["orca.cmdnames"].LIVE_REGIONS_PREVIOUS = "test"
        essential_modules["orca.cmdnames"].LIVE_REGIONS_ADVANCE_POLITENESS = "test"
        essential_modules["orca.cmdnames"].LIVE_REGIONS_ARE_ANNOUNCED = "test"
        essential_modules["orca.cmdnames"].LIVE_REGIONS_NEXT = "test"

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_class = test_context.Mock()
        input_event_handler_instance = test_context.Mock()
        input_event_handler_class.return_value = input_event_handler_instance
        input_event_mock.InputEventHandler = input_event_handler_class

        keybindings_mock = essential_modules["orca.keybindings"]

        def create_keybindings_instance():
            instance = test_context.Mock()
            instance.is_empty = test_context.Mock(return_value=True)
            instance.remove_key_grabs = test_context.Mock()
            instance.add = test_context.Mock()
            instance.remove = test_context.Mock()
            instance.key_bindings = []
            return instance

        keybindings_mock.KeyBindings = test_context.Mock(side_effect=create_keybindings_instance)
        keybindings_mock.KeyBinding = test_context.Mock()
        keybindings_mock.DEFAULT_MODIFIER_MASK = 1
        keybindings_mock.NO_MODIFIER_MASK = 0
        keybindings_mock.ORCA_MODIFIER_MASK = 8

        essential_modules["orca.messages"].LIVE_REGIONS_SUPPORT_DISABLED = "test"

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_instance = test_context.Mock()
        settings_instance.set_setting = test_context.Mock()
        settings_instance.override_key_bindings = test_context.Mock(
            side_effect=lambda handlers, bindings, is_desktop: bindings
        )
        settings_manager_mock.get_manager = test_context.Mock(return_value=settings_instance)

        # Set live region settings
        settings_mock = essential_modules["orca.settings"]
        settings_mock.inferLiveRegions = True
        settings_mock.presentLiveRegionFromInactiveTab = True

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_instance.get_locus_of_focus = test_context.Mock(return_value=None)
        focus_manager_mock.get_manager = test_context.Mock(return_value=focus_instance)

        script_manager_mock = essential_modules["orca.script_manager"]
        script_instance = test_context.Mock()
        script_manager_mock.get_manager = test_context.Mock()
        script_manager_mock.get_manager.return_value.get_active_script = test_context.Mock(
            return_value=script_instance
        )

        axobject_mock = essential_modules["orca.AXObject"]
        axobject_mock.get_attributes_dict = test_context.Mock(return_value={})
        axobject_mock.get_name = test_context.Mock(return_value="")
        axobject_mock.find_ancestor = test_context.Mock(return_value=None)
        axobject_mock.find_ancestor_inclusive = test_context.Mock(return_value=None)

        axutilities_mock = essential_modules["orca.AXUtilities"]
        axutilities_mock.is_live_region = test_context.Mock(return_value=True)
        axutilities_mock.is_aria_alert = test_context.Mock(return_value=False)
        axutilities_mock.get_focused_object = test_context.Mock(return_value=None)
        axutilities_mock.find_all_live_regions = test_context.Mock(return_value=[])

        return essential_modules

    def test_get_presenter(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter function returns singleton."""

        _ = self._setup_dependencies(test_context)
        from orca.live_region_presenter import get_presenter

        presenter1 = get_presenter()
        assert presenter1 is not None
        assert presenter1.msg_queue is not None

        presenter2 = get_presenter()
        assert presenter1 is presenter2
