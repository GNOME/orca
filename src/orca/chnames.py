# -*- coding: utf-8 -*-
# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Provides getCharacterName that maps punctuation marks and other
individual characters into localized words."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from . import mathsymbols
from . import orca_state
from .orca_i18n import _

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
chnames['\u00a0'] = _("no break space")

# Translators: this is the spoken word for the character '¡' (U+00a1)
#
chnames['\u00a1'] = _("inverted exclamation point")

# Translators: this is the spoken word for the character '¢' (U+00a2)
#
chnames['\u00a2'] = _("cents")

# Translators: this is the spoken word for the character '£' (U+00a3)
#
chnames['\u00a3'] = _("pounds")

# Translators: this is the spoken word for the character '¤' (U+00a4)
#
chnames['\u00a4'] = _("currency sign")

# Translators: this is the spoken word for the character '¥' (U+00a5)
#
chnames['\u00a5'] = _("yen")

# Translators: this is the spoken word for the character '¦' (U+00a6)
#
chnames['\u00a6'] = _("broken bar")

# Translators: this is the spoken word for the character '§' (U+00a7)
#
chnames['\u00a7'] = _("section")

# Translators: this is the spoken word for the character '¨' (U+00a8)
#
chnames['\u00a8'] = _("diaeresis")

# Translators: this is the spoken word for the character '©' (U+00a9)
#
chnames['\u00a9'] = _("copyright")

# Translators: this is the spoken word for the character 'ª' (U+00aa)
#
chnames['\u00aa'] = _("superscript a")

# Translators: this is the spoken word for the character '«' (U+00ab)
#
chnames['\u00ab'] = _("left double angle bracket")

# Translators: this is the spoken word for the character '¬' (U+00ac)
#
chnames['\u00ac'] = _("logical not")

# Translators: this is the spoken word for the character '­' (U+00ad)
#
chnames['\u00ad'] = _("soft hyphen")

# Translators: this is the spoken word for the character '®' (U+00ae)
#
chnames['\u00ae'] = _("registered")

# Translators: this is the spoken word for the character '¯' (U+00af)
#
chnames['\u00af'] = _("macron")

# Translators: this is the spoken word for the character '°' (U+00b0)
#
chnames['\u00b0'] = _("degrees")

# Translators: this is the spoken word for the character '±' (U+00b1)
#
chnames['\u00b1'] = _("plus or minus")

# Translators: this is the spoken word for the character '²' (U+00b2)
#
chnames['\u00b2'] = _("superscript 2")

# Translators: this is the spoken word for the character '³' (U+00b3)
#
chnames['\u00b3'] = _("superscript 3")

# Translators: this is the spoken word for the character '´' (U+00b4)
#
chnames['\u00b4'] = _("acute")

# Translators: this is the spoken word for the character 'µ' (U+00b5)
#
chnames['\u00b5'] = _("mu")

# Translators: this is the spoken word for the character '¶' (U+00b6)
#
chnames['\u00b6'] = _("paragraph marker")

# Translators: this is the spoken word for the character '·' (U+00b7)
#
chnames['\u00b7'] = _("middle dot")

# Translators: this is the spoken word for the character '¸' (U+00b8)
#
chnames['\u00b8'] = _("cedilla")

# Translators: this is the spoken word for the character '¹' (U+00b9)
#
chnames['\u00b9'] = _("superscript 1")

# Translators: this is the spoken word for the character 'º' (U+00ba)
#
chnames['\u00ba'] = _("ordinal")

# Translators: this is the spoken word for the character '»' (U+00bb)
#
chnames['\u00bb'] = _("right double angle bracket")

# Translators: this is the spoken word for the character '¼' (U+00bc)
#
chnames['\u00bc'] = _("one fourth")

# Translators: this is the spoken word for the character '½' (U+00bd)
#
chnames['\u00bd'] = _("one half")

# Translators: this is the spoken word for the character '¾' (U+00be)
#
chnames['\u00be'] = _("three fourths")

# Translators: this is the spoken word for the character '¿' (U+00bf)
#
chnames['\u00bf'] = _("inverted question mark")

