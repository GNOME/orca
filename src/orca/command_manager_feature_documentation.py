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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA 02110-1301 USA.

"""Feature documentation for Orca's keyboard layouts and modifier keys."""

from __future__ import annotations

from . import guilabels
from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for keyboard layouts and modifier keys."""

    return FeaturePageDoc(
        page_id="features_keyboard_layout",
        title="Keyboard layout and Orca Modifier",
        link_title="Keyboard layout and Orca Modifier",
        description="Choose shortcuts and modifier keys for Orca commands.",
        guide_xref="index#getting_started",
        target="keyboard-layout.feature",
        sections=(
            FeatureSectionDoc(
                title="Keyboard layout and Orca Modifier",
                preference_categories=("commands",),
                command_groups=("keyboard-layout.commands",),
                intro=(
                    "Orca has two keyboard layouts that determine the default shortcuts for "
                    "some commands, such as flat review, Where Am I, and Say All. Desktop uses "
                    "numeric keypad keys for some commands. Laptop does not use keypad keys. "
                    "Num Lock must be off to use Desktop keypad shortcuts. You can use either "
                    "layout on any computer.\n\n"
                    "Orca also has its own modifier key, which works like Shift, Ctrl, or Alt: "
                    "hold it down while pressing another key to perform a command. In this "
                    "documentation, Orca Modifier means whichever key you have configured for this "
                    "purpose.\n\n"
                    "You can choose one or more of the following as Orca Modifier keys: "
                    "Insert, Keypad Insert, and Caps Lock. Desktop defaults to Insert and "
                    "Keypad Insert; Laptop defaults to Caps Lock. Each layout has its own "
                    "modifier-key settings. "
                    "At least one modifier must remain enabled.\n\n"
                    "Orca takes over the normal behavior of configured modifier keys. "
                    "Press a configured modifier key twice quickly to perform its usual "
                    "single-press action."
                    "\n\n"
                    "In the command lists, press twice or press three times means to press "
                    f"the shortcut that many times quickly. {guilabels.MODIFIER_KEYS} is "
                    "the name of the setting for selecting your Orca Modifier keys."
                ),
                settings_and_commands=(FeatureLinkDoc("preferences.commands"),),
                links=(FeatureLinkDoc("screen-reader.configuration"),),
            ),
        ),
    )
