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

"""Module for notification messages"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L." \
                "Copyright (c) 2010 Informal Informatica LTDA."
__license__   = "LGPL"

import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk

from . import cmdnames
from . import debug
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import orca_state

class NotificationPresenter:
    """Provides access to the notification history."""

    def __init__(self):
        self._gui = None
        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)
        self._max_size = 55

        # The list is arranged with the most recent message being at the end of
        # the list. The current index is relative to, and used directly, with the
        # python list, i.e. self._notifications[-3] would return the third-to-last
        # notification message.
        self._notifications = []
        self._current_index = -1

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the notification-presenter keybindings."""

        if refresh:
            msg = "NOTIFICATION PRESENTER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the notification-presenter handlers."""

        if refresh:
            msg = "NOTIFICATION PRESENTER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def save_notification(self, message):
        """Adds message to the list of notification messages."""

        tokens = ["NOTIFICATION PRESENTER: Adding '", message, "'."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        to_remove = max(len(self._notifications) - self._max_size + 1, 0)
        self._notifications = self._notifications[to_remove:]
        self._notifications.append([message, time.time()])

    def clear_list(self):
        """Clears the notifications list."""

        msg = "NOTIFICATION PRESENTER: Clearing list."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._notifications = []
        self._current_index = -1

    def _setup_handlers(self):
        """Sets up the notification-presenter input event handlers."""

        self._handlers = {}

        self._handlers["present_last_notification"] = \
            input_event.InputEventHandler(
                self._present_last_notification,
                cmdnames.NOTIFICATION_MESSAGES_LAST)

        self._handlers["present_next_notification"] = \
            input_event.InputEventHandler(
                self._present_next_notification,
                cmdnames.NOTIFICATION_MESSAGES_NEXT)

        self._handlers["present_previous_notification"] = \
            input_event.InputEventHandler(
                self._present_previous_notification,
                cmdnames.NOTIFICATION_MESSAGES_PREVIOUS)

        self._handlers["show_notification_list"] = \
            input_event.InputEventHandler(
                self._show_notification_list,
                cmdnames.NOTIFICATION_MESSAGES_LIST)

        msg = "NOTIFICATION PRESENTER: Handlers set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the notification-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("present_last_notification")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("present_next_notification")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("present_previous_notification")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("show_notification_list")))

        msg = "NOTIFICATION PRESENTER: Bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _timestamp_to_string(self, timestamp):
        diff = time.time() - timestamp
        if diff < 60:
            return messages.secondsAgo(diff)

        if diff < 3600:
            minutes = round(diff / 60)
            return messages.minutesAgo(minutes)

        if diff < 86400:
            hours = round(diff / 3600)
            return messages.hoursAgo(hours)

        days = round(diff / 86400)
        return messages.daysAgo(days)

    def _present_last_notification(self, script, event=None):
        """Presents the last notification."""

        if not self._notifications:
            script.presentMessage(messages.NOTIFICATION_NO_MESSAGES)
            return True

        msg = "NOTIFICATION PRESENTER: Presenting last notification."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        message, timestamp = self._notifications[-1]
        string = f"{message} {self._timestamp_to_string(timestamp)}"
        script.presentMessage(string)
        self._current_index = -1
        return True

    def _present_previous_notification(self, script, event=None):
        """Presents the previous notification."""

        if not self._notifications:
            script.presentMessage(messages.NOTIFICATION_NO_MESSAGES)
            return True

        msg = (
            f"NOTIFICATION PRESENTER: Presenting previous notification. "
            f"Current index: {self._current_index}"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # This is the first (oldest) message in the list.
        if self._current_index == 0 :
            script.presentMessage(messages.NOTIFICATION_LIST_TOP)
            message, timestamp = self._notifications[self._current_index]
        else:
            try:
                index = self._current_index - 1
                message, timestamp = self._notifications[index]
                self._current_index -= 1
            except IndexError:
                msg = "NOTIFICATION PRESENTER: Handling IndexError exception."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                script.presentMessage(messages.NOTIFICATION_LIST_TOP)
                message, timestamp = self._notifications[self._current_index]

        string = f"{message} {self._timestamp_to_string(timestamp)}"
        script.presentMessage(string)
        return True

    def _present_next_notification(self, script, event=None):
        """Presents the next notification."""

        if not self._notifications:
            script.presentMessage(messages.NOTIFICATION_NO_MESSAGES)
            return True

        msg = (
            f"NOTIFICATION PRESENTER: Presenting next notification. "
            f"Current index: {self._current_index}"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # This is the last (newest) message in the list.
        if self._current_index == -1:
            script.presentMessage(messages.NOTIFICATION_LIST_BOTTOM)
            message, timestamp = self._notifications[self._current_index]
        else:
            try:
                index = self._current_index + 1
                message, timestamp = self._notifications[index]
                self._current_index += 1
            except IndexError:
                msg = "NOTIFICATION PRESENTER: Handling IndexError exception."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                script.presentMessage(messages.NOTIFICATION_LIST_BOTTOM)
                message, timestamp = self._notifications[self._current_index]

        string = f"{message} {self._timestamp_to_string(timestamp)}"
        script.presentMessage(string)
        return True

    def _show_notification_list(self, script, event=None):
        """Opens a dialog with a list of the notifications."""

        if not self._notifications:
            script.presentMessage(messages.NOTIFICATION_NO_MESSAGES)
            return True

        msg = "NOTIFICATION PRESENTER: Showing notification list."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        rows = [(message, self._timestamp_to_string(timestamp)) \
                    for message, timestamp in reversed(self._notifications)]
        title = guilabels.notifications_count(len(self._notifications))
        column_headers = [guilabels.NOTIFICATIONS_COLUMN_HEADER,
                          guilabels.NOTIFICATIONS_RECEIVED_TIME]
        self._gui = NotificationListGUI(script, title, column_headers, rows)
        self._gui.show_gui()
        return True

    def on_dialog_destroyed(self):
        """Handler for the 'destroyed' signal of the dialog."""

        self._gui = None

class NotificationListGUI:
    """The dialog containing the notifications list."""

    def __init__(self, script, title, column_headers, rows):
        self._script = script
        self._model = None
        self._gui = self._create_dialog(title, column_headers, rows)

    def _create_dialog(self, title, column_headers, rows):
        dialog = Gtk.Dialog(title,
                            None,
                            Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CLEAR, Gtk.ResponseType.APPLY,
                             Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        dialog.set_default_size(600, 400)

        grid = Gtk.Grid()
        content_area = dialog.get_content_area()
        content_area.add(grid)

        scrolled_window = Gtk.ScrolledWindow()
        grid.add(scrolled_window)

        tree = Gtk.TreeView()
        tree.set_hexpand(True)
        tree.set_vexpand(True)
        scrolled_window.add(tree)

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

    def on_response(self, dialog, response):
        """The handler for the 'response' signal."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()
            return

        if response == Gtk.ResponseType.APPLY and self._model is not None:
            self._model.clear()
            getPresenter().clear_list()
            self._script.presentMessage(messages.NOTIFICATION_NO_MESSAGES)
            time.sleep(1)
            self._gui.destroy()

    def show_gui(self):
        """Shows the notifications list dialog."""

        self._gui.show_all()
        time_stamp = orca_state.lastInputEvent.timestamp
        if time_stamp == 0:
            time_stamp = Gtk.get_current_event_time()
        self._gui.present_with_time(time_stamp)

_presenter = NotificationPresenter()
def getPresenter():
    """Returns the Notification Presenter"""

    return _presenter