# Translators: this is the spoken word for the character 'á' (U+00e1)
#
chnames['\u00e1'] = _("a acute")

# Translators: this is the spoken word for the character 'À' (U+00c0)
#
chnames['\u00c0'] = _("A GRAVE")

# Translators: this is the spoken word for the character 'Á' (U+00c1)
#
chnames['\u00c1'] = _("A ACUTE")

# Translators: this is the spoken word for the character 'Â' (U+00c2)
#
chnames['\u00c2'] = _("A CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ã' (U+00c3)
#
chnames['\u00c3'] = _("A TILDE")

# Translators: this is the spoken word for the character 'Ä' (U+00c4)
#
chnames['\u00c4'] = _("A UMLAUT")

# Translators: this is the spoken word for the character 'Å' (U+00c5)
#
chnames['\u00c5'] = _("A RING")

# Translators: this is the spoken word for the character 'Æ' (U+00c6)
#
chnames['\u00c6'] = _("A E")

# Translators: this is the spoken word for the character 'Ç' (U+00c7)
#
chnames['\u00c7'] = _("C CEDILLA")

# Translators: this is the spoken word for the character 'È' (U+00c8)
#
chnames['\u00c8'] = _("E GRAVE")

# Translators: this is the spoken word for the character 'É' (U+00c9)
#
chnames['\u00c9'] = _("E ACUTE")

# Translators: this is the spoken word for the character 'Ê' (U+00ca)
#
chnames['\u00ca'] = _("E CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ë' (U+00cb)
#
chnames['\u00cb'] = _("E UMLAUT")

# Translators: this is the spoken word for the character 'Ì' (U+00cc)
#
chnames['\u00cc'] = _("I GRAVE")

# Translators: this is the spoken word for the character 'Í' (U+00cd)
#
chnames['\u00cd'] = _("I ACUTE")

# Translators: this is the spoken word for the character 'Î' (U+00ce)
#
chnames['\u00ce'] = _("I CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ï' (U+00cf)
#
chnames['\u00cf'] = _("I UMLAUT")

# Translators: this is the spoken word for the character 'Ð' (U+00d0)
#
chnames['\u00d0'] = _("ETH")

# Translators: this is the spoken word for the character 'Ñ' (U+00d1)
#
chnames['\u00d1'] = _("N TILDE")

# Translators: this is the spoken word for the character 'Ò' (U+00d2)
#
chnames['\u00d2'] = _("O GRAVE")

# Translators: this is the spoken word for the character 'Ó' (U+00d3)
#
chnames['\u00d3'] = _("O ACUTE")

# Translators: this is the spoken word for the character 'Ô' (U+00d4)
#
chnames['\u00d4'] = _("O CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Õ' (U+00d5)
#
chnames['\u00d5'] = _("O TILDE")

# Translators: this is the spoken word for the character 'Ö' (U+00d6)
#
chnames['\u00d6'] = _("O UMLAUT")

# Translators: this is the spoken word for the character '×' (U+00d7)
#
chnames['\u00d7'] = _("times")

# Translators: this is the spoken word for the character 'Ø' (U+00d8)
#
chnames['\u00d8'] = _("O STROKE")

# Translators: this is the spoken word for the character 'Ù' (U+00d9)
#
chnames['\u00d9'] = _("U GRAVE")

# Translators: this is the spoken word for the character 'Ú' (U+00da)
#
chnames['\u00da'] = _("U ACUTE")

# Translators: this is the spoken word for the character 'Û' (U+00db)
#
chnames['\u00db'] = _("U CIRCUMFLEX")

# Translators: this is the spoken word for the character 'Ü' (U+00dc)
#
chnames['\u00dc'] = _("U UMLAUT")

# Translators: this is the spoken word for the character 'Ý' (U+00dd)
#
chnames['\u00dd'] = _("Y ACUTE")

# Translators: this is the spoken word for the character 'Þ' (U+00de)
#
chnames['\u00de'] = _("THORN")

# Translators: this is the spoken word for the character 'ß' (U+00df)
#
chnames['\u00df'] = _("s sharp")

# Translators: this is the spoken word for the character 'à' (U+00e0)
#
chnames['\u00e0'] = _("a grave")

# Translators: this is the spoken word for the character 'â' (U+00e2)
#
chnames['\u00e2'] = _("a circumflex")

# Translators: this is the spoken word for the character 'ã' (U+00e3)
#
chnames['\u00e3'] = _("a tilde")

# Translators: this is the spoken word for the character 'ä' (U+00e4)
#
chnames['\u00e4'] = _("a umlaut")

# Translators: this is the spoken word for the character 'å' (U+00e5)
#
chnames['\u00e5'] = _("a ring")

# Translators: this is the spoken word for the character 'æ' (U+00e6)
#
chnames['\u00e6'] = _("a e")

# Translators: this is the spoken word for the character 'ç' (U+00e7)
#
chnames['\u00e7'] = _("c cedilla")

# Translators: this is the spoken word for the character 'è' (U+00e8)
#
chnames['\u00e8'] = _("e grave")

# Translators: this is the spoken word for the character 'é' (U+00e9)
#
chnames['\u00e9'] = _("e acute")

# Translators: this is the spoken word for the character 'ê' (U+00ea)
#
chnames['\u00ea'] = _("e circumflex")

# Translators: this is the spoken word for the character 'ë' (U+00eb)
#
chnames['\u00eb'] = _("e umlaut")

# Translators: this is the spoken word for the character 'ì' (U+00ec)
#
chnames['\u00ec'] = _("i grave")

# Translators: this is the spoken word for the character 'í' (U+00ed)
#
chnames['\u00ed'] = _("i acute")

# Translators: this is the spoken word for the character 'î' (U+00ee)
#
chnames['\u00ee'] = _("i circumflex")

# Translators: this is the spoken word for the character 'ï' (U+00ef)
#
chnames['\u00ef'] = _("i umlaut")

# Translators: this is the spoken word for the character 'ð' (U+00f0)
#
chnames['\u00f0'] = _("eth")

# Translators: this is the spoken word for the character 'ñ' (U+00f1)
#
chnames['\u00f1'] = _("n tilde")

# Translators: this is the spoken word for the character 'ò' (U+00f2)
#
chnames['\u00f2'] = _("o grave")

# Translators: this is the spoken word for the character 'ó' (U+00f3)
#
chnames['\u00f3'] = _("o acute")

# Translators: this is the spoken word for the character 'ô' (U+00f4)
#
chnames['\u00f4'] = _("o circumflex")

# Translators: this is the spoken word for the character 'õ' (U+00f5)
#
chnames['\u00f5'] = _("o tilde")

# Translators: this is the spoken word for the character 'ö' (U+00f6)
#
chnames['\u00f6'] = _("o umlaut")

# Translators: this is the spoken word for the character '÷' (U+00f7)
#
chnames['\u00f7'] = _("divided by")

# Translators: this is the spoken word for the character 'ø' (U+00f8)
#
chnames['\u00f8'] = _("o stroke")

# Translators: this is the spoken word for the character 'þ' (U+00fe)
#
chnames['\u00fe'] = _("thorn")

# Translators: this is the spoken word for the character 'ú' (U+00fa)
#
chnames['\u00fa'] = _("u acute")

# Translators: this is the spoken word for the character 'ù' (U+00f9)
#
chnames['\u00f9'] = _("u grave")

# Translators: this is the spoken word for the character 'û' (U+00fb)
#
chnames['\u00fb'] = _("u circumflex")

# Translators: this is the spoken word for the character 'ü' (U+00fc)
#
chnames['\u00fc'] = _("u umlaut")

# Translators: this is the spoken word for the character 'ý' (U+00fd)
#
chnames['\u00fd'] = _("y acute")

# Translators: this is the spoken word for the character 'ÿ' (U+00ff)
#
chnames['\u00ff'] = _("y umlaut")

# Translators: this is the spoken word for the character 'Ÿ' (U+0178)
#
chnames['\u0178'] = _("Y UMLAUT")

# Translators: this is the spoken word for the character 'ƒ' (U+0192)
#
chnames['\u0192'] = _("florin")

# Translators: this is the spoken word for the character '–' (U+2013)
#
chnames['\u2013'] = _("en dash")

# Translators: this is the spoken word for the left single quote: ‘
# (U+2018)
#
chnames['\u2018'] = _("left single quote")

# Translators: this is the spoken word for the right single quote: ’
# (U+2019)
#
chnames['\u2019'] = _("right single quote")

# Translators: this is the spoken word for the character '‚' (U+201a)
#
chnames['\u201a'] = _("single low quote")

# Translators: this is the spoken word for the character '“' (U+201c)
#
chnames['\u201c'] = _("left double quote")

# Translators: this is the spoken word for the character '”' (U+201d)
#
chnames['\u201d'] = _("right double quote")

# Translators: this is the spoken word for the character '„' (U+201e)
#
chnames['\u201e'] = _("double low quote")

# Translators: this is the spoken word for the character '†' (U+2020)
#
chnames['\u2020'] = _("dagger")

# Translators: this is the spoken word for the character '‡' (U+2021)
#
chnames['\u2021'] = _("double dagger")

# Translators: this is the spoken word for the character '•' (U+2022)
#
chnames['\u2022'] = _("bullet")

# Translators: this is the spoken word for the character '‣' (U+2023)
#
chnames['\u2023'] = _("triangular bullet")

# Translators: this is the spoken word for the character '‰' (U+2030)
#
chnames['\u2030'] = _("per mille")

# Translators: this is the spoken word for the character '′' (U+2032)
#
chnames['\u2032'] = _("prime")

# Translators: this is the spoken word for the character '″' (U+2033)
#
chnames['\u2033'] = _("double prime")

# Translators: this is the spoken word for the character '‴' (U+2034)
#
chnames['\u2034'] = _("triple prime")

# Translators: this is the spoken word for the character '⁃' (U+2043)
#
chnames['\u2043'] = _("hyphen bullet")

# Translators: this is the spoken word for the character '€' (U+20ac)
#
chnames['\u20ac'] = _("euro")

# Translators: this is the spoken word for the character '™' (U+2122)
#
chnames['\u2122'] = _("trademark")

# Translators: this is the spoken word for the character '✓' (U+2713)
# It can be used as a bullet in a list.
#
chnames['\u2713'] = _("check mark")

# Translators: this is the spoken word for the character '✔' (U+2714)
# It can be used as a bullet in a list.
#
chnames['\u2714'] = _("heavy check mark")

# Translators: this is the spoken word for the character 'x' (U+2717)
# This symbol is included here because it can be used as a bullet in 
# an OOo list.  The goal is to inform the user of the appearance of 
# the bullet, while making it clear that it is a bullet and not simply 
# the typed letter 'x'.  "Ballot x" might confuse the user.  Hence the 
# use of "x-shaped bullet".
#
chnames['\u2717'] = _("x-shaped bullet")

# Translators: this is the spoken word for the character '⁰' (U+2070)
#
chnames['\u2070'] = _("superscript 0")

# Translators: this is the spoken word for the character '⁴' (U+2074)
#
chnames['\u2074'] = _("superscript 4")

# Translators: this is the spoken word for the character '⁵' (U+2075)
#
chnames['\u2075'] = _("superscript 5")

# Translators: this is the spoken word for the character '⁶' (U+2076)
#
chnames['\u2076'] = _("superscript 6")

# Translators: this is the spoken word for the character '⁷' (U+2077)
#
chnames['\u2077'] = _("superscript 7")

# Translators: this is the spoken word for the character '⁸' (U+2078)
#
chnames['\u2078'] = _("superscript 8")

# Translators: this is the spoken word for the character '⁹' (U+2079)
#
chnames['\u2079'] = _("superscript 9")

# Translators: this is the spoken word for the character '⁺' (U+207a)
#
chnames['\u207a'] = _("superscript plus")

# Translators: this is the spoken word for the character '⁻' (U+207b)
#
chnames['\u207b'] = _("superscript minus")

# Translators: this is the spoken word for the character '⁼' (U+207c)
#
chnames['\u207c'] = _("superscript equals")

# Translators: this is the spoken word for the character '⁽' (U+207d)
#
chnames['\u207d'] = _("superscript left paren")

# Translators: this is the spoken word for the character '⁾' (U+207e)
#
chnames['\u207e'] = _("superscript right paren")

# Translators: this is the spoken word for the character 'ⁿ' (U+207f)
#
chnames['\u207f'] = _("superscript n")

# Translators: this is the spoken word for the character '₀' (U+2080)
#
chnames['\u2080'] = _("subscript 0")

# Translators: this is the spoken word for the character '₁' (U+2081)
#
chnames['\u2081'] = _("subscript 1")

# Translators: this is the spoken word for the character '₂' (U+2082)
#
chnames['\u2082'] = _("subscript 2")

# Translators: this is the spoken word for the character '₃' (U+2083)
#
chnames['\u2083'] = _("subscript 3")

# Translators: this is the spoken word for the character '₄' (U+2084)
#
chnames['\u2084'] = _("subscript 4")

# Translators: this is the spoken word for the character '₅' (U+2085)
#
chnames['\u2085'] = _("subscript 5")

# Translators: this is the spoken word for the character '₆' (U+2086)
#
chnames['\u2086'] = _("subscript 6")

# Translators: this is the spoken word for the character '₇' (U+2087)
#
chnames['\u2087'] = _("subscript 7")

# Translators: this is the spoken word for the character '₈' (U+2088)
#
chnames['\u2088'] = _("subscript 8")

# Translators: this is the spoken word for the character '₉' (U+2089)
#
chnames['\u2089'] = _("subscript 9")

# Translators: this is the spoken word for the character '₊' (U+208a)
#
chnames['\u208a'] = _("subscript plus")

# Translators: this is the spoken word for the character '₋' (U+208b)
#
chnames['\u208b'] = _("subscript minus")

# Translators: this is the spoken word for the character '₌' (U+208c)
#
chnames['\u208c'] = _("subscript equals")

# Translators: this is the spoken word for the character '₍' (U+208d)
#
chnames['\u208d'] = _("subscript left paren")

# Translators: this is the spoken word for the character '₎' (U+208e)
#
chnames['\u208e'] = _("subscript right paren")

# Translators:  StarOffice/OOo includes private-use unicode character U+E00A 
# as a bullet which looks like the black square: ■ (U+25A0).  Therefore, 
# please use the same translation for this character.
#
chnames['\ue00a'] = _("black square")

# Translators:  StarOffice/OOo includes private-use unicode character U+E00C 
# as a bullet which looks like the black diamond: ◆ (U+25C6).  Therefore, 
# please use the same translation for this character.
#
chnames['\ue00c'] = _("black diamond")

# Translators: This refers to U+FFFC, the "object replacement character."
# This character appears in the accessible text of documents and serves as
# indication of the presence of an object within the text (e.g. an image
# or form field inside a paragraph). In an application which has full
# accessibility support for embedded objects, Orca should present the object
# and NOT speak this character. However, for applications where this support
# is missing, the user can arrow to this character and Orca should not be
# silent. This string is what Orca will speak to the user should this occur.
# More information about this character can be found at:
# * http://www.fileformat.info/info/unicode/char/fffc/index.htm
# * http://en.wikipedia.org/wiki/Specials_(Unicode_block)
#
chnames['\ufffc'] = _("object replacement character")

def getCharacterName(character):
    """Given a character, return its name as people might refer to it
    in ordinary conversation.

    Arguments:
    - character: the character to get the name for

    Returns a string representing the name for the character
    """

    mathName = mathsymbols.getCharacterName(character)
    charName = chnames.get(character)
    if not (charName or mathName):
        return character
    if mathName and not charName:
        return mathName
    if charName and not mathName:
        return charName
    if orca_state.activeScript and orca_state.activeScript.utilities.isInMath():
        return mathName

    return charName
