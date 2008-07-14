# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""A very experimental approach to the refreshable Braille display.  This
module treats each line of the display as a sequential set of regions, where
each region can potentially backed by an Accessible object.  Depending upon
the Accessible object, the cursor routing keys can be used to perform
operations on the Accessible object, such as invoking default actions or
moving the text caret.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import logging
log = logging.getLogger("braille")

import signal

try:
    import louis
except ImportError:
    louis = None
    _defaultContractionTable = None
else:
    _defaultContractionTable = louis.getDefaultTable()

# We'll use the official BrlAPI pythons (as of BrlTTY 3.8) if they
# are available.  Otherwise, we'll fall back to our own bindings.
#
try:
    import brlapi
    import gobject

    brlAPI = None
    useBrlAPIBindings = True
    brlAPIRunning = False
    brlAPISourceId = 0
except:
    import brl
    useBrlAPIBindings = False
    brlAPIRunning = False

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import brlmon
except:
    pass
import debug
import eventsynthesizer
import orca_state
import settings

from orca_i18n import _                          # for gettext support

# If True, this module has been initialized.
#
_initialized = False

# The braille monitor
#
monitor = None

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

BRL_FLG_REPEAT_INITIAL = 0x800000
BRL_FLG_REPEAT_DELAY   = 0x400000

# Common names for most used BrlTTY commands, to be shown in the GUI:
# ATM, the ones used in default.py are:
#
command_name = {}

# Translators: this is a command for a button on a refreshable braille
# display (an external hardware device used by people who are blind).
# When pressing the button, the display scrolls to the left.
#
command_name[CMD_FWINLT]   = _("Line Left")

# Translators: this is a command for a button on a refreshable braille
# display (an external hardware device used by people who are blind).
# When pressing the button, the display scrolls to the right.
#
command_name[CMD_FWINRT]   = _("Line Right")

# Translators: this is a command for a button on a refreshable braille
# display (an external hardware device used by people who are blind).
# When pressing the button, the display scrolls up.
#
command_name[CMD_LNUP]     = _("Line Up")

# Translators: this is a command for a button on a refreshable braille
# display (an external hardware device used by people who are blind).
# When pressing the button, the display scrolls down.
#
command_name[CMD_LNDN]     = _("Line Down")

# Translators: this is a command for a button on a refreshable braille
# display (an external hardware device used by people who are blind).
# When pressing the button, the display scrolls to the top left of the
# window.
#
command_name[CMD_TOP_LEFT] = _("Top Left")

# Translators: this is a command for a button on a refreshable braille
# display (an external hardware device used by people who are blind).
# When pressing the button, the display scrolls to the bottom right of
# the window.
#
command_name[CMD_BOT_LEFT] = _("Bottom Right")

