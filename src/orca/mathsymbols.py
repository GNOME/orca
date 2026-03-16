# Orca
#
# Copyright 2014 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

# pylint: disable=too-many-lines

"""Turns math symbols into their spoken representation."""

import unicodedata

from . import debug
from .orca_i18n import C_  # pylint: disable=import-error

SPEAK_NEVER = 1
SPEAK_ALWAYS = 2
SPEAK_FOR_CHARS = 3
speak_style = SPEAK_ALWAYS  # pylint: disable=invalid-name

fall_back_on_unicode_data = False  # pylint: disable=invalid-name

_all: dict[str, str] = {}
_alnum: dict[str, str] = {}
_arrows: dict[str, str] = {}
_operators: dict[str, str] = {}
_shapes: dict[str, str] = {}
_combining: dict[str, str] = {}

# Note that the following are to help us identify what is likely a math symbol
# (as opposed to one serving the function of an image in "This way up.")
_arrows.update(dict.fromkeys(map(chr, range(0x2190, 0x2200)), ""))
_arrows.update(dict.fromkeys(map(chr, range(0x2750, 0x2800)), ""))
_arrows.update(dict.fromkeys(map(chr, range(0x2B30, 0x2B50)), ""))
_operators.update(dict.fromkeys(map(chr, range(0x2220, 0x2300)), ""))
_operators.update(dict.fromkeys(map(chr, range(0x2A00, 0x2B00)), ""))
_shapes.update(dict.fromkeys(map(chr, range(0x25A0, 0x2600)), ""))

