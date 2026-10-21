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

from .help_metadata import (
    FeatureLinkDoc,
    FeaturePageDoc,
    FeatureSectionDoc,
)


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for troubleshooting orca."""

    return FeaturePageDoc(
        page_id="features_debugging",
        title="Troubleshooting and getting help",
        link_title="Troubleshooting and getting help",
        description="Troubleshoot problems, get help, and report bugs or request features.",
        guide_xref="index#troubleshooting",
        target="debugging.feature",
        sections=(
            FeatureSectionDoc(
                title="Checking whether Orca can access an application",
                intro=(
                    "If Orca does not present an application, leave that application running "
                    "and run `orca -l` in a terminal. This lists the applications known to "
                    "AT-SPI, the accessibility service Orca uses."
                ),
                details=(
                    "If the application is not listed, Orca has no way of knowing it exists. "
                    "The application is not exposing an accessibility tree or accessibility "
                    "events to Orca, so Orca cannot present its content or respond to changes "
                    "within it.\n\n"
                    "An application being listed does not guarantee that all of its content "
                    "is accessible, but it confirms that AT-SPI knows about the application."
                ),
            ),
            FeatureSectionDoc(
                command_names=("clear_atspi_app_cache",),
                title="Refreshing an application's accessibility information",
                intro=(
                    "AT-SPI caches accessibility information about an application's objects. "
                    "It clears affected cached information in response to accessibility events "
                    "from the application or its toolkit. Normally, Orca should receive current "
                    "information without manual intervention."
                ),
                links=(FeatureLinkDoc("preferences.commands"),),
            ),
            FeatureSectionDoc(
                title="Testing speech output",
                intro=(
                    "If Orca is not speaking, test its speech system independently from "
                    "a terminal. For Speech Dispatcher, run "
                    '`spd-say "This is a speech test."`. For Spiel, run '
                    '`spiel "This is a speech test."`. You may need to install the '
                    "corresponding command-line tool first."
                ),
                details=(
                    "If the command does not produce speech either, the problem is with "
                    "the speech system, its synthesizer, or your audio output, rather than "
                    "Orca alone. If it does produce speech, check Orca's selected speech "
                    "system, synthesizer, and voice: the command may use different defaults. "
                    "Both tools let you specify a voice and other options. Run "
                    "`spd-say --help` or `spiel --help` for details."
                ),
            ),
            FeatureSectionDoc(
                title="If Orca remains unresponsive",
                intro=(
                    "If Orca does not respond in other applications either, restart it using "
                    "your desktop's screen reader controls. If you started Orca as a regular "
                    "application, you can instead run `orca --replace`. See "
                    "[[screen-reader.introduction]] for the distinction between these ways of "
                    "running Orca."
                ),
                links=(
                    FeatureLinkDoc("screen-reader.introduction"),
                    FeatureLinkDoc(
                        "screen-reader.settings-backup",
                        summary=(
                            "Back up your settings before testing with defaults, "
                            "then restore them afterward."
                        ),
                    ),
                ),
            ),
            FeatureSectionDoc(
                title="Collecting debugging information",
                intro=(
                    "Start Orca with verbose debugging enabled using `orca --debug`, or "
                    "`orca --debug-file FILE` to choose the log destination. If Orca is already "
                    "running as an application, add `--replace`, for example "
                    "`orca --replace --debug`. If your desktop manages Orca as a service, "
                    "stop it using the desktop's screen reader controls first.\n\n"
                    "Debug logs can become very large. If possible, limit your activity "
                    "while logging to the steps needed to demonstrate the problem.\n\n"
                    "Debug logs contain detailed information about "
                    "your actions and interactions with applications while logging is enabled, "
                    "including application content. Review logs for private information before "
                    "sharing them."
                ),
                command_groups=("commands.debugging-tools",),
            ),
            FeatureSectionDoc(
                title="Getting help and reporting problems",
                intro=(
                    "The Orca mailing list is where most Orca-related communication "
                    "takes place. Its knowledgeable, helpful user community shares "
                    "advice and discusses problems and ideas. The list archive is "
                    "searchable, so you can look for earlier discussions of your question.\n\n"
                    "You can file bug reports and feature requests in Orca's GitLab "
                    "project. For a bug report, include your Orca version, the affected "
                    "application and its version, the steps to reproduce the problem, "
                    "and what you expected compared with what happened. Include the "
                    "results of any troubleshooting steps you tried."
                ),
                links=(
                    FeatureLinkDoc(
                        "https://www.freelists.org/list/orca",
                        label="Orca mailing list",
                        summary="Subscribe to the list or search its archive.",
                    ),
                    FeatureLinkDoc(
                        "https://gitlab.gnome.org/GNOME/orca",
                        label="Orca on GitLab",
                        summary="Report bugs and request features.",
                    ),
                ),
            ),
        ),
    )
