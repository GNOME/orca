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

"""Feature documentation for key echo and typing echo."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for echo."""

    return FeaturePageDoc(
        page_id="features_typing_echo",
        title="Echo",
        link_title="Echo",
        description="Spoken feedback for keys you press and text you enter.",
        guide_xref="index#output",
        target="typing-echo.feature",
        sections=(
            FeatureSectionDoc(
                title="Echo",
                preference_categories=("echo",),
                details=(
                    "Key echo provides feedback about keys you press; typing echo provides "
                    "feedback about text entered in an editable field or terminal. The settings "
                    "below describe the available feedback and how the different forms of echo "
                    "interact."
                ),
                command_groups=("commands.echo",),
            ),
        ),
    )
