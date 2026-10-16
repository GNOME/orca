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

"""Feature documentation for document presentation."""

from __future__ import annotations

from . import guilabels
from .help_metadata import (
    FeatureDocumentationDoc,
    FeatureLinkDoc,
    FeaturePageDoc,
    FeatureSectionDoc,
)


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for reading documents and web pages."""

    return FeatureDocumentationDoc(
        pages=(
            FeaturePageDoc(
                page_id="features_reading_documents",
                title="Reading documents and web pages",
                link_title="Reading documents and web pages",
                description="Read documents, web pages, and interactive content.",
                guide_xref="",
                target="documents.reading",
                intro=(
                    "These topics describe ways to read and navigate documents and web pages "
                    "with Orca."
                ),
                sections_as_pages=True,
                preference_category="documents",
                topics=("math-navigation.feature",),
                topics_guide_xref="index#reading",
                sections=(
                    FeatureSectionDoc(
                        title="Browse mode and focus mode",
                        topic_id="browse_mode_and_focus_mode",
                        command_groups=("documents.mode-commands",),
                        intro=(
                            "When reading document content, Orca uses two modes: browse mode "
                            "and focus mode.\n\n"
                            "Browse mode lets Orca provide navigation for reading documents "
                            "and web content. Focus mode lets the application handle its "
                            "navigation keys instead. Other Orca commands, including table "
                            "navigation and commands using the Orca Modifier, remain available."
                        ),
                        settings_and_commands=(
                            FeatureLinkDoc(
                                "documents.mode-commands",
                                "Browse mode and focus mode commands",
                                "Switch between browse mode and focus mode.",
                            ),
                            FeatureLinkDoc("documents.native-navigation"),
                            FeatureLinkDoc("documents.caret-navigation"),
                            FeatureLinkDoc("documents.structural-navigation"),
                        ),
                        details=(
                            "Orca can switch to focus mode automatically when navigation lands "
                            "on an interactive widget. You can enable or disable automatic "
                            "focus mode separately for native navigation, caret navigation, "
                            f"and structural navigation in {guilabels.DOCUMENTS} preferences.\n\n"
                            "Sticky modes override automatic switching. Sticky focus mode "
                            "keeps Orca in focus mode until you explicitly change modes. "
                            "Sticky browse mode keeps Orca in browse mode until you explicitly "
                            "change modes."
                            "\n\n"
                            "Some web applications, including desktop applications built with "
                            "the Electron web framework, start in sticky focus mode so their "
                            "own keyboard interactions work. "
                            f"Configure this with {guilabels.AUTO_STICKY_FOCUS_MODE} "
                            f"in the {guilabels.NATIVE_NAVIGATION} section of "
                            f"{guilabels.DOCUMENTS} preferences."
                        ),
                    ),
                    FeatureSectionDoc(
                        title="Caret navigation",
                        topic_id="caret_navigation",
                        include_target="documents.caret-navigation.feature",
                    ),
                    FeatureSectionDoc(
                        title="Structural navigation",
                        topic_id="structural_navigation",
                        include_target="documents.structural-navigation.feature",
                    ),
                    FeatureSectionDoc(
                        title="Table navigation",
                        topic_id="table_navigation",
                        include_target="documents.table-navigation.feature",
                    ),
                    FeatureSectionDoc(
                        title="Native navigation",
                        topic_id="native_navigation",
                        include_target="documents.native-navigation.feature",
                    ),
                    FeatureSectionDoc(
                        title="Live regions",
                        topic_id="live_regions",
                        include_target="documents.live-regions.feature",
                    ),
                ),
            ),
        ),
        sections=(
            FeatureSectionDoc(
                title="Native navigation",
                topic_id="native_navigation",
                target="documents.native-navigation.feature",
                preference_panels=("document_presenter.native-navigation",),
                intro=(
                    "Native navigation refers to keyboard input handled by the application "
                    "rather than Orca. Examples include Tab, Shift+Tab, Page Up, Page Down, "
                    "Enter, and Space."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "documents.native-navigation",
                        "",
                        "Configure focus-mode, find-result, and page-load behavior.",
                    ),
                ),
            ),
        ),
    )
