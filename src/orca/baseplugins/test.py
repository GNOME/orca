# - coding: utf-8 -

# Copyright (C) 2010, J. Félix Ontañón <felixonta@gmail.com>
# Copyright (C) 2011, J. Ignacio Álvarez <neonigma@gmail.com>

# This file is part of Pluglib.

# Pluglib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pluglib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pluglib.  If not, see <http://www.gnu.org/licenses/>.

from orca.pluglib.interfaces import *

from orca.orca_i18n import _         # for gettext support
from orca.orca_i18n import ngettext  # for ngettext support
from orca.orca_i18n import C_        # to provide qualified translatable strings

import orca.input_event
import orca.keybindings
import orca.orca as orca_module
_settingsManager = getattr(orca_module, '_settingsManager')
 
import time

class testPlugin(IPlugin, IPresenter, ICommand):
    name = 'Date and Time'
    description = 'Present the date and time to the user' 
    version = '0.9'
    authors = ['J. Ignacio Alvarez <neonigma@gmail.com>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        print 'Date and time plugin started'

        self.myKeyBindings = orca.keybindings.KeyBindings()

        self.presentTimeHandler = orca.input_event.InputEventHandler(
            self.presentTime,
            # Translators: Orca can present the current time to the
            # user when the user presses
            # a shortcut key.
            #
            _("Present current time."))

        self.myKeyBindings.add(orca.keybindings.KeyBinding(
            "t",
            1 << orca.settings.MODIFIER_ORCA,
            1 << orca.settings.MODIFIER_ORCA,
            self.presentTimeHandler))


        self.presentDateHandler = orca.input_event.InputEventHandler(
            self.presentDate,
            # Translators: Orca can present the current date to the
            # user when the user presses
            # a shortcut key.
            #
            _("Present current date."))

        self.myKeyBindings.add(orca.keybindings.KeyBinding(
            "d",
            1 << orca.settings.MODIFIER_ORCA,
            1 << orca.settings.MODIFIER_ORCA,
            self.presentDateHandler))

        orca.settings.keyBindingsMap["default"] = self.myKeyBindings

    def presentTime(self, script, inputEvent=None):
        timeFormat = _settingsManager.getSetting('presentTimeFormat')
        message = time.strftime(timeFormat, time.localtime())
        self.presentMessage(message, script)
        return True

    def presentDate(self, script, inputEvent=None):
        dateFormat = _settingsManager.getSetting('presentDateFormat')
        message = time.strftime(dateFormat, time.localtime())
        self.presentMessage(message, script)
        return True

    def removePluginKeybinding(self):
        self.removeKeybinding(self.presentTimeHandler)

IPlugin.register(testPlugin)
