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

"""Feature documentation for non-speech audio."""

from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns the combined sound topic."""

    return FeaturePageDoc(
        page_id="features_sound",
        title="Sound",
        link_title="Sound",
        description="Non-speech audio cues and progress-bar beeps.",
        guide_xref="index#output",
        target="sound.feature",
        sections=(
            FeatureSectionDoc(
                title="Sound",
                intro=(
                    "Orca can use non-speech audio cues and beeps to indicate progress-bar changes."
                ),
                details=(
                    "Sound icons are short audio cues for events such as an error. "
                    "Their files are loaded from the sounds directory in your Orca "
                    "user-data directory, normally `~/.local/share/orca/sounds`.\n\n"
                    "Progress-bar beeps rise in pitch as progress increases."
                ),
                preference_categories=("sound",),
                links=(
                    FeatureLinkDoc("speech.progress-bars.feature", "Speech progress bars"),
                    FeatureLinkDoc("braille.progress-bars.feature", "Braille progress bars"),
                ),
            ),
        ),
    )
