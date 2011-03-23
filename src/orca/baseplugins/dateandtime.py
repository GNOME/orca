# Orca
#
# Copyright 2011 Consorcio Fernando de los Rios.
# Author: J. Ignacio Alvarez <jialvarez@emergya.es>
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

"""Plugin to present date and time to the user"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

from orca.pluglib.interfaces import IPluginManager, IPlugin, ICommand, \
    IPresenter, IConfigurable, IDependenciesChecker, PluginManagerError

from orca.orca_i18n import _         # for gettext support
from orca.orca_i18n import ngettext  # for ngettext support
from orca.orca_i18n import C_        # to provide qualified translatable strings

import orca.input_event
import orca.keybindings
 
import time

class dtPlugin(IPlugin, IPresenter, ICommand):
    name = 'Date and Time'
    description = 'Present the date and time to the user' 
    version = '0.9'
    authors = ['J. Ignacio Alvarez <jialvarez@emergya.es>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        global _settingsManager

        import orca.orca as orca_module
        _settingsManager = getattr(orca_module, '_settingsManager')

    def enable(self):
        global _settingsManager

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

    def disable(self):
        self.removePluginKeybinding()

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
        self.removeKeybinding("default")

IPlugin.register(dtPlugin)
