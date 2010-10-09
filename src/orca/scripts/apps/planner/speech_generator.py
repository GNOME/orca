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

import orca.speech_generator as speech_generator

from orca.orca_i18n import _         # for gettext support

class SpeechGenerator(speech_generator.SpeechGenerator):

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateLabelAndName(self, obj, **args):
        """Gets the label and the name if the name is different from the label.
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
                speech_generator.SpeechGenerator._generateLabelAndName(
                    self, obj, **args))

        return result
