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

"""Provides a method, getRoleName, that converts the role name of an
Accessible object into a localized string.
"""

from orca_i18n import _ # for gettext support

# [[[TODO: WDW - make sure these match, and are complete.  The keys
# appear to be taken from /gnome/at-spi/cspi/spi_accessible.c:role_names.]]]
#
rolenames = {}
rolenames["push button"] = _("button")
rolenames["layered pane"] = _("list view")
rolenames["tree table"] = _("tree view")
rolenames["tree"] = _("tree view")
rolenames["frame"] = ""
rolenames["page tab"] = _("tab")


def getRoleName (obj):
    """Returns the localized name of the given Accessible object.
    If a localized name cannot be discovered, this will return
    the string as defined by the at-spi.
    
    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object.
    """
    
    name = obj.role
    try:
        return rolenames[name]
    except:
        return name

