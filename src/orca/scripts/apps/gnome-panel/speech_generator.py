# Orca
#
# Copyright 2010 Joanmarie Diggs.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom speech generator for gnome-panel."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.settings_manager as settings_manager
import orca.speech_generator as speech_generator

_settingsManager = settings_manager.getManager()

class SpeechGenerator(speech_generator.SpeechGenerator):

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateName(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the name of the object.  If the object is directly
        displaying any text, that text will be treated as the name.
        Otherwise, the accessible name of the object will be used.  If
        there is no accessible name, then the description of the
        object will be used.  This method will return an empty array
        if nothing can be found.
        """

        acss = self.voice(speech_generator.DEFAULT)
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_FRAME:
            if _settingsManager.getSetting('onlySpeakDisplayedText'):
                return []
            else:
                acss = self.voice(speech_generator.SYSTEM)

        result = speech_generator.SpeechGenerator.\
            _generateName(self, obj, **args)

        if result:
            result.extend(acss)

        return result
