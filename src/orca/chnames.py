# -*- coding: utf-8 -*-
# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Provides getCharacterName that maps punctuation marks and other
individual characters into localized words."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
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

# Translators: this is the spoken word for the character '!' (U+0021)
#
chnames["!"] = _("exclaim")

# Translators: this is the spoken word for the character '"' (U+0022)
#
chnames["\""] = _("quote")

# Translators: this is the spoken word for the character '#' (U+0023)
#
chnames["#"] = _("number")

# Translators: this is the spoken word for the character '$' (U+0024)
#
chnames["$"] = _("dollar")

# Translators: this is the spoken word for the character '%' (U+0025)
#
chnames["%"] = _("percent")

# Translators: this is the spoken word for the character '&' (U+0026)
#
chnames["&"] = _("and")

# Translators: this is the spoken word for the character ''' (U+0027)
#
chnames["'"] = _("apostrophe")

# Translators: this is the spoken word for the character '(' (U+0028)
#
chnames["("] = _("left paren")

# Translators: this is the spoken word for the character ')' (U+0029)
#
chnames[")"] = _("right paren")

# Translators: this is the spoken word for the character '*' (U+002a)
#
chnames["*"] = _("star")

# Translators: this is the spoken word for the character '+' (U+002b)
#
chnames["+"] = _("plus")

# Translators: this is the spoken word for the character ',' (U+002c)
#
chnames[","] = _("comma")

# Translators: this is the spoken word for the character '-' (U+002d)
#
chnames["-"] = _("dash")

# Translators: this is the spoken word for the character '.' (U+002e)
#
chnames["."] = _("dot")

# Translators: this is the spoken word for the character '/' (U+002f)
#
chnames["/"] = _("slash")

# Translators: this is the spoken word for the character ':' (U+003a)
#
chnames[":"] = _("colon")

# Translators: this is the spoken word for the character ';' (U+003b)
#
chnames[";"] = _("semicolon")

# Translators: this is the spoken word for the character '< ' (U+003c)
#
chnames["<"] = _("less")

# Translators: this is the spoken word for the character '=' (U+003d)
#
chnames["="] = _("equals")

# Translators: this is the spoken word for the character '> ' (U+003e)
#
chnames[">"] = _("greater")

# Translators: this is the spoken word for the character '?' (U+003f)
#
chnames["?"] = _("question")

# Translators: this is the spoken word for the character '@' (U+0040)
#
chnames["@"] = _("at")

# Translators: this is the spoken word for the character '[' (U+005b)
#
chnames["["] = _("left bracket")

# Translators: this is the spoken word for the character '\' (U+005c)
#
chnames["\\"] = _("backslash")

# Translators: this is the spoken word for the character ']' (U+005d)
#
chnames["]"] = _("right bracket")

# Translators: this is the spoken word for the character '^' (U+005e)
#
chnames["^"] = _("caret")

# Translators: this is the spoken word for the character '_' (U+005f)
#
chnames["_"] = _("underline")

# Translators: this is the spoken word for the character '`' (U+0060)
#
chnames["`"] = _("grave")

# Translators: this is the spoken word for the character '{' (U+007b)
#
chnames["{"] = _("left brace")

# Translators: this is the spoken word for the character '|' (U+007c)
#
chnames["|"] = _("vertical bar")

# Translators: this is the spoken word for the character '}' (U+007d)
#
chnames["}"] = _("right brace")

# Translators: this is the spoken word for the character '~' (U+007e)
#
chnames["~"] = _("tilde")

# Translators: this is the spoken character for the no break space
# character (e.g., "&nbsp;" in HTML -- U+00a0)
#
chnames[u'\u00a0'] = _("no break space")

# Translators: this is the spoken word for the character '¡' (U+00a1)
#
chnames[u'\u00a1'] = _("inverted exclamation point")

# Translators: this is the spoken word for the character '¢' (U+00a2)
#
chnames[u'\u00a2'] = _("cents")

# Translators: this is the spoken word for the character '£' (U+00a3)
#
chnames[u'\u00a3'] = _("pounds")

# Translators: this is the spoken word for the character '¤' (U+00a4)
#
chnames[u'\u00a4'] = _("currency sign")

# Translators: this is the spoken word for the character '¥' (U+00a5)
#
chnames[u'\u00a5'] = _("yen")

# Translators: this is the spoken word for the character '¦' (U+00a6)
#
chnames[u'\u00a6'] = _("broken bar")

