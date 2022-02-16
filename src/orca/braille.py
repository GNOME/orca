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

import locale
import signal
import os
import re

from gi.repository import GLib

from . import brltablenames
from . import cmdnames
from . import debug
from . import eventsynthesizer
from . import logger
from . import orca_state
from . import settings
from . import settings_manager

from .orca_platform import tablesdir

_logger = logger.getLogger()
log = _logger.newLog("braille")
_monitor = None
_settingsManager = settings_manager.getManager()

try:
    msg = "BRAILLE: About to import brlapi."
    debug.println(debug.LEVEL_INFO, msg, True)

    import brlapi
    _brlAPI = None
    _brlAPIAvailable = True
    _brlAPIRunning = False
    _brlAPISourceId = 0
except:
    msg = "BRAILLE: Could not import brlapi."
    debug.println(debug.LEVEL_INFO, msg, True)
    _brlAPIAvailable = False
    _brlAPIRunning = False
else:
    msg = "BRAILLE: brlapi imported %s" % brlapi
    debug.println(debug.LEVEL_INFO, msg, True)

try:
    msg = "BRAILLE: About to import louis."
    debug.println(debug.LEVEL_INFO, msg, True)
    import louis
except:
    msg = "BRAILLE: Could not import liblouis"
    debug.println(debug.LEVEL_INFO, msg, True)
    louis = None
else:
    msg = "BRAILLE: liblouis imported %s" % louis
    debug.println(debug.LEVEL_INFO, msg, True)

    msg = "BRAILLE: tables location: %s" % tablesdir
    debug.println(debug.LEVEL_INFO, msg, True)

    # TODO: Can we get the tablesdir info at runtime?
    if not tablesdir:
        msg = "BRAILLE: Disabling liblouis due to unknown table location." \
              "This usually means orca was built before liblouis was installed."
        debug.println(debug.LEVEL_INFO, msg, True)
        louis = None

try:
    from . import brlmon
except:
    settings.enableBrailleMonitor = False


# brlapi keys which are not allowed to interrupt speech:
#
dontInteruptSpeechKeys = []
if _brlAPIAvailable:
    dontInteruptSpeechKeys = [ \
        brlapi.KEY_CMD_HWINLT, brlapi.KEY_CMD_HWINRT, \
        brlapi.KEY_CMD_FWINLT, brlapi.KEY_CMD_FWINRT, \
        brlapi.KEY_CMD_FWINLTSKIP, brlapi.KEY_CMD_FWINRTSKIP, \
        brlapi.KEY_CMD_LNUP, brlapi.KEY_CMD_LNDN]

# Common names for most used BrlTTY commands, to be shown in the GUI:
# ATM, the ones used in default.py are:
#
command_name = {}

if _brlAPIAvailable:
    command_name[brlapi.KEY_CMD_HWINLT]     = cmdnames.BRAILLE_LINE_LEFT
    command_name[brlapi.KEY_CMD_FWINLT]     = cmdnames.BRAILLE_LINE_LEFT
    command_name[brlapi.KEY_CMD_FWINLTSKIP] = cmdnames.BRAILLE_LINE_LEFT
    command_name[brlapi.KEY_CMD_HWINRT]     = cmdnames.BRAILLE_LINE_RIGHT
    command_name[brlapi.KEY_CMD_FWINRT]     = cmdnames.BRAILLE_LINE_RIGHT
    command_name[brlapi.KEY_CMD_FWINRTSKIP] = cmdnames.BRAILLE_LINE_RIGHT
    command_name[brlapi.KEY_CMD_LNUP]       = cmdnames.BRAILLE_LINE_UP
    command_name[brlapi.KEY_CMD_LNDN]       = cmdnames.BRAILLE_LINE_DOWN
    command_name[brlapi.KEY_CMD_FREEZE]     = cmdnames.BRAILLE_FREEZE
    command_name[brlapi.KEY_CMD_TOP_LEFT]   = cmdnames.BRAILLE_TOP_LEFT
    command_name[brlapi.KEY_CMD_BOT_LEFT]   = cmdnames.BRAILLE_BOTTOM_LEFT
    command_name[brlapi.KEY_CMD_HOME]       = cmdnames.BRAILLE_HOME
    command_name[brlapi.KEY_CMD_SIXDOTS]    = cmdnames.BRAILLE_SIX_DOTS
    command_name[brlapi.KEY_CMD_ROUTE]      = cmdnames.BRAILLE_ROUTE_CURSOR
    command_name[brlapi.KEY_CMD_CUTBEGIN]   = cmdnames.BRAILLE_CUT_BEGIN
    command_name[brlapi.KEY_CMD_CUTLINE]    = cmdnames.BRAILLE_CUT_LINE

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

