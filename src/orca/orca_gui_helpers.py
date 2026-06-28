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

"""Shared helpers for Orca GTK user interfaces."""

# pylint: disable=no-member
# pylint: disable=too-many-arguments
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import gi

gi.require_version("Atk", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atk, Gdk, Gio, GLib, Gtk  # pylint: disable=no-name-in-module

from . import debug

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import Any


@dataclass
class AppearanceProviders:
    """CSS providers for conditional appearance settings."""

    hc: Gtk.CssProvider
    dark: Gtk.CssProvider
    shapes: Gtk.CssProvider | None = None


@dataclass(frozen=True)
class ListRowAction:
    """Action button metadata for custom list rows."""

    name: str
    label: str
    callback: Callable[[Gtk.Button], None]
    icon_name: str | None = None


_BASE_CSS = b"""
    decoration {
        border-radius: 15px;
    }
    @define-color orca_sidebar_bg shade(@theme_bg_color, 0.98);
    list.frame {
        border-color: alpha(@theme_fg_color, 0.15);
    }
    .orca-left-headerbar {
        background-color: @orca_sidebar_bg;
        background-image: none;
        border-bottom-width: 0;
    }
    .orca-panel-headerbar {
        background-color: @theme_bg_color;
        background-image: none;
        border-bottom-width: 0;
    }
    .orca-sidebar {
        background-color: @orca_sidebar_bg;
    }
    .orca-sidebar scrolledwindow,
    .orca-sidebar list {
        background-color: transparent;
    }
    .orca-sidebar list {
        padding: 6px 0;
    }
    .orca-sidebar list row {
        border-radius: 9px;
        min-height: 36px;
        padding: 0 8px;
        margin: 0 6px 2px;
    }
    .orca-sidebar list row:selected {
        background-color: alpha(@theme_fg_color, 0.10);
    }
    .orca-sidebar list row:selected,
    .orca-sidebar list row:selected label {
        color: @theme_fg_color;
    }
    .orca-sidebar list row:hover {
        background-color: alpha(@theme_fg_color, 0.07);
    }
    .orca-sidebar list row:selected:hover {
        background-color: alpha(@theme_fg_color, 0.13);
    }
    .orca-sidebar list row:active,
    .orca-sidebar list row:selected:active {
        background-color: alpha(@theme_fg_color, 0.19);
    }
    list.frame row:focus {
        box-shadow: inset 0 0 0 2px alpha(@theme_selected_bg_color, 0.5);
    }
"""

_HIGH_CONTRAST_CSS = b"""
    list.frame {
        border-color: alpha(@theme_fg_color, 0.4);
    }
    list separator {
        background-color: alpha(@theme_fg_color, 0.4);
    }
    .dim-label {
        opacity: 1.0;
    }
"""

_DARK_MODE_CSS = b"""
    @define-color orca_sidebar_bg @theme_bg_color;
    window.background {
        background-color: @theme_base_color;
    }
    .orca-dialog {
        background-color: @theme_base_color;
    }
    .orca-dialog-content {
        background-color: @theme_base_color;
    }
    .orca-dialog-content list.frame,
    .orca-dialog-content scrolledwindow.frame {
        border-color: alpha(@theme_fg_color, 0.35);
    }
    .orca-panel-headerbar {
        background-color: @theme_base_color;
    }
    switch slider {
        background-image: image(white);
    }
"""

_GNOME_DARK_CSS = b"""
    @define-color theme_bg_color #303030;
    @define-color theme_base_color #242424;
    @define-color orca_sidebar_bg #2e2e32;
"""

_STATUS_SHAPES_CSS = b"""
    switch image {
        color: @theme_fg_color;
    }
    switch:checked image {
        color: white;
    }
"""

_appearance_refs: list[tuple] = []


def _style_provider_priority() -> int | None:
    """Return GTK's application CSS priority, if available."""

    priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    if isinstance(priority, int):
        return priority
    return None


def sync_appearance() -> tuple | None:
    """Bridge GNOME color-scheme and high-contrast gsettings to GTK3."""

    if _appearance_refs:
        return _appearance_refs[0]

    gtk_settings = Gtk.Settings.get_default()  # pylint: disable=no-value-for-parameter
    screen = Gdk.Screen.get_default()  # pylint: disable=no-value-for-parameter
    if gtk_settings is None or screen is None:
        return None

    priority = _style_provider_priority()
    if priority is None:
        return None

    base_provider = Gtk.CssProvider()
    base_provider.load_from_data(_BASE_CSS)
    Gtk.StyleContext.add_provider_for_screen(
        screen,
        base_provider,
        priority,
    )

    providers = AppearanceProviders(
        hc=Gtk.CssProvider(),
        dark=Gtk.CssProvider(),
    )
    providers.hc.load_from_data(_HIGH_CONTRAST_CSS)
    dark_css = _DARK_MODE_CSS
    if "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP", ""):
        dark_css += _GNOME_DARK_CSS
    providers.dark.load_from_data(dark_css)

    try:
        interface_settings = Gio.Settings(schema_id="org.gnome.desktop.interface")
        a11y_settings = Gio.Settings(schema_id="org.gnome.desktop.a11y.interface")
        if "show-status-shapes" in a11y_settings.list_keys():
            shapes_provider = Gtk.CssProvider()
            shapes_provider.load_from_data(_STATUS_SHAPES_CSS)
            providers.shapes = shapes_provider
        apply_appearance(
            interface_settings,
            a11y_settings,
            gtk_settings,
            screen,
            providers,
        )

        def on_setting_changed(*_args):
            apply_appearance(
                interface_settings,
                a11y_settings,
                gtk_settings,
                screen,
                providers,
            )

        interface_settings.connect("changed::color-scheme", on_setting_changed)
        a11y_settings.connect("changed::high-contrast", on_setting_changed)
        if providers.shapes is not None:
            a11y_settings.connect("changed::show-status-shapes", on_setting_changed)
        gtk_settings.connect("notify::gtk-theme-name", on_setting_changed)
        _appearance_refs.append((interface_settings, a11y_settings, base_provider, providers))
        return _appearance_refs[0]
    except GLib.Error as error:
        msg = f"ORCA GUI: Exception syncing appearance: {error}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
    return None


