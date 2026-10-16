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

"""Feature documentation for getting started with Orca."""

from __future__ import annotations

from . import guilabels
from .help_metadata import (
    FeatureDocumentationDoc,
    FeaturePageDoc,
    FeatureSectionDoc,
)


def get_feature_documentation() -> FeatureDocumentationDoc:
    """Returns introductory and configuration documentation."""

    return FeatureDocumentationDoc(
        pages=(_get_introduction_documentation(), _get_configuration_documentation()),
    )


def _get_introduction_documentation() -> FeaturePageDoc:
    """Returns documentation for starting Orca and finding help."""

    return FeaturePageDoc(
        page_id="introduction",
        title="Starting and stopping Orca",
        link_title="Starting and stopping Orca",
        description="Start and stop Orca using your desktop or the command line.",
        guide_xref="index#getting_started",
        target="screen-reader.introduction",
        sections=(
            FeatureSectionDoc(
                title="Starting Orca",
                intro=(
                    "Use your desktop's accessibility settings to enable its screen "
                    "reader or arrange for Orca to start automatically. In GNOME, the "
                    "default shortcut to turn the screen reader on or off is Alt+Super+S.\n\n"
                    "You can also start Orca by running `orca` in a terminal or your "
                    "desktop's Run dialog."
                ),
            ),
            FeatureSectionDoc(
                title="Stopping Orca",
                intro=(
                    "If your desktop manages Orca as a service, use its screen reader "
                    "controls to turn Orca off. The quit command is for an Orca instance "
                    "started as a regular application. Using it for a systemd-managed "
                    "instance can cause the service to restart Orca."
                ),
                command_names=("shutdownHandler",),
            ),
            FeatureSectionDoc(
                title="Command-line options",
                intro=(
                    "These commands display information or manage extension approval without "
                    "starting Orca:\n\n"
                    "- `orca --help`: Display the available options and their usage.\n"
                    "- `orca --version`: Display the installed version of Orca.\n"
                    "- `orca -l` or `orca --list-apps`: List known running applications.\n"
                    "- `orca --approve-extension FILENAME`: Approve a user extension for loading.\n"
                    "- `orca --revoke-extension FILENAME`: Revoke a user extension's approval.\n\n"
                    "These commands start Orca:\n\n"
                    "- `orca -p NAME` or `orca --profile NAME`: Start Orca with the named "
                    "settings profile.\n"
                    "- `orca -s` or `orca --setup`: Start Orca and open the Preferences window. "
                    "If Orca is already running, open its Preferences window instead.\n"
                    "- `orca --speech-system NAME`: Start Orca with the selected speech system. "
                    "The supported names are `speechdispatcherfactory` for Speech Dispatcher "
                    "(the default) and `spiel` for Spiel. The selected backend must be installed "
                    "and available.\n"
                    "- `orca -r` or `orca --replace`: Start Orca, replacing an instance "
                    "started as an application.\n"
                    "- `orca --debug`: Start Orca with verbose debugging enabled, saving the "
                    "log to a file with a timestamped filename.\n"
                    "- `orca --debug-file FILE`: Start Orca with verbose debugging enabled, "
                    "saving the log to the specified file.\n\n"
                    "If Orca is already running as an application, add `-r` or `--replace` "
                    "when starting it with debugging, a different speech system, or a "
                    "different profile. For example, "
                    "`orca --replace --debug`. If your desktop manages Orca as a service, use "
                    "the desktop's screen reader controls to stop it before starting Orca "
                    "with these options, rather than using `--replace`."
                ),
            ),
        ),
    )


def _get_configuration_documentation() -> FeaturePageDoc:
    """Returns documentation for opening and using preferences."""

    return FeaturePageDoc(
        page_id="preferences",
        title="Preferences",
        link_title="Preferences",
        description="Open preferences and save your settings.",
        guide_xref="index#getting_started",
        target="screen-reader.configuration",
        topics_title="Settings categories",
        sections=(
            FeatureSectionDoc(
                title="Opening preferences",
                target="screen-reader.opening-preferences",
                intro=(
                    "Use the commands below to open the global or application Preferences window."
                ),
                command_names=(
                    "preferencesSettingsHandler",
                    "appPreferencesSettingsHandler",
                ),
                details=(
                    "You can also run `orca -s` or `orca --setup` in a terminal or your "
                    "desktop's Run dialog to start Orca and open the Preferences window. "
                    "If Orca is already running, this opens its Preferences window instead."
                    "\n\n"
                    "Application preferences override global preferences for that "
                    "application. For example, you can use different speech settings in "
                    "your browser and text editor."
                ),
            ),
            FeatureSectionDoc(
                title="Changing and saving settings",
                target="screen-reader.saving-preferences",
                intro=(
                    "Settings are grouped into categories in the side panel on the left. "
                    "Use Up Arrow and Down Arrow to choose a category. As you change "
                    "categories, the panel on the right displays that category's settings. "
                    "Press Tab to move into that panel.\n\n"
                    "Some categories contain subcategories. Use Up Arrow and Down Arrow "
                    "to choose one, then Right Arrow or Enter to open it. Press Left Arrow "
                    "or Escape to return to the subcategory list. From the main settings "
                    "list, press Left Arrow to return to the sidebar. Use Tab and Shift+Tab "
                    "to move among controls.\n\n"
                    f"The {guilabels.MENU_BUTTON_OPTIONS} menu button is at the top of "
                    "the left panel. Press F10 "
                    f"to move to {guilabels.MENU_BUTTON_OPTIONS}. You can also reach it "
                    "from the sidebar with "
                    "Shift+Tab. Press Enter or Space to open the menu. "
                    f"Use the {guilabels.MENU_BUTTON_OPTIONS} menu's apply action to "
                    "save your changes without "
                    "closing the window, or its save action to save and close it.\n\n"
                    f"The {guilabels.MENU_BUTTON_OPTIONS} menu's {guilabels.BTN_CANCEL} action "
                    "closes the window and discards "
                    "unsaved preference edits. Changes already applied remain saved."
                    "\n\n"
                    "Preferences is a window, not a dialog: Escape does not close it. "
                    f"Close it with Alt+F4 or the {guilabels.MENU_BUTTON_OPTIONS} menu. "
                    "If you press Alt+F4 with "
                    "unsaved changes, Orca prompts you to save them, close without saving, "
                    "or cancel and return to preferences. In global preferences, you can "
                    "also save the changes as a new profile."
                ),
            ),
        ),
    )
