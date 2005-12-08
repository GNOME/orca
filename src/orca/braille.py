# Orca
#
# Copyright 2005 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""A very experimental approach to the refreshable Braille display.  This
module treats each line of the display as a sequential set of regions, where
each region can potentially backed by an Accessible object.  Depending upon
the Accessible object, the cursor routing keys can be used to perform
operations on the Accessible object, such as invoking default actions or
moving the text caret.

The logical structure maintained by this module is a potentially a very large
2 dimensional text area.  For each line, the text for each region is merely
concatenated together, possibly creating a line that is longer than the
physical display.  In addition, there may be any number of lines.  This module
uses the physical display as a viewport into this large area, and provides
support for the user to press BrlTTY command keys to scroll this viewport to
view all the content.  [[[TODO: WDW - the goal is to support multi-line
displays, but I've only really built in support for a single line display.
Logged as bugzilla bug 319752.]]]

As a means to keep things simple for now, regions can only exist on a single
line.  That is, a region cannot cross line boundaries.

After initialization, a typical use of this module would be as follows:

    braille.clear()
    line = braille.Line()
    line.addRegion(braille.Region(...))
    line.addRegion(braille.Component(...))
    textRegion = braille.Text(...)
    line.addRegion(textRegion)
    braille.addLine(line)
    braille.setFocus(textRegion)
    braille.refresh()

