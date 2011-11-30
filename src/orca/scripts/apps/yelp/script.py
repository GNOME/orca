# Orca
#
# Copyright 2011 The Orca Team.
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

""" Custom script for Yelp v3."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

import orca.scripts.toolkits.WebKitGtk as WebKitGtk

from orca.structural_navigation import StructuralNavigation

class Script(WebKitGtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""

        WebKitGtk.Script.__init__(self, app, isBrowser=True)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script."""

        enabledTypes = [StructuralNavigation.ANCHOR,
                        StructuralNavigation.BLOCKQUOTE,
                        StructuralNavigation.BUTTON,
                        StructuralNavigation.CHECK_BOX,
                        StructuralNavigation.CHUNK,
                        StructuralNavigation.COMBO_BOX,
                        StructuralNavigation.ENTRY,
                        StructuralNavigation.FORM_FIELD,
                        StructuralNavigation.HEADING,
                        StructuralNavigation.LANDMARK,
                        StructuralNavigation.LIST,
                        StructuralNavigation.LIST_ITEM,
                        StructuralNavigation.LIVE_REGION,
                        StructuralNavigation.PARAGRAPH,
                        StructuralNavigation.RADIO_BUTTON,
                        StructuralNavigation.SEPARATOR,
                        StructuralNavigation.TABLE,
                        StructuralNavigation.TABLE_CELL,
                        StructuralNavigation.UNVISITED_LINK,
                        StructuralNavigation.VISITED_LINK]

        return enabledTypes
