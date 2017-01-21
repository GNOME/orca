# Mouse reviewer for Orca
#
# Copyright 2008 Eitan Isaacson
# Copyright 2016 Igalia, S.L.
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

"""Mouse review mode."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Eitan Isaacson" \
                "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import gi
import math
import pyatspi
import time

from gi.repository import Gdk
try:
    gi.require_version("Wnck", "3.0")
    from gi.repository import Wnck
    _mouseReviewCapable = True
except:
    _mouseReviewCapable = False

from . import debug
from . import event_manager
from . import messages
from . import orca_state
from . import script_manager
from . import settings_manager
from . import speech

_eventManager = event_manager.getManager()
_scriptManager = script_manager.getManager()
_settingsManager = settings_manager.getManager()

class _StringContext:
    """The textual information associated with an _ItemContext."""

    def __init__(self, obj, script=None, string="", start=0, end=0):
        """Initialize the _StringContext.

        Arguments:
        - string: The human-consumable string
        - obj: The accessible object associated with this string
        - start: The start offset with respect to entire text, if one exists
        - end: The end offset with respect to the entire text, if one exists
        - script: The script associated with the accessible object
        """

        self._obj = hash(obj)
        self._script = script
        self._string = string
        self._start = start
        self._end = end

    def __eq__(self, other):
        return other is not None \
            and self._obj == other._obj \
            and self._string == other._string \
            and self._start == other._start \
            and self._end == other._end

    def present(self):
        """Presents this context to the user."""

        if not (self._script and self._string):
            return False

        voice = self._script.speechGenerator.voice(string=self._string)
        string = self._script.utilities.adjustForRepeats(self._string)
        self._script.speakMessage(string, voice=voice, interrupt=False)
        self._script.displayBrailleMessage(self._string, -1)
        return True


class _ItemContext:
    """Holds all the information of the item at a specified point."""

    def __init__(self, x=0, y=0, obj=None, frame=None, script=None):
        """Initialize the _ItemContext.

        Arguments:
        - x: The X coordinate
        - y: The Y coordinate
        - obj: The accessible object of interest at that coordinate
        - frame: The containing accessible object (often a top-level window)
        - script: The script associated with the accessible object
        """

        self._x = x
        self._y = y
        self._obj = obj
        self._frame = frame
        self._script = script
        self._string = self._getStringContext()

    def __eq__(self, other):
        return other is not None \
            and self._frame == other._frame \
            and self._obj == other._obj \
            and self._string == other._string

    def _getStringContext(self):
        """Returns the _StringContext associated with the specified point."""

        if not (self._script and self._obj):
            return _StringContext(self._obj)

        interfaces = pyatspi.listInterfaces(self._obj)
        if "Text" not in interfaces:
            return _StringContext(self._obj, self._script)

        state = self._obj.getState()
        if not state.contains(pyatspi.STATE_SELECTABLE):
            boundary = pyatspi.TEXT_BOUNDARY_WORD_START
        else:
            boundary = pyatspi.TEXT_BOUNDARY_LINE_START

        string, start, end = self._script.utilities.textAtPoint(
            self._obj, self._x, self._y, boundary=boundary)
        if not string and self._script.utilities.isTextArea(self._obj):
            string = self._script.speechGenerator.getRoleName(self._obj)

        return _StringContext(self._obj, self._script, string, start, end)

    def present(self, prior):
        """Presents this context to the user."""

        if self == prior:
            return False

        interrupt = self._obj and self._obj != prior._obj \
            or math.sqrt((self._x - prior._x)**2 + (self._y - prior._y)**2) > 25

        if interrupt:
            self._script.presentationInterrupt()

        if self._frame and self._frame != prior._frame:
            self._script.presentObject(self._frame, alreadyFocused=True)

        if self._string != prior._string and self._string.present():
            return True

        if self._obj and self._obj != prior._obj:
            self._script.presentObject(self._obj)

        return True


class MouseReviewer:
    """Main class for the mouse-review feature."""

    def __init__(self):
        self._active = _settingsManager.getSetting("enableMouseReview")
        self._currentMouseOver = _ItemContext()
        self._pointer = None
        self._windows = []
        self._handlerIds = {}

        if not _mouseReviewCapable:
            msg = "MOUSE REVIEW ERROR: Wnck is not available"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        display = Gdk.Display.get_default()
        try:
            seat = Gdk.Display.get_default_seat(display)
            self._pointer = seat.get_pointer()
        except AttributeError:
            msg = "MOUSE REVIEW ERROR: Gtk+ 3.20 is not available"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if not self._active:
            return

        self.activate()

    def _get_listeners(self):
        """Returns the accessible-event listeners for mouse review."""

        return {"mouse:abs": self._listener}

    def activate(self):
        """Activates mouse review."""

        _eventManager.registerModuleListeners(self._get_listeners())
        screen = Wnck.Screen.get_default()
        if screen:
            i = screen.connect("window-stacking-changed", self._on_stacking_changed)
            self._handlerIds[i] = screen

    def deactivate(self):
        """Deactivates mouse review."""

        _eventManager.deregisterModuleListeners(self._get_listeners())
        for key, value in self._handlerIds.items():
            value.disconnect(key)
        self._handlerIds = {}

    def toggle(self, script=None, event=None):
        """Toggle mouse reviewing on or off."""

        if not _mouseReviewCapable:
            return

        self._active = not self._active
        _settingsManager.setSetting("enableMouseReview", self._active)

        if not self._active:
            self.deactivate()
            msg = messages.MOUSE_REVIEW_DISABLED
        else:
            self.activate()
            msg = messages.MOUSE_REVIEW_ENABLED

        if orca_state.activeScript:
            orca_state.activeScript.presentMessage(msg)

    def _on_stacking_changed(self, screen):
        """Callback for Wnck's window-stacking-changed signal."""

        stacked = screen.get_windows_stacked()
        stacked.reverse()
        self._windows = stacked

    def _contains_point(self, obj, x, y, coordType=None):
        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        try:
            return obj.queryComponent().contains(x, y, coordType)
        except:
            return False

    def _has_bounds(self, obj, bounds, coordType=None):
        """Returns True if the bounding box of obj is bounds."""

        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        try:
            extents = obj.queryComponent().getExtents(coordType)
        except:
            return False

        return list(extents) == list(bounds)

    def _accessible_window_at_point(self, pX, pY):
        """Returns the accessible window at the specified coordinates."""

        window = None
        for w in self._windows:
            x, y, width, height = w.get_geometry()
            if x <= pX <= x + width and y <= pY <= y + height:
                window = w
                break

        if not window:
            return None

        app = None
        pid = window.get_application().get_pid()
        for a in pyatspi.Registry.getDesktop(0):
            if a.get_process_id() == pid:
                app = a
                break

        if not app:
            return None

        candidates = [o for o in app if self._contains_point(o, pX, pY)]
        if len(candidates) == 1:
            return candidates[0]

        name = window.get_name()
        matches = [o for o in candidates if o.name == name]
        if len(matches) == 1:
            return matches[0]

        bbox = window.get_client_window_geometry()
        matches = [o for o in candidates if self._has_bounds(o, bbox)]
        if len(matches) == 1:
            return matches[0]

        return None

    def _on_mouse_moved(self, event):
        """Callback for mouse:abs events."""

        screen, pX, pY = self._pointer.get_position()
        window = self._accessible_window_at_point(pX, pY)
        msg = "MOUSE REVIEW: Window at (%i, %i) is %s" % (pX, pY, window)
        debug.println(debug.LEVEL_INFO, msg, True)
        if not window:
            return

        script = orca_state.activeScript
        if not script:
            return

        obj = script.utilities.descendantAtPoint(window, pX, pY)
        msg = "MOUSE REVIEW: Object at (%i, %i) is %s" % (pX, pY, obj)
        debug.println(debug.LEVEL_INFO, msg, True)

        script = _scriptManager.getScript(window.getApplication(), obj)
        new = _ItemContext(pX, pY, obj, window, script)
        new.present(self._currentMouseOver)
        self._currentMouseOver = new

    def _listener(self, event):
        """Generic listener, mainly to output debugging info."""

        startTime = time.time()
        msg = "\nvvvvv PROCESS OBJECT EVENT %s vvvvv" % event.type
        debug.println(debug.LEVEL_INFO, msg, False)

        if event.type.startswith("mouse:abs"):
            self._on_mouse_moved(event)

        msg = "TOTAL PROCESSING TIME: %.4f\n" % (time.time() - startTime)
        msg += "^^^^^ PROCESS OBJECT EVENT %s ^^^^^\n" % event.type
        debug.println(debug.LEVEL_INFO, msg, False)


reviewer = MouseReviewer()
