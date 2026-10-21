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

from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns documentation for managing personal extensions."""

    return FeaturePageDoc(
        page_id="features_user_extensions",
        title="User extensions",
        link_title="User extensions",
        description="Add and manage personal Orca features.",
        guide_xref="index#interaction",
        target="extensions.feature",
        intro=(
            "User extensions add personal features, commands, and settings to Orca. "
            "Install extension files or package directories in "
            "`~/.local/share/orca/extensions/`, or the corresponding location under "
            "your XDG data directory. Only install code from sources you trust: "
            "approved extensions run with your user account's permissions and can "
            "access content Orca presents, including typed text and messages.\n\n"
            "Orca does not have an official extension store. Community catalogs "
            "and stores are not endorsed or security-reviewed by the Orca project."
        ),
        details=(
            "Use the settings below to inspect and manage installed extensions. You can also "
            "approve or revoke approval from the command line, as described in "
            "[[screen-reader.introduction]]. Extensions approved that way load on the next Orca "
            "startup."
        ),
        sections=(
            FeatureSectionDoc(
                title="Extension settings",
                preference_categories=("extensions",),
                links=(FeatureLinkDoc("screen-reader.introduction"),),
            ),
            FeatureSectionDoc(
                title="Command shortcuts",
                intro=(
                    "An extension can load successfully even if some of its commands have no "
                    "shortcut. If a requested shortcut is already used by an Orca command or "
                    "another extension, the conflicting extension command is left unbound. See "
                    "[[keyboard-layout.feature]] for configuring shortcuts."
                ),
                links=(FeatureLinkDoc("preferences.commands"),),
            ),
        ),
    )
