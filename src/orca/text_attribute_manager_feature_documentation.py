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

"""Feature documentation for text formatting and attributes."""

from __future__ import annotations

from . import cmdnames, guilabels
from .help_metadata import CommandShortcutDoc, FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for examining text attributes."""

    return FeaturePageDoc(
        page_id="features_text_attributes",
        title="Text attributes",
        link_title="Text attributes",
        description="Examine text formatting in speech and braille.",
        guide_xref="index#reading",
        target="text-attributes.feature",
        intro=(
            "Text attributes describe the font, style, alignment, colors, and other "
            "formatting associated with text. The information available to Orca depends "
            "on which attributes the application exposes to assistive technologies."
        ),
        sections=(
            FeatureSectionDoc(
                title="Checking formatting",
                preference_categories=("text-attributes",),
                shortcuts=(CommandShortcutDoc("Orca Modifier+F", "readCharAttributesHandler"),),
                command_names=("readCharAttributesHandler", "show_character_attributes"),
                intro=(
                    "Press Orca Modifier+F to present formatting information for the current "
                    f"character. In {guilabels.TEXT_ATTRIBUTES} preferences, you can "
                    "configure which "
                    "attributes are spoken and the order in which they are presented. Orca "
                    "omits attributes whose values are treated as defaults. You can "
                    "customize these selections for individual applications.\n\n"
                    "Press the same key combination twice quickly to open a window showing "
                    "all available attributes for that character, including attributes you "
                    "have not enabled for speech. You can read and copy the details. Press "
                    "Escape to close the window.\n\n"
                    "When flat review is active, these commands use the character at the "
                    "review location. Otherwise, they use the character at the text caret. "
                    "If no formatting information is available, Orca tells you."
                ),
                settings_and_commands=(FeatureLinkDoc("preferences.text-attributes"),),
            ),
            FeatureSectionDoc(
                title="Automatic announcements",
                command_names=("cycle_text_attribute_change_mode",),
                intro=(
                    "Orca can announce formatting changes, such as bold or italic, as you "
                    f"move through text. In {guilabels.SPEECH} preferences, open "
                    f"{guilabels.VERBOSITY} and set {guilabels.TEXT_ATTRIBUTE_CHANGES} "
                    f"to {guilabels.TEXT_ATTRIBUTE_CHANGES_OFF}, "
                    f"{guilabels.TEXT_ATTRIBUTE_CHANGES_EDITABLE}, or "
                    f"{guilabels.TEXT_ATTRIBUTE_CHANGES_ALWAYS}. Say All has "
                    f"a separate {guilabels.TEXT_ATTRIBUTE_CHANGES} setting for "
                    "continuous reading.\n\n"
                    "Automatic announcements are independent of the attribute list used "
                    "by the explicit formatting command.\n\n"
                    f"The {cmdnames.CYCLE_TEXT_ATTRIBUTE_CHANGE_MODE} command switches "
                    "among these announcement modes for the current session.\n\n"
                    "Applications can also expose spelling and grammar errors as text "
                    "attributes, often corresponding to a squiggly underline on screen. "
                    "Orca can announce these errors when you move into the affected text "
                    "or when the application marks a word as misspelled while you type.\n\n"
                    f"The {guilabels.SPEECH_SPEAK_MISSPELLED_WORD_INDICATOR} setting "
                    f"in {guilabels.SPEECH} preferences controls "
                    "these error announcements and is enabled by default. These announcements "
                    "do not require key echo or word echo to be enabled."
                ),
                settings_and_commands=(
                    FeatureLinkDoc("speech.verbosity"),
                    FeatureLinkDoc("preferences.say-all"),
                ),
            ),
            FeatureSectionDoc(
                title="Braille indicators",
                intro=(
                    f"In {guilabels.TEXT_ATTRIBUTES} preferences, you can configure "
                    "which attributes "
                    "are marked in braille, independently of which ones are spoken. "
                    "Enable braille marking for the mistake attribute to mark spelling "
                    "and grammar errors.\n\n"
                    f"In {guilabels.BRAILLE} preferences, open "
                    f"{guilabels.BRAILLE_DISPLAY_SETTINGS} and configure the "
                    f"{guilabels.BRAILLE_TEXT_ATTRIBUTES_INDICATOR.removesuffix(':')} "
                    "indicator. These dots act like underlining on the braille "
                    "display. The same indicator is used for all attributes you have enabled "
                    "for braille; it shows where an attribute is present, rather than which "
                    "attribute it is. If the indicator is set to None, no attribute markers "
                    "are shown."
                ),
                settings_and_commands=(FeatureLinkDoc("preferences.braille.display-settings"),),
            ),
        ),
    )
