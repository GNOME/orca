# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2023 Igalia, S.L.
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
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements

"""Module for learn mode"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk

from . import cmdnames
from . import command_manager
from . import debug
from . import guilabels
from . import input_event
from . import input_event_manager
from . import keybindings
from . import messages
from . import presentation_manager
from . import script_manager

if TYPE_CHECKING:
    from .scripts import default


class LearnModePresenter:
    """Provides implementation of learn mode"""

    def __init__(self) -> None:
        self._is_active: bool = False
        self._gui: CommandListGUI | None = None
        self._initialized: bool = False

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_LEARN_MODE
        kb = keybindings.KeyBinding("h", keybindings.ORCA_MODIFIER_MASK)

        manager.add_command(
            command_manager.KeyboardCommand(
                "enterLearnModeHandler",
                self.start,
                group_label,
                cmdnames.ENTER_LEARN_MODE,
                desktop_keybinding=kb,
                laptop_keybinding=kb,
            )
        )

        msg = "LEARN MODE PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def is_active(self) -> bool:
        """Returns True if we're in learn mode"""

        return self._is_active

    def start(
        self, _script: default.Script | None = None, _event: input_event.InputEvent | None = None
    ) -> bool:
        """Starts learn mode."""

        if self._is_active:
            msg = "LEARN MODE PRESENTER: Start called when already active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        presenter = presentation_manager.get_manager()
        presenter.present_message(messages.VERSION)
        presenter.speak_message(messages.LEARN_MODE_START_SPEECH)
        presenter.present_braille_message(messages.LEARN_MODE_START_BRAILLE)

        input_event_manager.get_manager().grab_keyboard("Entering learn mode")
        msg = "LEARN MODE PRESENTER: Is now active"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._is_active = True
        command_manager.get_manager().set_learn_mode_active(True)
        return True

    def quit(
        self, _script: default.Script | None = None, _event: input_event.InputEvent | None = None
    ) -> bool:
        """Quits learn mode."""

        if not self._is_active:
            msg = "LEARN MODE PRESENTER: Quit called when already inactive"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        presenter = presentation_manager.get_manager()
        presenter.present_message(messages.LEARN_MODE_STOP)

        input_event_manager.get_manager().ungrab_keyboard("Exiting learn mode")
        msg = "LEARN MODE PRESENTER: Is now inactive"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._is_active = False
        command_manager.get_manager().set_learn_mode_active(False)
        return True

    def handle_event(
        self,
        event: input_event.KeyboardEvent,
        command: command_manager.KeyboardCommand | None = None,
    ) -> bool:
        """Handles the keyboard event in learn mode."""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return False

        presentation_manager.get_manager().present_key_event(event)

        if event.is_printable_key() and event.get_click_count() == 2 and command is None:
            presentation_manager.get_manager().spell_phonetically(event.get_key_name())

        if event.keyval_name == "Escape":
            self.quit(script, event)
            return True

        if event.keyval_name == "F1" and not event.modifiers:
            self.show_help(script, event)
            return True

        if event.keyval_name == "F2" and not event.modifiers:
            self.list_orca_shortcuts(script, event)
            return True

        if command is not None:
            description = command.get_description()
            if description:
                presentation_manager.get_manager().present_message(description)

        return True

    def handle_braille_event(
        self,
        _script: default.Script,
        _event: input_event.BrailleEvent,
        command: command_manager.BrailleCommand | None,
    ) -> bool:
        """Handles braille event in learn mode. Returns True if command should not execute."""

        if command is None:
            return True

        description = command.get_description()
        if description:
            presentation_manager.get_manager().speak_message(description)

        return not command.executes_in_learn_mode()

    def list_orca_shortcuts(self, script: default.Script, event: input_event.KeyboardEvent) -> bool:
        """Shows a simple gui listing Orca's bound commands."""

        items = 0
        commands_by_group: dict[str, list[command_manager.KeyboardCommand]] = {}
        for cmd in command_manager.get_manager().get_all_keyboard_commands():
            keybinding = cmd.get_keybinding()
            if keybinding is None:
                continue

            if cmd.get_group_label() not in commands_by_group:
                commands_by_group[cmd.get_group_label()] = []
            commands_by_group[cmd.get_group_label()].append(cmd)
            items += 1

        title = messages.shortcuts_found_orca(items)
        if not commands_by_group:
            presentation_manager.get_manager().present_message(title)
            return True

        self.quit(script, event)
        column_headers = [guilabels.KB_HEADER_FUNCTION, guilabels.KB_HEADER_KEY_BINDING]
        self._gui = CommandListGUI(script, title, column_headers, commands_by_group)
        self._gui.show_gui()
        return True

    def show_help(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        page: str = "",
    ) -> bool:
        """Displays Orca's documentation."""

        self.quit(script, event)
        uri = "help:orca"
        if page:
            uri += f"/{page}"
        Gtk.show_uri(Gdk.Screen.get_default(), uri, time.time())  # pylint: disable=no-value-for-parameter
        return True


class CommandListGUI:
    """Shows a list of commands and their bindings."""

    def __init__(
        self,
        script: default.Script,
        title: str,
        column_headers: list[str],
        commands_dict: dict[str, list[command_manager.KeyboardCommand]],
    ) -> None:
        self._script: default.Script = script
        self._model: Gtk.TreeStore | None = None
        self._gui: Gtk.Dialog = self._create_dialog(title, column_headers, commands_dict)

    def _create_dialog(
        self,
        title: str,
        column_headers: list[str],
        commands_dict: dict[str, list[command_manager.KeyboardCommand]],
    ) -> Gtk.Dialog:
        """Creates the commands-list dialog."""

        dialog = Gtk.Dialog(
            title, None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        )
        dialog.set_default_size(1000, 800)

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

        self._model = Gtk.TreeStore(*cols)

        for group, commands in commands_dict.items():
            if not commands:
                continue
            group_iter = self._model.append(None, [group, ""])
            for cmd in commands:
                kb = cmd.get_keybinding()
                kb_string = kb.as_string() if kb else ""
                self._model.append(group_iter, [cmd.get_description(), kb_string])

        tree.set_model(self._model)
        tree.expand_all()
        dialog.connect("response", self.on_response)
        return dialog

    def on_response(self, _dialog: Gtk.Dialog, response: int) -> None:
        """Handler for the 'response' signal."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()

    def show_gui(self) -> None:
        """Shows the dialog."""

        self._gui.show_all()  # pylint: disable=no-member
        self._gui.present_with_time(time.time())


_presenter: LearnModePresenter = LearnModePresenter()


def get_presenter() -> LearnModePresenter:
    """Returns the Learn Mode Presenter"""

    return _presenter
