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

"""Provides braille presentation support."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import os
from enum import Enum
from typing import Any

from . import braille
from . import dbus_service
from . import debug
from . import guilabels
from . import input_event_manager
from . import preferences_grid_base
from . import settings
from .orca_platform import tablesdir # pylint: disable=import-error

class VerbosityLevel(Enum):
    """Verbosity level enumeration with int values from settings."""

    BRIEF = settings.VERBOSITY_LEVEL_BRIEF
    VERBOSE = settings.VERBOSITY_LEVEL_VERBOSE

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

class BrailleIndicator(Enum):
    """Braille indicator enumeration with int values from settings."""

    NONE = settings.BRAILLE_UNDERLINE_NONE
    DOT7 = settings.BRAILLE_UNDERLINE_7
    DOT8 = settings.BRAILLE_UNDERLINE_8
    DOTS78 = settings.BRAILLE_UNDERLINE_BOTH

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


class BrailleVerbosityPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Braille Verbosity preferences page."""

    def __init__(self, presenter: BraillePresenter) -> None:
        self._presenter = presenter
        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.OBJECT_PRESENTATION_IS_DETAILED,
                getter=presenter._get_verbosity_is_detailed,
                setter=presenter._set_verbosity_is_detailed,
                prefs_key="brailleVerbosityLevel"
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_SHOW_CONTEXT,
                getter=presenter.get_display_ancestors,
                setter=presenter.set_display_ancestors,
                prefs_key="enableBrailleContext"
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
                prefs_key="displayObjectMnemonic"
            ),
        ]

        super().__init__(guilabels.VERBOSITY, controls)

    def save_settings(self) -> dict[str, Any]:
        """Save settings, adding integer value for rolename style."""

        result = super().save_settings()
        result["brailleRolenameStyle"] = settings.brailleRolenameStyle
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
            prefs_key="enableContractedBraille"
        )

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.EnumPreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_DISABLE_END_OF_LINE_SYMBOL,
                getter=presenter._get_disable_eol,
                setter=presenter._set_disable_eol,
                prefs_key="disableBrailleEOL"
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_WORD_WRAP,
                getter=presenter.get_word_wrap_is_enabled,
                setter=presenter.set_word_wrap_is_enabled,
                prefs_key="enableBrailleWordWrap"
            ),
            self._enable_contracted_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_COMPUTER_BRAILLE_AT_CURSOR,
                getter=presenter.get_computer_braille_at_cursor_is_enabled,
                setter=presenter.set_computer_braille_at_cursor_is_enabled,
                prefs_key="enableComputerBrailleAtCursor",
                determine_sensitivity=self._contracted_enabled
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_CONTRACTION_TABLE,
                options=table_names,
                values=table_paths,
                getter=presenter.get_contraction_table_path,
                setter=presenter.set_contraction_table_from_path,
                prefs_key="brailleContractionTable",
                determine_sensitivity=self._contracted_enabled
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_HYPERLINK_INDICATOR,
                options=[
                    guilabels.BRAILLE_DOT_NONE,
                    guilabels.BRAILLE_DOT_7,
                    guilabels.BRAILLE_DOT_8,
                    guilabels.BRAILLE_DOT_7_8
                ],
                values=[
                    settings.BRAILLE_UNDERLINE_NONE,
                    settings.BRAILLE_UNDERLINE_7,
                    settings.BRAILLE_UNDERLINE_8,
                    settings.BRAILLE_UNDERLINE_BOTH
                ],
                getter=presenter._get_link_indicator_as_int,
                setter=presenter.set_link_indicator_from_int,
                prefs_key="brailleLinkIndicator",
                member_of=guilabels.BRAILLE_INDICATORS
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_SELECTION_INDICATOR,
                options=[
                    guilabels.BRAILLE_DOT_NONE,
                    guilabels.BRAILLE_DOT_7,
                    guilabels.BRAILLE_DOT_8,
                    guilabels.BRAILLE_DOT_7_8
                ],
                values=[
                    settings.BRAILLE_UNDERLINE_NONE,
                    settings.BRAILLE_UNDERLINE_7,
                    settings.BRAILLE_UNDERLINE_8,
                    settings.BRAILLE_UNDERLINE_BOTH
                ],
                getter=presenter._get_selector_indicator_as_int,
                setter=presenter.set_selector_indicator_from_int,
                prefs_key="brailleSelectorIndicator",
                member_of=guilabels.BRAILLE_INDICATORS
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_TEXT_ATTRIBUTES_INDICATOR,
                options=[
                    guilabels.BRAILLE_DOT_NONE,
                    guilabels.BRAILLE_DOT_7,
                    guilabels.BRAILLE_DOT_8,
                    guilabels.BRAILLE_DOT_7_8
                ],
                values=[
                    settings.BRAILLE_UNDERLINE_NONE,
                    settings.BRAILLE_UNDERLINE_7,
                    settings.BRAILLE_UNDERLINE_8,
                    settings.BRAILLE_UNDERLINE_BOTH
                ],
                getter=presenter._get_text_attributes_indicator_as_int,
                setter=presenter.set_text_attributes_indicator_from_int,
                prefs_key="textAttributesBrailleIndicator",
                member_of=guilabels.BRAILLE_INDICATORS
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
            prefs_key="flashIsPersistent"
        )

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.IntRangePreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_FLASH_MESSAGES,
                getter=presenter.get_flash_messages_are_enabled,
                setter=presenter.set_flash_messages_are_enabled,
                prefs_key="enableFlashMessages"
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_MESSAGES_ARE_DETAILED,
                getter=presenter.get_flash_messages_are_detailed,
                setter=presenter.set_flash_messages_are_detailed,
                prefs_key="flashIsDetailed"
            ),
            self._flash_persistent_control,
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.BRAILLE_DURATION_SECS,
                minimum=1,
                maximum=100,
                getter=presenter._get_flash_duration_seconds,
                setter=presenter._set_flash_duration_seconds,
                determine_sensitivity=self._flash_not_persistent
            ),
        ]

        super().__init__(guilabels.BRAILLE_FLASH_MESSAGES, controls)

    def _flash_not_persistent(self) -> bool:
        """Check if flash messages are not persistent in the UI."""

        widget = self.get_widget_for_control(self._flash_persistent_control)
        return not widget.get_active() if widget else True

    def save_settings(self) -> dict:
        """Persist staged values, including brailleFlashTime in milliseconds."""

        result = super().save_settings()
        result["brailleFlashTime"] = self._presenter.get_flash_message_duration()
        return result


class BrailleProgressBarsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Braille Progress Bars preferences page."""

    def __init__(self, presenter: BraillePresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_BRAILLE_UPDATES,
                getter=presenter.get_braille_progress_bar_updates,
                setter=presenter.set_braille_progress_bar_updates,
                prefs_key="brailleProgressBarUpdates"
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_braille_interval,
                setter=presenter.set_progress_bar_braille_interval,
                prefs_key="progressBarBrailleInterval",
                minimum=0,
                maximum=100
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=presenter.get_progress_bar_braille_verbosity,
                setter=presenter.set_progress_bar_braille_verbosity,
                prefs_key="progressBarBrailleVerbosity",
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


class BraillePreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Braille preferences page with nested stack navigation."""

    def __init__(
        self,
        presenter: BraillePresenter,
        title_change_callback: preferences_grid_base.Callable[[str], None] | None = None
    ) -> None:

        super().__init__(guilabels.BRAILLE)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._verbosity_grid = BrailleVerbosityPreferencesGrid(presenter)
        self._display_settings_grid = BrailleDisplaySettingsPreferencesGrid(presenter)
        self._flash_messages_grid = BrailleFlashMessagesPreferencesGrid(presenter)
        self._progress_bars_grid = BrailleProgressBarsPreferencesGrid(presenter)

        self._build()
        self._initializing = False
        self.refresh()

    def _build(self) -> None:
        """Build the nested stack UI."""

        row = 0

        categories = [
            (guilabels.VERBOSITY, "verbosity", self._verbosity_grid),
            (guilabels.BRAILLE_DISPLAY_SETTINGS, "display_settings", self._display_settings_grid),
            (guilabels.BRAILLE_FLASH_MESSAGES, "flash_messages", self._flash_messages_grid),
            (guilabels.PROGRESS_BARS, "progress-bars", self._progress_bars_grid),
        ]

        enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=guilabels.BRAILLE_ENABLE_BRAILLE_SUPPORT,
            enable_getter=self._presenter.get_braille_is_enabled,
            enable_setter=self._presenter.set_braille_is_enabled,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.BRAILLE
        )

        self.attach(enable_listbox, 0, row, 1, 1)
        row += 1
        self.attach(stack, 0, row, 1, 1)

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self.multipage_on_becoming_visible()

    def reload(self) -> None:
        """Fetch fresh values and update UI."""

        self._verbosity_grid.reload()
        self._display_settings_grid.reload()
        self._flash_messages_grid.reload()
        self._progress_bars_grid.reload()

    def save_settings(self) -> dict:
        """Persist staged values."""

        result: dict[str, Any] = {}
        result["enableBraille"] = self._presenter.get_braille_is_enabled()
        result.update(self._verbosity_grid.save_settings())
        result.update(self._display_settings_grid.save_settings())
        result.update(self._flash_messages_grid.save_settings())
        result.update(self._progress_bars_grid.save_settings())
        return result

    def refresh(self) -> None:
        """Update widgets from staged values."""

        self._initializing = True
        self._verbosity_grid.refresh()
        self._display_settings_grid.refresh()
        self._flash_messages_grid.refresh()
        self._progress_bars_grid.refresh()
        self._initializing = False

    def has_changes(self) -> bool:
        """Return True if any child grid has unsaved changes."""

        return (
            self._verbosity_grid.has_changes()
            or self._display_settings_grid.has_changes()
            or self._flash_messages_grid.has_changes()
            or self._progress_bars_grid.has_changes()
            or self._has_unsaved_changes
        )


