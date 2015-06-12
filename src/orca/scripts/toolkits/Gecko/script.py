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
from orca.scripts import default
from orca.scripts import web
from .script_utilities import Utilities


class Script(web.Script):

    def __init__(self, app):
        super().__init__(app)

        # TODO - JD: This should also not be needed. In theory, they've
        # converted to the new attribute styles.

        # A dictionary of Gecko-style attribute names and their equivalent/
        # expected names. This is necessary so that we can present the
        # attributes to the user in a consistent fashion across apps and
        # toolkits. Note that underlinesolid and line-throughsolid are
        # temporary fixes: text_attribute_names.py assumes a one-to-one
        # correspondence. This is not a problem when going from attribute
        # name to localized name; in the reverse direction, we need more
        # context (i.e. we can't safely make them both be "solid"). A
        # similar issue exists with "start" which means no justification
        # has explicitly been set. If we set that to "none", "none" will
        # no longer have a single reverse translation.
        #
        self.attributeNamesDict = {
            "font-weight"             : "weight",
            "font-family"             : "family-name",
            "font-style"              : "style",
            "text-align"              : "justification",
            "text-indent"             : "indent",
            "font-size"               : "size",
            "background-color"        : "bg-color",
            "color"                   : "fg-color",
            "text-line-through-style" : "strikethrough",
            "text-underline-style"    : "underline",
            "text-position"           : "vertical-align",
            "writing-mode"            : "direction",
            "-moz-left"               : "left",
            "-moz-right"              : "right",
            "-moz-center"             : "center",
            "start"                   : "no justification",
            "underlinesolid"          : "single",
            "line-throughsolid"       : "solid"}

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

        if self.findCommandRun:
            self.findCommandRun = False
            self.find()
            return

        if not event.detail1:
            return

        role = event.source.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            orca.setLocusOfFocus(event, event.source)

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

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if super().onFocusedChanged(event):
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

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if super().onShowingChanged(event):
            return

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
