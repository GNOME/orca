# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2016 Igalia, S.L.
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

"""Custom script for LibreOffice."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orca import (
    braille_presenter,
    debug,
    flat_review_presenter,
    focus_manager,
    input_event,
    input_event_manager,
    messages,
    presentation_manager,
    speech_presenter,
    structural_navigator,
    table_navigator,
    typing_echo_presenter,
)
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.scripts import default

from .braille_generator import BrailleGenerator
from .script_utilities import Utilities
from .speech_generator import SpeechGenerator

if TYPE_CHECKING:
    from gi.repository import Atspi


class Script(default.Script):
    """Custom script for LibreOffice."""

    # Override the base class type annotations
    utilities: Utilities

    def _create_braille_generator(self) -> BrailleGenerator:
        """Creates and returns the braille generator for this script."""

        return BrailleGenerator(self)

    def _create_speech_generator(self) -> SpeechGenerator:
        """Creates and returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def _pan_braille_left(self, event: input_event.InputEvent | None = None) -> bool:
        """Pans the braille display to the left."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if (
            flat_review_presenter.get_presenter().is_active()
            or AXUtilities.is_spreadsheet_cell(focus)
            or not AXUtilities.is_paragraph(focus)
        ):
            return super()._pan_braille_left(event)

        if braille_presenter.get_presenter().pan_left():
            return True

        # At edge of a paragraph. Try to move caret to previous line.
        start_offset = AXText.get_line_at_offset(focus)[1]
        if start_offset > 0:
            AXText.set_caret_offset(focus, start_offset - 1)
            return True

        obj = self.utilities.find_previous_object(focus)
        if obj is not None:
            focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
            AXText.set_caret_offset_to_end(obj)
            return True

        return super()._pan_braille_left(event)

    def _pan_braille_right(self, event: input_event.InputEvent | None = None) -> bool:
        """Pans the braille display to the right."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if (
            flat_review_presenter.get_presenter().is_active()
            or AXUtilities.is_spreadsheet_cell(focus)
            or not AXUtilities.is_paragraph(focus)
        ):
            return super()._pan_braille_right(event)

        if braille_presenter.get_presenter().pan_right():
            return True

        # At edge of a paragraph. Try to move caret to next line.
        end_offset = AXText.get_line_at_offset(focus)[2]
        if end_offset < AXText.get_character_count(focus):
            AXText.set_caret_offset(focus, end_offset)
            return True

        obj = self.utilities.find_next_object(focus)
        if obj is not None:
            focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
            AXText.set_caret_offset_to_start(obj)
            return True

        return super()._pan_braille_right(event)

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None,
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        if self.run_find_command_on:
            return super().locus_of_focus_changed(event, old_focus, new_focus)

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().quit()

        # TODO - JD: This is a hack that needs to be done better. For now it
        # fixes the broken echo previous word on Return.
        if (
            new_focus != old_focus
            and AXUtilities.is_paragraph(new_focus)
            and AXUtilities.is_paragraph(old_focus)
        ):
            if input_event_manager.get_manager().last_event_was_return():
                typing_echo_presenter.get_presenter().echo_previous_word(old_focus)
                return True

            # TODO - JD: And this hack is another one that needs to be done better.
            # But this will get us to speak the entire paragraph when navigation by
            # paragraph has occurred.
            if input_event_manager.get_manager().last_event_was_paragraph_navigation():
                string = AXText.get_all_text(new_focus)
                if string:
                    presentation_manager.get_manager().speak_accessible_text(new_focus, string)
                    self.update_braille(new_focus)
                    offset = AXText.get_caret_offset(new_focus)
                    focus_manager.get_manager().set_last_cursor_position(new_focus, offset)
                    return True

        return super().locus_of_focus_changed(event, old_focus, new_focus)

    def _on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        if not AXObject.get_parent(event.source):
            msg = "SOFFICE: Event source lacks parent"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super()._on_active_changed(event)

    def _on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if event.any_data == focus:
            return True

        if AXUtilities.is_paragraph(focus):
            return super()._on_active_descendant_changed(event)

        if (
            AXUtilities.is_spreadsheet_cell(event.any_data)
            and not AXUtilities.is_focused(event.any_data)
            and not AXUtilities.is_focused(event.source)
        ):
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

        return super()._on_active_descendant_changed(event)

    def _on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if event.detail1 == -1:
            return True

        if AXUtilities.is_paragraph(event.source) and not AXUtilities.is_focused(event.source):
            # TODO - JD: Can we remove this?
            AXObject.clear_cache(
                event.source,
                False,
                "Caret-moved event from object which lacks focused state.",
            )
            if AXUtilities.is_focused(event.source):
                msg = "SOFFICE: Clearing cache was needed due to missing state-changed event."
                debug.print_message(debug.LEVEL_INFO, msg, True)

        if table_navigator.get_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was table navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if structural_navigator.get_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was structural navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_spreadsheet_cell(focus_manager.get_manager().get_locus_of_focus()):
            if not self.utilities.is_cell_being_edited(event.source):
                msg = "SOFFICE: Event ignored: Source is not cell being edited."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        return super()._on_caret_moved(event)

    def _on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        if AXUtilities.is_spreadsheet_cell(event.any_data):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)
            return True

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

        manager = focus_manager.get_manager()
        if AXUtilities.is_last_cell(event.any_data):
            active_row, active_col = AXTable.get_last_cell_coordinates()
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
            presentation_manager.get_manager().present_message(full, brief)
            return True

        return super()._on_children_added(event)

    def _handle_spreadsheet_focus(self, event: Atspi.Event, focus: Atspi.Accessible) -> bool:
        """Returns True if the spreadsheet focus event was handled."""

        if not AXUtilities.is_spreadsheet_table(event.source):
            return False

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
            focus_manager.get_manager().set_locus_of_focus(
                None,
                AXObject.get_parent(event.source),
                False,
            )

        return False

    def _on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        manager = focus_manager.get_manager()
        if not event.detail1 or manager.in_say_all():
            return True

        # LibreOffice seems to fire focus events for root panes (in documents) and panels
        # in the spell-check dialog for ancestors of the actual focus -- for which we also
        # get events.
        focus = manager.get_locus_of_focus()
        if AXObject.is_ancestor(focus, event.source):
            msg = "SOFFICE: Event ignored: Source is ancestor of current focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if table_navigator.get_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was table navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        if structural_navigator.get_navigator().last_input_event_was_navigation_command():
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

        if self._handle_spreadsheet_focus(event, focus):
            return True

        return super()._on_focused_changed(event)

    def _on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        # https://bugs.documentfoundation.org/show_bug.cgi?id=163801
        if AXUtilities.is_paragraph(event.source):
            msg = "SOFFICE: Ignoring event on unsupported role."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super()._on_selected_changed(event)

    def _on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        # https://bugs.documentfoundation.org/show_bug.cgi?id=163801
        if AXUtilities.is_paragraph(event.source):
            msg = "SOFFICE: Ignoring event on unsupported role."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_spreadsheet_table(event.source):
            presenter = speech_presenter.get_presenter()
            if presenter.get_only_speak_displayed_text():
                return True
            if presenter.get_always_announce_selected_range_in_spreadsheet():
                self.utilities.speak_selected_cell_range(event.source)
                return True
            if self.utilities.handle_row_and_column_selection_change(event.source):
                return True
            self.utilities.handle_cell_selection_change(event.source)
            return True

        return super()._on_selection_changed(event)
