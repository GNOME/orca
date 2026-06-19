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

"""Preferences grid for typing echo support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, preferences_grid_base, typing_echo_presenter

if TYPE_CHECKING:
    from .typing_echo_presenter import TypingEchoPresenter


class TypingEchoPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Typing Echo preferences page."""

    _gsettings_schema = "typing-echo"

    def __init__(self, presenter: TypingEchoPresenter) -> None:
        self._enable_key_echo_control = preferences_grid_base.BooleanPreferenceControl(
            label=guilabels.ECHO_ENABLE_KEY_ECHO,
            getter=presenter.get_key_echo_enabled,
            setter=presenter.set_key_echo_enabled,
            prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_KEY_ECHO,
        )

        controls = [
            self._enable_key_echo_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_ALPHABETIC_KEYS,
                getter=presenter.get_alphabetic_keys_enabled,
                setter=presenter.set_alphabetic_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_ALPHABETIC_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_NUMERIC_KEYS,
                getter=presenter.get_numeric_keys_enabled,
                setter=presenter.set_numeric_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_NUMERIC_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_PUNCTUATION_KEYS,
                getter=presenter.get_punctuation_keys_enabled,
                setter=presenter.set_punctuation_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_PUNCTUATION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_SPACE,
                getter=presenter.get_space_enabled,
                setter=presenter.set_space_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_SPACE,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_MODIFIER_KEYS,
                getter=presenter.get_modifier_keys_enabled,
                setter=presenter.set_modifier_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_MODIFIER_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_FUNCTION_KEYS,
                getter=presenter.get_function_keys_enabled,
                setter=presenter.set_function_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_FUNCTION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_ACTION_KEYS,
                getter=presenter.get_action_keys_enabled,
                setter=presenter.set_action_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_ACTION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_NAVIGATION_KEYS,
                getter=presenter.get_navigation_keys_enabled,
                setter=presenter.set_navigation_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_NAVIGATION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_DIACRITICAL_KEYS,
                getter=presenter.get_diacritical_keys_enabled,
                setter=presenter.set_diacritical_keys_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_DIACRITICAL_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_CHARACTER,
                getter=presenter.get_character_echo_enabled,
                setter=presenter.set_character_echo_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_CHARACTER_ECHO,
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_WORD,
                getter=presenter.get_word_echo_enabled,
                setter=presenter.set_word_echo_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_WORD_ECHO,
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_SENTENCE,
                getter=presenter.get_sentence_echo_enabled,
                setter=presenter.set_sentence_echo_enabled,
                prefs_key=typing_echo_presenter.TypingEchoPresenter.KEY_SENTENCE_ECHO,
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
        ]

        self._presenter = presenter
        super().__init__(guilabels.ECHO, controls, info_message=guilabels.ECHO_INFO)
