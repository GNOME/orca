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

# pylint: disable=no-member
# pylint: disable=too-many-instance-attributes

from __future__ import annotations

import os
import shutil
from typing import Any

import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # pylint: disable=no-name-in-module

from . import (
    command_manager,
    debug,
    extension_loader,
    extension_preferences,
    extension_preferences_dialog,
    guilabels,
    orca_gui_helpers,
    preferences_grid_base,
    presentation_manager,
)


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
        self._settings_buttons_by_filename: dict[str, Gtk.Button] = {}
        self._delete_buttons_by_filename: dict[str, Gtk.Button] = {}
        self._approval_buttons_by_filename: dict[str, Gtk.Button] = {}
        self._summary_labels_by_filename: dict[str, Gtk.Label] = {}
        self._approval_button_size_group = orca_gui_helpers.create_horizontal_size_group()
        self._staged_settings_by_class_name: dict[
            str,
            tuple[list[extension_preferences.ExtensionPreference], dict[str, Any]],
        ] = {}
        self._syncing_filenames: set[str] = set()
        self._build()
        self.refresh()

    def _build(self) -> None:
        """Create the Gtk widgets composing the grid."""

        row = 0

        info_listbox = orca_gui_helpers.create_info_listbox(guilabels.EXTENSIONS_INFO)
        self.attach(info_listbox, 0, row, 1, 1)
        row += 1

        section_box, section_content, _heading_label = orca_gui_helpers.create_section_box(
            guilabels.USER_EXTENSIONS,
            margin_top=0,
        )
        self._scrolled = orca_gui_helpers.create_preferences_scrolled_window()
        orca_gui_helpers.add_section_content(section_box, section_content, self._scrolled)
        self.attach(section_box, 0, row, 1, 1)

    def reload(self) -> None:
        """Reload extension metadata and refresh the UI."""

        self.refresh()

    def save_settings(self, _profile: str = "", _app_name: str = "") -> dict:
        """Save settings for this grid."""

        result: dict[str, Any] = {}
        for class_name, (preferences, values) in self._staged_settings_by_class_name.items():
            extension = self._loader.get_loaded_user_extension(class_name)
            if extension is None:
                continue

            for pref in preferences:
                value = values[pref.key]
                if value == pref.default:
                    extension.settings.reset(pref.key)
                else:
                    extension.settings.set(pref.key, value)
                result[f"{class_name}/{pref.key}"] = value

        self._staged_settings_by_class_name = {}
        self._has_unsaved_changes = False
        return result

    def refresh(self) -> None:
        """Rebuild the user extension list."""

        assert self._scrolled is not None
        self._listbox = orca_gui_helpers.create_framed_listbox(
            selection_mode=Gtk.SelectionMode.SINGLE,
            accessible_name=guilabels.USER_EXTENSIONS,
        )
        self._rows_by_filename = {}
        self._switches_by_filename = {}
        self._info_buttons_by_filename = {}
        self._settings_buttons_by_filename = {}
        self._delete_buttons_by_filename = {}
        self._approval_buttons_by_filename = {}
        self._summary_labels_by_filename = {}
        self._approval_button_size_group = orca_gui_helpers.create_horizontal_size_group()

        infos = self._loader.discover_user_extensions(self._extensions_dir)
        if not infos:
            self._listbox.add(orca_gui_helpers.create_info_row(guilabels.EXTENSIONS_NO_EXTENSIONS))
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

        row, summary_label, _detail_label, action_buttons = orca_gui_helpers.create_action_list_row(
            self._get_summary_text(info),
            self._get_detail_text(info),
            actions=self._get_actions(info.filename),
            stack_labels=True,
        )

        switch = orca_gui_helpers.create_switch_control(
            self._on_switch_toggled,
            info.status is extension_loader.UserExtensionStatus.APPROVED,
            "",
            handler_args=(info.filename,),
        )

        hbox = self._get_action_list_row_box(row)
        hbox.pack_start(switch, False, False, 0)

        self._listbox.add(row)
        self._rows_by_filename[info.filename] = row
        self._switches_by_filename[info.filename] = switch
        self._summary_labels_by_filename[info.filename] = summary_label
        self._info_buttons_by_filename[info.filename] = action_buttons["info"]
        self._settings_buttons_by_filename[info.filename] = action_buttons["settings"]
        self._delete_buttons_by_filename[info.filename] = action_buttons["delete"]
        self._approval_buttons_by_filename[info.filename] = action_buttons["approval"]
        self._configure_approval_button(action_buttons["approval"])
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
    ) -> list[orca_gui_helpers.ListRowAction]:
        """Returns action buttons for an extension row."""

        return [
            orca_gui_helpers.ListRowAction(
                "info",
                guilabels.EXTENSIONS_INFO_BUTTON,
                lambda _button: self._on_info_clicked(filename),
                "help-about-symbolic",
            ),
            orca_gui_helpers.ListRowAction(
                "settings",
                guilabels.EXTENSIONS_SETTINGS_BUTTON,
                lambda _button: self._on_settings_clicked(filename),
                "emblem-system-symbolic",
            ),
            orca_gui_helpers.ListRowAction(
                "delete",
                guilabels.EXTENSIONS_DELETE,
                lambda _button: self._on_delete_clicked(filename),
                "user-trash-symbolic",
            ),
            orca_gui_helpers.ListRowAction(
                "approval",
                guilabels.EXTENSIONS_APPROVE,
                lambda _button: self._on_approval_clicked(filename),
            ),
        ]

    def _configure_approval_button(self, button: Gtk.Button) -> None:
        """Configure the stable approve/revoke action button."""

        button.set_valign(Gtk.Align.CENTER)
        button.set_size_request(112, -1)
        self._approval_button_size_group.add_widget(button)

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
        settings_button = self._settings_buttons_by_filename.get(filename)
        delete_button = self._delete_buttons_by_filename.get(filename)
        approval_button = self._approval_buttons_by_filename.get(filename)
        detail_text = self._get_detail_text(info)

        if summary_label is not None:
            orca_gui_helpers.set_stacked_label_text(
                summary_label,
                self._get_summary_text(info),
                detail_text,
            )

        status = info.status
        can_toggle = status in (
            extension_loader.UserExtensionStatus.APPROVED,
            extension_loader.UserExtensionStatus.DISABLED,
        )

        if approval_button is not None:
            self._sync_approval_button(approval_button, status)

        if info_button is not None:
            info_button.set_sensitive(True)

        if settings_button is not None:
            settings_button.set_sensitive(self._can_show_settings(info))

        if delete_button is not None:
            delete_button.set_sensitive(True)

        if switch is not None:
            self._syncing_filenames.add(filename)
            switch.set_sensitive(can_toggle)
            switch.set_active(status is extension_loader.UserExtensionStatus.APPROVED)
            self._syncing_filenames.discard(filename)

    @staticmethod
    def _sync_approval_button(
        button: Gtk.Button,
        status: extension_loader.UserExtensionStatus,
    ) -> None:
        """Sync approval action button with status."""

        label = guilabels.EXTENSIONS_APPROVE
        sensitive = status in (
            extension_loader.UserExtensionStatus.UNAPPROVED,
            extension_loader.UserExtensionStatus.MODIFIED,
            extension_loader.UserExtensionStatus.APPROVED,
            extension_loader.UserExtensionStatus.DISABLED,
        )

        if status is extension_loader.UserExtensionStatus.MODIFIED:
            label = guilabels.EXTENSIONS_REAPPROVE
        elif status in (
            extension_loader.UserExtensionStatus.APPROVED,
            extension_loader.UserExtensionStatus.DISABLED,
        ):
            label = guilabels.EXTENSIONS_REVOKE

        button.set_image(None)
        button.set_label(label)
        button.get_accessible().set_name(label)
        button.set_sensitive(sensitive)

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
        dialog = orca_gui_helpers.create_dialog(
            self._get_display_name(info),
            default_size=(640, -1),
            default_response=Gtk.ResponseType.CLOSE,
            resizable=False,
        )
        dialog.set_transient_for(transient_for)

        listbox = orca_gui_helpers.create_framed_listbox(
            selection_mode=Gtk.SelectionMode.SINGLE,
            separators=True,
        )
        listbox.set_margin_top(6)
        listbox.set_margin_bottom(6)
        listbox.set_margin_start(6)
        listbox.set_margin_end(6)

        for label, value in self._get_info_dialog_rows(info):
            if label == guilabels.EXTENSIONS_INFO_WEBSITE:
                listbox.add(orca_gui_helpers.create_key_link_row(label, value))
            else:
                listbox.add(orca_gui_helpers.create_key_value_row(label, value))

        content_area = dialog.get_content_area()
        content_area.add(listbox)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def _can_show_settings(self, info: extension_loader.UserExtensionInfo) -> bool:
        """Returns whether info has user-visible settings."""

        if info.status is not extension_loader.UserExtensionStatus.APPROVED:
            return False
        if info.class_name is None:
            return False
        extension = self._loader.get_loaded_user_extension(info.class_name)
        if extension is None:
            return False
        return any(
            extension_preferences.is_supported_in_generated_dialog(pref)
            for pref in extension.get_preferences()
        )

    def _on_settings_clicked(self, filename: str) -> None:
        """Show settings for an extension."""

        info = self._get_info(filename)
        if info is None or info.class_name is None:
            return

        extension = self._loader.get_loaded_user_extension(info.class_name)
        if extension is None:
            return

        preferences = extension.get_preferences()
        if not preferences:
            return

        parent = self.get_toplevel()
        transient_for = parent if isinstance(parent, Gtk.Window) else None
        dialog = extension_preferences_dialog.ExtensionPreferencesDialog(
            extension,
            preferences,
            self._get_staged_settings(info.class_name),
            transient_for,
        )
        values = dialog.run()
        if values is None:
            return

        staged_preferences = [pref for pref in preferences if pref.key in values]
        self._staged_settings_by_class_name[info.class_name] = (staged_preferences, values)
        self._has_unsaved_changes = True

    def _get_staged_settings(self, class_name: str) -> dict[str, Any] | None:
        """Return currently staged settings for class_name."""

        staged = self._staged_settings_by_class_name.get(class_name)
        if staged is None:
            return None
        _preferences, values = staged
        return values

    def _get_info_dialog_rows(
        self,
        info: extension_loader.UserExtensionInfo,
    ) -> list[tuple[str, str]]:
        """Returns rows for the extension information dialog."""

        rows = [
            (guilabels.EXTENSIONS_INFO_NAME, self._get_display_name(info)),
            (guilabels.EXTENSIONS_INFO_DESCRIPTION, info.description),
            (guilabels.EXTENSIONS_INFO_LOCATION, info.filepath),
            (guilabels.EXTENSIONS_INFO_STATUS, self._get_info_status(info)),
            (guilabels.EXTENSIONS_INFO_VERSION, info.version),
            (guilabels.EXTENSIONS_INFO_AUTHOR, info.author),
            (guilabels.EXTENSIONS_INFO_ORGANIZATION, info.organization),
            (guilabels.EXTENSIONS_INFO_COPYRIGHT, info.copyright),
            (guilabels.EXTENSIONS_INFO_WEBSITE, info.website),
        ]
        return [(label, value) for label, value in rows if value]

    def _get_info_status(self, info: extension_loader.UserExtensionInfo) -> str:
        """Returns the status text for the extension information dialog."""

        status = self._get_status_label(info.status)
        conflict_note = self._get_keybinding_conflicts(info)
        if conflict_note:
            return f"{status}; {conflict_note}"
        return status

    @staticmethod
    def _get_keybinding_conflicts(info: extension_loader.UserExtensionInfo) -> str:
        """Returns any keybinding conflicts for info."""

        if info.status is not extension_loader.UserExtensionStatus.APPROVED:
            return ""

        if not info.class_name:
            return ""

        has_conflicts = command_manager.get_manager().has_user_extension_keybinding_conflicts(
            info.class_name
        )
        if not has_conflicts:
            return ""

        return guilabels.EXTENSIONS_INFO_KEYBINDING_CONFLICT

    def _on_approval_clicked(self, filename: str) -> None:
        """Approve, re-approve, or revoke approval for an extension."""

        info = self._get_info(filename)
        if info is None:
            return

        class_name = info.class_name
        revoking = info.status in (
            extension_loader.UserExtensionStatus.APPROVED,
            extension_loader.UserExtensionStatus.DISABLED,
        )
        if revoking:
            self._loader.revoke_extension(filename)
            if class_name:
                self._loader.notify_user_extension_state_changed(class_name, False)
        else:
            self._loader.approve_extension_file(info.filepath)

        self._loader.reload_user_extensions(self._extensions_dir)
        if class_name and not revoking:
            self._loader.notify_user_extension_state_changed(class_name, True)
        if info := self._get_info(filename):
            self._sync_row(info)

    def _on_delete_clicked(self, filename: str) -> None:
        """Delete an extension file or package directory."""

        info = self._get_info(filename)
        if info is None:
            return

        if not self._confirm_delete(info):
            return

        if not self._is_deletable_extension_path(info.filepath):
            tokens = [
                "EXTENSION LOADER PREFERENCES: Refusing to delete unexpected path",
                info.filepath,
            ]
            debug.print_tokens(debug.LEVEL_WARNING, tokens, True)
            self._present_delete_error(info)
            return

        try:
            if os.path.isdir(info.filepath) and not os.path.islink(info.filepath):
                shutil.rmtree(info.filepath)
            else:
                os.remove(info.filepath)
        except OSError as error:
            msg = f"EXTENSION LOADER PREFERENCES: Could not delete {info.filepath}: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            self._present_delete_error(info)
            self._loader.reload_user_extensions(self._extensions_dir)
            self.refresh()
            return

        if info.class_name:
            self._loader.notify_user_extension_state_changed(info.class_name, False)
        self._loader.revoke_extension(filename)
        if info.class_name:
            disabled = [
                class_name
                for class_name in self._loader.get_disabled_extensions()
                if class_name != info.class_name
            ]
            self._loader.set_disabled_extensions(disabled)
            self._staged_settings_by_class_name.pop(info.class_name, None)

        self._loader.reload_user_extensions(self._extensions_dir)
        self.refresh()

    def _is_deletable_extension_path(self, filepath: str) -> bool:
        """Returns True if filepath is a direct child of the user extensions directory."""

        extensions_dir = os.path.realpath(self._extensions_dir)
        target = os.path.realpath(filepath)
        if os.path.dirname(target) != extensions_dir:
            return False
        return os.path.basename(target) == os.path.basename(filepath)

    def _confirm_delete(self, info: extension_loader.UserExtensionInfo) -> bool:
        """Returns True if the user confirms deleting info."""

        parent = self.get_toplevel()
        transient_for = parent if isinstance(parent, Gtk.Window) else None
        dialog = Gtk.MessageDialog(
            transient_for=transient_for,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=guilabels.EXTENSIONS_DELETE_CONFIRMATION_TITLE,
        )
        dialog.format_secondary_text(
            guilabels.EXTENSIONS_DELETE_CONFIRMATION_MESSAGE % self._get_display_name(info)
        )
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def _present_delete_error(self, info: extension_loader.UserExtensionInfo) -> None:
        """Present a deletion error message."""

        presentation_manager.get_manager().present_message(
            guilabels.EXTENSIONS_DELETE_ERROR_MESSAGE % self._get_display_name(info),
        )

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
        enabled = switch.get_active()
        if enabled:
            if info.class_name not in disabled:
                return
            disabled = [name for name in disabled if name != info.class_name]
        elif info.class_name not in disabled:
            disabled = [*disabled, info.class_name]
        else:
            return

        self._loader.set_disabled_extensions(disabled)
        if not enabled:
            self._loader.notify_user_extension_state_changed(info.class_name, False)
        self._loader.reload_user_extensions(self._extensions_dir)
        if enabled:
            self._loader.notify_user_extension_state_changed(info.class_name, True)
        if info := self._get_info(filename):
            self._sync_row(info)
