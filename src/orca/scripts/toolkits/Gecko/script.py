# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
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

"""Custom script for Gecko toolkit.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Orca Team."
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
from . import script_settings
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
        self.arrowToLineBeginningCheckButton = None
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
             Script.expandComboBox,
             Script.goTopOfFile,
             Script.goBottomOfFile,
             Script.goBeginningOfLine,
             Script.goEndOfLine]

        self._liveRegionFunctions = \
            [Script.setLivePolitenessOff,
             Script.advanceLivePoliteness,
             Script.monitorLiveRegions,
             Script.reviewLiveAnnouncement]

        if script_settings.controlCaretNavigation:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Orca is controlling the caret.")
        else:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Gecko is controlling the caret.")

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
        self._previousLineContents = None
        self.currentLineContents = None
        self._nextLineContents = None

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

        # See bug 665522 - comment 5
        app.setCacheMask(pyatspi.cache.DEFAULT ^ pyatspi.cache.CHILDREN)

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

        enabledTypes = [GeckoStructuralNavigation.ANCHOR,
                        GeckoStructuralNavigation.BLOCKQUOTE,
                        GeckoStructuralNavigation.BUTTON,
                        GeckoStructuralNavigation.CHECK_BOX,
                        GeckoStructuralNavigation.CHUNK,
                        GeckoStructuralNavigation.COMBO_BOX,
                        GeckoStructuralNavigation.ENTRY,
                        GeckoStructuralNavigation.FORM_FIELD,
                        GeckoStructuralNavigation.HEADING,
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
        enable = script_settings.structuralNavigationEnabled
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

        self.inputEventHandlers["expandComboBoxHandler"] = \
            input_event.InputEventHandler(
                Script.expandComboBox,
                cmdnames.CARET_NAVIGATION_EXPAND_COMBO_BOX)

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

        self.inputEventHandlers["goPreviousObjectInOrderHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousObjectInOrder,
                cmdnames.CARET_NAVIGATION_PREV_OBJECT)

        self.inputEventHandlers["goNextObjectInOrderHandler"] = \
            input_event.InputEventHandler(
                Script.goNextObjectInOrder,
                cmdnames.CARET_NAVIGATION_NEXT_OBJECT)

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

        if script_settings.controlCaretNavigation:
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
        value = script_settings.controlCaretNavigation
        self.controlCaretNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.controlCaretNavigationCheckButton.set_active(value) 
        generalGrid.attach(self.controlCaretNavigationCheckButton, 0, 0, 1, 1)

        label = guilabels.USE_STRUCTURAL_NAVIGATION
        value = self.structuralNavigation.enabled
        self.structuralNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.structuralNavigationCheckButton.set_active(value)
        generalGrid.attach(self.structuralNavigationCheckButton, 0, 1, 1, 1)

        label = guilabels.CARET_NAVIGATION_START_OF_LINE
        value = script_settings.arrowToLineBeginning
        self.arrowToLineBeginningCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.arrowToLineBeginningCheckButton.set_active(value)
        generalGrid.attach(self.arrowToLineBeginningCheckButton, 0, 3, 1, 1)

        label = guilabels.READ_PAGE_UPON_LOAD
        value = script_settings.sayAllOnLoad
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

        label = guilabels.FIND_SPEAK_RESULTS
        value = script_settings.speakResultsDuringFind
        self.speakResultsDuringFindCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakResultsDuringFindCheckButton.set_active(value)
        findGrid.attach(self.speakResultsDuringFindCheckButton, 0, 0, 1, 1)

        label = guilabels.FIND_ONLY_SPEAK_CHANGED_LINES
        value = script_settings.onlySpeakChangedLinesDuringFind
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
                   Gtk.Adjustment(script_settings.minimumFindLength, 0, 20, 1)
        self.minimumFindLengthSpinButton = Gtk.SpinButton()
        self.minimumFindLengthSpinButton.set_adjustment(
            self.minimumFindLengthAdjustment)
        hgrid.attach(self.minimumFindLengthSpinButton, 1, 0, 1, 1)
        self.minimumFindLengthLabel.set_mnemonic_widget(
            self.minimumFindLengthSpinButton)

        grid.show_all()

        return grid

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        prefs.writelines("\n")
        prefix = "orca.scripts.toolkits.Gecko.script_settings"
        prefs.writelines("import %s\n\n" % prefix)

        value = self.controlCaretNavigationCheckButton.get_active()
        prefs.writelines("%s.controlCaretNavigation = %s\n" % (prefix, value))
        script_settings.controlCaretNavigation = value

        value = self.structuralNavigationCheckButton.get_active()
        prefs.writelines("%s.structuralNavigationEnabled = %s\n" \
                         % (prefix, value))
        script_settings.structuralNavigationEnabled = value

        value = self.arrowToLineBeginningCheckButton.get_active()
        prefs.writelines("%s.arrowToLineBeginning = %s\n" % (prefix, value))
        script_settings.arrowToLineBeginning = value

        value = self.sayAllOnLoadCheckButton.get_active()
        prefs.writelines("%s.sayAllOnLoad = %s\n" % (prefix, value))
        script_settings.sayAllOnLoad = value

        value = self.speakResultsDuringFindCheckButton.get_active()
        prefs.writelines("%s.speakResultsDuringFind = %s\n" % (prefix, value))
        script_settings.speakResultsDuringFind = value

        value = self.changedLinesOnlyCheckButton.get_active()
        prefs.writelines("%s.onlySpeakChangedLinesDuringFind = %s\n"\
                         % (prefix, value))
        script_settings.onlySpeakChangedLinesDuringFind = value

        value = self.minimumFindLengthSpinButton.get_value()
        prefs.writelines("%s.minimumFindLength = %s\n" % (prefix, value))
        script_settings.minimumFindLength = value

        # These structural navigation settings used to be application-
        # specific preferences because at the time structural navigation
        # was implemented it was part of the Gecko script. These settings
        # are now part of settings.py so that other scripts can implement
        # structural navigation. But until that happens, there's no need
        # to move these controls/change the preferences dialog.
        # 
        value = self.speakCellCoordinatesCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellCoordinates = %s\n" % value)
        _settingsManager.setSetting('speakCellCoordinates', value)

        value = self.speakCellSpanCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellSpan = %s\n" % value)
        _settingsManager.setSetting('speakCellSpan', value)

        value = self.speakCellHeadersCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellHeaders = %s\n" % value)
        _settingsManager.setSetting('speakCellHeaders', value)

        value = self.skipBlankCellsCheckButton.get_active()
        prefs.writelines("orca.settings.skipBlankCells = %s\n" % value)
        _settingsManager.setSetting('skipBlankCells', value)

    def getAppState(self):
        """Returns an object that can be passed to setAppState.  This
        object will be use by setAppState to restore any state information
        that was being maintained by the script."""
        return [default.Script.getAppState(self),
                self._documentFrameCaretContext]

    def setAppState(self, appState):
        """Sets the application state using the given appState object.

        Arguments:
        - appState: an object obtained from getAppState
        """
        try:
            [defaultAppState,
             self._documentFrameCaretContext] = appState
            default.Script.setAppState(self, defaultAppState)
        except:
            debug.printException(debug.LEVEL_WARNING)

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
                return self.useCaretNavigationModel(keyboardEvent)
            elif handler \
                 and (handler.function in self.structuralNavigation.functions \
                      or handler.function in self._liveRegionFunctions):
                return self.useStructuralNavigationModel()
            else:
                consumes = handler != None
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                return self.useCaretNavigationModel(keyboardEvent)
            elif handler \
                 and (handler.function in self.structuralNavigation.functions \
                      or handler.function in self._liveRegionFunctions):
                return self.useStructuralNavigationModel()
            else:
                consumes = handler != None
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
            utterances = self.getUtterancesFromContents(contents)
            clumped = self.clumpUtterances(utterances)
            for i in range(len(clumped)):
                [obj, startOffset, endOffset, text] = \
                                             contents[min(i, len(contents)-1)]
                [element, voice] = clumped[i]
                if isinstance(element, str):
                    element = self.utilities.adjustForRepeats(element)
                if isinstance(element, (Pause, ACSS)):
                    # At the moment, SayAllContext is expecting a string; not
                    # a Pause. For now, being conservative and catching that
                    # here. See bug #591351.
                    #
                    continue
                yield [speechserver.SayAllContext(obj, element,
                                                  startOffset, endOffset),
                       voice]

            obj = contents[-1][0]
            characterOffset = max(0, contents[-1][2] - 1)

            if sayAllBySentence:
                [obj, characterOffset] = \
                    self.findNextCaretInOrder(obj, characterOffset)
            else:
                [obj, characterOffset] = \
                    self.findNextLine(obj, characterOffset)
            done = (obj == None)

    def __sayAllProgressCallback(self, context, callbackType):
        if callbackType == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            #
            # Attempt to keep the content visible on the screen as
            # it is being read, but avoid links as grabFocus sometimes
            # makes them disappear and sayAll to subsequently stop.
            #
            if context.currentOffset == 0 and \
               context.obj.getRole() in [pyatspi.ROLE_HEADING,
                                         pyatspi.ROLE_SECTION,
                                         pyatspi.ROLE_PARAGRAPH] \
               and context.obj.parent.getRole() != pyatspi.ROLE_LINK:
                characterCount = context.obj.queryText().characterCount
                self.setCaretPosition(context.obj, characterCount-1)
        elif callbackType == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            try:
                self.setCaretPosition(context.obj, context.currentOffset)
            except:
                characterCount = context.obj.queryText().characterCount
                self.setCaretPosition(context.obj, characterCount-1)
            self.updateBraille(context.obj)
        elif callbackType == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            try:
                self.setCaretPosition(context.obj, context.currentOffset)
            except:
                characterCount = context.obj.queryText().characterCount
                self.setCaretPosition(context.obj, characterCount-1)
            self.updateBraille(context.obj)

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
            if end - start >= script_settings.minimumFindLength:
                enoughSelected = True

        # Haing done that, update the caretContext. If the user wants
        # matches spoken, we also need to if we are on the same line
        # as before.
        #
        origObj, origOffset = self.getCaretContext()
        self.setCaretContext(obj, offset)
        if enoughSelected and script_settings.speakResultsDuringFind:
            origExtents = self.getExtents(origObj, origOffset - 1, origOffset)
            newExtents = self.getExtents(obj, offset - 1, offset)
            lineChanged = not self.onSameLine(origExtents, newExtents)

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
               not script_settings.onlySpeakChangedLinesDuringFind:
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

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            if event.source.getRole() == pyatspi.ROLE_LINK:
                orca.setLocusOfFocus(event, event.source)
            return

        contextObj, contextOffset = self.getCaretContext()
        if event.detail1 == contextOffset and event.source == contextObj:
            return

        obj = event.source
        firstObj, firstOffset = self.findFirstCaretContext(obj, event.detail1)
        if firstOffset == contextOffset and firstObj == contextObj:
            return

        if contextObj and contextObj.parent == firstObj:
            return

        if self.isAriaWidget(obj) or not self.inDocumentContent(obj):
            default.Script.onCaretMoved(self, event)
            return

        if self.utilities.inFindToolbar():
            self.presentFindResults(obj, event.detail1)
            return

        self.setCaretContext(obj, event.detail1)
        if not script_settings.controlCaretNavigation \
           or obj.getState().contains(pyatspi.STATE_EDITABLE):
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
        if self.isAriaWidget(obj.parent):
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
        elif not script_settings.sayAllOnLoad:
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
            if self.isAriaWidget(event.source):
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

        if not script_settings.controlCaretNavigation:
            default.Script.onFocusedChanged(self, event)
            return

        obj = event.source
        if self.isAriaWidget(obj) or not self.inDocumentContent(obj):
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
            return

        caretOffset = -1
        if self.utilities.inFindToolbar(oldFocus):
            newFocus, caretOffset = self.getCaretContext()

        text = self.utilities.queryNonEmptyText(newFocus)
        if text and (0 <= text.caretOffset < text.characterCount):
            caretOffset = text.caretOffset

        self.setCaretContext(newFocus, caretOffset)
        default.Script.locusOfFocusChanged(self, event, oldFocus, newFocus)

    def findObjectOnLine(self, obj, offset, contents):
        """Determines if the item described by the object and offset is
        in the line contents.

        Arguments:
        - obj: the Accessible
        - offset: the character offset within obj
        - contents: a list of (obj, startOffset, endOffset, string) tuples

        Returns the index of the item if found; -1 if not found.
        """

        if not obj or not contents or not len(contents):
            return -1

        index = -1
        for content in contents:
            [candidate, start, end, string] = content

            # When we get the line contents, we include a focusable list
            # as a list and combo box as a combo box because that is what
            # we want to present.  However, when we set the caret context,
            # we set it to the position (and object) that immediately
            # precedes it.  Therefore, that's what we need to look at when
            # trying to determine our position.
            #
            try:
                role = candidate.getRole()
            except (LookupError, RuntimeError):
                role = None
            try:
                state = candidate.getState()
            except (LookupError, RuntimeError):
                state = pyatspi.StateSet()
            if role in [pyatspi.ROLE_LIST, pyatspi.ROLE_COMBO_BOX] \
               and state.contains(pyatspi.STATE_FOCUSABLE) \
               and not self.utilities.isSameObject(obj, candidate):
                start = self.utilities.characterOffsetInParent(candidate)
                end = start + 1
                candidate = candidate.parent

            if self.utilities.isSameObject(obj, candidate) \
               and (start <= offset < end or role == pyatspi.ROLE_ENTRY):
                index = contents.index(content)
                break

        return index

    def _updateLineCache(self, obj, offset):
        """Tries to intelligently update our stored lines. Destroying them if
        need be.

        Arguments:
        - obj: the Accessible
        - offset: the character offset within obj
        """

        index = self.findObjectOnLine(obj, offset, self.currentLineContents)
        if index < 0:
            index = self.findObjectOnLine(obj,
                                          offset,
                                          self._previousLineContents)
            if index >= 0:
                self._nextLineContents = self.currentLineContents
                self.currentLineContents = self._previousLineContents
                self._previousLineContents = None
            else:
                index = self.findObjectOnLine(obj,
                                              offset,
                                              self._nextLineContents)
                if index >= 0:
                    self._previousLineContents = self.currentLineContents
                    self.currentLineContents = self._nextLineContents
                    self._nextLineContents = None
                else:
                    self._destroyLineCache()

    def _destroyLineCache(self):
        """Removes all of the stored lines."""

        self._previousLineContents = None
        self.currentLineContents = None
        self._nextLineContents = None
        self.currentAttrs = {}

    def presentLine(self, obj, offset):
        """Presents the current line in speech and in braille.

        Arguments:
        - obj: the Accessible at the caret
        - offset: the offset within obj
        """

        contents = self.currentLineContents
        index = self.findObjectOnLine(obj, offset, contents)
        if index < 0:
            self.currentLineContents = self.getLineContentsAtOffset(obj,
                                                                    offset)
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

        if self.isAriaWidget(obj) or not self.inDocumentContent():
            default.Script.updateBraille(self, obj, extraRegion)
            return

        if not obj:
            return

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)

        # Some text areas have a character offset of -1 when you tab
        # into them.  In these cases, they show all the text as being
        # selected.  We don't know quite what to do in that case,
        # so we'll just pretend the caret is at the beginning (0).
        #
        [focusedObj, focusedCharacterOffset] = self.getCaretContext()

        # [[[TODO: HACK - WDW when composing e-mail in Thunderbird and
        # when entering text in editable text areas, Gecko likes to
        # force the last character of a line to be a newline.  So,
        # we adjust for this because we want to keep meaningful text
        # on the display.]]]
        #
        needToRefresh = False
        lineContentsOffset = focusedCharacterOffset
        focusedObjText = self.utilities.queryNonEmptyText(focusedObj)
        if focusedObjText:
            char = focusedObjText.getText(focusedCharacterOffset,
                                          focusedCharacterOffset + 1)
            if char == "\n":
                lineContentsOffset = max(0, focusedCharacterOffset - 1)
                needToRefresh = True

        if not self.isNavigableAria(focusedObj):
            # Sometimes looking for the first caret context means that we
            # are on a child within a non-navigable object (such as the
            # text within a page tab). If so, set the focusedObj to the
            # parent widget.
            #
            if not self.isAriaWidget(focusedObj):
                focusedObj, focusedCharacterOffset = focusedObj.parent, 0
                lineContentsOffset = 0

        # Sometimes we just want to present the current object rather
        # than the full line. For instance, if we're on a slider we
        # should just present that slider. We'll assume we want the
        # full line, however.
        #
        presentOnlyFocusedObj = False
        if focusedObj and focusedObj.getRole() == pyatspi.ROLE_SLIDER:
            presentOnlyFocusedObj = True

        contents = self.currentLineContents
        index = self.findObjectOnLine(focusedObj,
                                      max(0, lineContentsOffset),
                                      contents)
        if index < 0 or needToRefresh:
            contents = self.getLineContentsAtOffset(focusedObj,
                                                    max(0, lineContentsOffset))
            self.currentLineContents = contents
            index = self.findObjectOnLine(focusedObj,
                                          max(0, lineContentsOffset),
                                          contents)

        if not len(contents):
            return

        whitespace = [" ", "\n", self.NO_BREAK_SPACE_CHARACTER]

        focusedRegion = None
        for i, content in enumerate(contents):
            isFocusedObj = (i == index)
            [obj, startOffset, endOffset, string] = content
            if not obj:
                continue
            elif presentOnlyFocusedObj and not isFocusedObj:
                continue

            role = obj.getRole()
            if (not len(string) and role != pyatspi.ROLE_PARAGRAPH) \
               or self.utilities.isEntry(obj) \
               or self.utilities.isPasswordText(obj) \
               or role in [pyatspi.ROLE_LINK, pyatspi.ROLE_PUSH_BUTTON]:
                [regions, fRegion] = \
                          self.brailleGenerator.generateBraille(obj)

                if isFocusedObj:
                    focusedRegion = fRegion

            else:
                regions = [self.getNewBrailleText(obj,
                                                  startOffset=startOffset,
                                                  endOffset=endOffset)]

                if role == pyatspi.ROLE_CAPTION:
                    regions.append(self.getNewBrailleRegion(
                        " " + self.brailleGenerator.getLocalizedRoleName(obj)))

                if isFocusedObj:
                    focusedRegion = regions[0]

            # We only want to display the heading role and level if we
            # have found the final item in that heading, or if that
            # heading contains no children.
            #
            isLastObject = (i == len(contents) - 1)
            if role == pyatspi.ROLE_HEADING \
               and (isLastObject or not obj.childCount):
                heading = obj
            elif isLastObject:
                heading = self.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_HEADING], [pyatspi.ROLE_DOCUMENT_FRAME])
            else:
                heading = None

            if heading:
                level = self.getHeadingLevel(heading)
                headingString = \
                    object_properties.ROLE_HEADING_LEVEL_BRAILLE % level
                if not string.endswith(" "):
                    headingString = " " + headingString
                if not isLastObject:
                    headingString += " "
                regions.append(self.getNewBrailleRegion((headingString)))

            # Add whitespace if we need it. [[[TODO: JD - But should we be
            # doing this in the braille generators rather than here??]]]
            #
            if regions and len(line.regions) \
               and regions[0].string and line.regions[-1].string \
               and not regions[0].string[0] in whitespace \
               and not line.regions[-1].string[-1] in whitespace:

                # There is nothing separating the previous braille region from
                # this one. We might or might not want to add some whitespace
                # for readability.
                #
                lastObj = contents[i - 1][0]

                # If we have two of the same braille class, or if the previous
                # region is a component or a generic region, or an image link,
                # we should add some space.
                #
                if line.regions[-1].__class__ == regions[0].__class__ \
                   or line.regions[-1].__class__ in [braille.Component,
                                                     braille.Region] \
                   or lastObj.getRole() == pyatspi.ROLE_IMAGE \
                   or obj.getRole() == pyatspi.ROLE_IMAGE:
                    self.addToLineAsBrailleRegion(" ", line)

                # The above check will catch table cells with uniform
                # contents and form fields -- and do so more efficiently
                # than walking up the hierarchy. But if we have a cell
                # with text next to a cell with a link.... Ditto for
                # sections on the same line.
                #
                else:
                    layoutRoles = [pyatspi.ROLE_TABLE_CELL,
                                   pyatspi.ROLE_SECTION,
                                   pyatspi.ROLE_LIST_ITEM]
                    if role in layoutRoles:
                        acc1 = obj
                    else:
                        acc1 = self.utilities.ancestorWithRole(
                            obj, layoutRoles, [pyatspi.ROLE_DOCUMENT_FRAME])
                    if acc1:
                        if lastObj.getRole() == acc1.getRole():
                            acc2 = lastObj
                        else:
                            acc2 = self.utilities.ancestorWithRole(
                                lastObj,
                                layoutRoles,
                                [pyatspi.ROLE_DOCUMENT_FRAME])
                        if not self.utilities.isSameObject(acc1, acc2):
                            self.addToLineAsBrailleRegion(" ", line)

            self.addBrailleRegionsToLine(regions, line)

            if isLastObject:
                line.regions[-1].string = line.regions[-1].string.rstrip(" ")

            # If we're inside of a combo box, we only want to display
            # the selected menu item.
            #
            if obj.getRole() == pyatspi.ROLE_MENU_ITEM \
               and obj.getState().contains(pyatspi.STATE_FOCUSED):
                break

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
        text = self.utilities.queryNonEmptyText(obj)
        if text:
            # If the caret is at the end of text and we're not in an
            # entry, something bad is going on, so decrement the offset
            # before speaking the character.
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string) \
               and not obj.getState().contains(pyatspi.STATE_EDITABLE):
                print("YIKES in Gecko.sayCharacter!")
                characterOffset -= 1

        if characterOffset >= 0:
            self.speakCharacterAtOffset(obj, characterOffset)

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent():
            default.Script.sayWord(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        text = self.utilities.queryNonEmptyText(obj)
        if text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the previous word.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next word via
            # a call to goNextWord.]]]
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string) \
               and not obj.getState().contains(pyatspi.STATE_EDITABLE):
                print("YIKES in Gecko.sayWord!")
                characterOffset -= 1

        # Ideally in an entry we would just let default.sayWord() handle
        # things.  That fails to work when navigating backwords by word.
        # Because getUtterancesFromContents() now uses the speech_generator
        # with entries, we need to handle word navigation in entries here.
        #
        wordContents = self.getWordContentsAtOffset(obj, characterOffset)
        [textObj, startOffset, endOffset, word] = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        if not self.utilities.isEntry(textObj):
            self.speakContents(wordContents)
        else:
            word = self.utilities.substring(textObj, startOffset, endOffset)
            speech.speak([word], self.getACSS(textObj, word))

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
        text = self.utilities.queryNonEmptyText(obj)
        if text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the current line.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next line via
            # a call to goNextLine.]]]
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string) \
               and not obj.getState().contains(pyatspi.STATE_EDITABLE):
                print("YIKES in Gecko.sayLine!")
                characterOffset -= 1

        self.speakContents(self.getLineContentsAtOffset(obj, characterOffset))

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """
        if self.flatReviewContext \
           or self.isAriaWidget(orca_state.locusOfFocus) \
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
           or self.isAriaWidget(orca_state.locusOfFocus) \
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
            role = obj.getRole()
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

        if not script_settings.controlCaretNavigation:
            return False

        if not self.inDocumentContent():
            return False

        if not self.isNavigableAria(orca_state.locusOfFocus):
            return False

        if keyboardEvent.event_string in ["Page_Up", "Page_Down"]:
            return False

        if keyboardEvent.modifiers & settings.SHIFT_MODIFIER_MASK:
            return False

        if self._loadingDocumentContent:
            return False

        if not orca_state.locusOfFocus:
            return False

        weHandleIt = True
        obj = orca_state.locusOfFocus
        role = obj.getRole()
        if self.utilities.isEntry(obj):
            text        = obj.queryText()
            length      = text.characterCount
            caretOffset = text.caretOffset
            singleLine  = obj.getState().contains(
                pyatspi.STATE_SINGLE_LINE)

            # Single line entries have an additional newline character
            # at the end.
            #
            newLineAdjustment = int(not singleLine)

            # Home and End should not be overridden if we're in an
            # entry.
            #
            if keyboardEvent.event_string in ["Home", "End"]:
                return False

            # We want to use our caret navigation model in an entry if
            # there's nothing in the entry, we're at the beginning of
            # the entry and press Left or Up, or we're at the end of the
            # entry and press Right or Down.
            #
            if length == 0 \
               or ((length == 1) and (text.getText(0, -1) == "\n")):
                weHandleIt = True
            elif caretOffset <= 0:
                weHandleIt = keyboardEvent.event_string \
                             in ["Up", "Left"]
            elif caretOffset >= length - newLineAdjustment \
                 and not self._autocompleteVisible:
                weHandleIt = keyboardEvent.event_string \
                             in ["Down", "Right"]
            else:
                weHandleIt = False

            if singleLine and not weHandleIt \
               and not self._autocompleteVisible:
                weHandleIt = keyboardEvent.event_string in ["Up", "Down"]

        elif keyboardEvent.modifiers & settings.ALT_MODIFIER_MASK:
            # Alt+Down Arrow is the Firefox command to expand/collapse the
            # *currently focused* combo box.  When Orca is controlling the
            # caret, it is possible to navigate into a combo box *without
            # giving focus to that combo box*.  Under these circumstances,
            # the menu item has focus.  Because the user knows that he/she
            # is on a combo box, he/she expects to be able to use Alt+Down
            # Arrow to expand the combo box.  Therefore, if a menu item has
            # focus and Alt+Down Arrow is pressed, we will handle it by
            # giving the combo box focus and expanding it as the user
            # expects.  We also want to avoid grabbing focus on a combo box.
            # Therefore, if the caret is immediately before a combo box,
            # we'll hand it the same way.
            #
            if keyboardEvent.event_string == "Down":
                [obj, offset] = self.getCaretContext()
                index = self.getChildIndex(obj, offset)
                if index >= 0:
                    weHandleIt = \
                        obj[index].getRole() == pyatspi.ROLE_COMBO_BOX
                if not weHandleIt:
                    weHandleIt = role == pyatspi.ROLE_MENU_ITEM

        elif role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_MENU_ITEM]:
            weHandleIt = keyboardEvent.event_string in ["Left", "Right"]

        elif role == pyatspi.ROLE_LIST_ITEM:
            weHandleIt = not obj.getState().contains(pyatspi.STATE_FOCUSED)

        elif role == pyatspi.ROLE_LIST:
            weHandleIt = not obj.getState().contains(pyatspi.STATE_FOCUSABLE)

        return weHandleIt

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation.
        This should return False if we're in something like an entry
        or a list.
        """

        letThemDoItEditableRoles = [pyatspi.ROLE_ENTRY,
                                    pyatspi.ROLE_TEXT,
                                    pyatspi.ROLE_PASSWORD_TEXT]
        letThemDoItSelectionRoles = [pyatspi.ROLE_LIST,
                                     pyatspi.ROLE_LIST_ITEM,
                                     pyatspi.ROLE_MENU_ITEM]

        if not self.structuralNavigation.enabled:
            return False

        if not self.isNavigableAria(orca_state.locusOfFocus):
            return False

        if self._loadingDocumentContent:
            return False

        # If the Orca_Modifier key was pressed, we're handling it.
        #
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            mods = orca_state.lastInputEvent.modifiers
            isOrcaKey = mods & settings.ORCA_MODIFIER_MASK
            if isOrcaKey:
                return True

        obj = orca_state.locusOfFocus
        while obj:
            if obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
                # Don't use the structural navivation model if the
                # user is editing the document.
                return not obj.getState().contains(pyatspi.STATE_EDITABLE)
            elif obj.getRole() in letThemDoItEditableRoles:
                return not obj.getState().contains(pyatspi.STATE_EDITABLE)
            elif obj.getRole() in letThemDoItSelectionRoles:
                return not obj.getState().contains(pyatspi.STATE_FOCUSED)
            elif obj.getRole() == pyatspi.ROLE_COMBO_BOX:
                return False
            else:
                obj = obj.parent

        return False

    def isNavigableAria(self, obj):
        """Returns True if the object being examined is an ARIA widget where
           we want to provide Orca keyboard navigation.  Returning False
           indicates that we want Firefox to handle key commands.
        """

        try:
            state = obj.getState()
        except (LookupError, RuntimeError):
            debug.println(debug.LEVEL_SEVERE,
                          "isNavigableAria() - obj no longer exists")
            return True
        except:
            pass
        else:
            # If the current object isn't even showing, we don't want to hand
            # this off to Firefox's native caret navigation because who knows
            # where we'll wind up....
            #
            if not state.contains(pyatspi.STATE_SHOWING):
                return True

        # Sometimes the child of an ARIA widget claims focus. It may lack
        # the attributes we're looking for. Therefore, if obj is not an
        # ARIA widget, we'll also consider the parent's attributes.
        #
        attrs = self._getAttrDictionary(obj)
        if obj and not self.isAriaWidget(obj):
            attrs.update(self._getAttrDictionary(obj.parent))

        try:
            # ARIA landmark widgets
            if set(attrs['xml-roles'].split()).intersection(\
               set(settings.ariaLandmarks)):
                return True
            # ARIA live region
            elif 'container-live' in attrs:
                return True
            # Don't treat links as ARIA widgets. And we should be able to
            # escape/exit ARIA entries just like we do HTML entries (How
            # is the user supposed to know which he/she happens to be in?)
            #
            elif obj.getRole() in [pyatspi.ROLE_ENTRY,
                                   pyatspi.ROLE_LINK,
                                   pyatspi.ROLE_ALERT,
                                   pyatspi.ROLE_PARAGRAPH,
                                   pyatspi.ROLE_SECTION]:
                return obj.parent.getRole() not in [pyatspi.ROLE_COMBO_BOX,
                                                    pyatspi.ROLE_PAGE_TAB]
            # All other ARIA widgets we will assume are navigable if
            # they are not focused.
            #
            else:
                return not obj.getState().contains(pyatspi.STATE_FOCUSABLE)
        except (KeyError, TypeError):
            return True

    def isAriaWidget(self, obj=None):
        """Returns True if the object being examined is an ARIA widget.

        Arguments:
        - obj: The accessible object of interest.  If None, the
        locusOfFocus is examined.
        """
        try:
            return self.generatorCache['isAria'][obj]
        except:
            pass
        obj = obj or orca_state.locusOfFocus

        # TODO - JD: It seems insufficient to take a "if it's ARIA, use
        # the default script" approach. For instance, an ARIA dialog does
        # not have "unrelated labels"; it has embedded object characters
        # just like other Gecko content. Unless and until Gecko exposes
        # ARIA widgets as proper widgets, we'll need to not be so trusting.
        # For now, just add hacks on a per-case basis until there is time
        # to properly review this code.
        try:
            role = obj.getRole()
        except:
            pass
        else:
            if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
                return False

        attrs = self._getAttrDictionary(obj)
        if 'isAria' not in self.generatorCache:
            self.generatorCache['isAria'] = {}
        self.generatorCache['isAria'][obj] = \
            ('xml-roles' in attrs and 'live' not in attrs)
        return self.generatorCache['isAria'][obj]

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

    def getExtents(self, obj, startOffset, endOffset):
        """Returns [x, y, width, height] of the text at the given offsets
        if the object implements accessible text, or just the extents of
        the object if it doesn't implement accessible text.
        """
        if not obj:
            return [0, 0, 0, 0]

        # The menu items that are children of combo boxes have unique
        # extents based on their physical position, even though they are
        # not showing.  Therefore, if the object in question is a menu
        # item, get the object extents rather than the range extents for
        # the text. Similarly, if it's a menu in a combo box, get the
        # extents of the combo box.
        #
        text = self.utilities.queryNonEmptyText(obj)
        if text and obj.getRole() != pyatspi.ROLE_MENU_ITEM:
            extents = text.getRangeExtents(startOffset, endOffset, 0)
        elif obj.getRole() == pyatspi.ROLE_MENU \
             and obj.parent.getRole() == pyatspi.ROLE_COMBO_BOX:
            ext = obj.parent.queryComponent().getExtents(0)
            extents = [ext.x, ext.y, ext.width, ext.height]
        else:
            ext = obj.queryComponent().getExtents(0)
            extents = [ext.x, ext.y, ext.width, ext.height]
        return extents

    def onSameLine(self, a, b, pixelDelta=5):
        """Determine if extents a and b are on the same line.

        Arguments:
        -a: [x, y, width, height]
        -b: [x, y, width, height]

        Returns True if a and b are on the same line.
        """

        # If a and b are identical, by definition they are on the same line.
        #
        if a == b:
            return True

        # For now, we'll just take a look at the bottom of the area.
        # The code after this takes the whole extents into account,
        # but that logic has issues in the case where we have
        # something very tall next to lots of shorter lines (e.g., an
        # image with lots of text to the left or right of it.  The
        # number 11 here represents something that seems to work well
        # with superscripts and subscripts on a line as well as pages
        # with smaller fonts on them, such as craig's list.
        #
        if abs(a[1] - b[1]) > 11:
            return False

        # If there's an overlap of 1 pixel or less, they are on different
        # lines.  Keep in mind "lowest" and "highest" mean visually on the
        # screen, but that the value is the y coordinate.
        #
        highestBottom = min(a[1] + a[3], b[1] + b[3])
        lowestTop     = max(a[1],        b[1])
        if lowestTop >= highestBottom - 1:
            return False

        return True

        # If we do overlap, lets see how much.  We'll require a 25% overlap
        # for now...
        #
        #if lowestTop < highestBottom:
        #    overlapAmount = highestBottom - lowestTop
        #    shortestHeight = min(a[3], b[3])
        #    return ((1.0 * overlapAmount) / shortestHeight) > 0.25
        #else:
        #    return False

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

    def getAutocompleteEntry(self, obj):
        """Returns the ROLE_ENTRY object of a ROLE_AUTOCOMPLETE object or
        None if the entry cannot be found.
        """

        for child in obj:
            if child and (child.getRole() == pyatspi.ROLE_ENTRY):
                return child

        return None

    def getCellCoordinates(self, obj):
        """Returns the [row, col] of a ROLE_TABLE_CELL or [0, 0]
        if the coordinates cannot be found.
        """
        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            obj = self.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_TABLE_CELL], [pyatspi.ROLE_DOCUMENT_FRAME])

        parentTable = self.utilities.ancestorWithRole(
            obj, [pyatspi.ROLE_TABLE], [pyatspi.ROLE_DOCUMENT_FRAME])
        try:
            table = parentTable.queryTable()
        except:
            pass
        else:
            index = self.utilities.cellIndex(obj)
            row = table.getRowAtIndex(index)
            col = table.getColumnAtIndex(index)
            return [row, col]

        return [0, 0]

    def isBlankCell(self, obj):
        """Returns True if the table cell is empty or consists of a single
        non-breaking space.

        Arguments:
        - obj: the table cell to examime
        """

        text = self.utilities.displayedText(obj)
        if text and text != '\u00A0':
            return False
        else:
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LINK:
                    return False

            return True

    def isFormField(self, obj):
        """Returns True if the given object is a field inside of a form."""

        if not obj or not self.inDocumentContent(obj):
            return False

        formRoles = [pyatspi.ROLE_CHECK_BOX,
                     pyatspi.ROLE_RADIO_BUTTON,
                     pyatspi.ROLE_COMBO_BOX,
                     pyatspi.ROLE_DOCUMENT_FRAME,
                     pyatspi.ROLE_LIST,
                     pyatspi.ROLE_ENTRY,
                     pyatspi.ROLE_PASSWORD_TEXT,
                     pyatspi.ROLE_PUSH_BUTTON]

        state = obj.getState()
        isField = obj.getRole() in formRoles \
                  and state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        if obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            isField = isField and state.contains(pyatspi.STATE_EDITABLE)

        return isField

    def isUselessObject(self, obj):
        """Returns true if the given object is an obj that doesn't
        have any meaning associated with it and it is not inside a
        link."""

        if not obj:
            return True

        useless = False

        textObj = self.utilities.queryNonEmptyText(obj)
        if not textObj and obj.getRole() == pyatspi.ROLE_PARAGRAPH:
            # Under these circumstances, this object is useless even
            # if it is the child of a link.
            #
            return True
        elif obj.getRole() in [pyatspi.ROLE_IMAGE, \
                               pyatspi.ROLE_TABLE_CELL, \
                               pyatspi.ROLE_SECTION]:
            text = self.utilities.displayedText(obj)
            if (not text) or (len(text) == 0):
                text = self.utilities.displayedLabel(obj)
                if (not text) or (len(text) == 0):
                    useless = True

        if useless:
            link = self.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
            if link:
                if obj.getRole() == pyatspi.ROLE_IMAGE:
                    # If this object had alternative text and/or a title,
                    # we wouldn't be here. We need to determine if this
                    # image is indeed worth presenting and not a duplicate
                    # piece of information. See Facebook's timeline and/or
                    # bug 584540.
                    #
                    for child in obj.parent:
                        if self.utilities.displayedText(child):
                            # Some other sibling is presenting information.
                            # We'll treat this image as useless.
                            #
                            break
                    else:
                        # No other siblings are presenting information.
                        #
                        if obj.parent.getRole() == pyatspi.ROLE_LINK:
                            if not link.name:
                                # If no siblings are presenting information,
                                # but the link had a name, then we'd know we
                                # had text along with the image(s). Given the
                                # lack of name, we'll treat the first image as
                                # the useful one and ignore the rest.
                                #
                                useless = obj.getIndexInParent() > 0
                        else:
                            # The image must be in a paragraph or section or
                            # heading or something else that might result in
                            # it being on its own line.
                            #
                            textObj = \
                                self.utilities.queryNonEmptyText(obj.parent)
                            if textObj:
                                text = textObj.getText(0, -1)
                                text = text.replace(\
                                    self.EMBEDDED_OBJECT_CHARACTER, "").strip()
                                if not text:
                                    # There's no other text on this line inside
                                    # of this link. We don't want to skip over
                                    # this line, so we'll treat the first image
                                    # as useful.
                                    #
                                    useless = obj.getIndexInParent() > 0
                else:
                    useless = False

        return useless

    def pursueForFlatReview(self, obj):
        """Determines if we should look any further at the object
        for flat review."""

        # It should be enough to check for STATE_SHOWING, but Gecko seems
        # to reverse STATE_SHOWING and STATE_VISIBLE, exposing STATE_SHOWING
        # for objects which are offscreen. So, we'll check for both. See
        # bug #542833. [[[TODO - JD: We're putting this check in just this
        # script for now to be on the safe side. Consider for the default
        # script as well?]]]
        #
        try:
            state = obj.getState()
        except:
            pass
            return False
        else:
            return state.contains(pyatspi.STATE_SHOWING) \
                   and state.contains(pyatspi.STATE_VISIBLE)
 
    def getHeadingLevel(self, obj):
        """Determines the heading level of the given object.  A value
        of 0 means there is no heading level."""

        level = 0

        if obj is None:
            return level

        if obj.getRole() == pyatspi.ROLE_HEADING:
            attributes = obj.getAttributes()
            if attributes is None:
                return level
            for attribute in attributes:
                if attribute.startswith("level:"):
                    level = int(attribute.split(":")[1])
                    break

        return level

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

    def getMeaningfulObjectsFromLine(self, line):
        """Attempts to strip a list of (obj, start, end) tuples into one
        that contains only meaningful objects."""

        if not line or not len(line):
            return []

        lineContents = []
        for item in line:
            role = item[0].getRole()

            # If it's labelling something on this line, don't move to
            # it.
            #
            if role == pyatspi.ROLE_LABEL \
               and self.isLabellingContents(item[0], line):
                continue

            # Rather than do a brute force label infer, we'll focus on
            # entries as they are the most common and their label is
            # likely on this line.  The functional label may be made up
            # of several objects, so we'll examine the strings of what
            # we've got and pop off the ones that match.
            #
            elif self.utilities.isEntry(item[0]):
                label = \
                    self.labelInference.inferFromTextLeft(item[0]) \
                    or self.labelInference.inferFromTextRight(item[0]) 
                index = len(lineContents) - 1
                while label and index >= 0:
                    prevItem = lineContents[index]
                    prevText = self.utilities.queryNonEmptyText(prevItem[0])
                    if prevText:
                        string = prevText.getText(prevItem[1], prevItem[2])
                        if label.endswith(string):
                            lineContents.pop()
                            length = len(label) - len(string)
                            label = label[0:length]
                        else:
                            break
                    index -= 1

            else:
                text = self.utilities.queryNonEmptyText(item[0])
                if text:
                    string = text.getText(item[1], item[2])
                    if not len(string.strip()):
                        continue

            lineContents.append(item)

        return lineContents

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

        if role == pyatspi.ROLE_LIST_ITEM and not characterOffset and obj.name:
            words = obj.name.split()
            characterOffset = len(words[0])

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
                                             pyatspi.ROLE_LIST]

        text = self.utilities.queryNonEmptyText(obj)
        if text:
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
        elif obj.childCount and obj[0] and not doNotDescend:
            try:
                return self.findNextCaretInOrder(obj[0],
                                                 -1,
                                                 includeNonText)
            except:
                pass

        elif includeNonText and (startOffset < 0):
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
                                             pyatspi.ROLE_LIST]

        text = self.utilities.queryNonEmptyText(obj)
        if text:
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
        elif obj.childCount and obj[obj.childCount - 1] and not doNotDescend:
            try:
                return self.findPreviousCaretInOrder(
                    obj[obj.childCount - 1],
                    -1,
                    includeNonText)
            except:
                pass

        elif includeNonText and (startOffset < 0):
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
                if parent.getState().contains(pyatspi.STATE_FOCUSABLE) \
                   and not self.isAriaWidget(parent):
                    return parent

            while previousObj.childCount:
                role = previousObj.getRole()
                state = previousObj.getState()
                if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_MENU]:
                    break
                elif role == pyatspi.ROLE_LIST \
                     and state.contains(pyatspi.STATE_FOCUSABLE) \
                     and not self.isAriaWidget(previousObj):
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
        if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_MENU]:
            descend = False
        elif role == pyatspi.ROLE_LIST \
            and obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
            and not self.isAriaWidget(obj):
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

        self._updateLineCache(obj, characterOffset)

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

        # We'll let the default script handle entries and other entry-like
        # things (e.g. the text portion of a dojo spin button).
        #
        if not self.inDocumentContent(obj) \
           or self.utilities.isEntry(obj) \
           or self.utilities.isPasswordText(obj):
            return default.Script.getTextLineAtCaret(self, obj, offset)

        # Find the current line.
        #
        contextObj, contextOffset = self.getCaretContext()
        contextOffset = max(0, contextOffset)
        contents = self.currentLineContents
        if self.findObjectOnLine(contextObj, contextOffset, contents) < 0:
            contents = self.getLineContentsAtOffset(contextObj, contextOffset)

        # Determine the caretOffset.
        #
        if self.utilities.isSameObject(obj, contextObj):
            caretOffset = contextOffset
        else:
            try:
                text = obj.queryText()
            except:
                caretOffset = 0
            else:
                caretOffset = text.caretOffset

        # The reason we typically use this method is to present the contents
        # of the current line, so our initial assumption is that the obj
        # being passed in is also on this line. We'll try that first. We
        # might have multiple instances of obj, in which case we'll have
        # to consider the offset as well.
        #
        for content in contents:
            candidate, startOffset, endOffset, string = content
            if self.utilities.isSameObject(candidate, obj) \
               and (offset is None or (startOffset <= offset <= endOffset)):
                return string, caretOffset, startOffset

        # If we're still here, obj presumably is not on this line. This
        # shouldn't happen, but if it does we'll let the default script
        # handle it for now.
        #
        #print "getTextLineAtCaret failed"
        return default.Script.getTextLineAtCaret(self, obj, offset)

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
            return None

    def getWordContentsAtOffset(self, obj, characterOffset, boundary=None):
        """Returns an ordered list where each element is composed of an
        [obj, startOffset, endOffset, string] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the given object and characterOffset.  The first element in
        the list represents the beginning of the word.  The last
        element in the list represents the character just before the
        beginning of the next word.

        Arguments:
        -obj: the object to start at
        -characterOffset: the characterOffset in the object
        -boundary: the pyatsi word boundary to use
        """

        if not obj:
            return []

        boundary = boundary or pyatspi.TEXT_BOUNDARY_WORD_START
        text = self.utilities.queryNonEmptyText(obj)
        if text:
            word = text.getTextAtOffset(characterOffset, boundary)
            if word[1] < characterOffset <= word[2]:
                characterOffset = word[1]

        contents = self.utilities.getObjectsFromEOCs(obj, characterOffset, boundary)
        if len(contents) > 1 \
           and contents[0][0].getRole() == pyatspi.ROLE_LIST_ITEM:
            contents = [contents[0]]

        return contents

    def getLineContentsAtOffset(self, obj, offset):
        """Returns an ordered list where each element is composed of an
        [obj, startOffset, endOffset, string] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the given object and characterOffset.  The first element in
        the list represents the beginning of the line.  The last
        element in the list represents the character just before the
        beginning of the next line.

        Arguments:
        -obj: the object to start at
        -offset: the character offset in the object
        """

        if not obj:
            return []
        
        # If it's an ARIA widget, we want the default generators to give
        # us all the details.
        #
        if not self.isNavigableAria(obj):
            if not self.isAriaWidget(obj):
                obj = obj.parent

            objects = [[obj, 0, 1, ""]]
            ext = obj.queryComponent().getExtents(0)
            extents = [ext.x, ext.y, ext.width, ext.height]
            for i in range(obj.getIndexInParent() + 1, obj.parent.childCount):
                newObj = obj.parent[i]
                ext = newObj.queryComponent().getExtents(0)
                newExtents = [ext.x, ext.y, ext.width, ext.height]
                if self.onSameLine(extents, newExtents):
                    objects.append([newObj, 0, 1, ""])
                else:
                    break
            for i in range(obj.getIndexInParent() - 1, -1, -1):
                newObj = obj.parent[i]
                ext = newObj.queryComponent().getExtents(0)
                newExtents = [ext.x, ext.y, ext.width, ext.height]
                if self.onSameLine(extents, newExtents):
                    objects[0:0] = [[newObj, 0, 1, ""]]
                else:
                    break

            return objects

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START

        # Find the beginning of this line w.r.t. this object.
        #
        text = self.utilities.queryNonEmptyText(obj)
        if not text:
            offset = 0
        else:            
            if offset == -1:
                offset = 0

            [line, start, end] = text.getTextAtOffset(offset, boundary)

            # If we're still seeing bogusity, which we only seem to see when
            # moving up, locate the previous character and use it instead.
            #
            if not (start <= offset < end):
                pObj, pOffset = self.findPreviousCaretInOrder(obj, end)
                if pObj:
                    obj, offset = pObj, pOffset
                    text = self.utilities.queryNonEmptyText(obj)
                    if text:
                        [line, start, end] = \
                            text.getTextAtOffset(offset, boundary)

            if start <= offset < end:
                # So far so good. If the line doesn't begin with an EOC, we
                # have our first character for this object.
                #
                try:
                    isEOC = line.startswith(self.EMBEDDED_OBJECT_CHARACTER)
                except:
                    isEOC = False
                if not isEOC:
                    offset = start
                else:
                    # The line may begin with a link, or it may begin with
                    # an anchor which makes this text something one can jump
                    # to via a link. Anchors are bad.
                    #
                    childIndex = self.getChildIndex(obj, start)
                    if childIndex >= 0:
                        child = obj[childIndex]
                        childText = self.utilities.queryNonEmptyText(child)
                        if not childText:
                            # It's probably an anchor. It might be something
                            # else, but that's okay because we do another
                            # check later to make sure we have everything on
                            # the left. Set the offset to just after the
                            # assumed anchor.
                            #
                            offset = start + 1
                        elif obj.getRole() == pyatspi.ROLE_PARAGRAPH \
                             and child.getRole() == pyatspi.ROLE_PARAGRAPH:
                            # We don't normally see nested paragraphs. But
                            # they occur at least when a paragraph begins
                            # with a multi-line-high character. If we set
                            # the beginning of this line to that initial
                            # character, we'll get stuck. See bug 592383.
                            #
                            if end - start > 1 and end - offset == 1:
                                # We must be Up Arrowing. Set the offset to
                                # just past the EOC so that we present the
                                # line rather than saying "blank."
                                #
                                offset = start + 1
                        else:
                            # It's a link that ends on our left. Who knows
                            # where it starts? Might be on the previous
                            # line. We will assume that it begins on this
                            # line if the start offset is 0. However, it
                            # might be an image link which occupies more
                            # than just this line. To be safe, we'll also
                            # look to be sure that the text does not start
                            # with an embedded object character. See bug
                            # 587794.
                            #
                            cOffset = childText.characterCount - 1
                            [cLine, cStart, cEnd] = \
                                childText.getTextAtOffset(cOffset, boundary)
                            if cStart == 0 \
                               and not cLine.startswith(\
                                self.EMBEDDED_OBJECT_CHARACTER) \
                               and obj.getRole() != pyatspi.ROLE_PANEL:
                                # It starts on this line.
                                #
                                obj = child
                                offset = cStart
                            else:
                                offset = start + 1

        extents = self.getExtents(obj, offset, offset + 1)

        # Get the objects on this line.
        #
        objects = self.utilities.getObjectsFromEOCs(obj, offset, boundary)

        # Check for things on the left.
        #
        lastExtents = (0, 0, 0, 0)
        done = False
        while not done:
            [firstObj, start, end, string] = objects[0]
            [prevObj, pOffset] = self.findPreviousCaretInOrder(firstObj, start)
            if not prevObj or self.utilities.isSameObject(prevObj, firstObj):
                break

            text = self.utilities.queryNonEmptyText(prevObj)
            if text:
                line = text.getTextAtOffset(pOffset, boundary)
                pOffset = line[1]
                # If a line begins with a link, getTextAtOffset might
                # return a zero-length string. If we have a valid offset
                # increment the pOffset by 1 before getting the extents.
                #
                if line[1] > 0 and line[1] == line[2]:
                    pOffset += 1

            prevExtents = self.getExtents(prevObj, pOffset, pOffset + 1)
            if self.onSameLine(extents, prevExtents) \
               and extents != prevExtents \
               and lastExtents != prevExtents:
                toAdd = self.utilities.getObjectsFromEOCs(prevObj, pOffset, boundary)
                toAdd = [x for x in toAdd if x not in objects]
                if not toAdd:
                    break

                # Depending on the line, there's a chance that we got our
                # current object as part of toAdd. Check for dupes and just
                # add up to the current object if we find them.
                #
                try:
                    index = toAdd.index(objects[0])
                except:
                    index = len(toAdd)
                objects[0:0] = toAdd[0:index]
            else:
                break

            lastExtents = prevExtents

        # Check for things on the right.
        #
        lastExtents = (0, 0, 0, 0)
        done = False
        while not done:
            [lastObj, start, end, string] = objects[-1]
            [nextObj, nOffset] = self.findNextCaretInOrder(lastObj, end)
            if self.utilities.isSameObject(lastObj, nextObj):
                [nextObj, nOffset] = \
                    self.findNextCaretInOrder(nextObj, nOffset)

            if not nextObj or self.utilities.isSameObject(nextObj, lastObj):
                break

            text = self.utilities.queryNonEmptyText(nextObj)
            if text:
                line = text.getTextAtOffset(nOffset + 1, boundary)
                nOffset = line[1]

            nextExtents = self.getExtents(nextObj, nOffset, nOffset + 1)

            if self.onSameLine(extents, nextExtents) \
               and extents != nextExtents \
               and lastExtents != nextExtents \
               or nextExtents == (0, 0, 0, 0):
                toAdd = self.utilities.getObjectsFromEOCs(nextObj, nOffset, boundary)
                toAdd = [x for x in toAdd if x not in objects]
                objects.extend(toAdd)
                done = not toAdd
            elif (nextObj.getRole() in [pyatspi.ROLE_SECTION,
                                        pyatspi.ROLE_TABLE_CELL] \
                  and self.isUselessObject(nextObj)):
                toAdd = self.utilities.getObjectsFromEOCs(nextObj, nOffset, boundary)
                toAdd = [x for x in toAdd if x not in objects]
                done = True
                for item in toAdd:
                    itemExtents = self.getExtents(item[0], item[1], item[2])
                    if self.onSameLine(extents, itemExtents):
                        objects.append(item)
                        done = False
                    else:
                        done = True
                if done:
                    break
            else:
                break

            lastExtents = nextExtents

        return objects

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

    # [[[TODO: WDW - this needs to be moved to the speech generator.]]]
    #
    def getACSS(self, obj, string):
        """Returns the ACSS to speak anything for the given obj."""

        if obj.getRole() == pyatspi.ROLE_LINK:
            acss = self.voices[settings.HYPERLINK_VOICE]
        elif string and isinstance(string, str) \
            and string.isupper() \
            and string.strip().isalpha():
            acss = self.voices[settings.UPPERCASE_VOICE]
        else:
            acss = self.voices[settings.DEFAULT_VOICE]

        return acss

    def getUtterancesFromContents(self, contents, speakRole=True):
        """Returns a list of [text, acss] tuples based upon the list
        of [obj, startOffset, endOffset, string] tuples passed in.

        Arguments:
        -contents: a list of [obj, startOffset, endOffset, string] tuples
        -speakRole: if True, speak the roles of objects
        """

        if not len(contents):
            return []

        # Even if we want to speakRole, we don't want to do that for the
        # document frame.  And we're going to special-case headings so that
        # that we don't overspeak heading role info, which we're in danger
        # of doing if a heading includes links or images.
        #
        doNotSpeakRoles = [pyatspi.ROLE_DOCUMENT_FRAME,
                           pyatspi.ROLE_HEADING,
                           pyatspi.ROLE_LIST_ITEM,
                           pyatspi.ROLE_TEXT,
                           pyatspi.ROLE_ALERT]

        utterances = []
        prevObj = None
        for content in contents:
            [obj, startOffset, endOffset, string] = content
            string = self.utilities.adjustForRepeats(string)
            role = obj.getRole()

            # If we don't have an object, there's nothing to do. If we have
            # a string, but it consists solely of spaces, we have nothing to
            # say. If it's a label for an object in our contents, we'll get
            # that label via the speech generator for the object.
            #
            if not obj \
               or len(string) and not len(string.strip(" ")) \
               or self.isLabellingContents(obj, contents):
                continue

            # TODO - JD: this is a temporary and sad hack borrowed from
            # clumpUtterances() which is no longer called by speakContents().
            # Ultimately this sort of crap belongs in a generator (along with
            # other similiar crap).
            if string == "\n" and len(contents) == 1 \
               and _settingsManager.getSetting('speakBlankLines'):
                string = messages.BLANK

            # Thunderbird now does something goofy with smileys in
            # email: exposes them as a nested paragraph with a name
            # consisting of the punctuation used to create the smiley
            # and an empty accessible text object. This causes us to
            # speak tutorial info for each smiley. :-( type in text.
            #
            elif role == pyatspi.ROLE_PARAGRAPH and not len(string):
                string = obj.name
                # We also see goofiness in some pages. That can cause
                # SayAll by Sentence to spit up. See bug 591351. So
                # if we still do not have string and if we've got
                # more than object in contents, let's dump this one.
                #
                if len(contents) > 1 and not len(string):
                    continue

            # If it is a "useless" image (i.e. not a link, no associated
            # text), ignore it, unless it's the only thing here.
            #
            elif role == pyatspi.ROLE_IMAGE and self.isUselessObject(obj) \
                 and len(contents) > 1:
                continue

            # If the focused item is a checkbox or a radio button for which
            # we had to infer the label, odds are that the inferred label is
            # immediately to the right. Under these circumstances, we'll
            # double speak the "label". It would be nice to avoid that.
            # [[[TODO - JD: This is the simple version. It does not handle
            # the possibility of the fake label being comprised of multiple
            # objects.]]]
            #
            if prevObj \
               and prevObj.getRole() in [pyatspi.ROLE_CHECK_BOX,
                                         pyatspi.ROLE_RADIO_BUTTON] \
               and prevObj.getState().contains(pyatspi.STATE_FOCUSED):
                if self.labelInference.infer(prevObj) == string.strip():
                    continue

            # If we don't have a string, then use the speech generator.
            # Otherwise, we'll want to speak the string and possibly the
            # role.
            #
            if not len(string) \
               or self.utilities.isEntry(obj) \
               or self.utilities.isPasswordText(obj) \
               or role == pyatspi.ROLE_PUSH_BUTTON and obj.name:
                rv = self.speechGenerator.generateSpeech(obj)
                # Crazy crap to make clump and friends happy until we can
                # kill them. (They don't deal well with what the speech
                # generator provides.)
                for item in rv:
                    if isinstance(item, str):
                        utterances.append([item, self.getACSS(obj, item)])
            else:
                utterances.append([string, self.getACSS(obj, string)])
                if speakRole and not role in doNotSpeakRoles:
                    utterance = self.speechGenerator.getRoleName(obj)
                    if utterance:
                        utterances.append(utterance)
  
            # If the object is a heading, or is contained within a heading,
            # speak that role information at the end of the object.
            #
            isLastObject = (contents.index(content) == (len(contents) - 1))
            isHeading = (role == pyatspi.ROLE_HEADING)
            if speakRole and (isLastObject or isHeading):
                if isHeading:
                    heading = obj
                else:
                    heading = self.utilities.ancestorWithRole(
                        obj,
                        [pyatspi.ROLE_HEADING],
                        [pyatspi.ROLE_DOCUMENT_FRAME])

                if heading:
                    utterance = self.speechGenerator.getRoleName(heading)
                    if utterance:
                        utterances.append(utterance)

            prevObj = obj

        return utterances

    def clumpUtterances(self, utterances):
        """Returns a list of utterances clumped together by acss.

        Arguments:
        -utterances: unclumped utterances
        -speakRole: if True, speak the roles of objects
        """

        clumped = []

        for [element, acss] in utterances:
            if len(clumped) == 0:
                clumped = [[element, acss]]
            elif acss == clumped[-1][1] \
                 and isinstance(element, str) \
                 and isinstance(clumped[-1][0], str):
                clumped[-1][0] = clumped[-1][0].rstrip(" ")
                clumped[-1][0] += " " + element
            else:
                clumped.append([element, acss])

        if (len(clumped) == 1) and (clumped[0][0] == "\n"):
            if _settingsManager.getSetting('speakBlankLines'):
                return [[messages.BLANK, self.voices[settings.SYSTEM_VOICE]]]

        if len(clumped) and isinstance(clumped[-1][0], str):
            clumped[-1][0] = clumped[-1][0].rstrip(" ")

        return clumped

    def speakContents(self, contents, speakRole=True):
        """Speaks each string in contents using the associated voice/acss"""
        utterances = self.getUtterancesFromContents(contents, speakRole)
        for utterance in utterances:
            speech.speak(utterance, interrupt=False)

    def speakCharacterAtOffset(self, obj, characterOffset):
        """Speaks the character at the given characterOffset in the
        given object."""
        character = self.getCharacterAtOffset(obj, characterOffset)
        self.speakMisspelledIndicator(obj, characterOffset)
        if obj:
            if character and character != self.EMBEDDED_OBJECT_CHARACTER:
                speech.speakCharacter(character,
                                      self.getACSS(obj, character))
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

        # To be consistent with Gecko's native navigation, we want to move
        # to the next (or technically the previous) word start boundary.
        #
        boundary = pyatspi.TEXT_BOUNDARY_WORD_START
        contents = self.getWordContentsAtOffset(obj, characterOffset, boundary)
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
            contents = \
                self.getWordContentsAtOffset(obj, characterOffset, boundary)
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

        # To be consistent with Gecko's native navigation, we want to
        # move to the next word end boundary.
        #
        boundary = pyatspi.TEXT_BOUNDARY_WORD_START
        contents = self.getWordContentsAtOffset(obj, characterOffset, boundary)
        if not (len(contents) and contents[-1][2]):
            return

        [obj, startOffset, endOffset, string] = contents[-1]
        if string and string[-1].isspace():
            endOffset -= 1
        self.setCaretPosition(obj, endOffset)
        self.updateBraille(obj)
        self.speakMisspelledIndicator(obj, startOffset)
        self.speakContents(contents)

    def findPreviousLine(self, obj, characterOffset, updateCache=True):
        """Locates the caret offset at the previous line in the document
        window.

        Arguments:
        -obj:             the object from which the search should begin
        -characterOffset: the offset within obj from which the search should
                          begin
        -updateCache:     whether or not we should update the line cache

        Returns the [obj, characterOffset] at the beginning of the line.
        """

        if not obj:
            [obj, characterOffset] = self.getCaretContext()

        if not obj:
            return self.getTopOfFile()

        currentLine = self.currentLineContents
        index = self.findObjectOnLine(obj, characterOffset, currentLine)
        if index < 0:
            text = self.utilities.queryNonEmptyText(obj)
            if text and text.characterCount == characterOffset:
                characterOffset -= 1
            currentLine = self.getLineContentsAtOffset(obj, characterOffset)

        prevObj = currentLine[0][0]
        prevOffset = currentLine[0][1]
        [prevObj, prevOffset] = \
            self.findPreviousCaretInOrder(currentLine[0][0], currentLine[0][1])

        extents = self.getExtents(currentLine[0][0],
                                  currentLine[0][1],
                                  currentLine[0][2])
        prevExtents = self.getExtents(prevObj, prevOffset, prevOffset + 1)
        while self.onSameLine(extents, prevExtents) \
              and (extents != prevExtents):
            [prevObj, prevOffset] = \
                self.findPreviousCaretInOrder(prevObj, prevOffset)
            prevExtents = self.getExtents(prevObj, prevOffset, prevOffset + 1)

        # If the user did some back-to-back arrowing, we might already have
        # the line contents.
        #
        prevLine = self._previousLineContents
        index = self.findObjectOnLine(prevObj, prevOffset, prevLine)
        if index < 0:
            prevLine = self.getLineContentsAtOffset(prevObj, prevOffset)

        if not prevLine:
            return [None, -1]

        prevObj = prevLine[0][0]
        prevOffset = prevLine[0][1]

        failureCount = 0
        while failureCount < 5 and prevObj and currentLine == prevLine:
            # For some reason we're stuck. We'll try a few times by
            # caret before trying by object.
            #
            # print "find prev line failed", prevObj, prevOffset
            [prevObj, prevOffset] = \
                      self.findPreviousCaretInOrder(prevObj, prevOffset)
            prevLine = self.getLineContentsAtOffset(prevObj, prevOffset)
            failureCount += 1
        if currentLine == prevLine:
            # print "find prev line still stuck", prevObj, prevOffset
            documentFrame = self.utilities.documentFrame()
            prevObj = self.findPreviousObject(prevObj, documentFrame)
            prevOffset = 0

        [prevObj, prevOffset] = self.findNextCaretInOrder(prevObj,
                                                          prevOffset - 1)

        if not script_settings.arrowToLineBeginning:
            extents = self.getExtents(obj,
                                      characterOffset,
                                      characterOffset + 1)
            oldX = extents[0]
            for item in prevLine:
                extents = self.getExtents(item[0], item[1], item[1] + 1)
                newX1 = extents[0]
                newX2 = newX1 + extents[2]
                if newX1 < oldX <= newX2:
                    newObj = item[0]
                    newOffset = 0
                    text = self.utilities.queryNonEmptyText(prevObj)
                    if text:
                        newY = extents[1] + extents[3] / 2
                        newOffset = text.getOffsetAtPoint(oldX, newY, 0)
                        if 0 <= newOffset <= characterOffset:
                            prevOffset = newOffset
                            prevObj = newObj
                    break

        if updateCache:
            self._nextLineContents = self.currentLineContents
            self.currentLineContents = prevLine

        return [prevObj, prevOffset]

    def findNextLine(self, obj, characterOffset, updateCache=True):
        """Locates the caret offset at the next line in the document
        window.

        Arguments:
        -obj:             the object from which the search should begin
        -characterOffset: the offset within obj from which the search should
                          begin
        -updateCache:     whether or not we should update the line cache

        Returns the [obj, characterOffset] at the beginning of the line.
        """

        if not obj:
            [obj, characterOffset] = self.getCaretContext()

        if not obj:
            return self.getBottomOfFile()

        currentLine = self.currentLineContents
        index = self.findObjectOnLine(obj, characterOffset, currentLine)
        if index < 0:
            currentLine = self.getLineContentsAtOffset(obj, characterOffset)

        [nextObj, nextOffset] = \
            self.findNextCaretInOrder(currentLine[-1][0],
                                      currentLine[-1][2] - 1)

        extents = self.getExtents(currentLine[-1][0],
                                  currentLine[-1][1],
                                  currentLine[-1][2])
        nextExtents = self.getExtents(nextObj, nextOffset, nextOffset + 1)
        while self.onSameLine(extents, nextExtents) \
              and (extents != nextExtents):
            [nextObj, nextOffset] = \
                self.findNextCaretInOrder(nextObj, nextOffset)
            nextExtents = self.getExtents(nextObj, nextOffset, nextOffset + 1)

        # If the user did some back-to-back arrowing, we might already have
        # the line contents.
        #
        nextLine = self._nextLineContents
        index = self.findObjectOnLine(nextObj, nextOffset, nextLine)
        if index < 0:
            nextLine = self.getLineContentsAtOffset(nextObj, nextOffset)

        if not nextLine:
            return [None, -1]

        failureCount = 0
        while failureCount < 5 and nextObj and currentLine == nextLine:
            # For some reason we're stuck. We'll try a few times by
            # caret before trying by object.
            #
            #print "find next line failed", nextObj, nextOffset
            [nextObj, nextOffset] = \
                      self.findNextCaretInOrder(nextObj, nextOffset)
            if nextObj:
                nextLine = self.getLineContentsAtOffset(nextObj, nextOffset)
                failureCount += 1

        if currentLine == nextLine:
            #print "find next line still stuck", nextObj, nextOffset
            documentFrame = self.utilities.documentFrame()
            nextObj = self.findNextObject(nextObj, documentFrame)
            nextOffset = 0

        # On a page which contains tables which are not only nested, but
        # are surrounded by line break characters and/or embedded within
        # a paragraph or span, there's an excellent chance that we'll skip
        # right over the nested content. See bug #555055. If we can detect
        # this condition, we should set the nextOffset to the EOC which
        # represents the nested content before findNextCaretInOrder does
        # its thing.
        #
        if nextOffset == 0 \
           and self.getCharacterAtOffset(nextObj, nextOffset) == "\n" \
           and self.getCharacterAtOffset(nextObj, nextOffset + 1) == \
               self.EMBEDDED_OBJECT_CHARACTER:
            nextOffset += 1

        [nextObj, nextOffset] = \
                  self.findNextCaretInOrder(nextObj, max(0, nextOffset) - 1)

        if not script_settings.arrowToLineBeginning:
            extents = self.getExtents(obj,
                                      characterOffset,
                                      characterOffset + 1)
            oldX = extents[0]
            for item in nextLine:
                extents = self.getExtents(item[0], item[1], item[1] + 1)
                newX1 = extents[0]
                newX2 = newX1 + extents[2]
                if newX1 < oldX <= newX2:
                    newObj = item[0]
                    newOffset = 0
                    text = self.utilities.queryNonEmptyText(nextObj)
                    if text:
                        newY = extents[1] + extents[3] / 2
                        newOffset = text.getOffsetAtPoint(oldX, newY, 0)
                        if newOffset >= 0:
                            nextOffset = newOffset
                            nextObj = newObj
                    break

        if updateCache:
            self._previousLineContents = self.currentLineContents
            self.currentLineContents = nextLine

        return [nextObj, nextOffset]

    def goPreviousLine(self, inputEvent):
        """Positions the caret offset at the previous line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        [obj, characterOffset] = self.getCaretContext()
        [prevObj, prevCharOffset] = self.findPreviousLine(obj, characterOffset)
        if not prevObj:
            return False

        [obj, caretOffset] = self.findFirstCaretContext(prevObj, prevCharOffset)
        self.setCaretPosition(obj, caretOffset)
        self.presentLine(prevObj, prevCharOffset)

        return True

    def goNextLine(self, inputEvent):
        """Positions the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        [obj, characterOffset] = self.getCaretContext()
        [nextObj, nextCharOffset] = self.findNextLine(obj, characterOffset)
        if not nextObj:
            return False

        [obj, caretOffset] = self.findFirstCaretContext(nextObj, nextCharOffset)
        self.setCaretPosition(obj, caretOffset)
        self.presentLine(nextObj, nextCharOffset)

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

    def expandComboBox(self, inputEvent):
        """If focus is on a menu item, but the containing combo box does not
        have focus, give the combo box focus and expand it.  Note that this
        is necessary because with Orca controlling the caret it is possible
        to arrow to a menu item within the combo box without actually giving
        the containing combo box focus.
        """

        [obj, characterOffset] = self.getCaretContext()
        comboBox = None
        if obj.getRole() == pyatspi.ROLE_MENU_ITEM:
            comboBox = self.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_COMBO_BOX], [pyatspi.ROLE_DOCUMENT_FRAME])
        else:
            index = self.getChildIndex(obj, characterOffset)
            if index >= 0:
                comboBox = obj[index]

        if not comboBox:
            return

        try:
            action = comboBox.queryAction()
        except:
            pass
        else:
            orca.setLocusOfFocus(None, comboBox)
            comboBox.queryComponent().grabFocus()
            for i in range(0, action.nActions):
                name = action.getName(i)
                # Translators: this is the action name for the 'open' action.
                #
                if name in ["open", _("open")]:
                    action.doAction(i)
                    break
    def goPreviousObjectInOrder(self, inputEvent):
        """Go to the previous object in order, regardless of type or size."""

        [obj, characterOffset] = self.getCaretContext()

        # Work our way out of form lists and combo boxes.
        #
        if obj and obj.getState().contains(pyatspi.STATE_SELECTABLE):
            obj = obj.parent.parent
            characterOffset = self.utilities.characterOffsetInParent(obj)
            self.currentLineContents = None

        characterOffset = max(0, characterOffset)
        [prevObj, prevOffset] = [obj, characterOffset]
        found = False
        mayHaveGoneTooFar = False

        line = self.currentLineContents \
               or self.getLineContentsAtOffset(obj, characterOffset)
        startingPoint = line
        useful = self.getMeaningfulObjectsFromLine(line)

        while line and not found:
            index = self.findObjectOnLine(prevObj, prevOffset, useful)
            if not self.utilities.isSameObject(obj, prevObj):
                # The question is, have we found the beginning of this
                # object?  If the offset is 0 or there's more than one
                # object on this line and we started on a later line,
                # it's safe to assume we've found the beginning.
                #
                found = (prevOffset == 0) \
                        or (len(useful) > 1 and line != startingPoint)

                # Otherwise, we won't know for certain until we've gone
                # to the line(s) before this one and found a different
                # object, at which point we may have gone too far.
                #
                if not found:
                    mayHaveGoneTooFar = True
                    obj = prevObj
                    characterOffset = prevOffset

            elif 0 < index < len(useful):
                prevObj = useful[index - 1][0]
                prevOffset = useful[index - 1][1]
                found = (prevOffset == 0) or (index > 1)
                if not found:
                    mayHaveGoneTooFar = True

            elif self.utilities.isSameObject(obj, prevObj) \
                 and 0 == prevOffset < characterOffset:
                found = True

            if not found:
                self._nextLineContents = line
                prevLine = self.findPreviousLine(line[0][0], line[0][1])
                line = self.currentLineContents
                useful = self.getMeaningfulObjectsFromLine(line)
                prevObj = useful[-1][0]
                prevOffset = useful[-1][1]
                if self.currentLineContents == self._nextLineContents:
                    break

        if not found:
            self.presentMessage(messages.WRAPPING_TO_BOTTOM)
            [prevObj, prevOffset] = self.getBottomOfFile()
            line = self.getLineContentsAtOffset(prevObj, prevOffset)
            useful = self.getMeaningfulObjectsFromLine(line)
            if useful:
                prevObj = useful[-1][0]
                prevOffset = useful[-1][1]
            found = not (prevObj is None)

        elif mayHaveGoneTooFar and self._nextLineContents:
            if not self.utilities.isSameObject(obj, prevObj):
                prevObj = useful[index][0]
                prevOffset = useful[index][1]

        if found:
            self.currentLineContents = line
            self.setCaretPosition(prevObj, prevOffset)
            self.updateBraille(prevObj)
            objectContents = self.getObjectContentsAtOffset(prevObj,
                                                            prevOffset)
            objectContents = [objectContents[0]]
            self.speakContents(objectContents)

    def goNextObjectInOrder(self, inputEvent):
        """Go to the next object in order, regardless of type or size."""

        [obj, characterOffset] = self.getCaretContext()

        # Work our way out of form lists and combo boxes.
        #
        if obj and obj.getState().contains(pyatspi.STATE_SELECTABLE):
            obj = obj.parent.parent
            characterOffset = self.utilities.characterOffsetInParent(obj)
            self.currentLineContents = None

        characterOffset = max(0, characterOffset)
        [nextObj, nextOffset] = [obj, characterOffset]
        found = False

        line = self.currentLineContents \
               or self.getLineContentsAtOffset(obj, characterOffset)

        while line and not found:
            useful = self.getMeaningfulObjectsFromLine(line)
            index = self.findObjectOnLine(nextObj, nextOffset, useful)
            if not self.utilities.isSameObject(obj, nextObj):
                nextObj = useful[0][0]
                nextOffset = useful[0][1]
                found = True
            elif 0 <= index < len(useful) - 1:
                nextObj = useful[index + 1][0]
                nextOffset = useful[index + 1][1]
                found = True
            else:
                self._previousLineContents = line
                [nextObj, nextOffset] = self.findNextLine(line[-1][0],
                                                          line[-1][2])
                line = self.currentLineContents
                if self.currentLineContents == self._previousLineContents:
                    break

        if not found:
            self.presentMessage(messages.WRAPPING_TO_TOP)
            [nextObj, nextOffset] = self.getTopOfFile()
            line = self.getLineContentsAtOffset(nextObj, nextOffset)
            useful = self.getMeaningfulObjectsFromLine(line)
            if useful:
                nextObj = useful[0][0]
                nextOffset = useful[0][1]
            found = not (nextObj is None)

        if found:
            self.currentLineContents = line
            self.setCaretPosition(nextObj, nextOffset)
            self.updateBraille(nextObj)
            objectContents = self.getObjectContentsAtOffset(nextObj,
                                                            nextOffset)
            objectContents = [objectContents[0]]
            self.speakContents(objectContents)

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

    def toggleCaretNavigation(self, inputEvent):
        """Toggles between Firefox native and Orca caret navigation."""

        if script_settings.controlCaretNavigation:
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.removeByHandler(keyBinding.handler)
            script_settings.controlCaretNavigation = False
            string = messages.CARET_CONTROL_GECKO
        else:
            script_settings.controlCaretNavigation = True
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
