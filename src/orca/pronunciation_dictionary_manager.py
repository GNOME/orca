# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Manager for user's pronunciation dictionary that maps words to what they sound like."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations
from typing import Callable, TYPE_CHECKING


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import guilabels
from . import messages
from . import preferences_grid_base
from . import script_manager
from . import settings_manager
from . import speech_and_verbosity_manager

if TYPE_CHECKING:
    from .scripts import default


class PronunciationDictionaryPreferencesGrid(  # pylint: disable=too-many-instance-attributes
    preferences_grid_base.PreferencesGridBase
):
    """GtkGrid containing the Pronunciation Dictionary preferences page."""

    def __init__(self, manager: "PronunciationDictionaryManager", script: default.Script) -> None:
        super().__init__(guilabels.PRONUNCIATION)
        self._manager: PronunciationDictionaryManager = manager
        self._script: default.Script = script
        self._initializing: bool = True

        self._pronunciations: list[tuple[str, str]] = []
        self._listbox: Gtk.ListBox | None = None
        self._saved_use_pronunciation_dictionary: bool = False
        self._has_unsaved_changes: bool = False
        self._loaded_from_settings: bool = False

        # Size group to ensure all left labels (phrases) have the same width
        self._left_label_size_group: Gtk.SizeGroup = Gtk.SizeGroup(
            mode=Gtk.SizeGroupMode.HORIZONTAL
        )

        self._build()
        self.refresh()

    def _build(self) -> None:
        """Create the Gtk widgets composing the grid."""

        row = 0

        # Info box
        info_listbox = self._create_info_listbox(guilabels.PRONUNCIATION_DICTIONARY_INFO)
        info_listbox.set_margin_bottom(12)
        self.attach(info_listbox, 0, row, 1, 1)
        row += 1

        # Header box with title and + button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(6)

        title_label = Gtk.Label(label=guilabels.PRONUNCIATION_DICTIONARY)
        title_label.set_halign(Gtk.Align.START)
        title_label.get_style_context().add_class("heading")
        header_box.pack_start(title_label, True, True, 0)

        add_button = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        add_button.get_accessible().set_name(guilabels.DICTIONARY_NEW_ENTRY)
        add_button.connect("clicked", self._on_add_clicked)
        header_box.pack_end(add_button, False, False, 0)

        self.attach(header_box, 0, row, 1, 1)
        row += 1

        # ListBox for pronunciation entries
        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._listbox.get_style_context().add_class("frame")

        # Disable pronunciation dictionary when listbox is shown
        self._listbox.connect("realize", self._on_listbox_realize)
        self._listbox.connect("unrealize", self._on_listbox_unrealize)

        scrolled_window = self._create_scrolled_window(self._listbox)
        self.attach(scrolled_window, 0, row, 1, 1)

    def _create_two_label_row(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        left_label_text: str,
        right_label_text: str,
        edit_handler: Callable[[Gtk.Button], None] | None = None,
        delete_handler: Callable[[Gtk.Button], None] | None = None,
        include_top_separator: bool = True,
        left_label_size_group: Gtk.SizeGroup | None = None,
    ) -> Gtk.ListBoxRow:
        """Create a single listbox row with two labels and optional edit/delete buttons."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        if include_top_separator:
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox.pack_start(separator, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hbox.set_margin_start(12)
        hbox.set_margin_end(12)
        hbox.set_margin_top(12)
        hbox.set_margin_bottom(12)

        left_label = Gtk.Label(label=left_label_text, xalign=0)

        if left_label_size_group:
            left_label_size_group.add_widget(left_label)

        hbox.pack_start(left_label, False, False, 0)

        right_label = Gtk.Label(label=right_label_text, xalign=0)
        right_label.set_hexpand(True)
        hbox.pack_start(right_label, True, True, 0)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        delete_button = None
        if delete_handler:
            delete_button = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.DND)
            delete_button.set_relief(Gtk.ReliefStyle.NONE)
            delete_button.get_accessible().set_name(guilabels.DICTIONARY_DELETE)
            delete_button.connect("clicked", delete_handler)
            button_box.pack_start(delete_button, False, False, 0)

        edit_button = None
        if edit_handler:
            edit_button = Gtk.Button.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.DND)
            edit_button.set_relief(Gtk.ReliefStyle.NONE)
            edit_button.get_accessible().set_name(guilabels.DIALOG_EDIT)
            edit_button.connect("clicked", edit_handler)
            button_box.pack_start(edit_button, False, False, 0)

        hbox.pack_end(button_box, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)
        row.add(vbox)

        row.delete_button = delete_button
        row.edit_button = edit_button

        return row

    def _create_row(
        self, phrase: str, substitution: str, row_index: int, include_top_separator: bool = True
    ) -> Gtk.ListBoxRow:
        """Create a ListBoxRow for a pronunciation entry."""

        row = self._create_two_label_row(
            phrase,
            substitution,
            edit_handler=self._on_edit_clicked,
            delete_handler=self._on_delete_clicked,
            include_top_separator=include_top_separator,
            left_label_size_group=self._left_label_size_group,
        )
        # Store row_index as Python attributes
        row.pronunciation_row_index = row_index

        if row.edit_button:
            row.edit_button.pronunciation_row_index = row_index

        if row.delete_button:
            row.delete_button.pronunciation_row_index = row_index

        return row

    def _on_edit_clicked(self, button: Gtk.Button) -> None:
        """Handle edit button click."""

        row_index = button.pronunciation_row_index
        phrase, substitution = self._pronunciations[row_index]
        self._show_edit_dialog(phrase, substitution, row_index)

    def _on_delete_clicked(self, button: Gtk.Button) -> None:
        """Handle delete button click."""

        row_index = button.pronunciation_row_index
        phrase, _ = self._pronunciations[row_index]
        del self._pronunciations[row_index]
        self._has_unsaved_changes = True
        self.refresh()

        script = script_manager.get_manager().get_active_script()
        if script:
            script.present_message(messages.PRONUNCIATION_DELETED % phrase)

    def _on_listbox_realize(self, _widget: Gtk.Widget) -> None:
        """Disable pronunciation dictionary when listbox is shown."""

        speech_manager = speech_and_verbosity_manager.get_manager()
        self._saved_use_pronunciation_dictionary = speech_manager.get_use_pronunciation_dictionary()
        speech_manager.set_use_pronunciation_dictionary(False)

    def _on_listbox_unrealize(self, _widget: Gtk.Widget) -> None:
        """Restore pronunciation dictionary when listbox is hidden."""

        speech_manager = speech_and_verbosity_manager.get_manager()
        speech_manager.set_use_pronunciation_dictionary(self._saved_use_pronunciation_dictionary)

    def _on_add_clicked(self, _button: Gtk.Button) -> None:
        """Handle Add button click to open add dialog."""

        self._show_add_dialog()

    def _show_add_dialog(self) -> None:
        """Show dialog to add a new pronunciation."""

        speech_manager = speech_and_verbosity_manager.get_manager()
        saved_use_pronunciation_dictionary = speech_manager.get_use_pronunciation_dictionary()
        speech_manager.set_use_pronunciation_dictionary(False)

        dialog, add_button = self._create_header_bar_dialog(
            guilabels.ADD_NEW_PRONUNCIATION, guilabels.DIALOG_CANCEL, guilabels.DIALOG_ADD
        )

        content_area = dialog.get_content_area()

        listbox = preferences_grid_base.FocusManagedListBox()

        # Size group to ensure labels have same width and entries align
        label_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        # Actual string row
        phrase_entry = Gtk.Entry()
        phrase_entry.set_size_request(-1, 40)
        phrase_row = self._create_labeled_entry_row(
            guilabels.DICTIONARY_ACTUAL_STRING,
            phrase_entry,
            include_top_separator=False,
            label_size_group=label_size_group,
        )
        listbox.add_row_with_widget(phrase_row, phrase_entry)

        # Replacement string row
        substitution_entry = Gtk.Entry()
        substitution_entry.set_size_request(-1, 40)
        substitution_row = self._create_labeled_entry_row(
            guilabels.DICTIONARY_REPLACEMENT_STRING,
            substitution_entry,
            label_size_group=label_size_group,
        )
        listbox.add_row_with_widget(substitution_row, substitution_entry)

        def on_entry_activate(_entry):
            """Only activate dialog if both fields are filled."""
            if phrase_entry.get_text().strip() and substitution_entry.get_text().strip():
                dialog.response(Gtk.ResponseType.OK)

        phrase_entry.connect("activate", on_entry_activate)
        substitution_entry.connect("activate", on_entry_activate)

        content_area.pack_start(listbox, True, True, 0)

        def on_response(dlg, response_id):
            if response_id == Gtk.ResponseType.OK:
                phrase = phrase_entry.get_text().strip()
                substitution = substitution_entry.get_text().strip()
                if phrase and substitution:
                    self._pronunciations.append((phrase, substitution))
                    self._has_unsaved_changes = True
                    self.refresh()
            speech_manager.set_use_pronunciation_dictionary(saved_use_pronunciation_dictionary)
            dlg.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()
        add_button.grab_default()
        phrase_entry.grab_focus()

    def _show_edit_dialog(  # pylint: disable=too-many-locals
        self, phrase: str, substitution: str, row_index: int
    ) -> None:
        """Show dialog to edit an existing pronunciation."""

        speech_manager = speech_and_verbosity_manager.get_manager()
        saved_use_pronunciation_dictionary = speech_manager.get_use_pronunciation_dictionary()
        speech_manager.set_use_pronunciation_dictionary(False)

        dialog, edit_button = self._create_header_bar_dialog(
            guilabels.EDIT_PRONUNCIATION, guilabels.DIALOG_CANCEL, guilabels.DIALOG_EDIT
        )

        content_area = dialog.get_content_area()

        listbox = preferences_grid_base.FocusManagedListBox()

        # Size group to ensure labels have same width and entries align
        label_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        # Actual string row
        phrase_entry = Gtk.Entry()
        phrase_entry.set_text(phrase)
        phrase_entry.set_size_request(-1, 40)
        phrase_row = self._create_labeled_entry_row(
            guilabels.DICTIONARY_ACTUAL_STRING,
            phrase_entry,
            include_top_separator=False,
            label_size_group=label_size_group,
        )
        listbox.add_row_with_widget(phrase_row, phrase_entry)

        # Replacement string row
        substitution_entry = Gtk.Entry()
        substitution_entry.set_text(substitution)
        substitution_entry.set_size_request(-1, 40)
        substitution_row = self._create_labeled_entry_row(
            guilabels.DICTIONARY_REPLACEMENT_STRING,
            substitution_entry,
            label_size_group=label_size_group,
        )
        listbox.add_row_with_widget(substitution_row, substitution_entry)

        def on_entry_activate(_entry):
            """Only activate dialog if both fields are filled."""
            if phrase_entry.get_text().strip() and substitution_entry.get_text().strip():
                dialog.response(Gtk.ResponseType.OK)

        phrase_entry.connect("activate", on_entry_activate)
        substitution_entry.connect("activate", on_entry_activate)

        content_area.pack_start(listbox, True, True, 0)

        def on_response(dlg, response_id):
            if response_id == Gtk.ResponseType.OK:
                new_phrase = phrase_entry.get_text().strip()
                new_substitution = substitution_entry.get_text().strip()
                if new_phrase and new_substitution:
                    self._pronunciations[row_index] = (new_phrase, new_substitution)
                    self._has_unsaved_changes = True
                    self.refresh()
            speech_manager.set_use_pronunciation_dictionary(saved_use_pronunciation_dictionary)
            dlg.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()
        edit_button.grab_default()
        phrase_entry.grab_focus()

    def reload(self) -> None:
        """Reload settings from the manager and refresh the UI."""

        self._pronunciations = []
        self._loaded_from_settings = False
        self._has_unsaved_changes = False
        self.refresh()

    def save_settings(self) -> dict[str, list[str]]:
        """Save settings and return a dictionary of the current values for those settings."""

        self._manager.set_dictionary({})
        result = {}

        for phrase, substitution in self._pronunciations:
            if phrase and substitution:
                self._manager.set_pronunciation(phrase, substitution)
                # Save in old format [actual, replacement] for backward compatibility.
                # TODO - JD: When we migrate to gsettings, we can store as {actual: replacement}.
                result[phrase.lower()] = [phrase, substitution]

        self._has_unsaved_changes = False
        return result

    def refresh(self) -> None:
        """Update listbox to reflect current pronunciation list."""

        if self._listbox is None:
            return

        self._initializing = True

        for child in self._listbox.get_children():
            self._listbox.remove(child)

        if not self._loaded_from_settings:
            self._loaded_from_settings = True
            manager = settings_manager.get_manager()
            if self._script and self._script.app:
                pronunciation_dict = manager.get_pronunciations()
            else:
                prefs_dict = manager.get_general_settings()
                profile = prefs_dict.get("profile", ["Default", "default"])[1]
                pronunciation_dict = manager.get_pronunciations(profile)

            for key in sorted(pronunciation_dict.keys()):
                value = pronunciation_dict[key]
                if isinstance(value, list):
                    replacement = value[1] if len(value) > 1 else value[0]
                else:
                    replacement = value

                self._pronunciations.append((key, replacement))

        if self._pronunciations:
            for index, (phrase, substitution) in enumerate(self._pronunciations):
                row = self._create_row(phrase, substitution, index, include_top_separator=index > 0)
                self._listbox.add(row)
        else:
            empty_row = self._create_info_row(guilabels.DICTIONARY_EMPTY)
            self._listbox.add(empty_row)

        self._listbox.show_all()
        self._initializing = False


class PronunciationDictionaryManager:
    """Manager for the pronunciation dictionary."""

    def __init__(self) -> None:
        self._dictionary: dict[str, str] = {}

    def create_preferences_grid(
        self, script: default.Script
    ) -> PronunciationDictionaryPreferencesGrid:
        """Returns the GtkGrid containing the pronunciation dictionary UI."""

        return PronunciationDictionaryPreferencesGrid(self, script)

    def get_pronunciation(self, word: str) -> str:
        """Returns the pronunciation for word, or word if not found."""

        return self._dictionary.get(word.lower(), word)

    def set_pronunciation(self, word: str, replacement: str) -> None:
        """Adds word/replacement pair."""

        # TODO - JD: Storing the words as lowercase is what we've done historically.
        # However, this means that on occasions where case sensitivity matters, there
        # will be a false positive (e.g., "US" vs "us"). Consider adding a checkbox
        # to the UI to allow users to choose case sensitivity for individual entries.

        key = word.lower()
        self._dictionary[key] = replacement

    def get_dictionary(self) -> dict[str, str]:
        """Returns the pronunciation dictionary."""

        return self._dictionary

    def set_dictionary(self, value: dict[str, str]) -> None:
        """Sets the pronunciation dictionary."""

        self._dictionary = value


_manager = PronunciationDictionaryManager()


def get_manager() -> PronunciationDictionaryManager:
    """Returns the pronunciation-dictionary-manager singleton."""

    return _manager
