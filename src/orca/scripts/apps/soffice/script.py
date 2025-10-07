# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010-2013 The Orca Team.
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
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
# pylint: disable=too-many-public-methods

"""Custom script for LibreOffice."""

from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team."
__license__   = "LGPL"

from typing import TYPE_CHECKING

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from orca import braille
from orca import cmdnames
from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca import guilabels
from orca import keybindings
from orca import input_event
from orca import messages
from orca import settings_manager
from orca import speech_and_verbosity_manager
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.scripts import default

from .braille_generator import BrailleGenerator
from .script_utilities import Utilities
from .spellcheck import SpellCheck
from .speech_generator import SpeechGenerator

if TYPE_CHECKING:
    from gi.repository import Atspi


class Script(default.Script):
    """Custom script for LibreOffice."""

    # Override the base class type annotations
    utilities: Utilities
    spellcheck: SpellCheck

    def __init__(self, app: Atspi.Accessible) -> None:
        super().__init__(app)

        self.speak_spreadsheet_coordinates_check_button: Gtk.CheckButton | None = None
        self.always_speak_selected_spreadsheet_range_check_button: Gtk.CheckButton | None = None
        self.skip_blank_cells_check_button: Gtk.CheckButton | None = None
        self.speak_cell_coordinates_check_button: Gtk.CheckButton | None = None
        self.speak_cell_headers_check_button: Gtk.CheckButton | None = None
        self.speak_cell_span_check_button: Gtk.CheckButton | None = None

    def get_braille_generator(self) -> BrailleGenerator:
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_speech_generator(self) -> SpeechGenerator:
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_spellcheck(self) -> SpellCheck:
        """Returns the spellcheck for this script."""

        return SpellCheck(self)

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

        default.Script.setup_input_event_handlers(self)
        self.input_event_handlers["presentInputLineHandler"] = \
            input_event.InputEventHandler(
                Script.present_input_line,
                cmdnames.PRESENT_INPUT_LINE)

        self.input_event_handlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_left,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_right,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

    def get_app_key_bindings(self) -> keybindings.KeyBindings:
        """Returns the application-specific keybindings for this script."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers["presentInputLineHandler"]))


        return bindings

    def get_app_preferences_gui(self) -> Gtk.Grid:
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        # TODO - JD: All table settings belong in a non-app dialog page.

        speech_manager = speech_and_verbosity_manager.get_manager()
        grid = Gtk.Grid()
        grid.set_border_width(12)

        label = guilabels.SPREADSHEET_SPEAK_CELL_COORDINATES
        value = speech_manager.get_announce_spreadsheet_cell_coordinates()
        self.speak_spreadsheet_coordinates_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speak_spreadsheet_coordinates_check_button.set_active(value)
        grid.attach(self.speak_spreadsheet_coordinates_check_button, 0, 0, 1, 1)

        label = guilabels.SPREADSHEET_SPEAK_SELECTED_RANGE
        value = speech_manager.get_always_announce_selected_range_in_spreadsheet()
        self.always_speak_selected_spreadsheet_range_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.always_speak_selected_spreadsheet_range_check_button.set_active(value)
        grid.attach(self.always_speak_selected_spreadsheet_range_check_button, 0, 1, 1, 1)

        table_frame = Gtk.Frame()
        grid.attach(table_frame, 0, 2, 1, 1)

        label = Gtk.Label(label=f"<b>{guilabels.TABLE_NAVIGATION}</b>")
        label.set_use_markup(True)
        table_frame.set_label_widget(label)

        table_alignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        table_alignment.set_padding(0, 0, 12, 0)
        table_frame.add(table_alignment)
        table_grid = Gtk.Grid()
        table_alignment.add(table_grid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = speech_manager.get_announce_cell_coordinates()
        self.speak_cell_coordinates_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speak_cell_coordinates_check_button.set_active(value)
        table_grid.attach(self.speak_cell_coordinates_check_button, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = speech_manager.get_announce_cell_span()
        self.speak_cell_span_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speak_cell_span_check_button.set_active(value)
        table_grid.attach(self.speak_cell_span_check_button, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = speech_manager.get_announce_cell_headers()
        self.speak_cell_headers_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speak_cell_headers_check_button.set_active(value)
        table_grid.attach(self.speak_cell_headers_check_button, 0, 2, 1, 1)

        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = self.get_table_navigator().get_skip_blank_cells()
        self.skip_blank_cells_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.skip_blank_cells_check_button.set_active(value)
        table_grid.attach(self.skip_blank_cells_check_button, 0, 3, 1, 1)

        spellcheck = self.spellcheck.get_app_preferences_gui()
        grid.attach(spellcheck, 0, len(grid.get_children()), 1, 1)
        grid.show_all()

        return grid

    def get_preferences_from_gui(self) -> dict[str, bool]:
        """Returns a dictionary with the app-specific preferences."""

        assert self.speak_cell_span_check_button
        assert self.speak_cell_headers_check_button
        assert self.skip_blank_cells_check_button
        assert self.speak_cell_coordinates_check_button
        assert self.speak_spreadsheet_coordinates_check_button
        assert self.always_speak_selected_spreadsheet_range_check_button

        prefs = {
            "speakCellSpan":
                self.speak_cell_span_check_button.get_active(),
            "speakCellHeaders":
                self.speak_cell_headers_check_button.get_active(),
            "skipBlankCells":
                self.skip_blank_cells_check_button.get_active(),
            "speakCellCoordinates":
                self.speak_cell_coordinates_check_button.get_active(),
            "speakSpreadsheetCoordinates":
                self.speak_spreadsheet_coordinates_check_button.get_active(),
            "alwaysSpeakSelectedSpreadsheetRange":
                self.always_speak_selected_spreadsheet_range_check_button.get_active(),
        }

        prefs.update(self.spellcheck.get_preferences_from_gui())
        return prefs

    def pan_braille_left(
        self,
        event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans the braille display to the left."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_flat_review_presenter().is_active() \
           or not braille.beginningIsShowing \
           or self.utilities.is_spreadsheet_cell(focus) \
           or not AXUtilities.is_paragraph(focus):
            return super().pan_braille_left(event, pan_amount)

        start_offset = AXText.get_line_at_offset(focus)[1]
        if 0 < start_offset:
            AXText.set_caret_offset(focus, start_offset - 1)
            return True

        obj = self.utilities.find_previous_object(focus)
        if obj is not None:
            focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
            AXText.set_caret_offset_to_end(obj)
            return True

        return super().pan_braille_left(event, pan_amount)

    def pan_braille_right(
        self,
        event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans the braille display to the right."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_flat_review_presenter().is_active() \
           or not braille.endIsShowing \
           or self.utilities.is_spreadsheet_cell(focus) \
           or not AXUtilities.is_paragraph(focus):
            return super().pan_braille_right(event, pan_amount)

        end_offset = AXText.get_line_at_offset(focus)[2]
        if end_offset < AXText.get_character_count(focus):
            AXText.set_caret_offset(focus, end_offset)
            return True

        obj = self.utilities.find_next_object(focus)
        if obj is not None:
            focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
            AXText.set_caret_offset_to_start(obj)
            return True

        return super().pan_braille_right(event, pan_amount)

    def present_input_line(self, _event: "input_event.InputEvent") -> bool:
        """Presents the contents of the input line for the current cell."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not self.utilities.is_spreadsheet_cell(focus):
            self.present_message(messages.SPREADSHEET_NOT_IN_A)
            return True

        text = AXTable.get_cell_formula(focus)
        if not text:
            text = AXText.get_all_text(focus) or messages.EMPTY

        self.present_message(text)
        return True

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        if self.run_find_command_on:
            return super().locus_of_focus_changed(event, old_focus, new_focus)

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        if self.spellcheck.is_suggestions_item(new_focus) \
           and not self.spellcheck.is_suggestions_item(old_focus):
            self.update_braille(new_focus)
            self.spellcheck.present_suggestion_list_item(include_label=True)
            return True

        # TODO - JD: This is a hack that needs to be done better. For now it
        # fixes the broken echo previous word on Return.
        if new_focus != old_focus \
             and AXUtilities.is_paragraph(new_focus) and AXUtilities.is_paragraph(old_focus):
            if input_event_manager.get_manager().last_event_was_return():
                self.get_typing_echo_presenter().echo_previous_word(self, old_focus)
                return True

            # TODO - JD: And this hack is another one that needs to be done better.
            # But this will get us to speak the entire paragraph when navigation by
            # paragraph has occurred.
            if input_event_manager.get_manager().last_event_was_paragraph_navigation():
                string = AXText.get_all_text(new_focus)
                if string:
                    voice = self.speech_generator.voice(obj=new_focus, string=string)
                    self.speak_message(string, voice=voice)
                    self.update_braille(new_focus)
                    offset = AXText.get_caret_offset(new_focus)
                    focus_manager.get_manager().set_last_cursor_position(new_focus,offset)
                    return True

        return super().locus_of_focus_changed(event, old_focus, new_focus)

    def on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        if not AXObject.get_parent(event.source):
            msg = "SOFFICE: Event source lacks parent"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_active_changed(event)

    def on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if event.any_data == focus:
            return True

        if AXUtilities.is_paragraph(focus):
            return super().on_active_descendant_changed(event)

        if event.source == self.spellcheck.get_suggestions_list():
            if AXUtilities.is_focused(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.any_data, False)
                self.update_braille(event.any_data)
                self.spellcheck.present_suggestion_list_item()
            else:
                self.spellcheck.present_error_details()
            return True

        if self.utilities.is_spreadsheet_cell(event.any_data) \
           and not AXUtilities.is_focused(event.any_data) \
           and not AXUtilities.is_focused(event.source) :
            msg = "SOFFICE: Neither source nor child have focused state. Clearing cache on table."
            AXObject.clear_cache(event.source, False, msg)

        if event.source != focus and not AXObject.find_ancestor(focus, lambda x: x == event.source):
            msg = "SOFFICE: Working around LO bug 161444."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            # If we immediately set focus to the table, the lack of common ancestor will result in
            # the ancestry up to the frame being spoken.
            manager.set_locus_of_focus(None, AXObject.get_parent(event.source), False)
            # Now setting focus to the table should cause us to present it. Then we can handle the
            # presentation of the actual event we're processing without too much chattiness.
            manager.set_locus_of_focus(event, event.source)

        return super().on_active_descendant_changed(event)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if event.detail1 == -1:
            return True

        if AXUtilities.is_paragraph(event.source) and not AXUtilities.is_focused(event.source):
            # TODO - JD: Can we remove this?
            AXObject.clear_cache(event.source,
                                 False,
                                 "Caret-moved event from object which lacks focused state.")
            if AXUtilities.is_focused(event.source):
                msg = "SOFFICE: Clearing cache was needed due to missing state-changed event."
                debug.print_message(debug.LEVEL_INFO, msg, True)

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was table navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_structural_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was structural navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.is_spreadsheet_cell(focus_manager.get_manager().get_locus_of_focus()):
            if not self.utilities.is_cell_being_edited(event.source):
                msg = "SOFFICE: Event ignored: Source is not cell being edited."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        return super().on_caret_moved(event)

    def on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        if self.utilities.is_spreadsheet_cell(event.any_data):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)
            return True

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

        manager = focus_manager.get_manager()
        if AXTable.is_last_cell(event.any_data):
            active_row, active_col = manager.get_last_cell_coordinates()
            if active_row < 0 or active_col < 0:
                return True

            if manager.focus_is_dead():
                manager.set_locus_of_focus(event, event.source, False)

            self.utilities.handle_undo_text_event(event)
            row_count = AXTable.get_row_count(event.source)
            if active_row == row_count:
                full = messages.TABLE_ROW_DELETED_FROM_END
                brief = messages.TABLE_ROW_DELETED
            else:
                full = messages.TABLE_ROW_INSERTED_AT_END
                brief = messages.TABLE_ROW_INSERTED
            self.present_message(full, brief)
            return True

        return super().on_children_added(event)

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return True

        manager = focus_manager.get_manager()
        if manager.in_say_all():
            return True

        focus = manager.get_locus_of_focus()
        if AXUtilities.is_root_pane(event.source) and AXObject.is_ancestor(focus, event.source):
            msg = "SOFFICE: Event ignored: Source is root pane ancestor of current focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was table navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        if self.get_structural_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was structural navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        if AXUtilities.is_text(event.source) or AXUtilities.is_list(event.source):
            combobox = AXObject.find_ancestor(event.source, AXUtilities.is_combo_box)
            if combobox:
                focus_manager.get_manager().set_locus_of_focus(event, combobox, True)
                return True

        if AXUtilities.is_paragraph(event.source):
            input_manager = input_event_manager.get_manager()
            if input_manager.last_event_was_left() or input_manager.last_event_was_right():
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
                return True

        if self.utilities.is_spreadsheet_table(event.source):
            if focus_manager.get_manager().focus_is_dead():
                msg = "SOFFICE: Event believed to be post-editing focus claim."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
                return True

            if AXUtilities.is_paragraph(focus) or AXUtilities.is_table_cell(focus):
                if AXObject.find_ancestor(focus, lambda x: x == event.source):
                    msg = "SOFFICE: Event believed to be post-editing focus claim based on role."
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
                    return True

                # If we were in a cell, and a different table is claiming focus, it's likely that
                # the current sheet has just changed. There will not be a common ancestor between
                # the old cell and the table and we'll wind up re-announcing the frame. To prevent
                # that, set the focus to the parent of the sheet before the default script causes
                # the table to be presented.
                manager.set_locus_of_focus(None, AXObject.get_parent(event.source), False)

        return super().on_focused_changed(event)

    def on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        # https://bugs.documentfoundation.org/show_bug.cgi?id=163801
        if AXUtilities.is_paragraph(event.source):
            msg = "SOFFICE: Ignoring event on unsupported role."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_selected_changed(event)

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        # https://bugs.documentfoundation.org/show_bug.cgi?id=163801
        if AXUtilities.is_paragraph(event.source):
            msg = "SOFFICE: Ignoring event on unsupported role."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.is_spreadsheet_table(event.source):
            manager = speech_and_verbosity_manager.get_manager()
            if manager.get_only_speak_displayed_text():
                return True
            if manager.get_always_announce_selected_range_in_spreadsheet():
                self.utilities.speak_selected_cell_range(event.source)
                return True
            if self.utilities.handle_row_and_column_selection_change(event.source):
                return True
            self.utilities.handle_cell_selection_change(event.source)
            return True

        if event.source == self.spellcheck.get_suggestions_list():
            if focus_manager.get_manager().focus_is_active_window():
                msg = "SOFFICE: Not presenting because locusOfFocus is window"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            elif AXUtilities.is_focused(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.any_data, False)
                self.update_braille(event.any_data)
                self.spellcheck.present_suggestion_list_item()
            else:
                self.spellcheck.present_error_details()
            return True

        return super().on_selection_changed(event)

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        super().on_window_activated(event)
        if not self.spellcheck.is_spell_check_window(event.source):
            self.spellcheck.deactivate()
            return True

        self.spellcheck.present_error_details()
        return True

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        self.spellcheck.deactivate()
        return super().on_window_deactivated(event)
