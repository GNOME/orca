# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
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

"""Custom script for planner."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.braille_generator as braille_generator

from orca.orca_i18n import _ # for gettext support

class BrailleGenerator(braille_generator.BrailleGenerator):
    """We make this to appropiately present ribbon's toggle button in
    a toolbar used to display in a menu those options that doesn't
    fill in toolbar when the application is resized. Also for each one
    of the grphics buttons in the main window."""

    def __init__(self, script):
        braille_generator.BrailleGenerator.__init__(self, script)

    def _generateDisplayedText(self, obj, **args ):
        """Returns an array of strings for use by braille that represents all
        the text being displayed by the object. [[[WDW - consider
        returning an empty array if this is not a text object.]]]
        """
        result = []

        # This is the black triangle at the far right of the toolbar.
        #
        handleRibbonButton = \
            obj and not obj.name \
            and obj.getRole() == pyatspi.ROLE_TOGGLE_BUTTON \
            and obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR

        # This is one of the Gantt, Tasks, Resources, etc., buttons on the
        # left hand side of the main window.
        #
        handleTabButton = \
            obj and not obj.name \
            and obj.getRole() == pyatspi.ROLE_TOGGLE_BUTTON \
            and obj.parent.getRole() == pyatspi.ROLE_FILLER \
            and len(obj.parent) == 2

        if handleRibbonButton:
            result.append(_("Display more options"))
        elif handleTabButton:
            result.append(self._script.utilities.displayedText(obj.parent[1]))
        else:
            result.extend(
                braille_generator.BrailleGenerator._generateDisplayedText(
                    self, obj, **args))

        return result
