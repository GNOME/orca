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

"""Feature documentation for reviewing screen contents."""

from __future__ import annotations

from .help_metadata import (
    FeatureDocumentationDoc,
    FeatureLinkDoc,
    FeaturePageDoc,
    FeatureSectionDoc,
)


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for flat review and related features."""

    return FeatureDocumentationDoc(
        pages=(
            FeaturePageDoc(
                page_id="features_reviewing_objects",
                title="Reviewing and interacting with objects",
                link_title="Reviewing and interacting with objects",
                description="Review contents and objects independently of focus.",
                guide_xref="",
                intro=(
                    "These topics describe ways to review visible contents and explore "
                    "accessible objects without moving application focus or the caret."
                ),
                sections_as_pages=True,
                topics_guide_xref="index#reviewing",
                generate_guide=False,
                sections=(
                    FeatureSectionDoc(
                        title="Flat review",
                        preference_categories=("flat-review",),
                        topic_id="flat_review",
                        command_groups=("commands.flat-review",),
                        target="reviewing.flat-review",
                        intro=(
                            "Flat review lets you examine the visible contents of the active "
                            "window independently of focus and the caret. Orca treats the "
                            "window as a two-dimensional sequence of lines, items, and "
                            "characters."
                        ),
                        details=(
                            "Use the flat review navigation commands to begin reviewing "
                            "the window. Off-screen content is not included.\n\n"
                            "The review location and the application's caret are separate. "
                            "You can configure when review follows focus and caret changes, "
                            "how changes at the review location are presented, or use commands "
                            "to move one location to the other. The settings and commands "
                            "below describe these options.\n\n"
                            "Keeping the review location independent does not freeze the "
                            "window's content. Text can still change or scroll out of view, "
                            "so the exact position may no longer be available. Orca retains "
                            "one review location, rather than a separate location for each "
                            "window. Reviewing another window replaces the previous one."
                        ),
                        settings_and_commands=(
                            FeatureLinkDoc(
                                "commands.flat-review",
                                "Flat review commands",
                                "Navigate by line, item, character, and object.",
                            ),
                            FeatureLinkDoc(
                                "preferences.flat-review",
                                "",
                                "Configure how flat review follows focus and presents updates.",
                            ),
                            FeatureLinkDoc(
                                "reviewing.orca-find",
                                "Orca Find",
                                "Search visible contents in the active window.",
                            ),
                        ),
                    ),
                    FeatureSectionDoc(
                        title="Orca Find",
                        topic_id="orca_find",
                        command_groups=("commands.find",),
                        target="reviewing.orca-find",
                        intro=(
                            "Orca Find searches visible contents in the active window. When "
                            "there is a match, Orca activates flat review and moves the review "
                            "location to the matching item or text."
                        ),
                        details=(
                            "Finding a match does not move application focus or reposition the "
                            "caret. To search document content beyond the visible portion, use "
                            "the application's search feature. See "
                            "[[documents.native-navigation.feature]] for application search and "
                            "Orca's presentation of its results."
                        ),
                        links=(FeatureLinkDoc("documents.native-navigation.feature"),),
                        settings_and_commands=(
                            FeatureLinkDoc(
                                "commands.find",
                                "Find commands",
                                "Open the Find dialog and move to the next or previous match.",
                            ),
                            FeatureLinkDoc(
                                "reviewing.flat-review",
                                "Flat review",
                                "Review visible contents in the active window.",
                            ),
                        ),
                    ),
                    FeatureSectionDoc(
                        title="Object navigation",
                        topic_id="object_navigation",
                        include_target="reviewing.object-navigation",
                    ),
                    FeatureSectionDoc(
                        title="Mouse review and clicking",
                        topic_id="mouse_review",
                        include_target="reviewing.mouse-review",
                    ),
                ),
            ),
        ),
    )
