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

from . import cmdnames, guilabels
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
                title="Reviewing and Exploring Objects",
                link_title="Reviewing and exploring objects",
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
                            "Any flat review command starts reviewing the visible contents; "
                            "off-screen content is not included. Orca refreshes the review "
                            "context as the window, text, or caret changes.\n\n"
                            f"{guilabels.FLAT_REVIEW} preferences control whether the review "
                            "location "
                            "follows focus and caret changes. Using application navigation "
                            "keys leaves flat review. You can also toggle flat review off "
                            "and back on to rebuild the context.\n\n"
                            "The home position is the beginning of the window's content; "
                            "the end position is its last item. Bottom left is the start "
                            f"of the last line. {cmdnames.FLAT_REVIEW_SHOW_CONTENTS} opens "
                            "the entire "
                            "review content in a text window."
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
                            "The Find dialog lets you enter text to search for, choose whether "
                            "to start from the current location or the top of the window, match "
                            "case, match whole words, search backward, and wrap around. After "
                            "you perform a search, use the Find commands to move to the next "
                            "or previous match without reopening the dialog.\n\n"
                            "If you have not searched yet, Find Next and Find Previous open "
                            "the dialog. Search text is interpreted as a regular expression; "
                            "characters such as a period or an asterisk have special meanings. "
                            "Use a backslash before a special character to match it literally.\n\n"
                            "Finding a match does not move application focus or reposition the "
                            "caret."
                        ),
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
                        title="Mouse review",
                        topic_id="mouse_review",
                        include_target="reviewing.mouse-review",
                    ),
                ),
            ),
        ),
    )
