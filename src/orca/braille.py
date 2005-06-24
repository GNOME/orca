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

import brl
import core
import debug

# If True, this module has been initialized.
#
_initialized = False

# The index for each of these maps to BrlAPI's brldefs.h file.
#
BRLAPI_COMMANDS = [
  "CMD_NOOP",
  "CMD_LNUP",
  "CMD_LNDN",
  "CMD_WINUP",
  "CMD_WINDN",
  "CMD_PRDIFLN",
  "CMD_NXDIFLN",
  "CMD_ATTRUP",
  "CMD_ATTRDN",
  "CMD_TOP",
  "CMD_BOT",
  "CMD_TOP_LEFT",
  "CMD_BOT_LEFT",
  "CMD_PRPGRPH",
  "CMD_NXPGRPH",
  "CMD_PRPROMPT",
  "CMD_NXPROMPT",
  "CMD_PRSEARCH",
  "CMD_NXSEARCH",
  "CMD_CHRLT",
  "CMD_CHRRT",
  "CMD_HWINLT",
  "CMD_HWINRT",
  "CMD_FWINLT",
  "CMD_FWINRT",
  "CMD_FWINLTSKIP",
  "CMD_FWINRTSKIP",
  "CMD_LNBEG",
  "CMD_LNEND",
  "CMD_HOME",
  "CMD_BACK",
  "CMD_FREEZE",
  "CMD_DISPMD",
  "CMD_SIXDOTS",
  "CMD_SLIDEWIN",
  "CMD_SKPIDLNS",
  "CMD_SKPBLNKWINS",
  "CMD_CSRVIS",
  "CMD_CSRHIDE",
  "CMD_CSRTRK",
  "CMD_CSRSIZE",
  "CMD_CSRBLINK",
  "CMD_ATTRVIS",
  "CMD_ATTRBLINK",
  "CMD_CAPBLINK",
  "CMD_TUNES",
  "CMD_HELP",
  "CMD_INFO",
  "CMD_LEARN",
  "CMD_PREFMENU",
  "CMD_PREFSAVE",
  "CMD_PREFLOAD",
  "CMD_MENU_FIRST_ITEM",
  "CMD_MENU_LAST_ITEM",
  "CMD_MENU_PREV_ITEM",
  "CMD_MENU_NEXT_ITEM",
  "CMD_MENU_PREV_SETTING",
  "CMD_MENU_NEXT_SETTING",
  "CMD_SAY_LINE",
  "CMD_SAY_ABOVE",
  "CMD_SAY_BELOW",
  "CMD_MUTE",
  "CMD_SPKHOME",
  "CMD_SWITCHVT_PREV",
  "CMD_SWITCHVT_NEXT",
  "CMD_CSRJMP_VERT",
  "CMD_PASTE",
  "CMD_RESTARTBRL",
  "CMD_RESTARTSPEECH"]

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

# The viewport is a rectangular region of size _displaySize whose upper left
# corner is defined by the point (x, line number).  As such, the viewport is
# identified solely by its upper left point.
#
_viewport = [0, 0]

# The current cursor position (x, y) on the Braille display.
# (-1, -1) indicates no cursor is to be drawn.
#
_cursorPosition = [-1, -1]

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

    if (command >= 0) and (command < len(BRLAPI_COMMANDS)):
        debug.printInputEvent(
            level,
            "BRAILLE EVENT: %s (%x)" % (BRLAPI_COMMANDS[command], command))
    else:
        debug.printInputEvent(
            level,
            "BRAILLE EVENT: %x" % command)
    

class Region:
    """A Braille region to be displayed on the display.  The width of
    each region is determined by the string obtained from its getString
    method.
    """

    def __init__(self, string=""):
        """Creates a new Region containing the given string.
    
        Arguments:
        - string: the string to be displayed
        """
        
        self.string = string
        
    def getString(self):
        """Returns the string associated with this region."""
        return self.string
    
    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""
        

class Component(Region):
    """A subclass of Region backed by an accessible.  This Region will react
    to any cursor routing key events and perform the default action on the
    accessible, if a default action exists.
    """
    
    def __init__(self, accessible, string=None):
        """Creates a new Component.

        Arguments:
        - accessible: the accessible
        - string: the string to use (default = accessible.label)
        """
        
        self.accessible = accessible
        if string:
            self.string = string
        else:
            self.string = self.accessible.label

    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""
        
        actions = self.accessible.action
        if actions is None:
            debug.println(debug.LEVEL_FINER,
                          "braille.Component.processCursorKey: no action")
        else:
            actions.doAction(0)
        

class ToggleButton(Component):
    """A subclass of Region backed by an accessible check box.  This Region
    will react to any cursor routing key events and perform the default action
    on the accessible.  This region also includes the state of the check box.
    """
    
    def __init__(self, accessible):
        self.accessible = accessible
        set = self.accessible.state
        if set.count(core.Accessibility.STATE_CHECKED):
            self.string = "<x> " + self.accessible.label
        else:
            self.string = "< > " + self.accessible.label

            
