# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""Exposes a dictionary, chnames, that maps punctuation characters
into localized words.
"""

from orca_i18n import _ # for gettext support

chnames = {}
chnames[" "] = _("space")
chnames["!"] = _("bang")
chnames["\""] = _("quote")
chnames["#"] = _("number")
chnames["$"] = _("dollar")
chnames["%"] = _("percent")
chnames["&"] = _("and")
chnames["'"] = _("tick")
chnames["("] = _("left")
chnames[")"] = _("right")
chnames["*"] = _("star")
chnames["+"] = _("plus")
chnames[","] = _("comma")
chnames["-"] = _("dash")
chnames["."] = _("dot")
chnames["/"] = _("slash")
chnames["?"] = _("question")
chnames[":"] = _("collun")
chnames[";"] = _("semi")
chnames["<"] = _("less")
chnames[">"] = _("greater")
chnames["["] = _("left bracket")
chnames["]"] = _("right bracket")
chnames["{"] = _("left brace")
chnames["}"] = _("right brace")
chnames["\\"] = _("back")
chnames["|"] = _("bar")
