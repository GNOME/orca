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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

import time
from typing import TYPE_CHECKING

import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk

from . import cmdnames
from . import debug
from . import guilabels
from . import input_event
from . import input_event_manager
from . import keybindings
from . import messages
from . import script_manager
from . import settings
from . import settings_manager
from . import speech
from .ax_object import AXObject

if TYPE_CHECKING:
    from .scripts import default


class LearnModePresenter:
    """Provides implementation of learn mode"""

    def __init__(self) -> None:
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._is_active: bool = False
        self._gui: CommandListGUI | None = None

    def is_active(self) -> bool:
        """Returns True if we're in learn mode"""

        return self._is_active

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the learn-mode-presenter keybindings."""

        if refresh:
            msg = f"LEARN MODE PRESENTER: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("LEARN MODE PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the learn-mode-presenter handlers."""

        if refresh:
            msg = "LEARN MODE PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the learn-mode-presenter input event handlers."""

        self._handlers = {}

        self._handlers["enterLearnModeHandler"] = \
            input_event.InputEventHandler(
                self.start,
                cmdnames.ENTER_LEARN_MODE)

        msg = "LEARN MODE PRESENTER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up the learn-mode-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "h",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["enterLearnModeHandler"]))

        msg = "LEARN MODE PRESENTER: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def start(
        self,
        script: default.Script | None = None,
        _event: input_event.InputEvent | None = None
    ) -> bool:
        """Starts learn mode."""

        if self._is_active:
            msg = "LEARN MODE PRESENTER: Start called when already active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if script is None:
            script = script_manager.get_manager().get_active_script()

        if script is not None:
            script.present_message(messages.VERSION)
            script.speak_message(messages.LEARN_MODE_START_SPEECH)
            script.display_message(messages.LEARN_MODE_START_BRAILLE)

        input_event_manager.get_manager().grab_keyboard("Entering learn mode")
        msg = "LEARN MODE PRESENTER: Is now active"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._is_active = True
        return True

    def quit(
        self,
        script: default.Script | None = None,
        _event: input_event.InputEvent | None = None
    ) -> bool:
        """Quits learn mode."""

        if not self._is_active:
            msg = "LEARN MODE PRESENTER: Quit called when already inactive"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if script is None:
            script = script_manager.get_manager().get_active_script()

        if script is not None:
            script.present_message(messages.LEARN_MODE_STOP)

        input_event_manager.get_manager().ungrab_keyboard("Exiting learn mode")
        msg = "LEARN MODE PRESENTER: Is now inactive"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._is_active = False
        return True

    def handle_event(self, event: input_event.InputEvent | None = None) -> bool:
        """Handles the event if learn mode is active."""

        if not self._is_active:
            return False

        if not isinstance(event, input_event.KeyboardEvent):
            return False

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return False

        key_name = None
        if event.is_printable_key():
            key_name = event.get_key_name()

        voice = script.speech_generator.voice(string=key_name)
        speech.speak_key_event(event, voice[0] if voice else None)

        if event.is_printable_key() and event.get_click_count() == 2 \
           and event.get_handler() is None:
            script.spell_phonetically(event.get_key_name())

        if event.keyval_name == "Escape":
            self.quit(script, event)
            return True

        if event.keyval_name == "F1" and not event.modifiers:
            self.show_help(script, event)
            return True

        if event.keyval_name in ["F2", "F3"] and not event.modifiers:
            self.list_orca_shortcuts(script, event)
            return True

        self.present_command(event)
        return True

    def present_command(self, event: input_event.InputEvent | None = None) -> bool:
        """Presents the command bound to event."""

        if not isinstance(event, input_event.KeyboardEvent):
            return True

        handler = event.get_handler()
        if handler is None:
            return True

        if handler.learn_mode_enabled and handler.description:
            script = script_manager.get_manager().get_active_script()
            if script is None:
                return True
            script.present_message(handler.description)

        return True

    def list_orca_shortcuts(self, script: default.Script, event: input_event.KeyboardEvent) -> bool:
        """Shows a simple gui listing Orca's bound commands."""

        layout = settings_manager.get_manager().get_setting("keyboardLayout")
        is_desktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        items = 0
        bindings = {}
        if event is None or event.keyval_name == "F2":
            bound = script.get_default_keybindings_deprecated().get_bound_bindings()
            bindings[guilabels.KB_GROUP_DEFAULT] = bound
            items += len(bound)

            bound = script.get_learn_mode_presenter().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_LEARN_MODE] = bound
            items += len(bound)

            bound = script.get_where_am_i_presenter().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_WHERE_AM_I] = bound
            items += len(bound)

            bound = script.get_speech_and_verbosity_manager().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_SPEECH_VERBOSITY] = bound
            items += len(bound)

            bound = script.get_sleep_mode_manager().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_SLEEP_MODE] = bound
            items += len(bound)

            bound = script.get_flat_review_presenter().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_FLAT_REVIEW] = bound
            items += len(bound)

            bound = script.get_flat_review_finder().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_FIND] = bound
            items += len(bound)

            bound = script.get_object_navigator().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_OBJECT_NAVIGATION] = bound
            items += len(bound)

            bound = script.get_caret_navigator().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_CARET_NAVIGATION] = bound
            items += len(bound)

            bound = script.get_structural_navigator().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_STRUCTURAL_NAVIGATION] = bound
            items += len(bound)

            bound = script.get_table_navigator().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_TABLE_NAVIGATION] = bound
            items += len(bound)

            bound = script.get_system_information_presenter().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_SYSTEM_INFORMATION] = bound
            items += len(bound)

            bound = script.get_notification_presenter().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_NOTIFICATIONS] = bound
            items += len(bound)

            bound = script.get_clipboard_presenter().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_CLIPBOARD] = bound
            items += len(bound)

            bound = script.get_bookmarks().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_BOOKMARKS] = bound
            items += len(bound)

            bound = script.get_mouse_reviewer().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_MOUSE_REVIEW] = bound
            items += len(bound)

            bound = script.get_action_presenter().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_ACTIONS] = bound
            items += len(bound)

            bound = script.get_debugging_tools_manager().get_bindings(
                is_desktop=is_desktop).get_bound_bindings()
            bindings[guilabels.KB_GROUP_DEBUGGING_TOOLS] = bound
            items += len(bound)

            title = messages.shortcuts_found_orca(items)
        else:
            app_name = AXObject.get_name(script.app) or messages.APPLICATION_NO_NAME
            bound = script.get_app_key_bindings().get_bound_bindings()
            if bound:
                bindings[app_name] = bound
            title = messages.shortcuts_found_app(len(bound), app_name)

        if not bindings:
            script.present_message(title)
            return True

        self.quit(script, event)
        column_headers = [guilabels.KB_HEADER_FUNCTION, guilabels.KB_HEADER_KEY_BINDING]
        self._gui = CommandListGUI(script, title, column_headers, bindings)
        self._gui.show_gui()
        return True

    def show_help(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        page: str = ""
    ) -> bool:
        """Displays Orca's documentation."""

        self.quit(script, event)
        uri = "help:orca"
        if page:
            uri += f"/{page}"
        Gtk.show_uri(Gdk.Screen.get_default(), uri, time.time())
        return True

