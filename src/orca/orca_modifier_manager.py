# Orca
#
# Copyright 2023 Igalia, S.L.
# Copyright 2023 GNOME Foundation Inc.
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
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches

"""Manages the Orca modifier key."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L." \
                "Copyright (c) 2023 GNOME Foundation Inc."
__license__   = "LGPL"

import os
import re
import subprocess
from typing import TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi
from gi.repository import GLib
from gi.repository import Gdk

from . import debug
from . import keybindings
from . import input_event_manager
from . import settings_manager

if TYPE_CHECKING:
    from .input_event import KeyboardEvent

class OrcaModifierManager:
    """Manages the Orca modifier."""

    def __init__(self) -> None:
        self._grabbed_modifiers: dict = {}
        self._is_pressed: bool = False

        # Related to hacks which will soon die.
        self._original_xmodmap: bytes = b""
        self._caps_lock_cleared: bool = False
        self._need_to_restore_orca_modifier: bool = False

        # Event handlers for input devices being plugged in/unplugged.
        display = Gdk.Display.get_default()
        if display is not None:
            device_manager = display.get_device_manager()
            device_manager.connect("device-added", self._on_device_changed)
            device_manager.connect("device-removed", self._on_device_changed)
        else:
            msg = "ORCA MODIFIER MANAGER: Cannot listen for input device changes."
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def _on_device_changed(self, _device_manager, device: Gdk.Device) -> None:
        """Handles device-* signals."""

        source = device.get_source()
        tokens = ["ORCA MODIFIER MANAGER: Device changed", source]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if source == Gdk.InputSource.KEYBOARD:
            self.refresh_orca_modifiers("Keyboard change detected.")

    def is_orca_modifier(self, modifier: str) -> bool:
        """Returns True if modifier is one of the user's Orca modifier keys."""

        if modifier not in settings_manager.get_manager().get_setting("orcaModifierKeys"):
            return False

        if modifier in ["Insert", "KP_Insert"]:
            return self.is_modifier_grabbed(modifier)

        return True

    def get_pressed_state(self) -> bool:
        """Returns True if the Orca modifier has been pressed but not yet released."""

        return self._is_pressed

    def set_pressed_state(self, is_pressed: bool) -> None:
        """Updates the pressed state of the modifier based on event."""

        msg = f"ORCA MODIFIER MANAGER: Setting pressed state to {is_pressed}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._is_pressed = is_pressed

    def is_modifier_grabbed(self, modifier: str) -> bool:
        """Returns True if there is an existing grab for modifier."""

        return modifier in self._grabbed_modifiers

    def add_grabs_for_orca_modifiers(self) -> None:
        """Adds grabs for all of the user's Orca modifier keys."""

        for modifier in settings_manager.get_manager().get_setting("orcaModifierKeys"):
            # TODO - JD: We currently handle CapsLock one way and Insert a different way.
            # Ideally that will stop being the case at some point.
            if modifier in ["Insert", "KP_Insert"]:
                self.add_modifier_grab(modifier)

    def remove_grabs_for_orca_modifiers(self) -> None:
        """Removes grabs for all of the user's Orca modifier keys."""

        for modifier in settings_manager.get_manager().get_setting("orcaModifierKeys"):
            # TODO - JD: We currently handle CapsLock one way and Insert a different way.
            # Ideally that will stop being the case at some point.
            if modifier in ["Insert", "KP_Insert"]:
                self.remove_modifier_grab(modifier)

        msg = "ORCA MODIFIER MANAGER: Setting pressed state to False for grab removal"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._is_pressed = False

    def add_modifier_grab(self, modifier: str) -> None:
        """Adds a grab for modifier."""

        if modifier in self._grabbed_modifiers:
            return

        keyval, keycode = keybindings.get_keycodes(modifier)
        grab_id = input_event_manager.get_manager().add_grab_for_modifier(modifier, keyval, keycode)
        if grab_id != -1:
            self._grabbed_modifiers[modifier] = grab_id

    def remove_modifier_grab(self, modifier: str) -> None:
        """Removes the grab for modifier."""

        grab_id = self._grabbed_modifiers.get(modifier)
        if grab_id is None:
            return

        input_event_manager.get_manager().remove_grab_for_modifier(modifier, grab_id)
        del self._grabbed_modifiers[modifier]

    def toggle_modifier(self, keyboard_event: KeyboardEvent) -> None:
        """Toggles the modifier to enable double-clicking causing normal behavior."""

        if keyboard_event.keyval_name in ["Caps_Lock", "Shift_Lock"]:
            self._toggle_modifier_lock(keyboard_event)
            return

        self._toggle_modifier_grab(keyboard_event)

    def _toggle_modifier_grab(self, keyboard_event: KeyboardEvent) -> None:
        """Toggles the grab for a modifier to enable double-clicking causing normal behavior."""

        # Because we will synthesize another press and release, wait until the real release.
        if keyboard_event.is_pressed_key():
            return

        def toggle(hw_code):
            Atspi.generate_keyboard_event(hw_code, "", Atspi.KeySynthType.PRESSRELEASE)
            return False

        def restore_grab(modifier):
            self.add_modifier_grab(modifier)
            return False

        msg = "ORCA MODIFIER MANAGER: Removing grab pre-toggle"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.remove_modifier_grab(keyboard_event.keyval_name)

        msg = f"ORCA MODIFIER MANAGER: Scheduling toggle of {keyboard_event.keyval_name}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        GLib.timeout_add(1, toggle, keyboard_event.hw_code)

        msg = "ORCA MODIFIER MANAGER: Scheduling re-adding grab post-toggle"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        GLib.timeout_add(500, restore_grab, keyboard_event.keyval_name)

    def _toggle_modifier_lock(self, keyboard_event: KeyboardEvent) -> None:
        """Toggles the lock for a modifier to enable double-clicking causing normal behavior."""

        if not keyboard_event.is_pressed_key():
            return

        def toggle(modifiers, modifier):
            if modifiers & modifier:
                lock = Atspi.KeySynthType.UNLOCKMODIFIERS
                msg = "ORCA MODIFIER MANAGER: Unlocking CapsLock"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            else:
                lock = Atspi.KeySynthType.LOCKMODIFIERS
                msg = "ORCA MODIFIER MANAGER: Locking CapsLock"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            Atspi.generate_keyboard_event(modifier, "", lock)

        if keyboard_event.keyval_name == "Caps_Lock":
            modifier = 1 << Atspi.ModifierType.SHIFTLOCK
        elif keyboard_event.keyval_name == "Shift_Lock":
            modifier = 1 << Atspi.ModifierType.SHIFT
        else:
            return

        msg = "ORCA MODIFIER MANAGER: Scheduling lock change"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        GLib.timeout_add(1, toggle, keyboard_event.modifiers, modifier)

    def refresh_orca_modifiers(self, reason: str = "") -> None:
        """Refreshes the Orca modifier keys."""

        msg = "ORCA MODIFIER MANAGER: Refreshing Orca modifiers"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.unset_orca_modifiers(reason)
        with subprocess.Popen(["xkbcomp", os.environ["DISPLAY"], "-"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as p:
            self._original_xmodmap, _ = p.communicate()
        self._create_orca_xmodmap()

    def _create_orca_xmodmap(self) -> None:
        """Makes an Orca-specific Xmodmap so that the Orca modifier works."""

        msg = "ORCA MODIFIER MANAGER: Creating Orca xmodmap"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if self.is_orca_modifier("Caps_Lock") or self.is_orca_modifier("Shift_Lock"):
            self.set_caps_lock_as_orca_modifier(True)
            self._caps_lock_cleared = True
        elif self._caps_lock_cleared:
            self.set_caps_lock_as_orca_modifier(False)
            self._caps_lock_cleared = False

    def unset_orca_modifiers(self, reason: str = "") -> None:
        """Turns the Orca modifiers back into their original purpose."""

        msg = "ORCA MODIFIER MANAGER: Attempting to restore original xmodmap"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not self._original_xmodmap:
            msg = "ORCA MODIFIER MANAGER: No stored xmodmap found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._caps_lock_cleared = False
        with subprocess.Popen(["xkbcomp", "-w0", "-", os.environ["DISPLAY"]],
                              stdin=subprocess.PIPE, stdout=None, stderr=None) as p:
            p.communicate(self._original_xmodmap)

        msg = "ORCA MODIFIER MANAGER: Original xmodmap restored"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_caps_lock_as_orca_modifier(self, enable: bool) -> None:
        """Enable or disable use of the caps lock key as an Orca modifier key."""

        msg = "ORCA MODIFIER MANAGER: Setting caps lock as the Orca modifier"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        interpret_caps_line_prog = re.compile(
            r'^\s*interpret\s+Caps[_+]Lock[_+]AnyOfOrNone\s*\(all\)\s*{\s*$', re.I)
        normal_caps_line_prog = re.compile(
            r'^\s*action\s*=\s*LockMods\s*\(\s*modifiers\s*=\s*Lock\s*\)\s*;\s*$', re.I)
        interpret_shift_line_prog = re.compile(
            r'^\s*interpret\s+Shift[_+]Lock[_+]AnyOf\s*\(\s*Shift\s*\+\s*Lock\s*\)\s*{\s*$', re.I)
        normal_shift_line_prog = re.compile(
            r'^\s*action\s*=\s*LockMods\s*\(\s*modifiers\s*=\s*Shift\s*\)\s*;\s*$', re.I)
        disabled_mod_line_prog = re.compile(
            r'^\s*action\s*=\s*NoAction\s*\(\s*\)\s*;\s*$', re.I)
        normal_caps_line = '        action= LockMods(modifiers=Lock);'
        normal_shift_line = '        action= LockMods(modifiers=Shift);'
        disabled_mod_line = '        action= NoAction();'
        lines = self._original_xmodmap.decode('UTF-8').split('\n')
        found_caps_interpret_section = False
        found_shift_interpret_section = False
        modified = False
        for i, line in enumerate(lines):
            if not found_caps_interpret_section and not found_shift_interpret_section:
                if interpret_caps_line_prog.match(line):
                    found_caps_interpret_section = True
                elif interpret_shift_line_prog.match(line):
                    found_shift_interpret_section = True
            elif found_caps_interpret_section:
                if enable:
                    if normal_caps_line_prog.match(line):
                        lines[i] = disabled_mod_line
                        modified = True
                else:
                    if disabled_mod_line_prog.match(line):
                        lines[i] = normal_caps_line
                        modified = True
                if line.find('}'):
                    found_caps_interpret_section = False
            elif found_shift_interpret_section:
                if enable:
                    if normal_shift_line_prog.match(line):
                        lines[i] = disabled_mod_line
                        modified = True
                else:
                    if disabled_mod_line_prog.match(line):
                        lines[i] = normal_shift_line
                        modified = True
                if line.find('}'):
                    found_shift_interpret_section = False
        if modified:
            msg = "ORCA MODIFIER MANAGER: Updating xmodmap"
            debug.print_message(debug.LEVEL_INFO, msg, True)


            with subprocess.Popen(["xkbcomp", "-w0", "-", os.environ["DISPLAY"]],
                              stdin=subprocess.PIPE, stdout=None, stderr=None) as p:
                p.communicate(bytes('\n'.join(lines), 'UTF-8'))
        else:
            msg = "ORCA MODIFIER MANAGER: Not updating xmodmap"
            debug.print_message(debug.LEVEL_INFO, msg, True)


_manager: OrcaModifierManager = OrcaModifierManager()

def get_manager() -> OrcaModifierManager:
    """Returns the OrcaModifierManager singleton."""

    return _manager
