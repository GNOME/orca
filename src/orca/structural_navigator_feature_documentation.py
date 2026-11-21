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

"""Feature documentation for structural navigation."""

from __future__ import annotations

from . import guilabels
from .help_metadata import (
    FeatureDocumentationDoc,
    FeatureLinkDoc,
    FeatureSectionDoc,
)


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for structural navigation."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Structural navigation",
                preference_panels=("document_presenter.structural-navigation",),
                topic_id="structural_navigation",
                command_groups=("documents.structural-navigation.commands",),
                target="documents.structural-navigation.feature",
                intro=(
                    "Structural navigation lets you move to the next or previous object of a "
                    "chosen type, or bring up a list of matching objects. Types include "
                    "headings, links, buttons and other interactive controls, lists, landmarks, "
                    "tables, and large text blocks."
                ),
                settings_and_commands=(
                    FeatureLinkDoc("documents.structural-navigation.commands"),
                    FeatureLinkDoc("documents.structural-navigation"),
                ),
                details=(
                    "Use the list commands below to open a dialog containing matching objects, "
                    "such as headings or links. Use Up Arrow and Down Arrow to choose an item, "
                    "then Tab to reach the dialog's buttons.\n\n"
                    f'"{guilabels.BTN_JUMP_TO}" closes the list and moves to the chosen object '
                    "without activating it. "
                    f'"{guilabels.ACTIVATE}" performs its action, such as following a link '
                    "or pressing a button. This button is unavailable if the object does not "
                    "support an action.\n\n"
                    "Pressing Enter while the list has focus activates the chosen object if "
                    "it supports an action; otherwise, it jumps to the object. "
                    f'Press Escape or use "{guilabels.BTN_CANCEL}" to close the list without '
                    "moving to or activating an object.\n\n"
                    "Structural navigation is not limited to web content. It can be used in "
                    "document content and in application user interfaces. It relies on the "
                    "accessible collections interface, an API that lets Orca search the "
                    "accessibility tree efficiently. This tree is the structured view of an "
                    "application's objects provided to assistive technologies. Applications and "
                    "toolkits that do not support this interface, or omit objects from the "
                    "tree, will not work as expected.\n\n"
                    "When browse mode is active, structural navigation can move among "
                    "interactive widgets and other document elements. If focus mode is active, "
                    "switch to browse mode before using structural navigation in document "
                    "content. The settings and commands below control its scope and behavior."
                ),
                links=(
                    FeatureLinkDoc(
                        "documents.live-regions.feature",
                        summary="Includes the structural navigation commands for live regions.",
                    ),
                ),
            ),
        ),
    )