# Set to True when we lower our output priority
#
idle = False

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
               "hu-hu-g2": brltablenames.HU_HU_G2,
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
    userLocale = locale.getlocale(locale.LC_MESSAGES)[0]
    msg = "BRAILLE: User locale is %s" % userLocale
    debug.println(debug.LEVEL_INFO, msg, True)

    if userLocale in (None, "C"):
        userLocale = locale.getdefaultlocale()[0]
        msg = "BRAILLE: Default locale is %s" % userLocale
        debug.println(debug.LEVEL_INFO, msg, True)

    if userLocale in (None, "C"):
        msg = "BRAILLE: Locale cannot be determined. Falling back on 'en-us'"
        debug.println(debug.LEVEL_INFO, msg, True)
        language = "en-us"
    else:
        language = "-".join(userLocale.split("_")).lower()

    try:
        tables = [x for x in os.listdir(tablesdir) if x[-4:] in (".utb", ".ctb")]
    except OSError:
        msg = "BRAILLE: Exception calling os.listdir for %s" % tablesdir
        debug.println(debug.LEVEL_INFO, msg, True)
        return ""

    # Some of the tables are probably not a good choice for default table....
    exclude = ["interline", "mathtext"]

    # Some of the tables might be a better default than others. For instance, someone who
    # can read grade 2 braille presumably can read grade 1; the reverse is not necessarily
    # true. Literary braille might be easier for some users to read than computer braille.
    # We can adjust this based on user feedback, but in general the goal is a sane default
    # for the largest group of users; not the perfect default for all users.
    prefer = ["g1", "g2", "comp6", "comp8"]

    isCandidate = lambda t: t.startswith(language) and not any(e in t for e in exclude)
    tables = list(filter(isCandidate, tables))
    msg = "BRAILLE: %i candidate tables for locale found: %s" % (len(tables), ", ".join(tables))
    debug.println(debug.LEVEL_INFO, msg, True)

    if not tables:
        return ""

    for p in prefer:
        for table in tables:
            if p in table:
                return os.path.join(tablesdir, table)

    # If we couldn't find a preferred match, just go with the first match for the locale.
    return os.path.join(tablesdir, tables[0])

