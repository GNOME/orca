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

"""Exposes a dictionary, keynames, that maps key events
into localized words."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc."
__license__   = "LGPL"


from .orca_i18n import _
from .orca_i18n import C_

# __keynames is a dictionary where the keys represent a UTF-8
# string for a keyboard key and the values represent the common
# phrase used to describe the key.
#
__keynames = {}

# Translators: this is how someone would speak the name of the shift key
#
__keynames["Shift"]        = C_("keyboard", "Shift")

# Translators: this is how someone would speak the name of the alt key
#
__keynames["Alt"]          = C_("keyboard", "Alt")

# Translators: this is how someone would speak the name of the control key
#
__keynames["Control"]      = C_("keyboard", "Control")

# Translators: this is how someone would speak the name of the left shift key
#
__keynames["Shift_L"]      = _("left shift")

# Translators: this is how someone would speak the name of the left alt key
#
__keynames["Alt_L"]        = _("left alt")

# Translators: this is how someone would speak the name of the left ctrl key
#
__keynames["Control_L"]    = _("left control")

# Translators: this is how someone would speak the name of the right shift key
#
__keynames["Shift_R"]      = _("right shift")

# Translators: this is how someone would speak the name of the right alt key
#
__keynames["Alt_R"]        = _("right alt")

# Translators: this is how someone would speak the name of the right ctrl key
#
__keynames["Control_R"]    = _("right control")

# Translators: this is how someone would speak the name of the left meta key
#
__keynames["Meta_L"]       = _("left meta")

# Translators: this is how someone would speak the name of the right meta key
#
__keynames["Meta_R"]       = _("right meta")

# Translators: this is how someone would speak the name of the num lock key
#
__keynames["Num_Lock"]     = _("num lock")

# Translators: this is how someone would speak the name of the caps lock key
#
__keynames["Caps_Lock"]    = _("caps lock")

# Translators: this is how someone would speak the name of the shift lock key
# There is no reason to make it different from the translation for "caps lock"
#
__keynames["Shift_Lock"]    = _("shift lock")

# Translators: this is how someone would speak the name of the scroll lock key
#
__keynames["Scroll_Lock"]  = _("scroll lock")

# Translators: this is how someone would speak the name of the page up key
#
__keynames["Page_Up"]      = _("page up")

# Translators: this is how someone would speak the name of the page up key
#
__keynames["KP_Page_Up"]      = _("page up")

# Translators: this is how someone would speak the name of the page up key
#
__keynames["Prior"]      = _("page up")

# Translators: this is how someone would speak the name of the page up key
#
__keynames["KP_Prior"]      = _("page up")

# Translators: this is how someone would speak the name of the page down key
#
__keynames["Page_Down"]    = _("page down")

# Translators: this is how someone would speak the name of the page down key
#
__keynames["KP_Page_Down"]    = _("page down")

# Translators: this is how someone would speak the name of the page down key
#
__keynames["Next"]    = _("page down")

# Translators: this is how someone would speak the name of the page down key
#
__keynames["KP_Next"]    = _("page down")

# Translators: this is how someone would speak the name of the tab key
#
__keynames["Tab"] = _("tab")

# Translators: this is how someone would speak the name of the left tab key
#
__keynames["ISO_Left_Tab"] = _("left tab")

# Translators: this is the spoken word for the space character
#
__keynames["space"] = _("space")

# Translators: this is how someone would speak the name of the backspace key
#
__keynames["BackSpace"] = _("backspace")

# Translators: this is how someone would speak the name of the return key
#
__keynames["Return"] = _("return")

# Translators: this is how someone would speak the name of the enter key
#
__keynames["KP_Enter"] = _("enter")

# Translators: this is how someone would speak the name of the up arrow key
#
__keynames["Up"] = _("up")

# Translators: this is how someone would speak the name of the up arrow key
#
__keynames["KP_Up"] = _("up")

# Translators: this is how someone would speak the name of the down arrow key
#
__keynames["Down"] = _("down")

# Translators: this is how someone would speak the name of the down arrow key
#
__keynames["KP_Down"] = _("down")

# Translators: this is how someone would speak the name of the left arrow key
#
__keynames["Left"] = _("left")

# Translators: this is how someone would speak the name of the left arrow key
#
__keynames["KP_Left"] = _("left")

# Translators: this is how someone would speak the name of the right arrow key
#
__keynames["Right"] = _("right")

# Translators: this is how someone would speak the name of the right arrow key
#
__keynames["KP_Right"] = _("right")

# Translators: this is how someone would speak the name of the left super key
#
__keynames["Super_L"] = _("left super")

# Translators: this is how someone would speak the name of the right super key
#
__keynames["Super_R"] = _("right super")

# Translators: this is how someone would speak the name of the menu key
#
__keynames["Menu"] = _("menu")

# Translators: this is how someone would speak the name of the ISO shift key
#
__keynames["ISO_Level3_Shift"] = _("Alt Gr")

# Translators: this is how someone would speak the name of the help key
#
__keynames["Help"] = _("help")

# Translators: this is how someone would speak the name of the multi key
#
__keynames["Multi_key"] = _("multi")

# Translators: this is how someone would speak the name of the mode switch key
#
__keynames["Mode_switch"] = _("mode switch")

# Translators: this is how someone would speak the name of the escape key
#
__keynames["Escape"] = _("escape")

# Translators: this is how someone would speak the name of the insert key
#
__keynames["Insert"] = _("insert")

# Translators: this is how someone would speak the name of the insert key
#
__keynames["KP_Insert"] = _("insert")

# Translators: this is how someone would speak the name of the delete key
#
__keynames["Delete"] = _("delete")

# Translators: this is how someone would speak the name of the delete key
#
__keynames["KP_Delete"] = _("delete")

# Translators: this is how someone would speak the name of the home key
#
__keynames["Home"] = _("home")

# Translators: this is how someone would speak the name of the home key
#
__keynames["KP_Home"] = _("home")

# Translators: this is how someone would speak the name of the end key
#
__keynames["End"] = _("end")

# Translators: this is how someone would speak the name of the end key
#
__keynames["KP_End"] = _("end")

# Translators: this is how someone would speak the name of the begin key
#
__keynames["KP_Begin"] = _("begin")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the grave glyph
#
__keynames["dead_grave"] = _("grave")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the acute glyph
#
__keynames["dead_acute"] = _("acute")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the circumflex glyph
#
__keynames["dead_circumflex"] = _("circumflex")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the tilde glyph
#
__keynames["dead_tilde"] = _("tilde")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the diaeresis glyph
#
__keynames["dead_diaeresis"] = _("diaeresis")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the ring glyph
#
__keynames["dead_abovering"] = _("ring")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the cedilla glyph
#
__keynames["dead_cedilla"] = _("cedilla")

# Translators: this is how someone would speak the name of the
# non-spacing diacritical key for the stroke glyph
#
__keynames["dead_stroke"] = _("stroke")

# Translators: this is how someone would speak the name of the minus key
#
__keynames["minus"]      = _("minus")

# Translators: this is how someone would speak the name of the plus key
#
__keynames["plus"]      = _("plus")


def get_key_name(key: str) -> str | None:
    """Return the localized name for the key."""

    return __keynames.get(key)

def localizeKeySequence(keys):
    """Given a sequence of keys, such as 'Shift Control A', localize the
    full sequence.

    Arguments:
    - keys: the key sequence to localize

    Returns a string representing the localized version to present to the
    user
    """

    keyList = keys.split()
    for key in keyList:
        keyName = get_key_name(key) or key
        keys = keys.replace(key, keyName)

    return keys
