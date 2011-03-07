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

"""Test script example."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import time
from orca.interfaces import *
import orca.input_event as input_event

from orca.settings_manager import SettingsManager

from orca.orca_i18n import _         # for gettext support
from orca.orca_i18n import ngettext  # for ngettext support
from orca.orca_i18n import C_        # to provide qualified translatable strings

import orca.notification_messages as notification_messages

from orca.plug_event_manager import PluginEventManager, PluginEvent, plug_event_manager as pem

from orca.event_manager import EventManager
_eventManager = EventManager()

import pdb
pdb.set_trace()
import orca.scripts.default
#print Script

_settingsManager = SettingsManager()
if _settingsManager is None:
    print "Could not load the settings manager. Exiting."
    sys.exit(1)


class testPlugin(IPlugin, IPresenter):
    name = 'Test Plugin'
    description = 'A testing plugin for code tests' 
    version = '0.1pre'
    authors = ['J. Ignacio Alvarez <neonigma@gmail.com>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        print 'Hello World (plugin started)!'

    def registerEvent(self, name, function=None, data=None):
        event = PluginEvent(name)
        pem.add_event(event)
        pem.connect(name, function, data)

    def presentTimeEvent(self):
        print "present time event"

    def getPresentTimeHandler(self, function):
        return input_event.InputEventHandler(
                function,
                # Translators: Orca can present the current time to the
                # user when the user presses
                # a shortcut key.
                #
                _("Present current time."))

    def getPresentDateHandler(self, function):
        return input_event.InputEventHandler(
                function,
                # Translators: Orca can present the current date to the
                # user when the user presses
                # a shortcut key.
                #
                _("Present current date."))

IPlugin.register(testPlugin)