# Translators: this is a command for a button on a refreshable braille
# display (an external hardware device used by people who are blind).
# When pressing the button, the display scrolls to position containing
# the cursor.
#
command_name[CMD_HOME]     = _("Cursor Position")

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
viewport = [0, 0]

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

    def __init__(self, string, cursorOffset=0, expandOnCursor=False):
        """Creates a new Region containing the given string.

        Arguments:
        - string: the string to be displayed
        - cursorOffset: a 0-based index saying where to draw the cursor
                        for this Region if it gets focus.
        """

        if not string:
            string = ""

        # If louis is None, then we don't go into contracted mode.
        self.contracted = settings.enableContractedBraille and \
                          louis is not None
        
        self.expandOnCursor = expandOnCursor
        
        string = string.decode("UTF-8")
        string = string.strip('\n')
        self.rawLine = string.encode("UTF-8")

        if self.contracted:
            self.contractionTable = settings.brailleContractionTable or \
                                    _defaultContractionTable

            self.string, self.inPos, self.outPos, self.cursorOffset = \
                         self.contractLine(self.rawLine,
                                           cursorOffset, expandOnCursor)
        else:
            self.string = self.rawLine
            self.cursorOffset = cursorOffset
            
    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""
        pass

    def getAttributeMask(self):
        """Creates a string which can be used as the attrOr field of brltty's
        write structure for the purpose of indicating text attributes and
        selection."""

        # Create an empty mask.
        #
        mask = ['\x00'] * len(self.string)
        return "".join(mask)
    
    def repositionCursor(self):
        """Reposition the cursor offset for contracted mode.
        """
        if self.contracted:
            self.string, self.inPos, self.outPos, self.cursorOffset = \
                       self.contractLine(self.rawLine,
                                         self.cursorOffset,
                                         self.expandOnCursor)

    def contractLine(self, line, cursorOffset=0, expandOnCursor=False):
        """Contract the given line. Returns the contracted line, and the
        cursor position in the contracted line.

        Arguments:
        - line: Line to contract.
        - cursorOffset: Offset of cursor,defaults to 0.
        - expandOnCursor: Expand word under cursor, False by default.
        """

        try:
            cursorOnSpace = line[cursorOffset] == ' '
        except IndexError:
            cursorOnSpace = False
            
        if not expandOnCursor or cursorOnSpace:
            contracted, inPos, outPos, cursorPos = \
                             louis.translate([self.contractionTable],
                                             line.decode(),
                                             cursorPos=cursorOffset)
        else:
            contracted, inPos, outPos, cursorPos = \
                             louis.translate([self.contractionTable],
                                             line.decode(),
                                             cursorPos=cursorOffset,
                                             mode=louis.MODE.compbrlAtCursor)

        return contracted, inPos, outPos, cursorPos
    
    def displayToBufferOffset(self, display_offset):
        try:
            offset = self.inPos[display_offset]
        except IndexError:
            # Off the chart, we just place the cursor at the end of the line.
            offset = len(self.rawLine)
        except AttributeError:
            # Not in contracted mode.
            offset = display_offset

        return offset

    def setContractedBraille(self, contracted):
        if self.contracted == contracted:
            return
        self.contracted = contracted
        if contracted:
            self.contractionTable = settings.brailleContractionTable or \
                                    _defaultContractionTable
            self.contractRegion()
        else:
            self.expandRegion()

    def contractRegion(self):
        self.string, self.inPos, self.outPos, self.cursorOffset = \
                     self.contractLine(self.rawLine,
                                       self.cursorOffset,
                                       self.expandOnCursor)
        
    def expandRegion(self):
        if not self.contracted:
            return
        self.string = self.rawLine
        try:
            self.cursorOffset = self.inPos[self.cursorOffset]
        except IndexError:
            self.cursorOffset = len(self.string)
        
class Component(Region):
    """A subclass of Region backed by an accessible.  This Region will react
    to any cursor routing key events and perform the default action on the
    accessible, if a default action exists.
    """

    def __init__(self, accessible, string, cursorOffset=0,
                 indicator='', expandOnCursor=False):
        """Creates a new Component.

        Arguments:
        - accessible: the accessible
        - string: the string to use to represent the component
        - cursorOffset: a 0-based index saying where to draw the cursor
                        for this Region if it gets focus.
        """

        Region.__init__(self, string, cursorOffset, expandOnCursor)
        if indicator:
            if self.string:
                self.string = indicator + ' ' + self.string
            else:
                self.string = indicator

        self.accessible = accessible

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""

        try:
            action = self.accessible.queryAction()
        except:
            # Do a mouse button 1 click if we have to.  For example, page tabs
            # don't have any actions but we want to be able to select them with
            # the cursor routing key.
            #
            debug.println(debug.LEVEL_FINEST,
                          "braille.Component.processRoutingKey: no action")
            try:
                eventsynthesizer.clickObject(self.accessible, 1)
            except:
                debug.printException(debug.LEVEL_SEVERE)
        else:
            action.doAction(0)

