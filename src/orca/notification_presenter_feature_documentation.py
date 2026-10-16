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

from . import guilabels
from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for notifications."""

    return FeaturePageDoc(
        page_id="features_notifications",
        title="Notifications",
        link_title="Notifications",
        description="Review recent notification messages.",
        guide_xref="index#information",
        target="reviewing.notifications",
        intro=(
            "Notifications are brief messages from applications or the desktop, such as "
            "new-message alerts or low-battery warnings. Orca keeps recent notifications "
            "it receives so you can review an announcement you missed or interrupted."
        ),
        sections=(
            FeatureSectionDoc(
                title="Reviewing messages",
                intro=(
                    "Use the last notification command to return to the most recent "
                    "message. The previous and next commands move through older and newer "
                    "messages. Each command also reports how long ago the message was "
                    "received."
                ),
                command_names=(
                    "present_last_notification",
                    "present_previous_notification",
                    "present_next_notification",
                    "show_notification_list",
                ),
            ),
            FeatureSectionDoc(
                title="Notification list",
                intro=(
                    "The notification messages list shows recent messages, newest first, "
                    "alongside how long ago each was received. Use Up Arrow and Down Arrow "
                    "to move through the messages.\n\n"
                    f"Use {guilabels.BTN_CLEAR} to remove the notification history "
                    "and close the list. "
                    f"Use {guilabels.BTN_CLOSE} to dismiss the list without clearing it.\n\n"
                    "The history contains notifications received by Orca during the "
                    "current session and is cleared when Orca restarts."
                ),
            ),
        ),
    )
