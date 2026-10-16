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

"""Feature documentation for braille."""

from __future__ import annotations

from . import cmdnames, guilabels
from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for braille."""

    return FeaturePageDoc(
        page_id="features_braille_guide",
        title="Braille",
        link_title="Braille",
        description="Read and control braille output.",
        guide_xref="index#output",
        target="braille.feature",
        sections_as_pages=True,
        preference_category="braille",
        intro=(
            "These topics describe braille output, display settings, temporary messages, "
            "and the on-screen braille display."
        ),
        sections=(
            FeatureSectionDoc(
                title="Braille output",
                topic_id="output",
                target="braille.output.feature",
                preference_panels=("braille_presenter.braille",),
                intro=(
                    "Read content with a refreshable braille display and control its reading "
                    "location."
                ),
                details=(
                    "Braille displays communicate with Orca through BRLTTY, a service that "
                    "connects braille displays to applications. Configure your display in "
                    "BRLTTY before enabling braille output.\n\n"
                    "You can pan the braille display, return to the current location, route "
                    "the cursor, or mark text for copying. Standard keyboard bindings can "
                    f"be changed in {guilabels.COMMANDS} preferences. "
                    "Braille display bindings depend on "
                    "the display and BRLTTY configuration and cannot be rebound in Orca.\n\n"
                    "Cursor routing moves the caret to the character at a selected braille "
                    "cell or activates the item at that cell. To copy text, use "
                    f"{cmdnames.BRAILLE_CUT_BEGIN} at its start and {cmdnames.BRAILLE_CUT_LINE} "
                    "at its end. Orca selects the text and copies "
                    "it to the clipboard; paste it using the destination application's "
                    "usual paste command."
                ),
                command_groups=("braille.commands.panning-and-routing",),
            ),
            FeatureSectionDoc(
                title="Verbosity",
                topic_id="verbosity",
                intro="Configure how much object information you read in braille.",
                preference_panels=("braille_presenter.verbosity",),
            ),
            FeatureSectionDoc(
                title="Display settings",
                topic_id="display_settings",
                intro="Configure braille wrapping, contraction, and indicator dots.",
                details=(
                    "You can toggle contracted braille using a standard keyboard or a "
                    "braille display. See Braille output for how their bindings are configured."
                ),
                links=(FeatureLinkDoc("braille.output.feature"),),
                preference_panels=("braille_presenter.display-settings",),
                command_groups=("braille.commands.contraction",),
            ),
            FeatureSectionDoc(
                title="Flash messages",
                topic_id="flash_messages",
                intro=(
                    "Flash messages temporarily show Orca messages and command feedback in "
                    "braille, then restore the previous display contents."
                ),
                preference_panels=("braille_presenter.flash-messages",),
            ),
            FeatureSectionDoc(
                title="Progress bars",
                topic_id="progress_bars",
                target="braille.progress-bars.feature",
                intro="Follow progress-bar updates on your braille display.",
                preference_panels=("braille_presenter.progress-bars",),
                links=(
                    FeatureLinkDoc("speech.progress-bars.feature", "Speech progress bars"),
                    FeatureLinkDoc("sound.feature"),
                ),
            ),
            FeatureSectionDoc(
                title="On-screen braille display",
                topic_id="on_screen_display",
                intro=(
                    "The on-screen braille display is a window intended for developers that "
                    "shows what would be presented on a braille display."
                ),
                preference_panels=("braille_presenter.on-screen-display",),
                command_groups=("braille.commands.on-screen-display",),
            ),
        ),
    )
