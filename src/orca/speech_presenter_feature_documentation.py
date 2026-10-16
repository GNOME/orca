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

"""Reusable feature topics for speech presentation."""

from .help_metadata import FeatureDocumentationDoc, FeatureLinkDoc, FeatureSectionDoc


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns presentation topics included in the Speech and Voices guide."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Tables",
                topic_id="tables",
                target="speech.tables.feature",
                intro=(
                    "Configure whether you hear the current cell or the whole row "
                    "while navigating tables."
                ),
                preference_panels=("speech_presenter.tables",),
                command_groups=("speech.commands.tables",),
                links=(FeatureLinkDoc("documents.table-navigation.feature"),),
            ),
            FeatureSectionDoc(
                title="Progress bars",
                topic_id="progress_bars",
                target="speech.progress-bars.feature",
                intro="Orca can speak progress updates as an operation proceeds.",
                preference_panels=("speech_presenter.progress-bars",),
                links=(
                    FeatureLinkDoc("braille.progress-bars.feature", "Braille progress bars"),
                    FeatureLinkDoc("sound.feature"),
                ),
            ),
            FeatureSectionDoc(
                title="Container announcements",
                topic_id="container_announcements",
                target="speech.container-announcements.feature",
                intro=(
                    "Orca can identify containers, such as lists, articles, and tables, "
                    "as you navigate document and web content."
                ),
                details=(
                    "This preferences group also includes announcements for tracked changes "
                    "such as insertions and deletions; these are changes to content rather "
                    "than containers. Say All has separate announcement settings for "
                    "continuous reading."
                ),
                links=(FeatureLinkDoc("say-all.feature"),),
                preference_panels=("speech_presenter.container-announcements",),
            ),
            FeatureSectionDoc(
                title="On-screen speech display",
                topic_id="on_screen_display",
                target="speech.on-screen-display.feature",
                intro="The on-screen speech display shows the text Orca is speaking.",
                preference_panels=("speech_presenter.on-screen-display",),
                command_groups=("speech.commands.on-screen-display",),
            ),
        )
    )