class RadioButton(Component):
    """A subclass of Region backed by an accessible radio button.  This Region
    will react to any cursor routing key events and perform the default action
    on the accessible.  This region also includes the state of the radio
    button.
    """
    
    def __init__(self, accessible):
        self.accessible = accessible
        set = self.accessible.state
        if set.count(core.Accessibility.STATE_CHECKED):
            self.string = "<x>" + self.accessible.label
        else:
            self.string = "< > " + self.accessible.label

            
class Text(Region):
    """A subclass of Region backed by a Text object.  This Region will
    react to any cursor routing key events by positioning the caret in the
    associated text object. [[[TODO: WDW - need to add in text selection
    capabilities.]]]"""
    
    def __init__(self, accessible, line, lineOffset, caretOffset):
        """Creates a new Text region.

        Arguments:
        - accessible: the accessible that implements AccessibleText
        - line: the string to display (should be a whole line)
        - lineOffset: the 0-based index of the character beginning the line
        - caretOffset: the 0-based index of the caret location
        """
        
        self.accessible = accessible
        self.text = accessible.text
        self.string = line + " "
        self.lineOffset = lineOffset
        self.caretOffset = caretOffset
        
    def processCursorKey(self, offset):
        """Processes a cursor key press on this Component.  The offset is
        0-based, where 0 represents the leftmost character of text associated
        with this region.  Note that the zeroeth character may have been
        scrolled off the display."""
        
        linePosition = offset
        newCaretOffset = self.lineOffset + linePosition
        self.text.setCaretOffset(newCaretOffset)

        
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

    def getString(self):
        string = ""
        for region in self.regions:
            string = string + region.getString()
        return string
    
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
    global _cursorPosition
    
    _lines = []
    _cursorPosition = [-1, -1]


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

    
def setCursor(x, y):
    """Sets the cursor position and automatically scrolls the viewport to
    show the cursor.

    Arguments:
    - x: the 0-based x location for all of the logical content
    - y: the 0-based line number (default = 0)
    """

    if not _initialized:
        return
    
    _cursorPosition[0] = x
    _cursorPosition[1] = y

    # Automatically scroll the viewport to hold the cursor, if necessary.
    # The viewport will move up and down line by line if necessary and
    # left and right by the display size chunks at a time if necessary.
    #
    if _cursorPosition[1] >= 0:
        _viewport[1] = _cursorPosition[1]

    if _cursorPosition[0] >= 0:
        _viewport[0] = 0
        while _cursorPosition[0] >= (_viewport[0] + _displaySize[0]):
            _viewport[0] = _viewport[0] + _displaySize[0]


def setFocus(region, offset=0):
    """Sets the cursor to point to the given region.

    Arguments:
    - region: the given region, which much be in a line that has been
              added to the logical display
    - offset: the offset into the region
    """

    global _lines
    y = 0
    done = False
    for line in _lines:
        x = 0
        for reg in line.regions:
            if reg == region:
                done = True
                break
            else:
                x = x + len(reg.getString())
        if done:
            break
        else:
            y = y + 1

    if done:
        setCursor(x + offset, y)
    else:
        setCursor(-1, -1)

        
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
    global _cursorPosition

    lineNum = _viewport[1]    

    # Get the string for the line.
    #
    string = ""
    if len(_lines) > 0:
        string = _lines[lineNum].getString()

    # Convert the logical cursor location (_cursorPosition) to a physical
    # cursor location.
    #
    cursor = -1
    if _cursorPosition[1] == lineNum:
        if _cursorPosition[0] >= 0:
            cursor = _cursorPosition[0] - _viewport[0]

    # Now normalize the cursor position to BrlTTY, which uses 1 as
    # the first cursor position as opposed to 0.
    #
    if (cursor < 0) or (cursor >= _displaySize[0]):
        cursor = 0
    else:
        cursor = cursor + 1

    brl.writeText(cursor, string[_viewport[0]:])
    

def displayMessage(message, cursor=-1):
    """Displays a single line, setting the cursor to the given position,
    ensuring that the cursor is in view.

    Arguments:
    - message: the string to display
    - cursor: the 0-based cursor position, where -1 (default) means no cursor
    """
    
    clear()
    addLine(Line(Region(message)))
    setCursor(cursor, 0)
    refresh()

        
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
    command = command & 0xfff
    _printBrailleEvent(debug.LEVEL_FINE, command)

    if _callback:
        try:
            # Like key event handlers, a return value of True means
            # the command was consumed.
            #
            if _callback(command):
                return
        except:
            debug.printException(debug.LEVEL_SEVERE)
            return

    if (command >= 0) and (command < len(BRLAPI_COMMANDS)):
        commandString = BRLAPI_COMMANDS[command]
        if commandString == "CMD_FWINLT":
            _viewport[0] = max(0, _viewport[0] - _displaySize[0])
            refresh()
        elif commandString == "CMD_FWINRT":
             if len(_lines) > 0:
                 lineNum = _viewport[1]    
                 newX = _viewport[0] + _displaySize[0]
                 if newX < len(_lines[lineNum].getString()):
                     _viewport[0] = newX
                     refresh()
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
