# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

"""Provides various utility functions for Orca."""

def isDesiredFocusedItem(obj, rolesList):
    """Called to determine if the given object and it's hierarchy of
       parent objects, each have the desired roles.

    Arguments:
    - obj: the accessible object to check.
    - rolesList: the list of desired roles for the components and the
      hierarchy of its parents.

    Returns True if all roles match.
    """

    current = obj
    for i in range(0, len(rolesList)):
        if (current == None) or (current.role != rolesList[i]):
            return False
        current = current.parent

    return True
