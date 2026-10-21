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

"""Feature documentation for settings profiles."""

from . import guilabels
from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns the combined profiles topic."""

    return FeaturePageDoc(
        page_id="features_profiles",
        title="Profiles",
        link_title="Profiles",
        description="Create collections of settings for different activities.",
        guide_xref="index#getting_started",
        target="profiles.feature",
        sections=(
            FeatureSectionDoc(
                title="Profiles",
                intro=(
                    "Profiles are named collections of Orca settings for different activities. "
                    f'Orca normally starts with the "{guilabels.PROFILE_DEFAULT}" profile. '
                    "To start with another saved "
                    "profile, run `orca -p NAME` or `orca --profile NAME`, replacing NAME with "
                    "the profile's name. If Orca is already running as an application, add "
                    "`--replace`."
                ),
                preference_categories=("profiles",),
                command_groups=("commands.profiles",),
                links=(FeatureLinkDoc("screen-reader.settings-backup"),),
            ),
        ),
    )
