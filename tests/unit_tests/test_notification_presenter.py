# Unit tests for notification_presenter.py methods.
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

"""Unit tests for notification_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext

@pytest.mark.unit
class TestNotificationPresenter:
    """Test NotificationPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Returns all dependencies needed for NotificationPresenter testing."""

        additional_modules = ["gi", "gi.repository", "gi.repository.GObject", "gi.repository.Gtk"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        gobject_mock = essential_modules["gi.repository.GObject"]
        gobject_mock.TYPE_STRING = str

        gtk_mock = essential_modules["gi.repository.Gtk"]

        gtk_mock.DialogFlags = test_context.Mock()
        gtk_mock.DialogFlags.MODAL = 1
        gtk_mock.ResponseType = test_context.Mock()
        gtk_mock.ResponseType.APPLY = -10
        gtk_mock.ResponseType.CLOSE = -7
        gtk_mock.STOCK_CLEAR = "gtk-clear"
        gtk_mock.STOCK_CLOSE = "gtk-close"

        dialog_mock = test_context.Mock()
        dialog_mock.set_default_size = test_context.Mock()
        dialog_mock.get_content_area = test_context.Mock()
        dialog_mock.connect = test_context.Mock()
        dialog_mock.show_all = test_context.Mock()
        dialog_mock.present_with_time = test_context.Mock()
        dialog_mock.destroy = test_context.Mock()

        content_area_mock = test_context.Mock()
        content_area_mock.add = test_context.Mock()
        dialog_mock.get_content_area.return_value = content_area_mock

        grid_mock = test_context.Mock()
        scrolled_window_mock = test_context.Mock()
        scrolled_window_mock.add = test_context.Mock()

        tree_view_mock = test_context.Mock()
        tree_view_mock.set_hexpand = test_context.Mock()
        tree_view_mock.set_vexpand = test_context.Mock()
        tree_view_mock.append_column = test_context.Mock()
        tree_view_mock.set_model = test_context.Mock()

        cell_renderer_mock = test_context.Mock()
        tree_column_mock = test_context.Mock()
        tree_column_mock.set_sort_column_id = test_context.Mock()

        list_store_mock = test_context.Mock()
        list_store_mock.append = test_context.Mock(return_value="mock_iter")
        list_store_mock.set_value = test_context.Mock()
        list_store_mock.clear = test_context.Mock()

        gtk_mock.Dialog = test_context.Mock(return_value=dialog_mock)
        gtk_mock.Grid = test_context.Mock(return_value=grid_mock)
        gtk_mock.ScrolledWindow = test_context.Mock(return_value=scrolled_window_mock)
        gtk_mock.TreeView = test_context.Mock(return_value=tree_view_mock)
        gtk_mock.CellRendererText = test_context.Mock(return_value=cell_renderer_mock)
        gtk_mock.TreeViewColumn = test_context.Mock(return_value=tree_column_mock)
        gtk_mock.ListStore = test_context.Mock(return_value=list_store_mock)

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.NOTIFICATION_MESSAGES_LAST = "presentLastNotification"
        cmdnames_mock.NOTIFICATION_MESSAGES_NEXT = "presentNextNotification"
        cmdnames_mock.NOTIFICATION_MESSAGES_PREVIOUS = "presentPreviousNotification"
        cmdnames_mock.NOTIFICATION_MESSAGES_LIST = "showNotificationsList"

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(
            return_value=controller_mock
        )
        dbus_service_mock.command = lambda func: func

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        guilabels_mock = essential_modules["orca.guilabels"]
        guilabels_mock.notifications_count = test_context.Mock(
            return_value="Notifications (2)"
        )
        guilabels_mock.NOTIFICATIONS_COLUMN_HEADER = "Message"
        guilabels_mock.NOTIFICATIONS_RECEIVED_TIME = "Time"

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_class = test_context.Mock()
        input_event_handler_instance = test_context.Mock()
        input_event_handler_class.return_value = input_event_handler_instance
        input_event_mock.InputEventHandler = input_event_handler_class
        input_event_mock.InputEvent = test_context.mocker.MagicMock

        keybindings_mock = essential_modules["orca.keybindings"]

        def create_keybindings_instance():
            instance = test_context.Mock()
            instance.is_empty = test_context.Mock(return_value=True)
            instance.remove_key_grabs = test_context.Mock()
            instance.add = test_context.Mock()
            return instance

        keybindings_mock.KeyBindings = test_context.Mock(
            side_effect=create_keybindings_instance
        )
        keybinding_instance = test_context.Mock()
        keybindings_mock.KeyBinding = test_context.Mock(return_value=keybinding_instance)
        keybindings_mock.DEFAULT_MODIFIER_MASK = 1
        keybindings_mock.NO_MODIFIER_MASK = 0

        messages_mock = essential_modules["orca.messages"]
        messages_mock.NOTIFICATION_NO_MESSAGES = "No notification messages"
        messages_mock.NOTIFICATION_LIST_TOP = "Beginning of notification list"
        messages_mock.NOTIFICATION_LIST_BOTTOM = "End of notification list"
        messages_mock.seconds_ago = lambda x: f"{int(x)} seconds ago"
        messages_mock.minutes_ago = lambda x: f"{x} minutes ago"
        messages_mock.hours_ago = lambda x: f"{x} hours ago"
        messages_mock.days_ago = lambda x: f"{x} days ago"

        essential_modules["dialog"] = dialog_mock
        essential_modules["list_store"] = list_store_mock
        essential_modules["tree_view"] = tree_view_mock

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.__init__."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_controller = test_context.Mock()
        mock_get_controller = test_context.patch(
            "orca.notification_presenter.dbus_service.get_remote_controller",
            return_value=mock_controller,
        )
        presenter = NotificationPresenter()

        assert presenter._gui is None
        assert isinstance(presenter._handlers, dict)
        assert presenter._max_size == 55
        assert presenter._notifications == []
        assert presenter._current_index == -1

        mock_get_controller.assert_called()
        mock_controller.register_decorated_module.assert_called()

    @pytest.mark.parametrize(
        "refresh",
        [
            pytest.param(True, id="refresh_true"),
            pytest.param(False, id="empty_bindings"),
        ],
    )
    def test_get_bindings(self, test_context: OrcaTestContext, refresh: bool) -> None:
        """Test NotificationPresenter.get_bindings with various refresh settings."""
        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        bindings = presenter.get_bindings(refresh=refresh, is_desktop=bool(refresh))
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
        """Test NotificationPresenter.get_handlers with various refresh settings."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        handlers = presenter.get_handlers(refresh=refresh)

        assert isinstance(handlers, dict)
        assert len(handlers) == 4

        if check_handler_names:
            expected_handlers = [
                "present_last_notification",
                "present_next_notification",
                "present_previous_notification",
                "show_notification_list",
            ]
            for handler_name in expected_handlers:
                assert handler_name in handlers

    def test_save_notification_basic(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.save_notification."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        test_message = "Test notification message"
        test_context.patch("time.time", return_value=1234567890)
        presenter.save_notification(test_message)

        assert len(presenter._notifications) == 1
        message, timestamp = presenter._notifications[0]
        assert message == test_message
        assert timestamp == 1234567890

    def test_save_notification_max_size_limit(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.save_notification respects max size limit."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        presenter._max_size = 3

        test_context.patch("time.time", return_value=1234567890)
        presenter.save_notification("Message 1")
        presenter.save_notification("Message 2")
        presenter.save_notification("Message 3")
        presenter.save_notification("Message 4")

        assert len(presenter._notifications) == 3
        messages = [msg for msg, _ in presenter._notifications]
        assert messages == ["Message 2", "Message 3", "Message 4"]

    def test_clear_list(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.clear_list."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        presenter._notifications = [("Test 1", 123.0), ("Test 2", 456.0)]
        presenter._current_index = -2
        presenter.clear_list()

        assert presenter._notifications == []
        assert presenter._current_index == -1

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter._setup_handlers."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        len(presenter._handlers)
        presenter._setup_handlers()

        assert len(presenter._handlers) == 4

    def test_setup_bindings(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter._setup_bindings."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        presenter._setup_bindings()

    @pytest.mark.parametrize(
        "time_diff, expected_result",
        [
            pytest.param(30, "30 seconds ago", id="thirty_seconds"),
            pytest.param(90, "2 minutes ago", id="ninety_seconds"),
            pytest.param(1800, "30 minutes ago", id="thirty_minutes"),
            pytest.param(7200, "2 hours ago", id="two_hours"),
            pytest.param(90000, "1 days ago", id="one_day"),
        ],
    )
    def test_timestamp_to_string(self, test_context, time_diff, expected_result) -> None:
        """Test NotificationPresenter._timestamp_to_string."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        current_time = 1234567890
        test_timestamp = current_time - time_diff
        test_context.patch("time.time", return_value=current_time)
        result = presenter._timestamp_to_string(test_timestamp)
        assert result == expected_result

    def test_present_last_notification_no_messages(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.present_last_notification with no messages."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        result = presenter.present_last_notification(mock_script, None, True)

        assert result is True
        mock_script.present_message.assert_called_once_with("No notification messages")

    def test_present_last_notification_with_messages(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.present_last_notification with messages."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890
        test_message = "Last notification"

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification(test_message)

        test_context.patch("time.time", return_value=current_time)
        result = presenter.present_last_notification(mock_script, None, True)

        assert result is True
        mock_script.present_message.assert_called_once_with(f"{test_message} 1 minutes ago")
        assert presenter._current_index == -1

    def test_present_last_notification_no_notify(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.present_last_notification with notify_user=False."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        result = presenter.present_last_notification(mock_script, None, False)

        assert result is True
        mock_script.present_message.assert_not_called()

    def test_present_previous_notification_no_messages(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.present_previous_notification with no messages."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        result = presenter.present_previous_notification(mock_script, None, True)

        assert result is True
        mock_script.present_message.assert_called_once_with("No notification messages")

    def test_present_previous_notification_at_top(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.present_previous_notification at list top."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification("Message 1")
        presenter.save_notification("Message 2")
        presenter._current_index = 0
        test_context.patch("time.time", return_value=current_time)
        result = presenter.present_previous_notification(mock_script, None, True)

        assert result is True
        assert mock_script.present_message.call_count == 2
        mock_script.present_message.assert_any_call("Beginning of notification list")
        mock_script.present_message.assert_any_call("Message 1 1 minutes ago")

    def test_present_previous_notification_normal_navigation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test NotificationPresenter.present_previous_notification normal navigation."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification("Message 1")
        presenter.save_notification("Message 2")
        presenter._current_index = -1
        test_context.patch("time.time", return_value=current_time)
        result = presenter.present_previous_notification(mock_script, None, True)

        assert result is True
        assert presenter._current_index == -2
        mock_script.present_message.assert_called_once_with("Message 1 1 minutes ago")

    @pytest.mark.parametrize(
        "method_name,start_index",
        [
            pytest.param("present_previous_notification", -1, id="previous_index_error"),
            pytest.param("present_next_notification", 0, id="next_index_error"),
        ],
    )
    def test_navigation_index_error(
        self, test_context: OrcaTestContext, method_name, start_index
    ) -> None:
        """Test notification navigation methods handle IndexError scenarios."""
        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification("Message 1")
        presenter._current_index = start_index

        original_notifications = presenter._notifications.copy()
        presenter._notifications = []
        test_context.patch("time.time", return_value=current_time)

        method = getattr(presenter, method_name)
        result = method(mock_script, None, True)

        presenter._notifications = original_notifications
        assert result is True
        mock_script.present_message.assert_called_with("No notification messages")

    def test_present_next_notification_no_messages(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.present_next_notification with no messages."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        result = presenter.present_next_notification(mock_script, None, True)

        assert result is True
        mock_script.present_message.assert_called_once_with("No notification messages")

    def test_present_next_notification_at_bottom(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.present_next_notification at list bottom."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification("Message 1")
        presenter.save_notification("Message 2")
        presenter._current_index = -1
        test_context.patch("time.time", return_value=current_time)
        result = presenter.present_next_notification(mock_script, None, True)

        assert result is True
        assert mock_script.present_message.call_count == 2
        mock_script.present_message.assert_any_call("End of notification list")
        mock_script.present_message.assert_any_call("Message 2 1 minutes ago")

    def test_present_next_notification_normal_navigation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test NotificationPresenter.present_next_notification normal navigation."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification("Message 1")
        presenter.save_notification("Message 2")
        presenter._current_index = -2
        test_context.patch("time.time", return_value=current_time)
        result = presenter.present_next_notification(mock_script, None, True)

        assert result is True
        assert presenter._current_index == -1
        mock_script.present_message.assert_called_once_with("Message 2 1 minutes ago")

    def test_show_notification_list_no_messages(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.show_notification_list with no messages."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        result = presenter.show_notification_list(mock_script, None, True)

        assert result is True
        mock_script.present_message.assert_called_once_with("No notification messages")

    def test_show_notification_list_create_gui(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.show_notification_list creates GUI."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification("Message 1")
        presenter.save_notification("Message 2")
        test_context.patch("time.time", return_value=current_time)
        result = presenter.show_notification_list(mock_script, None, True)

        assert result is True
        assert presenter._gui is not None

    def test_show_notification_list_existing_gui(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.show_notification_list with existing GUI."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = NotificationPresenter()
        current_time = 1234567890

        test_context.patch("time.time", return_value=current_time - 60)
        presenter.save_notification("Message 1")

        mock_gui = test_context.Mock()
        mock_gui.show_gui = test_context.Mock()
        presenter._gui = mock_gui
        test_context.patch("time.time", return_value=current_time)
        result = presenter.show_notification_list(mock_script, None, True)

        assert result is True
        assert presenter._gui is mock_gui
        mock_gui.show_gui.assert_called_once()

    def test_on_dialog_destroyed(self, test_context: OrcaTestContext) -> None:
        """Test NotificationPresenter.on_dialog_destroyed."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import NotificationPresenter

        presenter = NotificationPresenter()
        mock_dialog = test_context.Mock()
        presenter._gui = test_context.Mock()
        presenter.on_dialog_destroyed(mock_dialog)

        assert presenter._gui is None


@pytest.mark.unit
class TestNotificationListGUI:
    """Test NotificationListGUI class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Returns all dependencies needed for NotificationPresenter testing."""

        additional_modules = ["gi", "gi.repository", "gi.repository.GObject", "gi.repository.Gtk"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        gobject_mock = essential_modules["gi.repository.GObject"]
        gobject_mock.TYPE_STRING = str

        gtk_mock = essential_modules["gi.repository.Gtk"]

        gtk_mock.DialogFlags = test_context.Mock()
        gtk_mock.DialogFlags.MODAL = 1
        gtk_mock.ResponseType = test_context.Mock()
        gtk_mock.ResponseType.APPLY = -10
        gtk_mock.ResponseType.CLOSE = -7
        gtk_mock.STOCK_CLEAR = "gtk-clear"
        gtk_mock.STOCK_CLOSE = "gtk-close"

        dialog_mock = test_context.Mock()
        dialog_mock.set_default_size = test_context.Mock()
        dialog_mock.get_content_area = test_context.Mock()
        dialog_mock.connect = test_context.Mock()
        dialog_mock.show_all = test_context.Mock()
        dialog_mock.present_with_time = test_context.Mock()
        dialog_mock.destroy = test_context.Mock()

        content_area_mock = test_context.Mock()
        content_area_mock.add = test_context.Mock()
        dialog_mock.get_content_area.return_value = content_area_mock

        grid_mock = test_context.Mock()
        scrolled_window_mock = test_context.Mock()
        scrolled_window_mock.add = test_context.Mock()

        tree_view_mock = test_context.Mock()
        tree_view_mock.set_hexpand = test_context.Mock()
        tree_view_mock.set_vexpand = test_context.Mock()
        tree_view_mock.append_column = test_context.Mock()
        tree_view_mock.set_model = test_context.Mock()

        list_store_mock = test_context.Mock()
        list_store_mock.clear = test_context.Mock()
        list_store_mock.append = test_context.Mock()

        tree_view_column_mock = test_context.Mock()
        cell_renderer_text_mock = test_context.Mock()

        gtk_mock.Dialog = test_context.Mock(return_value=dialog_mock)
        gtk_mock.Grid = test_context.Mock(return_value=grid_mock)
        gtk_mock.ScrolledWindow = test_context.Mock(return_value=scrolled_window_mock)
        gtk_mock.TreeView = test_context.Mock(return_value=tree_view_mock)
        gtk_mock.ListStore = test_context.Mock(return_value=list_store_mock)
        gtk_mock.TreeViewColumn = test_context.Mock(return_value=tree_view_column_mock)
        gtk_mock.CellRendererText = test_context.Mock(return_value=cell_renderer_text_mock)

        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_locus_of_focus = test_context.Mock(return_value=None)
        essential_modules["orca.focus_manager"].get_manager = test_context.Mock(
            return_value=focus_manager_instance
        )

        script_manager_instance = test_context.Mock()
        script_instance = test_context.Mock()
        script_manager_instance.get_active_script = test_context.Mock(
            return_value=script_instance
        )
        essential_modules["orca.script_manager"].get_manager = test_context.Mock(
            return_value=script_manager_instance
        )

        input_event_handler_mock = test_context.Mock()
        essential_modules["orca.input_event"].InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )

        essential_modules[
            "orca.messages"
        ].NOTIFICATION_PRESENTER_MESSAGE_NOT_FOUND = "No notification message found"
        essential_modules[
            "orca.messages"
        ].NOTIFICATION_PRESENTER_MESSAGE_DUPLICATE = "Duplicate notification"

        essential_modules["orca.guilabels"].NOTIFICATION_LIST_TITLE = "Notification List"
        essential_modules["dialog"] = dialog_mock
        essential_modules["list_store"] = list_store_mock
        essential_modules["tree_view"] = tree_view_mock

        return essential_modules

    def test_notification_list_gui_constructor_validation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test NotificationListGUI class can be imported and instantiated."""

        self._setup_dependencies(test_context)
        orca_i18n_mock = test_context.Mock()
        orca_i18n_mock._ = lambda x: x
        test_context.patch_module("orca.orca_i18n", orca_i18n_mock)

        from orca.notification_presenter import NotificationListGUI

        assert NotificationListGUI is not None


@pytest.mark.unit
class TestNotificationPresenterModule:
    """Test module-level functions."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Returns all dependencies needed for NotificationPresenter testing."""

        additional_modules = ["gi", "gi.repository", "gi.repository.GObject", "gi.repository.Gtk"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        gobject_mock = essential_modules["gi.repository.GObject"]
        gobject_mock.TYPE_STRING = str

        gtk_mock = essential_modules["gi.repository.Gtk"]

        gtk_mock.DialogFlags = test_context.Mock()
        gtk_mock.DialogFlags.MODAL = 1
        gtk_mock.ResponseType = test_context.Mock()
        gtk_mock.ResponseType.APPLY = -10
        gtk_mock.ResponseType.CLOSE = -7
        gtk_mock.STOCK_CLEAR = "gtk-clear"
        gtk_mock.STOCK_CLOSE = "gtk-close"

        dialog_mock = test_context.Mock()
        dialog_mock.set_default_size = test_context.Mock()
        dialog_mock.get_content_area = test_context.Mock()
        dialog_mock.connect = test_context.Mock()
        dialog_mock.show_all = test_context.Mock()
        dialog_mock.present_with_time = test_context.Mock()
        dialog_mock.destroy = test_context.Mock()

        content_area_mock = test_context.Mock()
        content_area_mock.add = test_context.Mock()
        dialog_mock.get_content_area.return_value = content_area_mock

        grid_mock = test_context.Mock()
        scrolled_window_mock = test_context.Mock()
        scrolled_window_mock.add = test_context.Mock()

        tree_view_mock = test_context.Mock()
        tree_view_mock.set_hexpand = test_context.Mock()
        tree_view_mock.set_vexpand = test_context.Mock()
        tree_view_mock.append_column = test_context.Mock()
        tree_view_mock.set_model = test_context.Mock()

        list_store_mock = test_context.Mock()
        list_store_mock.clear = test_context.Mock()
        list_store_mock.append = test_context.Mock()

        tree_view_column_mock = test_context.Mock()
        cell_renderer_text_mock = test_context.Mock()

        gtk_mock.Dialog = test_context.Mock(return_value=dialog_mock)
        gtk_mock.Grid = test_context.Mock(return_value=grid_mock)
        gtk_mock.ScrolledWindow = test_context.Mock(return_value=scrolled_window_mock)
        gtk_mock.TreeView = test_context.Mock(return_value=tree_view_mock)
        gtk_mock.ListStore = test_context.Mock(return_value=list_store_mock)
        gtk_mock.TreeViewColumn = test_context.Mock(return_value=tree_view_column_mock)
        gtk_mock.CellRendererText = test_context.Mock(return_value=cell_renderer_text_mock)

        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_locus_of_focus = test_context.Mock(return_value=None)
        essential_modules["orca.focus_manager"].get_manager = test_context.Mock(
            return_value=focus_manager_instance
        )

        script_manager_instance = test_context.Mock()
        script_instance = test_context.Mock()
        script_manager_instance.get_active_script = test_context.Mock(
            return_value=script_instance
        )
        essential_modules["orca.script_manager"].get_manager = test_context.Mock(
            return_value=script_manager_instance
        )

        input_event_handler_mock = test_context.Mock()
        essential_modules["orca.input_event"].InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )

        essential_modules[
            "orca.messages"
        ].NOTIFICATION_PRESENTER_MESSAGE_NOT_FOUND = "No notification message found"
        essential_modules[
            "orca.messages"
        ].NOTIFICATION_PRESENTER_MESSAGE_DUPLICATE = "Duplicate notification"

        essential_modules["orca.guilabels"].NOTIFICATION_LIST_TITLE = "Notification List"
        essential_modules["dialog"] = dialog_mock
        essential_modules["list_store"] = list_store_mock
        essential_modules["tree_view"] = tree_view_mock

        return essential_modules

    def test_get_presenter(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter function."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import get_presenter

        presenter = get_presenter()
        assert presenter is not None
        assert presenter._notifications is not None
        assert presenter._current_index is not None

        presenter2 = get_presenter()
        assert presenter is presenter2