class Text(Region):
    """A subclass of Region backed by a Text object.  This Region will
    react to any cursor routing key events by positioning the caret in
    the associated text object. The line displayed will be the
    contents of the text object preceded by an optional label.
    [[[TODO: WDW - need to add in text selection capabilities.  Logged
    as bugzilla bug 319754.]]]"""

    def __init__(self, accessible, label="", eol="", 
                 startOffset=None, endOffset=None):
        """Creates a new Text region.

        Arguments:
        - accessible: the accessible that implements AccessibleText
        - label: an optional label to display
        """

        self.accessible = accessible
        if orca_state.activeScript:
            [string, self.caretOffset, self.lineOffset] = \
                 orca_state.activeScript.getTextLineAtCaret(self.accessible)
        else:
            string = ""

        string = string.decode("UTF-8")

        try:
            endOffset = endOffset - self.lineOffset
        except TypeError:
            pass

        try:
            self.startOffset = startOffset - self.lineOffset
        except TypeError:
            self.startOffset = 0

        string = string[self.startOffset:endOffset]

        self.caretOffset -= self.startOffset

        cursorOffset = min(self.caretOffset - self.lineOffset, len(string))

        self._maxCaretOffset = self.lineOffset + len(string.decode("UTF-8"))

        self.eol = eol

        if label:
            self.label = label + ' '
        else:
            self.label = ''

        string = self.label + string

        cursorOffset += len(self.label)

        Region.__init__(self, string, cursorOffset, True)

        if not self.contracted and not settings.disableBrailleEOL:
            self.string += self.eol

    def repositionCursor(self):
        """Attempts to reposition the cursor in response to a new
        caret position.  If it is possible (i.e., the caret is on
        the same line as it was), reposition the cursor and return
        True.  Otherwise, return False.
        """

        [string, caretOffset, lineOffset] = \
                 orca_state.activeScript.getTextLineAtCaret(self.accessible)
        cursorOffset = min(caretOffset - lineOffset, len(string))
        
        if lineOffset != self.lineOffset:
            return False

        self.caretOffset = caretOffset
        self.lineOffset = lineOffset

        cursorOffset += len(self.label)

        if self.contracted:
            self.string, self.inPos, self.outPos, cursorOffset = \
                       self.contractLine(self.rawLine, cursorOffset, True)

        self.cursorOffset = cursorOffset

        return True

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of text
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""
        
        offset = self.displayToBufferOffset(offset)

        if offset < 0:
            return

        newCaretOffset = min(self.lineOffset + offset, self._maxCaretOffset)
        orca_state.activeScript.setCaretOffset(
            self.accessible, newCaretOffset)

    def getAttributeMask(self):
        """Creates a string which can be used as the attrOr field of brltty's
        write structure for the purpose of indicating text attributes and
        selection."""

        try:
            text = self.accessible.queryText()
        except NotImplementedError:
            return ''

        # Start with an empty mask.
        #
        stringLength = len(self.rawLine) - len(self.label)
        lineEndOffset = self.lineOffset + stringLength
        regionMask = [settings.TEXT_ATTR_BRAILLE_NONE]*stringLength

        attrIndicator = settings.textAttributesBrailleIndicator
        selIndicator = settings.brailleSelectorIndicator
        linkIndicator = settings.brailleLinkIndicator
        script = orca_state.activeScript

        if linkIndicator != settings.BRAILLE_LINK_NONE:
            try:
                hyperText = self.accessible.queryHypertext()
                nLinks = hyperText.getNLinks()
            except:
                nLinks = 0

            n = 0
            while n < nLinks:
                link = hyperText.getLink(n)
                if self.lineOffset <= link.startIndex:
                    for i in xrange(link.startIndex, link.endIndex):
                        try:
                            regionMask[i] |= linkIndicator
                        except:
                            pass
                n += 1

        if attrIndicator:
            enabledAttributes = script.attribsToDictionary(
                settings.enabledBrailledTextAttributes)

            offset = self.lineOffset
            while offset < lineEndOffset:
                attributes, startOffset, endOffset = \
                            script.getTextAttributes(self.accessible,
                                                     offset, True)
                if endOffset <= offset:
                    break
                mask = settings.TEXT_ATTR_BRAILLE_NONE
                offset = endOffset
                for attrib in attributes:
                    if enabledAttributes.get(attrib, '') != '':
                        if enabledAttributes[attrib] != attributes[attrib]:
                            mask = attrIndicator
                            break
                if mask != settings.TEXT_ATTR_BRAILLE_NONE:
                    maskStart = max(startOffset - self.lineOffset, 0)
                    maskEnd = min(endOffset - self.lineOffset, stringLength)
                    for i in xrange(maskStart, maskEnd):
                        regionMask[i] |= attrIndicator

        if selIndicator:
            selections = script.getTextSelections(self.accessible)
            for startOffset, endOffset in selections:
                maskStart = max(startOffset - self.lineOffset, 0)
                maskEnd = min(endOffset - self.lineOffset, stringLength)
                for i in xrange(maskStart, maskEnd):
                    regionMask[i] |= selIndicator

        if self.contracted:
            contractedMask = [0] * len(self.rawLine)
            outPos = self.outPos[len(self.label):]
            if self.label:
                # Transform the offsets.
                outPos = \
                       [offset - len(self.label) - 1 for offset in outPos]
            for i, m in enumerate(regionMask):
                try:
                    contractedMask[outPos[i]] |= m
                except IndexError:
                    continue
            regionMask = contractedMask

        # Add empty mask characters for the EOL character as well as for
        # any label that might be present.
        #
        regionMask += [0]*len(self.eol)

        if self.label:
            regionMask = [0]*len(self.label) + regionMask

        return ''.join(map(chr, regionMask))

    def contractLine(self, line, cursorOffset=0, expandOnCursor=True):
        contracted, inPos, outPos, cursorPos = Region.contractLine(
            self, line, cursorOffset, expandOnCursor)
        
        return contracted + self.eol, inPos, outPos, cursorPos

    def displayToBufferOffset(self, display_offset):
        offset = Region.displayToBufferOffset(self, display_offset)
        offset += self.startOffset
        offset -= len(self.label)
        return offset

    def setContractedBraille(self, contracted):
        Region.setContractedBraille(self, contracted)
        if not contracted:
            self.string += self.eol

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
        Component.__init__(self, accessible, string,
                           cursorOffset, expandOnCursor=True)
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
        Region.__init__(self, string, expandOnCursor=True)
        self.accessible = accessible
        self.lineOffset = lineOffset
        self.zone = zone

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of text
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""

        offset = self.displayToBufferOffset(offset)
        newCaretOffset = self.lineOffset + offset
        orca_state.activeScript.setCaretOffset(self.accessible, newCaretOffset)

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

        Returns [string, offsetIndex, attributeMask]
        """

        string = ""
        focusOffset = -1
        attributeMask = ""
        for region in self.regions:
            if region == _regionWithFocus:
                focusOffset = len(string.decode("UTF-8"))
            if region.string:
                # [[[TODO: WDW - HACK: Replace UTF-8 ellipses with "..."
                # The ultimate solution is to get i18n support into
                # BrlTTY.]]]
                #
                string += region.string.replace("\342\200\246", "...")
            mask = region.getAttributeMask()
            attributeMask += mask

        return [string, focusOffset, attributeMask]

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
        foundRegion = None
        string = ""
        pos = 0
        for region in self.regions:
            foundRegion = region
            string = string + region.string
            if len(string.decode("UTF-8")) > offset:
                break
            else:
                pos = len(string.decode("UTF-8"))

        if offset >= len(string.decode("UTF-8")):
            return [None, -1]
        else:
            return [foundRegion, offset - pos]

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of string
        associated with this line.  Note that the zeroeth character may have
        been scrolled off the display."""

        [region, regionOffset] = self.getRegionAtOffset(offset)
        if region:
            region.processRoutingKey(regionOffset)

    def setContractedBraille(self, contracted):
        for region in self.regions:
            region.setContractedBraille(contracted)