if louis:
    _defaultContractionTable = getDefaultTable()
    msg = "BRAILLE: Default contraction table is: %s" % _defaultContractionTable
    debug.println(debug.LEVEL_INFO, msg, True)

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
        self.contracted = settings.enableContractedBraille and louis is not None

        self.expandOnCursor = expandOnCursor

        # The uncontracted string for the line.
        #
        self.rawLine = string.strip("\n")

        if self.contracted:
            self.contractionTable = settings.brailleContractionTable or _defaultContractionTable
            if string.strip():
                msg = "BRAILLE: Contracting '%s' with table %s" % (string, self.contractionTable)
                debug.println(debug.LEVEL_INFO, msg, True)

            self.string, self.inPos, self.outPos, self.cursorOffset = \
                         self.contractLine(self.rawLine,
                                           cursorOffset, expandOnCursor)
        else:
            if string.strip():
                if not settings.enableContractedBraille:
                    msg = "BRAILLE: Not contracting '%s' because contracted braille is not enabled." % string
                    debug.println(debug.LEVEL_INFO, msg, True)
                else:
                    msg = "BRAILLE: Not contracting '%s' due to problem with liblouis." % string
                    debug.println(debug.LEVEL_INFO, msg, True)

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
          include knowing that we will fail and/or it taking an
          unreasonable amount of time (AKA Gecko).
        """

        # Create an empty mask.
        #
        return '\x00' * len(self.string)

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
        # Note that if cursorOffset is beyond the end of the buffer,
        # a spurious value is returned by liblouis in cursorPos.
        #
        if cursorOffset >= len(line):
            cursorPos = len(contracted)
        else:
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
            self.contractionTable = settings.brailleContractionTable or _defaultContractionTable
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
          include knowing that we will fail and/or it taking an
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

        if not _regionWithFocus:
            return False

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
          include knowing that we will fail and/or it taking an
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

    def __str__(self):
        return "ReviewComponent: %s, %d" % (self.zone, self.cursorOffset)

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

    def __str__(self):
        return "ReviewText: %s, %d" % (self.zone, self.cursorOffset)

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
          include knowing that we will fail and/or it taking an
          unreasonable amount of time (AKA Gecko).

        Returns [string, offsetIndex, attributeMask, ranges]
        """

        string = ""
        focusOffset = -1
        attributeMask = ""
        ranges = []
        for region in self.regions:
            if region == _regionWithFocus:
                focusOffset = len(string)
            if region.string:
                string += region.string
            mask = region.getAttributeMask(getLinkMask)
            attributeMask += mask

        words = [word.span() for word in re.finditer(r"(^\s+|\S+\s*)", string)]
        span = []
        for start, end in words:
            if span and end - span[0] > _displaySize[0]:
                ranges.append(span)
                span = []
            if not span:
                # Subdivide long words that exceed the display width.
                wordLength = end - start
                if wordLength > _displaySize[0]:
                    displayWidths = wordLength // _displaySize[0]
                    if displayWidths:
                        for i in range(displayWidths):
                            ranges.append([start + i * _displaySize[0], start + (i+1) * _displaySize[0]])
                        if wordLength % _displaySize[0]:
                            span = [start + displayWidths * _displaySize[0], end]
                        else:
                            continue
                else:
                    span = [start, end]
            else:
                span[1] = end
            if end == focusOffset:
                ranges.append(span)
                span = []
        else:
            if span:
                ranges.append(span)

        return [string, focusOffset, attributeMask, ranges]

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
    if len(_lines) > 0:
        return _lines[viewport[1]]
    else:
        return Line()

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
      knowing that we will fail and/or it taking an unreasonable
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
    [string, offset, attributeMask, ranges] = line.getLineInfo(getLinkMask)

    # If the cursor is too far right, we scroll the viewport
    # so the cursor will be on the last cell of the display.
    #
    if _regionWithFocus.cursorOffset >= _displaySize[0]:
        offset += _regionWithFocus.cursorOffset - _displaySize[0] + 1

    viewport[0] = max(0, offset)

def _idleBraille():
    """Try to hand off control to other screen readers without completely
    shutting down the BrlAPI connection"""

    global idle

    if not idle:
        try:
            msg = "BRAILLE: Attempting to idle braille."
            debug.println(debug.LEVEL_INFO, msg, True)
            _brlAPI.setParameter(brlapi.PARAM_CLIENT_PRIORITY, 0, False, 0)
            idle = True
        except:
            msg = "BRAILLE: Idling braille failled. This requires BrlAPI >= 0.8."
            debug.println(debug.LEVEL_INFO, msg, True)
            pass
        else:
            msg = "BRAILLE: Idling braille succeeded."
            debug.println(debug.LEVEL_INFO, msg, True)

    return idle

def _clearBraille():
    """Clear Braille output, hand off control to other screen readers, without
    completely shutting down the BrlAPI connection"""

    if not _brlAPIRunning:
        # We do want to try to clear the output we left on the device
        init(_callback)

    if _brlAPIRunning:
        try:
            _brlAPI.writeText("", 0)
            _idleBraille()
        except:
            msg = "BRAILLE: BrlTTY seems to have disappeared."
            debug.println(debug.LEVEL_WARNING, msg, True)
            shutdown()

