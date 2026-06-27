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

from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # pylint: disable=no-name-in-module

from . import guilabels, orca_gui_helpers
from .extension_preferences import (
    ExtensionPreference,
    ExtensionPreferenceKind,
    is_supported_in_generated_dialog,
)

if TYPE_CHECKING:
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
            for pref in preferences
        }
        self._dialog, _ok_button = orca_gui_helpers.create_header_bar_dialog(
            extension.GROUP_LABEL,
            guilabels.BTN_CANCEL,
            guilabels.BTN_OK,
            transient_for=transient_for,
            width=560,
        )
        self._listbox = orca_gui_helpers.FocusManagedListBox()
        self._listbox.set_margin_top(6)
        self._listbox.set_margin_bottom(6)
        self._listbox.set_margin_start(6)
        self._listbox.set_margin_end(6)
        self._label_size_group = orca_gui_helpers.create_horizontal_size_group()
        self._build()

    def run(self) -> dict[str, Any] | None:
        """Run the dialog and return staged values if accepted."""

        self._dialog.show_all()
        response = self._dialog.run()
        values = dict(self._values) if response == Gtk.ResponseType.OK else None
        self._dialog.destroy()
        return values

    def _build(self) -> None:
        """Build the preference rows."""

        for index, pref in enumerate(self._preferences):
            include_separator = index > 0
            row, widget = self._create_row(pref, include_separator)
            self._listbox.add_row_with_widget(row, widget)

        self._dialog.get_content_area().add(self._listbox.get_container())

    @staticmethod
    def _normalize_value(pref: ExtensionPreference, value: Any) -> Any:
        """Return a value supported by pref."""

        if pref.kind is not ExtensionPreferenceKind.ENUM:
            return value
        values = [option_value for option_value, _label in pref.options]
        if value in values:
            return value
        if pref.default in values:
            return pref.default
        if values:
            return values[0]
        return pref.default

    def _create_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, Gtk.Widget]:
        """Create a row for pref."""

        if pref.kind is ExtensionPreferenceKind.BOOLEAN:
            return self._create_boolean_row(pref, include_separator)
        if pref.kind is ExtensionPreferenceKind.STRING:
            return self._create_string_row(pref, include_separator)
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
    ) -> tuple[Gtk.ListBoxRow, Gtk.Switch]:
        """Create a boolean row."""

        row, switch, _label = orca_gui_helpers.create_switch_row(
            pref.label,
            lambda widget, _pspec: self._set_value(pref.key, widget.get_active()),
            bool(self._values[pref.key]),
            include_top_separator=include_separator,
            label_size_group=self._label_size_group,
        )
        return row, switch

    def _create_string_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, Gtk.Entry]:
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
        return row, entry

    def _create_integer_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, Gtk.SpinButton]:
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
        return row, spin

    def _create_float_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, Gtk.Scale]:
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
        return row, scale

    def _create_enum_row(
        self,
        pref: ExtensionPreference,
        include_separator: bool,
    ) -> tuple[Gtk.ListBoxRow, Gtk.ComboBoxText]:
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
        return row, combo

    @staticmethod
    def _get_enum_value(pref: ExtensionPreference, index: int) -> Any:
        """Return the enum value at index."""

        if 0 <= index < len(pref.options):
            return pref.options[index][0]
        return pref.default

    def _set_value(self, key: str, value: Any) -> None:
        """Set a staged value."""

        self._values[key] = value