_bold = range(0x1D400, 0x1D434)
_italic = range(0x1D434, 0x1D468)
_bold_italic = range(0x1D468, 0x1D49C)
_script = range(0x1D49C, 0x1D4D0)
_bold_script = range(0x1D4D0, 0x1D504)
_fraktur = range(0x1D504, 0x1D538)
_double_struck = range(0x1D538, 0x1D56C)
_bold_fraktur = range(0x1D56C, 0x1D5A0)
_sans_serif = range(0x1D5A0, 0x1D5D4)
_sans_serif_bold = range(0x1D5D4, 0x1D608)
_sans_serif_italic = range(0x1D608, 0x1D63C)
_sans_serif_bold_italic = range(0x1D63C, 0x1D670)
_monospace = range(0x1D670, 0x1D6A4)
_dotless = range(0x1D6A4, 0x1D6A8)
_bold_greek = range(0x1D6A8, 0x1D6E2)
_italic_greek = range(0x1D6E2, 0x1D71C)
_bold_italic_greek = range(0x1D71C, 0x1D756)
_sans_serif_bold_greek = range(0x1D756, 0x1D790)
_sans_serif_bold_italic_greek = range(0x1D790, 0x1D7CA)
_bold_greek_digamma = range(0x1D7CA, 0x1D7CC)
_bold_digits = range(0x1D7CE, 0x1D7D8)
_double_struck_digits = range(0x1D7D8, 0x1D7E2)
_sans_serif_digits = range(0x1D7E2, 0x1D7EC)
_sans_serif_bold_digits = range(0x1D7EC, 0x1D7F6)
_monospace_digits = range(0x1D7F6, 0x1D800)
_other_double_struck = [0x2102, 0x210D, 0x2115, 0x2119, 0x211A, 0x211D, 0x2124]
_other_fraktur = [0x212D, 0x210C, 0x2111, 0x211C, 0x2128]
_other_italic = [0x210E]
_other_script = [
    0x212C,
    0x2130,
    0x2131,
    0x210B,
    0x2110,
    0x2112,
    0x2133,
    0x211B,
    0x212F,
    0x210A,
    0x2134,
]

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD = C_("math symbol", "bold %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
ITALIC = C_("math symbol", "italic %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD_ITALIC = C_("math symbol", "bold italic %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SCRIPT = C_("math symbol", "script %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD_SCRIPT = C_("math symbol", "bold script %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
FRAKTUR = C_("math symbol", "fraktur %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
DOUBLE_STRUCK = C_("math symbol", "double-struck %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD_FRAKTUR = C_("math symbol", "bold fraktur %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF = C_("math symbol", "sans-serif %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF_BOLD = C_("math symbol", "sans-serif bold %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF_ITALIC = C_("math symbol", "sans-serif italic %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF_BOLD_ITALIC = C_("math symbol", "sans-serif bold italic %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
MONOSPACE = C_("math symbol", "monospace %s")

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
DOTLESS = C_("math symbol", "dotless %s")

# Translators: this is the spoken representation for the character '←' (U+2190)
_arrows["\u2190"] = C_("math symbol", "left arrow")

# Translators: this is the spoken representation for the character '↑' (U+2191)
_arrows["\u2191"] = C_("math symbol", "up arrow")

# Translators: this is the spoken representation for the character '→' (U+2192)
_arrows["\u2192"] = C_("math symbol", "right arrow")

# Translators: this is the spoken representation for the character '↓' (U+2193)
_arrows["\u2193"] = C_("math symbol", "down arrow")

# Translators: this is the spoken representation for the character '↔' (U+2194)
_arrows["\u2194"] = C_("math symbol", "left right arrow")

# Translators: this is the spoken representation for the character '↕' (U+2195)
_arrows["\u2195"] = C_("math symbol", "up down arrow")

# Translators: this is the spoken representation for the character '↖' (U+2196)
_arrows["\u2196"] = C_("math symbol", "north west arrow")

# Translators: this is the spoken representation for the character '↗' (U+2197)
_arrows["\u2197"] = C_("math symbol", "north east arrow")

# Translators: this is the spoken representation for the character '↘' (U+2198)
_arrows["\u2198"] = C_("math symbol", "south east arrow")

# Translators: this is the spoken representation for the character '↤' (U+21a4)
_arrows["\u21a4"] = C_("math symbol", "left arrow from bar")

# Translators: this is the spoken representation for the character '↥' (U+21a5)
_arrows["\u21a5"] = C_("math symbol", "up arrow from bar")

# Translators: this is the spoken representation for the character '↦' (U+21a6)
_arrows["\u21a6"] = C_("math symbol", "right arrow from bar")

# Translators: this is the spoken representation for the character '↧' (U+21a7)
_arrows["\u21a7"] = C_("math symbol", "down arrow from bar")

# Translators: this is the spoken representation for the character '⇐' (U+21d0)
_arrows["\u21d0"] = C_("math symbol", "left double arrow")

# Translators: this is the spoken representation for the character '⇑' (U+21d1)
_arrows["\u21d1"] = C_("math symbol", "up double arrow")

# Translators: this is the spoken representation for the character '⇒' (U+21d2)
_arrows["\u21d2"] = C_("math symbol", "right double arrow")

# Translators: this is the spoken representation for the character '⇓' (U+21d3)
_arrows["\u21d3"] = C_("math symbol", "down double arrow")

# Translators: this is the spoken representation for the character '⇔' (U+21d4)
_arrows["\u21d4"] = C_("math symbol", "left right double arrow")

# Translators: this is the spoken representation for the character '⇕' (U+21d5)
_arrows["\u21d5"] = C_("math symbol", "up down double arrow")

# Translators: this is the spoken representation for the character '⇖' (U+21d6)
_arrows["\u21d6"] = C_("math symbol", "north west double arrow")

# Translators: this is the spoken representation for the character '⇗' (U+21d7)
_arrows["\u21d7"] = C_("math symbol", "north east double arrow")

# Translators: this is the spoken representation for the character '⇘' (U+21d8)
_arrows["\u21d8"] = C_("math symbol", "south east double arrow")

# Translators: this is the spoken representation for the character '⇙' (U+21d9)
_arrows["\u21d9"] = C_("math symbol", "south west double arrow")

# Translators: this is the spoken representation for the character '➔' (U+2794)
_arrows["\u2794"] = C_("math symbol", "right-pointing arrow")

# Translators: this is the spoken representation for the character '➢' (U+27a2)
_arrows["\u27a2"] = C_("math symbol", "right-pointing arrowhead")

# Translators: this is the spoken word for the character '-' (U+002d) when used
# as a MathML operator.
_operators["\u002d"] = C_("math symbol", "minus")

# Translators: this is the spoken word for the character '<' (U+003c) when used
# as a MathML operator.
_operators["\u003c"] = C_("math symbol", "less than")

# Translators: this is the spoken word for the character '>' (U+003e) when used
# as a MathML operator.
_operators["\u003e"] = C_("math symbol", "greater than")

# Translators: this is the spoken word for the character '^' (U+005e) when used
# as a MathML operator.
_operators["\u005e"] = C_("math symbol", "circumflex")

# Translators: this is the spoken word for the character 'ˇ' (U+02c7) when used
# as a MathML operator.
_operators["\u02c7"] = C_("math symbol", "háček")

# Translators: this is the spoken word for the character '˘' (U+02d8) when used
# as a MathML operator.
_operators["\u02d8"] = C_("math symbol", "breve")

# Translators: this is the spoken word for the character '˙' (U+02d9) when used
# as a MathML operator.
_operators["\u02d9"] = C_("math symbol", "dot")

# Translators: this is the spoken word for the character '‖' (U+2016) when used
# as a MathML operator.
_operators["\u2016"] = C_("math symbol", "double vertical line")

# Translators: this is the spoken representation for the character '…' (U+2026)
_operators["\u2026"] = C_("math symbol", "horizontal ellipsis")

# Translators: this is the spoken representation for the character '∀' (U+2200)
_operators["\u2200"] = C_("math symbol", "for all")

# Translators: this is the spoken representation for the character '∁' (U+2201)
_operators["\u2201"] = C_("math symbol", "complement")

# Translators: this is the spoken representation for the character '∂' (U+2202)
_operators["\u2202"] = C_("math symbol", "partial differential")

# Translators: this is the spoken representation for the character '∃' (U+2203)
_operators["\u2203"] = C_("math symbol", "there exists")

# Translators: this is the spoken representation for the character '∄' (U+2204)
_operators["\u2204"] = C_("math symbol", "there does not exist")

# Translators: this is the spoken representation for the character '∅' (U+2205)
_operators["\u2205"] = C_("math symbol", "empty set")

# Translators: this is the spoken representation for the character '∆' (U+2206)
_operators["\u2206"] = C_("math symbol", "increment")

# Translators: this is the spoken representation for the character '∇' (U+2207)
_operators["\u2207"] = C_("math symbol", "nabla")

# Translators: this is the spoken representation for the character '∈' (U+2208)
_operators["\u2208"] = C_("math symbol", "element of")

# Translators: this is the spoken representation for the character '∉' (U+2209)
_operators["\u2209"] = C_("math symbol", "not an element of")

# Translators: this is the spoken representation for the character '∊' (U+220a)
_operators["\u220a"] = C_("math symbol", "small element of")

# Translators: this is the spoken representation for the character '∋' (U+220b)
_operators["\u220b"] = C_("math symbol", "contains as a member")

# Translators: this is the spoken representation for the character '∌' (U+220c)
_operators["\u220c"] = C_("math symbol", "does not contain as a member")

# Translators: this is the spoken representation for the character '∍' (U+220d)
_operators["\u220d"] = C_("math symbol", "small contains as a member")

# Translators: this is the spoken representation for the character '∎' (U+220e)
_operators["\u220e"] = C_("math symbol", "end of proof")

# Translators: this is the spoken representation for the character '∏' (U+220f)
_operators["\u220f"] = C_("math symbol", "product")

# Translators: this is the spoken representation for the character '∐' (U+2210)
_operators["\u2210"] = C_("math symbol", "coproduct")

# Translators: this is the spoken representation for the character '∑' (U+2211)
_operators["\u2211"] = C_("math symbol", "sum")

# Translators: this is the spoken representation for the character '−' (U+2212)
_operators["\u2212"] = C_("math symbol", "minus")

# Translators: this is the spoken representation for the character '∓' (U+2213)
_operators["\u2213"] = C_("math symbol", "minus or plus")

# Translators: this is the spoken representation for the character '∔' (U+2214)
_operators["\u2214"] = C_("math symbol", "dot plus")

# Translators: this is the spoken representation for the character '∕' (U+2215)
_operators["\u2215"] = C_("math symbol", "division slash")

# Translators: this is the spoken representation for the character '∖' (U+2216)
_operators["\u2216"] = C_("math symbol", "set minus")

# Translators: this is the spoken representation for the character '∗' (U+2217)
_operators["\u2217"] = C_("math symbol", "asterisk operator")

# Translators: this is the spoken representation for the character '∘' (U+2218)
_operators["\u2218"] = C_("math symbol", "ring operator")

# Translators: this is the spoken representation for the character '∙' (U+2219)
_operators["\u2219"] = C_("math symbol", "bullet operator")

# Translators: this is the spoken representation for the character '√' (U+221a)
_operators["\u221a"] = C_("math symbol", "square root")

# Translators: this is the spoken representation for the character '∛' (U+221b)
_operators["\u221b"] = C_("math symbol", "cube root")

# Translators: this is the spoken representation for the character '∜' (U+221c)
_operators["\u221c"] = C_("math symbol", "fourth root")

# Translators: this is the spoken representation for the character '∝' (U+221d)
_operators["\u221d"] = C_("math symbol", "proportional to")

# Translators: this is the spoken representation for the character '∞' (U+221e)
_operators["\u221e"] = C_("math symbol", "infinity")

# Translators: this is the spoken representation for the character '∟' (U+221f)
_operators["\u221f"] = C_("math symbol", "right angle")

# Translators: this is the spoken representation for the character '∠' (U+2220)
_operators["\u2220"] = C_("math symbol", "angle")

# Translators: this is the spoken representation for the character '∡' (U+2221)
_operators["\u2221"] = C_("math symbol", "measured angle")

# Translators: this is the spoken representation for the character '∢' (U+2222)
_operators["\u2222"] = C_("math symbol", "spherical angle")

# Translators: this is the spoken representation for the character '∣' (U+2223)
_operators["\u2223"] = C_("math symbol", "divides")

# Translators: this is the spoken representation for the character '∤' (U+2224)
_operators["\u2224"] = C_("math symbol", "does not divide")

# Translators: this is the spoken representation for the character '∥' (U+2225)
_operators["\u2225"] = C_("math symbol", "parallel to")

# Translators: this is the spoken representation for the character '∦' (U+2226)
_operators["\u2226"] = C_("math symbol", "not parallel to")

# Translators: this is the spoken representation for the character '∧' (U+2227)
_operators["\u2227"] = C_("math symbol", "logical and")

# Translators: this is the spoken representation for the character '∨' (U+2228)
_operators["\u2228"] = C_("math symbol", "logical or")

# Translators: this is the spoken representation for the character '∩' (U+2229)
_operators["\u2229"] = C_("math symbol", "intersection")

# Translators: this is the spoken representation for the character '∪' (U+222a)
_operators["\u222a"] = C_("math symbol", "union")

# Translators: this is the spoken representation for the character '∫' (U+222b)
_operators["\u222b"] = C_("math symbol", "integral")

# Translators: this is the spoken representation for the character '∬' (U+222c)
_operators["\u222c"] = C_("math symbol", "double integral")

# Translators: this is the spoken representation for the character '∭' (U+222d)
_operators["\u222d"] = C_("math symbol", "triple integral")

# Translators: this is the spoken representation for the character '∮' (U+222e)
_operators["\u222e"] = C_("math symbol", "contour integral")

# Translators: this is the spoken representation for the character '∯' (U+222f)
_operators["\u222f"] = C_("math symbol", "surface integral")

# Translators: this is the spoken representation for the character '∰' (U+2230)
_operators["\u2230"] = C_("math symbol", "volume integral")

# Translators: this is the spoken representation for the character '∱' (U+2231)
_operators["\u2231"] = C_("math symbol", "clockwise integral")

# Translators: this is the spoken representation for the character '∲' (U+2232)
_operators["\u2232"] = C_("math symbol", "clockwise contour integral")

# Translators: this is the spoken representation for the character '∳' (U+2233)
_operators["\u2233"] = C_("math symbol", "anticlockwise contour integral")

# Translators: this is the spoken representation for the character '∴' (U+2234)
_operators["\u2234"] = C_("math symbol", "therefore")

# Translators: this is the spoken representation for the character '∵' (U+2235)
_operators["\u2235"] = C_("math symbol", "because")

# Translators: this is the spoken representation for the character '∶' (U+2236)
_operators["\u2236"] = C_("math symbol", "ratio")

# Translators: this is the spoken representation for the character '∷' (U+2237)
_operators["\u2237"] = C_("math symbol", "proportion")

# Translators: this is the spoken representation for the character '∸' (U+2238)
_operators["\u2238"] = C_("math symbol", "dot minus")

# Translators: this is the spoken representation for the character '∹' (U+2239)
_operators["\u2239"] = C_("math symbol", "excess")

# Translators: this is the spoken representation for the character '∺' (U+223a)
_operators["\u223a"] = C_("math symbol", "geometric proportion")

# Translators: this is the spoken representation for the character '∻' (U+223b)
_operators["\u223b"] = C_("math symbol", "homothetic")

# Translators: this is the spoken representation for the character '∼' (U+223c)
_operators["\u223c"] = C_("math symbol", "tilde")

# Translators: this is the spoken representation for the character '∽' (U+223d)
_operators["\u223d"] = C_("math symbol", "reversed tilde")

# Translators: this is the spoken representation for the character '∾' (U+223e)
_operators["\u223e"] = C_("math symbol", "inverted lazy S")

# Translators: this is the spoken representation for the character '∿' (U+223f)
_operators["\u223f"] = C_("math symbol", "sine wave")

# Translators: this is the spoken representation for the character '≀' (U+2240)
_operators["\u2240"] = C_("math symbol", "wreath product")

# Translators: this is the spoken representation for the character '≁' (U+2241)
_operators["\u2241"] = C_("math symbol", "not tilde")

# Translators: this is the spoken representation for the character '≂' (U+2242)
_operators["\u2242"] = C_("math symbol", "minus tilde")

# Translators: this is the spoken representation for the character '≃' (U+2243)
_operators["\u2243"] = C_("math symbol", "asymptotically equal to")

# Translators: this is the spoken representation for the character '≄' (U+2244)
_operators["\u2244"] = C_("math symbol", "not asymptotically equal to")

# Translators: this is the spoken representation for the character '≅' (U+2245)
_operators["\u2245"] = C_("math symbol", "approximately equal to")

# Translators: this is the spoken representation for the character '≆' (U+2246)
_operators["\u2246"] = C_("math symbol", "approximately but not actually equal to")

# Translators: this is the spoken representation for the character '≇' (U+2247)
_operators["\u2247"] = C_("math symbol", "neither approximately nor actually equal to")

# Translators: this is the spoken representation for the character '≈' (U+2248)
_operators["\u2248"] = C_("math symbol", "almost equal to")

# Translators: this is the spoken representation for the character '≉' (U+2249)
_operators["\u2249"] = C_("math symbol", "not almost equal to")

# Translators: this is the spoken representation for the character '≊' (U+224a)
_operators["\u224a"] = C_("math symbol", "almost equal or equal to")

# Translators: this is the spoken representation for the character '≋' (U+224b)
_operators["\u224b"] = C_("math symbol", "triple tilde")

# Translators: this is the spoken representation for the character '≌' (U+224c)
_operators["\u224c"] = C_("math symbol", "all equal to")

# Translators: this is the spoken representation for the character '≍' (U+224d)
_operators["\u224d"] = C_("math symbol", "equivalent to")

# Translators: this is the spoken representation for the character '≎' (U+224e)
_operators["\u224e"] = C_("math symbol", "geometrically equivalent to")

# Translators: this is the spoken representation for the character '≏' (U+224f)
_operators["\u224f"] = C_("math symbol", "difference between")

# Translators: this is the spoken representation for the character '≐' (U+2250)
_operators["\u2250"] = C_("math symbol", "approaches the limit")

# Translators: this is the spoken representation for the character '≑' (U+2251)
_operators["\u2251"] = C_("math symbol", "geometrically equal to")

# Translators: this is the spoken representation for the character '≒' (U+2252)
_operators["\u2252"] = C_("math symbol", "approximately equal to or the image of")

# Translators: this is the spoken representation for the character '≓' (U+2253)
_operators["\u2253"] = C_("math symbol", "image of or approximately equal to")

# Translators: this is the spoken representation for the character '≔' (U+2254)
_operators["\u2254"] = C_("math symbol", "colon equals")

# Translators: this is the spoken representation for the character '≕' (U+2255)
_operators["\u2255"] = C_("math symbol", "equals colon")

# Translators: this is the spoken representation for the character '≖' (U+2256)
_operators["\u2256"] = C_("math symbol", "ring in equal to")

# Translators: this is the spoken representation for the character '≗' (U+2257)
_operators["\u2257"] = C_("math symbol", "ring equal to")

# Translators: this is the spoken representation for the character '≘' (U+2258)
_operators["\u2258"] = C_("math symbol", "corresponds to")

# Translators: this is the spoken representation for the character '≙' (U+2259)
_operators["\u2259"] = C_("math symbol", "estimates")

# Translators: this is the spoken representation for the character '≚' (U+225a)
_operators["\u225a"] = C_("math symbol", "equiangular to")

# Translators: this is the spoken representation for the character '≛' (U+225b)
_operators["\u225b"] = C_("math symbol", "star equals")

# Translators: this is the spoken representation for the character '≜' (U+225c)
_operators["\u225c"] = C_("math symbol", "delta equal to")

# Translators: this is the spoken representation for the character '≝' (U+225d)
_operators["\u225d"] = C_("math symbol", "equal to by definition")

# Translators: this is the spoken representation for the character '≞' (U+225e)
_operators["\u225e"] = C_("math symbol", "measured by")

# Translators: this is the spoken representation for the character '≟' (U+225f)
_operators["\u225f"] = C_("math symbol", "questioned equal to")

# Translators: this is the spoken representation for the character '≠' (U+2260)
_operators["\u2260"] = C_("math symbol", "not equal to")

# Translators: this is the spoken representation for the character '≡' (U+2261)
_operators["\u2261"] = C_("math symbol", "identical to")

# Translators: this is the spoken representation for the character '≢' (U+2262)
_operators["\u2262"] = C_("math symbol", "not identical to")

# Translators: this is the spoken representation for the character '≣' (U+2263)
_operators["\u2263"] = C_("math symbol", "strictly equivalent to")

# Translators: this is the spoken representation for the character '≤' (U+2264)
_operators["\u2264"] = C_("math symbol", "less than or equal to")

# Translators: this is the spoken representation for the character '≥' (U+2265)
_operators["\u2265"] = C_("math symbol", "greater than or equal to")

# Translators: this is the spoken representation for the character '≦' (U+2266)
_operators["\u2266"] = C_("math symbol", "less than over equal to")

# Translators: this is the spoken representation for the character '≧' (U+2267)
_operators["\u2267"] = C_("math symbol", "greater than over equal to")

# Translators: this is the spoken representation for the character '≨' (U+2268)
_operators["\u2268"] = C_("math symbol", "less than but not equal to")

# Translators: this is the spoken representation for the character '≩' (U+2269)
_operators["\u2269"] = C_("math symbol", "greater than but not equal to")

# Translators: this is the spoken representation for the character '≪' (U+226a)
_operators["\u226a"] = C_("math symbol", "much less than")

# Translators: this is the spoken representation for the character '≫' (U+226b)
_operators["\u226b"] = C_("math symbol", "much greater than")

# Translators: this is the spoken representation for the character '≬' (U+226c)
_operators["\u226c"] = C_("math symbol", "between")

# Translators: this is the spoken representation for the character '≭' (U+226d)
_operators["\u226d"] = C_("math symbol", "not equivalent to")

# Translators: this is the spoken representation for the character '≮' (U+226e)
_operators["\u226e"] = C_("math symbol", "not less than")

# Translators: this is the spoken representation for the character '≯' (U+226f)
_operators["\u226f"] = C_("math symbol", "not greater than")

# Translators: this is the spoken representation for the character '≰' (U+2270)
_operators["\u2270"] = C_("math symbol", "neither less than nor equal to")

# Translators: this is the spoken representation for the character '≱' (U+2271)
_operators["\u2271"] = C_("math symbol", "neither greater than nor equal to")

# Translators: this is the spoken representation for the character '≲' (U+2272)
_operators["\u2272"] = C_("math symbol", "less than or equivalent to")

# Translators: this is the spoken representation for the character '≳' (U+2273)
_operators["\u2273"] = C_("math symbol", "greater than or equivalent to")

# Translators: this is the spoken representation for the character '≴' (U+2274)
_operators["\u2274"] = C_("math symbol", "neither less than nor equivalent to")

# Translators: this is the spoken representation for the character '≵' (U+2275)
_operators["\u2275"] = C_("math symbol", "neither greater than nor equivalent to")

# Translators: this is the spoken representation for the character '≶' (U+2276)
_operators["\u2276"] = C_("math symbol", "less than or greater than")

# Translators: this is the spoken representation for the character '≷' (U+2277)
_operators["\u2277"] = C_("math symbol", "greater than or less than")

# Translators: this is the spoken representation for the character '≸' (U+2278)
_operators["\u2278"] = C_("math symbol", "neither less than nor greater than")

# Translators: this is the spoken representation for the character '≹' (U+2279)
_operators["\u2279"] = C_("math symbol", "neither greater than nor less than")

# Translators: this is the spoken representation for the character '≺' (U+227a)
_operators["\u227a"] = C_("math symbol", "precedes")

# Translators: this is the spoken representation for the character '≻' (U+227b)
_operators["\u227b"] = C_("math symbol", "succeeds")

# Translators: this is the spoken representation for the character '≼' (U+227c)
_operators["\u227c"] = C_("math symbol", "precedes or equal to")

# Translators: this is the spoken representation for the character '≽' (U+227d)
_operators["\u227d"] = C_("math symbol", "succeeds or equal to")

# Translators: this is the spoken representation for the character '≾' (U+227e)
_operators["\u227e"] = C_("math symbol", "precedes or equivalent to")

# Translators: this is the spoken representation for the character '≿' (U+227f)
_operators["\u227f"] = C_("math symbol", "succeeds or equivalent to")

# Translators: this is the spoken representation for the character '⊀' (U+2280)
_operators["\u2280"] = C_("math symbol", "does not precede")

# Translators: this is the spoken representation for the character '⊁' (U+2281)
_operators["\u2281"] = C_("math symbol", "does not succeed")

# Translators: this is the spoken representation for the character '⊂' (U+2282)
_operators["\u2282"] = C_("math symbol", "subset of")

# Translators: this is the spoken representation for the character '⊃' (U+2283)
_operators["\u2283"] = C_("math symbol", "superset of")

# Translators: this is the spoken representation for the character '⊄' (U+2284)
_operators["\u2284"] = C_("math symbol", "not a subset of")

# Translators: this is the spoken representation for the character '⊅' (U+2285)
_operators["\u2285"] = C_("math symbol", "not a superset of")

# Translators: this is the spoken representation for the character '⊆' (U+2286)
_operators["\u2286"] = C_("math symbol", "subset of or equal to")

# Translators: this is the spoken representation for the character '⊇' (U+2287)
_operators["\u2287"] = C_("math symbol", "superset of or equal to")

# Translators: this is the spoken representation for the character '⊈' (U+2288)
_operators["\u2288"] = C_("math symbol", "neither a subset of nor equal to")

# Translators: this is the spoken representation for the character '⊉' (U+2289)
_operators["\u2289"] = C_("math symbol", "neither a superset of nor equal to")

# Translators: this is the spoken representation for the character '⊊' (U+228a)
_operators["\u228a"] = C_("math symbol", "subset of with not equal to")

# Translators: this is the spoken representation for the character '⊋' (U+228b)
_operators["\u228b"] = C_("math symbol", "superset of with not equal to")

# Translators: this is the spoken representation for the character '⊌' (U+228c)
_operators["\u228c"] = C_("math symbol", "multiset")

# Translators: this is the spoken representation for the character '⊍' (U+228d)
_operators["\u228d"] = C_("math symbol", "multiset multiplication")

# Translators: this is the spoken representation for the character '⊎' (U+228e)
_operators["\u228e"] = C_("math symbol", "multiset union")

# Translators: this is the spoken representation for the character '⊏' (U+228f)
_operators["\u228f"] = C_("math symbol", "square image of")

# Translators: this is the spoken representation for the character '⊐' (U+2290)
_operators["\u2290"] = C_("math symbol", "square original of")

# Translators: this is the spoken representation for the character '⊑' (U+2291)
_operators["\u2291"] = C_("math symbol", "square image of or equal to")

# Translators: this is the spoken representation for the character '⊒' (U+2292)
_operators["\u2292"] = C_("math symbol", "square original of or equal to")

# Translators: this is the spoken representation for the character '⊓' (U+2293)
_operators["\u2293"] = C_("math symbol", "square cap")

# Translators: this is the spoken representation for the character '⊔' (U+2294)
_operators["\u2294"] = C_("math symbol", "square cup")

# Translators: this is the spoken representation for the character '⊕' (U+2295)
_operators["\u2295"] = C_("math symbol", "circled plus")

# Translators: this is the spoken representation for the character '⊖' (U+2296)
_operators["\u2296"] = C_("math symbol", "circled minus")

# Translators: this is the spoken representation for the character '⊗' (U+2297)
_operators["\u2297"] = C_("math symbol", "circled times")

# Translators: this is the spoken representation for the character '⊘' (U+2298)
_operators["\u2298"] = C_("math symbol", "circled division slash")

# Translators: this is the spoken representation for the character '⊙' (U+2299)
_operators["\u2299"] = C_("math symbol", "circled dot operator")

# Translators: this is the spoken representation for the character '⊚' (U+229a)
_operators["\u229a"] = C_("math symbol", "circled ring operator")

# Translators: this is the spoken representation for the character '⊛' (U+229b)
_operators["\u229b"] = C_("math symbol", "circled asterisk operator")

# Translators: this is the spoken representation for the character '⊜' (U+229c)
_operators["\u229c"] = C_("math symbol", "circled equals")

# Translators: this is the spoken representation for the character '⊝' (U+229d)
_operators["\u229d"] = C_("math symbol", "circled dash")

# Translators: this is the spoken representation for the character '⊞' (U+229e)
_operators["\u229e"] = C_("math symbol", "squared plus")

# Translators: this is the spoken representation for the character '⊟' (U+229f)
_operators["\u229f"] = C_("math symbol", "squared minus")

# Translators: this is the spoken representation for the character '⊠' (U+22a0)
_operators["\u22a0"] = C_("math symbol", "squared times")

# Translators: this is the spoken representation for the character '⊡' (U+22a1)
_operators["\u22a1"] = C_("math symbol", "squared dot operator")

# Translators: this is the spoken representation for the character '⊢' (U+22a2)
_operators["\u22a2"] = C_("math symbol", "right tack")

# Translators: this is the spoken representation for the character '⊣' (U+22a3)
_operators["\u22a3"] = C_("math symbol", "left tack")

# Translators: this is the spoken representation for the character '⊤' (U+22a4)
_operators["\u22a4"] = C_("math symbol", "down tack")

# Translators: this is the spoken representation for the character '⊥' (U+22a5)
_operators["\u22a5"] = C_("math symbol", "up tack")

# Translators: this is the spoken representation for the character '⊦' (U+22a6)
_operators["\u22a6"] = C_("math symbol", "assertion")

# Translators: this is the spoken representation for the character '⊧' (U+22a7)
_operators["\u22a7"] = C_("math symbol", "models")

# Translators: this is the spoken representation for the character '⊨' (U+22a8)
_operators["\u22a8"] = C_("math symbol", "true")

# Translators: this is the spoken representation for the character '⊩' (U+22a9)
_operators["\u22a9"] = C_("math symbol", "forces")

# Translators: this is the spoken representation for the character '⊪' (U+22aa)
_operators["\u22aa"] = C_("math symbol", "triple vertical bar right turnstile")

# Translators: this is the spoken representation for the character '⊫' (U+22ab)
_operators["\u22ab"] = C_("math symbol", "double vertical bar double right turnstile")

# Translators: this is the spoken representation for the character '⊬' (U+22ac)
_operators["\u22ac"] = C_("math symbol", "does not prove")

# Translators: this is the spoken representation for the character '⊭' (U+22ad)
_operators["\u22ad"] = C_("math symbol", "not true")

# Translators: this is the spoken representation for the character '⊮' (U+22ae)
_operators["\u22ae"] = C_("math symbol", "does not force")

# Translators: this is the spoken representation for the character '⊯' (U+22af)
_operators["\u22af"] = C_("math symbol", "negated double vertical bar double right turnstile")

# Translators: this is the spoken representation for the character '⊰' (U+22b0)
_operators["\u22b0"] = C_("math symbol", "precedes under relation")

# Translators: this is the spoken representation for the character '⊱' (U+22b1)
_operators["\u22b1"] = C_("math symbol", "succeeds under relation")

# Translators: this is the spoken representation for the character '⊲' (U+22b2)
_operators["\u22b2"] = C_("math symbol", "normal subgroup of")

# Translators: this is the spoken representation for the character '⊳' (U+22b3)
_operators["\u22b3"] = C_("math symbol", "contains as normal subgroup")

# Translators: this is the spoken representation for the character '⊴' (U+22b4)
_operators["\u22b4"] = C_("math symbol", "normal subgroup of or equal to")

# Translators: this is the spoken representation for the character '⊵' (U+22b5)
_operators["\u22b5"] = C_("math symbol", "contains as normal subgroup of or equal to")

# Translators: this is the spoken representation for the character '⊶' (U+22b6)
_operators["\u22b6"] = C_("math symbol", "original of")

# Translators: this is the spoken representation for the character '⊷' (U+22b7)
_operators["\u22b7"] = C_("math symbol", "image of")

# Translators: this is the spoken representation for the character '⊸' (U+22b8)
_operators["\u22b8"] = C_("math symbol", "multimap")

# Translators: this is the spoken representation for the character '⊹' (U+22b9)
_operators["\u22b9"] = C_("math symbol", "hermitian conjugate matrix")

# Translators: this is the spoken representation for the character '⊺' (U+22ba)
_operators["\u22ba"] = C_("math symbol", "intercalate")

# Translators: this is the spoken representation for the character '⊻' (U+22bb)
_operators["\u22bb"] = C_("math symbol", "xor")

# Translators: this is the spoken representation for the character '⊼' (U+22bc)
_operators["\u22bc"] = C_("math symbol", "nand")

# Translators: this is the spoken representation for the character '⊽' (U+22bd)
_operators["\u22bd"] = C_("math symbol", "nor")

# Translators: this is the spoken representation for the character '⊾' (U+22be)
_operators["\u22be"] = C_("math symbol", "right angle with arc")

# Translators: this is the spoken representation for the character '⊿' (U+22bf)
_operators["\u22bf"] = C_("math symbol", "right triangle")

# Translators: this is the spoken representation for the character '⋀' (U+22c0)
_operators["\u22c0"] = C_("math symbol", "logical and")

# Translators: this is the spoken representation for the character '⋁' (U+22c1)
_operators["\u22c1"] = C_("math symbol", "logical or")

# Translators: this is the spoken representation for the character '⋂' (U+22c2)
_operators["\u22c2"] = C_("math symbol", "intersection")

# Translators: this is the spoken representation for the character '⋃' (U+22c3)
_operators["\u22c3"] = C_("math symbol", "union")

# Translators: this is the spoken representation for the character '⋄' (U+22c4)
_operators["\u22c4"] = C_("math symbol", "diamond operator")

# Translators: this is the spoken representation for the character '⋅' (U+22c5)
_operators["\u22c5"] = C_("math symbol", "dot operator")

# Translators: this is the spoken representation for the character '⋆' (U+22c6)
_operators["\u22c6"] = C_("math symbol", "star operator")

# Translators: this is the spoken representation for the character '⋇' (U+22c7)
_operators["\u22c7"] = C_("math symbol", "division times")

# Translators: this is the spoken representation for the character '⋈' (U+22c8)
_operators["\u22c8"] = C_("math symbol", "bowtie")

# Translators: this is the spoken representation for the character '⋉' (U+22c9)
_operators["\u22c9"] = C_("math symbol", "left normal factor semidirect product")

# Translators: this is the spoken representation for the character '⋊' (U+22ca)
_operators["\u22ca"] = C_("math symbol", "right normal factor semidirect product")

# Translators: this is the spoken representation for the character '⋋' (U+22cb)
_operators["\u22cb"] = C_("math symbol", "left semidirect product")

# Translators: this is the spoken representation for the character '⋌' (U+22cc)
_operators["\u22cc"] = C_("math symbol", "right semidirect product")

# Translators: this is the spoken representation for the character '⋍' (U+22cd)
_operators["\u22cd"] = C_("math symbol", "reversed tilde equals")

# Translators: this is the spoken representation for the character '⋎' (U+22ce)
_operators["\u22ce"] = C_("math symbol", "curly logical or")

# Translators: this is the spoken representation for the character '⋏' (U+22cf)
_operators["\u22cf"] = C_("math symbol", "curly logical and")

# Translators: this is the spoken representation for the character '⋐' (U+22d0)
_operators["\u22d0"] = C_("math symbol", "double subset")

# Translators: this is the spoken representation for the character '⋑' (U+22d1)
_operators["\u22d1"] = C_("math symbol", "double superset")

# Translators: this is the spoken representation for the character '⋒' (U+22d2)
_operators["\u22d2"] = C_("math symbol", "double intersection")

# Translators: this is the spoken representation for the character '⋓' (U+22d3)
_operators["\u22d3"] = C_("math symbol", "double union")

# Translators: this is the spoken representation for the character '⋔' (U+22d4)
_operators["\u22d4"] = C_("math symbol", "pitchfork")

# Translators: this is the spoken representation for the character '⋕' (U+22d5)
_operators["\u22d5"] = C_("math symbol", "equal and parallel to")

# Translators: this is the spoken representation for the character '⋖' (U+22d6)
_operators["\u22d6"] = C_("math symbol", "less than with dot")

# Translators: this is the spoken representation for the character '⋗' (U+22d7)
_operators["\u22d7"] = C_("math symbol", "greater than with dot")

# Translators: this is the spoken representation for the character '⋘' (U+22d8)
_operators["\u22d8"] = C_("math symbol", "very much less than")

# Translators: this is the spoken representation for the character '⋙' (U+22d9)
_operators["\u22d9"] = C_("math symbol", "very much greater than")

# Translators: this is the spoken representation for the character '⋚' (U+22da)
_operators["\u22da"] = C_("math symbol", "less than equal to or greater than")

# Translators: this is the spoken representation for the character '⋛' (U+22db)
_operators["\u22db"] = C_("math symbol", "greater than equal to or less than")

# Translators: this is the spoken representation for the character '⋜' (U+22dc)
_operators["\u22dc"] = C_("math symbol", "equal to or less than")

# Translators: this is the spoken representation for the character '⋝' (U+22dd)
_operators["\u22dd"] = C_("math symbol", "equal to or greater than")

# Translators: this is the spoken representation for the character '⋝' (U+22de)
_operators["\u22de"] = C_("math symbol", "equal to or precedes")

# Translators: this is the spoken representation for the character '⋝' (U+22df)
_operators["\u22df"] = C_("math symbol", "equal to or succeeds")

# Translators: this is the spoken representation for the character '⋠' (U+22e0)
_operators["\u22e0"] = C_("math symbol", "does not precede or equal")

# Translators: this is the spoken representation for the character '⋡' (U+22e1)
_operators["\u22e1"] = C_("math symbol", "does not succeed or equal")

# Translators: this is the spoken representation for the character '⋢' (U+22e2)
_operators["\u22e2"] = C_("math symbol", "not square image of or equal to")

# Translators: this is the spoken representation for the character '⋣' (U+22e3)
_operators["\u22e3"] = C_("math symbol", "not square original of or equal to")

# Translators: this is the spoken representation for the character '⋤' (U+22e4)
_operators["\u22e4"] = C_("math symbol", "square image of or not equal to")

# Translators: this is the spoken representation for the character '⋥' (U+22e5)
_operators["\u22e5"] = C_("math symbol", "square original of or not equal to")

# Translators: this is the spoken representation for the character '⋦' (U+22e6)
_operators["\u22e6"] = C_("math symbol", "less than but not equivalent to")

# Translators: this is the spoken representation for the character '⋧' (U+22e7)
_operators["\u22e7"] = C_("math symbol", "greater than but not equivalent to")

# Translators: this is the spoken representation for the character '⋨' (U+22e8)
_operators["\u22e8"] = C_("math symbol", "precedes but not equivalent to")

# Translators: this is the spoken representation for the character '⋩' (U+22e9)
_operators["\u22e9"] = C_("math symbol", "succeeds but not equivalent to")

# Translators: this is the spoken representation for the character '⋪' (U+22ea)
_operators["\u22ea"] = C_("math symbol", "not normal subgroup of")

# Translators: this is the spoken representation for the character '⋫' (U+22eb)
_operators["\u22eb"] = C_("math symbol", "does not contain as normal subgroup")

# Translators: this is the spoken representation for the character '⋬' (U+22ec)
_operators["\u22ec"] = C_("math symbol", "not normal subgroup of or equal to")

# Translators: this is the spoken representation for the character '⋭' (U+22ed)
_operators["\u22ed"] = C_("math symbol", "does not contain as normal subgroup or equal")

# Translators: this is the spoken representation for the character '⋮' (U+22ee)
_operators["\u22ee"] = C_("math symbol", "vertical ellipsis")

# Translators: this is the spoken representation for the character '⋯' (U+22ef)
_operators["\u22ef"] = C_("math symbol", "midline horizontal ellipsis")

# Translators: this is the spoken representation for the character '⋰' (U+22f0)
_operators["\u22f0"] = C_("math symbol", "up right diagonal ellipsis")

# Translators: this is the spoken representation for the character '⋱' (U+22f1)
_operators["\u22f1"] = C_("math symbol", "down right diagonal ellipsis")

# Translators: this is the spoken representation for the character '⋲' (U+22f2)
_operators["\u22f2"] = C_("math symbol", "element of with long horizontal stroke")

# Translators: this is the spoken representation for the character '⋳' (U+22f3)
_operators["\u22f3"] = C_("math symbol", "element of with vertical bar at end of horizontal stroke")

# Translators: this is the spoken representation for the character '⋴' (U+22f4)
_operators["\u22f4"] = C_(
    "math symbol",
    "small element of with vertical bar at end of horizontal stroke",
)

# Translators: this is the spoken representation for the character '⋵' (U+22f5)
_operators["\u22f5"] = C_("math symbol", "element of with dot above")

# Translators: this is the spoken representation for the character '⋶' (U+22f6)
_operators["\u22f6"] = C_("math symbol", "element of with overbar")

# Translators: this is the spoken representation for the character '⋷' (U+22f7)
_operators["\u22f7"] = C_("math symbol", "small element of with overbar")

# Translators: this is the spoken representation for the character '⋸' (U+22f8)
_operators["\u22f8"] = C_("math symbol", "element of with underbar")

# Translators: this is the spoken representation for the character '⋹' (U+22f9)
_operators["\u22f9"] = C_("math symbol", "element of with two horizontal strokes")

# Translators: this is the spoken representation for the character '⋺' (U+22fa)
_operators["\u22fa"] = C_("math symbol", "contains with long horizontal stroke")

# Translators: this is the spoken representation for the character '⋻' (U+22fb)
_operators["\u22fb"] = C_("math symbol", "contains with vertical bar at end of horizontal stroke")

# Translators: this is the spoken representation for the character '⋼' (U+22fc)
_operators["\u22fc"] = C_(
    "math symbol",
    "small contains with vertical bar at end of horizontal stroke",
)

# Translators: this is the spoken representation for the character '⋽' (U+22fd)
_operators["\u22fd"] = C_("math symbol", "contains with overbar")

# Translators: this is the spoken representation for the character '⋾' (U+22fe)
_operators["\u22fe"] = C_("math symbol", "small contains with overbar")

# Translators: this is the spoken representation for the character '⋿' (U+22ff)
_operators["\u22ff"] = C_("math symbol", "z notation bag membership")

# Translators: this is the spoken representation for the character '⌈' (U+2308)
_operators["\u2308"] = C_("math symbol", "left ceiling")

# Translators: this is the spoken representation for the character '⌉' (U+2309)
_operators["\u2309"] = C_("math symbol", "right ceiling")

# Translators: this is the spoken representation for the character '⌊' (U+230a)
_operators["\u230a"] = C_("math symbol", "left floor")

# Translators: this is the spoken representation for the character '⌋' (U+230b)
_operators["\u230b"] = C_("math symbol", "right floor")

# Translators: this is the spoken representation for the character '⏞' (U+23de)
_operators["\u23de"] = C_("math symbol", "top brace")

# Translators: this is the spoken representation for the character '⏟' (U+23df)
_operators["\u23df"] = C_("math symbol", "bottom brace")

# Translators: this is the spoken representation for the character '⟨' (U+27e8)
_operators["\u27e8"] = C_("math symbol", "left angle bracket")

# Translators: this is the spoken representation for the character '⟩' (U+27e9)
_operators["\u27e9"] = C_("math symbol", "right angle bracket")

# Translators: this is the spoken representation for the character '⨀' (U+2a00)
_operators["\u2a00"] = C_("math symbol", "circled dot")

# Translators: this is the spoken representation for the character '⨁' (U+2a01)
_operators["\u2a01"] = C_("math symbol", "circled plus")

# Translators: this is the spoken representation for the character '⨂' (U+2a02)
_operators["\u2a02"] = C_("math symbol", "circled times")
# Translators: this is the spoken representation for the character '⨃' (U+2a03)
_operators["\u2a03"] = C_("math symbol", "union with dot")
# Translators: this is the spoken representation for the character '⨄' (U+2a04)
_operators["\u2a04"] = C_("math symbol", "union with plus")
# Translators: this is the spoken representation for the character '⨅' (U+2a05)
_operators["\u2a05"] = C_("math symbol", "square intersection")
# Translators: this is the spoken representation for the character '⨆' (U+2a06)
_operators["\u2a06"] = C_("math symbol", "square union")

# Translators: this is the spoken representation for the character '■' (U+25a0)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes["\u25a0"] = C_("math symbol", "black square")

# Translators: this is the spoken representation for the character '□' (U+25a1)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes["\u25a1"] = C_("math symbol", "white square")

# Translators: this is the spoken representation for the character '◆' (U+25c6)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes["\u25c6"] = C_("math symbol", "black diamond")

# Translators: this is the spoken representation for the character '○' (U+25cb)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes["\u25cb"] = C_("math symbol", "white circle")

# Translators: this is the spoken representation for the character '●' (U+25cf)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes["\u25cf"] = C_("math symbol", "black circle")

# Translators: this is the spoken representation for the character '◦' (U+25e6)
_shapes["\u25e6"] = C_("math symbol", "white bullet")

# Translators: this is the spoken representation for the character '◾' (U+25fe)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes["\u25fe"] = C_("math symbol", "black medium small square")

# Translators: this is the spoken representation for the character '̱' (U+0331)
# which combines with the preceding character. '%s' is a placeholder for the
# preceding character. Some examples of combined symbols can be seen in this
# table: http://www.w3.org/TR/MathML3/appendixc.html#oper-dict.entries-table.
_combining["\u0331"] = C_("math symbol", "%s with underline")

# Translators: this is the spoken representation for the character '̸' (U+0338)
# which combines with the preceding character. '%s' is a placeholder for the
# preceding character. Some examples of combined symbols can be seen in this
# table: http://www.w3.org/TR/MathML3/appendixc.html#oper-dict.entries-table.
_combining["\u0338"] = C_("math symbol", "%s with slash")

# Translators: this is the spoken representation for the character '⃒' (U+20D2)
# which combines with the preceding character. '%s' is a placeholder for the
# preceding character. Some examples of combined symbols can be seen in this
# table: http://www.w3.org/TR/MathML3/appendixc.html#oper-dict.entries-table.
_combining["\u20d2"] = C_("math symbol", "%s with vertical line")

_all.update(_arrows)
_all.update(_operators)
_all.update(_shapes)


_STYLE_MAP: list[tuple[str, list[range | list[int]]]] = [
    (BOLD, [_bold, _bold_greek, _bold_digits]),
    (ITALIC, [_italic, _italic_greek, _other_italic]),
    (BOLD_ITALIC, [_bold_italic, _bold_italic_greek]),
    (SCRIPT, [_script, _other_script]),
    (BOLD_SCRIPT, [_bold_script]),
    (FRAKTUR, [_fraktur, _other_fraktur]),
    (DOUBLE_STRUCK, [_double_struck, _double_struck_digits, _other_double_struck]),
    (BOLD_FRAKTUR, [_bold_fraktur]),
    (SANS_SERIF, [_sans_serif, _sans_serif_digits]),
    (SANS_SERIF_BOLD, [_sans_serif_bold, _sans_serif_bold_greek, _sans_serif_bold_digits]),
    (SANS_SERIF_ITALIC, [_sans_serif_italic]),
    (SANS_SERIF_BOLD_ITALIC, [_sans_serif_bold_italic, _sans_serif_bold_italic_greek]),
    (MONOSPACE, [_monospace, _monospace_digits]),
    (DOTLESS, [_dotless]),
]


def _get_style_string(symbol):
    o = ord(symbol)
    for style, dicts in _STYLE_MAP:
        if any(o in d for d in dicts):
            return style
    return "%s"


def _update_symbols(symbol_dict):
    _all.update(symbol_dict)


def _get_spoken_name(symbol, include_style):
    if symbol not in _all:
        return ""

    name = _all.get(symbol)
    if not name and fall_back_on_unicode_data:
        name = unicodedata.name(symbol).lower()
        _update_symbols({symbol: name})
        return name

    if include_style and symbol in _alnum:
        name = _get_style_string(symbol) % name

    return name


def get_character_name(symbol):
    """Returns the character name of symbol."""

    result = _get_spoken_name(symbol, speak_style != SPEAK_NEVER)
    msg = f"MATHSYMBOLS: Name of '{symbol}' is '{result}'"
    debug.print_message(debug.LEVEL_INFO, msg, True, True)
    return result


def adjust_for_speech(string):
    """Adjusts string for speech by replacing math symbols with their spoken names."""

    # Handle combining characters first
    # Combining characters modify the preceding character
    result = string
    for combining_char, name_template in _combining.items():
        # Look for any character followed by the combining character
        i = 0
        while i < len(result) - 1:
            if result[i + 1] == combining_char:
                base_char = result[i]
                name = name_template % base_char
                # Replace the base char + combining char with the spoken name
                result = result[:i] + f" {name} " + result[i + 2 :]
                i += len(f" {name} ")
            else:
                i += 1

    # Handle regular math symbols
    include_style = speak_style == SPEAK_ALWAYS
    for char in _all:
        if char in result:
            name = _get_spoken_name(char, include_style)
            if name:
                result = result.replace(char, f" {name} ")

    return result
