# Orca
#
# Copyright 2023 The Orca Team
# Author: Rynhardt Kruger <rynkruger@gmail.com>
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

"""Provides ability to navigate objects hierarchically."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import (
    cmdnames,
    dbus_service,
    debug,
    focus_manager,
    guilabels,
    input_event,
    keybindings,
    messages,
    presentation_manager,
)
from .ax_event_synthesizer import AXEventSynthesizer
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .command import Command, KeyboardCommand
from .extension import Extension

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class ObjectNavigator(Extension):
    """Provides ability to navigate objects hierarchically."""

    GROUP_LABEL = guilabels.KB_GROUP_OBJECT_NAVIGATION

    def __init__(self) -> None:
        self._navigator_focus: Atspi.Accessible | None = None
        self._last_navigator_focus: Atspi.Accessible | None = None
        self._last_locus_of_focus: Atspi.Accessible | None = None
        self._simplify: bool = True
        super().__init__()

    def _get_commands(self) -> list[Command]:
        commands_data = [
            ("object_navigator_up", self.move_to_parent, cmdnames.NAVIGATOR_UP, "Up"),
            ("object_navigator_down", self.move_to_first_child, cmdnames.NAVIGATOR_DOWN, "Down"),
            ("object_navigator_next", self.move_to_next_sibling, cmdnames.NAVIGATOR_NEXT, "Right"),
            (
                "object_navigator_previous",
                self.move_to_previous_sibling,
                cmdnames.NAVIGATOR_PREVIOUS,
                "Left",
            ),
            (
                "object_navigator_perform_action",
                self.perform_action,
                cmdnames.NAVIGATOR_PERFORM_ACTION,
                "Return",
            ),
            (
                "object_navigator_toggle_simplify",
                self.toggle_simplify,
                cmdnames.NAVIGATOR_TOGGLE_SIMPLIFIED,
                "s",
            ),
        ]

        commands: list[Command] = []
        for name, function, description, keysym in commands_data:
            kb = keybindings.KeyBinding(keysym, keybindings.ORCA_CTRL_MODIFIER_MASK)
            commands.append(
                KeyboardCommand(
                    name,
                    function,
                    self.GROUP_LABEL,
                    description,
                    desktop_keybinding=kb,
                    laptop_keybinding=kb,
                ),
            )
        return commands

    def _include_in_simple_navigation(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj should be included in simple navigation."""

        return AXUtilities.is_paragraph(obj)

    def _exclude_from_simple_navigation(
        self,
        _script: default.Script,
        obj: Atspi.Accessible,
    ) -> bool:
        """Returns True if obj should be excluded from simple navigation."""

        if self._include_in_simple_navigation(obj):
            tokens = ["OBJECT NAVIGATOR: Not excluding", obj, ": explicit inclusion"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        # is_layout_only should catch things that really should be skipped.
        #
        # You do not want to exclude all sections because they may be focusable, e.g.
        # <div tabindex=0>foo</div> should not be excluded, despite the poor authoring.
        #
        # You do not want to exclude table cells and headers because it will make the
        # selectable items in tables non-navigable (e.g. the mail folders in Evolution)
        if AXUtilities.is_layout_only(obj):
            tokens = ["OBJECT NAVIGATOR: Excluding", obj, ": is layout only"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["OBJECT NAVIGATOR: Not excluding", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def _children(self, script: default.Script, obj: Atspi.Accessible) -> list:
        """Returns a list of children for obj, taking simple navigation into account."""

        if not AXObject.get_child_count(obj):
            return []

        children = list(AXObject.iter_children(obj))
        if not self._simplify:
            return children

        # Add the children of excluded objects to our list of children.
        functional_children = []
        for child in children:
            if self._exclude_from_simple_navigation(script, child):
                functional_children.extend(self._children(script, child))
            else:
                functional_children.append(child)

        return functional_children

    def _parent(self, script: default.Script, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the parent for obj, taking simple navigation into account."""

        parent = AXObject.get_parent(obj)
        if not self._simplify:
            return parent

        # The first non-excluded ancestor is the functional parent.
        while parent is not None and self._exclude_from_simple_navigation(script, parent):
            parent = AXObject.get_parent(parent)

        return parent

    def _set_navigator_focus(self, obj: Atspi.Accessible) -> None:
        """Changes the navigator focus, storing the previous focus."""

        self._last_navigator_focus = self._navigator_focus
        self._navigator_focus = obj

    def _update(self) -> None:
        """Updates the navigator focus to Orca's object of interest."""

        mode, region = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        obj = region or focus_manager.get_manager().get_locus_of_focus()
        if self._last_locus_of_focus == obj or (
            region is None and mode == focus_manager.FLAT_REVIEW
        ):
            return

        self._navigator_focus = obj
        self._last_locus_of_focus = obj

    def _present(self, script: default.Script, notify_user: bool = True) -> None:
        """Presents the current navigator focus to the user."""

        tokens = ["OBJECT NAVIGATOR: Presenting", self._navigator_focus]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        focus_manager.get_manager().emit_region_changed(
            self._navigator_focus,
            mode=focus_manager.OBJECT_NAVIGATOR,
        )
        if not notify_user:
            msg = "OBJECT NAVIGATOR: _present called with notify_user=False"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        script.present_object(self._navigator_focus, priorObj=self._last_navigator_focus)

    @dbus_service.command
    def move_to_parent(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves the navigator focus to the parent of the current focus."""

        tokens = [
            "OBJECT NAVIGATOR: move_to_parent. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._update()
        parent = self._parent(script, self._navigator_focus)
        if parent is not None:
            self._set_navigator_focus(parent)
            self._present(script, notify_user)
        elif notify_user:
            presentation_manager.get_manager().present_message(messages.NAVIGATOR_NO_PARENT)
        return True

    @dbus_service.command
    def move_to_first_child(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves the navigator focus to the first child of the current focus."""

        tokens = [
            "OBJECT NAVIGATOR: move_to_first_child. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._update()
        children = self._children(script, self._navigator_focus)
        if not children:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.NAVIGATOR_NO_CHILDREN)
            return True

        self._set_navigator_focus(children[0])
        self._present(script, notify_user)
        return True

    @dbus_service.command
    def move_to_next_sibling(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves the navigator focus to the next sibling of the current focus."""

        tokens = [
            "OBJECT NAVIGATOR: move_to_next_sibling. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._update()
        parent = self._parent(script, self._navigator_focus)
        if parent is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.NAVIGATOR_NO_NEXT)
            return True

        siblings = self._children(script, parent)
        if self._navigator_focus in siblings:
            index = siblings.index(self._navigator_focus)
            if index < len(siblings) - 1:
                self._set_navigator_focus(siblings[index + 1])
                self._present(script, notify_user)
            elif notify_user:
                presentation_manager.get_manager().present_message(messages.NAVIGATOR_NO_NEXT)
        else:
            self._set_navigator_focus(parent)
            self._present(script, notify_user)
        return True

    @dbus_service.command
    def move_to_previous_sibling(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves the navigator focus to the previous sibling of the current focus."""

        tokens = [
            "OBJECT NAVIGATOR: move_to_previous_sibling. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._update()
        parent = self._parent(script, self._navigator_focus)
        if parent is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.NAVIGATOR_NO_PREVIOUS)
            return True

        siblings = self._children(script, parent)
        if self._navigator_focus in siblings:
            index = siblings.index(self._navigator_focus)
            if index > 0:
                self._set_navigator_focus(siblings[index - 1])
                self._present(script, notify_user)
            elif notify_user:
                presentation_manager.get_manager().present_message(messages.NAVIGATOR_NO_PREVIOUS)
        else:
            self._set_navigator_focus(parent)
            self._present(script, notify_user)
        return True

    @dbus_service.command
    def toggle_simplify(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles simplified navigation."""

        tokens = [
            "OBJECT NAVIGATOR: toggle_simplify. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._simplify = not self._simplify
        if notify_user:
            if self._simplify:
                presentation_manager.get_manager().present_message(
                    messages.NAVIGATOR_SIMPLIFIED_ENABLED,
                )
            else:
                presentation_manager.get_manager().present_message(
                    messages.NAVIGATOR_SIMPLIFIED_DISABLED,
                )
        return True

    @dbus_service.command
    def perform_action(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Attempts to click on the current focus."""

        tokens = [
            "OBJECT NAVIGATOR: perform_action. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXEventSynthesizer.try_all_clickable_actions(self._navigator_focus):
            return True

        AXEventSynthesizer.click_object(self._navigator_focus, 1)
        return True


_navigator: ObjectNavigator = ObjectNavigator()


def get_navigator() -> ObjectNavigator:
    """Returns the Object Navigator"""

    return _navigator
