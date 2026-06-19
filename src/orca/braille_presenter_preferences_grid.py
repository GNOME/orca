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

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines

"""Preferences grids for braille presentation support."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import braille_presenter, gsettings_registry, guilabels, preferences_grid_base

if TYPE_CHECKING:
    from collections.abc import Callable

    from .braille_presenter import BraillePresenter


class BrailleVerbosityPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Braille Verbosity preferences page."""

    def __init__(self, presenter: BraillePresenter) -> None:
        self._presenter = presenter
        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.OBJECT_PRESENTATION_IS_DETAILED,
                getter=presenter._get_verbosity_is_detailed,
                setter=presenter._set_verbosity_is_detailed,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_SHOW_CONTEXT,
                getter=presenter.get_display_ancestors,
                setter=presenter.set_display_ancestors,
                prefs_key=braille_presenter.BraillePresenter.KEY_DISPLAY_ANCESTORS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ABBREVIATED_ROLE_NAMES,
                getter=presenter._get_use_abbreviated_rolenames,
                setter=presenter._set_use_abbreviated_rolenames,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.PRESENT_OBJECT_MNEMONICS,
                getter=presenter.get_present_mnemonics,
                setter=presenter.set_present_mnemonics,
                prefs_key=braille_presenter.BraillePresenter.KEY_PRESENT_MNEMONICS,
            ),
        ]

        super().__init__(guilabels.VERBOSITY, controls)

    def save_settings(self, profile: str = "", app_name: str = "") -> dict[str, Any]:
        """Save settings, writing enum values for verbosity and rolename style."""

        result = super().save_settings(profile, app_name)
        result[braille_presenter.BraillePresenter.KEY_VERBOSITY_LEVEL] = (
            self._presenter.get_verbosity_level()
        )
        rolename_style = self._presenter.get_rolename_style().upper()
        result[braille_presenter.BraillePresenter.KEY_ROLENAME_STYLE] = (
            braille_presenter.VerbosityLevel[rolename_style].value
        )
        return result


class BrailleDisplaySettingsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Braille Display Settings preferences page."""

    def __init__(self, presenter: BraillePresenter) -> None:
        table_dict = presenter.get_contraction_tables_dict()
        table_names = sorted(table_dict.keys()) if table_dict else []
        table_paths = [table_dict[name] for name in table_names] if table_dict else []

        self._enable_contracted_control = preferences_grid_base.BooleanPreferenceControl(
            label=guilabels.BRAILLE_ENABLE_CONTRACTED_BRAILLE,
            getter=presenter.get_contracted_braille_is_enabled,
            setter=presenter.set_contracted_braille_is_enabled,
            prefs_key=braille_presenter.BraillePresenter.KEY_CONTRACTED_BRAILLE,
        )

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.EnumPreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_END_OF_LINE_SYMBOL,
                getter=presenter.get_end_of_line_indicator_is_enabled,
                setter=presenter.set_end_of_line_indicator_is_enabled,
                prefs_key=braille_presenter.BraillePresenter.KEY_END_OF_LINE_INDICATOR,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_WORD_WRAP,
                getter=presenter.get_word_wrap_is_enabled,
                setter=presenter.set_word_wrap_is_enabled,
                prefs_key=braille_presenter.BraillePresenter.KEY_WORD_WRAP,
            ),
            self._enable_contracted_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_COMPUTER_BRAILLE_AT_CURSOR,
                getter=presenter.get_computer_braille_at_cursor_is_enabled,
                setter=presenter.set_computer_braille_at_cursor_is_enabled,
                prefs_key=braille_presenter.BraillePresenter.KEY_COMPUTER_BRAILLE_AT_CURSOR,
                determine_sensitivity=self._contracted_enabled,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_CONTRACTION_TABLE,
                options=table_names,
                values=table_paths,
                getter=presenter.get_contraction_table_path,
                setter=presenter.set_contraction_table_from_path,
                prefs_key=braille_presenter.BraillePresenter.KEY_CONTRACTION_TABLE,
                determine_sensitivity=self._contracted_enabled,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_HYPERLINK_INDICATOR,
                options=[
                    guilabels.BRAILLE_DOT_NONE,
                    guilabels.BRAILLE_DOT_7,
                    guilabels.BRAILLE_DOT_8,
                    guilabels.BRAILLE_DOT_7_8,
                ],
                values=[
                    braille_presenter.BrailleIndicator.NONE.value,
                    braille_presenter.BrailleIndicator.DOT7.value,
                    braille_presenter.BrailleIndicator.DOT8.value,
                    braille_presenter.BrailleIndicator.DOTS78.value,
                ],
                getter=presenter._get_link_indicator_as_int,
                setter=presenter.set_link_indicator_from_int,
                prefs_key=braille_presenter.BraillePresenter.KEY_LINK_INDICATOR,
                member_of=guilabels.BRAILLE_INDICATORS,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_SELECTION_INDICATOR,
                options=[
                    guilabels.BRAILLE_DOT_NONE,
                    guilabels.BRAILLE_DOT_7,
                    guilabels.BRAILLE_DOT_8,
                    guilabels.BRAILLE_DOT_7_8,
                ],
                values=[
                    braille_presenter.BrailleIndicator.NONE.value,
                    braille_presenter.BrailleIndicator.DOT7.value,
                    braille_presenter.BrailleIndicator.DOT8.value,
                    braille_presenter.BrailleIndicator.DOTS78.value,
                ],
                getter=presenter._get_selector_indicator_as_int,
                setter=presenter.set_selector_indicator_from_int,
                prefs_key=braille_presenter.BraillePresenter.KEY_SELECTOR_INDICATOR,
                member_of=guilabels.BRAILLE_INDICATORS,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_TEXT_ATTRIBUTES_INDICATOR,
                options=[
                    guilabels.BRAILLE_DOT_NONE,
                    guilabels.BRAILLE_DOT_7,
                    guilabels.BRAILLE_DOT_8,
                    guilabels.BRAILLE_DOT_7_8,
                ],
                values=[
                    braille_presenter.BrailleIndicator.NONE.value,
                    braille_presenter.BrailleIndicator.DOT7.value,
                    braille_presenter.BrailleIndicator.DOT8.value,
                    braille_presenter.BrailleIndicator.DOTS78.value,
                ],
                getter=presenter._get_text_attributes_indicator_as_int,
                setter=presenter.set_text_attributes_indicator_from_int,
                prefs_key=braille_presenter.BraillePresenter.KEY_TEXT_ATTRIBUTES_INDICATOR,
                member_of=guilabels.BRAILLE_INDICATORS,
            ),
        ]

        super().__init__(guilabels.BRAILLE_DISPLAY_SETTINGS, controls)

    def _contracted_enabled(self) -> bool:
        """Check if contracted braille is enabled in the UI."""

        widget = self.get_widget_for_control(self._enable_contracted_control)
        return widget.get_active() if widget else True


class BrailleFlashMessagesPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Braille Flash Messages preferences page."""

    def __init__(self, presenter: BraillePresenter) -> None:
        self._presenter = presenter
        self._flash_persistent_control = preferences_grid_base.BooleanPreferenceControl(
            label=guilabels.BRAILLE_MESSAGES_ARE_PERSISTENT,
            getter=presenter.get_flash_messages_are_persistent,
            setter=presenter.set_flash_messages_are_persistent,
            prefs_key=braille_presenter.BraillePresenter.KEY_FLASH_MESSAGES_PERSISTENT,
        )

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.IntRangePreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_FLASH_MESSAGES,
                getter=presenter.get_flash_messages_are_enabled,
                setter=presenter.set_flash_messages_are_enabled,
                prefs_key=braille_presenter.BraillePresenter.KEY_FLASH_MESSAGES,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_MESSAGES_ARE_DETAILED,
                getter=presenter.get_flash_messages_are_detailed,
                setter=presenter.set_flash_messages_are_detailed,
                prefs_key=braille_presenter.BraillePresenter.KEY_FLASH_MESSAGES_DETAILED,
            ),
            self._flash_persistent_control,
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.BRAILLE_DURATION_SECS,
                minimum=1,
                maximum=100,
                getter=presenter._get_flash_duration_seconds,
                setter=presenter._set_flash_duration_seconds,
                determine_sensitivity=self._flash_not_persistent,
            ),
        ]

        super().__init__(guilabels.BRAILLE_FLASH_MESSAGES, controls)

    def _flash_not_persistent(self) -> bool:
        """Check if flash messages are not persistent in the UI."""

        widget = self.get_widget_for_control(self._flash_persistent_control)
        return not widget.get_active() if widget else True

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Persist staged values, including flash-message-duration in milliseconds."""

        result = super().save_settings(profile, app_name)
        result[braille_presenter.BraillePresenter.KEY_FLASH_MESSAGE_DURATION] = (
            self._presenter.get_flash_message_duration()
        )
        return result


class BrailleProgressBarsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Braille Progress Bars preferences page."""

    def __init__(self, presenter: BraillePresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_BRAILLE_UPDATES,
                getter=presenter.get_braille_progress_bar_updates,
                setter=presenter.set_braille_progress_bar_updates,
                prefs_key=braille_presenter.BraillePresenter.KEY_BRAILLE_PROGRESS_BAR_UPDATES,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_braille_interval,
                setter=presenter.set_progress_bar_braille_interval,
                prefs_key=braille_presenter.BraillePresenter.KEY_PROGRESS_BAR_BRAILLE_INTERVAL,
                minimum=0,
                maximum=100,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=presenter.get_progress_bar_braille_verbosity,
                setter=presenter.set_progress_bar_braille_verbosity,
                prefs_key=braille_presenter.BraillePresenter.KEY_PROGRESS_BAR_BRAILLE_VERBOSITY,
                options=[
                    guilabels.PROGRESS_BAR_ALL,
                    guilabels.PROGRESS_BAR_APPLICATION,
                    guilabels.PROGRESS_BAR_WINDOW,
                ],
                values=[
                    braille_presenter.ProgressBarVerbosity.ALL.value,
                    braille_presenter.ProgressBarVerbosity.APPLICATION.value,
                    braille_presenter.ProgressBarVerbosity.WINDOW.value,
                ],
            ),
        ]

        super().__init__(guilabels.PROGRESS_BARS, controls)


class BrailleOSDPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the braille on-screen display preferences page."""

    def __init__(self, presenter: BraillePresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.BRAILLE_MONITOR_CELL_COUNT,
                getter=presenter.get_monitor_cell_count,
                setter=presenter.set_monitor_cell_count,
                prefs_key=braille_presenter.BraillePresenter.KEY_MONITOR_CELL_COUNT,
                minimum=1,
                maximum=80,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_MONITOR_SHOW_DOTS,
                getter=presenter.get_monitor_show_dots,
                setter=presenter.set_monitor_show_dots,
                prefs_key=braille_presenter.BraillePresenter.KEY_MONITOR_SHOW_DOTS,
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.BRAILLE_MONITOR_FOREGROUND,
                getter=presenter.get_monitor_foreground,
                setter=presenter.set_monitor_foreground,
                prefs_key=braille_presenter.BraillePresenter.KEY_MONITOR_FOREGROUND,
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.BRAILLE_MONITOR_BACKGROUND,
                getter=presenter.get_monitor_background,
                setter=presenter.set_monitor_background,
                prefs_key=braille_presenter.BraillePresenter.KEY_MONITOR_BACKGROUND,
            ),
        ]

        super().__init__(
            guilabels.ON_SCREEN_DISPLAY,
            controls,
            info_message=guilabels.BRAILLE_MONITOR_INFO,
        )


# pylint: disable-next=too-many-instance-attributes
class BraillePreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Braille preferences page with nested stack navigation."""

    def __init__(
        self,
        presenter: BraillePresenter,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(guilabels.BRAILLE)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._verbosity_grid = BrailleVerbosityPreferencesGrid(presenter)
        self._display_settings_grid = BrailleDisplaySettingsPreferencesGrid(presenter)
        self._flash_messages_grid = BrailleFlashMessagesPreferencesGrid(presenter)
        self._progress_bars_grid = BrailleProgressBarsPreferencesGrid(presenter)
        self._osd_grid = BrailleOSDPreferencesGrid(presenter)

        self._build()
        self._initializing = False

    def _build(self) -> None:
        """Build the nested stack UI."""

        row = 0

        categories = [
            (guilabels.VERBOSITY, "verbosity", self._verbosity_grid),
            (guilabels.BRAILLE_DISPLAY_SETTINGS, "display_settings", self._display_settings_grid),
            (guilabels.BRAILLE_FLASH_MESSAGES, "flash_messages", self._flash_messages_grid),
            (guilabels.PROGRESS_BARS, "progress-bars", self._progress_bars_grid),
            (guilabels.ON_SCREEN_DISPLAY, "osd", self._osd_grid),
        ]

        enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=guilabels.BRAILLE_ENABLE_BRAILLE_SUPPORT,
            enable_getter=self._presenter.get_braille_is_enabled,
            enable_setter=self._presenter.set_braille_is_enabled,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.BRAILLE,
        )

        self.attach(enable_listbox, 0, row, 1, 1)
        row += 1
        self.attach(stack, 0, row, 1, 1)

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self.multipage_on_becoming_visible()

    def reload(self) -> None:
        """Fetch fresh values and update UI."""

        self._initializing = True
        self._has_unsaved_changes = False
        self._verbosity_grid.reload()
        self._display_settings_grid.reload()
        self._flash_messages_grid.reload()
        self._progress_bars_grid.reload()
        self._osd_grid.reload()
        self._initializing = False

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Persist staged values."""

        assert self._multipage_enable_switch is not None
        result: dict[str, Any] = {}
        result[braille_presenter.BraillePresenter.KEY_ENABLED] = (
            self._multipage_enable_switch.get_active()
        )
        result.update(self._verbosity_grid.save_settings())
        result.update(self._display_settings_grid.save_settings())
        result.update(self._flash_messages_grid.save_settings())
        result.update(self._progress_bars_grid.save_settings())
        result.update(self._osd_grid.save_settings())

        if profile:
            skip = not app_name and profile == "default"
            gsettings_registry.get_registry().save_schema(
                "braille",
                result,
                profile,
                app_name,
                skip,
            )

        return result

    def refresh(self) -> None:
        """Update widgets from staged values."""

        self._initializing = True
        self._verbosity_grid.refresh()
        self._display_settings_grid.refresh()
        self._flash_messages_grid.refresh()
        self._progress_bars_grid.refresh()
        self._osd_grid.refresh()
        self._initializing = False

    def has_changes(self) -> bool:
        """Return True if there are unsaved changes."""

        return (
            self._has_unsaved_changes
            or self._verbosity_grid.has_changes()
            or self._display_settings_grid.has_changes()
            or self._flash_messages_grid.has_changes()
            or self._progress_bars_grid.has_changes()
            or self._osd_grid.has_changes()
        )
