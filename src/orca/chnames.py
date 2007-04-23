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

# chnames is a dictionary where the keys represent a unicode character
# and the values represent the common term used for the character.
#
chnames = {}

# Translators: this is the spoken word for the space character
#
chnames[" "] = _("space")

# Translators: this is the spoken word for the newline character
#
chnames["\n"] = _("newline")

# Translators: this is the spoken word for the tab character
#
chnames["\t"] = _("tab")

# Translators: this is the spoken word for the exclamation point: !
#
chnames["!"] = _("exclaim")

# Translators: this is the spoken word for the apostrophe: '
#
chnames["'"] = _("apostrophe")

# Translators: this is the spoken word for the left single quote: ‘
# (U+2018)
#
chnames[u'\u2018'] = _("left single quote")

# Translators: this is the spoken word for the right single quote: ’
# (U+2019)
#
chnames[u'\u2019'] = _("right single quote")

# Translators: this is the spoken word for the comma: ,
#
chnames[","] = _("comma")

# Translators: this is the spoken word for the period: .
#
chnames["."] = _("dot")

# Translators: this is the spoken word for the question mark: ?
#
chnames["?"] = _("question")

# Translators: this is the spoken word for the double quote: "
#
chnames["\""] = _("quote")

# Translators: this is the spoken word for the left double quote: “
# (U+201C)
#
chnames[u'\u201C']  = _("left double quote")

# Translators: this is the spoken word for the right double quote: ”
# (U+201D)
#
chnames[u'\u201D']  = _("right double quote")

# Translators: this is the spoken word for the left parentheses: (
#
chnames["("] = _("left paren")

# Translators: this is the spoken word for the right parentheses: (
#
chnames[")"] = _("right paren")

# Translators: this is the spoken word for the hyphen: -
#
chnames["-"] = _("dash")

# Translators: this is the spoken word for the en dash: –
# (U+2013)
#
chnames[u'\u2013'] = _("en dash")

# Translators: this is the spoken word for the underscore: _
#
chnames["_"] = _("underscore")

# Translators: this is the spoken word for the colon: :
#
chnames[":"] = _("colon")

# Translators: this is the spoken word for the semicolon: ;
#
chnames[";"] = _("semicolon")

# Translators: this is the spoken word for the less than sign: <
#
chnames["<"] = _("less than")

# Translators: this is the spoken word for the greater than sign: >
#
chnames[">"] = _("greater than")

# Translators: this is the spoken word for the left square bracket: [
#
chnames["["] = _("left bracket")

# Translators: this is the spoken word for the right square bracket: ]
#
chnames["]"] = _("right bracket")

# Translators: this is the spoken word for the backslash: \
#
chnames["\\"] = _("backslash")

# Translators: this is the spoken word for the vertical line: |
#
chnames["|"] = _("vertical line")

# Translators: this is the spoken word for the accent grave: `
#
chnames["`"] = _("grave accent")

# Translators: this is the spoken word for the tilde: ~
#
chnames["~"] = _("tilde")

# Translators: this is the spoken word for the left squiggly brace: {
#
chnames["{"] = _("left brace")

# Translators: this is the spoken word for the right squiggly brace: {
#
chnames["}"] = _("right brace")

# Translators: this is the spoken word for the octothorpe: #
#
chnames["#"] = _("number")

# Translators: this is the spoken word for the dollar sign: $
#
chnames["$"] = _("dollar")

# Translators: this is the spoken word for the cent sign: ¢
# (U+00A2)
#
chnames[u'\u00A2'] = _("cent")

# Translators: this is the spoken word for the pound sign: £
# (U+00A3)
#
chnames[u'\u00A3'] = _("pound")

# Translators: this is the spoken word for the yen sign: ¥
# (U+00A5)
#
chnames[u'\u00A5'] = _("yen")

# Translators: this is the spoken word for the euro sign: €
# (U+20AC)
#
chnames[u'\u20AC'] = _("euro")

# Translators: this is the spoken word for the percent sign: %
#
chnames["%"] = _("percent")

# Translators: this is the spoken word for the ampersand: &
#
chnames["&"] = _("and")