def getRegionAtCell(cell):
    """Given a 1-based cell offset, return the braille region
    associated with that cell in the form of [region, offsetinregion]
    where 'region' is the region associated with the cell and
    'offsetinregion' is the 0-based offset of where the cell is
    in the region, where 0 represents the beginning of the region, """

    if len(_lines) > 0:
        offset = (cell - 1) + viewport[0]
        lineNum = viewport[1]
        return _lines[lineNum].getRegionAtOffset(offset)
    else:
        return [None, -1]

def clear():
    """Clears the logical structure, but keeps the Braille display as is
    (until a refresh operation).
    """

    global _lines
    global _regionWithFocus
    global viewport

    _lines = []
    _regionWithFocus = None
    viewport = [0, 0]

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

    _lines.append(line)
    line._index = len(_lines)

def getShowingLine():
    """Returns the Line that is currently being painted on the display.
    """
    return _lines[viewport[1]]

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
                viewport[1] = lineNum
                done = True
                break
        if done:
            break
        else:
            lineNum += 1

    line = _lines[viewport[1]]
    [string, offset, attributeMask] = line.getLineInfo()

    # If the cursor is too far right, we scroll the viewport
    # so the cursor will be on the last cell of the display.
    #
    if _regionWithFocus.cursorOffset >= _displaySize[0]:
        offset += _regionWithFocus.cursorOffset - _displaySize[0] + 1

    viewport[0] = max(0, offset)

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
    global monitor

    if len(_lines) == 0:
        if useBrlAPIBindings:
            if brlAPIRunning:
                brlAPI.writeText("", 0)
        else:
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
    line = _lines[viewport[1]]
    [string, focusOffset, attributeMask] = line.getLineInfo()
    cursorOffset = -1
    if focusOffset >= 0:
        cursorOffset = focusOffset + _regionWithFocus.cursorOffset

    # Now, if desired, we'll automatically pan the viewport to show
    # the cursor.  If there's no targetCursorCell, then we favor the
    # left of the display if we need to pan left, or we favor the
    # right of the display if we need to pan right.
    #
    if panToCursor and (cursorOffset >= 0):
        if len(string.decode("UTF-8")) <= _displaySize[0]:
            viewport[0] = 0
        elif targetCursorCell:
            viewport[0] = max(0, cursorOffset - targetCursorCell + 1)
        elif cursorOffset < viewport[0]:
            viewport[0] = max(0, cursorOffset)
        elif cursorOffset >= (viewport[0] + _displaySize[0]):
            viewport[0] = max(0, cursorOffset - _displaySize[0] + 1)

    startPos = viewport[0]
    endPos = startPos + _displaySize[0]

    # Now normalize the cursor position to BrlTTY, which uses 1 as
    # the first cursor position as opposed to 0.
    #
    cursorCell = cursorOffset - startPos
    if (cursorCell < 0) or (cursorCell >= _displaySize[0]):
        cursorCell = 0
    else:
        cursorCell += 1 # Normalize to 1-based offset

    logLine = "BRAILLE LINE:  '%s'" % string
    debug.println(debug.LEVEL_INFO, logLine)
    log.info(logLine)
    logLine = "     VISIBLE:  '%s', cursor=%d" % \
                    (string[startPos:endPos], cursorCell)
    debug.println(debug.LEVEL_INFO, logLine)
    log.info(logLine)

    string = string.decode("UTF-8")
    substring = string[startPos:endPos].encode("UTF-8")
    if useBrlAPIBindings:
        if brlAPIRunning:
            writeStruct = brlapi.WriteStruct()
            writeStruct.regionBegin = 1
            writeStruct.regionSize = len(substring.decode("UTF-8"))
            while writeStruct.regionSize < _displaySize[0]:
                substring += " "
                if attributeMask:
                    attributeMask += '\x00'
                writeStruct.regionSize += 1
            writeStruct.text = substring
            writeStruct.cursor = cursorCell
            writeStruct.charset = "UTF-8"

            # [[[WDW - if you want to muck around with the dots on the
            # display to do things such as add underlines, you can use
            # the attrOr field of the write structure to do so.  The
            # attrOr field is a string whose length must be the same
            # length as the display and whose dots will end up showing
            # up on the display.  Each character represents a bitfield
            # where each bit corresponds to a dot (i.e., bit 0 = dot 1,
            # bit 1 = dot 2, and so on).  Here's an example that underlines
            # all the text.]]]
            #
            #myUnderline = ""
            #for i in range(0, _displaySize[0]):
            #    myUnderline += '\xc0'
            #writeStruct.attrOr = myUnderline

            if attributeMask:
                writeStruct.attrOr = attributeMask[startPos:endPos]

            brlAPI.write(writeStruct)
    else:
        brl.writeText(cursorCell, substring)

    if settings.enableBrailleMonitor:
        if not monitor:
            monitor = brlmon.BrlMon(_displaySize[0])
            monitor.show_all()
        if attributeMask:
            subMask = attributeMask[startPos:endPos]
        else:
            subMask = None
        monitor.writeText(cursorCell, substring, subMask)
    elif monitor:
        monitor.destroy()
        monitor = None

    beginningIsShowing = startPos == 0
    endIsShowing = endPos >= len(string)

