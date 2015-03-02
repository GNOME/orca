# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import signal
import os

from gi.repository import GLib

try:
    import louis
except ImportError:
    louis = None

try:
    import brlapi

    _brlAPI = None
    _brlAPIAvailable = True
    _brlAPIRunning = False
    _brlAPISourceId = 0
except:
    _brlAPIAvailable = False
    _brlAPIRunning = False

from . import settings

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    from . import brlmon
except:
    settings.enableBrailleMonitor = False

from . import brltablenames
from . import cmdnames
from . import debug
from . import eventsynthesizer
from . import logger
from . import orca_state

_logger = logger.getLogger()
log = _logger.newLog("braille")

# Right now, the orca autogen.sh/configure needs a priori knowledge of
# where the liblouis tables are.  When running autogen.sh/configure,
# orca_platform.py:tablesdir will be set to point to the liblouis table
# location.  If not found, it will be the empty string.  We need to
# capture that error condition, otherwise braille contraction will
# just plain fail.  See also bgo#610134.  [[TODO: WDW - see if the
# liblouis bindings can give us the tablesdir information at runtime
# http://code.google.com/p/liblouis/issues/detail?id=9]]
#
from .orca_platform import tablesdir
if louis and not tablesdir:
    debug.println(debug.LEVEL_SEVERE,
                  "Contraction tables for liblouis cannot be found.")
    debug.println(debug.LEVEL_SEVERE,
                  "This usually means orca was built before")
    debug.println(debug.LEVEL_SEVERE,
                  "liblouis was installed. Contracted braille will")
    debug.println(debug.LEVEL_SEVERE,
                  "not be available.")
    louis = None
    
# The braille monitor
#
_monitor = None

# brlapi keys which are not allowed to interupt speech:
#
dontInteruptSpeechKeys = []
if _brlAPIAvailable:
    dontInteruptSpeechKeys = [brlapi.KEY_CMD_FWINLT, brlapi.KEY_CMD_FWINRT, \
        brlapi.KEY_CMD_LNUP, brlapi.KEY_CMD_LNDN]

# Common names for most used BrlTTY commands, to be shown in the GUI:
# ATM, the ones used in default.py are:
#
command_name = {}

if _brlAPIAvailable:
    command_name[brlapi.KEY_CMD_FWINLT]   = cmdnames.BRAILLE_LINE_LEFT
    command_name[brlapi.KEY_CMD_FWINRT]   = cmdnames.BRAILLE_LINE_RIGHT
    command_name[brlapi.KEY_CMD_LNUP]     = cmdnames.BRAILLE_LINE_UP
    command_name[brlapi.KEY_CMD_LNDN]     = cmdnames.BRAILLE_LINE_DOWN
    command_name[brlapi.KEY_CMD_FREEZE]   = cmdnames.BRAILLE_FREEZE
    command_name[brlapi.KEY_CMD_TOP_LEFT] = cmdnames.BRAILLE_TOP_LEFT
    command_name[brlapi.KEY_CMD_BOT_LEFT] = cmdnames.BRAILLE_BOTTOM_LEFT
    command_name[brlapi.KEY_CMD_HOME]     = cmdnames.BRAILLE_HOME
    command_name[brlapi.KEY_CMD_SIXDOTS]  = cmdnames.BRAILLE_SIX_DOTS
    command_name[brlapi.KEY_CMD_ROUTE]    = cmdnames.BRAILLE_ROUTE_CURSOR
    command_name[brlapi.KEY_CMD_CUTBEGIN] = cmdnames.BRAILLE_CUT_BEGIN
    command_name[brlapi.KEY_CMD_CUTLINE]  = cmdnames.BRAILLE_CUT_LINE

# The size of the physical display (width, height).  The coordinate system of
# the display is set such that the upper left is (0,0), x values increase from
# left to right, and y values increase from top to bottom.
#
# For the purposes of testing w/o a braille display, we'll set the display
# size to width=32 and height=1.
#
# [[[TODO: WDW - Only a height of 1 is support at this time.]]]
#
DEFAULT_DISPLAY_SIZE = 32
_displaySize = [DEFAULT_DISPLAY_SIZE, 1]

# The list of lines on the display.  This represents the entire amount of data
# to be drawn on the display.  It will be clipped by the viewport if too large.
#
_lines = []

# The region with focus.  This will be displayed at the home position.
#
_regionWithFocus = None

# The last text information painted.  This has the following fields:
#
# lastTextObj = the last accessible
# lastCaretOffset = the last caret offset of the last text displayed
# lastLineOffset = the last line offset of the last text displayed
# lastCursorCell = the last cell on the braille display for the caret
#
_lastTextInfo = (None, 0, 0, 0)

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

# The event source of a timeout used for flashing a message.
#
_flashEventSourceId = 0

# Line information saved prior to flashing any messages
#
_saved = None

