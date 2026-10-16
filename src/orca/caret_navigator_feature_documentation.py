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

"""Feature documentation for caret navigation."""

from __future__ import annotations

from .help_metadata import (
    CommandShortcutDoc,
    FeatureDocumentationDoc,
    FeatureLinkDoc,
    FeatureSectionDoc,
)


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for caret navigation."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Caret navigation",
                preference_panels=("document_presenter.caret-navigation",),
                topic_id="caret_navigation",
                shortcuts=(CommandShortcutDoc("Orca Modifier+F12", "toggle_enabled"),),
                command_groups=("documents.caret-navigation.commands",),
                target="documents.caret-navigation.feature",
                intro=(
                    "Caret navigation lets you move through text by character, word, and "
                    "line, as well as to the beginning and end of lines and documents."
                ),
                settings_and_commands=(
                    FeatureLinkDoc("documents.caret-navigation.commands"),
                    FeatureLinkDoc("documents.caret-navigation"),
                ),
                details=(
                    "Caret navigation is not limited to web content. It is intended to work "
                    "in text objects, including terminals, when the application exposes the "
                    "needed text information to assistive technologies.\n\n"
                    "When browse mode is active, you can use caret navigation commands to "
                    "read and move through document content. If focus mode is active, switch "
                    "to browse mode before using caret navigation commands. In text objects "
                    "where browse mode is not supported, you can manually turn Orca's caret "
                    "navigation on or off with Orca Modifier+F12. This command changes the "
                    "current session across applications; it does not save a preference.\n\n"
                    "Layout mode affects how text from adjacent objects is combined into "
                    "lines. Use the settings below to configure it and automatic focus mode."
                ),
            ),
        ),
    )
