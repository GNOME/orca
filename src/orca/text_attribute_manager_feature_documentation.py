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

from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


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
                command_names=("readCharAttributesHandler", "show_character_attributes"),
                intro=(
                    "The settings and commands below let you choose which formatting "
                    "information Orca presents and inspect the attributes of the current "
                    "character."
                ),
                settings_and_commands=(FeatureLinkDoc("preferences.text-attributes"),),
            ),
            FeatureSectionDoc(
                title="Automatic announcements",
                command_names=("cycle_text_attribute_change_mode",),
                preference_controls=(
                    "speech.text-attribute-changes",
                    "say-all.text-attribute-changes",
                ),
                intro=(
                    "Orca can announce formatting changes, such as bold or italic, as you move "
                    "through text. The settings below control these announcements. "
                    "Applications can also expose spelling and grammar errors as "
                    "text attributes, often corresponding to a squiggly underline on screen. "
                    "Configure those announcements in [[speech.verbosity]]."
                ),
            ),
            FeatureSectionDoc(
                title="Braille indicators",
                intro=(
                    "Braille indicators mark formatting without adding words to the display. "
                    "They are independent of spoken formatting announcements. Configure the "
                    "indicator in [[braille.display-settings.feature]]."
                ),
            ),
        ),
    )
