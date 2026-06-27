# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Preferences grid for Say All support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, preferences_grid_base, say_all_presenter, text_attribute_manager

if TYPE_CHECKING:
    from .say_all_presenter import SayAllPresenter


class SayAllPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Say All preferences page."""

    _gsettings_schema = "say-all"
    _documentation_summary = "Use these settings to control Orca's continuous reading command."

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for Say All preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.GENERAL_SAY_ALL,
            panel_id="say_all_presenter.say-all",
            description="Say All settings control Orca's continuous reading command.",
            schema="say-all",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SAY_ALL_BY,
                    kind="choice",
                    summary=(
                        "Say All reads from the current location to the end of the document; "
                        "this controls whether it pauses after each sentence or after each line."
                    ),
                    schema="say-all",
                    key=say_all_presenter.SayAllPresenter.KEY_STYLE,
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.SAY_ALL_STYLE_SENTENCE,
                            value=say_all_presenter.SayAllStyle.SENTENCE.string_name,
                            summary="Pauses after each sentence.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.SAY_ALL_STYLE_LINE,
                            value=say_all_presenter.SayAllStyle.LINE.string_name,
                            summary="Pauses after each line.",
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SPEECH_ONLY_SPEAK_DISPLAYED_TEXT,
                    kind="switch",
                    summary=("Controls whether Say All skips text that is not visually displayed."),
                    schema="say-all",
                    key=say_all_presenter.SayAllPresenter.KEY_ONLY_SPEAK_DISPLAYED_TEXT,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SAY_ALL_REWIND_AND_FAST_FORWARD_BY,
                    kind="group",
                    summary=(
                        "Controls which commands can move within the document while Say All "
                        "is active."
                    ),
                    controls=(
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.SAY_ALL_UP_AND_DOWN_ARROW,
                            kind="switch",
                            summary=(
                                "Allows Up Arrow and Down Arrow to move within the document "
                                "during Say All so you can re-hear recent content or skip "
                                "ahead without restarting Say All."
                            ),
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_REWIND_AND_FAST_FORWARD,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.SAY_ALL_STRUCTURAL_NAVIGATION,
                            kind="switch",
                            summary=(
                                "Allows structural navigation commands, such as heading and "
                                "paragraph navigation, to move backward and forward during "
                                "Say All."
                            ),
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_STRUCTURAL_NAVIGATION,
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.CHANGE_ANNOUNCEMENTS,
                    kind="group",
                    summary=(
                        "Controls which document revision and text formatting changes Orca "
                        "announces during Say All."
                    ),
                    controls=(
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_TRACKED_CHANGES,
                            kind="switch",
                            summary=(
                                "Controls whether Orca announces tracked changes during Say All."
                            ),
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_TRACKED_CHANGES,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.TEXT_ATTRIBUTE_CHANGES,
                            kind="choice",
                            summary=(
                                "Controls when Orca announces text formatting changes during "
                                "Say All."
                            ),
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_TEXT_ATTRIBUTE_CHANGE_MODE,
                            value_docs=(
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.TEXT_ATTRIBUTE_CHANGES_OFF,
                                    value="off",
                                    summary="Does not announce formatting changes.",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.TEXT_ATTRIBUTE_CHANGES_EDITABLE,
                                    value="editable-only",
                                    summary="Announces formatting changes only in editable text.",
                                ),
                                preferences_grid_base.PreferenceValueDoc(
                                    label=guilabels.TEXT_ATTRIBUTE_CHANGES_ALWAYS,
                                    value="always",
                                    summary="Always announces formatting changes.",
                                ),
                            ),
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.ANNOUNCEMENTS,
                    kind="group",
                    summary=(
                        "Controls which document and web-container boundaries Orca announces "
                        "during Say All."
                    ),
                    controls=(
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_ARTICLES,
                            kind="switch",
                            summary="Controls whether Orca announces articles during Say All.",
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_ARTICLE,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_BLOCKQUOTES,
                            kind="switch",
                            summary="Controls whether Orca announces blockquotes during Say All.",
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_BLOCKQUOTE,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_CODE_BLOCKS,
                            kind="switch",
                            summary="Controls whether Orca announces code blocks during Say All.",
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_CODE_BLOCK,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_FORMS,
                            kind="switch",
                            summary="Controls whether Orca announces forms during Say All.",
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_FORM,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_LANDMARKS,
                            kind="switch",
                            summary=(
                                "Controls whether Orca announces ARIA landmarks during Say All."
                            ),
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_LANDMARK,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_LISTS,
                            kind="switch",
                            summary="Controls whether Orca announces lists during Say All.",
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_LIST,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_PANELS,
                            kind="switch",
                            summary="Controls whether Orca announces panels during Say All.",
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_GROUPING,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ANNOUNCE_TABLES,
                            kind="switch",
                            summary="Controls whether Orca announces tables during Say All.",
                            schema="say-all",
                            key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_TABLE,
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, presenter: SayAllPresenter) -> None:
        self._only_speak_displayed_control = preferences_grid_base.BooleanPreferenceControl(
            label=guilabels.SPEECH_ONLY_SPEAK_DISPLAYED_TEXT,
            getter=presenter.get_only_speak_displayed_text,
            setter=presenter.set_only_speak_displayed_text,
            prefs_key=say_all_presenter.SayAllPresenter.KEY_ONLY_SPEAK_DISPLAYED_TEXT,
        )

        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.SAY_ALL_BY,
                options=[guilabels.SAY_ALL_STYLE_SENTENCE, guilabels.SAY_ALL_STYLE_LINE],
                values=[
                    say_all_presenter.SayAllStyle.SENTENCE.value,
                    say_all_presenter.SayAllStyle.LINE.value,
                ],
                getter=presenter.get_style_as_int,
                setter=presenter.set_style_from_int,
                prefs_key=say_all_presenter.SayAllPresenter.KEY_STYLE,
            ),
            self._only_speak_displayed_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SAY_ALL_UP_AND_DOWN_ARROW,
                getter=presenter.get_rewind_and_fast_forward_enabled,
                setter=presenter.set_rewind_and_fast_forward_enabled,
                prefs_key=say_all_presenter.SayAllPresenter.KEY_REWIND_AND_FAST_FORWARD,
                member_of=guilabels.SAY_ALL_REWIND_AND_FAST_FORWARD_BY,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SAY_ALL_STRUCTURAL_NAVIGATION,
                getter=presenter.get_structural_navigation_enabled,
                setter=presenter.set_structural_navigation_enabled,
                prefs_key=say_all_presenter.SayAllPresenter.KEY_STRUCTURAL_NAVIGATION,
                member_of=guilabels.SAY_ALL_REWIND_AND_FAST_FORWARD_BY,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ANNOUNCE_TRACKED_CHANGES,
                getter=presenter.get_announce_tracked_changes,
                setter=presenter.set_announce_tracked_changes,
                prefs_key=say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_TRACKED_CHANGES,
                member_of=guilabels.CHANGE_ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.TEXT_ATTRIBUTE_CHANGES,
                options=[
                    guilabels.TEXT_ATTRIBUTE_CHANGES_OFF,
                    guilabels.TEXT_ATTRIBUTE_CHANGES_EDITABLE,
                    guilabels.TEXT_ATTRIBUTE_CHANGES_ALWAYS,
                ],
                values=[
                    text_attribute_manager.TextAttributeChangeMode.OFF.value,
                    text_attribute_manager.TextAttributeChangeMode.EDITABLE_ONLY.value,
                    text_attribute_manager.TextAttributeChangeMode.ALWAYS.value,
                ],
                getter=presenter.get_text_attribute_change_mode_as_int,
                setter=presenter.set_text_attribute_change_mode_from_int,
                prefs_key=say_all_presenter.SayAllPresenter.KEY_TEXT_ATTRIBUTE_CHANGE_MODE,
                member_of=guilabels.CHANGE_ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            *[
                preferences_grid_base.BooleanPreferenceControl(
                    label=label,
                    getter=getter,
                    setter=setter,
                    prefs_key=key,
                    member_of=guilabels.ANNOUNCEMENTS,
                    determine_sensitivity=self._only_speak_displayed_text_is_off,
                )
                for label, getter, setter, key in [
                    (
                        guilabels.ANNOUNCE_ARTICLES,
                        presenter.get_announce_article,
                        presenter.set_announce_article,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_ARTICLE,
                    ),
                    (
                        guilabels.ANNOUNCE_BLOCKQUOTES,
                        presenter.get_announce_blockquote,
                        presenter.set_announce_blockquote,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_BLOCKQUOTE,
                    ),
                    (
                        guilabels.ANNOUNCE_CODE_BLOCKS,
                        presenter.get_announce_code_block,
                        presenter.set_announce_code_block,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_CODE_BLOCK,
                    ),
                    (
                        guilabels.ANNOUNCE_FORMS,
                        presenter.get_announce_form,
                        presenter.set_announce_form,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_FORM,
                    ),
                    (
                        guilabels.ANNOUNCE_LANDMARKS,
                        presenter.get_announce_landmark,
                        presenter.set_announce_landmark,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_LANDMARK,
                    ),
                    (
                        guilabels.ANNOUNCE_LISTS,
                        presenter.get_announce_list,
                        presenter.set_announce_list,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_LIST,
                    ),
                    (
                        guilabels.ANNOUNCE_PANELS,
                        presenter.get_announce_grouping,
                        presenter.set_announce_grouping,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_GROUPING,
                    ),
                    (
                        guilabels.ANNOUNCE_TABLES,
                        presenter.get_announce_table,
                        presenter.set_announce_table,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_TABLE,
                    ),
                ]
            ],
        ]

        info = (
            f"{guilabels.SAY_ALL_INFO}\n\n{guilabels.SAY_ALL_NAVIGATION_INFO}"
            f"\n\n{guilabels.SAY_ALL_ANNOUNCEMENTS_INFO}"
        )
        super().__init__(guilabels.GENERAL_SAY_ALL, controls, info_message=info)

    def _only_speak_displayed_text_is_off(self) -> bool:
        """Returns True if only-speak-displayed-text is off in the UI."""

        return not self._get_control_value(self._only_speak_displayed_control, False)
