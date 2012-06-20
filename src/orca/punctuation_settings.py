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

"""Punctuation Verbosity settings.
The Orca punctuation settings are broken up into 4 modes.

These modes are None, Some, Most and All.

They are defined by a group of radio buttons on the speech
page of the configuration user interface.

Each mode is defined below. The 4 bits of information listed here are:

  - The actual printed symbol.

  - How the symbol should be pronounced (in the chnames dictionary in
    chnames.py keyed by symbol).

  - The level at which the symbol should be spoken. Note that this
    denotes the level containing all lower levels.

  - Whether or not the spoken name for the symbol should replace the
    actual symbol or be inserted before the symbol.
"""

__id__  = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from . import settings

#  Whether or not the spoken name for the symbol should replace the
#  actual symbol or be inserted before the symbol.
#
PUNCTUATION_REPLACE = 0
PUNCTUATION_INSERT  = 1

# The lowest level at which the spoken name should be spoken. Thus a symbol
# with a level of LEVEL_MOST will be spoken at LEVEL_MOST and LEVEL_ALL.
#
LEVEL_ALL  = settings.PUNCTUATION_STYLE_ALL
LEVEL_MOST = settings.PUNCTUATION_STYLE_MOST
LEVEL_SOME = settings.PUNCTUATION_STYLE_SOME
LEVEL_NONE = settings.PUNCTUATION_STYLE_NONE

# Bullets and bullet-like characters
#
middle_dot           =  '\u00b7'
bullet               =  '\u2022'
triangular_bullet    =  '\u2023'
hyphen_bullet        =  '\u2043'
black_square         =  '\u25a0'
white_square         =  '\u25a1'
white_bullet         =  '\u25e6'
white_circle         =  '\u25cb'
black_diamond        =  '\u25c6'
black_circle         =  '\u25cf'
check_mark           =  '\u2713'
heavy_check_mark     =  '\u2714'
x_shaped_bullet      =  '\u2717'
heavy_right_arrow    =  '\u2794'
right_arrowhead      =  '\u27a2'

# StarOffice/OOo's special-purpose bullet chararacters
#
SO_black_square      =  '\ue00a'
SO_black_diamond     =  '\ue00c'

# Miscellaneous other symbols
#
cent                 =  '\u00a2'
pound                =  '\u00a3'
yen                  =  '\u00a5'
section              =  '\u00a7'
copyright_sign       =  '\u00a9'
left_double_angle    =  '\u00ab'
not_sign             =  '\u00ac'
registered           =  '\u00ae'
degree               =  '\u00b0'
plus_minus           =  '\u00b1'
right_double_angle   =  '\u00bb'
one_quarter          =  '\u00bc'
one_half             =  '\u00bd'
three_quarters       =  '\u00be'
multiply             =  '\u00d7'
divide               =  '\u00f7'
en_dash              =  '\u2013'
left_single_quote    =  '\u2018'
right_single_quote   =  '\u2019'
single_low_quote     =  '\u201a'
left_double_quote    =  '\u201c'
right_double_quote   =  '\u201d'
double_low_quote     =  '\u201e'
dagger               =  '\u2020'
double_dagger        =  '\u2021'
per_mille            =  '\u2030'
prime                =  '\u2032'
double_prime         =  '\u2033'
euro                 =  '\u20ac'
trademark            =  '\u2122'
left_arrow           =  '\u2190'
right_arrow          =  '\u2192'
infinity             =  '\u221e'
almost_equal         =  '\u2248'
not_equal            =  '\u2260'
lt_or_equal          =  '\u2264'
gt_or_equal          =  '\u2265'
square_root          =  '\u221a'
cube_root            =  '\u221b'

superscript_zero        =  '\u2070'
superscript1            =  '\u00b9'
superscript2            =  '\u00b2'
superscript3            =  '\u00b3'
superscript4            =  '\u2074'
superscript5            =  '\u2075'
superscript6            =  '\u2076'
superscript7            =  '\u2077'
superscript8            =  '\u2078'
superscript9            =  '\u2079'
superscript_plus        =  '\u207a'
superscript_minus       =  '\u207b'
superscript_equals      =  '\u207c'
superscript_left_paren  =  '\u207d'
superscript_right_paren =  '\u207e'
superscriptn            =  '\u207f'
subscript_zero          =  '\u2080'
subscript1              =  '\u2081'
subscript2              =  '\u2082'
subscript3              =  '\u2083'
subscript4              =  '\u2084'
subscript5              =  '\u2085'
subscript6              =  '\u2086'
subscript7              =  '\u2087'
subscript8              =  '\u2088'
subscript9              =  '\u2089'
subscript_plus          =  '\u208a'
subscript_minus         =  '\u208b'
subscript_equals        =  '\u208c'
subscript_left_paren    =  '\u208d'
subscript_right_paren   =  '\u208e'

