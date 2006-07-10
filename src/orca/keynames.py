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

"""Exposes a dictionary, keynames, that maps key events
into localized words."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

keynames = {}
keynames["Shift_L"]      = _("left shift")
keynames["Alt_L"]      = _("left alt")
keynames["Control_L"]      = _("left control")
keynames["Shift_L"]      = _("left shift")
keynames["Shift_R"]      = _("right shift")
keynames["Alt_R"]      = _("right alt")
keynames["Control_R"]      = _("right control")
keynames["ISO_Left_Tab"] = _("left tab")
keynames["SunF36"]       = _("F 11")
keynames["SunF37"]       = _("F 12")
