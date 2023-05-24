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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.object_properties as object_properties
import orca.braille_generator as braille_generator
from orca.ax_object import AXObject

########################################################################
#                                                                      #
# Custom BrailleGenerator                                              #
#                                                                      #
########################################################################

class BrailleGenerator(braille_generator.BrailleGenerator):
    """Provides a braille generator specific to WebKitGtk."""

    def __init__(self, script):
        braille_generator.BrailleGenerator.__init__(self, script)

    def __generateHeadingRole(self, obj):
        result = []
        level = self._script.utilities.headingLevel(obj)
        result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)

        return result

    def _generateRoleName(self, obj, **args):
        """Prevents some roles from being displayed."""

        doNotDisplay = [Atspi.Role.FORM,
                        Atspi.Role.SECTION,
                        Atspi.Role.UNKNOWN]
        if not AXObject.has_state(obj, Atspi.StateType.FOCUSABLE):
            doNotDisplay.extend([Atspi.Role.LIST,
                                 Atspi.Role.LIST_ITEM,
                                 Atspi.Role.PANEL])

        result = []
        role = args.get('role', AXObject.get_role(obj))
        if role == Atspi.Role.HEADING:
            result.extend(self.__generateHeadingRole(obj))
        elif not role in doNotDisplay:
            result.extend(braille_generator.BrailleGenerator._generateRoleName(
                self, obj, **args))
            parent = AXObject.get_parent(obj)
            if AXObject.get_role(parent) == Atspi.Role.HEADING:
                result.extend(self.__generateHeadingRole(parent))

        return result

    def _generateAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object.  This is typically used to present the context for
        an object (e.g., the names of the window, the panels, etc.,
        that the object is contained in).  If the 'priorObj' attribute
        of the args dictionary is set, only the differences in
        ancestry between the 'priorObj' and the current obj will be
        computed.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """

        if self._script.utilities.isWebKitGtk(obj):
            return []

        return braille_generator.BrailleGenerator._generateAncestors(
            self, obj, **args)

    def _generateEol(self, obj, **args):
        if self._script.utilities.isWebKitGtk(obj) \
           and AXObject.get_role(obj) == Atspi.Role.PARAGRAPH \
           and not AXObject.has_state(obj, Atspi.StateType.EDITABLE):
            return []

        return braille_generator.BrailleGenerator._generateEol(
            self, obj, **args)