# Translators: this is the spoken word for the character '§' (U+00a7)
#
chnames[u'\u00a7'] = _("section")

# Translators: this is the spoken word for the character '¨' (U+00a8)
#
chnames[u'\u00a8'] = _("umlaut")

# Translators: this is the spoken word for the character '©' (U+00a9)
#
chnames[u'\u00a9'] = _("copyright")

# Translators: this is the spoken word for the character 'ª' (U+00aa)
#
chnames[u'\u00aa'] = _("superscript a")

# Translators: this is the spoken word for the character '«' (U+00ab)
#
chnames[u'\u00ab'] = _("left double angle bracket")

# Translators: this is the spoken word for the character '¬' (U+00ac)
#
chnames[u'\u00ac'] = _("logical not")

# Translators: this is the spoken word for the character '­' (U+00ad)
#
chnames[u'\u00ad'] = _("soft hyphen")

# Translators: this is the spoken word for the character '®' (U+00ae)
#
chnames[u'\u00ae'] = _("registered")

# Translators: this is the spoken word for the character '¯' (U+00af)
#
chnames[u'\u00af'] = _("macron")

# Translators: this is the spoken word for the character '°' (U+00b0)
#
chnames[u'\u00b0'] = _("degrees")

# Translators: this is the spoken word for the character '±' (U+00b1)
#
chnames[u'\u00b1'] = _("plus or minus")

# Translators: this is the spoken word for the character '²' (U+00b2)
#
chnames[u'\u00b2'] = _("superscript 2")

# Translators: this is the spoken word for the character '³' (U+00b3)
#
chnames[u'\u00b3'] = _("superscript 3")

# Translators: this is the spoken word for the character '´' (U+00b4)
#
chnames[u'\u00b4'] = _("acute accent")

# Translators: this is the spoken word for the character 'µ' (U+00b5)
#
chnames[u'\u00b5'] = _("mu")

# Translators: this is the spoken word for the character '¶' (U+00b6)
#
chnames[u'\u00b6'] = _("paragraph marker")

# Translators: this is the spoken word for the character '·' (U+00b7)
#
chnames[u'\u00b7'] = _("middle dot")

# Translators: this is the spoken word for the character '¸' (U+00b8)
#
chnames[u'\u00b8'] = _("cedilla")

# Translators: this is the spoken word for the character '¹' (U+00b9)
#
chnames[u'\u00b9'] = _("superscript 1")

# Translators: this is the spoken word for the character 'º' (U+00ba)
#
chnames[u'\u00ba'] = _("ordinal")

# Translators: this is the spoken word for the character '»' (U+00bb)
#
chnames[u'\u00bb'] = _("right double angle bracket")

# Translators: this is the spoken word for the character '¼' (U+00bc)
#
chnames[u'\u00bc'] = _("one fourth")

# Translators: this is the spoken word for the character '½' (U+00bd)
#
chnames[u'\u00bd'] = _("one half")

# Translators: this is the spoken word for the character '¾' (U+00be)
#
chnames[u'\u00be'] = _("three fourths")

# Translators: this is the spoken word for the character '¿' (U+00bf)
#
chnames[u'\u00bf'] = _("inverted question mark")

# Translators: this is the spoken word for the character 'á' (U+00e1)
#
chnames[u'\u00e1'] = _("a acute")

# Translators: this is the spoken word for the character 'À' (U+00c0)
#
chnames[u'\u00c0'] = _("A GRAVE")

# Translators: this is the spoken word for the character 'Á' (U+00c1)
#
chnames[u'\u00c1'] = _("A ACUTE")

