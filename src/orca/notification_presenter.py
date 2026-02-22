# Orca
#
# Copyright 2023 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
# Based on the feature created by:
# Author: Jose Vilmar <vilmar@informal.com.br>
# Copyright 2010 Informal Informatica LTDA.
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

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Module for notification messages"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk

from . import (
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    guilabels,
    input_event,
    messages,
    presentation_manager,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .scripts import default


class NotificationPresenter:
    """Provides access to the notification history."""

    def __init__(self) -> None:
        self._gui: NotificationListGUI | None = None
        self._max_size: int = 55

        # The list is arranged with the most recent message being at the end of
        # the list. The current index is relative to, and used directly, with the
        # python list, i.e. self._notifications[-3] would return the third-to-last
        # notification message.
        self._notifications: list[tuple[str, float]] = []
        self._current_index: int = -1
        self._initialized: bool = False

        msg = "NOTIFICATION PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("NotificationPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_NOTIFICATIONS

        commands_data = [
            (
                "present_last_notification",
                self.present_last_notification,
                cmdnames.NOTIFICATION_MESSAGES_LAST,
            ),
            (
                "present_next_notification",
                self.present_next_notification,
                cmdnames.NOTIFICATION_MESSAGES_NEXT,
            ),
            (
                "present_previous_notification",
                self.present_previous_notification,
                cmdnames.NOTIFICATION_MESSAGES_PREVIOUS,
            ),
            (
                "show_notification_list",
                self.show_notification_list,
                cmdnames.NOTIFICATION_MESSAGES_LIST,
            ),
        ]

        for name, function, description in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=None,
                    laptop_keybinding=None,
                ),
            )

        msg = "NOTIFICATION PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def save_notification(self, message: str) -> None:
        """Adds message to the list of notification messages."""

        tokens = ["NOTIFICATION PRESENTER: Adding '", message, "'."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        to_remove = max(len(self._notifications) - self._max_size + 1, 0)
        self._notifications = self._notifications[to_remove:]
        self._notifications.append((message, time.time()))

    def clear_list(self) -> None:
        """Clears the notifications list."""

        msg = "NOTIFICATION PRESENTER: Clearing list."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._notifications = []
        self._current_index = -1

    def _timestamp_to_string(self, timestamp: float) -> str:
        diff = time.time() - timestamp
        if diff < 60:
            return messages.seconds_ago(diff)

        if diff < 3600:
            minutes = round(diff / 60)
            return messages.minutes_ago(minutes)

        if diff < 86400:
            hours = round(diff / 3600)
            return messages.hours_ago(hours)

        days = round(diff / 86400)
        return messages.days_ago(days)

    @dbus_service.command
    def present_last_notification(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the last notification."""

        tokens = [
            "NOTIFICATION PRESENTER: present_last_notification. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self._notifications:
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.NOTIFICATION_NO_MESSAGES,
                )
            return True

        message, timestamp = self._notifications[-1]
        string = f"{message} {self._timestamp_to_string(timestamp)}"
        presentation_manager.get_manager().present_message(string)
        self._current_index = -1
        return True

    @dbus_service.command
    def present_previous_notification(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the previous notification."""

        tokens = [
            "NOTIFICATION PRESENTER: present_previous_notification. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
            "Current index:",
            self._current_index,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self._notifications:
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.NOTIFICATION_NO_MESSAGES,
                )
            return True

        # This is the first (oldest) message in the list.
        if self._current_index == 0:
            presentation_manager.get_manager().present_message(messages.NOTIFICATION_LIST_TOP)
            message, timestamp = self._notifications[self._current_index]
        else:
            try:
                index = self._current_index - 1
                message, timestamp = self._notifications[index]
                self._current_index -= 1
            except IndexError:
                msg = "NOTIFICATION PRESENTER: Handling IndexError exception."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                presentation_manager.get_manager().present_message(messages.NOTIFICATION_LIST_TOP)
                message, timestamp = self._notifications[self._current_index]

        string = f"{message} {self._timestamp_to_string(timestamp)}"
        presentation_manager.get_manager().present_message(string)
        return True

    @dbus_service.command
    def present_next_notification(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the next notification."""

        tokens = [
            "NOTIFICATION PRESENTER: present_next_notification. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
            "Current index:",
            self._current_index,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self._notifications:
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.NOTIFICATION_NO_MESSAGES,
                )
            return True

        # This is the last (newest) message in the list.
        if self._current_index == -1:
            presentation_manager.get_manager().present_message(messages.NOTIFICATION_LIST_BOTTOM)
            message, timestamp = self._notifications[self._current_index]
        else:
            try:
                index = self._current_index + 1
                message, timestamp = self._notifications[index]
                self._current_index += 1
            except IndexError:
                msg = "NOTIFICATION PRESENTER: Handling IndexError exception."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                presentation_manager.get_manager().present_message(
                    messages.NOTIFICATION_LIST_BOTTOM,
                )
                message, timestamp = self._notifications[self._current_index]

        string = f"{message} {self._timestamp_to_string(timestamp)}"
        presentation_manager.get_manager().present_message(string)
        return True

    @dbus_service.command
    def show_notification_list(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Opens a dialog with a list of the notifications."""

        tokens = [
            "NOTIFICATION PRESENTER: show_notification_list. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self._notifications:
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.NOTIFICATION_NO_MESSAGES,
                )
            return True

        if self._gui:
            msg = "NOTIFICATION PRESENTER: Notification list already exists. Showing."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._gui.show_gui()
            return True

        rows = [
            (message, self._timestamp_to_string(timestamp))
            for message, timestamp in reversed(self._notifications)
        ]
        title = guilabels.notifications_count(len(self._notifications))
        column_headers = [
            guilabels.NOTIFICATIONS_COLUMN_HEADER,
            guilabels.NOTIFICATIONS_RECEIVED_TIME,
        ]
        self._gui = NotificationListGUI(
            script,
            title,
            column_headers,
            rows,
            self.on_dialog_destroyed,
        )
        self._gui.show_gui()
        return True

    def on_dialog_destroyed(self, _dialog: Gtk.Dialog) -> None:
        """Handler for the 'destroyed' signal of the dialog."""

        self._gui = None


class NotificationListGUI:
    """The dialog containing the notifications list."""

    def __init__(
        self,
        script: default.Script,
        title: str,
        column_headers: list[str],
        rows: list[tuple[str, str]],
        destroyed_callback: Callable[[Gtk.Dialog], None],
    ):
        self._script: default.Script = script
        self._model: Gtk.ListStore | None = None
        self._gui: Gtk.Dialog = self._create_dialog(title, column_headers, rows)
        self._gui.connect("destroy", destroyed_callback)

    def _create_dialog(
        self,
        title: str,
        column_headers: list[str],
        rows: list[tuple[str, str]],
    ) -> Gtk.Dialog:
        dialog = Gtk.Dialog(
            title,
            None,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CLEAR, Gtk.ResponseType.APPLY, Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE),
        )
        dialog.set_default_size(600, 400)

        grid = Gtk.Grid()
        content_area = dialog.get_content_area()
        content_area.add(grid)

        scrolled_window = Gtk.ScrolledWindow()
        grid.add(scrolled_window)  # pylint: disable=no-member

        tree = Gtk.TreeView()
        tree.set_hexpand(True)
        tree.set_vexpand(True)
        scrolled_window.add(tree)  # pylint: disable=no-member

        cols = len(column_headers) * [GObject.TYPE_STRING]
        for i, header in enumerate(column_headers):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(header, cell, text=i)
            tree.append_column(column)
            if header:
                column.set_sort_column_id(i)

        self._model = Gtk.ListStore(*cols)
        for row in rows:
            row_iter = self._model.append(None)
            for i, cell in enumerate(row):
                self._model.set_value(row_iter, i, cell)

        tree.set_model(self._model)
        dialog.connect("response", self.on_response)
        return dialog

    def on_response(self, _dialog: Gtk.Dialog, response: int) -> None:
        """The handler for the 'response' signal."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()
            return

        if response == Gtk.ResponseType.APPLY and self._model is not None:
            self._model.clear()
            get_presenter().clear_list()
            presentation_manager.get_manager().present_message(messages.NOTIFICATION_NO_MESSAGES)
            time.sleep(1)
            self._gui.destroy()

    def show_gui(self) -> None:
        """Shows the notifications list dialog."""

        self._gui.show_all()  # pylint: disable=no-member
        self._gui.present_with_time(time.time())


_presenter: NotificationPresenter = NotificationPresenter()


def get_presenter() -> NotificationPresenter:
    """Returns the Notification Presenter"""

    return _presenter