def _enableBraille():
    """Re-enable Braille output after making it idle or clearing it"""
    global idle

    msg = "BRAILLE: Enabling braille. BrlAPI running: %s" % _brlAPIRunning
    debug.println(debug.LEVEL_INFO, msg, True)

    if not _brlAPIRunning:
        msg = "BRAILLE: Need to initialize first."
        debug.println(debug.LEVEL_INFO, msg, True)
        init(_callback)

    if _brlAPIRunning:
        if idle:
            msg = "BRAILLE: Is running, but idling."
            debug.println(debug.LEVEL_INFO, msg, True)
            try:
                # Restore default priority
                msg = "BRAILLE: Attempting to de-idle braille."
                debug.println(debug.LEVEL_INFO, msg, True)
                _brlAPI.setParameter(brlapi.PARAM_CLIENT_PRIORITY, 0, False, 50)
                idle = False
            except:
                msg = "BRAILLE: could not restore priority"
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                msg = "BRAILLE: De-idle succeeded."
                debug.println(debug.LEVEL_INFO, msg, True)

def disableBraille():
    """Hand off control to other screen readers, shutting down the BrlAPI
    connection if needed"""

    global idle

    msg = "BRAILLE: Disabling braille. BrlAPI running: %s" % _brlAPIRunning
    debug.println(debug.LEVEL_INFO, msg, True)

    if _brlAPIRunning and not idle:
        msg = "BRAILLE: BrlApi running and not idle."
        debug.println(debug.LEVEL_INFO, msg, True)

        if not _idleBraille() and not _settingsManager.getSetting('enableBraille'):
            # BrlAPI before 0.8 and we really want to shut down
            msg = "BRAILLE: could not go idle, completely shut down"
            debug.println(debug.LEVEL_INFO, msg, True)
            shutdown()

def checkBrailleSetting():
    """Disable Braille if it got disabled in the preferences"""

    msg = "BRAILLE: Checking braille setting."
    debug.println(debug.LEVEL_INFO, msg, True)

    if not _settingsManager.getSetting('enableBraille'):
        disableBraille()

