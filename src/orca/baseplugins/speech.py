# - coding: utf-8 -

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

import orca.settings as settings
import orca.orca_state as orca_state

import orca.orca as orca_module
_settingsManager = getattr(orca_module, '_settingsManager')
 

class speechPlugin(IPlugin, IPresenter):
    name = 'Speech Plugin'
    description = 'Activate or not the speech for the user' 
    version = '0.9'
    authors = ['J. Ignacio Alvarez <neonigma@gmail.com>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        print 'Date and time plugin started'

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

IPlugin.register(speechPlugin)
