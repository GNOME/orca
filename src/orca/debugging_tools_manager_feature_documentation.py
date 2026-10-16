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

"""Feature documentation for troubleshooting orca."""

from __future__ import annotations

from .help_metadata import FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for troubleshooting orca."""

    return FeaturePageDoc(
        page_id="features_debugging",
        title="Troubleshooting Orca",
        link_title="Troubleshooting Orca",
        description="Collect information for troubleshooting.",
        guide_xref="index#troubleshooting",
        target="debugging.feature",
        sections=(
            FeatureSectionDoc(
                title="Troubleshooting Orca",
                intro=(
                    "Start Orca with verbose debugging enabled using `orca --debug`, or "
                    "`orca --debug-file FILE` to choose the log destination. If Orca is already "
                    "running as an application, add `--replace`, for example "
                    "`orca --replace --debug`. If your desktop manages Orca as a service, "
                    "stop it using the desktop's screen reader controls first.\n\n"
                    "Debug logs contain detailed information about "
                    "your actions and interactions with applications while logging is enabled, "
                    "including application content. Review logs for private information before "
                    "sharing them."
                ),
                command_groups=("commands.debugging-tools",),
                details=(
                    "The debug-level command cycles through all messages, informational "
                    "messages, warnings, severe errors, and off. The cache command clears "
                    "stored accessibility information for the current application so Orca "
                    "can request fresh information from it."
                ),
            ),
        ),
    )