NOTE: for the most part, this module will happily do as requested if it isn't
initialized.  The only impact will be that nothing will be displayed on the
Braille display.
"""

import atspi
import brl
import debug
import eventsynthesizer

from orca_i18n import _                          # for gettext support
from rolenames import getShortBrailleForRoleName # localized role names
from rolenames import getLongBrailleForRoleName  # localized role names

# If True, this module has been initialized.
#
_initialized = False

# Each of these maps to BrlAPI's brldefs.h file.
#
CMD_NOOP              = 0x00
CMD_LNUP              = 0x01
CMD_LNDN              = 0x02
CMD_WINUP             = 0x03
CMD_WINDN             = 0x04
CMD_PRDIFLN           = 0x05
CMD_NXDIFLN           = 0x06
CMD_ATTRUP            = 0x07
CMD_ATTRDN            = 0x08
CMD_TOP               = 0x09
CMD_BOT               = 0x0a
CMD_TOP_LEFT          = 0x0b
CMD_BOT_LEFT          = 0x0c
CMD_PRPGRPH           = 0x0d
CMD_NXPGRPH           = 0x0e
CMD_PRPROMPT          = 0x0f
CMD_NXPROMPT          = 0x10
CMD_PRSEARCH          = 0x11
CMD_NXSEARCH          = 0x12
CMD_CHRLT             = 0x13
CMD_CHRRT             = 0x14
CMD_HWINLT            = 0x15
CMD_HWINRT            = 0x16
CMD_FWINLT            = 0x17
CMD_FWINRT            = 0x18
CMD_FWINLTSKIP        = 0x19
CMD_FWINRTSKIP        = 0x1a
CMD_LNBEG             = 0x1b
CMD_LNEND             = 0x1c
CMD_HOME              = 0x1d
CMD_BACK              = 0x1e
CMD_FREEZE            = 0x1f
CMD_DISPMD            = 0x20
CMD_SIXDOTS           = 0x21
CMD_SLIDEWIN          = 0x22
CMD_SKPIDLNS          = 0x23
CMD_SKPBLNKWINS       = 0x24
CMD_CSRVIS            = 0x25
CMD_CSRHIDE           = 0x26
CMD_CSRTRK            = 0x27
CMD_CSRSIZE           = 0x28
CMD_CSRBLINK          = 0x29
CMD_ATTRVIS           = 0x2a
CMD_ATTRBLINK         = 0x2b
CMD_CAPBLINK          = 0x2c
CMD_TUNES             = 0x2d
CMD_HELP              = 0x2e
CMD_INFO              = 0x2f
CMD_LEARN             = 0x30
CMD_PREFMENU          = 0x31
CMD_PREFSAVE          = 0x32
CMD_PREFLOAD          = 0x33
CMD_MENU_FIRST_ITEM   = 0x34
CMD_MENU_LAST_ITEM    = 0x35
CMD_MENU_PREV_ITEM    = 0x36
CMD_MENU_NEXT_ITEM    = 0x37
CMD_MENU_PREV_SETTING = 0x38
CMD_MENU_NEXT_SETTING = 0x39
CMD_SAY_LINE          = 0x3a
CMD_SAY_ABOVE         = 0x3b
CMD_SAY_BELOW         = 0x3c
CMD_MUTE              = 0x3d
CMD_SPKHOME           = 0x3e
CMD_SWITCHVT_PREV     = 0x3f
CMD_SWITCHVT_NEXT     = 0x40
CMD_CSRJMP_VERT       = 0x41
CMD_PASTE             = 0x42
CMD_RESTARTBRL        = 0x43
CMD_RESTARTSPEECH     = 0x44
CMD_MAX               = 0x44

BRL_FLG_REPEAT_INITIAL= 0x800000
BRL_FLG_REPEAT_DELAY  = 0x400000

# The size of the physical display (width, height).  The coordinate system of
# the display is set such that the upper left is (0,0), x values increase from
# left to right, and y values increase from top to bottom.
#
# For the purposes of testing w/o a braille display, we'll set the display
# size to width=32 and height=1.
#
# [[[TODO: WDW - Only a height of 1 is support at this time.]]]
#
_displaySize = [32, 1]

# The list of lines on the display.  This represents the entire amount of data
# to be drawn on the display.  It will be clipped by the viewport if too large.
#
_lines = []

# The region with focus.  This will be displayed at the home position.
#
_regionWithFocus = None

# The viewport is a rectangular region of size _displaySize whose upper left
# corner is defined by the point (x, line number).  As such, the viewport is
# identified solely by its upper left point.
#
_viewport = [0, 0]

# The callback to call on a BrlTTY input event.  This is passed to
# the init method.
#
_callback = None

# If True, the given portion of the currently displayed line is showing
# on the display.
#
endIsShowing = False
beginningIsShowing = False

# 1-based offset saying which braille cell has the cursor.  A value
# of 0 means no cell has the cursor.
#
cursorCell = 0

def _printBrailleEvent(level, command):
    """Prints out a Braille event.  The given level may be overridden
    if the eventDebugLevel (see debug.setEventDebugLevel) is greater in
    debug.py.

    Arguments:
    - command: the BrlAPI command for the key that was pressed.
    """

    debug.printInputEvent(
        level,
        "BRAILLE EVENT: %x" % command)

class Region:
    """A Braille region to be displayed on the display.  The width of
    each region is determined by its string.
    """

    def __init__(self, string, cursorOffset=0):
        """Creates a new Region containing the given string.

        Arguments:
        - string: the string to be displayed
        - cursorOffset: a 0-based index saying where to draw the cursor
                        for this Region if it gets focus.
        """

        if not string:
            string = ""

        if string[-1:] == "\n":
            string = string[:-1]

        self.string = string
        self.cursorOffset = cursorOffset

    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""
        pass

class Component(Region):
    """A subclass of Region backed by an accessible.  This Region will react
    to any cursor routing key events and perform the default action on the
    accessible, if a default action exists.
    """

    def __init__(self, accessible, string, cursorOffset=0):
        """Creates a new Component.

        Arguments:
        - accessible: the accessible
        - string: the string to use to represent the component
        - cursorOffset: a 0-based index saying where to draw the cursor
                        for this Region if it gets focus.
        """

        Region.__init__(self, string, cursorOffset)
        self.accessible = accessible

    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""

        actions = self.accessible.action
        if actions:
            actions.doAction(0)
        else:

            # [[[WDW - HACK to do a mouse button 1 click if we have
            # to.  For example, page tabs don't have any actions but
            # we want to be able to select them with the cursor
            # routing key.]]]
            #
            debug.println(debug.LEVEL_FINEST,
                          "braille.Component.processCursorKey: no action")
            try:
                eventsynthesizer.clickObject(self.accessible, 1)
            except:
                debug.printException(debug.LEVEL_SEVERE)

class Text(Region):
    """A subclass of Region backed by a Text object.  This Region will
    react to any cursor routing key events by positioning the caret in
    the associated text object. The line displayed will be the
    contents of the text object preceded by an optional label.
    [[[TODO: WDW - need to add in text selection capabilities.  Logged
    as bugzilla bug 319754.]]]"""

    def __init__(self, accessible, label=None):
        """Creates a new Text region.

        Arguments:
        - accessible: the accessible that implements AccessibleText
        - label: an optional label to display
        """

        self.accessible = accessible
        result = atspi.getTextLineAtCaret(self.accessible)
        self.caretOffset = result[1]
        self.lineOffset = result[2]
        cursorOffset = self.caretOffset - self.lineOffset

        self.label = label
        if self.label:
            string = self.label + " " + result[0]
            cursorOffset += len(self.label) + 1
        else:
            string = result[0]

        Region.__init__(self, string, cursorOffset)

    def repositionCursor(self):
        """Attempts to reposition the cursor in response to a new
        caret position.  If it is possible (i.e., the caret is on
        the same line as it was), reposition the cursor and return
        True.  Otherwise, return False.
        """

        result = atspi.getTextLineAtCaret(self.accessible)
        caretOffset = result[1]
        lineOffset = result[2]
        cursorOffset = caretOffset - lineOffset
        if self.label:
            cursorOffset += len(self.label) + 1

        if lineOffset != self.lineOffset:
            return False
        else:
            self.caretOffset = caretOffset
            self.lineOffset = lineOffset
            self.cursorOffset = cursorOffset

        return True

    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of text associated
        with this region.  Note that the zeroeth character may have been
        scrolled off the display."""

        if self.label:
            offset = offset - len(self.label) - 1
            if offset < 0:
                return

        newCaretOffset = self.lineOffset + offset
        self.accessible.text.setCaretOffset(newCaretOffset)

