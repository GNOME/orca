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

from . import guilabels, preferences_grid_base
from .help_metadata import (
    PreferenceCategoryDoc,
    PreferenceControlDoc,
    PreferencePanelDoc,
)
from .typing_echo_presenter_settings import TypingEchoSettings

if TYPE_CHECKING:
    from .typing_echo_presenter import TypingEchoPresenter


class TypingEchoPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Typing Echo preferences page."""

    _gsettings_schema = "typing-echo"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for echo preferences."""

        return PreferencePanelDoc(
            title=guilabels.ECHO,
            panel_id="typing_echo_presenter.echo",
            category=PreferenceCategoryDoc(
                category_id="echo",
                title="Echo",
                description=(
                    "Echo speaks the keys you press and the text you enter. Configure key "
                    "echo and typing echo."
                ),
                panels=("typing_echo_presenter.echo",),
            ),
            command_groups=("commands.echo",),
            schema="typing-echo",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.ECHO_ENABLE_KEY_ECHO,
                    kind="switch",
                    summary=(
                        "Controls whether Orca speaks keys as they are pressed, including keys "
                        "that do not insert text, such as navigation and function keys. Choose "
                        "which key types are spoken with the key-type settings below. In "
                        "terminals, key echo also waits for matching text to appear before "
                        "announcing a printable key, so input that is not displayed, such as a "
                        "password, is not echoed."
                    ),
                    schema="typing-echo",
                    key=TypingEchoSettings.KEY_KEY_ECHO,
                ),
                PreferenceControlDoc(
                    label=guilabels.ECHO_KEYS_TO_ECHO,
                    kind="group",
                    summary="Controls which types of keys Orca speaks when they are pressed.",
                    controls=(
                        PreferenceControlDoc(
                            label=guilabels.ECHO_ALPHABETIC_KEYS,
                            kind="switch",
                            summary="Controls whether Orca speaks keys such as A, B, and C.",
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_ALPHABETIC_KEYS,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_NUMERIC_KEYS,
                            kind="switch",
                            summary="Controls whether Orca speaks keys such as 1, 2, and 3.",
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_NUMERIC_KEYS,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_PUNCTUATION_KEYS,
                            kind="switch",
                            summary=(
                                "Controls whether Orca speaks keys such as percent, "
                                "semicolon, and question mark."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_PUNCTUATION_KEYS,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_SPACE,
                            kind="switch",
                            summary="Controls whether Orca speaks Space when it is pressed.",
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_SPACE,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_MODIFIER_KEYS,
                            kind="switch",
                            summary=(
                                "Controls whether Orca speaks modifier keys such as Shift, "
                                "Ctrl, Alt, and Meta."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_MODIFIER_KEYS,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_FUNCTION_KEYS,
                            kind="switch",
                            summary=(
                                "Controls whether Orca speaks function keys from F1 through F12."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_FUNCTION_KEYS,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_ACTION_KEYS,
                            kind="switch",
                            summary=(
                                "Controls whether Orca speaks action keys such as Backspace, "
                                "Delete, Enter, Escape, Tab, Page Up, and Page Down."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_ACTION_KEYS,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_NAVIGATION_KEYS,
                            kind="switch",
                            summary=(
                                "Controls whether Orca speaks navigation keys such as Left "
                                "Arrow, Right Arrow, Up Arrow, Down Arrow, Home, and End."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_NAVIGATION_KEYS,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_DIACRITICAL_KEYS,
                            kind="switch",
                            summary=(
                                "Controls whether Orca speaks diacritical keys, such as "
                                "keys used to add accents to letters."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_DIACRITICAL_KEYS,
                        ),
                    ),
                ),
                PreferenceControlDoc(
                    label=guilabels.ECHO_TYPING_ECHO,
                    kind="group",
                    summary=(
                        "Controls whether Orca speaks text inserted into the document as you type."
                    ),
                    controls=(
                        PreferenceControlDoc(
                            label=guilabels.ECHO_CHARACTER,
                            kind="switch",
                            summary=(
                                "Announces text inserted as you type in an editable field or "
                                "terminal, rather than the key press itself. It depends on the "
                                "application reporting inserted text through its accessibility "
                                "support. When both key echo and character echo are enabled, "
                                "Orca uses character echo for printable text typed into an "
                                "editable field or terminal and suppresses the corresponding "
                                "key echo, avoiding duplicate announcements. Other enabled key "
                                "types can still be announced, as can printable keys pressed "
                                "outside editable text."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_CHARACTER_ECHO,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_WORD,
                            kind="switch",
                            summary=(
                                "Announces completed words. Enable it alongside character echo "
                                "to have both individual characters and completed words spoken."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_WORD_ECHO,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.ECHO_SENTENCE,
                            kind="switch",
                            summary=(
                                "Announces completed sentences. Enable it alongside character "
                                "echo to have both individual characters and completed "
                                "sentences spoken."
                            ),
                            schema="typing-echo",
                            key=TypingEchoSettings.KEY_SENTENCE_ECHO,
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, presenter: TypingEchoPresenter) -> None:
        self._enable_key_echo_control = preferences_grid_base.BooleanPreferenceControl(
            label=guilabels.ECHO_ENABLE_KEY_ECHO,
            getter=presenter.get_key_echo_enabled,
            setter=presenter.set_key_echo_enabled,
            prefs_key=TypingEchoSettings.KEY_KEY_ECHO,
        )

        controls = [
            self._enable_key_echo_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_ALPHABETIC_KEYS,
                getter=presenter.get_alphabetic_keys_enabled,
                setter=presenter.set_alphabetic_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_ALPHABETIC_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_NUMERIC_KEYS,
                getter=presenter.get_numeric_keys_enabled,
                setter=presenter.set_numeric_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_NUMERIC_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_PUNCTUATION_KEYS,
                getter=presenter.get_punctuation_keys_enabled,
                setter=presenter.set_punctuation_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_PUNCTUATION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_SPACE,
                getter=presenter.get_space_enabled,
                setter=presenter.set_space_enabled,
                prefs_key=TypingEchoSettings.KEY_SPACE,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_MODIFIER_KEYS,
                getter=presenter.get_modifier_keys_enabled,
                setter=presenter.set_modifier_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_MODIFIER_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_FUNCTION_KEYS,
                getter=presenter.get_function_keys_enabled,
                setter=presenter.set_function_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_FUNCTION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_ACTION_KEYS,
                getter=presenter.get_action_keys_enabled,
                setter=presenter.set_action_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_ACTION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_NAVIGATION_KEYS,
                getter=presenter.get_navigation_keys_enabled,
                setter=presenter.set_navigation_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_NAVIGATION_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_DIACRITICAL_KEYS,
                getter=presenter.get_diacritical_keys_enabled,
                setter=presenter.set_diacritical_keys_enabled,
                prefs_key=TypingEchoSettings.KEY_DIACRITICAL_KEYS,
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_CHARACTER,
                getter=presenter.get_character_echo_enabled,
                setter=presenter.set_character_echo_enabled,
                prefs_key=TypingEchoSettings.KEY_CHARACTER_ECHO,
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_WORD,
                getter=presenter.get_word_echo_enabled,
                setter=presenter.set_word_echo_enabled,
                prefs_key=TypingEchoSettings.KEY_WORD_ECHO,
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_SENTENCE,
                getter=presenter.get_sentence_echo_enabled,
                setter=presenter.set_sentence_echo_enabled,
                prefs_key=TypingEchoSettings.KEY_SENTENCE_ECHO,
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
        ]

        self._presenter = presenter
        super().__init__(guilabels.ECHO, controls, info_message=guilabels.ECHO_INFO)
