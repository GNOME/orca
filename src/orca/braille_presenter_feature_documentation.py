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

from . import object_properties
from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for braille."""

    return FeaturePageDoc(
        page_id="features_braille_guide",
        title="Braille",
        link_title="Braille",
        description="Braille presentation of on-screen content and Orca messages.",
        guide_xref="index#output",
        target="braille.feature",
        sections_as_pages=True,
        preference_category="braille",
        sections=(
            FeatureSectionDoc(
                title="Braille output",
                topic_id="output",
                target="braille.output.feature",
                preference_panels=("braille_presenter.braille",),
                details=(
                    "Braille displays communicate with Orca through BRLTTY, a service that "
                    "connects braille displays to applications. Depending on your display and "
                    "system setup, you may need to configure your display in BRLTTY. You may "
                    "also need to start BRLTTY before running Orca if your system does not "
                    "start it automatically. Orca does not start BRLTTY itself.\n\n"
                    "Orca uses the following indicators to show the state of controls "
                    "in braille:\n\n"
                    f"- Check boxes: `{object_properties.CHECK_BOX_INDICATORS_BRAILLE[0]}` "
                    f"for unchecked, `{object_properties.CHECK_BOX_INDICATORS_BRAILLE[1]}` "
                    f"for checked, and `{object_properties.CHECK_BOX_INDICATORS_BRAILLE[2]}` "
                    "for partially checked.\n"
                    f"- Radio buttons: `{object_properties.RADIO_BUTTON_INDICATORS_BRAILLE[0]}` "
                    f"for unselected and `{object_properties.RADIO_BUTTON_INDICATORS_BRAILLE[1]}` "
                    "for selected.\n"
                    f"- Switches: `{object_properties.SWITCH_INDICATORS_BRAILLE[0]}` "
                    f"for off and `{object_properties.SWITCH_INDICATORS_BRAILLE[1]}` for on.\n"
                    f"- Toggle buttons: `{object_properties.TOGGLE_BUTTON_INDICATORS_BRAILLE[0]}` "
                    "for not pressed and "
                    f"`{object_properties.TOGGLE_BUTTON_INDICATORS_BRAILLE[1]}` "
                    "for pressed.\n"
                    f"- Read-only text: `{object_properties.STATE_READ_ONLY_BRAILLE}` "
                    "indicates that the text cannot be edited.\n\n"
                    "Orca can also mark links, selected text, and text attributes by raising "
                    "dots beneath the affected characters, similar to underlining. See "
                    "[[braille.display-settings.feature]] to configure these indicators, "
                    "and [[text-attributes.feature]] to choose which text attributes are marked."
                ),
                command_groups=("braille.commands.panning-and-routing",),
            ),
            FeatureSectionDoc(
                title="Verbosity",
                topic_id="verbosity",
                intro="Configure how much object information is displayed in braille.",
                preference_panels=("braille_presenter.verbosity",),
            ),
            FeatureSectionDoc(
                title="Display settings",
                topic_id="display_settings",
                target="braille.display-settings.feature",
                intro=(
                    "Braille display settings control how text fits on your display and how "
                    "additional information is marked."
                ),
                details=(
                    "Contracted braille uses abbreviations for words and groups of letters, "
                    "allowing more text to fit on the display. Orca uses liblouis translation "
                    "tables to determine the symbols and contractions for your language.\n"
                    "\n"
                    "Indicator dots mark information such as links and selected text without "
                    "adding words to the display. See [[text-attributes.feature]] to choose "
                    "which text attributes are marked."
                ),
                links=(
                    FeatureLinkDoc("braille.output.feature"),
                    FeatureLinkDoc("text-attributes.feature"),
                ),
                preference_panels=("braille_presenter.display-settings",),
                command_groups=("braille.commands.contraction",),
            ),
            FeatureSectionDoc(
                title="Flash messages",
                topic_id="flash_messages",
                intro=(
                    "Flash messages are temporary messages on the braille display that "
                    "provide feedback from Orca, such as confirmation that a setting has "
                    "changed. They replace the displayed content without moving focus or "
                    "the caret. When a message expires, Orca restores the previous display "
                    "contents."
                ),
                preference_panels=("braille_presenter.flash-messages",),
            ),
            FeatureSectionDoc(
                title="Progress bars",
                topic_id="progress_bars",
                target="braille.progress-bars.feature",
                intro=(
                    "Orca can show progress-bar updates on your braille display so you can "
                    "track tasks such as downloads or file transfers."
                ),
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
