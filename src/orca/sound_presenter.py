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

from typing import Any

from . import dbus_service
from . import debug
from . import guilabels
from . import preferences_grid_base
from . import settings


class SoundGeneralPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Sound General preferences page."""

    def __init__(self, presenter: SoundPresenter) -> None:
        controls = [
            preferences_grid_base.FloatRangePreferenceControl(
                label=guilabels.SOUND_VOLUME,
                getter=presenter.get_sound_volume,
                setter=presenter.set_sound_volume,
                prefs_key="soundVolume",
                minimum=0.0,
                maximum=1.0
            ),
        ]

        super().__init__(guilabels.GENERAL, controls)


class SoundProgressBarsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Sound Progress Bars preferences page."""

    def __init__(self, presenter: SoundPresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_BEEP_UPDATES,
                getter=presenter.get_beep_progress_bar_updates,
                setter=presenter.set_beep_progress_bar_updates,
                prefs_key="beepProgressBarUpdates"
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_beep_interval,
                setter=presenter.set_progress_bar_beep_interval,
                prefs_key="progressBarBeepInterval",
                minimum=0,
                maximum=100
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=presenter.get_progress_bar_beep_verbosity,
                setter=presenter.set_progress_bar_beep_verbosity,
                prefs_key="progressBarBeepVerbosity",
                options=[
                    guilabels.PROGRESS_BAR_ALL,
                    guilabels.PROGRESS_BAR_APPLICATION,
                    guilabels.PROGRESS_BAR_WINDOW,
                ],
                values=[
                    settings.PROGRESS_BAR_ALL,
                    settings.PROGRESS_BAR_APPLICATION,
                    settings.PROGRESS_BAR_WINDOW,
                ]
            ),
        ]

        super().__init__(guilabels.PROGRESS_BARS, controls)


class SoundPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Sound preferences page with nested stack navigation."""

    def __init__(
        self,
        presenter: SoundPresenter,
        title_change_callback: preferences_grid_base.Callable[[str], None] | None = None
    ) -> None:

        super().__init__(guilabels.SOUND)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._general_grid = SoundGeneralPreferencesGrid(presenter)
        self._progress_bars_grid = SoundProgressBarsPreferencesGrid(presenter)

        self._build()
        self._initializing = False
        self.refresh()

    def _build(self) -> None:
        """Build the nested stack UI."""

        row = 0

        categories = [
            (guilabels.GENERAL, "general", self._general_grid),
            (guilabels.PROGRESS_BARS, "progress-bars", self._progress_bars_grid),
        ]

        enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=guilabels.SOUND_ENABLE_SOUND_SUPPORT,
            enable_getter=self._presenter.get_sound_is_enabled,
            enable_setter=self._presenter.set_sound_is_enabled,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.SOUND
        )

        self.attach(enable_listbox, 0, row, 1, 1)
        row += 1
        self.attach(stack, 0, row, 1, 1)

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self.multipage_on_becoming_visible()

    def reload(self) -> None:
        """Fetch fresh values and update UI."""

        self._general_grid.reload()
        self._progress_bars_grid.reload()

    def save_settings(self) -> dict:
        """Persist staged values."""

        result: dict[str, Any] = {}
        result["enableSound"] = self._presenter.get_sound_is_enabled()
        result.update(self._general_grid.save_settings())
        result.update(self._progress_bars_grid.save_settings())
        return result

    def refresh(self) -> None:
        """Update widgets from staged values."""

        self._initializing = True
        self._general_grid.refresh()
        self._progress_bars_grid.refresh()
        self._initializing = False

    def has_changes(self) -> bool:
        """Return True if any child grid has unsaved changes."""

        return (
            self._general_grid.has_changes()
            or self._progress_bars_grid.has_changes()
            or self._has_unsaved_changes
        )


class SoundPresenter:
    """Provides sound presentation support."""

    def __init__(self) -> None:
        msg = "SOUND PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SoundPresenter", self)

    def create_preferences_grid(
        self,
        title_change_callback: preferences_grid_base.Callable[[str], None] | None = None
    ) -> SoundPreferencesGrid:
        """Returns the GtkGrid containing the preferences UI."""

        return SoundPreferencesGrid(self, title_change_callback)

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
