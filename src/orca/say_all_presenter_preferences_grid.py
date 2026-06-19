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
                    (
                        guilabels.ANNOUNCE_TRACKED_CHANGES,
                        presenter.get_announce_tracked_changes,
                        presenter.set_announce_tracked_changes,
                        say_all_presenter.SayAllPresenter.KEY_ANNOUNCE_TRACKED_CHANGES,
                    ),
                ]
            ],
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
                member_of=guilabels.ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
        ]

        info = (
            f"{guilabels.SAY_ALL_INFO}\n\n{guilabels.SAY_ALL_NAVIGATION_INFO}"
            f"\n\n{guilabels.SAY_ALL_CONTAINER_INFO}"
        )
        super().__init__(guilabels.GENERAL_SAY_ALL, controls, info_message=info)

    def _only_speak_displayed_text_is_off(self) -> bool:
        """Returns True if only-speak-displayed-text is off in the UI."""

        widget = self.get_widget_for_control(self._only_speak_displayed_control)
        if widget:
            return not widget.get_active()
        return True
