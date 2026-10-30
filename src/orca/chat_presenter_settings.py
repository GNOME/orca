# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

"""Settings keys and values for chat."""

from __future__ import annotations

from enum import Enum

from . import gsettings_registry


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.ChatMessageVerbosity",
    values={"all": 0, "all-if-focused": 1, "focused-channel": 2, "active-channel": 3},
)
class ChatMessageVerbosity(Enum):
    """Chat message verbosity level enumeration."""

    ALL_ANY_APP = 0
    ALL_ACTIVE_APP = 1
    CURRENT_ACTIVE_APP = 2
    CURRENT_ANY_APP = 3

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower().replace("_", "-")


class ChatSettings:
    """The chat settings keys."""

    KEY_ANNOUNCE_BUDDY_TYPING = "announce-buddy-typing"
    KEY_MESSAGE_VERBOSITY = "message-verbosity"
    KEY_ROOM_HISTORIES = "room-histories"
    KEY_SPEAK_ROOM_NAME = "speak-room-name"
    KEY_SPEAK_ROOM_NAME_LAST = "speak-room-name-last"