# punctuation is a dictionary where the keys represent a unicode
# character and the values are a list of two elements where the
# first represents the punctuation style and the second represents
# the action to take.
#
punctuation = {}

punctuation["!"] =  [ LEVEL_ALL,  PUNCTUATION_INSERT ]
punctuation["'"] =  [ LEVEL_ALL,  PUNCTUATION_REPLACE ]
punctuation[","] =  [ LEVEL_ALL,  PUNCTUATION_INSERT ]
punctuation["."] =  [ LEVEL_ALL,  PUNCTUATION_INSERT ]
punctuation["?"] =  [ LEVEL_ALL,  PUNCTUATION_INSERT ]
punctuation[right_single_quote] = [ LEVEL_ALL, PUNCTUATION_REPLACE ]

punctuation["\""] = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["("]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[")"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["-"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["_"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[":"]  = [ LEVEL_MOST, PUNCTUATION_INSERT ]
punctuation[";"]  = [ LEVEL_MOST, PUNCTUATION_INSERT ]
punctuation["<"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[">"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["["]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["]"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["\\"] = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["|"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["`"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["~"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["{"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["}"]  = [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[left_single_quote]  =  [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[left_double_quote]  =  [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[right_double_quote] =  [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[en_dash]            =  [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[double_low_quote]   =  [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation[single_low_quote]   =  [ LEVEL_MOST, PUNCTUATION_REPLACE ]
punctuation["#"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["$"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["%"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["&"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["*"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["+"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["/"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["="] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["@"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation["^"] =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[cent]               =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[pound]              =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[yen]                =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[euro]               =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[not_sign]           =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[copyright_sign]     =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[registered]         =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[trademark]          =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[degree]             =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[plus_minus]         =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[multiply]           =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[divide]             =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[infinity]           =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[almost_equal]       =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[not_equal]          =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[lt_or_equal]        =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[gt_or_equal]        =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[square_root]        =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[cube_root]          =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[dagger]             =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[double_dagger]      =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[section]            =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[prime]              =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[double_prime]       =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]
punctuation[per_mille]          =  [ LEVEL_SOME, PUNCTUATION_REPLACE ]

punctuation[left_arrow]         =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[right_arrow]        =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[left_double_angle]  =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[right_double_angle] =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[middle_dot]         =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[bullet]             =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[triangular_bullet]  =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[hyphen_bullet]      =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[black_square]       =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[white_square]       =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[white_bullet]       =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[white_circle]       =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[black_diamond]      =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[black_circle]       =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[check_mark]         =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[heavy_check_mark]   =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[x_shaped_bullet]    =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[heavy_right_arrow]  =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[right_arrowhead]    =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[SO_black_square]    =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[SO_black_diamond]   =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[one_quarter]        =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[one_half]           =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[three_quarters]     =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]

punctuation[superscript_zero]        =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript1]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript2]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript3]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript4]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript5]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript6]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript7]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript8]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript9]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript_plus]        =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript_minus]       =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript_equals]      =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript_left_paren]  =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscript_right_paren] =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[superscriptn]            =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript_zero]          =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript1]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript2]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript3]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript4]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript5]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript6]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript7]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript8]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript9]              =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript_plus]          =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript_minus]         =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript_equals]        =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript_left_paren]    =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]
punctuation[subscript_right_paren]   =  [ LEVEL_NONE, PUNCTUATION_REPLACE ]

def getPunctuationInfo(character):
    """Given a punctuation character, return the value
    [punctuation_style, punctuation_action] or None

    Arguments:
    - character: the punctuation character to get the information for

    Returns return the value [punctuation_style, punctuation_action]
    or None
    """

    return punctuation.get(character)
