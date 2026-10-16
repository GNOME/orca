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

"""Feature documentation for user extensions."""

from __future__ import annotations

from . import guilabels
from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns documentation for managing personal extensions."""

    return FeaturePageDoc(
        page_id="features_user_extensions",
        title="User extensions",
        link_title="User extensions",
        description="Add and manage personal Orca features.",
        guide_xref="index#interaction",
        target="extensions.feature",
        sections=(
            FeatureSectionDoc(
                title="Installing and approving extensions",
                preference_categories=("extensions",),
                intro=(
                    "User extensions add personal features, commands, and settings to Orca. "
                    "Install extension files or package directories in "
                    "~/.local/share/orca/extensions, or the corresponding location under "
                    "your XDG data directory. Only install code from sources you trust: "
                    "approved extensions run with your user account's permissions."
                ),
                details=(
                    f"Open {guilabels.USER_EXTENSIONS} in the global Preferences window "
                    "to inspect an "
                    "extension's information and approve it for loading. Changing its code "
                    "invalidates approval; inspect the changes before reapproving it. "
                    "Revoking approval prevents the extension from loading.\n\n"
                    "Use the switch beside an approved extension to enable or disable it "
                    f"without removing its approval. The {guilabels.EXTENSIONS_SETTINGS_BUTTON} "
                    "action opens any preferences "
                    "provided by the extension. Delete removes the extension file or package "
                    "after confirmation."
                ),
            ),
        ),
    )