class CommandListGUI:
    """Shows a list of commands and their bindings."""

    def __init__(
        self,
        script: default.Script,
        title: str,
        column_headers: list[str],
        bindings_dict: dict[str, list[keybindings.KeyBinding]]
    ) -> None:
        self._script: default.Script = script
        self._model: Gtk.TreeStore | None = None
        self._gui: Gtk.Dialog = self._create_dialog(title, column_headers, bindings_dict)

    def _create_dialog(
        self,
        title: str,
        column_headers: list[str],
        bindings_dict: dict[str, list[keybindings.KeyBinding]]
    ) -> Gtk.Dialog:
        """Creates the commands-list dialog."""

        dialog = Gtk.Dialog(title,
                            None,
                            Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        dialog.set_default_size(1000, 800)

        grid = Gtk.Grid()
        content_area = dialog.get_content_area()
        content_area.add(grid)

        scrolled_window = Gtk.ScrolledWindow()
        grid.add(scrolled_window) # pylint: disable=no-member

        tree = Gtk.TreeView()
        tree.set_hexpand(True)
        tree.set_vexpand(True)
        scrolled_window.add(tree) # pylint: disable=no-member

        cols = len(column_headers) * [GObject.TYPE_STRING]
        for i, header in enumerate(column_headers):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(header, cell, text=i)
            tree.append_column(column)
            if header:
                column.set_sort_column_id(i)

        self._model = Gtk.TreeStore(*cols)

        for group, bindings in bindings_dict.items():
            if not bindings:
                continue
            group_iter = self._model.append(None, [group, ""])
            for binding in bindings:
                self._model.append(group_iter, [binding.handler.description, binding.as_string()])

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

        self._gui.show_all() # pylint: disable=no-member
        self._gui.present_with_time(time.time())


_presenter: LearnModePresenter = LearnModePresenter()
def get_presenter() -> LearnModePresenter:
    """Returns the Learn Mode Presenter"""

    return _presenter