# Translators: this is the spoken word for the character 'Â' (U+00c2)
#
chnames[u'\u00c2'] = _("A CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ã' (U+00c3)
#
chnames[u'\u00c3'] = _("A TILDE")

# Translators: this is the spoken word for the character 'Ä' (U+00c4)
#
chnames[u'\u00c4'] = _("A UMLAUT")

# Translators: this is the spoken word for the character 'Å' (U+00c5)
#
chnames[u'\u00c5'] = _("A RING")

# Translators: this is the spoken word for the character 'Æ' (U+00c6)
#
chnames[u'\u00c6'] = _("A E")

# Translators: this is the spoken word for the character 'Ç' (U+00c7)
#
chnames[u'\u00c7'] = _("C CEDILLA")

# Translators: this is the spoken word for the character 'È' (U+00c8)
#
chnames[u'\u00c8'] = _("E GRAVE")

# Translators: this is the spoken word for the character 'É' (U+00c9)
#
chnames[u'\u00c9'] = _("E ACUTE")

# Translators: this is the spoken word for the character 'Ê' (U+00ca)
#
chnames[u'\u00ca'] = _("E CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ë' (U+00cb)
#
chnames[u'\u00cb'] = _("E UMLAUT")

# Translators: this is the spoken word for the character 'Ì' (U+00cc)
#
chnames[u'\u00cc'] = _("I GRAVE")

# Translators: this is the spoken word for the character 'Í' (U+00cd)
#
chnames[u'\u00cd'] = _("I ACUTE")

# Translators: this is the spoken word for the character 'Î' (U+00ce)
#
chnames[u'\u00ce'] = _("I CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ï' (U+00cf)
#
chnames[u'\u00cf'] = _("I UMLAUT")

# Translators: this is the spoken word for the character 'Ð' (U+00d0)
#
chnames[u'\u00d0'] = _("ETH")

# Translators: this is the spoken word for the character 'Ñ' (U+00d1)
#
chnames[u'\u00d1'] = _("N TILDE")

# Translators: this is the spoken word for the character 'Ò' (U+00d2)
#
chnames[u'\u00d2'] = _("O GRAVE")

# Translators: this is the spoken word for the character 'Ó' (U+00d3)
#
chnames[u'\u00d3'] = _("O ACUTE")

# Translators: this is the spoken word for the character 'Ô' (U+00d4)
#
chnames[u'\u00d4'] = _("O CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Õ' (U+00d5)
#
chnames[u'\u00d5'] = _("O TILDE")

# Translators: this is the spoken word for the character 'Ö' (U+00d6)
#
chnames[u'\u00d6'] = _("O UMLAUT")

# Translators: this is the spoken word for the character '×' (U+00d7)
#
chnames[u'\u00d7'] = _("times")

# Translators: this is the spoken word for the character 'Ø' (U+00d8)
#
chnames[u'\u00d8'] = _("O STROKE")

# Translators: this is the spoken word for the character 'Ù' (U+00d9)
#
chnames[u'\u00d9'] = _("U GRAVE")

# Translators: this is the spoken word for the character 'Ú' (U+00da)
#
chnames[u'\u00da'] = _("U ACUTE")

# Translators: this is the spoken word for the character 'Û' (U+00db)
#
chnames[u'\u00db'] = _("U CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ü' (U+00dc)
#
chnames[u'\u00dc'] = _("U UMLAUT")

# Translators: this is the spoken word for the character 'Ý' (U+00dd)
#
chnames[u'\u00dd'] = _("Y ACUTE")

# Translators: this is the spoken word for the character 'Þ' (U+00de)
#
chnames[u'\u00de'] = _("THORN")

# Translators: this is the spoken word for the character 'ß' (U+00df)
#
chnames[u'\u00df'] = _("s sharp")

# Translators: this is the spoken word for the character 'à' (U+00e0)
#
chnames[u'\u00e0'] = _("a grave")

# Translators: this is the spoken word for the character 'â' (U+00e2)
#
chnames[u'\u00e2'] = _("a circumflex")

# Translators: this is the spoken word for the character 'ã' (U+00e3)
#
chnames[u'\u00e3'] = _("a tilde")

# Translators: this is the spoken word for the character 'ä' (U+00e4)
#
chnames[u'\u00e4'] = _("a umlaut")

# Translators: this is the spoken word for the character 'å' (U+00e5)
#
chnames[u'\u00e5'] = _("a ring")

# Translators: this is the spoken word for the character 'æ' (U+00e6)
#
chnames[u'\u00e6'] = _("a e")

# Translators: this is the spoken word for the character 'ç' (U+00e7)
#
chnames[u'\u00e7'] = _("c cedilla")

# Translators: this is the spoken word for the character 'è' (U+00e8)
#
chnames[u'\u00e8'] = _("e grave")

# Translators: this is the spoken word for the character 'é' (U+00e9)
#
chnames[u'\u00e9'] = _("e acute")

# Translators: this is the spoken word for the character 'ê' (U+00ea)
#
chnames[u'\u00ea'] = _("e circumflex")

# Translators: this is the spoken word for the character 'ë' (U+00eb)
#
chnames[u'\u00eb'] = _("e umlaut")

# Translators: this is the spoken word for the character 'ì' (U+00ec)
#
chnames[u'\u00ec'] = _("i grave")

# Translators: this is the spoken word for the character 'í' (U+00ed)
#
chnames[u'\u00ed'] = _("i acute")

# Translators: this is the spoken word for the character 'î' (U+00ee)
#
chnames[u'\u00ee'] = _("i circumflex")

# Translators: this is the spoken word for the character 'ï' (U+00ef)
#
chnames[u'\u00ef'] = _("i umlaut")

# Translators: this is the spoken word for the character 'ð' (U+00f0)
#
chnames[u'\u00f0'] = _("eth")

# Translators: this is the spoken word for the character 'ñ' (U+00f1)
#
chnames[u'\u00f1'] = _("n tilde")

# Translators: this is the spoken word for the character 'ò' (U+00f2)
#
chnames[u'\u00f2'] = _("o grave")

# Translators: this is the spoken word for the character 'ó' (U+00f3)
#
chnames[u'\u00f3'] = _("o acute")

# Translators: this is the spoken word for the character 'ô' (U+00f4)
#
chnames[u'\u00f4'] = _("o circumflex")

# Translators: this is the spoken word for the character 'õ' (U+00f5)
#
chnames[u'\u00f5'] = _("o tilde")

# Translators: this is the spoken word for the character 'ö' (U+00f6)
#
chnames[u'\u00f6'] = _("o umlaut")

# Translators: this is the spoken word for the character '÷' (U+00f7)
#
chnames[u'\u00f7'] = _("divided by")

# Translators: this is the spoken word for the character 'ø' (U+00f8)
#
chnames[u'\u00f8'] = _("o stroke")

# Translators: this is the spoken word for the character 'þ' (U+00fe)
#
chnames[u'\u00fe'] = _("thorn")

# Translators: this is the spoken word for the character 'ú' (U+00fa)
#
chnames[u'\u00fa'] = _("u acute")

# Translators: this is the spoken word for the character 'ù' (U+00f9)
#
chnames[u'\u00f9'] = _("u grave")

# Translators: this is the spoken word for the character 'û' (U+00fb)
#
chnames[u'\u00fb'] = _("u circumflex")

# Translators: this is the spoken word for the character 'ü' (U+00fc)
#
chnames[u'\u00fc'] = _("u umlaut")

# Translators: this is the spoken word for the character 'ý' (U+00fd)
#
chnames[u'\u00fd'] = _("y acute")

# Translators: this is the spoken word for the character 'ÿ' (U+00ff)
#
chnames[u'\u00ff'] = _("y umlaut")

# Translators: this is the spoken word for the character 'Ÿ' (U+0178)
#
chnames[u'\u0178'] = _("Y UMLAUT")

# Translators: this is the spoken word for the character 'ƒ' (U+0192)
#
chnames[u'\u0192'] = _("florin")

# Translators: this is the spoken word for the character '–' (U+2013)
#
chnames[u'\u2013'] = _("en dash")

# Translators: this is the spoken word for the left single quote: ‘
# (U+2018)
#
chnames[u'\u2018'] = _("left single quote")

# Translators: this is the spoken word for the right single quote: ’
# (U+2019)
#
chnames[u'\u2019'] = _("right single quote")

# Translators: this is the spoken word for the character '‚' (U+201a)
#
chnames[u'\u201a'] = _("single low quote")

# Translators: this is the spoken word for the character '“' (U+201c)
#
chnames[u'\u201c'] = _("left double quote")

# Translators: this is the spoken word for the character '”' (U+201d)
#
chnames[u'\u201d'] = _("right double quote")

# Translators: this is the spoken word for the character '„' (U+201e)
#
chnames[u'\u201e'] = _("double low quote")

# Translators: this is the spoken word for the character '†' (U+2020)
#
chnames[u'\u2020'] = _("dagger")

# Translators: this is the spoken word for the character '‡' (U+2021)
#
chnames[u'\u2021'] = _("double dagger")

# Translators: this is the spoken word for the character '•' (U+2022)
#
chnames[u'\u2022'] = _("bullet")

# Translators: this is the spoken word for the character '‣' (U+2023)
#
chnames[u'\u2023'] = _("triangular bullet")

# Translators: this is the spoken word for the character '‰' (U+2030)
#
chnames[u'\u2030'] = _("per mille")

# Translators: this is the spoken word for the character '′' (U+2032)
#
chnames[u'\u2032'] = _("prime")

# Translators: this is the spoken word for the character '″' (U+2033)
#
chnames[u'\u2033'] = _("double prime")

# Translators: this is the spoken word for the character '⁃' (U+2043)
#
chnames[u'\u2043'] = _("hyphen bullet")

# Translators: this is the spoken word for the character '€' (U+20ac)
#
chnames[u'\u20ac'] = _("euro")

# Translators: this is the spoken word for the character '™' (U+2122)
#
chnames[u'\u2122'] = _("trademark")

# Translators: this is the spoken word for the character '←' (U+2190)
#
chnames[u'\u2190'] = _("left arrow")

# Translators: this is the spoken word for the character '→' (U+2192)
#
chnames[u'\u2192'] = _("right arrow")

# Translators: this is the spoken word for the character '≈' (U+2248)
#
chnames[u'\u2248'] = _("almost equal to")

# Translators: this is the spoken word for the character '≠' (U+2260)
#
chnames[u'\u2260'] = _("not equal to")

# Translators: this is the spoken word for the character '≤' (U+2264)
#
chnames[u'\u2264'] = _("less than or equal to")

# Translators: this is the spoken word for the character '≥' (U+2265)
#
chnames[u'\u2265'] = _("greater than or equal to")

# Translators: this is the spoken word for the character '√' (U+221a)
#
chnames[u'\u221a'] = _("square root")

# Translators: this is the spoken word for the character '∛' (U+221b)
#
chnames[u'\u221b'] = _("cube root")

# Translators: this is the spoken word for the character '∞' (U+221e)
#
chnames[u'\u221e'] = _("infinity")

# Translators: this is the spoken word for the character '■' (U+25a0)
# It can be used as a bullet in a list.
#
chnames[u'\u25a0'] = _("black square")

# Translators: this is the spoken word for the character '□' (U+25a1)
# It can be used as a bullet in a list.
#
chnames[u'\u25a1'] = _("white square")

# Translators: this is the spoken word for the character '◆' (U+25c6)
# It can be used as a bullet in a list.
#
chnames[u'\u25c6'] = _("black diamond")

# Translators: this is the spoken word for the character '○' (U+25cb)
# It can be used as a bullet in a list.
#
chnames[u'\u25cb'] = _("white circle")

# Translators: this is the spoken word for the character '●' (U+25cf)
# It can be used as a bullet in a list.
#
chnames[u'\u25cf'] = _("black circle")

# Translators: this is the spoken word for the character '◦' (U+25e6)
#
chnames[u'\u25e6'] = _("white bullet")

# Translators: this is the spoken word for the character '✓' (U+2713)
# It can be used as a bullet in a list.
#
chnames[u'\u2713'] = _("check mark")

# Translators: this is the spoken word for the character '✔' (U+2714)
# It can be used as a bullet in a list.
#
chnames[u'\u2714'] = _("heavy check mark")

# Translators: this is the spoken word for the character 'x' (U+2717)
# This symbol is included here because it can be used as a bullet in 
# an OOo list.  The goal is to inform the user of the appearance of 
# the bullet, while making it clear that it is a bullet and not simply 
# the typed letter 'x'.  "Ballot x" might confuse the user.  Hence the 
# use of "x-shaped bullet".
#
chnames[u'\u2717'] = _("x-shaped bullet")

# Translators: this is the spoken word for the character '➔' (U+2794)
# This symbol is included here because it can be used as a bullet in 
# an OOo list. The goal is to inform the user of the appearance of 
# the bullet without too much verbiage, hence simply "right-pointing arrow".
#
chnames[u'\u2974'] = _("right-pointing arrow")

# Translators: this is the spoken word for the character '➢' (U+27a2)
# This symbol is included here because it can be used as a bullet in an 
# OOo list. The goal is to inform the user of the appearance of the bullet 
# without too much verbiage, hence simply "right-pointing arrowhead".
#
chnames[u'\u27a2'] = _("right-pointing arrowhead")

# Translators:  StarOffice/OOo includes private-use unicode character U+E00A 
# as a bullet which looks like the black square: ■ (U+25A0).  Therefore, 
# please use the same translation for this character.
#
chnames[u'\ue00a'] = _("black square")

# Translators:  StarOffice/OOo includes private-use unicode character U+E00C 
# as a bullet which looks like the black diamond: ◆ (U+25C6).  Therefore, 
# please use the same translation for this character.
#
chnames[u'\ue00c'] = _("black diamond")

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
