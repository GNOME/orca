# Orca
#
# Copyright 2016 Igalia, S.L.
#
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

"""Utilities for obtaining sounds to be presented for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version('Atspi', '2.0') 
from gi.repository import Atspi

import os
import pyatspi

from . import generator
from . import settings_manager

_settingsManager = settings_manager.getManager()

METHOD_PREFIX = "_generate"


class Icon:
    """Sound file representing a particular aspect of an object."""

    def __init__(self, location, filename):
        self.path = os.path.join(location, filename)

    def __str__(self):
        return 'Icon(path: %s, isValid: %s)' % (self.path, self.isValid())

    def isValid(self):
        return os.path.isfile(self.path)

class Tone:
    """Tone representing a particular aspect of an object."""

    SINE_WAVE = 0
    SQUARE_WAVE = 1
    SAW_WAVE = 2
    TRIANGLE_WAVE = 3
    SILENCE = 4
    WHITE_UNIFORM_NOISE = 5
    PINK_NOISE = 6
    SINE_WAVE_USING_TABLE = 7
    PERIODIC_TICKS = 8
    WHITE_GAUSSIAN_NOISE = 9
    RED_NOISE = 10
    INVERTED_PINK_NOISE = 11
    INVERTED_RED_NOISE = 12

    def __init__(self, duration, frequency, volumeMultiplier=1, wave=SINE_WAVE):
        self.duration = duration
        self.frequency = min(max(0, frequency), 20000)
        self.volume = _settingsManager.getSetting('soundVolume') * volumeMultiplier
        self.wave = wave

    def __str__(self):
        return 'Tone(duration: %s, frequency: %s, volume: %s, wave: %s)' \
            % (self.duration, self.frequency, self.volume, self.wave)

class SoundGenerator(generator.Generator):
    """Takes accessible objects and produces the sound(s) to be played."""

    def __init__(self, script):
        super().__init__(script, 'sound')
        self._sounds = os.path.join(_settingsManager.getPrefsDir(), 'sounds')

    def _convertFilenameToIcon(self, filename):
        icon = Icon(self._sounds, filename)
        if icon.isValid():
            return icon

        return None

    def generateSound(self, obj, **args):
        """Returns an array of sounds for the complete presentation of obj."""

        return self.generate(obj, **args)

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generateAvailability(self, obj, **args):
        """Returns an array of sounds indicating obj is grayed out."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateAvailability(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateCheckedState(self, obj, **args):
        """Returns an array of sounds indicating the checked state of obj."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateCheckedState(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateClickable(self, obj, **args):
        """Returns an array of sounds indicating obj is clickable."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateClickable(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateExpandableState(self, obj, **args):
        """Returns an array of sounds indicating the expanded state of obj."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateExpandableState(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateHasLongDesc(self, obj, **args):
        """Returns an array of sounds indicating obj has a longdesc."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateHasLongDesc(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateMenuItemCheckedState(self, obj, **args):
        """Returns an array of sounds indicating the checked state of obj."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateMenuItemCheckedState(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateMultiselectableState(self, obj, **args):
        """Returns an array of sounds indicating obj is multiselectable."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateMultiselectableState(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateRadioState(self, obj, **args):
        """Returns an array of sounds indicating the selected state of obj."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateRadioState(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateReadOnly(self, obj, **args):
        """Returns an array of sounds indicating obj is read only."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateReadOnly(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateRequired(self, obj, **args):
        """Returns an array of sounds indicating obj is required."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateRequired(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateSwitchState(self, obj, **args):
        """Returns an array of sounds indicating the on/off state of obj."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateSwitchState(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateToggleState(self, obj, **args):
        """Returns an array of sounds indicating the toggled state of obj."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        filenames = super()._generateToggleState(obj, **args)
        result = list(map(self._convertFilenameToIcon, filenames))
        if result:
            return result

        return []

    def _generateVisitedState(self, obj, **args):
        """Returns an array of sounds indicating the visited state of obj."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        if not args.get('mode', None):
            args['mode'] = self._mode

        args['stringType'] = 'visited'
        if obj.getState().contains(pyatspi.STATE_VISITED):
            filenames = [self._script.formatting.getString(**args)]
            result = list(map(self._convertFilenameToIcon, filenames))
            if result:
                return result

        return []

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _generatePercentage(self, obj, **args):
        """Returns an array of sounds reflecting the percentage of obj."""

        if not _settingsManager.getSetting('playSoundForValue'):
            return []

        percent = self._script.utilities.getValueAsPercent(obj)
        if percent is None:
            return []

        return []

    def _generateProgressBarValue(self, obj, **args):
        """Returns an array of sounds representing the progress bar value."""

        if args.get('isProgressBarUpdate'):
            if not self._shouldPresentProgressBarUpdate(obj, **args):
                return []
        elif not _settingsManager.getSetting('playSoundForValue'):
            return []

        percent = self._script.utilities.getValueAsPercent(obj)
        if percent is None:
            return []

        # To better indicate the progress completion.
        if percent >= 99:
            duration = 1
        else:
            duration = 0.075

        # Reduce volume as pitch increases.
        volumeMultiplier = 1 - (percent / 120)

        # Adjusting so that the initial beeps are not too deep.
        if percent < 7:
            frequency = int(98 + percent * 5.4)
        else:
            frequency = int(percent * 22)

        return [Tone(duration, frequency, volumeMultiplier, Tone.SINE_WAVE)]

    def _getProgressBarUpdateInterval(self):
        interval = _settingsManager.getSetting('progressBarBeepInterval')
        if interval is None:
            return super()._getProgressBarUpdateInterval()

        return int(interval)

    def _shouldPresentProgressBarUpdate(self, obj, **args):
        if not _settingsManager.getSetting('beepProgressBarUpdates'):
            return False

        return super()._shouldPresentProgressBarUpdate(obj, **args)

    #####################################################################
    #                                                                   #
    # Role and hierarchical information                                 #
    #                                                                   #
    #####################################################################

    def _generatePositionInSet(self, obj, **args):
        """Returns an array of sounds reflecting the set position of obj."""

        if not _settingsManager.getSetting('playSoundForPositionInSet'):
            return []

        position, setSize = self._script.utilities.getPositionAndSetSize(obj)
        percent = int((position / setSize) * 100)

        return []

    def _generateRoleName(self, obj, **args):
        """Returns an array of sounds indicating the role of obj."""

        if not _settingsManager.getSetting('playSoundForRole'):
            return []

        role = args.get('role', obj.getRole())
        filename = Atspi.role_get_name(role).replace(' ', '_')
        result = self._convertFilenameToIcon(filename)
        if result:
            return [result]

        return []
