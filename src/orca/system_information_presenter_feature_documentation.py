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

"""Feature documentation for system information."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for system information."""

    return FeaturePageDoc(
        page_id="features_system_information",
        title="System information",
        link_title="System information",
        description="Check the time, date, battery, and resource usage.",
        guide_xref="index#information",
        target="system-information.feature",
        sections=(
            FeatureSectionDoc(
                title="System information",
                intro="Present the date, time, battery status, and resource usage.",
                details=(
                    "Presenting battery status and CPU and memory usage requires the Python "
                    "psutil package, often packaged as python3-psutil."
                ),
                preference_categories=("system-information",),
                command_groups=("commands.system-information",),
            ),
        ),
    )
