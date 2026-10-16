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

from . import guilabels
from .help_metadata import CommandShortcutDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for math navigation."""

    return FeaturePageDoc(
        page_id="features_math_navigation",
        title="Math navigation",
        link_title="Math navigation",
        description="Read and explore mathematical expressions.",
        guide_xref="index#reading",
        target="math-navigation.feature",
        sections=(
            FeatureSectionDoc(
                title="Math navigation",
                intro="Explore mathematical expressions and their component parts.",
                details=(
                    "Math navigation requires MathCAT, a library for presenting mathematical "
                    "expressions. To start, move to an expression, such as an equation, "
                    "fraction, or formula, and press Orca Modifier+Alt+M. "
                    "Press Escape to leave math navigation.\n\n"
                    "An expression contains related parts, such as a fraction's numerator "
                    "and denominator. Movement commands explore these parts; zooming in "
                    "explores smaller parts and zooming out returns to larger structures.\n\n"
                    f"The {guilabels.MATH_NAV_MODE.removesuffix(':')} setting selects "
                    f"granularity: {guilabels.MATH_NAV_MODE_ENHANCED} for "
                    f"meaningful subexpressions, {guilabels.MATH_NAV_MODE_SIMPLE} "
                    f"for smaller pieces, and {guilabels.MATH_NAV_MODE_CHARACTER} "
                    "for individual characters. The granularity commands switch among "
                    "these modes while you explore. Read commands speak the selected part; "
                    "Describe commands give an outline of its structure. Speech mode "
                    "chooses which of these presentations follows a move. In a matrix, "
                    "cells are the entries arranged in rows and "
                    "columns.\n\n"
                    "The Where am I commands in math navigation describe your location "
                    "within the expression, rather than your location in the application.\n\n"
                    "You can set numbered place markers to return to, read, or describe "
                    "parts of an expression."
                ),
                preference_panels=("math_presenter.math-presentation",),
                command_groups=("commands.math-navigation",),
                shortcuts=(CommandShortcutDoc("Orca Modifier+Alt+M", "math_enter"),),
            ),
        ),
    )
