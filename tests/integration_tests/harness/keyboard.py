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

"""Key-synthesis helpers for native-app integration tests."""

import gi

gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi, Gdk

KEYSYM_A, KEYSYM_B, KEYSYM_C, KEYSYM_D, KEYSYM_E, KEYSYM_F, KEYSYM_G = (ord(c) for c in "abcdefg")
KEYSYM_H, KEYSYM_I, KEYSYM_J, KEYSYM_K, KEYSYM_L, KEYSYM_M, KEYSYM_N = (ord(c) for c in "hijklmn")
KEYSYM_O, KEYSYM_P, KEYSYM_Q, KEYSYM_R, KEYSYM_S, KEYSYM_T, KEYSYM_U = (ord(c) for c in "opqrstu")
KEYSYM_V, KEYSYM_W, KEYSYM_X, KEYSYM_Y, KEYSYM_Z = (ord(c) for c in "vwxyz")

KEYSYM_0, KEYSYM_1, KEYSYM_2, KEYSYM_3, KEYSYM_4 = (ord(c) for c in "01234")
KEYSYM_5, KEYSYM_6, KEYSYM_7, KEYSYM_8, KEYSYM_9 = (ord(c) for c in "56789")

# Non-printable keysyms from <X11/keysymdef.h>.
KEYSYM_SPACE = 0x0020
KEYSYM_RETURN = 0xFF0D
KEYSYM_ESCAPE = 0xFF1B
KEYSYM_BACKSPACE = 0xFF08
KEYSYM_TAB = 0xFF09
KEYSYM_DELETE = 0xFFFF
KEYSYM_INSERT = 0xFF63
KEYSYM_HOME = 0xFF50
KEYSYM_END = 0xFF57
KEYSYM_LEFT = 0xFF51
KEYSYM_RIGHT = 0xFF53
KEYSYM_UP = 0xFF52
KEYSYM_DOWN = 0xFF54
KEYSYM_PAGE_UP = 0xFF55
KEYSYM_PAGE_DOWN = 0xFF56
KEYSYM_KP_INSERT = 0xFF9E
KEYSYM_SHIFT_L = 0xFFE1
KEYSYM_SHIFT_R = 0xFFE2
KEYSYM_CONTROL_L = 0xFFE3
KEYSYM_CONTROL_R = 0xFFE4
KEYSYM_CAPS_LOCK = 0xFFE5
KEYSYM_SHIFT_LOCK = 0xFFE6
KEYSYM_META_L = 0xFFE7
KEYSYM_META_R = 0xFFE8
KEYSYM_ALT_L = 0xFFE9
KEYSYM_ALT_R = 0xFFEA
KEYSYM_SUPER_L = 0xFFEB
KEYSYM_SUPER_R = 0xFFEC
KEYSYM_F1 = 0xFFBE
KEYSYM_F2 = 0xFFBF
KEYSYM_F3 = 0xFFC0
KEYSYM_F4 = 0xFFC1
KEYSYM_F5 = 0xFFC2
KEYSYM_F6 = 0xFFC3
KEYSYM_F7 = 0xFFC4
KEYSYM_F8 = 0xFFC5
KEYSYM_F9 = 0xFFC6
KEYSYM_F10 = 0xFFC7
KEYSYM_F11 = 0xFFC8
KEYSYM_F12 = 0xFFC9


def press_key(keysym: int) -> None:
    """Synthesizes a key-down event for keysym."""

    Atspi.generate_keyboard_event(_keycode_for_keysym(keysym), None, Atspi.KeySynthType.PRESS)


def release_key(keysym: int) -> None:
    """Synthesizes a key-up event for keysym."""

    Atspi.generate_keyboard_event(_keycode_for_keysym(keysym), None, Atspi.KeySynthType.RELEASE)


def tap_key(keysym: int) -> None:
    """Presses and releases a single keysym."""

    press_key(keysym)
    release_key(keysym)


def press_chord(modifiers: list[int], keysym: int) -> None:
    """Holds modifiers, taps keysym, releases the modifiers in reverse order."""

    pressed: list[int] = []
    try:
        for modifier in modifiers:
            press_key(modifier)
            pressed.append(modifier)
        press_key(keysym)
        release_key(keysym)
    finally:
        for modifier in reversed(pressed):
            release_key(modifier)


def _keycode_for_keysym(keysym: int) -> int:
    """Returns the first X keycode whose keymap entry produces keysym."""

    keymap = Gdk.Keymap.get_default()
    found, keys = keymap.get_entries_for_keyval(keysym)
    if not found or not keys:
        raise RuntimeError(f"No keycode found for keysym {keysym:#x}")
    return keys[0].keycode