# Translators: These are the braille translation table names for different
# languages. You could read about braille tables at:
# http://en.wikipedia.org/wiki/Braille
#
TABLE_NAMES = {"Cz-Cz-g1": brltablenames.CZ_CZ_G1,
               "Es-Es-g1": brltablenames.ES_ES_G1,
               "Fr-Ca-g2": brltablenames.FR_CA_G2,
               "Fr-Fr-g2": brltablenames.FR_FR_G2,
               "Lv-Lv-g1": brltablenames.LV_LV_G1,
               "Nl-Nl-g1": brltablenames.NL_NL_G1,
               "No-No-g0": brltablenames.NO_NO_G0,
               "No-No-g1": brltablenames.NO_NO_G1,
               "No-No-g2": brltablenames.NO_NO_G2,
               "No-No-g3": brltablenames.NO_NO_G3,
               "Pl-Pl-g1": brltablenames.PL_PL_G1,
               "Pt-Pt-g1": brltablenames.PT_PT_G1,
               "Se-Se-g1": brltablenames.SE_SE_G1,
               "ar-ar-g1": brltablenames.AR_AR_G1,
               "cy-cy-g1": brltablenames.CY_CY_G1,
               "cy-cy-g2": brltablenames.CY_CY_G2,
               "de-de-g0": brltablenames.DE_DE_G0,
               "de-de-g1": brltablenames.DE_DE_G1,
               "de-de-g2": brltablenames.DE_DE_G2,
               "en-GB-g2": brltablenames.EN_GB_G2,
               "en-gb-g1": brltablenames.EN_GB_G1,
               "en-us-g1": brltablenames.EN_US_G1,
               "en-us-g2": brltablenames.EN_US_G2,
               "fr-ca-g1": brltablenames.FR_CA_G1,
               "fr-fr-g1": brltablenames.FR_FR_G1,
               "gr-gr-g1": brltablenames.GR_GR_G1,
               "hi-in-g1": brltablenames.HI_IN_G1,
               "hu-hu-comp8": brltablenames.HU_HU_8DOT,
               "hu-hu-g1": brltablenames.HU_HU_G1,
               "it-it-g1": brltablenames.IT_IT_G1,
               "nl-be-g1": brltablenames.NL_BE_G1}

def listTables():
    tables = {}
    try:
        for fname in os.listdir(tablesdir):
            if fname[-4:] in (".utb", ".ctb"):
                alias = fname[:-4]
                tables[TABLE_NAMES.get(alias, alias)] = \
                    os.path.join(tablesdir, fname)
    except OSError:
        pass

    return tables

def getDefaultTable():
    try:
        for fname in os.listdir(tablesdir):
            if fname[-4:] in (".utb", ".ctb"):
                if fname.startswith("en-us"):
                    return os.path.join(tablesdir, fname)
    except OSError:
        pass

    return ""

if louis:
    _defaultContractionTable = getDefaultTable()

def _printBrailleEvent(level, command):
    """Prints out a Braille event.  The given level may be overridden
    if the eventDebugLevel (see debug.setEventDebugLevel) is greater in
    debug.py.

    Arguments:
    - command: the BrlAPI command for the key that was pressed.
    """

    debug.printInputEvent(
        level,
        "BRAILLE EVENT: %s" % repr(command))

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

        # The uncontracted string for the line.
        #
        self.rawLine = string.strip("\n")

        if self.contracted:
            self.contractionTable = settings.brailleContractionTable or \
                                    _defaultContractionTable

            self.string, self.inPos, self.outPos, self.cursorOffset = \
                         self.contractLine(self.rawLine,
                                           cursorOffset, expandOnCursor)
        else:
            self.string = self.rawLine
            self.cursorOffset = cursorOffset

    def __str__(self):
        return "Region: '%s', %d" % (self.string, self.cursorOffset)

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""
        pass

    def getAttributeMask(self, getLinkMask=True):
        """Creates a string which can be used as the attrOr field of brltty's
        write structure for the purpose of indicating text attributes, links,
        and selection.

        Arguments:
        - getLinkMask: Whether or not we should take the time to get
          the attributeMask for links. Reasons we might not want to
          include knowning that we will fail and/or it taking an
          unreasonable amount of time (AKA Gecko).
        """

        # Double check for ellipses.
        #
        maskSize = len(self.string) + (2 * self.string.count('\u2026'))

        # Create an empty mask.
        #
        mask = ['\x00'] * maskSize
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
            mode = 0
        else:
            mode = louis.compbrlAtCursor

        contracted, inPos, outPos, cursorPos = \
            louis.translate([self.contractionTable],
                            line,
                            cursorPos=cursorOffset,
                            mode=mode)

        # Make sure the cursor is at a realistic spot.
        #
        cursorPos = min(cursorPos, len(contracted))

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
        if contracted:
            self.contractionTable = settings.brailleContractionTable or \
                                    _defaultContractionTable
            self.contractRegion()
        else:
            self.expandRegion()

    def contractRegion(self):
        if self.contracted:
            return
        self.string, self.inPos, self.outPos, self.cursorOffset = \
                     self.contractLine(self.rawLine,
                                       self.cursorOffset,
                                       self.expandOnCursor)
        self.contracted = True

    def expandRegion(self):
        if not self.contracted:
            return
        self.string = self.rawLine
        try:
            self.cursorOffset = self.inPos[self.cursorOffset]
        except IndexError:
            self.cursorOffset = len(self.string)
        self.contracted = False

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

    def __str__(self):
        return "Component: '%s', %d" % (self.string, self.cursorOffset)

    def getCaretOffset(self, offset):
        """Returns the caret position of the given offset if the object
        has text with a caret.  Otherwise, returns -1.

        Arguments:
        - offset: 0-based offset of the cell on the physical display
        """
        return -1

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of string
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""

        if orca_state.activeScript and orca_state.activeScript.utilities.\
           grabFocusBeforeRouting(self.accessible, offset):
            try:
                self.accessible.queryComponent().grabFocus()
            except:
                pass

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
                debug.println(debug.LEVEL_SEVERE,
                              "Could not process routing key:")
                debug.printException(debug.LEVEL_SEVERE)
        else:
            action.doAction(0)

