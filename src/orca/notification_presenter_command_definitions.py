# Orca
#
# Copyright 2023 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
# Based on the feature created by:
# Author: Jose Vilmar <vilmar@informal.com.br>
# Copyright 2010 Informal Informatica LTDA.
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

"""Command definitions for notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .notification_presenter import NotificationPresenter


def get_commands(owner: NotificationPresenter) -> list[Command]:
    """Returns commands for notifications."""

    return [
        KeyboardCommand(
            "present_last_notification",
            owner.present_last_notification,
            owner.GROUP_LABEL,
            cmdnames.NOTIFICATION_MESSAGES_LAST,
        ),
        KeyboardCommand(
            "present_next_notification",
            owner.present_next_notification,
            owner.GROUP_LABEL,
            cmdnames.NOTIFICATION_MESSAGES_NEXT,
        ),
        KeyboardCommand(
            "present_previous_notification",
            owner.present_previous_notification,
            owner.GROUP_LABEL,
            cmdnames.NOTIFICATION_MESSAGES_PREVIOUS,
        ),
        KeyboardCommand(
            "show_notification_list",
            owner.show_notification_list,
            owner.GROUP_LABEL,
            cmdnames.NOTIFICATION_MESSAGES_LIST,
        ),
    ]
