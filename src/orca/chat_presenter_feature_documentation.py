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

"""Feature documentation for chat."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for chat."""

    return FeaturePageDoc(
        page_id="features_chat",
        title="Chat",
        link_title="Chat",
        description="Follow incoming chat messages and review recent messages.",
        guide_xref="index#interaction",
        target="chat.feature",
        sections=(
            FeatureSectionDoc(
                title="Chat",
                intro=(
                    "Orca can announce incoming messages and review recent messages in "
                    "supported chat applications. The chat-specific settings and commands "
                    "on this page primarily apply to traditional chat applications, such "
                    "as graphical IRC clients."
                ),
                details=(
                    "Many newer communication applications present messages through "
                    "standard interface controls, such as GTK4 lists, or web content in "
                    "Electron applications. Orca presents that content using its general "
                    "application and web support. Message presentation in these applications "
                    "depends on their accessibility support, and the chat-specific settings "
                    "and commands on this page may not apply.\n\n"
                    "These features depend on accessibility information from the application "
                    "or its toolkit that lets Orca recognize messages, their senders, and "
                    "the conversations they belong to. Orca currently recognizes these parts "
                    "of the interface in some chat applications. If the chat features do "
                    "not work in your application, its interface may not yet be recognized, "
                    "even if other parts of the application work well with Orca. Adding "
                    "support may require changes in Orca, the application or its toolkit, "
                    "or both."
                ),
                preference_categories=("chat",),
                command_groups=("commands.chat",),
            ),
        ),
    )
