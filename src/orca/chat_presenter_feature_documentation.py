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

"""Feature documentation for chat."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for chat."""

    return FeaturePageDoc(
        page_id="features_chat",
        title="Chat",
        link_title="Chat",
        description="Configure and review chat message presentation.",
        guide_xref="index#interaction",
        target="chat.feature",
        sections=(
            FeatureSectionDoc(
                title="Chat",
                intro=(
                    "Orca can announce incoming messages and review recent messages in "
                    "supported chat applications. These applications and settings may refer "
                    "to conversations as rooms or channels."
                ),
                preference_categories=("chat",),
                command_groups=("commands.chat",),
            ),
        ),
    )
