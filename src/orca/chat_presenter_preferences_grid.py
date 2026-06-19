# Orca
#
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

"""Preferences grid for chat support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import chat_presenter, guilabels, preferences_grid_base

if TYPE_CHECKING:
    from .chat_presenter import ChatPresenter


class ChatPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Preferences grid for Chat settings."""

    _gsettings_schema = "chat"
    _documentation_summary = (
        "Use these settings to control how chat messages and chat-room context are presented."
    )

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for chat preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.KB_GROUP_CHAT,
            panel_id="chat_presenter.chat",
            description=(
                "Chat settings control how Orca presents messages, room names, typing "
                "status, and message history in supported chat applications."
            ),
            schema="chat",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.CHAT_SPEAK_ROOM_NAME,
                    kind="switch",
                    summary="Controls whether Orca includes the chat room name with messages.",
                    schema="chat",
                    key=chat_presenter.ChatPresenter.KEY_SPEAK_ROOM_NAME,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.CHAT_SPEAK_ROOM_NAME_LAST,
                    kind="switch",
                    summary=(
                        "Controls whether the chat room name is spoken after the message "
                        "instead of before it."
                    ),
                    schema="chat",
                    key=chat_presenter.ChatPresenter.KEY_SPEAK_ROOM_NAME_LAST,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.CHAT_ANNOUNCE_BUDDY_TYPING,
                    kind="switch",
                    summary="Controls whether Orca announces when people are typing.",
                    schema="chat",
                    key=chat_presenter.ChatPresenter.KEY_ANNOUNCE_BUDDY_TYPING,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.CHAT_SEPARATE_MESSAGE_HISTORIES,
                    kind="switch",
                    summary=(
                        "Controls whether Orca keeps separate recent-message histories for "
                        "each chat room."
                    ),
                    schema="chat",
                    key=chat_presenter.ChatPresenter.KEY_ROOM_HISTORIES,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.CHAT_SPEAK_MESSAGES_FROM,
                    kind="choice",
                    summary="Controls which incoming chat messages Orca speaks automatically.",
                    schema="chat",
                    key=chat_presenter.ChatPresenter.KEY_MESSAGE_VERBOSITY,
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.CHAT_SPEAK_MESSAGES_ALL,
                            value="all",
                            summary=(
                                "Speaks messages from all channels, even when another "
                                "application is active."
                            ),
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.CHAT_SPEAK_MESSAGES_ACTIVE_CHANNEL,
                            value="focused-channel",
                            summary=(
                                "Speaks messages from the active channel, even when another "
                                "application is active."
                            ),
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED,
                            value="all-if-focused",
                            summary=(
                                "Speaks messages from all channels while the chat application "
                                "is active."
                            ),
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.CHAT_SPEAK_MESSAGES_ACTIVE,
                            value="active-channel",
                            summary=(
                                "Speaks messages from the active channel while the chat "
                                "application is active."
                            ),
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, presenter: ChatPresenter) -> None:
        options = [
            guilabels.CHAT_SPEAK_MESSAGES_ALL,
            guilabels.CHAT_SPEAK_MESSAGES_ACTIVE_CHANNEL,
            guilabels.CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED,
            guilabels.CHAT_SPEAK_MESSAGES_ACTIVE,
        ]
        values = [
            chat_presenter.ChatMessageVerbosity.ALL_ANY_APP.value,
            chat_presenter.ChatMessageVerbosity.CURRENT_ANY_APP.value,
            chat_presenter.ChatMessageVerbosity.ALL_ACTIVE_APP.value,
            chat_presenter.ChatMessageVerbosity.CURRENT_ACTIVE_APP.value,
        ]

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.SelectionPreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SPEAK_ROOM_NAME,
                getter=presenter.get_speak_room_name,
                setter=presenter.set_speak_room_name,
                prefs_key=chat_presenter.ChatPresenter.KEY_SPEAK_ROOM_NAME,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SPEAK_ROOM_NAME_LAST,
                getter=presenter.get_speak_room_name_last,
                setter=presenter.set_speak_room_name_last,
                prefs_key=chat_presenter.ChatPresenter.KEY_SPEAK_ROOM_NAME_LAST,
                determine_sensitivity=presenter.get_speak_room_name,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_ANNOUNCE_BUDDY_TYPING,
                getter=presenter.get_announce_buddy_typing,
                setter=presenter.set_announce_buddy_typing,
                prefs_key=chat_presenter.ChatPresenter.KEY_ANNOUNCE_BUDDY_TYPING,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SEPARATE_MESSAGE_HISTORIES,
                getter=presenter.get_room_histories,
                setter=presenter.set_room_histories,
                prefs_key=chat_presenter.ChatPresenter.KEY_ROOM_HISTORIES,
            ),
            preferences_grid_base.SelectionPreferenceControl(
                label=guilabels.CHAT_SPEAK_MESSAGES_FROM,
                options=options,
                values=values,
                getter=presenter.get_message_verbosity,
                setter=presenter.set_message_verbosity,
                prefs_key=chat_presenter.ChatPresenter.KEY_MESSAGE_VERBOSITY,
            ),
        ]

        super().__init__(guilabels.KB_GROUP_CHAT, controls)