class ReviewComponent(Component):
    """A subclass of Component that is to be used for flat review mode."""

    def __init__(self, accessible, string, cursorOffset, zone):
        """Creates a new Component.

        Arguments:
        - accessible: the accessible
        - string: the string to use to represent the component
        - cursorOffset: a 0-based index saying where to draw the cursor
                        for this Region if it gets focus.
        - zone: the flat review Zone associated with this component
        """

        Component.__init__(self, accessible, string, cursorOffset)
        self.zone = zone

class ReviewText(Region):
    """A subclass of Region backed by a Text object.  This Region will
    does not react to the caret changes, but will react if one updates
    the cursorPosition.  This class is meant to be used by flat review
    mode to show the current character position.
    """

    def __init__(self, accessible, string, lineOffset, zone):
        """Creates a new Text region.

        Arguments:
        - accessible: the accessible that implements AccessibleText
        - string: the string to use to represent the component
        - lineOffset: the character offset into where the text line starts
        - zone: the flat review Zone associated with this component
        """

        Region.__init__(self, string)
        self.accessible = accessible
        self.lineOffset = lineOffset
        self.zone = zone

    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of text associated
        with this region.  Note that the zeroeth character may have been
        scrolled off the display."""

        newCaretOffset = self.lineOffset + offset
        self.accessible.text.setCaretOffset(newCaretOffset)

class Line:
    """A horizontal line on the display.  Each Line is composed of a sequential
    set of Regions.
    """

    def __init__(self, region=None):
        self.regions = []
        self.string = ""
        if region:
            self.addRegion(region)

    def addRegion(self, region):
        self.regions.append(region)

    def addRegions(self, regions):
        self.regions.extend(regions)

    def getLineInfo(self):
        """Computes the complete string for this line as well as a
        0-based index where the focused region starts on this line.
        If the region with focus is not on this line, then the index
        will be -1.

        Returns [string, offsetIndex]
        """

        string = ""
        focusOffset = -1
        for region in self.regions:
            if region == _regionWithFocus:
                focusOffset = len(string)
            string += region.string

        return [string, focusOffset]

    def getRegionAtOffset(self, offset):
        """Finds the Region at the given 0-based offset in this line.

        Returns the [region, offsetinregion] where the region is
        the region at the given offset, and offsetinregion is the
        0-based offset from the beginning of the region, representing
        where in the region the given offset is."""

        # Translate the cursor offset for this line into a cursor offset
        # for a region, and then pass the event off to the region for
        # handling.
        #
        region = None
        string = ""
        pos = 0
        for region in self.regions:
            string = string + region.string
            if len(string) > offset:
                break
            else:
                pos = len(string)

        return [region, offset - pos]

    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of string
        associated with this line.  Note that the zeroeth character may have
        been scrolled off the display."""

        [region, regionOffset] = self.getRegionAtOffset(offset)
        region.processCursorKey(regionOffset)