def create_headerbar(title: str) -> Gtk.HeaderBar:
    """Return an Orca-styled header bar."""

    headerbar = Gtk.HeaderBar()
    headerbar.set_show_close_button(True)
    headerbar.set_title(title)
    headerbar.get_style_context().add_class("orca-panel-headerbar")
    return headerbar


def set_margins(
    widget: Gtk.Widget,
    *,
    start: int = 0,
    end: int = 0,
    top: int = 0,
    bottom: int = 0,
) -> None:
    """Set all margins on a widget at once."""

    widget.set_margin_start(start)
    widget.set_margin_end(end)
    widget.set_margin_top(top)
    widget.set_margin_bottom(bottom)


def create_row_box(spacing: int = 12, margin: int = 12) -> Gtk.Box:
    """Return a standard horizontal row box."""

    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing)
    set_margins(hbox, start=margin, end=margin, top=margin, bottom=margin)
    return hbox


def create_vertical_row_box(spacing: int = 6, margin: int = 12) -> Gtk.Box:
    """Return a standard vertical row box."""

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)
    set_margins(vbox, start=margin, end=margin, top=margin, bottom=margin)
    return vbox


def create_heading_label(text: str, margin_top: int = 12) -> Gtk.Label:
    """Return a heading label."""

    label = Gtk.Label(label=text, xalign=0)
    label.get_style_context().add_class("heading")
    label.set_margin_top(margin_top)
    label.set_margin_bottom(6)
    return label


def create_heading_action_box(
    heading: str,
    icon_name: str,
    accessible_name: str,
    clicked_handler: Callable[[Gtk.Button], None],
) -> tuple[Gtk.Box, Gtk.Button]:
    """Return a heading row with a trailing icon button."""

    header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    header_box.set_margin_bottom(6)

    title_label = create_heading_label(heading, margin_top=0)
    title_label.set_margin_bottom(0)
    title_label.set_halign(Gtk.Align.START)
    header_box.pack_start(title_label, True, True, 0)

    button = Gtk.Button.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    button.get_accessible().set_name(accessible_name)
    button.connect("clicked", clicked_handler)
    header_box.pack_end(button, False, False, 0)
    return header_box, button


def create_section_box(
    heading: str,
    *,
    margin_top: int = 12,
) -> tuple[Gtk.Box, Gtk.Box, Gtk.Label]:
    """Return a vertical section with a heading and content box."""

    section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    section_box.set_hexpand(True)

    heading_label = create_heading_label(heading, margin_top=max(0, margin_top))
    section_box.pack_start(heading_label, False, False, 0)

    content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    content_box.set_hexpand(True)
    content_box.set_margin_top(6)
    relation_set = content_box.get_accessible().ref_relation_set()
    relation_set.add(
        Atk.Relation.new([heading_label.get_accessible()], Atk.RelationType.LABELLED_BY)
    )
    section_box.pack_start(content_box, True, True, 0)
    return section_box, content_box, heading_label


def add_section_content(section_box: Gtk.Box, content_box: Gtk.Box, child: Gtk.Widget) -> None:
    """Add content to a section, preserving child expansion semantics."""

    expand = child.get_vexpand()
    content_box.pack_start(child, expand, True, 0)
    if child.get_hexpand():
        content_box.set_hexpand(True)
        section_box.set_hexpand(True)
    if expand:
        content_box.set_vexpand(True)
        section_box.set_vexpand(True)


def add_labelled_by(widget: Gtk.Widget, label: Gtk.Label) -> None:
    """Add an accessible labelled-by relation from widget to label."""

    relation_set = widget.get_accessible().ref_relation_set()
    relation_set.add(Atk.Relation.new([label.get_accessible()], Atk.RelationType.LABELLED_BY))


