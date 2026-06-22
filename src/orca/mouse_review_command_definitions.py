# Mouse reviewer for Orca
#
# Copyright 2008 Eitan Isaacson
# Copyright 2016 Igalia, S.L.
# Copyright 2026 SUSE LLC.
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

"""Command definitions for mouse review."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .mouse_review import MouseReviewer


def get_commands(owner: MouseReviewer) -> list[Command]:
    """Returns commands for mouse review."""

    return [
        KeyboardCommand(
            "toggleMouseReviewHandler",
            owner.toggle,
            owner.GROUP_LABEL,
            cmdnames.MOUSE_REVIEW_TOGGLE,
        ),
    ]
