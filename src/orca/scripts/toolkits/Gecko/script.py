# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
# Copyright 2014-2015 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Orca Team." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import debug
from orca import orca
from orca import orca_state
from orca.scripts import default
from orca.scripts import web
from .script_utilities import Utilities


class Script(web.Script):

    def __init__(self, app):
        super().__init__(app)

        # This can be removed once this Mozilla bug is fixed:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1174204
        self.attributeNamesDict = {
            "background-color"        : "bg-color",
            "color"                   : "fg-color"}

        # This one needs some more consideration for all toolkits.
        self.attributeNamesDict["invalid"] = "text-spelling"

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if super().locusOfFocusChanged(event, oldFocus, newFocus):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.locusOfFocusChanged(self, event, oldFocus, newFocus)

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if super().onActiveChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onActiveChanged(self, event)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if super().onBusyChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onBusyChanged(self, event)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if super().onCaretMoved(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onCaretMoved(self, event)

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if super().onCheckedChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onCheckedChanged(self, event)

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        if super().onChildrenChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onChildrenChanged(self, event)

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        if super().onDocumentLoadComplete(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onDocumentLoadComplete(self, event)

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if super().onDocumentLoadStopped(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onDocumentLoadStopped(self, event)

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        if super().onDocumentReload(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onDocumentReload(self, event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.utilities.inDocumentContent(event.source):
            return

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # in which object:state-changed:focused events are missing.

        role = event.source.getRole()

        # Unfiled. When a context menu pops up, we seem to get a focus: event,
        # but no object:state-changed:focused event from Gecko.
        if role == pyatspi.ROLE_MENU:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. When the Thunderbird 'do you want to replace this file'
        # attachment dialog pops up, the 'Replace' button emits a focus:
        # event, but we only seem to get the object:state-changed:focused
        # event when it gives up focus.
        if role == pyatspi.ROLE_PUSH_BUTTON:
            orca.setLocusOfFocus(event, event.source)

        # Some of the dialogs used by Thunderbird (and perhaps Firefox?) seem
        # to be using Gtk+ 2, along with its associated focused-event issues.
        # Unfortunately, because Gtk+ 2 doesn't expose a per-object toolkit,
        # we cannot know that a given widget is Gtk+ 2. Therefore, we'll put
        # our Gtk+ 2 toolkit script hacks here as well just to be safe.
        if role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_PASSWORD_TEXT]:
            orca.setLocusOfFocus(event, event.source)

        if role == pyatspi.ROLE_COMBO_BOX:
            orca.setLocusOfFocus(event, event.source)

        if role == pyatspi.ROLE_PAGE_TAB:
            orca.setLocusOfFocus(event, event.source)

        if role == pyatspi.ROLE_RADIO_BUTTON:
            orca.setLocusOfFocus(event, event.source)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if super().onFocusedChanged(event):
            return

        if event.source.getRole() == pyatspi.ROLE_PANEL:
            if orca_state.locusOfFocus == orca_state.activeWindow:
                msg = "GECKO: Ignoring event believed to be noise."
                debug.println(debug.LEVEL_INFO, msg)
                return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onFocusedChanged(self, event)

    def onMouseButton(self, event):
        """Callback for mouse:button accessibility events."""

        if super().onMouseButton(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onMouseButton(self, event)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if super().onNameChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onNameChanged(self, event)

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if super().onSelectedChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onSelectedChanged(self, event)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if super().onSelectionChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onSelectionChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if super().onShowingChanged(event):
            return

        if event.detail1 and self.utilities.isTopLevelChromeAlert(event.source):
            msg = "GECKO: Event handled: Presenting event source"
            debug.println(debug.LEVEL_INFO, msg)
            self.presentObject(event.source)
            return True

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onShowingChanged(self, event)

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if super().onTextDeleted(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if super().onTextInserted(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onTextInserted(self, event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if super().onTextSelectionChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onTextSelectionChanged(self, event)

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        if super().onWindowActivated(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onWindowActivated(self, event)

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        if super().onWindowDeactivated(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg)
        default.Script.onWindowDeactivated(self, event)

    def handleProgressBarUpdate(self, event, obj):
        """Determine whether this progress bar event should be spoken or not.
        For Firefox, we don't want to speak the small "page load" progress
        bar. All other Firefox progress bars get passed onto the parent
        class for handling.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj:  the Accessible progress bar object.
        """

        rolesList = [pyatspi.ROLE_PROGRESS_BAR, \
                     pyatspi.ROLE_STATUS_BAR, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if not self.utilities.hasMatchingHierarchy(event.source, rolesList):
            default.Script.handleProgressBarUpdate(self, event, obj)
