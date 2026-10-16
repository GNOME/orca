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

"""Feature documentation for Where Am I and related object details."""

from __future__ import annotations

from . import cmdnames
from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for learning about the current location."""

    return FeaturePageDoc(
        page_id="features_where_am_i",
        title="Where Am I",
        link_title="Where Am I",
        description="Learn about your current location.",
        guide_xref="index#reviewing",
        target="reviewing.where-am-i",
        intro=(
            "Where Am I presents information about your current location, such as the "
            "focused control, its state, and its position within a group."
        ),
        sections=(
            FeatureSectionDoc(
                title="Basic and detailed Where Am I",
                intro=(
                    "Basic Where Am I repeats information about the current item. Detailed "
                    "Where Am I can add information about containing groups and other "
                    "details. The information provided depends on the type of object and "
                    "your current location. Some objects provide the same information for "
                    "both commands."
                ),
                command_names=("whereAmIBasicHandler", "whereAmIDetailedHandler"),
            ),
            FeatureSectionDoc(
                title="Window and dialog information",
                command_names=(
                    "getTitleHandler",
                    "getStatusBarHandler",
                    "present_default_button",
                ),
            ),
            FeatureSectionDoc(
                title="Other ways to get details",
                intro=(
                    f"{cmdnames.WHERE_AM_I_SELECTION} presents selected text. It can also "
                    "report selected objects, such as files "
                    "or spreadsheet cells.\n\n"
                    "You can also present a spreadsheet cell's formula, an object's "
                    "size and position, or details about the current link."
                ),
                command_names=(
                    "whereAmISelectionHandler",
                    "whereAmILinkHandler",
                    "presentSizeAndPositionHandler",
                    "present_cell_formula",
                ),
            ),
            FeatureSectionDoc(
                title="Related topics",
                links=(FeatureLinkDoc("text-attributes.feature"),),
            ),
        ),
    )
