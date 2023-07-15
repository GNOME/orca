# Orca
#
# Copyright (C) 2010-2013 Igalia, S.L.
#
# Author: Alejandro Pinheiro Iglesias <apinheiro@igalia.com>
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
__copyright__ = "Copyright (c) 2010-2013 Igalia, S.L."
__license__   = "LGPL"

import time

import orca.debug as debug
import orca.orca as orca
import orca.scripts.toolkits.clutter as clutter
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .formatting import Formatting
from .script_utilities import Utilities

class Script(clutter.Script):

    def __init__(self, app):
        clutter.Script.__init__(self, app)
        self._activeDialog = (None, 0) # (Accessible, Timestamp)
        self._activeDialogLabels = {}  # key == hash(obj), value == name

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        return Utilities(self)

    def deactivate(self):
        """Called when this script is deactivated."""

        self.utilities.clearCachedObjects()
        super().deactivate()

    def skipObjectEvent(self, event):
        """Determines whether or not this event should be skipped due to
        being redundant, part of an event flood, etc."""

        # We must handle all dialogs ourselves in this script.
        if AXUtilities.is_dialog(event.source):
            return False

        if AXUtilities.is_window(event.source):
            return self.utilities.isBogusWindowFocusClaim(event)

        return clutter.Script.skipObjectEvent(self, event)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        if (event and event.type == "window:activate" and newFocus and not AXObject.get_name(newFocus)):
            queuedEvent = self._getQueuedEvent("object:state-changed:focused", True)
            if queuedEvent and queuedEvent.source != event.source:
                msg = "GNOME SHELL: Have matching focused event. Not announcing nameless window."
                debug.println(debug.LEVEL_INFO, msg, True)
                return

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def _presentDialogLabel(self, event):
        activeDialog, timestamp = self._activeDialog
        if not activeDialog or not AXUtilities.is_label(event.source):
            return False

        obj = hash(event.source)
        name = AXObject.get_name(event.source)
        if name == self._activeDialogLabels.get(obj):
            return True

        parentDialog = AXObject.find_ancestor(event.source, AXUtilities.is_dialog)
        if activeDialog == parentDialog:
            self.presentMessage(name)
            self._activeDialogLabels[obj] = name
            return True

        return False

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self._presentDialogLabel(event):
            return

        clutter.Script.onNameChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if not event.detail1:
            return

        # When entering overview with many open windows, we get quite
        # a few state-changed:showing events for nameless panels. The
        # act of processing these by the default script causes us to
        # present nothing, and introduces a significant delay before
        # presenting the Top Bar button when Ctrl+Alt+Tab was pressed.
        if AXUtilities.is_panel(event.source) and not AXObject.get_name(event.source):
            return

        # We cannot count on events or their order from dialog boxes.
        # Therefore, the only way to reliably present a dialog is by
        # ignoring the events of the dialog itself and keeping track
        # of the current dialog.
        activeDialog, timestamp = self._activeDialog
        if not event.detail1 and event.source == activeDialog:
            self._activeDialog = (None, 0)
            self._activeDialogLabels = {}
            return

        if activeDialog and event.detail1 and AXUtilities.is_label(event.source):
            if self._presentDialogLabel(event):
                return

        clutter.Script.onShowingChanged(self, event)

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        # Some buttons, like the Wikipedia button, claim to be selected but
        # lack STATE_SELECTED. The other buttons, such as in the Dash and
        # event switcher, seem to have the right state. Since the ones with
        # the wrong state seem to be things we don't want to present anyway
        # we'll stop doing so and hope we are right.
        if event.detail1:
            if AXUtilities.is_panel(event.source):
                AXObject.clear_cache(event.source)
            if AXUtilities.is_selected(event.source):
                orca.setLocusOfFocus(event, event.source)
            return

        clutter.Script.onSelectedChanged(self, event)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        # The dialog will get presented when its first child gets focus.
        if AXUtilities.is_dialog(event.source):
            return

        # We're getting a spurious focus claim from the gnome-shell window after
        # the window switcher is used.
        if AXUtilities.is_window(event.source):
            return

        if not AXObject.get_name(event.source) and AXUtilities.is_menu_item(event.source) \
           and not self.utilities.labelsForObject(event.source):
            descendant = AXObject.find_descendant(event.source, AXUtilities.is_slider)
            if descendant is not None:
                orca.setLocusOfFocus(event, descendant)
                return

        # This is to present dialog boxes which are, to the user, newly
        # activated. And if something is claiming to be focused that is
        # not in a dialog, that's good to know as well, so update our
        # state regardless.
        activeDialog, timestamp = self._activeDialog
        if not activeDialog:
            dialog = AXObject.find_ancestor(event.source, AXUtilities.is_dialog)
            self._activeDialog = (dialog, time.time())
            if dialog:
                orca.setLocusOfFocus(None, dialog)
                labels = self.utilities.unrelatedLabels(dialog)
                for label in labels:
                    self._activeDialogLabels[hash(label)] = AXObject.get_name(label)

        clutter.Script.onFocusedChanged(self, event)

    def echoPreviousWord(self, obj, offset=None):
        try:
            text = obj.queryText()
        except NotImplementedError:
            return False

        if not offset:
            if text.caretOffset == -1:
                offset = text.characterCount - 1
            else:
                offset = text.caretOffset - 1

        if offset == 0:
            return False

        return super().echoPreviousWord(obj, offset)

    def isActivatableEvent(self, event):
        if event.type.startswith('object:state-changed:selected') and event.detail1:
            return True

        if self.utilities.isBogusWindowFocusClaim(event):
            return False

        return super().isActivatableEvent(event)
