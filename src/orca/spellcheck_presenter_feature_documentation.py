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
        description="Review spelling errors and suggestions in supported spell checkers.",
        guide_xref="index#reading",
        target="spell-check.feature",
        sections=(
            FeatureSectionDoc(
                title="Spell checking",
                intro=(
                    "Orca can present spelling errors and suggestions while you use "
                    "a supported application's spell checker."
                ),
                details=(
                    "These features depend on accessibility information from the application "
                    "or its toolkit that lets Orca recognize the misspelled word, suggestions "
                    "list, and other parts of the spell-checking dialog. Orca currently "
                    "recognizes these parts of the interface in some applications. If these "
                    "features do not work in your application's spell checker, its interface "
                    "may not yet be recognized, even if other parts of the application work "
                    "well with Orca. Adding support may require changes in Orca, the "
                    "application or its toolkit, or both.\n\n"
                    "Even when an application's spell-checking dialog is not supported, Orca "
                    "can announce misspelled words as you navigate or type. The application's "
                    "spelling-error indicators, usually red squiggly underlines, must be "
                    "enabled and exposed as accessibility text attributes. Announcements "
                    "while typing also require the application to report changes to those "
                    "attributes through accessibility events. Configure these announcements "
                    "in [[speech.verbosity]]."
                ),
                preference_categories=("spell-check",),
            ),
        ),
    )
