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

"""Module for performing accessible actions via a menu"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import cmdnames
from . import debug
from . import input_event
from . import keybindings
from . import messages
from . import orca
from . import orca_state
from .ax_object import AXObject

class ActionPresenter:
    """Provides menu for performing accessible actions on an object."""

    def __init__(self):
        self._handlers = self._setup_handlers()
        self._bindings = self._setup_bindings()
        self._gui = None
        self._obj = None

    def get_bindings(self):
        """Returns the action-presenter keybindings."""

        return self._bindings

    def get_handlers(self):
        """Returns the action-presenter handlers."""

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the action-presenter input event handlers."""

        handlers = {}

        handlers["show_actions_menu"] = \
            input_event.InputEventHandler(
                self.show_actions_menu,
                cmdnames.SHOW_ACTIONS_MENU)

        return handlers

    def _setup_bindings(self):
        """Sets up and returns the action-presenter key bindings."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("show_actions_menu")))

        return bindings

    def _perform_action(self, action):
        """Attempts to perform the named action."""

        result = AXObject.do_named_action(self._obj, action)
        msg = f"ActionPresenter: Performing {action} on {self._obj} succeeded: {result}"
        debug.println(debug.LEVEL_INFO, msg, True)
        self._gui = None

    def show_actions_menu(self, script, event=None):
        """Shows a menu with all the available accessible actions."""

        obj = orca.getActiveModeAndObjectOfInterest()[1] or orca_state.locusOfFocus
        if obj is None:
            full = messages.LOCATION_NOT_FOUND_FULL
            brief = messages.LOCATION_NOT_FOUND_BRIEF
            script.presentMessage(full, brief)
            return True

        actions = {}
        for i in range(AXObject.get_n_actions(obj)):
            name = AXObject.get_action_name(obj, i)
            description = AXObject.get_action_description(obj, i)
            msg = (
                f"ActionPresenter: Action {i} on {obj}: '{name}' "
                f"(localized description: '{description}')"
            )
            debug.println(debug.LEVEL_INFO, msg, True)
            actions[name] = description or name

        if not actions.items():
            name = AXObject.get_name(obj) or script.speechGenerator.getLocalizedRoleName(obj)
            script.presentMessage(messages.NO_ACTIONS_FOUND_ON % name)
            return True

        self._obj = obj
        self._gui = ActionMenu(actions, self._perform_action)
        self._gui.show_gui()
        return True


class ActionMenu(Gtk.Menu):
    """A simple Gtk.Menu containing a list of accessible actions."""

    def __init__(self, actions, handler):
        super().__init__()
        self.on_option_selected = handler
        for name, description in actions.items():
            menu_item = Gtk.MenuItem(label=description)
            menu_item.connect("activate", self._on_activate, name)
            self.append(menu_item)

    def _on_activate(self, widget, option):
        """Handler for the 'activate' menuitem signal"""

        self.on_option_selected(option)

    def show_gui(self):
        """Shows the menu"""

        self.show_all()
        time_stamp = orca_state.lastInputEvent.timestamp
        if time_stamp == 0:
            time_stamp = Gtk.get_current_event_time()
        self.popup(None, None, None, None, 0, time_stamp)


_presenter = ActionPresenter()
def getPresenter():
    return _presenter
