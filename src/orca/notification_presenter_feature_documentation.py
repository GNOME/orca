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

"""Feature documentation for reviewing notification messages."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for notifications."""

    return FeaturePageDoc(
        page_id="features_notifications",
        title="Notifications",
        link_title="Notifications",
        description="Review recent notification messages.",
        guide_xref="index#interaction",
        target="reviewing.notifications",
        sections=(
            FeatureSectionDoc(
                title="Notifications",
                intro=(
                    "Notifications are brief messages from applications or the desktop, such as "
                    "new-message alerts or low-battery warnings. Orca keeps recent "
                    "notifications it receives so you can review an announcement you missed or "
                    "interrupted. This history is cleared when Orca restarts."
                ),
                command_names=(
                    "present_last_notification",
                    "present_previous_notification",
                    "present_next_notification",
                    "show_notification_list",
                ),
            ),
        ),
    )
