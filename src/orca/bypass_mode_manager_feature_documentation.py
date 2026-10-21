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

"""Feature documentation for bypass mode."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for bypass mode."""

    return FeaturePageDoc(
        page_id="features_bypass_mode",
        title="Bypass mode",
        link_title="Bypass mode",
        description="Pass keys to applications without Orca handling commands.",
        guide_xref="index#interaction",
        target="bypass-mode.feature",
        sections=(
            FeatureSectionDoc(
                title="Bypass mode",
                intro=(
                    "Bypass mode stops Orca from handling commands and lets the application "
                    "receive them instead."
                ),
                command_groups=("commands.bypass-mode",),
            ),
        ),
    )
