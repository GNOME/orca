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
    CommandShortcutDoc,
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
                shortcuts=(
                    CommandShortcutDoc("Orca Modifier+Shift+T", "table_navigator_toggle_enabled"),
                ),
                command_groups=("documents.table-navigation.commands",),
                target="documents.table-navigation.feature",
                intro=(
                    "Table navigation lets you use Orca commands to move by cell, row, "
                    "and column in tables."
                ),
                details=(
                    "Table navigation is not limited to document content. It can also be used "
                    "in application tables. To move among tables in document content, use "
                    "structural navigation commands for tables. Table navigation commands "
                    "move within the current table.\n\n"
                    "Table navigation commands are enabled by default. Unlike caret navigation "
                    "and structural navigation commands, table navigation commands are not "
                    "suspended when Orca switches between browse mode and focus mode. You can "
                    "turn table navigation on or off with Orca Modifier+Shift+T."
                    "\n\n"
                    "Orca's dynamic headers feature lets you mark the current row or column "
                    "as headers for the table. Orca can then present those cells as row or "
                    "column headers as you navigate. This is useful when a table does not "
                    "expose its headers to assistive technologies, such as a text document "
                    "or spreadsheet where the headers are only visually formatted as bold "
                    "cells. Headers are announced when they change, rather than "
                    "repeated for every cell with the same header.\n\n"
                    "To set column headers, move to the row that contains the column "
                    "headers, then use the command to set dynamic column headers. To set "
                    "row headers, move to the column that contains the row headers, then "
                    "use the command to set dynamic row headers.\n\n"
                    "To clear dynamic headers, press the shortcut you used to set them "
                    "twice quickly."
                ),
                settings_and_commands=(
                    FeatureLinkDoc("documents.table-navigation.commands"),
                    FeatureLinkDoc("documents.table-navigation"),
                    FeatureLinkDoc("speech.tables.feature", "Speech table settings"),
                ),
            ),
        ),
    )
