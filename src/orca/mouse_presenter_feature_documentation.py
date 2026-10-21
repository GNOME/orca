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

"""Feature documentation for mouse review."""

from __future__ import annotations

from .help_metadata import FeatureDocumentationDoc, FeatureLinkDoc, FeatureSectionDoc


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for mouse review."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Mouse review and clicking",
                preference_categories=("mouse",),
                topic_id="mouse_review",
                command_groups=("commands.mouse",),
                target="reviewing.mouse-review",
                intro=(
                    "Mouse review presents accessible objects under the mouse pointer as you "
                    "move it. Unlike flat review, it is not limited to the active window."
                ),
                details=(
                    "Orca also provides pointer-routing and clicking commands. Mouse review, "
                    "pointer routing, and simulated clicks may not work as expected, or at all, "
                    "on Wayland. Accessible actions can still work when supported by the "
                    "application or toolkit."
                ),
                settings_and_commands=(
                    FeatureLinkDoc("commands.mouse"),
                    FeatureLinkDoc("preferences.mouse"),
                ),
            ),
        ),
    )
