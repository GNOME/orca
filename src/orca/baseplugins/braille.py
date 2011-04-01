# Orca
#
# Copyright 2011 Consorcio Fernando de los Rios.
# Author: J. Ignacio Alvarez <jialvarez@emergya.es>
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

"""Plugin that implements Braille functions"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

from orca.pluglib.interfaces import IPluginManager, IPlugin, ICommand, \
    IPresenter, IConfigurable, IDependenciesChecker, PluginManagerError

from orca.orca_i18n import _         # for gettext support
from orca.orca_i18n import ngettext  # for ngettext support
from orca.orca_i18n import C_        # to provide qualified translatable strings

import orca.input_event
import orca.keybindings
 
import time

try:
    import brlapi
    availableBrlApi = True
except ImportError, e:
    availableBrlApi = False

class braillePlugin(IPlugin, IPresenter):
    name = 'Braille'
    description = 'Braille display'
    version = '0.9'
    authors = ['J. Ignacio Alvarez <jialvarez@emergya.es>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        global _regionWithFocus
        _regionWithFocus = None
        self._regionWithFocus = _regionWithFocus

        global louis
        
        try:
            import louis
        except ImportError:
            louis = None

    def enable(self):
        import logging
        self.log = logging.getLogger("braille")
        
        import signal
        import os

        global gobject 
        import gobject
        gobject.threads_init()

        if availableBrlApi == True:
            self._brlAPI = None
            self._brlAPIAvailable = True
            self._brlAPIRunning = False
            self._brlAPISourceId = 0
        else:
            self._brlAPIAvailable = False
            self._brlAPIRunning = False
        
        try:
            # This can fail due to gtk not being available.  We want to
            # be able to recover from that if possible.  The main driver
            # for this is to allow "orca --text-setup" to work even if
            # the desktop is not running.
            #
            global brlmon
            import orca.brlmon as brlmon
        except:
            pass

        global debug
        global eventsynthesizer
        global orca_state
        global settings
        global orca

        import orca.debug as debug
        import orca.eventsynthesizer as eventsynthesizer
        import orca.orca_state as orca_state
        import orca.settings as settings
        import orca.orca as orca
        
        # Right now, the orca autogen.sh/configure needs a priori knowledge of
        # where the liblouis tables are.  When running autogen.sh/configure,
        # orca_platform.py:tablesdir will be set to point to the liblouis table
        # location.  If not found, it will be the empty string.  We need to
        # capture that error condition, otherwise braille contraction will
        # just plain fail.  See also bgo#610134.  [[TODO: WDW - see if the
        # liblouis bindings can give us the tablesdir information at runtime
        # http://code.google.com/p/liblouis/issues/detail?id=9]]
        #
        global tablesdir
        from orca.orca_platform import tablesdir as tablesdir

        global louis
        try:
            import louis
        except ImportError:
            louis = None

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
        
        global _
        from orca.orca_i18n import _                          # for gettext support
        
        # The braille monitor
        #
        self._monitor = None
        
        # brlapi keys which are not allowed to interupt speech:
        #
        self.dontInteruptSpeechKeys = []
        if self._brlAPIAvailable:
            self.dontInteruptSpeechKeys = [brlapi.KEY_CMD_FWINLT, brlapi.KEY_CMD_FWINRT, \
                brlapi.KEY_CMD_LNUP, brlapi.KEY_CMD_LNDN]
        
        # Common names for most used BrlTTY commands, to be shown in the GUI:
        # ATM, the ones used in default.py are:
        #
        self.command_name = {}
        
        if self._brlAPIAvailable:
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display scrolls to the left.
            #
            self.command_name[brlapi.KEY_CMD_FWINLT]   = _("Line Left")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display scrolls to the right.
            #
            self.command_name[brlapi.KEY_CMD_FWINRT]   = _("Line Right")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display scrolls up.
            #
            self.command_name[brlapi.KEY_CMD_LNUP]     = _("Line Up")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display scrolls down.
            #
            self.command_name[brlapi.KEY_CMD_LNDN]     = _("Line Down")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, it instructs the braille display to freeze.
            #
            self.command_name[brlapi.KEY_CMD_FREEZE]     = _("Freeze")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display scrolls to the top left of the
            # window.
            #
            self.command_name[brlapi.KEY_CMD_TOP_LEFT] = _("Top Left")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display scrolls to the bottom right of
            # the window.
            #
            self.command_name[brlapi.KEY_CMD_BOT_LEFT] = _("Bottom Right")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display scrolls to position containing
            # the cursor.
            #
            self.command_name[brlapi.KEY_CMD_HOME]     = _("Cursor Position")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # When pressing the button, the display toggles between contracted and
            # contracted braille.
            #
            self.command_name[brlapi.KEY_CMD_SIXDOTS]  = _("Six Dots")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # This command represents a whole set of buttons known as cursor
            # routings keys and are a way for a user to tell the machine they are
            # interested in a particular character on the display.
            #
            self.command_name[brlapi.KEY_CMD_ROUTE]    = _("Cursor Routing")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # This command represents the start of a selection operation.  It is
            # called "Cut Begin" to map to what BrlTTY users are used to:  in
            # character cell mode operation on virtual consoles, the act of copying
            # text is erroneously called a "cut" operation.
            #
            self.command_name[brlapi.KEY_CMD_CUTBEGIN] = _("Cut Begin")
        
            # Translators: this is a command for a button on a refreshable braille
            # display (an external hardware device used by people who are blind).
            # This command represents marking the endpoint of a selection.  It is
            # called "Cut Line" to map to what BrlTTY users are used to:  in
            # character cell mode operation on virtual consoles, the act of copying
            # text is erroneously called a "cut" operation.
            #
            self.command_name[brlapi.KEY_CMD_CUTLINE] = _("Cut Line")
        
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
        self._displaySize = [DEFAULT_DISPLAY_SIZE, 1]
        
        # The list of lines on the display.  This represents the entire amount of data
        # to be drawn on the display.  It will be clipped by the self.viewport if too large.
        #
        self._lines = []
        
        # The region with focus.  This will be displayed at the home position.
        #
        self._regionWithFocus = None

        # The last text information painted.  This has the following fields:
        #
        # lastTextObj = the last accessible
        # lastCaretOffset = the last caret offset of the last text displayed
        # lastLineOffset = the last line offset of the last text displayed
        # lastCursorCell = the last cell on the braille display for the caret
        #
        self._lastTextInfo = (None, 0, 0, 0)
        
        # The self.viewport is a rectangular region of size self._displaySize whose upper left
        # corner is defined by the point (x, line number).  As such, the self.viewport is
        # identified solely by its upper left point.
        #
        self.viewport = [0, 0]
        
        # The callback to call on a BrlTTY input event.  This is passed to
        # the init method.
        #
        self._callback = None
        
        # If True, the given portion of the currently displayed line is showing
        # on the display.
        #
        self.endIsShowing = False
        self.beginningIsShowing = False
        
        # 1-based offset saying which braille cell has the cursor.  A value
        # of 0 means no cell has the cursor.
        #
        self.cursorCell = 0
        
        # The event source of a timeout used for flashing a message.
        #
        self._flashEventSourceId = 0
        
        # Line information saved prior to flashing any messages
        #
        self._saved = None
        
        # Translators: These are the braille translation table names for different
        # languages. You could read about braille tables at:
        # http://en.wikipedia.org/wiki/Braille
        #
        global TABLE_NAMES
        TABLE_NAMES = {"Cz-Cz-g1": _("Czech Grade 1"),
                       "Es-Es-g1": _("Spanish Grade 1"),
                       "Fr-Ca-g2": _("Canada French Grade 2"),
                       "Fr-Fr-g2": _("France French Grade 2"),
                       "Lv-Lv-g1": _("Latvian Grade 1"),
                       "Nl-Nl-g1": _("Netherlands Dutch Grade 1"),
                       "No-No-g0": _("Norwegian Grade 0"),
                       "No-No-g1": _("Norwegian Grade 1"),
                       "No-No-g2": _("Norwegian Grade 2"),
                       "No-No-g3": _("Norwegian Grade 3"),
                       "Pl-Pl-g1": _("Polish Grade 1"),
                       "Pt-Pt-g1": _("Portuguese Grade 1"),
                       "Se-Se-g1": _("Swedish Grade 1"),
                       "ar-ar-g1": _("Arabic Grade 1"),
                       "cy-cy-g1": _("Welsh Grade 1"),
                       "cy-cy-g2": _("Welsh Grade 2"),
                       "de-de-g0": _("German Grade 0"),
                       "de-de-g1": _("German Grade 1"),
                       "de-de-g2": _("German Grade 2"),
                       "en-GB-g2": _("U.K. English Grade 2"),
                       "en-gb-g1": _("U.K. English Grade 1"),
                       "en-us-g1": _("U.S. English Grade 1"),
                       "en-us-g2": _("U.S. English Grade 2"),
                       "fr-ca-g1": _("Canada French Grade 1"),
                       "fr-fr-g1": _("France French Grade 1"),
                       "gr-gr-g1": _("Greek Grade 1"),
                       "hi-in-g1": _("Hindi Grade 1"),
                       "it-it-g1": _("Italian Grade 1"),
                       "nl-be-g1": _("Belgium Dutch Grade 1")}

        if louis:
            _defaultContractionTable = self.getDefaultTable()

        _settingsManager = getattr(orca, '_settingsManager')

        plugins = _settingsManager.getPlugins(_settingsManager.getSetting('activeProfile')[1])

        self.isActive = plugins['braille']['active']

        settings.enableBraille = True
        self.shutdown()
        self.init()

    def listTables(self):
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
    
    def getDefaultTable(self):
        try:
            for fname in os.listdir(tablesdir):
                if fname[-4:] in (".utb", ".ctb"):
                    if fname.startswith("en-us"):
                        return os.path.join(tablesdir, fname)
        except OSError:
            pass
    
        return ""
    
    def _printBrailleEvent(self, level, command):
        """Prints out a Braille event.  The given level may be overridden
        if the eventDebugLevel (see debug.setEventDebugLevel) is greater in
        debug.py.
    
        Arguments:
        - command: the BrlAPI command for the key that was pressed.
        """
    
        debug.printInputEvent(
            level,
            "BRAILLE EVENT: %s" % repr(command))

    def getRegionAtCell(self, cell):
        """Given a 1-based cell offset, return the braille region
        associated with that cell in the form of [region, offsetinregion]
        where 'region' is the region associated with the cell and
        'offsetinregion' is the 0-based offset of where the cell is
        in the region, where 0 represents the beginning of the region.
        """
    
        if len(self._lines) > 0:
            offset = (cell - 1) + self.viewport[0]
            lineNum = self.viewport[1]
            return self._lines[lineNum].getRegionAtOffset(offset)
        else:
            return [None, -1]
    
    def getCaretContext(self, event):
        """Gets the accesible and caret offset associated with the given
        event.  The event should have a BrlAPI event that contains an
        argument value that corresponds to a cell on the display.
    
        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
        the dictionary form of the expanded BrlAPI event.
        """
    
        offset = event.event["argument"]
        [region, regionOffset] = self.getRegionAtCell(offset + 1)
        if region and (isinstance(region, Text) or isinstance(region, ReviewText)):
            accessible = region.accessible
            caretOffset = region.getCaretOffset(regionOffset)
        else:
            accessible = None
            caretOffset = -1
    
        return [accessible, caretOffset]
    
    def clear(self):
        """Clears the logical structure, but keeps the Braille display as is
        (until a refresh operation).
        """
    
        self._lines = []
        self._regionWithFocus = None
        self.viewport = [0, 0]
    
    def setLines(self, lines):
        _lines = lines
    
    def addLine(self, line):
        """Adds a line to the logical display for painting.  The line is added to
        the end of the current list of known lines.  It is necessary for the
        viewport to be over the lines and for refresh to be called for the new
        line to be painted.
    
        Arguments:
        - line: an instance of Line to add.
        """
    
        self._lines.append(line)
        line._index = len(self._lines)
    
    def getShowingLine(self):
        """Returns the Line that is currently being painted on the display.
        """
        return self._lines[self.viewport[1]]
    
    def setFocus(self, region, panToFocus=True, getLinkMask=True):
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
    
        self._regionWithFocus = region
    
        if not panToFocus or (not self._regionWithFocus):
            return
    
        # Adjust the self.viewport according to the new region with focus.
        # The goal is to have the first cell of the region be in the
        # home position, but we will give priority to make sure the
        # cursor for the region is on the display.  For example, when
        # faced with a long text area, we'll show the position with
        # the caret vs. showing the beginning of the region.
    
        lineNum = 0
        done = False
        for line in self._lines:
            for reg in line.regions:
                if reg == self._regionWithFocus:
                    self.viewport[1] = lineNum
                    done = True
                    break
            if done:
                break
            else:
                lineNum += 1
    
        line = self._lines[self.viewport[1]]
        [string, offset, attributeMask] = line.getLineInfo(getLinkMask)
    
        # If the cursor is too far right, we scroll the self.viewport
        # so the cursor will be on the last cell of the display.
        #
        if self._regionWithFocus.cursorOffset >= self._displaySize[0]:
            offset += self._regionWithFocus.cursorOffset - self._displaySize[0] + 1
    
        self.viewport[0] = max(0, offset)
    
    def _realignViewport(self, string, focusOffset, cursorOffset):
        """Realigns the braille display to account for braille alignment
        preferences.  By the time this method is called, if there is a
        cursor cell to be displayed, it should already be somewhere in
        the self.viewport.  All we're going to do is adjust the self.viewport a
        little to align the self.viewport edge according to the
        settings.brailleAlignmentStyle.
    
        Arguments:
        - string: the entire string to be presented
        - focusOffset: where in string the focused region begins
        - cursorOffset: where in the string the cursor should be
    
        Returns: the self.viewport[0] value is potentially modified.
        """
    
        # pylint complains we don't set self.viewport, which in fact we do if
        # 'jump' ends up being set.
        #
        # pylint: disable-msg=W0602
        #
        jump = 0
    
        # If there's no cursor to show or we're doing
        # ALIGN_BRAILLE_BY_EDGE, the self.viewport should already be where it
        # belongs.  Otherwise, we may need to do some adjusting of the
        # self.viewport.
        #
        if (cursorOffset < 0) \
           or (settings.brailleAlignmentStyle == settings.ALIGN_BRAILLE_BY_EDGE) \
           or not (cursorOffset >= self.viewport[0]
                   and cursorOffset < (self.viewport[0] + self._displaySize[0])):
            pass
        else:
            # The left and right margin values are absolute values in the
            # string and represent where in the string the margins of the
            # current self.viewport lie.  Note these are margins and not the
            # actual edges of the self.viewport.
            #
            leftMargin = self.viewport[0] + settings.brailleAlignmentMargin - 1
            rightMargin = (self.viewport[0] + self._displaySize[0]) \
                          - settings.brailleAlignmentMargin
    
            # This represents how far left in the string we want to search
            # and also how far left we'll realign the self.viewport. Setting it
            # to focusOffset means we won't move the self.viewport further left
            # than the beginning of the current region with focus.
            #
            leftMostEdge = max(0, focusOffset)
    
            # If we align by margin, we just want to keep the cursor at or
            # in between the margins.  The only time we go outside the
            # margins are when we are at the ends of the string.
            #
            if settings.brailleAlignmentStyle == settings.ALIGN_BRAILLE_BY_MARGIN:
                if cursorOffset < leftMargin:
                    jump = cursorOffset - leftMargin
                elif cursorOffset > rightMargin:
                    jump = cursorOffset - rightMargin
            elif settings.brailleAlignmentStyle == settings.ALIGN_BRAILLE_BY_WORD:
                # When we align by word, we want to try to show complete
                # words at the edges of the braille display.  When we're
                # near the left edge, we'll try to start a word at the
                # left edge.  When we're near the right edge, we'll try to
                # end a word at the right edge.
                #
                if cursorOffset < leftMargin:
                    # Find the index of the character that is the first
                    # letter of the word prior to left edge of the
                    # self.viewport.
                    #
                    inWord = False
                    leftWordEdge = self.viewport[0] - 1
                    while leftWordEdge >= leftMostEdge:
                        if not string[leftWordEdge] in ' \t\n\r\v\f':
                            inWord = True
                        elif inWord:
                            leftWordEdge += 1
                            break
                        leftWordEdge -= 1
                    leftWordEdge = max(leftMostEdge, leftWordEdge)
                    jump = leftWordEdge - self.viewport[0]
                elif cursorOffset > rightMargin:
                    # Find the index of the character that is the last
                    # letter of the word after the right edge of the
                    # self.viewport.
                    #
                    inWord = False
                    rightWordEdge = self.viewport[0] + self._displaySize[0]
                    while rightWordEdge < len(string):
                        if not string[rightWordEdge] in ' \t\n\r\v\f':
                            inWord = True
                        elif inWord:
                            break
                        rightWordEdge += 1
                    rightWordEdge = min(len(string), rightWordEdge)
                    jump = max(0, rightWordEdge - (self.viewport[0] + self._displaySize[0]))
    
                # We use the brailleMaximumJump to help us handle really
                # long words.  The (jump/abs(jump)) stuff is a quick and
                # dirty way to retain the sign (i.e., +1 or -1).
                #
                if abs(jump) > settings.brailleMaximumJump:
                    jump = settings.brailleMaximumJump * (jump/abs(jump))
    
        if jump:
            # Set the self.viewport's left edge based upon the jump, making
            # sure we don't go any farther left than the leftMostEdge.
            #
            self.viewport[0] = max(leftMostEdge, self.viewport[0] + jump)
    
            # Now, make sure we don't scroll too far to the right.  That
            # is, avoid showing blank spaces to the right if there is more
            # of the string that can be shown.
            #
            self.viewport[0] = min(self.viewport[0],
                              max(leftMostEdge, len(string) - self._displaySize[0]))
    
    def refresh(self, 
                panToCursor=True,
                targetCursorCell=0,
                getLinkMask=True,
                stopFlash=True):
        """Repaints the Braille on the physical display.  This clips the entire
        logical structure by the self.viewport and also sets the cursor to the
        appropriate location.  [[[TODO: WDW - I'm not sure how BrlTTY handles
        drawing to displays with more than one line, so I'm only going to handle
        drawing one line right now.]]]
    
        Arguments:
    
        - panToCursor: if True, will adjust the self.viewport so the cursor is
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
    
        # Check out what we were displaying the last time - it might be
        # the same text object we are displaying now.
        #
        (lastTextObj, lastCaretOffset, lastLineOffset, lastCursorCell) = \
            self._lastTextInfo
        if self._regionWithFocus and isinstance(self._regionWithFocus, braillePlugin().Text):
            currentTextObj = self._regionWithFocus.accessible
            currentCaretOffset = self._regionWithFocus.caretOffset
            currentLineOffset = self._regionWithFocus.lineOffset
        else:
            currentTextObj = None
            currentCaretOffset = 0
            currentLineOffset = 0
    
        if stopFlash:
            self.killFlash(restoreSaved=False)
    
        if len(self._lines) == 0:
            if not self._brlAPIRunning:
                self.init(self._callback, settings.tty)
            if self._brlAPIRunning:
                try:
                    self._brlAPI.writeText("", 0)
                except:
                    debug.println(debug.LEVEL_WARNING,
                                  "BrlTTY seems to have disappeared:")
                    debug.printException(debug.LEVEL_WARNING)
                    self.shutdown()
            self._lastTextInfo = (None, 0, 0, 0)
            return
    
        # Now determine the location of the cursor.  First, we'll figure
        # out the 1-based offset for where we want the cursor to be.  If
        # the target cell is less than zero, it means an offset from the
        # right hand side of the display.
        #
        if targetCursorCell < 0:
            targetCursorCell = self._displaySize[0] + targetCursorCell + 1
    
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
                targetCursorCell = min(self._displaySize[0],
                                       lastCursorCell \
                                       + (currentCaretOffset - lastCaretOffset))
            elif lastCaretOffset > currentCaretOffset:
                targetCursorCell = max(1,
                                       lastCursorCell \
                                       - (lastCaretOffset - currentCaretOffset))
    
        # Now, we figure out the 0-based offset for where the cursor
        # actually is in the string.
        #
        line = self._lines[self.viewport[1]]
        [string, focusOffset, attributeMask] = line.getLineInfo(getLinkMask)
        cursorOffset = -1
        if focusOffset >= 0:
            cursorOffset = focusOffset + self._regionWithFocus.cursorOffset
    
        # Now, if desired, we'll automatically pan the self.viewport to show
        # the cursor.  If there's no targetCursorCell, then we favor the
        # left of the display if we need to pan left, or we favor the
        # right of the display if we need to pan right.
        #
        if panToCursor and (cursorOffset >= 0):
            if len(string) <= self._displaySize[0]:
                self.viewport[0] = 0
            elif targetCursorCell:
                self.viewport[0] = max(0, cursorOffset - targetCursorCell + 1)
            elif cursorOffset < self.viewport[0]:
                self.viewport[0] = max(0, cursorOffset)
            elif cursorOffset >= (self.viewport[0] + self._displaySize[0]):
                self.viewport[0] = max(0, cursorOffset - self._displaySize[0] + 1)
    
        # The cursorOffset should be somewhere in the self.viewport right now.
        # Let's try to realign the self.viewport so that the cursor shows up
        # according to the settings.brailleAlignmentStyle setting.
        #
        self._realignViewport(string, focusOffset, cursorOffset)
    
        startPos = self.viewport[0]
        endPos = startPos + self._displaySize[0]
    
        # Now normalize the cursor position to BrlTTY, which uses 1 as
        # the first cursor position as opposed to 0.
        #
        self.cursorCell = cursorOffset - startPos
        if (self.cursorCell < 0) or (self.cursorCell >= self._displaySize[0]):
            self.cursorCell = 0
        else:
            self.cursorCell += 1 # Normalize to 1-based offset
    
        logLine = "BRAILLE LINE:  '%s'" % string
        debug.println(debug.LEVEL_INFO, logLine)
        self.log.info(logLine.encode("UTF-8"))
        logLine = "     VISIBLE:  '%s', cursor=%d" % \
                        (string[startPos:endPos], self.cursorCell)
        debug.println(debug.LEVEL_INFO, logLine)
        self.log.info(logLine.encode("UTF-8"))
    
        substring = string[startPos:endPos]
        if not self._brlAPIRunning:
            self.init(self._callback, settings.tty)
        if self._brlAPIRunning:
            writeStruct = brlapi.WriteStruct()
            writeStruct.regionBegin = 1
            writeStruct.regionSize = len(substring)
            while writeStruct.regionSize < self._displaySize[0]:
                substring += " "
                if attributeMask:
                    attributeMask += '\x00'
                writeStruct.regionSize += 1
            writeStruct.text = substring
            writeStruct.cursor = self.cursorCell
    
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
            #for i in range(0, self._displaySize[0]):
            #    myUnderline += '\xc0'
            #writeStruct.attrOr = myUnderline
    
            if attributeMask:
                writeStruct.attrOr = attributeMask[startPos:endPos]
    
            if not self._brlAPIRunning:
                self.init(self._callback, settings.tty)
            if self._brlAPIRunning:
                try:
                    self._brlAPI.write(writeStruct)
                except:
                    debug.println(debug.LEVEL_WARNING,
                                  "BrlTTY seems to have disappeared:")
                    debug.printException(debug.LEVEL_WARNING)
                    self.shutdown()
    
        if settings.enableBrailleMonitor:
            if not self._monitor:
                self._monitor = brlmon.BrlMon(self._displaySize[0])
                self._monitor.show_all()
            if attributeMask:
                subMask = attributeMask[startPos:endPos]
            else:
                subMask = None
            self._monitor.writeText(self.cursorCell, substring, subMask)
        elif self._monitor:
            self._monitor.destroy()
            self._monitor = None
    
        self.beginningIsShowing = startPos == 0
        self.endIsShowing = endPos >= len(string)
    
        # Remember the text information we were presenting (if any)
        #
        if self._regionWithFocus and isinstance(self._regionWithFocus, braillePlugin().Text):
            self._lastTextInfo = (self._regionWithFocus.accessible,
                             self._regionWithFocus.caretOffset,
                             self._regionWithFocus.lineOffset,
                             self.cursorCell)
        else:
            self._lastTextInfo = (None, 0, 0, 0)
    
    def _flashCallback(self):
        if self._flashEventSourceId:
            (self._lines, self._regionWithFocus, self.viewport, flashTime) = self._saved
            self.refresh(panToCursor=False, stopFlash=False)
            self._flashEventSourceId = 0
    
        return False
    
    def killFlash(self, restoreSaved=True):
        if self._flashEventSourceId:
            if self._flashEventSourceId > 0:
                gobject.source_remove(self._flashEventSourceId)
            if restoreSaved:
                (self._lines, self._regionWithFocus, self.viewport, flashTime) = self._saved
                self.refresh(panToCursor=False, stopFlash=False)
            self._flashEventSourceId = 0
    
    def resetFlashTimer(self):
        if self._flashEventSourceId > 0:
            gobject.source_remove(self._flashEventSourceId)
            flashTime = self._saved[3]
            self._flashEventSourceId = gobject.timeout_add(flashTime, self._flashCallback)
    
    def _initFlash(self, flashTime):
        """Sets up the state needed to flash a message or clears any existing
        flash if nothing is to be flashed.
    
        Arguments:
        - flashTime:  if non-0, the number of milliseconds to display the
                      regions before reverting back to what was there before.
                      A 0 means to not do any flashing.  A negative number
                      means display the message until some other message
                      comes along or the user presses a cursor routing key.
        """
    
        if self._flashEventSourceId:
            if self._flashEventSourceId > 0:
                gobject.source_remove(self._flashEventSourceId)
            self._flashEventSourceId = 0
        else:
            self._saved = (self._lines, self._regionWithFocus, self.viewport, flashTime)
    
        if flashTime > 0:
            self._flashEventSourceId = gobject.timeout_add(flashTime, self._flashCallback)
        elif flashTime < 0:
            self._flashEventSourceId = -666
    
    def displayRegions(self, regionInfo, flashTime=0):
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
    
        self._initFlash(flashTime)
        regions = regionInfo[0]
        focusedRegion = regionInfo[1]
    
        self.clear()
        line = self.Line()
        for item in regions:
            line.addRegion(item)
        self.addLine(line)
        self.setFocus(focusedRegion)
        self.refresh(stopFlash=False)
    
    def displayMessage(self, message, cursor=-1, flashTime=0):
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
    
        self._initFlash(flashTime)
        self.clear()
        region = self.Region(message, cursor)
        self.addLine(self.Line(region))
        self.setFocus(region)
        self.refresh(True, stopFlash=False)
    
    def panLeft(self, panAmount=0):
        """Pans the display to the left, limiting the pan to the beginning
        of the line being displayed.
    
        Arguments:
        - panAmount: the amount to pan.  A value of 0 means the entire
                     width of the physical display.
    
        Returns True if a pan actually happened.
        """
    
        oldX = self.viewport[0]
    
        if panAmount == 0:
            panAmount = self._displaySize[0]
    
        if self.viewport[0] > 0:
            self.viewport[0] = max(0, self.viewport[0] - panAmount)
    
        return oldX != self.viewport[0]
    
    def panRight(self, panAmount=0):
        """Pans the display to the right, limiting the pan to the length
        of the line being displayed.
    
        Arguments:
        - panAmount: the amount to pan.  A value of 0 means the entire
                     width of the physical display.
    
        Returns True if a pan actually happened.
        """
    
        oldX = self.viewport[0]
    
        if panAmount == 0:
            panAmount = self._displaySize[0]
    
        if len(self._lines) > 0:
            lineNum = self.viewport[1]
            newX = self.viewport[0] + panAmount
            [string, focusOffset, attributeMask] = self._lines[lineNum].getLineInfo()
            if newX < len(string):
                self.viewport[0] = newX
    
        return oldX != self.viewport[0]
    
    def panToOffset(self, offset):
        """Automatically pan left or right to make sure the current offset is
        showing."""
    
        while offset < self.viewport[0]:
            debug.println(debug.LEVEL_FINEST,
                          "braille.panToOffset (left) %d" % offset)
            if not self.panLeft():
                break
    
        while offset >= (self.viewport[0] + self._displaySize[0]):
            debug.println(debug.LEVEL_FINEST,
                          "braille.panToOffset (right) %d" % offset)
            if not self.panRight():
                break
    
    def returnToRegionWithFocus(self, inputEvent=None):
        """Pans the display so the region with focus is displayed.
    
        Arguments:
        - inputEvent: the InputEvent instance that caused this to be called.
    
        Returns True to mean the command should be consumed.
        """
    
        self.setFocus(self._regionWithFocus)
        self.refresh(True)
    
        return True
    
    def setContractedBraille(self, event):
        """Turns contracted braille on or off based upon the event.
    
        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
        the dictionary form of the expanded BrlAPI event.
        """
    
        settings.enableContractedBraille = \
            (event.event["flags"] & brlapi.KEY_FLG_TOGGLE_ON) != 0
        for line in self._lines:
            line.setContractedBraille(settings.enableContractedBraille)
        self.refresh()
    
    def processRoutingKey(self, event):
        """Processes a cursor routing key event.
    
        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
        the dictionary form of the expanded BrlAPI event.
        """
    
        # If a message is being flashed, we'll use a routing key to dismiss it.
        #
        if self._flashEventSourceId:
            self.killFlash()
            return
    
        cell = event.event["argument"]
    
        if len(self._lines) > 0:
            cursor = cell + self.viewport[0]
            lineNum = self.viewport[1]
            self._lines[lineNum].processRoutingKey(cursor)
    
        return True
    
    def _processBrailleEvent(self, event):
        """Handles BrlTTY command events.  This passes commands on to Orca for
        processing.
    
        Arguments:
        - event: the BrlAPI input event (expanded)
        """
    
        self._printBrailleEvent(debug.LEVEL_FINE, event)
    
        consumed = False
    
        if settings.timeoutCallback and (settings.timeoutTime > 0):
            signal.signal(signal.SIGALRM, settings.timeoutCallback)
            signal.alarm(settings.timeoutTime)
    
        if self._callback:
            try:
                # Like key event handlers, a return value of True means
                # the command was consumed.
                #
                consumed = self._callback(event)
            except:
                debug.println(debug.LEVEL_WARNING, "Issue processing event:")
                debug.printException(debug.LEVEL_WARNING)
                consumed = False
    
        if settings.timeoutCallback and (settings.timeoutTime > 0):
            signal.alarm(0)
    
        return consumed
    
    def _brlAPIKeyReader(self, source, condition):
        """Method to read a key from the BrlAPI bindings.  This is a
        gobject IO watch handler.
        """
        try:
            key = self._brlAPI.readKey(False)
        except:
            debug.println(debug.LEVEL_WARNING, "BrlTTY seems to have disappeared:")
            debug.printException(debug.LEVEL_WARNING)
            self.shutdown()
            return
        if key:
            self._processBrailleEvent(self._brlAPI.expandKeyCode(key))
        return self._brlAPIRunning
    
    def setupKeyRanges(self, keys):
        """Hacky method to tell BrlTTY what to send and not send us via
        the readKey method.  This only works with BrlTTY v3.8 and better.
    
        Arguments:
        -keys: a list of BrlAPI commands.
        """
        if not self._brlAPIRunning:
            self.init(self._callback, settings.tty)
        if not self._brlAPIRunning:
            return
    
        # First, start by ignoring everything.
        #
        self._brlAPI.ignoreKeys(brlapi.rangeType_all, [0])
    
        # Next, enable cursor routing keys.
        #
        keySet = [brlapi.KEY_TYPE_CMD | brlapi.KEY_CMD_ROUTE]
    
        # Finally, enable the commands we care about.
        #
        for key in keys:
            keySet.append(brlapi.KEY_TYPE_CMD | key)
    
        self._brlAPI.acceptKeys(brlapi.rangeType_command, keySet)
    
    def init(self, callback=None, tty=7):
        """Initializes the braille module, connecting to the BrlTTY driver.
    
        Arguments:
        - callback: the method to call with a BrlTTY input event.
        - tty: the tty port to take ownership of (default = 7)
        Returns False if BrlTTY cannot be accessed or braille has
        not been enabled.
        """
    
        if self._brlAPIRunning:
            return True
    
        if not settings.enableBraille or not self.isActive:
            return False
    
        self._callback = callback
    
        try:
            self._brlAPI = brlapi.Connection()
    
            try:
                windowPath = os.environ["WINDOWPATH"]
                self._brlAPI.enterTtyModeWithPath()
                self._brlAPIRunning = True
                debug.println(\
                    debug.LEVEL_CONFIGURATION,
                    "Braille module has been initialized using WINDOWPATH=" \
                    + "%s" % windowPath)
            except:
                self._brlAPI.enterTtyMode(tty)
                self._brlAPIRunning = True
                debug.println(\
                    debug.LEVEL_CONFIGURATION,
                    "Braille module has been initialized using tty=%d" % tty)
            self._brlAPISourceId = gobject.io_add_watch(self._brlAPI.fileDescriptor,
                                                   gobject.IO_IN,
                                                   self._brlAPIKeyReader)
        except:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Could not initialize BrlTTY:")
            debug.printException(debug.LEVEL_CONFIGURATION)
            self._brlAPIRunning = False
            return False
    
        # [[[TODO: WDW - For some reason, BrlTTY wants to say the height of the
        # Vario is 40 so we hardcode it to 1 for now.]]]
        #
        #self._displaySize = (brl.getDisplayWidth(), brl.getDisplayHeight())
        (x, y) = self._brlAPI.displaySize
        self._displaySize = [x, 1]
    
        # The monitor will be created in refresh if needed.
        #
        if self._monitor:
            self._monitor.destroy()
            self._monitor = None
    
        debug.println(debug.LEVEL_CONFIGURATION,
                      "braille display size = (%d, %d)" \
                      % (self._displaySize[0], self._displaySize[1]))
    
        self.clear()
        self.refresh(True)
    
        return True
    
    def shutdown(self):
        """Shuts down the braille module.   Returns True if the shutdown procedure
        was run.
        """
    
        if self._brlAPIRunning:
            self._brlAPIRunning = False
            gobject.source_remove(self._brlAPISourceId)
            self._brlAPISourceId = 0
            try:
                self._brlAPI.leaveTtyMode()
            except:
                pass
            if self._monitor:
                self._monitor.destroy()
                self._monitor = None
            self._displaySize = [DEFAULT_DISPLAY_SIZE, 1]
        else:
            return False
    
        return True
    
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
    
            import orca.settings as settings
    
            if not string:
                string = ""
    
            # If louis is None, then we don't go into contracted mode.
            self.contracted = settings.enableContractedBraille and \
                              louis is not None
    
            self.expandOnCursor = expandOnCursor
    
            # The uncontracted string for the line.
            #
            self.rawLine = string.decode("UTF-8").strip("\n")
    
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
            maskSize = len(self.string) + (2 * self.string.count(u'\u2026'))
    
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
    
            braillePlugin().Region.__init__(self, string, cursorOffset, expandOnCursor)
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
            braillePlugin().Component.__init__(self, accessible, string, cursorOffset, '', True)
    
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
    
            import orca.orca_state as orca_state
            import orca.settings as settings
    
            self.accessible = accessible
            if orca_state.activeScript and self.accessible:
                [string, self.caretOffset, self.lineOffset] = \
                     orca_state.activeScript.getTextLineAtCaret(self.accessible,
                                                                startOffset)
            else:
                string = ""
                self.caretOffset = 0
                self.lineOffset = 0
    
            string = string.decode("UTF-8")
            if label:
                label = label.decode("UTF-8")
            if eol:
                eol = eol.decode("UTF-8")
    
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
    
            self._maxCaretOffset = self.lineOffset + len(string)
    
            self.eol = eol
    
            if label:
                self.label = label + ' '
            else:
                self.label = ''
    
            string = self.label + string
    
            cursorOffset += len(self.label)
    
            braillePlugin().Region.__init__(self, string, cursorOffset, True)
    
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
            string = string.decode("UTF-8")
    
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
            regionMask = [settings.TEXT_ATTR_BRAILLE_NONE]*stringLength
    
            attrIndicator = settings.textAttributesBrailleIndicator
            selIndicator = settings.brailleSelectorIndicator
            linkIndicator = settings.brailleLinkIndicator
            script = orca_state.activeScript
    
            if getLinkMask and linkIndicator != settings.BRAILLE_LINK_NONE:
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
                keys, enabledAttributes = script.utilities.stringToKeysAndDict(
                    settings.enabledBrailledTextAttributes)
    
                offset = self.lineOffset
                while offset < lineEndOffset:
                    attributes, startOffset, endOffset = \
                        script.utilities.textAttributes(self.accessible,
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
                selections = script.utilities.allTextSelections(self.accessible)
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
                regionMask = contractedMask[:len(self.string)]
    
            # Add empty mask characters for the EOL character as well as for
            # any label that might be present.
            #
            regionMask += [0]*len(self.eol)
    
            if self.label:
                regionMask = [0]*len(self.label) + regionMask
    
            return ''.join(map(chr, regionMask))
    
        def contractLine(self, line, cursorOffset=0, expandOnCursor=True):
            contracted, inPos, outPos, cursorPos = \
                    braillePlugin().Region.contractLine(
                            self, line, cursorOffset, expandOnCursor)
    
            return contracted + self.eol, inPos, outPos, cursorPos
    
        def displayToBufferOffset(self, display_offset):
            offset = braillePlugin().Region.displayToBufferOffset(self, display_offset)
            offset += self.startOffset
            offset -= len(self.label)
            return offset
    
        def setContractedBraille(self, contracted):
            braillePlugin().Region.setContractedBraille(self, contracted)
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
            braillePlugin().Component.__init__(self, accessible, string,
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
            braillePlugin().Region.__init__(self, string, expandOnCursor=True)
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
                if region == braillePlugin()._regionWithFocus:
                    focusOffset = len(string)
                if region.string:
                    # [[[TODO: WDW - HACK: Replace ellipses with "..."
                    # The ultimate solution is to get i18n support into
                    # BrlTTY.]]]
                    #
                    string += region.string.replace(u'\u2026', "...")
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

    def disable(self):
        settings.enableBraille = False
        self.isActive = False
        self.shutdown()

IPlugin.register(braillePlugin)