def refresh(panToCursor=True, targetCursorCell=0, getLinkMask=True, stopFlash=True):
    """Repaints the Braille on the physical display.  This clips the entire
    logical structure by the viewport and also sets the cursor to the
    appropriate location.  [[[TODO: WDW - I'm not sure how BrlTTY handles
    drawing to displays with more than one line, so I'm only going to handle
    drawing one line right now.]]]

    Arguments:
    - panToCursor: if True, will adjust the viewport so the cursor is showing.
    - targetCursorCell: Only effective if panToCursor is True.
      0 means automatically place the cursor somewhere on the display so
      as to minimize movement but show as much of the line as possible.
      A positive value is a 1-based target cell from the left side of
      the display and a negative value is a 1-based target cell from the
      right side of the display.
    - getLinkMask: Whether or not we should take the time to get the
      attributeMask for links. Reasons we might not want to include
      knowing that we will fail and/or it taking an unreasonable
      amount of time (AKA Gecko).
    - stopFlash: if True, kill any flashed message that may be showing.
    """

    # TODO - JD: Split this work out into smaller methods.

    global endIsShowing
    global beginningIsShowing
    global cursorCell
    global _monitor
    global _lastTextInfo

    msg = "BRAILLE: Refresh. Pan: %s target: %i" % (panToCursor, targetCursorCell)
    debug.println(debug.LEVEL_INFO, msg, True)

    if stopFlash:
        killFlash(restoreSaved=False)

    # TODO - JD: This should be taken care of in orca.py.
    if not _settingsManager.getSetting('enableBraille') \
       and not _settingsManager.getSetting('enableBrailleMonitor'):
        if _brlAPIRunning:
            msg = "BRAILLE: FIXME - Braille disabled, but not properly shut down."
            debug.println(debug.LEVEL_INFO, msg, True)
            shutdown()
        _lastTextInfo = (None, 0, 0, 0)
        return

    if len(_lines) == 0:
        _clearBraille()
        _lastTextInfo = (None, 0, 0, 0)
        return


    lastTextObj, lastCaretOffset, lastLineOffset, lastCursorCell = _lastTextInfo
    msg = "BRAILLE: Last text obj: %s (Caret: %i, Line: %i, Cell: %i)" % _lastTextInfo
    debug.println(debug.LEVEL_INFO, msg, True)

    if _regionWithFocus and isinstance(_regionWithFocus, Text):
        currentTextObj = _regionWithFocus.accessible
        currentCaretOffset = _regionWithFocus.caretOffset
        currentLineOffset = _regionWithFocus.lineOffset
    else:
        currentTextObj = None
        currentCaretOffset = 0
        currentLineOffset = 0

    onSameLine = currentTextObj and currentTextObj == lastTextObj \
        and currentLineOffset == lastLineOffset

    msg = "BRAILLE: Current text obj: %s (Caret: %i, Line: %i). On same line: %s" % \
        (currentTextObj, currentCaretOffset, currentLineOffset, bool(onSameLine))
    debug.println(debug.LEVEL_INFO, msg, True)

    if targetCursorCell < 0:
        targetCursorCell = _displaySize[0] + targetCursorCell + 1
        msg = "BRAILLE: Adjusted targetCursorCell to: %i" % targetCursorCell
        debug.println(debug.LEVEL_INFO, msg, True)

    # If there is no target cursor cell and panning to cursor was
    # requested, then try to set one.  We
    # currently only do this for text objects, and we do so by looking
    # at the last position of the caret offset and cursor cell.  The
    # primary goal here is to keep the cursor movement on the display
    # somewhat predictable.

    if panToCursor and targetCursorCell == 0 and onSameLine:
        if lastCursorCell == 0:
            msg = "BRAILLE: Not adjusting targetCursorCell. User panned caret out of view."
            debug.println(debug.LEVEL_INFO, msg, True)
        elif lastCaretOffset == currentCaretOffset:
            targetCursorCell = lastCursorCell
            msg = "BRAILLE: Setting targetCursorCell to previous value. Caret hasn't moved."
            debug.println(debug.LEVEL_INFO, msg, True)
        elif lastCaretOffset < currentCaretOffset:
            newLocation = lastCursorCell + (currentCaretOffset - lastCaretOffset)
            if newLocation <= _displaySize[0]:
                msg = "BRAILLE: Setting targetCursorCell based on offset: %i" % newLocation
                debug.println(debug.LEVEL_INFO, msg, True)
                targetCursorCell = newLocation
            else:
                msg = "BRAILLE: Setting targetCursorCell to end of display."
                debug.println(debug.LEVEL_INFO, msg, True)
                targetCursorCell = _displaySize[0]
        elif lastCaretOffset > currentCaretOffset:
            newLocation = lastCursorCell - (lastCaretOffset - currentCaretOffset)
            if newLocation >= 1:
                msg = "BRAILLE: Setting targetCursorCell based on offset: %i" % newLocation
                debug.println(debug.LEVEL_INFO, msg, True)
                targetCursorCell = newLocation
            else:
                msg = "BRAILLE: Setting targetCursorCell to start of display."
                debug.println(debug.LEVEL_INFO, msg, True)
                targetCursorCell = 1

    # Now, we figure out the 0-based offset for where the cursor actually is in the string.

    line = _lines[viewport[1]]
    [string, focusOffset, attributeMask, ranges] = line.getLineInfo(getLinkMask)
    msg = "BRAILLE: Line %i: '%s' focusOffset: %i %s" % (viewport[1], string, focusOffset, ranges)
    debug.println(debug.LEVEL_INFO, msg, True)

    cursorOffset = -1
    if focusOffset >= 0:
        cursorOffset = focusOffset + _regionWithFocus.cursorOffset
        msg = "BRAILLE: Cursor offset in line string is: %i" % cursorOffset
        debug.println(debug.LEVEL_INFO, msg, True)

    # Now, if desired, we'll automatically pan the viewport to show
    # the cursor.  If there's no targetCursorCell, then we favor the
    # left of the display if we need to pan left, or we favor the
    # right of the display if we need to pan right.
    #
    if panToCursor and (cursorOffset >= 0):
        if len(string) <= _displaySize[0] and cursorOffset < _displaySize[0]:
            msg = "BRAILLE: Not adjusting offset %i. Cursor offset fits on display." % viewport[0]
            debug.println(debug.LEVEL_INFO, msg, True)
        elif targetCursorCell:
            viewport[0] = max(0, cursorOffset - targetCursorCell + 1)
            msg = "BRAILLE: Adjusting offset to %i based on targetCursorCell" % viewport[0]
            debug.println(debug.LEVEL_INFO, msg, True)
        elif cursorOffset < viewport[0]:
            viewport[0] = max(0, cursorOffset)
            msg = "BRAILLE: Adjusting offset to %i (cursor on left)" % viewport[0]
            debug.println(debug.LEVEL_INFO, msg, True)
        elif cursorOffset >= (viewport[0] + _displaySize[0]):
            viewport[0] = max(0, cursorOffset - _displaySize[0] + 1)
            msg = "BRAILLE: Adjusting offset to %i (cursor beyond display end)" % viewport[0]
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            rangeForOffset = _getRangeForOffset(cursorOffset)
            viewport[0] = max(0, rangeForOffset[0])
            msg = "BRAILLE: Adjusting offset to %i (unhandled condition)" % viewport[0]
            debug.println(debug.LEVEL_INFO, msg, True)
            if cursorOffset >= (viewport[0] + _displaySize[0]):
                viewport[0] = max(0, cursorOffset - _displaySize[0] + 1)
                msg = "BRAILLE: Readjusting offset to %i (cursor beyond display end)" % viewport[0]
                debug.println(debug.LEVEL_INFO, msg, True)

    startPos, endPos = _adjustForWordWrap(targetCursorCell)
    viewport[0] = startPos

    # Now normalize the cursor position to BrlTTY, which uses 1 as
    # the first cursor position as opposed to 0.
    #
    cursorCell = cursorOffset - startPos
    if (cursorCell < 0) or (cursorCell >= _displaySize[0]):
        cursorCell = 0
    else:
        cursorCell += 1 # Normalize to 1-based offset

    logLine = "BRAILLE LINE:  '%s'" % string
    debug.println(debug.LEVEL_INFO, logLine, True)
    log.info(logLine)

    logLine = "     VISIBLE:  '%s', cursor=%d" % \
                    (string[startPos:endPos], cursorCell)
    debug.println(debug.LEVEL_INFO, logLine, True)
    log.info(logLine)

    substring = string[startPos:endPos]
    if attributeMask:
        submask = attributeMask[startPos:endPos]
    else:
        submask = ""

    submask += '\x00' * (len(substring) - len(submask))

    if _settingsManager.getSetting('enableBraille'):
        _enableBraille()

    if _settingsManager.getSetting('enableBraille') and _brlAPIRunning:
        writeStruct = brlapi.WriteStruct()
        writeStruct.regionBegin = 1
        writeStruct.regionSize = len(substring)
        while writeStruct.regionSize < _displaySize[0]:
            substring += " "
            if attributeMask:
                submask += '\x00'
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
            writeStruct.attrOr = submask

        try:
            _brlAPI.write(writeStruct)
        except:
            msg = "BRAILLE: BrlTTY seems to have disappeared."
            debug.println(debug.LEVEL_WARNING, msg, True)
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