def getRegionAtCell(cell):
    """Given a 1-based cell offset, return the braille region
    associated with that cell in the form of [region, offsetinregion]
    where 'region' is the region associated with the cell and
    'offsetinregion' is the 0-based offset of where the cell is
    in the region, where 0 represents the beginning of the region, """

    if len(_lines) > 0:
        offset = (cell - 1) + _viewport[0]
        lineNum = _viewport[1]
        return _lines[lineNum].getRegionAtOffset(offset)
    else:
        return [None, -1]

def clear():
    """Clears the logical structure, but keeps the Braille display as is
    (until a refresh operation).
    """

    global _lines
    global _regionWithFocus
    global _viewport

    _lines = []
    _regionWithFocus = None
    _viewport = [0, 0]

def setLines(lines):
    global _lines
    _lines = lines

def addLine(line):
    """Adds a line to the logical display for painting.  The line is added to
    the end of the current list of known lines.  It is necessary for the
    viewport to be over the lines and for refresh to be called for the new
    line to be painted.

    Arguments:
    - line: an instance of Line to add.
    """

    global _lines

    _lines.append(line)
    line._index = len(_lines)

def getShowingLine():
    """Returns the Line that is currently being painted on the display.
    """
    return _lines[_viewport[1]]

def setFocus(region, panToFocus=True):
    """Specififes the region with focus.  This region will be positioned
    at the home position if panToFocus is True.

    Arguments:
    - region: the given region, which much be in a line that has been
              added to the logical display
    """

    global _regionWithFocus

    _regionWithFocus = region

    if not panToFocus or (not _regionWithFocus):
        return

    # Adjust the viewport according to the new region with focus.
    # The goal is to have the first cell of the region be in the
    # home position, but we will give priority to make sure the
    # cursor for the region is on the display.  For example, when
    # faced with a long text area, we'll show the position with
    # the caret vs. showing the beginning of the region.

    lineNum = 0
    done = False
    for line in _lines:
        for reg in line.regions:
            if reg == _regionWithFocus:
                _viewport[1] = lineNum
                done = True
                break
        if done:
            break
        else:
            lineNum += 1

    line = _lines[_viewport[1]]
    [string, offset] = line.getLineInfo()

    # If the cursor is too far right, we scroll the viewport
    # so the cursor will be on the last cell of the display.
    #
    if _regionWithFocus.cursorOffset >= _displaySize[0]:
        offset += _regionWithFocus.cursorOffset - _displaySize[0] + 1

    _viewport[0] = max(0, offset)

