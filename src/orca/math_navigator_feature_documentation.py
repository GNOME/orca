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

"""Feature documentation for math navigation."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for math navigation."""

    return FeaturePageDoc(
        page_id="features_math_navigation",
        title="Math navigation",
        link_title="Math navigation",
        description="Explore mathematical expressions using MathCAT.",
        guide_xref="index#reading",
        target="math-navigation.feature",
        sections=(
            FeatureSectionDoc(
                title="Math navigation",
                intro="Explore mathematical expressions.",
                details=(
                    "Orca uses [MathCAT](https://daisy.github.io/MathCAT/) to provide speech, "
                    "braille, and navigation for mathematical expressions written in MathML.\n\n"
                    "Orca's math navigation commands and default shortcuts are intended to "
                    "follow MathCAT's. The command and navigation-mode descriptions below are "
                    "adapted from MathCAT's documentation. Consult the "
                    "[MathCAT user guide](https://daisy.github.io/MathCAT/users.html) for more "
                    "information."
                ),
                preference_panels=("math_presenter.math-presentation",),
                command_groups=("commands.math-navigation",),
            ),
        ),
    )
