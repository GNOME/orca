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

    _documentation_summary = (
        "Use these settings to choose how much context and object information appears in braille."
    )

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for braille verbosity preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.VERBOSITY,
            panel_id="braille_presenter.verbosity",
            description=(
                "Braille verbosity controls how much contextual and object information "
                "Orca shows on the braille display."
            ),
            schema="braille",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.OBJECT_PRESENTATION_IS_DETAILED,
                    kind="switch",
                    summary="Controls whether Orca shows more detailed object information.",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_SHOW_CONTEXT,
                    kind="switch",
                    summary=(
                        "Controls whether Orca shows contextual information about the "
                        "current object, such as the panel it is inside."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_DISPLAY_ANCESTORS,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_ABBREVIATED_ROLE_NAMES,
                    kind="switch",
                    summary=(
                        "Controls whether Orca uses abbreviated role names, such as btn for button."
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.PRESENT_OBJECT_MNEMONICS,
                    kind="switch",
                    summary="Controls whether Orca shows object mnemonics in braille.",
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_PRESENT_MNEMONICS,
                ),
            ),
        )

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

    _documentation_summary = (
        "Use these settings to control braille wrapping, contracted braille, and indicator dots."
    )

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for braille display settings."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.BRAILLE_DISPLAY_SETTINGS,
            panel_id="braille_presenter.display-settings",
            description=(
                "Display settings control how text is arranged on the braille display, "
                "which braille rules are used, and which dots mark links, selections, "
                "and text attributes."
            ),
            schema="braille",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_ENABLE_END_OF_LINE_SYMBOL,
                    kind="switch",
                    summary=(
                        "Controls whether Orca shows the end-of-line indicator at the "
                        "end of each line of text."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_END_OF_LINE_INDICATOR,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_ENABLE_WORD_WRAP,
                    kind="switch",
                    summary=(
                        "Controls whether Orca adjusts displayed text so only full words are "
                        "shown. When word wrap is off, Orca uses all available cells so more "
                        "text can be shown at once."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_WORD_WRAP,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_ENABLE_CONTRACTED_BRAILLE,
                    kind="switch",
                    summary=(
                        "Controls whether Orca uses contracted braille, such as shorter "
                        "forms of common letter combinations and words."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_CONTRACTED_BRAILLE,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_COMPUTER_BRAILLE_AT_CURSOR,
                    kind="switch",
                    summary=(
                        "When contracted braille is enabled, controls whether the word at "
                        "the cursor is shown in uncontracted computer braille."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_COMPUTER_BRAILLE_AT_CURSOR,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_CONTRACTION_TABLE,
                    kind="combo",
                    summary=("Selects the table Orca uses for braille symbols and contractions."),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_CONTRACTION_TABLE,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_INDICATORS,
                    kind="group",
                    summary=(
                        "Controls which braille dots Orca uses to mark links, selections, "
                        "and text attributes. These indicators are shown like underlining "
                        "on the braille display."
                    ),
                    controls=(
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.BRAILLE_HYPERLINK_INDICATOR,
                            kind="combo",
                            summary=(
                                "Selects the dot or dots Orca uses to mark text that is "
                                "part of a link."
                            ),
                            schema="braille",
                            key=braille_presenter.BraillePresenter.KEY_LINK_INDICATOR,
                            value_docs=(
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_NONE,
                                    value="none",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_7,
                                    value="dot7",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_8,
                                    value="dot8",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_7_8,
                                    value="dots78",
                                ),
                            ),
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.BRAILLE_SELECTION_INDICATOR,
                            kind="combo",
                            summary=("Selects the dot or dots Orca uses to mark selected text."),
                            schema="braille",
                            key=braille_presenter.BraillePresenter.KEY_SELECTOR_INDICATOR,
                            value_docs=(
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_NONE,
                                    value="none",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_7,
                                    value="dot7",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_8,
                                    value="dot8",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_7_8,
                                    value="dots78",
                                ),
                            ),
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.BRAILLE_TEXT_ATTRIBUTES_INDICATOR,
                            kind="combo",
                            summary=(
                                "Selects the dot or dots Orca uses to mark text attributes, "
                                "such as bold."
                            ),
                            schema="braille",
                            key=braille_presenter.BraillePresenter.KEY_TEXT_ATTRIBUTES_INDICATOR,
                            value_docs=(
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_NONE,
                                    value="none",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_7,
                                    value="dot7",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_8,
                                    value="dot8",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.BRAILLE_DOT_7_8,
                                    value="dots78",
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

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

    _documentation_summary = "Use these settings to control temporary braille announcements."

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for braille flash message preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.BRAILLE_FLASH_MESSAGES,
            panel_id="braille_presenter.flash-messages",
            description=(
                "Braille flash messages are announcements, such as Orca messages or "
                "command feedback, shown on the braille display. Temporary flash "
                "messages are shown briefly, after which the original display contents "
                "are restored."
            ),
            schema="braille",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_ENABLE_FLASH_MESSAGES,
                    kind="switch",
                    summary="Controls whether Orca shows messages and command feedback in braille.",
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_FLASH_MESSAGES,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_MESSAGES_ARE_DETAILED,
                    kind="switch",
                    summary=(
                        "Controls whether Orca shows detailed braille messages when a "
                        "brief alternative is available. For instance, detailed command "
                        "feedback might include both the setting name and its new value."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_FLASH_MESSAGES_DETAILED,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_MESSAGES_ARE_PERSISTENT,
                    kind="switch",
                    summary=(
                        "Controls whether flash messages remain displayed until the display "
                        "is updated instead of disappearing after the configured duration."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_FLASH_MESSAGES_PERSISTENT,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_DURATION_SECS,
                    kind="spin",
                    summary=(
                        "Sets how long temporary braille messages are displayed when "
                        "they are not persistent. This setting is ignored when messages "
                        "are persistent."
                    ),
                    minimum="1",
                    maximum="100",
                ),
            ),
        )

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

    _documentation_summary = (
        "Use these settings to decide whether progress-bar changes are shown in braille and "
        "how often they are updated."
    )

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for braille progress-bar preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.PROGRESS_BARS,
            panel_id="braille_presenter.progress-bars",
            description=(
                "Progress bar settings control whether Orca shows progress-bar changes "
                "in braille, how often updates are shown, and which progress bars apply."
            ),
            schema="braille",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.GENERAL_BRAILLE_UPDATES,
                    kind="switch",
                    summary="Controls whether Orca periodically shows progress-bar updates.",
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_BRAILLE_PROGRESS_BAR_UPDATES,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.GENERAL_FREQUENCY_SECS,
                    kind="spin",
                    summary="Sets how often Orca shows progress-bar updates.",
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_PROGRESS_BAR_BRAILLE_INTERVAL,
                    minimum="0",
                    maximum="100",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.GENERAL_APPLIES_TO,
                    kind="combo",
                    summary="Selects which progress bars produce braille updates.",
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_PROGRESS_BAR_BRAILLE_VERBOSITY,
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

    _documentation_summary = "Use these settings to control the visual braille monitor window."

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for braille on-screen display preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.ON_SCREEN_DISPLAY,
            panel_id="braille_presenter.on-screen-display",
            description=guilabels.BRAILLE_MONITOR_INFO,
            schema="braille",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_MONITOR_CELL_COUNT,
                    kind="spin",
                    summary=(
                        "Sets the number of braille cells shown in the on-screen braille display."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_MONITOR_CELL_COUNT,
                    minimum="1",
                    maximum="80",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_MONITOR_SHOW_DOTS,
                    kind="switch",
                    summary=(
                        "Controls whether the on-screen braille display shows Unicode "
                        "braille dot patterns instead of text characters."
                    ),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_MONITOR_SHOW_DOTS,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_MONITOR_FOREGROUND,
                    kind="color",
                    summary="Selects the text color for the on-screen braille display.",
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_MONITOR_FOREGROUND,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_MONITOR_BACKGROUND,
                    kind="color",
                    summary=("Selects the background color for the on-screen braille display."),
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_MONITOR_BACKGROUND,
                ),
            ),
        )

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

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for the braille preferences landing page."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.BRAILLE,
            panel_id="manual.braille",
            description=(
                "Braille settings control what Orca presents in braille. The list "
                "contains braille-related settings and pages.\n\n"
                "Activate a row, or press Right Arrow, to open its settings. Press "
                "Left Arrow, Escape, or Alt+Left to return to the list."
            ),
            show_available_settings=False,
            schema="braille",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_ENABLE_BRAILLE_SUPPORT,
                    kind="switch",
                    summary="Turns braille output on or off.",
                    schema="braille",
                    key=braille_presenter.BraillePresenter.KEY_ENABLED,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.VERBOSITY,
                    kind="page",
                    summary="Opens settings for how much information Orca shows in braille.",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_DISPLAY_SETTINGS,
                    kind="page",
                    summary="Opens settings for braille wrapping, contraction, and indicators.",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.BRAILLE_FLASH_MESSAGES,
                    kind="page",
                    summary="Opens settings for temporary braille messages.",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.PROGRESS_BARS,
                    kind="page",
                    summary="Opens settings for when Orca shows progress-bar updates in braille.",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.ON_SCREEN_DISPLAY,
                    kind="page",
                    summary="Opens settings for the on-screen braille display.",
                ),
            ),
        )

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
