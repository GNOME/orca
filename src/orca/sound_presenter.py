# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2025 Igalia, S.L.
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

# pylint: disable=too-many-public-methods

"""Provides sound presentation support."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011-2025 Igalia, S.L."
__license__   = "LGPL"

from . import dbus_service
from . import debug
from . import settings

class SoundPresenter:
    """Provides sound presentation support."""

    def __init__(self) -> None:
        msg = "SOUND PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SoundPresenter", self)

    @dbus_service.getter
    def get_sound_is_enabled(self) -> bool:
        """Returns whether sound is enabled."""

        return settings.enableSound

    @dbus_service.setter
    def set_sound_is_enabled(self, value: bool) -> bool:
        """Sets whether sound is enabled."""

        msg = f"SOUND PRESENTER: Setting enable sound to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableSound = value
        return True

    @dbus_service.getter
    def get_sound_volume(self) -> float:
        """Returns the sound volume (0.0 to 1.0)."""

        return settings.soundVolume

    @dbus_service.setter
    def set_sound_volume(self, value: float) -> bool:
        """Sets the sound volume (0.0 to 1.0)."""

        msg = f"SOUND PRESENTER: Setting sound volume to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.soundVolume = value
        return True

    @dbus_service.getter
    def get_beep_progress_bar_updates(self) -> bool:
        """Returns whether beep progress bar updates are enabled."""

        return settings.beepProgressBarUpdates

    @dbus_service.setter
    def set_beep_progress_bar_updates(self, value: bool) -> bool:
        """Sets whether beep progress bar updates are enabled."""

        msg = f"SOUND PRESENTER: Setting beep progress bar updates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.beepProgressBarUpdates = value
        return True

    @dbus_service.getter
    def get_progress_bar_beep_interval(self) -> int:
        """Returns the beep progress bar update interval in seconds."""

        return settings.progressBarBeepInterval

    @dbus_service.setter
    def set_progress_bar_beep_interval(self, value: int) -> bool:
        """Sets the beep progress bar update interval in seconds."""

        msg = f"SOUND PRESENTER: Setting progress bar beep interval to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarBeepInterval = value
        return True

    @dbus_service.getter
    def get_progress_bar_beep_verbosity(self) -> int:
        """Returns the beep progress bar verbosity level."""

        return settings.progressBarBeepVerbosity

    @dbus_service.setter
    def set_progress_bar_beep_verbosity(self, value: int) -> bool:
        """Sets the beep progress bar verbosity level."""

        msg = f"SOUND PRESENTER: Setting progress bar beep verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarBeepVerbosity = value
        return True


_presenter: SoundPresenter = SoundPresenter()

def get_presenter() -> SoundPresenter:
    """Returns the Sound Presenter"""

    return _presenter
