# Orca
#
# Copyright 2007 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

# __phonnames is a dictionary where the keys represent a UTF-8
# character (possibly multibyte) and the values represent the common
# 'military' term used for the character.
#
__phonnames = {}

# Translators: alpha is the spoken military/phonetic spelling for the
# letter a
#
__phonnames["a"] = _("alpha")

# Translators: bravo is the spoken military/phonetic spelling for the
# letter b
#
__phonnames["b"] = _("bravo")

# Translators: charlie is the spoken military/phonetic spelling for
# the letter c
#
__phonnames["c"] = _("charlie")

# Translators: delta is the spoken military/phonetic spelling for the
# letter d
#
__phonnames["d"] = _("delta")

# Translators: echo is the spoken military/phonetic spelling for the
# letter e
#
__phonnames["e"] = _("echo")

# Translators: foxtrot is the spoken military/phonetic spelling for
# the letter f
#
__phonnames["f"] = _("foxtrot")

# Translators: golf is the spoken military/phonetic spelling for the
# letter g
#
__phonnames["g"] = _("golf")

# Translators: hotel is the spoken military/phonetic spelling for the
# letter h
#
__phonnames["h"] = _("hotel")

# Translators: india is the spoken military/phonetic spelling for the
# letter i
#
__phonnames["i"] = _("india")

# Translators: juliet is the spoken military/phonetic spelling for the
# letter j
#
__phonnames["j"] = _("juliet")

# Translators: kilo is the spoken military/phonetic spelling for the
# letter k
#
__phonnames["k"] = _("kilo")

# Translators: lima is the spoken military/phonetic spelling for the
# letter l
#
__phonnames["l"] = _("lima")

# Translators: mike is the spoken military/phonetic spelling for the
# letter m
#
__phonnames["m"] = _("mike")

# Translators: november is the spoken military/phonetic spelling for
# the letter n
#
__phonnames["n"] = _("november")

# Translators: oscar is the spoken military/phonetic spelling for the
# letter o
#
__phonnames["o"] = _("oscar")

# Translators: papa is the spoken military/phonetic spelling for the
# letter p
#
__phonnames["p"] = _("papa")

# Translators: quebec is the spoken military/phonetic spelling for the
# letter q
#
__phonnames["q"] = _("quebec")

# Translators: romeo is the spoken military/phonetic spelling for the
# letter r
#
__phonnames["r"] = _("romeo")

# Translators: sierra is the spoken military/phonetic spelling for the
# letter s
#
__phonnames["s"] = _("sierra")

# Translators: tango is the spoken military/phonetic spelling for the
# letter t
#
__phonnames["t"] = _("tango")

# Translators: uniform is the spoken military/phonetic spelling for
# the letter u
#
__phonnames["u"] = _("uniform")

# Translators: victor is the spoken military/phonetic spelling for the
# letter v
#
__phonnames["v"] = _("victor")

# Translators: whiskey is the spoken military/phonetic spelling for
# the letter w
#
__phonnames["w"] = _("whiskey")

# Translators: xray is the spoken military/phonetic spelling for the
# letter x
#
__phonnames["x"] = _("xray")

# Translators: yankee is the spoken military/phonetic spelling for the
# letter y
#
__phonnames["y"] = _("yankee")

# Translators: zulu is the spoken military/phonetic spelling for the
# letter z
#
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
