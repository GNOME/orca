# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Preferences grid for the pronunciation dictionary."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # pylint: disable=no-name-in-module

from . import (
    gsettings_registry,
    guilabels,
    messages,
    preferences_grid_base,
    presentation_manager,
    script_manager,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .pronunciation_dictionary_manager import PronunciationDictionaryManager
    from .scripts import default


class PronunciationDictionaryPreferencesGrid(  # pylint: disable=too-many-instance-attributes
    preferences_grid_base.PreferencesGridBase,
):
    """GtkGrid containing the Pronunciation Dictionary preferences page."""

    # pylint: disable=no-member

    BUILD_BATCH_SIZE: int = 50

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for pronunciation preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.PRONUNCIATION,
            panel_id="manual.pronunciation",
            description=(
                guilabels.PRONUNCIATION_DICTIONARY_INFO
                + "\n\n"
                + "The pronunciation dictionary is a list of words and replacement text. "
                "Add a new entry from the dictionary header. Edit or delete an existing "
                "entry from its row."
            ),
            schema="pronunciations",
            show_available_settings=False,
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.PRONUNCIATION_DICTIONARY,
                    kind="list",
                    summary=(
                        "Lists words and the replacement text Orca sends to speech before "
                        "speaking them."
                    ),
                    actions=(
                        preferences_grid_base.PreferenceActionDoc(
                            label=guilabels.ADD_NEW_PRONUNCIATION,
                            summary=(
                                "Opens a dialog where you can add a word and the replacement "
                                "text Orca should speak."
                            ),
                            placement="header",
                        ),
                    ),
                    item_actions=(
                        preferences_grid_base.PreferenceActionDoc(
                            label=guilabels.EDIT_PRONUNCIATION,
                            summary=(
                                "Opens a dialog where you can change the selected pronunciation "
                                "entry."
                            ),
                        ),
                        preferences_grid_base.PreferenceActionDoc(
                            label=guilabels.DICTIONARY_DELETE,
                            summary="Removes the selected pronunciation entry.",
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, manager: PronunciationDictionaryManager, script: default.Script) -> None:
        super().__init__(guilabels.PRONUNCIATION)
        self._manager: PronunciationDictionaryManager = manager
        self._script: default.Script = script
        self._initializing: bool = True

        self._pronunciations: list[tuple[str, str]] = []
        self._inherited_keys: set[str] = set()
        self._deleted_inherited_keys: set[str] = set()
        self._listbox: Gtk.ListBox | None = None
        self._has_unsaved_changes: bool = False
        self._loaded_from_settings: bool = False
        self._pending_build_id: int = 0
        self._pending_build_index: int = 0

        self._build()
        # Build rows lazily once the page is mapped in idle-time chunks. With thousands of entries,
        # mapping the page all at once floods AT-SPI with state-changed:showing events and blocks
        # main loop for several seconds. Chunking spreads that flood across idle ticks.
        self.connect("map", self._on_map)
        self.connect("destroy", self._on_destroy)
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

        # Suppress pronunciation substitution while editing entries
        self._listbox.connect("realize", self._on_listbox_realize)
        self._listbox.connect("unrealize", self._on_listbox_unrealize)

        scrolled_window = self._create_scrolled_window(self._listbox)
        self.attach(scrolled_window, 0, row, 1, 1)

    def _create_two_label_row(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        left_label_text: str,
        right_label_text: str,
        edit_handler: Callable[[Gtk.Button], None] | None = None,
        delete_handler: Callable[[Gtk.Button], None] | None = None,
        include_top_separator: bool = True,
        left_label_size_group: Gtk.SizeGroup | None = None,
    ) -> Gtk.ListBoxRow:
        """Create a single listbox row with two labels and optional edit/delete buttons."""

        actions = []
        if delete_handler:
            actions.append(
                preferences_grid_base.ListRowAction(
                    "delete",
                    guilabels.DICTIONARY_DELETE,
                    delete_handler,
                    "user-trash-symbolic",
                )
            )
        if edit_handler:
            actions.append(
                preferences_grid_base.ListRowAction(
                    "edit",
                    guilabels.DIALOG_EDIT,
                    edit_handler,
                    "document-edit-symbolic",
                )
            )

        row, _left_label, _right_label, action_buttons = self._create_action_list_row(
            left_label_text,
            right_label_text,
            actions,
            include_top_separator=include_top_separator,
            primary_label_size_group=left_label_size_group,
        )

        row.delete_button = action_buttons.get("delete")
        row.edit_button = action_buttons.get("edit")

        return row

    def _create_row(
        self,
        phrase: str,
        substitution: str,
        row_index: int,
        include_top_separator: bool = True,
    ) -> Gtk.ListBoxRow:
        """Create a ListBoxRow for a pronunciation entry."""

        row = self._create_two_label_row(
            phrase,
            substitution,
            edit_handler=self._on_edit_clicked,
            delete_handler=self._on_delete_clicked,
            include_top_separator=include_top_separator,
        )

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
        key = phrase.lower()
        if key in self._inherited_keys:
            self._deleted_inherited_keys.add(key)
            self._inherited_keys.discard(key)
        del self._pronunciations[row_index]
        self._has_unsaved_changes = True
        self.refresh()

        script = script_manager.get_manager().get_active_script()
        if script:
            presentation_manager.get_manager().present_message(
                messages.PRONUNCIATION_DELETED % phrase,
            )

    def _on_listbox_realize(self, _widget: Gtk.Widget) -> None:
        """Suppress pronunciation substitution while editing entries."""

        self._manager.suppress()

    def _on_listbox_unrealize(self, _widget: Gtk.Widget) -> None:
        """Restore pronunciation substitution when done editing entries."""

        self._manager.unsuppress()

    def _on_add_clicked(self, _button: Gtk.Button) -> None:
        """Handle Add button click to open add dialog."""

        self._show_add_dialog()

    def _show_add_dialog(self) -> None:
        """Show dialog to add a new pronunciation."""

        dialog, add_button = self._create_header_bar_dialog(
            guilabels.ADD_NEW_PRONUNCIATION,
            guilabels.DIALOG_CANCEL,
            guilabels.DIALOG_ADD,
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
            dlg.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()
        add_button.grab_default()
        phrase_entry.grab_focus()

    def _show_edit_dialog(  # pylint: disable=too-many-locals
        self,
        phrase: str,
        substitution: str,
        row_index: int,
    ) -> None:
        """Show dialog to edit an existing pronunciation."""

        dialog, edit_button = self._create_header_bar_dialog(
            guilabels.EDIT_PRONUNCIATION,
            guilabels.DIALOG_CANCEL,
            guilabels.DIALOG_EDIT,
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
                    self._inherited_keys.discard(phrase.lower())
                    self._pronunciations[row_index] = (new_phrase, new_substitution)
                    self._has_unsaved_changes = True
                    self.refresh()
            dlg.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()
        edit_button.grab_default()
        phrase_entry.grab_focus()

    def reload(self) -> None:
        """Reload settings from the manager and refresh the UI."""

        self._pronunciations = []
        self._inherited_keys = set()
        self._deleted_inherited_keys = set()
        self._loaded_from_settings = False
        self._has_unsaved_changes = False
        self.refresh()

    def save_settings(  # pylint: disable=too-many-branches
        self,
        profile: str = "",
        app_name: str = "",
    ) -> dict[str, list[str]]:
        """Save settings and return a dictionary of the current values for those settings."""

        self._manager.set_dictionary({})
        result: dict[str, list[str]] = {}

        for phrase, substitution in self._pronunciations:
            if phrase and substitution:
                self._manager.set_pronunciation(phrase, substitution)
                result[phrase.lower()] = [phrase, substitution]

        self._has_unsaved_changes = False

        if profile:
            registry = gsettings_registry.get_registry()
            parent_pronunciations: dict[str, str] = {}
            if profile != "default" or app_name:
                if profile != "default":
                    parent_pronunciations |= registry.get_pronunciations("default", "")
                if app_name:
                    parent_pronunciations |= registry.get_pronunciations(profile, "")

            diff: dict[str, str] = {}
            for key, value in result.items():
                replacement = value[1]
                if parent_pronunciations.get(key) != replacement:
                    diff[key] = replacement
            for key in self._deleted_inherited_keys:
                if key in parent_pronunciations:
                    diff[key] = ""

            pron_gs = registry.get_settings("pronunciations", profile, "pronunciations", app_name)
            if pron_gs is not None:
                if diff:
                    pron_gs.set_value("entries", GLib.Variant("a{ss}", diff))
                elif pron_gs.get_user_value("entries") is not None:
                    pron_gs.reset("entries")

        return result

    def refresh(self) -> None:
        """Update listbox to reflect current pronunciation list."""

        if self._listbox is None:
            return

        self._cancel_pending_build()
        self._initializing = True

        for child in self._listbox.get_children():
            self._listbox.remove(child)
        self._pending_build_index = 0

        if not self._loaded_from_settings:
            self._loaded_from_settings = True
            registry = gsettings_registry.get_registry()
            profile = registry.get_active_profile()
            app_name = ""
            if self._script and self._script.app:
                from .ax_object import AXObject  # pylint: disable=import-outside-toplevel

                app_name = AXObject.get_name(self._script.app)

            pronunciation_dict = registry.layered_lookup(
                "pronunciations",
                "entries",
                "a{ss}",
                app_name=app_name or None,
                default={},
            )
            local_dict = registry.get_pronunciations(profile, app_name)
            self._inherited_keys = set(pronunciation_dict.keys()) - set(local_dict.keys())

            for key in sorted(pronunciation_dict.keys()):
                if pronunciation_dict[key]:
                    self._pronunciations.append((key, pronunciation_dict[key]))

        if self._pronunciations:
            if self.get_mapped():
                self._schedule_build_chunk()
        else:
            empty_row = self._create_info_row(guilabels.DICTIONARY_EMPTY)
            self._listbox.add(empty_row)
            empty_row.show_all()

        self._initializing = False

    def _on_map(self, _widget: Gtk.Widget) -> None:
        """Start (or resume) the chunked row build when the page becomes visible."""

        if self._pending_build_id != 0:
            return
        if self._pending_build_index < len(self._pronunciations):
            self._schedule_build_chunk()

    def _on_destroy(self, _widget: Gtk.Widget) -> None:
        """Cancel any in-flight chunked build before the widget goes away."""

        self._cancel_pending_build()
        self._listbox = None

    def _cancel_pending_build(self) -> None:
        """Stop any in-flight chunked row build."""

        if self._pending_build_id != 0:
            GLib.source_remove(self._pending_build_id)
            self._pending_build_id = 0

    def _schedule_build_chunk(self) -> None:
        """Queue an idle callback to add the next batch of rows."""

        self._pending_build_id = GLib.idle_add(self._build_chunk)

    def _build_chunk(self) -> bool:
        """Add up to BUILD_BATCH_SIZE rows. Returns True to keep idling."""

        if self._listbox is None:
            self._pending_build_id = 0
            return False

        end = min(self._pending_build_index + self.BUILD_BATCH_SIZE, len(self._pronunciations))
        for index in range(self._pending_build_index, end):
            phrase, substitution = self._pronunciations[index]
            row = self._create_row(
                phrase,
                substitution,
                index,
                include_top_separator=index > 0,
            )
            self._listbox.add(row)
            row.show_all()
        self._pending_build_index = end

        if end >= len(self._pronunciations):
            self._pending_build_id = 0
            return False
        return True
