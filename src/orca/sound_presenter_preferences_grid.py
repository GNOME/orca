# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Preferences grids for sound presentation support."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import (
    gsettings_registry,
    guilabels,
    orca_gui_helpers,
    preferences_grid_base,
    sound_presenter,
)

if TYPE_CHECKING:
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    from .sound_presenter import SoundPresenter


class SoundProgressBarsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Sound Progress Bars preferences page."""

    _documentation_summary = (
        "Use these settings to decide whether progress-bar changes are indicated with beeps."
    )

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for sound progress-bar preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.PROGRESS_BARS,
            panel_id="sound_presenter.progress-bars",
            description=(
                "Progress bar settings control whether Orca indicates progress-bar "
                "changes with beeps, how often beeps occur, and which progress bars apply."
            ),
            schema="sound",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.GENERAL_BEEP_UPDATES,
                    kind="switch",
                    summary="Controls whether Orca periodically beeps for progress-bar updates.",
                    schema="sound",
                    key=sound_presenter.SoundPresenter.KEY_BEEP_PROGRESS_BAR_UPDATES,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.GENERAL_FREQUENCY_SECS,
                    kind="spin",
                    summary="Sets how often Orca beeps for progress-bar updates.",
                    schema="sound",
                    key=sound_presenter.SoundPresenter.KEY_PROGRESS_BAR_BEEP_INTERVAL,
                    minimum="0",
                    maximum="100",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.GENERAL_APPLIES_TO,
                    kind="combo",
                    summary="Selects which progress bars produce beep updates.",
                    schema="sound",
                    key=sound_presenter.SoundPresenter.KEY_PROGRESS_BAR_BEEP_VERBOSITY,
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.PROGRESS_BAR_ALL,
                            summary="Progress bars in all applications.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.PROGRESS_BAR_APPLICATION,
                            summary="Progress bars in the active application.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.PROGRESS_BAR_WINDOW,
                            summary="Progress bars in the active window.",
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, presenter: SoundPresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_BEEP_UPDATES,
                getter=presenter.get_beep_progress_bar_updates,
                setter=presenter.set_beep_progress_bar_updates,
                prefs_key=sound_presenter.SoundPresenter.KEY_BEEP_PROGRESS_BAR_UPDATES,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_beep_interval,
                setter=presenter.set_progress_bar_beep_interval,
                prefs_key=sound_presenter.SoundPresenter.KEY_PROGRESS_BAR_BEEP_INTERVAL,
                minimum=0,
                maximum=100,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=presenter.get_progress_bar_beep_verbosity,
                setter=presenter.set_progress_bar_beep_verbosity,
                prefs_key=sound_presenter.SoundPresenter.KEY_PROGRESS_BAR_BEEP_VERBOSITY,
                options=[
                    guilabels.PROGRESS_BAR_ALL,
                    guilabels.PROGRESS_BAR_APPLICATION,
                    guilabels.PROGRESS_BAR_WINDOW,
                ],
                values=[
                    sound_presenter.ProgressBarVerbosity.ALL.value,
                    sound_presenter.ProgressBarVerbosity.APPLICATION.value,
                    sound_presenter.ProgressBarVerbosity.WINDOW.value,
                ],
            ),
        ]

        super().__init__(guilabels.PROGRESS_BARS, controls)


class SoundPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Sound preferences page with nested stack navigation."""

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for sound output preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.SOUND,
            panel_id="manual.sound-output",
            description=(
                "Sound settings control Orca's non-speech audio output. The list contains "
                "sound-related settings and pages.\n\n"
                "Activate a row, or press Right Arrow, to open its settings. Press "
                "Left Arrow, Escape, or Alt+Left to return to the list."
            ),
            show_available_settings=False,
            schema="sound",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SOUND_ENABLE_SOUND_SUPPORT,
                    kind="switch",
                    summary="Turns sound output on or off.",
                    schema="sound",
                    key=sound_presenter.SoundPresenter.KEY_ENABLED,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SOUND_VOLUME,
                    kind="number",
                    summary="Sets the volume for Orca sounds.",
                    schema="sound",
                    key=sound_presenter.SoundPresenter.KEY_VOLUME,
                    minimum="0.0",
                    maximum="1.0",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.PROGRESS_BARS,
                    kind="page",
                    summary="Opens settings for when Orca beeps for progress-bar updates.",
                ),
            ),
        )

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
        self._volume_listbox: preferences_grid_base.PreferencesFocusManagedListBox | None = None

        self._build()
        self._initializing = False

    def _build(self) -> None:
        """Build the nested stack UI."""

        row = 0

        categories = [
            (guilabels.PROGRESS_BARS, "progress-bars", self._progress_bars_grid),
        ]

        enable_listbox, stack, _categories_listbox = self._create_child_grid_preferences_stack(
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
        self._volume_listbox = preferences_grid_base.PreferencesFocusManagedListBox()

        volume_row, self._volume_scale, _volume_label = orca_gui_helpers.create_range_slider_row(
            guilabels.SOUND_VOLUME,
            self._presenter.get_sound_volume(),
            0.0,
            1.0,
            changed_handler=self._on_volume_changed,
            include_top_separator=False,
            digits=1,
            steps=10,
            page_steps=10,
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
        result["enabled"] = self._presenter.get_sound_is_enabled()
        result["volume"] = self._presenter.get_sound_volume()
        result.update(self._progress_bars_grid.save_settings())

        if profile:
            skip = not app_name and profile == "default"
            gsettings_registry.get_registry().save_schema("sound", result, profile, app_name, skip)

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