# Translators: this is the spoken word for the star: *
#
chnames["*"] = _("star")

# Translators: this is the spoken word for the plus: +
#
chnames["+"] = _("plus")

# Translators: this is the spoken word for the forward slash: /
#
chnames["/"] = _("slash")

# Translators: this is the spoken word for the equals sign: =
#
chnames["="] = _("equals")

# Translators: this is the spoken word for the at sign: @
#
chnames["@"] = _("at")

# Translators: this is the spoken word for the hat sign: ^
#
chnames["^"] = _("caret")

# Translators: this is the spoken word for the not sign: ¬
# (U+00AC)
#
chnames[u'\u00AC'] = _("not")

# Translators: this is the spoken word for the copyright sign: ©
# (U+00A9)
#
chnames[u'\u00A9'] = _("copyright")

# Translators: this is the spoken word for the registered sign: ®
# (U+00AE)
#
chnames[u'\u00AE'] = _("registered")

# Translators: this is the spoken word for the trademark sign: ™
# (U+2122)
#
chnames[u'\u2122'] = _("trademark")

# Translators: this is the spoken word for the degree symbol: °
# (U+00B0)
#
chnames[u'\u00B0'] =  _("degree") 

# Translators: this is the spoken word for the plus/minus symbol: ±
# (U+00B1)
#
chnames[u'\u00B1'] = _("plus minus")

# Translators: this is the spoken word for a superscripted 2: ²
# (U+00B2)
#
chnames[u'\u00B2'] = _("2 superscript")

# Translators: this is the spoken word for a superscripted 3: ³
# (U+00B3)
#
chnames[u'\u00B3'] = _("3 superscript")

# Translators: this is the spoken word for the 1/4 sign: ¼
# (U+00BC)
#
chnames[u'\u00BC'] = _("one quarter")

# Translators: this is the spoken word for the 1/2 sign: ½
# (U+00BD)
#
chnames[u'\u00BD'] = _("one half")

# Translators: this is the spoken word for the 3/4 sign: ¾
# (U+00BE)
#
chnames[u'\u00BE'] = _("three quarters")

# Translators: this is the spoken word for the multiplication sign: ×
# (U+00D7)
#
chnames[u'\u00D7'] = _("times")

# Translators: this is the spoken word for the division sign: ÷
# (U+00F7)
#
chnames[u'\u00F7'] = _("divided by")

# Translators: this is the spoken word for the n tilde: ñ
# (U+00F1)
#
chnames[u'\u00F1'] = _("n tilde")

# Translators: this is the spoken word for the per mille sign: ‰
# (U+2030)
# 
chnames[u'\u2030'] = _("per mille")

# Translators: this is the spoken word for the prime sign: ′
# (U+2032)
# 
chnames[u'\u2032'] = _("prime")

# Translators: this is the spoken word for the double prime sign: ″
# (U+2033)
# 
chnames[u'\u2033'] = _("double prime")

# Translators: this is the spoken word for the almost-equal-to sign: ≈
# (U+2248)
# 
chnames[u'\u2248'] = _("almost equal to")

# Translators: this is the spoken word for the not-equal-to sign: ≠
# (U+2260)
# 
chnames[u'\u2260'] = _("not equal to")

# Translators: this is the spoken word for the less-than-or-equal-to sign: ≤
# (U+2264)
#
chnames[u'\u2264'] = _("less than or equal to")

# Translators: this is the spoken word for the greater-than-or-equal-to 
# sign: ≥ (U+2265)
#
chnames[u'\u2265'] = _("greater-than or equal to")

# Translators: this is the spoken word for the square-root symbol: √
# (U+221A)
#
chnames[u'\u221A'] = _("square root")

# Translators: this is the spoken word for the cube-root symbol: ∛
# (U+221B)
#
chnames[u'\u221B'] = _("cube root")

# Translators: this is the spoken word for the infinity symbol: ∞
# (U+221E)
#
chnames[u'\u221E'] = _("infinity")

# Translators: this is the spoken word for the section symbol: §
# (U+00A7)
#
chnames[u'\u00A7'] = _("section")