def displayRegions(regionInfo):
    """Displays a list of regions on a single line, setting focus to the
       specified region.  The regionInfo parameter is something that is
       typically returned by a call to braillegenerator.getBrailleRegions.

    Arguments:
    - regionInfo: a list where the first element is a list of regions
                  to display and the second element is the region
                  with focus (must be in the list from element 0)
    """

    regions = regionInfo[0]
    focusedRegion = regionInfo[1]

    clear()
    line = Line()
    for item in regions:
        line.addRegion(item)
    addLine(line)
    setFocus(focusedRegion)
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

    oldX = viewport[0]

    if panAmount == 0:
        panAmount = _displaySize[0]

    if viewport[0] > 0:
        viewport[0] = max(0, viewport[0] - panAmount)

    return oldX != viewport[0]

def panRight(panAmount=0):
    """Pans the display to the right, limiting the pan to the length
    of the line being displayed.

    Arguments:
    - panAmount: the amount to pan.  A value of 0 means the entire
                 width of the physical display.

    Returns True if a pan actually happened.
    """

    oldX = viewport[0]

    if panAmount == 0:
        panAmount = _displaySize[0]

    if len(_lines) > 0:
        lineNum = viewport[1]
        newX = viewport[0] + panAmount
        [string, focusOffset, attributeMask] = _lines[lineNum].getLineInfo()
        if newX < len(string.decode("UTF-8")):
            viewport[0] = newX

    return oldX != viewport[0]

