# Orca
#
# Copyright 2023 Igalia, S.L.
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

"""
A script which has no commands, has no presentation, and ignores events.
The main use cases for this script are self-voicing apps and VMs which
should be usable without having to quit Orca entirely.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

from orca import debug
from orca import focus_manager
from orca import messages
from orca import orca_modifier_manager
from orca.scripts import default
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

class Script(default.Script):
    """The sleep-mode script."""

    def activate(self):
        """Called when this script is activated."""

        tokens = ["SLEEP MODE: Activating script for", self.app]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        orca_modifier_manager.getManager().unset_orca_modifiers("Entering sleep mode.")
        self.addKeyGrabs("script activation")

    def deactivate(self):
        """Called when this script is deactivated."""

        tokens = ["SLEEP MODE: De-activating script for", self.app]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        self.removeKeyGrabs("script deactivation")
        orca_modifier_manager.getManager().refresh_orca_modifiers("Exiting sleep mode.")

    def getBrailleGenerator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def getBrailleBindings(self):
        """Returns the braille bindings for this script."""

        msg = "SLEEP MODE: Has no braille bindings."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return {}

    def getKeyBindings(self, enabledOnly=True):
        """Returns the keybindings for this script."""

        return self.sleepModeManager.get_bindings()

    def addKeyGrabs(self, reason=""):
        """Adds key grabs for this script."""

        self.keyBindings = self.getKeyBindings()
        self.keyBindings.addKeyGrabs()

    def removeKeyGrabs(self, reason=""):
        """Adds key grabs for this script."""

        self.keyBindings.removeKeyGrabs(reason)

    def setupInputEventHandlers(self):
        return self.sleepModeManager.get_handlers()

    def updateBraille(self, obj, **args):
        """Updates the braille display to show the give object."""

        msg = "SLEEP MODE: Not updating braille."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def presentKeyboardEvent(self, event):
        """Presents the keyboard event to the user."""

        msg = "SLEEP MODE: Not presenting keyboard event."
        debug.printMessage(debug.LEVEL_INFO, msg, True, True)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        tokens = ["SLEEP MODE: focus changed from", oldFocus, "to", newFocus, "due to", event]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if oldFocus is None and AXUtilities.is_application(AXObject.get_parent(newFocus)):
            focus_manager.getManager().clear_state("Sleep mode enabled for this app.")
            self.clearBraille()
            self.presentMessage(messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(self.app))
            return

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_active_changed(self, event):
        """Callback for object:state-changed:active accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_column_reordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_children_removed(self, event):
        """Callback for object:children-changed:removed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_document_load_complete(self, event):
        """Callback for document:load-complete accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_document_load_complete(self, event)

    def on_document_load_stopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_document_reload(self, event):
        """Callback for document:reload accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_focus(self, event):
        """Callback for focus: accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_mouse_button(self, event):
        """Callback for mouse:button accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_text_attributes_changed(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        focus_manager.getManager().clear_state("Sleep mode enabled for this app.")
        self.clearBraille()
        self.presentMessage(messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(self.app))

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