def _adjustForWordWrap(targetCursorCell):
    startPos = viewport[0]
    endPos = startPos + _displaySize[0]
    msg = "BRAILLE: Current range: (%i, %i). Target cell: %i." % (startPos, endPos, targetCursorCell)
    debug.println(debug.LEVEL_INFO, msg, True)

    if not _lines or not settings.enableBrailleWordWrap:
        return startPos, endPos

    line = _lines[viewport[1]]
    lineString, focusOffset, attributeMask, ranges = line.getLineInfo()
    ranges = list(filter(lambda x: x[0] <= startPos + targetCursorCell < x[1], ranges))
    if ranges:
        msg = "BRAILLE: Adjusted range: (%i, %i)" % (ranges[0][0], ranges[-1][1])
        debug.println(debug.LEVEL_INFO, msg, True)
        if ranges[-1][1] - ranges[0][0] > _displaySize[0]:
            msg = "BRAILLE: Not adjusting range which is greater than display size"
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            startPos, endPos = ranges[0][0], ranges[-1][1]

    return startPos, endPos

def _getRangeForOffset(offset):
    string, focusOffset, attributeMask, ranges = _lines[viewport[1]].getLineInfo()
    for r in ranges:
        if r[0] <= offset < r[1]:
            return r
    for r in ranges:
        if offset == r[1]:
            return r

    return [0, 0]

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
        oldStart, oldEnd = _getRangeForOffset(oldX)
        newStart, newEnd = _getRangeForOffset(oldStart - _displaySize[0])
        panAmount = max(0, min(oldStart - newStart, _displaySize[0]))

    viewport[0] = max(0, viewport[0] - panAmount)
    msg = "BRAILLE: Panning left. Amount: %i (from %i to %i)" % (panAmount, oldX, viewport[0])
    debug.println(debug.LEVEL_INFO, msg, True)
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
        oldStart, oldEnd = _getRangeForOffset(oldX)
        newStart, newEnd = _getRangeForOffset(oldEnd)
        panAmount = max(0, min(newStart - oldStart, _displaySize[0]))

    if len(_lines) > 0:
        lineNum = viewport[1]
        newX = viewport[0] + panAmount
        string, focusOffset, attributeMask, ranges = _lines[lineNum].getLineInfo()
        if newX < len(string):
            viewport[0] = newX

    msg = "BRAILLE: Panning right. Amount: %i (from %i to %i)" % (panAmount, oldX, viewport[0])
    debug.println(debug.LEVEL_INFO, msg, True)
    return oldX != viewport[0]