def create_dialog(
    title: str,
    *,
    default_size: tuple[int, int] | None = None,
    buttons: Sequence[tuple[str, int]] | None = None,
    default_response: int | None = None,
    modal: bool = True,
    resizable: bool = True,
    content_margin: int = 12,
) -> Gtk.Dialog:
    """Return an Orca-styled dialog."""

    sync_appearance()
    dialog = Gtk.Dialog(title=title, modal=modal)
    dialog.get_style_context().add_class("orca-dialog")
    dialog.set_titlebar(create_headerbar(title))
    dialog.set_resizable(resizable)
    if default_size is not None:
        dialog.set_default_size(*default_size)

    if buttons is None:
        from . import guilabels  # pylint: disable=import-outside-toplevel

        buttons = ((guilabels.BTN_CLOSE, Gtk.ResponseType.CLOSE),)
    for label, response in buttons:
        dialog.add_button(label, response)
    if default_response is not None:
        dialog.set_default_response(default_response)

    content_area = dialog.get_content_area()
    content_area.get_style_context().add_class("orca-dialog-content")
    content_area.set_border_width(content_margin)

    action_area = dialog.get_action_area()
    action_area.get_style_context().add_class("orca-dialog-content")
    action_area.get_style_context().add_class("orca-dialog-action-area")
    action_area.set_margin_start(content_margin)
    action_area.set_margin_end(content_margin)
    action_area.set_margin_top(content_margin)
    action_area.set_margin_bottom(content_margin)
    return dialog


def create_header_bar_dialog(
    title: str,
    cancel_label: str,
    ok_label: str,
    *,
    transient_for: Gtk.Widget | None = None,
    width: int = 600,
) -> tuple[Gtk.Dialog, Gtk.Button]:
    """Return a header-bar dialog with Cancel and suggested OK-style actions."""

    sync_appearance()
    parent = transient_for if isinstance(transient_for, Gtk.Window) else None
    dialog = Gtk.Dialog(
        title=title,
        transient_for=parent,
        modal=True,
        destroy_with_parent=True,
        use_header_bar=True,
    )
    dialog.set_default_size(width, -1)
    dialog.set_deletable(False)
    dialog.get_style_context().add_class("orca-dialog")

    header_bar = dialog.get_header_bar()
    header_bar.get_style_context().add_class("orca-panel-headerbar")

    cancel_button = Gtk.Button.new_with_mnemonic(cancel_label)
    cancel_button.connect("clicked", lambda _button: dialog.response(Gtk.ResponseType.CANCEL))
    header_bar.pack_start(cancel_button)

    ok_button = Gtk.Button.new_with_mnemonic(ok_label)
    ok_button.get_style_context().add_class("suggested-action")
    ok_button.connect("clicked", lambda _button: dialog.response(Gtk.ResponseType.OK))
    ok_button.set_can_default(True)
    header_bar.pack_end(ok_button)

    content_area = dialog.get_content_area()
    content_area.get_style_context().add_class("orca-dialog-content")
    content_area.set_border_width(24)
    content_area.set_spacing(18)

    return dialog, ok_button


def _separator_header_func(row: Gtk.ListBoxRow, before: Gtk.ListBoxRow | None, _data) -> None:
    """Add a separator before rows after the first one."""

    if before is not None:
        row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))


def set_listbox_separators(listbox: Gtk.ListBox) -> None:
    """Add separators between rows in listbox."""

    listbox.set_header_func(_separator_header_func, None)


