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

"""Settings keys and values for braille."""

from __future__ import annotations

from enum import Enum

from . import gsettings_registry


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.VerbosityLevel",
    values={"brief": 0, "verbose": 1},
)
class VerbosityLevel(Enum):
    """Verbosity level enumeration."""

    BRIEF = 0
    VERBOSE = 1

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.BrailleIndicator",
    values={"none": 0, "dot7": 64, "dot8": 128, "dots78": 192},
)
class BrailleIndicator(Enum):
    """Braille indicator enumeration."""

    NONE = 0x00
    DOT7 = 0x40
    DOT8 = 0x80
    DOTS78 = 0xC0

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.ProgressBarVerbosity",
    values={"all": 0, "application": 1, "window": 2},
)
class ProgressBarVerbosity(Enum):
    """Progress bar verbosity level enumeration."""

    ALL = 0
    APPLICATION = 1
    WINDOW = 2


class BrailleSettings:
    """The braille settings keys."""

    KEY_BRAILLE_PROGRESS_BAR_UPDATES = "braille-progress-bar-updates"
    KEY_COMPUTER_BRAILLE_AT_CURSOR = "computer-braille-at-cursor"
    KEY_CONTRACTED_BRAILLE = "contracted-braille"
    KEY_CONTRACTION_TABLE = "contraction-table"
    KEY_DISPLAY_ANCESTORS = "display-ancestors"
    KEY_ENABLED = "enabled"
    KEY_END_OF_LINE_INDICATOR = "end-of-line-indicator"
    KEY_FLASH_MESSAGES = "flash-messages"
    KEY_FLASH_MESSAGES_DETAILED = "flash-messages-detailed"
    KEY_FLASH_MESSAGES_PERSISTENT = "flash-messages-persistent"
    KEY_FLASH_MESSAGE_DURATION = "flash-message-duration"
    KEY_LINK_INDICATOR = "link-indicator"
    KEY_MONITOR_BACKGROUND = "monitor-background"
    KEY_MONITOR_CELL_COUNT = "monitor-cell-count"
    KEY_MONITOR_FOREGROUND = "monitor-foreground"
    KEY_MONITOR_SHOW_DOTS = "monitor-show-dots"
    KEY_PRESENT_MNEMONICS = "present-mnemonics"
    KEY_PROGRESS_BAR_BRAILLE_INTERVAL = "progress-bar-braille-interval"
    KEY_PROGRESS_BAR_BRAILLE_VERBOSITY = "progress-bar-braille-verbosity"
    KEY_ROLENAME_STYLE = "rolename-style"
    KEY_SELECTOR_INDICATOR = "selector-indicator"
    KEY_TEXT_ATTRIBUTES_INDICATOR = "text-attributes-indicator"
    KEY_VERBOSITY_LEVEL = "verbosity-level"
    KEY_WORD_WRAP = "word-wrap"