class Link(Component):
    """A subclass of Component backed by an accessible.  This Region will be
    marked as a link by dots 7 or 8, depending on the user's preferences.
    """

    def __init__(self, accessible, string, cursorOffset=0):
        """Initialize a Link region. similar to Component, but here we always
        have the region expand on cursor."""
        Component.__init__(self, accessible, string, cursorOffset, '', True)

    def __str__(self):
        return "Link: '%s', %d" % (self.string, self.cursorOffset)

    def getAttributeMask(self, getLinkMask=True):
        """Creates a string which can be used as the attrOr field of brltty's
        write structure for the purpose of indicating text attributes and
        selection.
        Arguments:

        - getLinkMask: Whether or not we should take the time to get
          the attributeMask for links. Reasons we might not want to
          include knowning that we will fail and/or it taking an
          unreasonable amount of time (AKA Gecko).
        """

        # Create an link indicator mask.
        #
        return chr(settings.brailleLinkIndicator) * len(self.string)

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
        if orca_state.activeScript and self.accessible:
            [string, self.caretOffset, self.lineOffset] = \
                 orca_state.activeScript.getTextLineAtCaret(
                     self.accessible, startOffset=startOffset, endOffset=endOffset)
        else:
            string = ""
            self.caretOffset = 0
            self.lineOffset = 0

        try:
            endOffset = endOffset - self.lineOffset
        except TypeError:
            endOffset = len(string)

        try:
            self.startOffset = startOffset - self.lineOffset
        except TypeError:
            self.startOffset = 0

        string = string[self.startOffset:endOffset]

        self.caretOffset -= self.startOffset

        cursorOffset = min(self.caretOffset - self.lineOffset, len(string))

        self._maxCaretOffset = self.lineOffset + len(string)

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
        elif settings.disableBrailleEOL:
            # Ensure there is a place to click on at the end of a line
            # so the user can route the caret to the end of the line.
            #
            self.string += ' '

    def __str__(self):
        return "Text: '%s', %d" % (self.string, self.cursorOffset)

    def repositionCursor(self):
        """Attempts to reposition the cursor in response to a new
        caret position.  If it is possible (i.e., the caret is on
        the same line as it was), reposition the cursor and return
        True.  Otherwise, return False.
        """

        [string, caretOffset, lineOffset] = \
                 orca_state.activeScript.getTextLineAtCaret(self.accessible,
                                                            self.startOffset)

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

    def getCaretOffset(self, offset):
        """Returns the caret position of the given offset if the object
        has text with a caret.  Otherwise, returns -1.

        Arguments:
        - offset: 0-based offset of the cell on the physical display
        """
        offset = self.displayToBufferOffset(offset)

        if offset < 0:
            return -1

        return min(self.lineOffset + offset, self._maxCaretOffset)

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of text
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display.
        """

        caretOffset = self.getCaretOffset(offset)

        if caretOffset < 0:
            return

        orca_state.activeScript.utilities.setCaretOffset(
            self.accessible, caretOffset)

    def getAttributeMask(self, getLinkMask=True):
        """Creates a string which can be used as the attrOr field of brltty's
        write structure for the purpose of indicating text attributes, links,
        and selection.

        Arguments:
        - getLinkMask: Whether or not we should take the time to get
          the attributeMask for links. Reasons we might not want to
          include knowning that we will fail and/or it taking an
          unreasonable amount of time (AKA Gecko).
        """

        try:
            text = self.accessible.queryText()
        except NotImplementedError:
            return ''

        # Start with an empty mask.
        #
        stringLength = len(self.rawLine) - len(self.label)
        lineEndOffset = self.lineOffset + stringLength
        regionMask = [settings.BRAILLE_UNDERLINE_NONE]*stringLength

        attrIndicator = settings.textAttributesBrailleIndicator
        selIndicator = settings.brailleSelectorIndicator
        linkIndicator = settings.brailleLinkIndicator
        script = orca_state.activeScript

        if getLinkMask and linkIndicator != settings.BRAILLE_UNDERLINE_NONE:
            try:
                hyperText = self.accessible.queryHypertext()
                nLinks = hyperText.getNLinks()
            except:
                nLinks = 0

            n = 0
            while n < nLinks:
                link = hyperText.getLink(n)
                if self.lineOffset <= link.startIndex:
                    for i in range(link.startIndex, link.endIndex):
                        try:
                            regionMask[i] |= linkIndicator
                        except:
                            pass
                n += 1

        if attrIndicator:
            keys, enabledAttributes = script.utilities.stringToKeysAndDict(
                settings.enabledBrailledTextAttributes)

            offset = self.lineOffset
            while offset < lineEndOffset:
                attributes, startOffset, endOffset = \
                    script.utilities.textAttributes(self.accessible,
                                                    offset, True)
                if endOffset <= offset:
                    break
                mask = settings.BRAILLE_UNDERLINE_NONE
                offset = endOffset
                for attrib in attributes:
                    if enabledAttributes.get(attrib, '') != '':
                        if enabledAttributes[attrib] != attributes[attrib]:
                            mask = attrIndicator
                            break
                if mask != settings.BRAILLE_UNDERLINE_NONE:
                    maskStart = max(startOffset - self.lineOffset, 0)
                    maskEnd = min(endOffset - self.lineOffset, stringLength)
                    for i in range(maskStart, maskEnd):
                        regionMask[i] |= attrIndicator

        if selIndicator:
            selections = script.utilities.allTextSelections(self.accessible)
            for startOffset, endOffset in selections:
                maskStart = max(startOffset - self.lineOffset, 0)
                maskEnd = min(endOffset - self.lineOffset, stringLength)
                for i in range(maskStart, maskEnd):
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
            regionMask = contractedMask[:len(self.string)]

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

    def getCaretOffset(self, offset):
        """Returns the caret position of the given offset if the object
        has text with a caret.  Otherwise, returns -1.

        Arguments:
        - offset: 0-based offset of the cell on the physical display
        """
        offset = self.displayToBufferOffset(offset)

        if offset < 0:
            return -1

        return self.lineOffset + offset

    def processRoutingKey(self, offset):
        """Processes a cursor routing key press on this Component.  The offset
        is 0-based, where 0 represents the leftmost character of text
        associated with this region.  Note that the zeroeth character may have
        been scrolled off the display."""

        caretOffset = self.getCaretOffset(offset)
        orca_state.activeScript.utilities.setCaretOffset(
            self.accessible, caretOffset)

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

    def getLineInfo(self, getLinkMask=True):
        """Computes the complete string for this line as well as a
        0-based index where the focused region starts on this line.
        If the region with focus is not on this line, then the index
        will be -1.

        Arguments:
        - getLinkMask: Whether or not we should take the time to get
          the attributeMask for links. Reasons we might not want to
          include knowning that we will fail and/or it taking an
          unreasonable amount of time (AKA Gecko).

        Returns [string, offsetIndex, attributeMask]
        """

        string = ""
        focusOffset = -1
        attributeMask = ""
        for region in self.regions:
            if region == _regionWithFocus:
                focusOffset = len(string)
            if region.string:
                # [[[TODO: WDW - HACK: Replace ellipses with "..."
                # The ultimate solution is to get i18n support into
                # BrlTTY.]]]
                #
                string += region.string.replace('\u2026', "...")
            mask = region.getAttributeMask(getLinkMask)
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
            if len(string) > offset:
                break
            else:
                pos = len(string)

        if offset >= len(string):
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
    in the region, where 0 represents the beginning of the region.
    """

    if len(_lines) > 0:
        offset = (cell - 1) + viewport[0]
        lineNum = viewport[1]
        return _lines[lineNum].getRegionAtOffset(offset)
    else:
        return [None, -1]