class BraillePresenter:
    """Provides braille presentation support."""

    def __init__(self) -> None:
        msg = "BRAILLE PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("BraillePresenter", self)

    def create_preferences_grid(
        self,
        title_change_callback: preferences_grid_base.Callable[[str], None] | None = None
    ) -> BraillePreferencesGrid:
        """Returns the GtkGrid containing the preferences UI."""

        return BraillePreferencesGrid(self, title_change_callback)

    def _get_verbosity_is_detailed(self) -> bool:
        """Returns whether braille verbosity is set to detailed/verbose."""

        level = settings.brailleVerbosityLevel
        return level == settings.VERBOSITY_LEVEL_VERBOSE

    def _set_verbosity_is_detailed(self, value: bool) -> bool:
        """Sets braille verbosity to detailed/verbose if True, brief if False."""

        level = settings.VERBOSITY_LEVEL_VERBOSE if value else settings.VERBOSITY_LEVEL_BRIEF
        msg = f"BRAILLE PRESENTER: Setting verbosity level to {level}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleVerbosityLevel = level
        return True

    def _get_disable_eol(self) -> bool:
        """Returns whether the end-of-line indicator is disabled."""

        return settings.disableBrailleEOL

    def _set_disable_eol(self, value: bool) -> bool:
        """Sets whether the end-of-line indicator is disabled."""

        msg = f"BRAILLE PRESENTER: Setting disable-eol to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.disableBrailleEOL = value
        return True

    def _get_use_abbreviated_rolenames(self) -> bool:
        """Returns whether abbreviated role names are used."""

        style = settings.brailleRolenameStyle
        return style == settings.VERBOSITY_LEVEL_BRIEF

    def _set_use_abbreviated_rolenames(self, value: bool) -> bool:
        """Sets whether abbreviated role names are used."""

        if value:
            style = settings.VERBOSITY_LEVEL_BRIEF
        else:
            style = settings.VERBOSITY_LEVEL_VERBOSE
        msg = f"BRAILLE PRESENTER: Setting rolename style to {'abbreviated' if value else 'full'}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleRolenameStyle = style
        return True

    def _get_flash_duration_seconds(self) -> int:
        """Returns flash duration in seconds (converted from milliseconds)."""

        duration_ms = self.get_flash_message_duration()
        return max(1, duration_ms // 1000)

    def _set_flash_duration_seconds(self, value: int) -> None:
        """Sets flash duration in seconds (converts to milliseconds)."""

        duration_ms = value * 1000
        self.set_flash_message_duration(duration_ms)

    def use_braille(self) -> bool:
        """Returns whether braille is to be used."""

        result = settings.enableBraille or settings.enableBrailleMonitor
        if not result:
            msg = "BRAILLE PRESENTER: Braille is disabled."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_braille_is_enabled(self) -> bool:
        """Returns whether braille is enabled."""

        return settings.enableBraille

    @dbus_service.setter
    def set_braille_is_enabled(self, value: bool) -> bool:
        """Sets whether braille is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableBraille = value

        if value:
            braille.init(input_event_manager.get_manager().process_braille_event)
        else:
            braille.shutdown()

        return True

    def use_verbose_braille(self) -> bool:
        """Returns whether the braille verbosity level is set to verbose."""

        level = settings.brailleVerbosityLevel
        return level == settings.VERBOSITY_LEVEL_VERBOSE

    @dbus_service.getter
    def get_verbosity_level(self) -> str:
        """Returns the current braille verbosity level for object presentation."""

        int_value = settings.brailleVerbosityLevel
        return VerbosityLevel(int_value).string_name

    @dbus_service.setter
    def set_verbosity_level(self, value: str) -> bool:
        """Sets the braille verbosity level for object presentation."""

        try:
            level = VerbosityLevel[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid verbosity level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting verbosity level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleVerbosityLevel = level.value
        return True

    def use_full_rolenames(self) -> bool:
        """Returns whether full rolenames should be used."""

        level = settings.brailleRolenameStyle
        return level == settings.VERBOSITY_LEVEL_VERBOSE

    @dbus_service.getter
    def get_rolename_style(self) -> str:
        """Returns the current rolename style for object presentation."""

        int_value = settings.brailleRolenameStyle
        return VerbosityLevel(int_value).string_name

    @dbus_service.setter
    def set_rolename_style(self, value: str) -> bool:
        """Sets the current rolename style for object presentation."""

        try:
            level = VerbosityLevel[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid rolename style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting rolename style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleRolenameStyle = level.value
        return True

    @dbus_service.getter
    def get_present_mnemonics(self) -> bool:
        """Returns whether mnemonics are presented on the braille display."""

        return settings.displayObjectMnemonic

    @dbus_service.setter
    def set_present_mnemonics(self, value: bool) -> bool:
        """Sets whether mnemonics are presented on the braille display."""

        msg = f"BRAILLE PRESENTER: Setting present mnemonics to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.displayObjectMnemonic = value
        return True

    @dbus_service.getter
    def get_display_ancestors(self) -> bool:
        """Returns whether ancestors of the current object will be displayed."""

        return settings.enableBrailleContext

    @dbus_service.setter
    def set_display_ancestors(self, value: bool) -> bool:
        """Sets whether ancestors of the current object will be displayed."""

        msg = f"BRAILLE PRESENTER: Setting enable braille context to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableBrailleContext = value
        return True

    @dbus_service.getter
    def get_braille_progress_bar_updates(self) -> bool:
        """Returns whether braille progress bar updates are enabled."""

        return settings.brailleProgressBarUpdates

    @dbus_service.setter
    def set_braille_progress_bar_updates(self, value: bool) -> bool:
        """Sets whether braille progress bar updates are enabled."""

        msg = f"BRAILLE PRESENTER: Setting braille progress bar updates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleProgressBarUpdates = value
        return True

    @dbus_service.getter
    def get_progress_bar_braille_interval(self) -> int:
        """Returns the braille progress bar update interval in seconds."""

        return settings.progressBarBrailleInterval

    @dbus_service.setter
    def set_progress_bar_braille_interval(self, value: int) -> bool:
        """Sets the braille progress bar update interval in seconds."""

        msg = f"BRAILLE PRESENTER: Setting progress bar braille interval to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarBrailleInterval = value
        return True

    @dbus_service.getter
    def get_progress_bar_braille_verbosity(self) -> int:
        """Returns the braille progress bar verbosity level."""

        return settings.progressBarBrailleVerbosity

    @dbus_service.setter
    def set_progress_bar_braille_verbosity(self, value: int) -> bool:
        """Sets the braille progress bar verbosity level."""

        msg = f"BRAILLE PRESENTER: Setting progress bar braille verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarBrailleVerbosity = value
        return True

    @dbus_service.getter
    def get_contracted_braille_is_enabled(self) -> bool:
        """Returns whether contracted braille is enabled."""

        return settings.enableContractedBraille

    @dbus_service.setter
    def set_contracted_braille_is_enabled(self, value: bool) -> bool:
        """Sets whether contracted braille is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable contracted braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableContractedBraille = value
        return True

    @dbus_service.getter
    def get_computer_braille_at_cursor_is_enabled(self) -> bool:
        """Returns whether computer braille is used at the cursor position."""

        return settings.enableComputerBrailleAtCursor

    @dbus_service.setter
    def set_computer_braille_at_cursor_is_enabled(self, value: bool) -> bool:
        """Sets whether computer braille is used at the cursor position."""

        msg = f"BRAILLE PRESENTER: Setting enable computer braille at cursor to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableComputerBrailleAtCursor = value
        return True

    def get_contraction_table_path(self) -> str:
        """Returns the current braille contraction table file path."""

        return settings.brailleContractionTable

    @dbus_service.getter
    def get_contraction_table(self) -> str:
        """Returns the current braille contraction table name."""

        full_path = settings.brailleContractionTable
        if not full_path:
            return ""
        return os.path.splitext(os.path.basename(full_path))[0]

    @dbus_service.getter
    def get_available_contraction_tables(self) -> list[str]:
        """Returns a list of available contraction table names."""

        table_files = braille.get_table_files()
        return [os.path.splitext(filename)[0] for filename in table_files]

    def get_contraction_tables_dict(self) -> dict[str, str]:
        """Returns a dictionary mapping display names to table file paths."""

        return braille.list_tables()

    @dbus_service.setter
    def set_contraction_table(self, value: str) -> bool:
        """Sets the current braille contraction table."""

        table_files = braille.get_table_files()
        base_name = os.path.splitext(value)[0]
        filename = None
        for table_file in table_files:
            if table_file.startswith(base_name + "."):
                filename = table_file
                break

        if not filename:
            msg = f"BRAILLE PRESENTER: Invalid contraction table: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        full_path = os.path.join(tablesdir, filename)
        msg = f"BRAILLE PRESENTER: Setting contraction table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleContractionTable = full_path
        return True

    def set_contraction_table_from_path(self, file_path: str) -> bool:
        """Sets the current braille contraction table from a file path."""

        msg = f"BRAILLE PRESENTER: Setting contraction table to {file_path}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleContractionTable = file_path
        return True

    @dbus_service.getter
    def get_end_of_line_indicator_is_enabled(self) -> bool:
        """Returns whether the end-of-line indicator is enabled."""

        # The setting, unfortunately, is disableBrailleEOL.
        return not settings.disableBrailleEOL

    @dbus_service.setter
    def set_end_of_line_indicator_is_enabled(self, value: bool) -> bool:
        """Sets whether the end-of-line indicator is enabled."""

        # The setting, unfortunately, is disableBrailleEOL.
        value = not value
        msg = f"BRAILLE PRESENTER: Setting disable-eol to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.disableBrailleEOL = value
        return True

    @dbus_service.getter
    def get_word_wrap_is_enabled(self) -> bool:
        """Returns whether braille word wrap is enabled."""

        return settings.enableBrailleWordWrap

    @dbus_service.setter
    def set_word_wrap_is_enabled(self, value: bool) -> bool:
        """Sets whether braille word wrap is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable word wrap to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableBrailleWordWrap = value
        return True

    @dbus_service.getter
    def get_flash_messages_are_enabled(self) -> bool:
        """Returns whether 'flash' messages (i.e. announcements) are enabled."""

        return settings.enableFlashMessages

    @dbus_service.setter
    def set_flash_messages_are_enabled(self, value: bool) -> bool:
        """Sets whether 'flash' messages (i.e. announcements) are enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable flash messages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableFlashMessages = value
        return True

    def get_flashtime_from_settings(self) -> int:
        """Returns flash message duration in milliseconds based on user settings."""

        if self.get_flash_messages_are_persistent():
            return -1
        return self.get_flash_message_duration()

    @dbus_service.getter
    def get_flash_message_duration(self) -> int:
        """Returns flash message duration in milliseconds."""

        return settings.brailleFlashTime

    @dbus_service.setter
    def set_flash_message_duration(self, value: int) -> bool:
        """Sets flash message duration in milliseconds."""

        msg = f"BRAILLE PRESENTER: Setting braille flash time to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleFlashTime = value
        return True

    def set_selector_indicator_from_int(self, value: int) -> bool:
        """Sets the braille selector indicator from an int value."""

        msg = f"BRAILLE PRESENTER: Setting selector indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleSelectorIndicator = value
        return True

    def set_link_indicator_from_int(self, value: int) -> bool:
        """Sets the braille link indicator from an int value."""

        msg = f"BRAILLE PRESENTER: Setting link indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleLinkIndicator = value
        return True

    def set_text_attributes_indicator_from_int(self, value: int) -> bool:
        """Sets the braille text attributes indicator from an int value."""

        msg = f"BRAILLE PRESENTER: Setting text attributes indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.textAttributesBrailleIndicator = value
        return True

    @dbus_service.getter
    def get_flash_messages_are_persistent(self) -> bool:
        """Returns whether 'flash' messages are persistent (as opposed to temporary)."""

        return settings.flashIsPersistent

    @dbus_service.setter
    def set_flash_messages_are_persistent(self, value: bool) -> bool:
        """Sets whether 'flash' messages are persistent (as opposed to temporary)."""

        msg = f"BRAILLE PRESENTER: Setting flash messages are persistent to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.flashIsPersistent = value
        return True

    @dbus_service.getter
    def get_flash_messages_are_detailed(self) -> bool:
        """Returns whether 'flash' messages are detailed (as opposed to brief)."""

        return settings.flashIsDetailed

    @dbus_service.setter
    def set_flash_messages_are_detailed(self, value: bool) -> bool:
        """Sets whether 'flash' messages are detailed (as opposed to brief)."""

        msg = f"BRAILLE PRESENTER: Setting flash messages are detailed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.flashIsDetailed = value
        return True

    def _get_selector_indicator_as_int(self) -> int:
        """Returns the braille selector indicator as an int."""

        value = settings.brailleSelectorIndicator
        msg = f"BRAILLE PRESENTER: Getting selector indicator: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return value

    @dbus_service.getter
    def get_selector_indicator(self) -> str:
        """Returns the braille selector indicator style."""

        int_value = settings.brailleSelectorIndicator
        return BrailleIndicator(int_value).string_name

    @dbus_service.setter
    def set_selector_indicator(self, value: str) -> bool:
        """Sets the braille selector indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid selector indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting selector indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleSelectorIndicator = indicator.value
        return True

    def _get_link_indicator_as_int(self) -> int:
        """Returns the braille link indicator as an int."""

        value = settings.brailleLinkIndicator
        msg = f"BRAILLE PRESENTER: Getting link indicator: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return value

    @dbus_service.getter
    def get_link_indicator(self) -> str:
        """Returns the braille link indicator style."""

        int_value = settings.brailleLinkIndicator
        return BrailleIndicator(int_value).string_name

    @dbus_service.setter
    def set_link_indicator(self, value: str) -> bool:
        """Sets the braille link indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid link indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting link indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleLinkIndicator = indicator.value
        return True

    def _get_text_attributes_indicator_as_int(self) -> int:
        """Returns the braille text attributes indicator as an int."""

        value = settings.textAttributesBrailleIndicator
        msg = f"BRAILLE PRESENTER: Getting text attributes indicator: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return value

    @dbus_service.getter
    def get_text_attributes_indicator(self) -> str:
        """Returns the braille text attributes indicator style."""

        int_value = settings.textAttributesBrailleIndicator
        return BrailleIndicator(int_value).string_name

    @dbus_service.setter
    def set_text_attributes_indicator(self, value: str) -> bool:
        """Sets the braille text attributes indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid text attributes indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting text attributes indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.textAttributesBrailleIndicator = indicator.value
        return True


_presenter: BraillePresenter = BraillePresenter()

def get_presenter() -> BraillePresenter:
    """Returns the Braille Presenter"""

    return _presenter
