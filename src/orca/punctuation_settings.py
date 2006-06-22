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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import settings

#  Whether or not the spoken name for the symbol should replace the
#  actual symbol or be inserted before the symbol.
#
PUNCTUATION_REPLACE = 0
PUNCTUATION_INSERT  = 1

punctuation = {}

punctuation["!"] =  [ settings.PUNCTUATION_STYLE_ALL,  PUNCTUATION_INSERT ]
punctuation["'"] =  [ settings.PUNCTUATION_STYLE_ALL,  PUNCTUATION_REPLACE ]
punctuation[","] =  [ settings.PUNCTUATION_STYLE_ALL,  PUNCTUATION_INSERT ]
punctuation["."] =  [ settings.PUNCTUATION_STYLE_ALL,  PUNCTUATION_INSERT ]
punctuation["?"] =  [ settings.PUNCTUATION_STYLE_ALL,  PUNCTUATION_INSERT ]

punctuation["\""] = [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["("] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation[")"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["-"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_INSERT ]
punctuation["_"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation[":"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_INSERT ]
punctuation[";"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_INSERT ]
punctuation["<"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation[">"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["["] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["]"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["\\"] = [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["|"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["`"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["~"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["{"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]
punctuation["}"] =  [ settings.PUNCTUATION_STYLE_MOST, PUNCTUATION_REPLACE ]

punctuation["#"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["$"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["%"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["&"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["*"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["+"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["/"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["="] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["@"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
punctuation["^"] =  [ settings.PUNCTUATION_STYLE_SOME, PUNCTUATION_REPLACE ]
