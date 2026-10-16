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

"""Feature documentation for say all."""

from __future__ import annotations

from . import guilabels
from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for say all."""

    return FeaturePageDoc(
        page_id="features_say_all",
        title="Say All",
        link_title="Say All",
        description="Read continuously from your current location.",
        guide_xref="index#reading",
        target="say-all.feature",
        sections=(
            FeatureSectionDoc(
                title="Say All",
                intro="Say All reads continuously from your current location.",
                preference_categories=("say-all",),
                details=(
                    "Press a key to interrupt continuous reading. If enabled in "
                    f"{guilabels.GENERAL_SAY_ALL} preferences, Up Arrow and Down Arrow "
                    "rewind and fast-forward instead. You can "
                    "also enable structural navigation during Say All, so moving to "
                    "another heading or other document element continues reading from there."
                ),
                command_groups=("commands.say-all",),
            ),
        ),
    )
