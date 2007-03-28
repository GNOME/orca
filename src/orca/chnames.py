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

# Translators: this is the spoken word for the space character
#
__chnames[" "] = _("space")

# Translators: this is the spoken word for the newline character
#
__chnames["\n"] = _("newline")

# Translators: this is the spoken word for the tab character
#
__chnames["\t"] = _("tab")

# Translators: this is the spoken word for the exclamation point: !
#
__chnames["!"] = _("exclaim")

# Translators: this is the spoken word for the apostrophe: '
#
__chnames["'"] = _("apostrophe")

# Translators: this is the spoken word for the comma: ,
#
__chnames[","] = _("comma")

# Translators: this is the spoken word for the period: .
#
__chnames["."] = _("dot")

# Translators: this is the spoken word for the question mark: ?
#
__chnames["?"] = _("question")

# Translators: this is the spoken word for the double quote: "
#
__chnames["\""] = _("quote")

# Translators: this is the spoken word for the left parentheses: (
#
__chnames["("] = _("left paren")

# Translators: this is the spoken word for the right parentheses: (
#
__chnames[")"] = _("right paren")

# Translators: this is the spoken word for the hyphen: -
#
__chnames["-"] = _("dash")

# Translators: this is the spoken word for the underscore: _
#
__chnames["_"] = _("underscore")

# Translators: this is the spoken word for the colon: :
#
__chnames[":"] = _("colon")

# Translators: this is the spoken word for the semicolon: ;
#
__chnames[";"] = _("semicolon")

# Translators: this is the spoken word for the less than sign: <
#
__chnames["<"] = _("less than")

# Translators: this is the spoken word for the greater than sign: >
#
__chnames[">"] = _("greater than")

# Translators: this is the spoken word for the left square bracket: [
#
__chnames["["] = _("left bracket")

# Translators: this is the spoken word for the right square bracket: ]
#
__chnames["]"] = _("right bracket")

# Translators: this is the spoken word for the backslash: \
#
__chnames["\\"] = _("backslash")

# Translators: this is the spoken word for the vertical line: |
#
__chnames["|"] = _("vertical line")

# Translators: this is the spoken word for the accent grave: `
#
__chnames["`"] = _("grave accent")

# Translators: this is the spoken word for the tilde: ~
#
__chnames["~"] = _("tilde")

# Translators: this is the spoken word for the left squiggly brace: {
#
__chnames["{"] = _("left brace")

# Translators: this is the spoken word for the right squiggly brace: {
#
__chnames["}"] = _("right brace")

# Translators: this is the spoken word for the octothorpe: #
#
__chnames["#"] = _("pound")

# Translators: this is the spoken word for the dollar sign: $
#
__chnames["$"] = _("dollar")

# Translators: this is the spoken word for the percent sign: %
#
__chnames["%"] = _("percent")

# Translators: this is the spoken word for the ampersand: &
#
__chnames["&"] = _("and")

# Translators: this is the spoken word for the star: *
#
__chnames["*"] = _("star")

# Translators: this is the spoken word for the plus: +
#
__chnames["+"] = _("plus")

# Translators: this is the spoken word for the forward slash: /
#
__chnames["/"] = _("slash")

# Translators: this is the spoken word for the equals sign: =
#
__chnames["="] = _("equals")

# Translators: this is the spoken word for the at sign: @
#
__chnames["@"] = _("at")

# Translators: this is the spoken word for the hat sign: ^
#
__chnames["^"] = _("caret")

# Translators: this is the spoken word for the plus/minus symbol
#
__chnames["\xc2\xb1"] = _("plus minus")

# Translators: this is the spoken word for the division sign
#
__chnames["\xc3\xb7"] = _("divide")

# Translators: this is the spoken word for the multiplication sign
#
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
