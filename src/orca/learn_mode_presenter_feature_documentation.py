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

"""Feature documentation for learn mode."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for learn mode."""

    return FeaturePageDoc(
        page_id="features_learn_mode",
        title="Learn mode",
        link_title="Learn mode",
        description="Explore Orca shortcuts without performing their commands.",
        guide_xref="index#getting_started",
        target="learn-mode.feature",
        sections=(
            FeatureSectionDoc(
                title="Learn mode",
                intro=(
                    "Learn mode lets you explore Orca shortcuts without performing their "
                    "commands. Press a key or key combination, and Orca presents the "
                    "associated command description in speech and braille, if one is assigned."
                ),
                details=(
                    "Press F1 to leave learn mode and open Orca help. Press F2 to leave learn "
                    "mode and show Orca shortcuts. Press Escape to exit learn mode without "
                    "opening another window."
                ),
                command_groups=("commands.learn-mode",),
            ),
        ),
    )
