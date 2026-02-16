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
# pylint: disable=wrong-import-position
# pylint: disable=too-many-lines

"""Provides braille presentation support."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import os
from enum import Enum
from typing import Any, TYPE_CHECKING

from . import braille
from . import braille_monitor
from . import brltablenames
from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import guilabels
from . import input_event
from . import input_event_manager
from . import messages
from . import preferences_grid_base
from . import settings
from . import gsettings_registry
from .orca_platform import tablesdir  # pylint: disable=import-error

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.VerbosityLevel",
    values={"brief": 0, "verbose": 1},
)
class VerbosityLevel(Enum):
    """Verbosity level enumeration with int values from settings."""

    BRIEF = settings.VERBOSITY_LEVEL_BRIEF
    VERBOSE = settings.VERBOSITY_LEVEL_VERBOSE

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.BrailleIndicator",
    values={"none": 0, "dot7": 64, "dot8": 128, "dots78": 192},
)
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
                prefs_key="brailleVerbosityLevel",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_SHOW_CONTEXT,
                getter=presenter.get_display_ancestors,
                setter=presenter.set_display_ancestors,
                prefs_key="enableBrailleContext",
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
                prefs_key="displayObjectMnemonic",
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
            prefs_key="enableContractedBraille",
        )

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.EnumPreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_END_OF_LINE_SYMBOL,
                getter=presenter.get_end_of_line_indicator_is_enabled,
                setter=presenter.set_end_of_line_indicator_is_enabled,
                prefs_key="enableBrailleEOL",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_WORD_WRAP,
                getter=presenter.get_word_wrap_is_enabled,
                setter=presenter.set_word_wrap_is_enabled,
                prefs_key="enableBrailleWordWrap",
            ),
            self._enable_contracted_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_COMPUTER_BRAILLE_AT_CURSOR,
                getter=presenter.get_computer_braille_at_cursor_is_enabled,
                setter=presenter.set_computer_braille_at_cursor_is_enabled,
                prefs_key="enableComputerBrailleAtCursor",
                determine_sensitivity=self._contracted_enabled,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.BRAILLE_CONTRACTION_TABLE,
                options=table_names,
                values=table_paths,
                getter=presenter.get_contraction_table_path,
                setter=presenter.set_contraction_table_from_path,
                prefs_key="brailleContractionTable",
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
                    settings.BRAILLE_UNDERLINE_NONE,
                    settings.BRAILLE_UNDERLINE_7,
                    settings.BRAILLE_UNDERLINE_8,
                    settings.BRAILLE_UNDERLINE_BOTH,
                ],
                getter=presenter._get_link_indicator_as_int,
                setter=presenter.set_link_indicator_from_int,
                prefs_key="brailleLinkIndicator",
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
                    settings.BRAILLE_UNDERLINE_NONE,
                    settings.BRAILLE_UNDERLINE_7,
                    settings.BRAILLE_UNDERLINE_8,
                    settings.BRAILLE_UNDERLINE_BOTH,
                ],
                getter=presenter._get_selector_indicator_as_int,
                setter=presenter.set_selector_indicator_from_int,
                prefs_key="brailleSelectorIndicator",
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
                    settings.BRAILLE_UNDERLINE_NONE,
                    settings.BRAILLE_UNDERLINE_7,
                    settings.BRAILLE_UNDERLINE_8,
                    settings.BRAILLE_UNDERLINE_BOTH,
                ],
                getter=presenter._get_text_attributes_indicator_as_int,
                setter=presenter.set_text_attributes_indicator_from_int,
                prefs_key="textAttributesBrailleIndicator",
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
            prefs_key="flashIsPersistent",
        )

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.IntRangePreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_ENABLE_FLASH_MESSAGES,
                getter=presenter.get_flash_messages_are_enabled,
                setter=presenter.set_flash_messages_are_enabled,
                prefs_key="enableFlashMessages",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_MESSAGES_ARE_DETAILED,
                getter=presenter.get_flash_messages_are_detailed,
                setter=presenter.set_flash_messages_are_detailed,
                prefs_key="flashIsDetailed",
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
                prefs_key="brailleProgressBarUpdates",
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_braille_interval,
                setter=presenter.set_progress_bar_braille_interval,
                prefs_key="progressBarBrailleInterval",
                minimum=0,
                maximum=100,
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
                prefs_key="brailleMonitorCellCount",
                minimum=1,
                maximum=80,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.BRAILLE_MONITOR_SHOW_DOTS,
                getter=presenter.get_monitor_show_dots,
                setter=presenter.set_monitor_show_dots,
                prefs_key="brailleMonitorShowDots",
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.BRAILLE_MONITOR_FOREGROUND,
                getter=presenter.get_monitor_foreground,
                setter=presenter.set_monitor_foreground,
                prefs_key="brailleMonitorForeground",
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.BRAILLE_MONITOR_BACKGROUND,
                getter=presenter.get_monitor_background,
                setter=presenter.set_monitor_background,
                prefs_key="brailleMonitorBackground",
            ),
        ]

        super().__init__(
            guilabels.ON_SCREEN_DISPLAY, controls, info_message=guilabels.BRAILLE_MONITOR_INFO
        )


# pylint: disable-next=too-many-instance-attributes
class BraillePreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Braille preferences page with nested stack navigation."""

    def __init__(
        self,
        presenter: BraillePresenter,
        title_change_callback: preferences_grid_base.Callable[[str], None] | None = None,
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
        self.refresh()

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

        self._verbosity_grid.reload()
        self._display_settings_grid.reload()
        self._flash_messages_grid.reload()
        self._progress_bars_grid.reload()
        self._osd_grid.reload()

    def save_settings(self) -> dict:
        """Persist staged values."""

        result: dict[str, Any] = {}
        result["enableBraille"] = self._presenter.get_braille_is_enabled()
        result.update(self._verbosity_grid.save_settings())
        result.update(self._display_settings_grid.save_settings())
        result.update(self._flash_messages_grid.save_settings())
        result.update(self._progress_bars_grid.save_settings())
        result.update(self._osd_grid.save_settings())
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


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Braille", name="braille")
class BraillePresenter:
    """Provides braille presentation support."""

    def __init__(self) -> None:
        msg = "BRAILLE PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("BraillePresenter", self)
        self._command_names: dict[int, str] | None = None
        self._table_names: dict[str, str] | None = None
        self._monitor: braille_monitor.BrailleMonitor | None = None
        self._monitor_enabled_override: bool | None = None
        self._initialized = False

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        manager.add_command(
            command_manager.KeyboardCommand(
                "toggle_braille_monitor",
                self.toggle_monitor,
                guilabels.BRAILLE,
                cmdnames.TOGGLE_BRAILLE_MONITOR,
            )
        )

        msg = "BRAILLE PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @dbus_service.command
    def toggle_monitor(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles the braille monitor on and off."""

        tokens = [
            "BRAILLE PRESENTER: toggle_monitor. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        from . import presentation_manager  # pylint: disable=import-outside-toplevel

        if self.get_monitor_is_enabled():
            self.set_monitor_is_enabled(False)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(
                    messages.BRAILLE_MONITOR_DISABLED
                )
        else:
            self.set_monitor_is_enabled(True)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.BRAILLE_MONITOR_ENABLED)
        return True

    @staticmethod
    def _build_table_names() -> dict[str, str]:
        """Returns display names for braille translation tables."""

        return {
            "Cz-Cz-g1": brltablenames.CZ_CZ_G1,
            "Es-Es-g1": brltablenames.ES_ES_G1,
            "Fr-Ca-g2": brltablenames.FR_CA_G2,
            "Fr-Fr-g2": brltablenames.FR_FR_G2,
            "Lv-Lv-g1": brltablenames.LV_LV_G1,
            "Nl-Nl-g1": brltablenames.NL_NL_G1,
            "No-No-g0": brltablenames.NO_NO_G0,
            "No-No-g1": brltablenames.NO_NO_G1,
            "No-No-g2": brltablenames.NO_NO_G2,
            "No-No-g3": brltablenames.NO_NO_G3,
            "Pl-Pl-g1": brltablenames.PL_PL_G1,
            "Pt-Pt-g1": brltablenames.PT_PT_G1,
            "Se-Se-g1": brltablenames.SE_SE_G1,
            "ar-ar-g1": brltablenames.AR_AR_G1,
            "cy-cy-g1": brltablenames.CY_CY_G1,
            "cy-cy-g2": brltablenames.CY_CY_G2,
            "de-de-g0": brltablenames.DE_DE_G0,
            "de-de-g1": brltablenames.DE_DE_G1,
            "de-de-g2": brltablenames.DE_DE_G2,
            "en-GB-g2": brltablenames.EN_GB_G2,
            "en-gb-g1": brltablenames.EN_GB_G1,
            "en-us-g1": brltablenames.EN_US_G1,
            "en-us-g2": brltablenames.EN_US_G2,
            "fr-ca-g1": brltablenames.FR_CA_G1,
            "fr-fr-g1": brltablenames.FR_FR_G1,
            "gr-gr-g1": brltablenames.GR_GR_G1,
            "hi-in-g1": brltablenames.HI_IN_G1,
            "hu-hu-comp8": brltablenames.HU_HU_8DOT,
            "hu-hu-g1": brltablenames.HU_HU_G1,
            "hu-hu-g2": brltablenames.HU_HU_G2,
            "it-it-g1": brltablenames.IT_IT_G1,
            "nl-be-g1": brltablenames.NL_BE_G1,
        }

    def get_table_names(self) -> dict[str, str]:
        """Returns table aliases mapped to localized display names."""

        if self._table_names is None:
            self._table_names = self._build_table_names()
        return dict(self._table_names)

    @staticmethod
    def _build_command_names() -> dict[int, str]:
        """Return BrlTTY command names for presentation in the UI."""

        command_names: dict[int, str] = {}

        def add_command(command_id: int | None, label: str) -> None:
            if command_id is not None:
                command_names[command_id] = label

        add_command(braille.BRLAPI_KEY_CMD_HWINLT, cmdnames.BRAILLE_LINE_LEFT)
        add_command(braille.BRLAPI_KEY_CMD_FWINLT, cmdnames.BRAILLE_LINE_LEFT)
        add_command(braille.BRLAPI_KEY_CMD_FWINLTSKIP, cmdnames.BRAILLE_LINE_LEFT)
        add_command(braille.BRLAPI_KEY_CMD_HWINRT, cmdnames.BRAILLE_LINE_RIGHT)
        add_command(braille.BRLAPI_KEY_CMD_FWINRT, cmdnames.BRAILLE_LINE_RIGHT)
        add_command(braille.BRLAPI_KEY_CMD_FWINRTSKIP, cmdnames.BRAILLE_LINE_RIGHT)
        add_command(braille.BRLAPI_KEY_CMD_LNUP, cmdnames.BRAILLE_LINE_UP)
        add_command(braille.BRLAPI_KEY_CMD_LNDN, cmdnames.BRAILLE_LINE_DOWN)
        add_command(braille.BRLAPI_KEY_CMD_FREEZE, cmdnames.BRAILLE_FREEZE)
        add_command(braille.BRLAPI_KEY_CMD_TOP_LEFT, cmdnames.BRAILLE_TOP_LEFT)
        add_command(braille.BRLAPI_KEY_CMD_BOT_LEFT, cmdnames.BRAILLE_BOTTOM_LEFT)
        add_command(braille.BRLAPI_KEY_CMD_HOME, cmdnames.BRAILLE_HOME)
        add_command(braille.BRLAPI_KEY_CMD_SIXDOTS, cmdnames.BRAILLE_SIX_DOTS)
        add_command(braille.BRLAPI_KEY_CMD_ROUTE, cmdnames.BRAILLE_ROUTE_CURSOR)
        add_command(braille.BRLAPI_KEY_CMD_CUTBEGIN, cmdnames.BRAILLE_CUT_BEGIN)
        add_command(braille.BRLAPI_KEY_CMD_CUTLINE, cmdnames.BRAILLE_CUT_LINE)

        return command_names

    def get_command_names(self) -> dict[int, str]:
        """Returns a mapping of BrlTTY command IDs to user-visible labels."""

        if self._command_names is None:
            self._command_names = self._build_command_names()
        return dict(self._command_names)

    def create_preferences_grid(
        self, title_change_callback: preferences_grid_base.Callable[[str], None] | None = None
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

        result = settings.enableBraille or self.get_monitor_is_enabled()
        if not result:
            msg = "BRAILLE PRESENTER: Braille is disabled."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_monitor_is_enabled(self) -> bool:
        """Returns whether the braille monitor is enabled."""

        return self._monitor_enabled_override or False

    @dbus_service.setter
    def set_monitor_is_enabled(self, value: bool) -> bool:
        """Sets whether the braille monitor is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable braille monitor to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._monitor_enabled_override = value
        if not value:
            self.destroy_monitor()
        return True

    @gsettings_registry.get_registry().gsetting(
        key="monitor-cell-count",
        schema="braille",
        gtype="i",
        default=32,
        summary="Braille monitor cell count",
        settings_key="brailleMonitorCellCount",
    )
    @dbus_service.getter
    def get_monitor_cell_count(self) -> int:
        """Returns the configured braille monitor cell count."""

        return settings.brailleMonitorCellCount

    @dbus_service.setter
    def set_monitor_cell_count(self, value: int) -> bool:
        """Sets the braille monitor cell count."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor cell count to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleMonitorCellCount = value
        self.destroy_monitor()
        return True

    @gsettings_registry.get_registry().gsetting(
        key="monitor-show-dots",
        schema="braille",
        gtype="b",
        default=False,
        summary="Show Unicode braille dots in braille monitor",
        settings_key="brailleMonitorShowDots",
    )
    @dbus_service.getter
    def get_monitor_show_dots(self) -> bool:
        """Returns whether the braille monitor shows Unicode braille dots."""

        return settings.brailleMonitorShowDots

    @dbus_service.setter
    def set_monitor_show_dots(self, value: bool) -> bool:
        """Sets whether the braille monitor shows Unicode braille dots."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor show dots to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleMonitorShowDots = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="monitor-foreground",
        schema="braille",
        gtype="s",
        default="#000000",
        summary="Braille monitor foreground color",
        settings_key="brailleMonitorForeground",
    )
    @dbus_service.getter
    def get_monitor_foreground(self) -> str:
        """Returns the braille monitor foreground color."""

        return settings.brailleMonitorForeground

    @dbus_service.setter
    def set_monitor_foreground(self, value: str) -> bool:
        """Sets the braille monitor foreground color."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor foreground to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleMonitorForeground = value
        if self._monitor is not None:
            self._monitor.reapply_css()
        return True

    @gsettings_registry.get_registry().gsetting(
        key="monitor-background",
        schema="braille",
        gtype="s",
        default="#ffffff",
        summary="Braille monitor background color",
        settings_key="brailleMonitorBackground",
    )
    @dbus_service.getter
    def get_monitor_background(self) -> str:
        """Returns the braille monitor background color."""

        return settings.brailleMonitorBackground

    @dbus_service.setter
    def set_monitor_background(self, value: str) -> bool:
        """Sets the braille monitor background color."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor background to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleMonitorBackground = value
        if self._monitor is not None:
            self._monitor.reapply_css()
        return True

    # pylint: disable-next=too-many-arguments
    def present_regions(
        self,
        regions: list[braille.Region],
        focused_region: braille.Region | None,
        extra_region: braille.Region | None = None,
        *,
        pan_to_cursor: bool = True,
        indicate_links: bool = True,
        stop_flash: bool = True,
    ) -> None:
        """Build a line from regions and present it as a single braille line."""

        if extra_region is not None:
            regions = list(regions)
            regions.append(extra_region)
            focused_region = extra_region

        line = braille.Line()
        line.add_regions(regions)
        braille.display_line(
            line,
            focused_region,
            pan_to_cursor=pan_to_cursor,
            indicate_links=indicate_links,
            stop_flash=stop_flash,
        )

    def present_generated_braille(
        self, script: default.Script, obj: Atspi.Accessible, **args: Any
    ) -> None:
        """Generates braille for obj using the script's braille generator and displays it."""

        if not self.use_braille():
            return

        result, focused_region = script.braille_generator.generate_braille(obj, **args)
        if result:
            self.present_regions(
                list(result),
                focused_region,
                extra_region=args.get("extraRegion"),
            )

    @gsettings_registry.get_registry().gsetting(
        key="enabled",
        schema="braille",
        gtype="b",
        default=True,
        summary="Enable braille output",
        settings_key="enableBraille",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="verbosity-level",
        schema="braille",
        genum="org.gnome.Orca.VerbosityLevel",
        default="verbose",
        summary="Braille verbosity level (brief, verbose)",
        settings_key="brailleVerbosityLevel",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="rolename-style",
        schema="braille",
        genum="org.gnome.Orca.VerbosityLevel",
        default="verbose",
        summary="Braille rolename style (brief, verbose)",
        settings_key="brailleRolenameStyle",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="present-mnemonics",
        schema="braille",
        gtype="b",
        default=True,
        summary="Present mnemonics on braille display",
        settings_key="displayObjectMnemonic",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="display-ancestors",
        schema="braille",
        gtype="b",
        default=True,
        summary="Display ancestors of current object",
        settings_key="enableBrailleContext",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="braille-progress-bar-updates",
        schema="braille",
        gtype="b",
        default=False,
        summary="Show progress bar updates in braille",
        settings_key="brailleProgressBarUpdates",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="progress-bar-braille-interval",
        schema="braille",
        gtype="i",
        default=10,
        summary="Progress bar braille update interval in seconds",
        settings_key="progressBarBrailleInterval",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="progress-bar-braille-verbosity",
        schema="braille",
        genum="org.gnome.Orca.ProgressBarVerbosity",
        default="application",
        summary="Progress bar braille verbosity (all, application, window)",
        settings_key="progressBarBrailleVerbosity",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="contracted-braille",
        schema="braille",
        gtype="b",
        default=False,
        summary="Enable contracted braille",
        settings_key="enableContractedBraille",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="computer-braille-at-cursor",
        schema="braille",
        gtype="b",
        default=True,
        summary="Use computer braille at cursor position",
        settings_key="enableComputerBrailleAtCursor",
    )
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

        return settings.brailleContractionTable or braille.get_default_contraction_table()

    @gsettings_registry.get_registry().gsetting(
        key="contraction-table",
        schema="braille",
        gtype="s",
        default="",
        summary="Braille contraction table name",
        settings_key="brailleContractionTable",
    )
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

        table_files = self._get_table_files()
        return [os.path.splitext(filename)[0] for filename in table_files]

    def get_contraction_tables_dict(self) -> dict[str, str]:
        """Returns a dictionary mapping display names to table file paths."""

        names = self.get_table_names()
        tables = {}
        for fname in self._get_table_files():
            alias = fname[:-4]
            tables[names.get(alias, alias)] = os.path.join(tablesdir, fname)
        return tables

    @dbus_service.setter
    def set_contraction_table(self, value: str) -> bool:
        """Sets the current braille contraction table."""

        table_files = self._get_table_files()
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

    @staticmethod
    def _get_table_files() -> list[str]:
        """Returns a list of braille table filenames in the tables directory."""

        try:
            return [fname for fname in os.listdir(tablesdir) if fname[-4:] in (".utb", ".ctb")]
        except OSError:
            return []

    def set_contraction_table_from_path(self, file_path: str) -> bool:
        """Sets the current braille contraction table from a file path."""

        msg = f"BRAILLE PRESENTER: Setting contraction table to {file_path}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.brailleContractionTable = file_path
        return True

    @gsettings_registry.get_registry().gsetting(
        key="end-of-line-indicator",
        schema="braille",
        gtype="b",
        default=True,
        summary="Show end-of-line indicator",
        settings_key="enableBrailleEOL",
    )
    @dbus_service.getter
    def get_end_of_line_indicator_is_enabled(self) -> bool:
        """Returns whether the end-of-line indicator is enabled."""

        return settings.enableBrailleEOL

    @dbus_service.setter
    def set_end_of_line_indicator_is_enabled(self, value: bool) -> bool:
        """Sets whether the end-of-line indicator is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable-eol to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableBrailleEOL = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="word-wrap",
        schema="braille",
        gtype="b",
        default=False,
        summary="Enable braille word wrap",
        settings_key="enableBrailleWordWrap",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="flash-messages",
        schema="braille",
        gtype="b",
        default=True,
        summary="Enable braille flash messages",
        settings_key="enableFlashMessages",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="flash-message-duration",
        schema="braille",
        gtype="i",
        default=5000,
        summary="Flash message duration in milliseconds",
        settings_key="brailleFlashTime",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="flash-messages-persistent",
        schema="braille",
        gtype="b",
        default=False,
        summary="Make flash messages persistent",
        settings_key="flashIsPersistent",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="flash-messages-detailed",
        schema="braille",
        gtype="b",
        default=True,
        summary="Use detailed flash messages",
        settings_key="flashIsDetailed",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="selector-indicator",
        schema="braille",
        genum="org.gnome.Orca.BrailleIndicator",
        default="dots78",
        summary="Braille selector indicator style (none, dot7, dot8, dots78)",
        settings_key="brailleSelectorIndicator",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="link-indicator",
        schema="braille",
        genum="org.gnome.Orca.BrailleIndicator",
        default="dots78",
        summary="Braille link indicator style (none, dot7, dot8, dots78)",
        settings_key="brailleLinkIndicator",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key="text-attributes-indicator",
        schema="braille",
        genum="org.gnome.Orca.BrailleIndicator",
        default="none",
        summary="Braille text attributes indicator style (none, dot7, dot8, dots78)",
        settings_key="textAttributesBrailleIndicator",
    )
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

    def kill_flash(self, restore_saved: bool = True) -> None:
        """Kills any flashed message currently being displayed."""

        braille.kill_flash(restore_saved)

    def present_message(self, message: str, restore_previous: bool = True) -> None:
        """Displays a single line message in braille."""

        if not self.use_braille():
            return

        flash_time = self.get_flashtime_from_settings()

        if not restore_previous and flash_time:
            braille.kill_flash(restore_saved=False)

        braille.display_message(message, flash_time=flash_time)

    def pan_left(self) -> bool:
        """Pans the braille display left, returning True if the display moved."""

        if not self.use_braille():
            return False

        moved = braille.pan_left()
        if moved:
            braille.refresh(pan_to_cursor=False, stop_flash=False)
        return moved

    def pan_right(self) -> bool:
        """Pans the braille display right, returning True if the display moved."""

        if not self.use_braille():
            return False

        moved = braille.pan_right()
        if moved:
            braille.refresh(pan_to_cursor=False, stop_flash=False)
        return moved

    def pan_to_beginning(self) -> None:
        """Pans the braille display all the way to the beginning of the line."""

        if not self.use_braille():
            return

        while braille.pan_left():
            pass
        braille.refresh(pan_to_cursor=False, stop_flash=True)

    def pan_to_end(self) -> None:
        """Pans the braille display all the way to the end of the line."""

        if not self.use_braille():
            return

        while braille.pan_right():
            pass
        braille.refresh(pan_to_cursor=False, stop_flash=True)

    def check_braille_setting(self) -> None:
        """Checks the braille setting and disables braille if necessary."""

        braille.check_braille_setting()

    def disable_braille(self) -> None:
        """Idles or shuts down braille output if enabled."""

        braille.disable_braille()

    def set_brlapi_priority(self, high: bool = False) -> None:
        """Sets the BrlAPI priority level.

        Args:
            high: If True, use high priority (for flat review). Otherwise use default.
        """

        if high:
            braille.set_brlapi_priority(braille.BRLAPI_PRIORITY_HIGH)
        else:
            braille.set_brlapi_priority()

    def update_monitor(
        self, cursor_cell: int, substring: str, mask: str | None, display_size: int
    ) -> None:
        """Updates the braille monitor display, creating it on demand if enabled."""

        if not self.get_monitor_is_enabled():
            return

        cell_count = settings.brailleMonitorCellCount or display_size
        if self._monitor is None:
            self._monitor = braille_monitor.BrailleMonitor(
                cell_count,
                on_close=lambda: self.set_monitor_is_enabled(False),
            )
            self._monitor.show_all()

        if settings.brailleMonitorShowDots:
            substring = self._to_unicode_braille(substring)

        self._monitor.write_text(cursor_cell, substring, mask)

    @staticmethod
    def _to_unicode_braille(text: str) -> str:
        """Convert text to Unicode braille dot pattern characters.

        Uses louis.charToDots() to map each character to its braille dot pattern,
        then converts to Unicode braille characters (U+2800 block).
        """

        try:
            import louis  # pylint: disable=import-outside-toplevel

            table = settings.brailleContractionTable if settings.enableContractedBraille else ""
            if not table:
                table = "en-us-comp8.ctb"
            dots_str = louis.charToDots([table], text)
            return "".join(chr(0x2800 | (ord(c) & 0xFF)) for c in dots_str)
        except Exception:  # pylint: disable=broad-except
            return text

    def destroy_monitor(self) -> None:
        """Destroys the braille monitor widget if it exists."""

        if self._monitor is not None:
            self._monitor.destroy()
            self._monitor = None

    def init_braille(self) -> None:
        """Initializes braille if enabled."""

        braille.set_monitor_callback(self.update_monitor)
        if not self.get_braille_is_enabled():
            return

        braille.init(input_event_manager.get_manager().process_braille_event)

    def shutdown_braille(self) -> None:
        """Shuts down braille."""

        braille.shutdown()


_presenter: BraillePresenter = BraillePresenter()


def get_presenter() -> BraillePresenter:
    """Returns the Braille Presenter"""

    return _presenter
