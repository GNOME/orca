# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2025 Igalia, S.L.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods

"""Implements structural navigation."""

from __future__ import annotations

import functools
from enum import Enum
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import (
    command_manager,
    dbus_service,
    debug,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event_manager,
    live_region_presenter,
    messages,
    object_properties,
    orca_gui_navlist,
    presentation_manager,
    say_all_presenter,
    script_manager,
    structural_navigator_command_definitions,
)
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_utilities_text import CaretSetReason
from .extension import Extension

if TYPE_CHECKING:
    from collections.abc import Callable

    from .command import Command
    from .dbus_service import UInt32
    from .input_event import InputEvent
    from .scripts import default


class NavigationMode(Enum):
    """Represents the structural navigation modes available."""

    OFF = "OFF"
    DOCUMENT = "DOCUMENT"
    GUI = "GUI"


class NavigationType(Enum):
    """The type of object a structural-navigation command moves amongst."""

    ANNOTATION = "annotation"
    BLOCKQUOTE = "blockquote"
    BUTTON = "button"
    CHECK_BOX = "checkbox"
    COMBO_BOX = "combobox"
    ENTRY = "entry"
    FORM_FIELD = "form_field"
    HEADING = "heading"
    IFRAME = "iframe"
    IMAGE = "image"
    LANDMARK = "landmark"
    LIST = "list"
    LIST_ITEM = "list_item"
    LIVE_REGION = "live_region"
    PARAGRAPH = "paragraph"
    RADIO_BUTTON = "radio_button"
    SEPARATOR = "separator"
    TABLE = "table"
    LINK = "link"
    UNVISITED_LINK = "unvisited_link"
    VISITED_LINK = "visited_link"
    LARGE_OBJECT = "large_object"
    CLICKABLE = "clickable"


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.StructuralNavigation",
    name="structural-navigation",
)
class StructuralNavigator(Extension):
    """Implements the structural navigation support available to scripts."""

    _SCHEMA = "structural-navigation"
    KEY_WRAPS = "wraps"
    KEY_LARGE_OBJECT_TEXT_LENGTH = "large-object-text-length"
    KEY_ENABLED = "enabled"
    KEY_TRIGGERS_FOCUS_MODE = "triggers-focus-mode"
    KEY_SKIP_UNLABELED_IMAGES = "skip-unlabeled-images"

    def _get_setting(self, key: str, gtype: str, default: Any) -> Any:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            gtype,
            default=default,
        )

    GROUP_LABEL = guilabels.KB_GROUP_STRUCTURAL_NAVIGATION

    def __init__(self) -> None:
        self._last_input_event: InputEvent | None = None

        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended: bool = False
        self._mode_for_script: dict[default.Script, NavigationMode] = {}
        self._previous_mode_for_script: dict[default.Script, NavigationMode] = {}
        super().__init__()

    @staticmethod
    def navigation_command(func):
        """Decorator that logs the command, records the input event, and returns True."""

        @functools.wraps(func)
        def wrapper(self, script, event=None, notify_user=True) -> bool:
            tokens = [
                "STRUCTURAL NAVIGATOR:",
                func,
                "\nScript:",
                script,
                "\nEvent:",
                event,
                "\nnotify_user:",
                notify_user,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.set_last_input_event(event)
            func(self, script, notify_user)
            return True

        return wrapper

    def _get_commands(self) -> list[Command]:
        return structural_navigator_command_definitions.get_commands(self)

    def _is_active_script(self, script):
        active_script = script_manager.get_manager().get_active_script()
        if active_script == script:
            return True

        tokens = ["STRUCTURAL NAVIGATOR:", script, "is not the active script", active_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def get_mode(self, script: default.Script) -> NavigationMode:
        """Returns the current structural-navigator mode associated with script."""

        return self._mode_for_script.get(script, NavigationMode.OFF)

    def set_mode(self, script: default.Script, mode: NavigationMode) -> None:
        """Sets the structural-navigator mode."""

        tokens = ["STRUCTURAL NAVIGATOR: Setting mode for", script, f"to {mode}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._mode_for_script[script] = mode

        if not (script and self._is_active_script(script)):
            return

        # Use the per-script mode combined with the user's preference to determine
        # whether commands should be active, without overwriting the preference.
        effective = mode != NavigationMode.OFF and self.get_is_enabled()
        command_manager.get_manager().set_group_enabled(
            guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
            effective,
        )

    def set_last_input_event(self, event: InputEvent | None) -> None:
        """Records the input event associated with the most recent navigation command."""

        self._last_input_event = event

    def last_input_event_was_navigation_command(self) -> bool:
        """Returns true if the last input event was a navigation command."""

        if self._last_input_event is None:
            return False

        manager = input_event_manager.get_manager()
        result = manager.last_event_equals_or_is_release_for_event(self._last_input_event)
        if self._last_input_event is not None:
            string = self._last_input_event.as_single_line_string()
        else:
            string = "None"

        msg = (
            f"STRUCTURAL NAVIGATOR: Last navigation event ({string}) is last input event: {result}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def last_command_prevents_focus_mode(self) -> bool:
        """Returns True if the last command was navigation but the setting disallows focus mode."""

        if not self.last_input_event_was_navigation_command():
            return False

        return not self.get_triggers_focus_mode()

    @gsettings_registry.get_registry().gsetting(
        key=KEY_WRAPS,
        schema="structural-navigation",
        gtype="b",
        default=True,
        summary="Wrap when reaching top/bottom",
        migration_key="wrappedStructuralNavigation",
    )
    @dbus_service.getter
    def get_navigation_wraps(self) -> bool:
        """Returns whether navigation wraps when reaching the top/bottom of the document."""

        return self._get_setting(self.KEY_WRAPS, "b", True)

    @dbus_service.setter
    def set_navigation_wraps(self, value: bool) -> bool:
        """Sets whether navigation wraps when reaching the top/bottom of the document."""

        msg = f"STRUCTURAL NAVIGATOR: Setting navigation wraps to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, self.KEY_WRAPS, value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_LARGE_OBJECT_TEXT_LENGTH,
        schema="structural-navigation",
        gtype="i",
        default=75,
        summary="Minimum text length for large objects",
        migration_key="largeObjectTextLength",
    )
    @dbus_service.getter
    def get_large_object_text_length(self) -> UInt32:
        """Returns the minimum number of characters to be considered a 'large object'."""

        return self._get_setting(self.KEY_LARGE_OBJECT_TEXT_LENGTH, "i", 75)

    @dbus_service.setter
    def set_large_object_text_length(self, value: UInt32) -> bool:
        """Sets the minimum number of characters to be considered a 'large object'."""

        msg = f"STRUCTURAL NAVIGATOR: Setting large object text length to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_LARGE_OBJECT_TEXT_LENGTH,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ENABLED,
        schema="structural-navigation",
        gtype="b",
        default=True,
        summary="Enable structural navigation",
        migration_key="structuralNavigationEnabled",
    )
    @dbus_service.getter
    def get_is_enabled(self) -> bool:
        """Returns whether structural navigation is enabled."""

        return self._get_setting(self.KEY_ENABLED, "b", True)

    @dbus_service.setter
    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether structural navigation is enabled."""

        if self.get_is_enabled() == value:
            msg = f"STRUCTURAL NAVIGATOR: Enabled already {value}. Refreshing command group."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            command_manager.get_manager().set_group_enabled(
                guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
                value,
            )
            return True

        msg = f"STRUCTURAL NAVIGATOR: Setting enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ENABLED,
            value,
        )

        script = script_manager.get_manager().get_active_script()
        if not script:
            return True

        current_mode = self.get_mode(script)
        if not value and current_mode == NavigationMode.OFF:
            return True

        self._last_input_event = None
        if value:
            if previous_mode := self._previous_mode_for_script.get(script):
                tokens = ["STRUCTURAL NAVIGATOR: Restoring mode for", script, "to", previous_mode]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                self._mode_for_script[script] = previous_mode
        else:
            self._previous_mode_for_script[script] = current_mode
            tokens = ["STRUCTURAL NAVIGATOR: Saving", current_mode, "as previous mode for", script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._mode_for_script[script] = NavigationMode.OFF

        command_manager.get_manager().set_group_enabled(
            guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_TRIGGERS_FOCUS_MODE,
        schema="structural-navigation",
        gtype="b",
        default=False,
        summary="Structural navigation triggers focus mode",
        migration_key="structNavTriggersFocusMode",
    )
    @dbus_service.getter
    def get_triggers_focus_mode(self) -> bool:
        """Returns whether structural navigation triggers focus mode."""

        return self._get_setting(self.KEY_TRIGGERS_FOCUS_MODE, "b", False)

    @dbus_service.setter
    def set_triggers_focus_mode(self, value: bool) -> bool:
        """Sets whether structural navigation triggers focus mode."""

        if self.get_triggers_focus_mode() == value:
            return True

        msg = f"STRUCTURAL NAVIGATOR: Setting triggers focus mode to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_TRIGGERS_FOCUS_MODE,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SKIP_UNLABELED_IMAGES,
        schema="structural-navigation",
        gtype="b",
        default=False,
        summary="Skip unlabeled images during navigation",
    )
    @dbus_service.getter
    def get_skip_unlabeled_images(self) -> bool:
        """Returns whether unlabeled images are skipped during navigation."""

        return self._get_setting(self.KEY_SKIP_UNLABELED_IMAGES, "b", False)

    @dbus_service.setter
    def set_skip_unlabeled_images(self, value: bool) -> bool:
        """Sets whether unlabeled images are skipped during navigation."""

        msg = f"STRUCTURAL NAVIGATOR: Setting skip unlabeled images to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SKIP_UNLABELED_IMAGES,
            value,
        )
        return True

    @dbus_service.command
    def cycle_mode(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycles among the structural navigation modes."""

        tokens = [
            "STRUCTURAL NAVIGATOR: cycle_mode. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and self._is_active_script(script)):
            return False

        self._last_input_event = None
        previous_mode = self.get_mode(script)
        msg = ""
        mode = None
        if previous_mode == NavigationMode.OFF:
            mode = NavigationMode.DOCUMENT
            msg = messages.STRUCTURAL_NAVIGATION_KEYS_DOCUMENT
        elif previous_mode == NavigationMode.GUI:
            mode = NavigationMode.OFF
            msg = messages.STRUCTURAL_NAVIGATION_KEYS_OFF
        else:
            mode = NavigationMode.GUI
            msg = messages.STRUCTURAL_NAVIGATION_KEYS_GUI

        if notify_user:
            presentation_manager.get_manager().present_message(msg)
        self.set_mode(script, mode)
        if mode == NavigationMode.DOCUMENT:
            root = self._determine_root_container(script)
            if not AXObject.supports_collection(root) and notify_user:
                presentation_manager.get_manager().present_message(
                    messages.STRUCTURAL_NAVIGATION_NOT_SUPPORTED_FULL,
                    messages.STRUCTURAL_NAVIGATION_NOT_SUPPORTED_BRIEF,
                )
        return True

    def suspend_commands(self, script, suspended, reason=""):
        """Suspends structural navigation independent of the enabled setting."""

        if not (script and self._is_active_script(script)):
            return

        msg = f"STRUCTURAL NAVIGATOR: Suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._suspended = suspended
        command_manager.get_manager().set_group_suspended(
            guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
            suspended,
        )

    def _get_container_for_nested_item(
        self, obj: Atspi.Accessible, nav_type: NavigationType
    ) -> Atspi.Accessible:
        # If an author put an ARIA heading inside a native heading (or vice versa), obj
        # could be the inner heading. If we treat the outer heading as as the previous heading
        # and then set the caret context to the first position inside the outer heading, i.e.
        # the inner heading, we'll get stuck. Thanks authors.
        if nav_type is NavigationType.HEADING:
            if ancestor := AXUtilities.find_ancestor(obj, AXUtilities.is_heading):
                tokens = [
                    "STRUCTURAL NAVIGATOR: Current heading",
                    obj,
                    "is inside another heading",
                    ancestor,
                    "Treating the outer heading as current.",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return ancestor
            return obj

        if nav_type is NavigationType.LIVE_REGION:
            candidate = obj
            while ancestor := AXUtilities.find_ancestor(candidate, AXUtilities.is_live_region):
                candidate = ancestor
            if candidate != obj:
                tokens = [
                    "STRUCTURAL NAVIGATOR: Current live region",
                    obj,
                    "is inside another live region",
                    candidate,
                    "Treating the outer region as current.",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return candidate

        return obj

    @staticmethod
    def _get_adjacent_or_wrap(
        objects: list[Atspi.Accessible],
        index: int,
        is_next: bool,
        should_wrap: bool,
        notify_user: bool,
    ) -> Atspi.Accessible | None:
        """Returns the adjacent object in the list, wrapping if enabled."""

        if is_next:
            if index + 1 < len(objects):
                return objects[index + 1]
            wrap_msg = messages.WRAPPING_TO_TOP
            wrap_target = objects[0]
        else:
            if index > 0:
                return objects[index - 1]
            wrap_msg = messages.WRAPPING_TO_BOTTOM
            wrap_target = objects[-1]

        if not should_wrap:
            return None
        if notify_user:
            presentation_manager.get_manager().present_message(wrap_msg)
        return wrap_target

    # pylint: disable-next=too-many-locals
    def _get_object_in_direction(
        self,
        script: default.Script,
        objects: list[Atspi.Accessible],
        is_next: bool,
        nav_type: NavigationType,
        should_wrap: bool | None = None,
        notify_user: bool = True,
    ) -> Atspi.Accessible | None:
        """Returns the next/previous object in relation to the current location."""

        if not objects:
            return None

        if should_wrap is None:
            should_wrap = self.get_navigation_wraps()

        index_by_object = {match: i for i, match in enumerate(objects)}

        # If we're in a matching object, return the next/previous one in the list.
        obj = focus_manager.get_manager().get_locus_of_focus()
        candidate = obj
        while candidate:
            if (index := index_by_object.get(candidate)) is None:
                candidate = AXObject.get_parent(candidate)
                continue

            if not is_next and nav_type in (NavigationType.HEADING, NavigationType.LIVE_REGION):
                alternative = self._get_container_for_nested_item(candidate, nav_type)
                if (alternative_index := index_by_object.get(alternative)) is not None:
                    index = alternative_index

            return self._get_adjacent_or_wrap(
                objects,
                index,
                is_next,
                should_wrap,
                notify_user,
            )

        # If we're not in a matching object, find the next/previous one based on the path.
        if not is_next:
            objects.reverse()

        current_path = AXObject.get_path(obj)
        for match in objects:
            path = AXObject.get_path(match)
            comparison = script.utilities.path_comparison(path, current_path)
            # A descendant of the focused object is always "after" it in path terms,
            # but the caret may have already moved past that descendant's location.
            if comparison > 0 and self._caret_is_past_descendant(obj, match):
                comparison = -1
            if (comparison > 0 and is_next) or (comparison < 0 and not is_next):
                return match

        if not should_wrap:
            return None

        wrap_msg = messages.WRAPPING_TO_TOP if is_next else messages.WRAPPING_TO_BOTTOM
        if notify_user:
            presentation_manager.get_manager().present_message(wrap_msg)
        return objects[0] if obj != objects[0] else None

    def _caret_is_past_descendant(
        self,
        obj: Atspi.Accessible,
        match: Atspi.Accessible,
    ) -> bool:
        """Returns True if match is a descendant of obj and the caret in obj is past it."""

        if not AXUtilities.is_ancestor(match, obj):
            return False

        child = match
        parent = AXObject.get_parent(child)
        while parent and parent != obj:
            child = parent
            parent = AXObject.get_parent(child)

        child_offset = AXHypertext.get_character_offset_in_parent(child)
        if child_offset < 0:
            return False

        caret_offset = AXText.get_caret_offset(obj)
        if caret_offset < 0:
            return False

        tokens = [
            "STRUCTURAL NAVIGATOR: Match",
            match,
            "is descendant of",
            obj,
            f"at offset {child_offset}; caret is at {caret_offset}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return caret_offset > child_offset

    def _get_state_string(self, obj: Atspi.Accessible) -> str:
        if AXUtilities.is_switch(obj):
            off, on = object_properties.SWITCH_INDICATORS_SPEECH
            return on if AXUtilities.is_checked(obj) else off

        if AXUtilities.is_check_box(obj):
            unchecked, checked, partially = object_properties.CHECK_BOX_INDICATORS_SPEECH
            if AXUtilities.is_indeterminate(obj):
                return partially
            return checked if AXUtilities.is_checked(obj) else unchecked

        if AXUtilities.is_radio_button(obj):
            unselected, selected = object_properties.RADIO_BUTTON_INDICATORS_SPEECH
            return selected if AXUtilities.is_checked(obj) else unselected

        if AXUtilities.is_link(obj):
            return (
                object_properties.STATE_VISITED
                if AXUtilities.is_visited(obj)
                else object_properties.STATE_UNVISITED
            )

        return ""

    def _get_item_string_by_role(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> str | None:
        """Returns a string for the object based on its role, or None if not role-specific."""

        if AXUtilities.is_table(obj):
            caption = AXTable.get_caption(obj)
            return AXText.get_all_text(caption) if caption else ""

        if AXUtilities.is_internal_frame(obj):
            result = self._get_item_string(script, AXObject.get_child(obj, 0))
            return result or AXUtilities.get_localized_role_name(obj)

        if AXUtilities.is_list(obj):
            children = list(AXObject.iter_children(obj, AXUtilities.is_list_item))
            count = len(children)
            counter = (
                messages.nested_list_item_count
                if AXUtilities.get_nesting_level(obj)
                else messages.list_item_count
            )
            return counter(count)

        if AXUtilities.is_description_list(obj):
            return messages.description_list_term_count(
                len(AXUtilities.find_all_description_terms(obj)),
            )

        if AXUtilities.is_image(obj):
            result = AXObject.get_image_description(obj)
            if not result:
                parent = AXObject.get_parent(obj)
                if AXUtilities.is_link(parent):
                    result = self._get_item_string(script, parent)
                else:
                    result = AXUtilities.get_localized_role_name(obj)
            return result

        return None

    def _get_item_string(self, script: default.Script, obj: Atspi.Accessible) -> str:
        if obj is None:
            return ""

        result = (
            AXObject.get_name(obj)
            or AXObject.get_description(obj)
            or AXUtilities.get_displayed_label(obj)
            or AXUtilities.get_displayed_description(obj)
        )
        if result:
            return result

        role_result = self._get_item_string_by_role(script, obj)
        if role_result is not None:
            return role_result

        if AXUtilities.is_page_tab_list(obj):
            return messages.tab_list_item_count(
                len(list(AXObject.iter_children(obj, AXUtilities.is_page_tab))),
            )

        if result := script.utilities.expand_eocs(obj):
            return result

        if AXUtilities.is_link(obj):
            result = AXHypertext.get_link_basename(obj)

        return result

    def _present_line(
        self,
        script: default.Script,
        obj: Atspi.Accessible | None = None,
        offset: int | None = None,
        notify_user: bool = True,
    ) -> None:
        if obj is None:
            return

        manager = focus_manager.get_manager()
        presenter = say_all_presenter.get_presenter()
        if manager.in_say_all() and presenter.get_structural_navigation_enabled():
            presenter.say_all(script, event=None, obj=obj, offset=offset)
            return

        prior_obj = manager.get_locus_of_focus()
        manager.emit_region_changed(obj, offset, mode=focus_manager.STRUCTURAL_NAVIGATOR)
        contents = script.utilities.get_line_contents_at_offset(obj, offset or 0)
        if contents and contents[0] and AXObject.supports_text(contents[0][0]):
            script.utilities.set_caret_position(
                contents[0][0], contents[0][1], reason=CaretSetReason.STRUCTURAL_NAVIGATION
            )
        if not notify_user:
            msg = "STRUCTURAL NAVIGATOR: _present_line called with notify_user=False"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            manager.set_locus_of_focus(None, obj, False)
            return

        pres_manager = presentation_manager.get_manager()
        pres_manager.speak_contents(contents, prior_obj=prior_obj)
        pres_manager.display_contents(contents)

    def _present_object(
        self,
        script: default.Script,
        obj: Atspi.Accessible | None = None,
        not_found_message: str = messages.STRUCTURAL_NAVIGATION_NOT_FOUND,
        offset: int | None = None,
        notify_user: bool = True,
    ) -> None:
        if obj is None:
            if notify_user:
                presentation_manager.get_manager().present_message(
                    not_found_message,
                    messages.STRUCTURAL_NAVIGATION_NOT_FOUND,
                )
            return

        if offset is None:
            offset = 0

        manager = focus_manager.get_manager()
        if self.get_mode(script) == NavigationMode.GUI:
            manager.set_locus_of_focus(None, obj)
            AXObject.grab_focus(obj)
            AXObject.clear_cache(obj, False, "Checking state after focus grab")
            if not AXUtilities.is_focused(obj) and notify_user:
                presentation_manager.get_manager().present_message(messages.NOT_FOCUSED)
            return

        presenter = say_all_presenter.get_presenter()
        if manager.in_say_all() and presenter.get_structural_navigation_enabled():
            presenter.say_all(script, event=None, obj=obj, offset=offset)
            return

        manager.emit_region_changed(obj, offset, mode=focus_manager.STRUCTURAL_NAVIGATOR)
        if not notify_user:
            msg = "STRUCTURAL NAVIGATOR: _present_object called with notify_user=False"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            manager.set_locus_of_focus(None, obj, False)
            if AXObject.supports_text(obj):
                script.utilities.set_caret_position(
                    obj, offset, reason=CaretSetReason.STRUCTURAL_NAVIGATION
                )
            return

        presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
        script.present_object(obj, offset=offset)

    def _present_object_list(
        self,
        script: default.Script,
        objects: list[Atspi.Accessible],
        dialog_title: str,
        column_headers: list[str],
        row_data_func: Callable,
        notify_user: bool = True,
    ) -> None:
        dialog_title = f"{dialog_title}: {messages.items_found(len(objects))}"
        if not objects:
            if notify_user:
                presentation_manager.get_manager().present_message(dialog_title)
            return

        current_object = script.utilities.get_caret_context()[0]
        try:
            index = objects.index(current_object)
        except ValueError:
            index = 0

        rows = [(obj, -1, *row_data_func(obj)) for obj in objects]
        orca_gui_navlist.show_ui(dialog_title, column_headers, rows, index)

    def _determine_root_container(self, script: default.Script) -> Atspi.Accessible:
        mode = self.get_mode(script)
        focus = focus_manager.get_manager().get_locus_of_focus()
        root = AXUtilities.find_ancestor_inclusive(focus, AXUtilities.is_modal_dialog)
        if root is None:
            if mode == NavigationMode.DOCUMENT:
                root = script.utilities.get_top_level_document_for_object(focus)
            elif mode == NavigationMode.GUI:
                root = AXUtilities.find_ancestor_inclusive(focus, AXUtilities.is_dialog_or_window)
                if root is None:
                    root = focus_manager.get_manager().get_active_window()

        tokens = ["STRUCTURAL NAVIGATOR: Root for", focus, "is", root, f"mode: {mode}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return root

    def _is_non_document_object(self, obj: Atspi.Accessible, must_be_showing: bool = True) -> bool:
        if AXUtilities.is_document_descendant(obj, inclusive=True):
            return False
        return not (must_be_showing and not AXUtilities.is_showing(obj))

    ########################
    #                      #
    # Annotations          #
    #                      #
    ########################

    def _get_all_annotations(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_annotations(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_annotation(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous annotation."""

        matches = self._get_all_annotations(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.ANNOTATION)
        self._present_object(
            script,
            result,
            messages.NO_MORE_ANNOTATIONS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def next_annotation(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next annotation."""

        matches = self._get_all_annotations(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.ANNOTATION)
        self._present_object(
            script,
            result,
            messages.NO_MORE_ANNOTATIONS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def list_annotations(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of annotations."""

        self._present_object_list(
            script,
            self._get_all_annotations(script),
            guilabels.SN_TITLE_ANNOTATION,
            [guilabels.SN_HEADER_ANNOTATION, guilabels.SN_HEADER_ROLE],
            lambda obj: [
                self._get_item_string(script, obj),
                AXUtilities.get_localized_role_name(obj),
            ],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Blockquotes          #
    #                      #
    ########################

    def _get_all_blockquotes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_block_quotes(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_blockquote(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous blockquote."""

        matches = self._get_all_blockquotes(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.BLOCKQUOTE)
        self._present_object(script, result, messages.NO_MORE_BLOCKQUOTES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_blockquote(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next blockquote."""

        matches = self._get_all_blockquotes(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.BLOCKQUOTE)
        self._present_object(script, result, messages.NO_MORE_BLOCKQUOTES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_blockquotes(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of blockquotes."""

        self._present_object_list(
            script,
            self._get_all_blockquotes(script),
            guilabels.SN_TITLE_BLOCKQUOTE,
            [guilabels.SN_HEADER_BLOCKQUOTE],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Buttons              #
    #                      #
    ########################

    def _get_all_buttons(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_buttons(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_button(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous button."""

        matches = self._get_all_buttons(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.BUTTON)
        self._present_object(script, result, messages.NO_MORE_BUTTONS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_button(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next button."""

        matches = self._get_all_buttons(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.BUTTON)
        self._present_object(script, result, messages.NO_MORE_BUTTONS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_buttons(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of buttons."""

        self._present_object_list(
            script,
            self._get_all_buttons(script),
            guilabels.SN_TITLE_BUTTON,
            [guilabels.SN_HEADER_BUTTON],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Check boxes          #
    #                      #
    ########################

    def _get_all_checkboxes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_check_boxes(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_checkbox(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous checkbox."""

        matches = self._get_all_checkboxes(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.CHECK_BOX)
        self._present_object(script, result, messages.NO_MORE_CHECK_BOXES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_checkbox(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next checkbox."""

        matches = self._get_all_checkboxes(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.CHECK_BOX)
        self._present_object(script, result, messages.NO_MORE_CHECK_BOXES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_checkboxes(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of checkboxes."""

        self._present_object_list(
            script,
            self._get_all_checkboxes(script),
            guilabels.SN_TITLE_CHECK_BOX,
            [guilabels.SN_HEADER_CHECK_BOX, guilabels.SN_HEADER_STATE],
            lambda obj: [self._get_item_string(script, obj), self._get_state_string(obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Large Objects        #
    #                      #
    ########################

    def _get_all_large_objects(self, script: default.Script) -> list[Atspi.Accessible]:
        minimum_length = self.get_large_object_text_length()

        def _is_large(obj):
            if AXUtilities.is_heading(obj):
                return True
            if AXUtilities.is_list(obj):
                return True
            if AXUtilities.is_table(obj):
                return True
            text = AXText.get_all_text(obj)
            return len(text) > minimum_length and text.count("\ufffc") / len(text) < 0.05

        root = self._determine_root_container(script)
        roles = [
            *AXUtilities.get_large_container_roles(),
            Atspi.Role.HEADING,
            Atspi.Role.PARAGRAPH,
            Atspi.Role.SECTION,
        ]
        return AXUtilities.find_all_with_role(root, roles, pred=_is_large)

    @dbus_service.command
    @navigation_command
    def previous_large_object(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous large object."""

        matches = self._get_all_large_objects(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.LARGE_OBJECT)
        self._present_object(
            script,
            result,
            messages.NO_MORE_LARGE_OBJECTS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def next_large_object(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next large object."""

        matches = self._get_all_large_objects(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.LARGE_OBJECT)
        self._present_object(
            script,
            result,
            messages.NO_MORE_LARGE_OBJECTS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def list_large_objects(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of large objects."""

        self._present_object_list(
            script,
            self._get_all_large_objects(script),
            guilabels.SN_TITLE_LARGE_OBJECT,
            [guilabels.SN_HEADER_OBJECT, guilabels.SN_HEADER_ROLE],
            lambda obj: [
                self._get_item_string(script, obj),
                AXUtilities.get_localized_role_name(obj),
            ],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Combo Boxes          #
    #                      #
    ########################

    def _get_all_comboboxes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_combo_boxes(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_combobox(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous combo box."""

        matches = self._get_all_comboboxes(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.COMBO_BOX)
        self._present_object(script, result, messages.NO_MORE_COMBO_BOXES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_combobox(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next combo box."""

        matches = self._get_all_comboboxes(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.COMBO_BOX)
        self._present_object(script, result, messages.NO_MORE_COMBO_BOXES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_comboboxes(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of combo boxes."""

        self._present_object_list(
            script,
            self._get_all_comboboxes(script),
            guilabels.SN_TITLE_COMBO_BOX,
            [guilabels.SN_HEADER_COMBO_BOX],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Entries              #
    #                      #
    ########################

    def _get_all_entries(self, script: default.Script) -> list[Atspi.Accessible]:
        def parent_is_not_editable(obj):
            parent = AXObject.get_parent(obj)
            return parent is not None and not AXUtilities.is_editable(parent)

        if self.get_mode(script) == NavigationMode.GUI:

            def pred(x):
                return self._is_non_document_object(x)
        else:
            pred = parent_is_not_editable

        root = self._determine_root_container(script)
        return AXUtilities.find_all_editable_objects(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_entry(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous entry."""

        matches = self._get_all_entries(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.ENTRY)
        self._present_object(script, result, messages.NO_MORE_ENTRIES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_entry(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next entry."""

        matches = self._get_all_entries(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.ENTRY)
        self._present_object(script, result, messages.NO_MORE_ENTRIES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_entries(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of entries."""

        self._present_object_list(
            script,
            self._get_all_entries(script),
            guilabels.SN_TITLE_ENTRY,
            [guilabels.SN_HEADER_LABEL, guilabels.SN_HEADER_VALUE],
            lambda obj: [self._get_item_string(script, obj), AXText.get_all_text(obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Form Fields          #
    #                      #
    ########################

    def _get_all_form_fields(self, script: default.Script) -> list[Atspi.Accessible]:
        def is_not_noneditable_doc_frame(obj):
            if AXUtilities.is_document_frame(obj):
                return AXUtilities.is_editable(obj)
            return True

        def pred(x):
            if self.get_mode(script) == NavigationMode.GUI:
                return self._is_non_document_object(x)
            return is_not_noneditable_doc_frame(x)

        root = self._determine_root_container(script)
        return AXUtilities.find_all_form_fields(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_form_field(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous form field."""

        matches = self._get_all_form_fields(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.FORM_FIELD)
        self._present_object(script, result, messages.NO_MORE_FORM_FIELDS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_form_field(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next form field."""

        matches = self._get_all_form_fields(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.FORM_FIELD)
        self._present_object(script, result, messages.NO_MORE_FORM_FIELDS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_form_fields(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of form fields."""

        self._present_object_list(
            script,
            self._get_all_form_fields(script),
            guilabels.SN_TITLE_FORM_FIELD,
            [guilabels.SN_HEADER_LABEL, guilabels.SN_HEADER_ROLE, guilabels.SN_HEADER_VALUE],
            lambda obj: [
                self._get_item_string(script, obj),
                AXUtilities.get_localized_role_name(obj),
                AXText.get_all_text(obj),
            ],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Headings             #
    #                      #
    ########################

    def _get_all_headings(
        self,
        script: default.Script,
        level: int | None = None,
    ) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        if level is None:
            return AXUtilities.find_all_headings(root, pred=pred)
        return AXUtilities.find_all_headings_at_level(root, level, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_heading(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous heading."""

        matches = self._get_all_headings(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.HEADING)
        self._present_object(script, result, messages.NO_MORE_HEADINGS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_heading(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next heading."""

        matches = self._get_all_headings(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.HEADING)
        self._present_object(script, result, messages.NO_MORE_HEADINGS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_headings(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of headings."""

        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING,
            [guilabels.SN_HEADER_HEADING, guilabels.SN_HEADER_LEVEL],
            lambda obj: [
                self._get_item_string(script, obj),
                str(AXUtilities.get_heading_level(obj)),
            ],
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def previous_heading_level_1(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous level 1 heading."""

        matches = self._get_all_headings(script, 1)
        result = self._get_object_in_direction(script, matches, False, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 1, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def next_heading_level_1(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next level 1 heading."""

        matches = self._get_all_headings(script, 1)
        result = self._get_object_in_direction(script, matches, True, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 1, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def list_headings_level_1(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of level 1 headings."""

        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 1,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def previous_heading_level_2(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous level 2 heading."""

        matches = self._get_all_headings(script, 2)
        result = self._get_object_in_direction(script, matches, False, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 2, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def next_heading_level_2(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next level 2 heading."""

        matches = self._get_all_headings(script, 2)
        result = self._get_object_in_direction(script, matches, True, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 2, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def list_headings_level_2(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of level 2 headings."""

        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 2,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def previous_heading_level_3(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous level 3 heading."""

        matches = self._get_all_headings(script, 3)
        result = self._get_object_in_direction(script, matches, False, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 3, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def next_heading_level_3(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next level 3 heading."""

        matches = self._get_all_headings(script, 3)
        result = self._get_object_in_direction(script, matches, True, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 3, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def list_headings_level_3(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of level 3 headings."""

        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 3,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def previous_heading_level_4(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous level 4 heading."""

        matches = self._get_all_headings(script, 4)
        result = self._get_object_in_direction(script, matches, False, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 4, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def next_heading_level_4(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next level 4 heading."""

        matches = self._get_all_headings(script, 4)
        result = self._get_object_in_direction(script, matches, True, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 4, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def list_headings_level_4(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of level 4 headings."""

        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 4,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def previous_heading_level_5(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous level 5 heading."""

        matches = self._get_all_headings(script, 5)
        result = self._get_object_in_direction(script, matches, False, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 5, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def next_heading_level_5(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next level 5 heading."""

        matches = self._get_all_headings(script, 5)
        result = self._get_object_in_direction(script, matches, True, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 5, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def list_headings_level_5(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of level 5 headings."""

        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 5,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def previous_heading_level_6(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous level 6 heading."""

        matches = self._get_all_headings(script, 6)
        result = self._get_object_in_direction(script, matches, False, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 6, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def next_heading_level_6(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next level 6 heading."""

        matches = self._get_all_headings(script, 6)
        result = self._get_object_in_direction(script, matches, True, NavigationType.HEADING)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 6, notify_user=notify_user
        )

    @dbus_service.command
    @navigation_command
    def list_headings_level_6(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of level 6 headings."""

        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 6,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Iframes              #
    #                      #
    ########################

    def _get_all_iframes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_internal_frames(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_iframe(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous iframe."""

        matches = self._get_all_iframes(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.IFRAME)
        self._present_object(script, result, messages.NO_MORE_IFRAMES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_iframe(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next iframe."""

        matches = self._get_all_iframes(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.IFRAME)
        self._present_object(script, result, messages.NO_MORE_IFRAMES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_iframes(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of iframes."""

        self._present_object_list(
            script,
            self._get_all_iframes(script),
            guilabels.SN_TITLE_IFRAME,
            [guilabels.SN_HEADER_IFRAME],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Images               #
    #                      #
    ########################

    @staticmethod
    def _image_is_labeled(obj: Atspi.Accessible) -> bool:
        """Returns True if the image has an accessible name or description."""

        return bool(
            AXObject.get_name(obj)
            or AXObject.get_description(obj)
            or AXObject.get_image_description(obj)
        )

    def _get_all_images(self, script: default.Script) -> list[Atspi.Accessible]:
        is_gui_mode = self.get_mode(script) == NavigationMode.GUI
        skip_unlabeled = self.get_skip_unlabeled_images()

        def pred(obj):
            if is_gui_mode and not self._is_non_document_object(obj):
                return False
            return not (skip_unlabeled and not self._image_is_labeled(obj))

        root = self._determine_root_container(script)
        return AXUtilities.find_all_images_and_image_maps(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_image(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous image."""

        matches = self._get_all_images(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.IMAGE)
        self._present_object(script, result, messages.NO_MORE_IMAGES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_image(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next image."""

        matches = self._get_all_images(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.IMAGE)
        self._present_object(script, result, messages.NO_MORE_IMAGES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_images(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of images."""

        self._present_object_list(
            script,
            self._get_all_images(script),
            guilabels.SN_TITLE_IMAGE,
            [guilabels.SN_HEADER_IMAGE],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Landmarks            #
    #                      #
    ########################

    def _get_all_landmarks(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_landmarks(root, pred=pred)

    def _present_landmark(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        notify_user: bool,
    ) -> None:
        if obj is None:
            self._present_object(script, obj, messages.NO_MORE_LANDMARKS, notify_user=notify_user)
            return

        self._present_line(script, obj, 0)

    @dbus_service.command
    @navigation_command
    def previous_landmark(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous landmark."""

        matches = self._get_all_landmarks(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.LANDMARK)
        self._present_landmark(script, result, notify_user)

    @dbus_service.command
    @navigation_command
    def next_landmark(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next landmark."""

        matches = self._get_all_landmarks(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.LANDMARK)
        self._present_landmark(script, result, notify_user)

    @dbus_service.command
    @navigation_command
    def list_landmarks(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of landmarks."""

        self._present_object_list(
            script,
            self._get_all_landmarks(script),
            guilabels.SN_TITLE_LANDMARK,
            [guilabels.SN_HEADER_LANDMARK, guilabels.SN_HEADER_ROLE],
            lambda obj: [
                self._get_item_string(script, obj),
                AXUtilities.get_localized_role_name(obj),
            ],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Lists                #
    #                      #
    ########################

    def _get_all_lists(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_lists(
            root,
            include_description_lists=True,
            include_tab_lists=True,
            pred=pred,
        )

    def _get_first_item(self, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        # Given a huge list, navigating to the item and presenting the ancestor list is more
        # performant.
        return AXObject.get_child(obj, 0)

    @dbus_service.command
    @navigation_command
    def previous_list(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous list."""

        matches = self._get_all_lists(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.LIST)
        result = self._get_first_item(result) or result
        self._present_object(script, result, messages.NO_MORE_LISTS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_list(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next list."""

        matches = self._get_all_lists(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.LIST)
        result = self._get_first_item(result) or result
        self._present_object(script, result, messages.NO_MORE_LISTS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_lists(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of lists."""

        self._present_object_list(
            script,
            self._get_all_lists(script),
            guilabels.SN_TITLE_LIST,
            [guilabels.SN_HEADER_LIST],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # List Items           #
    #                      #
    ########################

    def _get_all_list_items(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_list_items(
            root,
            include_description_terms=True,
            include_tabs=True,
            pred=pred,
        )

    @dbus_service.command
    @navigation_command
    def previous_list_item(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous list item."""

        matches = self._get_all_list_items(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.LIST_ITEM)
        self._present_object(script, result, messages.NO_MORE_LIST_ITEMS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_list_item(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next list item."""

        matches = self._get_all_list_items(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.LIST_ITEM)
        self._present_object(script, result, messages.NO_MORE_LIST_ITEMS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_list_items(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of list items."""

        self._present_object_list(
            script,
            self._get_all_list_items(script),
            guilabels.SN_TITLE_LIST_ITEM,
            [guilabels.SN_HEADER_LIST_ITEM],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Live Regions         #
    #                      #
    ########################

    def _get_all_live_regions(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_live_regions(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_live_region(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous live region."""

        matches = self._get_all_live_regions(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.LIVE_REGION)
        self._present_object(script, result, messages.NO_MORE_LIVE_REGIONS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_live_region(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next live region."""

        matches = self._get_all_live_regions(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.LIVE_REGION)
        self._present_object(script, result, messages.NO_MORE_LIVE_REGIONS, notify_user=notify_user)

    def _last_live_region(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Goes to the last live region."""

        tokens = [
            "STRUCTURAL NAVIGATOR: last_live_region. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        live_region_presenter.get_presenter().go_last_live_region(script, event)
        return True

    ########################
    #                      #
    # Paragraphs           #
    #                      #
    ########################

    def _get_all_paragraphs(self, script: default.Script) -> list[Atspi.Accessible]:
        def has_at_least_three_characters(obj):
            if AXUtilities.is_heading(obj):
                return True
            # We're choosing 3 characters as the minimum because some paragraphs contain a single
            # image or link and a text of length 2: An embedded object character and a space.
            # We want to skip these.
            return AXText.get_character_count(obj) > 2

        def pred(x):
            if self.get_mode(script) == NavigationMode.GUI:
                return self._is_non_document_object(x)
            return has_at_least_three_characters(x)

        root = self._determine_root_container(script)
        return AXUtilities.find_all_paragraphs(root, True, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_paragraph(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous paragraph."""

        matches = self._get_all_paragraphs(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.PARAGRAPH)
        self._present_object(script, result, messages.NO_MORE_PARAGRAPHS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_paragraph(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next paragraph."""

        matches = self._get_all_paragraphs(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.PARAGRAPH)
        self._present_object(script, result, messages.NO_MORE_PARAGRAPHS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_paragraphs(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of paragraphs."""

        self._present_object_list(
            script,
            self._get_all_paragraphs(script),
            guilabels.SN_TITLE_PARAGRAPH,
            [guilabels.SN_HEADER_PARAGRAPH],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Radio Buttons        #
    #                      #
    ########################

    def _get_all_radio_buttons(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_radio_buttons(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_radio_button(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous radio button."""

        matches = self._get_all_radio_buttons(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.RADIO_BUTTON)
        self._present_object(
            script,
            result,
            messages.NO_MORE_RADIO_BUTTONS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def next_radio_button(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next radio button."""

        matches = self._get_all_radio_buttons(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.RADIO_BUTTON)
        self._present_object(
            script,
            result,
            messages.NO_MORE_RADIO_BUTTONS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def list_radio_buttons(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of radio buttons."""

        self._present_object_list(
            script,
            self._get_all_radio_buttons(script),
            guilabels.SN_TITLE_RADIO_BUTTON,
            [guilabels.SN_HEADER_RADIO_BUTTON, guilabels.SN_HEADER_STATE],
            lambda obj: [self._get_item_string(script, obj), self._get_state_string(obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Separators           #
    #                      #
    ########################

    def _get_all_separators(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_separators(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_separator(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous separator."""

        matches = self._get_all_separators(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.SEPARATOR)
        self._present_object(script, result, messages.NO_MORE_SEPARATORS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_separator(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next separator."""

        matches = self._get_all_separators(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.SEPARATOR)
        self._present_object(script, result, messages.NO_MORE_SEPARATORS, notify_user=notify_user)

    ########################
    #                      #
    # Tables               #
    #                      #
    ########################

    def _get_all_tables(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_tables(root, pred=pred)

    def _get_first_table_cell(self, table: Atspi.Accessible) -> Atspi.Accessible | None:
        # Given a huge table, navigating to the cell and presenting the ancestor table is more
        # performant.
        if not AXUtilities.is_table(table):
            return None

        if cell := AXTable.get_cell_at(table, 0, 0):
            return cell

        tokens = ["STRUCTURAL NAVIGATOR: Broken table interface for", table]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        cell = AXUtilities.get_table_cell(table)
        if cell:
            tokens = ["STRUCTURAL NAVIGATOR: Located", cell, "for first cell"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return None

    @dbus_service.command
    @navigation_command
    def previous_table(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous table."""

        matches = self._get_all_tables(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.TABLE)
        obj = self._get_first_table_cell(result) or result
        self._present_object(script, obj, messages.NO_MORE_TABLES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_table(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next table."""

        matches = self._get_all_tables(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.TABLE)
        obj = self._get_first_table_cell(result) or result
        self._present_object(script, obj, messages.NO_MORE_TABLES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_tables(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of tables."""

        self._present_object_list(
            script,
            self._get_all_tables(script),
            guilabels.SN_TITLE_TABLE,
            [guilabels.SN_HEADER_CAPTION, guilabels.SN_HEADER_DESCRIPTION],
            lambda obj: [
                self._get_item_string(script, obj),
                AXUtilities.get_table_description_for_presentation(obj),
            ],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Unvisited Links      #
    #                      #
    ########################

    def _get_all_unvisited_links(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_unvisited_links(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_unvisited_link(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous unvisited link."""

        matches = self._get_all_unvisited_links(script)
        result = self._get_object_in_direction(
            script, matches, False, NavigationType.UNVISITED_LINK
        )
        self._present_object(
            script,
            result,
            messages.NO_MORE_UNVISITED_LINKS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def next_unvisited_link(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next unvisited link."""

        matches = self._get_all_unvisited_links(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.UNVISITED_LINK)
        self._present_object(
            script,
            result,
            messages.NO_MORE_UNVISITED_LINKS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def list_unvisited_links(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of unvisited links."""

        self._present_object_list(
            script,
            self._get_all_unvisited_links(script),
            guilabels.SN_TITLE_UNVISITED_LINK,
            [guilabels.SN_HEADER_LINK, guilabels.SN_HEADER_URI],
            lambda obj: [self._get_item_string(script, obj), AXHypertext.get_link_uri(obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Visited Links        #
    #                      #
    ########################

    def _get_all_visited_links(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_visited_links(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_visited_link(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous visited link."""

        matches = self._get_all_visited_links(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.VISITED_LINK)
        self._present_object(
            script,
            result,
            messages.NO_MORE_VISITED_LINKS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def next_visited_link(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next visited link."""

        matches = self._get_all_visited_links(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.VISITED_LINK)
        self._present_object(
            script,
            result,
            messages.NO_MORE_VISITED_LINKS,
            notify_user=notify_user,
        )

    @dbus_service.command
    @navigation_command
    def list_visited_links(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of visited links."""

        self._present_object_list(
            script,
            self._get_all_visited_links(script),
            guilabels.SN_TITLE_VISITED_LINK,
            [guilabels.SN_HEADER_LINK, guilabels.SN_HEADER_URI],
            lambda obj: [self._get_item_string(script, obj), AXHypertext.get_link_uri(obj)],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Links                #
    #                      #
    ########################

    def _get_all_links(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_links(root, pred=pred)

    @dbus_service.command
    @navigation_command
    def previous_link(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous link."""

        matches = self._get_all_links(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.LINK)
        self._present_object(script, result, messages.NO_MORE_LINKS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_link(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next link."""

        matches = self._get_all_links(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.LINK)
        self._present_object(script, result, messages.NO_MORE_LINKS, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_links(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of links."""

        self._present_object_list(
            script,
            self._get_all_links(script),
            guilabels.SN_TITLE_LINK,
            [guilabels.SN_HEADER_LINK, guilabels.SN_HEADER_STATE, guilabels.SN_HEADER_URI],
            lambda obj: [
                self._get_item_string(script, obj),
                self._get_state_string(obj),
                AXHypertext.get_link_uri(obj),
            ],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Clickables           #
    #                      #
    ########################

    def _get_all_clickables(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        result = AXUtilities.find_all_clickables(root, pred=pred)
        result += AXUtilities.find_all_focusable_objects_with_click_ancestor(root, pred=pred)
        return result

    @dbus_service.command
    @navigation_command
    def previous_clickable(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the previous clickable."""

        matches = self._get_all_clickables(script)
        result = self._get_object_in_direction(script, matches, False, NavigationType.CLICKABLE)
        self._present_object(script, result, messages.NO_MORE_CLICKABLES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def next_clickable(self, script: default.Script, notify_user: bool = True) -> None:
        """Goes to the next clickable."""

        matches = self._get_all_clickables(script)
        result = self._get_object_in_direction(script, matches, True, NavigationType.CLICKABLE)
        self._present_object(script, result, messages.NO_MORE_CLICKABLES, notify_user=notify_user)

    @dbus_service.command
    @navigation_command
    def list_clickables(self, script: default.Script, notify_user: bool = True) -> None:
        """Displays a list of clickables."""

        self._present_object_list(
            script,
            self._get_all_clickables(script),
            guilabels.SN_TITLE_CLICKABLE,
            [guilabels.SN_HEADER_CLICKABLE, guilabels.SN_HEADER_ROLE],
            lambda obj: [
                self._get_item_string(script, obj),
                AXUtilities.get_localized_role_name(obj),
            ],
            notify_user=notify_user,
        )

    ########################
    #                      #
    # Containers           #
    #                      #
    ########################

    def _get_current_container(self, script: default.Script) -> Atspi.Accessible | None:
        focus = focus_manager.get_manager().get_locus_of_focus()
        if container := AXUtilities.find_ancestor_inclusive(focus, AXUtilities.is_large_container):
            root = self._determine_root_container(script)
            if not AXUtilities.is_ancestor(container, root):
                return None
        return container

    @dbus_service.command
    @navigation_command
    def container_start(self, script: default.Script, notify_user: bool = True) -> None:
        """Moves to the start of the current container."""

        container = self._get_current_container(script)
        if container is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.CONTAINER_NOT_IN_A)
            return

        obj, offset = script.utilities.next_context(container, -1)
        self._present_line(script, obj, offset, notify_user)

    @dbus_service.command
    @navigation_command
    def container_end(self, script: default.Script, notify_user: bool = True) -> None:
        """Moves to the end of the current container."""

        container = self._get_current_container(script)
        if container is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.CONTAINER_NOT_IN_A)
            return

        # Unlike going to the start of the container, when we move to the next edge
        # we pass beyond it on purpose. This makes us consistent with NVDA.
        obj, offset = script.utilities.last_context(container)
        next_object, next_offset = script.utilities.next_context(obj, offset)
        if next_object is None:
            next_object, next_offset = obj, offset

        self._present_line(script, next_object, next_offset, notify_user)


_navigator = StructuralNavigator()


def get_navigator() -> StructuralNavigator:
    """Returns the Structural Navigator"""

    return _navigator