def refresh(panToCursor=True, targetCursorCell=0):
    """Repaints the Braille on the physical display.  This clips the entire
    logical structure by the viewport and also sets the cursor to the
    appropriate location.  [[[TODO: WDW - I'm not sure how BrlTTY handles
    drawing to displays with more than one line, so I'm only going to handle
    drawing one line right now.]]]

    Arguments:

    - panToCursor: if True, will adjust the viewport so the cursor is
                   showing.
    - targetCursorCell: Only effective if panToCursor is True.
                        0 means automatically place the cursor somewhere
                        on the display so as to minimize movement but
                        show as much of the line as possible.  A positive
                        value is a 1-based target cell from the left side
                        of the display and a negative value is a 1-based
                        target cell from the right side of the display.
    """

    global endIsShowing
    global beginningIsShowing
    global cursorCell

    if len(_lines) == 0:
        brl.writeText(0, "")
        return

    # Now determine the location of the cursor.  First, we'll figure
    # out the 1-based offset for where we want the cursor to be.  If
    # the target cell is less than zero, it means an offset from the
    # right hand side of the display.
    #
    if targetCursorCell < 0:
        targetCursorCell = _displaySize[0] + targetCursorCell + 1

    # Now, we figure out the 0-based offset for where the cursor
    # actually is in the string.
    #
    line = _lines[_viewport[1]]
    [string, focusOffset] = line.getLineInfo()
    cursorOffset = -1
    if focusOffset >= 0:
        cursorOffset = focusOffset + _regionWithFocus.cursorOffset

    # Now, if desired, we'll automatically pan the viewport to show
    # the cursor.  If there's no targetCursorCell, then we favor the
    # left of the display if we need to pan left, or we favor the
    # right of the display if we need to pan right.
    #
    if panToCursor and (cursorOffset >= 0):
        if len(string) <= _displaySize[0]:
            _viewport[0] = 0
        elif targetCursorCell:
            _viewport[0] = max(0, cursorOffset - targetCursorCell + 1)
        elif cursorOffset < _viewport[0]:
            _viewport[0] = max(0, cursorOffset)
        elif cursorOffset >= (_viewport[0] + _displaySize[0]):
            _viewport[0] = max(0, cursorOffset - _displaySize[0] + 1)

    startPos = _viewport[0]
    endPos = startPos + _displaySize[0]

    # Now normalize the cursor position to BrlTTY, which uses 1 as
    # the first cursor position as opposed to 0.
    #
    cursorCell = cursorOffset - startPos
    if (cursorCell < 0) or (cursorCell >= _displaySize[0]):
        cursorCell = 0
    else:
        cursorCell += 1 # Normalize to 1-based offset

    debug.println(debug.LEVEL_INFO, "BRAILLE LINE:  '%s'" % string)

    debug.println(debug.LEVEL_INFO, "     VISIBLE:  '%s', cursor=%d" \
                  % (string[startPos:endPos], cursorCell))

    brl.writeText(cursorCell, string[startPos:endPos])

    beginningIsShowing = startPos == 0
    endIsShowing = endPos >= len(string)

def displayRegions(regions, indexOfFocusRegion=0):
    """Displays a list of regions on a single line, setting focus to the 
       specified region.

    Arguments:
    - regions: a list of regions to display
    - indexOfFocusRegion: which region in the list should receive focus,
                          or the first one if this is not specified
    """

    clear()
    line = Line()
    for item in regions:
        line.addRegion(item)
    addLine(line)
    setFocus(regions[indexOfFocusRegion])
    refresh()

def displayMessage(message, cursor=-1):
    """Displays a single line, setting the cursor to the given position,
    ensuring that the cursor is in view.

    Arguments:
    - message: the string to display
    - cursor: the 0-based cursor position, where -1 (default) means no cursor
    """

    clear()
    region = Region(message, cursor)
    addLine(Line(region))
    setFocus(region)
    refresh(True)

def panLeft(panAmount=0):
    """Pans the display to the left, limiting the pan to the beginning
    of the line being displayed.

    Arguments:
    - panAmount: the amount to pan.  A value of 0 means the entire
                 width of the physical display.

    Returns True if a pan actually happened.
    """

    oldX = _viewport[0]

    if panAmount == 0:
        panAmount = _displaySize[0]

    if _viewport[0] > 0:
        _viewport[0] = max(0, _viewport[0] - panAmount)

    return oldX != _viewport[0]

