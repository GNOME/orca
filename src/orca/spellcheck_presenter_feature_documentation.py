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

"""Feature documentation for spell checking."""

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns the combined spell-checking topic."""

    return FeaturePageDoc(
        page_id="features_spell_check",
        title="Spell checking",
        link_title="Spell checking",
        description="Hear spelling errors and suggestions in supported spell checkers.",
        guide_xref="index#interaction",
        target="spell-check.feature",
        sections=(
            FeatureSectionDoc(
                title="Spell checking",
                intro=(
                    "Orca can present spelling errors and suggestions while you use "
                    "a supported application's spell checker."
                ),
                details=(
                    "Orca needs to identify the misspelled word, suggestions list, and "
                    "other parts of the application's spell checker to present this information."
                ),
                preference_categories=("spell-check",),
            ),
        ),
    )
