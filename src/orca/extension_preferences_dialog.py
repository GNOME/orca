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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Default preferences dialog for user extensions."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atk", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atk, Gdk, Gtk  # pylint: disable=no-name-in-module

from . import guilabels, orca_gui_helpers
from .extension_preferences import (
    ExtensionPreference,
    ExtensionPreferenceKind,
    is_supported_in_generated_dialog,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .extension import Extension


class ExtensionPreferencesDialog:
    """Default staged preferences dialog for a user extension."""

    def __init__(
        self,
        extension: Extension,
        preferences: list[ExtensionPreference],
        initial_values: dict[str, Any] | None = None,
        transient_for: Gtk.Window | None = None,
    ) -> None:
        self._extension = extension
        self._preferences = [pref for pref in preferences if is_supported_in_generated_dialog(pref)]
        initial_values = initial_values or {}
        self._values = {
            pref.key: self._normalize_value(
                pref,
                initial_values.get(
                    pref.key,
                    extension.settings.get(pref.key, default=pref.default),
                ),
            )
            for pref in self._preferences
            if self._is_setting(pref)
        }
        self._dialog, _ok_button = orca_gui_helpers.create_header_bar_dialog(
            extension.GROUP_LABEL,
            guilabels.BTN_CANCEL,
            guilabels.BTN_OK,
            transient_for=transient_for,
            width=720,
        )
        if transient_for is not None:
            transient_for.connect("destroy", self._on_parent_destroy)

        self._label_size_group = orca_gui_helpers.create_horizontal_size_group()
        self._content_height_request = 0
        self._build()
        self._dialog.set_default_size(720, self._dialog_height_request())

    @staticmethod
    def _is_setting(preference: ExtensionPreference) -> bool:
        """Return True if preference represents a stored setting."""

        return preference.kind is not ExtensionPreferenceKind.INFO

    def run(self) -> dict[str, Any] | None:
        """Run the dialog and return staged values if accepted."""

        self._dialog.show_all()
        response = self._dialog.run()
        values = dict(self._values) if response == Gtk.ResponseType.OK else None
        self._dialog.destroy()
        return values

    def _on_parent_destroy(self, *_args: Any) -> None:
        """Responds to parent destruction by closing the dialog."""

        if self._dialog.get_visible():
            self._dialog.response(Gtk.ResponseType.DELETE_EVENT)

    def _build(self) -> None:
        """Build the preference rows."""

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_hexpand(True)
        content_box.set_vexpand(True)
        orca_gui_helpers.set_margins(content_box, start=6, end=6, top=6, bottom=6)

        listbox: orca_gui_helpers.FocusManagedListBox | None = None
        listbox_row_count = 0

        def flush_listbox() -> None:
            nonlocal listbox, listbox_row_count
            if listbox is not None:
                container = listbox.get_container()
                container.set_margin_start(12)
                container.set_margin_end(12)
                content_box.pack_start(container, False, False, 0)
                self._content_height_request += self._regular_listbox_height(listbox_row_count)
                listbox = None
                listbox_row_count = 0

        for pref in self._preferences:
            if pref.kind is ExtensionPreferenceKind.INFO:
                flush_listbox()
                info_listbox = orca_gui_helpers.create_info_listbox(pref.label)
                info_listbox.set_margin_start(12)
                info_listbox.set_margin_end(12)
                content_box.pack_start(info_listbox, False, False, 0)
                self._content_height_request += 96
                continue

            if pref.kind in (
                ExtensionPreferenceKind.STRING_LIST,
                ExtensionPreferenceKind.DICTIONARY,
            ):
                flush_listbox()
                if pref.kind is ExtensionPreferenceKind.STRING_LIST:
                    section, _button = self._create_string_list_section(pref)
                else:
                    section, _button = self._create_dictionary_section(pref)
                content_box.pack_start(section, True, True, 0)
                self._content_height_request += self._editable_list_section_height(pref)
                continue

            if listbox is None:
                listbox = orca_gui_helpers.FocusManagedListBox()
                listbox.set_hexpand(True)

            row, widgets = self._create_row(pref, listbox_row_count > 0)
            listbox.add_row_with_widgets(row, widgets)
            listbox_row_count += 1

        flush_listbox()

        scrolled_window = orca_gui_helpers.create_scrolled_window(
            content_box,
            hscroll_policy=Gtk.PolicyType.NEVER,
            vscroll_policy=Gtk.PolicyType.AUTOMATIC,
            hexpand=True,
            vexpand=True,
            framed=False,
        )
        self._dialog.get_content_area().add(scrolled_window)

    @staticmethod
    def _regular_listbox_height(row_count: int) -> int:
        """Return a useful default height for a group of standard rows."""

        return max(1, row_count) * 56 + 12

    def _editable_list_section_height(self, pref: ExtensionPreference) -> int:
        """Return a useful default height for an editable list section."""

        values = self._values[pref.key]
        item_count = len(values) if isinstance(values, (dict, list)) else 0
        return 64 + self._list_section_height(item_count) + 12

    def _dialog_height_request(self) -> int:
        """Return a content-based default height for the dialog."""

        return max(260, min(800, self._content_height_request + 96))

    @staticmethod
    def _normalize_value(pref: ExtensionPreference, value: Any) -> Any:
        """Return a value supported by pref."""

        if pref.kind is ExtensionPreferenceKind.ENUM:
            values = [option_value for option_value, _label in pref.options]
            if value in values:
                return value
            if pref.default in values:
                return pref.default
            if values:
                return values[0]
            return pref.default
        if pref.kind is ExtensionPreferenceKind.STRING_LIST:
            if isinstance(value, list) and all(isinstance(item, str) for item in value):
                return list(value)
            return list(pref.default) if isinstance(pref.default, list) else []
        if pref.kind is ExtensionPreferenceKind.DICTIONARY:
            if isinstance(value, dict) and all(isinstance(key, str) for key in value):
                return dict(value)
            return dict(pref.default) if isinstance(pref.default, dict) else {}
        if pref.kind is ExtensionPreferenceKind.COLOR:
            return ExtensionPreferencesDialog._normalize_color(value, pref.default)
        return value

    @staticmethod
    def _normalize_color(value: Any, default: Any) -> str:
        """Return a valid color string."""

        if isinstance(value, str) and Gdk.color_parse(value) is not None:
            return value
        if isinstance(default, str) and Gdk.color_parse(default) is not None:
            return default
        return "#000000"

    @staticmethod
    def _list_section_height(item_count: int) -> int:
        """Return a useful default height for an editable list section."""

        return max(160, min(240, max(1, item_count) * 56))

    def _create_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.Widget, ...]]:
        """Create a row for pref."""

        if pref.kind is ExtensionPreferenceKind.BOOLEAN:
            return self._create_boolean_row(pref, include_separator)
        if pref.kind is ExtensionPreferenceKind.STRING:
            return self._create_string_row(pref, include_separator)
        if pref.kind is ExtensionPreferenceKind.PATH:
            return self._create_path_row(pref, include_separator)
        if pref.kind is ExtensionPreferenceKind.COLOR:
            return self._create_color_row(pref, include_separator)
        if pref.kind is ExtensionPreferenceKind.INTEGER:
            return self._create_integer_row(pref, include_separator)
        if pref.kind is ExtensionPreferenceKind.FLOAT:
            return self._create_float_row(pref, include_separator)
        if pref.kind is ExtensionPreferenceKind.ENUM:
            return self._create_enum_row(pref, include_separator)
        raise ValueError(f"Unsupported extension preference kind: {pref.kind}")

    def _create_boolean_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.Switch]]:
        """Create a boolean row."""

        row, switch, _label = orca_gui_helpers.create_switch_row(
            pref.label,
            lambda widget, _pspec: self._set_value(pref.key, widget.get_active()),
            bool(self._values[pref.key]),
            include_top_separator=include_separator,
            label_size_group=self._label_size_group,
        )
        return row, (switch,)

    def _create_string_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.Entry]]:
        """Create a string row."""

        entry = orca_gui_helpers.create_entry(
            str(self._values[pref.key]),
            changed_handler=lambda widget: self._set_value(pref.key, widget.get_text()),
            size_request=(280, -1),
        )
        row = orca_gui_helpers.create_labeled_entry_row(
            pref.label,
            entry,
            include_top_separator=include_separator,
            label_size_group=self._label_size_group,
        )
        return row, (entry,)

    def _create_path_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.Entry, Gtk.Button]]:
        """Create a path row with an entry and browse button."""

        entry = orca_gui_helpers.create_entry(
            str(self._values[pref.key]),
            changed_handler=lambda widget: self._set_value(pref.key, widget.get_text()),
            size_request=(280, -1),
        )
        browse_button = Gtk.Button.new_with_mnemonic(guilabels.EXTENSIONS_SETTINGS_BROWSE)
        browse_button.set_valign(Gtk.Align.CENTER)
        browse_button.connect("clicked", lambda _button: self._browse_for_path(pref, entry))

        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        input_box.set_hexpand(True)
        input_box.pack_start(entry, True, True, 0)
        input_box.pack_start(browse_button, False, False, 0)

        row, _hbox, label = orca_gui_helpers.create_row_structure(
            include_separator,
            pref.label,
            input_box,
            label_xalign=0,
            label_size_group=self._label_size_group,
            widget_expand=True,
        )
        assert label is not None
        label.set_mnemonic_widget(entry)
        orca_gui_helpers.add_labelled_by(entry, label)
        browse_button.get_accessible().set_name(
            f"{pref.label}: {guilabels.EXTENSIONS_SETTINGS_BROWSE}"
        )
        return row, (entry, browse_button)

    def _browse_for_path(self, pref: ExtensionPreference, entry: Gtk.Entry) -> None:
        """Browse for a path and put it in entry."""

        action = (
            Gtk.FileChooserAction.SELECT_FOLDER if pref.directory else Gtk.FileChooserAction.SAVE
        )
        dialog = Gtk.FileChooserDialog(
            title=pref.label,
            transient_for=self._dialog,
            action=action,
        )
        dialog.add_buttons(
            guilabels.DIALOG_CANCEL,
            Gtk.ResponseType.CANCEL,
            guilabels.BTN_OK,
            Gtk.ResponseType.OK,
        )
        dialog.set_modal(True)
        path = entry.get_text().strip()
        if path:
            expanded_path = os.path.abspath(os.path.expanduser(path))
            if pref.directory:
                dialog.set_filename(expanded_path)
            else:
                dialog.set_current_folder(os.path.dirname(expanded_path))
                dialog.set_current_name(os.path.basename(expanded_path))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename:
                entry.set_text(filename)
                self._set_value(pref.key, filename)
        dialog.destroy()

    def _create_color_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.ColorButton]]:
        """Create a color row."""

        row, color_button, _label = orca_gui_helpers.create_color_button_row(
            pref.label,
            lambda widget: self._set_value(
                pref.key,
                orca_gui_helpers.rgba_to_hex(widget.get_rgba()),
            ),
            include_top_separator=include_separator,
            label_size_group=self._label_size_group,
        )
        orca_gui_helpers.set_color_button_hex(color_button, str(self._values[pref.key]))
        return row, (color_button,)

    def _create_integer_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.SpinButton]]:
        """Create an integer row."""

        adjustment = orca_gui_helpers.create_range_adjustment(
            int(self._values[pref.key]),
            int(pref.minimum if pref.minimum is not None else 0),
            int(pref.maximum if pref.maximum is not None else 100),
        )
        row, spin, _label = orca_gui_helpers.create_spin_button_row(
            pref.label,
            adjustment,
            lambda widget: self._set_value(pref.key, widget.get_value_as_int()),
            include_top_separator=include_separator,
            label_size_group=self._label_size_group,
        )
        return row, (spin,)

    def _create_float_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.Scale]]:
        """Create a float row."""

        row, scale, _label = orca_gui_helpers.create_range_slider_row(
            pref.label,
            float(self._values[pref.key]),
            float(pref.minimum if pref.minimum is not None else 0.0),
            float(pref.maximum if pref.maximum is not None else 1.0),
            changed_handler=lambda widget: self._set_value(pref.key, widget.get_value()),
            include_top_separator=include_separator,
            digits=2,
            label_size_group=self._label_size_group,
        )
        return row, (scale,)

    def _create_enum_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, tuple[Gtk.ComboBoxText]]:
        """Create an enum row."""

        if not pref.options:
            raise ValueError(f"Enum preference {pref.key!r} has no options")

        items = [(str(value), label) for value, label in pref.options]
        row, combo, _label = orca_gui_helpers.create_combo_box_text_row(
            pref.label,
            items,
            include_top_separator=include_separator,
            changed_handler=lambda widget: self._set_value(
                pref.key,
                self._get_enum_value(pref, widget.get_active()),
            ),
            label_size_group=self._label_size_group,
        )
        values = [value for value, _label in pref.options]
        combo.set_active(values.index(self._values[pref.key]))
        return row, (combo,)

    @staticmethod
    def _get_enum_value(pref: ExtensionPreference, index: int) -> Any:
        """Return the enum value at index."""

        if 0 <= index < len(pref.options):
            return pref.options[index][0]
        return pref.default

    def _create_string_list_section(
        self,
        pref: ExtensionPreference,
    ) -> tuple[Gtk.Widget, Gtk.Button]:
        """Create a string-list section."""

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.set_hexpand(True)
        vbox.set_vexpand(True)

        listbox = orca_gui_helpers.create_framed_listbox(
            selection_mode=Gtk.SelectionMode.SINGLE,
            accessible_name=pref.label,
        )
        listbox.set_hexpand(True)
        listbox.set_vexpand(True)
        values = self._values[pref.key]
        if not isinstance(values, list):
            values = []
            self._set_value(pref.key, values)

        header_box, add_button = orca_gui_helpers.create_heading_action_box(
            pref.label,
            "list-add-symbolic",
            guilabels.EXTENSIONS_SETTINGS_NEW_ITEM,
            lambda _button: self._add_string_list_item(pref, listbox, values),
        )
        add_button.get_accessible().set_name(
            f"{pref.label}: {guilabels.EXTENSIONS_SETTINGS_NEW_ITEM}"
        )
        orca_gui_helpers.set_margins(header_box, start=12, end=12, top=12, bottom=6)

        self._populate_string_listbox(pref, listbox, values)
        scrolled_window = orca_gui_helpers.create_scrolled_window(
            listbox,
            hscroll_policy=Gtk.PolicyType.NEVER,
            vscroll_policy=Gtk.PolicyType.AUTOMATIC,
            size_request=(500, self._list_section_height(len(values))),
            hexpand=True,
            vexpand=True,
        )
        scrolled_window.set_margin_start(12)
        scrolled_window.set_margin_end(12)
        scrolled_window.set_margin_bottom(12)

        vbox.pack_start(header_box, False, False, 0)
        vbox.pack_start(scrolled_window, True, True, 0)
        return vbox, add_button

    def _populate_string_listbox(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: list[str],
    ) -> None:
        """Populate listbox with string-list values."""

        for child in listbox.get_children():
            listbox.remove(child)
        for index, value in enumerate(values):

            def delete_handler(_button: Gtk.Button, position: int = index) -> None:
                self._delete_string_list_item(pref, listbox, values, position)

            def edit_handler(_button: Gtk.Button, position: int = index) -> None:
                self._edit_string_list_item(pref, listbox, values, position)

            actions = (
                orca_gui_helpers.ListRowAction(
                    "delete",
                    guilabels.EXTENSIONS_SETTINGS_DELETE_ITEM,
                    delete_handler,
                    "user-trash-symbolic",
                ),
                orca_gui_helpers.ListRowAction(
                    "edit",
                    guilabels.DIALOG_EDIT,
                    edit_handler,
                    "document-edit-symbolic",
                ),
            )
            row, _primary_label, _secondary_label, _action_buttons = (
                orca_gui_helpers.create_action_list_row(
                    value,
                    "",
                    actions,
                    include_top_separator=index > 0,
                )
            )
            listbox.add(row)
        listbox.show_all()

    def _add_string_list_item(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: list[str],
    ) -> None:
        """Add a string-list item."""

        value = self._run_string_list_item_editor(
            guilabels.EXTENSIONS_SETTINGS_NEW_ITEM,
            "",
            values,
            None,
            pref.item_validator,
            pref.item_error,
        )
        if value is None:
            return
        values.append(value)
        self._populate_string_listbox(pref, listbox, values)

    def _edit_string_list_item(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: list[str],
        index: int,
    ) -> None:
        """Edit a string-list item."""

        value = self._run_string_list_item_editor(
            guilabels.DIALOG_EDIT,
            values[index],
            values,
            index,
            pref.item_validator,
            pref.item_error,
        )
        if value is None:
            return
        values[index] = value
        self._populate_string_listbox(pref, listbox, values)

    def _delete_string_list_item(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: list[str],
        index: int,
    ) -> None:
        """Delete a string-list item."""

        del values[index]
        self._populate_string_listbox(pref, listbox, values)

    def _create_dictionary_section(
        self,
        pref: ExtensionPreference,
    ) -> tuple[Gtk.Widget, Gtk.Button]:
        """Create a dictionary section."""

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.set_hexpand(True)
        vbox.set_vexpand(True)

        listbox = orca_gui_helpers.create_framed_listbox(
            selection_mode=Gtk.SelectionMode.SINGLE,
            accessible_name=pref.label,
        )
        listbox.set_hexpand(True)
        listbox.set_vexpand(True)
        values = self._values[pref.key]
        if not isinstance(values, dict):
            values = {}
            self._set_value(pref.key, values)

        header_box, add_button = orca_gui_helpers.create_heading_action_box(
            pref.label,
            "list-add-symbolic",
            guilabels.EXTENSIONS_SETTINGS_NEW_ITEM,
            lambda _button: self._add_dictionary_item(pref, listbox, values),
        )
        add_button.get_accessible().set_name(
            f"{pref.label}: {guilabels.EXTENSIONS_SETTINGS_NEW_ITEM}"
        )
        orca_gui_helpers.set_margins(header_box, start=12, end=12, top=12, bottom=6)

        self._populate_dictionary_listbox(pref, listbox, values)
        scrolled_window = orca_gui_helpers.create_scrolled_window(
            listbox,
            hscroll_policy=Gtk.PolicyType.NEVER,
            vscroll_policy=Gtk.PolicyType.AUTOMATIC,
            size_request=(500, self._list_section_height(len(values))),
            hexpand=True,
            vexpand=True,
        )
        scrolled_window.set_margin_start(12)
        scrolled_window.set_margin_end(12)
        scrolled_window.set_margin_bottom(12)

        vbox.pack_start(header_box, False, False, 0)
        vbox.pack_start(scrolled_window, True, True, 0)
        return vbox, add_button

    def _populate_dictionary_listbox(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: dict[str, Any],
    ) -> None:
        """Populate listbox with dictionary values."""

        for child in listbox.get_children():
            listbox.remove(child)
        for index, (key, value) in enumerate(values.items()):

            def delete_handler(_button: Gtk.Button, item_key: str = key) -> None:
                self._delete_dictionary_item(pref, listbox, values, item_key)

            def edit_handler(_button: Gtk.Button, item_key: str = key) -> None:
                self._edit_dictionary_item(pref, listbox, values, item_key)

            actions = (
                orca_gui_helpers.ListRowAction(
                    "delete",
                    guilabels.EXTENSIONS_SETTINGS_DELETE_ITEM,
                    delete_handler,
                    "user-trash-symbolic",
                ),
                orca_gui_helpers.ListRowAction(
                    "edit",
                    guilabels.DIALOG_EDIT,
                    edit_handler,
                    "document-edit-symbolic",
                ),
            )
            row, _primary_label, _secondary_label, _action_buttons = (
                orca_gui_helpers.create_action_list_row(
                    key,
                    str(value),
                    actions,
                    include_top_separator=index > 0,
                )
            )
            listbox.add(row)
        listbox.show_all()

    def _add_dictionary_item(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: dict[str, Any],
    ) -> None:
        """Add a dictionary item."""

        result = self._run_dictionary_item_editor(pref, "", "", values, None)
        if result is None:
            return
        key, value = result
        values[key] = value
        self._set_value(pref.key, values)
        self._populate_dictionary_listbox(pref, listbox, values)

    def _edit_dictionary_item(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: dict[str, Any],
        key: str,
    ) -> None:
        """Edit a dictionary item."""

        result = self._run_dictionary_item_editor(pref, key, str(values[key]), values, key)
        if result is None:
            return
        new_key, new_value = result
        if new_key != key:
            del values[key]
        values[new_key] = new_value
        self._set_value(pref.key, values)
        self._populate_dictionary_listbox(pref, listbox, values)

    def _delete_dictionary_item(
        self,
        pref: ExtensionPreference,
        listbox: Gtk.ListBox,
        values: dict[str, Any],
        key: str,
    ) -> None:
        """Delete a dictionary item."""

        del values[key]
        self._set_value(pref.key, values)
        self._populate_dictionary_listbox(pref, listbox, values)

    def _run_string_list_item_editor(
        self,
        title: str,
        value: str,
        values: list[str],
        current_index: int | None,
        validator: Callable[[str], bool] | None = None,
        validation_error: str = "",
    ) -> str | None:
        """Run the string-list item editor with duplicate validation."""

        def item_is_duplicate(text: str) -> bool:
            text = text.strip()
            return any(index != current_index and item == text for index, item in enumerate(values))

        def is_valid(text: str) -> bool:
            text = text.strip()
            if item_is_duplicate(text):
                return False
            return validator is None or validator(text)

        def error_message(text: str) -> str:
            if item_is_duplicate(text):
                return guilabels.EXTENSIONS_SETTINGS_DUPLICATE_ITEM
            return validation_error or guilabels.EXTENSIONS_SETTINGS_INVALID_ITEM

        return self._run_string_editor(title, value, is_valid, error_message)

    def _run_dictionary_item_editor(
        self,
        pref: ExtensionPreference,
        key: str,
        value: str,
        values: dict[str, Any],
        current_key: str | None,
    ) -> tuple[str, str] | None:
        """Run the dictionary item editor with duplicate validation."""

        title = (
            guilabels.EXTENSIONS_SETTINGS_NEW_ITEM if current_key is None else guilabels.DIALOG_EDIT
        )
        ok_label = guilabels.DIALOG_ADD if current_key is None else guilabels.DIALOG_EDIT
        dialog, ok_button = orca_gui_helpers.create_header_bar_dialog(
            title,
            guilabels.DIALOG_CANCEL,
            ok_label,
            transient_for=self._dialog,
            width=560,
        )

        def key_is_duplicate(text: str) -> bool:
            text = text.strip()
            return any(item_key != current_key and item_key == text for item_key in values)

        def key_is_valid(text: str) -> bool:
            text = text.strip()
            if not text or key_is_duplicate(text):
                return False
            return pref.item_validator is None or pref.item_validator(text)

        def value_is_valid(text: str) -> bool:
            text = text.strip()
            return bool(text) and (pref.value_validator is None or pref.value_validator(text))

        def key_error_message(text: str) -> str:
            if key_is_duplicate(text):
                return guilabels.EXTENSIONS_SETTINGS_DUPLICATE_ITEM
            return pref.item_error or guilabels.EXTENSIONS_SETTINGS_INVALID_ITEM

        def value_error_message() -> str:
            return pref.value_error or guilabels.EXTENSIONS_SETTINGS_INVALID_VALUE

        key_state = {"is_invalid": False}
        value_state = {"is_invalid": False}

        def update_ok_button(_widget: Gtk.Entry) -> None:
            key_valid = key_is_valid(key_entry.get_text())
            value_valid = value_is_valid(value_entry.get_text())
            key_has_text = bool(key_entry.get_text().strip())
            value_has_text = bool(value_entry.get_text().strip())
            key_is_invalid = key_has_text and not key_valid
            value_is_invalid = value_has_text and not value_valid
            ok_button.set_sensitive(key_valid and value_valid)

            key_error_label.set_text(key_error_message(key_entry.get_text()))
            key_error_label.set_visible(key_is_invalid)
            key_error_label.set_sensitive(key_is_invalid)
            key_error_label.set_can_focus(key_is_invalid)
            self._sync_validation_accessibility(
                key_entry,
                key_error_label,
                key_is_invalid,
                key_state,
            )

            value_error_label.set_text(value_error_message())
            value_error_label.set_visible(value_is_invalid)
            value_error_label.set_sensitive(value_is_invalid)
            value_error_label.set_can_focus(value_is_invalid)
            self._sync_validation_accessibility(
                value_entry,
                value_error_label,
                value_is_invalid,
                value_state,
            )

        def activate_entry(_widget: Gtk.Entry) -> None:
            if key_is_valid(key_entry.get_text()) and value_is_valid(value_entry.get_text()):
                dialog.response(Gtk.ResponseType.OK)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(6)
        grid.set_margin_start(12)
        grid.set_margin_end(12)
        grid.set_margin_top(12)
        grid.set_margin_bottom(12)

        key_label_text = pref.key_label or guilabels.EXTENSIONS_SETTINGS_DICTIONARY_NAME
        value_label_text = pref.value_label or guilabels.EXTENSIONS_SETTINGS_DICTIONARY_VALUE
        key_label = Gtk.Label(label=key_label_text)
        key_label.set_xalign(0)
        value_label = Gtk.Label(label=value_label_text)
        value_label.set_xalign(0)
        key_entry = orca_gui_helpers.create_entry(
            key,
            size_request=(-1, 40),
            changed_handler=update_ok_button,
            activate_handler=activate_entry,
        )
        value_entry = orca_gui_helpers.create_entry(
            value,
            size_request=(-1, 40),
            changed_handler=update_ok_button,
            activate_handler=activate_entry,
        )
        key_entry.set_hexpand(True)
        value_entry.set_hexpand(True)
        key_label.set_mnemonic_widget(key_entry)
        value_label.set_mnemonic_widget(value_entry)
        orca_gui_helpers.add_labelled_by(key_entry, key_label)
        orca_gui_helpers.add_labelled_by(value_entry, value_label)
        grid.attach(key_label, 0, 0, 1, 1)
        grid.attach(key_entry, 1, 0, 1, 1)
        grid.attach(value_label, 0, 2, 1, 1)
        grid.attach(value_entry, 1, 2, 1, 1)

        key_error_label = self._create_error_label(key_error_message(key))
        value_error_label = self._create_error_label(value_error_message())
        grid.attach(key_error_label, 0, 1, 2, 1)
        grid.attach(value_error_label, 0, 3, 2, 1)

        dialog.get_content_area().pack_start(grid, True, True, 0)
        update_ok_button(key_entry)
        dialog.show_all()
        update_ok_button(key_entry)
        key_entry.grab_focus()
        response = dialog.run()
        self._sync_validation_accessibility(key_entry, key_error_label, False, key_state)
        self._sync_validation_accessibility(value_entry, value_error_label, False, value_state)
        result = (
            (key_entry.get_text().strip(), value_entry.get_text().strip())
            if response == Gtk.ResponseType.OK
            else None
        )
        dialog.destroy()
        return result

    def _run_string_editor(
        self,
        title: str,
        value: str,
        validator: Callable[[str], bool] | None = None,
        validation_error: str | Callable[[str], str] = "",
    ) -> str | None:
        """Run a one-entry string editor."""

        dialog, ok_button = orca_gui_helpers.create_header_bar_dialog(
            title,
            guilabels.DIALOG_CANCEL,
            guilabels.DIALOG_ADD if not value else guilabels.DIALOG_EDIT,
            transient_for=self._dialog,
            width=560,
        )

        def is_valid(text: str) -> bool:
            text = text.strip()
            return bool(text) and (validator is None or validator(text))

        validation_state = {"is_invalid": False}

        def get_validation_error(text: str) -> str:
            if callable(validation_error):
                return validation_error(text)
            return validation_error or guilabels.EXTENSIONS_SETTINGS_INVALID_ITEM

        def update_ok_button(widget: Gtk.Entry) -> None:
            valid = is_valid(widget.get_text())
            has_text = bool(widget.get_text().strip())
            is_invalid = has_text and not valid
            ok_button.set_sensitive(valid)
            error_label.set_text(get_validation_error(widget.get_text()))
            error_label.set_visible(is_invalid)
            error_label.set_sensitive(is_invalid)
            error_label.set_can_focus(is_invalid)
            self._sync_validation_accessibility(
                widget,
                error_label,
                is_invalid,
                validation_state,
            )

        def activate_entry(widget: Gtk.Entry) -> None:
            if is_valid(widget.get_text()):
                dialog.response(Gtk.ResponseType.OK)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(6)
        grid.set_margin_start(12)
        grid.set_margin_end(12)
        grid.set_margin_top(12)
        grid.set_margin_bottom(12)

        label = Gtk.Label(label=title)
        label.set_xalign(0)
        entry = orca_gui_helpers.create_entry(
            value,
            size_request=(-1, 40),
            changed_handler=update_ok_button,
            activate_handler=activate_entry,
        )
        entry.set_hexpand(True)
        label.set_mnemonic_widget(entry)
        orca_gui_helpers.add_labelled_by(entry, label)
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(entry, 1, 0, 1, 1)

        error_label = self._create_error_label(get_validation_error(value))
        grid.attach(error_label, 0, 1, 2, 1)

        dialog.get_content_area().pack_start(grid, True, True, 0)
        update_ok_button(entry)
        dialog.show_all()
        is_invalid = bool(value.strip()) and not is_valid(value)
        error_label.set_visible(is_invalid)
        error_label.set_sensitive(is_invalid)
        error_label.set_can_focus(is_invalid)
        self._sync_validation_accessibility(entry, error_label, is_invalid, validation_state)
        entry.grab_focus()
        response = dialog.run()
        self._sync_validation_accessibility(entry, error_label, False, validation_state)
        result = entry.get_text().strip() if response == Gtk.ResponseType.OK else None
        dialog.destroy()
        return result or None

    @staticmethod
    def _create_error_label(message: str) -> Gtk.Label:
        """Create an error label for a generated settings editor."""

        label = Gtk.Label(label=message)
        label.set_can_focus(False)
        label.set_selectable(True)
        label.get_accessible().set_role(Atk.Role.LABEL)
        label.set_xalign(0)
        label.set_line_wrap(True)
        label.set_max_width_chars(60)
        label.get_style_context().add_class("error")
        return label

    @staticmethod
    def _sync_validation_accessibility(
        entry: Gtk.Entry,
        error_label: Gtk.Label,
        is_invalid: bool,
        validation_state: dict[str, bool],
    ) -> None:
        """Sync validation state and error-message relations."""

        entry_accessible = entry.get_accessible()
        error_accessible = error_label.get_accessible()
        if entry_accessible is None or error_accessible is None:
            return

        previous_is_invalid = validation_state["is_invalid"]
        if previous_is_invalid != is_invalid:
            entry_accessible.notify_state_change(Atk.StateType.INVALID_ENTRY, is_invalid)
            validation_state["is_invalid"] = is_invalid

        ExtensionPreferencesDialog._remove_relation(
            entry_accessible,
            Atk.RelationType.ERROR_MESSAGE,
        )
        ExtensionPreferencesDialog._remove_relation(
            error_accessible,
            Atk.RelationType.ERROR_FOR,
        )
        if is_invalid:
            entry_accessible.ref_relation_set().add_relation_by_type(
                Atk.RelationType.ERROR_MESSAGE,
                error_accessible,
            )
            error_accessible.ref_relation_set().add_relation_by_type(
                Atk.RelationType.ERROR_FOR,
                entry_accessible,
            )

    @staticmethod
    def _remove_relation(accessible: Atk.Object, relation_type: Atk.RelationType) -> None:
        """Remove relation_type from accessible if present."""

        relation_set = accessible.ref_relation_set()
        relation = relation_set.get_relation_by_type(relation_type)
        if relation is not None:
            relation_set.remove(relation)

    def _set_value(self, key: str, value: Any) -> None:
        """Set a staged value."""

        self._values[key] = value
