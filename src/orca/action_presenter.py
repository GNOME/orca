# Orca
#
# Copyright 2023 Igalia, S.L.
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

"""Module for performing accessible actions via a list"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from . import (
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    focus_manager,
    guilabels,
    input_event,
    keybindings,
    messages,
    presentation_manager,
    script_manager,
)
from .ax_object import AXObject
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from collections.abc import Callable

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class ActionPresenter:
    """Provides a list for performing accessible actions on an object."""

    def __init__(self) -> None:
        self._gui: ActionList | None = None
        self._obj: Atspi.Accessible | None = None
        self._window: Atspi.Accessible | None = None
        self._initialized: bool = False

        msg = "ACTION PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("ActionPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_ACTIONS
        kb = keybindings.KeyBinding("a", keybindings.ORCA_SHIFT_MODIFIER_MASK)

        manager.add_command(
            command_manager.KeyboardCommand(
                "show_actions_list",
                self.show_actions_list,
                group_label,
                cmdnames.SHOW_ACTIONS_LIST,
                desktop_keybinding=kb,
                laptop_keybinding=kb,
            ),
        )

        msg = "ACTION PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _restore_focus(self) -> None:
        """Restores focus to the object associated with the actions list."""

        tokens = ["ACTION PRESENTER: Restoring focus to", self._obj, "in", self._window]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        reason = "Action Presenter list is being destroyed"
        app = AXUtilities.get_application(self._obj)
        script = script_manager.get_manager().get_script(app, self._obj)
        script_manager.get_manager().set_active_script(script, reason)

        manager = focus_manager.get_manager()
        manager.clear_state(reason)
        manager.set_active_window(self._window)
        manager.set_locus_of_focus(None, self._obj)

    def _clear_gui_and_restore_focus(self) -> None:
        """Clears the GUI reference and then restores focus."""

        self._gui = None
        self._restore_focus()

    def _perform_action(self, action: str) -> None:
        """Attempts to perform the named action."""

        if self._gui is None:
            msg = "ACTION PRESENTER: _perform_action called when self._gui is None."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._gui.hide()
        result = AXObject.do_named_action(self._obj, action)
        tokens = ["ACTION PRESENTER: Performing", action, "on", self._obj, "succeeded:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        GLib.idle_add(self._gui.destroy)

    @dbus_service.command
    def show_actions_list(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Shows a list of all the accessible actions exposed by the focused object."""

        tokens = [
            "ACTION PRESENTER: show_actions_list. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = focus_manager.get_manager()
        obj = manager.get_active_mode_and_object_of_interest()[1] or manager.get_locus_of_focus()
        if obj is None:
            full = messages.LOCATION_NOT_FOUND_FULL
            brief = messages.LOCATION_NOT_FOUND_BRIEF
            presentation_manager.get_manager().present_message(full, brief)
            return True

        actions = {}
        for i in range(AXObject.get_n_actions(obj)):
            name = AXObject.get_action_name(obj, i)
            localized_name = AXObject.get_action_localized_name(obj, i)
            description = AXObject.get_action_description(obj, i)
            tokens = [
                f"ACTION PRESENTER: Action {i} on",
                obj,
                f": '{name}' localized name: '{localized_name}' ",
                f"localized description: '{description}'",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            actions[name] = localized_name or description or name

        if not actions.items():
            name = AXObject.get_name(obj) or AXUtilities.get_localized_role_name(obj)
            presentation_manager.get_manager().present_message(messages.NO_ACTIONS_FOUND_ON % name)
            return True

        self._obj = obj
        self._window = manager.get_active_window()
        self._gui = ActionList(actions, self._perform_action, self._clear_gui_and_restore_focus)
        self._gui.show_gui()
        return True


class ActionList(Gtk.Window):
    """A Gtk.Window containing a Gtk.ListBox of accessible actions."""

    def __init__(
        self,
        actions: dict[str, str],
        action_handler: Callable[[str], None],
        cleanup_handler: Callable[[], None],
    ) -> None:
        super().__init__(window_position=Gtk.WindowPosition.MOUSE, transient_for=None)
        self.set_title(guilabels.ACTIONS_LIST)
        self.set_decorated(False)

        self.connect("destroy", self._on_hidden)
        self.on_option_selected = action_handler
        self.on_list_hidden = cleanup_handler

        self._list_box = Gtk.ListBox()
        self._list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._list_box.connect("row-activated", self._on_row_activated)
        self._list_box.set_margin_top(5)
        self._list_box.set_margin_bottom(5)

        for name, description in actions.items():
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=description, xalign=0)
            label.set_margin_start(10)
            label.set_margin_end(10)
            row.add(label)  # pylint: disable=no-member
            row._action_name = name
            self._list_box.add(row)  # pylint: disable=no-member

        self.add(self._list_box)  # pylint: disable=no-member

        self.connect("key-press-event", self._on_key_press)

    def _on_key_press(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handles key presses for the window, e.g. Escape to close."""

        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False

    def _on_row_activated(self, _list_box: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Handler for the 'row-activated' signal of the Gtk.ListBox"""

        action_name = getattr(row, "_action_name", None)
        if action_name:
            self.on_option_selected(action_name)

    def _on_hidden(self, *_args: tuple[Any, ...]) -> None:
        """Handler for the 'destroy' window signal"""

        msg = "ACTION PRESENTER: ActionList destroyed"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.on_list_hidden()

    def show_gui(self) -> None:
        """Shows the window"""

        self.show_all()  # pylint: disable=no-member
        self.present_with_time(time.time())
        self._list_box.grab_focus()


_presenter = ActionPresenter()


def get_presenter() -> ActionPresenter:
    """Returns the action presenter."""

    return _presenter