def panRight(panAmount=0):
    """Pans the display to the right, limiting the pan to the length
    of the line being displayed.

    Arguments:
    - panAmount: the amount to pan.  A value of 0 means the entire
                 width of the physical display.

    Returns True if a pan actually happened.
    """

    oldX = _viewport[0]

    if panAmount == 0:
        panAmount = _displaySize[0]

    if len(_lines) > 0:
        lineNum = _viewport[1]
        newX = _viewport[0] + panAmount
        [string, focusOffset] = _lines[lineNum].getLineInfo()
        if newX < len(string):
            _viewport[0] = newX

    return oldX != _viewport[0]

def panToOffset(offset):
    """Automatically pan left or right to make sure the current offset is
    showing."""

    while offset < _viewport[0]:
        debug.println(debug.LEVEL_FINEST,
                      "braille.panToOffset (left) %d" % offset)
        if not panLeft():
            break

    while offset >= (_viewport[0] + _displaySize[0]):
        debug.println(debug.LEVEL_FINEST,
                      "braille.panToOffset (right) %d" % offset)
        if not panRight():
            break

def returnToRegionWithFocus(inputEvent=None):
    """Pans the display so the region with focus is displayed.

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True to mean the command should be consumed.
    """

    setFocus(_regionWithFocus)
    refresh(True)

    return True

def _processBrailleEvent(command):
    """Handles BrlTTY command events.  This passes commands on to Orca for
    processing.  If Orca does not handle them (as indicated by a return value
    of false from the callback passed to init, it will attempt to handle the
    command itself - either by panning the viewport or passing cursor routing
    keys to the Regions for handling.

    Arguments:
    - command: the BrlAPI command for the key that was pressed.
    """

    _printBrailleEvent(debug.LEVEL_FINE, command)

    # [[[TODO: WDW - DaveM suspects the Alva driver is sending us a
    # repeat flag.  So...let's kill a couple birds here until BrlTTY
    # 3.8 fixes the problem: we'll disable autorepeat and we'll also
    # strip out the autorepeat flag if this is the first press of a
    # button.]]]
    #
    if command & BRL_FLG_REPEAT_INITIAL:
        command &= ~(BRL_FLG_REPEAT_INITIAL | BRL_FLG_REPEAT_DELAY)
    elif command & BRL_FLG_REPEAT_DELAY:
        return True

    if _callback:
        try:
            # Like key event handlers, a return value of True means
            # the command was consumed.
            #
            if _callback(command):
                return True
        except:
            debug.printException(debug.LEVEL_SEVERE)

    if (command >= 0x100) and (command < (0x100 + _displaySize[0])):
        if len(_lines) > 0:
            cursor = (command - 0x100) + _viewport[0]
            lineNum = _viewport[1]
            _lines[lineNum].processCursorKey(cursor)
	    return True

    return False

def init(callback=None, tty=7):
    """Initializes the braille module, connecting to the BrlTTY driver.

    Arguments:
    - callback: the method to call with a BrlTTY input event.
    - tty: the tty port to take ownership of (default = 7)
    Returns True if the initialization procedure was run or False if this
    module has already been initialized.
    """

    global _initialized
    global _displaySize
    global _callback

    if _initialized:
        return False

    _callback = callback

    if brl.init(tty):
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Braille module has been initialized.")
        brl.registerCallback(_processBrailleEvent)
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Braille module has NOT been initialized.")
        return False

    # [[[TODO: WDW - For some reason, BrlTTY wants to say the height of the
    # Vario is 40 so we hardcode it to 1 for now.]]]
    #
    #_displaySize = (brl.getDisplayWidth(), brl.getDisplayHeight())
    _displaySize = [brl.getDisplayWidth(), 1]

    debug.println(debug.LEVEL_CONFIGURATION,
                  "braille display size = (%d, %d)" \
                  % (_displaySize[0], _displaySize[1]))

    clear()
    refresh(True)

    _initialized = True

    return True

def shutdown():
    """Shuts down the braille module.   Returns True if the shutdown procedure
    was run or False if this module has not been initialized.
    """

    global _initialized

    if not _initialized:
        return False

    brl.shutdown()

    _initialized = False

    return True
