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

gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk

from . import cmdnames
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import orca_state
from . import settings
from . import settings_manager
from .ax_object import AXObject
from .script import Script

class LearnModePresenter:
    """Provides implementation of learn mode"""

    def __init__(self):
        self._handlers = self._setup_handlers()
        self._bindings = self._setup_bindings()
        self._is_active = False
        self._gui = None

    def is_active(self):
        return self._is_active

    def get_bindings(self):
        """Returns the learn-mode-presenter keybindings."""

        return self._bindings

    def get_handlers(self):
        """Returns the learn-mode-presenter handlers."""

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the learn-mode-presenter input event handlers."""

        handlers = {}

        handlers["enterLearnModeHandler"] = \
            input_event.InputEventHandler(
                self.start,
                cmdnames.ENTER_LEARN_MODE)

        return handlers

    def _setup_bindings(self):
        """Sets up and returns the learn-mode-presenter key bindings."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "h",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("enterLearnModeHandler")))

        return bindings

    def start(self, script=None, event=None):
        """Starts learn mode."""

        if self._is_active:
            return True

        if script is not None:
            script.presentMessage(messages.VERSION)
            script.speakMessage(messages.LEARN_MODE_START_SPEECH)
            script.displayBrailleMessage(messages.LEARN_MODE_START_BRAILLE)

        Atspi.Device.grab_keyboard(orca_state.device)
        self._is_active = True
        return True

    def quit(self, script=None, event=None):
        """Quits learn mode."""

        if not self._is_active:
            return True

        if not isinstance(script, Script):
            script = orca_state.activeScript

        script.presentMessage(messages.LEARN_MODE_STOP)
        Atspi.Device.ungrab_keyboard(orca_state.device)
        self._is_active = False
        return True

    def handle_event(self, event=None):
        """Handles the event if learn mode is active."""

        if not self._is_active:
            return False

        if not isinstance(event, input_event.KeyboardEvent):
            return False

        orca_state.activeScript.speakKeyEvent(event)
        if event.isPrintableKey() and event.getClickCount() == 2 \
           and event.getHandler() is None:
            orca_state.activeScript.phoneticSpellCurrentItem(event.event_string)

        if event.event_string == "Escape":
            self.quit(event)
            return True

        if event.event_string == "F1" and not event.modifiers:
            self.show_help(orca_state.activeScript, event)
            return True

        if event.event_string in ["F2", "F3"] and not event.modifiers:
            self.list_orca_shortcuts(orca_state.activeScript, event)
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
            orca_state.activeScript.presentMessage(handler.description)

        return True

    def list_orca_shortcuts(self, script, event=None):
        """Shows a simple gui listing Orca's bound commands."""

        if event is None:
            event = orca_state.lastNonModifierKeyEvent

        layout = settings_manager.getManager().getSetting("keyboardLayout")
        is_desktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        items = 0
        bindings = {}
        if event is None or event.event_string == "F2":
            bound = script.getLearnModePresenter().get_bindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_LEARN_MODE] = bound
            items += len(bound)

            bound = script.getDefaultKeyBindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_DEFAULT] = bound
            items += len(bound)

            bound = script.getWhereAmIPresenter().get_bindings(is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_WHERE_AM_I] = bound
            items += len(bound)

            bound = script.getSpeechAndVerbosityManager().get_bindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_SPEECH_VERBOSITY] = bound
            items += len(bound)

            bound = script.getFlatReviewPresenter().get_bindings(is_desktop).getBoundBindings()
            bindings[guilabels.KB_GROUP_FLAT_REVIEW] = bound
            items += len(bound)

            bound = script.getObjectNavigator().get_bindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_OBJECT_NAVIGATION] = bound
            items += len(bound)

            bound = script.getDateAndTimePresenter().get_bindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_DATE_AND_TIME] = bound
            items += len(bound)

            bound = script.getNotificationPresenter().get_bindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_NOTIFICATIONS] = bound
            items += len(bound)

            bound = script.getBookmarks().get_bindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_BOOKMARKS] = bound
            items += len(bound)

            bound = script.getMouseReviewer().get_bindings().getBoundBindings()
            bindings[guilabels.KB_GROUP_MOUSE_REVIEW] = bound
            items += len(bound)

            bound = script.getActionPresenter().get_bindings().getBoundBindings()
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

        script.learnModePresenter.quit()
        column_headers = [guilabels.KB_HEADER_FUNCTION, guilabels.KB_HEADER_KEY_BINDING]
        self._gui = CommandListGUI(script, title, column_headers, bindings)
        self._gui.show_gui()

    def show_help(self, script=None, event=None, page=""):
        """Displays Orca's documentation."""

        self.quit()
        uri = "help:orca"
        if page:
            uri += f"/{page}"
        Gtk.show_uri(Gdk.Screen.get_default(), uri, Gtk.get_current_event_time())
        return True

class CommandListGUI:

    def __init__(self, script, title, column_headers, bindings_dict):
        self._script = script
        self._model = None
        self._gui = self._create_dialog(title, column_headers, bindings_dict)

    def _create_dialog(self, title, column_headers, bindings_dict):
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
            iter = self._model.append(None, [group, ""])
            for binding in bindings:
                self._model.append(iter, [binding.handler.description, binding.asString()])

        tree.set_model(self._model)
        tree.expand_all()
        dialog.connect("response", self.on_response)
        return dialog

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()
            return

    def show_gui(self):
        self._gui.show_all()
        ts = orca_state.lastInputEvent.timestamp
        if ts == 0:
            ts = Gtk.get_current_event_time()
        self._gui.present_with_time(ts)


_presenter = LearnModePresenter()
def getPresenter():
    return _presenter
