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

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # pylint: disable=no-name-in-module

from . import debug, guilabels

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class AppearanceProviders:
    """CSS providers for conditional appearance settings."""

    hc: Gtk.CssProvider
    dark: Gtk.CssProvider
    shapes: Gtk.CssProvider | None = None


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


def create_scrolled_window(child: Gtk.Widget | None = None) -> Gtk.ScrolledWindow:
    """Return a framed scrolled window for Orca dialogs."""

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.get_style_context().add_class("frame")
    scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
    if child is not None:
        scrolled_window.add(child)  # pylint: disable=no-member
    return scrolled_window


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
