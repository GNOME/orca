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

"""Exposes a dictionary, chnames, that maps punctuation marks and
other individual characters into localized words."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

chnames = {}
chnames[" "] = _("space")
chnames["\n"] = _("newline")
chnames["\t"] = _("tab")

chnames["!"] = _("exclaim")
chnames["'"] = _("apostrophe")
chnames[","] = _("comma")
chnames["."] = _("dot")
chnames["?"] = _("question")

chnames["\""] = _("quote")
chnames["("] = _("left paren")
chnames[")"] = _("right paren")
chnames["-"] = _("dash")
chnames["_"] = _("underscore")
chnames[":"] = _("colon")
chnames[";"] = _("semicolon")
chnames["<"] = _("less than")
chnames[">"] = _("greater than")
chnames["["] = _("left bracket")
chnames["]"] = _("right bracket")
chnames["\\"] = _("backslash")
chnames["|"] = _("vertical line")
chnames["`"] = _("grave accent")
chnames["~"] = _("tilde")
chnames["{"] = _("left brace")
chnames["}"] = _("right brace")

chnames["#"] = _("pound")
chnames["$"] = _("dollar")
chnames["%"] = _("percent")
chnames["&"] = _("and")
chnames["*"] = _("star")
chnames["+"] = _("plus")
chnames["/"] = _("slash")
chnames["="] = _("equals")
chnames["@"] = _("at")
chnames["^"] = _("caret")
