# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Command definitions for live regions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand
from .help_metadata import CommandDoc, CommandGroupDoc, CommandSectionDoc

if TYPE_CHECKING:
    from .live_region_presenter import LiveRegionPresenter


def get_documentation() -> CommandGroupDoc:
    """Returns documentation metadata for live region commands."""

    return CommandGroupDoc(
        target="documents.live-regions.commands",
        commands=(
            CommandDoc(
                "toggle_live_region_presentation",
                details=(
                    "Turns announcements off for the current page. Use it again to restore "
                    "announcements. It does not change your saved default settings."
                ),
            ),
            CommandDoc(
                "toggle_live_region_support",
                details=(
                    "Turns live region support on or off. When enabled, Orca keeps the last "
                    "nine live region messages so you can review them later."
                ),
            ),
            CommandDoc(
                "advance_live_politeness",
                details=(
                    "Cycles through off, polite, and assertive politeness levels for the "
                    "current live region."
                ),
            ),
        ),
        summary=(
            "Live regions are areas of a web page that update automatically, "
            "such as stock tickers, weather updates, or chat messages."
        ),
        sections=(
            CommandSectionDoc(
                title="Commands",
                command_names=(
                    "toggle_live_region_support",
                    "advance_live_politeness",
                    "toggle_live_region_presentation",
                    "present_previous_live_region_message",
                    "present_next_live_region_message",
                ),
            ),
        ),
    )


def get_commands(owner: LiveRegionPresenter) -> list[Command]:
    """Returns commands for live regions."""

    kb_orca_backslash = keybindings.KeyBinding("backslash", keybindings.ORCA_MODIFIER_MASK)
    return [
        KeyboardCommand(
            "toggle_live_region_support",
            owner.toggle_monitoring,
            owner.GROUP_LABEL,
            cmdnames.LIVE_REGIONS_MONITOR,
            desktop_keybinding=kb_orca_backslash,
            laptop_keybinding=kb_orca_backslash,
            is_group_toggle=True,
        ),
        KeyboardCommand(
            "present_previous_live_region_message",
            owner.present_previous_live_region_message,
            owner.GROUP_LABEL,
            cmdnames.LIVE_REGIONS_PREVIOUS,
        ),
        KeyboardCommand(
            "advance_live_politeness",
            owner._advance_politeness_level,  # pylint: disable=protected-access
            owner.GROUP_LABEL,
            cmdnames.LIVE_REGIONS_ADVANCE_POLITENESS,
        ),
        KeyboardCommand(
            "toggle_live_region_presentation",
            owner.toggle_live_region_presentation,
            owner.GROUP_LABEL,
            cmdnames.LIVE_REGIONS_ARE_ANNOUNCED,
            is_group_toggle=True,
        ),
        KeyboardCommand(
            "present_next_live_region_message",
            owner.present_next_live_region_message,
            owner.GROUP_LABEL,
            cmdnames.LIVE_REGIONS_NEXT,
        ),
    ]
