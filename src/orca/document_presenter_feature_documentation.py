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
                page_id="features_reading_documents_guide",
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
                generate_guide=False,
                sections=(
                    FeatureSectionDoc(
                        title="Browse mode and focus mode",
                        topic_id="browse_mode_and_focus_mode",
                        target="documents.modes.feature",
                        command_groups=("documents.mode-commands",),
                        preference_controls=(
                            "documents.native-focus-mode",
                            "documents.sticky-focus-mode",
                            "documents.caret-focus-mode",
                            "documents.structural-focus-mode",
                        ),
                        intro=(
                            "Navigate document content and interact with controls.\n\n"
                            "Browse mode lets Orca provide navigation for reading documents "
                            "and web content. Focus mode lets the application handle its "
                            "navigation keys instead. Other Orca commands, including table "
                            "navigation and commands using the Orca Modifier, remain available."
                            "\n\n"
                            "Unlike screen readers that use a virtual buffer, Orca does not "
                            "create a separate, off-screen copy of a document or web page for "
                            "browse mode. You navigate the content in the application itself. "
                            "In browse mode, Orca handles navigation commands and updates your "
                            "position within that content."
                        ),
                        settings_and_commands=(
                            FeatureLinkDoc(
                                "documents.mode-commands",
                                "Browse mode and focus mode commands",
                                "Switch between browse mode and focus mode.",
                            ),
                        ),
                        details=(
                            "Orca can switch between modes automatically as you navigate. The "
                            "settings and commands below control automatic switching and let "
                            "you choose a mode explicitly."
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
                links=(
                    FeatureLinkDoc("documents.modes.feature"),
                    FeatureLinkDoc("reviewing.orca-find"),
                ),
                preference_panels=("document_presenter.native-navigation",),
                intro=(
                    "Native navigation refers to keyboard input handled by the application "
                    "rather than Orca. Examples include Tab, Shift+Tab, Page Up, Page Down, "
                    "Enter, and Space."
                ),
                details=(
                    "To search text in a document or web page, use the application's search "
                    "feature. Its search can include text that is not currently visible. The "
                    "application controls the search and navigation to matches; Orca's "
                    "presentation depends on the accessibility information it provides. The "
                    "settings below control presentation of supported application search "
                    "results. For searching visible window contents with flat review, see "
                    "[[reviewing.orca-find]]."
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