class FocusManagedListBox(Gtk.ListBox):
    """ListBox that manages focus for interactive widgets in rows."""

    def __init__(self, heading: str = ""):
        super().__init__()
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.get_style_context().add_class("frame")
        self.set_can_focus(False)
        set_listbox_separators(self)

        self._widgets: list[Gtk.Widget] = []
        self._rows: list[Gtk.ListBoxRow] = []
        self._exiting_backward = [False]
        self._container: Gtk.Box | None = None

        if heading:
            label = create_heading_label(heading)
            self._container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self._container.pack_start(label, False, False, 0)
            self._container.pack_start(self, False, False, 0)
            relation_set = self.get_accessible().ref_relation_set()
            relation_set.add(
                Atk.Relation.new([label.get_accessible()], Atk.RelationType.LABELLED_BY),
            )

    def get_container(self) -> Gtk.Widget:
        """Return the container to attach to a grid, or self if no heading."""

        return self._container or self

    def add_row_with_widget(self, row: Gtk.ListBoxRow, widget: Gtk.Widget) -> None:
        """Add a row with its associated interactive widget."""

        self.add_row_with_widgets(row, [widget])

    def add_row_with_widgets(self, row: Gtk.ListBoxRow, widgets: Sequence[Gtk.Widget]) -> None:
        """Add a row with associated interactive widgets."""

        if not widgets:
            self.add(row)
            self._rows.append(row)
            return

        for widget in widgets:
            widget.connect("key-press-event", self._on_widget_key_press)
        row.connect("focus-in-event", self._on_row_focus_in, widgets[0])

        self.add(row)
        self._rows.append(row)
        self._widgets.extend(widgets)

    def get_last_row(self) -> Gtk.ListBoxRow | None:
        """Return the last row that was added, or None if no rows."""

        if self._rows:
            return self._rows[-1]
        return None

    def _focus_next_sensitive_widget(self, widget: Gtk.Widget) -> bool:
        """Focus the next sensitive widget after the given one."""

        try:
            current_index = self._widgets.index(widget)
            for next_index in range(current_index + 1, len(self._widgets)):
                if self._widgets[next_index].get_sensitive():
                    self._widgets[next_index].grab_focus()
                    return True
        except ValueError:
            pass
        return False

    def _focus_prev_sensitive_widget(self, widget: Gtk.Widget) -> bool:
        """Focus the previous sensitive widget before the given one."""

        try:
            current_index = self._widgets.index(widget)
            for prev_index in range(current_index - 1, -1, -1):
                if self._widgets[prev_index].get_sensitive():
                    self._widgets[prev_index].grab_focus()
                    return True
            if self._rows:
                self._exiting_backward[0] = True
                self._rows[0].grab_focus()
        except ValueError:
            pass
        return False

    def _navigate_left_from_widget(self, _widget: Gtk.Widget) -> bool:
        """Handle Left arrow from widget. Subclasses can override."""

        return False

    def _on_widget_key_press(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handle Tab, Shift+Tab, and Left arrow to navigate."""

        if event.keyval == Gdk.KEY_Tab:
            return self._focus_next_sensitive_widget(widget)
        if event.keyval == Gdk.KEY_Left:
            return self._navigate_left_from_widget(widget)
        if event.keyval == Gdk.KEY_ISO_Left_Tab:
            return self._focus_prev_sensitive_widget(widget)
        return False

    def _on_row_focus_in(self, _row, _event, widget: Gtk.Widget) -> bool:
        """Redirect focus from row to widget."""

        if self._exiting_backward[0]:
            self._exiting_backward[0] = False
            return False

        def activate_widget():
            widget.grab_focus()

        GLib.idle_add(activate_widget)
        return False


def create_framed_listbox(
    *,
    selection_mode: Gtk.SelectionMode = Gtk.SelectionMode.NONE,
    accessible_name: str = "",
    separators: bool = False,
) -> Gtk.ListBox:
    """Return an Orca-styled framed listbox."""

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(selection_mode)
    listbox.get_style_context().add_class("frame")
    if accessible_name:
        listbox.get_accessible().set_name(accessible_name)
    if separators:
        set_listbox_separators(listbox)
    return listbox


def create_info_row(
    message: str,
    icon_name: str = "dialog-information-symbolic",
) -> Gtk.ListBoxRow:
    """Return an informational listbox row."""

    row = Gtk.ListBoxRow()
    row.set_activatable(False)
    row.set_can_focus(True)

    hbox = create_row_box()

    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DND)
    icon.set_valign(Gtk.Align.START)
    hbox.pack_start(icon, False, False, 0)

    icon_accessible = icon.get_accessible()
    if icon_accessible:
        icon_accessible.set_role(Atk.Role.IMAGE)

    label = Gtk.Label(label=message, xalign=0)
    label.set_line_wrap(True)
    label.set_max_width_chars(60)
    label.set_hexpand(True)
    hbox.pack_start(label, True, True, 0)

    row.add(hbox)

    row_accessible = row.get_accessible()
    if row_accessible:
        row_accessible.set_name(message)
        row_accessible.set_role(Atk.Role.LABEL)

    return row


def create_info_listbox(
    message: str,
    icon_name: str = "dialog-information-symbolic",
) -> Gtk.ListBox:
    """Return a framed listbox containing one informational row."""

    listbox = create_framed_listbox()
    listbox_accessible = listbox.get_accessible()
    if listbox_accessible:
        listbox_accessible.set_role(Atk.Role.PANEL)
    listbox.add(create_info_row(message, icon_name))
    listbox.set_margin_bottom(12)
    return listbox


def create_key_value_row(label_text: str, value_text: str) -> Gtk.ListBoxRow:
    """Return a non-activatable row with a label and value."""

    row = Gtk.ListBoxRow()
    row.set_activatable(False)

    hbox = create_row_box()
    label = Gtk.Label(label=f"{label_text}: {value_text}", xalign=0)
    label.set_hexpand(True)
    label.set_line_wrap(True)
    label.set_max_width_chars(72)
    hbox.pack_start(label, True, True, 0)

    row.add(hbox)
    return row


def create_key_link_row(label_text: str, uri: str) -> Gtk.ListBoxRow:
    """Return a non-activatable row with a label and link button."""

    row = Gtk.ListBoxRow()
    row.set_activatable(False)

    hbox = create_row_box(spacing=0)
    label = Gtk.Label(label=f"{label_text}: ", xalign=0)
    link_button = Gtk.LinkButton.new_with_label(uri, uri)
    link_button.get_accessible().set_name(f"{label_text}: {uri}")
    link_button.set_relief(Gtk.ReliefStyle.NONE)

    def focus_link() -> bool:
        link_button.grab_focus()
        return False

    def on_row_focus_in(*_args) -> bool:
        GLib.idle_add(focus_link)
        return False

    row.connect("focus-in-event", on_row_focus_in)
    hbox.pack_start(label, False, False, 0)
    hbox.pack_start(link_button, False, False, 0)

    row.add(hbox)
    return row


def create_row_structure(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    include_top_separator: bool = True,
    label_text: str | None = None,
    widget: Gtk.Widget | None = None,
    label_xalign: float | None = None,
    label_halign: Gtk.Align | None = None,
    label_hexpand: bool = True,
    widget_expand: bool = False,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.Box, Gtk.Label | None]:
    """Return a standard listbox row structure."""

    row = Gtk.ListBoxRow()
    row.set_activatable(False)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    if include_top_separator:
        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

    hbox = create_row_box()

    label = None
    if label_text and widget:
        label = Gtk.Label(label=label_text)
        label.set_use_underline(True)
        if label_xalign is not None:
            label.set_xalign(label_xalign)
        if label_halign is not None:
            label.set_halign(label_halign)
        label.set_hexpand(label_hexpand)
        if label_size_group is not None:
            label_size_group.add_widget(label)
        hbox.pack_start(label, label_hexpand, label_hexpand, 0)
        if not isinstance(widget, Gtk.Button):
            label.set_mnemonic_widget(widget)
        hbox.pack_end(widget, widget_expand, widget_expand, 0)

    vbox.pack_start(hbox, False, False, 0)
    row.add(vbox)
    return row, hbox, label


def create_switch_control(
    changed_handler: Callable[..., None] | None = None,
    state: bool | None = None,
    accessible_name: str = "",
    handler_args: tuple[object, ...] = (),
) -> Gtk.Switch:
    """Return an Orca-styled switch."""

    switch = Gtk.Switch()
    switch.set_valign(Gtk.Align.CENTER)
    if state is not None:
        switch.set_active(state)
    if accessible_name:
        switch.get_accessible().set_name(accessible_name)
    switch.get_accessible().set_role(Atk.Role.SWITCH)
    if changed_handler is not None:
        switch.connect("notify::active", changed_handler, *handler_args)
    return switch


def create_switch_row(
    label_text: str,
    changed_handler: Callable[..., None],
    state: bool,
    include_top_separator: bool = True,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.Switch, Gtk.Label]:
    """Return a standard listbox row with a label and switch."""

    switch = create_switch_control(changed_handler, state)
    row, _hbox, label = create_row_structure(
        include_top_separator,
        label_text,
        switch,
        label_xalign=0,
        label_size_group=label_size_group,
    )
    assert label is not None
    return row, switch, label


def create_spin_button_row(
    label_text: str,
    adjustment: Gtk.Adjustment,
    changed_handler: Callable[[Gtk.SpinButton], None] | None = None,
    include_top_separator: bool = True,
    digits: int = 0,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.SpinButton, Gtk.Label]:
    """Return a standard listbox row with a label and spin button."""

    spin = Gtk.SpinButton(adjustment=adjustment)
    spin.set_digits(digits)
    spin.set_valign(Gtk.Align.CENTER)
    if changed_handler is not None:
        spin.connect("value-changed", changed_handler)

    row, _hbox, label = create_row_structure(
        include_top_separator,
        label_text,
        spin,
        label_xalign=0,
        label_size_group=label_size_group,
    )
    assert label is not None
    return row, spin, label


def create_range_adjustment(
    value: float,
    minimum: float,
    maximum: float,
    *,
    steps: int = 100,
    page_steps: int = 10,
) -> Gtk.Adjustment:
    """Return an adjustment for numeric range controls."""

    extent = maximum - minimum
    step_increment = extent / steps if steps else extent
    page_increment = extent / page_steps if page_steps else extent
    return Gtk.Adjustment(
        value=value,
        lower=minimum,
        upper=maximum,
        step_increment=step_increment,
        page_increment=page_increment,
    )


def create_horizontal_size_group() -> Gtk.SizeGroup:
    """Return a horizontal size group."""

    return Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)


def create_slider_row(
    label_text: str,
    adjustment: Gtk.Adjustment,
    changed_handler: Callable[[Gtk.Scale], None] | None = None,
    include_top_separator: bool = True,
    digits: int = 0,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.Scale, Gtk.Label]:
    """Return a standard listbox row with a label and horizontal slider."""

    scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
    scale.set_digits(digits)
    scale.set_draw_value(True)
    scale.set_value_pos(Gtk.PositionType.RIGHT)
    scale.set_hexpand(True)
    scale.set_valign(Gtk.Align.CENTER)
    if changed_handler is not None:
        scale.connect("value-changed", changed_handler)

    row, _hbox, label = create_row_structure(
        include_top_separator,
        label_text,
        scale,
        label_halign=Gtk.Align.START,
        label_hexpand=False,
        widget_expand=True,
        label_size_group=label_size_group,
    )

    assert label is not None
    return row, scale, label


def create_range_slider_row(
    label_text: str,
    value: float,
    minimum: float,
    maximum: float,
    *,
    changed_handler: Callable[[Gtk.Scale], None] | None = None,
    include_top_separator: bool = True,
    digits: int = 0,
    steps: int = 100,
    page_steps: int = 10,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.Scale, Gtk.Label]:
    """Return a slider row for a numeric range."""

    adjustment = create_range_adjustment(
        value,
        minimum,
        maximum,
        steps=steps,
        page_steps=page_steps,
    )
    return create_slider_row(
        label_text,
        adjustment,
        changed_handler=changed_handler,
        include_top_separator=include_top_separator,
        digits=digits,
        label_size_group=label_size_group,
    )


def create_color_button_row(
    label_text: str,
    changed_handler: Callable[[Gtk.ColorButton], None] | None = None,
    include_top_separator: bool = True,
    use_alpha: bool = False,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.ColorButton, Gtk.Label]:
    """Return a standard listbox row with a label and color button."""

    color_button = Gtk.ColorButton()
    color_button.set_use_alpha(use_alpha)
    color_button.set_valign(Gtk.Align.CENTER)
    if changed_handler is not None:
        color_button.connect("color-set", changed_handler)

    row, _hbox, label = create_row_structure(
        include_top_separator,
        label_text,
        color_button,
        label_xalign=0,
        label_size_group=label_size_group,
    )
    assert label is not None
    return row, color_button, label


def set_color_button_hex(button: Gtk.ColorButton, hex_color: str) -> None:
    """Set a color button's color from a hex string."""

    button.set_color(Gdk.color_parse(hex_color))  # type: ignore[arg-type]


def rgba_to_hex(rgba: Gdk.RGBA) -> str:
    """Return a hex color string for rgba's red, green, and blue channels."""

    return f"#{int(rgba.red * 255):02x}{int(rgba.green * 255):02x}{int(rgba.blue * 255):02x}"


def create_entry(
    text: str = "",
    *,
    activates_default: bool = False,
    changed_handler: Callable[[Gtk.Entry], None] | None = None,
    activate_handler: Callable[[Gtk.Entry], None] | None = None,
    size_request: tuple[int, int] | None = None,
) -> Gtk.Entry:
    """Return a standard entry field."""

    entry = Gtk.Entry()
    if text:
        entry.set_text(text)
    entry.set_activates_default(activates_default)
    if size_request is not None:
        entry.set_size_request(*size_request)
    if changed_handler is not None:
        entry.connect("changed", changed_handler)
    if activate_handler is not None:
        entry.connect("activate", activate_handler)
    return entry


def create_labeled_entry_row(
    label_text: str,
    entry: Gtk.Entry,
    include_top_separator: bool = True,
    label_size_group: Gtk.SizeGroup | None = None,
) -> Gtk.ListBoxRow:
    """Return a standard listbox row with a label and entry field."""

    row, hbox, _label = create_row_structure(include_top_separator)
    hbox.pack_start(
        create_labeled_entry_box(label_text, entry, label_size_group),
        True,
        True,
        0,
    )
    return row


def create_labeled_entry_box(
    label_text: str,
    entry: Gtk.Entry,
    label_size_group: Gtk.SizeGroup | None = None,
    margin: int = 0,
) -> Gtk.Box:
    """Return a horizontal box with a label and entry field."""

    hbox = create_row_box(margin=margin)
    label = Gtk.Label(label=label_text, xalign=0)
    label.set_use_underline(True)
    hbox.pack_start(label, False, False, 0)

    if label_size_group:
        label_size_group.add_widget(label)

    entry.set_hexpand(True)
    label.set_mnemonic_widget(entry)
    hbox.pack_start(entry, True, True, 0)
    return hbox


def create_combo_box(
    model: Gtk.ListStore,
    changed_handler: Callable[[Gtk.ComboBox], None],
    *,
    valign: Gtk.Align | None = None,
) -> Gtk.ComboBox:
    """Return a combo box with Orca's standard text renderer setup."""

    combo = Gtk.ComboBox()
    combo.set_model(model)
    renderer = Gtk.CellRendererText()
    combo.pack_start(renderer, True)
    combo.add_attribute(renderer, "text", 0)
    combo.set_hexpand(False)
    if valign is not None:
        combo.set_valign(valign)
    combo.connect("changed", changed_handler)
    return combo


def create_combo_box_row(
    label_text: str,
    model: Gtk.ListStore,
    changed_handler: Callable[[Gtk.ComboBox], None],
    include_top_separator: bool = True,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.ComboBox, Gtk.Label]:
    """Return a standard listbox row with a label and combo box."""

    combo = create_combo_box(model, changed_handler, valign=Gtk.Align.CENTER)
    row, _hbox, label = create_row_structure(
        include_top_separator,
        label_text,
        combo,
        label_halign=Gtk.Align.START,
        label_size_group=label_size_group,
    )
    assert label is not None
    return row, combo, label


def enable_first_letter_nav(combo: Gtk.ComboBoxText) -> None:
    """Enable first-letter navigation on a ComboBoxText."""

    def on_key_press(_widget: Gtk.Widget, event: Any) -> bool:
        char = event.string.lower()
        if not char or not char.isalpha():
            return False
        model = combo.get_model()
        current = max(combo.get_active(), 0)
        for offset in range(1, len(model) + 1):
            idx = (current + offset) % len(model)
            text = (model[idx][0] or "").lower()
            if text.startswith(char):
                combo.set_active(idx)
                return True
        return False

    combo.connect("key-press-event", on_key_press)


def create_combo_box_text_row(
    label_text: str,
    items: Sequence[tuple[str, str]],
    include_top_separator: bool = True,
    changed_handler: Callable[[Gtk.ComboBoxText], None] | None = None,
    label_size_group: Gtk.SizeGroup | None = None,
) -> tuple[Gtk.ListBoxRow, Gtk.ComboBoxText, Gtk.Label | None]:
    """Return a listbox row with a label and ComboBoxText populated from items."""

    combo = Gtk.ComboBoxText()
    for item_id, display_text in items:
        combo.append(item_id, display_text)
    if items:
        combo.set_active(0)
    enable_first_letter_nav(combo)
    if changed_handler is not None:
        combo.connect("changed", changed_handler)

    row, _hbox, label = create_row_structure(
        include_top_separator,
        label_text,
        combo,
        label_xalign=0,
        label_halign=Gtk.Align.START,
        label_size_group=label_size_group,
    )

    return row, combo, label


def create_button_row(
    label_text: str,
    icon_name: str | None,
    clicked_handler: Callable[[Gtk.Button], None],
    include_top_separator: bool = True,
) -> tuple[Gtk.ListBoxRow, Gtk.Button, Gtk.Label]:
    """Return a standard listbox row with a label and button."""

    button = Gtk.Button()
    if icon_name:
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DND)
        button.set_image(icon)
    button.set_valign(Gtk.Align.CENTER)
    button.connect("clicked", clicked_handler)

    row, _hbox, label = create_row_structure(
        include_top_separator,
        label_text,
        button,
        label_halign=Gtk.Align.START,
    )

    assert label is not None
    return row, button, label