# Translators: this is the spoken word for the dagger symbol: †
# (U+2020)
#
chnames[u'\u2020'] = _("dagger")

# Translators: this is the spoken word for the double-dagger symbol: ‡
# (U+2021)
#
chnames[u'\u2021'] = _("double dagger")

# Translators: this is the spoken word for the middle dot: ·
# (U+00B7) 
#
chnames[u'\u00B7'] = _("middle dot")

# Translators: this is the spoken word for the bullet: •
# (U+2022)
#
chnames[u'\u2022'] = _("bullet")

# Translators: this is the spoken word for the triangular bullet: ‣
# (U+2023)
#
chnames[u'\u2023'] = _("triangular bullet")

# Translators: this is the spoken word for the hyphen bullet: ⁃
# (U+2043)
#
chnames[u'\u2043'] = _("hyphen bullet")

# Translators: this is the spoken word for the black square: ■
# (U+25A0).  It can be used as a bullet in a list.
#
chnames[u'\u25A0'] = _("black square")

# Translators: this is the spoken word for the white square: □
# (U+25A1). It can be used as a bullet in a list.
#
chnames[u'\u25A1'] = _("white square")

# Translators: this is the spoken word for the white bullet: ◦
# (U+25E6)
#
chnames[u'\u25E6'] = _("white bullet")

# Translators: this is the spoken word for the white circle: ○
# (U+25CB). It can be used as a bullet in a list.
#
chnames[u'\u25CB'] = _("white circle")

# Translators: this is the spoken word for the black circle: ●
# (U+25CF). It can be used as a bullet in a list.
#
chnames[u'\u25CF'] = _("black circle")

# Translators: this is the spoken word for the black diamond: ◆
# (U+25C6). It can be used as a bullet in a list.
#
chnames[u'\u25C6'] = _("black diamond")

# Translators: this is the spoken word for the check mark: ✓
# (U+2713). It can be used as a bullet in a list.
#
chnames[u'\u2713'] = _("check mark")

# Translators: this is the spoken word for the heavy check mark: ✔
# (U+2714). It can be used as a bullet in a list.
#
chnames[u'\u2714'] = _("heavy check mark")

# Translators: this is the spoken word for the character which unicode.org
# names "ballot x": ✗ (U+2717). This symbol is included here because it
# can be used as a bullet in an OOo list.  The goal is to inform the user
# of the appearance of the bullet, while making it clear that it is a bullet
# and not simply the typed letter 'x'.  "Ballot x" might confuse the user.
# Hence the use of "x-shaped bullet".
#
chnames[u'\u2717'] = _("x-shaped bullet")

# Translators: this is the spoken word for the character which unicode.org
# names "heavy wide-headed rightwards arrow": ➔ (U+2794). This symbol
# is included here because it can be used as a bullet in an OOo list. The
# goal is to inform the user of the appearance of the bullet without too
# much verbiage, hence simply "right-pointing arrow".
#
chnames[u'\u2794'] = _("right-pointing arrow")

# Translators: this is the spoken word for the character which unicode.org
# names "three-d top-lighted rightwards arrowhead": ➢ (U+27A2). This symbol
# is included here because it can be used as a bullet in an OOo list. The
# goal is to inform the user of the appearance of the bullet without too
# much verbiage, hence simply "right-pointing arrowhead".
#
chnames[u'\u27A2'] = _("right-pointing arrowhead")

# Translators:  StarOffice/OOo includes private-use unicode character U+E00A
# as a bullet which looks like the black square: ■ (U+25A0).  Therefore,
# please use the same translation for this character.
#
chnames[u'\uE00A'] = _("black square")

# Translators:  StarOffice/OOo includes private-use unicode character U+E00C
# as a bullet which looks like the black diamond: ◆ (U+25C6).  Therefore,
# please use the same translation for this character.
#
chnames[u'\uE00C'] = _("black diamond")

def getCharacterName(character):
    """Given a character, return its name as people might refer to it
    in ordinary conversation.

    Arguments:
    - character: the character to get the name for

    Returns a string representing the name for the character
    """

    if not isinstance(character, unicode):
        character = character.decode("UTF-8")

    try:
        return chnames[character]
    except:
        return character
