# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Custom script for gedit."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.orca as orca
import orca.orca_state as orca_state
import orca.scripts.toolkits.gtk as gtk
from .spellcheck import SpellCheck

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""

        gtk.Script.__init__(self, app)

    def getSpellCheck(self):
        """Returns the spellcheck for this script."""

        return SpellCheck(self)

    def getAppPreferencesGUI(self):
        """Returns a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        from gi.repository import Gtk

        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.attach(self.spellcheck.getAppPreferencesGUI(), 0, 0, 1, 1)
        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        return self.spellcheck.getPreferencesFromGUI()

    def doWhereAmI(self, inputEvent, basicOnly):
        """Performs the whereAmI operation."""

        if self.spellcheck.isActive():
            self.spellcheck.presentErrorDetails(not basicOnly)

        super().doWhereAmI(inputEvent, basicOnly)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if self.spellcheck.isSuggestionsItem(newFocus):
            includeLabel = not self.spellcheck.isSuggestionsItem(oldFocus)
            self.updateBraille(newFocus)
            self.spellcheck.presentSuggestionListItem(includeLabel=includeLabel)
            return

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if event.source == self.spellcheck.getSuggestionsList():
            return

        gtk.Script.onActiveDescendantChanged(self, event)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        state = event.source.getState()
        if state.contains(pyatspi.STATE_MULTI_LINE):
            self.spellcheck.setDocumentPosition(event.source, event.detail1)

        gtk.Script.onCaretMoved(self, event)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        gtk.Script.onFocusedChanged(self, event)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if not self.spellcheck.isActive():
            gtk.Script.onNameChanged(self, event)
            return

        name = event.source.name
        if name == self.spellcheck.getMisspelledWord():
            self.spellcheck.presentErrorDetails()
            return

        parent = event.source.parent
        if parent != self.spellcheck.getSuggestionsList() \
           or not parent.getState().contains(pyatspi.STATE_FOCUSED):
            return

        entry = self.spellcheck.getChangeToEntry()
        if name != self.utilities.displayedText(entry):
            return

        # If we're here, the locusOfFocus was in the selection list when
        # that list got destroyed and repopulated. Focus is still there.
        orca.setLocusOfFocus(event, event.source, False)
        self.updateBraille(orca_state.locusOfFocus)

    def onSensitiveChanged(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""

        if event.source == self.spellcheck.getChangeToEntry() \
           and self.spellcheck.presentCompletionMessage():
            return

        gtk.Script.onSensitiveChanged(self, event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if event.source == orca_state.locusOfFocus:
            gtk.Script.onTextSelectionChanged(self, event)
            return

        if not self.utilities.isSearchEntry(orca_state.locusOfFocus, True):
            return

        # To avoid extreme chattiness.
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if keyString in ["BackSpace", "Delete"]:
            return

        self.sayLine(event.source)

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        gtk.Script.onWindowActivated(self, event)
        if not self.spellcheck.isCheckWindow(event.source):
            return

        self.spellcheck.presentErrorDetails()
        orca.setLocusOfFocus(None, self.spellcheck.getChangeToEntry(), False)
        self.updateBraille(orca_state.locusOfFocus)

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        gtk.Script.onWindowDeactivated(self, event)
        self.spellcheck.deactivate()
