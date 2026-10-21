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

"""Feature documentation for table navigation."""

from __future__ import annotations

from .help_metadata import (
    FeatureDocumentationDoc,
    FeatureLinkDoc,
    FeatureSectionDoc,
)


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for table navigation."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Table navigation",
                preference_panels=("document_presenter.table-navigation",),
                topic_id="table_navigation",
                command_groups=("documents.table-navigation.commands",),
                target="documents.table-navigation.feature",
                intro=(
                    "Table navigation lets you use Orca commands to move by cell, row, "
                    "and column in tables."
                ),
                details=(
                    "Table navigation is not limited to document content. It can also be used "
                    "in application tables. To move among tables in document content, use "
                    "structural navigation. Table navigation moves within the current table and "
                    "remains available in both browse mode and focus mode.\n\n"
                    "Some tables do not expose their headers to assistive technologies, such as "
                    "a text document or spreadsheet where headers are only visually formatted "
                    "as bold cells. The dynamic-header commands below let you identify those "
                    "headers."
                ),
                settings_and_commands=(
                    FeatureLinkDoc("documents.table-navigation.commands"),
                    FeatureLinkDoc("documents.table-navigation"),
                    FeatureLinkDoc("speech.tables.feature", "Speech table settings"),
                ),
            ),
        ),
    )
