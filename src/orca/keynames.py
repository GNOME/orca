# Orca
#
# Copyright 2006-2007 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Exposes a dictionary, keynames, that maps key events
into localized words."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import chnames

from orca_i18n import _ # for gettext support

# __keynames is a dictionary where the keys represent a UTF-8
# string for a keyboard key and the values represent the common
# phrase used to describe the key.
#
__keynames = {}

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

# Translators: this is how someone would speak the name of the scroll lock key
#
__keynames["Scroll_Lock"]  = _("scroll lock")

# Translators: this is how someone would speak the name of the page up key
#
__keynames["Page_Up"]      = _("page up")

# Translators: this is how someone would speak the name of the page down key
#
__keynames["Page_Down"]    = _("page down")

# Translators: this is how someone would speak the name of the left tab key
#
__keynames["ISO_Left_Tab"] = _("left tab")

# Translators: this is how someone would speak the name of the F11 key
#
__keynames["SunF36"]       = _("F 11")

# Translators: this is how someone would speak the name of the F12 key
#
__keynames["SunF37"]       = _("F 12")

# Translators: this is the spoken word for the space character
#
__keynames["space"] = _("space")

def getKeyName(key):
    """Given a keyboard key, return its name as people might refer to it
    in ordinary conversation.

    Arguments:
    - key: the key to get the name for

    Returns a string representing the name for the key
    """

    if isinstance(key, unicode):
        key = key.encode("UTF-8")

    try:
        return __keynames[key]
    except:
        return chnames.getCharacterName(key)