def panToOffset(offset):
    """Automatically pan left or right to make sure the current offset is
    showing."""

    while offset < viewport[0]:
        debug.println(debug.LEVEL_FINEST,
                      "braille.panToOffset (left) %d" % offset)
        if not panLeft():
            break

    while offset >= (viewport[0] + _displaySize[0]):
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

    consumed = False

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    if _callback:
        try:
            # Like key event handlers, a return value of True means
            # the command was consumed.
            #
            consumed = _callback(command)
        except:
            debug.printException(debug.LEVEL_WARNING)
            consumed = False

    if (command >= 0x100) and (command < (0x100 + _displaySize[0])):
        if len(_lines) > 0:
            cursor = (command - 0x100) + viewport[0]
            lineNum = viewport[1]
            _lines[lineNum].processRoutingKey(cursor)
            consumed = True

    if command in (0x2141, 65): # Toggle six dot braille
        settings.enableContractedBraille = not settings.enableContractedBraille
        for line in _lines:
            line.setContractedBraille(settings.enableContractedBraille)
        refresh()

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    return consumed

def _brlAPIKeyReader(source, condition):
    """Method to read a key from the BrlAPI bindings.  This is a
    gobject IO watch handler.
    """
    key = brlAPI.readKey(False)
    if key:
        #flags = key >> 32
        lower = key & 0xFFFFFFFF
        #keyType = lower >> 29
        keyCode = lower & 0x1FFFFFFF
        
        # [[TODO: WDW - HACK If we have a cursor routing key, map
        # it back to the code we used to get with earlier versions
        # of BrlAPI (i.e., bit 0x100 was the indicator of a cursor
        # routing key instead of 0x1000).  This may change before
        # the offical BrlAPI Python bindings are released.]]]
        #
        if keyCode & 0x10000:
            keyCode = 0x100 | (keyCode & 0xFF)
        if keyCode:
            _processBrailleEvent(keyCode)
    return brlAPIRunning

