# Orca
#
# Copyright 2018-2019 Igalia, S.L.
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

"""Custom script for Chromium."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018-2019 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import time

from orca import debug
from orca import orca
from orca import orca_state
from orca.scripts import default
from orca.scripts import web
from .braille_generator import BrailleGenerator
from .script_utilities import Utilities
from .speech_generator import SpeechGenerator


class Script(web.Script):

    def __init__(self, app):
        super().__init__(app)

        self.presentIfInactive = False

        # Chromium doesn't always emit parent-change events. While we don't listen
        # for those ourselves, those events tell AT-SPI2 to update the cached parent.
        # If we cache the parent, then we can wind up getting stuck. Example page is
        # the Github issue page when the issue search field gets focus.
        app.setCacheMask(pyatspi.cache.DEFAULT ^
                         pyatspi.cache.CHILDREN ^
                         pyatspi.cache.PARENT ^
                         pyatspi.cache.NAME ^
                         pyatspi.cache.DESCRIPTION)

    def getBrailleGenerator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def isActivatableEvent(self, event):
        """Returns True if this event should activate this script."""

        if event.type == "window:activate":
            return self.utilities.canBeActiveWindow(event.source)

        return super().isActivatableEvent(event)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if super().locusOfFocusChanged(event, oldFocus, newFocus):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.locusOfFocusChanged(self, event, oldFocus, newFocus)

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if super().onActiveChanged(event):
            return

        role = event.source.getRole()
        if event.detail1 and role == pyatspi.ROLE_FRAME \
           and not self.utilities.canBeActiveWindow(event.source):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onActiveChanged(self, event)

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if super().onActiveDescendantChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onActiveDescendantChanged(self, event)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.hasNoSize(event.source):
            msg = "CHROMIUM: Ignoring event from page with no size."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if not self.utilities.documentFrameURI(event.source):
            msg = "CHROMIUM: Ignoring event from page with no URI."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onBusyChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onBusyChanged(self, event)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.isStaticTextLeaf(event.source):
            msg = "CHROMIUM: Ignoring event from static-text leaf"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if self.utilities.isRedundantAutocompleteEvent(event):
            msg = "CHROMIUM: Ignoring redundant autocomplete event"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onCaretMoved(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onCaretMoved(self, event)

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if super().onCheckedChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onCheckedChanged(self, event)

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        if self.utilities.isStaticTextLeaf(event.any_data):
            msg = "CHROMIUM: Ignoring because child is static text leaf"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onChildrenChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onChildrenChanged(self, event)

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        if not self.utilities.documentFrameURI(event.source):
            msg = "CHROMIUM: Ignoring event from page with no URI."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onDocumentLoadComplete(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentLoadComplete(self, event)

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if not self.utilities.documentFrameURI(event.source):
            msg = "CHROMIUM: Ignoring event from page with no URI."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onDocumentLoadStopped(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentLoadStopped(self, event)

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        if not self.utilities.documentFrameURI(event.source):
            msg = "CHROMIUM: Ignoring event from page with no URI."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onDocumentReload(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentReload(self, event)

    def onExpandedChanged(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if super().onExpandedChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onExpandedChanged(self, event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # This event is deprecated. We should get object:state-changed:focused
        # events instead.

        if super().onFocus(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onFocus(self, event)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if self.utilities.isDocument(event.source) \
           and not self.utilities.documentFrameURI(event.source):
            msg = "CHROMIUM: Ignoring event from document with no URI."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onFocusedChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onFocusedChanged(self, event)

    def onMouseButton(self, event):
        """Callback for mouse:button accessibility events."""

        if super().onMouseButton(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onMouseButton(self, event)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if super().onNameChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onNameChanged(self, event)

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if super().onSelectedChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onSelectedChanged(self, event)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if super().onSelectionChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onSelectionChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if event.detail1 and self.utilities.isMenuWithNoSelectedChild(event.source):
            topLevel = self.utilities.topLevelObject(event.source)
            if self.utilities.canBeActiveWindow(topLevel):
                orca_state.activeWindow = topLevel
                notify = not self.utilities.isPopupMenuForCurrentItem(event.source)
                orca.setLocusOfFocus(event, event.source, notify)
            return

        if super().onShowingChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onShowingChanged(self, event)

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if super().onTextDeleted(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if super().onTextInserted(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onTextInserted(self, event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if self.utilities.isStaticTextLeaf(event.source):
            msg = "CHROMIUM: Ignoring event from static-text leaf"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if self.utilities.isListItemMarker(event.source):
            msg = "CHROMIUM: Ignoring event from list item marker"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onTextSelectionChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onTextSelectionChanged(self, event)

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        if not self.utilities.canBeActiveWindow(event.source):
            return

        # If this is a frame for a popup menu, we don't want to treat
        # it like a proper window:activate event because it's not as
        # far as the end-user experience is concerned.
        activeItem = self.utilities.popupMenuForFrame(event.source)
        if activeItem:
            selected = self.utilities.selectedChildren(activeItem)
            if len(selected) == 1:
                activeItem = selected[0]

            msg = "CHROMIUM: Setting locusOfFocus to %s" % activeItem
            orca_state.activeWindow = event.source
            orca.setLocusOfFocus(event, activeItem)
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if super().onWindowActivated(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onWindowActivated(self, event)

        # Right now we don't get accessibility events for alerts which are
        # already showing at the time of window activation. If that changes,
        # we should store presented alerts so we don't double-present them.
        for child in event.source:
            if child.getRole() == pyatspi.ROLE_ALERT:
                self.presentObject(child)

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        if super().onWindowDeactivated(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onWindowDeactivated(self, event)
