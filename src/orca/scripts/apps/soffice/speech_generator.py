# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

# pylint: disable=wrong-import-position

"""Produces speech presentation for accessible objects."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING, Any

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import debug
from orca import focus_manager
from orca import messages
from orca import speech_and_verbosity_manager
from orca import speech_generator
from orca.ax_component import AXComponent
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    from . import script


class SpeechGenerator(speech_generator.SpeechGenerator):
    """Produces speech presentation for accessible objects."""

    # Type annotation to override the base class script type
    _script: script.Script

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"SOFFICE SPEECH GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @log_generator_output
    def _generate_accessible_name(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._script.utilities.is_spreadsheet_cell(obj):
            # Currently the coordinates of the cell are exposed as the name.
            return []
        return super()._generate_accessible_name(obj, **args)

    @log_generator_output
    def _generate_text_line(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if AXUtilities.is_combo_box(obj):
            if entry := AXObject.find_descendant(obj, AXUtilities.is_text_input):
                return super()._generate_text_line(entry)
            return []

        # TODO - JD: The SayLine, etc. code should be generated and not put
        # together in the scripts. In addition, the voice crap needs to go
        # here. Then it needs to be removed from the scripts.
        if AXObject.supports_text(obj):
            text = AXText.get_line_at_offset(obj)[0]
            if not text:
                result: list[Any] = [messages.BLANK]
                result.extend(self.voice(string=text, obj=obj, **args))
                return result

        return super()._generate_text_line(obj, **args)

    @log_generator_output
    def _generate_state_pressed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Treat toggle buttons in the toolbar specially. This is so we can
        have more natural sounding speech such as "bold on", "bold off", etc."""

        if not AXUtilities.is_toggle_button(obj, args.get("role")):
            return []

        if not AXUtilities.is_tool_bar(AXObject.get_parent(obj)):
            return super()._generate_state_pressed(obj, **args)

        if AXUtilities.is_checked(obj):
            result: list[Any] = [messages.ON]
        else:
            result = [messages.OFF]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def _generate_too_long(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """If there is text in this spread sheet cell, compare the size of
        the text within the table cell with the size of the actual table
        cell and report back to the user if it is larger.

        Returns an indication of how many characters are greater than the size
        of the spread sheet cell, or None if the message fits.
        """
        if self._only_speak_displayed_text():
            return []

        # TODO - JD: Can this be moved to AXText?
        result: list[Any] = []
        length = AXText.get_character_count(obj)
        too_long_count = 0
        extents = AXComponent.get_rect(obj)
        for i in range(length):
            rect = AXText.get_character_rect(obj, i)
            if rect.x < extents.x:
                too_long_count += 1
            elif rect.x + rect.width > extents.x + extents.width:
                too_long_count += length - i
                break
        if too_long_count > 0:
            result = [messages.characters_too_long(too_long_count)]
        if result:
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def _generate_has_formula(self, obj: Atspi.Accessible, **args) -> list[Any]:
        formula = AXTable.get_cell_formula(obj)
        if not formula:
            return []

        if args.get("formatType") == "basicWhereAmI":
            result: list[Any] = [f"{messages.HAS_FORMULA}. {formula}"]
        else:
            result = [messages.HAS_FORMULA]

        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_real_table_cell(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if focus_manager.get_manager().in_say_all():
            return []

        result = super()._generate_real_table_cell(obj, **args)

        speech_manager = speech_and_verbosity_manager.get_manager()
        if not self._script.utilities.is_spreadsheet_cell(obj):
            if self._script.get_table_navigator().last_input_event_was_navigation_command():
                return result

            if speech_manager.get_announce_cell_coordinates():
                result.append(AXObject.get_name(obj))
            return result

        if speech_manager.get_announce_spreadsheet_cell_coordinates() \
           or args.get("formatType") == "basicWhereAmI":
            label = AXTable.get_label_for_cell_coordinates(obj) \
                or self._script.utilities.spreadsheet_cell_name(obj)
            result.append(label)

        if self._script.utilities.should_read_full_row(obj, args.get("priorObj")):
            if self._script.utilities.cell_row_changed(obj):
                return result

        too_long = self._generate_too_long(obj, **args)
        if too_long:
            result.extend(self._generate_pause(obj, **args))
            result.extend(too_long)

        has_formula = self._generate_has_formula(obj, **args)
        if has_formula:
            result.extend(self._generate_pause(obj, **args))
            result.extend(has_formula)

        if result == speech_generator.PAUSE:
            result = [messages.BLANK]
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_new_ancestors(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._script.utilities.is_spreadsheet_cell(obj) \
           and self._script.utilities.is_document_panel(AXObject.get_parent(args.get("priorObj"))):
            return []

        return super()._generate_new_ancestors(obj, **args)

    @log_generator_output
    def _generate_old_ancestors(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._script.utilities.is_spreadsheet_cell(args.get("priorObj")):
            return []

        return super()._generate_old_ancestors(obj, **args)
