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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-lines
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-statements

"""Base class for preference grid UI components."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atk", "1.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atk, Gdk, GLib, Gtk

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


class CategoryListBoxRow(Gtk.ListBoxRow):
    """ListBoxRow for category selection with category identifier."""

    def __init__(self, category: str) -> None:
        super().__init__()
        self._category = category

    @property
    def category(self) -> str:
        """Get the category identifier."""
        return self._category


class CommandListBoxRow(Gtk.ListBoxRow):
    """ListBoxRow for command keybindings with command details."""

    def __init__(self) -> None:
        super().__init__()
        self._command = None
        self._vbox = None
        self._binding_label = None

    @property
    def command(self):
        """Get the command."""
        return self._command

    @command.setter
    def command(self, value) -> None:
        """Set the command."""
        self._command = value

    @property
    def vbox(self):
        """Get the vbox container."""
        return self._vbox

    @vbox.setter
    def vbox(self, value) -> None:
        """Set the vbox container."""
        self._vbox = value

    @property
    def binding_label(self):
        """Get the binding label."""
        return self._binding_label

    @binding_label.setter
    def binding_label(self, value) -> None:
        """Set the binding label."""
        self._binding_label = value


# pylint: disable-next=too-few-public-methods
class RadioButtonWithActions(Gtk.RadioButton):
    """RadioButton with associated action buttons for navigation."""

    def __init__(self, label: str | None = None, group: Gtk.RadioButton | None = None) -> None:
        super().__init__(label=label, group=group)
        self._action_buttons: list[Gtk.Button] = []

    @property
    def action_buttons(self) -> list[Gtk.Button]:
        """Get the list of action buttons."""
        return self._action_buttons

    @action_buttons.setter
    def action_buttons(self, value: list[Gtk.Button]) -> None:
        """Set the list of action buttons."""
        self._action_buttons = value


class StackedPreferencesHelper:
    """Helper for managing stacked drill-down preferences UI."""

    def __init__(self) -> None:
        self.stack: Gtk.Stack | None = None
        self.categories_listbox: Gtk.ListBox | None = None
        self.detail_listbox: Gtk.ListBox | None = None
        self.disable_widgets: list[Gtk.Widget] = []
        self.on_category_activated_callback: Callable[[Gtk.ListBoxRow], None] | None = None

    def show_categories(self) -> None:
        """Switch to categories view and enable registered widgets."""

        if self.stack:
            self.stack.set_visible_child_name("categories")

        for widget in self.disable_widgets:
            widget.set_sensitive(True)

    def show_detail(self) -> None:
        """Switch to detail view and disable registered widgets."""

        if self.stack:
            self.stack.set_visible_child_name("detail")

        for widget in self.disable_widgets:
            widget.set_sensitive(False)

    def register_disable_widgets(self, *widgets: Gtk.Widget) -> None:
        """Register widgets that should be disabled when in detail view."""

        self.disable_widgets.extend(widgets)


@dataclass
class BooleanPreferenceControl:  # pylint: disable=too-many-instance-attributes
    """Represents a boolean preference with its UI label and getters/setters."""

    label: str
    getter: Callable[[], bool | None]
    setter: Callable[[bool], Any]
    prefs_key: str | None = None
    member_of: str | None = None
    determine_sensitivity: Callable[[], bool] | None = None
    apply_immediately: bool = True


@dataclass
class IntRangePreferenceControl:  # pylint: disable=too-many-instance-attributes
    """Represents an integer range preference with its UI label and getters/setters."""

    label: str
    minimum: int
    maximum: int
    getter: Callable[[], int]
    setter: Callable[[int], Any]
    prefs_key: str | None = None
    member_of: str | None = None
    determine_sensitivity: Callable[[], bool] | None = None
    apply_immediately: bool = False


@dataclass
class FloatRangePreferenceControl:  # pylint: disable=too-many-instance-attributes
    """Represents a float range preference with its UI label and getters/setters."""

    label: str
    minimum: float
    maximum: float
    getter: Callable[[], float]
    setter: Callable[[float], Any]
    prefs_key: str | None = None
    member_of: str | None = None
    determine_sensitivity: Callable[[], bool] | None = None


@dataclass
class EnumPreferenceControl:  # pylint: disable=too-many-instance-attributes
    """Represents an enumerated preference with its UI label and getters/setters."""

    label: str
    options: list[str]
    getter: Callable[[], Any]
    setter: Callable[[Any], Any]
    values: list[Any] | None = None
    prefs_key: str | None = None
    member_of: str | None = None
    determine_sensitivity: Callable[[], bool] | None = None


@dataclass
class ColorPreferenceControl:
    """Represents a color preference with its UI label and getters/setters."""

    label: str
    getter: Callable[[], str]
    setter: Callable[[str], Any]
    prefs_key: str | None = None
    member_of: str | None = None
    determine_sensitivity: Callable[[], bool] | None = None


@dataclass
class SelectionPreferenceControl:  # pylint: disable=too-many-instance-attributes
    """Control for selection-based preferences with optional actions."""

    label: str
    options: list[str]
    getter: Callable[[], Any]
    setter: Callable[[Any], Any] | None
    values: list[Any] | None = None
    prefs_key: str | None = None
    member_of: str | None = None
    get_actions_for_option: Callable[[Any], list[tuple[str, str, Callable[[], None]]]] | None = None
    determine_sensitivity: Callable[[], bool] | None = None
    apply_immediately: bool = True
    tracks_changes: bool = True


# pylint: disable=no-member
class FocusManagedListBox(Gtk.ListBox):
    """A ListBox that automatically manages focus for interactive widgets in rows."""

    def __init__(self):
        super().__init__()
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.get_style_context().add_class("frame")
        self.set_can_focus(False)

        # Show separators between rows
        self.set_header_func(self._separator_header_func, None)

        self._widgets = []
        self._rows = []
        self._exiting_backward = [False]

    @staticmethod
    def _separator_header_func(row, before, _user_data):
        """Add separator between rows (standard GTK ListBox pattern)."""

        if before is not None:
            row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    def add_row_with_widget(self, row: Gtk.ListBoxRow, widget: Gtk.Widget) -> None:
        """Add a row with its associated interactive widget."""

        widget.connect("key-press-event", self._on_widget_key_press)
        row.connect("focus-in-event", self._on_row_focus_in, widget)

        self.add(row)
        self._rows.append(row)
        self._widgets.append(widget)

    def get_last_row(self) -> Gtk.ListBoxRow | None:
        """Return the last row that was added, or None if no rows."""

        if self._rows:
            return self._rows[-1]
        return None

    # pylint: disable-next=too-many-return-statements
    def _on_widget_key_press(self, widget: Gtk.Widget, event) -> bool:
        """Handle Tab, Shift+Tab, and Left arrow to navigate."""

        if event.keyval == Gdk.KEY_Tab:
            try:
                current_index = self._widgets.index(widget)
                for next_index in range(current_index + 1, len(self._widgets)):
                    next_widget = self._widgets[next_index]
                    if next_widget.get_sensitive():
                        next_widget.grab_focus()
                        return True
                return False
            except ValueError:
                pass
            return False

        # Left arrow: exit nested group first, then move to sidebar
        # But not for widgets where arrows have meaning (sliders, spin buttons)
        if event.keyval == Gdk.KEY_Left:
            if isinstance(widget, (Gtk.Scale, Gtk.SpinButton)):
                return False
            parent = self.get_parent()
            first_grid = None
            while parent is not None:
                if isinstance(parent, PreferencesGridBase):
                    if first_grid is None:
                        first_grid = parent
                    if parent.is_in_multipage_detail():
                        parent.multipage_show_categories()
                        return True
                parent = parent.get_parent()
            if first_grid is not None:
                first_grid.focus_sidebar()
                return True
            return False

        if event.keyval == Gdk.KEY_ISO_Left_Tab:
            try:
                current_index = self._widgets.index(widget)
                for prev_index in range(current_index - 1, -1, -1):
                    prev_widget = self._widgets[prev_index]
                    if prev_widget.get_sensitive():
                        prev_widget.grab_focus()
                        return True
                if self._rows:
                    self._exiting_backward[0] = True
                    self._rows[0].grab_focus()
                    return False
            except ValueError:
                pass

        return False

    def _on_row_focus_in(self, _row, _event, widget: Gtk.Widget) -> bool:
        """Redirect focus from row to widget and activate radio buttons."""

        if self._exiting_backward[0]:
            self._exiting_backward[0] = False
            return False

        def activate_widget():
            widget.grab_focus()

        GLib.idle_add(activate_widget)
        return False


# pylint: enable=no-member


# pylint: disable-next=too-few-public-methods, too-many-instance-attributes
class PreferencesGridBase(Gtk.Grid):
    """Base class for all preferences grid widgets with common UI helpers."""

    # pylint: disable=no-member
    def __init__(self, tab_label: str) -> None:
        """Initialize the preferences grid with a tab label."""

        super().__init__()
        self._tab_label = tab_label
        self._has_unsaved_changes = False
        self._focus_sidebar_callback: Callable[[], None] | None = None
        self.set_border_width(24)
        self.set_margin_start(100)
        self.set_margin_end(100)
        self.set_margin_top(40)
        self.set_margin_bottom(40)
        self.set_row_spacing(12)
        self.set_column_spacing(48)

        self._stacked_prefs_helper: StackedPreferencesHelper | None = None
        self._multipage_stack: Gtk.Stack | None = None
        self._multipage_title_callback: Callable[[str], None] | None = None
        self._multipage_main_title: str | None = None
        self._multipage_categories: list[tuple[str, str, PreferencesGridBase]] | None = None
        self._multipage_category_map: dict[str, tuple[str, PreferencesGridBase]] | None = None
        self._multipage_enable_listbox: FocusManagedListBox | None = None
        self._multipage_enable_switch: Gtk.Switch | None = None
        self._multipage_enable_initial: bool = False
        self._multipage_categories_listbox: Gtk.ListBox | None = None
        self._multipage_last_activated_row: Gtk.ListBoxRow | None = None

    @staticmethod
    def _set_margins(
        widget: Gtk.Widget,
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

    @property
    def _stack(self) -> Gtk.Stack | None:
        """Access stack through helper for backward compatibility."""
        return self._stacked_prefs_helper.stack if self._stacked_prefs_helper else None

    @property
    def _categories_listbox(self) -> Gtk.ListBox | None:
        """Access categories listbox through helper for backward compatibility."""
        return self._stacked_prefs_helper.categories_listbox if self._stacked_prefs_helper else None

    @property
    def _detail_listbox(self) -> Gtk.ListBox | None:
        """Access detail listbox through helper for backward compatibility."""
        return self._stacked_prefs_helper.detail_listbox if self._stacked_prefs_helper else None

    def get_label(self) -> Gtk.Label:
        """Return a Gtk.Label for use as panel label."""

        label = Gtk.Label(label=self._tab_label)
        label.show()
        return label

    def has_changes(self) -> bool:
        """Return True if the user has made changes that haven't been written to file."""

        return self._has_unsaved_changes

    def revert_changes(self) -> None:
        """Revert any changes that were applied immediately but not saved."""

    def on_becoming_visible(self) -> None:
        """Called when this grid becomes the visible panel in the main stack."""

    def set_focus_sidebar_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback to focus the sidebar navigation list."""

        self._focus_sidebar_callback = callback
        # Forward to child grids in multi-page structures
        if self._multipage_categories:
            for _label, _page_id, grid in self._multipage_categories:
                grid.set_focus_sidebar_callback(callback)

    def focus_sidebar(self) -> None:
        """Move focus to the sidebar navigation list."""

        if self._focus_sidebar_callback:
            self._focus_sidebar_callback()

    def is_in_multipage_detail(self) -> bool:
        """Returns True if this grid has a multipage stack showing a detail page."""

        if self._multipage_stack is None:
            return False
        visible_child = self._multipage_stack.get_visible_child_name()
        return visible_child is not None and visible_child != "categories"

    def _create_header_bar_dialog(
        self,
        title: str,
        cancel_label: str,
        ok_label: str,
        width: int = 600,
    ) -> tuple[Gtk.Dialog, Gtk.Button]:
        """Create a dialog with header bar, no close button, and consistent styling."""

        dialog = Gtk.Dialog(
            title=title,
            transient_for=self.get_toplevel(),
            modal=True,
            destroy_with_parent=True,
            use_header_bar=True,
        )
        dialog.set_default_size(width, -1)
        dialog.set_deletable(False)

        header_bar = dialog.get_header_bar()

        cancel_button = Gtk.Button.new_with_mnemonic(cancel_label)
        cancel_button.connect("clicked", lambda btn: dialog.response(Gtk.ResponseType.CANCEL))
        header_bar.pack_start(cancel_button)

        ok_button = Gtk.Button.new_with_mnemonic(ok_label)
        ok_button.get_style_context().add_class("suggested-action")
        ok_button.connect("clicked", lambda btn: dialog.response(Gtk.ResponseType.OK))
        ok_button.set_can_default(True)
        header_bar.pack_end(ok_button)

        content_area = dialog.get_content_area()
        content_area.set_border_width(24)
        content_area.set_spacing(18)

        return dialog, ok_button

    def _create_frame(self, label: str, margin_top: int = 0) -> tuple[Gtk.Frame, Gtk.Grid]:
        """Create a labeled frame."""

        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        label_widget = Gtk.Label(label=label, xalign=0)
        label_widget.get_style_context().add_class("heading")
        label_widget.set_margin_top(max(0, margin_top))
        label_widget.set_margin_bottom(6)
        frame.set_label_widget(label_widget)

        content_container = Gtk.Grid()
        content_container.set_row_spacing(6)
        content_container.set_column_spacing(12)
        content_container.set_margin_top(6)

        frame.add(content_container)

        return frame, content_container

    def _create_info_row(
        self,
        message: str,
        icon_name: str = "dialog-information-symbolic",
    ) -> Gtk.ListBoxRow:
        """Create a single-row informational message with icon."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        row.set_can_focus(True)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

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

    def _create_info_listbox(
        self,
        message: str,
        icon_name: str = "dialog-information-symbolic",
    ) -> Gtk.ListBox:
        """Create a listbox with a single info row with proper accessibility."""

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.get_style_context().add_class("frame")

        listbox_accessible = listbox.get_accessible()
        if listbox_accessible:
            listbox_accessible.set_role(Atk.Role.PANEL)

        info_row = self._create_info_row(message, icon_name)
        listbox.add(info_row)

        return listbox

    def _create_label(
        self,
        text: str,
        halign: Gtk.Align = Gtk.Align.END,
        valign: Gtk.Align = Gtk.Align.FILL,
    ) -> Gtk.Label:
        """Create a label with mnemonic support."""

        label = Gtk.Label()
        label.set_text_with_mnemonic(text)
        label.set_halign(halign)
        label.set_valign(valign)
        return label

    def _create_row_structure(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        include_top_separator: bool = True,
        label_text: str | None = None,
        widget: Gtk.Widget | None = None,
        label_xalign: float | None = None,
        label_halign: Gtk.Align | None = None,
        label_hexpand: bool = True,
        widget_expand: bool = False,
    ) -> tuple[Gtk.ListBoxRow, Gtk.Box, Gtk.Label | None]:
        """Create basic row structure with optional label+widget pair."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        if include_top_separator:
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox.pack_start(separator, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

        label = None
        if label_text and widget:
            label = Gtk.Label(label=label_text)
            label.set_use_underline(True)

            if label_xalign is not None:
                label.set_xalign(label_xalign)
            if label_halign is not None:
                label.set_halign(label_halign)

            label.set_hexpand(label_hexpand)
            hbox.pack_start(label, label_hexpand, label_hexpand, 0)

            if not isinstance(widget, Gtk.Button):
                label.set_mnemonic_widget(widget)
            hbox.pack_end(widget, widget_expand, widget_expand, 0)

        vbox.pack_start(hbox, False, False, 0)
        row.add(vbox)

        return row, hbox, label

    def _create_combo_box_row(
        self,
        label_text: str,
        model: Gtk.ListStore,
        changed_handler: Callable[[Gtk.ComboBox], None],
        include_top_separator: bool = True,
    ) -> tuple[Gtk.ListBoxRow, Gtk.ComboBox, Gtk.Label]:
        """Create a single listbox row with label and combo box."""

        combo = Gtk.ComboBox()
        combo.set_model(model)
        renderer = Gtk.CellRendererText()
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        combo.set_valign(Gtk.Align.CENTER)
        combo.connect("changed", changed_handler)

        row, _hbox, label = self._create_row_structure(
            include_top_separator,
            label_text,
            combo,
            label_halign=Gtk.Align.START,
        )

        return row, combo, label

    def _create_switch_row(
        self,
        label_text: str,
        changed_handler: Callable[[Gtk.Switch, Any], None],
        state: bool,
        include_top_separator: bool = True,
    ) -> tuple[Gtk.ListBoxRow, Gtk.Switch, Gtk.Label]:
        """Create a single listbox row with label and switch."""

        switch = Gtk.Switch()
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_active(state)
        switch.connect("notify::active", changed_handler)

        switch_accessible = switch.get_accessible()
        switch_accessible.set_role(Atk.Role.SWITCH)

        row, _hbox, label = self._create_row_structure(
            include_top_separator,
            label_text,
            switch,
            label_xalign=0,
        )

        return row, switch, label

    def _create_slider_row(
        self,
        label_text: str,
        adjustment: Gtk.Adjustment,
        changed_handler: Callable[[Gtk.Scale], None] | None = None,
        include_top_separator: bool = True,
    ) -> tuple[Gtk.ListBoxRow, Gtk.Scale, Gtk.Label]:
        """Create a single listbox row with label and horizontal slider."""

        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        scale.set_draw_value(True)
        scale.set_value_pos(Gtk.PositionType.RIGHT)
        scale.set_hexpand(True)
        scale.set_valign(Gtk.Align.CENTER)
        if changed_handler is not None:
            scale.connect("value-changed", changed_handler)

        row, _hbox, label = self._create_row_structure(
            include_top_separator,
            label_text,
            scale,
            label_halign=Gtk.Align.START,
            label_hexpand=False,
            widget_expand=True,
        )

        return row, scale, label

    def _create_button_listbox(
        self,
        items: list[tuple[str, str | None, Callable[[Gtk.Button], None]]],
    ) -> tuple[FocusManagedListBox, list[Gtk.Button]]:
        """Create a listbox with one or more label+button rows."""

        listbox = FocusManagedListBox()
        all_buttons = []

        for label_text, icon_name, clicked_handler in items:
            row, button, _label = self._create_button_row(
                label_text,
                icon_name,
                clicked_handler,
                include_top_separator=False,
            )

            listbox.add_row_with_widget(row, button)
            all_buttons.append(button)

        return listbox, all_buttons

    def _create_button_row(
        self,
        label_text: str,
        icon_name: str | None,
        clicked_handler: Callable[[Gtk.Button], None],
        include_top_separator: bool = True,
    ) -> tuple[Gtk.ListBoxRow, Gtk.Button, Gtk.Label]:
        """Create a single listbox row with label and button."""

        button = Gtk.Button()
        if icon_name:
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DND)
            button.set_image(icon)
        button.set_valign(Gtk.Align.CENTER)
        button.connect("clicked", clicked_handler)

        row, _hbox, label = self._create_row_structure(
            include_top_separator,
            label_text,
            button,
            label_halign=Gtk.Align.START,
        )

        return row, button, label

    def _create_labeled_entry_row(
        self,
        label_text: str,
        entry: Gtk.Entry,
        include_top_separator: bool = True,
        label_size_group: Gtk.SizeGroup | None = None,
    ) -> Gtk.ListBoxRow:
        """Create a ListBoxRow with a label and entry field."""

        row, hbox, _ = self._create_row_structure(include_top_separator)

        label = Gtk.Label(label=label_text, xalign=0)
        label.set_use_underline(True)
        hbox.pack_start(label, False, False, 0)

        if label_size_group:
            label_size_group.add_widget(label)

        entry.set_hexpand(True)
        label.set_mnemonic_widget(entry)
        hbox.pack_start(entry, True, True, 0)

        return row

    def _create_combo_box(
        self,
        model: Gtk.ListStore,
        changed_handler: Callable[[Gtk.ComboBox], None],
    ) -> Gtk.ComboBox:
        """Create a combo box with standard formatting."""

        combo = Gtk.ComboBox()
        combo.set_model(model)
        renderer = Gtk.CellRendererText()
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        combo.set_hexpand(False)
        combo.connect("changed", changed_handler)
        return combo

    def _create_scrolled_window(self, widget: Gtk.Widget) -> Gtk.ScrolledWindow:
        """Create a scrolled window containing the widget with standard settings."""

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_shadow_type(Gtk.ShadowType.IN)  # pylint: disable=no-member
        scrolled.set_size_request(700, -1)
        scrolled.add(widget)  # pylint: disable=no-member
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        return scrolled

    def _create_stacked_preferences(
        self,
        on_category_activated: Callable[[Gtk.ListBoxRow], None],
        on_detail_row_activated: Callable[[Gtk.ListBox, Gtk.ListBoxRow], None] | None = None,
    ) -> tuple[Gtk.Stack, Gtk.ListBox, Gtk.ListBox]:
        """Create a stack-based drill-down preferences UI with ListBox detail view."""

        helper = StackedPreferencesHelper()
        self._stacked_prefs_helper = helper

        helper.stack = Gtk.Stack()
        helper.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        helper.categories_listbox = Gtk.ListBox()
        helper.categories_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        helper.categories_listbox.connect("key-press-event", self._on_stack_categories_key_press)
        helper.categories_listbox.connect("row-activated", self._on_stack_category_activated)
        helper.on_category_activated_callback = on_category_activated
        categories_scrolled = self._create_scrolled_window(helper.categories_listbox)
        helper.stack.add_named(categories_scrolled, "categories")

        helper.detail_listbox = Gtk.ListBox()
        helper.detail_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        helper.detail_listbox.connect("key-press-event", self._on_stack_detail_key_press)
        if on_detail_row_activated:
            helper.detail_listbox.connect("row-activated", on_detail_row_activated)
        detail_scrolled = self._create_scrolled_window(helper.detail_listbox)
        helper.stack.add_named(detail_scrolled, "detail")

        helper.stack.set_hexpand(True)
        helper.stack.set_visible_child_name("categories")
        return (helper.stack, helper.categories_listbox, helper.detail_listbox)

    def _add_stack_category_row(
        self,
        listbox: Gtk.ListBox,
        label: str,
        **custom_attrs,
    ) -> CategoryListBoxRow:
        """Add a category row to the categories listbox with chevron icon."""

        category = custom_attrs.get("category", "")
        row = CategoryListBoxRow(category)
        row.set_activatable(True)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

        label_widget = Gtk.Label(label=label, xalign=0)
        label_widget.set_hexpand(True)
        hbox.pack_start(label_widget, True, True, 0)

        chevron = Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        chevron_accessible = chevron.get_accessible()
        if chevron_accessible:
            chevron_accessible.set_name("")
            chevron_accessible.set_role(Atk.Role.BUTTON)
        hbox.pack_end(chevron, False, False, 0)

        row.add(hbox)

        row.show_all()
        listbox.add(row)
        return row

    def _register_stack_disable_widgets(self, *widgets: Gtk.Widget) -> None:
        """Register widgets that should be disabled when in detail view."""

        if self._stacked_prefs_helper:
            self._stacked_prefs_helper.register_disable_widgets(*widgets)

    def _show_stack_categories(self) -> None:
        """Switch to categories view and enable registered widgets."""

        if self._stacked_prefs_helper:
            self._stacked_prefs_helper.show_categories()

    def _show_stack_detail(self) -> None:
        """Switch to detail view and disable registered widgets."""

        if self._stacked_prefs_helper:
            self._stacked_prefs_helper.show_detail()

    def _on_stack_category_activated(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Internal handler for category activation - delegates to callback."""

        if self._stacked_prefs_helper and self._stacked_prefs_helper.on_category_activated_callback:
            self._stacked_prefs_helper.on_category_activated_callback(row)

    def _on_stack_categories_key_press(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handle key press in categories page - Right arrow activates focused row."""

        if event.keyval == Gdk.KEY_Right:
            # Get the focused row (selection mode is NONE, so get_selected_row won't work)
            if self._categories_listbox:
                focused_child = self._categories_listbox.get_focus_child()
                if focused_child and isinstance(focused_child, Gtk.ListBoxRow):
                    self._on_stack_category_activated(self._categories_listbox, focused_child)
                    return True
        return False

    def _on_stack_detail_key_press(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handle key press in detail page - Left/Escape/Alt+Left to go back."""

        # Don't intercept Left for widgets where arrows have meaning
        focused = widget.get_toplevel().get_focus()
        if event.keyval == Gdk.KEY_Left and isinstance(focused, (Gtk.Scale, Gtk.SpinButton)):
            return False

        # Left arrow or Escape to go back to categories
        if event.keyval in [Gdk.KEY_Left, Gdk.KEY_Escape]:
            self._show_stack_categories()
            return True

        # Alt+Left to go back
        if event.keyval == Gdk.KEY_Left and event.state & Gdk.ModifierType.MOD1_MASK:
            self._show_stack_categories()
            return True

        return False

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def _create_multi_page_stack(
        self,
        enable_label: str | None,
        enable_getter: Callable[[], bool] | None,
        enable_setter: Callable[[bool], Any] | None,
        categories: list[tuple[str, str, PreferencesGridBase]],
        title_change_callback: Callable[[str], None] | None = None,
        main_title: str | None = None,
    ) -> tuple[FocusManagedListBox | None, Gtk.Stack, Gtk.ListBox]:
        """Create a multi-page nested stack with optional enable switch and category navigation.

        This helper encapsulates the common pattern used by Speech and Braille preferences
        where there's an enable switch at the top, a categories page, and multiple child
        grid pages for each category.

        Args:
            enable_label: Label for the enable switch (e.g., "Enable speech"), or None to skip
            enable_getter: Function to get current enable state, or None to skip
            enable_setter: Function to set enable state, or None to skip
            categories: List of (label, page_id, grid) tuples for each category
            title_change_callback: Optional callback to update window title
            main_title: Title to use when on categories page (defaults to grid's label)

        Returns:
            Tuple of (enable_listbox, stack, categories_listbox) for additional customization.
            enable_listbox will be None if enable_label/getter/setter are None.

        Example:
            categories = [
                (guilabels.GENERAL, "general", self._general_grid),
                (guilabels.SETTINGS, "settings", self._settings_grid),
            ]
            enable_listbox, stack, categories_listbox = self._create_multi_page_stack(
                enable_label=guilabels.ENABLE_FEATURE,
                enable_getter=self._manager.get_enabled,
                enable_setter=self._manager.set_enabled,
                categories=categories,
                title_change_callback=self._update_title,
                main_title=guilabels.FEATURE
            )
        """

        if main_title is None:
            main_title = self._label.get_text()

        self._multipage_title_callback = title_change_callback
        self._multipage_main_title = main_title
        self._multipage_categories = categories
        self._multipage_category_map = {
            page_id: (label, grid) for label, page_id, grid in categories
        }

        enable_listbox: FocusManagedListBox | None = None
        if enable_label is not None and enable_getter is not None and enable_setter is not None:
            enable_listbox = FocusManagedListBox()
            enable_row, enable_switch, _label = self._create_switch_row(
                enable_label,
                lambda switch, _param: self._on_multipage_enable_toggled(switch, enable_setter),
                enable_getter(),
                include_top_separator=False,
            )
            enable_listbox.add_row_with_widget(enable_row, enable_switch)
            self._multipage_enable_switch = enable_switch
            self._multipage_enable_initial = enable_getter()
        self._multipage_enable_listbox = enable_listbox

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_hexpand(True)
        stack.set_vexpand(True)

        categories_listbox = Gtk.ListBox()
        categories_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        categories_listbox.connect("row-activated", self._on_multipage_category_activated)
        categories_listbox.connect("key-press-event", self._on_multipage_categories_key_press)
        categories_listbox.set_header_func(self._multipage_separator_header_func, None)

        for label, page_id, _grid in categories:
            self._add_stack_category_row(categories_listbox, label, category=page_id)

        categories_listbox.get_style_context().add_class("frame")
        categories_listbox.set_vexpand(False)
        categories_listbox.set_valign(Gtk.Align.START)
        stack.add_named(categories_listbox, "categories")

        for _label, page_id, grid in categories:
            grid.set_border_width(0)
            grid.set_margin_start(0)
            grid.set_margin_end(0)
            grid.set_margin_top(0)
            grid.set_margin_bottom(0)
            grid.set_row_spacing(6)
            for child in grid.get_children():
                if isinstance(child, Gtk.Frame):
                    child.set_margin_start(0)
                    child.set_margin_end(0)
                    child.set_margin_top(6)
                    child.set_margin_bottom(0)

            stack.add_named(grid, page_id)
            grid.connect("key-press-event", self._on_multipage_child_key_press)

        stack.set_visible_child_name("categories")

        stack.set_margin_start(0)
        stack.set_margin_end(0)
        stack.set_margin_top(0)
        stack.set_margin_bottom(0)

        if enable_getter is not None:
            stack.set_sensitive(enable_getter())

        self._multipage_stack = stack
        self._multipage_categories_listbox = categories_listbox

        return (enable_listbox, stack, categories_listbox)

    @staticmethod
    def _multipage_separator_header_func(row, before, _user_data):
        """Add separator between rows in multi-page categories listbox."""

        if before is not None:
            row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    def _on_multipage_enable_toggled(
        self,
        switch: Gtk.Switch,
        setter: Callable[[bool], Any],
    ) -> None:
        """Handle enable switch toggle in multi-page stack."""

        if self._initializing:
            return

        enabled = switch.get_active()
        if self._multipage_stack:
            self._multipage_stack.set_sensitive(enabled)

        if enabled:
            setter(True)

        self._has_unsaved_changes = enabled != self._multipage_enable_initial

    def _on_multipage_categories_key_press(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handle key press in multi-page categories - Right arrow activates focused row."""

        if event.keyval == Gdk.KEY_Right:
            if self._multipage_categories_listbox:
                focused_child = self._multipage_categories_listbox.get_focus_child()
                if focused_child and isinstance(focused_child, Gtk.ListBoxRow):
                    self._on_multipage_category_activated(
                        self._multipage_categories_listbox,
                        focused_child,
                    )
                    return True
        return False

    def _on_multipage_category_activated(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Handle category activation in multi-page stack."""

        if not isinstance(row, CategoryListBoxRow):
            return

        category_id = row.category
        if not category_id or not self._multipage_stack:
            return

        self._multipage_last_activated_row = row

        if self._multipage_enable_listbox:
            self._multipage_enable_listbox.hide()

        # Show the child before switching to it (it may have been hidden when leaving)
        if self._multipage_category_map is not None and category_id in self._multipage_category_map:
            _, grid = self._multipage_category_map[category_id]
            if grid:
                grid.show_all()

        self._multipage_stack.set_visible_child_name(category_id)
        if self._multipage_title_callback and self._multipage_category_map is not None:
            label, _ = self._multipage_category_map.get(
                category_id,
                (self._multipage_main_title or "", None),
            )
            self._multipage_title_callback(label or "")

        # Focus first widget in grid
        if self._multipage_category_map is not None and category_id in self._multipage_category_map:
            _, grid = self._multipage_category_map[category_id]
            if grid:
                GLib.idle_add(self._multipage_focus_first_widget, grid)

    def _multipage_focus_first_widget(self, grid: PreferencesGridBase) -> bool:
        """Focus the first focusable widget in a multi-page child grid."""

        def focus_first_row(listbox):
            """Focus the first focusable row in a listbox."""

            rows = listbox.get_children()
            for row in rows:
                if row.get_sensitive() and row.get_visible():
                    row.grab_focus()
                    return True
            return False

        def get_children_via_foreach(container):
            """Get non-internal children via foreach."""

            children = []
            container.foreach(children.append)
            return children

        children = get_children_via_foreach(grid)

        # Reverse children since foreach() returns Grid children in reverse attachment order
        children = list(reversed(children))

        for child in children:
            if isinstance(child, Gtk.Frame):
                frame_child = child.get_child()
                if frame_child and isinstance(frame_child, Gtk.Container):
                    grandchildren = get_children_via_foreach(frame_child)
                    # Reverse if it's a Grid (foreach returns Grid children in reverse order)
                    if isinstance(frame_child, Gtk.Grid):
                        grandchildren = list(reversed(grandchildren))
                    for grandchild in grandchildren:
                        if isinstance(grandchild, Gtk.ListBox):
                            if focus_first_row(grandchild):
                                return False

            elif isinstance(child, Gtk.ScrolledWindow):
                sw_children = get_children_via_foreach(child)

                for sw_child in sw_children:
                    if isinstance(sw_child, Gtk.Container):
                        viewport_children = get_children_via_foreach(sw_child)
                    else:
                        viewport_children = []

                    for vp_child in viewport_children:
                        if isinstance(vp_child, Gtk.Grid):
                            grid_children = get_children_via_foreach(vp_child)

                            # Reverse since foreach returns Grid children in reverse order
                            reversed_children = list(reversed(grid_children))

                            for gc in reversed_children:
                                if isinstance(gc, Gtk.ListBox):
                                    if focus_first_row(gc):
                                        return False
                return False

            elif isinstance(child, Gtk.ListBox):
                if focus_first_row(child):
                    return False

        return False

    def _on_multipage_child_key_press(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handle key press in multi-page child grids - Left/Escape to go back."""

        # Don't intercept Left for widgets where arrows have meaning
        focused = widget.get_toplevel().get_focus()
        if event.keyval == Gdk.KEY_Left and isinstance(focused, (Gtk.Scale, Gtk.SpinButton)):
            return False

        if event.keyval in [Gdk.KEY_Left, Gdk.KEY_Escape]:
            self.multipage_show_categories()
            return True

        if event.keyval == Gdk.KEY_Left and event.state & Gdk.ModifierType.MOD1_MASK:
            self.multipage_show_categories()
            return True

        return False

    def multipage_show_categories(self) -> None:
        """Switch back to categories view in multi-page stack."""

        if self._multipage_stack:
            # Explicitly hide the current child if it's a detail page so AT-SPI
            # updates visibility states for the categories listbox. Without this,
            # items may be reported as "not showing" and not presented. However,
            # if the current child is already the categories listbox, hiding it
            # causes GTK Stack to fall back to another child.
            current_child = self._multipage_stack.get_visible_child()
            if current_child and current_child != self._multipage_categories_listbox:
                current_child.hide()
            self._multipage_stack.set_visible_child_name("categories")

        if self._multipage_enable_listbox:
            self._multipage_enable_listbox.show()

        if self._multipage_title_callback and self._multipage_main_title is not None:
            self._multipage_title_callback(self._multipage_main_title)

        if self._multipage_categories_listbox:
            self._multipage_categories_listbox.show_all()

        if self._multipage_last_activated_row:
            self._multipage_last_activated_row.grab_focus()
        elif self._multipage_categories_listbox:
            self._multipage_categories_listbox.grab_focus()

    def multipage_on_becoming_visible(self) -> None:
        """Reset multi-page stack to categories view when grid becomes visible.

        Call this from your on_becoming_visible() override if using multi-page stack.
        """

        self._multipage_last_activated_row = None
        self.multipage_show_categories()


ControlType = (
    BooleanPreferenceControl
    | IntRangePreferenceControl
    | FloatRangePreferenceControl
    | EnumPreferenceControl
    | ColorPreferenceControl
    | SelectionPreferenceControl
)


class AutoPreferencesGrid(PreferencesGridBase):  # pylint: disable=too-many-instance-attributes
    """Simplified preferences grid that automatically builds UI from control definitions."""

    _gsettings_schema: str = ""

    # pylint: disable=no-member
    def __init__(
        self,
        tab_label: str,
        controls: Sequence[ControlType],
        info_message: str = "",
        info_icon: str = "dialog-information-symbolic",
    ) -> None:
        """Initialize the grid with a list of controls."""

        super().__init__(tab_label)
        self._controls = list(controls)
        self._widgets: list[Gtk.Widget] = []
        self._rows: list[Gtk.ListBoxRow] = []
        self._group_labels: dict[str, Gtk.Label] = {}
        self._group_listboxes: dict[str, FocusManagedListBox] = {}
        self._info_message = info_message
        self._info_icon = info_icon
        self._info_listbox: Gtk.ListBox | None = None
        self._initializing = True

        self._combo_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self._widget_to_control_index: dict[Gtk.Widget, int] = {}
        self._radio_to_selection_value: dict[Gtk.RadioButton, Any] = {}

        self._build()
        self._initializing = False
        self.refresh()

    # pylint: disable-next=too-many-statements
    def _build(self) -> None:
        """Automatically build UI from controls, grouping by member_of."""

        content_grid = Gtk.Grid()
        content_grid.set_row_spacing(12)
        content_grid.set_column_spacing(48)

        row = 0

        if self._info_message:
            self._info_listbox = self._create_info_listbox(self._info_message, self._info_icon)
            self._info_listbox.set_margin_bottom(24)
            content_grid.attach(self._info_listbox, 0, row, 1, 1)
            row += 1

        # Group controls by member_of.
        groups: dict[str | None, list[tuple[int, ControlType]]] = {}
        for i, control in enumerate(self._controls):
            member = control.member_of
            if member not in groups:
                groups[member] = []
            groups[member].append((i, control))

        # Ungrouped controls.
        if None in groups:
            listbox = FocusManagedListBox()
            listbox.set_hexpand(True)
            listbox.set_halign(Gtk.Align.FILL)
            listbox.get_accessible().set_name(self._tab_label)
            for index, control in groups[None]:
                widget = self._create_control_row(control, listbox)
                self._widget_to_control_index[widget] = index
                if isinstance(widget, Gtk.RadioButton):
                    for radio in widget.get_group():
                        self._widget_to_control_index[radio] = index
                self._widgets.insert(index, widget)
                last_row = listbox.get_last_row()
                if last_row:
                    self._rows.insert(index, last_row)
            content_grid.attach(listbox, 0, row, 1, 1)
            row += 1

        # Then process named groups in order they appear.
        seen_groups: set[str | None] = {None}
        for control in self._controls:
            member = control.member_of
            if member is not None and member not in seen_groups:
                seen_groups.add(member)

                label = Gtk.Label(label=member, xalign=0)
                label.get_style_context().add_class("heading")
                label.set_margin_top(12 if row > 0 else 0)
                label.set_margin_bottom(6)
                content_grid.attach(label, 0, row, 1, 1)
                self._group_labels[member] = label
                row += 1

                listbox = FocusManagedListBox()
                listbox.set_hexpand(True)
                listbox.set_halign(Gtk.Align.FILL)
                listbox.get_accessible().set_name(member)
                self._group_listboxes[member] = listbox

                for index, group_control in groups[member]:
                    widget = self._create_control_row(group_control, listbox)
                    self._widget_to_control_index[widget] = index
                    if isinstance(widget, Gtk.RadioButton):
                        for radio in widget.get_group():
                            self._widget_to_control_index[radio] = index
                    self._widgets.insert(index, widget)
                    last_row = listbox.get_last_row()
                    if last_row:
                        self._rows.insert(index, last_row)

                content_grid.attach(listbox, 0, row, 1, 1)
                row += 1

                label_atk = label.get_accessible()
                listbox_atk = listbox.get_accessible()
                atk_relation_set = listbox_atk.ref_relation_set()
                atk_relation_set.add(Atk.Relation.new([label_atk], Atk.RelationType.LABELLED_BY))

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(content_grid)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        self.attach(scrolled, 0, 0, 1, 1)

    def get_group_listbox(self, group_name: str) -> FocusManagedListBox | None:
        """Get the listbox for a named group, or None if not found."""

        return self._group_listboxes.get(group_name)

    def add_button_to_group_header(
        self,
        group_name: str,
        icon_name: str,
        callback: Callable[[Gtk.Button], None],
        accessible_name: str,
    ) -> Gtk.Button | None:
        """Add a button to a group's header. Returns the button or None if group not found."""

        label = self._group_labels.get(group_name)
        if label is None:
            return None

        parent = label.get_parent()
        if parent is None:
            return None

        button = Gtk.Button.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        button.get_accessible().set_name(accessible_name)
        button.connect("clicked", callback)

        label_text = label.get_label()
        margin_top = label.get_margin_top()
        margin_bottom = label.get_margin_bottom()

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_margin_top(margin_top)
        header_box.set_margin_bottom(margin_bottom)

        new_label = Gtk.Label(label=label_text, xalign=0)
        new_label.get_style_context().add_class("heading")
        header_box.pack_start(new_label, True, True, 0)
        header_box.pack_end(button, False, False, 0)

        if isinstance(parent, Gtk.Grid):
            top = parent.child_get_property(label, "top-attach")
            left = parent.child_get_property(label, "left-attach")
            parent.remove(label)
            parent.attach(header_box, left, top, 1, 1)
            header_box.show_all()

        self._group_labels[group_name] = new_label

        listbox = self._group_listboxes.get(group_name)
        if listbox:
            new_label_atk = new_label.get_accessible()
            listbox_atk = listbox.get_accessible()
            atk_relation_set = listbox_atk.ref_relation_set()
            atk_relation_set.add(Atk.Relation.new([new_label_atk], Atk.RelationType.LABELLED_BY))

        return button

    def _create_control_row(self, control: ControlType, listbox: FocusManagedListBox) -> Gtk.Widget:
        """Create a row for any type of control."""

        if isinstance(control, BooleanPreferenceControl):
            return self._create_boolean_row(control, listbox)
        if isinstance(control, IntRangePreferenceControl):
            return self._create_int_range_row(control, listbox)
        if isinstance(control, FloatRangePreferenceControl):
            return self._create_float_range_row(control, listbox)
        if isinstance(control, EnumPreferenceControl):
            return self._create_enum_row(control, listbox)
        if isinstance(control, ColorPreferenceControl):
            return self._create_color_row(control, listbox)
        if isinstance(control, SelectionPreferenceControl):
            return self._create_selection_row(control, listbox)
        raise TypeError(f"Unknown control type: {type(control)}")

    def _create_boolean_row(
        self,
        control: BooleanPreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.Switch:
        """Create a switch row for a boolean control."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

        label = Gtk.Label(label=control.label, xalign=0)
        label.set_use_underline(True)
        label.set_hexpand(True)
        hbox.pack_start(label, True, True, 0)

        switch = Gtk.Switch()
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("notify::active", self._on_value_changed)
        label.set_mnemonic_widget(switch)

        switch_accessible = switch.get_accessible()
        switch_accessible.set_role(Atk.Role.SWITCH)
        hbox.pack_end(switch, False, False, 0)

        row.add(hbox)
        listbox.add_row_with_widget(row, switch)
        return switch

    def _create_int_range_row(
        self,
        control: IntRangePreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.SpinButton:
        """Create a spin button row for an integer range control."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

        label = Gtk.Label(label=control.label, xalign=0)
        label.set_use_underline(True)
        label.set_hexpand(True)
        hbox.pack_start(label, True, True, 0)

        adjustment = Gtk.Adjustment(
            value=control.minimum,
            lower=control.minimum,
            upper=control.maximum,
            step_increment=1,
            page_increment=10,
        )
        spin = Gtk.SpinButton(adjustment=adjustment)
        spin.set_digits(0)
        spin.connect("value-changed", self._on_value_changed)
        label.set_mnemonic_widget(spin)
        hbox.pack_end(spin, False, False, 0)
        row.add(hbox)
        listbox.add_row_with_widget(row, spin)
        return spin

    def _create_float_range_row(
        self,
        control: FloatRangePreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.Scale:
        """Create a scale row for a float range control."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._set_margins(vbox, start=12, end=12, top=12, bottom=12)

        label = Gtk.Label(label=control.label, xalign=0)
        label.set_use_underline(True)
        vbox.pack_start(label, False, False, 0)

        scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            control.minimum,
            control.maximum,
            (control.maximum - control.minimum) / 100,
        )
        scale.set_draw_value(True)
        scale.set_value_pos(Gtk.PositionType.RIGHT)
        scale.connect("value-changed", self._on_value_changed)
        label.set_mnemonic_widget(scale)
        vbox.pack_start(scale, False, False, 0)

        row.add(vbox)
        listbox.add_row_with_widget(row, scale)
        return scale

    @staticmethod
    def _set_color_button_hex(button: Gtk.ColorButton, hex_color: str) -> None:
        """Set a ColorButton's color from a hex string."""

        button.set_color(Gdk.color_parse(hex_color))  # type: ignore[arg-type]

    @staticmethod
    def _rgba_to_hex(rgba: Gdk.RGBA) -> str:
        """Convert a Gdk.RGBA to a hex color string."""

        return f"#{int(rgba.red * 255):02x}{int(rgba.green * 255):02x}{int(rgba.blue * 255):02x}"

    def _create_color_row(
        self,
        control: ColorPreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.ColorButton:
        """Create a color button row for a color control."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

        label = Gtk.Label(label=control.label, xalign=0)
        label.set_use_underline(True)
        label.set_hexpand(True)
        hbox.pack_start(label, True, True, 0)

        color_button = Gtk.ColorButton()
        color_button.set_use_alpha(False)
        self._set_color_button_hex(color_button, control.getter())
        color_button.connect("color-set", self._on_value_changed)
        label.set_mnemonic_widget(color_button)
        hbox.pack_end(color_button, False, False, 0)
        row.add(hbox)
        listbox.add_row_with_widget(row, color_button)
        return color_button

    def _create_enum_row(
        self,
        control: EnumPreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.ComboBoxText:
        """Create a combo box row for an enum control."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

        label = Gtk.Label(label=control.label, xalign=0)
        label.set_use_underline(True)
        label.set_hexpand(True)
        hbox.pack_start(label, True, True, 0)

        combo = Gtk.ComboBoxText()
        for option in control.options:
            combo.append_text(option)
        combo.connect("changed", self._on_value_changed)
        label.set_mnemonic_widget(combo)

        self._combo_size_group.add_widget(combo)
        hbox.pack_end(combo, False, False, 0)
        row.add(hbox)
        listbox.add_row_with_widget(row, combo)

        return combo

    def _create_selection_row(
        self,
        control: SelectionPreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.Widget:
        """Create a combo box or radio button rows for a selection control."""

        if control.get_actions_for_option is None:
            return self._create_selection_combo_row(control, listbox)
        return self._create_selection_radio_rows(control, listbox)

    def _create_selection_combo_row(
        self,
        control: SelectionPreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.ComboBoxText:
        """Create a combo box row for a selection control (no per-item actions)."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._set_margins(hbox, start=12, end=12, top=12, bottom=12)

        label = Gtk.Label(label=control.label, xalign=0)
        label.set_use_underline(True)
        label.set_hexpand(True)
        hbox.pack_start(label, True, True, 0)

        combo = Gtk.ComboBoxText()
        for option in control.options:
            combo.append_text(option)
        combo.connect("changed", self._on_value_changed)
        label.set_mnemonic_widget(combo)

        self._combo_size_group.add_widget(combo)
        hbox.pack_end(combo, False, False, 0)
        row.add(hbox)
        listbox.add_row_with_widget(row, combo)

        return combo

    def _create_selection_radio_rows(
        self,
        control: SelectionPreferenceControl,
        listbox: FocusManagedListBox,
    ) -> Gtk.RadioButton:
        """Create radio button rows with three-dot menus for a selection control."""

        assert control.get_actions_for_option is not None
        values = control.values if control.values is not None else control.options
        first_radio = None
        current_value = control.getter()

        for option_label, value in zip(control.options, values, strict=True):
            row = Gtk.ListBoxRow()
            row.set_activatable(False)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            hbox.set_margin_start(12)
            hbox.set_margin_end(12)
            hbox.set_margin_top(12)
            hbox.set_margin_bottom(12)

            if first_radio is None:
                radio = RadioButtonWithActions(label=option_label)
                first_radio = radio
            else:
                radio = RadioButtonWithActions(group=first_radio, label=option_label)

            radio.set_hexpand(True)
            radio.connect("toggled", self._on_value_changed)
            radio.connect("key-press-event", self._on_radio_key_press)
            self._radio_to_selection_value[radio] = value
            hbox.pack_start(radio, True, True, 0)

            actions = control.get_actions_for_option(value)
            action_buttons = []
            if actions:
                button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

                for action_label, icon_name, callback in actions:
                    button = Gtk.Button.new_from_icon_name(icon_name, Gtk.IconSize.DND)
                    button.set_relief(Gtk.ReliefStyle.NONE)
                    button.get_accessible().set_name(action_label)
                    button.connect("clicked", lambda _btn, cb=callback: cb())
                    button.connect("key-press-event", self._on_action_button_key_press)
                    button_box.pack_start(button, False, False, 0)
                    action_buttons.append(button)

                hbox.pack_end(button_box, False, False, 0)

            radio.action_buttons = action_buttons

            row.add(hbox)
            listbox.add_row_with_widget(row, radio)

            if value == current_value:
                listbox.select_row(row)

        return first_radio

    # pylint: disable-next=too-many-return-statements
    def _on_radio_key_press(self, radio: Gtk.RadioButton, event) -> bool:
        """Handle navigation keys for radio button group."""

        if event.keyval == Gdk.KEY_Tab and not event.state & Gdk.ModifierType.SHIFT_MASK:
            if isinstance(radio, RadioButtonWithActions) and radio.action_buttons:
                radio.action_buttons[0].grab_focus()
                return True
            return False

        # Left arrow: exit nested group first, then move to sidebar
        if event.keyval == Gdk.KEY_Left:
            parent: Gtk.Widget | None = self
            while parent is not None:
                if isinstance(parent, PreferencesGridBase):
                    if parent.is_in_multipage_detail():
                        parent.multipage_show_categories()
                        return True
                parent = parent.get_parent()
            self.focus_sidebar()
            return True

        if event.keyval in (Gdk.KEY_Up, Gdk.KEY_Down):
            group = radio.get_group()
            if not group:
                return False

            current_index = -1
            for i, r in enumerate(group):
                if r == radio:
                    current_index = i
                    break

            if current_index == -1:
                return False

            if event.keyval == Gdk.KEY_Down:
                next_index = (current_index - 1) % len(group)
            else:
                next_index = (current_index + 1) % len(group)

            next_radio = group[next_index]

            def activate_next():
                next_radio.grab_focus()
                next_radio.set_active(True)
                return False

            GLib.idle_add(activate_next)
            return True

        return False

    # pylint: disable-next=too-many-return-statements
    def _on_action_button_key_press(self, button: Gtk.Button, event) -> bool:
        """Handle Tab/Shift+Tab navigation for action buttons."""

        parent = button.get_parent()  # button_box
        if not parent:
            return False

        parent = parent.get_parent()  # hbox
        if not parent:
            return False

        radio = None
        for child in parent.get_children():
            if isinstance(child, Gtk.RadioButton):
                radio = child
                break

        if not radio or not isinstance(radio, RadioButtonWithActions):
            return False

        if not radio.action_buttons:
            return False

        action_buttons = radio.action_buttons

        try:
            current_index = action_buttons.index(button)
        except ValueError:
            return False

        if event.keyval == Gdk.KEY_Tab and not event.state & Gdk.ModifierType.SHIFT_MASK:
            if current_index < len(action_buttons) - 1:
                action_buttons[current_index + 1].grab_focus()
                return True
            return False
        if event.keyval == Gdk.KEY_ISO_Left_Tab or (
            event.keyval == Gdk.KEY_Tab and (event.state & Gdk.ModifierType.SHIFT_MASK)
        ):
            if current_index > 0:
                action_buttons[current_index - 1].grab_focus()
                return True
            radio.grab_focus()
            return True

        # Left arrow: exit nested group first, then move to sidebar
        if event.keyval == Gdk.KEY_Left:
            widget: Gtk.Widget | None = self
            while widget is not None:
                if isinstance(widget, PreferencesGridBase):
                    if widget.is_in_multipage_detail():
                        widget.multipage_show_categories()
                        return True
                widget = widget.get_parent()
            self.focus_sidebar()
            return True

        return False

    def _on_value_changed(self, widget: Gtk.Widget, *_args: Any) -> None:
        """Handle value changes in any widget."""

        if self._initializing:
            return

        # For radio buttons, only process the activation (not deactivation)
        if isinstance(widget, Gtk.RadioButton) and not widget.get_active():
            return

        # Check if this is an apply_immediately control
        tracks_changes = True
        if widget in self._widget_to_control_index:
            control = self._controls[self._widget_to_control_index[widget]]
            if isinstance(control, BooleanPreferenceControl) and control.apply_immediately:
                assert isinstance(widget, Gtk.Switch)
                control.setter(widget.get_active())
            elif isinstance(control, IntRangePreferenceControl) and control.apply_immediately:
                assert isinstance(widget, Gtk.SpinButton)
                control.setter(widget.get_value_as_int())
            elif isinstance(control, ColorPreferenceControl):
                assert isinstance(widget, Gtk.ColorButton)
                control.setter(self._rgba_to_hex(widget.get_rgba()))
            elif isinstance(control, SelectionPreferenceControl):
                if control.apply_immediately and control.setter is not None:
                    if isinstance(widget, Gtk.ComboBoxText):
                        active = widget.get_active()
                        if active >= 0:
                            value_list = control.values or control.options
                            control.setter(value_list[active])
                    elif isinstance(widget, Gtk.RadioButton):
                        if widget in self._radio_to_selection_value:
                            control.setter(self._radio_to_selection_value[widget])
                tracks_changes = control.tracks_changes

        if tracks_changes:
            self._has_unsaved_changes = True
        self._update_sensitivity()

    def _update_sensitivity(self) -> None:
        """Update widget and row sensitivity based on determine_sensitivity callbacks."""

        sensitivity_cache: dict[int, bool] = {}
        callback_results: dict[Callable[[], bool], bool] = {}
        for i, control in enumerate(self._controls):
            callback = control.determine_sensitivity
            if callback is not None:
                if callback not in callback_results:
                    callback_results[callback] = callback()
                sensitive = callback_results[callback]
                sensitivity_cache[i] = sensitive
                self._widgets[i].set_sensitive(sensitive)
                self._rows[i].set_sensitive(sensitive)

        for group_name, label in self._group_labels.items():
            group_indices = [i for i, c in enumerate(self._controls) if c.member_of == group_name]
            if not group_indices:
                continue

            all_insensitive = all(
                i in sensitivity_cache and not sensitivity_cache[i] for i in group_indices
            )
            label.set_sensitive(not all_insensitive)

    def has_changes(self) -> bool:
        """Return True if the user has made changes that haven't been written to file."""

        for i, control in enumerate(self._controls):
            if isinstance(control, IntRangePreferenceControl):
                widget = self._widgets[i]
                if isinstance(widget, Gtk.SpinButton):
                    widget.update()

        return self._has_unsaved_changes

    def reload(self) -> None:
        """Reload all values from their getters and refresh the UI."""

        self._has_unsaved_changes = False
        self.refresh()

    def refresh(self) -> None:
        """Update all widgets to reflect current values."""

        self._initializing = True

        for i, control in enumerate(self._controls):
            widget = self._widgets[i]

            if isinstance(control, BooleanPreferenceControl):
                assert isinstance(widget, Gtk.Switch)
                widget.set_active(control.getter())

            elif isinstance(control, IntRangePreferenceControl):
                assert isinstance(widget, Gtk.SpinButton)
                widget.set_value(control.getter())

            elif isinstance(control, FloatRangePreferenceControl):
                assert isinstance(widget, Gtk.Scale)
                widget.set_value(control.getter())

            elif isinstance(control, EnumPreferenceControl):
                assert isinstance(widget, Gtk.ComboBoxText)
                current_value = control.getter()
                value_list = control.values or control.options
                try:
                    index = value_list.index(current_value)
                    widget.set_active(index)
                except ValueError:
                    pass

            elif isinstance(control, ColorPreferenceControl):
                assert isinstance(widget, Gtk.ColorButton)
                self._set_color_button_hex(widget, control.getter())

            elif isinstance(control, SelectionPreferenceControl):
                current_value = control.getter()
                if isinstance(widget, Gtk.ComboBoxText):
                    # Combo box variant
                    value_list = control.values or control.options
                    try:
                        index = value_list.index(current_value)
                        widget.set_active(index)
                    except ValueError:
                        pass
                elif isinstance(widget, Gtk.RadioButton):
                    for radio in widget.get_group():
                        if radio in self._radio_to_selection_value:
                            if self._radio_to_selection_value[radio] == current_value:
                                radio.set_active(True)
                                break

        self._initializing = False
        self._update_sensitivity()

    # pylint: disable-next=too-many-statements
    def save_settings(self, profile: str = "", app_name: str = "") -> dict[str, Any]:
        """Save all values using their setters and return a dict of changes."""

        result = {}

        for i, control in enumerate(self._controls):
            widget = self._widgets[i]

            if isinstance(control, BooleanPreferenceControl):
                assert isinstance(widget, Gtk.Switch)
                value = widget.get_active()
                control.setter(value)
                if control.prefs_key:
                    result[control.prefs_key] = value

            elif isinstance(control, IntRangePreferenceControl):
                assert isinstance(widget, Gtk.SpinButton)
                value = int(widget.get_value())
                control.setter(value)
                if control.prefs_key:
                    result[control.prefs_key] = value

            elif isinstance(control, FloatRangePreferenceControl):
                assert isinstance(widget, Gtk.Scale)
                value = widget.get_value()
                control.setter(value)
                if control.prefs_key:
                    result[control.prefs_key] = value

            elif isinstance(control, EnumPreferenceControl):
                assert isinstance(widget, Gtk.ComboBoxText)
                active = widget.get_active()
                if active >= 0:
                    value_list = control.values or control.options
                    value = value_list[active]
                    control.setter(value)
                    if control.prefs_key:
                        result[control.prefs_key] = value

            elif isinstance(control, ColorPreferenceControl):
                assert isinstance(widget, Gtk.ColorButton)
                value = self._rgba_to_hex(widget.get_rgba())
                control.setter(value)
                if control.prefs_key:
                    result[control.prefs_key] = value

            elif isinstance(control, SelectionPreferenceControl):
                value = None
                if isinstance(widget, Gtk.ComboBoxText):
                    active = widget.get_active()
                    if active >= 0:
                        value_list = control.values or control.options
                        value = value_list[active]
                elif isinstance(widget, Gtk.RadioButton):
                    for radio in widget.get_group():
                        if radio.get_active() and radio in self._radio_to_selection_value:
                            value = self._radio_to_selection_value[radio]
                            break

                if value is not None and control.setter is not None:
                    control.setter(value)
                    if control.prefs_key:
                        result[control.prefs_key] = value

        self._has_unsaved_changes = False
        self._write_gsettings(result, profile, app_name)
        return result

    def _write_gsettings(self, result: dict, profile: str, app_name: str) -> None:
        """Writes this grid's settings to dconf if profile and schema are set."""

        if not profile or not self._gsettings_schema:
            return
        from . import gsettings_registry  # pylint: disable=import-outside-toplevel

        skip_defaults = not app_name and profile == "default"
        gsettings_registry.get_registry().save_schema(
            self._gsettings_schema,
            result,
            profile,
            app_name,
            skip_defaults,
        )

    def get_widget(self, index: int) -> Gtk.Widget | None:
        """Get the widget at the specified index, or None if out of range."""

        if 0 <= index < len(self._widgets):
            return self._widgets[index]
        return None

    def get_widget_for_control(self, control: ControlType) -> Gtk.Widget | None:
        """Find the widget corresponding to a control object, or None if not found."""

        for ctrl, widget in zip(self._controls, self._widgets, strict=True):
            if ctrl is control:
                return widget
        return None
