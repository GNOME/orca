# Mouse reviewer for Orca
#
# Copyright 2008 Eitan Isaacson
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
__copyright__ = "Copyright (c) 2008 Eitan Isaacson"
__license__   = "LGPL"

import gi

from . import debug

try:
    gi.require_version("Wnck", "3.0")
    from gi.repository import Wnck
    _mouseReviewCapable = True
except:
    debug.println(debug.LEVEL_WARNING, \
                  "Python module wnck not found, mouse review not available.")
    _mouseReviewCapable = False

import pyatspi
from gi.repository import Gdk
from gi.repository import GLib

from . import event_manager
from . import script_manager
from . import speech
from . import braille
from . import settings

_eventManager = event_manager.getManager()
_scriptManager = script_manager.getManager()

class BoundingBox:
    """A bounding box, currently it is used to test if a given point is
    inside the bounds of the box.
    """

    def __init__(self, x, y, width, height):
        """Initialize a bounding box.

        Arguments:
        - x: Left border of box.
        - y: Top border of box.
        - width: Width of box.
        - height: Height of box.
        """
        self.x, self.y, self.width, self.height = x, y, width, height

    def isInBox(self, x, y):
        """Test if a given point is inside a box.

        Arguments:
        - x: X coordinate.
        - y: Y coordinate.

        Returns True if point is inside box.
        """
        return (self.x <= x <= self.x + self.width) and \
            (self.y <= y <= self.y + self.height)

class _WordContext:
    """A word on which the mouse id hovering above. This class should have
    enough info to make it unique, so we know when we have left the word.
    """
    def __init__(self, word, acc, start, end):
        """Initialize a word context.

        Arguments:
        - word: The string of the word we are on.
        - acc: The accessible object that contains the word.
        - start: The start offset of the word in the text.
        - end: The end offset of the word in the text.
        """
        self.word = word
        self.acc = acc
        self.start = start
        self.end = end

    def __cmp__(self, other):
        """Compare two word contexts, if they refer to the same word, return 0.
        Otherwise return 1
        """
        if other is None:
            return 1
        return int(not(self.word == other.word and self.acc == other.acc and
                       self.start == other.start and self.end == other.end))

class _ItemContext:
    """An _ItemContext holds all the information of the item we are currently
    hovering above. If the accessible supports word speaking, we also store
    a word context here.
    """
    def __init__(self, x=0, y=0, acc=None, frame=None, app=None, script=None):
        """Initialize an _ItemContext with all the information we have.

        Arguments:
        - x: The X coordinate of the pointer.
        - y: The Y coordinate of the pointer.
        - acc: The end-node accessible at that coordinate.
        - frame: The top-level frame below the pointer.
        - app: The application the pointer is hovering above.
        - script: The script for the context's application.
        """
        self.acc = acc
        self.frame = frame
        self.app = app
        self.script = script
        self.word_ctx = self._getWordContext(x, y)

    def _getWordContext(self, x, y):
        """If the context's accessible supports it, retrieve the word we are
        currently hovering above.

        Arguments:
        - x: The X coordinate of the pointer.
        - y: The Y coordinate of the pointer.

        Returns a _WordContext of the current word, or None.
        """
        if not self.script or not self.script.speakWordUnderMouse(self.acc):
            return None
        word, start, end = self.script.utilities.wordAtCoords(self.acc, x, y)
        return _WordContext(word, self.acc, start, end)

