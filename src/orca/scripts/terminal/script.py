# Orca
#
# Copyright 2016 Igalia, S.L.
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

"""Script for terminal support."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from gi.repository import GLib

from orca import (
    braille_presenter,
    debug,
    flat_review_presenter,
    focus_manager,
    input_event_manager,
    presentation_manager,
    typing_echo_presenter,
)
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.enums import TextEventReason
from orca.scripts import default

from .script_utilities import Utilities

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(default.Script):
    """Script for terminal support."""

    utilities: Utilities
    # Minimum seconds between background braille refreshes, including flat review.
    # Recent input and direct navigation or focus updates bypass the interval.
    _BRAILLE_UPDATE_INTERVAL = 0.2

    def __init__(self, app: Atspi.Accessible) -> None:
        super().__init__(app)
        self.present_if_inactive: bool = False
        self._text_event: Atspi.Event | None = None
        self._pending_braille_object: Atspi.Accessible | None = None
        self._braille_timer_id: int = 0
        self._last_braille_update: float = 0.0

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def get_braille_update_interval(self) -> float:
        """Allows immediate updates for a short period after any input event."""

        event = input_event_manager.get_manager().get_last_input_event()
        if event is not None and time.time() - event.time <= self._BRAILLE_UPDATE_INTERVAL:
            return 0.0
        return self._BRAILLE_UPDATE_INTERVAL

    def deactivate(self) -> None:
        """Cancels pending braille output when this script becomes inactive."""

        self._cancel_braille_update()
        super().deactivate()

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None,
    ) -> bool:
        """Updates the caret context when focus changes."""

        if old_focus != new_focus:
            self._cancel_braille_update()
            self.utilities.clear_caret_context()
        return super().locus_of_focus_changed(event, old_focus, new_focus)

    def _on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        return self._handle_text_event(event, self._present_text_insertion)

    def _on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        return self._handle_text_event(event, super()._on_text_deleted)

    def _handle_text_event(
        self, event: Atspi.Event, handler: Callable[[Atspi.Event], bool]
    ) -> bool:
        """Identifies braille refreshes requested by text-change handlers."""

        previous_event = self._text_event
        self._text_event = event
        try:
            return handler(event)
        finally:
            self._text_event = previous_event

    def _cancel_braille_update(self) -> None:
        """Discards a pending text-change refresh."""

        if self._braille_timer_id:
            GLib.source_remove(self._braille_timer_id)
            self._braille_timer_id = 0
        self._pending_braille_object = None

    def _flush_deferred_braille(self) -> bool:
        """Presents the final deferred update even if output has stopped."""

        self._braille_timer_id = 0
        obj = self._pending_braille_object
        self._pending_braille_object = None
        if obj is not None and obj == focus_manager.get_manager().get_locus_of_focus():
            self.update_braille(obj)
        return GLib.SOURCE_REMOVE

    def update_braille(self, obj: Atspi.Accessible, offset: int | None = None) -> None:
        """Limits background text refreshes while keeping responses to input immediate."""

        if not braille_presenter.get_presenter().use_braille():
            self._cancel_braille_update()
            return

        review = flat_review_presenter.get_presenter()
        if review.is_active() and review.last_input_event_was_review_command():
            self._cancel_braille_update()
            return

        event = self._text_event
        if event is not None and event.source == obj and offset is None:
            remaining = self.get_braille_update_interval() - (
                time.monotonic() - self._last_braille_update
            )
            if remaining > 0:
                self._pending_braille_object = obj
                if not self._braille_timer_id:
                    self._braille_timer_id = GLib.timeout_add(
                        max(1, int(remaining * 1000) + 1), self._flush_deferred_braille
                    )
                return
        self._cancel_braille_update()
        self._last_braille_update = time.monotonic()
        super().update_braille(obj, offset)

    def _present_text_insertion(self, event: Atspi.Event) -> bool:
        """Presents text inserted into the terminal."""

        typing_echo_presenter.get_presenter().echo_delayed_terminal_press(self, event)

        if AXUtilities.get_text_event_reason(event) in (
            TextEventReason.AUTO_INSERTION_UNPRESENTABLE,
            TextEventReason.TERMINAL_SCROLLING_REPAINT,
        ) or not self.utilities.treat_event_as_command(event):
            msg = "TERMINAL: Passing along event to default script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return super()._on_text_inserted(event)

        msg = "TERMINAL: Insertion is believed to be due to terminal command"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.update_braille(event.source)

        new_string = self.utilities.inserted_text(event)
        if len(new_string) == 1:
            presentation_manager.get_manager().speak_character(new_string)
        else:
            presentation_manager.get_manager().speak_accessible_text(event.source, new_string)

        if flat_review_presenter.get_presenter().is_active():
            msg = "TERMINAL: Flat review presenter is active. Ignoring insertion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        offset = AXText.get_caret_offset(event.source)
        focus_manager.get_manager().set_last_cursor_position(event.source, offset)
        self.utilities.set_caret_context(event.source, offset)
        AXUtilities.update_cached_selected_text(event.source)
        return True
