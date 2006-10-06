# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
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

"""Provides getCharacterName that maps punctuation marks and other
individual characters into localized words."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

# __chnames is a dictionary where the keys represent a UTF-8
# character (possibly multibyte) and the values represent the common
# term used for the character.
#
__chnames = {}
__chnames[" "] = _("space")
__chnames["\n"] = _("newline")
__chnames["\t"] = _("tab")

__chnames["!"] = _("exclaim")
__chnames["'"] = _("apostrophe")
__chnames[","] = _("comma")
__chnames["."] = _("dot")
__chnames["?"] = _("question")

__chnames["\""] = _("quote")
__chnames["("] = _("left paren")
__chnames[")"] = _("right paren")
__chnames["-"] = _("dash")
__chnames["_"] = _("underscore")
__chnames[":"] = _("colon")
__chnames[";"] = _("semicolon")
__chnames["<"] = _("less than")
__chnames[">"] = _("greater than")
__chnames["["] = _("left bracket")
__chnames["]"] = _("right bracket")
__chnames["\\"] = _("backslash")
__chnames["|"] = _("vertical line")
__chnames["`"] = _("grave accent")
__chnames["~"] = _("tilde")
__chnames["{"] = _("left brace")
__chnames["}"] = _("right brace")

__chnames["#"] = _("pound")
__chnames["$"] = _("dollar")
__chnames["%"] = _("percent")
__chnames["&"] = _("and")
__chnames["*"] = _("star")
__chnames["+"] = _("plus")
__chnames["/"] = _("slash")
__chnames["="] = _("equals")
__chnames["@"] = _("at")
__chnames["^"] = _("caret")

__chnames["\xc2\xb1"] = _("plus minus")
__chnames["\xc3\xb7"] = _("divide")
__chnames["\xc3\x97"] = _("multiply")

def getCharacterName(character):
    """Given a character, return its name as people might refer to it
    in ordinary conversation.

    Arguments:
    - character: the character to get the name for

    Returns a string representing the name for the character
    """

    if isinstance(character, unicode):
        character = character.encode("UTF-8")

    try:
        return __chnames[character]
    except:
        return character
