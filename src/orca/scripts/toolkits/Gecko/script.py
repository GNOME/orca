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

    def isActivatableEvent(self, event):
        if event.type == "window:activate":
            return self.utilities.canBeActiveWindow(event.source)

        return super().isActivatableEvent(event)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if super().locusOfFocusChanged(event, oldFocus, newFocus):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.locusOfFocusChanged(self, event, oldFocus, newFocus)

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if super().onActiveChanged(event):
            return

        if event.detail1 and event.source.getRole() == pyatspi.ROLE_FRAME \
           and not self.utilities.canBeActiveWindow(event.source):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onActiveChanged(self, event)

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if super().onActiveDescendantChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onActiveDescendantChanged(self, event)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.isNotRealDocument(event.source):
            msg = "GECKO: Ignoring: Event source is not real document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onBusyChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onBusyChanged(self, event)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if super().onCaretMoved(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onCaretMoved(self, event)

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if super().onCheckedChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onCheckedChanged(self, event)

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        if super().onChildrenChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onChildrenChanged(self, event)

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        if self.utilities.isNotRealDocument(event.source):
            msg = "GECKO: Ignoring: Event source is not real document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onDocumentLoadComplete(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentLoadComplete(self, event)

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if super().onDocumentLoadStopped(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentLoadStopped(self, event)

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        if super().onDocumentReload(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentReload(self, event)

    def onExpandedChanged(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if super().onExpandedChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onExpandedChanged(self, event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # This event is deprecated. We should get object:state-changed:focused
        # events instead.

        if super().onFocus(event):
            return

        if self.utilities.isLayoutOnly(event.source):
            return

        if event.source == orca_state.activeWindow:
            msg = "GECKO: Ignoring event for active window."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # in which object:state-changed:focused events are missing. And in the
        # case of Gecko dialogs, that seems to happen a lot.
        orca.setLocusOfFocus(event, event.source)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if super().onFocusedChanged(event):
            return

        if event.source.getRole() == pyatspi.ROLE_PANEL:
            if orca_state.locusOfFocus == orca_state.activeWindow:
                msg = "GECKO: Ignoring event believed to be noise."
                debug.println(debug.LEVEL_INFO, msg, True)
                return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onFocusedChanged(self, event)

    def onMouseButton(self, event):
        """Callback for mouse:button accessibility events."""

        if super().onMouseButton(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onMouseButton(self, event)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if super().onNameChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onNameChanged(self, event)

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if super().onSelectedChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onSelectedChanged(self, event)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if super().onSelectionChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onSelectionChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if super().onShowingChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onShowingChanged(self, event)

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if super().onTextDeleted(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if super().onTextInserted(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onTextInserted(self, event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if super().onTextSelectionChanged(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onTextSelectionChanged(self, event)

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        if not self.utilities.canBeActiveWindow(event.source):
            return

        if super().onWindowActivated(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onWindowActivated(self, event)

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        if super().onWindowDeactivated(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onWindowDeactivated(self, event)
