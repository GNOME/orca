# Orca
#
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

"""Command definitions for chat."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .chat_presenter import ChatPresenter


def get_commands(owner: ChatPresenter) -> list[Command]:
    """Returns commands for chat."""

    return [
        KeyboardCommand(
            "chat_toggle_room_name_prefix",
            owner.toggle_prefix,
            owner.GROUP_LABEL,
            cmdnames.CHAT_TOGGLE_ROOM_NAME_PREFIX,
        ),
        KeyboardCommand(
            "chat_toggle_buddy_typing",
            owner.toggle_buddy_typing,
            owner.GROUP_LABEL,
            cmdnames.CHAT_TOGGLE_BUDDY_TYPING,
        ),
        KeyboardCommand(
            "chat_toggle_message_histories",
            owner.toggle_message_histories,
            owner.GROUP_LABEL,
            cmdnames.CHAT_TOGGLE_MESSAGE_HISTORIES,
        ),
        KeyboardCommand(
            "chat_previous_message",
            owner.present_previous_message,
            owner.GROUP_LABEL,
            cmdnames.CHAT_PREVIOUS_MESSAGE,
        ),
        KeyboardCommand(
            "chat_next_message",
            owner.present_next_message,
            owner.GROUP_LABEL,
            cmdnames.CHAT_NEXT_MESSAGE,
        ),
    ]
