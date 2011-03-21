# Orca
#
# Copyright (C) 2010 Joanmarie Diggs
#
# Author: Joanmarie Diggs <joanied@gnome.org>
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
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs"
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

        if obj.getRole() == pyatspi.ROLE_LIST and obj.childCount:
            obj = obj[0]

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
            orca.setLocusOfFocus(None, child, False)
            return

        structural_navigation.StructuralNavigation._setCaretPosition(
            self, obj, characterOffset)
