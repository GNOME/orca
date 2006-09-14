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

"""Exposes a dictionary, phonnames, that maps each letter of the 
alphabet into its localized phonetic equivalent."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

phonnames = {}
phonnames["a"] = _("alpha")
phonnames["b"] = _("bravo")
phonnames["c"] = _("charlie")
phonnames["d"] = _("delta")
phonnames["e"] = _("echo")
phonnames["f"] = _("foxtrot")
phonnames["g"] = _("golf")
phonnames["h"] = _("hotel")
phonnames["i"] = _("india")
phonnames["j"] = _("juliet")
phonnames["k"] = _("kilo")
phonnames["l"] = _("lima")
phonnames["m"] = _("mike")
phonnames["n"] = _("november")
phonnames["o"] = _("oscar")
phonnames["p"] = _("papa")
phonnames["q"] = _("quebec")
phonnames["r"] = _("romeo")
phonnames["s"] = _("sierra")
phonnames["t"] = _("tango")
phonnames["u"] = _("uniform")
phonnames["v"] = _("victor")
phonnames["w"] = _("whiskey")
phonnames["x"] = _("xray")
phonnames["y"] = _("yankee")
phonnames["z"] = _("zulu")
