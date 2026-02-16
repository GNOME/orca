# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

# pylint: disable=wrong-import-position
# pylint: disable=c-extension-no-member
# pylint: disable=no-member
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

"""Displays a GUI for the user to set Orca preferences."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import time
from typing import Any, TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GObject

from . import braille_presenter
from . import chat_presenter
from . import command_manager
from . import debug
from . import document_presenter
from . import event_manager
from . import guilabels
from . import learn_mode_presenter
from . import messages
from . import mouse_review
from . import orca
from . import preferences_grid_base
from . import presentation_manager
from . import profile_manager
from . import pronunciation_dictionary_manager
from . import say_all_presenter
from . import settings
from . import settings_manager
from . import sound_presenter
from . import speech_presenter
from . import spellcheck_presenter
from . import system_information_presenter
from . import text_attribute_manager
from . import typing_echo_presenter
from .ax_object import AXObject

if TYPE_CHECKING:
    from .scripts import default


class NavigationRow(Gtk.ListBoxRow):
    """ListBoxRow with a panel_id attribute for navigation."""

    def __init__(self, panel_id: str | None = None) -> None:
        super().__init__()
        self.panel_id = panel_id


class OrcaSetupGUI(Gtk.ApplicationWindow):  # pylint: disable=too-many-instance-attributes
    """Preferences window for configuring Orca screen reader settings."""

    WINDOW: OrcaSetupGUI | None = None

    def __init__(self, script: "default.Script", prefs_dict: dict[str, Any]) -> None:
        if OrcaSetupGUI.WINDOW is not None:
            return

        super().__init__(title=guilabels.DIALOG_SCREEN_READER_PREFERENCES)

        self.connect("destroy", self.window_destroyed)
        self.connect("delete-event", self.window_closed)

        self.prefs_dict = prefs_dict
        self.script = script
        self._settings_applied = False
        self._app_name: str | None = None
        if script.app is not None:
            self._app_name = AXObject.get_name(script.app) or None
        self._current_page_title: str = ""
        self._current_panel_id: str | None = None
        self._original_profile: str = profile_manager.get_manager().get_active_profile()

        titlebar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.left_headerbar = Gtk.HeaderBar()
        self.left_headerbar.set_show_close_button(True)
        self.left_headerbar.set_title(guilabels.DIALOG_SCREEN_READER_PREFERENCES)

        self.menu_button = Gtk.MenuButton()
        menu_image = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
        self.menu_button.set_image(menu_image)
        self.menu_button.get_accessible().set_name(guilabels.MENU_BUTTON_OPTIONS)

        popover = Gtk.Popover()
        menu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        help_item = Gtk.ModelButton()
        help_item.set_property("text", guilabels.DIALOG_HELP)
        help_item.connect("clicked", lambda _: self.help_button_clicked(None))
        menu_box.pack_start(help_item, False, False, 0)

        self.apply_item = Gtk.ModelButton()
        self.apply_item.set_property("text", guilabels.DIALOG_APPLY)
        self.apply_item.connect("clicked", lambda _: self.apply_button_clicked(None))
        menu_box.pack_start(self.apply_item, False, False, 0)

        self.save_item = Gtk.ModelButton()
        self.save_item.set_property("text", guilabels.BTN_SAVE)
        self.save_item.connect("clicked", lambda _: self.ok_button_clicked(None))
        menu_box.pack_start(self.save_item, False, False, 0)

        # Save Profile As is only for global preferences (profiles are global)
        if not self._app_name:
            save_as_item = Gtk.ModelButton()
            save_as_item.set_property("text", guilabels.PROFILE_SAVE_AS_TITLE)
            save_as_item.connect("clicked", lambda _: self._on_save_profile_as())
            menu_box.pack_start(save_as_item, False, False, 0)

        cancel_item = Gtk.ModelButton()
        cancel_item.set_property("text", guilabels.DIALOG_CANCEL)
        cancel_item.connect("clicked", lambda _: self.cancel_button_clicked(None))
        menu_box.pack_start(cancel_item, False, False, 0)

        menu_box.show_all()
        popover.add(menu_box)
        self.menu_button.set_popover(popover)

        self.left_headerbar.pack_end(self.menu_button)

        titlebar_box.pack_start(self.left_headerbar, False, False, 0)

        titlebar_separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        titlebar_box.pack_start(titlebar_separator, False, False, 0)

        self.panel_headerbar = Gtk.HeaderBar()
        self.panel_headerbar.set_show_close_button(False)
        self.panel_headerbar.set_title("")

        titlebar_box.pack_start(self.panel_headerbar, True, True, 0)

        self.set_titlebar(titlebar_box)

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.sidebar_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.sidebar_scrolled = Gtk.ScrolledWindow()
        self.sidebar_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.get_accessible().set_name(guilabels.PREFERENCES_CATEGORIES)
        self.listbox.connect("row-selected", self._on_row_selected)
        self.sidebar_scrolled.add(self.listbox)
        self.sidebar_vbox.pack_start(self.sidebar_scrolled, True, True, 0)

        self.listbox.connect("key-press-event", self._on_listbox_key_press)

        self.hbox.pack_start(self.sidebar_vbox, False, False, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.hbox.pack_start(separator, False, False, 0)

        self.content_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vhomogeneous(False)
        stack_scrolled = Gtk.ScrolledWindow()
        stack_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        stack_scrolled.add(self.stack)
        self.content_vbox.pack_start(stack_scrolled, True, True, 0)

        self.hbox.pack_start(self.content_vbox, True, True, 0)

        main_vbox.pack_start(self.hbox, True, True, 0)

        self.add(main_vbox)

        # Create all preference grids
        # Profiles grid controls are insensitive for app-specific prefs
        prof_manager = profile_manager.get_manager()
        self.profiles_grid = prof_manager.create_preferences_grid(
            profile_loaded_callback=self._on_profile_loaded,
            is_app_specific=bool(self._app_name),
            labels_update_callback=self.update_menu_labels,
            unsaved_changes_checker=self._has_unsaved_changes_in_grids,
        )
        self.stack.add_named(self.profiles_grid, "profiles")
        self._add_navigation_row("profiles", self.profiles_grid.get_label().get_text())
        self.update_menu_labels()

        presenter = speech_presenter.get_presenter()

        def update_title(title: str) -> None:
            """Update the panel header title and window accessible name."""

            self._set_page_title(title)

        self.speech_grid = presenter.create_speech_preferences_grid(
            title_change_callback=update_title
        )
        self.stack.add_named(self.speech_grid, "speech")
        self._add_navigation_row("speech", self.speech_grid.get_label().get_text())

        braille_pres = braille_presenter.get_presenter()
        self.braille_grid = braille_pres.create_preferences_grid(title_change_callback=update_title)
        self.stack.add_named(self.braille_grid, "braille")
        self._add_navigation_row("braille", self.braille_grid.get_label().get_text())

        sound_pres = sound_presenter.get_presenter()
        self.sound_grid = sound_pres.create_preferences_grid(title_change_callback=update_title)
        self.stack.add_named(self.sound_grid, "sound")
        self._add_navigation_row("sound", self.sound_grid.get_label().get_text())

        cmd_manager = command_manager.get_manager()
        self.keybindings_grid = cmd_manager.create_preferences_grid(
            self.script, title_change_callback=update_title
        )
        self.stack.add_named(self.keybindings_grid, "keybindings")
        self._add_navigation_row("keybindings", self.keybindings_grid.get_label().get_text())

        typing_pres = typing_echo_presenter.get_presenter()
        self.typing_echo_grid = typing_pres.create_preferences_grid()
        self.stack.add_named(self.typing_echo_grid, "typing_echo")
        self._add_navigation_row("typing_echo", self.typing_echo_grid.get_label().get_text())

        mouse_reviewer = mouse_review.get_reviewer()
        self.mouse_grid = mouse_reviewer.create_preferences_grid()
        self.stack.add_named(self.mouse_grid, "mouse")
        self._add_navigation_row("mouse", self.mouse_grid.get_label().get_text())

        doc_presenter = document_presenter.get_presenter()
        self.document_grid = doc_presenter.create_preferences_grid(update_title)
        self.stack.add_named(self.document_grid, "documents")
        self._add_navigation_row("documents", self.document_grid.get_label().get_text())

        say_all_pres = say_all_presenter.get_presenter()
        self.say_all_grid = say_all_pres.create_preferences_grid()
        self.stack.add_named(self.say_all_grid, "say_all")
        self._add_navigation_row("say_all", self.say_all_grid.get_label().get_text())

        pronunciation_manager = pronunciation_dictionary_manager.get_manager()
        self.pronunciation_grid = pronunciation_manager.create_preferences_grid(self.script)
        self.stack.add_named(self.pronunciation_grid, "pronunciation")
        self._add_navigation_row("pronunciation", self.pronunciation_grid.get_label().get_text())

        spellcheck_pres = spellcheck_presenter.get_presenter()
        self.spellcheck_grid = spellcheck_pres.create_preferences_grid()
        self.stack.add_named(self.spellcheck_grid, "spellcheck")
        self._add_navigation_row("spellcheck", self.spellcheck_grid.get_label().get_text())

        chat_pres = chat_presenter.get_presenter()
        self.chat_grid = chat_pres.create_preferences_grid()
        self.stack.add_named(self.chat_grid, "chat")
        self._add_navigation_row("chat", self.chat_grid.get_label().get_text())

        text_attr_mgr = text_attribute_manager.get_manager()
        self.text_attributes_grid = text_attr_mgr.create_preferences_grid()
        self.stack.add_named(self.text_attributes_grid, "text_attributes")
        self._add_navigation_row(
            "text_attributes", self.text_attributes_grid.get_label().get_text()
        )

        system_info_presenter = system_information_presenter.get_presenter()
        self.time_and_date_grid = system_info_presenter.create_time_and_date_preferences_grid()
        self.stack.add_named(self.time_and_date_grid, "time_and_date")
        self._add_navigation_row("time_and_date", self.time_and_date_grid.get_label().get_text())

        self._page_to_grid = {
            "speech": self.speech_grid,
            "braille": self.braille_grid,
            "keybindings": self.keybindings_grid,
            "typing_echo": self.typing_echo_grid,
            "say_all": self.say_all_grid,
            "spellcheck": self.spellcheck_grid,
            "chat": self.chat_grid,
            "mouse": self.mouse_grid,
            "documents": self.document_grid,
            "pronunciation": self.pronunciation_grid,
            "sound": self.sound_grid,
            "time_and_date": self.time_and_date_grid,
            "text_attributes": self.text_attributes_grid,
            "profiles": self.profiles_grid,
        }

        for grid in self._page_to_grid.values():
            grid.set_focus_sidebar_callback(self._focus_sidebar)

        first_row = self.listbox.get_row_at_index(0)
        if first_row:
            self.listbox.select_row(first_row)

        self._init_gui_state()

    def _sync_headerbar_widths(self) -> None:
        headerbar_width = self.left_headerbar.get_allocated_width()
        sidebar_width = self.sidebar_vbox.get_allocated_width()
        max_width = max(headerbar_width, sidebar_width)

        self.left_headerbar.set_size_request(max_width, -1)
        self.sidebar_vbox.set_size_request(max_width, -1)

    def _set_height_from_sidebar(self) -> None:
        """Set window height to fit the sidebar items, capped at 800px."""

        sidebar_height = self.listbox.get_preferred_height()[1]
        headerbar_height = self.left_headerbar.get_allocated_height()
        height = min(sidebar_height + headerbar_height, 800)
        self.resize(self.get_allocated_width(), height)

    def _on_listbox_key_press(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        if event.keyval == Gdk.KEY_Tab:
            self.stack.child_focus(Gtk.DirectionType.TAB_FORWARD)
            return True
        if event.keyval == Gdk.KEY_ISO_Left_Tab:
            # Shift+Tab from listbox should go back to menu button
            self.menu_button.grab_focus()
            return True
        return False

    def _focus_sidebar(self) -> None:
        """Move focus to the sidebar navigation listbox."""

        selected_row = self.listbox.get_selected_row()
        if selected_row:
            selected_row.grab_focus()
        else:
            self.listbox.grab_focus()

    def _add_navigation_row(self, panel_id: str, label_text: str) -> NavigationRow:
        """Add a navigation row to the sidebar listbox and return it."""

        row = NavigationRow(panel_id=panel_id)

        label = Gtk.Label(label=label_text, xalign=0)
        label.set_margin_start(12)
        label.set_margin_end(12)
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        row.add(label)

        self.listbox.add(row)
        return row

    def _on_row_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        """Handle listbox row selection and switch to the selected panel."""

        if row is None or not isinstance(row, NavigationRow):
            return

        # Skip if this is a non-selectable header row
        if row.panel_id is None:
            return

        panel_id = row.panel_id

        # Update the panel title in headerbar and accessible name
        if panel_id == "application":
            title = AXObject.get_name(self.script.app)
        else:
            child = self.stack.get_child_by_name(panel_id)
            title = child.get_label().get_text()

        self._set_page_title(title)

        self.stack.set_visible_child_name(panel_id)

        # Only reset multi-page grids when switching to a different panel.
        # This preserves sub-category state when focus returns to the
        # sidebar via Shift-Tab without changing the selected row.
        child = self.stack.get_child_by_name(panel_id)
        if isinstance(child, preferences_grid_base.PreferencesGridBase):
            if panel_id != self._current_panel_id:
                child.on_becoming_visible()

        self._current_panel_id = panel_id

    def write_user_preferences(
        self, pronunciation_dict: dict[str, Any], key_bindings_dict: dict[str, Any]
    ) -> None:
        """Write out the user's generic Orca preferences."""

        # For backwards compatibility (These settings no longer exist, but older versions of
        # Orca assume these key exist in the prefs dict.)
        self.prefs_dict["progressBarUpdateInterval"] = self.prefs_dict.get(
            "progressBarSpeechInterval", 10
        )
        self.prefs_dict["progressBarVerbosity"] = self.prefs_dict.get(
            "progressBarSpeechVerbosity", settings.PROGRESS_BAR_APPLICATION
        )

        settings.speechSystemOverride = None
        settings_manager.get_manager().save_settings(
            self.script, self.prefs_dict, pronunciation_dict, key_bindings_dict
        )

    def _init_gui_state(self, include_profiles: bool = False) -> None:
        """Adjust the settings of the various widgets based on user settings."""

        self._reload_all_grids(include_profiles=include_profiles)

    def show_gui(self) -> None:
        """Show the Orca configuration GUI window."""

        # Helper to enable configuring mode after a brief delay
        def enable_configuring_mode():
            settings_manager.get_manager().set_configuring(True)

            return False

        if OrcaSetupGUI.WINDOW is not None:
            OrcaSetupGUI.WINDOW.present()
            return

        OrcaSetupGUI.WINDOW = self

        accel_group = Gtk.AccelGroup()
        OrcaSetupGUI.WINDOW.add_accel_group(accel_group)

        # Select first row and set visible child before showing dialog
        first_row = self.listbox.get_row_at_index(0)
        if first_row and isinstance(first_row, NavigationRow) and first_row.panel_id:
            self.listbox.select_row(first_row)
            panel_id = first_row.panel_id
            # Set initial panel title in headerbar
            if panel_id == "application":
                title = AXObject.get_name(self.script.app)
            else:
                child = self.stack.get_child_by_name(panel_id)
                title = child.get_label().get_text()
            self._set_page_title(title)
            self.stack.set_visible_child_name(panel_id)

        OrcaSetupGUI.WINDOW.show_all()
        self._sync_headerbar_widths()
        self._set_height_from_sidebar()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(150)
        OrcaSetupGUI.WINDOW.present_with_time(time.time())

        # Set accessible name after window is realized
        def set_accessible_name() -> bool:
            self.update_menu_labels()
            return False

        GLib.idle_add(set_accessible_name)

        # Enable configuring mode after a brief delay to allow initial setup to complete
        GLib.timeout_add(100, enable_configuring_mode)

    def help_button_clicked(self, _widget: Gtk.Button) -> None:
        """Handle Help button click to show preferences help."""

        learn_mode_presenter.get_presenter().show_help(page="preferences")

    def _reload_all_grids(self, include_profiles: bool = False) -> None:
        """Reload all preference grids from settings."""

        self.speech_grid.reload()
        self.braille_grid.reload()
        self.sound_grid.reload()
        self.mouse_grid.reload()
        self.document_grid.reload()
        self.pronunciation_grid.reload()
        if include_profiles:
            self.profiles_grid.reload()
        self.time_and_date_grid.reload()
        self.text_attributes_grid.reload()
        self.typing_echo_grid.reload()
        self.say_all_grid.reload()
        self.spellcheck_grid.reload()
        self.chat_grid.reload()
        self.keybindings_grid.reload()

    def apply_button_clicked(self, _widget: Gtk.Button) -> None:
        """Handle Apply button click to save and apply preferences."""

        msg = "PREFERENCES DIALOG: Apply button clicked"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        profile_data = self.prefs_dict.get("profile", settings.profile)
        profile_name = profile_data[1] if isinstance(profile_data, list) else "default"
        save_app = self._app_name or ""

        # Save profiles first so any renames happen before saving other settings
        # (profiles are global, not saved for app-specific preferences)
        if not self._app_name:
            profile_values = self.profiles_grid.save_settings()
            self.prefs_dict.update(profile_values)

        speech_values = self.speech_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(speech_values)

        braille_values = self.braille_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(braille_values)
        sound_values = self.sound_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(sound_values)
        updated_values = self.typing_echo_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(updated_values)
        say_all_values = self.say_all_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(say_all_values)
        spellcheck_values = self.spellcheck_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(spellcheck_values)
        chat_values = self.chat_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(chat_values)
        mouse_values = self.mouse_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(mouse_values)
        document_values = self.document_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(document_values)
        time_and_date_values = self.time_and_date_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(time_and_date_values)
        text_attr_values = self.text_attributes_grid.save_settings(profile_name, save_app)
        self.prefs_dict.update(text_attr_values)
        pronunciation_dict = self.pronunciation_grid.save_settings(profile_name, save_app)
        keybindings_general, key_bindings_dict = self.keybindings_grid.save_settings(
            profile_name, save_app
        )
        self.prefs_dict.update(keybindings_general)

        self.write_user_preferences(pronunciation_dict, key_bindings_dict)
        orca.load_user_settings(self.script, skip_reload_message=True)

        # Speak the settings reloaded message after a delay to ensure speech has fully started.
        def speak_settings_reloaded() -> bool:
            presentation_manager.get_manager().speak_message(messages.SETTINGS_RELOADED)
            return False

        GLib.timeout_add(100, speak_settings_reloaded)

        self._reload_all_grids()

        # Re-apply user keybinding overrides and refresh grabs so changes work immediately.
        command_manager.get_manager().activate_commands("Applied preferences")

        self._settings_applied = True

        msg = "PREFERENCES DIALOG: Handling Apply button click complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def cancel_button_clicked(self, _widget: Gtk.Button) -> None:
        """Handle Cancel button click to close window without saving."""

        msg = "PREFERENCES DIALOG: Cancel button clicked"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        for grid in self._page_to_grid.values():
            grid.revert_changes()
        self.destroy()

        msg = "PREFERENCES DIALOG: Handling Cancel button click complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def ok_button_clicked(self, widget: Gtk.Button | None = None) -> None:
        """Handle OK button click to save preferences and close window."""

        msg = "PREFERENCES DIALOG: OK button clicked"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        self.apply_button_clicked(widget)  # type: ignore[arg-type]
        self.destroy()

        msg = "PREFERENCES DIALOG: Handling OK button click complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def _on_save_profile_as(self) -> None:
        """Handle Save Profile As menu item."""

        new_profile = self.profiles_grid.get_new_profile_name()
        if new_profile is None:
            return

        # Set the new profile and save using existing methods
        self.prefs_dict["profile"] = new_profile
        self.prefs_dict["activeProfile"] = new_profile
        self.apply_button_clicked(None)
        self._on_profile_loaded(new_profile)

    def window_closed(self, _widget: Gtk.Widget, _event: Any) -> bool:
        """Handle window close signal by suspending events temporarily."""

        msg = "PREFERENCES DIALOG: Window is being closed"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        has_unsaved_changes = not self._settings_applied and (
            self.speech_grid.has_changes()
            or self.braille_grid.has_changes()
            or self.sound_grid.has_changes()
            or self.typing_echo_grid.has_changes()
            or self.say_all_grid.has_changes()
            or self.spellcheck_grid.has_changes()
            or self.chat_grid.has_changes()
            or self.mouse_grid.has_changes()
            or self.document_grid.has_changes()
            or self.time_and_date_grid.has_changes()
            or self.text_attributes_grid.has_changes()
            or (not self._app_name and self.profiles_grid.has_changes())
            or self.pronunciation_grid.has_changes()
            or self.keybindings_grid.has_changes()
        )

        # Check if profile was switched during this session
        current_profile = profile_manager.get_manager().get_active_profile()
        profile_was_switched = current_profile != self._original_profile

        if has_unsaved_changes:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text=guilabels.PREFERENCES_CLOSE_WITHOUT_SAVE,
            )
            dialog.format_secondary_text(guilabels.PREFERENCES_CHANGES_WILL_BE_LOST)

            profile_label = self._get_current_profile_label()
            save_button = dialog.add_button(
                guilabels.MENU_SAVE_PROFILE % profile_label, Gtk.ResponseType.YES
            )
            save_button.get_style_context().add_class("suggested-action")

            # Only show "New Profile" for global preferences (profiles are global)
            if not self._app_name:
                dialog.add_button(guilabels.PROFILE_CREATE_NEW, Gtk.ResponseType.APPLY)

            dialog.add_button(guilabels.BTN_CLOSE_WITHOUT_SAVING, Gtk.ResponseType.NO)
            dialog.add_button(guilabels.DIALOG_CANCEL, Gtk.ResponseType.CANCEL)

            dialog.show_all()
            dialog.present()
            save_button.grab_focus()
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                self.apply_button_clicked(None)
            elif response == Gtk.ResponseType.APPLY:
                self._on_save_profile_as()
            elif response in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
                return True
            else:
                for grid in self._page_to_grid.values():
                    grid.revert_changes()

        elif profile_was_switched:
            # Profile was switched but no other changes - show simple dialog
            current_label = self._get_current_profile_label()
            original_label = self.profiles_grid.get_profile_label(self._original_profile)
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text=guilabels.PREFERENCES_PROFILE_SWITCHED,
            )

            use_button = dialog.add_button(
                guilabels.PROFILE_USE % current_label, Gtk.ResponseType.YES
            )
            use_button.get_style_context().add_class("suggested-action")
            dialog.add_button(
                guilabels.PROFILE_SWITCH_BACK_TO % original_label, Gtk.ResponseType.NO
            )

            dialog.show_all()
            dialog.present()
            use_button.grab_focus()
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.NO:
                profile_manager.get_manager().load_profile(self._original_profile)

        self.suspend_events()
        GObject.timeout_add(1000, self.resume_events)

        msg = "PREFERENCES DIALOG: Window closure complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        return False

    def window_destroyed(self, _widget: Gtk.Widget) -> None:
        """Handle window destroyed signal by clearing window reference."""

        msg = "PREFERENCES WINDOW: Window is being destroyed"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        OrcaSetupGUI.WINDOW = None

        msg = "PREFERENCES WINDOW: Window destruction complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        settings_manager.get_manager().set_configuring(False)

    def _has_unsaved_changes_in_grids(self) -> bool:
        """Check if any preference grid (except profiles) has unsaved changes."""

        return (
            self.speech_grid.has_changes()
            or self.braille_grid.has_changes()
            or self.sound_grid.has_changes()
            or self.typing_echo_grid.has_changes()
            or self.say_all_grid.has_changes()
            or self.spellcheck_grid.has_changes()
            or self.chat_grid.has_changes()
            or self.mouse_grid.has_changes()
            or self.document_grid.has_changes()
            or self.time_and_date_grid.has_changes()
            or self.text_attributes_grid.has_changes()
            or self.pronunciation_grid.has_changes()
            or self.keybindings_grid.has_changes()
        )

    def resume_events(self) -> bool:
        """Re-register event listeners after window closure."""

        msg = "PREFERENCES DIALOG: Re-registering floody events."
        debug.print_message(debug.LEVEL_ALL, msg, True)

        manager = event_manager.get_manager()
        manager.register_listener("object:state-changed:showing")
        manager.register_listener("object:children-changed:remove")
        manager.register_listener("object:selection-changed")
        manager.register_listener("object:property-change:accessible-name")
        return False

    def suspend_events(self) -> None:
        """Deregister event listeners to prevent interference during closure."""

        msg = "PREFERENCES DIALOG: Deregistering floody events."
        debug.print_message(debug.LEVEL_ALL, msg, True)

        manager = event_manager.get_manager()
        manager.deregister_listener("object:state-changed:showing")
        manager.deregister_listener("object:children-changed:remove")
        manager.deregister_listener("object:selection-changed")
        manager.deregister_listener("object:property-change:accessible-name")

    def _get_current_profile_label(self) -> str:
        """Get the display label for the current profile, including pending renames."""

        return self.profiles_grid.get_current_profile_label()

    def _get_panel_title(self, page_title: str) -> str:
        """Build the panel header title with profile in parentheses."""

        profile_label = self._get_current_profile_label()
        return f"{page_title} ({profile_label})"

    def _set_page_title(self, title: str) -> None:
        """Set the current page title, updating panel header and accessible name."""

        self._current_page_title = title
        self.panel_headerbar.set_title(self._get_panel_title(title))
        self.get_accessible().set_name(self._get_accessible_name(title))

    def _get_accessible_name(self, page_title: str = "") -> str:
        """Build the accessible name for the window."""

        if self._app_name:
            base_title = guilabels.PREFERENCES_APPLICATION_TITLE % self._app_name
        else:
            base_title = guilabels.DIALOG_SCREEN_READER_PREFERENCES_ACCESSIBLE

        profile_label = self._get_current_profile_label()

        if page_title:
            return f"{base_title}, {page_title}, {profile_label}"
        return f"{base_title}, {profile_label}"

    def update_menu_labels(self) -> None:
        """Update Apply and Save menu items and panel title to show the current profile."""

        profile_label = self._get_current_profile_label()
        self.apply_item.set_property("text", guilabels.MENU_APPLY_PROFILE % profile_label)
        self.save_item.set_property("text", guilabels.MENU_SAVE_PROFILE % profile_label)

        if self._app_name:
            self.left_headerbar.set_subtitle(self._app_name)
        else:
            self.left_headerbar.set_subtitle(None)

        if self._current_page_title:
            self._set_page_title(self._current_page_title)

    def _on_profile_loaded(self, profile: list[str]) -> None:
        """Handle profile loaded callback and reload all preference grids."""

        if not self.get_realized():
            return

        self.prefs_dict = settings_manager.get_manager().get_general_settings(profile[1])
        self._init_gui_state(include_profiles=False)
        self.update_menu_labels()
