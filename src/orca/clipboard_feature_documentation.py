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

"""Feature documentation for clipboard."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for clipboard."""

    return FeaturePageDoc(
        page_id="features_clipboard",
        title="Clipboard",
        link_title="Clipboard",
        description="Present the contents of the system clipboard.",
        guide_xref="index#interaction",
        target="clipboard.feature",
        sections=(
            FeatureSectionDoc(
                title="Clipboard",
                intro="Orca can present text copied to the system clipboard.",
                details=(
                    "Orca uses the desktop clipboard service when possible, such as Klipper "
                    "or GPaste. If no supported service is available, Orca falls back to GTK "
                    "clipboard support, which may be limited on Wayland."
                ),
                command_groups=("commands.clipboard",),
            ),
        ),
    )