def setupKeyRanges(keys):
    """Hacky method to tell BrlTTY what to send and not send us via
    the readKey method.  This only works with BrlTTY v3.8 and better.

    Arguments:
    -keys: a list of BrlAPI commands.
    """
    if not brlAPIRunning:
        return

    try:
        # First, start by ignoring everything.
        #
        brlAPI.ignoreKeys(brlapi.rangeType_all, [0])

        # Next, enable cursor routing keys.
        #
        keySet = [brlapi.KEY_TYPE_CMD | brlapi.KEY_CMD_ROUTE]

        # Finally, enable the commands we care about.
        #
        for key in keys:
            keySet.append(brlapi.KEY_TYPE_CMD | key)
            
        brlAPI.acceptKeys(brlapi.rangeType_command, keySet)

        brlAPI.acceptKeys(brlapi.rangeType_key, [65])

        debug.println(debug.LEVEL_FINEST, "Using BrlAPI v0.5.0+")
    except:
        debug.printException(debug.LEVEL_FINEST)
        try:
            # Old, incompatible way that was in v3.8 devel, but
            # changed prior to release.  We need this just in case
            # people have not updated yet.

            # First, start by ignoring everything.
            #
            brlAPI.ignoreKeyRange(0,
                                  brlapi.KEY_FLAGS_MASK \
                                  | brlapi.KEY_TYPE_MASK \
                                  | brlapi.KEY_CODE_MASK)

            # Next, enable cursor routing keys.
            #
            brlAPI.acceptKeyRange(brlapi.KEY_TYPE_CMD | brlapi.KEY_CMD_ROUTE,
                                  brlapi.KEY_TYPE_CMD \
                                  | brlapi.KEY_CMD_ROUTE \
                                  | brlapi.KEY_CMD_ARG_MASK)

            # Finally, enable the commands we care about.
            #
            keySet = []
            for key in keys:
                keySet.append(brlapi.KEY_TYPE_CMD | key)
            if len(keySet):
                brlAPI.acceptKeySet(keySet)

            debug.println(debug.LEVEL_FINEST,
                          "Using BrlAPI pre-release v0.5.0")
        except:
            debug.printException(debug.LEVEL_FINEST)
            debug.println(
                debug.LEVEL_WARNING,
                "Braille module cannot listen for braille input events")

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

    if useBrlAPIBindings:
        try:
            global brlAPI
            global brlAPIRunning
            global brlAPISourceId

            gobject.threads_init()
            brlAPI = brlapi.Connection()

            try:
                import os
                windowPath = os.environ["WINDOWPATH"]
                brlAPI.enterTtyModeWithPath()
                brlAPIRunning = True
                debug.println(\
                    debug.LEVEL_CONFIGURATION,
                    "Braille module has been initialized using WINDOWPATH=" \
                    + "%s" % windowPath)
            except:
                brlAPI.enterTtyMode(tty)
                brlAPIRunning = True
                debug.println(\
                    debug.LEVEL_CONFIGURATION,
                    "Braille module has been initialized using tty=%d" % tty)
            brlAPISourceId = gobject.io_add_watch(brlAPI.fileDescriptor,
                                                  gobject.IO_IN,
                                                  _brlAPIKeyReader)
        except:
            debug.printException(debug.LEVEL_FINEST)
            return False
    else:
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
    if useBrlAPIBindings:
        (x, y) = brlAPI.displaySize
        _displaySize = [x, 1]
    else:
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

    global brlAPIRunning
    global brlAPISourceId

    if useBrlAPIBindings:
        if brlAPIRunning:
            brlAPIRunning = False
            gobject.source_remove(brlAPISourceId)
            brlAPISourceId = 0
            brlAPI.leaveTtyMode()
    else:
        brl.shutdown()

    _initialized = False

    return True