def create_flat_icon_button(
    icon_name: str,
    accessible_name: str,
    icon_size: Gtk.IconSize = Gtk.IconSize.DND,
) -> Gtk.Button:
    """Return a flat icon button with an accessible name."""

    button = Gtk.Button.new_from_icon_name(icon_name, icon_size)
    button.set_relief(Gtk.ReliefStyle.NONE)
    button.get_accessible().set_name(accessible_name)
    return button


def set_stacked_label_text(
    label: Gtk.Label,
    primary_text: str,
    secondary_text: str = "",
    detail_text: str = "",
) -> None:
    """Set text for a stacked action-row label."""

    lines = [primary_text]
    lines.extend(text for text in (secondary_text, detail_text) if text)
    label.set_text("\n".join(lines))


def create_action_list_row(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    primary_text: str,
    secondary_text: str,
    actions: Sequence[ListRowAction] = (),
    include_top_separator: bool = True,
    primary_label_size_group: Gtk.SizeGroup | None = None,
    stack_labels: bool = False,
    detail_text: str = "",
) -> tuple[Gtk.ListBoxRow, Gtk.Label, Gtk.Label, dict[str, Gtk.Button]]:
    """Return a list row with labels and trailing action buttons."""

    row = Gtk.ListBoxRow()
    row.set_activatable(False)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    if include_top_separator:
        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

    hbox = create_row_box()

    primary_label = Gtk.Label(label=primary_text, xalign=0)
    secondary_label = Gtk.Label(label=secondary_text, xalign=0)
    if stack_labels:
        primary_label.set_hexpand(True)
        primary_label.set_line_wrap(True)
        primary_label.set_max_width_chars(60)
        set_stacked_label_text(primary_label, primary_text, secondary_text, detail_text)
        hbox.pack_start(primary_label, True, True, 0)
    else:
        if primary_label_size_group:
            primary_label_size_group.add_widget(primary_label)
        hbox.pack_start(primary_label, False, False, 0)
        secondary_label.set_hexpand(True)
        hbox.pack_start(secondary_label, True, True, 0)

    action_buttons: dict[str, Gtk.Button] = {}
    button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    for action in actions:
        if action.icon_name:
            button = Gtk.Button.new_from_icon_name(action.icon_name, Gtk.IconSize.DND)
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.get_accessible().set_name(action.label)
        else:
            button = Gtk.Button(label=action.label)
        button.connect("clicked", action.callback)
        button_box.pack_start(button, False, False, 0)
        action_buttons[action.name] = button

    hbox.pack_end(button_box, False, False, 0)
    vbox.pack_start(hbox, False, False, 0)
    row.add(vbox)
    return row, primary_label, secondary_label, action_buttons


