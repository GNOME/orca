# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
# Copyright 2014 Igalia, S.L.
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

# [[[TODO: WDW - Pylint is giving us a bunch of errors along these
# lines throughout this file:
#
# E1103:4241:Script.updateBraille: Instance of 'list' has no 'getRole'
# member (but some types could not be inferred)
#
# I don't know what is going on, so I'm going to tell pylint to
# disable those messages for Gecko.py.]]]
#
# pylint: disable-msg=E1103

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Orca Team." \
                "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

from gi.repository import Gtk
import pyatspi
import time
import urllib.parse

import orca.braille as braille
import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.scripts.default as default
import orca.eventsynthesizer as eventsynthesizer
import orca.guilabels as guilabels
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.liveregions as liveregions
import orca.messages as messages
import orca.object_properties as object_properties
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech as speech
import orca.speechserver as speechserver

from . import keymaps
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .formatting import Formatting
from .bookmarks import GeckoBookmarks
from .structural_navigation import GeckoStructuralNavigation
from .script_utilities import Utilities

from orca.orca_i18n import _
from orca.speech_generator import Pause
from orca.acss import ACSS

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# Script                                                               #
#                                                                      #
########################################################################

class Script(default.Script):
    """The script for Firefox."""

    ####################################################################
    #                                                                  #
    # Overridden Script Methods                                        #
    #                                                                  #
    ####################################################################

    def __init__(self, app):
        default.Script.__init__(self, app)
        # Initialize variables to make pylint happy.
        #
        self.changedLinesOnlyCheckButton = None
        self.controlCaretNavigationCheckButton = None
        self.minimumFindLengthAdjustment = None
        self.minimumFindLengthLabel = None
        self.minimumFindLengthSpinButton = None
        self.sayAllOnLoadCheckButton = None
        self.skipBlankCellsCheckButton = None
        self.speakCellCoordinatesCheckButton = None
        self.speakCellHeadersCheckButton = None
        self.speakCellSpanCheckButton = None
        self.speakResultsDuringFindCheckButton = None
        self.structuralNavigationCheckButton = None
        self.autoFocusModeStructNavCheckButton = None
        self.autoFocusModeCaretNavCheckButton = None

        # _caretNavigationFunctions are functions that represent fundamental
        # ways to move the caret (e.g., by the arrow keys).
        #
        self._caretNavigationFunctions = \
            [Script.goNextCharacter,
             Script.goPreviousCharacter,
             Script.goNextWord,
             Script.goPreviousWord,
             Script.goNextLine,
             Script.goPreviousLine,
             Script.goTopOfFile,
             Script.goBottomOfFile,
             Script.goBeginningOfLine,
             Script.goEndOfLine]

        self._liveRegionFunctions = \
            [Script.setLivePolitenessOff,
             Script.advanceLivePoliteness,
             Script.monitorLiveRegions,
             Script.reviewLiveAnnouncement]

        if _settingsManager.getSetting('caretNavigationEnabled') == None:
            _settingsManager.setSetting('caretNavigationEnabled', True)
        if _settingsManager.getSetting('sayAllOnLoad') == None:
            _settingsManager.setSetting('sayAllOnLoad', True)

        # We keep track of whether we're currently in the process of
        # loading a page.
        #
        self._loadingDocumentContent = False
        self._loadingDocumentTime = 0.0

        # In tabbed content (i.e., Firefox's support for one tab per
        # URL), we also keep track of the caret context in each tab.
        # the key is the document frame and the value is the caret
        # context for that frame.
        #
        self._documentFrameCaretContext = {}

        # During a find we get caret-moved events reflecting the changing
        # screen contents.  The user can opt to have these changes announced.
        # If the announcement is enabled, it still only will be made if the
        # selected text is a certain length (user-configurable) and if the
        # line has changed (so we don't keep repeating the line).  However,
        # the line has almost certainly changed prior to this length being
        # reached.  Therefore, we need to make an initial announcement, which
        # means we need to know if that has already taken place.
        #
        self.madeFindAnnouncement = False

        # We don't want to prevent the user from arrowing into an
        # autocomplete when it appears in a search form.  We need to
        # keep track if one has appeared or disappeared.
        #
        self._autocompleteVisible = False

        # Create the live region manager and start the message manager
        self.liveMngr = liveregions.LiveRegionManager(self)

        # We want to keep track of the line contents we just got so that
        # we can speak and braille this information without having to call
        # getLineContentsAtOffset() twice.
        #
        self.currentLineContents = None

        # For really large objects, a call to getAttributes can take up to
        # two seconds! This is a Firefox bug. We'll try to improve things
        # by storing attributes.
        #
        self.currentAttrs = {}

        # Last focused frame. We are only interested in frame focused events
        # when it is a different frame, so here we store the last frame
        # that recieved state-changed:focused.
        #
        self._currentFrame = None

        # A dictionary of Gecko-style attribute names and their equivalent/
        # expected names. This is necessary so that we can present the
        # attributes to the user in a consistent fashion across apps and
        # toolkits. Note that underlinesolid and line-throughsolid are
        # temporary fixes: text_attribute_names.py assumes a one-to-one
        # correspondence. This is not a problem when going from attribute
        # name to localized name; in the reverse direction, we need more
        # context (i.e. we can't safely make them both be "solid"). A
        # similar issue exists with "start" which means no justification
        # has explicitly been set. If we set that to "none", "none" will
        # no longer have a single reverse translation.
        #
        self.attributeNamesDict = {
            "font-weight"             : "weight",
            "font-family"             : "family-name",
            "font-style"              : "style",
            "text-align"              : "justification",
            "text-indent"             : "indent",
            "font-size"               : "size",
            "background-color"        : "bg-color",
            "color"                   : "fg-color",
            "text-line-through-style" : "strikethrough",
            "text-underline-style"    : "underline",
            "text-position"           : "vertical-align",
            "writing-mode"            : "direction",
            "-moz-left"               : "left",
            "-moz-right"              : "right",
            "-moz-center"             : "center",
            "start"                   : "no justification",
            "underlinesolid"          : "single",
            "line-throughsolid"       : "solid"}

        # Keep track of the last object which appeared as a result of
        # the user routing the mouse pointer over an object. Also keep
        # track of the object which is associated with the mouse over
        # so that we can restore focus to it if need be.
        #
        self.lastMouseOverObject = None
        self.preMouseOverContext = [None, -1]
        self.inMouseOverObject = False

        self._inFocusMode = False
        self._focusModeIsSticky = False

        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False

        # See bug 665522 - comment 5
        app.setCacheMask(pyatspi.cache.DEFAULT ^ pyatspi.cache.CHILDREN)

    def deactivate(self):
        """Called when this script is deactivated."""

        self._loadingDocumentContent = False
        self._loadingDocumentTime = 0.0

    def getBookmarks(self):
        """Returns the "bookmarks" class for this script.
        """
        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = GeckoBookmarks(self)
            return self.bookmarks

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script.
        """

        enabledTypes = [GeckoStructuralNavigation.BLOCKQUOTE,
                        GeckoStructuralNavigation.BUTTON,
                        GeckoStructuralNavigation.CHECK_BOX,
                        GeckoStructuralNavigation.CHUNK,
                        GeckoStructuralNavigation.CLICKABLE,
                        GeckoStructuralNavigation.COMBO_BOX,
                        GeckoStructuralNavigation.ENTRY,
                        GeckoStructuralNavigation.FORM_FIELD,
                        GeckoStructuralNavigation.HEADING,
                        GeckoStructuralNavigation.IMAGE,
                        GeckoStructuralNavigation.LANDMARK,
                        GeckoStructuralNavigation.LINK,
                        GeckoStructuralNavigation.LIST,
                        GeckoStructuralNavigation.LIST_ITEM,
                        GeckoStructuralNavigation.LIVE_REGION,
                        GeckoStructuralNavigation.PARAGRAPH,
                        GeckoStructuralNavigation.RADIO_BUTTON,
                        GeckoStructuralNavigation.SEPARATOR,
                        GeckoStructuralNavigation.TABLE,
                        GeckoStructuralNavigation.TABLE_CELL,
                        GeckoStructuralNavigation.UNVISITED_LINK,
                        GeckoStructuralNavigation.VISITED_LINK]

        return enabledTypes

    def getStructuralNavigation(self):
        """Returns the 'structural navigation' class for this script.
        """
        types = self.getEnabledStructuralNavigationTypes()
        enable = _settingsManager.getSetting('structuralNavigationEnabled')
        return GeckoStructuralNavigation(self, types, enable)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings.
        """

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(\
            self.structuralNavigation.inputEventHandlers)

        self.inputEventHandlers["goNextCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goNextCharacter,
                cmdnames.CARET_NAVIGATION_NEXT_CHAR)

        self.inputEventHandlers["goPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousCharacter,
                cmdnames.CARET_NAVIGATION_PREV_CHAR)

        self.inputEventHandlers["goNextWordHandler"] = \
            input_event.InputEventHandler(
                Script.goNextWord,
                cmdnames.CARET_NAVIGATION_NEXT_WORD)

        self.inputEventHandlers["goPreviousWordHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousWord,
                cmdnames.CARET_NAVIGATION_PREV_WORD)

        self.inputEventHandlers["goNextLineHandler"] = \
            input_event.InputEventHandler(
                Script.goNextLine,
                cmdnames.CARET_NAVIGATION_NEXT_LINE)

        self.inputEventHandlers["goPreviousLineHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousLine,
                cmdnames.CARET_NAVIGATION_PREV_LINE)

        self.inputEventHandlers["goTopOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goTopOfFile,
                cmdnames.CARET_NAVIGATION_FILE_START)

        self.inputEventHandlers["goBottomOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goBottomOfFile,
                cmdnames.CARET_NAVIGATION_FILE_END)

        self.inputEventHandlers["goBeginningOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.goBeginningOfLine,
                cmdnames.CARET_NAVIGATION_LINE_START)

        self.inputEventHandlers["goEndOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.goEndOfLine,
                cmdnames.CARET_NAVIGATION_LINE_END)

        self.inputEventHandlers["advanceLivePoliteness"] = \
            input_event.InputEventHandler(
                Script.advanceLivePoliteness,
                cmdnames.LIVE_REGIONS_ADVANCE_POLITENESS)

        self.inputEventHandlers["setLivePolitenessOff"] = \
            input_event.InputEventHandler(
                Script.setLivePolitenessOff,
                cmdnames.LIVE_REGIONS_SET_POLITENESS_OFF)

        self.inputEventHandlers["monitorLiveRegions"] = \
            input_event.InputEventHandler(
                Script.monitorLiveRegions,
                cmdnames.LIVE_REGIONS_MONITOR)

        self.inputEventHandlers["reviewLiveAnnouncement"] = \
            input_event.InputEventHandler(
                Script.reviewLiveAnnouncement,
                cmdnames.LIVE_REGIONS_REVIEW)

        self.inputEventHandlers["toggleCaretNavigationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleCaretNavigation,
                cmdnames.CARET_NAVIGATION_TOGGLE)

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                cmdnames.SAY_ALL)

        self.inputEventHandlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["moveToMouseOverHandler"] = \
            input_event.InputEventHandler(
                Script.moveToMouseOver,
                cmdnames.MOUSE_OVER_MOVE)

        self.inputEventHandlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.inputEventHandlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

    def __getArrowBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        arrow keys for navigating HTML content.
        """

        keyBindings = keybindings.KeyBindings()
        keyBindings.load(keymaps.arrowKeymap, self.inputEventHandlers)
        return keyBindings

    def getToolkitKeyBindings(self):
        """Returns the toolkit-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        keyBindings.load(keymaps.commonKeymap, self.inputEventHandlers)

        if _settingsManager.getSetting('keyboardLayout') == \
                orca.settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            keyBindings.load(keymaps.desktopKeymap, self.inputEventHandlers)
        else:
            keyBindings.load(keymaps.laptopKeymap, self.inputEventHandlers)

        if _settingsManager.getSetting('caretNavigationEnabled'):
            for keyBinding in self.__getArrowBindings().keyBindings:
                keyBindings.add(keyBinding)

        bindings = self.structuralNavigation.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        generalFrame = Gtk.Frame()
        grid.attach(generalFrame, 0, 0, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.PAGE_NAVIGATION)
        label.set_use_markup(True)
        generalFrame.set_label_widget(label)

        generalAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        generalAlignment.set_padding(0, 0, 12, 0)
        generalFrame.add(generalAlignment)
        generalGrid = Gtk.Grid()
        generalAlignment.add(generalGrid)

        label = guilabels.USE_CARET_NAVIGATION
        value = _settingsManager.getSetting('caretNavigationEnabled')
        self.controlCaretNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.controlCaretNavigationCheckButton.set_active(value) 
        generalGrid.attach(self.controlCaretNavigationCheckButton, 0, 0, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_CARET_NAV
        value = _settingsManager.getSetting('caretNavTriggersFocusMode')
        self.autoFocusModeCaretNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.autoFocusModeCaretNavCheckButton.set_active(value)
        generalGrid.attach(self.autoFocusModeCaretNavCheckButton, 0, 1, 1, 1)

        label = guilabels.USE_STRUCTURAL_NAVIGATION
        value = self.structuralNavigation.enabled
        self.structuralNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.structuralNavigationCheckButton.set_active(value)
        generalGrid.attach(self.structuralNavigationCheckButton, 0, 2, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_STRUCT_NAV
        value = _settingsManager.getSetting('structNavTriggersFocusMode')
        self.autoFocusModeStructNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.autoFocusModeStructNavCheckButton.set_active(value)
        generalGrid.attach(self.autoFocusModeStructNavCheckButton, 0, 3, 1, 1)

        label = guilabels.READ_PAGE_UPON_LOAD
        value = _settingsManager.getSetting('sayAllOnLoad')
        self.sayAllOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.sayAllOnLoadCheckButton.set_active(value)
        generalGrid.attach(self.sayAllOnLoadCheckButton, 0, 4, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 1, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.TABLE_NAVIGATION)
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = _settingsManager.getSetting('speakCellCoordinates')
        self.speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self.speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = _settingsManager.getSetting('speakCellSpan')
        self.speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self.speakCellSpanCheckButton, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = _settingsManager.getSetting('speakCellHeaders')
        self.speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self.speakCellHeadersCheckButton, 0, 2, 1, 1)
           
        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = _settingsManager.getSetting('skipBlankCells')
        self.skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self.skipBlankCellsCheckButton, 0, 3, 1, 1)

        findFrame = Gtk.Frame()
        grid.attach(findFrame, 0, 2, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.FIND_OPTIONS)
        label.set_use_markup(True)
        findFrame.set_label_widget(label)

        findAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        findAlignment.set_padding(0, 0, 12, 0)
        findFrame.add(findAlignment)
        findGrid = Gtk.Grid()
        findAlignment.add(findGrid)

        verbosity = _settingsManager.getSetting('findResultsVerbosity')

        label = guilabels.FIND_SPEAK_RESULTS
        value = verbosity != settings.FIND_SPEAK_NONE
        self.speakResultsDuringFindCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakResultsDuringFindCheckButton.set_active(value)
        findGrid.attach(self.speakResultsDuringFindCheckButton, 0, 0, 1, 1)

        label = guilabels.FIND_ONLY_SPEAK_CHANGED_LINES
        value = verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED
        self.changedLinesOnlyCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.changedLinesOnlyCheckButton.set_active(value)
        findGrid.attach(self.changedLinesOnlyCheckButton, 0, 1, 1, 1)

        hgrid = Gtk.Grid()
        findGrid.attach(hgrid, 0, 2, 1, 1)

        self.minimumFindLengthLabel = \
              Gtk.Label(label=guilabels.FIND_MINIMUM_MATCH_LENGTH)
        self.minimumFindLengthLabel.set_alignment(0, 0.5)
        hgrid.attach(self.minimumFindLengthLabel, 0, 0, 1, 1)

        self.minimumFindLengthAdjustment = \
                   Gtk.Adjustment(_settingsManager.getSetting('findResultsMinimumLength'), 0, 20, 1)
        self.minimumFindLengthSpinButton = Gtk.SpinButton()
        self.minimumFindLengthSpinButton.set_adjustment(
            self.minimumFindLengthAdjustment)
        hgrid.attach(self.minimumFindLengthSpinButton, 1, 0, 1, 1)
        self.minimumFindLengthLabel.set_mnemonic_widget(
            self.minimumFindLengthSpinButton)

        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        if not self.speakResultsDuringFindCheckButton.get_active():
            verbosity = settings.FIND_SPEAK_NONE
        elif self.changedLinesOnlyCheckButton.get_active():
            verbosity = settings.FIND_SPEAK_IF_LINE_CHANGED
        else:
            verbosity = settings.FIND_SPEAK_ALL

        return {
            'findResultsVerbosity': verbosity,
            'findResultsMinimumLength': self.minimumFindLengthSpinButton.get_value(),
            'sayAllOnLoad': self.sayAllOnLoadCheckButton.get_active(),
            'structuralNavigationEnabled': self.structuralNavigationCheckButton.get_active(),
            'structNavTriggersFocusMode': self.autoFocusModeStructNavCheckButton.get_active(),
            'caretNavigationEnabled': self.controlCaretNavigationCheckButton.get_active(),
            'caretNavTriggersFocusMode': self.autoFocusModeCaretNavCheckButton.get_active(),
            'speakCellCoordinates': self.speakCellCoordinatesCheckButton.get_active(),
            'speakCellSpan': self.speakCellSpanCheckButton.get_active(),
            'speakCellHeaders': self.speakCellHeadersCheckButton.get_active(),
            'skipBlankCells': self.skipBlankCellsCheckButton.get_active()
        }

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """

        # We need to do this here. Orca caret and structural navigation
        # often result in the user being repositioned without our getting
        # a corresponding AT-SPI event. Without an AT-SPI event, script.py
        # won't know to dump the generator cache. See bgo#618827.
        #
        self.generatorCache = {}

        # The reason we override this method is that we only want
        # to consume keystrokes under certain conditions.  For
        # example, we only control the arrow keys when we're
        # managing caret navigation and we're inside document content.
        #
        # [[[TODO: WDW - this might be broken when we're inside a
        # text area that's inside document (or anything else that
        # we want to allow to control its own destiny).]]]

        user_bindings = None
        user_bindings_map = _settingsManager.getSetting('keyBindingsMap')
        if self.__module__ in user_bindings_map:
            user_bindings = user_bindings_map[self.__module__]
        elif "default" in user_bindings_map:
            user_bindings = user_bindings_map["default"]

        consumes = False
        if user_bindings:
            handler = user_bindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                consumes = self.useCaretNavigationModel(keyboardEvent)
                self._lastCommandWasCaretNav = consumes
                self._lastCommandWasStructNav = False
            elif handler \
                 and (handler.function in self.structuralNavigation.functions \
                      or handler.function in self._liveRegionFunctions):
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
            else:
                consumes = handler != None
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = False
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                consumes = self.useCaretNavigationModel(keyboardEvent)
                self._lastCommandWasCaretNav = consumes
                self._lastCommandWasStructNav = False
            elif handler \
                 and (handler.function in self.structuralNavigation.functions \
                      or handler.function in self._liveRegionFunctions):
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
            else:
                consumes = handler != None
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = False
        return consumes

    def textLines(self, obj):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        # Determine the correct "say all by" mode to use.
        #
        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
        sayAllBySentence = sayAllStyle == settings.SAYALL_STYLE_SENTENCE

        [obj, characterOffset] = self.getCaretContext()
        if sayAllBySentence:
            # Attempt to locate the start of the current sentence by
            # searching to the left for a sentence terminator.  If we don't
            # find one, or if the "say all by" mode is not sentence, we'll
            # just start the sayAll from at the beginning of this line/object.
            #
            text = self.utilities.queryNonEmptyText(obj)
            if text:
                [line, startOffset, endOffset] = \
                    text.getTextAtOffset(characterOffset,
                                         pyatspi.TEXT_BOUNDARY_LINE_START)
                beginAt = 0
                if line.strip():
                    terminators = ['. ', '? ', '! ']
                    for terminator in terminators:
                        try:
                            index = line.rindex(terminator,
                                                0,
                                                characterOffset - startOffset)
                            if index > beginAt:
                                beginAt = index
                        except:
                            pass
                    characterOffset = startOffset + beginAt
                else:
                    [obj, characterOffset] = \
                        self.findNextCaretInOrder(obj, characterOffset)

        done = False
        while not done:
            if sayAllBySentence:
                contents = self.getObjectContentsAtOffset(obj, characterOffset)
            else:
                contents = self.getLineContentsAtOffset(obj, characterOffset)
            for content in contents:
                obj, startOffset, endOffset, text = content
                if self.isLabellingContents(obj, contents):
                    continue

                utterances = self.getUtterancesFromContents([content], True)

                # TODO - JD: This is sad, but it's better than the old, broken
                # clumpUtterances(). We really need to fix the speechservers'
                # SayAll support. In the meantime, the generators should be
                # providing one ACSS per string.
                elements = list(filter(lambda x: isinstance(x, str), utterances[0]))
                voices = list(filter(lambda x: isinstance(x, ACSS), utterances[0]))
                if len(elements) != len(voices):
                    continue

                for i, element in enumerate(elements):
                    yield [speechserver.SayAllContext(obj, element,
                                                      startOffset, endOffset),
                           voices[i]]

            obj = contents[-1][0]
            characterOffset = contents[-1][2]
            [obj, characterOffset] = self.findNextCaretInOrder(obj, characterOffset)
            done = (obj == None)

    def presentFindResults(self, obj, offset):
        """Updates the caret context to the match indicated by obj and
        offset.  Then presents the results according to the user's
        preferences.

        Arguments:
        -obj: The accessible object within the document
        -offset: The offset with obj where the caret should be positioned
        """

        # At some point in Firefox 3.2 we started getting detail1 values of
        # -1 for the caret-moved events for unfocused content during a find.
        # We don't want to base the new caret offset -- or the current line
        # on this value. We should be able to count on the selection range
        # instead -- across FF 3.0, 3.1, and 3.2.
        #
        enoughSelected = False
        text = self.utilities.queryNonEmptyText(obj)
        if text and text.getNSelections():
            [start, end] = text.getSelection(0)
            offset = max(offset, start)
            if end - start >= _settingsManager.getSetting('findResultsMinimumLength'):
                enoughSelected = True

        # Haing done that, update the caretContext. If the user wants
        # matches spoken, we also need to if we are on the same line
        # as before.
        #
        origObj, origOffset = self.getCaretContext()
        self.setCaretContext(obj, offset)
        verbosity = _settingsManager.getSetting('findResultsVerbosity')
        if enoughSelected and verbosity != settings.FIND_SPEAK_NONE:
            origExtents = self.utilities.getExtents(origObj, origOffset - 1, origOffset)
            newExtents = self.utilities.getExtents(obj, offset - 1, offset)
            lineChanged = not self.utilities.extentsAreOnSameLine(origExtents, newExtents)

            # If the user starts backspacing over the text in the
            # toolbar entry, he/she is indicating they want to perform
            # a different search. Because madeFindAnnounement may
            # be set to True, we should reset it -- but only if we
            # detect the line has also changed.  We're not getting
            # events from the Find entry, so we have to compare
            # offsets.
            #
            if self.utilities.isSameObject(origObj, obj) \
               and (origOffset > offset) and lineChanged:
                self.madeFindAnnouncement = False

            if lineChanged or not self.madeFindAnnouncement or \
               verbosity != settings.FIND_SPEAK_IF_LINE_CHANGED:
                self.presentLine(obj, offset)
                self.madeFindAnnouncement = True

    def sayAll(self, inputEvent):
        """Speaks the contents of the document beginning with the present
        location.  Overridden in this script because the sayAll could have
        been started on an object without text (such as an image).
        """

        if not self.inDocumentContent():
            return default.Script.sayAll(self, inputEvent)

        else:
            speech.sayAll(self.textLines(orca_state.locusOfFocus),
                          self.__sayAllProgressCallback)

        return True

    def __sayAllProgressCallback(self, context, progressType):
        if not self.inDocumentContent():
            default.Script.__sayAllProgressCallback(self, context, progressType)
            return

        orca.setLocusOfFocus(None, context.obj, notifyScript=False)
        self.setCaretContext(context.obj, context.currentOffset)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if not self.inDocumentContent(event.source):
            default.Script.onCaretMoved(self, event)
            return

        if self._lastCommandWasCaretNav:
            msg = "INFO: Caret-moved event ignored: last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg)
            return

        if self._lastCommandWasStructNav:
            msg = "INFO: Caret-moved event ignored: last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg)
            return

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            if event.source.getRole() == pyatspi.ROLE_LINK:
                orca.setLocusOfFocus(event, event.source)
                self.setCaretContext(event.source, event.detail1)
            return

        char, start, end = text.getTextAtOffset(event.detail1, pyatspi.TEXT_BOUNDARY_CHAR)
        if char == self.EMBEDDED_OBJECT_CHARACTER:
            msg = "INFO: Caret-moved event ignored: Caret moved to embedded object"
            debug.println(debug.LEVEL_INFO, msg)
            return

        if not char:
            msg = "INFO: Caret-moved event ignored: Caret moved to empty character"
            debug.println(debug.LEVEL_INFO, msg)
            return

        contextObj, contextOffset = self.getCaretContext()
        if event.detail1 == contextOffset and event.source == contextObj:
            return

        obj = event.source
        state = obj.getState()

        firstObj, firstOffset = self.findFirstCaretContext(obj, event.detail1)
        if firstOffset == contextOffset and firstObj == contextObj:
            return

        if contextObj and contextObj.parent == firstObj \
           and not state.contains(pyatspi.STATE_EDITABLE):
            return

        if self.utilities.inFindToolbar():
            self.presentFindResults(obj, event.detail1)
            return

        self.setCaretContext(obj, event.detail1)
        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode \
           or state.contains(pyatspi.STATE_EDITABLE):
            orca.setLocusOfFocus(event, obj, False)

        default.Script.onCaretMoved(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an an object.

        Arguments:
        - event: the Event
        """

        self._destroyLineCache()
        if not event.source.getState().contains(pyatspi.STATE_EDITABLE):
            if self.inMouseOverObject:
                obj = self.lastMouseOverObject
                while obj and (obj != obj.parent):
                    if self.utilities.isSameObject(event.source, obj):
                        self.restorePreMouseOverContext()
                        break
                    obj = obj.parent

        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        self._destroyLineCache()

        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

        default.Script.onTextInserted(self, event)

    def _getCtrlShiftSelectionsStrings(self):
        return [messages.LINE_SELECTED_DOWN,
                messages.LINE_UNSELECTED_DOWN,
                messages.LINE_SELECTED_UP,
                messages.LINE_UNSELECTED_UP]

    def onTextSelectionChanged(self, event):
        """Called when an object's text selection changes.

        Arguments:
        - event: the Event
        """

        if self.utilities.inFindToolbar():
            self.presentFindResults(event.source, -1)
            self._saveFocusedObjectInfo(orca_state.locusOfFocus)
            return

        if not self.inDocumentContent(orca_state.locusOfFocus) \
           and self.inDocumentContent(event.source):
            return

        text = self.utilities.queryNonEmptyText(event.source)
        char, start, end = text.getTextAtOffset(text.caretOffset, pyatspi.TEXT_BOUNDARY_CHAR)
        if char == self.EMBEDDED_OBJECT_CHARACTER:
            msg = "INFO: Text-selection event ignored: Caret offset is at embedded object"
            debug.println(debug.LEVEL_INFO, msg)
            return

        default.Script.onTextSelectionChanged(self, event)

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if self.findCommandRun:
            self.findCommandRun = False
            self.find()
            return

        if not event.detail1:
            return

        role = event.source.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            orca.setLocusOfFocus(event, event.source)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        try:
            obj = event.source
            role = obj.getRole()
            name = obj.name
        except:
            return
        if role != pyatspi.ROLE_DOCUMENT_FRAME:
             return

        try:
            focusRole = orca_state.locusOfFocus.getRole()
        except:
            focusRole = None

        # The event is for the changing contents of the help frame as the user
        # navigates from topic to topic in the list on the left. Ignore this.
        if focusRole == pyatspi.ROLE_LIST_ITEM \
           and not self.inDocumentContent(orca_state.locusOfFocus):
            return
 
        finishedLoading = False
        if event.detail1:
            self._loadingDocumentContent = True
            message = messages.PAGE_LOADING_START
        elif name:
            message = messages.PAGE_LOADING_END_NAMED % name
            finishedLoading = True
        else:
            message = messages.PAGE_LOADING_END
            finishedLoading = True
 
        if not _settingsManager.getSetting('onlySpeakDisplayedText'):
            self.presentMessage(message)
 
        if not finishedLoading:
            return

        if not self._focusModeIsSticky:
            self._inFocusMode = False

        # Store the document frame otherwise the first time it gains focus (e.g.
        # the first time the user arrows off of a link into non-focusable text),
        # onFocused will start chatting unnecessarily.
        self._currentFrame = obj
 
        # First try to figure out where the caret is on the newly loaded page.
        # If it is on an editable object (e.g., a text entry), then present just
        # that object. Otherwise, force the caret to the top of the page and
        # start a SayAll from that position.
        [obj, characterOffset] = self.getCaretContext()
        atTop = False
        if not obj:
            self.clearCaretContext()
            [obj, characterOffset] = self.getCaretContext()
            atTop = True
        if not obj:
             return
        if not atTop and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            self.clearCaretContext()
            [obj, characterOffset] = self.getCaretContext()
            if not obj:
                return
 
        # For braille, we just show the current line containing the caret. For
        # speech, however, we will start a Say All operation if the caret is in
        # an unfocusable area (e.g., it's not in a text entry area such as
        # Google's search text entry or a link that we just returned to by
        # pressing the back button). Otherwise, we'll just speak the line that
        # the caret is on.
        self.updateBraille(obj)
        if obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            speech.speak(self.speechGenerator.generateSpeech(obj))
        elif not _settingsManager.getSetting('sayAllOnLoad'):
            self.speakContents(
                self.getLineContentsAtOffset(obj, characterOffset))
        elif _settingsManager.getSetting('enableSpeech'):
            self.sayAll(None)

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        if event.any_data is None:
            return

        if not event.type.startswith("object:children-changed:add"):
            return

        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

        child = event.any_data
        try:
            childRole = child.getRole()
        except:
            return

        if childRole == pyatspi.ROLE_ALERT:
            orca.setLocusOfFocus(event, child)
            return

        if childRole == pyatspi.ROLE_DIALOG:
            if self.inDocumentContent(event.source):
                orca.setLocusOfFocus(event, child)
            return

        if self.lastMouseRoutingTime \
           and 0 < time.time() - self.lastMouseRoutingTime < 1:
            utterances = []
            utterances.append(messages.NEW_ITEM_ADDED)
            utterances.extend(
                self.speechGenerator.generateSpeech(child, force=True))
            speech.speak(utterances)
            self.lastMouseOverObject = child
            self.preMouseOverContext = self.getCaretContext()
            return

        default.Script.onChildrenChanged(self, event)

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = True

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            # Reset the live region manager.
            self.liveMngr.reset()
            self._loadingDocumentContent = False
            self._loadingDocumentTime = time.time()

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = False
            self._loadingDocumentTime = time.time()

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """
        if event.source.getRole() == pyatspi.ROLE_FRAME:
            self.liveMngr.flushMessages()

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.inDocumentContent(event.source):
            return

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # during the remainder of the unstable (3.11) development cycle.

        role = event.source.getRole()

        # Unfiled. When a context menu pops up, we seem to get a focus: event,
        # but no object:state-changed:focused event from Gecko.
        if role == pyatspi.ROLE_MENU:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. When the Thunderbird 'do you want to replace this file'
        # attachment dialog pops up, the 'Replace' button emits a focus:
        # event, but we only seem to get the object:state-changed:focused
        # event when it gives up focus.
        if role == pyatspi.ROLE_PUSH_BUTTON:
            orca.setLocusOfFocus(event, event.source)

        # Some of the dialogs used by Thunderbird (and perhaps Firefox?) seem
        # to be using Gtk+ 2, along with its associated focused-event issues.
        # Unfortunately, because Gtk+ 2 doesn't expose a per-object toolkit,
        # we cannot know that a given widget is Gtk+ 2. Therefore, we'll put
        # our Gtk+ 2 toolkit script hacks here as well just to be safe.
        if role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_PASSWORD_TEXT]:
            orca.setLocusOfFocus(event, event.source)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        if not _settingsManager.getSetting('caretNavigationEnabled'):
            default.Script.onFocusedChanged(self, event)
            return

        obj = event.source
        if not self.inDocumentContent(obj):
            default.Script.onFocusedChanged(self, event)
            return

        state = obj.getState()
        if state.contains(pyatspi.STATE_EDITABLE):
            default.Script.onFocusedChanged(self, event)
            return

        role = obj.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            orca.setLocusOfFocus(event, event.source)
            return

        # As the caret moves into a non-focusable element, Gecko emits the
        # signal on the first focusable element in the ancestry.
        rolesToIgnore = pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_PANEL
        if role in rolesToIgnore:
            if self.inDocumentContent():
                return

            contextObj, contextOffset = self.getCaretContext()
            if contextObj:
                orca.setLocusOfFocus(event, contextObj)
                return

        # If we caused this event, we don't want to double-present it.
        if self._lastCommandWasCaretNav:
            msg = "INFO: Focus change event ignored: last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg)
            return

        if self._lastCommandWasStructNav:
            msg = "INFO: Focus change event handled manually: last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg)
            if role != pyatspi.ROLE_LINK:
                self.setCaretContext(event.source, 0)
                orca.setLocusOfFocus(event, event.source)
            return

        default.Script.onFocusedChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # TODO - JD: Once there are separate scripts for the Gecko toolkit
        # and the Firefox browser, the stuff below belongs in the browser
        # script and not in the toolkit script.
 
        try:
            eventRole = event.source.getRole()
            focusedRole = orca_state.locusOfFocus.getRole()
        except:
            default.Script.onShowingChanged(self, event)
            return

        # If an autocomplete appears beneath an entry, we don't want
        # to prevent the user from being able to arrow into it.
        if eventRole == pyatspi.ROLE_WINDOW \
           and focusedRole in [pyatspi.ROLE_ENTRY, pyatspi.ROLE_LIST_ITEM]:
            self._autocompleteVisible = event.detail1
            # If the autocomplete has just appeared, we want to speak
            # its appearance if the user's verbosity level is verbose
            # or if the user forced it to appear with (Alt+)Down Arrow.
            if self._autocompleteVisible:
                level = _settingsManager.getSetting('speechVerbosityLevel')
                speakIt = level == settings.VERBOSITY_LEVEL_VERBOSE
                if not speakIt:
                    eventString, mods = self.utilities.lastKeyAndModifiers()
                    speakIt = eventString == "Down"
                if speakIt:
                    speech.speak(self.speechGenerator.getLocalizedRoleName(
                        event.source, pyatspi.ROLE_AUTOCOMPLETE))
                    return

        default.Script.onShowingChanged(self, event)

    def handleProgressBarUpdate(self, event, obj):
        """Determine whether this progress bar event should be spoken or not.
        For Firefox, we don't want to speak the small "page load" progress
        bar. All other Firefox progress bars get passed onto the parent
        class for handling.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj:  the Accessible progress bar object.
        """

        rolesList = [pyatspi.ROLE_PROGRESS_BAR, \
                     pyatspi.ROLE_STATUS_BAR, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if not self.utilities.hasMatchingHierarchy(event.source, rolesList):
            default.Script.handleProgressBarUpdate(self, event, obj)

    def _useFocusMode(self, obj):
        if self._focusModeIsSticky:
            return True

        if not orca.settings.structNavTriggersFocusMode \
           and self._lastCommandWasStructNav:
            return False

        if not orca.settings.caretNavTriggersFocusMode \
           and self._lastCommandWasCaretNav:
            return False

        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            return False

        if not state.contains(pyatspi.STATE_FOCUSED) \
           and not state.contains(pyatspi.STATE_SELECTED):
            return False

        if state.contains(pyatspi.STATE_EDITABLE) \
           or state.contains(pyatspi.STATE_EXPANDABLE):
            return True

        focusModeRoles = [pyatspi.ROLE_COMBO_BOX,
                          pyatspi.ROLE_ENTRY,
                          pyatspi.ROLE_LIST_BOX,
                          pyatspi.ROLE_LIST_ITEM,
                          pyatspi.ROLE_MENU,
                          pyatspi.ROLE_MENU_ITEM,
                          pyatspi.ROLE_CHECK_MENU_ITEM,
                          pyatspi.ROLE_RADIO_MENU_ITEM,
                          pyatspi.ROLE_PAGE_TAB,
                          pyatspi.ROLE_PASSWORD_TEXT,
                          pyatspi.ROLE_PROGRESS_BAR,
                          pyatspi.ROLE_SLIDER,
                          pyatspi.ROLE_SPIN_BUTTON,
                          pyatspi.ROLE_TOOL_BAR,
                          pyatspi.ROLE_TABLE_CELL,
                          pyatspi.ROLE_TABLE_ROW,
                          pyatspi.ROLE_TABLE,
                          pyatspi.ROLE_TREE_TABLE,
                          pyatspi.ROLE_TREE]

        if role in focusModeRoles:
            return True

        return False

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Called when the object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldFocus: Accessible that is the old focus
        - newFocus: Accessible that is the new focus
        """

        if not newFocus:
            orca_state.noFocusTimeStamp = time.time()
            return

        if self.utilities.inFindToolbar(newFocus):
            self.madeFindAnnouncement = False

        if not self.inDocumentContent(newFocus):
            default.Script.locusOfFocusChanged(self, event, oldFocus, newFocus)
            self._inFocusMode = False
            return

        caretOffset = -1
        if self.utilities.inFindToolbar(oldFocus):
            newFocus, caretOffset = self.getCaretContext()

        text = self.utilities.queryNonEmptyText(newFocus)
        if text and (0 <= text.caretOffset < text.characterCount):
            caretOffset = text.caretOffset

        self.setCaretContext(newFocus, caretOffset)
        default.Script.locusOfFocusChanged(self, event, oldFocus, newFocus)

        if self._focusModeIsSticky:
            return

        if self._useFocusMode(newFocus) != self._inFocusMode:
            self.togglePresentationMode(None)

    def _destroyLineCache(self):
        """Removes all of the stored lines."""

        self.currentLineContents = None
        self.currentAttrs = {}

    def presentLine(self, obj, offset):
        """Presents the current line in speech and in braille.

        Arguments:
        - obj: the Accessible at the caret
        - offset: the offset within obj
        """

        contents = self.getLineContentsAtOffset(obj, offset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakContents(self.currentLineContents)
        self.updateBraille(obj)

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the given object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: update disabled")
            return

        if not self.inDocumentContent() or self._inFocusMode:
            default.Script.updateBraille(self, obj, extraRegion)
            return

        if not obj:
            return

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)

        [focusedObj, focusedOffset] = self.getCaretContext()
        contents = self.getLineContentsAtOffset(focusedObj, focusedOffset)
        if not len(contents):
            return

        contents = self.utilities.filterContentsForPresentation(contents)
        index = self.utilities.findObjectInContents(focusedObj, focusedOffset, contents)
        focusedRegion = None
        lastObj = None
        for i, content in enumerate(contents):
            [obj, startOffset, endOffset, string] = content
            [regions, fRegion] = self.brailleGenerator.generateBraille(
                obj, startOffset=startOffset, endOffset=endOffset)
            if i == index:
                focusedRegion = fRegion

            if line.regions and regions:
                if line.regions[-1].string:
                    lastChar = line.regions[-1].string[-1]
                else:
                    lastChar = ""
                if regions[0].string:
                    nextChar = regions[0].string[0]
                else:
                    nextChar = ""
                if self.utilities.needsSeparator(lastChar, nextChar):
                    self.addToLineAsBrailleRegion(" ", line)

            self.addBrailleRegionsToLine(regions, line)
            lastObj = obj

        if line.regions:
            line.regions[-1].string = line.regions[-1].string.rstrip(" ")

        # TODO - JD: This belongs in the generator.
        if lastObj and lastObj.getRole() != pyatspi.ROLE_HEADING:
            heading = self.utilities.ancestorWithRole(
                lastObj, [pyatspi.ROLE_HEADING], [pyatspi.ROLE_DOCUMENT_FRAME])
            if heading:
                level = self.utilities.headingLevel(heading)
                string = " %s" % object_properties.ROLE_HEADING_LEVEL_BRAILLE % level
                self.addToLineAsBrailleRegion(string, line)

        if extraRegion:
            self.addBrailleRegionToLine(extraRegion, line)

        self.setBrailleFocus(focusedRegion, getLinkMask=False)
        self.refreshBraille(panToCursor=True, getLinkMask=False)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #

        if not self.inDocumentContent() or self.utilities.isEntry(obj):
            default.Script.sayCharacter(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        if characterOffset >= 0:
            self.speakCharacterAtOffset(obj, characterOffset)

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent() or self.utilities.isEntry(obj):
            default.Script.sayWord(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        wordContents = self.utilities.getWordContentsAtOffset(obj, characterOffset)

        [textObj, startOffset, endOffset, word] = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        self.speakContents(wordContents)

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent() or self.utilities.isEntry(obj):
            default.Script.sayLine(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        self.speakContents(self.getLineContentsAtOffset(obj, characterOffset))

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """
        if self.flatReviewContext \
           or not self.inDocumentContent() \
           or not self.isBrailleBeginningShowing():
            default.Script.panBrailleLeft(self, inputEvent, panAmount)
        else:
            self.goPreviousLine(inputEvent)
            while self.panBrailleInDirection(panToLeft=False):
                pass
            self.refreshBraille(False)
        return True

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """
        if self.flatReviewContext \
           or not self.inDocumentContent() \
           or not self.isBrailleEndShowing():
            default.Script.panBrailleRight(self, inputEvent, panAmount)
        elif self.goNextLine(inputEvent):
            while self.panBrailleInDirection(panToLeft=True):
                pass
            self.refreshBraille(False)
        return True

    ####################################################################
    #                                                                  #
    # Utility Methods                                                  #
    #                                                                  #
    ####################################################################

    def inDocumentContent(self, obj=None):
        """Returns True if the given object (defaults to the current
        locus of focus is in the document content).
        """

        if not obj:
            obj = orca_state.locusOfFocus
        try:
            return self.generatorCache['inDocumentContent'][obj]
        except:
            pass

        result = False
        while obj:
            try:
                role = obj.getRole()
            except:
                return False
            if role == pyatspi.ROLE_DOCUMENT_FRAME \
                    or role == pyatspi.ROLE_EMBEDDED:
                result = True
                break
            else:
                obj = obj.parent

        if 'inDocumentContent' not in self.generatorCache:
            self.generatorCache['inDocumentContent'] = {}

        if obj:
            self.generatorCache['inDocumentContent'][obj] = result
            
        return result

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if we should do our own caret navigation.
        """

        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode:
            return False

        if not self.inDocumentContent():
            return False

        if keyboardEvent.event_string in ["Page_Up", "Page_Down"]:
            return False

        if keyboardEvent.modifiers & keybindings.SHIFT_MODIFIER_MASK:
            return False

        if self._loadingDocumentContent:
            return False

        if not orca_state.locusOfFocus:
            return False

        return True

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation.
        This should return False if we're in something like an entry
        or a list.
        """

        if not self.structuralNavigation.enabled or self._inFocusMode:
            return False

        if not self.inDocumentContent():
            return False

        if self._loadingDocumentContent:
            return False

        return True

    def _getAttrDictionary(self, obj):
        if not obj:
            return {}

        try:
            return dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return {}

    def handleAsLiveRegion(self, event):
        """Returns True if the given event (object:children-changed, object:
        text-insert only) should be considered a live region event"""

        if self._loadingDocumentContent \
           or not _settingsManager.getSetting('inferLiveRegions'):
            return False

        attrs = self._getAttrDictionary(event.source)
        if 'container-live' in attrs:
            return True

        return False

    def getChildIndex(self, obj, characterOffset):
        """Given an object that implements accessible text, determine
        the index of the child that is represented by an
        EMBEDDED_OBJECT_CHARACTER at characterOffset in the object's
        accessible text."""

        try:
            hypertext = obj.queryHypertext()
        except NotImplementedError:
            index = -1
        else:
            index = hypertext.getLinkIndex(characterOffset)

        return index

    def isLabellingContents(self, obj, contents):
        """Given and obj and a list of [obj, startOffset, endOffset] tuples,
        determine if obj is labelling anything in the tuples.

        Returns the object being labelled, or None.
        """

        if obj.getRole() != pyatspi.ROLE_LABEL:
            return None

        relationSet = obj.getRelationSet()
        if not relationSet:
            return None

        for relation in relationSet:
            if relation.getRelationType() \
                == pyatspi.RELATION_LABEL_FOR:
                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    for content in contents:
                        if content[0] == target:
                            return target

        return None
 
    def getTopOfFile(self):
        """Returns the object and first caret offset at the top of the
         document frame."""

        documentFrame = self.utilities.documentFrame()
        [obj, offset] = self.findFirstCaretContext(documentFrame, 0)

        return [obj, offset]

    def getBottomOfFile(self):
        """Returns the object and last caret offset at the bottom of the
         document frame."""

        documentFrame = self.utilities.documentFrame()
        text = self.utilities.queryNonEmptyText(documentFrame)
        if text:
            char = text.getText(text.characterCount - 1, text.characterCount)
            if char != self.EMBEDDED_OBJECT_CHARACTER:
                return [documentFrame, text.characterCount - 1]

        obj = self.getLastObject(documentFrame)
        offset = 0

        # If the last object is a link, it may be more efficient to check
        # for text that follows.
        #
        if obj and obj.getRole() == pyatspi.ROLE_LINK:
            text = self.utilities.queryNonEmptyText(obj.parent)
            if text:
                char = text.getText(text.characterCount - 1,
                                    text.characterCount)
                if char != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj.parent, text.characterCount - 1]

        # obj should now be the very last item in the entire document frame
        # and not have children of its own.  Therefore, it should have text.
        # If it doesn't, we don't want to be here.
        #
        text = self.utilities.queryNonEmptyText(obj)
        if text:
            offset = text.characterCount - 1
        else:
            obj = self.findPreviousObject(obj, documentFrame)

        while obj:
            [lastObj, lastOffset] = self.findNextCaretInOrder(obj, offset)
            if not lastObj \
               or self.utilities.isSameObject(lastObj, obj) \
               and (lastOffset == offset):
                break

            [obj, offset] = [lastObj, lastOffset]

        return [obj, offset]

    def getLastObject(self, documentFrame):
        """Returns the last object in the document frame"""

        try:
            lastChild = documentFrame[documentFrame.childCount - 1]
        except:
            lastChild = documentFrame
        while lastChild:
            lastObj = self.findNextObject(lastChild, documentFrame)
            if lastObj and lastObj != lastChild:
                lastChild = lastObj
            else:
                break

        return lastChild

    def getPageSummary(self, obj):
        """Returns the quantity of headings, forms, tables, visited links,
        and unvisited links on the page containing obj.
        """

        docframe = self.utilities.documentFrame()
        col = docframe.queryCollection()
        headings = 0
        forms = 0
        tables = 0
        vlinks = 0
        uvlinks = 0
        percentRead = None

        stateset = pyatspi.StateSet()
        roles = [pyatspi.ROLE_HEADING, pyatspi.ROLE_LINK, pyatspi.ROLE_TABLE,
                 pyatspi.ROLE_FORM]
        rule = col.createMatchRule(stateset.raw(), col.MATCH_NONE,
                                   "", col.MATCH_NONE,
                                   roles, col.MATCH_ANY,
                                   "", col.MATCH_NONE,
                                   False)

        matches = col.getMatches(rule, col.SORT_ORDER_CANONICAL, 0, True)
        col.freeMatchRule(rule)
        for obj in matches:
            role = obj.getRole()
            if role == pyatspi.ROLE_HEADING:
                headings += 1
            elif role == pyatspi.ROLE_FORM:
                forms += 1
            elif role == pyatspi.ROLE_TABLE \
                      and not self.utilities.isLayoutOnly(obj):
                tables += 1
            elif role == pyatspi.ROLE_LINK:
                if obj.getState().contains(pyatspi.STATE_VISITED):
                    vlinks += 1
                else:
                    uvlinks += 1

        return [headings, forms, tables, vlinks, uvlinks, percentRead]

    ####################################################################
    #                                                                  #
    # Methods to find previous and next objects.                       #
    #                                                                  #
    ####################################################################

    def findFirstCaretContext(self, obj, characterOffset):
        """Given an object and a character offset, find the first
        [obj, characterOffset] that is actually presenting something
        on the display.  The reason we do this is that the
        [obj, characterOffset] passed in may actually be pointing
        to an embedded object character.  In those cases, we dig
        into the hierarchy to find the 'real' thing.

        Arguments:
        -obj: an accessible object
        -characterOffset: the offset of the character where to start
        looking for real text

        Returns [obj, characterOffset] that points to real content.
        """

        try:
            role = obj.getRole()
        except:
            return [None, -1]

        if role == pyatspi.ROLE_TABLE and obj.childCount:
            child = obj[0]
            if child.getRole() in [pyatspi.ROLE_CAPTION, pyatspi.ROLE_LIST]:
                obj = child
            else:
                obj = obj.queryTable().getAccessibleAt(0, 0)
            return self.findFirstCaretContext(obj, 0)

        text = self.utilities.queryNonEmptyText(obj)
        if not text:
            return [obj, -1]

        character = text.getText(characterOffset, characterOffset + 1)
        if len(character) == 1 and character != self.EMBEDDED_OBJECT_CHARACTER:
            return [obj, characterOffset]

        try:
            childIndex = self.getChildIndex(obj, characterOffset)
            child = obj[childIndex]

            # Handle bogus empty paragraphs. Bug 677615.
            # Make that bogus empty text objects.
            textRoles = [pyatspi.ROLE_HEADING,
                         pyatspi.ROLE_PARAGRAPH,
                         pyatspi.ROLE_SECTION]
            if child.getRole() in textRoles \
               and not self.utilities.queryNonEmptyText(child):
                return self.findFirstCaretContext(obj, characterOffset + 1)

            return self.findFirstCaretContext(child, 0)

        except:
            return [obj, -1]

        return [obj, characterOffset]

    def findNextCaretInOrder(self, obj=None,
                             startOffset=-1,
                             includeNonText=True):
        """Given an object at a character offset, return the next
        caret context following an in-order traversal rule.

        Arguments:
        - root: the Accessible to start at.  If None, starts at the
        document frame.
        - startOffset: character position in the object text field
        (if it exists) to start at.  Defaults to -1, which means
        start at the beginning - that is, the next character is the
        first character in the object.
        - includeNonText: If False, only land on objects that support the
        accessible text interface; otherwise, include logical leaf
        nodes like check boxes, combo boxes, etc.

        Returns [obj, characterOffset] or [None, -1]
        """

        if not obj:
            obj = self.utilities.documentFrame()

        if not obj or not self.inDocumentContent(obj):
            return [None, -1]

        if obj.getRole() == pyatspi.ROLE_INVALID:
            debug.println(debug.LEVEL_SEVERE, \
                          "findNextCaretInOrder: object is invalid")
            return [None, -1]

        # We do not want to descend objects of certain role types.
        #
        doNotDescend = obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
                       and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                             pyatspi.ROLE_LIST_BOX,
                                             pyatspi.ROLE_LIST,
                                             pyatspi.ROLE_PUSH_BUTTON,
                                             pyatspi.ROLE_TABLE_CELL,
                                             pyatspi.ROLE_TOGGLE_BUTTON,
                                             pyatspi.ROLE_TOOL_BAR]

        isHidden = self.utilities.isHidden(obj)
        isOffScreenLabel = self.utilities.isOffScreenLabel(obj, startOffset)
        skip = isHidden or isOffScreenLabel

        text = self.utilities.queryNonEmptyText(obj)
        if text and not skip:
            unicodeText = self.utilities.unicodeText(obj)

            # Delete the final space character if we find it.  Otherwise,
            # we'll arrow to it.  (We can't just strip the string otherwise
            # we skip over blank lines that one could otherwise arrow to.)
            #
            if len(unicodeText) > 1 and unicodeText[-1] == " ":
                unicodeText = unicodeText[0:len(unicodeText) - 1]

            nextOffset = startOffset + 1
            while 0 <= nextOffset < len(unicodeText):
                if unicodeText[nextOffset] != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, nextOffset]
                elif obj.childCount:
                    try:
                        child = obj[self.getChildIndex(obj, nextOffset)]
                    except:
                        break
                    if child:
                        return self.findNextCaretInOrder(child,
                                                         -1,
                                                       includeNonText)
                    else:
                        nextOffset += 1
                else:
                    nextOffset += 1

        # If this is a list or combo box in an HTML form, we don't want
        # to place the caret inside the list, but rather treat the list
        # as a single object.  Otherwise, if it has children, look there.
        #
        elif obj.childCount and obj[0] and not doNotDescend and not skip:
            try:
                return self.findNextCaretInOrder(obj[0],
                                                 -1,
                                                 includeNonText)
            except:
                pass

        elif includeNonText and startOffset < 0 and not skip:
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.utilities.documentFrame()
        if self.utilities.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = \
                self.utilities.characterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findNextCaretInOrder(obj.parent,
                                                 characterOffsetInParent,
                                                 includeNonText)
            else:
                index = obj.getIndexInParent() + 1
                if index < obj.parent.childCount:
                    try:
                        return self.findNextCaretInOrder(
                            obj.parent[index],
                            -1,
                            includeNonText)
                    except:
                        pass
            obj = obj.parent

        return [None, -1]

    def findPreviousCaretInOrder(self,
                                 obj=None,
                                 startOffset=-1,
                                 includeNonText=True):
        """Given an object an a character offset, return the previous
        caret context following an in order traversal rule.

        Arguments:
        - root: the Accessible to start at.  If None, starts at the
        document frame.
        - startOffset: character position in the object text field
        (if it exists) to start at.  Defaults to -1, which means
        start at the end - that is, the previous character is the
        last character of the object.

        Returns [obj, characterOffset] or [None, -1]
        """

        if not obj:
            obj = self.utilities.documentFrame()

        if not obj or not self.inDocumentContent(obj):
            return [None, -1]

        if obj.getRole() == pyatspi.ROLE_INVALID:
            debug.println(debug.LEVEL_SEVERE, \
                          "findPreviousCaretInOrder: object is invalid")
            return [None, -1]

        # We do not want to descend objects of certain role types.
        #
        doNotDescend = obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
                       and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                             pyatspi.ROLE_LIST_BOX,
                                             pyatspi.ROLE_LIST,
                                             pyatspi.ROLE_PUSH_BUTTON,
                                             pyatspi.ROLE_TABLE_CELL,
                                             pyatspi.ROLE_TOGGLE_BUTTON,
                                             pyatspi.ROLE_TOOL_BAR]

        isHidden = self.utilities.isHidden(obj)
        isOffScreenLabel = self.utilities.isOffScreenLabel(obj, startOffset)
        skip = isHidden or isOffScreenLabel

        text = self.utilities.queryNonEmptyText(obj)
        if text and not skip:
            unicodeText = self.utilities.unicodeText(obj)

            # Delete the final space character if we find it.  Otherwise,
            # we'll arrow to it.  (We can't just strip the string otherwise
            # we skip over blank lines that one could otherwise arrow to.)
            #
            if len(unicodeText) > 1 and unicodeText[-1] == " ":
                unicodeText = unicodeText[0:len(unicodeText) - 1]

            if (startOffset == -1) or (startOffset > len(unicodeText)):
                startOffset = len(unicodeText)
            previousOffset = startOffset - 1
            while previousOffset >= 0:
                if unicodeText[previousOffset] \
                    != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, previousOffset]
                elif obj.childCount:
                    child = obj[self.getChildIndex(obj, previousOffset)]
                    if child:
                        return self.findPreviousCaretInOrder(child,
                                                             -1,
                                                             includeNonText)
                    else:
                        previousOffset -= 1
                else:
                    previousOffset -= 1

        # If this is a list or combo box in an HTML form, we don't want
        # to place the caret inside the list, but rather treat the list
        # as a single object.  Otherwise, if it has children, look there.
        #
        elif obj.childCount and obj[obj.childCount - 1] and not doNotDescend \
             and not skip:
            try:
                return self.findPreviousCaretInOrder(
                    obj[obj.childCount - 1],
                    -1,
                    includeNonText)
            except:
                pass

        elif includeNonText and startOffset < 0 and not skip:
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.utilities.documentFrame()
        if self.utilities.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = \
                self.utilities.characterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findPreviousCaretInOrder(obj.parent,
                                                     characterOffsetInParent,
                                                     includeNonText)
            else:
                index = obj.getIndexInParent() - 1
                if index >= 0:
                    try:
                        return self.findPreviousCaretInOrder(
                            obj.parent[index],
                            -1,
                            includeNonText)
                    except:
                        pass
            obj = obj.parent

        return [None, -1]

    def findPreviousObject(self, obj, documentFrame):
        """Finds the object prior to this one, where the tree we're
        dealing with is a DOM and 'prior' means the previous object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        """

        previousObj = None
        characterOffset = 0

        # If the object is the document frame, the previous object is
        # the one that follows us relative to our offset.
        #
        if self.utilities.isSameObject(obj, documentFrame):
            [obj, characterOffset] = self.getCaretContext()

        if not obj:
            return None

        index = obj.getIndexInParent() - 1
        if (index < 0):
            if not self.utilities.isSameObject(obj, documentFrame):
                previousObj = obj.parent
            else:
                # We're likely at the very end of the document
                # frame.
                previousObj = self.getLastObject(documentFrame)
        else:
            # [[[TODO: HACK - WDW defensive programming because Gecko
            # ally hierarchies are not always working.  Objects say
            # they have children, but these children don't exist when
            # we go to get them.  So...we'll just keep going backwards
            # until we find a real child that we can work with.]]]
            #
            while not isinstance(previousObj,
                                 pyatspi.Accessibility.Accessible) \
                and index >= 0:
                previousObj = obj.parent[index]
                index -= 1

            # Now that we're at a child we can work with, we need to
            # look at it further.  It could be the root of a hierarchy.
            # In that case, the last child in this hierarchy is what
            # we want.  So, we dive down the 'right hand side' of the
            # tree to get there.
            #
            # [[[TODO: HACK - WDW we need to be defensive because of
            # Gecko's broken a11y hierarchies, so we make this much
            # more complex than it really has to be.]]]
            #
            if not previousObj:
                if not self.utilities.isSameObject(obj, documentFrame):
                    previousObj = obj.parent
                else:
                    previousObj = obj

            role = previousObj.getRole()
            if role == pyatspi.ROLE_MENU_ITEM:
                return previousObj.parent.parent
            elif role == pyatspi.ROLE_LIST_ITEM:
                parent = previousObj.parent
                if parent.getState().contains(pyatspi.STATE_FOCUSABLE):
                    return parent

            while previousObj.childCount:
                role = previousObj.getRole()
                state = previousObj.getState()
                if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_LIST_BOX, pyatspi.ROLE_MENU]:
                    break
                elif role == pyatspi.ROLE_LIST \
                     and state.contains(pyatspi.STATE_FOCUSABLE):
                    break
                elif previousObj.childCount > 1000:
                    break

                index = previousObj.childCount - 1
                while index >= 0:
                    child = previousObj[index]
                    childOffset = self.utilities.characterOffsetInParent(child)
                    if isinstance(child, pyatspi.Accessibility.Accessible) \
                       and not (self.utilities.isSameObject(
                            previousObj, documentFrame) \
                        and childOffset > characterOffset):
                        previousObj = child
                        break
                    else:
                        index -= 1
                if index < 0:
                    break

        if self.utilities.isSameObject(previousObj, documentFrame):
            previousObj = None

        return previousObj

    def findNextObject(self, obj, documentFrame):
        """Finds the object after to this one, where the tree we're
        dealing with is a DOM and 'next' means the next object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        """

        nextObj = None
        characterOffset = 0

        # If the object is the document frame, the next object is
        # the one that follows us relative to our offset.
        #
        if self.utilities.isSameObject(obj, documentFrame):
            [obj, characterOffset] = self.getCaretContext()

        if not obj:
            return None

        # If the object has children, we'll choose the first one,
        # unless it's a combo box or a focusable HTML list.
        #
        # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
        # a bit of a challenge.]]]
        #
        role = obj.getRole()
        if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_LIST_BOX, pyatspi.ROLE_MENU]:
            descend = False
        elif role == pyatspi.ROLE_LIST \
            and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            descend = False
        elif obj.childCount > 1000:
            descend = False
        else:
            descend = True

        index = 0
        while descend and index < obj.childCount:
            child = obj[index]
            # bandaid for Gecko broken hierarchy
            if child is None:
                index += 1
                continue
            childOffset = self.utilities.characterOffsetInParent(child)
            if isinstance(child, pyatspi.Accessibility.Accessible) \
               and not (self.utilities.isSameObject(obj, documentFrame) \
                        and childOffset < characterOffset):
                nextObj = child
                break
            else:
                index += 1

        # Otherwise, we'll look to the next sibling.
        #
        # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
        # a bit of a challenge.]]]
        #
        if not nextObj and obj.getIndexInParent() != -1:
            index = obj.getIndexInParent() + 1
            while index < obj.parent.childCount:
                child = obj.parent[index]
                if isinstance(child, pyatspi.Accessibility.Accessible):
                    nextObj = child
                    break
                else:
                    index += 1

        # If there is no next sibling, we'll move upwards.
        #
        candidate = obj
        while not nextObj:
            # Go up until we find a parent that might have a sibling to
            # the right for us.
            #
            while candidate and candidate.parent \
                  and candidate.getIndexInParent() >= \
                      candidate.parent.childCount - 1 \
                  and not self.utilities.isSameObject(candidate, documentFrame):
                candidate = candidate.parent

            # Now...let's get the sibling.
            #
            # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
            # a bit of a challenge.]]]
            #
            if not self.utilities.isSameObject(candidate, documentFrame):
                index = candidate.getIndexInParent() + 1
                while index < candidate.parent.childCount:
                    child = candidate.parent[index]
                    if isinstance(child, pyatspi.Accessibility.Accessible):
                        nextObj = child
                        break
                    else:
                        index += 1

                # We've exhausted trying to get all the children, but
                # Gecko's broken hierarchy has failed us for all of
                # them.  So, we need to go higher.
                #
                candidate = candidate.parent
            else:
                break

        return nextObj

    ####################################################################
    #                                                                  #
    # Methods to get information about current object.                 #
    #                                                                  #
    ####################################################################

    def clearCaretContext(self):
        """Deletes all knowledge of a character context for the current
        document frame."""

        documentFrame = self.utilities.documentFrame()
        self._destroyLineCache()
        try:
            del self._documentFrameCaretContext[hash(documentFrame)]
        except:
            pass

    def setCaretContext(self, obj=None, characterOffset=-1):
        """Sets the caret context for the current document frame."""

        # We keep a context for each page tab shown.
        # [[[TODO: WDW - probably should figure out how to destroy
        # these contexts when a tab is killed.]]]
        #
        documentFrame = self.utilities.documentFrame()

        if not documentFrame:
            return

        self._documentFrameCaretContext[hash(documentFrame)] = \
            [obj, characterOffset]

    def getTextLineAtCaret(self, obj, offset=None):
        """Gets the portion of the line of text where the caret (or optional
        offset) is. This is an override to accomodate the intricities of our
        caret navigation management and to deal with bogus line information
        being returned by Gecko when using getTextAtOffset.

        Argument:
        - obj: an Accessible object that implements the AccessibleText
          interface
        - offset: an optional caret offset to use.

        Returns the [string, caretOffset, startOffset] for the line of text
        where the caret is.
        """

        if self._inFocusMode or not self.inDocumentContent(obj) \
           or self.utilities.isEntry(obj) \
           or self.utilities.isPasswordText(obj):
            return default.Script.getTextLineAtCaret(self, obj, offset)

        if offset == None:
            try:
                offset = max(0, obj.queryText().caretOffset)
            except:
                offset = 0

        contextObj, contextOffset = self.getCaretContext()
        if self.utilities.isSameObject(contextObj, obj):
            caretOffset = contextOffset
        else:
            caretOffset = offset

        contents = self.getLineContentsAtOffset(obj, offset)
        contents = list(filter(lambda x: x[0] == obj, contents))
        if len(contents) == 1:
            index = 0
        else:
            index = self.utilities.findObjectInContents(obj, offset, contents)

        if index > -1:
            candidate, startOffset, endOffset, string = contents[index]
            if string.find(self.EMBEDDED_OBJECT_CHARACTER) == -1:
                return string, caretOffset, startOffset

        return '', 0, 0

    def searchForCaretLocation(self, acc):
        """Attempts to locate the caret on the page independent of our
        caret context. This functionality is needed when a page loads
        and the URL is for a fragment (anchor, id, named object) within
        that page.

        Arguments:
        - acc: The top-level accessible in which we suspect to find the
          caret (most likely the document frame).

        Returns the [obj, caretOffset] containing the caret if it can
        be determined. Otherwise [None, -1] is returned.
        """

        context = [None, -1]
        while acc:
            try:
                offset = acc.queryText().caretOffset
            except:
                acc = None
            else:
                context = [acc, offset]
                childIndex = self.getChildIndex(acc, offset)
                if childIndex >= 0 and acc.childCount:
                    acc = acc[childIndex]
                else:
                    break

        return context

    def getCaretContext(self, includeNonText=True):
        """Returns the current [obj, caretOffset] if defined.  If not,
        it returns the first [obj, caretOffset] found by an in order
        traversal from the beginning of the document."""

        # We keep a context for each page tab shown.
        # [[[TODO: WDW - probably should figure out how to destroy
        # these contexts when a tab is killed.]]]
        #
        documentFrame = self.utilities.documentFrame()

        if not documentFrame:
            return [None, -1]

        try:
            return self._documentFrameCaretContext[hash(documentFrame)]
        except:
            # If we don't have a context, we should attempt to see if we
            # can find the caret first. Failing that, we'll start at the
            # top.
            #
            [obj, caretOffset] = self.searchForCaretLocation(documentFrame)
            self._documentFrameCaretContext[hash(documentFrame)] = \
                self.findNextCaretInOrder(obj,
                                          max(-1, caretOffset - 1),
                                          includeNonText)

        [obj, caretOffset] = \
            self._documentFrameCaretContext[hash(documentFrame)]

        return [obj, caretOffset]

    def getCharacterAtOffset(self, obj, characterOffset):
        """Returns the character at the given characterOffset in the
        given object or None if the object does not implement the
        accessible text specialization.
        """

        try:
            unicodeText = self.utilities.unicodeText(obj)
            return unicodeText[characterOffset]
        except:
            return ""

    def getLineContentsAtOffset(self, obj, offset):
        if not obj:
            return []

        if self.utilities.findObjectInContents(obj, offset, self.currentLineContents) == -1:
            self.currentLineContents = self.utilities.getLineContentsAtOffset(
                obj, offset, _settingsManager.getSetting('layoutMode'))

        return self.currentLineContents

    def getObjectContentsAtOffset(self, obj, characterOffset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset, string] tuple.  The list is 
        created via an in-order traversal of the document contents 
        starting and stopping at the given object.
        """

        return self.utilities.getObjectsFromEOCs(obj, characterOffset)

    ####################################################################
    #                                                                  #
    # Methods to speak current objects.                                #
    #                                                                  #
    ####################################################################

    def getUtterancesFromContents(self, contents, eliminatePauses=False):
        """Returns a list of [text, acss] tuples based upon the list
        of [obj, startOffset, endOffset, string] tuples passed in.

        Arguments:
        -contents: a list of [obj, startOffset, endOffset, string] tuples
        """

        if not len(contents):
            return []

        utterances = []
        contents = self.utilities.filterContentsForPresentation(contents)
        lastObj = None
        for content in contents:
            [obj, startOffset, endOffset, string] = content
            utterance = self.speechGenerator.generateSpeech(
                obj, startOffset=startOffset, endOffset=endOffset)
            if eliminatePauses:
                utterance = list(filter(lambda x: not isinstance(x, Pause), utterance))
            if utterance and utterance[0]:
                utterances.append(utterance)
            lastObj = obj

        # TODO - JD: This belongs in the generator.
        if lastObj and lastObj.getRole() != pyatspi.ROLE_HEADING:
            heading = self.utilities.ancestorWithRole(
                lastObj, [pyatspi.ROLE_HEADING], [pyatspi.ROLE_DOCUMENT_FRAME])
            if heading:
                utterance = self.speechGenerator.getRoleName(heading)
                utterances.append(utterance)

        if not utterances:
            if eliminatePauses:
                string = ""
            else:
                string = messages.BLANK
            utterances = [string, self.voices[settings.DEFAULT_VOICE]]

        return utterances

    def speakContents(self, contents):
        """Speaks each string in contents using the associated voice/acss"""

        speech.speak(self.getUtterancesFromContents(contents))

    def speakCharacterAtOffset(self, obj, characterOffset):
        """Speaks the character at the given characterOffset in the
        given object."""
        character = self.getCharacterAtOffset(obj, characterOffset)
        self.speakMisspelledIndicator(obj, characterOffset)
        if obj:
            if character and character != self.EMBEDDED_OBJECT_CHARACTER:
                self.speakCharacter(character)
            elif not self.utilities.isEntry(obj):
                # We won't have a character if we move to the end of an
                # entry (in which case we're not on a character and therefore
                # have nothing to say), or when we hit a component with no
                # text (e.g. checkboxes) or reset the caret to the parent's
                # characterOffset (lists).  In these latter cases, we'll just
                # speak the entire component.
                #
                utterances = self.speechGenerator.generateSpeech(obj)
                speech.speak(utterances)

    ####################################################################
    #                                                                  #
    # Methods to navigate to previous and next objects.                #
    #                                                                  #
    ####################################################################

    def setCaretPosition(self, obj, characterOffset):
        """Sets the caret position to the given character offset in the
        given object.
        """

        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        self.setCaretContext(obj, characterOffset)
        if self._focusModeIsSticky:
            return

        try:
            state = obj.getState()
        except:
            return

        orca.setLocusOfFocus(None, obj, notifyScript=False)
        if state.contains(pyatspi.STATE_FOCUSABLE):
            obj.queryComponent().grabFocus()

        text = self.utilities.queryNonEmptyText(obj)
        if text:
            text.setCaretOffset(characterOffset)

        if self._useFocusMode(obj) != self._inFocusMode:
            self.togglePresentationMode(None)

    def moveToMouseOver(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the mouse over which has just appeared.
        """

        if not self.lastMouseOverObject:
            self.presentMessage(messages.MOUSE_OVER_NOT_FOUND)
            return

        if not self.inMouseOverObject:
            obj = self.lastMouseOverObject
            offset = 0
            if obj and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                [obj, offset] = self.findFirstCaretContext(obj, offset)

            if obj and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                obj.queryComponent().grabFocus()
            elif obj:
                contents = self.getObjectContentsAtOffset(obj, offset)
                # If we don't have anything to say, let's try one more
                # time.
                #
                if len(contents) == 1 and not contents[0][3].strip():
                    [obj, offset] = self.findNextCaretInOrder(obj, offset)
                    contents = self.getObjectContentsAtOffset(obj, offset)
                self.setCaretPosition(obj, offset)
                self.speakContents(contents)
                self.updateBraille(obj)
            self.inMouseOverObject = True
        else:
            # Route the mouse pointer where it was before both to "clean up
            # after ourselves" and also to get the mouse over object to go
            # away.
            #
            x, y = self.oldMouseCoordinates
            eventsynthesizer.routeToPoint(x, y)
            self.restorePreMouseOverContext()

    def restorePreMouseOverContext(self):
        """Cleans things up after a mouse-over object has been hidden."""

        obj, offset = self.preMouseOverContext
        if obj and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            [obj, offset] = self.findFirstCaretContext(obj, offset)

        if obj and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            obj.queryComponent().grabFocus()
        elif obj:
            self.setCaretPosition(obj, offset)
            self.speakContents(self.getObjectContentsAtOffset(obj, offset))
            self.updateBraille(obj)
        self.inMouseOverObject = False
        self.lastMouseOverObject = None

    def goNextCharacter(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the document window.
        """
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break

        if not obj:
            [obj, characterOffset] = self.getBottomOfFile()
        else:
            self.speakCharacterAtOffset(obj, characterOffset)

        self.setCaretPosition(obj, characterOffset)
        self.updateBraille(obj)

    def goPreviousCharacter(self, inputEvent):
        """Positions the caret offset to the previous character or object
        in the document window.
        """
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.findPreviousCaretInOrder(
                obj, characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break

        if not obj:
            [obj, characterOffset] = self.getTopOfFile()
        else:
            self.speakCharacterAtOffset(obj, characterOffset)

        self.setCaretPosition(obj, characterOffset)
        self.updateBraille(obj)

    def goPreviousWord(self, inputEvent):
        """Positions the caret offset to beginning of the previous
        word or object in the document window.
        """

        [obj, characterOffset] = self.getCaretContext()

        # Make sure we have a word.
        #
        [obj, characterOffset] = \
            self.findPreviousCaretInOrder(obj, characterOffset)

        contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
        if not len(contents):
            return

        [obj, startOffset, endOffset, string] = contents[0]
        if len(contents) == 1 \
           and endOffset - startOffset == 1 \
           and self.getCharacterAtOffset(obj, startOffset) == " ":
            # Our "word" is just a space. This can happen if the previous
            # word was a mark of punctuation surrounded by whitespace (e.g.
            # " | ").
            #
            [obj, characterOffset] = \
                self.findPreviousCaretInOrder(obj, startOffset)
            contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
            if len(contents):
                [obj, startOffset, endOffset, string] = contents[0]

        self.setCaretPosition(obj, startOffset)
        self.updateBraille(obj)
        self.speakMisspelledIndicator(obj, startOffset)
        self.speakContents(contents)

    def goNextWord(self, inputEvent):
        """Positions the caret offset to the end of next word or object
        in the document window.
        """

        [obj, characterOffset] = self.getCaretContext()

        # Make sure we have a word.
        #
        characterOffset = max(0, characterOffset)
        [obj, characterOffset] = \
            self.findNextCaretInOrder(obj, characterOffset)

        contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
        if not (len(contents) and contents[-1][2]):
            return

        [obj, startOffset, endOffset, string] = contents[-1]
        if string and string[-1].isspace():
            endOffset -= 1
        self.setCaretPosition(obj, endOffset)
        self.updateBraille(obj)
        self.speakMisspelledIndicator(obj, startOffset)
        self.speakContents(contents)

    def goPreviousLine(self, inputEvent):
        """Positions the caret offset at the previous line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        [obj, characterOffset] = self.getCaretContext()
        thisLine = self.getLineContentsAtOffset(obj, characterOffset)
        if not thisLine and thisLine[0]:
            return False

        startObj, startOffset = thisLine[0][0], thisLine[0][1]
        prevObj, prevOffset = self.findPreviousCaretInOrder(startObj, startOffset)
        if prevObj == startObj:
            prevObj, prevOffset = self.findPreviousCaretInOrder(prevObj, prevOffset)

        if not prevObj:
            return False

        prevLine = self.getLineContentsAtOffset(prevObj, prevOffset)
        if prevLine:
            prevObj, prevOffset = prevLine[0][0], prevLine[0][1]

        [obj, caretOffset] = self.findFirstCaretContext(prevObj, prevOffset)
        self.setCaretPosition(obj, caretOffset)
        self.presentLine(prevObj, prevOffset)

        return True

    def goNextLine(self, inputEvent):
        """Positions the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        [obj, characterOffset] = self.getCaretContext()
        thisLine = self.getLineContentsAtOffset(obj, characterOffset)
        if not thisLine and thisLine[0]:
            return False

        lastObj, lastOffset = thisLine[-1][0], thisLine[-1][2]
        nextObj, nextOffset = self.findNextCaretInOrder(lastObj, lastOffset - 1)
        if nextObj and self.getCharacterAtOffset(nextObj, nextOffset).isspace():
            nextObj, nextOffset = self.findNextCaretInOrder(nextObj, nextOffset)

        if not nextObj:
            return False

        nextLine = self.getLineContentsAtOffset(nextObj, nextOffset)
        if nextLine:
            nextObj, nextOffset = nextLine[0][0], nextLine[0][1]

        [obj, caretOffset] = self.findFirstCaretContext(nextObj, nextOffset)
        self.setCaretPosition(obj, caretOffset)
        self.presentLine(nextObj, nextOffset)

        return True

    def goBeginningOfLine(self, inputEvent):
        """Positions the caret offset at the beginning of the line."""

        [obj, characterOffset] = self.getCaretContext()
        line = self.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = self.findFirstCaretContext(line[0][0], line[0][1])
        self.setCaretPosition(obj, characterOffset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goEndOfLine(self, inputEvent):
        """Positions the caret offset at the end of the line."""

        [obj, characterOffset] = self.getCaretContext()
        line = self.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = line[-1][0], line[-1][2] - 1
        self.setCaretPosition(obj, characterOffset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goTopOfFile(self, inputEvent):
        """Positions the caret offset at the beginning of the document."""

        [obj, characterOffset] = self.getTopOfFile()
        self.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def goBottomOfFile(self, inputEvent):
        """Positions the caret offset at the end of the document."""

        [obj, characterOffset] = self.getBottomOfFile()
        self.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def advanceLivePoliteness(self, inputEvent):
        """Advances live region politeness level."""
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.advancePoliteness(orca_state.locusOfFocus)
        else:
            self.presentMessage(messages.LIVE_REGIONS_OFF)

    def monitorLiveRegions(self, inputEvent):
        if not _settingsManager.getSetting('inferLiveRegions'):
            _settingsManager.setSetting('inferLiveRegions', True)
            self.presentMessage(messages.LIVE_REGIONS_MONITORING_ON)
        else:
            _settingsManager.setSetting('inferLiveRegions', False)
            self.liveMngr.flushMessages()
            self.presentMessage(messages.LIVE_REGIONS_MONITORING_OFF)

    def setLivePolitenessOff(self, inputEvent):
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.setLivePolitenessOff()
        else:
            self.presentMessage(messages.LIVE_REGIONS_OFF)

    def reviewLiveAnnouncement(self, inputEvent):
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.reviewLiveAnnouncement( \
                                    int(inputEvent.event_string[1:]))
        else:
            self.presentMessage(messages.LIVE_REGIONS_OFF)

    def enableStickyFocusMode(self, inputEvent):
        self._inFocusMode = True
        self._focusModeIsSticky = True
        self.presentMessage(messages.MODE_FOCUS_IS_STICKY)

    def togglePresentationMode(self, inputEvent):
        if self._inFocusMode:
            [obj, characterOffset] = self.getCaretContext()
            try:
                parentRole = obj.parent.getRole()
            except:
                parentRole = None
            if parentRole == pyatspi.ROLE_LIST_BOX:
                self.setCaretContext(obj.parent, -1)
            elif parentRole == pyatspi.ROLE_MENU:
                self.setCaretContext(obj.parent.parent, -1)

            self.presentMessage(messages.MODE_BROWSE)
        else:
            self.presentMessage(messages.MODE_FOCUS)
        self._inFocusMode = not self._inFocusMode
        self._focusModeIsSticky = False

    def toggleCaretNavigation(self, inputEvent):
        """Toggles between Firefox native and Orca caret navigation."""

        if _settingsManager.getSetting('caretNavigationEnabled'):
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.removeByHandler(keyBinding.handler)
            _settingsManager.setSetting('caretNavigationEnabled', False)
            string = messages.CARET_CONTROL_GECKO
        else:
            _settingsManager.setSetting('caretNavigationEnabled', True)
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.add(keyBinding)
            string = messages.CARET_CONTROL_ORCA

        debug.println(debug.LEVEL_CONFIGURATION, string)
        self.presentMessage(string)

    def speakWordUnderMouse(self, acc):
        """Determine if the speak-word-under-mouse capability applies to
        the given accessible.

        Arguments:
        - acc: Accessible to test.

        Returns True if this accessible should provide the single word.
        """
        if self.inDocumentContent(acc):
            try:
                ai = acc.queryAction()
            except NotImplementedError:
                return True
        default.Script.speakWordUnderMouse(self, acc)
