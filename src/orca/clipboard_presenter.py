# Utilities related to the clipboard
#
# Copyright 2024-2025 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Utilities related to the clipboard."""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import (
    clipboard_manager,
    clipboard_presenter_command_definitions,
    dbus_service,
    debug,
    guilabels,
    input_event,
    input_event_manager,
    messages,
    presentation_manager,
    script_manager,
)
from .ax_utilities import AXUtilities
from .extension import Extension

if TYPE_CHECKING:
    from .command import Command
    from .scripts import default


class ClipboardPresenter(Extension):
    """Manages clipboard-related functionality."""

    GROUP_LABEL = guilabels.KB_GROUP_CLIPBOARD

    def __init__(self) -> None:
        self._event_listener: Atspi.EventListener = Atspi.EventListener.new(self._listener)
        self._last_clipboard_update_text: str = ""
        self._last_clipboard_update_time: float = time.time()
        super().__init__()

    def _get_commands(self) -> list[Command]:
        return clipboard_presenter_command_definitions.get_commands(self)

    @dbus_service.command
    def present_clipboard_contents(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the clipboard contents."""

        tokens = [
            "CLIPBOARD PRESENTER: present_clipboard_contents. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = clipboard_manager.get_manager()
        if not manager.is_ready():
            msg = "CLIPBOARD PRESENTER: Cannot present contents, no active manager."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        contents = manager.get_text()
        if not contents or len(contents) > 5000:
            contents = messages.character_count(len(contents))
        presentation_manager.get_manager().present_message(
            messages.CLIPBOARD_CONTAINS % contents,
            contents,
        )
        return True

    def activate(self) -> None:
        """Activates the presenter."""

        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Activating", True)
        self._event_listener.register("object:text-changed")
        clipboard_manager.get_manager().connect(self._present_clipboard_contents_change)
        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Activated", True)

    def deactivate(self) -> None:
        """Deactivates the presenter."""

        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Deactivating", True)
        self._event_listener.deregister("object:text-changed")
        clipboard_manager.get_manager().disconnect()
        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Deactivated", True)

    def is_clipboard_text_changed_event(self, event: Atspi.Event) -> bool:
        """Returns True if event is a text changed event associated with the clipboard."""

        if not event.type.startswith("object:text-changed"):
            return False

        if not (AXUtilities.is_editable(event.source) or AXUtilities.is_terminal(event.source)):
            return False

        manager = input_event_manager.get_manager()
        if (
            not manager.last_event_was_command()
            or manager.last_event_was_undo()
            or manager.last_event_was_backspace()
        ):
            return False

        if "delete" in event.type and manager.last_event_was_paste():
            return False

        contents = clipboard_manager.get_manager().get_text()
        if not contents:
            return False

        # Some applications send multiple text insertion events for part of a given paste.
        words_match = bool(re.search(r"\w", event.any_data)) == bool(re.search(r"\w", contents))
        return words_match and contents.startswith(event.any_data.rstrip())

    def _present_clipboard_contents_change(self, string: str) -> None:
        """Presents the clipboard contents change."""

        tokens = ["CLIPBOARD PRESENTER: Contents changed to: '", string, "'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if (
            string == self._last_clipboard_update_text
            and time.time() - self._last_clipboard_update_time < 1
        ):
            msg = "CLIPBOARD PRESENTER: Not presenting change: likely duplicate."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._last_clipboard_update_text = string
        self._last_clipboard_update_time = time.time()
        script = script_manager.get_manager().get_active_script()
        if script is None:
            return

        manager = input_event_manager.get_manager()
        if manager.last_event_was_cut():
            presentation_manager.get_manager().present_message(
                messages.CLIPBOARD_CUT_FULL,
                messages.CLIPBOARD_CUT_BRIEF,
            )
            return

        if manager.last_event_was_copy():
            presentation_manager.get_manager().present_message(
                messages.CLIPBOARD_COPIED_FULL,
                messages.CLIPBOARD_COPIED_BRIEF,
            )
            return

        if manager.last_event_was_paste():
            presentation_manager.get_manager().present_command_announcement()
            return

        msg = "CLIPBOARD PRESENTER: Not presenting change: is not cut, copy, or paste"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _listener(self, event: Atspi.Event) -> None:
        """Generic listener for events of interest."""

        tokens = ["CLIPBOARD PRESENTER: Possible change event", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if self.is_clipboard_text_changed_event(event):
            self._present_clipboard_contents_change(event.any_data)


_presenter: ClipboardPresenter = ClipboardPresenter()


def get_presenter() -> ClipboardPresenter:
    """Returns the Clipboard Presenter singleton."""

    return _presenter
