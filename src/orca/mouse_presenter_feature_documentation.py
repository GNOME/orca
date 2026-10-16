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

from . import cmdnames, guilabels
from .help_metadata import FeatureDocumentationDoc, FeatureLinkDoc, FeatureSectionDoc


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for mouse review."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Mouse review",
                preference_categories=("mouse",),
                topic_id="mouse_review",
                command_groups=("commands.mouse",),
                target="reviewing.mouse-review",
                intro=(
                    "Mouse review presents accessible objects under the mouse pointer as "
                    "you move it. Unlike flat review, it is not limited to the active window."
                ),
                details=(
                    "Mouse review is disabled by default. To enable it, turn on "
                    f"{guilabels.GENERAL_SPEAK_OBJECT_UNDER_MOUSE} "
                    f"in {guilabels.MOUSE} preferences.\n\n"
                    f"The {cmdnames.MOUSE_REVIEW_TOGGLE} command works whether or not you have "
                    "enabled mouse review in preferences, "
                    "so you can turn mouse review on only when you need it.\n\n"
                    "The pointer-routing and click commands act on the flat review location "
                    "when flat review is active, or on the focused object otherwise.\n\n"
                    "Mouse review, pointer routing, and simulated clicks depend on support "
                    "from your desktop. They may not work on Wayland."
                ),
                settings_and_commands=(
                    FeatureLinkDoc("commands.mouse"),
                    FeatureLinkDoc("preferences.mouse"),
                ),
                links=(FeatureLinkDoc("reviewing.flat-review"),),
            ),
        ),
    )
