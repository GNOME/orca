# Orca
#
# Copyright (C) 2010 Joanmarie Diggs
# Copyright (C) 2011-2012 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs" \
                "Copyright (c) 2011-2012 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.orca as orca
import orca.structural_navigation as structural_navigation

########################################################################
#                                                                      #
# Custom Structural Navigation                                         #
#                                                                      #
########################################################################

class StructuralNavigation(structural_navigation.StructuralNavigation):

    def __init__(self, script, enabledTypes, enabled):
        """WebKitGtk specific Structural Navigation."""

        structural_navigation.StructuralNavigation.__init__(self,
                                                            script,
                                                            enabledTypes,
                                                            enabled)
        self.collectionEnabled = False

    def _getCaretPosition(self, obj):
        """Returns the [obj, characterOffset] where the caret should be
        positioned. For most scripts, the object should not change and
        the offset should be 0.

        Arguments:
        - obj: the accessible object in which the caret should be
          positioned.
        """

        if not obj.childCount:
            return [obj, 0]

        child = obj[0]
        if obj.getRole() == pyatspi.ROLE_LIST:
            return [child, 0]

        name = obj.name
        if name and name == child.name and child.getRole() == pyatspi.ROLE_LINK:
            return [child, 0]

        return [obj, 0]

    def _setCaretPosition(self, obj, characterOffset):
        """Sets the caret at the specified offset within obj.

        Arguments:
        - obj: the accessible object in which the caret should be
          positioned.
        - characterOffset: the offset at which to position the caret.
        """

        if characterOffset == 0:
            child, offset = self._script.setCaretAtStart(obj)

            if child and child.getRole() == pyatspi.ROLE_LIST_ITEM:
                for c in child:
                    start, end = self._script.utilities.getHyperlinkRange(c)
                    if start == offset:
                        child = c
                        break

            orca.setLocusOfFocus(None, child, False)
            return

        structural_navigation.StructuralNavigation._setCaretPosition(
            self, obj, characterOffset)
