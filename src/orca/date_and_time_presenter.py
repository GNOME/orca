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
from . import input_event
from . import keybindings
from . import settings_manager


class DateAndTimePresenter:
    """Provides commands to present the date and time."""

    def __init__(self):
        self._handlers = self._setup_handlers()
        self._bindings = self._setup_bindings()

    def get_bindings(self):
        """Returns the date-and-time-presenter keybindings."""

        return self._bindings

    def get_handlers(self):
        """Returns the date-and-time-presenter handlers."""

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the date-and-time-presenter input event handlers."""

        handlers = {}

        handlers["presentTimeHandler"] = \
            input_event.InputEventHandler(
                self.present_time,
                cmdnames.PRESENT_CURRENT_TIME)

        handlers["presentDateHandler"] = \
            input_event.InputEventHandler(
                self.present_date,
                cmdnames.PRESENT_CURRENT_DATE)

        return handlers

    def _setup_bindings(self):
        """Sets up and returns the date-and-time-presenter key bindings."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("presentTimeHandler"),
                1))

        bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("presentDateHandler"),
                2))

        return bindings

    def present_time(self, script, event=None):
        """Presents the current time."""

        format = settings_manager.getManager().getSetting('presentTimeFormat')
        script.presentMessage(time.strftime(format, time.localtime()))
        return True

    def present_date(self, script, event=None):
        """Presents the current date."""

        format = settings_manager.getManager().getSetting('presentDateFormat')
        script.presentMessage(time.strftime(format, time.localtime()))
        return True


_presenter = DateAndTimePresenter()
def getPresenter():
    return _presenter
