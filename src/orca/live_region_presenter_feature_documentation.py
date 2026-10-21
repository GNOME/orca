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

"""Feature documentation for live regions."""

from __future__ import annotations

from .help_metadata import FeatureDocumentationDoc, FeatureSectionDoc


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for live regions."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Live regions",
                topic_id="live_regions",
                command_groups=("documents.live-regions.commands",),
                command_names=("previous_live_region", "next_live_region", "last_live_region"),
                target="documents.live-regions.feature",
                intro=(
                    "Live regions are areas of a web page that update automatically, such "
                    "as stock tickers, weather updates, chat messages, or alerts."
                ),
                details=(
                    "Live regions have a politeness level that suggests when assistive "
                    "technologies should present updates. Off requests no announcements, polite "
                    "requests announcements when other speech has finished, and assertive "
                    "requests immediate announcements. The commands below control presentation "
                    "and navigation."
                ),
            ),
        ),
    )
