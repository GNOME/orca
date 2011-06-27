# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011 The Orca Team
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

# NOTE: This is an interim step in the plan for Orca to co-exist
# with various magnification solutions rather than to drive them.
# Orca should only fall back on this module if gnome-shell mag is
# unavailable. And in a GNOME 3 environment, there are no other
# magnification solutions. Hence the lack of functionality. ;-)

def magnifyAccessible(event, obj, extents=None):
    pass

def init():
    return False

def shutdown():
    return False