def create_scrolled_window(
    child: Gtk.Widget | None = None,
    *,
    hscroll_policy: Gtk.PolicyType | None = None,
    vscroll_policy: Gtk.PolicyType | None = None,
    size_request: tuple[int, int] | None = None,
    hexpand: bool | None = None,
    vexpand: bool | None = None,
) -> Gtk.ScrolledWindow:
    """Return a framed scrolled window for Orca dialogs."""

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.get_style_context().add_class("frame")
    scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
    if hscroll_policy is not None or vscroll_policy is not None:
        scrolled_window.set_policy(
            hscroll_policy or Gtk.PolicyType.AUTOMATIC,
            vscroll_policy or Gtk.PolicyType.AUTOMATIC,
        )
    if size_request is not None:
        scrolled_window.set_size_request(*size_request)
    if hexpand is not None:
        scrolled_window.set_hexpand(hexpand)
    if vexpand is not None:
        scrolled_window.set_vexpand(vexpand)
    if child is not None:
        scrolled_window.add(child)  # pylint: disable=no-member
    return scrolled_window


def create_preferences_scrolled_window(child: Gtk.Widget | None = None) -> Gtk.ScrolledWindow:
    """Return a scrolled window for preferences-grid content."""

    return create_scrolled_window(
        child or Gtk.Box(),
        hscroll_policy=Gtk.PolicyType.NEVER,
        vscroll_policy=Gtk.PolicyType.AUTOMATIC,
        size_request=(700, -1),
        hexpand=True,
        vexpand=True,
    )


