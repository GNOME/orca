# Orca
#
# Copyright 2013 The Orca Team.
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

"""Custom script for evince."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013 The Orca Team."
__license__   = "LGPL"

import pyatspi

import orca.keybindings as keybindings
import orca.orca_state as orca_state
import orca.scripts.default as default
import orca.settings as settings
from orca.structural_navigation import StructuralNavigation
from .script_utilities import Utilities

########################################################################
#                                                                      #
# The evince script class.                                             #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(
            self.structuralNavigation.inputEventHandlers)

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()
        bindings = self.structuralNavigation.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getStructuralNavigation(self):
        """Returns the 'structural navigation' class for this script."""

        types = self.getEnabledStructuralNavigationTypes()
        return StructuralNavigation(self, types, True)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script."""

        enabledTypes = [StructuralNavigation.BUTTON,
                        StructuralNavigation.CHECK_BOX,
                        StructuralNavigation.COMBO_BOX,
                        StructuralNavigation.ENTRY,
                        StructuralNavigation.FORM_FIELD,
                        StructuralNavigation.HEADING,
                        StructuralNavigation.LINK,
                        StructuralNavigation.LIST,
                        StructuralNavigation.LIST_ITEM,
                        StructuralNavigation.PARAGRAPH,
                        StructuralNavigation.RADIO_BUTTON,
                        StructuralNavigation.TABLE,
                        StructuralNavigation.TABLE_CELL,
                        StructuralNavigation.UNVISITED_LINK,
                        StructuralNavigation.VISITED_LINK]

        return enabledTypes

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation."""

        if not self.structuralNavigation.enabled:
            return False

        states = orca_state.locusOfFocus.getState()
        if states.contains(pyatspi.STATE_EDITABLE):
            return False

        return True

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""
 
        obj = event.source
        if obj.getRole() == pyatspi.ROLE_ALERT and event.detail1:
            labels = self.utilities.unrelatedLabels(obj)
            message = " ".join(map(self.utilities.displayedText, labels))
            self.presentMessage(
                message, voice=self.voices.get(settings.DEFAULT_VOICE))
            return
 
        default.Script.onShowingChanged(self, event)
