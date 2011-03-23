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

"""Plugin that represents speeching"""

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

import orca.settings as settings
# este peta, quizas hay que meterlo en el enable
import orca.orca_state as orca_state

class speechPlugin(IPlugin, IPresenter):
    name = 'Speech Plugin'
    description = 'Activate or not the speech for the user' 
    version = '0.9'
    authors = ['J. Ignacio Alvarez <jialvarez@emergya.es>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        print 'Date and time plugin started'

    def enable(self):
        print 'Date and time plugin started'

        import orca.orca as orca_module
        _settingsManager = getattr(orca_module, '_settingsManager')

        """Toggle the silencing of speech.
    
        Returns True to indicate the input event has been consumed.
        """
        import orca.speech as speech
        speech.stop()
        if settings.silenceSpeech:
            settings.silenceSpeech = False
            # Translators: this is a spoken prompt letting the user know
            # that speech synthesis has been turned back on.
            #
            orca_state.activeScript.presentMessage(_("Speech enabled."))
        else:
            # Translators: this is a spoken prompt letting the user know
            # that speech synthesis has been temporarily turned off.
            #
            orca_state.activeScript.presentMessage(_("Speech disabled."))
            settings.silenceSpeech = True

    def disable(self):
        print 'disable dummy method!'

IPlugin.register(speechPlugin)