class MouseReviewer:
    """Main class for the mouse-review feature.
    """
    def __init__(self):
        """Initalize a mouse reviewer class.
        """
        if not _mouseReviewCapable:
            return

        # Need to do this and allow the main loop to cycle once to get any info
        # IMPORTANT: This causes orca to segfault upon launch in Wayland.
        # wnck_screen = Wnck.Screen.get_default()
        self.active = False
        self._currentMouseOver = _ItemContext()
        self._oldMouseOver = _ItemContext()
        self._lastReportedCoord = None

    def toggle(self, on=None):
        """Toggle mouse reviewing on or off.

        Arguments:
        - on: If set to True or False, explicitly toggles reviewing on or off.
        """
        if not _mouseReviewCapable:
            return

        if on is None:
            on = not self.active
        if on and not self.active:
            _eventManager.registerModuleListeners(
                {"mouse:abs":self._onMouseMoved})
        elif not on and self.active:
            _eventManager.deregisterModuleListeners(
                {"mouse:abs":self._onMouseMoved})
        self.active = on

    def _onMouseMoved(self, event):
        """Callback for "mouse:abs" AT-SPI event. We will check after the dwell
        delay if the mouse moved away, if it didn't we will review the
        component under it.

        Arguments:
        - event: The event we recieved.
        """
        if settings.mouseDwellDelay:
            GLib.timeout_add(settings.mouseDwellDelay,
                             self._mouseDwellTimeout,
                             event.detail1,
                             event.detail2)
        else:
            self._mouseDwellTimeout(event.detail1, event.detail2)

    def _mouseDwellTimeout(self, prev_x, prev_y):
        """Dwell timout callback. If we are still dwelling, review the
        component.

        Arguments:
        - prev_x: Previous X coordinate of mouse pointer.
        - prev_y: Previous Y coordinate of mouse pointer.
        """
        display = Gdk.Display.get_default()
        screen, x, y, flags =  display.get_pointer()
        if abs(prev_x - x) <= settings.mouseDwellMaxDrift \
           and abs(prev_y - y) <= settings.mouseDwellMaxDrift \
           and not (x, y) == self._lastReportedCoord:
            self._lastReportedCoord = (x, y)
            self._reportUnderMouse(x, y)
        return False

    def _reportUnderMouse(self, x, y):
        """Report the element under the given coordinates:

        Arguments:
        - x: X coordinate.
        - y: Y coordinate.
        """
        current_element = self._getContextUnderMouse(x, y)
        if not current_element:
            return

        self._currentMouseOver, self._oldMouseOver = \
            current_element, self._currentMouseOver

        output_obj = []

        if current_element.acc.getRole() in (pyatspi.ROLE_MENU_ITEM,
                                             pyatspi.ROLE_COMBO_BOX) and \
                current_element.acc.getState().contains(
                    pyatspi.STATE_SELECTED):
            # If it is selected, we are probably doing that by hovering over it
            # Orca will report this in any case.
            return

        if self._currentMouseOver.frame != self._oldMouseOver.frame and \
                settings.mouseDwellDelay == 0:
            output_obj.append(self._currentMouseOver.frame)

        if self._currentMouseOver.acc != self._oldMouseOver.acc \
                or (settings.mouseDwellDelay > 0 and \
                        not self._currentMouseOver.word_ctx):
            output_obj.append(self._currentMouseOver.acc)

        if self._currentMouseOver.word_ctx:
            if self._currentMouseOver.word_ctx != self._oldMouseOver.word_ctx:
                output_obj.append(self._currentMouseOver.word_ctx.word)

        self._outputElements(output_obj)
        return False

    def _outputElements(self, output_obj):
        """Output the given elements.
        TODO: Now we are mainly using WhereAmI, we might need to find out a
        better, less verbose output method.

        Arguments:
        - output_obj: A list of objects to output, could be accessibles and
        text.
        """
        if output_obj:
            speech.stop()
        for obj in output_obj:
            if obj is None:
                continue
            if isinstance(obj, str):
                speech.speak(obj)
                # TODO: There is probably something more useful that we could
                # display.
                braille.displayMessage(obj)
            else:
                speech.speak(
                    self._currentMouseOver.script.speechGenerator.\
                        generateSpeech(obj))
                self._currentMouseOver.script.updateBraille(obj)

    def _getZOrder(self, frame_name):
        """Determine the stack position of a given window.

        Arguments:
        - frame_name: The name of the window.

        Returns position of given window in window-managers stack.
        """
        # This is neccesary because z-order is still broken in AT-SPI.
        wnck_screen = Wnck.Screen.get_default()
        window_order = \
            [w.get_name() for w in wnck_screen.get_windows_stacked()]
        return window_order.index(frame_name)

    def _getContextUnderMouse(self, x, y):
        """Get the context under the mouse.

        Arguments:
        - x: X coordinate.
        - y: Y coordinate.

        Returns _ItemContext of the component under the mouse.
        """

        # Inspect accessible under mouse
        desktop = pyatspi.Registry.getDesktop(0)
        top_window = [None, -1]
        for app in desktop:
            if not app:
                continue
            script = _scriptManager.getScript(app)
            if not script:
                continue
            for frame in app:
                if not frame:
                    continue
                acc = script.utilities.componentAtDesktopCoords(frame, x, y)
                if acc:
                    try:
                        z_order = self._getZOrder(frame.name)
                    except ValueError:
                        # It's possibly a popup menu, so it would not be in
                        # our frame name list.
                        # And if it is, it is probably the top-most
                        # component.
                        try:
                            if acc.queryComponent().getLayer() == \
                                    pyatspi.LAYER_POPUP:
                                return _ItemContext(x, y, acc, frame,
                                                    app, script)
                        except:
                            pass
                    else:
                        if z_order > top_window[-1]:
                            top_window = \
                                [_ItemContext(x, y, acc, frame, app, script),
                                 z_order]
        return top_window[0]

# Initialize a singleton reviewer.
if Gdk.Display.get_default():
    mouse_reviewer = MouseReviewer()
else:
    raise RuntimeError('Cannot initialize mouse review, no display')

def toggle(script=None, event=None):
    """
    Toggle the reviewer on or off.

    Arguments:
    - script: Given script if this was called as a keybinding callback.
    - event: Given event if this was called as a keybinding callback.
    """
    mouse_reviewer.toggle()
