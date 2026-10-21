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

"""Feature documentation for object navigation."""

from __future__ import annotations

from .help_metadata import FeatureDocumentationDoc, FeatureLinkDoc, FeatureSectionDoc


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns feature documentation for object navigation."""

    return FeatureDocumentationDoc(
        sections=(
            FeatureSectionDoc(
                title="Object navigation",
                topic_id="object_navigation",
                command_groups=("commands.object-navigation",),
                target="reviewing.object-navigation",
                intro=(
                    "Object navigation lets you move through the accessible object hierarchy "
                    "without moving application focus or the caret. It is not limited to "
                    "objects visible on screen."
                ),
                details=(
                    "Applications provide objects in a hierarchy: a parent contains child "
                    "objects, and children with the same parent are siblings. For example, a "
                    "toolbar can contain several buttons. Object navigation uses a separate "
                    "navigator focus; the commands below explore and interact with the object "
                    "at that location."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "commands.object-navigation",
                        "Object navigation commands",
                        "Move through the accessible object hierarchy.",
                    ),
                ),
            ),
        ),
    )
