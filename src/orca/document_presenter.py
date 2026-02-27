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

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments, too-many-positional-arguments

"""Module for document-related presentation and navigation settings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi, Gtk

from . import (
    caret_navigator,
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    input_event_manager,
    keybindings,
    live_region_presenter,
    messages,
    preferences_grid_base,
    presentation_manager,
    script_manager,
    structural_navigator,
    table_navigator,
)
from .ax_component import AXComponent
from .ax_document import AXDocument
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from collections.abc import Callable

    from .scripts import default


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.FindResultsVerbosity",
    values={"none": 0, "if-line-changed": 1, "all": 2},
)
class FindResultsVerbosity(Enum):
    """Find results verbosity level enumeration."""

    NONE = 0
    IF_LINE_CHANGED = 1
    ALL = 2

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower().replace("_", "-")


@dataclass
class _AppModeState:
    """Tracks focus/browse mode state for a specific application."""

    in_focus_mode: bool = True
    focus_mode_is_sticky: bool = False
    browse_mode_is_sticky: bool = False
    user_has_toggled: bool = False


class CaretNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for caret navigation settings within the Documents page."""

    _gsettings_schema = "caret-navigation"

    def __init__(self) -> None:
        nav = caret_navigator.get_navigator()

        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return nav.get_is_enabled()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_CARET_NAVIGATION,
                getter=nav.get_is_enabled,
                setter=nav.set_is_enabled,
                prefs_key="enabled",
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=nav.get_triggers_focus_mode,
                setter=nav.set_triggers_focus_mode,
                prefs_key="triggers-focus-mode",
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CONTENT_LAYOUT_MODE,
                getter=nav.get_layout_mode,
                setter=nav.set_layout_mode,
                prefs_key="layout-mode",
                determine_sensitivity=is_enabled,
            ),
        ]
        info = (
            f"{guilabels.CARET_NAVIGATION_INFO}\n\n{guilabels.AUTOMATIC_FOCUS_MODE_INFO}"
            f"\n\n{guilabels.LAYOUT_MODE_INFO}"
        )
        super().__init__(guilabels.KB_GROUP_CARET_NAVIGATION, controls, info_message=info)

        self._enabled_switch = self._widgets[0]


class StructuralNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for structural navigation settings within the Documents page."""

    _gsettings_schema = "structural-navigation"

    def __init__(self) -> None:
        nav = structural_navigator.get_navigator()

        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return nav.get_is_enabled()

        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
                getter=nav.get_is_enabled,
                setter=nav.set_is_enabled,
                prefs_key="enabled",
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=nav.get_triggers_focus_mode,
                setter=nav.set_triggers_focus_mode,
                prefs_key="triggers-focus-mode",
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_WRAP_AROUND,
                getter=nav.get_navigation_wraps,
                setter=nav.set_navigation_wraps,
                prefs_key="wraps",
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_LARGE_OBJECT_LENGTH,
                minimum=1,
                maximum=500,
                getter=nav.get_large_object_text_length,
                setter=nav.set_large_object_text_length,
                prefs_key="large-object-text-length",
                determine_sensitivity=is_enabled,
            ),
        ]
        info = (
            f"{guilabels.STRUCTURAL_NAVIGATION_INFO}\n\n{guilabels.AUTOMATIC_FOCUS_MODE_INFO}"
            f"\n\n{guilabels.LARGE_OBJECT_INFO}"
        )
        super().__init__(guilabels.KB_GROUP_STRUCTURAL_NAVIGATION, controls, info_message=info)

        self._enabled_switch = self._widgets[0]


class TableNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for table navigation settings within the Documents page."""

    _gsettings_schema = "table-navigation"

    def __init__(self) -> None:
        nav = table_navigator.get_navigator()

        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return nav.get_is_enabled()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_TABLE_NAVIGATION,
                getter=nav.get_is_enabled,
                setter=nav.set_is_enabled,
                prefs_key="enabled",
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.TABLE_SKIP_BLANK_CELLS,
                getter=nav.get_skip_blank_cells,
                setter=nav.set_skip_blank_cells,
                prefs_key="skip-blank-cells",
                determine_sensitivity=is_enabled,
            ),
        ]
        super().__init__(guilabels.KB_GROUP_TABLE_NAVIGATION, controls)

        self._enabled_switch = self._widgets[0]


class NativeNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for native navigation settings within the Documents page."""

    _gsettings_schema = "document"

    def __init__(self, presenter: DocumentPresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=presenter.get_native_nav_triggers_focus_mode,
                setter=presenter.set_native_nav_triggers_focus_mode,
                prefs_key="native-nav-triggers-focus-mode",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTO_STICKY_FOCUS_MODE,
                getter=presenter.get_auto_sticky_focus_mode_for_web_apps,
                setter=presenter.set_auto_sticky_focus_mode_for_web_apps,
                prefs_key="auto-sticky-focus-mode",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.FIND_SPEAK_RESULTS,
                getter=presenter.get_speak_find_results,
                setter=presenter.set_speak_find_results,
                prefs_key="find-results-verbosity",
                member_of=guilabels.FIND_OPTIONS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.FIND_ONLY_SPEAK_CHANGED_LINES,
                getter=presenter.get_only_speak_changed_lines,
                setter=presenter.set_only_speak_changed_lines,
                prefs_key="find-results-verbosity",
                determine_sensitivity=presenter.get_speak_find_results,
                member_of=guilabels.FIND_OPTIONS,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.FIND_MINIMUM_MATCH_LENGTH,
                minimum=0,
                maximum=20,
                getter=presenter.get_find_results_minimum_length,
                setter=presenter.set_find_results_minimum_length,
                prefs_key="find-results-minimum-length",
                member_of=guilabels.FIND_OPTIONS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.READ_PAGE_UPON_LOAD,
                getter=presenter.get_say_all_on_load,
                setter=presenter.set_say_all_on_load,
                prefs_key="say-all-on-load",
                member_of=guilabels.PAGE_LOAD,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.PAGE_SUMMARY_UPON_LOAD,
                getter=presenter.get_page_summary_on_load,
                setter=presenter.set_page_summary_on_load,
                prefs_key="page-summary-on-load",
                member_of=guilabels.PAGE_LOAD,
            ),
        ]
        info = (
            f"{guilabels.NATIVE_NAVIGATION_INFO}\n\n"
            f"{guilabels.AUTOMATIC_FOCUS_MODE_INFO}\n\n"
            f"{guilabels.AUTO_STICKY_FOCUS_MODE_INFO}"
        )
        super().__init__(guilabels.NATIVE_NAVIGATION, controls, info_message=info)


class DocumentPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Main document preferences grid with categorized navigation settings."""

    def __init__(
        self,
        presenter: DocumentPresenter,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(guilabels.DOCUMENTS)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._caret_grid = CaretNavigationPreferencesGrid()
        self._structural_grid = StructuralNavigationPreferencesGrid()
        self._table_grid = TableNavigationPreferencesGrid()
        self._native_grid = NativeNavigationPreferencesGrid(presenter)

        self._build()
        self._initializing = False

    def _build(self) -> None:
        categories = [
            (guilabels.KB_GROUP_CARET_NAVIGATION, "caret", self._caret_grid),
            (guilabels.KB_GROUP_STRUCTURAL_NAVIGATION, "structural", self._structural_grid),
            (guilabels.KB_GROUP_TABLE_NAVIGATION, "table", self._table_grid),
            (guilabels.NATIVE_NAVIGATION, "native", self._native_grid),
        ]

        _enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=None,
            enable_getter=None,
            enable_setter=None,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.DOCUMENTS,
        )

        self.attach(stack, 0, 0, 1, 1)

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self.multipage_on_becoming_visible()

    def reload(self) -> None:
        """Reload all child grids."""

        self._initializing = True
        self._has_unsaved_changes = False
        self._caret_grid.reload()
        self._structural_grid.reload()
        self._table_grid.reload()
        self._native_grid.reload()
        self._initializing = False

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Save all settings from child grids."""

        result = {}
        result.update(self._caret_grid.save_settings(profile, app_name))
        result.update(self._structural_grid.save_settings(profile, app_name))
        result.update(self._table_grid.save_settings(profile, app_name))
        result.update(self._native_grid.save_settings(profile, app_name))

        return result

    def has_changes(self) -> bool:
        """Check if any child grid has changes."""

        return (
            self._has_unsaved_changes
            or self._caret_grid.has_changes()
            or self._structural_grid.has_changes()
            or self._table_grid.has_changes()
            or self._native_grid.has_changes()
        )

    def refresh(self) -> None:
        """Refresh all child grids."""

        self._initializing = True
        self._caret_grid.refresh()
        self._structural_grid.refresh()
        self._table_grid.refresh()
        self._native_grid.refresh()
        self._initializing = False


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Document", name="document")
class DocumentPresenter:
    """Manages document-related presentation and navigation settings."""

    _SCHEMA = "document"

    def _get_setting(self, key: str, gtype: str, default: Any) -> Any:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            gtype,
            default=default,
        )

    def __init__(self) -> None:
        self._made_find_announcement = False
        self._app_states: dict[int, _AppModeState] = {}
        self._initialized: bool = False

        msg = "DOCUMENT PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("DocumentPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_DOCUMENTS

        # Keybindings (same for desktop and laptop)
        kb_a = keybindings.KeyBinding("a", keybindings.ORCA_MODIFIER_MASK)
        kb_a_2 = keybindings.KeyBinding("a", keybindings.ORCA_MODIFIER_MASK, click_count=2)
        kb_a_3 = keybindings.KeyBinding("a", keybindings.ORCA_MODIFIER_MASK, click_count=3)

        # (name, function, description, keybinding)
        commands_data = [
            (
                "toggle_presentation_mode",
                self.toggle_presentation_mode,
                cmdnames.TOGGLE_PRESENTATION_MODE,
                kb_a,
            ),
            (
                "enable_sticky_focus_mode",
                self.enable_sticky_focus_mode,
                cmdnames.SET_FOCUS_MODE_STICKY,
                kb_a_2,
            ),
            (
                "enable_sticky_browse_mode",
                self.enable_sticky_browse_mode,
                cmdnames.SET_BROWSE_MODE_STICKY,
                kb_a_3,
            ),
        ]

        for name, function, description, kb in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=kb,
                    laptop_keybinding=kb,
                ),
            )

        msg = "DOCUMENT PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _get_state_for_app(self, app: Atspi.Accessible | None) -> _AppModeState:
        """Returns the mode state for the given app, creating if needed."""

        if app is None:
            return _AppModeState()

        app_hash = hash(app)
        if app_hash not in self._app_states:
            self._app_states[app_hash] = _AppModeState()
        return self._app_states[app_hash]

    def _get_current_app(self) -> Atspi.Accessible | None:
        """Returns the current application from the active script."""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return None
        return script.app

    def _is_likely_electron_app(self, app: Atspi.Accessible | None) -> bool:
        """Returns True if app is likely an Electron app (Chromium-based, not a browser)."""

        if app is None:
            return False

        toolkit = AXObject.get_toolkit_name(app).lower()
        if toolkit != "chromium":
            return False

        app_name = AXObject.get_name(app).lower()
        known_browsers = ("brave", "chromium", "edge", "chrome", "opera", "vivaldi")
        result = not any(browser in app_name for browser in known_browsers)
        tokens = ["DOCUMENT PRESENTER:", app, "is likely Electron app:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _is_top_level_web_app(self, script: default.Script, obj: Atspi.Accessible | None) -> bool:
        """Returns True if obj is in a top-level web application (e.g., Google Docs)."""

        if obj is None:
            return False

        document = script.utilities.active_document()
        if document is None:
            return False

        if not AXUtilities.is_embedded(document):
            return False

        uri = AXDocument.get_uri(document)
        result = bool(uri and uri.startswith("http"))
        tokens = ["DOCUMENT PRESENTER:", document, f"is top-level web app: {result}. URI: {uri}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def in_focus_mode(self, app: Atspi.Accessible | None = None) -> bool:
        """Returns True if focus mode is active for the given app."""

        if app is None:
            app = self._get_current_app()
        if app is None:
            return False
        app_hash = hash(app)
        if app_hash not in self._app_states:
            return False
        return self._app_states[app_hash].in_focus_mode

    def focus_mode_is_sticky(self, app: Atspi.Accessible | None = None) -> bool:
        """Returns True if focus mode is sticky for the given app."""

        if app is None:
            app = self._get_current_app()
        if app is None:
            return False
        app_hash = hash(app)
        if app_hash not in self._app_states:
            return False
        return self._app_states[app_hash].focus_mode_is_sticky

    def browse_mode_is_sticky(self, app: Atspi.Accessible | None = None) -> bool:
        """Returns True if browse mode is sticky for the given app."""

        if app is None:
            app = self._get_current_app()
        if app is None:
            return False
        app_hash = hash(app)
        if app_hash not in self._app_states:
            return False
        return self._app_states[app_hash].browse_mode_is_sticky

    def _set_presentation_mode(
        self,
        script: default.Script,
        use_focus_mode: bool,
        obj: Atspi.Accessible | None = None,
        document: Atspi.Accessible | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Sets the presentation mode to focus or browse mode."""

        tokens = [
            f"DOCUMENT PRESENTER: set_presentation_mode. Use focus mode: {use_focus_mode},",
            obj,
            "in",
            document,
            f"notify user: {notify_user}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if obj is not None and AXObject.is_dead(obj):
            obj = None

        if not script.utilities.in_document_content(obj):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.DOCUMENT_NOT_IN_A)
            return False

        has_state = self.has_state_for_app(script.app)
        in_focus_mode = self.in_focus_mode(script.app)
        if has_state and in_focus_mode == use_focus_mode:
            msg = "DOCUMENT PRESENTER: Presentation mode already set."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        obj, _offset = script.utilities.get_caret_context(document)

        if in_focus_mode and not use_focus_mode:
            parent = AXObject.get_parent(obj)
            if AXUtilities.is_list_box(parent):
                script.utilities.set_caret_context(parent, -1)
            elif AXUtilities.is_menu(parent):
                script.utilities.set_caret_context(AXObject.get_parent(parent), -1)

        if not in_focus_mode and use_focus_mode:
            if (
                caret_navigator.get_navigator().last_input_event_was_navigation_command()
                or structural_navigator.get_navigator().last_input_event_was_navigation_command()
                or table_navigator.get_navigator().last_input_event_was_navigation_command()
            ):
                AXObject.grab_focus(obj)

        if notify_user:
            msg = messages.MODE_FOCUS if use_focus_mode else messages.MODE_BROWSE
            presentation_manager.get_manager().present_message(msg)

        state = self._get_state_for_app(script.app)
        state.in_focus_mode = use_focus_mode
        state.focus_mode_is_sticky = False
        state.browse_mode_is_sticky = False

        reason = "setting presentation mode"
        if not use_focus_mode:
            self._enable_document_navigators(script, reason)

        self.suspend_navigators(script, use_focus_mode, reason)
        return True

    def suspend_navigators(self, script: default.Script, suspended: bool, reason: str) -> bool:
        """Suspends or unsuspends navigation commands. Returns True if state changed."""

        caret_navigator.get_navigator().suspend_commands(script, suspended, reason)
        structural_navigator.get_navigator().suspend_commands(script, suspended, reason)
        live_region_presenter.get_presenter().suspend_commands(script, suspended, reason)
        table_navigator.get_navigator().suspend_commands(script, suspended, reason)
        return True

    def _enable_document_navigators(self, script: default.Script, reason: str) -> None:
        """Enables document navigators for the given script."""

        msg = f"DOCUMENT PRESENTER: _enable_document_navigators. Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        structural_navigator.get_navigator().set_mode(
            script,
            structural_navigator.NavigationMode.DOCUMENT,
        )
        caret_navigator.get_navigator().set_enabled_for_script(script, True)

    def _is_focus_mode_widget_by_state(self, obj: Atspi.Accessible) -> tuple[bool, str]:
        """Returns (True, reason) if obj's state makes it a focus mode widget."""

        if AXUtilities.is_editable(obj):
            return True, "it's editable"

        if (
            AXUtilities.is_expandable(obj)
            and AXUtilities.is_focusable(obj)
            and not AXUtilities.is_link(obj)
        ):
            return True, "it's expandable and focusable"

        return False, ""

    def _is_focus_mode_widget_by_role(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> tuple[bool | None, str]:
        """Returns (True/False, reason) if role determines focus mode, or (None, '') if unclear."""

        always_focus_mode_roles = [
            Atspi.Role.COMBO_BOX,
            Atspi.Role.ENTRY,
            Atspi.Role.LIST_BOX,
            Atspi.Role.MENU,
            Atspi.Role.MENU_ITEM,
            Atspi.Role.CHECK_MENU_ITEM,
            Atspi.Role.RADIO_MENU_ITEM,
            Atspi.Role.PAGE_TAB,
            Atspi.Role.PASSWORD_TEXT,
            Atspi.Role.PROGRESS_BAR,
            Atspi.Role.SLIDER,
            Atspi.Role.SPIN_BUTTON,
            Atspi.Role.TOOL_BAR,
            Atspi.Role.TREE_ITEM,
            Atspi.Role.TREE_TABLE,
            Atspi.Role.TREE,
        ]

        role = AXObject.get_role(obj)
        if role in always_focus_mode_roles:
            return True, "due to its role"

        if role in [Atspi.Role.TABLE_CELL, Atspi.Role.TABLE] and AXUtilities.is_layout_table(
            AXUtilities.get_table(obj),
        ):
            return False, "it's layout only"

        if AXUtilities.is_list_box_item(obj, role):
            return True, "it's a listbox item"

        if AXUtilities.is_button_with_popup(obj, role):
            return True, "it's a button with popup"

        focus_mode_roles = [Atspi.Role.EMBEDDED, Atspi.Role.TABLE_CELL, Atspi.Role.TABLE]
        if (
            role in focus_mode_roles
            and not script.utilities.is_text_block_element(obj)
            and not script.utilities.has_name_and_action_and_no_useful_children(obj)
            and not AXDocument.is_pdf(script.utilities.get_document_for_object(obj))
        ):
            return True, "based on presumed functionality"

        return None, ""

    def _is_focus_mode_widget_by_ancestry(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> tuple[bool, str]:
        """Returns (True, reason) if obj's ancestry makes it a focus mode widget."""

        ancestor_checks: list[tuple[Callable[[Atspi.Accessible], bool], str]] = [
            (AXUtilities.is_grid, "it's a grid descendant"),
            (AXUtilities.is_menu, "it's a menu descendant"),
            (AXUtilities.is_tool_bar, "it's a toolbar descendant"),
        ]
        for predicate, reason in ancestor_checks:
            if AXObject.find_ancestor(obj, predicate) is not None:
                return True, reason

        if script.utilities.is_content_editable_with_embedded_objects(obj):
            return True, "it's content editable"

        return False, ""

    def is_focus_mode_widget(self, script: default.Script, obj: Atspi.Accessible) -> bool:
        """Returns True if obj should be interacted with in focus mode."""

        result, reason = self._is_focus_mode_widget_by_state(obj)
        if not result:
            role_result, reason = self._is_focus_mode_widget_by_role(script, obj)
            if role_result is None:
                result, reason = self._is_focus_mode_widget_by_ancestry(script, obj)
            else:
                result = role_result

        prefix = "is" if result else "is not"
        if reason:
            tokens = ["DOCUMENT PRESENTER:", obj, f"{prefix} focus mode widget:", reason]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    @dbus_service.command
    def enable_sticky_browse_mode(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Enables sticky browse mode."""

        msg = f"DOCUMENT PRESENTER: enable_sticky_browse_mode({event}, {notify_user})"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not script.utilities.in_document_content():
            if notify_user:
                presentation_manager.get_manager().present_message(messages.DOCUMENT_NOT_IN_A)
            return True

        state = self._get_state_for_app(script.app)

        if not state.browse_mode_is_sticky or notify_user:
            presentation_manager.get_manager().present_message(messages.MODE_BROWSE_IS_STICKY)

        state.in_focus_mode = False
        state.focus_mode_is_sticky = False
        state.browse_mode_is_sticky = True
        state.user_has_toggled = True

        reason = "enable sticky browse mode"
        self.suspend_navigators(script, state.in_focus_mode, reason)
        return True

    @dbus_service.command
    def enable_sticky_focus_mode(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Enables sticky focus mode."""

        msg = f"DOCUMENT PRESENTER: enable_sticky_focus_mode({event}, {notify_user})"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not script.utilities.in_document_content():
            if notify_user:
                presentation_manager.get_manager().present_message(messages.DOCUMENT_NOT_IN_A)
            return True

        state = self._get_state_for_app(script.app)

        if not state.focus_mode_is_sticky or notify_user:
            presentation_manager.get_manager().present_message(messages.MODE_FOCUS_IS_STICKY)

        state.in_focus_mode = True
        state.focus_mode_is_sticky = True
        state.browse_mode_is_sticky = False
        state.user_has_toggled = True

        reason = "enable sticky focus mode"
        self.suspend_navigators(script, state.in_focus_mode, reason)
        return True

    @dbus_service.command
    def toggle_presentation_mode(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        document: Atspi.Accessible | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Switches between browse mode and focus mode (user-initiated)."""

        if not script.utilities.in_document_content():
            if notify_user:
                presentation_manager.get_manager().present_message(messages.DOCUMENT_NOT_IN_A)
            return True

        use_focus = not self.in_focus_mode(script.app)
        obj, _offset = script.utilities.get_caret_context(document)
        if event is not None and use_focus:
            AXObject.grab_focus(obj)

        self._set_presentation_mode(
            script,
            use_focus,
            obj=obj,
            document=document,
            notify_user=notify_user,
        )
        self._get_state_for_app(script.app).user_has_toggled = True
        return True

    @dbus_service.getter
    def get_in_focus_mode(self) -> bool:
        """Returns True if focus mode is active (web content only)."""

        if script := script_manager.get_manager().get_active_script():
            return self.in_focus_mode(script.app)
        return False

    @dbus_service.getter
    def get_focus_mode_is_sticky(self) -> bool:
        """Returns True if focus mode is active and 'sticky' (web content only)."""

        if script := script_manager.get_manager().get_active_script():
            return self.focus_mode_is_sticky(script.app)
        return False

    @dbus_service.getter
    def get_browse_mode_is_sticky(self) -> bool:
        """Returns True if browse mode is active and 'sticky' (web content only)."""

        if script := script_manager.get_manager().get_active_script():
            return self.browse_mode_is_sticky(script.app)
        return False

    def restore_mode_for_script(self, script: default.Script) -> None:
        """Restores navigator suspension state when a script is activated."""

        if script.app is None:
            return

        app_hash = hash(script.app)
        if app_hash not in self._app_states:
            return

        state = self._app_states[app_hash]

        # When restoring browse mode, also re-enable the navigators.
        # This is needed because another script (e.g. file browser) may have
        # disabled them via set_mode(OFF) while it was active.
        reason = "restoring mode state for activated script"
        if not state.in_focus_mode:
            self._enable_document_navigators(script, reason)

        self.suspend_navigators(script, state.in_focus_mode, reason)

        tokens = [
            "DOCUMENT PRESENTER: Restored mode for",
            script.app,
            ". Focus mode:",
            state.in_focus_mode,
            "Focus sticky:",
            state.focus_mode_is_sticky,
            "Browse sticky:",
            state.browse_mode_is_sticky,
            "User toggled:",
            state.user_has_toggled,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def has_state_for_app(self, app: Atspi.Accessible | None) -> bool:
        """Returns True if mode state exists for the given app."""

        if app is None:
            return False
        return hash(app) in self._app_states

    def clear_state_for_app(self, app: Atspi.Accessible | None) -> None:
        """Clears mode state when an app is closed."""

        if app is None:
            return
        app_hash = hash(app)
        if app_hash in self._app_states:
            del self._app_states[app_hash]
            tokens = ["DOCUMENT PRESENTER: Cleared state for", app]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def _handle_entering_document(
        self,
        script: default.Script,
        new_focus: Atspi.Accessible,
        old_focus: Atspi.Accessible | None,
    ) -> bool:
        """Handles mode/navigator setup when entering a document from outside."""

        if self.focus_mode_is_sticky(script.app):
            presentation_manager.get_manager().present_message(messages.MODE_FOCUS_IS_STICKY)
            reason = "locus of focus now in document, focus mode is sticky"
            self.suspend_navigators(script, True, reason)
            return True

        if self.browse_mode_is_sticky(script.app):
            presentation_manager.get_manager().present_message(messages.MODE_BROWSE_IS_STICKY)
            reason = "locus of focus now in document, browse mode is sticky"
            self._enable_document_navigators(script, reason)
            self.suspend_navigators(script, False, reason)
            return True

        # Only do app-type detection if setting is enabled and user hasn't explicitly
        # toggled mode. This allows the user to escape auto-enabled sticky focus mode.
        if (
            self.get_auto_sticky_focus_mode_for_web_apps()
            and not self._get_state_for_app(script.app).user_has_toggled
        ):
            if self._is_likely_electron_app(script.app):
                msg = "DOCUMENT PRESENTER: Electron app detected, enabling sticky focus mode"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.enable_sticky_focus_mode(script, notify_user=True)
                return True

            if self._is_top_level_web_app(script, new_focus):
                msg = "DOCUMENT PRESENTER: Top-level web app detected, enabling sticky focus mode"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.enable_sticky_focus_mode(script, notify_user=True)
                return True

        use_focus = self.use_focus_mode(new_focus, old_focus)
        reason = "entering document"
        if not use_focus:
            self._enable_document_navigators(script, reason)

        state = self._get_state_for_app(script.app)
        state.in_focus_mode = use_focus
        self.suspend_navigators(script, use_focus, reason)

        if use_focus:
            presentation_manager.get_manager().present_message(messages.MODE_FOCUS)
        else:
            presentation_manager.get_manager().present_message(messages.MODE_BROWSE)

        return True

    def update_mode_if_needed(
        self,
        script: default.Script,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None,
    ) -> bool:
        """Updates focus/browse mode based on a focus change. Returns True if handled."""

        old_doc = script.utilities.get_top_level_document_for_object(old_focus)
        new_doc = script.utilities.get_top_level_document_for_object(new_focus)

        tokens = [
            "DOCUMENT PRESENTER: Updating mode for focus change.",
            "Old focus:",
            old_focus,
            "old doc:",
            old_doc,
            "New focus:",
            new_focus,
            "new doc:",
            new_doc,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if new_doc is None:
            self.reset_find_announcement_state()
            reason = "locus of focus no longer in document"
            self.suspend_navigators(script, False, reason)
            structural_navigator.get_navigator().set_mode(
                script,
                structural_navigator.NavigationMode.OFF,
            )
            caret_navigator.get_navigator().set_enabled_for_script(script, False)
            return True

        if old_doc is None:
            return self._handle_entering_document(script, new_focus, old_focus)

        # Focus change within document
        if self.focus_mode_is_sticky(script.app) or self.browse_mode_is_sticky(script.app):
            return False

        use_focus = self.use_focus_mode(new_focus, old_focus)
        self._set_presentation_mode(script, use_focus, obj=new_focus, document=new_doc)
        return True

    def reset_find_announcement_state(self) -> None:
        """Resets the find announcement state."""

        self._made_find_announcement = False

    @gsettings_registry.get_registry().gsetting(
        key="native-nav-triggers-focus-mode",
        schema="document",
        gtype="b",
        default=True,
        summary="Native navigation triggers focus mode",
        migration_key="nativeNavTriggersFocusMode",
    )
    @dbus_service.getter
    def get_native_nav_triggers_focus_mode(self) -> bool:
        """Returns whether native navigation triggers focus mode."""

        return self._get_setting("native-nav-triggers-focus-mode", "b", True)

    @dbus_service.setter
    def set_native_nav_triggers_focus_mode(self, value: bool) -> bool:
        """Sets whether native navigation triggers focus mode."""

        if self.get_native_nav_triggers_focus_mode() == value:
            return True

        msg = f"DOCUMENT PRESENTER: Setting native nav triggers focus mode to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "native-nav-triggers-focus-mode",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="auto-sticky-focus-mode",
        schema="document",
        gtype="b",
        default=True,
        summary="Auto-detect sticky focus mode for web apps",
        migration_key="autoStickyFocusModeForWebApps",
    )
    @dbus_service.getter
    def get_auto_sticky_focus_mode_for_web_apps(self) -> bool:
        """Returns whether to auto-detect web apps and enable sticky focus mode."""

        return self._get_setting("auto-sticky-focus-mode", "b", True)

    @dbus_service.setter
    def set_auto_sticky_focus_mode_for_web_apps(self, value: bool) -> bool:
        """Sets whether to auto-detect web apps and enable sticky focus mode."""

        if self.get_auto_sticky_focus_mode_for_web_apps() == value:
            return True

        msg = f"DOCUMENT PRESENTER: Setting auto sticky focus mode for web apps to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "auto-sticky-focus-mode",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="say-all-on-load",
        schema="document",
        gtype="b",
        default=True,
        summary="Perform say all when document loads",
        migration_key="sayAllOnLoad",
    )
    @dbus_service.getter
    def get_say_all_on_load(self) -> bool:
        """Returns whether to perform say all when a document loads."""

        return self._get_setting("say-all-on-load", "b", True)

    @dbus_service.setter
    def set_say_all_on_load(self, value: bool) -> bool:
        """Sets whether to perform say all when a document loads."""

        if self.get_say_all_on_load() == value:
            return True

        msg = f"DOCUMENT PRESENTER: Setting say all on load to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "say-all-on-load", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="page-summary-on-load",
        schema="document",
        gtype="b",
        default=True,
        summary="Present page summary when document loads",
        migration_key="pageSummaryOnLoad",
    )
    @dbus_service.getter
    def get_page_summary_on_load(self) -> bool:
        """Returns whether to present a page summary when a document loads."""

        return self._get_setting("page-summary-on-load", "b", True)

    @dbus_service.setter
    def set_page_summary_on_load(self, value: bool) -> bool:
        """Sets whether to present a page summary when a document loads."""

        if self.get_page_summary_on_load() == value:
            return True

        msg = f"DOCUMENT PRESENTER: Setting page summary on load to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "page-summary-on-load",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="find-results-verbosity",
        schema="document",
        genum="org.gnome.Orca.FindResultsVerbosity",
        default="all",
        summary="Find results verbosity (none, if-line-changed, all)",
        migration_key="findResultsVerbosity",
    )
    def _get_find_results_verbosity_name(self) -> str:
        """Returns the find results verbosity level as a string name."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "find-results-verbosity",
            "",
            genum="org.gnome.Orca.FindResultsVerbosity",
            default="all",
        )

    @dbus_service.getter
    def get_speak_find_results(self) -> bool:
        """Returns whether to speak find results."""

        return self._get_find_results_verbosity_name() != "none"

    @dbus_service.setter
    def set_speak_find_results(self, value: bool) -> bool:
        """Sets whether to speak find results."""

        if self.get_speak_find_results() == value:
            return True

        msg = f"DOCUMENT PRESENTER: Setting speak find results to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        name = "all" if value else "none"
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "find-results-verbosity",
            name,
        )
        return True

    @dbus_service.getter
    def get_only_speak_changed_lines(self) -> bool:
        """Returns whether to only speak changed lines during find."""

        return self._get_find_results_verbosity_name() == "if-line-changed"

    @dbus_service.setter
    def set_only_speak_changed_lines(self, value: bool) -> bool:
        """Sets whether to only speak changed lines during find."""

        if self.get_only_speak_changed_lines() == value:
            return True

        msg = f"DOCUMENT PRESENTER: Setting only speak changed lines to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        name = "if-line-changed" if value else "all"
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "find-results-verbosity",
            name,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="find-results-minimum-length",
        schema="document",
        gtype="i",
        default=4,
        summary="Minimum length for find results to be spoken",
        migration_key="findResultsMinimumLength",
    )
    @dbus_service.getter
    def get_find_results_minimum_length(self) -> int:
        """Returns the minimum length for find results to be spoken."""

        return self._get_setting("find-results-minimum-length", "i", 4)

    @dbus_service.setter
    def set_find_results_minimum_length(self, value: int) -> bool:
        """Sets the minimum length for find results to be spoken."""

        if self.get_find_results_minimum_length() == value:
            return True

        msg = f"DOCUMENT PRESENTER: Setting find results minimum length to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "find-results-minimum-length",
            value,
        )
        return True

    def present_find_results(self, obj: Atspi.Accessible, offset: int) -> bool:
        """Presents find results if appropriate based on settings.

        Returns True if results were presented, False otherwise.
        """

        script = script_manager.get_manager().get_active_script()
        if script is None:
            msg = "DOCUMENT PRESENTER: No active script for find results presentation."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        document = script.utilities.get_document_for_object(obj)
        start = AXText.get_selection_start_offset(obj)
        if not document or start < 0:
            return False

        offset = max(offset, start)
        context = script.utilities.get_caret_context(document)
        script.utilities.set_caret_context(obj, offset, document=document)

        end = AXText.get_selection_end_offset(obj)
        if (
            end - start < self.get_find_results_minimum_length()
            or not self.get_speak_find_results()
        ):
            return False

        if self._made_find_announcement and self.get_only_speak_changed_lines():
            context_obj, context_offset = context
            context_rect = AXText.get_range_rect(context_obj, context_offset, context_offset + 1)
            current_rect = AXText.get_range_rect(obj, offset, offset + 1)
            if AXComponent.rects_are_on_same_line(context_rect, current_rect):
                return False

        contents = script.utilities.get_line_contents_at_offset(obj, offset)
        presentation_manager.get_manager().speak_contents(contents)
        script.update_braille(obj)

        results_count = script.utilities.get_find_results_count()
        if results_count:
            presentation_manager.get_manager().present_message(results_count)

        self._made_find_announcement = True
        return True

    def _force_browse_mode_for_web_app_descendant(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> bool:
        """Returns True if we should force browse mode for web-app descendant obj."""

        if not AXObject.find_ancestor(obj, AXUtilities.is_embedded):
            return False

        if AXUtilities.is_tool_tip(obj):
            return AXUtilities.is_focused(obj)

        if AXUtilities.is_document_web(obj):
            return not self.is_focus_mode_widget(script, obj)

        return False

    def _navigation_prevents_focus_mode(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        prev_obj: Atspi.Accessible | None,
    ) -> tuple[bool | None, str]:
        """Returns (True/False, reason) if navigation state determines focus mode.

        Returns (None, '') if navigation doesn't determine the result.
        """

        if self.focus_mode_is_sticky(script.app):
            return True, "focus mode is sticky"
        if self.browse_mode_is_sticky(script.app):
            return False, "browse mode is sticky"
        if (
            focus_manager.get_manager().in_say_all()
            or table_navigator.get_navigator().last_input_event_was_navigation_command()
        ):
            reason = "SayAll is active" if focus_manager.get_manager().in_say_all() else "table nav"
            return False, reason

        _structural_navigator = structural_navigator.get_navigator()
        _caret_navigator = caret_navigator.get_navigator()
        caret_prevents = (
            _caret_navigator.last_command_prevents_focus_mode()
            and AXObject.find_ancestor_inclusive(prev_obj, AXUtilities.is_tool_tip) is None
        )
        if _structural_navigator.last_command_prevents_focus_mode() or caret_prevents:
            struct_prevents = _structural_navigator.last_command_prevents_focus_mode()
            nav_type = "structural" if struct_prevents else "caret"
            return False, f"prevented by {nav_type} nav settings"

        old_doc = script.utilities.get_top_level_document_for_object(prev_obj)
        new_doc = script.utilities.get_top_level_document_for_object(obj)
        if old_doc == new_doc and not self.get_native_nav_triggers_focus_mode():
            was_struct_nav = _structural_navigator.last_input_event_was_navigation_command()
            was_caret_nav = _caret_navigator.last_input_event_was_navigation_command()
            if not (was_struct_nav or was_caret_nav):
                result = self.in_focus_mode(script.app)
                return result, "prevented by native nav settings"

        return None, ""

    def use_focus_mode(
        self,
        obj: Atspi.Accessible,
        prev_obj: Atspi.Accessible | None = None,
    ) -> bool:
        """Returns True if we should use focus mode in obj."""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            msg = "DOCUMENT PRESENTER: No active script for focus mode decision."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if prev_obj and AXObject.is_dead(prev_obj):
            prev_obj = None

        nav_result, reason = self._navigation_prevents_focus_mode(script, obj, prev_obj)
        if nav_result is not None:
            prefix = "Using" if nav_result else "Not using"
            msg = f"DOCUMENT PRESENTER: {prefix} focus mode: {reason}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return nav_result

        do_not_toggle = AXUtilities.is_link(obj) or AXUtilities.is_radio_button(obj)
        stay_in_focus = (
            self.in_focus_mode(script.app)
            and do_not_toggle
            and input_event_manager.get_manager().last_event_was_unmodified_arrow()
        )
        if self.is_focus_mode_widget(script, obj) or stay_in_focus:
            reason = "is a focus mode widget" if not stay_in_focus else "arrowing in link/radio"
            tokens = ["DOCUMENT PRESENTER: Using focus mode:", obj, reason]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        was_in_app = AXObject.find_ancestor(prev_obj, AXUtilities.is_embedded)
        is_in_app = AXObject.find_ancestor(obj, AXUtilities.is_embedded)
        if is_in_app:
            if not was_in_app:
                msg = "DOCUMENT PRESENTER: Using focus mode: just entered a web application"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            if self.in_focus_mode(script.app):
                force_browse = self._force_browse_mode_for_web_app_descendant(script, obj)
                if force_browse:
                    tokens = ["DOCUMENT PRESENTER: Forcing browse mode for web app descendant", obj]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                else:
                    msg = "DOCUMENT PRESENTER: Staying in focus mode: inside a web application"
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                return not force_browse

        tokens = ["DOCUMENT PRESENTER: Not using focus mode for", obj, "due to lack of cause"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def create_preferences_grid(
        self,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> DocumentPreferencesGrid:
        """Returns the preferences grid for document settings."""

        return DocumentPreferencesGrid(self, title_change_callback)


_presenter = DocumentPresenter()


def get_presenter() -> DocumentPresenter:
    """Returns the Document Presenter."""

    return _presenter
