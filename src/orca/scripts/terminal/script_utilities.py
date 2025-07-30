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

# pylint: disable=too-many-return-statements

"""Script utilities for terminal presentation."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import re
from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca import script_utilities
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_event import TextEventReason

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(script_utilities.Utilities):
    """Script utilities for terminal presentation."""

    def deleted_text(self, event: Atspi.Event) -> str:
        match = re.search(r"\n~", event.any_data)
        if not match:
            return event.any_data

        adjusted = event.any_data[:match.start()]
        tokens = ["TERMINAL: Adjusted deletion: '", adjusted, "'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return adjusted

    def inserted_text(self, event: Atspi.Event) -> str:
        if len(event.any_data) == 1:
            return event.any_data

        if AXUtilities.get_text_event_reason(event) == TextEventReason.AUTO_INSERTION_PRESENTABLE:
            return event.any_data

        if self._script.get_clipboard_presenter().is_clipboard_text_changed_event(event):
            return event.any_data

        start, end = event.detail1, event.detail1 + len(event.any_data)
        first_line = AXText.get_line_at_offset(event.source, start)
        tokens = ["TERMINAL: First line of insertion:", first_line]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        last_line = AXText.get_line_at_offset(event.source, end - 1)
        tokens = ["TERMINAL: Last line of insertion:", last_line]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if first_line == last_line:
            msg = "TERMINAL: Not adjusting single-line insertion."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return event.any_data

        current_line = AXText.get_line_at_offset(event.source, None)
        tokens = ["TERMINAL: Current line:", current_line]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if first_line != ("", 0, 0):
            start = first_line[1]

        if current_line not in (("", 0, 0), first_line, last_line):
            last_line = current_line

        if last_line != ("", 0, 0):
            end = last_line[2]
            if last_line[0].endswith("\n"):
                end -= 1

        adjusted = AXText.get_substring(event.source, start, end)
        if adjusted:
            tokens = ["TERMINAL: Adjusted insertion: '", adjusted, "'"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        else:
            msg = "TERMINAL: Adjustment failed. Returning any_data."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            adjusted = event.any_data

        return adjusted

    def treat_event_as_command(self, event: Atspi.Event) -> bool:
        """Returns true if we should treat this event as resulting from a command."""

        if event.source != focus_manager.get_manager().get_locus_of_focus():
            return False

        if event.type.startswith("object:text-changed:insert") and event.any_data.strip():
            # To let default script handle presentation.
            if input_event_manager.get_manager().last_event_was_paste():
                return False

            if event.any_data.count("\n~"):
                return False

            manager = input_event_manager.get_manager()
            if manager.last_event_was_return_tab_or_space():
                return bool(re.search(r"[^\d\s]", event.any_data))
            # TODO - JD: What condition specifically is this here for?
            if manager.last_event_was_alt_modified():
                return True
            if manager.last_event_was_printable_key():
                return len(event.any_data) > 1
            if AXText.get_caret_offset(event.source) == event.detail1 + event.detail2:
                return True

        return False

    def treat_event_as_noise(self, event: Atspi.Event) -> bool:
        """Returns true if we should treat this event as noise."""

        if input_event_manager.get_manager().last_event_was_command():
            return False

        if event.type.startswith("object:text-changed:delete") and event.any_data.strip():
            manager = input_event_manager.get_manager()
            if manager.last_event_was_return_tab_or_space():
                return True
            # TODO - JD: What condition specifically is this here for?
            if manager.last_event_was_alt_modified():
                return True
            if len(event.any_data) > 1 and manager.last_event_was_printable_key():
                return True

        return False
