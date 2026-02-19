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
# pylint: disable=wrong-import-position

"""Provides sound presentation support."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import time
from enum import Enum
from typing import Any, TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import dbus_service
from . import debug
from . import gsettings_registry
from . import guilabels
from . import preferences_grid_base
from . import sound

if TYPE_CHECKING:
    from .sound import Icon, Tone


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.ProgressBarVerbosity",
    values={"all": 0, "application": 1, "window": 2},
)
class ProgressBarVerbosity(Enum):
    """Progress bar verbosity level enumeration."""

    ALL = 0
    APPLICATION = 1
    WINDOW = 2

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


class SoundProgressBarsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Sound Progress Bars preferences page."""

    def __init__(self, presenter: SoundPresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_BEEP_UPDATES,
                getter=presenter.get_beep_progress_bar_updates,
                setter=presenter.set_beep_progress_bar_updates,
                prefs_key="beepProgressBarUpdates",
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_beep_interval,
                setter=presenter.set_progress_bar_beep_interval,
                prefs_key="progressBarBeepInterval",
                minimum=0,
                maximum=100,
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
                    ProgressBarVerbosity.ALL.value,
                    ProgressBarVerbosity.APPLICATION.value,
                    ProgressBarVerbosity.WINDOW.value,
                ],
            ),
        ]

        super().__init__(guilabels.PROGRESS_BARS, controls)


class SoundPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Sound preferences page with nested stack navigation."""

    def __init__(
        self,
        presenter: SoundPresenter,
        title_change_callback: preferences_grid_base.Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(guilabels.SOUND)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._progress_bars_grid = SoundProgressBarsPreferencesGrid(presenter)
        self._volume_scale: Gtk.Scale | None = None
        self._volume_listbox: preferences_grid_base.FocusManagedListBox | None = None

        self._build()
        self._initializing = False
        self.refresh()

    def _build(self) -> None:
        """Build the nested stack UI."""

        row = 0

        categories = [
            (guilabels.PROGRESS_BARS, "progress-bars", self._progress_bars_grid),
        ]

        enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=guilabels.SOUND_ENABLE_SOUND_SUPPORT,
            enable_getter=self._presenter.get_sound_is_enabled,
            enable_setter=self._presenter.set_sound_is_enabled,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.SOUND,
        )

        self.attach(enable_listbox, 0, row, 1, 1)
        row += 1

        # Volume slider on the main page
        self._volume_listbox = preferences_grid_base.FocusManagedListBox()

        volume_adj = Gtk.Adjustment(
            value=self._presenter.get_sound_volume(),
            lower=0.0,
            upper=1.0,
            step_increment=0.1,
            page_increment=0.1,
        )
        volume_row, self._volume_scale, _volume_label = self._create_slider_row(
            guilabels.SOUND_VOLUME,
            volume_adj,
            changed_handler=self._on_volume_changed,
            include_top_separator=False,
        )
        self._volume_listbox.add_row_with_widget(volume_row, self._volume_scale)
        self._volume_listbox.set_sensitive(self._presenter.get_sound_is_enabled())

        self.attach(self._volume_listbox, 0, row, 1, 1)
        row += 1

        self.attach(stack, 0, row, 1, 1)

    def _on_volume_changed(self, scale: Gtk.Scale) -> None:
        """Handle volume slider change."""

        if self._initializing:
            return
        value = scale.get_value()
        self._presenter.set_sound_volume(value)
        self._has_unsaved_changes = True

    def _on_multipage_enable_toggled(
        self,
        switch: Gtk.Switch,
        setter: preferences_grid_base.Callable[[bool], preferences_grid_base.Any],
    ) -> None:
        """Handle enable switch toggle - also controls volume slider sensitivity."""

        super()._on_multipage_enable_toggled(switch, setter)
        if self._volume_listbox is not None:
            self._volume_listbox.set_sensitive(switch.get_active())

    def _on_multipage_category_activated(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Handle category activation - also hide volume slider."""

        super()._on_multipage_category_activated(listbox, row)
        if self._volume_listbox is not None:
            self._volume_listbox.hide()

    def multipage_show_categories(self) -> None:
        """Switch back to categories view - also show volume slider."""

        super().multipage_show_categories()
        if self._volume_listbox is not None:
            self._volume_listbox.show()

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self.multipage_on_becoming_visible()

    def reload(self) -> None:
        """Fetch fresh values and update UI."""

        self._initializing = True
        self._has_unsaved_changes = False

        enabled = self._presenter.get_sound_is_enabled()
        if self._volume_listbox is not None:
            self._volume_listbox.set_sensitive(enabled)
        if self._volume_scale is not None:
            self._volume_scale.set_value(self._presenter.get_sound_volume())
        self._progress_bars_grid.reload()

        self._initializing = False

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Persist staged values."""

        result: dict[str, Any] = {}
        result["enableSound"] = self._presenter.get_sound_is_enabled()
        result["soundVolume"] = self._presenter.get_sound_volume()
        result.update(self._progress_bars_grid.save_settings())

        if profile:
            skip = not app_name and profile == "default"
            gsettings_registry.get_registry().save_schema_to_gsettings(
                "sound", result, profile, app_name, skip
            )

        return result

    def refresh(self) -> None:
        """Update widgets from staged values."""

        self._initializing = True
        if self._volume_scale is not None:
            self._volume_scale.set_value(self._presenter.get_sound_volume())
        self._progress_bars_grid.refresh()
        self._initializing = False

    def has_changes(self) -> bool:
        """Return True if any child grid has unsaved changes."""

        return self._progress_bars_grid.has_changes() or self._has_unsaved_changes


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Sound", name="sound")
class SoundPresenter:
    """Provides sound presentation support."""

    _SCHEMA = "sound"

    def _get_setting(self, key: str, gtype: str, default: Any) -> Any:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA, key, gtype, default=default
        )

    def __init__(self) -> None:
        msg = "SOUND PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SoundPresenter", self)
        self._progress_bar_cache: dict = {}

    def create_preferences_grid(
        self, title_change_callback: preferences_grid_base.Callable[[str], None] | None = None
    ) -> SoundPreferencesGrid:
        """Returns the GtkGrid containing the preferences UI."""

        return SoundPreferencesGrid(self, title_change_callback)

    @gsettings_registry.get_registry().gsetting(
        key="enabled",
        schema="sound",
        gtype="b",
        default=True,
        summary="Enable sound output",
        settings_key="enableSound",
    )
    @dbus_service.getter
    def get_sound_is_enabled(self) -> bool:
        """Returns whether sound is enabled."""

        return self._get_setting("enabled", "b", True)

    @dbus_service.setter
    def set_sound_is_enabled(self, value: bool) -> bool:
        """Sets whether sound is enabled."""

        msg = f"SOUND PRESENTER: Setting enable sound to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "enabled", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="volume",
        schema="sound",
        gtype="d",
        default=0.5,
        summary="Sound volume (0.0-1.0)",
        settings_key="soundVolume",
    )
    @dbus_service.getter
    def get_sound_volume(self) -> float:
        """Returns the sound volume (0.0 to 1.0)."""

        return self._get_setting("volume", "d", 0.5)

    @dbus_service.setter
    def set_sound_volume(self, value: float) -> bool:
        """Sets the sound volume (0.0 to 1.0)."""

        msg = f"SOUND PRESENTER: Setting sound volume to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "volume", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="beep-progress-bar-updates",
        schema="sound",
        gtype="b",
        default=False,
        summary="Beep progress bar updates",
        settings_key="beepProgressBarUpdates",
    )
    @dbus_service.getter
    def get_beep_progress_bar_updates(self) -> bool:
        """Returns whether beep progress bar updates are enabled."""

        return self._get_setting("beep-progress-bar-updates", "b", False)

    @dbus_service.setter
    def set_beep_progress_bar_updates(self, value: bool) -> bool:
        """Sets whether beep progress bar updates are enabled."""

        msg = f"SOUND PRESENTER: Setting beep progress bar updates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, "beep-progress-bar-updates", value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="progress-bar-beep-interval",
        schema="sound",
        gtype="i",
        default=0,
        summary="Progress bar beep interval in seconds",
        settings_key="progressBarBeepInterval",
    )
    @dbus_service.getter
    def get_progress_bar_beep_interval(self) -> int:
        """Returns the beep progress bar update interval in seconds."""

        return self._get_setting("progress-bar-beep-interval", "i", 0)

    @dbus_service.setter
    def set_progress_bar_beep_interval(self, value: int) -> bool:
        """Sets the beep progress bar update interval in seconds."""

        msg = f"SOUND PRESENTER: Setting progress bar beep interval to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, "progress-bar-beep-interval", value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="progress-bar-beep-verbosity",
        schema="sound",
        genum="org.gnome.Orca.ProgressBarVerbosity",
        default="application",
        summary="Progress bar beep verbosity (all, application, window)",
        settings_key="progressBarBeepVerbosity",
    )
    @dbus_service.getter
    def get_progress_bar_beep_verbosity(self) -> int:
        """Returns the beep progress bar verbosity level."""

        nick = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "progress-bar-beep-verbosity",
            "",
            genum="org.gnome.Orca.ProgressBarVerbosity",
            default="application",
        )
        return ProgressBarVerbosity[nick.upper()].value

    @dbus_service.setter
    def set_progress_bar_beep_verbosity(self, value: int) -> bool:
        """Sets the beep progress bar verbosity level."""

        msg = f"SOUND PRESENTER: Setting progress bar beep verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        level = ProgressBarVerbosity(value)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, "progress-bar-beep-verbosity", level.name.lower()
        )
        return True

    def should_present_progress_bar_update(
        self,
        obj: object,
        percent: int | None,
        is_same_app: bool,
        is_same_window: bool,
    ) -> bool:
        """Returns True if the progress bar update should be beeped."""

        if not self.get_beep_progress_bar_updates():
            return False

        last_time, last_value = self._progress_bar_cache.get(id(obj), (0.0, None))
        if percent == last_value:
            return False

        if percent != 100:
            interval = int(time.time() - last_time)
            if interval < self.get_progress_bar_beep_interval():
                return False

        verbosity = self.get_progress_bar_beep_verbosity()
        if verbosity == ProgressBarVerbosity.ALL.value:
            present = True
        elif verbosity == ProgressBarVerbosity.APPLICATION.value:
            present = is_same_app
        elif verbosity == ProgressBarVerbosity.WINDOW.value:
            present = is_same_window
        else:
            present = True

        if present:
            self._progress_bar_cache[id(obj)] = (time.time(), percent)

        return present

    def play(self, sounds: list[Icon | Tone] | Icon | Tone, interrupt: bool = True) -> None:
        """Plays the specified sound(s)."""

        if not sounds:
            return

        if not isinstance(sounds, list):
            sounds = [sounds]

        player = sound.get_player()
        player.play(sounds[0], interrupt)
        for i in range(1, len(sounds)):
            player.play(sounds[i], interrupt=False)

    def init_sound(self) -> None:
        """Initializes sound if enabled."""

        if not self.get_sound_is_enabled():
            return

        sound.get_player().init()

    def shutdown_sound(self) -> None:
        """Shuts down sound."""

        sound.get_player().shutdown()


_presenter: SoundPresenter = SoundPresenter()


def get_presenter() -> SoundPresenter:
    """Returns the Sound Presenter"""

    return _presenter