def panToOffset(offset):
    """Automatically pan left or right to make sure the current offset is
    showing."""

    msg = "BRAILLE: Panning to offset %i. Current offset: %i." % (offset, viewport[0])
    debug.println(debug.LEVEL_INFO, msg, True)

    while offset < viewport[0]:
        if not panLeft():
            break

    while offset >= (viewport[0] + _displaySize[0]):
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

    msg = "BRAILLE: Setting up key ranges."
    debug.println(debug.LEVEL_INFO, msg, True)

    if not _brlAPIRunning:
        init(_callback)

    if not _brlAPIRunning:
        msg = "BRAILLE: Not setting up key ranges: BrlAPI not running."
        debug.println(debug.LEVEL_INFO, msg, True)
        return

    msg = "BRAILLE: Ignoring all key ranges."
    debug.println(debug.LEVEL_INFO, msg, True)
    _brlAPI.ignoreKeys(brlapi.rangeType_all, [0])

    keySet = [brlapi.KEY_TYPE_CMD | brlapi.KEY_CMD_ROUTE]

    msg = "BRAILLE: Enabling commands:"
    debug.println(debug.LEVEL_INFO, msg, True)

    for key in keys:
        keySet.append(brlapi.KEY_TYPE_CMD | key)

    msg = "BRAILLE: Sending keys to BrlAPI."
    debug.println(debug.LEVEL_INFO, msg, True)
    _brlAPI.acceptKeys(brlapi.rangeType_command, keySet)

    msg = "BRAILLE: Key ranges set up."
    debug.println(debug.LEVEL_INFO, msg, True)

