# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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

"""Provides getPhoneticName method that maps each letter of the
alphabet into its localized phonetic equivalent."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

# __phonnames is a dictionary where the keys represent a UTF-8
# character (possibly multibyte) and the values represent the common
# 'military' term used for the character.
#
__phonnames = {}
__phonnames["a"] = _("alpha")
__phonnames["b"] = _("bravo")
__phonnames["c"] = _("charlie")
__phonnames["d"] = _("delta")
__phonnames["e"] = _("echo")
__phonnames["f"] = _("foxtrot")
__phonnames["g"] = _("golf")
__phonnames["h"] = _("hotel")
__phonnames["i"] = _("india")
__phonnames["j"] = _("juliet")
__phonnames["k"] = _("kilo")
__phonnames["l"] = _("lima")
__phonnames["m"] = _("mike")
__phonnames["n"] = _("november")
__phonnames["o"] = _("oscar")
__phonnames["p"] = _("papa")
__phonnames["q"] = _("quebec")
__phonnames["r"] = _("romeo")
__phonnames["s"] = _("sierra")
__phonnames["t"] = _("tango")
__phonnames["u"] = _("uniform")
__phonnames["v"] = _("victor")
__phonnames["w"] = _("whiskey")
__phonnames["x"] = _("xray")
__phonnames["y"] = _("yankee")
__phonnames["z"] = _("zulu")

def getPhoneticName(character):
    """Given a character, return its phonetic name, which is typically
    the 'military' term used for the character.

    Arguments:
    - character: the character to get the military name for

    Returns a string representing the military name for the character
    """

    if isinstance(character, unicode):
        character = character.encode("UTF-8")

    try:
        return __phonnames[character]
    except:
        return character
