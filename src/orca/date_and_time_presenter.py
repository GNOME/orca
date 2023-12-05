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

"""Module for date and time presentation"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

import time

from . import cmdnames
from . import debug
from . import input_event
from . import keybindings
from . import settings_manager


class DateAndTimePresenter:
    """Provides commands to present the date and time."""

    def __init__(self):
        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the date-and-time-presenter keybindings."""

        if refresh:
            msg = "DATE AND TIME PRESENTER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the date-and-time-presenter handlers."""

        if refresh:
            msg = "DATE AND TIME PRESENTER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up the date-and-time-presenter input event handlers."""

        self._handlers = {}

        self._handlers["presentTimeHandler"] = \
            input_event.InputEventHandler(
                self.present_time,
                cmdnames.PRESENT_CURRENT_TIME)

        self._handlers["presentDateHandler"] = \
            input_event.InputEventHandler(
                self.present_date,
                cmdnames.PRESENT_CURRENT_DATE)

        msg = "DATE AND TIME PRESENTER: Handlers set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the date-and-time-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("presentTimeHandler"),
                1))

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("presentDateHandler"),
                2))

        msg = "DATE AND TIME PRESENTER: Bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def present_time(self, script, event=None):
        """Presents the current time."""

        time_format = settings_manager.getManager().getSetting('presentTimeFormat')
        script.presentMessage(time.strftime(time_format, time.localtime()))
        return True

    def present_date(self, script, event=None):
        """Presents the current date."""

        data_format = settings_manager.getManager().getSetting('presentDateFormat')
        script.presentMessage(time.strftime(data_format, time.localtime()))
        return True


_presenter = DateAndTimePresenter()
def getPresenter():
    return _presenter