def create_tree_view() -> tuple[Gtk.ScrolledWindow, Gtk.TreeView]:
    """Return a framed scrolled window containing a tree view."""

    tree = Gtk.TreeView()
    tree.set_hexpand(True)
    tree.set_vexpand(True)
    return create_scrolled_window(tree), tree


def create_tree_view_dialog(
    title: str,
    *,
    column_headers: Sequence[str] | None = None,
    text_column_offset: int = 0,
    sort_empty_headers: bool = False,
    default_size: tuple[int, int] | None = None,
    buttons: Sequence[tuple[str, int]] | None = None,
    default_response: int | None = None,
    modal: bool = True,
    resizable: bool = True,
    content_margin: int = 12,
) -> tuple[Gtk.Dialog, Gtk.TreeView]:
    """Return an Orca-styled dialog containing a framed tree view."""

    dialog = create_dialog(
        title,
        default_size=default_size,
        buttons=buttons,
        default_response=default_response,
        modal=modal,
        resizable=resizable,
        content_margin=content_margin,
    )

    grid = Gtk.Grid()
    dialog.get_content_area().add(grid)

    scrolled_window, tree = create_tree_view()
    grid.add(scrolled_window)  # pylint: disable=no-member
    add_tree_view_columns(
        tree,
        column_headers or (),
        text_column_offset=text_column_offset,
        sort_empty_headers=sort_empty_headers,
    )
    return dialog, tree


