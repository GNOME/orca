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

# pylint: disable=no-member
# pylint: disable=too-many-instance-attributes

"""A GTK3 notebook whose pages hold focusable widgets and static text."""

import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaWidgetNotebook"


def _build_menu_bar() -> Gtk.MenuBar:
    menu_bar = Gtk.MenuBar()
    file_item = Gtk.MenuItem.new_with_mnemonic("_File")
    file_menu = Gtk.Menu()
    file_item.set_submenu(file_menu)
    for label in ("_New", "_Open", "_Quit"):
        file_menu.append(Gtk.MenuItem.new_with_mnemonic(label))
    menu_bar.append(file_item)
    return menu_bar


class _Widgets:
    """The first notebook page: one of every common focusable widget role."""

    def __init__(self) -> None:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.page = box

        self.save_button = Gtk.Button(label="Save")
        self.bold_toggle = Gtk.ToggleButton(label="Bold")
        self.enabled_check = Gtk.CheckButton(label="Enabled")
        self.quantity_spin = Gtk.SpinButton.new_with_range(0, 100, 1)
        self.quantity_spin.get_accessible().set_name("Quantity")
        self.color_combo = Gtk.ComboBoxText()
        for color in ("Red", "Green", "Blue"):
            self.color_combo.append_text(color)
        self.color_combo.get_accessible().set_name("Color")
        self.city_entry = Gtk.Entry()
        self.city_entry.get_accessible().set_name("City")
        self.website_link = Gtk.LinkButton.new_with_label("https://example.com", "Website")
        self.small_radio = Gtk.RadioButton.new_with_label(None, "Small")
        self.medium_radio = Gtk.RadioButton.new_with_label_from_widget(self.small_radio, "Medium")
        self.large_radio = Gtk.RadioButton.new_with_label_from_widget(self.small_radio, "Large")
        self.level_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 10, 1)
        self.level_scale.set_draw_value(False)
        self.level_scale.get_accessible().set_name("Level")
        self.bump_button = Gtk.Button(label="Bump Quantity in 2500 ms")
        self.bump_button.connect("clicked", self._on_bump_clicked)
        self.readonly_spin = Gtk.SpinButton.new_with_range(0, 100, 1)
        self.readonly_spin.set_editable(False)
        self.readonly_spin.get_accessible().set_name("Readonly")

        for widget in (
            self.save_button,
            self.bold_toggle,
            self.enabled_check,
            self.quantity_spin,
            self.color_combo,
            self.city_entry,
            self.website_link,
            self.small_radio,
            self.medium_radio,
            self.large_radio,
            self.level_scale,
            self.bump_button,
            self.readonly_spin,
        ):
            box.pack_start(widget, False, False, 0)
        self.reset()

    def _on_bump_clicked(self, _button: Gtk.Button) -> None:
        GLib.timeout_add(2500, self._bump_quantity)

    def _bump_quantity(self) -> bool:
        value = self.quantity_spin.get_value()
        if value < self.quantity_spin.get_adjustment().get_upper():
            self.quantity_spin.set_value(value + 1)
        return False

    def reset(self) -> None:
        """Restores every widget to its initial state so a session can be reused."""

        self.bold_toggle.set_active(False)
        self.enabled_check.set_active(False)
        self.quantity_spin.set_value(75)
        self.readonly_spin.set_value(25)
        self.color_combo.set_active(0)
        self.city_entry.set_text("Madrid")
        self.small_radio.set_active(True)
        self.level_scale.set_value(3)


def _build_messages_page() -> Gtk.Box:
    """A page using the accessible-description technique for static text."""

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    filter_entry = Gtk.Entry()
    filter_entry.get_accessible().set_name("Filter")
    filter_entry.get_accessible().set_description("3 matches found")
    box.pack_start(filter_entry, False, False, 0)

    options = Gtk.Frame(label="Options")
    options.get_accessible().set_description("Review before saving")
    options.add(Gtk.CheckButton(label="Agree"))
    box.pack_start(options, False, False, 0)

    return box


def _build_labels_page() -> Gtk.Box:
    """A page contrasting an unrelated static label with a label-for widget label."""

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    box.pack_start(Gtk.Label(label="Disk almost full"), False, False, 0)
    volume_label = Gtk.Label.new_with_mnemonic("_Volume")
    volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 10, 1)
    volume_scale.set_draw_value(False)
    volume_label.set_mnemonic_widget(volume_scale)
    box.pack_start(volume_label, False, False, 0)
    box.pack_start(volume_scale, False, False, 0)

    return box


def _file_row(name: str, detail: str, *, row_name: str | None = None) -> Gtk.ListBoxRow:
    row = Gtk.ListBoxRow()
    row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    row_box.pack_start(Gtk.Label(label=name), False, False, 0)
    row_box.pack_start(Gtk.Label(label=detail), False, False, 0)
    row.add(row_box)
    if row_name is not None:
        row.get_accessible().set_name(row_name)
    return row


def _build_files_page() -> Gtk.Box:
    """A page whose focusable list items exercise descendant presentation and its filter."""

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    listbox = Gtk.ListBox()
    listbox.add(_file_row("report.pdf", "shared"))
    listbox.add(_file_row("notes.txt", "private"))
    listbox.add(_file_row("Budget", "2 MB", row_name="Budget"))
    box.pack_start(listbox, True, True, 0)
    return box


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 320)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)

    widgets = _Widgets()
    notebook = Gtk.Notebook()
    notebook.append_page(widgets.page, Gtk.Label(label="Widgets"))
    notebook.append_page(_build_messages_page(), Gtk.Label(label="Messages"))
    notebook.append_page(_build_labels_page(), Gtk.Label(label="Labels"))
    notebook.append_page(_build_files_page(), Gtk.Label(label="Files"))

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    box.pack_start(_build_menu_bar(), False, False, 0)
    box.pack_start(notebook, True, True, 0)

    statusbar = Gtk.Statusbar()
    statusbar.push(statusbar.get_context_id("main"), "Ready. 3 items.")
    box.pack_start(statusbar, False, False, 0)

    window.add(box)

    def _reset_to_start(*_args: object) -> bool:
        widgets.reset()
        notebook.set_current_page(0)
        widgets.save_button.grab_focus()
        return True

    # F12 resets widget state and focus so one session can run every widget test.
    accel_group = Gtk.AccelGroup()
    window.add_accel_group(accel_group)
    reset_key, reset_mods = Gtk.accelerator_parse("F12")
    accel_group.connect(reset_key, reset_mods, Gtk.AccelFlags.VISIBLE, _reset_to_start)

    window.connect("map", lambda _widget: widgets.save_button.grab_focus())

    window.show_all()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
