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
displays, but I've only really built in support for a single line display.]]]

As a means to keep things simple for now, regions can only exist on a single
line.  That is, a region cannot cross line boundaries.

The main entry points into this module are as follows:

    o init/shutdown:  for initializing and shutting down this module

    o Line:           a class whose instances maintain an ordered list
                      of Regions

    o Region:         a class whose instances represent an area of text;
                      subclasses of Regions include Component, Text, etc.

    o clear:          clears the logical structure, but keeps the Braille
                      display as is (see refresh)

    o refresh:        repaints the logical structure on the Braille display
                      clipping content based upon the viewport setting
                      
    o addLine:        appends a Line instance to the logical structure

    o setCursor:      sets the position of the cursor (and automatically
                      scrolls the Braille display to show the cursor)

    o setFocus:       utility routine to set the cursor to a region

After initialization, a typical use of this module would be as follows:

    braille.clear()
    line = braille.Line()
    line.addRegion(braille.Region(...))
    line.addRegion(braille.Component(...))
    line.addRegion(braille.Text(...))
    braille.addLine(line)
    braille.setCursor(x,y)
    braille.refresh()

NOTE: for the most part, this module will happily do as requested if it isn't
initialized.  The only impact will be that nothing will be displayed on the
Braille display.
"""

import a11y
import brl
import core
import debug
import eventsynthesizer
import settings

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
# [[[TODO: WDW - Only a height of 1 is support at this time.]]]
#
_displaySize = [0, 0]

# The list of lines on the display.  This represents the entire amount of data
# to be drawn on the display.  It will be clipped by the viewport if too large.
#
_lines = []

# The region with focus.  This will be displayed at the home position.
#
_regionWithFocus = None

# A 0-based index on the physical display that specifies where the
# display of the _regionWithFocus should start.
#
_homePosition = 10

# The viewport is a rectangular region of size _displaySize whose upper left
# corner is defined by the point (x, line number).  As such, the viewport is
# identified solely by its upper left point.
#
_viewport = [0, 0]

# The callback to call on a BrlTTY input event.  This is passed to
# the init method.
#
_callback = None


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
    each region is determined by the string obtained from its getString
    method.
    """

    def __init__(self, string, cursorOffset=0):
        """Creates a new Region containing the given string.
    
        Arguments:
        - string: the string to be displayed
        - cursorOffset: a 0-based index saying where to draw the cursor
                        for this Region if it gets focus.
        """
        
        self.string = string
        self.cursorOffset = cursorOffset
        
    def getString(self):
        """Returns the string associated with this region."""
        return self.string
    
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
        
        self.accessible = accessible
        self.string = string
        self.cursorOffset = cursorOffset
        
    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""
        
        actions = self.accessible.action
        if actions:
            actions.doAction(0)
        else:
            
            # [[[TODO: WDW - HACK to do a mouse button 1 click if we
            # have to.  For example, page tabs don't have any actions
            # but we want to be able to select them with the cursor
            # routing key.]]]
            #
            debug.println(debug.LEVEL_FINER,
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
    [[[TODO: WDW - need to add in text selection capabilities.]]]"""
    
    def __init__(self, accessible, label=None):
        """Creates a new Text region.

        Arguments:
        - accessible: the accessible that implements AccessibleText
        - label: an optional label to display
        """
        
        self.accessible = accessible
        result = a11y.getTextLineAtCaret(self.accessible)
        self.caretOffset = result[1]
        self.lineOffset = result[2]
        self.cursorOffset = self.caretOffset - self.lineOffset

        self.label = label
        if self.label:
            self.string = self.label + " " + result[0]
            self.cursorOffset += len(self.label) + 1
        else:
            self.string = result[0]
            
        
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

        global _regionWithFocus
        
        string = ""
        focusOffset = -1
        for region in self.regions:
            if region == _regionWithFocus:
                focusOffset = len(string)
            string += region.getString()
        return [string, focusOffset]
        
    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of string
        associated with this line.  Note that the zeroeth character may have
        been scrolled off the display."""
        
        # Translate the cursor offset for this line into a cursor offset
        # for a region, and then pass the event off to the region for
        # handling.
        #
        string = ""
        pos = 0
        for region in self.regions:
            string = string + region.getString()
            if len(string) > offset:
                region.processCursorKey(offset - pos)
                break
            else:
                pos = len(string)


def clear():
    """Clears the logical structure, but keeps the Braille display as is
    (until a refresh operation).
    """

    global _lines
    global _regionWithFocus
    
    _lines = []
    _regionWithFocus = None
    _viewport = [0, 0]


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


def setFocus(region):
    """Specififes the region with focus.  This region will be positioned
    at the home position on a refresh.

    Arguments:
    - region: the given region, which much be in a line that has been
              added to the logical display
    """

    global _lines
    global _regionWithFocus
    global _viewport

    _regionWithFocus = region
    
    # Find the line whose Region has focus and adjust the viewport
    # accordingly.
    #
    _viewport = [0, 0]
    if _regionWithFocus is None:
        return

    # Adjust the viewport according to the new region with focus.
    # The goal is to have the first cell of the region be in the
    # home position, but we will give priority to make sure the
    # cursor for the region is on the display.
    #
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
    lineInfo = line.getLineInfo()
    offset = lineInfo[1]

    # If the cursor is too far right, we scroll the viewport
    # so the cursor will be on the last cell of the display.
    #
    if _regionWithFocus.cursorOffset >= _displaySize[0]:
        offset += _regionWithFocus.cursorOffset - _displaySize[0] + 1
    
    _viewport[0] = max(0, offset)

        
def refresh():
    """Repaints the Braille on the physical display.  This clips the entire
    logical structure by the viewport and also sets the cursor to the
    appropriate location.  [[[TODO: WDW - I'm not sure how BrlTTY handles
    drawing to displays with more than one line, so I'm only going to handle
    drawing one line right now.]]]
    """

    global _lines
    global _viewport
    global _displaySize
    global _regionWithFocus

    if len(_lines) == 0:
        brl.writeText(0, "")
        return

    # Get the string for the line.
    #
    line = _lines[_viewport[1]]
    lineInfo = line.getLineInfo()    
    string = lineInfo[0]

    # Now determine the location of the cursor.
    #
    cursor = -1
    focusOffset = lineInfo[1]
    if focusOffset >= 0:
        cursor = _regionWithFocus.cursorOffset + focusOffset

    startPos = max(0, _viewport[0])
    endPos = startPos + _displaySize[0]
    
    # Now normalize the cursor position to BrlTTY, which uses 1 as
    # the first cursor position as opposed to 0.
    #
    cursor = cursor - startPos
    if (cursor < 0) or (cursor >= _displaySize[0]):
        cursor = 0
    else:
        cursor = cursor + 1

    debug.println(debug.LEVEL_INFO, "BRAILLE LINE:  '%s'" % string)

    debug.println(debug.LEVEL_INFO, "     VISIBLE:  '%s', cursor=%d" \
                  % (string[startPos:endPos], cursor))
    
    brl.writeText(cursor, string[startPos:endPos])
    

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
    refresh()


def panLeft(inputEvent=None):
    """Pans the display to the left.
    
    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True to mean the command should be consumed.
    """

    if _viewport[0] > 0:
        _viewport[0] = max(0, _viewport[0] - _displaySize[0])
        
    refresh()

    return True


def panRight(inputEvent=None):
    """Pans the display to the right, limiting the pan to the length
    of the line being displayed.
   
    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True to mean the command should be consumed.
    """

    if len(_lines) > 0:
        lineNum = _viewport[1]    
        newX = _viewport[0] + _displaySize[0]
        lineInfo = _lines[lineNum].getLineInfo()
        string = lineInfo[0]
        if newX < len(string):
            _viewport[0] = newX
            refresh()

    return True


def returnToRegionWithFocus(inputEvent=None):
    """Pans the display so the region with focus is displayed.
    
    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True to mean the command should be consumed.
    """

    global _regionWithFocus

    setFocus(_regionWithFocus)
    refresh()

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

    global _lines
    global _viewport
    global _displaySize

    # [[[TODO: WDW - need to better understand why BrlTTY is giving
    # us larger values on the Alva display.  For now, we just strip
    # it off using 0xfff.]]]
    #
    # command = command & 0xfff
    _printBrailleEvent(debug.LEVEL_FINE, command)

    # [[[TODO: WDW - related to the above commented out line, DaveM
    # suspects the Alva driver is sending us a repeat flag.  So...let's
    # kill a couple birds here until BrlTTY 3.8 fixes the problem:
    # we'll disable autorepeat and we'll also strip out the autorepeat
    # flag if this is the first press of a button.]]]
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

    if (command >= 0) and (command <= CMD_MAX):
        if command == CMD_FWINLT:
            panLeft()
        elif command == CMD_FWINRT:
            panRight()
        elif command == CMD_HOME:
            returnToRegionWithFocus()
    elif (command >= 0x100) and (command < (0x100 + _displaySize[0])):
        if len(_lines) > 0:
            cursor = (command - 0x100) + _viewport[0]
            lineNum = _viewport[1]    
            _lines[lineNum].processCursorKey(cursor)


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
    refresh()
    
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
