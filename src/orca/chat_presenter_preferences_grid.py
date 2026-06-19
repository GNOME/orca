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
