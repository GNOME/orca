# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines

"""Provides utilities for managing input events."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from . import focus_manager
from . import input_event
from . import script_manager
from . import settings
from .ax_object import AXObject
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from . import keybindings

class InputEventManager:
    """Provides utilities for managing input events."""

    def __init__(self) -> None:
        self._last_input_event: input_event.InputEvent | None = None
        self._last_non_modifier_key_event: input_event.KeyboardEvent | None = None
        self._device: Atspi.Device | None = None
        self._mapped_keycodes: list[int] = []
        self._mapped_keysyms: list[int] = []
        self._grabbed_bindings: dict[int, keybindings.KeyBinding] = {}
        self._paused: bool = False

    def start_key_watcher(self) -> None:
        """Starts the watcher for keyboard input events."""

        msg = "INPUT EVENT MANAGER: Starting key watcher."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if Atspi.get_version() >= (2, 55, 90):
            self._device = Atspi.Device.new_full("org.gnome.Orca")
        else:
            self._device = Atspi.Device.new()
        self._device.add_key_watcher(self.process_keyboard_event)

    def stop_key_watcher(self) -> None:
        """Starts the watcher for keyboard input events."""

        msg = "INPUT EVENT MANAGER: Stopping key watcher."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._device = None

    def pause_key_watcher(self, pause: bool = True, reason: str = "") -> None:
        """Pauses processing of keyboard input events."""

        msg = f"INPUT EVENT MANAGER: Pause queueing: {pause}. {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._paused = pause

    def check_grabbed_bindings(self) -> None:
        """Checks the grabbed key bindings."""

        msg = f"INPUT EVENT MANAGER: {len(self._grabbed_bindings)} grabbed key bindings."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        for grab_id, binding in self._grabbed_bindings.items():
            msg = f"INPUT EVENT MANAGER: {grab_id} for: {binding}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def add_grabs_for_keybinding(self, binding: keybindings.KeyBinding) -> list[int]:
        """Adds grabs for binding if it is enabled, returns grab IDs."""

        if not (binding.is_enabled() and binding.is_bound()):
            return []

        if binding.has_grabs():
            tokens = ["INPUT EVENT MANAGER:", binding, "already has grabs."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        if self._device is None:
            tokens = ["INPUT EVENT MANAGER: No device to add grab for", binding]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        grab_ids = []
        for kd in binding.key_definitions():
            grab_id = self._device.add_key_grab(kd, None)
            # When we have double/triple-click bindings, the single-click binding will be
            # registered first, and subsequent attempts to register what is externally the
            # same grab will fail. If we only have a double/triple-click, it succeeds.
            # A grab id of 0 indicates failure.
            if grab_id == 0:
                continue
            grab_ids.append(grab_id)
            self._grabbed_bindings[grab_id] = binding

        return grab_ids

    def remove_grabs_for_keybinding(self, binding: keybindings.KeyBinding) -> None:
        """Removes grabs for binding."""

        if self._device is None:
            tokens = ["INPUT EVENT MANAGER: No device to remove grab from", binding]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        grab_ids = binding.get_grab_ids()
        if not grab_ids:
            tokens = ["INPUT EVENT MANAGER:", binding, "doesn't have grabs to remove."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        for grab_id in grab_ids:
            self._device.remove_key_grab(grab_id)
            removed = self._grabbed_bindings.pop(grab_id, None)
            if removed is None:
                msg = f"INPUT EVENT MANAGER: No key binding for grab id {grab_id}"
                debug.print_message(debug.LEVEL_INFO, msg, True)

    def map_keycode_to_modifier(self, keycode: int) -> int:
        """Maps keycode as a modifier, returns the newly-mapped modifier."""

        if self._device is None:
            msg = f"INPUT EVENT MANAGER: No device to map keycode {keycode} to modifier"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        self._mapped_keycodes.append(keycode)
        return self._device.map_modifier(keycode)

    def map_keysym_to_modifier(self, keysym: int) -> int:
        """Maps keysym as a modifier, returns the newly-mapped modifier."""

        if self._device is None:
            msg = f"INPUT EVENT MANAGER: No device to map keysym {keysym} to modifier"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        self._mapped_keysyms.append(keysym)
        return self._device.map_keysym_modifier(keysym)

    def unmap_all_modifiers(self) -> None:
        """Unmaps all previously mapped modifiers."""

        if self._device is None:
            msg = "INPUT EVENT MANAGER: No device to unmap all modifiers from"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        for keycode in self._mapped_keycodes:
            self._device.unmap_modifier(keycode)

        for keysym in self._mapped_keysyms:
            self._device.unmap_keysym_modifier(keysym)

        self._mapped_keycodes.clear()
        self._mapped_keysyms.clear()

    def add_grab_for_modifier(self, modifier: str, keysym: int, keycode: int) -> int:
        """Adds grab for modifier, returns grab id."""

        if self._device is None:
            msg = f"INPUT EVENT MANAGER: No device to add grab for {modifier}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        kd = Atspi.KeyDefinition()
        kd.keysym = keysym
        kd.keycode = keycode
        kd.modifiers = 0
        grab_id = self._device.add_key_grab(kd)

        msg = f"INPUT EVENT MANAGER: Grab id for {modifier}: {grab_id}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return grab_id

    def remove_grab_for_modifier(self, modifier: str, grab_id: int) -> None:
        """Removes grab for modifier."""

        if self._device is None:
            msg = f"INPUT EVENT MANAGER: No device to remove grab from {modifier}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._device.remove_key_grab(grab_id)
        msg = f"INPUT EVENT MANAGER: Grab id removed for {modifier}: {grab_id}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def grab_keyboard(self, reason: str = "") -> None:
        """Grabs the keyboard, e.g. when entering learn mode."""

        msg = "INPUT EVENT MANAGER: Grabbing keyboard"
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        Atspi.Device.grab_keyboard(self._device)

    def ungrab_keyboard(self, reason: str = "") -> None:
        """Removes keyboard grab, e.g. when exiting learn mode."""

        msg = "INPUT EVENT MANAGER: Ungrabbing keyboard"
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        Atspi.Device.ungrab_keyboard(self._device)

    def process_braille_event(self, event: Atspi.Event) -> bool:
        """Processes this Braille event."""

        braille_event = input_event.BrailleEvent(event)
        result = braille_event.process()
        self._last_input_event = braille_event
        self._last_non_modifier_key_event = None
        return result

    def process_mouse_button_event(self, event: Atspi.Event) -> None:
        """Processes this Mouse event."""

        mouse_event = input_event.MouseButtonEvent(event)
        mouse_event.set_click_count(self._determine_mouse_event_click_count(mouse_event))
        self._last_input_event = mouse_event

    def process_remote_controller_event(self, event: input_event.RemoteControllerEvent) -> None:
        """Processes this RemoteController event."""

        # TODO - JD: It probably makes sense to process remote controller events here rather
        # than just updating state.
        self._last_input_event = event
        self._last_non_modifier_key_event = None

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def process_keyboard_event(
        self,
        _device: Atspi.Device,
        pressed: bool,
        keycode: int,
        keysym: int,
        modifiers: int,
        text: str
    ) -> bool:
        """Processes this Atspi keyboard event."""

        if self._paused:
            msg = "INPUT EVENT MANAGER: Keyboard event processing is paused."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        event = input_event.KeyboardEvent(pressed, keycode, keysym, modifiers, text)
        if event in [self._last_input_event, self._last_non_modifier_key_event]:
            msg = "INPUT EVENT MANAGER: Received duplicate event."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        manager = focus_manager.get_manager()
        if pressed:
            window = manager.get_active_window()
            if not AXUtilities.can_be_active_window(window):
                new_window = AXUtilities.find_active_window()
                if new_window is not None:
                    window = new_window
                    tokens = ["INPUT EVENT MANAGER: Updating window and active window to", window]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    manager.set_active_window(window)
                else:
                    # One example: Brave's popup menus live in frames which lack the active state.
                    tokens = ["WARNING:", window, "cannot be active window. No alternative found."]
                    debug.print_tokens(debug.LEVEL_WARNING, tokens, True)
            event.set_window(window)
            event.set_object(manager.get_locus_of_focus())
            event.set_script(script_manager.get_manager().get_active_script())
        elif self.last_event_was_keyboard():
            assert isinstance(self._last_input_event, input_event.KeyboardEvent)
            event.set_window(self._last_input_event.get_window())
            event.set_object(self._last_input_event.get_object())
            event.set_script(self._last_input_event.get_script())
        else:
            event.set_window(manager.get_active_window())
            event.set_object(manager.get_locus_of_focus())
            event.set_script(script_manager.get_manager().get_active_script())

        event.set_click_count(self._determine_keyboard_event_click_count(event))
        event.process()

        if event.is_modifier_key():
            if self.is_release_for(event, self._last_input_event):
                msg = "INPUT EVENT MANAGER: Clearing last non modifier key event"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self._last_non_modifier_key_event = None
        else:
            self._last_non_modifier_key_event = event
        self._last_input_event = event
        return True

    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-positional-arguments

    def _determine_keyboard_event_click_count(self, event: input_event.KeyboardEvent) -> int:
        """Determines the click count of event."""

        if not self.last_event_was_keyboard():
            return 1

        if event.is_modifier_key():
            last_event = self._last_input_event
        else:
            last_event = self._last_non_modifier_key_event or self._last_input_event

        assert isinstance(last_event, input_event.KeyboardEvent)
        if (event.time - last_event.time > settings.doubleClickTimeout) or \
           (event.keyval_name != last_event.keyval_name) or \
           (event.get_object() != last_event.get_object()):
            return 1

        last_count = last_event.get_click_count()
        if not event.is_pressed_key():
            return last_count
        if last_event.is_pressed_key():
            return last_count
        if (event.is_modifier_key() and last_count == 2) or last_count == 3:
            return 1
        return last_count + 1

    def _determine_mouse_event_click_count(self, event: input_event.MouseButtonEvent) -> int:
        """Determines the click count of event."""

        if not self.last_event_was_mouse_button():
            return 1

        assert isinstance(self._last_input_event, input_event.MouseButtonEvent)
        if not event.pressed:
            return self._last_input_event.get_click_count()
        if self._last_input_event.button != event.button:
            return 1
        if event.time - self._last_input_event.time > settings.doubleClickTimeout:
            return 1

        return self._last_input_event.get_click_count() + 1

    def last_event_was_keyboard(self) -> bool:
        """Returns True if the last event is a keyboard event."""

        return isinstance(self._last_input_event, input_event.KeyboardEvent)

    def last_event_was_mouse_button(self) -> bool:
        """Returns True if the last event is a mouse button event."""

        return isinstance(self._last_input_event, input_event.MouseButtonEvent)

    def is_release_for(self, event1, event2):
        """Returns True if event1 is a release for event2."""

        if event1 is None or event2 is None:
            return False

        if not isinstance(event1, input_event.KeyboardEvent) \
           or not isinstance(event2, input_event.KeyboardEvent):
            return False

        if event1.is_pressed_key() or not event2.is_pressed_key():
            return False

        result = event1.id == event2.id \
            and event1.hw_code == event2.hw_code \
            and event1.keyval_name == event2.keyval_name

        if result and not event1.is_modifier_key:
            result = event1.modifiers == event2.modifiers

        msg = (
            f"INPUT EVENT MANAGER: {event1.as_single_line_string()} "
            f"is release for {event2.as_single_line_string()}: {result}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def last_event_equals_or_is_release_for_event(self, event):
        """Returns True if the last event equals the provided event, or is the release for it."""

        if self._last_input_event is event:
            return True

        if not self.last_event_was_keyboard():
            return False

        if self._last_non_modifier_key_event is None:
            return False

        if event == self._last_non_modifier_key_event:
            return True

        return self.is_release_for(self._last_non_modifier_key_event, event)

    def _last_key_and_modifiers(self):
        """Returns the last keyval name and modifiers"""

        if self._last_non_modifier_key_event is None:
            return "", 0

        if not self.last_event_was_keyboard():
            return "", 0

        return self._last_non_modifier_key_event.keyval_name, self._last_input_event.modifiers

    def last_event_was_command(self):
        """Returns True if the last event is believed to be a command."""

        if bool(self._last_key_and_modifiers()[1] & 1 << Atspi.ModifierType.CONTROL):
            msg = "INPUT EVENT MANAGER: Last event was command."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def last_event_was_shortcut_for(self, obj):
        """Returns True if the last event is believed to be a shortcut key for obj."""

        string = self._last_key_and_modifiers()[0]
        if not string:
            return False

        rv = False
        keys = AXObject.get_action_key_binding(obj, 0).split(";")
        for key in keys:
            if key.endswith(string.upper()):
                rv = True
                break

        if rv:
            tokens = ["INPUT EVENT MANAGER: Last event was shortcut for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def last_event_was_printable_key(self):
        """Returns True if the last event is believed to be a printable key."""

        if not self.last_event_was_keyboard():
            return False

        if self._last_input_event.is_printable_key():
            msg = "INPUT EVENT MANAGER: Last event was printable key"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def last_event_was_caret_navigation(self):
        """Returns True if the last event is believed to be caret navigation."""

        return self.last_event_was_character_navigation() \
            or self.last_event_was_word_navigation() \
            or self.last_event_was_line_navigation() \
            or self.last_event_was_line_boundary_navigation() \
            or self.last_event_was_file_boundary_navigation() \
            or self.last_event_was_page_navigation()

    def last_event_was_caret_selection(self):
        """Returns True if the last event is believed to be caret selection."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Home", "End", "Up", "Down", "Left", "Right"]:
            rv = False
        else:
            rv = bool(mods & 1 << Atspi.ModifierType.SHIFT)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was caret selection"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_backward_caret_navigation(self):
        """Returns True if the last event is believed to be backward caret navigation."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Up", "Left"]:
            rv = False
        else:
            rv = not mods & 1 << Atspi.ModifierType.SHIFT

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was backward caret navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_forward_caret_navigation(self):
        """Returns True if the last event is believed to be forward caret navigation."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Down", "Right"]:
            rv = False
        else:
            rv = not mods & 1 << Atspi.ModifierType.SHIFT

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was forward caret navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_forward_caret_selection(self):
        """Returns True if the last event is believed to be forward caret selection."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Down", "Right"]:
            rv = False
        else:
            rv = bool(mods & 1 << Atspi.ModifierType.SHIFT)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was forward caret selection"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_character_navigation(self):
        """Returns True if the last event is believed to be character navigation."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Left", "Right"]:
            rv = False
        elif mods & 1 << Atspi.ModifierType.CONTROL or mods & 1 << Atspi.ModifierType.ALT:
            rv = False
        else:
            rv = True

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was character navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_word_navigation(self):
        """Returns True if the last event is believed to be word navigation."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Left", "Right"]:
            rv = False
        else:
            rv = bool(mods & 1 << Atspi.ModifierType.CONTROL)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was word navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_previous_word_navigation(self):
        """Returns True if the last event is believed to be previous-word navigation."""

        string, mods = self._last_key_and_modifiers()
        if string != "Left":
            rv = False
        else:
            rv = bool(mods & 1 << Atspi.ModifierType.CONTROL)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was previous-word navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_next_word_navigation(self):
        """Returns True if the last event is believed to be next-word navigation."""

        string, mods = self._last_key_and_modifiers()
        if string != "Right":
            rv = False
        else:
            rv = bool(mods & 1 << Atspi.ModifierType.CONTROL)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was next-word navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_line_navigation(self):
        """Returns True if the last event is believed to be line navigation."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Up", "Down"]:
            rv = False
        elif mods & 1 << Atspi.ModifierType.CONTROL:
            rv = False
        else:
            focus = focus_manager.get_manager().get_locus_of_focus()
            if AXUtilities.is_single_line(focus):
                rv = False
            else:
                rv = not AXUtilities.is_widget_controlled_by_line_navigation(focus)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was line navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_paragraph_navigation(self):
        """Returns True if the last event is believed to be paragraph navigation."""

        string, mods = self._last_key_and_modifiers()
        if not (string in ["Up", "Down"] and mods & 1 << Atspi.ModifierType.CONTROL):
            rv = False
        else:
            rv = not mods & 1 << Atspi.ModifierType.SHIFT

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was paragraph navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_line_boundary_navigation(self):
        """Returns True if the last event is believed to be navigation to start/end of line."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Home", "End"]:
            rv = False
        else:
            rv = not mods & 1 << Atspi.ModifierType.CONTROL

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was line boundary navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_file_boundary_navigation(self):
        """Returns True if the last event is believed to be navigation to top/bottom of file."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Home", "End"]:
            rv = False
        else:
            rv = bool(mods & 1 << Atspi.ModifierType.CONTROL)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was file boundary navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_page_navigation(self):
        """Returns True if the last event is believed to be page navigation."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Page_Up", "Page_Down"]:
            rv = False
        elif mods & 1 << Atspi.ModifierType.CONTROL:
            rv = False
        else:
            focus = focus_manager.get_manager().get_locus_of_focus()
            if AXUtilities.is_single_line(focus):
                rv = False
            else:
                rv = not AXUtilities.is_widget_controlled_by_line_navigation(focus)

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was page navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_page_switch(self):
        """Returns True if the last event is believed to be a page switch."""

        string, mods = self._last_key_and_modifiers()
        if string.isnumeric():
            rv = bool(mods & 1 << Atspi.ModifierType.ALT)
        elif string in ["Page_Up", "Page_Down"]:
            rv = bool(mods & 1 << Atspi.ModifierType.CONTROL)
        else:
            rv = False

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was page switch"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_tab_navigation(self):
        """Returns True if the last event is believed to be Tab navigation."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Tab", "ISO_Left_Tab"]:
            rv = False
        elif mods & 1 << Atspi.ModifierType.CONTROL or mods & 1 << Atspi.ModifierType.ALT:
            rv = False
        else:
            rv = True

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was Tab navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_table_sort(self):
        """Returns True if the last event is believed to be a table sort."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_table_header(focus):
            rv = False
        elif self.last_event_was_mouse_button():
            rv = self.last_event_was_primary_click()
        elif self.last_event_was_keyboard():
            rv = self.last_event_was_return_or_space()
        else:
            rv = False

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was table sort"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_unmodified_arrow(self):
        """Returns True if the last event is an unmodified arrow."""

        string, mods = self._last_key_and_modifiers()
        if string not in ["Left", "Right", "Up", "Down"]:
            return False

        if mods & 1 << Atspi.ModifierType.CONTROL \
           or mods & 1 << Atspi.ModifierType.SHIFT \
           or mods & 1 << Atspi.ModifierType.ALT:
            return False

        # TODO: JD - 8 is the value of keybindings.MODIFIER_ORCA, but we need to
        # avoid a circular import.
        if mods & 1 << 8:
            return False

        return True

    def last_event_was_alt_modified(self):
        """Returns True if the last event was alt-modified."""

        mods = self._last_key_and_modifiers()[-1]
        return mods & 1 << Atspi.ModifierType.ALT

    def last_event_was_backspace(self):
        """Returns True if the last event is BackSpace."""

        return self._last_key_and_modifiers()[0] == "BackSpace"

    def last_event_was_down(self):
        """Returns True if the last event is Down."""

        return self._last_key_and_modifiers()[0] == "Down"

    def last_event_was_f1(self):
        """Returns True if the last event is F1."""

        return self._last_key_and_modifiers()[0] == "F1"

    def last_event_was_left(self):
        """Returns True if the last event is Left."""

        return self._last_key_and_modifiers()[0] == "Left"

    def last_event_was_left_or_right(self):
        """Returns True if the last event is Left or Right."""

        return self._last_key_and_modifiers()[0] in ["Left", "Right"]

    def last_event_was_page_up_or_page_down(self):
        """Returns True if the last event is Page_Up or Page_Down."""

        return self._last_key_and_modifiers()[0] in ["Page_Up", "Page_Down"]

    def last_event_was_right(self):
        """Returns True if the last event is Right."""

        return self._last_key_and_modifiers()[0] == "Right"

    def last_event_was_return(self):
        """Returns True if the last event is Return."""

        return self._last_key_and_modifiers()[0] == "Return"

    def last_event_was_return_or_space(self):
        """Returns True if the last event is Return or space."""

        return self._last_key_and_modifiers()[0] in ["Return", "space", " "]

    def last_event_was_return_tab_or_space(self):
        """Returns True if the last event is Return, Tab, or space."""

        return self._last_key_and_modifiers()[0] in ["Return", "Tab", "space", " "]

    def last_event_was_space(self):
        """Returns True if the last event is space."""

        return self._last_key_and_modifiers()[0] in [" ", "space"]

    def last_event_was_tab(self):
        """Returns True if the last event is Tab."""

        return self._last_key_and_modifiers()[0] == "Tab"

    def last_event_was_up(self):
        """Returns True if the last event is Up."""

        return self._last_key_and_modifiers()[0] == "Up"

    def last_event_was_up_or_down(self):
        """Returns True if the last event is Up or Down."""

        return self._last_key_and_modifiers()[0] in ["Up", "Down"]

    def last_event_was_delete(self):
        """Returns True if the last event is believed to be delete."""

        string, mods = self._last_key_and_modifiers()
        if string in ["Delete", "KP_Delete"]:
            rv = True
        elif string.lower() == "d":
            rv = bool(mods & 1 << Atspi.ModifierType.CONTROL)
        else:
            rv = False

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was delete"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_cut(self):
        """Returns True if the last event is believed to be the cut command."""

        string, mods = self._last_key_and_modifiers()
        if string.lower() != "x":
            return False

        if mods & 1 << Atspi.ModifierType.CONTROL and not mods & 1 << Atspi.ModifierType.SHIFT:
            msg = "INPUT EVENT MANAGER: Last event was cut"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_copy(self):
        """Returns True if the last event is believed to be the copy command."""

        string, mods = self._last_key_and_modifiers()
        if string.lower() != "c" or not mods & 1 << Atspi.ModifierType.CONTROL:
            rv = False
        elif AXUtilities.is_terminal(self._last_input_event.get_object()):
            rv = mods & 1 << Atspi.ModifierType.SHIFT
        else:
            rv = not mods & 1 << Atspi.ModifierType.SHIFT

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was copy"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_paste(self):
        """Returns True if the last event is believed to be the paste command."""

        string, mods = self._last_key_and_modifiers()
        if string.lower() != "v" or not mods & 1 << Atspi.ModifierType.CONTROL:
            rv = False
        elif AXUtilities.is_terminal(self._last_input_event.get_object()):
            rv = mods & 1 << Atspi.ModifierType.SHIFT
        else:
            rv = not mods & 1 << Atspi.ModifierType.SHIFT

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was paste"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_undo(self):
        """Returns True if the last event is believed to be the undo command."""

        string, mods = self._last_key_and_modifiers()
        if string.lower() != "z":
            return False
        if mods & 1 << Atspi.ModifierType.CONTROL and not mods & 1 << Atspi.ModifierType.SHIFT:
            msg = "INPUT EVENT MANAGER: Last event was undo"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_redo(self):
        """Returns True if the last event is believed to be the redo command."""

        string, mods = self._last_key_and_modifiers()
        if string.lower() == "z":
            rv = mods & 1 << Atspi.ModifierType.CONTROL and mods & 1 << Atspi.ModifierType.SHIFT
        elif string.lower() == "y":
            # LibreOffice
            rv = mods & 1 << Atspi.ModifierType.CONTROL \
                and not mods & 1 << Atspi.ModifierType.SHIFT
        else:
            rv = False

        if rv:
            msg = "INPUT EVENT MANAGER: Last event was redo"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def last_event_was_select_all(self):
        """Returns True if the last event is believed to be the select all command."""

        string, mods = self._last_key_and_modifiers()
        if string.lower() != "a":
            return False

        if (mods & 1 << Atspi.ModifierType.CONTROL and not mods & 1 << Atspi.ModifierType.SHIFT):
            msg = "INPUT EVENT MANAGER: Last event was select all"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_primary_click(self):
        """Returns True if the last event is a primary mouse click."""

        if not self.last_event_was_mouse_button():
            return False

        if self._last_input_event.button == "1" and self._last_input_event.pressed:
            msg = "INPUT EVENT MANAGER: Last event was primary click"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_primary_release(self):
        """Returns True if the last event is a primary mouse release."""

        if not self.last_event_was_mouse_button():
            return False

        if self._last_input_event.button == "1" and not self._last_input_event.pressed:
            msg = "INPUT EVENT MANAGER: Last event was primary release"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_primary_click_or_release(self):
        """Returns True if the last event is a primary mouse click or release."""

        if not self.last_event_was_mouse_button():
            return False

        if self._last_input_event.button == "1":
            msg = "INPUT EVENT MANAGER: Last event was primary click or release"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_middle_click(self):
        """Returns True if the last event is a middle mouse click."""

        if not self.last_event_was_mouse_button():
            return False

        if self._last_input_event.button == "2" and self._last_input_event.pressed:
            msg = "INPUT EVENT MANAGER: Last event was middle click"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_middle_release(self):
        """Returns True if the last event is a middle mouse release."""

        if not self.last_event_was_mouse_button():
            return False

        if self._last_input_event.button == "2" and not self._last_input_event.pressed:
            msg = "INPUT EVENT MANAGER: Last event was middle release"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_secondary_click(self):
        """Returns True if the last event is a secondary mouse click."""

        if not self.last_event_was_mouse_button():
            return False

        if self._last_input_event.button == "3" and self._last_input_event.pressed:
            msg = "INPUT EVENT MANAGER: Last event was secondary click"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False

    def last_event_was_secondary_release(self):
        """Returns True if the last event is a secondary mouse release."""

        if not self.last_event_was_mouse_button():
            return False

        if self._last_input_event.button == "3" and not self._last_input_event.pressed:
            msg = "INPUT EVENT MANAGER: Last event was secondary release"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        return False


_manager = InputEventManager()
def get_manager():
    """Returns the Input Event Manager singleton."""
    return _manager