def add_tree_view_columns(
    tree: Gtk.TreeView,
    column_headers: Sequence[str],
    *,
    text_column_offset: int = 0,
    sort_empty_headers: bool = False,
) -> None:
    """Add sortable text columns to a tree view."""

    for i, header in enumerate(column_headers):
        cell = Gtk.CellRendererText()
        model_column = i + text_column_offset
        column = Gtk.TreeViewColumn(header, cell, text=model_column)
        tree.append_column(column)
        if header or sort_empty_headers:
            column.set_sort_column_id(model_column)


def apply_appearance(
    interface_settings: Gio.Settings,
    a11y_settings: Gio.Settings,
    gtk_settings: Gtk.Settings,
    screen: Gdk.Screen,
    providers: AppearanceProviders,
) -> None:
    """Apply color-scheme, high-contrast, and status-shapes settings."""

    prefer_dark = interface_settings.get_string("color-scheme") == "prefer-dark"
    gtk_settings.set_property("gtk-application-prefer-dark-theme", prefer_dark)

    theme = gtk_settings.get_property("gtk-theme-name")
    if prefer_dark and theme == "HighContrast":
        gtk_settings.set_property("gtk-theme-name", "HighContrastInverse")
    elif not prefer_dark and theme == "HighContrastInverse":
        gtk_settings.set_property("gtk-theme-name", "HighContrast")

    priority = _style_provider_priority()
    if priority is None:
        return
    priority += 1
    conditional_providers: list[tuple[Gtk.CssProvider, bool]] = [
        (providers.hc, a11y_settings.get_boolean("high-contrast")),
        (providers.dark, prefer_dark),
    ]
    if providers.shapes is not None:
        conditional_providers.append(
            (providers.shapes, a11y_settings.get_boolean("show-status-shapes")),
        )
    for provider, enabled in conditional_providers:
        if enabled:
            Gtk.StyleContext.add_provider_for_screen(screen, provider, priority)
        else:
            Gtk.StyleContext.remove_provider_for_screen(screen, provider)