def init(callback=None):
    """Initializes the braille module, connecting to the BrlTTY driver.

    Arguments:
    - callback: the method to call with a BrlTTY input event.
    Returns False if BrlTTY cannot be accessed or braille has
    not been enabled.
    """

    if not settings.enableBraille:
        return False

    global _brlAPI
    global _brlAPIRunning
    global _brlAPISourceId
    global _displaySize
    global _callback
    global _monitor

    msg = "BRAILLE: Initializing. Callback: %s" % callback
    debug.println(debug.LEVEL_INFO, msg, True)

    if _brlAPIRunning:
        msg = "BRAILLE: BrlAPI is already running."
        debug.println(debug.LEVEL_INFO, msg, True)
        return True

    _callback = callback

    msg = "BRAILLE: WINDOWPATH=%s" % os.environ.get("WINDOWPATH")
    debug.println(debug.LEVEL_INFO, msg, True)

    msg = "BRAILLE: XDG_VTNR=%s" % os.environ.get("XDG_VTNR")
    debug.println(debug.LEVEL_INFO, msg, True)

    try:
        msg = "BRAILLE: Attempting connection with BrlAPI."
        debug.println(debug.LEVEL_INFO, msg, True)

        _brlAPI = brlapi.Connection()
        msg = "BRAILLE: Connection established with BrlAPI: %s" % _brlAPI
        debug.println(debug.LEVEL_INFO, msg, True)

        msg = "BRAILLE: Attempting to enter TTY mode."
        debug.println(debug.LEVEL_INFO, msg, True)

        _brlAPI.enterTtyModeWithPath()
        msg = "BRAILLE: TTY mode entered."
        debug.println(debug.LEVEL_INFO, msg, True)

        _brlAPIRunning = True

        (x, y) = _brlAPI.displaySize
        msg = "BRAILLE: Display size: (%i,%i)" % (x, y)
        debug.println(debug.LEVEL_INFO, msg, True)

        if x == 0:
            msg = "BRAILLE: Error - 0 cells suggests display is not yet plugged in."
            debug.println(debug.LEVEL_INFO, msg, True)
            raise Exception

        _brlAPISourceId = GLib.io_add_watch(_brlAPI.fileDescriptor,
                                            GLib.PRIORITY_DEFAULT,
                                            GLib.IO_IN,
                                            _brlAPIKeyReader)

    except NameError:
        msg = "BRAILLE: Initialization failed: BrlApi is not defined."
        debug.println(debug.LEVEL_INFO, msg, True)
        return False
    except:
        msg = "BRAILLE: Initialization failed."
        debug.println(debug.LEVEL_INFO, msg, True)
        debug.printException(debug.LEVEL_INFO)

        _brlAPIRunning = False

        if not _brlAPI:
            return False

        try:
            msg = "BRAILLE: Attempting to leave TTY mode."
            debug.println(debug.LEVEL_INFO, msg, True)
            _brlAPI.leaveTtyMode()
            msg = "BRAILLE: TTY mode exited."
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = "BRAILLE: Exception leaving TTY mode."
            debug.println(debug.LEVEL_INFO, msg, True)

        try:
            msg = "BRAILLE: Attempting to close connection."
            debug.println(debug.LEVEL_INFO, msg, True)
            _brlAPI.closeConnection()
            msg = "BRAILLE: Connection closed."
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = "BRAILLE: Exception closing connection."
            debug.println(debug.LEVEL_INFO, msg, True)

        _brlAPI = None
        return False

    _displaySize = [x, 1]
    idle = False

    # The monitor will be created in refresh if needed.
    if _monitor:
        _monitor.destroy()
        _monitor = None

    clear()
    refresh(True)

    msg = "BRAILLE: Initialized"
    debug.println(debug.LEVEL_INFO, msg, True)
    return True

def shutdown():
    """Shuts down the braille module.   Returns True if the shutdown procedure
    was run.
    """

    msg = "BRAILLE: Attempting braille shutdown."
    debug.println(debug.LEVEL_INFO, msg, True)

    global _brlAPI
    global _brlAPIRunning
    global _brlAPISourceId
    global _monitor
    global _displaySize

    if _brlAPIRunning:
        _brlAPIRunning = False

        msg = "BRAILLE: Removing BrlAPI Source ID."
        debug.println(debug.LEVEL_INFO, msg, True)

        GLib.source_remove(_brlAPISourceId)
        _brlAPISourceId = 0

        try:
            msg = "BRAILLE: Attempting to leave TTY mode."
            debug.println(debug.LEVEL_INFO, msg, True)
            _brlAPI.leaveTtyMode()
        except:
            msg = "BRAILLE: Exception leaving TTY mode."
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            msg = "BRAILLE: Leaving TTY mode succeeded."
            debug.println(debug.LEVEL_INFO, msg, True)

        try:
            msg = "BRAILLE: Attempting to close connection."
            debug.println(debug.LEVEL_INFO, msg, True)
            _brlAPI.closeConnection()
        except:
            msg = "BRAILLE: Exception closing connection."
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            msg = "BRAILLE: Closing connection succeeded."
            debug.println(debug.LEVEL_INFO, msg, True)

        _brlAPI = None

        if _monitor:
            _monitor.destroy()
            _monitor = None
        _displaySize = [DEFAULT_DISPLAY_SIZE, 1]
    else:
        msg = "BRAILLE: Braille was not running."
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    msg = "BRAILLE: Braille shutdown complete."
    debug.println(debug.LEVEL_INFO, msg, True)
    return True
