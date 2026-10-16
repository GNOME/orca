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

from . import cmdnames
from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for echo."""

    return FeaturePageDoc(
        page_id="features_typing_echo",
        title="Echo",
        link_title="Echo",
        description="Configure what you hear while typing.",
        guide_xref="index#output",
        target="typing-echo.feature",
        sections=(
            FeatureSectionDoc(
                title="Echo",
                preference_categories=("echo",),
                details=(
                    "Key echo announces the keys you press. You can choose which types of "
                    "keys are spoken.\n\n"
                    "Typing echo announces text inserted into an editable field. You can "
                    "hear individual characters, completed words, or completed sentences. "
                    "You can enable both key echo and character echo without hearing the "
                    "same character twice.\n\n"
                    f"{cmdnames.CYCLE_KEY_ECHO} switches among key echo, word echo, "
                    "sentence echo, key and word echo, word and sentence echo, and off."
                ),
                command_groups=("commands.echo",),
            ),
        ),
    )
