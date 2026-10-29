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

"""A GTK4 notebook whose pages hold focusable widgets and static text."""

import sys

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk

APP_TITLE = "OrcaWidgetNotebook"


def _build_menu_bar(window: Gtk.Window) -> Gtk.PopoverMenuBar:
    actions = Gio.SimpleActionGroup()
    for name in ("new", "open", "quit", "report", "summary"):
        actions.add_action(Gio.SimpleAction.new(name, None))
    window.insert_action_group("win", actions)
    recent = Gio.Menu()
    recent.append("_Report", "win.report")
    recent.append("_Summary", "win.summary")
    file_menu = Gio.Menu()
    file_menu.append("_New", "win.new")
    file_menu.append("_Open", "win.open")
    file_menu.append_submenu("_Recent", recent)
    file_menu.append("_Quit", "win.quit")
    menu = Gio.Menu()
    menu.append_submenu("_File", file_menu)
    return Gtk.PopoverMenuBar.new_from_model(menu)


class _Widgets:
    """The first notebook page: one of every common focusable widget role."""

    def __init__(self) -> None:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.page = box

        self.save_button = Gtk.Button(label="Save")
        self.bold_toggle = Gtk.ToggleButton(label="Bold")
        self.enabled_check = Gtk.CheckButton(label="Enabled")
        self.quantity_spin = Gtk.SpinButton.new_with_range(0, 100, 1)
        self.quantity_spin.update_property([Gtk.AccessibleProperty.LABEL], ["Quantity"])
        self.color_combo = Gtk.DropDown.new_from_strings(["Red", "Green", "Blue"])
        color_label = Gtk.Label.new_with_mnemonic("_Color")
        color_label.set_mnemonic_widget(self.color_combo)
        self.city_entry = Gtk.Entry()
        self.city_entry.update_property([Gtk.AccessibleProperty.LABEL], ["City"])
        self.website_link = Gtk.LinkButton.new_with_label("https://example.com", "Website")
        self.small_radio = Gtk.CheckButton(label="Small")
        self.medium_radio = Gtk.CheckButton(label="Medium", group=self.small_radio)
        self.large_radio = Gtk.CheckButton(label="Large", group=self.small_radio)
        self.level_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 10, 1)
        self.level_scale.set_draw_value(False)
        self.level_scale.update_property([Gtk.AccessibleProperty.LABEL], ["Level"])
        self.bump_button = Gtk.Button(label="Bump Quantity in 1000 ms")
        self.bump_button.connect("clicked", self._on_bump_clicked)
        self.readonly_spin = Gtk.SpinButton.new_with_range(0, 100, 1)
        self.readonly_spin.set_editable(False)
        self.readonly_spin.update_property([Gtk.AccessibleProperty.LABEL], ["Readonly"])

        for widget in (
            self.save_button,
            self.bold_toggle,
            self.enabled_check,
            self.quantity_spin,
            color_label,
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
            box.append(widget)
        self.reset()

    def _on_bump_clicked(self, _button: Gtk.Button) -> None:
        GLib.timeout_add(1000, self._bump_quantity)

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
        self.color_combo.set_selected(0)
        self.city_entry.set_text("Madrid")
        self.small_radio.set_active(True)
        self.level_scale.set_value(3)


def _build_messages_page() -> Gtk.Box:
    """A page using the accessible-description technique for static text."""

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    filter_entry = Gtk.Entry()
    filter_entry.update_property([Gtk.AccessibleProperty.LABEL], ["Filter"])
    filter_entry.update_property([Gtk.AccessibleProperty.DESCRIPTION], ["3 matches found"])
    box.append(filter_entry)

    options = Gtk.Frame(label="Options")
    options.update_property([Gtk.AccessibleProperty.DESCRIPTION], ["Review before saving"])
    content = Gtk.Box(accessible_role=Gtk.AccessibleRole.GROUP)
    content.append(Gtk.CheckButton(label="Agree"))
    options.set_child(content)
    box.append(options)

    return box


def _build_labels_page() -> Gtk.Box:
    """A page contrasting an unrelated static label with a label-for widget label."""

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    box.append(Gtk.Label(label="Disk almost full"))
    volume_label = Gtk.Label.new_with_mnemonic("_Volume")
    volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 10, 1)
    volume_scale.set_draw_value(False)
    volume_label.set_mnemonic_widget(volume_scale)
    box.append(volume_label)
    box.append(volume_scale)

    return box


def _file_row(name: str, detail: str, *, row_name: str | None = None) -> Gtk.ListBoxRow:
    row = Gtk.ListBoxRow()
    row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    row_box.append(Gtk.Label(label=name))
    row_box.append(Gtk.Label(label=detail))
    row.set_child(row_box)
    if row_name is not None:
        row.update_property([Gtk.AccessibleProperty.LABEL], [row_name])
    return row


def _build_files_page() -> Gtk.Box:
    """A page whose focusable list items exercise descendant presentation and its filter."""

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    listbox = Gtk.ListBox()
    listbox.append(_file_row("report.pdf", "shared"))
    listbox.append(_file_row("notes.txt", "private"))
    listbox.append(_file_row("Budget", "2 MB", row_name="Budget"))
    box.append(listbox)
    return box


def _build_list_availability_page() -> Gtk.Box:
    """A page with a list whose disabled rows cannot be reached with Tab."""

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    listbox = Gtk.ListBox()
    for label, sensitive in (
        ("Unavailable first", False),
        ("Available", True),
        ("Unavailable last", False),
    ):
        row = Gtk.ListBoxRow()
        row.set_child(Gtk.Label(label=label))
        row.set_sensitive(sensitive)
        listbox.append(row)
    box.append(listbox)
    box.append(Gtk.Button(label="After list"))
    return box


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    Gtk.init()
    loop = GLib.MainLoop()
    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 320)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("close-request", lambda _window: loop.quit())

    widgets = _Widgets()
    notebook = Gtk.Notebook()
    notebook.append_page(widgets.page, Gtk.Label(label="Widgets"))
    notebook.append_page(_build_messages_page(), Gtk.Label(label="Messages"))
    notebook.append_page(_build_labels_page(), Gtk.Label(label="Labels"))
    notebook.append_page(_build_files_page(), Gtk.Label(label="Files"))
    notebook.append_page(_build_list_availability_page(), Gtk.Label(label="Availability"))

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    box.append(_build_menu_bar(window))
    box.append(notebook)

    statusbar = Gtk.Box(accessible_role=Gtk.AccessibleRole.STATUS)
    statusbar.append(Gtk.Label(label="Ready. 3 items."))
    box.append(statusbar)

    window.set_child(box)

    def _reset_to_start(*_args: object) -> bool:
        widgets.reset()
        notebook.set_current_page(0)
        widgets.save_button.grab_focus()
        return True

    # F12 resets widget state and focus so one session can run every widget test.
    controller = Gtk.EventControllerKey()
    controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    controller.connect(
        "key-pressed",
        lambda _controller, keyval, _keycode, _state: keyval == Gdk.KEY_F12 and _reset_to_start(),
    )
    window.add_controller(controller)

    window.connect("map", lambda _widget: widgets.save_button.grab_focus())

    window.present()
    loop.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
