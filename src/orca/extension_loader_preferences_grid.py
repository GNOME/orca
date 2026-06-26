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

"""Preferences grid for user extension management."""

from __future__ import annotations

import os

import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # pylint: disable=no-name-in-module

from . import extension_loader, guilabels, orca_gui_base, preferences_grid_base


class ExtensionLoaderPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Preferences grid for approving and disabling user extensions."""

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for user extension preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.USER_EXTENSIONS,
            summary="Use these settings to approve and enable user extensions.",
            description=guilabels.EXTENSIONS_INFO,
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.USER_EXTENSIONS,
                    kind="list",
                    summary=(
                        "Lists user extension files and actions for approving or revoking them."
                    ),
                    dynamic_values=True,
                ),
            ),
        )

    def __init__(self) -> None:
        super().__init__(guilabels.USER_EXTENSIONS)
        self._loader = extension_loader.get_loader()
        user_data_dir = GLib.get_user_data_dir()  # pylint: disable=no-value-for-parameter
        self._extensions_dir = os.path.join(user_data_dir, "orca", "extensions")
        self._listbox: Gtk.ListBox | None = None
        self._scrolled: Gtk.ScrolledWindow | None = None
        self._rows_by_filename: dict[str, Gtk.ListBoxRow] = {}
        self._switches_by_filename: dict[str, Gtk.Switch] = {}
        self._info_buttons_by_filename: dict[str, Gtk.Button] = {}
        self._approve_buttons_by_filename: dict[str, Gtk.Button] = {}
        self._revoke_buttons_by_filename: dict[str, Gtk.Button] = {}
        self._summary_labels_by_filename: dict[str, Gtk.Label] = {}
        self._syncing_filenames: set[str] = set()
        self._build()
        self.refresh()

    def _build(self) -> None:
        """Create the Gtk widgets composing the grid."""

        row = 0

        info_listbox = self._create_info_listbox(guilabels.EXTENSIONS_INFO)
        info_listbox.set_margin_bottom(12)
        self.attach(info_listbox, 0, row, 1, 1)
        row += 1

        header_label = Gtk.Label(label=guilabels.USER_EXTENSIONS, xalign=0)
        header_label.get_style_context().add_class("heading")
        header_label.set_margin_bottom(6)
        self.attach(header_label, 0, row, 1, 1)
        row += 1

        self._scrolled = self._create_scrolled_window(Gtk.Box())
        self.attach(self._scrolled, 0, row, 1, 1)

    def reload(self) -> None:
        """Reload extension metadata and refresh the UI."""

        self.refresh()

    def save_settings(self, _profile: str = "", _app_name: str = "") -> dict:
        """Save settings for this grid."""

        return {}

    def refresh(self) -> None:
        """Rebuild the user extension list."""

        assert self._scrolled is not None
        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._listbox.get_style_context().add_class("frame")
        self._listbox.get_accessible().set_name(guilabels.USER_EXTENSIONS)
        self._rows_by_filename = {}
        self._switches_by_filename = {}
        self._info_buttons_by_filename = {}
        self._approve_buttons_by_filename = {}
        self._revoke_buttons_by_filename = {}
        self._summary_labels_by_filename = {}

        infos = self._loader.discover_user_extensions(self._extensions_dir)
        if not infos:
            self._listbox.add(self._create_info_row(guilabels.EXTENSIONS_NO_EXTENSIONS))
        else:
            for info in infos:
                self._add_extension_row(info)

        child = self._scrolled.get_child()
        if child is not None:
            self._scrolled.remove(child)
        self._scrolled.add(self._listbox)
        self._scrolled.show_all()

    def _add_extension_row(self, info: extension_loader.UserExtensionInfo) -> None:
        """Add one extension row to the list."""

        assert self._listbox is not None

        row, summary_label, _detail_label, action_buttons = self._create_action_list_row(
            self._get_summary_text(info),
            self._get_detail_text(info),
            actions=self._get_actions(info.filename),
            stack_labels=True,
        )

        switch = self._create_switch_control(
            self._on_switch_toggled,
            info.status is extension_loader.UserExtensionStatus.APPROVED,
            "",
            info.filename,
        )

        hbox = self._get_action_list_row_box(row)
        hbox.pack_start(switch, False, False, 0)

        self._listbox.add(row)
        self._rows_by_filename[info.filename] = row
        self._switches_by_filename[info.filename] = switch
        self._summary_labels_by_filename[info.filename] = summary_label
        self._info_buttons_by_filename[info.filename] = action_buttons["info"]
        self._approve_buttons_by_filename[info.filename] = action_buttons["approve"]
        self._revoke_buttons_by_filename[info.filename] = action_buttons["revoke"]
        self._sync_row(info)

    @staticmethod
    def _get_action_list_row_box(row: Gtk.ListBoxRow) -> Gtk.Box:
        """Returns the horizontal box in an action list row."""

        vbox = row.get_child()
        assert isinstance(vbox, Gtk.Box)
        children = vbox.get_children()
        assert children and isinstance(children[-1], Gtk.Box)
        return children[-1]

    def _get_actions(
        self,
        filename: str,
    ) -> list[preferences_grid_base.ListRowAction]:
        """Returns action buttons for an extension row."""

        return [
            preferences_grid_base.ListRowAction(
                "info",
                guilabels.EXTENSIONS_INFO_BUTTON,
                lambda _button: self._on_info_clicked(filename),
                "help-about-symbolic",
            ),
            preferences_grid_base.ListRowAction(
                "approve",
                guilabels.EXTENSIONS_APPROVE,
                lambda _button: self._on_approve_clicked(filename),
                "emblem-ok-symbolic",
            ),
            preferences_grid_base.ListRowAction(
                "revoke",
                guilabels.EXTENSIONS_REVOKE,
                lambda _button: self._on_revoke_clicked(filename),
                "user-trash-symbolic",
            ),
        ]

    def _get_info(self, filename: str) -> extension_loader.UserExtensionInfo | None:
        """Returns the current info for a user extension."""

        infos = self._loader.discover_user_extensions(self._extensions_dir)
        return next((info for info in infos if info.filename == filename), None)

    def _sync_row(self, info: extension_loader.UserExtensionInfo) -> None:
        """Update stable row widgets to match the extension status."""

        filename = info.filename
        summary_label = self._summary_labels_by_filename.get(filename)
        switch = self._switches_by_filename.get(filename)
        info_button = self._info_buttons_by_filename.get(filename)
        approve_button = self._approve_buttons_by_filename.get(filename)
        revoke_button = self._revoke_buttons_by_filename.get(filename)
        detail_text = self._get_detail_text(info)

        if summary_label is not None:
            self._set_stacked_label_text(summary_label, self._get_summary_text(info), detail_text)

        status = info.status
        can_approve = status in (
            extension_loader.UserExtensionStatus.UNAPPROVED,
            extension_loader.UserExtensionStatus.MODIFIED,
        )
        can_revoke = status in (
            extension_loader.UserExtensionStatus.APPROVED,
            extension_loader.UserExtensionStatus.DISABLED,
            extension_loader.UserExtensionStatus.MODIFIED,
        )
        can_toggle = status in (
            extension_loader.UserExtensionStatus.APPROVED,
            extension_loader.UserExtensionStatus.DISABLED,
        )

        if approve_button is not None:
            approve_label = guilabels.EXTENSIONS_APPROVE
            if status is extension_loader.UserExtensionStatus.MODIFIED:
                approve_label = guilabels.EXTENSIONS_REAPPROVE
            approve_button.get_accessible().set_name(approve_label)
            approve_button.set_sensitive(can_approve)

        if info_button is not None:
            info_button.set_sensitive(True)

        if revoke_button is not None:
            revoke_button.set_sensitive(can_revoke)

        if switch is not None:
            self._syncing_filenames.add(filename)
            switch.set_sensitive(can_toggle)
            switch.set_active(status is extension_loader.UserExtensionStatus.APPROVED)
            self._syncing_filenames.discard(filename)

    def _get_detail_text(self, info: extension_loader.UserExtensionInfo) -> str:
        """Returns the secondary row detail text for an extension."""

        if info.status in (
            extension_loader.UserExtensionStatus.APPROVED,
            extension_loader.UserExtensionStatus.DISABLED,
            extension_loader.UserExtensionStatus.UNAPPROVED,
        ):
            return info.description

        if info.description:
            return info.description
        status = self._get_status_label(info.status)
        return status

    @staticmethod
    def _get_display_name(info: extension_loader.UserExtensionInfo) -> str:
        """Returns the display name for an extension."""

        return info.group_label or info.class_name or guilabels.EXTENSIONS_STATUS_INVALID

    def _get_summary_text(self, info: extension_loader.UserExtensionInfo) -> str:
        """Returns the primary row text for an extension."""

        return f"{self._get_display_name(info)}: {info.filename}"

    @staticmethod
    def _get_status_label(status: extension_loader.UserExtensionStatus) -> str:
        """Returns the user-visible label for a status."""

        labels = {
            extension_loader.UserExtensionStatus.INVALID: guilabels.EXTENSIONS_STATUS_INVALID,
            extension_loader.UserExtensionStatus.UNAPPROVED: guilabels.EXTENSIONS_STATUS_UNAPPROVED,
            extension_loader.UserExtensionStatus.APPROVED: guilabels.EXTENSIONS_STATUS_APPROVED,
            extension_loader.UserExtensionStatus.DISABLED: guilabels.EXTENSIONS_STATUS_DISABLED,
            extension_loader.UserExtensionStatus.MODIFIED: guilabels.EXTENSIONS_STATUS_MODIFIED,
        }
        return labels[status]

    def _on_info_clicked(self, filename: str) -> None:
        """Show metadata for an extension."""

        info = self._get_info(filename)
        if info is None:
            return

        parent = self.get_toplevel()
        transient_for = parent if isinstance(parent, Gtk.Window) else None
        dialog = orca_gui_base.create_dialog(
            self._get_display_name(info),
            default_size=(640, -1),
            default_response=Gtk.ResponseType.CLOSE,
            resizable=False,
        )
        dialog.set_transient_for(transient_for)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        listbox.get_style_context().add_class("frame")
        listbox.set_header_func(self._separator_header_func, None)
        listbox.set_margin_top(6)
        listbox.set_margin_bottom(6)
        listbox.set_margin_start(6)
        listbox.set_margin_end(6)

        for label, value in self._get_info_dialog_rows(info):
            if label == guilabels.EXTENSIONS_INFO_WEBSITE:
                listbox.add(self._create_info_dialog_link_row(label, value))
            else:
                listbox.add(self._create_info_dialog_row(label, value))

        content_area = dialog.get_content_area()
        content_area.add(listbox)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    @staticmethod
    def _separator_header_func(row: Gtk.ListBoxRow, before: Gtk.ListBoxRow | None, _data) -> None:
        """Add separators between metadata rows."""

        if before is not None:
            row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    @staticmethod
    def _create_info_dialog_row(label: str, value: str) -> Gtk.ListBoxRow:
        """Returns a metadata row."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        label_widget = Gtk.Label(label=f"{label}: {value}", xalign=0)
        label_widget.set_margin_top(6)
        label_widget.set_margin_bottom(6)
        label_widget.set_margin_start(12)
        label_widget.set_margin_end(12)
        label_widget.set_hexpand(True)
        label_widget.set_line_wrap(True)
        label_widget.set_max_width_chars(72)

        row.add(label_widget)
        return row

    @staticmethod
    def _create_info_dialog_link_row(label: str, value: str) -> Gtk.ListBoxRow:
        """Returns a metadata row with an activatable link."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.set_margin_top(6)
        hbox.set_margin_bottom(6)
        hbox.set_margin_start(12)
        hbox.set_margin_end(12)

        label_widget = Gtk.Label(label=f"{label}: ", xalign=0)
        link_button = Gtk.LinkButton.new_with_label(value, value)
        link_button.get_accessible().set_name(f"{label}: {value}")
        link_button.set_relief(Gtk.ReliefStyle.NONE)

        def focus_link() -> bool:
            link_button.grab_focus()
            return False

        def on_row_focus_in(*_args) -> bool:
            GLib.idle_add(focus_link)
            return False

        row.connect("focus-in-event", on_row_focus_in)
        hbox.pack_start(label_widget, False, False, 0)
        hbox.pack_start(link_button, False, False, 0)
        row.add(hbox)
        return row

    def _get_info_dialog_rows(
        self,
        info: extension_loader.UserExtensionInfo,
    ) -> list[tuple[str, str]]:
        """Returns rows for the extension information dialog."""

        rows = [
            (guilabels.EXTENSIONS_INFO_NAME, self._get_display_name(info)),
            (guilabels.EXTENSIONS_INFO_DESCRIPTION, info.description),
            (guilabels.EXTENSIONS_INFO_LOCATION, info.filepath),
            (guilabels.EXTENSIONS_INFO_STATUS, self._get_status_label(info.status)),
            (guilabels.EXTENSIONS_INFO_VERSION, info.version),
            (guilabels.EXTENSIONS_INFO_AUTHOR, info.author),
            (guilabels.EXTENSIONS_INFO_ORGANIZATION, info.organization),
            (guilabels.EXTENSIONS_INFO_COPYRIGHT, info.copyright),
            (guilabels.EXTENSIONS_INFO_WEBSITE, info.website),
        ]
        return [(label, value) for label, value in rows if value]

    def _on_approve_clicked(self, filename: str) -> None:
        """Approve or re-approve an extension."""

        info = self._get_info(filename)
        if info is None:
            return

        self._loader.approve_extension_file(info.filepath)
        self._loader.reload_user_extensions(self._extensions_dir)
        if info := self._get_info(filename):
            self._sync_row(info)
            if switch := self._switches_by_filename.get(filename):
                switch.grab_focus()

    def _on_revoke_clicked(self, filename: str) -> None:
        """Revoke approval for an extension."""

        self._loader.revoke_extension(filename)
        self._loader.reload_user_extensions(self._extensions_dir)
        if info := self._get_info(filename):
            self._sync_row(info)
            if approve_button := self._approve_buttons_by_filename.get(filename):
                approve_button.grab_focus()

    def _on_switch_toggled(
        self,
        switch: Gtk.Switch,
        _pspec: object,
        filename: str,
    ) -> None:
        """Enable or disable an extension."""

        if filename in self._syncing_filenames:
            return

        info = self._get_info(filename)
        if info is None:
            return
        if info.class_name is None:
            return

        disabled = self._loader.get_disabled_extensions()
        if switch.get_active():
            if info.class_name not in disabled:
                return
            disabled = [name for name in disabled if name != info.class_name]
        elif info.class_name not in disabled:
            disabled = [*disabled, info.class_name]
        else:
            return

        self._loader.set_disabled_extensions(disabled)
        self._loader.reload_user_extensions(self._extensions_dir)
        if info := self._get_info(filename):
            self._sync_row(info)
