# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
# Copyright 2014-2015 Igalia, S.L.
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
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

from gi.repository import Gtk
import pyatspi
import time

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
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech as speech
import orca.speechserver as speechserver

from . import keymaps
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .bookmarks import GeckoBookmarks
from .structural_navigation import GeckoStructuralNavigation
from .script_utilities import Utilities
from .tutorial_generator import TutorialGenerator

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
        self.layoutModeCheckButton = None

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

        if _settingsManager.getSetting('caretNavigationEnabled') == None:
            _settingsManager.setSetting('caretNavigationEnabled', True)
        if _settingsManager.getSetting('sayAllOnLoad') == None:
            _settingsManager.setSetting('sayAllOnLoad', True)

        # We keep track of whether we're currently in the process of
        # loading a page.
        #
        self._loadingDocumentContent = False

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
        self._madeFindAnnouncement = False

        # For really large objects, a call to getAttributes can take up to
        # two seconds! This is a Firefox bug. We'll try to improve things
        # by storing attributes.
        #
        self.currentAttrs = {}

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
        self._lastCommandWasMouseButton = False

        self._sayAllContents = []

        # See bug 665522 - comment 5 regarding children. We're also seeing
        # stale names in both Gecko and other toolkits.
        app.setCacheMask(
            pyatspi.cache.DEFAULT ^ pyatspi.cache.CHILDREN ^ pyatspi.cache.NAME)

    def deactivate(self):
        """Called when this script is deactivated."""

        self._sayAllContents = []
        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._loadingDocumentContent = False
        self._madeFindAnnouncement = False
        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = False
        self._lastMouseOverObject = None
        self._preMouseOverContext = None, -1
        self._inMouseOverObject = False
        self.utilities.clearCachedObjects()

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

    def getTutorialGenerator(self):
        """Returns the tutorial generator for this script."""
        return TutorialGenerator(self)

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

    def getLiveRegionManager(self):
        """Returns the live region support for this script."""

        return liveregions.LiveRegionManager(self)

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

        self.inputEventHandlers.update(self.liveRegionManager.inputEventHandlers)

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

        if _settingsManager.getSetting('caretNavigationEnabled'):
            for keyBinding in self.__getArrowBindings().keyBindings:
                keyBindings.add(keyBinding)

        bindings = self.structuralNavigation.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        liveRegionBindings = self.liveRegionManager.keyBindings
        for keyBinding in liveRegionBindings.keyBindings:
            keyBindings.add(keyBinding)

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers.get("togglePresentationModeHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers.get("enableStickyFocusModeHandler"),
                2))

        layout = _settingsManager.getSetting('keyboardLayout')
        if layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            key = "KP_Multiply"
        else:
            key = "0"

        keyBindings.add(
            keybindings.KeyBinding(
                key,
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers.get("moveToMouseOverHandler")))

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

        label = guilabels.CONTENT_LAYOUT_MODE
        value = _settingsManager.getSetting('layoutMode')
        self.layoutModeCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.layoutModeCheckButton.set_active(value)
        generalGrid.attach(self.layoutModeCheckButton, 0, 5, 1, 1)

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
            'layoutMode': self.layoutModeCheckButton.get_active(),
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
                self._lastCommandWasMouseButton = False
            elif handler and handler.function in self.structuralNavigation.functions:
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
                self._lastCommandWasMouseButton = False
            elif handler and handler.function in self.liveRegionManager.functions:
                # This is temporary.
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
                self._lastCommandWasMouseButton = False
            else:
                consumes = handler != None
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = False
                self._lastCommandWasMouseButton = False
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                consumes = self.useCaretNavigationModel(keyboardEvent)
                self._lastCommandWasCaretNav = consumes
                self._lastCommandWasStructNav = False
                self._lastCommandWasMouseButton = False
            elif handler and handler.function in self.structuralNavigation.functions:
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
                self._lastCommandWasMouseButton = False
            elif handler and handler.function in self.liveRegionManager.functions:
                # This is temporary.
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
                self._lastCommandWasMouseButton = False
            else:
                consumes = handler != None
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = False
                self._lastCommandWasMouseButton = False
        return consumes

    # TODO - JD: This needs to be moved out of the scripts.
    def textLines(self, obj, offset=None):
        """Creates a generator that can be used to iterate document content."""

        if not self.utilities.inDocumentContent():
            super().textLines(obj, offset)
            return

        self._sayAllIsInterrupted = False

        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
        sayAllBySentence = sayAllStyle == settings.SAYALL_STYLE_SENTENCE
        if offset == None:
            obj, characterOffset = self.utilities.getCaretContext()
        else:
            characterOffset = offset

        self._inSayAll = True
        done = False
        while not done:
            if sayAllBySentence:
                contents = self.utilities.getSentenceContentsAtOffset(obj, characterOffset)
            else:
                contents = self.utilities.getLineContentsAtOffset(obj, characterOffset)
            self._sayAllContents = contents
            for content in contents:
                obj, startOffset, endOffset, text = content
                utterances = self.speechGenerator.generateContents([content], eliminatePauses=True)

                # TODO - JD: This is sad, but it's better than the old, broken
                # clumpUtterances(). We really need to fix the speechservers'
                # SayAll support. In the meantime, the generators should be
                # providing one ACSS per string.
                elements = list(filter(lambda x: isinstance(x, str), utterances[0]))
                voices = list(filter(lambda x: isinstance(x, ACSS), utterances[0]))
                if len(elements) != len(voices):
                    continue

                for i, element in enumerate(elements):
                    context = speechserver.SayAllContext(
                        obj, element, startOffset, endOffset)
                    self._sayAllContexts.append(context)
                    yield [context, voices[i]]

            lastObj, lastOffset = contents[-1][0], contents[-1][2]
            obj, characterOffset = self.utilities.findNextCaretInOrder(lastObj, lastOffset - 1)
            if (obj, characterOffset) == (lastObj, lastOffset):
                obj, characterOffset = self.utilities.findNextCaretInOrder(lastObj, lastOffset)

            done = (obj == None)

        self._inSayAll = False
        self._sayAllContents = []
        self._sayAllContexts = []

    def presentFindResults(self, obj, offset):
        """Updates the context and presents the find results if appropriate."""

        text = self.utilities.queryNonEmptyText(obj)
        if not (text and text.getNSelections()):
            return

        context = self.utilities.getCaretContext(documentFrame=None)

        start, end = text.getSelection(0)
        offset = max(offset, start)
        self.utilities.setCaretContext(obj, offset, documentFrame=None)
        if end - start < _settingsManager.getSetting('findResultsMinimumLength'):
            return

        verbosity = _settingsManager.getSetting('findResultsVerbosity')
        if verbosity == settings.FIND_SPEAK_NONE:
            return

        if self._madeFindAnnouncement \
           and verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED \
           and not self.utilities.contextsAreOnSameLine(context, (obj, offset)):
            return

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        self.speakContents(contents)
        self.updateBraille(obj)
        self._madeFindAnnouncement = True

    def sayAll(self, inputEvent, obj=None, offset=None):
        """Speaks the contents of the document beginning with the present
        location.  Overridden in this script because the sayAll could have
        been started on an object without text (such as an image).
        """

        if not self.utilities.inDocumentContent():
            return default.Script.sayAll(self, inputEvent, obj, offset)

        else:
            obj = obj or orca_state.locusOfFocus
            speech.sayAll(self.textLines(obj, offset),
                          self.__sayAllProgressCallback)

        return True

    def _rewindSayAll(self, context, minCharCount=10):
        if not self.utilities.inDocumentContent():
            return default.Script._rewindSayAll(self, context, minCharCount)

        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        obj, start, end, string = self._sayAllContents[0]
        orca.setLocusOfFocus(None, obj, notifyScript=False)
        self.utilities.setCaretContext(obj, start)

        prevObj, prevOffset = self.utilities.findPreviousCaretInOrder(obj, start)
        self.sayAll(None, prevObj, prevOffset)
        return True

    def _fastForwardSayAll(self, context):
        if not self.utilities.inDocumentContent():
            return default.Script._fastForwardSayAll(self, context)

        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        obj, start, end, string = self._sayAllContents[-1]
        orca.setLocusOfFocus(None, obj, notifyScript=False)
        self.utilities.setCaretContext(obj, end)

        nextObj, nextOffset = self.utilities.findNextCaretInOrder(obj, end)
        self.sayAll(None, nextObj, nextOffset)
        return True

    def __sayAllProgressCallback(self, context, progressType):
        if not self.utilities.inDocumentContent() or self._inFocusMode:
            default.Script.__sayAllProgressCallback(self, context, progressType)
            return

        if progressType == speechserver.SayAllContext.INTERRUPTED:
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                self._sayAllIsInterrupted = True
                lastKey = orca_state.lastInputEvent.event_string
                if lastKey == "Down" and self._fastForwardSayAll(context):
                    return
                elif lastKey == "Up" and self._rewindSayAll(context):
                    return
                elif not self._lastCommandWasStructNav:
                    self.utilities.setCaretPosition(context.obj, context.currentOffset)
                    self.updateBraille(context.obj)

            self._inSayAll = False
            self._sayAllContents = []
            self._sayAllContexts = []
            return

        orca.setLocusOfFocus(None, context.obj, notifyScript=False)
        self.utilities.setCaretContext(context.obj, context.currentOffset)

    def _getCtrlShiftSelectionsStrings(self):
        return [messages.LINE_SELECTED_DOWN,
                messages.LINE_UNSELECTED_DOWN,
                messages.LINE_SELECTED_UP,
                messages.LINE_UNSELECTED_UP]

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

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onBusyChanged(event)
            return False

        if not self.utilities.inDocumentContent(orca_state.locusOfFocus):
            msg = "INFO: Ignoring: Locus of focus is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        self._loadingDocumentContent = event.detail1

        obj, offset = self.utilities.getCaretContext()
        if not obj or self.utilities.isZombie(obj):
            self.utilities.clearCaretContext()

        if not _settingsManager.getSetting('onlySpeakDisplayedText'):
            if event.detail1:
                msg = messages.PAGE_LOADING_START
            elif event.source.name:
                msg = messages.PAGE_LOADING_END_NAMED % event.source.name
            else:
                msg = messages.PAGE_LOADING_END
            self.presentMessage(msg)

        if event.detail1:
            return True

        if self.useFocusMode(orca_state.locusOfFocus) != self._inFocusMode:
            self.togglePresentationMode(None)

        obj, offset = self.utilities.getCaretContext()
        if not obj:
            msg = "INFO: Could not get caret context"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.isFocusModeWidget(obj):
            msg = "INFO: Setting locus of focus to focusModeWidget %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            return True

        state = obj.getState()
        if self.utilities.isLink(obj) and state.contains(pyatspi.STATE_FOCUSED):
            msg = "INFO: Setting locus of focus to focused link %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            return True

        if offset > 0:
            msg = "INFO: Setting locus of focus to context obj %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            return True

        self.updateBraille(obj)
        if state.contains(pyatspi.STATE_FOCUSABLE):
            msg = "INFO: Not doing SayAll due to focusable context obj %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            speech.speak(self.speechGenerator.generateSpeech(obj))
        elif not _settingsManager.getSetting('sayAllOnLoad'):
            msg = "INFO: Not doing SayAll due to sayAllOnLoad being False"
            debug.println(debug.LEVEL_INFO, msg)
            self.speakContents(self.getLineContentsAtOffset(obj, offset))
        elif _settingsManager.getSetting('enableSpeech'):
            msg = "INFO: Doing SayAll"
            debug.println(debug.LEVEL_INFO, msg)
            self.sayAll(None)
        else:
            msg = "INFO: Not doing SayAll due to enableSpeech being False"
            debug.println(debug.LEVEL_INFO, msg)

        return True

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "ERROR: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onCaretMoved(event)
            return False

        if self._lastCommandWasCaretNav:
            msg = "INFO: Event ignored: Last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self._lastCommandWasStructNav:
            msg = "INFO: Event ignored: Last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self._lastCommandWasMouseButton:
            msg = "INFO: Event handled: Last command was mouse button"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, event.source)
            self.utilities.setCaretContext(event.source, event.detail1)
            return True

        if self.utilities.inFindToolbar() and not self._madeFindAnnouncement:
            msg = "INFO: Event handled: Presenting find results"
            debug.println(debug.LEVEL_INFO, msg)
            self.presentFindResults(event.source, event.detail1)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Event ignored: Autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsForNonNavigableTextObject(event):
            msg = "INFO: Event ignored: Event source is non-navigable text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "INFO: Event handled: Updating position due to insertion"
            debug.println(debug.LEVEL_INFO, msg)
            self._saveLastCursorPosition(event.source, event.detail1)
            return True

        obj, offset = self.utilities.findFirstCaretContext(event.source, event.detail1)

        if self.utilities.caretMovedToSamePageFragment(event):
            msg = "INFO: Event handled: Caret moved to fragment"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            self.utilities.setCaretContext(obj, offset)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            if event.source.getRole() == pyatspi.ROLE_LINK:
                msg = "INFO: Event handled: Was for non-text link"
                debug.println(debug.LEVEL_INFO, msg)
                orca.setLocusOfFocus(event, event.source)
                self.utilities.setCaretContext(event.source, event.detail1)
            else:
                msg = "INFO: Event ignored: Was for non-text non-link"
                debug.println(debug.LEVEL_INFO, msg)
            return True

        char = text.getText(event.detail1, event.detail1+1)
        isEditable = obj.getState().contains(pyatspi.STATE_EDITABLE)
        if not char and not isEditable:
            msg = "INFO: Event ignored: Was for empty char in non-editable text"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if char == self.EMBEDDED_OBJECT_CHARACTER:
            if not self.utilities.isTextBlockElement(obj):
                msg = "INFO: Event ignored: Was for embedded non-textblock"
                debug.println(debug.LEVEL_INFO, msg)
                return True

            msg = "INFO: Setting locusOfFocus, context to: %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            self.utilities.setCaretContext(obj, offset)
            return True

        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode or isEditable:
            orca.setLocusOfFocus(event, event.source, False)
            self.utilities.setCaretContext(event.source, event.detail1)
            msg = "INFO: Setting locusOfFocus, context to: %s, %i" % \
                  (event.source, event.detail1)
            debug.println(debug.LEVEL_INFO, msg)
            super().onCaretMoved(event)
            return False

        self.utilities.setCaretContext(obj, offset)
        msg = "INFO: Setting context to: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg)
        super().onCaretMoved(event)
        return False

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onCheckedChanged(event)
            return False

        obj, offset = self.utilities.getCaretContext()
        if obj != event.source:
            msg = "INFO: Event source is not context object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        oldObj, oldState = self.pointOfReference.get('checkedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            msg = "INFO: Ignoring event, state hasn't changed"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        role = obj.getRole()
        if not (self._lastCommandWasCaretNav and role == pyatspi.ROLE_RADIO_BUTTON):
            msg = "INFO: Event is something default can handle"
            debug.println(debug.LEVEL_INFO, msg)
            super().onCheckedChanged(event)
            return False

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['checkedChange'] = hash(obj), event.detail1
        return True

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        if self.utilities.handleAsLiveRegion(event):
            msg = "INFO: Event to be handled as live region"
            debug.println(debug.LEVEL_INFO, msg)
            self.liveRegionManager.handleEvent(event)
            return True

        if self._loadingDocumentContent:
            msg = "INFO: Ignoring because document content is being loaded."
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not event.any_data or self.utilities.isZombie(event.any_data):
            msg = "INFO: Ignoring because any data is null or zombified."
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onChildrenChanged(event)
            return False

        obj, offset = self.utilities.getCaretContext()
        if obj and self.utilities.isZombie(obj):
            replicant = self.utilities.findReplicant(event.source, obj)
            if replicant:
                # Refrain from actually touching the replicant by grabbing
                # focus or setting the caret in it. Doing so will only serve
                # to anger it.
                msg = "INFO: Event handled by updating locusOfFocus and context"
                debug.println(debug.LEVEL_INFO, msg)
                orca.setLocusOfFocus(event, replicant, False)
                self.utilities.setCaretContext(replicant, offset)
                return True

        child = event.any_data
        if child.getRole() in [pyatspi.ROLE_ALERT, pyatspi.ROLE_DIALOG]:
            msg = "INFO: Setting locusOfFocus to event.any_data"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, child)
            return True

        if self.lastMouseRoutingTime and 0 < time.time() - self.lastMouseRoutingTime < 1:
            utterances = []
            utterances.append(messages.NEW_ITEM_ADDED)
            utterances.extend(self.speechGenerator.generateSpeech(child, force=True))
            speech.speak(utterances)
            self.lastMouseOverObject = child
            self.preMouseOverContext = self.utilities.getCaretContext()
            return True

        super().onChildrenChanged(event)
        return False

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        msg = "INFO: Updating loading state and resetting live regions"
        debug.println(debug.LEVEL_INFO, msg)
        self._loadingDocumentContent = False
        self.liveRegionManager.reset()
        return True

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        msg = "INFO: Updating loading state"
        debug.println(debug.LEVEL_INFO, msg)
        self._loadingDocumentContent = False
        return True

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        msg = "INFO: Updating loading state"
        debug.println(debug.LEVEL_INFO, msg)
        self._loadingDocumentContent = True
        return True

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.utilities.inDocumentContent(event.source):
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
            msg = "INFO: Ignoring because event source lost focus"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.isZombie(event.source):
            msg = "ERROR: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onFocusedChanged(event)
            return False

        state = event.source.getState()
        if state.contains(pyatspi.STATE_EDITABLE):
            msg = "INFO: Event source is editable"
            debug.println(debug.LEVEL_INFO, msg)
            super().onFocusedChanged(event)
            return False

        role = event.source.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            msg = "INFO: Event handled: Setting locusOfFocus to event source"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, event.source)
            return True

        if self._lastCommandWasCaretNav:
            msg = "INFO: Event ignored: Last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self._lastCommandWasStructNav:
            msg = "INFO: Event ignored: Last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if role in [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]:
            obj, offset = self.utilities.getCaretContext(event.source)
            if obj and self.utilities.isZombie(obj):
                msg = "INFO: Clearing context - obj is zombie"
                debug.println(debug.LEVEL_INFO, msg)
                self.utilities.clearCaretContext()
                obj, offset = self.utilities.getCaretContext(event.source)

            if obj:
                wasFocused = obj.getState().contains(pyatspi.STATE_FOCUSED)
                obj.clearCache()
                isFocused = obj.getState().contains(pyatspi.STATE_FOCUSED)
                if wasFocused == isFocused:
                    msg = "INFO: Event handled: Setting locusOfFocus to context"
                    debug.println(debug.LEVEL_INFO, msg)
                    orca.setLocusOfFocus(event, obj)
                    return True

        if not state.contains(pyatspi.STATE_FOCUSABLE) \
           and not state.contains(pyatspi.STATE_FOCUSED):
            msg = "INFO: Event ignored: Source is not focusable or focused"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onFocusedChanged(event)
        return False

    def onMouseButton(self, event):
        """Callback for mouse:button accessibility events."""

        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = True
        super().onMouseButton(event)
        return False

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self.utilities.eventIsStatusBarNoise(event):
            msg = "INFO: Ignoring event believed to be status bar noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if event.source.getRole() == pyatspi.ROLE_FRAME:
            msg = "INFO: Flusing messages from live region manager"
            debug.println(debug.LEVEL_INFO, msg)
            self.liveRegionManager.flushMessages()

        return True

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onShowingChanged(event)
            return False

        return True

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if self.utilities.eventIsStatusBarNoise(event):
            msg = "INFO: Ignoring event believed to be status bar noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onTextDeleted(event)
            return False

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Ignoring event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "INFO: Ignoring event believed to be due to text insertion"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        msg = "INFO: Clearing content cache due to text deletion"
        debug.println(debug.LEVEL_INFO, msg)
        self.utilities.clearContentCache()

        state = event.source.getState()
        if not state.contains(pyatspi.STATE_EDITABLE):
            if self.inMouseOverObject \
               and self.utilities.isZombie(self.lastMouseOverObject):
                msg = "INFO: Restoring pre-mouseover context"
                debug.println(debug.LEVEL_INFO, msg)
                self.restorePreMouseOverContext()

            msg = "INFO: Done processing non-editable source"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onTextDeleted(event)
        return False

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self.utilities.eventIsStatusBarNoise(event):
            msg = "INFO: Ignoring event believed to be status bar noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onTextInserted(event)
            return False

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Ignoring: Event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        # TODO - JD: As an experiment, we're stopping these at the event manager.
        # If that works, this can be removed.
        if self.utilities.eventIsEOCAdded(event):
            msg = "INFO: Ignoring: Event was for embedded object char"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        msg = "INFO: Clearing content cache due to text insertion"
        debug.println(debug.LEVEL_INFO, msg)
        self.utilities.clearContentCache()

        if self.utilities.handleAsLiveRegion(event):
            msg = "INFO: Event to be handled as live region"
            debug.println(debug.LEVEL_INFO, msg)
            self.liveRegionManager.handleEvent(event)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "INFO: Ignoring: Event source is not a text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        state = event.source.getState()
        if not state.contains(pyatspi.STATE_EDITABLE) \
           and event.source != orca_state.locusOfFocus:
            msg = "INFO: Done processing non-editable, non-locusOfFocus source"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onTextInserted(event)
        return False

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "ERROR: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onTextSelectionChanged(event)
            return False

        if self.utilities.inFindToolbar():
            msg = "INFO: Event handled: Presenting find results"
            debug.println(debug.LEVEL_INFO, msg)
            self.presentFindResults(event.source, -1)
            self._saveFocusedObjectInfo(orca_state.locusOfFocus)
            return True

        if not self.utilities.inDocumentContent(orca_state.locusOfFocus):
            msg = "INFO: Ignoring: Event in document content; focus is not"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Ignoring: Event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsForNonNavigableTextObject(event):
            msg = "INFO: Ignoring event for non-navigable text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "INFO: Ignoring: Event source is not a text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        char = text.getText(event.detail1, event.detail1+1)
        if char == self.EMBEDDED_OBJECT_CHARACTER:
            msg = "INFO: Ignoring: Event offset is at embedded object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        obj, offset = self.utilities.getCaretContext()
        if obj and obj.parent and event.source in [obj.parent, obj.parent.parent]:
            msg = "INFO: Ignoring: Source is context ancestor"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onTextSelectionChanged(event)
        return False

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

    def inFocusMode(self):
        """ Returns True if we're in focus mode."""

        return self._inFocusMode

    def focusModeIsSticky(self):
        """Returns True if we're in 'sticky' focus mode."""

        return self._focusModeIsSticky

    def useFocusMode(self, obj):
        """Returns True if we should use focus mode in obj."""

        if self._focusModeIsSticky:
            return True

        if not _settingsManager.getSetting('structNavTriggersFocusMode') \
           and self._lastCommandWasStructNav:
            return False

        if not _settingsManager.getSetting('caretNavTriggersFocusMode') \
           and self._lastCommandWasCaretNav:
            return False

        return self.utilities.isFocusModeWidget(obj)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if newFocus and self.utilities.isZombie(newFocus):
            msg = "ERROR: New focus is Zombie" % newFocus
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.utilities.inDocumentContent(newFocus):
            msg = "INFO: Locus of focus changed to non-document obj"
            self._madeFindAnnouncement = False
            self._inFocusMode = False
            debug.println(debug.LEVEL_INFO, msg)
            super().locusOfFocusChanged(event, oldFocus, newFocus)
            return False

        if oldFocus and self.utilities.isZombie(oldFocus):
            oldFocus = None

        caretOffset = 0
        if self.utilities.inFindToolbar(oldFocus):
            newFocus, caretOffset = self.utilities.getCaretContext()

        text = self.utilities.queryNonEmptyText(newFocus)
        if text and (0 <= text.caretOffset < text.characterCount):
            caretOffset = text.caretOffset

        self.utilities.setCaretContext(newFocus, caretOffset)
        self.updateBraille(newFocus)
        speech.speak(self.speechGenerator.generateSpeech(newFocus, priorObj=oldFocus))
        self._saveFocusedObjectInfo(newFocus)

        if not self._focusModeIsSticky \
           and self.useFocusMode(newFocus) != self._inFocusMode:
            self.togglePresentationMode(None)

        return True

    def presentLine(self, obj, offset):
        """Presents the current line in speech and in braille.

        Arguments:
        - obj: the Accessible at the caret
        - offset: the offset within obj
        """

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakContents(self.utilities.getLineContentsAtOffset(obj, offset))
        self.updateBraille(obj)

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the given object."""

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: disabled")
            return

        if not (self._lastCommandWasCaretNav or self._lastCommandWasStructNav) \
           or self._inFocusMode or not self.utilities.inDocumentContent():
            super().updateBraille(obj, extraRegion)
            return

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        self.displayContents(contents)

    def displayContents(self, contents):
        """Displays contents in braille."""

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: disabled")
            return

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)
        regions, focusedRegion = self.brailleGenerator.generateContents(contents)
        for region in regions:
            self.addBrailleRegionsToLine(region, line)

        if line.regions:
            line.regions[-1].string = line.regions[-1].string.rstrip(" ")

        self.setBrailleFocus(focusedRegion, getLinkMask=False)
        self.refreshBraille(panToCursor=True, getLinkMask=False)

    def speakContents(self, contents):
        """Speaks the specified contents."""

        utterances = self.speechGenerator.generateContents(contents)
        speech.speak(utterances)

    def speakCharacterAtOffset(self, obj, characterOffset):
        """Speaks the character at the given characterOffset in the
        given object."""
        character = self.utilities.getCharacterAtOffset(obj, characterOffset)
        self.speakMisspelledIndicator(obj, characterOffset)
        if obj:
            if character and character != self.EMBEDDED_OBJECT_CHARACTER:
                self.speakCharacter(character)
            elif not obj.getState().contains(pyatspi.STATE_EDITABLE):
                # We won't have a character if we move to the end of an
                # entry (in which case we're not on a character and therefore
                # have nothing to say), or when we hit a component with no
                # text (e.g. checkboxes) or reset the caret to the parent's
                # characterOffset (lists).  In these latter cases, we'll just
                # speak the entire component.
                #
                utterances = self.speechGenerator.generateSpeech(obj)
                speech.speak(utterances)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        if not self._lastCommandWasCaretNav:
            super().sayCharacter(obj)
            return

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        if not obj:
            return

        contents = self.utilities.getCharacterContentsAtOffset(obj, offset)
        if not contents:
            return

        obj, start, end, string = contents[0]
        if start > 0:
            string = string or "\n"

        if string:
            self.speakMisspelledIndicator(obj, start)
            self.speakCharacter(string)
        else:
            self.speakContents(contents)

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        if not self._lastCommandWasCaretNav:
            super().sayWord(obj)
            return

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        wordContents = self.utilities.getWordContentsAtOffset(obj, offset)
        textObj, startOffset, endOffset, word = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        self.speakContents(wordContents)

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        if not self._lastCommandWasCaretNav:
            super().sayLine(obj)
            return

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        self.speakContents(self.utilities.getLineContentsAtOffset(obj, offset))

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """
        if self.flatReviewContext \
           or not self.utilities.inDocumentContent() \
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
           or not self.utilities.inDocumentContent() \
           or not self.isBrailleEndShowing():
            default.Script.panBrailleRight(self, inputEvent, panAmount)
        elif self.goNextLine(inputEvent):
            while self.panBrailleInDirection(panToLeft=True):
                pass
            self.refreshBraille(False)
        return True

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if we should do our own caret navigation.
        """

        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode:
            return False

        if not self.utilities.inDocumentContent():
            return False

        if keyboardEvent.event_string in ["Page_Up", "Page_Down"]:
            return False

        if keyboardEvent.modifiers & keybindings.SHIFT_MODIFIER_MASK:
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

        if not self.utilities.inDocumentContent():
            return False

        return True
 
    ####################################################################
    #                                                                  #
    # Methods to get information about current object.                 #
    #                                                                  #
    ####################################################################

    def getTextLineAtCaret(self, obj, offset=None, startOffset=None, endOffset=None):
        """To-be-removed. Returns the string, caretOffset, startOffset."""

        if self._inFocusMode or not self.utilities.inDocumentContent(obj) \
           or obj.getState().contains(pyatspi.STATE_EDITABLE):
            return super().getTextLineAtCaret(obj, offset, startOffset, endOffset)

        text = self.utilities.queryNonEmptyText(obj)
        if offset is None:
            try:
                offset = max(0, text.caretOffset)
            except:
                offset = 0

        if text and startOffset is not None and endOffset is not None:
            return text.getText(startOffset, endOffset), offset, startOffset

        contextObj, contextOffset = self.utilities.getCaretContext(documentFrame=None)
        if contextObj == obj:
            caretOffset = contextOffset
        else:
            caretOffset = offset

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        contents = list(filter(lambda x: x[0] == obj, contents))
        if len(contents) == 1:
            index = 0
        else:
            index = self.utilities.findObjectInContents(obj, offset, contents)

        if index > -1:
            candidate, startOffset, endOffset, string = contents[index]
            if not self.EMBEDDED_OBJECT_CHARACTER in string:
                return string, caretOffset, startOffset

        return "", 0, 0

    ####################################################################
    #                                                                  #
    # Methods to navigate to previous and next objects.                #
    #                                                                  #
    ####################################################################

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
                [obj, offset] = self.utilities.findFirstCaretContext(obj, offset)

            if obj and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                obj.queryComponent().grabFocus()
            elif obj:
                contents = self.utilities.getObjectContentsAtOffset(obj, offset)
                # If we don't have anything to say, let's try one more
                # time.
                #
                if len(contents) == 1 and not contents[0][3].strip():
                    [obj, offset] = self.utilities.findNextCaretInOrder(obj, offset)
                    contents = self.utilities.getObjectContentsAtOffset(obj, offset)
                self.utilities.setCaretPosition(obj, offset)
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
            [obj, offset] = self.utilities.findFirstCaretContext(obj, offset)

        if obj and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            obj.queryComponent().grabFocus()
        elif obj:
            self.utilities.setCaretPosition(obj, offset)
            self.speakContents(self.utilities.getObjectContentsAtOffset(obj, offset))
            self.updateBraille(obj)
        self.inMouseOverObject = False
        self.lastMouseOverObject = None

    def goNextCharacter(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the document window.
        """
        [obj, characterOffset] = self.utilities.getCaretContext()
        while obj:
            [obj, characterOffset] = self.utilities.findNextCaretInOrder(obj,
                                                               characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break

        if not obj:
            [obj, characterOffset] = self.utilities.getBottomOfFile()

        self.utilities.setCaretPosition(obj, characterOffset)
        self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goPreviousCharacter(self, inputEvent):
        """Positions the caret offset to the previous character or object
        in the document window.
        """
        [obj, characterOffset] = self.utilities.getCaretContext()
        while obj:
            [obj, characterOffset] = self.utilities.findPreviousCaretInOrder(
                obj, characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break

        if not obj:
            [obj, characterOffset] = self.utilities.getTopOfFile()

        self.utilities.setCaretPosition(obj, characterOffset)
        self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goPreviousWord(self, inputEvent):
        """Positions the caret offset to beginning of the previous
        word or object in the document window.
        """

        [obj, characterOffset] = self.utilities.getCaretContext()

        # Make sure we have a word.
        #
        [obj, characterOffset] = \
            self.utilities.findPreviousCaretInOrder(obj, characterOffset)

        contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
        if not len(contents):
            return

        [obj, startOffset, endOffset, string] = contents[0]
        if len(contents) == 1 \
           and endOffset - startOffset == 1 \
           and self.utilities.getCharacterAtOffset(obj, startOffset) == " ":
            # Our "word" is just a space. This can happen if the previous
            # word was a mark of punctuation surrounded by whitespace (e.g.
            # " | ").
            #
            [obj, characterOffset] = \
                self.utilities.findPreviousCaretInOrder(obj, startOffset)
            contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
            if len(contents):
                [obj, startOffset, endOffset, string] = contents[0]

        self.utilities.setCaretPosition(obj, startOffset)
        self.updateBraille(obj)
        self.speakMisspelledIndicator(obj, startOffset)
        self.speakContents(contents)

    def goNextWord(self, inputEvent):
        """Positions the caret offset to the end of next word or object
        in the document window.
        """

        [obj, characterOffset] = self.utilities.getCaretContext()

        # Make sure we have a word.
        #
        characterOffset = max(0, characterOffset)
        [obj, characterOffset] = \
            self.utilities.findNextCaretInOrder(obj, characterOffset)

        contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
        if not (len(contents) and contents[-1][2]):
            return

        [obj, startOffset, endOffset, string] = contents[-1]
        if string and string[-1].isspace():
            endOffset -= 1
        self.utilities.setCaretPosition(obj, endOffset)
        self.updateBraille(obj)
        self.speakMisspelledIndicator(obj, startOffset)
        self.speakContents(contents)

    def goPreviousLine(self, inputEvent):
        """Positions the caret offset at the previous line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        if self._inSayAll \
           and _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            msg = "INFO: inSayAll and rewindAndFastforwardInSayAll is enabled"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        obj, offset = self.utilities.getCaretContext()
        msg = "INFO: Current context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg)

        if obj and self.utilities.isZombie(obj):
            msg = "INFO: Current context obj %s is zombie" % obj
            debug.println(debug.LEVEL_INFO, msg)

        line = self.utilities.getLineContentsAtOffset(obj, offset)
        msg = "INFO: Line contents for %s, %i: %s" % (obj, offset, line)
        debug.println(debug.LEVEL_INFO, msg)

        if not (line and line[0]):
            return False

        firstObj, firstOffset = line[0][0], line[0][1]
        msg = "INFO: First context on line is: %s, %i" % (firstObj, firstOffset)
        debug.println(debug.LEVEL_INFO, msg)

        obj, offset = self.utilities.previousContext(firstObj, firstOffset, True)
        msg = "INFO: Previous context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg)

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        if not contents:
            msg = "INFO: Could not get line contents for %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg)
            return False

        obj, start = contents[0][0], contents[0][1]
        self.utilities.setCaretPosition(obj, start)
        self.displayContents(contents)
        self.speakContents(contents)

        return True

    def goNextLine(self, inputEvent):
        """Positions the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        if self._inSayAll \
           and _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            msg = "INFO: inSayAll and rewindAndFastforwardInSayAll is enabled"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        obj, offset = self.utilities.getCaretContext()
        msg = "INFO: Current context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg)

        if obj and self.utilities.isZombie(obj):
            msg = "INFO: Current context obj %s is zombie" % obj
            debug.println(debug.LEVEL_INFO, msg)

        line = self.utilities.getLineContentsAtOffset(obj, offset)
        msg = "INFO: Line contents for %s, %i: %s" % (obj, offset, line)
        debug.println(debug.LEVEL_INFO, msg)

        if not (line and line[0]):
            return False

        lastObj, lastOffset = line[-1][0], line[-1][2] - 1
        msg = "INFO: Last context on line is: %s, %i" % (lastObj, lastOffset)
        debug.println(debug.LEVEL_INFO, msg)

        obj, offset = self.utilities.nextContext(lastObj, lastOffset, True)
        msg = "INFO: Next context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg)

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        if not contents:
            msg = "INFO: Could not get line contents for %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg)
            return False

        obj, start = contents[0][0], contents[0][1]
        self.utilities.setCaretPosition(obj, start)
        self.speakContents(contents)
        self.displayContents(contents)
        return True

    def goBeginningOfLine(self, inputEvent):
        """Positions the caret offset at the beginning of the line."""

        [obj, characterOffset] = self.utilities.getCaretContext()
        line = self.utilities.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = self.utilities.findFirstCaretContext(line[0][0], line[0][1])
        self.utilities.setCaretPosition(obj, characterOffset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goEndOfLine(self, inputEvent):
        """Positions the caret offset at the end of the line."""

        [obj, characterOffset] = self.utilities.getCaretContext()
        line = self.utilities.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = line[-1][0], line[-1][2] - 1
        self.utilities.setCaretPosition(obj, characterOffset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goTopOfFile(self, inputEvent):
        """Positions the caret offset at the beginning of the document."""

        [obj, characterOffset] = self.utilities.getTopOfFile()
        self.utilities.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def goBottomOfFile(self, inputEvent):
        """Positions the caret offset at the end of the document."""

        [obj, characterOffset] = self.utilities.getBottomOfFile()
        self.utilities.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def enableStickyFocusMode(self, inputEvent):
        self._inFocusMode = True
        self._focusModeIsSticky = True
        self.presentMessage(messages.MODE_FOCUS_IS_STICKY)

    def togglePresentationMode(self, inputEvent):
        if self._inFocusMode:
            [obj, characterOffset] = self.utilities.getCaretContext()
            try:
                parentRole = obj.parent.getRole()
            except:
                parentRole = None
            if parentRole == pyatspi.ROLE_LIST_BOX:
                self.utilities.setCaretContext(obj.parent, -1)
            elif parentRole == pyatspi.ROLE_MENU:
                self.utilities.setCaretContext(obj.parent.parent, -1)

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
        if self.utilities.inDocumentContent(acc):
            try:
                ai = acc.queryAction()
            except NotImplementedError:
                return True
        default.Script.speakWordUnderMouse(self, acc)
