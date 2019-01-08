# Orca
#
# Copyright 2018 Igalia, S.L.
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

# Please note: ATK support in Chromium needs much work. Until that work has been
# done, Orca will not be able to provide access to Chromium. This script is a
# work in progress.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018 Igalia, S.L."
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

        # Normally we don't cache the name, because we cannot count on apps and
        # tookits emitting name-changed events (needed by AT-SPI2 to update the
        # name so that we don't have stale values). However, if we don't cache
        # the name, we wind up with dead accessibles in (at least) the search bar
        # popup. For now, cache the name to get things working and clear the cache
        # for objects we plan to present. http://crbug.com/896706
        app.setCacheMask(pyatspi.cache.DEFAULT ^ pyatspi.cache.CHILDREN)

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

        # Normally we don't cache the name, because we cannot count on apps and
        # tookits emitting name-changed events (needed by AT-SPI2 to update the
        # name so that we don't have stale values). However, if we don't cache
        # the name, we wind up with dead accessibles in (at least) the search bar
        # popup. For now, cache the name to get things working and clear the cache
        # for objects we plan to present. Mind you, clearing the cache on objects
        # with many descendants can cause AT-SPI2 to become non-responsive so try
        # to guess what NOT to clear the cache for. http://crbug.com/896706
        doNotClearCacheFor = [pyatspi.ROLE_DIALOG,
                              pyatspi.ROLE_FRAME,
                              pyatspi.ROLE_LIST_BOX,
                              pyatspi.ROLE_MENU,
                              pyatspi.ROLE_REDUNDANT_OBJECT,
                              pyatspi.ROLE_TABLE,
                              pyatspi.ROLE_TREE,
                              pyatspi.ROLE_TREE_TABLE,
                              pyatspi.ROLE_UNKNOWN,
                              pyatspi.ROLE_WINDOW]
        if newFocus.getRole() not in doNotClearCacheFor:
            msg = "CHROMIUM: CANNOT CACHE NAME HACK: Clearing cache for %s" % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            newFocus.clearCache()

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

        # HACK: Remove this once Chromium emits focus changes after window activation.
        if event.detail1 and role == pyatspi.ROLE_FRAME:
            startTime = time.time()
            focusedObject = self.utilities.focusedObject(event.source)
            msg = "CHROMIUM: NO INITIAL FOCUS HACK. Focused object: %s - %.4fs" % \
                (focusedObject, time.time()-startTime)
            debug.println(debug.LEVEL_INFO, msg, True)
            if focusedObject:
                orca.setLocusOfFocus(event, focusedObject)

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

        if super().onBusyChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onBusyChanged(self, event)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

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

        if super().onChildrenChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onChildrenChanged(self, event)

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        if super().onDocumentLoadComplete(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentLoadComplete(self, event)

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if super().onDocumentLoadStopped(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentLoadStopped(self, event)

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        if super().onDocumentReload(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onDocumentReload(self, event)

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

        if event.source.getRole() == pyatspi.ROLE_PAGE_TAB and event.detail1:
            oldName = event.source.name
            event.source.clearCache()
            newName = event.source.name
            if oldName != newName:
                msg = "CHROMIUM: NO NAME CHANGE HACK: (name should be: '%s')" % newName
                debug.println(debug.LEVEL_INFO, msg, True)

        # Other apps and toolkits implement the selection interface, which is
        # what we use to present active-descendanty selection changes, leaving
        # state-changed:selected for notifications related to toggling the
        # selected state of the currently-focused item (e.g. pressing ctrl+space
        # in a file explorer). While handling active-descendanty changes here is
        # not technically a HACK, once Chromium implements the selection interface,
        # we should remove this code and defer to Orca's default handling.
        if event.detail1 and not self.utilities.isLayoutOnly(event.source) \
           and not "Selection" in pyatspi.listInterfaces(event.source.parent) \
           and self.utilities.canBeActiveWindow(self.utilities.topLevelObject(event.source)):
            msg = "CHROMIUM: NO SELECTION IFACE HACK: Setting %s to locusOfFocus" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, event.source)
            return

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

        if super().onTextSelectionChanged(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onTextSelectionChanged(self, event)

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        if not self.utilities.canBeActiveWindow(event.source):
            return

        if not event.source.name:
            orca_state.activeWindow = event.source

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

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        if super().onWindowDeactivated(event):
            return

        msg = "CHROMIUM: Passing along event to default script"
        debug.println(debug.LEVEL_INFO, msg, True)
        default.Script.onWindowDeactivated(self, event)

    def sayAll(self, inputEvent, obj=None, offset=None):
        msg = "CHROMIUM: SayAll not supported yet."
        debug.println(debug.LEVEL_INFO, msg, True)
        return True
