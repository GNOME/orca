# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""A dictionary that maps key events into localized descriptions."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from .orca_i18n import _, C_ # pylint: disable=import-error

# Contains keyboard-label:presentable-name pairs
_keynames: dict[str, str] = {}

# Translators: this is how someone would speak the name of the shift key
_keynames["Shift"] = C_("keyboard", "Shift")

# Translators: this is how someone would speak the name of the alt key
_keynames["Alt"] = C_("keyboard", "Alt")

# Translators: this is how someone would speak the name of the control key
_keynames["Control"] = C_("keyboard", "Control")

# Translators: this is how someone would speak the name of the left shift key
_keynames["Shift_L"] = _("left shift")

# Translators: this is how someone would speak the name of the left alt key
_keynames["Alt_L"] = _("left alt")

# Translators: this is how someone would speak the name of the left ctrl key
_keynames["Control_L"] = _("left control")

# Translators: this is how someone would speak the name of the right shift key
_keynames["Shift_R"] = _("right shift")

# Translators: this is how someone would speak the name of the right alt key
_keynames["Alt_R"] = _("right alt")

# Translators: this is how someone would speak the name of the right ctrl key
_keynames["Control_R"] = _("right control")

# Translators: this is how someone would speak the name of the left meta key
_keynames["Meta_L"] = _("left meta")

# Translators: this is how someone would speak the name of the right meta key
_keynames["Meta_R"] = _("right meta")

# Translators: this is how someone would speak the name of the num lock key
_keynames["Num_Lock"] = _("num lock")

# Translators: this is how someone would speak the name of the caps lock key
_keynames["Caps_Lock"] = _("caps lock")

# Translators: this is how someone would speak the name of the shift lock key
# There is no reason to make it different from the translation for "caps lock"
_keynames["Shift_Lock"] = _("shift lock")

# Translators: this is how someone would speak the name of the scroll lock key
_keynames["Scroll_Lock"] = _("scroll lock")

# Translators: this is how someone would speak the name of the page up key
_keynames["Page_Up"] = _("page up")

# Translators: this is how someone would speak the name of the page up key
_keynames["KP_Page_Up"] = _("page up")

# Translators: this is how someone would speak the name of the page up key
_keynames["Prior"] = _("page up")

# Translators: this is how someone would speak the name of the page up key
_keynames["KP_Prior"] = _("page up")

# Translators: this is how someone would speak the name of the page down key
_keynames["Page_Down"] = _("page down")

# Translators: this is how someone would speak the name of the page down key
_keynames["KP_Page_Down"] = _("page down")

# Translators: this is how someone would speak the name of the page down key
_keynames["Next"] = _("page down")

# Translators: this is how someone would speak the name of the page down key
_keynames["KP_Next"] = _("page down")

# Translators: this is how someone would speak the name of the tab key
_keynames["Tab"] = _("tab")

# Translators: this is how someone would speak the name of the left tab key
_keynames["ISO_Left_Tab"] = _("left tab")

# Translators: this is the spoken word for the space character
_keynames["space"] = _("space")

# Translators: this is how someone would speak the name of the backspace key
_keynames["BackSpace"] = _("backspace")

# Translators: this is how someone would speak the name of the return key
_keynames["Return"] = _("return")

# Translators: this is how someone would speak the name of the enter key
_keynames["KP_Enter"] = _("enter")

# Translators: this is how someone would speak the name of the up arrow key
_keynames["Up"] = _("up")

# Translators: this is how someone would speak the name of the up arrow key
_keynames["KP_Up"] = _("up")

# Translators: this is how someone would speak the name of the down arrow key
_keynames["Down"] = _("down")

# Translators: this is how someone would speak the name of the down arrow key
_keynames["KP_Down"] = _("down")

# Translators: this is how someone would speak the name of the left arrow key
_keynames["Left"] = _("left")

# Translators: this is how someone would speak the name of the left arrow key
_keynames["KP_Left"] = _("left")

# Translators: this is how someone would speak the name of the right arrow key
_keynames["Right"] = _("right")

# Translators: this is how someone would speak the name of the right arrow key
_keynames["KP_Right"] = _("right")

# Translators: this is how someone would speak the name of the left super key
_keynames["Super_L"] = _("left super")

# Translators: this is how someone would speak the name of the right super key
_keynames["Super_R"] = _("right super")

# Translators: this is how someone would speak the name of the menu key
_keynames["Menu"] = _("menu")

# Translators: this is how someone would speak the name of the ISO shift key
_keynames["ISO_Level3_Shift"] = _("Alt Gr")

# Translators: this is how someone would speak the name of the help key
_keynames["Help"] = _("help")

# Translators: this is how someone would speak the name of the multi key
_keynames["Multi_key"] = _("multi")

# Translators: this is how someone would speak the name of the mode switch key
_keynames["Mode_switch"] = _("mode switch")

# Translators: this is how someone would speak the name of the escape key
_keynames["Escape"] = _("escape")

# Translators: this is how someone would speak the name of the insert key
_keynames["Insert"] = _("insert")

# Translators: this is how someone would speak the name of the insert key
_keynames["KP_Insert"] = _("insert")

# Translators: this is how someone would speak the name of the delete key
_keynames["Delete"] = _("delete")

# Translators: this is how someone would speak the name of the delete key
_keynames["KP_Delete"] = _("delete")

# Translators: this is how someone would speak the name of the home key
_keynames["Home"] = _("home")

# Translators: this is how someone would speak the name of the home key
_keynames["KP_Home"] = _("home")

# Translators: this is how someone would speak the name of the end key
_keynames["End"] = _("end")

# Translators: this is how someone would speak the name of the end key
_keynames["KP_End"] = _("end")

# Translators: this is how someone would speak the name of the begin key
_keynames["KP_Begin"] = _("begin")

# Translators: this is how someone would speak the name of the  non-spacing
# diacritical key for the grave glyph
_keynames["dead_grave"] = _("grave")

# Translators: this is how someone would speak the name of the non-spacing
# diacritical key for the acute glyph
_keynames["dead_acute"] = _("acute")

# Translators: this is how someone would speak the name of the non-spacing
# diacritical key for the circumflex glyph
_keynames["dead_circumflex"] = _("circumflex")

# Translators: this is how someone would speak the name of the non-spacing
# diacritical key for the tilde glyph
_keynames["dead_tilde"] = _("tilde")

# Translators: this is how someone would speak the name of the non-spacing
# diacritical key for the diaeresis glyph
_keynames["dead_diaeresis"] = _("diaeresis")

# Translators: this is how someone would speak the name of the non-spacing
# diacritical key for the ring glyph
_keynames["dead_abovering"] = _("ring")

# Translators: this is how someone would speak the name of the non-spacing
# diacritical key for the cedilla glyph
_keynames["dead_cedilla"] = _("cedilla")

# Translators: this is how someone would speak the name of the non-spacing
# diacritical key for the stroke glyph
_keynames["dead_stroke"] = _("stroke")

# Translators: this is how someone would speak the name of the minus key
_keynames["minus"] = _("minus")

# Translators: this is how someone would speak the name of the plus key
_keynames["plus"] = _("plus")


def get_key_name(key: str) -> str | None:
    """Return the localized name for the key."""

    return _keynames.get(key)

def localize_key_sequence(keys: str) -> str:
    """Localizes key sequences such as 'Shift Control A'."""

    key_list = keys.split()
    for key in key_list:
        key_name = get_key_name(key) or key
        keys = keys.replace(key, key_name)

    return keys
