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

from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for say all."""

    return FeaturePageDoc(
        page_id="features_say_all",
        title="Say All",
        link_title="Say All",
        description="Read document content continuously from your current location.",
        guide_xref="index#reading",
        target="say-all.feature",
        sections=(
            FeatureSectionDoc(
                title="Say All",
                intro="Say All speaks document content continuously from your current location.",
                preference_categories=("say-all",),
                details=(
                    "The settings below control continuous presentation and navigation during "
                    "Say All. For presenting the visible contents of a window or dialog, see "
                    "[[reviewing.flat-review]]."
                ),
                command_groups=("commands.say-all",),
                links=(
                    FeatureLinkDoc("reviewing.flat-review"),
                    FeatureLinkDoc("text-attributes.feature"),
                ),
            ),
        ),
    )
