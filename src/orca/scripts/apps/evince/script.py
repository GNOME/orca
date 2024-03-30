# Orca
#
# Copyright 2013 The Orca Team.
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

"""Custom script for evince."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013 The Orca Team."
__license__   = "LGPL"

from orca import focus_manager
from orca import keybindings
from orca import settings
from orca import settings_manager
from orca.scripts.toolkits import gtk
from orca.ax_utilities import AXUtilities
from orca.structural_navigation import StructuralNavigation

class Script(gtk.Script):

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        gtk.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(self.structuralNavigation.get_handlers(True))

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        layout = settings_manager.getManager().getSetting('keyboardLayout')
        isDesktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        structNavBindings = self.structuralNavigation.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in structNavBindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

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
                        StructuralNavigation.UNVISITED_LINK,
                        StructuralNavigation.VISITED_LINK]

        return enabledTypes

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        obj = event.source
        if AXUtilities.is_focused(obj):
            focus_manager.getManager().set_locus_of_focus(event, event.source, False)

        gtk.Script.on_caret_moved(self, event)
