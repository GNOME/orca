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
from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns the combined profiles topic."""

    return FeaturePageDoc(
        page_id="features_profiles",
        title="Profiles",
        link_title="Profiles",
        description="Named collections of settings for different activities.",
        guide_xref="",
        target="profiles.feature",
        sections=(
            FeatureSectionDoc(
                title="Profiles",
                intro=(
                    "Profiles are named collections of Orca settings for different activities. "
                    f"Orca normally starts with the {guilabels.PROFILE_DEFAULT} profile. "
                    "To start with another saved "
                    "profile, run `orca -p NAME` or `orca --profile NAME`, replacing NAME with "
                    "the profile's name. If Orca is already running as an application, add "
                    "`--replace`."
                ),
                preference_categories=("profiles",),
                details=(
                    "To create a profile, activate the add button beside "
                    f"{guilabels.CURRENT_PROFILE}, "
                    f"type a unique name, and choose {guilabels.DIALOG_ADD}. "
                    "Orca copies the current profile's "
                    "saved settings and switches to the new profile. Apply recent edits "
                    "first if you want them included: unsaved changes are not copied and "
                    "are discarded if you continue.\n\n"
                    f"To rename a profile, use Tab to reach its {guilabels.MENU_RENAME} button. "
                    f"Type the new name and choose {guilabels.DIALOG_APPLY} in the rename dialog, "
                    "then apply or save the "
                    f"change using the Preferences window's {guilabels.MENU_BUTTON_OPTIONS} "
                    "menu.\n\n"
                    f"To remove a profile, use its {guilabels.MENU_REMOVE_PROFILE} button "
                    "and confirm. Removal "
                    "takes effect immediately and deletes its saved settings. If you remove "
                    f"the active profile, Orca switches to {guilabels.PROFILE_DEFAULT}. "
                    f"The {guilabels.PROFILE_DEFAULT} profile "
                    "cannot be renamed or removed."
                ),
                command_groups=("commands.profiles",),
            ),
        ),
    )
