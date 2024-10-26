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

"""Custom script for LibreOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team."
__license__   = "LGPL"

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from orca import cmdnames
from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca.scripts import default
from orca import guilabels
from orca import keybindings
from orca import input_event
from orca import messages
from orca import settings_manager
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

from .braille_generator import BrailleGenerator
from .script_utilities import Utilities
from .spellcheck import SpellCheck
from .speech_generator import SpeechGenerator


class Script(default.Script):

    def __init__(self, app):
        super().__init__(app)

        self.speakSpreadsheetCoordinatesCheckButton = None
        self.alwaysSpeakSelectedSpreadsheetRangeCheckButton = None
        self.skipBlankCellsCheckButton = None
        self.speakCellCoordinatesCheckButton = None
        self.speakCellHeadersCheckButton = None
        self.speakCellSpanCheckButton = None

    def get_braille_generator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_speech_generator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_spellcheck(self):
        """Returns the spellcheck for this script."""

        return SpellCheck(self)

    def get_utilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        default.Script.setup_input_event_handlers(self)
        self.input_event_handlers["presentInputLineHandler"] = \
            input_event.InputEventHandler(
                Script.presentInputLine,
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

    def get_app_key_bindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers["presentInputLineHandler"]))


        return keyBindings

    def get_app_preferences_gui(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        label = guilabels.SPREADSHEET_SPEAK_CELL_COORDINATES
        value = settings_manager.get_manager().get_setting('speakSpreadsheetCoordinates')
        self.speakSpreadsheetCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakSpreadsheetCoordinatesCheckButton.set_active(value)
        grid.attach(self.speakSpreadsheetCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.SPREADSHEET_SPEAK_SELECTED_RANGE
        value = settings_manager.get_manager().get_setting('alwaysSpeakSelectedSpreadsheetRange')
        self.alwaysSpeakSelectedSpreadsheetRangeCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.alwaysSpeakSelectedSpreadsheetRangeCheckButton.set_active(value)
        grid.attach(self.alwaysSpeakSelectedSpreadsheetRangeCheckButton, 0, 1, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 2, 1, 1)

        label = Gtk.Label(label=f"<b>{guilabels.TABLE_NAVIGATION}</b>")
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = settings_manager.get_manager().get_setting('speakCellCoordinates')
        self.speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self.speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = settings_manager.get_manager().get_setting('speakCellSpan')
        self.speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self.speakCellSpanCheckButton, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = settings_manager.get_manager().get_setting('speakCellHeaders')
        self.speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self.speakCellHeadersCheckButton, 0, 2, 1, 1)

        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = settings_manager.get_manager().get_setting('skipBlankCells')
        self.skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self.skipBlankCellsCheckButton, 0, 3, 1, 1)

        spellcheck = self.spellcheck.get_app_preferences_gui()
        grid.attach(spellcheck, 0, len(grid.get_children()), 1, 1)
        grid.show_all()

        return grid

    def get_preferences_from_gui(self):
        """Returns a dictionary with the app-specific preferences."""

        prefs = {
            'speakCellSpan':
                self.speakCellSpanCheckButton.get_active(),
            'speakCellHeaders':
                self.speakCellHeadersCheckButton.get_active(),
            'skipBlankCells':
                self.skipBlankCellsCheckButton.get_active(),
            'speakCellCoordinates':
                self.speakCellCoordinatesCheckButton.get_active(),
            'speakSpreadsheetCoordinates':
                self.speakSpreadsheetCoordinatesCheckButton.get_active(),
            'alwaysSpeakSelectedSpreadsheetRange':
                self.alwaysSpeakSelectedSpreadsheetRangeCheckButton.get_active(),
        }

        prefs.update(self.spellcheck.get_preferences_from_gui())
        return prefs

    def pan_braille_left(self, inputEvent=None, pan_amount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_flat_review_presenter().is_active() \
           or not self.isBrailleBeginningShowing() \
           or self.utilities.isSpreadSheetCell(focus) \
           or not self.utilities.isTextArea(focus):
            return default.Script.pan_braille_left(self, inputEvent, pan_amount)

        startOffset = AXText.get_line_at_offset(focus)[1]
        if 0 < startOffset:
            AXText.set_caret_offset(focus, startOffset - 1)
            return True

        obj = self.utilities.findPreviousObject(focus)
        if obj is not None:
            focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
            AXText.set_caret_offset_to_end(obj)
            return True

        return default.Script.pan_braille_left(self, inputEvent, pan_amount)

    def pan_braille_right(self, inputEvent=None, pan_amount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.get_flat_review_presenter().is_active() \
           or not self.isBrailleEndShowing() \
           or self.utilities.isSpreadSheetCell(focus) \
           or not self.utilities.isTextArea(focus):
            return default.Script.pan_braille_right(self, inputEvent, pan_amount)

        endOffset = AXText.get_line_at_offset(focus)[2]
        if endOffset < AXText.get_character_count(focus):
            AXText.set_caret_offset(focus, endOffset)
            return True

        obj = self.utilities.findNextObject(focus)
        if obj is not None:
            focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
            AXText.set_caret_offset_to_start(obj)
            return True

        return default.Script.pan_braille_right(self, inputEvent, pan_amount)

    def presentInputLine(self, inputEvent):
        """Presents the contents of the input line for the current cell.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not self.utilities.isSpreadSheetCell(focus):
            self.presentMessage(messages.SPREADSHEET_NOT_IN_A)
            return True

        text = AXTable.get_cell_formula(focus)
        if not text:
            text = AXText.get_all_text(focus) or messages.EMPTY

        self.presentMessage(text)
        return True

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - old_focus: Accessible that is the old locus of focus
        - new_focus: Accessible that is the new locus of focus
        """

        # Check to see if this is this is for the find command. See
        # comment #18 of bug #354463.
        #
        if self.run_find_command and \
           event.type.startswith("object:state-changed:focused"):
            self.run_find_command = False
            self.get_flat_review_finder().find(self)
            return

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        if self.spellcheck.isSuggestionsItem(new_focus) \
           and not self.spellcheck.isSuggestionsItem(old_focus):
            self.update_braille(new_focus)
            self.spellcheck.presentSuggestionListItem(includeLabel=True)
            return

        # TODO - JD: This is a hack that needs to be done better. For now it
        # fixes the broken echo previous word on Return.
        elif new_focus != old_focus \
             and AXUtilities.is_paragraph(new_focus) and AXUtilities.is_paragraph(old_focus):
            if input_event_manager.get_manager().last_event_was_return() \
               and settings_manager.get_manager().get_setting('enableEchoByWord'):
                self.echoPreviousWord(old_focus)
                return

            # TODO - JD: And this hack is another one that needs to be done better.
            # But this will get us to speak the entire paragraph when navigation by
            # paragraph has occurred.
            if input_event_manager.get_manager().last_event_was_paragraph_navigation():
                string = AXText.get_all_text(new_focus)
                if string:
                    voice = self.speech_generator.voice(obj=new_focus, string=string)
                    self.speakMessage(string, voice=voice)
                    self.update_braille(new_focus)
                    offset = AXText.get_caret_offset(new_focus)
                    self._saveLastCursorPosition(new_focus,offset)
                    return

        # Pass the event onto the parent class to be handled in the default way.
        default.Script.locus_of_focus_changed(self, event,
                                           old_focus, new_focus)

    def on_active_changed(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if not AXObject.get_parent(event.source):
            msg = "SOFFICE: Event source lacks parent"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        # Prevent this events from activating the find operation.
        # See comment #18 of bug #354463.
        if self.run_find_command:
            return

        default.Script.on_active_changed(self, event)

    def on_active_descendant_changed(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if event.any_data == focus:
            return

        if event.source == self.spellcheck.getSuggestionsList():
            if AXUtilities.is_focused(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.any_data, False)
                self.update_braille(event.any_data)
                self.spellcheck.presentSuggestionListItem()
            else:
                self.spellcheck.presentErrorDetails()
            return

        if self.utilities.isSpreadSheetCell(event.any_data) \
           and not AXUtilities.is_focused(event.any_data) \
           and not AXUtilities.is_focused(event.source) :
            msg = "SOFFICE: Neither source nor child have focused state. Clearing cache on table."
            AXObject.clear_cache(event.source, False, msg)

        if event.source != focus and not AXObject.find_ancestor(focus, lambda x: x == event.source):
            msg = "SOFFICE: Working around LO bug 161444."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            # If we immediately set focus to the table, the lack of common ancestor will result in
            # the ancestry up to the frame being spoken.
            manager.set_locus_of_focus(None, AXObject.get_parent(event.source), False)
            # Now setting focus to the table should cause us to present it. Then we can handle the
            # presentation of the actual event we're processing without too much chattiness.
            manager.set_locus_of_focus(event, event.source)

        default.Script.on_active_descendant_changed(self, event)

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        if self.utilities.isSpreadSheetCell(event.any_data):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)
            return

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

        if AXTable.is_last_cell(event.any_data):
            activeRow = self.point_of_reference.get('lastRow', -1)
            activeCol = self.point_of_reference.get('lastColumn', -1)
            if activeRow < 0 or activeCol < 0:
                return

            if focus_manager.get_manager().focus_is_dead():
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)

            self.utilities.handleUndoTextEvent(event)
            rowCount = AXTable.get_row_count(event.source)
            if activeRow == rowCount:
                full = messages.TABLE_ROW_DELETED_FROM_END
                brief = messages.TABLE_ROW_DELETED
            else:
                full = messages.TABLE_ROW_INSERTED_AT_END
                brief = messages.TABLE_ROW_INSERTED
            self.presentMessage(full, brief)
            return

        default.Script.on_children_added(self, event)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        if self._inSayAll:
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_root_pane(event.source) and AXObject.is_ancestor(focus, event.source):
            msg = "SOFFICE: Event ignored: Source is root pane ancestor of current focus."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was table navigation."
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        # We will present this when the selection changes.
        # TODO - JD: Is this still needed? If so, why is the default script not handling it?
        if AXUtilities.is_menu(event.source):
            return

        if AXUtilities.is_text(event.source) or AXUtilities.is_list(event.source):
            comboBox = AXObject.find_ancestor(event.source, AXUtilities.is_combo_box)
            if comboBox:
                focus_manager.get_manager().set_locus_of_focus(event, comboBox, True)
                return

        # TODO - JD: Why are we doing this early?
        if AXUtilities.is_tool_bar(AXObject.get_parent(event.source)):
            default.Script.on_focused_changed(self, event)
            return

        # TODO - JD: This is private. Also why is it here?
        if self.utilities._flowsFromOrToSelection(event.source):
            return

        if AXUtilities.is_paragraph(event.source):
            obj, offset = self.point_of_reference.get("lastCursorPosition", (None, -1))
            start, end, string = self.utilities.getCachedTextSelection(obj)
            if start != end:
                return

            manager = input_event_manager.get_manager()
            if manager.last_event_was_left() or manager.last_event_was_right():
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
                return

        if self.utilities.isSpreadSheetTable(event.source):
            if focus_manager.get_manager().focus_is_dead():
                msg = "SOFFICE: Event believed to be post-editing focus claim."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
                return

            if AXUtilities.is_paragraph(focus) or AXUtilities.is_table_cell(focus):
                msg = "SOFFICE: Event believed to be post-editing focus claim based on role."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
                return

        default.Script.on_focused_changed(self, event)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if event.detail1 == -1:
            return

        if AXUtilities.is_paragraph(event.source) and not AXUtilities.is_focused(event.source):
            # TODO - JD: Can we remove this?
            AXObject.clear_cache(event.source,
                                 False,
                                 "Caret-moved event from object which lacks focused state.")
            if AXUtilities.is_focused(event.source):
                msg = "SOFFICE: Clearing cache was needed due to missing state-changed event."
                debug.printMessage(debug.LEVEL_INFO, msg, True)

        if self.utilities._flowsFromOrToSelection(event.source):
           return

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "SOFFICE: Event ignored: Last input event was table navigation."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if self.utilities.isSpreadSheetCell(focus_manager.get_manager().get_locus_of_focus()):
            if not self.utilities.isCellBeingEdited(event.source):
                msg = "SOFFICE: Event ignored: Source is not cell being edited."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return

        super().on_caret_moved(event)

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if not AXUtilities.is_button(event.source) \
           or not AXUtilities.is_tool_bar(AXObject.get_parent(event.source)):
            default.Script.on_checked_changed(self, event)
            return

        sourceWindow = self.utilities.topLevelObject(event.source)
        focusWindow = self.utilities.topLevelObject(
            focus_manager.get_manager().get_locus_of_focus())
        if sourceWindow != focusWindow:
            return

        if AXUtilities.is_focused(event.source):
            self.presentObject(event.source, alreadyFocused=True, interrupt=True)

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        full, brief = "", ""
        if self.utilities.isSelectedTextDeletionEvent(event):
            msg = "SOFFICE: Change is believed to be due to deleting selected text"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            full = messages.SELECTION_DELETED
        elif self.utilities.isSelectedTextRestoredEvent(event):
            msg = "SOFFICE: Selection is believed to be due to restoring selected text"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            if self.utilities.handleUndoTextEvent(event):
                full = messages.SELECTION_RESTORED

        if full or brief:
            self.presentMessage(full, brief)
            self.utilities.updateCachedTextSelection(event.source)
            return

        super().on_selected_changed(event)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self.utilities.isSpreadSheetTable(event.source):
            if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
                return
            if settings_manager.get_manager().get_setting('alwaysSpeakSelectedSpreadsheetRange'):
                self.utilities.speakSelectedCellRange(event.source)
                return
            if self.utilities.handleRowAndColumnSelectionChange(event.source):
                return
            self.utilities.handleCellSelectionChange(event.source)
            return

        if event.source == self.spellcheck.getSuggestionsList():
            if focus_manager.get_manager().focus_is_active_window():
                msg = "SOFFICE: Not presenting because locusOfFocus is window"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            elif AXUtilities.is_focused(event.source):
                focus_manager.get_manager().set_locus_of_focus(event, event.any_data, False)
                self.update_braille(event.any_data)
                self.spellcheck.presentSuggestionListItem()
            else:
                self.spellcheck.presentErrorDetails()
            return

        super().on_selection_changed(event)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        super().on_window_activated(event)
        if not self.spellcheck.isCheckWindow(event.source):
            return

        child = AXObject.get_child(event.source, 0)
        if AXUtilities.is_dialog(child):
            focus_manager.get_manager().set_locus_of_focus(event, child, False)

        self.spellcheck.presentErrorDetails()

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        super().on_window_deactivated(event)
        self.spellcheck.deactivate()
