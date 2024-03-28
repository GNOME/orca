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

"""Module for learn mode"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk

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
from .ax_object import AXObject


class LearnModePresenter:
    """Provides implementation of learn mode"""

    def __init__(self):
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()
        self._is_active = False
        self._gui = None

    def is_active(self):
        """Returns True if we're in learn mode"""

        return self._is_active

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the learn-mode-presenter keybindings."""

        if refresh:
            msg = "LEARN MODE PRESENTER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.isEmpty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the learn-mode-presenter handlers."""

        if refresh:
            msg = "LEARN MODE PRESENTER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up the learn-mode-presenter input event handlers."""

        self._handlers = {}

        self._handlers["enterLearnModeHandler"] = \
            input_event.InputEventHandler(
                self.start,
                cmdnames.ENTER_LEARN_MODE)

        msg = "LEARN MODE PRESENTER: Handlers set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the learn-mode-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "h",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("enterLearnModeHandler")))

        msg = "LEARN MODE PRESENTER: Bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def start(self, script=None, event=None):
        """Starts learn mode."""

        if self._is_active:
            msg = "LEARN MODE PRESENTER: Start called when already active"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if script is None:
            script = script_manager.getManager().getActiveScript()

        if script is not None:
            script.presentMessage(messages.VERSION)
            script.speakMessage(messages.LEARN_MODE_START_SPEECH)
            script.displayBrailleMessage(messages.LEARN_MODE_START_BRAILLE)

        input_event_manager.getManager().grab_keyboard("Entering learn mode")
        msg = "LEARN MODE PRESENTER: Is now active"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._is_active = True
        return True

    def quit(self, script=None, event=None):
        """Quits learn mode."""

        if not self._is_active:
            msg = "LEARN MODE PRESENTER: Quit called when already inactive"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if script is None:
            script = script_manager.getManager().getActiveScript()

        if script is not None:
            script.presentMessage(messages.LEARN_MODE_STOP)

        input_event_manager.getManager().ungrab_keyboard("Exiting learn mode")
        msg = "LEARN MODE PRESENTER: Is now inactive"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._is_active = False
        return True

    def handle_event(self, event=None):
        """Handles the event if learn mode is active."""

        if not self._is_active:
            return False

        if not isinstance(event, input_event.KeyboardEvent):
            return False

        script = script_manager.getManager().getActiveScript()
        script.speakKeyEvent(event)
        if event.isPrintableKey() and event.getClickCount() == 2 \
           and event.getHandler() is None:
            script.phoneticSpellCurrentItem(event.event_string)

        if event.event_string == "Escape":
            self.quit(script=None, event=event)
            return True

        if event.event_string == "F1" and not event.modifiers:
            self.show_help(script, event)
            return True

        if event.event_string in ["F2", "F3"] and not event.modifiers:
            self.list_orca_shortcuts(script, event)
            return True

        self.present_command(event)
        return True

    def present_command(self, event=None):
        """Presents the command bound to event."""

        if not isinstance(event, input_event.KeyboardEvent):
            return True

        handler = event.getHandler()
        if handler is None:
            return True

        if handler.learnModeEnabled and handler.description:
            script = script_manager.getManager().getActiveScript()
            script.presentMessage(handler.description)

        return True

    def list_orca_shortcuts(self, script, event):
        """Shows a simple gui listing Orca's bound commands."""

        layout = settings_manager.getManager().getSetting("keyboardLayout")
        is_desktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        items = 0
        bindings = {}
        if event is None or event.event_string == "F2":
            bound = script.getDefaultKeyBindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_DEFAULT] = bound
            items += len(bound)

            bound = script.getLearnModePresenter().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_LEARN_MODE] = bound
            items += len(bound)

            bound = script.getWhereAmIPresenter().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_WHERE_AM_I] = bound
            items += len(bound)

            bound = script.getSpeechAndVerbosityManager().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_SPEECH_VERBOSITY] = bound
            items += len(bound)

            bound = script.getSleepModeManager().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_SLEEP_MODE] = bound
            items += len(bound)

            bound = script.getFlatReviewPresenter().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_FLAT_REVIEW] = bound
            items += len(bound)

            bound = script.getObjectNavigator().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_OBJECT_NAVIGATION] = bound
            items += len(bound)

            bound = script.getTableNavigator().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_TABLE_NAVIGATION] = bound
            items += len(bound)

            bound = script.getSystemInformationPresenter().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_SYSTEM_INFORMATION] = bound
            items += len(bound)

            bound = script.getNotificationPresenter().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_NOTIFICATIONS] = bound
            items += len(bound)

            bound = script.getBookmarks().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_BOOKMARKS] = bound
            items += len(bound)

            bound = script.getMouseReviewer().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_MOUSE_REVIEW] = bound
            items += len(bound)

            bound = script.getActionPresenter().get_bindings(
                is_desktop=is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_ACTIONS] = bound
            items += len(bound)

            title = messages.shortcutsFoundOrca(items)
        else:
            app_name = AXObject.get_name(script.app) or messages.APPLICATION_NO_NAME
            bound = script.getAppKeyBindings().getBoundBindings()
            bound.extend(script.getToolkitKeyBindings().getBoundBindings())
            if bound:
                bindings[app_name] = bound
            title = messages.shortcutsFoundApp(len(bound), app_name)

        if not bindings:
            script.presentMessage(title)
            return True

        self.quit(script, event)
        column_headers = [guilabels.KB_HEADER_FUNCTION, guilabels.KB_HEADER_KEY_BINDING]
        self._gui = CommandListGUI(script, title, column_headers, bindings)
        self._gui.show_gui()
        return True

    def show_help(self, script=None, event=None, page=""):
        """Displays Orca's documentation."""

        self.quit(script, event)
        uri = "help:orca"
        if page:
            uri += f"/{page}"
        Gtk.show_uri(Gdk.Screen.get_default(), uri, Gtk.get_current_event_time())
        return True

class CommandListGUI:
    """Shows a list of commands and their bindings."""

    def __init__(self, script, title, column_headers, bindings_dict):
        self._script = script
        self._model = None
        self._gui = self._create_dialog(title, column_headers, bindings_dict)

    def _create_dialog(self, title, column_headers, bindings_dict):
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

        self._model = Gtk.TreeStore(*cols)

        for group, bindings in bindings_dict.items():
            if not bindings:
                continue
            group_iter = self._model.append(None, [group, ""])
            for binding in bindings:
                self._model.append(group_iter, [binding.handler.description, binding.asString()])

        tree.set_model(self._model)
        tree.expand_all()
        dialog.connect("response", self.on_response)
        return dialog

    def on_response(self, dialog, response):
        """Handler for the 'response' signal."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()
            return

    def show_gui(self):
        """Shows the dialog."""

        self._gui.show_all()
        self._gui.present_with_time(Gtk.get_current_event_time())


_presenter = LearnModePresenter()
def getPresenter():
    """Returns the Learn Mode Presenter"""

    return _presenter