def getCaretContext(event):
    """Gets the accesible and caret offset associated with the given
    event.  The event should have a BrlAPI event that contains an
    argument value that corresponds to a cell on the display.

    Arguments:
    - event: an instance of input_event.BrailleEvent.  event.event is
    the dictionary form of the expanded BrlAPI event.
    """

    offset = event.event["argument"]
    [region, regionOffset] = getRegionAtCell(offset + 1)
    if region and (isinstance(region, Text) or isinstance(region, ReviewText)):
        accessible = region.accessible
        caretOffset = region.getCaretOffset(regionOffset)
    else:
        accessible = None
        caretOffset = -1

    return [accessible, caretOffset]

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

def setFocus(region, panToFocus=True, getLinkMask=True):
    """Specififes the region with focus.  This region will be positioned
    at the home position if panToFocus is True.

    Arguments:
    - region: the given region, which much be in a line that has been
      added to the logical display
    - panToFocus: whether or not to position the region at the home
      position
    - getLinkMask: Whether or not we should take the time to get the
      attributeMask for links. Reasons we might not want to include
      knowning that we will fail and/or it taking an unreasonable
      amount of time (AKA Gecko).
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
    [string, offset, attributeMask] = line.getLineInfo(getLinkMask)

    # If the cursor is too far right, we scroll the viewport
    # so the cursor will be on the last cell of the display.
    #
    if _regionWithFocus.cursorOffset >= _displaySize[0]:
        offset += _regionWithFocus.cursorOffset - _displaySize[0] + 1

    viewport[0] = max(0, offset)

def _realignViewport(string, focusOffset, cursorOffset):
    """Realigns the braille display to account for braille alignment
    preferences.  By the time this method is called, if there is a
    cursor cell to be displayed, it should already be somewhere in
    the viewport.  All we're going to do is adjust the viewport a
    little to align the viewport edge according to the
    settings.brailleAlignmentStyle.

    Arguments:
    - string: the entire string to be presented
    - focusOffset: where in string the focused region begins
    - cursorOffset: where in the string the cursor should be

    Returns: the viewport[0] value is potentially modified.
    """

    # pylint complains we don't set viewport, which in fact we do if
    # 'jump' ends up being set.
    #
    # pylint: disable-msg=W0602
    #
    global viewport

    jump = 0

    # If there's no cursor to show or we're doing
    # ALIGN_BRAILLE_BY_EDGE, the viewport should already be where it
    # belongs.  Otherwise, we may need to do some adjusting of the
    # viewport.
    #
    if (cursorOffset < 0) \
       or (settings.brailleAlignmentStyle == settings.BRAILLE_ALIGN_BY_EDGE) \
       or not (cursorOffset >= viewport[0]
               and cursorOffset < (viewport[0] + _displaySize[0])):
        pass
    else:
        # The left and right margin values are absolute values in the
        # string and represent where in the string the margins of the
        # current viewport lie.  Note these are margins and not the
        # actual edges of the viewport.
        #
        leftMargin = viewport[0] + settings.brailleAlignmentMargin - 1
        rightMargin = (viewport[0] + _displaySize[0]) \
                      - settings.brailleAlignmentMargin

        # This represents how far left in the string we want to search
        # and also how far left we'll realign the viewport. Setting it
        # to focusOffset means we won't move the viewport further left
        # than the beginning of the current region with focus.
        #
        leftMostEdge = max(0, focusOffset)

        # If we align by margin, we just want to keep the cursor at or
        # in between the margins.  The only time we go outside the
        # margins are when we are at the ends of the string.
        #
        if settings.brailleAlignmentStyle == settings.BRAILLE_ALIGN_BY_MARGIN:
            if cursorOffset < leftMargin:
                jump = cursorOffset - leftMargin
            elif cursorOffset > rightMargin:
                jump = cursorOffset - rightMargin
        elif settings.brailleAlignmentStyle == settings.BRAILLE_ALIGN_BY_WORD:
            # When we align by word, we want to try to show complete
            # words at the edges of the braille display.  When we're
            # near the left edge, we'll try to start a word at the
            # left edge.  When we're near the right edge, we'll try to
            # end a word at the right edge.
            #
            if cursorOffset < leftMargin:
                # Find the index of the character that is the first
                # letter of the word prior to left edge of the
                # viewport.
                #
                inWord = False
                leftWordEdge = viewport[0] - 1
                while leftWordEdge >= leftMostEdge:
                    if not string[leftWordEdge] in ' \t\n\r\v\f':
                        inWord = True
                    elif inWord:
                        leftWordEdge += 1
                        break
                    leftWordEdge -= 1
                leftWordEdge = max(leftMostEdge, leftWordEdge)
                jump = leftWordEdge - viewport[0]
            elif cursorOffset > rightMargin:
                # Find the index of the character that is the last
                # letter of the word after the right edge of the
                # viewport.
                #
                inWord = False
                rightWordEdge = viewport[0] + _displaySize[0]
                while rightWordEdge < len(string):
                    if not string[rightWordEdge] in ' \t\n\r\v\f':
                        inWord = True
                    elif inWord:
                        break
                    rightWordEdge += 1
                rightWordEdge = min(len(string), rightWordEdge)
                jump = max(0, rightWordEdge - (viewport[0] + _displaySize[0]))

            # We use the brailleMaximumJump to help us handle really
            # long words.  The (jump/abs(jump)) stuff is a quick and
            # dirty way to retain the sign (i.e., +1 or -1).
            #
            if abs(jump) > settings.brailleMaximumJump:
                jump = settings.brailleMaximumJump * (jump/abs(jump))

    if jump:
        # Set the viewport's left edge based upon the jump, making
        # sure we don't go any farther left than the leftMostEdge.
        #
        viewport[0] = max(leftMostEdge, viewport[0] + jump)

        # Now, make sure we don't scroll too far to the right.  That
        # is, avoid showing blank spaces to the right if there is more
        # of the string that can be shown.
        #
        viewport[0] = min(viewport[0],
                          max(leftMostEdge, len(string) - _displaySize[0]))

def refresh(panToCursor=True,
            targetCursorCell=0,
            getLinkMask=True,
            stopFlash=True):
    """Repaints the Braille on the physical display.  This clips the entire
    logical structure by the viewport and also sets the cursor to the
    appropriate location.  [[[TODO: WDW - I'm not sure how BrlTTY handles
    drawing to displays with more than one line, so I'm only going to handle
    drawing one line right now.]]]

    Arguments:

    - panToCursor: if True, will adjust the viewport so the cursor is
      showing.
    - targetCursorCell: Only effective if panToCursor is True.
      0 means automatically place the cursor somewhere on the display so
      as to minimize movement but show as much of the line as possible.
      A positive value is a 1-based target cell from the left side of
      the display and a negative value is a 1-based target cell from the
      right side of the display.
    - getLinkMask: Whether or not we should take the time to get the
      attributeMask for links. Reasons we might not want to include
      knowning that we will fail and/or it taking an unreasonable
      amount of time (AKA Gecko).
    - stopFlash: if True, kill any flashed message that may be showing.
    """

    global endIsShowing
    global beginningIsShowing
    global cursorCell
    global _monitor
    global _lastTextInfo

    # Check out what we were displaying the last time - it might be
    # the same text object we are displaying now.
    #
    (lastTextObj, lastCaretOffset, lastLineOffset, lastCursorCell) = \
        _lastTextInfo
    if _regionWithFocus and isinstance(_regionWithFocus, Text):
        currentTextObj = _regionWithFocus.accessible
        currentCaretOffset = _regionWithFocus.caretOffset
        currentLineOffset = _regionWithFocus.lineOffset
    else:
        currentTextObj = None
        currentCaretOffset = 0
        currentLineOffset = 0

    if stopFlash:
        killFlash(restoreSaved=False)

    if len(_lines) == 0:
        if not _brlAPIRunning:
            init(_callback, settings.tty)
        if _brlAPIRunning:
            try:
                _brlAPI.writeText("", 0)
            except:
                debug.println(debug.LEVEL_WARNING,
                              "BrlTTY seems to have disappeared:")
                debug.printException(debug.LEVEL_WARNING)
                shutdown()
        _lastTextInfo = (None, 0, 0, 0)
        return

    # Now determine the location of the cursor.  First, we'll figure
    # out the 1-based offset for where we want the cursor to be.  If
    # the target cell is less than zero, it means an offset from the
    # right hand side of the display.
    #
    if targetCursorCell < 0:
        targetCursorCell = _displaySize[0] + targetCursorCell + 1

    # If there is no target cursor cell, then try to set one.  We
    # currently only do this for text objects, and we do so by looking
    # at the last position of the caret offset and cursor cell.  The
    # primary goal here is to keep the cursor movement on the display
    # somewhat predictable.
    #
    if (targetCursorCell == 0) \
       and currentTextObj and (currentTextObj == lastTextObj) \
       and (currentLineOffset == lastLineOffset):
        if lastCursorCell == 0:
            # The lastCursorCell will be 0 if the user has panned
            # the display on a long line and the caret of the text
            # object is no longer in view.  We'll pass here and
            # let the panning code figure out what to do.
            #
            pass
        elif lastCaretOffset == currentCaretOffset:
            targetCursorCell = lastCursorCell
        elif lastCaretOffset < currentCaretOffset:
            targetCursorCell = min(_displaySize[0],
                                   lastCursorCell \
                                   + (currentCaretOffset - lastCaretOffset))
        elif lastCaretOffset > currentCaretOffset:
            targetCursorCell = max(1,
                                   lastCursorCell \
                                   - (lastCaretOffset - currentCaretOffset))

    # Now, we figure out the 0-based offset for where the cursor
    # actually is in the string.
    #
    line = _lines[viewport[1]]
    [string, focusOffset, attributeMask] = line.getLineInfo(getLinkMask)
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
            viewport[0] = 0
        elif targetCursorCell:
            viewport[0] = max(0, cursorOffset - targetCursorCell + 1)
        elif cursorOffset < viewport[0]:
            viewport[0] = max(0, cursorOffset)
        elif cursorOffset >= (viewport[0] + _displaySize[0]):
            viewport[0] = max(0, cursorOffset - _displaySize[0] + 1)

    # The cursorOffset should be somewhere in the viewport right now.
    # Let's try to realign the viewport so that the cursor shows up
    # according to the settings.brailleAlignmentStyle setting.
    #
    _realignViewport(string, focusOffset, cursorOffset)

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

    substring = string[startPos:endPos]
    if not _brlAPIRunning:
        init(_callback, settings.tty)
    if _brlAPIRunning:
        writeStruct = brlapi.WriteStruct()
        writeStruct.regionBegin = 1
        writeStruct.regionSize = len(substring)
        while writeStruct.regionSize < _displaySize[0]:
            substring += " "
            if attributeMask:
                attributeMask += '\x00'
            writeStruct.regionSize += 1
        writeStruct.text = substring
        writeStruct.cursor = cursorCell

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

        if not _brlAPIRunning:
            init(_callback, settings.tty)
        if _brlAPIRunning:
            try:
                _brlAPI.write(writeStruct)
            except:
                debug.println(debug.LEVEL_WARNING,
                              "BrlTTY seems to have disappeared:")
                debug.printException(debug.LEVEL_WARNING)
                shutdown()

    if settings.enableBrailleMonitor:
        if not _monitor:
            try:
                _monitor = brlmon.BrlMon(_displaySize[0])
                _monitor.show_all()
            except:
                debug.println(debug.LEVEL_WARNING, "brlmon failed")
                _monitor = None
        if attributeMask:
            subMask = attributeMask[startPos:endPos]
        else:
            subMask = None
        if _monitor:
            _monitor.writeText(cursorCell, substring, subMask)
    elif _monitor:
        _monitor.destroy()
        _monitor = None

    beginningIsShowing = startPos == 0
    endIsShowing = endPos >= len(string)

    # Remember the text information we were presenting (if any)
    #
    if _regionWithFocus and isinstance(_regionWithFocus, Text):
        _lastTextInfo = (_regionWithFocus.accessible,
                         _regionWithFocus.caretOffset,
                         _regionWithFocus.lineOffset,
                         cursorCell)
    else:
        _lastTextInfo = (None, 0, 0, 0)

def _flashCallback():
    global _lines
    global _regionWithFocus
    global viewport
    global _flashEventSourceId

    if _flashEventSourceId:
        (_lines, _regionWithFocus, viewport, flashTime) = _saved
        refresh(panToCursor=False, stopFlash=False)
        _flashEventSourceId = 0

    return False

def killFlash(restoreSaved=True):
    global _flashEventSourceId
    global _lines
    global _regionWithFocus
    global viewport
    if _flashEventSourceId:
        if _flashEventSourceId > 0:
            GLib.source_remove(_flashEventSourceId)
        if restoreSaved:
            (_lines, _regionWithFocus, viewport, flashTime) = _saved
            refresh(panToCursor=False, stopFlash=False)
        _flashEventSourceId = 0

def resetFlashTimer():
    global _flashEventSourceId
    if _flashEventSourceId > 0:
        GLib.source_remove(_flashEventSourceId)
        flashTime = _saved[3]
        _flashEventSourceId = GLib.timeout_add(flashTime, _flashCallback)

def _initFlash(flashTime):
    """Sets up the state needed to flash a message or clears any existing
    flash if nothing is to be flashed.

    Arguments:
    - flashTime:  if non-0, the number of milliseconds to display the
                  regions before reverting back to what was there before.
                  A 0 means to not do any flashing.  A negative number
                  means display the message until some other message
                  comes along or the user presses a cursor routing key.
    """

    global _saved
    global _flashEventSourceId

    if _flashEventSourceId:
        if _flashEventSourceId > 0:
            GLib.source_remove(_flashEventSourceId)
        _flashEventSourceId = 0
    else:
        _saved = (_lines, _regionWithFocus, viewport, flashTime)

    if flashTime > 0:
        _flashEventSourceId = GLib.timeout_add(flashTime, _flashCallback)
    elif flashTime < 0:
        _flashEventSourceId = -666

def displayRegions(regionInfo, flashTime=0):
    """Displays a list of regions on a single line, setting focus to the
       specified region.  The regionInfo parameter is something that is
       typically returned by a call to braille_generator.generateBraille.

    Arguments:
    - regionInfo: a list where the first element is a list of regions
                  to display and the second element is the region
                  with focus (must be in the list from element 0)
    - flashTime:  if non-0, the number of milliseconds to display the
                  regions before reverting back to what was there before.
                  A 0 means to not do any flashing.  A negative number
                  means display the message until some other message
                  comes along or the user presses a cursor routing key.
    """

    _initFlash(flashTime)
    regions = regionInfo[0]
    focusedRegion = regionInfo[1]

    clear()
    line = Line()
    for item in regions:
        line.addRegion(item)
    addLine(line)
    setFocus(focusedRegion)
    refresh(stopFlash=False)

def displayMessage(message, cursor=-1, flashTime=0):
    """Displays a single line, setting the cursor to the given position,
    ensuring that the cursor is in view.

    Arguments:
    - message: the string to display
    - cursor: the 0-based cursor position, where -1 (default) means no cursor
    - flashTime:  if non-0, the number of milliseconds to display the
                  regions before reverting back to what was there before.
                  A 0 means to not do any flashing.  A negative number
                  means display the message until some other message
                  comes along or the user presses a cursor routing key.
    """

    _initFlash(flashTime)
    clear()
    region = Region(message, cursor)
    addLine(Line(region))
    setFocus(region)
    refresh(True, stopFlash=False)

def displayKeyEvent(event):
    """Displays a KeyboardEvent. Typically reserved for locking keys like
    Caps Lock and Num Lock."""

    lockingStateString = event.getLockingStateString()
    if lockingStateString:
        keyname = event.getKeyName()
        msg = "%s %s" % (keyname, lockingStateString)
        displayMessage(msg, flashTime=settings.brailleFlashTime)

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
        if newX < len(string):
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

def setContractedBraille(event):
    """Turns contracted braille on or off based upon the event.

    Arguments:
    - event: an instance of input_event.BrailleEvent.  event.event is
    the dictionary form of the expanded BrlAPI event.
    """

    settings.enableContractedBraille = \
        (event.event["flags"] & brlapi.KEY_FLG_TOGGLE_ON) != 0
    for line in _lines:
        line.setContractedBraille(settings.enableContractedBraille)
    refresh()

def processRoutingKey(event):
    """Processes a cursor routing key event.

    Arguments:
    - event: an instance of input_event.BrailleEvent.  event.event is
    the dictionary form of the expanded BrlAPI event.
    """

    # If a message is being flashed, we'll use a routing key to dismiss it.
    #
    if _flashEventSourceId:
        killFlash()
        return

    cell = event.event["argument"]

    if len(_lines) > 0:
        cursor = cell + viewport[0]
        lineNum = viewport[1]
        _lines[lineNum].processRoutingKey(cursor)

    return True

def _processBrailleEvent(event):
    """Handles BrlTTY command events.  This passes commands on to Orca for
    processing.

    Arguments:
    - event: the BrlAPI input event (expanded)
    """

    _printBrailleEvent(debug.LEVEL_FINE, event)

    consumed = False

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    if _callback:
        try:
            # Like key event handlers, a return value of True means
            # the command was consumed.
            #
            consumed = _callback(event)
        except:
            debug.println(debug.LEVEL_WARNING, "Issue processing event:")
            debug.printException(debug.LEVEL_WARNING)
            consumed = False

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    return consumed

def _brlAPIKeyReader(source, condition):
    """Method to read a key from the BrlAPI bindings.  This is a
    gobject IO watch handler.
    """
    try:
        key = _brlAPI.readKey(False)
    except:
        debug.println(debug.LEVEL_WARNING, "BrlTTY seems to have disappeared:")
        debug.printException(debug.LEVEL_WARNING)
        shutdown()
        return
    if key:
        _processBrailleEvent(_brlAPI.expandKeyCode(key))
    return _brlAPIRunning

def setupKeyRanges(keys):
    """Hacky method to tell BrlTTY what to send and not send us via
    the readKey method.  This only works with BrlTTY v3.8 and better.

    Arguments:
    -keys: a list of BrlAPI commands.
    """
    if not _brlAPIRunning:
        init(_callback, settings.tty)
    if not _brlAPIRunning:
        return

    # First, start by ignoring everything.
    #
    _brlAPI.ignoreKeys(brlapi.rangeType_all, [0])

    # Next, enable cursor routing keys.
    #
    keySet = [brlapi.KEY_TYPE_CMD | brlapi.KEY_CMD_ROUTE]

    # Finally, enable the commands we care about.
    #
    for key in keys:
        keySet.append(brlapi.KEY_TYPE_CMD | key)

    _brlAPI.acceptKeys(brlapi.rangeType_command, keySet)

def init(callback=None, tty=7):
    """Initializes the braille module, connecting to the BrlTTY driver.

    Arguments:
    - callback: the method to call with a BrlTTY input event.
    - tty: the tty port to take ownership of (default = 7)
    Returns False if BrlTTY cannot be accessed or braille has
    not been enabled.
    """

    global _brlAPI
    global _brlAPIRunning
    global _brlAPISourceId
    global _displaySize
    global _callback
    global _monitor

    if _brlAPIRunning:
        return True

    if not settings.enableBraille:
        return False

    _callback = callback

    try:
        _brlAPI = brlapi.Connection()

        try:
            windowPath = os.environ["WINDOWPATH"]
            _brlAPI.enterTtyModeWithPath()
            _brlAPIRunning = True
            debug.println(\
                debug.LEVEL_CONFIGURATION,
                "Braille module has been initialized using WINDOWPATH=" \
                + "%s" % windowPath)
        except:
            try:
                vtnr = os.environ["XDG_VTNR"]
                _brlAPI.enterTtyModeWithPath()
                _brlAPIRunning = True
                debug.println(
                    debug.LEVEL_CONFIGURATION,
                    "Braille module has been initialized using XDG_VTNR=" \
                    + "%s" % vtnr)
            except:
                _brlAPI.enterTtyMode(tty)
                _brlAPIRunning = True
                debug.println(
                    debug.LEVEL_CONFIGURATION,
                    "Braille module has been initialized using tty=%d" % tty)
        _brlAPISourceId = GLib.io_add_watch(_brlAPI.fileDescriptor,
                                            GLib.PRIORITY_DEFAULT,
                                            GLib.IO_IN,
                                            _brlAPIKeyReader)
    except NameError:
        debug.println(debug.LEVEL_CONFIGURATION, "BrlApi is not defined")
        return False
    except:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Could not initialize BrlTTY:")
        debug.printException(debug.LEVEL_CONFIGURATION)
        _brlAPIRunning = False
        return False

    # [[[TODO: WDW - For some reason, BrlTTY wants to say the height of the
    # Vario is 40 so we hardcode it to 1 for now.]]]
    #
    #_displaySize = (brl.getDisplayWidth(), brl.getDisplayHeight())
    (x, y) = _brlAPI.displaySize
    _displaySize = [x, 1]

    # The monitor will be created in refresh if needed.
    #
    if _monitor:
        _monitor.destroy()
        _monitor = None

    debug.println(debug.LEVEL_CONFIGURATION,
                  "braille display size = (%d, %d)" \
                  % (_displaySize[0], _displaySize[1]))

    clear()
    refresh(True)

    return True

def shutdown():
    """Shuts down the braille module.   Returns True if the shutdown procedure
    was run.
    """

    global _brlAPIRunning
    global _brlAPISourceId
    global _monitor
    global _displaySize

    if _brlAPIRunning:
        _brlAPIRunning = False
        GLib.source_remove(_brlAPISourceId)
        _brlAPISourceId = 0
        try:
            _brlAPI.leaveTtyMode()
        except:
            pass
        if _monitor:
            _monitor.destroy()
            _monitor = None
        _displaySize = [DEFAULT_DISPLAY_SIZE, 1]
    else:
        return False

    return True
