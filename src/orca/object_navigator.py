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

"""Object for maintaining the state of the object navigator."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 The Orca Team"
__license__   = "LGPL"

from . import cmdnames
from . import debug
from . import eventsynthesizer
from . import input_event
from . import keybindings
from . import messages
from . import orca_state
from .ax_object import AXObject
from .ax_utilities import AXUtilities


class ObjectNavigator:
    def __init__(self):
        self._navigator_focus = None
        self._last_navigator_focus = None
        self._last_locus_of_focus = None
        self._simplify = True
        self._handlers = self._setup_handlers()
        self._bindings = self._setup_bindings()

    def get_bindings(self):
        """Returns the object-navigator keybindings."""

        return self._bindings

    def get_handlers(self):
        """Returns the object-navigator handlers."""

        return self._handlers

    def _setup_bindings(self):
        """Sets up and returns the object-navigator key bindings."""

        bindings = keybindings.KeyBindings()

        bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("object_navigator_up")))

        bindings.add(
            keybindings.KeyBinding(
                "Down",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("object_navigator_down")))

        bindings.add(
            keybindings.KeyBinding(
                "Right",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("object_navigator_next")))

        bindings.add(
            keybindings.KeyBinding(
                "Left",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("object_navigator_previous")))

        bindings.add(
            keybindings.KeyBinding(
                "Return",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("object_navigator_perform_action")))

        bindings.add(
            keybindings.KeyBinding(
                "s",
                keybindings.defaultModifierMask,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("object_navigator_toggle_simplify")))

        return bindings

    def _setup_handlers(self):
        """Sets up and returns the object-navigator input event handlers."""

        handlers = {}

        handlers["object_navigator_up"] = \
            input_event.InputEventHandler(
                self.up,
                cmdnames.NAVIGATOR_UP)

        handlers["object_navigator_down"] = \
            input_event.InputEventHandler(
                self.down,
                cmdnames.NAVIGATOR_DOWN)

        handlers["object_navigator_next"] = \
            input_event.InputEventHandler(
                self.next,
                cmdnames.NAVIGATOR_NEXT)

        handlers["object_navigator_previous"] = \
            input_event.InputEventHandler(
                self.previous,
                cmdnames.NAVIGATOR_PREVIOUS)

        handlers["object_navigator_perform_action"] = \
            input_event.InputEventHandler(
                self.perform_action,
                cmdnames.NAVIGATOR_PERFORM_ACTION)

        handlers["object_navigator_toggle_simplify"] = \
            input_event.InputEventHandler(
                self.toggle_simplify,
                cmdnames.NAVIGATOR_TOGGLE_SIMPLIFIED)

        return handlers

    def _include_in_simple_navigation(self, obj):
        """Returns True if obj should be included in simple navigation."""

        return AXUtilities.is_paragraph(obj)

    def _exclude_from_simple_navigation(self, script, obj):
        """Returns True if obj should be excluded from simple navigation."""

        if self._include_in_simple_navigation(obj):
            msg = "OBJECT NAVIGATOR: Not excluding %s: explicit inclusion" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if script.utilities.isLayoutOnly(obj):
            msg = "OBJECT NAVIGATOR: Excluding %s: is layout only" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_table_cell_or_header(obj):
            msg = "OBJECT NAVIGATOR: Excluding %s: is table cell or header" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_section(obj):
            msg = "OBJECT NAVIGATOR: Excluding %s: is section" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "OBJECT NAVIGATOR: Not excluding %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def _children(self, script, obj):
        """Returns a list of children for obj, taking simple navigation into account."""

        if not AXObject.get_child_count(obj):
            return []

        children = [child for child in AXObject.iter_children(obj)]
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

    def _parent(self, script, obj):
        """Returns the parent for obj, taking simple navigation into account."""

        parent = AXObject.get_parent(obj)
        if not self._simplify:
            return parent

        # The first non-excluded ancestor is the functional parent.
        while parent is not None and self._exclude_from_simple_navigation(script, parent):
            parent = AXObject.get_parent(parent)

        return parent

    def _set_navigator_focus(self, obj):
        """Changes the navigator focus, storing the previous focus."""

        self._last_navigator_focus = self._navigator_focus
        self._navigator_focus = obj

    def update(self):
        """Updates the navigator focus to Orca's locusOfFocus."""

        if self._last_locus_of_focus == orca_state.locusOfFocus:
            return

        self._navigator_focus = orca_state.locusOfFocus
        self._last_locus_of_focus = orca_state.locusOfFocus

    def present(self, script):
        """Presents the current navigator focus to the user."""

        script.presentObject(self._navigator_focus, priorObj=self._last_navigator_focus)

    def up(self, script, event=None):
        """Moves the navigator focus to the parent of the current focus."""

        self.update()
        parent = self._parent(script, self._navigator_focus)
        if parent is not None:
            self._set_navigator_focus(parent)
            self.present(script)
        else:
            script.presentMessage(messages.NAVIGATOR_NO_PARENT)

    def down(self, script, event=None):
        """Moves the navigator focus to the first child of the current focus."""

        self.update()
        children = self._children(script, self._navigator_focus)
        if not children:
            script.presentMessage(messages.NAVIGATOR_NO_CHILDREN)
            return

        self._set_navigator_focus(children[0])
        self.present(script)

    def next(self, script, event=None):
        """Moves the navigator focus to the next sibling of the current focus."""

        self.update()
        parent = self._parent(script, self._navigator_focus)
        if parent is None:
            script.presentMessage(messages.NAVIGATOR_NO_NEXT)
            return

        siblings = self._children(script, parent)
        if self._navigator_focus in siblings:
            index = siblings.index(self._navigator_focus)
            if index < len(siblings) - 1:
                self._set_navigator_focus(siblings[index+1])
                self.present(script)
            else:
                script.presentMessage(messages.NAVIGATOR_NO_NEXT)
        else:
            self._set_navigator_focus(parent)

    def previous(self, script, event=None):
        """Moves the navigator focus to the previous sibling of the current focus."""

        self.update()
        parent = self._parent(script, self._navigator_focus)
        if parent is None:
            script.presentMessage(messages.NAVIGATOR_NO_PREVIOUS)
            return

        siblings = self._children(script, parent)
        if self._navigator_focus in siblings:
            index = siblings.index(self._navigator_focus)
            if index > 0:
                self._set_navigator_focus(siblings[index-1])
                self.present(script)
            else:
                script.presentMessage(messages.NAVIGATOR_NO_PREVIOUS)
        else:
            self._set_navigator_focus(parent)

    def toggle_simplify(self, script, event=None):
        """Toggles simplified navigation."""

        self.navigator.simplify = not self.navigator.simplify
        if self.navigator.simplify:
            script.presentMessage(messages.NAVIGATOR_SIMPLIFIED_ENABLED)
        else:
            script.presentMessage(messages.NAVIGATOR_SIMPLIFIED_DISABLED)
        return True

    def perform_action(self, script, event=None):
        """Attempts to click on the current focus."""
        if eventsynthesizer.tryAllClickableActions(self._navigator_focus):
            return True

        eventsynthesizer.clickObject(self._navigator_focus, 1)
        return True


_navigator = ObjectNavigator()
def getNavigator():
    return _navigator
