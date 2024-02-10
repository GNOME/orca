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

import math
import time
from collections import deque

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

try:
    gi.require_version("Wnck", "3.0")
    from gi.repository import Wnck
    _mouseReviewCapable = True
except Exception:
    _mouseReviewCapable = False

from . import cmdnames
from . import debug
from . import focus_manager
from . import keybindings
from . import input_event
from . import messages
from . import script_manager
from . import settings_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities


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

        self._obj = obj
        self._script = script
        self._string = string
        self._start = start
        self._end = end
        self._boundingBox = 0, 0, 0, 0
        if script:
            self._boundingBox = script.utilities.getTextBoundingBox(obj, start, end)

    def __eq__(self, other):
        return other is not None \
            and self._obj == other._obj \
            and self._string == other._string \
            and self._start == other._start \
            and self._end == other._end

    def isSubstringOf(self, other):
        """Returns True if this is a substring of other."""

        if other is None:
            return False

        if not (self._obj and other._obj):
            return False

        thisBox = self.getBoundingBox()
        if thisBox == (0, 0, 0, 0):
            return False

        otherBox = other.getBoundingBox()
        if otherBox == (0, 0, 0, 0):
            return False

        # We get various and sundry results for the bounding box if the implementor
        # included newline characters as part of the word or line at offset. Try to
        # detect this and adjust the bounding boxes before getting the intersection.
        if thisBox[3] != otherBox[3] and self._obj == other._obj:
            thisNewLineCount = self._string.count("\n")
            if thisNewLineCount and thisBox[3] / thisNewLineCount == otherBox[3]:
                thisBox = *thisBox[0:3], otherBox[3]

        if self._script.utilities.intersection(thisBox, otherBox) != thisBox:
            return False

        if not (self._string and self._string.strip() in other._string):
            return False

        tokens = ["MOUSE REVIEW: '", self._string, "' is substring of '", other._string, "'"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return True

    def getBoundingBox(self):
        """Returns the bounding box associated with this context's range."""

        return self._boundingBox

    def getString(self):
        """Returns the string associated with this context."""

        return self._string

    def present(self):
        """Presents this context to the user."""

        if not self._script:
            msg = "MOUSE REVIEW: Not presenting due to lack of script"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not self._string:
            msg = "MOUSE REVIEW: Not presenting due to lack of string"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        voice = self._script.speechGenerator.voice(obj=self._obj, string=self._string)
        string = self._script.utilities.adjustForRepeats(self._string)

        focus_manager.getManager().emit_region_changed(
            self._obj, self._start, self._end, focus_manager.MOUSE_REVIEW)
        self._script.speakMessage(string, voice=voice, interrupt=False)
        self._script.displayBrailleMessage(self._string, -1)
        return True


class _ItemContext:
    """Holds all the information of the item at a specified point."""

    def __init__(self, x=0, y=0, obj=None, boundary=None, frame=None, script=None):
        """Initialize the _ItemContext.

        Arguments:
        - x: The X coordinate
        - y: The Y coordinate
        - obj: The accessible object of interest at that coordinate
        - boundary: The accessible-text boundary type
        - frame: The containing accessible object (often a top-level window)
        - script: The script associated with the accessible object
        """

        self._x = x
        self._y = y
        self._obj = obj
        self._boundary = boundary
        self._frame = frame
        self._script = script
        self._string = self._getStringContext()
        self._time = time.time()
        self._boundingBox = 0, 0, 0, 0
        if script:
            self._boundingBox = script.utilities.getBoundingBox(obj)

    def __eq__(self, other):
        return other is not None \
            and self._frame == other._frame \
            and self._obj == other._obj \
            and self._string == other._string

    def _treatAsDuplicate(self, prior):
        if self._obj != prior._obj or self._frame != prior._frame:
            msg = "MOUSE REVIEW: Not a duplicate: different objects"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self.getString() and prior.getString() and not self._isSubstringOf(prior):
            msg = "MOUSE REVIEW: Not a duplicate: not a substring of"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self._x == prior._x and self._y == prior._y:
            msg = "MOUSE REVIEW: Treating as duplicate: mouse didn't move"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        interval = self._time - prior._time
        if interval > 0.5:
            msg = f"MOUSE REVIEW: Not a duplicate: was {interval:.2f}s ago"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        msg = "MOUSE REVIEW: Treating as duplicate"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return True

    def _treatAsSingleObject(self):
        if not AXObject.supports_text(self._obj):
            return True

        if not self._obj.queryText().characterCount:
            return True

        return False

    def _getStringContext(self):
        """Returns the _StringContext associated with the specified point."""

        if not (self._script and self._obj):
            return _StringContext(self._obj)

        if self._treatAsSingleObject():
            return _StringContext(self._obj, self._script)

        try:
            string, start, end = self._script.utilities.textAtPoint(
                self._obj, self._x, self._y, self._boundary)
        except Exception as error:
            msg = f"MOUSE REVIEW: Exception getting text at point: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return _StringContext(self._obj, self._script)

        if string:
            string = self._script.utilities.expandEOCs(self._obj, start, end)

        return _StringContext(self._obj, self._script, string, start, end)

    def _getContainer(self):
        roles = [Atspi.Role.DIALOG,
                 Atspi.Role.FRAME,
                 Atspi.Role.LAYERED_PANE,
                 Atspi.Role.MENU,
                 Atspi.Role.PAGE_TAB,
                 Atspi.Role.TOOL_BAR,
                 Atspi.Role.WINDOW]
        return AXObject.find_ancestor(self._obj, lambda x: AXObject.get_role(x) in roles)

    def _isSubstringOf(self, other):
        """Returns True if this is a substring of other."""

        return self._string.isSubstringOf(other._string)

    def getObject(self):
        """Returns the accessible object associated with this context."""

        return self._obj

    def getBoundingBox(self):
        """Returns the bounding box associated with this context."""

        x, y, width, height = self._string.getBoundingBox()
        if not (width or height):
            return self._boundingBox

        return x, y, width, height

    def getString(self):
        """Returns the string associated with this context."""

        return self._string.getString()

    def getTime(self):
        """Returns the time associated with this context."""

        return self._time

    def _isInlineChild(self, prior):
        if not self._obj or not prior._obj:
            return False

        if AXObject.get_parent(prior._obj) != self._obj:
            return False

        if self._treatAsSingleObject():
            return False

        return AXUtilities.is_link(prior._obj)

    def present(self, prior):
        """Presents this context to the user."""

        if self == prior or self._treatAsDuplicate(prior):
            msg = "MOUSE REVIEW: Not presenting due to no change"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        interrupt = self._obj and self._obj != prior._obj \
            or math.sqrt((self._x - prior._x)**2 + (self._y - prior._y)**2) > 25

        if interrupt:
            self._script.presentationInterrupt()

        if self._frame and self._frame != prior._frame:
            self._script.presentObject(self._frame,
                                        alreadyFocused=True,
                                        inMouseReview=True,
                                        interrupt=True)

        if self._script.utilities.containsOnlyEOCs(self._obj):
            msg = "MOUSE REVIEW: Not presenting object which contains only EOCs"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self._obj and self._obj != prior._obj and not self._isInlineChild(prior):
            priorObj = prior._obj or self._getContainer()
            focus_manager.getManager().emit_region_changed(
                self._obj, mode=focus_manager.MOUSE_REVIEW)
            self._script.presentObject(self._obj, priorObj=priorObj, inMouseReview=True)
            if self._string.getString() == AXObject.get_name(self._obj):
                return True
            if not self._script.utilities.isEditableTextArea(self._obj):
                return True
            if AXUtilities.is_table_cell(self._obj) \
               and self._string.getString() == self._script.utilities.displayedText(self._obj):
                return True

        if self._string != prior._string and self._string.present():
            return True

        return True


class MouseReviewer:
    """Main class for the mouse-review feature."""

    def __init__(self):
        self._active = settings_manager.getManager().getSetting("enableMouseReview")
        self._currentMouseOver = _ItemContext()
        self._workspace = None
        self._windows = []
        self._all_windows = []
        self._handlerIds = {}
        self._eventListener = Atspi.EventListener.new(self._listener)
        self.inMouseEvent = False
        self._event_queue = deque()
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

        if not _mouseReviewCapable:
            msg = "MOUSE REVIEW ERROR: Wnck is not available"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if not self._active:
            return

        self.activate()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the mouse-review keybindings."""

        if refresh:
            msg = "MOUSE REVIEW: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.isEmpty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the mouse-review handlers."""

        if refresh:
            msg = "MOUSE REVIEW: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up the mouse-review input event handlers."""

        self._handlers = {}

        self._handlers["toggleMouseReviewHandler"] = \
            input_event.InputEventHandler(
                self.toggle,
                cmdnames.MOUSE_REVIEW_TOGGLE)

        msg = "MOUSE REVIEW: Handlers set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the mouse-review key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("toggleMouseReviewHandler")))

        msg = "MOUSE REVIEW: Bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def activate(self):
        """Activates mouse review."""

        if not _mouseReviewCapable:
            msg = "MOUSE REVIEW ERROR: Wnck is not available"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        # Set up the initial object as the one with the focus to avoid
        # presenting irrelevant info the first time.
        obj = focus_manager.getManager().get_locus_of_focus()
        script = None
        frame = None
        if obj:
            script = script_manager.getManager().getScript(AXObject.get_application(obj), obj)
        if script:
            frame = script.utilities.topLevelObject(obj)
        self._currentMouseOver = _ItemContext(obj=obj, frame=frame, script=script)

        self._eventListener.register("mouse:abs")
        screen = Wnck.Screen.get_default()
        if screen:
            # On first startup windows and workspace are likely to be None,
            # but the signals we connect to will get emitted when proper values
            # become available;  but in case we got disabled and re-enabled we
            # have to get the initial values manually.
            stacked = screen.get_windows_stacked()
            if stacked:
                stacked.reverse()
                self._all_windows = stacked
            self._workspace = screen.get_active_workspace()
            if self._workspace:
                self._update_workspace_windows()

            i = screen.connect("window-stacking-changed", self._on_stacking_changed)
            self._handlerIds[i] = screen
            i = screen.connect("active-workspace-changed", self._on_workspace_changed)
            self._handlerIds[i] = screen

        self._active = True

    def deactivate(self):
        """Deactivates mouse review."""

        self._eventListener.deregister("mouse:abs")
        for key, value in self._handlerIds.items():
            value.disconnect(key)
        self._handlerIds = {}
        self._workspace = None
        self._windows = []
        self._all_windows = []
        self._event_queue.clear()
        self._active = False

    def getCurrentItem(self):
        """Returns the accessible object being reviewed."""

        if not _mouseReviewCapable:
            return None

        if not self._active:
            return None

        obj = self._currentMouseOver.getObject()

        if time.time() - self._currentMouseOver.getTime() > 0.1:
            tokens = ["MOUSE REVIEW: Treating", obj, "as stale"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        return obj

    def toggle(self, script=None, event=None):
        """Toggle mouse reviewing on or off."""

        if not _mouseReviewCapable:
            return

        self._active = not self._active
        settings_manager.getManager().setSetting("enableMouseReview", self._active)

        if not self._active:
            self.deactivate()
            msg = messages.MOUSE_REVIEW_DISABLED
        else:
            self.activate()
            msg = messages.MOUSE_REVIEW_ENABLED

        script = script_manager.getManager().getActiveScript()
        if script is not None:
            script.presentMessage(msg)

    def _update_workspace_windows(self):
        self._windows = [w for w in self._all_windows
                         if w.is_on_workspace(self._workspace)]

    def _on_stacking_changed(self, screen):
        """Callback for Wnck's window-stacking-changed signal."""

        stacked = screen.get_windows_stacked()
        stacked.reverse()
        self._all_windows = stacked
        if self._workspace:
            self._update_workspace_windows()

    def _on_workspace_changed(self, screen, prev_ws=None):
        """Callback for Wnck's active-workspace-changed signal."""

        self._workspace = screen.get_active_workspace()
        self._update_workspace_windows()

    def _contains_point(self, obj, x, y):
        try:
            return obj.queryComponent().contains(x, y, Atspi.CoordType.WINDOW)
        except Exception:
            return False

    def _accessible_window_at_point(self, pX, pY):
        """Returns the accessible window and window based coordinates for the screen coordinates."""

        window = None
        for w in self._windows:
            if w.is_minimized():
                continue

            x, y, width, height = w.get_client_window_geometry()
            if x <= pX <= x + width and y <= pY <= y + height:
                window = w
                break

        if not window:
            return None, -1, -1

        windowApp = window.get_application()
        if not windowApp:
            return None, -1, -1

        app = AXUtilities.get_application_with_pid(windowApp.get_pid())
        if not app:
            return None, -1, -1

        # Adjust the pointer screen coordinates to be relative to the window. This is
        # needed because we won't be able to get the screen coordinates in Wayland.
        relativeX = pX - x
        relativeY = pY - y

        candidates = [o for o in AXObject.iter_children(
            app, lambda x: self._contains_point(x, relativeX, relativeY))]
        if len(candidates) == 1:
            return candidates[0], relativeX, relativeY

        name = window.get_name()
        matches = [o for o in candidates if AXObject.get_name(o) == name]
        if len(matches) == 1:
            return matches[0], relativeX, relativeY

        matches = [o for o in matches if AXUtilities.is_active(o)]
        if len(matches) == 1:
            return matches[0],relativeX, relativeY

        return None, -1, -1

    def _on_mouse_moved(self, event):
        """Callback for mouse:abs events."""

        pX, pY = event.detail1, event.detail2
        window, windowX, windowY = self._accessible_window_at_point(pX, pY)
        tokens = [f"MOUSE REVIEW: Window at ({pX}, {pY}) is", window]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not window:
            return

        script = script_manager.getManager().getScript(AXObject.get_application(window))
        if not script:
            return

        focus = focus_manager.getManager().get_locus_of_focus()
        if AXObject.is_dead(focus):
            menu = None
        elif AXUtilities.is_menu(focus):
            menu = focus
        else:
            menu = AXObject.find_ancestor(focus, AXUtilities.is_menu)

        obj = None
        if menu:
            obj = script.utilities.descendantAtPoint(menu, windowX, windowY)
            tokens = ["MOUSE REVIEW: Object in", menu, f"at ({windowX}, {windowY}) is", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if obj is None:
            obj = script.utilities.descendantAtPoint(window, windowX, windowY)
            tokens = ["MOUSE REVIEW: Object in", window, f"at ({windowX}, {windowY}) is", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.getManager().getScript(AXObject.get_application(window), obj)
        if menu and obj and not AXObject.find_ancestor(obj, AXUtilities.is_menu):
            if script.utilities.intersectingRegion(obj, menu) != (0, 0, 0, 0):
                tokens = ["MOUSE REVIEW:", obj, "believed to be under", menu]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return

        objDocument = script.utilities.getTopLevelDocumentForObject(obj)
        if objDocument and script.utilities.inDocumentContent():
            document = script.utilities.activeDocument()
            if document != objDocument:
                tokens = ["MOUSE REVIEW:", obj, "is not in active document", document]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return

        boundary = None
        x, y, width, height = self._currentMouseOver.getBoundingBox()
        if y <= windowY <= y + height and self._currentMouseOver.getString():
            boundary = Atspi.TextBoundaryType.WORD_START
        elif obj == self._currentMouseOver.getObject():
            boundary = Atspi.TextBoundaryType.LINE_START
        elif AXUtilities.is_selectable(obj):
            boundary = Atspi.TextBoundaryType.LINE_START
        elif script.utilities.isMultiParagraphObject(obj):
            boundary = Atspi.TextBoundaryType.LINE_START

        if len(self._event_queue):
            msg = "MOUSE REVIEW: Mouse moved again."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        new = _ItemContext(windowX, windowY, obj, boundary, window, script)
        if new.present(self._currentMouseOver):
            self._currentMouseOver = new

    def _process_event(self):
        if not self._event_queue:
            return

        event = self._event_queue.popleft()
        if len(self._event_queue):
            return

        startTime = time.time()
        tokens = ["\nvvvvv PROCESS OBJECT EVENT", event.type, "vvvvv"]
        debug.printTokens(debug.LEVEL_INFO, tokens, False)

        self.inMouseEvent = True
        self._on_mouse_moved(event)
        self.inMouseEvent = False

        msg = f"TOTAL PROCESSING TIME: {time.time() - startTime:.4f}\n"
        msg += f"^^^^^ PROCESS OBJECT EVENT {event.type} ^^^^^\n"
        debug.printMessage(debug.LEVEL_INFO, msg, False)

    def _listener(self, event):
        """Generic listener for events of interest."""

        if event.type.startswith("mouse:abs"):
            self._event_queue.append(event)
            GLib.timeout_add(50, self._process_event)


_reviewer = MouseReviewer()
def getReviewer():
    return _reviewer
