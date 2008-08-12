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
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import atk
import gtk
import pyatspi
import re
import time

import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.liveregions as liveregions
import orca.mag as mag
import orca.orca as orca
import orca.orca_state as orca_state
import orca.rolenames as rolenames
import orca.settings as settings
import orca.speech as speech
import orca.speechserver as speechserver

import script_settings
from braille_generator import BrailleGenerator
from speech_generator import SpeechGenerator
from where_am_i import GeckoWhereAmI
from bookmarks import GeckoBookmarks
from structural_navigation import GeckoStructuralNavigation

from orca.orca_i18n import _


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

        # We need to be able to distinguish focus events that are triggered
        # by the call to grabFocus() in setCaretPosition() from those that
        # are valid.  See bug #471537.
        #
        self._objectForFocusGrab = None

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

        # Last focused frame. We are only interested in frame focused events
        # when it is a different frame, so here we store the last frame
        # that recieved state-changed:focused.
        #
        self._currentFrame = None

    def getWhereAmI(self):
        """Returns the "where am I" class for this script.
        """
        return GeckoWhereAmI(self)

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
                        GeckoStructuralNavigation.LIST,
                        GeckoStructuralNavigation.LIST_ITEM,
                        GeckoStructuralNavigation.LIVE_REGION,
                        GeckoStructuralNavigation.PARAGRAPH,
                        GeckoStructuralNavigation.RADIO_BUTTON,
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

        # Debug only.
        #
        self.inputEventHandlers["dumpContentsHandler"] = \
            input_event.InputEventHandler(
                Script.dumpContents,
                "Dumps document content to stdout.")

        self.inputEventHandlers["goNextCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goNextCharacter,
                # Translators: this is for navigating HTML content one
                # character at a time.
                #
                _("Goes to next character."))

        self.inputEventHandlers["goPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousCharacter,
                # Translators: this is for navigating HTML content one
                # character at a time.
                #
               _( "Goes to previous character."))

        self.inputEventHandlers["goNextWordHandler"] = \
            input_event.InputEventHandler(
                Script.goNextWord,
                # Translators: this is for navigating HTML content one
                # word at a time.
                #
                _("Goes to next word."))

        self.inputEventHandlers["goPreviousWordHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousWord,
                # Translators: this is for navigating HTML content one
                # word at a time.
                #
                _("Goes to previous word."))

        self.inputEventHandlers["goNextLineHandler"] = \
            input_event.InputEventHandler(
                Script.goNextLine,
                # Translators: this is for navigating HTML content one
                # line at a time.
                #
                _("Goes to next line."))

        self.inputEventHandlers["goPreviousLineHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousLine,
                # Translators: this is for navigating HTML content one
                # line at a time.
                #
                _("Goes to previous line."))

        self.inputEventHandlers["goTopOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goTopOfFile,
                # Translators: this command will move the user to the
                # beginning of an HTML document.
                #
                _("Goes to the top of the file."))

        self.inputEventHandlers["goBottomOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goBottomOfFile,
                # Translators: this command will move the user to the
                # end of an HTML document.
                #
                _("Goes to the bottom of the file."))

        self.inputEventHandlers["goBeginningOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.goBeginningOfLine,
                # Translators: this command will move the user to the
                # beginning of the line in an HTML document.
                #
                _("Goes to the beginning of the line."))

        self.inputEventHandlers["goEndOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.goEndOfLine,
                # Translators: this command will move the user to the
                # end of the line in an HTML document.
                #
                _("Goes to the end of the line."))

        self.inputEventHandlers["expandComboBoxHandler"] = \
            input_event.InputEventHandler(
                Script.expandComboBox,
                # Translators: this is for causing a collapsed combo box
                # which was reached by Orca's caret navigation to be expanded.
                #
                _("Causes the current combo box to be expanded."))

        self.inputEventHandlers["advanceLivePoliteness"] = \
            input_event.InputEventHandler(
                Script.advanceLivePoliteness,
                # Translators: this is for advancing the live regions
                # politeness setting
                #
                _("Advance live region politeness setting."))

        self.inputEventHandlers["setLivePolitenessOff"] = \
            input_event.InputEventHandler(
                Script.setLivePolitenessOff,
                # Translators: this is for setting all live regions
                # to 'off' politeness.
                #
                _("Set default live region politeness level to off."))

        self.inputEventHandlers["monitorLiveRegions"] = \
            input_event.InputEventHandler(
                Script.monitorLiveRegions,
                # Translators: this is a toggle to monitor live regions
                # or not.
                #
                _("Monitor live regions."))

        self.inputEventHandlers["reviewLiveAnnouncement"] = \
            input_event.InputEventHandler(
                Script.reviewLiveAnnouncement,
                # Translators: this is for reviewing up to nine stored
                # previous live messages.
                #
                _("Review live region announcement."))

        self.inputEventHandlers["goPreviousObjectInOrderHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousObjectInOrder,
                # Translators: this is for navigating between objects
                # (regardless of type) in HTML
                #
                _("Goes to the previous object."))

        self.inputEventHandlers["goNextObjectInOrderHandler"] = \
            input_event.InputEventHandler(
                Script.goNextObjectInOrder,
                # Translators: this is for navigating between objects
                # (regardless of type) in HTML
                #
                _("Goes to the next object."))

        self.inputEventHandlers["toggleCaretNavigationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleCaretNavigation,
                # Translators: Gecko native caret navigation is where
                # Firefox itself controls how the arrow keys move the caret
                # around HTML content.  It's often broken, so Orca needs
                # to provide its own support.  As such, Orca offers the user
                # the ability to switch between the Firefox mode and the
                # Orca mode.
                #
                _("Switches between Gecko native and Orca caret navigation."))

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                # Translators: the Orca "SayAll" command allows the
                # user to press a key and have the entire document in
                # a window be automatically spoken to the user.  If
                # the user presses any key during a SayAll operation,
                # the speech will be interrupted and the cursor will
                # be positioned at the point where the speech was
                # interrupted.
                #
                _("Speaks entire document."))

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["document:reload"]                        = \
            self.onDocumentReload
        listeners["document:load-complete"]                 = \
            self.onDocumentLoadComplete
        listeners["document:load-stopped"]                  = \
            self.onDocumentLoadStopped
        listeners["object:state-changed:showing"]           = \
            self.onStateChanged
        listeners["object:state-changed:checked"]           = \
            self.onStateChanged
        listeners["object:state-changed:indeterminate"]     = \
            self.onStateChanged
        listeners["object:state-changed:busy"]              = \
            self.onStateChanged
        listeners["object:children-changed"]                = \
            self.onChildrenChanged
        listeners["object:text-changed:insert"]             = \
            self.onTextInserted
        listeners["object:state-changed:focused"]           = \
            self.onStateFocused

        # [[[TODO: HACK - WDW we need to accomodate Gecko's incorrect
        # use of underscores instead of dashes until they fix their bug.
        # See https://bugzilla.mozilla.org/show_bug.cgi?id=368729]]]
        #
        listeners["object:property-change:accessible_value"] = \
            self.onValueChanged

        return listeners

    def __getArrowBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        arrow keys for navigating HTML content.
        """

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["goNextCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["goPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                settings.defaultModifierMask,
                settings.CTRL_MODIFIER_MASK,
                self.inputEventHandlers["goNextWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                settings.defaultModifierMask,
                settings.CTRL_MODIFIER_MASK,
                self.inputEventHandlers["goPreviousWordHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Up",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["goPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["goNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Down",
                settings.defaultModifierMask,
                settings.ALT_MODIFIER_MASK,
                self.inputEventHandlers["expandComboBoxHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Home",
                settings.defaultModifierMask,
                settings.CTRL_MODIFIER_MASK,
                self.inputEventHandlers["goTopOfFileHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "End",
                settings.defaultModifierMask,
                settings.CTRL_MODIFIER_MASK,
                self.inputEventHandlers["goBottomOfFileHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Home",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["goBeginningOfLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "End",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["goEndOfLineHandler"]))

        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        # keybindings to provide chat room message history.
        messageKeys = [ "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9" ]
        for messageKey in messageKeys:
            keyBindings.add(
                keybindings.KeyBinding(
                    messageKey,
                    settings.defaultModifierMask,
                    settings.ORCA_MODIFIER_MASK,
                    self.inputEventHandlers["reviewLiveAnnouncement"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                settings.defaultModifierMask,
                settings.SHIFT_MODIFIER_MASK,
                self.inputEventHandlers["setLivePolitenessOff"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                settings.defaultModifierMask,
                settings.ORCA_SHIFT_MODIFIER_MASK,
                self.inputEventHandlers["monitorLiveRegions"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "backslash",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["advanceLivePoliteness"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "F12",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleCaretNavigationHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "SunF37",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleCaretNavigationHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Right",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["goNextObjectInOrderHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Left",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["goPreviousObjectInOrderHandler"]))

        if script_settings.controlCaretNavigation:
            for keyBinding in self.__getArrowBindings().keyBindings:
                keyBindings.add(keyBinding)

        bindings = self.structuralNavigation.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application.
        """

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(12)
        gtk.Widget.show(vbox)

        # General ("Page") Navigation frame.
        #
        generalFrame = gtk.Frame()
        gtk.Widget.show(generalFrame)
        gtk.Box.pack_start(vbox, generalFrame, False, False, 5)

        generalAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(generalAlignment)
        gtk.Container.add(generalFrame, generalAlignment)
        gtk.Alignment.set_padding(generalAlignment, 0, 0, 12, 0)

        generalVBox = gtk.VBox(False, 0)
        gtk.Widget.show(generalVBox)
        gtk.Container.add(generalAlignment, generalVBox)

        # Translators: Gecko native caret navigation is where
        # Firefox itself controls how the arrow keys move the caret
        # around HTML content.  It's often broken, so Orca needs
        # to provide its own support.  As such, Orca offers the user
        # the ability to switch between the Firefox mode and the
        # Orca mode.
        #
        label = _("Use _Orca Caret Navigation")
        self.controlCaretNavigationCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.controlCaretNavigationCheckButton)
        gtk.Box.pack_start(generalVBox,
                           self.controlCaretNavigationCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.controlCaretNavigationCheckButton,
                                    script_settings.controlCaretNavigation)

        # Translators: Orca provides keystrokes to navigate HTML content
        # in a structural manner: go to previous/next header, list item,
        # table, etc.
        #
        label = _("Use Orca _Structural Navigation")
        self.structuralNavigationCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.structuralNavigationCheckButton)
        gtk.Box.pack_start(generalVBox, self.structuralNavigationCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.structuralNavigationCheckButton,
                                    self.structuralNavigation.enabled)

        # Translators: when the user arrows up and down in HTML content,
        # it is some times beneficial to always position the cursor at the
        # beginning of the line rather than guessing the position directly
        # above the current cursor position.  This option allows the user
        # to decide the behavior they want.
        #
        label = \
            _("_Position cursor at start of line when navigating vertically")
        self.arrowToLineBeginningCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.arrowToLineBeginningCheckButton)
        gtk.Box.pack_start(generalVBox, self.arrowToLineBeginningCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.arrowToLineBeginningCheckButton,
                                    script_settings.arrowToLineBeginning)

        # Translators: when the user loads a new page in Firefox, they
        # can optionally tell Orca to automatically start reading a
        # page from beginning to end.
        #
        label = \
            _("Automatically start speaking a page when it is first _loaded")
        self.sayAllOnLoadCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.sayAllOnLoadCheckButton)
        gtk.Box.pack_start(generalVBox, self.sayAllOnLoadCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.sayAllOnLoadCheckButton,
                                    script_settings.sayAllOnLoad)

        # Translators: this is the title of a panel holding options for
        # how to navigate HTML content (e.g., Orca caret navigation,
        # positioning of caret, etc.).
        #
        generalLabel = gtk.Label("<b>%s</b>" % _("Page Navigation"))
        gtk.Widget.show(generalLabel)
        gtk.Frame.set_label_widget(generalFrame, generalLabel)
        gtk.Label.set_use_markup(generalLabel, True)

        # Table Navigation frame.
        #
        tableFrame = gtk.Frame()
        gtk.Widget.show(tableFrame)
        gtk.Box.pack_start(vbox, tableFrame, False, False, 5)

        tableAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(tableAlignment)
        gtk.Container.add(tableFrame, tableAlignment)
        gtk.Alignment.set_padding(tableAlignment, 0, 0, 12, 0)

        tableVBox = gtk.VBox(False, 0)
        gtk.Widget.show(tableVBox)
        gtk.Container.add(tableAlignment, tableVBox)

        # Translators: this is an option to tell Orca whether or not it
        # should speak table cell coordinates in HTML content.
        #
        label = _("Speak _cell coordinates")
        self.speakCellCoordinatesCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellCoordinatesCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellCoordinatesCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellCoordinatesCheckButton,
                                    settings.speakCellCoordinates)

        # Translators: this is an option to tell Orca whether or not it
        # should speak the span size of a table cell (e.g., how many
        # rows and columns a particular table cell spans in a table).
        #
        label = _("Speak _multiple cell spans")
        self.speakCellSpanCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellSpanCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellSpanCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellSpanCheckButton,
                                    settings.speakCellSpan)

        # Translators: this is an option for whether or not to speak
        # the header of a table cell in HTML content.
        #
        label = _("Announce cell _header")
        self.speakCellHeadersCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellHeadersCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellHeadersCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellHeadersCheckButton,
                                    settings.speakCellHeaders)

        # Translators: this is an option to allow users to skip over
        # empty/blank cells when navigating tables in HTML content.
        #
        label = _("Skip _blank cells")
        self.skipBlankCellsCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.skipBlankCellsCheckButton)
        gtk.Box.pack_start(tableVBox, self.skipBlankCellsCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.skipBlankCellsCheckButton,
                                    settings.skipBlankCells)

        # Translators: this is the title of a panel containing options
        # for specifying how to navigate tables in HTML content.
        #
        tableLabel = gtk.Label("<b>%s</b>" % _("Table Navigation"))
        gtk.Widget.show(tableLabel)
        gtk.Frame.set_label_widget(tableFrame, tableLabel)
        gtk.Label.set_use_markup(tableLabel, True)

        # Find Options frame.
        #
        findFrame = gtk.Frame()
        gtk.Widget.show(findFrame)
        gtk.Box.pack_start(vbox, findFrame, False, False, 5)

        findAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(findAlignment)
        gtk.Container.add(findFrame, findAlignment)
        gtk.Alignment.set_padding(findAlignment, 0, 0, 12, 0)

        findVBox = gtk.VBox(False, 0)
        gtk.Widget.show(findVBox)
        gtk.Container.add(findAlignment, findVBox)

        # Translators: this is an option to allow users to have Orca
        # automatically speak the line that contains the match while
        # the user is still in Firefox's Find toolbar.
        #
        label = _("Speak results during _find")
        self.speakResultsDuringFindCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakResultsDuringFindCheckButton)
        gtk.Box.pack_start(findVBox, self.speakResultsDuringFindCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakResultsDuringFindCheckButton,
                                    script_settings.speakResultsDuringFind)

        # Translators: this is an option which dictates whether the line
        # that contains the match from the Find toolbar should always
        # be spoken, or only spoken if it is a different line than the
        # line which contained the last match.
        #
        label = _("Onl_y speak changed lines during find")
        self.changedLinesOnlyCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.changedLinesOnlyCheckButton)
        gtk.Box.pack_start(findVBox, self.changedLinesOnlyCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.changedLinesOnlyCheckButton,
                              script_settings.onlySpeakChangedLinesDuringFind)

        hbox = gtk.HBox(False, 0)
        gtk.Widget.show(hbox)
        gtk.Box.pack_start(findVBox, hbox, False, False, 0)

        # Translators: this option allows the user to specify the number
        # of matched characters that must be present before Orca speaks
        # the line that contains the results from the Find toolbar.
        #
        self.minimumFindLengthLabel = \
              gtk.Label(_("Minimum length of matched text:"))
        self.minimumFindLengthLabel.set_alignment(0, 0.5)
        gtk.Widget.show(self.minimumFindLengthLabel)
        gtk.Box.pack_start(hbox, self.minimumFindLengthLabel, False, False, 5)

        self.minimumFindLengthAdjustment = \
                   gtk.Adjustment(script_settings.minimumFindLength, 0, 20, 1)
        self.minimumFindLengthSpinButton = \
                       gtk.SpinButton(self.minimumFindLengthAdjustment, 0.0, 0)
        gtk.Widget.show(self.minimumFindLengthSpinButton)
        gtk.Box.pack_start(hbox, self.minimumFindLengthSpinButton,
                           False, False, 5)

        acc_targets = []
        acc_src = self.minimumFindLengthLabel.get_accessible()
        relation_set = acc_src.ref_relation_set()
        acc_targ = self.minimumFindLengthSpinButton.get_accessible()
        acc_targets.append(acc_targ)
        relation = atk.Relation(acc_targets, 1)
        relation.set_property('relation-type', atk.RELATION_LABEL_FOR)
        relation_set.add(relation)

        # Translators: this is the title of a panel containing options
        # for using Firefox's Find toolbar.
        #
        findLabel = gtk.Label("<b>%s</b>" % _("Find Options"))
        gtk.Widget.show(findLabel)
        gtk.Frame.set_label_widget(findFrame, findLabel)
        gtk.Label.set_use_markup(findLabel, True)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        prefs.writelines("\n")
        prefix = "orca.scripts.toolkits.Gecko.script_settings"

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
        settings.speakCellCoordinates = value

        value = self.speakCellSpanCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellSpan = %s\n" % value)
        settings.speakCellSpan = value

        value = self.speakCellHeadersCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellHeaders = %s\n" % value)
        settings.speakCellHeaders = value

        value = self.skipBlankCellsCheckButton.get_active()
        prefs.writelines("orca.settings.skipBlankCells = %s\n" % value)
        settings.skipBlankCells = value

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

        # The reason we override this method is that we only want
        # to consume keystrokes under certain conditions.  For
        # example, we only control the arrow keys when we're
        # managing caret navigation and we're inside document content.
        #
        # [[[TODO: WDW - this might be broken when we're inside a
        # text area that's inside document (or anything else that
        # we want to allow to control its own destiny).]]]

        user_bindings = None
        user_bindings_map = settings.keyBindingsMap
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
        sayAllBySentence = \
                      (settings.sayAllStyle == settings.SAYALL_STYLE_SENTENCE)

        [obj, characterOffset] = self.getCaretContext()
        if sayAllBySentence:
            # Attempt to locate the start of the current sentence by
            # searching to the left for a sentence terminator.  If we don't
            # find one, or if the "say all by" mode is not sentence, we'll
            # just start the sayAll from at the beginning of this line/object.
            #
            text = self.queryNonEmptyText(obj)
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
            for i in xrange(len(clumped)):
                [obj, startOffset, endOffset] = \
                                             contents[min(i, len(contents)-1)]
                if obj.getRole() == pyatspi.ROLE_LABEL \
                   and len(obj.getRelationSet()):
                    # This label is labelling something and will be spoken
                    # in conjunction with the object with which it is
                    # associated.
                    #
                    continue
                [string, voice] = clumped[i]
                string = self.adjustForRepeats(string)
                yield [speechserver.SayAllContext(obj, string,
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
                                         pyatspi.ROLE_PARAGRAPH]:
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

        origObj, origOffset = self.getCaretContext()
        self.setCaretContext(obj, offset)
        origExtents = self.getExtents(origObj, origOffset - 1, origOffset)
        newExtents = self.getExtents(obj, offset - 1, offset)
        text = self.queryNonEmptyText(obj)
        if script_settings.speakResultsDuringFind and text:
            nSelections = text.getNSelections()
            if nSelections:
                [start, end] = text.getSelection(0)
                enoughSelected = (end - start) >= \
                                  script_settings.minimumFindLength
                lineChanged = not self.onSameLine(origExtents, newExtents)

                # If the user starts backspacing over the text in the
                # toolbar entry, he/she is indicating they want to perform
                # a different search. Because madeFindAnnounement may
                # be set to True, we should reset it -- but only if we
                # detect the line has also changed.  We're not getting
                # events from the Find entry, so we have to compare
                # offsets.
                #
                if self.isSameObject(origObj, obj) and (origOffset > offset) \
                   and lineChanged:
                    self.madeFindAnnouncement = False

                if enoughSelected:
                    if lineChanged or not self.madeFindAnnouncement or \
                       not script_settings.onlySpeakChangedLinesDuringFind:
                        line = self.getLineContentsAtOffset(obj, offset)
                        self.speakContents(line)
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

    def getDisplayedText(self, obj):
        """Returns the text being displayed for an object.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.  Overridden in this script because we have lots
        of whitespace we need to remove.
        """

        displayedText = default.Script.getDisplayedText(self, obj)
        if displayedText \
           and not (obj.getState().contains(pyatspi.STATE_EDITABLE) \
                    or obj.getRole() in [pyatspi.ROLE_ENTRY,
                                         pyatspi.ROLE_PASSWORD_TEXT]):
            displayedText = displayedText.strip()
            # Some ARIA widgets (e.g. the list items in the chat box
            # in gmail) implement the accessible text interface but
            # only contain whitespace. Ultimately we should probably
            # identify all of these instances, but for now, let's
            # make gmail work.
            #
            if not displayedText \
               and obj.getRole() == pyatspi.ROLE_LIST_ITEM \
               and obj.getState().contains(pyatspi.STATE_FOCUSED):
                displayedText = obj.name

        return displayedText

    def getDisplayedLabel(self, obj):
        """If there is an object labelling the given object, return the
        text being displayed for the object labelling this object.
        Otherwise, return None.  Overridden here to handle instances
        of bogus labels and form fields where a lack of labels necessitates
        our attempt to guess the text that is functioning as a label.

        Argument:
        - obj: the object in question

        Returns the string of the object labelling this object, or None
        if there is nothing of interest here.
        """

        string = None
        labels = self.findDisplayedLabel(obj)
        for label in labels:
            # Check to see if the official labels are valid.
            #
            bogus = False
            if self.inDocumentContent() \
               and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                     pyatspi.ROLE_LIST]:
                # Bogus case #1:
                # <label></label> surrounding the entire combo box/list which
                # makes the entire combo box's/list's contents serve as the
                # label. We can identify this case because the child of the
                # label is the combo box/list. See bug #428114, #441476.
                #
                if label.childCount:
                    bogus = (label[0].getRole() == obj.getRole())

            if not bogus:
                # Bogus case #2:
                # <label></label> surrounds not just the text serving as the
                # label, but whitespace characters as well (e.g. the text
                # serving as the label is on its own line within the HTML).
                # Because of the Mozilla whitespace bug, these characters
                # will become part of the label which will cause the label
                # and name to no longer match and Orca to seemingly repeat
                # the label.  Therefore, strip out surrounding whitespace.
                # See bug #441610 and
                # https://bugzilla.mozilla.org/show_bug.cgi?id=348901
                #
                expandedLabel = self.expandEOCs(label)
                if expandedLabel:
                    string = self.appendString(string, expandedLabel.strip())

        return string

    def onCaretMoved(self, event):
        """Caret movement in Gecko is somewhat unreliable and
        unpredictable, but we need to handle it.  When we detect caret
        movement, we make sure we update our own notion of the caret
        position: our caretContext is an [obj, characterOffset] that
        points to our current item and character (if applicable) of
        interest.  If our current item doesn't implement the
        accessible text specialization, the characterOffset value
        is meaningless (and typically -1)."""

        eventSourceRole = event.source.getRole()
        eventSourceState = event.source.getState()
        eventSourceInDocument = self.inDocumentContent(event.source)

        try:
            locusOfFocusRole = orca_state.locusOfFocus.getRole()
            locusOfFocusState = orca_state.locusOfFocus.getState()
        except:
            locusOfFocusRole = None
            locusOfFocusState = pyatspi.StateSet()
            locusOfFocusState = locusOfFocusState.raw()

        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            string = orca_state.lastNonModifierKeyEvent.event_string
            if self.useCaretNavigationModel(orca_state.lastInputEvent):
                # Orca is set to control the caret and is in a place where
                # doing so is appropriate.  Therefore, this event is likely
                # extraneous and can be ignored. Exceptions:
                #
                # 1. If the object is an entry and useCaretNavigationModel is
                #    true, then we must be at the edge of the entry and about
                #    to exit it (returning to the document).
                # 2. If the locusOfFocus was a same-page link, we will get a
                #    caret moved event for some object within the document
                #    frame.
                #
                if eventSourceRole != pyatspi.ROLE_ENTRY \
                   and self.isSameObject(event.source, orca_state.locusOfFocus):
                    return

            elif self.isAriaWidget(event.source):
                # Sometimes we get extra caret-moved events. See bug #471878
                # and Mozilla bug #394318. However, we cannot do a blanket
                # ignore of all caret-moved events.  See bug #539075 as an
                # example.
                #
                orca.setLocusOfFocus(event, event.source, False)
                if eventSourceRole == pyatspi.ROLE_SPIN_BUTTON:
                    text = self.queryNonEmptyText(event.source)
                    if text and text.characterCount == event.detail1:
                        return
                elif event.detail1 == 0 \
                     and eventSourceRole in [pyatspi.ROLE_PAGE_TAB,
                                             pyatspi.ROLE_LIST_ITEM,
                                             pyatspi.ROLE_MENU_ITEM]:
                    return

            elif eventSourceInDocument and not self.inDocumentContent() \
                 and orca_state.locusOfFocus:
                # This is an indication that soemthing else is moving
                # the caret on our behalf, such as a help window, the
                # Find toolbar, the UIUC accessiblity extension, etc.
                # If that's the case, we want to update our position.
                # If we're in the Find toolbar, we also want to present
                # the results.
                #
                parent = orca_state.locusOfFocus.parent
                if parent and parent.getRole() == pyatspi.ROLE_TOOL_BAR:
                    self.presentFindResults(event.source, event.detail1)
                else:
                    self.setCaretContext(event.source, event.detail1)
                return

        # If we're still here, and in document content, update the caret
        # context.
        #
        if eventSourceInDocument:
            text = self.queryNonEmptyText(event.source)
            if text:
                caretOffset = text.caretOffset
            else:
                caretOffset = 0

            [obj, characterOffset] = \
                self.findFirstCaretContext(event.source, caretOffset)
            self.setCaretContext(obj, characterOffset)

        # Pass the event along to the default script for processing.
        #
        default.Script.onCaretMoved(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an an object.

        Arguments:
        - event: the Event
        """

        self._destroyLineCache()
        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        self._destroyLineCache()

        # handle live region events
        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

        default.Script.onTextInserted(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed.  In particular, we are looking
        for addition events often associated with Javascipt insertion.  One such
        such example would be the programmatic insertion of a tooltip or alert
        dialog."""
        # no need moving forward if we don't have our target.
        if event.any_data is None:
            return

        # handle live region events
        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

        if event.type.startswith("object:children-changed:add") \
           and event.any_data.getRole() == pyatspi.ROLE_ALERT \
           and event.source.getRole() in [pyatspi.ROLE_SCROLL_PANE,
                                          pyatspi.ROLE_FRAME]:
            utterances = []
            utterances.append(rolenames.getSpeechForRoleName(event.any_data))
            if settings.speechVerbosityLevel == \
                    settings.VERBOSITY_LEVEL_VERBOSE:
                utterances.extend(\
                    self.speechGenerator.getSpeech(event.any_data, False))
            speech.speakUtterances(utterances)

    def onDocumentReload(self, event):
        """Called when the reload button is hit for a web page."""
        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = True

    def onDocumentLoadComplete(self, event):
        """Called when a web page load is completed."""
        # We care about the main document and we'll ignore document
        # events from HTML iframes.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            # Reset the live region manager.
            self.liveMngr.reset()
            self._loadingDocumentContent = False
            self._loadingDocumentTime = time.time()

    def onDocumentLoadStopped(self, event):
        """Called when a web page load is interrupted."""
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
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        try:
            eventSourceRole = event.source.getRole()
        except:
            return

        # Ignore events on the frame as they are often intermingled
        # with menu activity, wreaking havoc on the context. We will
        # ignore autocompletes because we get focus events for the
        # entry, which is the thing that really has focus anyway.
        #
        if eventSourceRole in [pyatspi.ROLE_FRAME,
                               pyatspi.ROLE_AUTOCOMPLETE]:
            return

        # If this event is the result of our calling grabFocus() on
        # this object in setCaretPosition(), we want to ignore it
        # unless it happens to be the same object as our current
        # caret context.
        #
        if self.isSameObject(event.source, self._objectForFocusGrab):
            [obj, characterOffset] = self.getCaretContext()
            if not self.isSameObject(event.source, obj):
                return

        self._objectForFocusGrab = None

        # We also ignore focus events on the panel that holds the document
        # frame.  We end up getting these typically because we've called
        # grabFocus on this panel when we're doing caret navigation.  In
        # those cases, we want the locus of focus to be the subcomponent
        # that really holds the caret.
        #
        if eventSourceRole == pyatspi.ROLE_PANEL:
            documentFrame = self.getDocumentFrame()
            if documentFrame and (documentFrame.parent == event.source):
                return
            else:
                # Web pages can contain their own panels.  If the locus
                # of focus is within that panel, we probably moved off
                # of a focusable item (like a link within the panel)
                # to something non-focusable (like text within the panel).
                # If we don't ignore this event, we'll loop to the top
                # of the panel.
                #
                containingPanel = \
                            self.getAncestor(orca_state.locusOfFocus,
                                             [pyatspi.ROLE_PANEL],
                                             [pyatspi.ROLE_DOCUMENT_FRAME])
                if self.isSameObject(containingPanel, event.source):
                    return

        # When we get a focus event on the document frame, it's usually
        # because we did a grabFocus on its parent in setCaretPosition.
        # We try to handle this here by seeing if there is already a
        # caret context for the document frame.  If we succeed, then
        # we set the focus on the object that's holding the caret.
        #
        if eventSourceRole == pyatspi.ROLE_DOCUMENT_FRAME:
            try:
                [obj, characterOffset] = self.getCaretContext()
                state = obj.getState()
                if not state.contains(pyatspi.STATE_FOCUSED):
                    if not state.contains(pyatspi.STATE_FOCUSABLE) \
                       or not self.inDocumentContent():
                        orca.setLocusOfFocus(event, obj)
                    return
            except:
                pass

        default.Script.onFocus(self, event)

    def onLinkSelected(self, event):
        """Called when a link gets selected.  Note that in Firefox 3,
        link selected events are not issued when a link is selected.
        Instead, a focus: event is issued.  This is 'old' code left
        over from Yelp and Firefox 2.

        Arguments:
        - event: the Event
        """

        text = self.queryNonEmptyText(event.source)
        hypertext = event.source.queryHypertext()
        linkIndex = self.getLinkIndex(event.source, text.caretOffset)

        if linkIndex >= 0:
            link = hypertext.getLink(linkIndex)
            linkText = text.getText(link.startIndex, link.endIndex)
            #[string, startOffset, endOffset] = text.getTextAtOffset(
            #    text.caretOffset,
            #    pyatspi.TEXT_BOUNDARY_LINE_START)
            #print "onLinkSelected", event.source.getRole() , string,
            #print "  caretOffset:     ", text.caretOffset
            #print "  line startOffset:", startOffset
            #print "  line endOffset:  ", startOffset
            #print "  caret in line:   ", text.caretOffset - startOffset
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        elif text:
            # We'll just assume the whole thing is a link.  This happens
            # in yelp when we navigate the table of contents of something
            # like the Desktop Accessibility Guide.
            #
            linkText = text.getText(0, -1)
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        else:
            speech.speak(rolenames.getSpeechForRoleName(event.source),
                         self.voices[settings.HYPERLINK_VOICE])

        self.updateBraille(event.source)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # HTML radio buttons don't automatically become selected when
        # they receive focus.  The user has to press the space bar on
        # them much like checkboxes.  But if the user clicks on the
        # radio button with the mouse, we'll wind up speaking the
        # state twice because of the focus event.
        #
        if event.type.startswith("object:state-changed:checked") \
           and event.source \
           and (event.source.getRole() == pyatspi.ROLE_RADIO_BUTTON) \
           and (event.detail1 == 1) \
           and self.inDocumentContent(event.source) \
           and not self.isAriaWidget(event.source) \
           and not isinstance(orca_state.lastInputEvent,
                              input_event.MouseButtonEvent):
            orca.visualAppearanceChanged(event, event.source)
            return

        # If an autocomplete appears beneath an entry, we don't want
        # to prevent the user from being able to arrow into it.
        #
        if event.type.startswith("object:state-changed:showing") \
           and event.source \
           and (event.source.getRole() == pyatspi.ROLE_WINDOW) \
           and orca_state.locusOfFocus:
            if orca_state.locusOfFocus.getRole() in [pyatspi.ROLE_ENTRY,
                                                     pyatspi.ROLE_LIST_ITEM]:
                self._autocompleteVisible = event.detail1
                # If the autocomplete has just appeared, we want to speak
                # its appearance if the user's verbosity level is verbose
                # or if the user forced it to appear with (Alt+)Down Arrow.
                #
                if self._autocompleteVisible:
                    speakIt = (settings.speechVerbosityLevel == \
                               settings.VERBOSITY_LEVEL_VERBOSE)
                    if not speakIt \
                       and isinstance(orca_state.lastInputEvent, 
                                      input_event.KeyboardEvent):
                        keyEvent = orca_state.lastNonModifierKeyEvent
                        speakIt = (keyEvent.event_string == ("Down"))
                    if speakIt:
                        speech.speak(rolenames.getSpeechForRoleName(\
                                event.source, pyatspi.ROLE_AUTOCOMPLETE))

        # We care when the document frame changes it's busy state.  That
        # means it has started/stopped loading content.
        #
        if event.type.startswith("object:state-changed:busy"):
            if event.source \
                and (event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME):
                finishedLoading = False
                if orca_state.locusOfFocus \
                    and (orca_state.locusOfFocus.getRole() \
                         == pyatspi.ROLE_LIST_ITEM) \
                   and not self.inDocumentContent(orca_state.locusOfFocus):
                    # The event is for the changing contents of the help
                    # frame as the user navigates from topic to topic in
                    # the list on the left.  Ignore this.
                    #
                    return

                elif event.detail1:
                    # A detail1=1 means the page has started loading.
                    #
                    self._loadingDocumentContent = True

                    # Translators: this is in reference to loading a web page.
                    #
                    message = _("Loading.  Please wait.")

                elif event.source.name:
                    # Translators: this is in reference to loading a web page.
                    #
                    message = _("Finished loading %s.") % event.source.name
                    finishedLoading = True

                else:
                    # Translators: this is in reference to loading a web page.
                    #
                    message = _("Finished loading.")
                    finishedLoading = True

                braille.displayMessage(message)
                speech.speak(message)

                if finishedLoading:
                    # We first try to figure out where the caret is on
                    # the newly loaded page.  If it is on an editable
                    # object (e.g., a text entry), then we present just
                    # that object.  Otherwise, we force the caret to the
                    # top of the page and start a SayAll from that position.
                    #
                    [obj, characterOffset] = self.getCaretContext()
                    atTop = False
                    if not obj:
                        self.clearCaretContext()
                        [obj, characterOffset] = self.getCaretContext()
                        atTop = True

                    # If we found nothing, then don't do anything.  Otherwise
                    # determine if we should do a SayAll or not.
                    #
                    if not obj:
                        return
                    elif not atTop \
                        and not obj.getState().contains(\
                            pyatspi.STATE_FOCUSABLE):
                        self.clearCaretContext()
                        [obj, characterOffset] = self.getCaretContext()
                        if not obj:
                            return

                    # For braille, we just show the current line
                    # containing the caret.  For speech, however, we
                    # will start a Say All operation if the caret is
                    # in an unfocusable area (e.g., it's not in a text
                    # entry area such as Google's search text entry
                    # or a link that we just returned to by pressing
                    # the back button). Otherwise, we'll just speak the
                    # line that the caret is on.
                    #
                    self.updateBraille(obj)

                    if obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                        speech.speakUtterances(\
                            self.speechGenerator.getSpeech(obj, False))
                    elif not script_settings.sayAllOnLoad:
                        self.speakContents(\
                            self.getLineContentsAtOffset(obj,
                                                         characterOffset))
                    elif settings.enableSpeech:
                        self.sayAll(None)

            return

        default.Script.onStateChanged(self, event)

    def onStateFocused(self, event):
        default.Script.onStateChanged(self, event)
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME and \
               event.detail1:
            documentFrame = event.source

            parent_attribs = self._getAttrDictionary(documentFrame.parent)
            parent_tag = parent_attribs.get('tag', '')

            if self._loadingDocumentContent or \
                   documentFrame == self._currentFrame or \
                   not parent_tag.endswith('browser'):
                return

            self._currentFrame = documentFrame

            braille.displayMessage(documentFrame.name)
            speech.stop()
            speech.speak(
                "%s %s" \
                % (documentFrame.name,
                   rolenames.rolenames[pyatspi.ROLE_PAGE_TAB].speech))

            [obj, characterOffset] = self.getCaretContext()
            if not obj:
                [obj, characterOffset] = self.findNextCaretInOrder()
                self.setCaretContext(obj, characterOffset)
            if not obj:
                return

            # When a document tab is tabbed to, we will just present the
            # line where the caret currently is.
            #
            self.presentLine(obj, characterOffset)

    def onWindowDeactivated(self, event):
        """Called whenever a toplevel window is deactivated.

        Arguments:
        - event: the Event
        """

        self._objectForFocusGrab = None
        default.Script.onWindowDeactivated(self, event)

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
        if not self.isDesiredFocusedItem(event.source, rolesList):
            default.Script.handleProgressBarUpdate(self, event, obj)

    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.  This
        method should not be called for objects whose visual appearance
        changes solely because of focus -- setLocusOfFocus is used for that.
        Instead, it is intended mostly for objects whose notional 'value' has
        changed, such as a checkbox changing state, a progress bar advancing,
        a slider moving, text inserted, caret moved, etc.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        if (obj.getRole() == pyatspi.ROLE_CHECK_BOX) \
            and obj.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, obj, False)

        default.Script.visualAppearanceChanged(self, event, obj)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
        # Sometimes we get different accessibles for the same object.
        #
        if self.isSameObject(oldLocusOfFocus, newLocusOfFocus):
            return

        # Try to handle the case where a spurious focus event was tossed
        # at us.
        #
        if newLocusOfFocus and self.inDocumentContent(newLocusOfFocus):
            text = self.queryNonEmptyText(newLocusOfFocus)
            if text:
                caretOffset = text.caretOffset

                # If the old locusOfFocus was not in the document frame, and
                # if the old locusOfFocus's frame is the same as the frame
                # containing the new locusOfFocus, we likely just returned
                # from a toolbar (find, location, menu bar, etc.).  We do
                # not want to speak the hierarchy between that toolbar and
                # the document frame.
                #
                if oldLocusOfFocus and \
                   not self.inDocumentContent(oldLocusOfFocus):
                    oldFrame = self.getFrame(oldLocusOfFocus)
                    newFrame = self.getFrame(newLocusOfFocus)
                    if self.isSameObject(oldFrame, newFrame) or \
                           newLocusOfFocus.getRole() == pyatspi.ROLE_DIALOG:
                        self.setCaretPosition(newLocusOfFocus, caretOffset)
                        self.presentLine(newLocusOfFocus, caretOffset)
                        return

            else:
                caretOffset = 0
            [obj, characterOffset] = \
                  self.findFirstCaretContext(newLocusOfFocus, caretOffset)
            self.setCaretContext(obj, characterOffset)

        # If we've just landed in the Find toolbar, reset
        # self.madeFindAnnouncement.
        #
        if newLocusOfFocus and \
           newLocusOfFocus.getRole() == pyatspi.ROLE_ENTRY and \
           newLocusOfFocus.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            self.madeFindAnnouncement = False

        # We'll ignore focus changes when the document frame is busy.
        # This will keep Orca from chatting too much while a page is
        # loading. But we should check to be sure the document frame
        # is really busy first and also that the event is not coming
        # from an object within a dialog box or alert.
        #
        documentFrame = self.getDocumentFrame()
        if documentFrame:
            self._loadingDocumentContent = \
                documentFrame.getState().contains(pyatspi.STATE_BUSY)

            if self._loadingDocumentContent and event and event.source:
                dialogRoles = [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]
                inDialog = event.source.getRole() in dialogRoles \
                    or self.getAncestor(event.source,
                                        dialogRoles,
                                        [pyatspi.ROLE_DOCUMENT_FRAME])

                if not inDialog:
                    return

        # Don't bother speaking all the information about the HTML
        # container - it's duplicated all over the place.  So, we
        # just speak the role.
        #
        if newLocusOfFocus \
           and newLocusOfFocus.getRole() == pyatspi.ROLE_HTML_CONTAINER:
            # We always automatically go back to focus tracking mode when
            # the focus changes.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()
            self.updateBraille(newLocusOfFocus)
            speech.speak(rolenames.getSpeechForRoleName(newLocusOfFocus))
            return

        default.Script.locusOfFocusChanged(self,
                                           event,
                                           oldLocusOfFocus,
                                           newLocusOfFocus)

    def findObjectOnLine(self, obj, offset, contents):
        """Determines if the item described by the object and offset is
        in the line contents.

        Arguments:
        - obj: the Accessible
        - offset: the character offset within obj
        - contents: a list of (obj, startOffset, endOffset) tuples

        Returns the index of the item if found; -1 if not found.
        """

        if not obj or not contents or not len(contents):
            return -1

        index = -1
        for content in contents:
            [candidate, start, end] = content

            # When we get the line contents, we include a focusable list
            # as a list and combo box as a combo box because that is what
            # we want to present.  However, when we set the caret context,
            # we set it to the position (and object) that immediately
            # precedes it.  Therefore, that's what we need to look at when
            # trying to determine our position.
            #
            if candidate.getRole() in [pyatspi.ROLE_LIST,
                                       pyatspi.ROLE_COMBO_BOX] \
               and candidate.getState().contains(pyatspi.STATE_FOCUSABLE):
                start = self.getCharacterOffsetInParent(candidate)
                end = start + 1
                candidate = candidate.parent

            if self.isSameObject(obj, candidate) \
               and start <= offset < end:
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
        self.speakContents(self.currentLineContents)
        self.updateBraille(obj)

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the given object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not self.inDocumentContent():
            default.Script.updateBraille(self, obj, extraRegion)
            return

        if not obj:
            return

        braille.clear()
        line = braille.Line()
        braille.addLine(line)

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
        focusedObjText = self.queryNonEmptyText(focusedObj)
        if focusedObjText:
            char = focusedObjText.getText(focusedCharacterOffset,
                                          focusedCharacterOffset + 1)
            if char == "\n":
                lineContentsOffset = max(0, focusedCharacterOffset - 1)
                needToRefresh = True

        contents = self.currentLineContents
        index = self.findObjectOnLine(focusedObj,
                                      max(0, lineContentsOffset),
                                      contents)
        if index < 0 or needToRefresh:
            contents = self.getLineContentsAtOffset(focusedObj,
                                                    max(0, lineContentsOffset))
            self.currentLineContents = contents

        if not len(contents):
            return

        focusedRegion = None
        for content in contents:
            [obj, startOffset, endOffset] = content
            if not obj:
                continue

            # If this is a label that's labelling something else, we'll
            # get the label via a braille generator. [[[TODO: WDW - this is
            # all to hack around the way checkboxes and their labels
            # are handled in document content.  For now, we will display
            # the label so we can track the caret in it on the braille
            # display.  So...we'll comment this section out.]]]
            #
            #if self.isLabellingContents(obj, contents):
            #    continue

            # Treat the focused combo box and its selected menu item
            # as the same object for the purposes of displaying the
            # item in braille.
            #
            if focusedObj.getRole() == pyatspi.ROLE_COMBO_BOX \
               and obj.getRole() == pyatspi.ROLE_MENU_ITEM:
                comboBox = self.getAncestor(obj,
                                            [pyatspi.ROLE_COMBO_BOX],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])
                isFocusedObj = self.isSameObject(comboBox, focusedObj)
            else:
                isFocusedObj = self.isSameObject(obj, focusedObj)

            text = self.queryNonEmptyText(obj)
            if text and text.getText(startOffset, endOffset) == " " \
               and not obj.getRole() in [pyatspi.ROLE_PAGE_TAB_LIST,
                                         pyatspi.ROLE_ENTRY]:
                continue

            if not self.isNavigableAria(obj):
                # Treat unnavigable ARIA widgets like normal default.py widgets
                #
                [regions, fRegion] = \
                          self.brailleGenerator.getBrailleRegions(obj)
                if isFocusedObj:
                    focusedRegion = fRegion
            elif obj.getRole() in [pyatspi.ROLE_ENTRY,
                                   pyatspi.ROLE_PASSWORD_TEXT] \
                or ((obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME) \
                    and obj.getState().contains(pyatspi.STATE_EDITABLE)):
                label = self.getDisplayedLabel(obj)
                regions = [braille.Text(obj,
                                        label,
                                        settings.brailleEOLIndicator)]
                if isFocusedObj:
                    focusedRegion = regions[0]
            elif text and (obj.getRole() != pyatspi.ROLE_MENU_ITEM):
                string = text.getText(startOffset, endOffset).decode('utf-8')
                string = string.rstrip()
                endOffset = startOffset + len(string)

                if endOffset == startOffset:
                    continue

                if obj.getRole() == pyatspi.ROLE_LINK:
                    link = obj
                else:
                    link = self.getAncestor(obj,
                                            [pyatspi.ROLE_LINK],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])

                if not link:
                    regions = [braille.Text(obj,
                                            startOffset=startOffset,
                                            endOffset=endOffset)]

                if link:
                    regions = [braille.Component(
                            link,
                            string + " " + \
                                rolenames.getBrailleForRoleName(link),
                            focusedCharacterOffset - startOffset,
                            expandOnCursor=True)]
                elif obj.getRole() == pyatspi.ROLE_CAPTION:
                    regions.append(braille.Region(
                        " " + rolenames.getBrailleForRoleName(obj)))

                if isFocusedObj \
                   and (focusedCharacterOffset >= startOffset) \
                   and (focusedCharacterOffset < endOffset):
                    focusedRegion = regions[0]

            elif self.isLayoutOnly(obj):
                continue
            else:
                [regions, fRegion] = \
                          self.brailleGenerator.getBrailleRegions(obj)
                if isFocusedObj:
                    focusedRegion = fRegion

            # We only want to display the heading role and level if we
            # have found the final item in that heading, or if that
            # heading contains no children.
            #
            containingHeading = \
                self.getAncestor(obj,
                                 [pyatspi.ROLE_HEADING],
                                 [pyatspi.ROLE_DOCUMENT_FRAME])
            isLastObject = contents.index(content) == (len(contents) - 1)
            if obj.getRole() == pyatspi.ROLE_HEADING:
                appendRole = isLastObject or not obj.childCount
            elif containingHeading and isLastObject:
                obj = containingHeading
                appendRole = True

            if obj.getRole() == pyatspi.ROLE_HEADING and appendRole:
                level = self.getHeadingLevel(obj)
                # Translators: the 'h' below represents a heading level
                # attribute for content that you might find in something
                # such as HTML content (e.g., <h1>). The translated form
                # is meant to be a single character followed by a numeric
                # heading level, where the single character is to indicate
                # 'heading'.
                #
                regions.append(braille.Region(" " + _("h%d" % level)))

            if len(line.regions):
                line.regions[-1].string.rstrip(" ")
                line.addRegion(braille.Region(" "))

            line.addRegions(regions)

            # If we're inside of a combo box, we only want to display
            # the selected menu item.
            #
            if obj.getRole() == pyatspi.ROLE_MENU_ITEM \
               and obj.getState().contains(pyatspi.STATE_FOCUSED):
                break

        if extraRegion:
            line.addRegion(extraRegion)

        if len(line.regions):
            line.regions[-1].string.rstrip(" ")

        braille.setFocus(focusedRegion)
        braille.refresh(True)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #

        if not self.inDocumentContent():
            default.Script.sayCharacter(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        text = self.queryNonEmptyText(obj)
        if text:
            # If the caret is at the end of text and we're not in an
            # entry, something bad is going on, so decrement the offset
            # before speaking the character.
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string) and \
               obj.getRole() != pyatspi.ROLE_ENTRY:
                print "YIKES in Gecko.sayCharacter!"
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
        text = self.queryNonEmptyText(obj)
        if text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the previous word.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next word via
            # a call to goNextWord.]]]
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string):
                print "YIKES in Gecko.sayWord!"
                characterOffset -= 1

        # Ideally in an entry we would just let default.sayWord() handle
        # things.  That fails to work when navigating backwords by word.
        # Because getUtterancesFromContents() now uses the speechgenerator
        # with entries, we need to handle word navigation in entries here.
        #
        wordContents = self.getWordContentsAtOffset(obj, characterOffset)
        if obj.getRole() != pyatspi.ROLE_ENTRY:
            self.speakContents(wordContents)
        else:
            [textObj, startOffset, endOffset] = wordContents[0]
            word = textObj.queryText().getText(startOffset, endOffset)
            speech.speakUtterances([word], self.getACSS(textObj, word))

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent() or \
           obj.getRole() == pyatspi.ROLE_ENTRY:
            default.Script.sayLine(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        text = self.queryNonEmptyText(obj)
        if text:
            # [[[TODO: WDW - the caret might be at the end of the text.
            # Not quite sure what to do in this case.  What we'll do here
            # is just speak the current line.  But...maybe we want to
            # make sure we say something like "end of line" or move the
            # caret context to the beginning of the next line via
            # a call to goNextLine.]]]
            #
            string = text.getText(0, -1)
            if characterOffset >= len(string):
                print "YIKES in Gecko.sayLine!"
                characterOffset -= 1

        self.speakContents(self.getLineContentsAtOffset(obj, characterOffset))

    ####################################################################
    #                                                                  #
    # Methods for debugging.                                           #
    #                                                                  #
    ####################################################################

    def outlineExtents(self, obj, startOffset, endOffset):
        """Draws an outline around the given text for the object or the entire
        object if it has no text.  This is for debug purposes only.

        Arguments:
        -obj: the object
        -startOffset: character offset to start at
        -endOffset: character offset just after last character to end at
        """
        [x, y, width, height] = self.getExtents(obj, startOffset, endOffset)
        self.drawOutline(x, y, width, height)

    def dumpInfo(self, obj):
        """Dumps the parental hierachy info of obj to stdout."""

        if obj.parent:
            self.dumpInfo(obj.parent)

        print "---"
        text = self.queryNonEmptyText(obj)
        if text and obj.getRole() != pyatspi.ROLE_DOCUMENT_FRAME:
            string = text.getText(0, -1)
        else:
            string = ""
        print obj, obj.name, obj.getRole(), \
              obj.accessible.getIndexInParent(), string
        offset = self.getCharacterOffsetInParent(obj)
        if offset >= 0:
            print "  offset =", offset

    def getDocumentContents(self):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the current caret context (or the beginning of the document if
        there is no caret context).

        WARNING: THIS TRAVERSES A LARGE PART OF THE DOCUMENT AND IS
        INTENDED PRIMARILY FOR DEBUGGING PURPOSES ONLY."""

        contents = []
        lastObj = None
        lastExtents = None
        self.clearCaretContext()
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            if True or obj.getState().contains(pyatspi.STATE_SHOWING):
                if self.queryNonEmptyText(obj):
                    # Check for text being on a different line.  Gecko
                    # gives us odd character extents sometimes, so we
                    # defensively ignore those.
                    #
                    characterExtents = self.getExtents(
                        obj, characterOffset, characterOffset + 1)
                    if characterExtents != (0, 0, 0, 0):
                        if lastExtents \
                           and not self.onSameLine(lastExtents,
                                                   characterExtents):
                            contents.append([None, -1, -1])
                            lastExtents = characterExtents

                    # Check to see if we've moved across objects or are
                    # still on the same object.  If we've moved, we want
                    # to add another context.  If we're still on the same
                    # object, we just want to update the end offset.
                    #
                    if (len(contents) == 0) or (obj != lastObj):
                        contents.append([obj,
                                         characterOffset,
                                         characterOffset + 1])
                    else:
                        [currentObj, startOffset, endOffset] = contents[-1]
                        if characterOffset == endOffset:
                            contents[-1] = [currentObj,    # obj
                                            startOffset,   # startOffset
                                            endOffset + 1] # endOffset
                        else:
                            contents.append([obj,
                                             characterOffset,
                                             characterOffset + 1])
                else:
                    # Some objects present text and/or something visual
                    # (e.g., a checkbox), so we want to track it.
                    #
                    contents.append([obj, -1, -1])

                lastObj = obj

            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)

        return contents

    def getDocumentString(self):
        """Trivial debug utility to stringify the document contents
        showing on the screen."""

        contents = ""
        lastObj = None
        lastCharacterExtents = None
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            if obj and obj.getState().contains(pyatspi.STATE_SHOWING):
                characterExtents = self.getExtents(
                    obj, characterOffset, characterOffset + 1)
                if lastObj and (lastObj != obj):
                    if obj.getRole() == pyatspi.ROLE_LIST_ITEM:
                        contents += "\n"
                    if lastObj.getRole() == pyatspi.ROLE_LINK:
                        contents += ">"
                    elif (lastCharacterExtents[1] < characterExtents[1]):
                        contents += "\n"
                    elif obj.getRole() == pyatspi.ROLE_TABLE_CELL:
                        parent = obj.parent
                        index = self.getCellIndex(obj)
                        if parent.queryTable().getColumnAtIndex(index) != 0:
                            contents += " "
                    elif obj.getRole() == pyatspi.ROLE_LINK:
                        contents += "<"
                contents += self.getCharacterAtOffset(obj, characterOffset)
                lastObj = obj
                lastCharacterExtents = characterExtents
            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)
        if lastObj and lastObj.getRole() == pyatspi.ROLE_LINK:
            contents += ">"
        return contents

    def dumpContents(self, inputEvent, contents=None):
        """Dumps the document frame content to stdout.

        Arguments:
        -inputEvent: the input event that caused this to be called
        -contents: an ordered list of [obj, startOffset, endOffset] tuples
        """
        if not contents:
            contents = self.getDocumentContents()
        string = ""
        extents = None
        for content in contents:
            [obj, startOffset, endOffset] = content
            if obj:
                extents = self.getBoundary(
                    self.getExtents(obj, startOffset, endOffset),
                    extents)
                text = self.queryNonEmptyText(obj)
                if text:
                    string += "[%s] text='%s' " % (obj.getRole(),
                                                   text.getText(startOffset,
                                                                endOffset))
                else:
                    string += "[%s] name='%s' " % (obj.getRole(), obj.name)
            else:
                string += "\nNEWLINE\n"
        print "==========================="
        print string
        self.drawOutline(extents[0], extents[1], extents[2], extents[3])

    ####################################################################
    #                                                                  #
    # Utility Methods                                                  #
    #                                                                  #
    ####################################################################

    def queryNonEmptyText(self, obj):
        """Get the text interface associated with an object, if it is
        non-empty.

        Arguments:
        - obj: an accessible object
        """

        try:
            text = obj.queryText()
        except:
            pass
        else:
            if text.characterCount:
                return text

        return None

    def inDocumentContent(self, obj=None):
        """Returns True if the given object (defaults to the current
        locus of focus is in the document content).
        """
        if not obj:
            obj = orca_state.locusOfFocus

        while obj:
            role = obj.getRole()
            if role == pyatspi.ROLE_DOCUMENT_FRAME \
                    or role == pyatspi.ROLE_EMBEDDED:
                return True
            else:
                obj = obj.parent
        return False

    def getDocumentFrame(self):
        """Returns the document frame that holds the content being shown."""

        # [[[TODO: WDW - this is based upon the 12-Oct-2006 implementation
        # that uses the EMBEDS relation on the top level frame as a means
        # to find the document frame.  Future implementations will break
        # this.]]]
        #
        documentFrame = None
        for child in self.app:
            if child.getRole() == pyatspi.ROLE_FRAME:
                relationSet = child.getRelationSet()
                for relation in relationSet:
                    if relation.getRelationType()  \
                        == pyatspi.RELATION_EMBEDS:
                        documentFrame = relation.getTarget(0)
                        if documentFrame.getState().contains( \
                            pyatspi.STATE_SHOWING):
                            break
                        else:
                            documentFrame = None

        return documentFrame

    def getURI(self, obj):
        """Return the URI for a given link object.

        Arguments:
        - obj: the Accessible object.
        """
        # Getting a link's URI requires a little workaround due to
        # https://bugzilla.mozilla.org/show_bug.cgi?id=379747.  You should be
        # able to use getURI() directly on the link but instead must use
        # ihypertext.getLink(0) on parent then use getURI on returned
        # ihyperlink.
        try:
            ihyperlink = obj.parent.queryHypertext().getLink(0)
        except:
            return None
        else:
            return ihyperlink.getURI(0)

    def getDocumentFrameURI(self):
        """Returns the URI of the document frame that is active."""
        documentFrame = self.getDocumentFrame()
        if documentFrame:
            # If the document frame belongs to a Thunderbird message which
            # has just been deleted, getAttributes() will crash Thunderbird.
            #
            if not documentFrame.getState().contains(pyatspi.STATE_DEFUNCT):
                attrs = documentFrame.queryDocument().getAttributes()
                for attr in attrs:
                    if attr.startswith('DocURL'):
                        return attr[7:]
        return None

    def getUnicodeText(self, obj):
        """Returns the unicode text for an object or None if the object
        doesn't implement the accessible text specialization.
        """

        text = self.queryNonEmptyText(obj)
        if text:
            unicodeText = text.getText(0, -1).decode("UTF-8")
        else:
            unicodeText = None
        return unicodeText

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if we should do our own caret navigation.
        """

        if not script_settings.controlCaretNavigation:
            return False

        if not self.inDocumentContent():
            return False

        if not self.isNavigableAria(orca_state.locusOfFocus):
            return False

        weHandleIt = True
        obj = orca_state.locusOfFocus
        if obj and (obj.getRole() == pyatspi.ROLE_ENTRY):
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
                    weHandleIt = obj.getRole() == pyatspi.ROLE_MENU_ITEM

        elif obj and (obj.getRole() == pyatspi.ROLE_COMBO_BOX):
            # We'll let Firefox handle the navigation of combo boxes.
            #
            weHandleIt = keyboardEvent.event_string in ["Left", "Right"]

        elif obj and (obj.getRole() in [pyatspi.ROLE_MENU_ITEM,
                                        pyatspi.ROLE_LIST_ITEM]):
            # We'll let Firefox handle the navigation of combo boxes and
            # lists in forms.
            #
            weHandleIt = not obj.getState().contains(pyatspi.STATE_FOCUSED)

        elif obj and (obj.getRole() == pyatspi.ROLE_LIST):
            # We'll let Firefox handle the navigation of lists in forms.
            #
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

        # If the current object isn't even showing, we don't want to hand
        # this off to Firefox's native caret navigation because who knows
        # where we'll wind up....
        #
        if obj and not obj.getState().contains(pyatspi.STATE_SHOWING):
            return True

        attrs = self._getAttrDictionary(orca_state.locusOfFocus)
        try:
            # ARIA landmark widgets
            if attrs['xml-roles'] in script_settings.ARIA_LANDMARKS:
                return True
            # ARIA live region
            elif 'container-live' in attrs:
                return True
            # Don't treat links as ARIA widgets. And we should be able to
            # escape/exit ARIA entries just like we do HTML entries (How
            # is the user supposed to know which he/she happens to be in?)
            #
            elif obj.getRole() in [pyatspi.ROLE_ENTRY, pyatspi.ROLE_LINK]:
                return True
            # All other ARIA widgets
            else:
                return False
        except (KeyError, TypeError):
            return True

    def isAriaWidget(self, obj=None):
        """Returns True if the object being examined is an ARIA widget.

        Arguments:
        - obj: The accessible object of interest.  If None, the
        locusOfFocus is examined.
        """
        obj = obj or orca_state.locusOfFocus
        attrs = self._getAttrDictionary(obj)
        return ('xml-roles' in attrs and 'live' not in attrs)

    def _getAttrDictionary(self, obj):
        return dict([attr.split(':', 1) for attr in obj.getAttributes()])

    def handleAsLiveRegion(self, event):
        """Returns True if the given event (object:children-changed, object:
        text-insert only) should be considered a live region event"""

        # We will try to eliminate objects that cannot be considered live
        # regions.  We will handle everything else as a live region.  We
        # will do the cheap tests first
        if self._loadingDocumentContent \
              or not  settings.inferLiveRegions:
            return False

        # Ideally, we would like to do a inDocumentContent() call to filter out
        # events that are not in the document.  Unfortunately, this is an
        # expensive call.  Instead we will do some heuristics to filter out
        # chrome events with the least amount of IPC as possible.

        # event.type specific checks
        if event.type.startswith('object:children-changed'):
            if event.type.endswith(':system'):
                # This will filter out list items that are not of interest and
                # events from other tabs.
                stateset = event.any_data.getState()
                if stateset.contains(pyatspi.STATE_SELECTABLE) \
                    or not stateset.contains(pyatspi.STATE_VISIBLE):
                    return False

                # Now we need to look at the object attributes
                attrs = self._getAttrDictionary(event.any_data)
                # Good live region markup
                if 'container-live' in attrs:
                    return True

                # We see this one with the URL bar opening (sometimes)
                if 'tag' in attrs and attrs['tag'] == 'xul:richlistbox':
                    return False

                if 'xml-roles' in attrs:
                    # This eliminates all ARIA widgets that are not
                    # considered live
                    if attrs['xml-roles'] != 'alert' \
                               and attrs['xml-roles'] != 'tooltip':
                        return False
                    # Only present tooltips when user wants them presented
                    elif attrs['xml-roles'] == 'tooltip' \
                                   and not settings.presentToolTips:
                        return False
            else:
                # Some alerts have been seen without the :system postfix.
                # We will take care of them separately.
                attrs = self._getAttrDictionary(event.any_data)
                if 'xml-roles' in attrs \
                                      and attrs['xml-roles'] == 'alert':
                    return True
                else:
                    return False

        elif event.type.startswith('object:text-changed:insert:system'):
            # Live regions will not be focusable.
            # Filter out events from hidden tabs (not VISIBLE)
            stateset = event.source.getState()
            if stateset.contains(pyatspi.STATE_FOCUSABLE) \
                   or stateset.contains(pyatspi.STATE_SELECTABLE) \
                   or not stateset.contains(pyatspi.STATE_VISIBLE):
                return False

            attrs = self._getAttrDictionary(event.source)
            # Good live region markup
            if 'container-live' in attrs:
                return True

            # This might be too restrictive but we need it to filter
            # out URLs that are displayed when the location list opens.
            if 'tag' in attrs \
                    and attrs['tag'] == 'xul:description' \
                    or attrs['tag'] == 'xul:label':
                return False

            # This eliminates all ARIA widgets that are not considered live
            if 'xml-roles' in attrs:
                return False
        else: # object:text-inserted events
            return False

        # This last filter gets rid of some events that come in after
        # window:activate event.  They are usually areas of a page that
        # are built dynamically.
        if time.time() - self._loadingDocumentTime > 2.0:
            return True
        else:
            return False

    def getCharacterOffsetInParent(self, obj):
        """Returns the character offset of the embedded object
        character for this object in its parent's accessible text.

        Arguments:
        - obj: an Accessible that should implement the accessible hyperlink
               specialization.

        Returns an integer representing the character offset of the
        embedded object character for this hyperlink in its parent's
        accessible text, or -1 something was amuck.
        """

        try:
            hyperlink = obj.queryHyperlink()
        except NotImplementedError:
            offset = -1
        else:
            # We need to make sure that this is an embedded object in
            # some accessible text (as opposed to an imagemap link).
            #
            try:
                obj.parent.queryText()
            except NotImplementedError:
                offset = -1
            else:
                offset = hyperlink.startIndex

        return offset

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
        text = self.queryNonEmptyText(obj)
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

    def getBoundary(self, a, b):
        """Returns the smallest [x, y, width, height] that encompasses
        both extents a and b.

        Arguments:
        -a: [x, y, width, height]
        -b: [x, y, width, height]
        """
        if not a:
            return b
        if not b:
            return a
        smallestX1 = min(a[0], b[0])
        smallestY1 = min(a[1], b[1])
        largestX2  = max(a[0] + a[2], b[0] + b[2])
        largestY2  = max(a[1] + a[3], b[1] + b[3])
        return [smallestX1,
                smallestY1,
                largestX2 - smallestX1,
                largestY2 - smallestY1]

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

    def getCellIndex(self, obj):
        """Returns the index of the cell which should be used with the
        table interface.  This is necessary because we cannot count on
        the index we need being the same as the index in the parent.
        See, for example, tables with captions and tables with rows
        that have attributes."""

        index = -1
        parent = self.getAncestor(obj,
                                 [pyatspi.ROLE_TABLE, 
                                  pyatspi.ROLE_TREE_TABLE,
                                  pyatspi.ROLE_TREE],
                                 [pyatspi.ROLE_DOCUMENT_FRAME])
        try:
            table = parent.queryTable()
        except:
            pass
        else:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
            index = attrs.get('table-cell-index')
            if index:
                index = int(index)
            else:
                index = obj.getIndexInParent()

        return index

    def getCellCoordinates(self, obj):
        """Returns the [row, col] of a ROLE_TABLE_CELL or [0, 0]
        if the coordinates cannot be found.
        """
        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            obj = self.getAncestor(obj,
                                   [pyatspi.ROLE_TABLE_CELL],
                                   [pyatspi.ROLE_DOCUMENT_FRAME])

        parent = obj.parent
        try:
            table = parent.queryTable()
        except:
            pass
        else:
            index = self.getCellIndex(obj)
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

        text = self.getDisplayedText(obj)
        if text and text != u'\u00A0':
            return False
        else:
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LINK:
                    return False

            return True

    def getLinkBasename(self, obj):
        """Returns the relevant information from the URI.  The idea is
        to attempt to strip off all prefix and suffix, much like the
        basename command in a shell."""

        basename = None

        try:
            hyperlink = obj.queryHyperlink()
        except:
            pass
        else:
            uri = hyperlink.getURI(0)
            if uri and len(uri):
                # Get the last thing after all the /'s, unless it ends
                # in a /.  If it ends in a /, we'll look to the stuff
                # before the ending /.
                #
                if uri[-1] == "/":
                    basename = uri[0:-1]
                    basename = basename.split('/')[-1]
                else:
                    basename = uri.split('/')[-1]
                    if basename.startswith("index"):
                        basename = uri.split('/')[-2]

                    # Now, try to strip off the suffixes.
                    #
                    basename = basename.split('.')[0]
                    basename = basename.split('?')[0]
                    basename = basename.split('#')[0]

        return basename

    def isFormField(self, obj):
        """Returns True if the given object is a field inside of a form."""

        if not obj or not self.inDocumentContent(obj):
            return False

        formRoles = [pyatspi.ROLE_CHECK_BOX,
                     pyatspi.ROLE_RADIO_BUTTON,
                     pyatspi.ROLE_COMBO_BOX,
                     pyatspi.ROLE_LIST,
                     pyatspi.ROLE_ENTRY,
                     pyatspi.ROLE_PASSWORD_TEXT,
                     pyatspi.ROLE_PUSH_BUTTON]

        state = obj.getState()
        isField = obj.getRole() in formRoles \
                  and state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        return isField

    def isUselessObject(self, obj):
        """Returns true if the given object is an obj that doesn't
        have any meaning associated with it and it is not inside a
        link."""

        if not obj:
            return True

        useless = False

        textObj = self.queryNonEmptyText(obj)
        if not textObj and obj.getRole() == pyatspi.ROLE_PARAGRAPH:
            useless = True
        elif obj.getRole() in [pyatspi.ROLE_IMAGE, \
                               pyatspi.ROLE_TABLE_CELL, \
                               pyatspi.ROLE_SECTION]:
            text = self.getDisplayedText(obj)
            if (not text) or (len(text) == 0):
                text = self.getDisplayedLabel(obj)
                if (not text) or (len(text) == 0):
                    useless = True

        if useless:
            link = self.getAncestor(obj,
                                    [pyatspi.ROLE_LINK],
                                    [pyatspi.ROLE_DOCUMENT_FRAME])
            if link:
                useless = False

        return useless

    def isLayoutOnly(self, obj):
        """Returns True if the given object is for layout purposes only."""

        if self.isUselessObject(obj):
            debug.println(debug.LEVEL_FINEST,
                          "Object deemed to be useless: %s" % obj)
            return True

        else:
            return default.Script.isLayoutOnly(self, obj)

    def pursueForFlatReview(self, obj):
        """Determines if we should look any further at the object
        for flat review."""

        # [[[TODO: HACK - WDW Gecko has issues about the SHOWING
        # state of objects, especially those in document frames.
        # It tells us the content in tabs that are not showing
        # is actually showing.  See:
        #
        # http://bugzilla.gnome.org/show_bug.cgi?id=408071
        #
        # To work around this, we do a little extra check.  If
        # the obj is a document, and it's not the one that
        # Firefox is currently showing the user, we skip it.
        #
        pursue = default.Script.pursueForFlatReview(self, obj)
        if pursue and (obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME):
            documentFrame = self.getDocumentFrame()
            pursue = obj == documentFrame

        return pursue

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

    def getNodeLevel(self, obj):
        """ Determines the level of at which this object is at by using the
        object attribute 'level'.  To be consistent with default.getNodeLevel()
        this value is 0-based (Gecko return is 1-based) """

        if obj is None or obj.getRole() == pyatspi.ROLE_HEADING:
            return -1

        attrs = obj.getAttributes()
        if attrs is None:
            return -1
        for attr in attrs:
            if attr.startswith("level:"):
                return int(attr[6:]) - 1
        return -1

    def getTopOfFile(self):
        """Returns the object and first caret offset at the top of the
         document frame."""

        documentFrame = self.getDocumentFrame()
        [obj, offset] = self.findFirstCaretContext(documentFrame, 0)

        return [obj, offset]

    def getBottomOfFile(self):
        """Returns the object and last caret offset at the bottom of the
         document frame."""

        documentFrame = self.getDocumentFrame()
        obj = self.getLastObject(documentFrame)
        offset = 0

        # obj should now be the very last item in the entire document frame
        # and not have children of its own.  Therefore, it should have text.
        # If it doesn't, we don't want to be here.
        #
        text = self.queryNonEmptyText(obj)
        if text:
            offset = text.characterCount - 1
        else:
            obj = self.findPreviousObject(obj, documentFrame)

        while obj:
            [lastObj, lastOffset] = self.findNextCaretInOrder(obj, offset)
            if not lastObj \
               or self.isSameObject(lastObj, obj) and (lastOffset == offset):
                break

            [obj, offset] = [lastObj, lastOffset]

        return [obj, offset]

    def getLastObject(self, documentFrame):
        """Returns the last object in the document frame"""

        lastChild = documentFrame[documentFrame.childCount - 1]
        while lastChild:
            lastObj = self.findNextObject(lastChild, documentFrame)
            if lastObj:
                lastChild = lastObj
            else:
                break

        return lastChild

    def getNextCellInfo(self, cell, direction):
        """Given a cell from which to start and a direction in which to
        search locates the next cell and returns it, along with its
        text, extents (as a tuple), and whether or not the cell contents
        consist of a form field.

        Arguments
        - cell: the table cell from which to start
        - direction: a string which can be one of four options: 'left',
                     'right', 'up', 'down'

        Returns [nextCell, text, extents, isField]
        """

        newCell = None
        text = None
        extents = ()
        isField = False
        if not cell or cell.getRole() != pyatspi.ROLE_TABLE_CELL:
            return [newCell, text, extents, isField]

        [row, col] = self.getCellCoordinates(cell)
        table = cell.parent.queryTable()
        rowspan = table.getRowExtentAt(row, col)
        colspan = table.getColumnExtentAt(row, col)
        nextCell = None
        if direction == "left" and col > 0:
            nextCell = (row, col - 1)
        elif direction == "right" \
             and (col + colspan <= table.nColumns - 1):
            nextCell = (row, col + colspan)
        elif direction == "up" and row > 0:
            nextCell = (row - 1, col)
        elif direction == "down" \
             and (row + rowspan <= table.nRows - 1):
            nextCell = (row + rowspan, col)
        if nextCell:
            newCell = table.getAccessibleAt(nextCell[0], nextCell[1])
            if newCell:
                [obj, offset] = self.findFirstCaretContext(newCell, 0)
                extents = self.getExtents(obj, offset, offset + 1)
                isField = self.isFormField(obj)
                if self.queryNonEmptyText(obj) \
                   and not self.isBlankCell(newCell):
                    text = self.getDisplayedText(obj)

        return [newCell, text, extents, isField]

    def expandEOCs(self, obj, startOffset=0, endOffset= -1):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with their text.

        Arguments
        - obj: the object whose text should be expanded
        - startOffset: the offset of the first character to be included
        - endOffset: the offset of the last character to be included

        Returns the fully expanded text for the object.
        """

        if not obj:
            return None

        string = None
        text = self.queryNonEmptyText(obj)
        if text:
            string = text.getText(startOffset, endOffset)
            unicodeText = string.decode("UTF-8")
            if unicodeText \
                and self.EMBEDDED_OBJECT_CHARACTER in unicodeText:
                toBuild = list(unicodeText)
                count = toBuild.count(self.EMBEDDED_OBJECT_CHARACTER)
                for i in xrange(count):
                    index = toBuild.index(self.EMBEDDED_OBJECT_CHARACTER)
                    child = obj[i]
                    childText = self.expandEOCs(child)
                    if not childText:
                        childText = ""
                    toBuild[index] = childText.decode("UTF-8")
                string = "".join(toBuild)

        return string

    def getObjectsFromEOCs(self, obj, offset, boundary):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with [obj, startOffset, endOffset] tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - offset: the character offset after which
        - boundary: the pyatspi text boundary type

        Returns a list of object tuples.
        """

        if not obj:
            return []

        elif obj.getRole() == pyatspi.ROLE_TABLE:
            # If this is a table, move to the first cell -- or the caption,
            # if present.
            # [[[TODOS - JD:
            #    1) It might be nice to announce the fact that we've just
            #       found a table, what its dimensions are, etc.
            #    2) It seems that down arrow moves us to the table, but up
            #       arrow moves us to the last row.  Possible side effect
            #       of our existing caret browsing implementation??]]]
            #
            if obj[0] and obj[0].getRole == pyatspi.ROLE_CAPTION:
                obj = obj[0]
            else:
                obj = obj.queryTable().getAccessibleAt(0, 0)

        objects = []
        text = self.queryNonEmptyText(obj)
        if text:
            [string, start, end] = text.getTextAfterOffset(offset, boundary)
        else:
            string = ""
            start = 0
            end = 1
        objects.append([obj, start, end])

        pattern = re.compile(self.EMBEDDED_OBJECT_CHARACTER)
        unicodeText = string.decode("UTF-8")
        matches = re.finditer(pattern, unicodeText)
        for m in matches:
            # Adjust the last object's endOffset to the last character
            # before the EOC.
            #
            childOffset = m.start(0) + start
            objects[-1][2] = childOffset
            if objects[-1][1] == objects[-1][2]:
                # A zero-length object is an indication of something
                # whose sole contents was an EOC.  Delete it from the
                # list.
                #
                objects.pop()

            # Recursively tack on the child's objects.
            #
            childIndex = self.getChildIndex(obj, childOffset)
            child = obj[childIndex]
            objects.extend(self.getObjectsFromEOCs(child, 0, boundary))

            # Tack on the remainder of the original object, if any.
            #
            if end > childOffset + 1:
                objects.append([obj, childOffset + 1, end])

        if obj.getRole() == pyatspi.ROLE_IMAGE and obj.childCount:
            # Imagemaps that don't have alternative text won't implement
            # the text interface, but they will have children (essentially
            # EOCs) that we need to get.
            #
            toAdd = []
            for child in obj:
                toAdd.extend(self.getObjectsFromEOCs(child, 0, boundary))
            if len(toAdd):
                if self.isSameObject(objects[-1][0], obj):
                    objects.pop()
                objects.extend(toAdd)

        return objects

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

            # Rather than do a brute force label guess, we'll focus on
            # entries as they are the most common and their label is
            # likely on this line.  The functional label may be made up
            # of several objects, so we'll examine the strings of what
            # we've got and pop off the ones that match.
            #
            elif role == pyatspi.ROLE_ENTRY:
                labelGuess = self.guessLabelFromLine(item[0])
                index = len(lineContents) - 1
                while labelGuess and index >= 0:
                    prevItem = lineContents[index]
                    prevText = self.queryNonEmptyText(prevItem[0])
                    if prevText:
                        string = prevText.getText(prevItem[1], prevItem[2])
                        if labelGuess.endswith(string):
                            lineContents.pop()
                            length = len(labelGuess) - len(string)
                            labelGuess = labelGuess[0:length]
                        else:
                            break
                    index -= 1

            else:
                text = self.queryNonEmptyText(item[0])
                if text:
                    string = text.getText(item[1], item[2]).decode("UTF-8")
                    if not len(string.strip()):
                        continue

            lineContents.append(item)

        return lineContents

    def guessLabelFromLine(self, obj):
        """Attempts to guess what the label of an unlabeled form control
        might be by looking at surrounding contents from the same line.

        Arguments
        - obj: the form field about which to take a guess

        Returns the text which we think might be the label or None if we
        give up.
        """

        # Based on Tom Brunet's comments on how Home Page Reader
        # approached the task of guessing labels.  Please see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        #
        #  1. Text/img that precedes control in same item.
        #  2. Text/img that follows control in same item (nothing between
        #     end of text and item)
        #
        # Reverse this order for radio buttons and check boxes
        #
        guess = None
        extents = obj.queryComponent().getExtents(0)
        objExtents = [extents.x, extents.y, extents.width, extents.height]

        lineContents = self.currentLineContents
        ourIndex = self.findObjectOnLine(obj, 0, lineContents)
        if ourIndex < 0:
            lineContents = self.getLineContentsAtOffset(obj, 0)
            ourIndex = self.findObjectOnLine(obj, 0, lineContents)

        objectsOnLine = []
        for content in lineContents:
            objectsOnLine.append(content[0])

        # Now that we know where we are, let's see who are neighbors are
        # and where they are.
        #
        onLeft = None
        onRight = None
        if ourIndex > 0:
            onLeft = objectsOnLine[ourIndex - 1]
        if 0 <= ourIndex < len(objectsOnLine) - 1:
            onRight = objectsOnLine[ourIndex + 1]

        # Normally we prefer what's on the left given a choice.  Reasons
        # to prefer what's on the right include looking at a radio button
        # or a checkbox. [[[TODO - JD: Language direction should also be
        # taken into account.]]]
        #
        preferRight = obj.getRole() in [pyatspi.ROLE_CHECK_BOX,
                                        pyatspi.ROLE_RADIO_BUTTON]

        # [[[TODO: JD: Nearby text that's not actually in the form may need
        # to be ignored.  Let's try that for now and adjust based on feedback
        # and testing.]]]
        #
        leftIsInForm = (onLeft and onLeft.getRole() == pyatspi.ROLE_FORM)
        if not leftIsInForm:
            leftIsInForm = self.getAncestor(onLeft,
                                            [pyatspi.ROLE_FORM],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])
        rightIsInForm = (onRight and onRight.getRole() == pyatspi.ROLE_FORM)
        if not rightIsInForm:
            rightIsInForm = self.getAncestor(onRight,
                                             [pyatspi.ROLE_FORM],
                                             [pyatspi.ROLE_DOCUMENT_FRAME])
        # If it's a radio button, we'll waive the requirement of the text
        # on the right being within the form (or rather, we'll just act as
        # if it were even if it's not).
        #
        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            rightIsInForm = True

        # [[[TODO: Grayed out buttons don't pass the isFormField() test
        # because they are neither focusable nor showing -- and thus
        # something we don't want to navigate to via structural navigation.
        # We may need to rethink our definition of isFormField().  In the
        # meantime, let's not used grayed out buttons as labels. As an
        # example, see the Search entry on live.gnome.org.]]]
        #
        if onLeft:
            leftIsFormField = self.isFormField(onLeft) \
                              or onLeft.getRole() == pyatspi.ROLE_PUSH_BUTTON
        if onRight:
            rightIsFormField = self.isFormField(onRight) \
                               or onRight.getRole() == pyatspi.ROLE_PUSH_BUTTON

        if onLeft and leftIsInForm and not leftIsFormField:
            # We want to get the text on the left including embedded objects
            # that are NOT form fields. If we find a form field on the left,
            # that will be the starting point of the text we want.
            #
            startOffset = 0
            endOffset = -1
            if self.isSameObject(obj.parent, onLeft):
                endOffset = self.getCharacterOffsetInParent(obj)
                index = obj.getIndexInParent()
                if index > 0:
                    prevSibling = onLeft[index - 1]
                    if self.isFormField(prevSibling):
                        startOffset = \
                                  self.getCharacterOffsetInParent(prevSibling)

            guess = self.expandEOCs(onLeft, startOffset, endOffset)
            if guess:
                guess = guess.decode("UTF-8").strip()
            if not guess and onLeft.getRole() == pyatspi.ROLE_IMAGE:
                guess = onLeft.name

        if (preferRight or not guess) \
           and onRight and rightIsInForm and not rightIsFormField:
            # The object's horizontal position plus its width tells us
            # where the text on the right can begin.  For now, define
            # "immediately after" as  within 50 pixels.
            #
            canStartAt = objExtents[0] + objExtents[2]
            onRightExtents = onRight.queryComponent().getExtents(0)
            onRightExtents = [onRightExtents.x, onRightExtents.y,
                              onRightExtents.width, onRightExtents.height]

            if (onRightExtents[0] - canStartAt) <= 50:
                # We want to get the text on the right including embedded
                # objects that are NOT form fields.  If we find a form field
                # on the right, that will be the ending point of the text we
                # want.  However, if we have a form field on the right and
                # do not have a reason to prefer the text on the right, our
                # label may be on the line above.  As an example, see the
                # bugzilla Advanced search... Bug Changes section.
                #
                startOffset = 0
                endOffset = -1
                if self.isSameObject(obj.parent, onRight):
                    startOffset = self.getCharacterOffsetInParent(obj)
                    index = obj.getIndexInParent()
                    if index < onRight.childCount - 1:
                        nextSibling = onRight[index + 1]
                        nextRole = nextSibling.getRole()
                        if self.isFormField(nextSibling) \
                           or nextRole == pyatspi.ROLE_RADIO_BUTTON:
                            endOffset = \
                                  self.getCharacterOffsetInParent(nextSibling)
                            if not preferRight:
                                return None

                guess = self.expandEOCs(onRight, startOffset, endOffset)
                if guess:
                    guess = guess.decode("UTF-8").strip()
                if not guess and onRight.getRole() == pyatspi.ROLE_IMAGE:
                    guess = onRight.name

        return guess

    def guessLabelFromOtherLines(self, obj):
        """Attempts to guess what the label of an unlabeled form control
        might be by looking at nearby contents from neighboring lines.

        Arguments
        - obj: the form field about which to take a guess

        Returns the text which we think might be the label or None if we
        give up.
        """

        # Based on Tom Brunet's comments on how Home Page Reader
        # approached the task of guessing labels.  Please see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        #
        guess = None
        extents = obj.queryComponent().getExtents(0)
        objExtents = \
               [extents.x, extents.y, extents.width, extents.height]

        index = self.findObjectOnLine(obj, 0, self.currentLineContents)
        if index > 0 and self._previousLineContents:
            prevLineContents = self._previousLineContents
            prevObj = prevLineContents[0][0]
            prevOffset = prevLineContents[0][1]
        else:
            [prevObj, prevOffset] = self.findPreviousLine(obj, 0, False)
            prevLineContents = self.getLineContentsAtOffset(prevObj,
                                                            prevOffset)
            self._previousLineContents = prevLineContents

        nextLineContents = self._nextLineContents
        if index > 0 and nextLineContents:
            nextObj = nextLineContents[0][0]
            nextOffset = nextLineContents[0][1]

        # The labels for combo boxes won't be found below the combo box
        # because expanding the combo box will cover up the label. Labels
        # for lists probably won't be below the list either.
        #
        if not nextLineContents and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                                      pyatspi.ROLE_MENU,
                                                      pyatspi.ROLE_MENU_ITEM,
                                                      pyatspi.ROLE_LIST,
                                                      pyatspi.ROLE_LIST_ITEM]:
            [nextObj, nextOffset] = self.findNextLine(obj, 0, False)
            nextLineContents = self.getLineContentsAtOffset(nextObj,
                                                            nextOffset)
            self._nextLineContents = nextLineContents
        else:
            [nextObj, nextOffset] = [None, 0]
            nextLineContents = []

        above = None
        for content in prevLineContents:
            extents = content[0].queryComponent().getExtents(0)
            aboveExtents = \
                 [extents.x, extents.y, extents.width, extents.height]

            # [[[TODO: Grayed out buttons don't pass the isFormField()
            # test because they are neither focusable nor showing -- and
            # thus something we don't want to navigate to via structural
            # navigation. We may need to rethink our definition of
            # isFormField().  In the meantime, let's not used grayed out
            # buttons as labels. As an example, see the Search entry on
            # live.gnome.org. We want to ignore menu items as well.]]]
            #
            aboveIsFormField = self.isFormField(content[0]) \
                        or content[0].getRole() in [pyatspi.ROLE_PUSH_BUTTON,
                                                    pyatspi.ROLE_MENU_ITEM,
                                                    pyatspi.ROLE_LIST]

            # [[[TODO - JD: Nearby text that's not actually in the form
            # may need to be ignored.  Let's do so unless it's directly
            # above the form field or the text above is contained in the
            # form's parent and adjust based on feedback, testing.]]]
            #
            theForm = self.getAncestor(obj,
                                       [pyatspi.ROLE_FORM],
                                       [pyatspi.ROLE_DOCUMENT_FRAME])
            aboveForm = self.getAncestor(obj,
                                         [pyatspi.ROLE_FORM],
                                         [pyatspi.ROLE_DOCUMENT_FRAME])
            aboveIsInForm = self.isSameObject(theForm, aboveForm)
            formIsInAbove = theForm \
                            and self.isSameObject(theForm.parent, content[0])

            # If the horizontal starting point of the object is the
            # same as the horizontal starting point of the text
            # above it, the text above it is probably serving as the
            # label. We'll allow for a 2 pixel difference.  If that
            # fails, and the text above starts within 50 pixels to
            # the left and ends somewhere above or beyond the current
            # form field, we'll give it the benefit of the doubt.
            # For an example of the latter case, see Bugzilla's Advanced
            # search page, Bug Changes section.
            #
            if (objExtents != aboveExtents) and not aboveIsFormField:
                guessThis = (0 <= abs(objExtents[0] - aboveExtents[0]) <= 2)
                if not guessThis:
                    objEnd = objExtents[0] + objExtents[2]
                    aboveEnd = aboveExtents[0] + aboveExtents[2]
                    guessThis = (0 <= objExtents[0] - aboveExtents[0] <= 50) \
                                 and (aboveEnd > objEnd) \
                                 and (aboveIsInForm or formIsInAbove)

                if guessThis:
                    above = content[0]
                    guessAbove = self.expandEOCs(content[0],
                                                 content[1],
                                                 content[2])
                    break

        below = None
        for content in nextLineContents:
            extents = content[0].queryComponent().getExtents(0)
            belowExtents = \
                 [extents.x, extents.y, extents.width, extents.height]
            # [[[TODO: Grayed out buttons don't pass the isFormField()
            # test because they are neither focusable nor showing -- and
            # thus something we don't want to navigate to via structural
            # navigation. We may need to rethink our definition of
            # isFormField().  In the meantime, let's not used grayed out
            # buttons as labels. As an example, see the Search entry on
            # live.gnome.org. We want to ignore menu items as well.]]]
            #
            belowIsFormField = self.isFormField(content[0]) \
                        or content[0].getRole() in [pyatspi.ROLE_PUSH_BUTTON,
                                                    pyatspi.ROLE_MENU_ITEM,
                                                    pyatspi.ROLE_LIST]

            # [[[TODO - JD: Nearby text that's not actually in the form
            # may need to be ignored.  Let's try that for now and adjust
            # based on feedback and testing.]]]
            #
            belowIsInForm = self.getAncestor(content[0],
                                             [pyatspi.ROLE_FORM],
                                             [pyatspi.ROLE_DOCUMENT_FRAME])

            # If the horizontal starting point of the object is the
            # same as the horizontal starting point of the text
            # below it, the text below it is probably serving as the
            # label. We'll allow for a 2 pixel difference.
            #
            if objExtents != belowExtents \
               and not belowIsFormField \
               and belowIsInForm \
               and 0 <= abs(objExtents[0] - belowExtents[0]) <= 2:
                below = content[0]
                guessBelow = self.expandEOCs(content[0],
                                             content[1],
                                             content[2])
                break

        if above:
            if not below:
                guess = guessAbove
            else:
                # We'll guess the nearest text.
                #
                bottomOfAbove = aboveExtents[1] + aboveExtents[3]
                topOfBelow = belowExtents[1]
                bottomOfObj = objExtents[1] + objExtents[3]
                topOfObject = objExtents[1]
                aboveProximity = topOfObject - bottomOfAbove
                belowProximity = topOfBelow - bottomOfObj
                if aboveProximity <=  belowProximity \
                   or belowProximity < 0:
                    guess = guessAbove
                else:
                    guess = guessBelow
        elif below:
            guess = guessBelow

        return guess

    def guessLabelFromTable(self, obj):
        """Attempts to guess what the label of an unlabeled form control
        might be by looking at surrounding table cells.

        Arguments
        - obj: the form field about which to take a guess

        Returns the text which we think might be the label or None if we
        give up.
        """

        # Based on Tom Brunet's comments on how Home Page Reader
        # approached the task of guessing labels.  Please see:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        #
        # "3. Text/img that precedes control in previous item/cell
        #     not another control in that item)..."
        #
        #  4. Text/img in cell above without other controls in this
        #     cell above."
        #
        # If that fails, we might as well look to the cell below. If the
        # text is immediately below the entry and nothing else looks like
        # a label, that text might be it. Given both text above and below
        # the control, the most likely label is probably the text that is
        # vertically nearest it. This theory will, of course, require
        # testing "in the wild."
        #
        guess = None
        extents = obj.queryComponent().getExtents(0)
        objExtents = [extents.x, extents.y, extents.width, extents.height]
        containingCell = \
                       self.getAncestor(obj,
                                        [pyatspi.ROLE_TABLE_CELL],
                                        [pyatspi.ROLE_DOCUMENT_FRAME])

        # If we're not in a table cell, pursuing this further is silly. If
        # we're in a table cell but are not the sole occupant of that cell,
        # we're likely in a more complex layout table than this approach
        # can handle.
        #
        if not containingCell \
           or (containingCell.childCount > 1):
            return guess
        elif self.getAncestor(obj,
                              [pyatspi.ROLE_PARAGRAPH],
                              [pyatspi.ROLE_TABLE,
                               pyatspi.ROLE_DOCUMENT_FRAME]):
            return guess

        [cellLeft, leftText, leftExtents, leftIsField] = \
                   self.getNextCellInfo(containingCell, "left")
        [cellRight, rightText, rightExtents, rightIsField] = \
                   self.getNextCellInfo(containingCell, "right")
        [cellAbove, aboveText, aboveExtents, aboveIsField] = \
                   self.getNextCellInfo(containingCell, "up")
        [cellBelow, belowText, belowExtents, belowIsField] = \
                   self.getNextCellInfo(containingCell, "down")

        if rightText:
            # The object's horizontal position plus its width tells us
            # where the text on the right can begin. For now, define
            # "immediately after" as  within 50 pixels.
            #
            canStartAt = objExtents[0] + objExtents[2]
            rightCloseEnough = rightExtents[0] - canStartAt <= 50

        if leftText and not leftIsField:
            guess = leftText
        elif rightText and rightCloseEnough and not rightIsField:
            guess = rightText
        elif aboveText and not aboveIsField:
            if not belowText or belowIsField:
                guess = aboveText
            else:
                # We'll guess the nearest text.
                #
                bottomOfAbove = aboveExtents[1] + aboveExtents[3]
                topOfBelow = belowExtents[1]
                bottomOfObj = objExtents[1] + objExtents[3]
                topOfObject = objExtents[1]
                aboveProximity = topOfObject - bottomOfAbove
                belowProximity = topOfBelow - bottomOfObj
                if aboveProximity <=  belowProximity:
                    guess = aboveText
                else:
                    guess = belowText
        elif belowText and not belowIsField:
            guess = belowText
        elif aboveIsField:
            # Given the lack of potential labels and the fact that
            # there's a form field immediately above us, there's
            # a reasonable chance that we're in a series of form
            # fields arranged grid-style.  It's even more likely
            # if the form fields above us are all of the same type
            # and size (say, within 1 pixel).
            #
            grid = False
            done = False
            nextCell = containingCell
            while not done:
                [nextCell, text, extents, isField] = \
                        self.getNextCellInfo(nextCell, "up")
                if nextCell:
                    dWidth = abs(objExtents[2] - extents[2])
                    dHeight = abs(objExtents[3] - extents[3])
                    if dWidth > 1 or dHeight > 1:
                        done = True
                    if not isField:
                        [row, col] = self.getCellCoordinates(nextCell)
                        if row == 0:
                            grid = True
                            done = True
                else:
                    done = True

            if grid:
                topCol = nextCell.parent.queryTable().getAccessibleAt(0, col)
                [objTop, offset] = self.findFirstCaretContext(topCol, 0)
                if self.queryNonEmptyText(topCol) \
                   and not self.isFormField(topCol):
                    guess = self.expandEOCs(topCol)

        return guess

    def guessTheLabel(self, obj, focusedOnly=True):
        """Attempts to guess what the label of an unlabeled form control
        might be.

        Arguments
        - obj: the form field about which to take a guess
        - focusedOnly: If True, only take guesses about the form field
          with focus.

        Returns the text which we think might be the label or None if we
        give up.
        """

        # The initial stab at this is based on Tom Brunet's comments
        # on how Home Page Reader approached this task.  His comments
        # can be found at the RFE for Mozilla to do this work for us:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=376481#c15
        # N.B. If you see a comment in quotes, it's taken directly from
        # Tom.
        #
        guess = None

        # If we're not in the document frame, we don't want to be guessing.
        # We also don't want to be guessing if the item doesn't have focus.
        #
        isFocused = obj.getState().contains(pyatspi.STATE_FOCUSED)
        if not self.inDocumentContent() \
           or (focusedOnly and not isFocused) \
           or self.isAriaWidget(obj):
            return guess

        # Because the guesswork is based upon spatial relations, if we're
        # in a list, look from the perspective of the first list item rather
        # than from the list as a whole.
        #
        if obj.getRole() == pyatspi.ROLE_LIST:
            obj = obj[0]

        guess = self.guessLabelFromLine(obj)
        # print "guess from line: ", guess
        if not guess:
            # Maybe it's in a table cell.
            #
            guess = self.guessLabelFromTable(obj)
            # print "guess from table: ", guess
        if not guess:
            # Maybe the text is above or below us, but not in a table
            # cell.
            #
            guess = self.guessLabelFromOtherLines(obj)
            #print "guess form other lines: ", guess
        if not guess:
            # We've pretty much run out of options.  From Tom's overview
            # of the approach for all controls:
            # "... 4. title attribute."
            # The title attribute seems to be exposed as the name.
            #
            guess = obj.name
            #print "Guessing the name: ", guess

        return guess.strip()

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
        looking for real rext

        Returns [obj, characterOffset] that points to real content.
        """

        text = self.queryNonEmptyText(obj)
        if text:
            unicodeText = self.getUnicodeText(obj)
            if characterOffset >= len(unicodeText):
                if obj.getRole() != pyatspi.ROLE_ENTRY:
                    return [obj, -1]
                else:
                    # We're at the end of an entry.  If we return -1,
                    # and then set the caretContext accordingly,
                    # findNextCaretInOrder() will think we're at the
                    # beginning and we'll never escape this entry.
                    #
                    return [obj, characterOffset]

            character = text.getText(characterOffset,
                                     characterOffset + 1).decode("UTF-8")
            if character == self.EMBEDDED_OBJECT_CHARACTER:
                if obj.childCount <= 0:
                    return self.findFirstCaretContext(obj, characterOffset + 1)
                try:
                    childIndex = self.getChildIndex(obj, characterOffset)
                    return self.findFirstCaretContext(obj[childIndex], 0)
                except:
                    return [obj, -1]
            else:
                # [[[TODO: WDW - HACK because Gecko currently exposes
                # whitespace from the raw HTML to us.  We can infer this
                # by seeing if the extents are nil.  If so, we skip to
                # the next character.]]]
                #
                extents = self.getExtents(obj,
                                          characterOffset,
                                          characterOffset + 1)
                if (extents == (0, 0, 0, 0)) \
                    and ((characterOffset + 1) < len(unicodeText)):
                    return self.findFirstCaretContext(obj, characterOffset + 1)
                else:
                    return [obj, characterOffset]
        else:
            return [obj, -1]

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
            obj = self.getDocumentFrame()

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

        text = self.queryNonEmptyText(obj)
        if text and not (self.isAriaWidget(obj) \
                         and obj.getRole() == pyatspi.ROLE_LIST):
            unicodeText = self.getUnicodeText(obj)

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
                    child = obj[self.getChildIndex(obj, nextOffset)]
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
                debug.printException(debug.LEVEL_SEVERE)

        elif includeNonText and (startOffset < 0) \
             and (not self.isLayoutOnly(obj)):
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.getDocumentFrame()
        if self.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
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
                        debug.printException(debug.LEVEL_SEVERE)
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
            obj = self.getDocumentFrame()

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

        text = self.queryNonEmptyText(obj)
        if text and not (self.isAriaWidget(obj) \
                         and obj.getRole() == pyatspi.ROLE_LIST):
            unicodeText = self.getUnicodeText(obj)

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
                debug.printException(debug.LEVEL_SEVERE)

        elif includeNonText and (startOffset < 0) \
            and (not self.isLayoutOnly(obj)):
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.getDocumentFrame()
        if self.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
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
                        debug.printException(debug.LEVEL_SEVERE)
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
        if self.isSameObject(obj, documentFrame):
            [obj, characterOffset] = self.getCaretContext()

        index = obj.getIndexInParent() - 1
        if (index < 0):
            if not self.isSameObject(obj, documentFrame):
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
                if not self.isSameObject(obj, documentFrame):
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
                    childOffset = self.getCharacterOffsetInParent(child)
                    if isinstance(child, pyatspi.Accessibility.Accessible) \
                       and not (self.isSameObject(previousObj, documentFrame) \
                        and childOffset > characterOffset):
                        previousObj = child
                        break
                    else:
                        index -= 1
                if index < 0:
                    break

        if self.isSameObject(previousObj, documentFrame):
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
        if self.isSameObject(obj, documentFrame):
            [obj, characterOffset] = self.getCaretContext()

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
            childOffset = self.getCharacterOffsetInParent(child)
            if isinstance(child, pyatspi.Accessibility.Accessible) \
               and not (self.isSameObject(obj, documentFrame) \
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
        if not nextObj:
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
            while (candidate.getIndexInParent() >= \
                  (candidate.parent.childCount - 1)) \
                and not self.isSameObject(candidate, documentFrame):
                candidate = candidate.parent

            # Now...let's get the sibling.
            #
            # [[[TODO: HACK - WDW Gecko's broken hierarchies make this
            # a bit of a challenge.]]]
            #
            if not self.isSameObject(candidate, documentFrame):
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

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""
        state = obj.getState()
        readOnly = obj.getRole() == pyatspi.ROLE_ENTRY \
                   and state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)
        debug.println(debug.LEVEL_ALL,
                      "Gecko.script.py:isReadOnlyTextArea=%s for %s" \
                      % (readOnly, debug.getAccessibleDetails(obj)))
        return readOnly

    def clearCaretContext(self):
        """Deletes all knowledge of a character context for the current
        document frame."""

        documentFrame = self.getDocumentFrame()
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
        documentFrame = self.getDocumentFrame()

        if not documentFrame:
            return

        self._documentFrameCaretContext[hash(documentFrame)] = \
            [obj, characterOffset]

        self._updateLineCache(obj, characterOffset)

    def getTextLineAtCaret(self, obj):
        """Gets the line of text where the caret is. This is an override to
        accomodate the intricities of our caret navigation management.

        Argument:
        - obj: an Accessible object that implements the AccessibleText
               interface

        Returns the [string, caretOffset, startOffset] for the line of text
        where the caret is.
        """

        contextObj, contextCaret = self.getCaretContext()

        if contextObj == obj and \
                not obj.getState().contains(pyatspi.STATE_EDITABLE):
            try:
                ti = obj.queryText()
            except NotImplementedError:
                return ["", 0, 0]
            else:
                string, startOffset, endOffset = ti.getTextAtOffset(
                    contextCaret, pyatspi.TEXT_BOUNDARY_LINE_START)
                caretOffset = contextCaret
        else:
            string, caretOffset, startOffset = \
                default.Script.getTextLineAtCaret(self, obj)


        return string, caretOffset, startOffset

    def getCaretContext(self, includeNonText=True):
        """Returns the current [obj, caretOffset] if defined.  If not,
        it returns the first [obj, caretOffset] found by an in order
        traversal from the beginning of the document."""

        # We keep a context for each page tab shown.
        # [[[TODO: WDW - probably should figure out how to destroy
        # these contexts when a tab is killed.]]]
        #
        documentFrame = self.getDocumentFrame()

        if not documentFrame:
            return [None, -1]

        try:
            return self._documentFrameCaretContext[hash(documentFrame)]
        except:
            self._documentFrameCaretContext[hash(documentFrame)] = \
                self.findNextCaretInOrder(None,
                                          -1,
                                          includeNonText)

        return self._documentFrameCaretContext[hash(documentFrame)]

    def getCharacterAtOffset(self, obj, characterOffset):
        """Returns the character at the given characterOffset in the
        given object or None if the object does not implement the
        accessible text specialization.
        """

        try:
            unicodeText = self.getUnicodeText(obj)
            return unicodeText[characterOffset].encode("UTF-8")
        except:
            return None

    def getWordContentsAtOffset(self, obj, characterOffset, boundary=None):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
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
        text = self.queryNonEmptyText(obj)
        if text:
            word = text.getTextAtOffset(characterOffset, boundary)
            if word[1] < characterOffset <= word[2]:
                characterOffset = word[1]

        contents = self.getObjectsFromEOCs(obj, characterOffset, boundary)
        if len(contents) > 1 \
           and contents[0][0].getRole() == pyatspi.ROLE_LIST_ITEM:
            contents = [contents[0]]

        return contents

    def getLineContentsAtOffset(self, obj, offset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
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

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START

        if obj.getRole() == pyatspi.ROLE_IMAGE \
           and obj.parent.getRole() == pyatspi.ROLE_LINK:
            offset = obj.getIndexInParent()
            obj = obj.parent

        # Find the beginning of this line w.r.t. this object.
        #
        text = self.queryNonEmptyText(obj)
        if text:
            [line, start, end] = text.getTextAtOffset(offset, boundary)
            unicodeText = line.decode("UTF-8")
            if unicodeText.startswith(self.EMBEDDED_OBJECT_CHARACTER):
                childIndex = self.getChildIndex(obj, start)
                if childIndex >= 0:
                    child = obj[childIndex]
                    childText = self.queryNonEmptyText(child)
                    childRole = child.getRole()
                    # If the object represented by the EOC at the beginning
                    # of this line is a section, it is functionally not part
                    # of this line and should not be included here.
                    #
                    if childText and childRole != pyatspi.ROLE_SECTION:
                        noChars = childText.characterCount
                        [cLine, cStart, cEnd] = \
                               childText.getTextAtOffset(noChars - 1, boundary)
                        if cEnd - cStart > 1:
                            obj = child
                            start = cStart
                        else:
                            start += 1
                    elif not childRole in [pyatspi.ROLE_LINK,
                                           pyatspi.ROLE_IMAGE,
                                           pyatspi.ROLE_SECTION]:
                        text = None
                        obj = child
                    else:
                        [line, start, end] = \
                               text.getTextAfterOffset(start + 1, boundary)
            elif offset > end and start < end:
                # Line break characters might be messing us up. If the
                # difference is 1, then we're moving down and want the
                # text that comes after this offset.  Otherwise, we're
                # moving up and want the text that comes after the end.
                #
                if offset - end > 1:
                    offset = end + 1
                [line, start, end] = text.getTextAfterOffset(end + 1, boundary)

        if text:
            offset = start
        else:
            offset = 0

        extents = self.getExtents(obj, offset, offset + 1)

        # Get the objects on this line.
        #
        objects = self.getObjectsFromEOCs(obj, offset, boundary)

        # Check for things on the left.
        #
        lastExtents = (0, 0, 0, 0)
        done = False
        while not done:
            [firstObj, start, end] = objects[0]
            isAria = not self.isNavigableAria(firstObj)

            text = self.queryNonEmptyText(firstObj)
            if text and start > 0 and not isAria:
                break

            if isAria:
                documentFrame = self.getDocumentFrame()
                prevObj = self.findPreviousObject(firstObj, documentFrame)
                pOffset = 0
            else:
                [prevObj, pOffset] = \
                    self.findPreviousCaretInOrder(firstObj, start)

            if not prevObj or self.isSameObject(prevObj, firstObj):
                break

            text = self.queryNonEmptyText(prevObj)
            if text:
                line = text.getTextAtOffset(pOffset, boundary)
                pOffset = line[1]

            prevExtents = self.getExtents(prevObj, pOffset, pOffset + 1)
            if self.onSameLine(extents, prevExtents) \
               and extents != prevExtents \
               and lastExtents != prevExtents \
               or prevExtents == (0, 0, 0, 0):
                toAdd = self.getObjectsFromEOCs(prevObj, pOffset, boundary)
                objects[0:0] = toAdd
            else:
                break

            lastExtents = prevExtents

        # Check for things on the right.
        #
        lastExtents = (0, 0, 0, 0)
        done = False
        while not done:
            [lastObj, start, end] = objects[-1]
            isAria = not self.isNavigableAria(lastObj)

            text = self.queryNonEmptyText(lastObj)
            if text and end < text.characterCount - 1 and not isAria:
                break

            if isAria:
                documentFrame = self.getDocumentFrame()
                nextObj = self.findNextObject(lastObj, documentFrame)
                nOffset = 0
            else:
                [nextObj, nOffset] = self.findNextCaretInOrder(lastObj, end)

            if not nextObj or self.isSameObject(nextObj, lastObj):
                break

            text = self.queryNonEmptyText(nextObj)
            if text:
                line = text.getTextAfterOffset(nOffset, boundary)
                nOffset = line[1]

            char = self.getCharacterAtOffset(nextObj, nOffset)
            if char == " ":
                nOffset += 1

            nextExtents = self.getExtents(nextObj, nOffset, nOffset + 1)

            if self.onSameLine(extents, nextExtents) \
               and extents != nextExtents \
               and lastExtents != nextExtents \
               or nextExtents == (0, 0, 0, 0):
                toAdd = self.getObjectsFromEOCs(nextObj, nOffset, boundary)
                objects.extend(toAdd)
            elif (nextObj.getRole() in [pyatspi.ROLE_SECTION,
                                        pyatspi.ROLE_TABLE_CELL] \
                  and not isAria and self.isUselessObject(nextObj)):
                toAdd = self.getObjectsFromEOCs(nextObj, nOffset, boundary)
                done = True
                for item in toAdd:
                    itemExtents = self.getExtents(item[0], item[1], item[2])
                    if self.onSameLine(extents, itemExtents):
                        objects.append(item)
                        done = False
                if done:
                    break
            else:
                break

            lastExtents = nextExtents

        # Get rid of duplicates (real and functional).
        #
        parentLink = None
        for o in objects:
            if objects.count(o) > 1:
                objects.pop(objects.index(o))
            elif o[0].parent.getRole() == pyatspi.ROLE_LINK:
                if not parentLink:
                    parentLink = o[0].parent
                elif self.isSameObject(o[0].parent, parentLink):
                    objects.pop(objects.index(o))
                else:
                    parentLink = o[0].parent

        return objects

    def getObjectContentsAtOffset(self, obj, characterOffset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset] tuple.  The list is created
        via an in-order traversal of the document contents starting and
        stopping at the given object.
        """

        #if not obj.getState().contains(pyatspi.STATE_SHOWING):
        #    return [[None, -1, -1]]
        contents = []
        if obj.getRole() == pyatspi.ROLE_TABLE:
            for child in obj:
                contents.extend(self.getObjectContentsAtOffset(child, 0))
            return contents

        elif not self.queryNonEmptyText(obj):
            return [[obj, -1, -1]]

        text = self.getUnicodeText(obj)
        for offset in range(characterOffset, len(text)):
            if text[offset] == self.EMBEDDED_OBJECT_CHARACTER:
                child = obj[self.getChildIndex(obj, offset)]
                if child:
                    contents.extend(self.getObjectContentsAtOffset(child, 0))
            elif len(contents):
                [currentObj, startOffset, endOffset] = contents[-1]
                if obj == currentObj:
                    contents[-1] = [obj, startOffset, offset + 1]
                else:
                    contents.append([obj, offset, offset + 1])
            else:
                contents.append([obj, offset, offset + 1])

        return contents

    ####################################################################
    #                                                                  #
    # Methods to speak current objects.                                #
    #                                                                  #
    ####################################################################

    def getACSS(self, obj, string):
        """Returns the ACSS to speak anything for the given obj."""
        if obj.getRole() == pyatspi.ROLE_LINK:
            acss = self.voices[settings.HYPERLINK_VOICE]
        elif string and string.isupper() and string.strip().isalpha():
            acss = self.voices[settings.UPPERCASE_VOICE]
        else:
            acss = self.voices[settings.DEFAULT_VOICE]

        return acss

    def getUtterancesFromContents(self, contents, speakRole=True):
        """Returns a list of [text, acss] tuples based upon the
        list of [obj, startOffset, endOffset] tuples passed in.

        Arguments:
        -contents: a list of [obj, startOffset, endOffset] tuples
        -speakRole: if True, speak the roles of objects
        """

        if not len(contents):
            return []

        utterances = []
        for content in contents:
            [obj, startOffset, endOffset] = content
            if not obj:
                continue

            # If this is a label that's labelling something else, we'll
            # get the label via a speech generator -- unless it's a
            # focusable list that doesn't have focus.
            #
            labelledContent = self.isLabellingContents(obj, contents)
            if labelledContent \
               and labelledContent.getRole() != pyatspi.ROLE_LIST:
                continue

            # The radio button's label gets added to the context in
            # default.locusOfFocusChanged() and not through the speech
            # generator -- unless we wind up having to guess the label.
            # Therefore, if we have a valid label for a radio button,
            # we need to add it here.
            #
            if (obj.getRole() == pyatspi.ROLE_RADIO_BUTTON) \
                and not self.isAriaWidget(obj):
                label = self.getDisplayedLabel(obj)
                if label:
                    utterances.append([label, self.getACSS(obj, label)])

            # We only want to announce the heading role and level if we
            # have found the final item in that heading, or if that
            # heading contains no children.
            #
            containingHeading = \
                self.getAncestor(obj,
                                 [pyatspi.ROLE_HEADING],
                                 [pyatspi.ROLE_DOCUMENT_FRAME])
            isLastObject = contents.index(content) == (len(contents) - 1)
            if obj.getRole() == pyatspi.ROLE_HEADING:
                speakThisRole = isLastObject or not obj.childCount
            else:
                # We also don't want to speak the role if it's a documement
                # frame or a table cell.  In addition, if the object is an
                # entry or password_text, _getSpeechForText() will add the
                # role after the label and before any text that is present
                # in that field.  We don't want to repeat the role.
                #
                speakThisRole = \
                    not obj.getRole() in [pyatspi.ROLE_DOCUMENT_FRAME,
                                          pyatspi.ROLE_TABLE_CELL,
                                          pyatspi.ROLE_ENTRY,
                                          pyatspi.ROLE_PASSWORD_TEXT]
            text = self.queryNonEmptyText(obj)
            if self.isAriaWidget(obj):
                # Treat ARIA widgets like normal default.py widgets
                #
                speakThisRole = False
                strings = self.speechGenerator.getSpeech(obj, False)
            elif text \
               and not obj.getRole() in [pyatspi.ROLE_ENTRY,
                                         pyatspi.ROLE_PASSWORD_TEXT,
                                         pyatspi.ROLE_RADIO_BUTTON,
                                         pyatspi.ROLE_MENU_ITEM]:
                strings = [text.getText(startOffset, endOffset)]
                if strings == [' '] and len(contents) > 1:
                    strings = []
            elif self.isLayoutOnly(obj):
                continue
            else:
                strings = self.speechGenerator.getSpeech(obj, False)

        # Pylint is confused and flags these errors:
        #
        # E1101:6957:Script.getUtterancesFromContents: Instance of
        # 'SpeechGenerator' has no 'getSpeechForObjectRole' member
        # E1101:6962:Script.getUtterancesFromContents: Instance of
        # 'SpeechGenerator' has no 'getSpeechForObjectRole' member
        #
        # So for now, we just disable these errors in this method.
        #
        # pylint: disable-msg=E1101

            if speakRole and speakThisRole:
                if text:
                    strings.extend(\
                       self.speechGenerator.getSpeechForObjectRole(obj))

                if containingHeading and isLastObject:
                    obj = containingHeading
                    strings.extend(\
                        self.speechGenerator.getSpeechForObjectRole(obj))

            for string in strings:
                utterances.append([string, self.getACSS(obj, string)])

            if speakRole and \
               speakThisRole and \
               obj.getRole() == pyatspi.ROLE_HEADING:
                level = self.getHeadingLevel(obj)
                if level:
                    utterances.append([" ", self.getACSS(obj, " ")])
                    # Translators: this is in reference to a heading level
                    # in HTML (e.g., For <h3>, the level is 3).
                    #
                    utterances.append([_("level %d") % level, None])

        return utterances

    def clumpUtterances(self, utterances):
        """Returns a list of utterances clumped together by acss.

        Arguments:
        -utterances: unclumped utterances
        -speakRole: if True, speak the roles of objects
        """

        clumped = []

        for [string, acss] in utterances:
            if len(clumped) == 0:
                clumped = [[string, acss]]
            elif acss == clumped[-1][1]:
                clumped [-1][0] = clumped[-1][0].rstrip(" ")
                clumped[-1][0] += " " + string
            else:
                clumped.append([string, acss])

        if (len(clumped) == 1) and (clumped[0][0] == "\n"):
            if settings.speakBlankLines:
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                return [[_("blank"), clumped[0][1]]]

        if len(clumped):
            clumped [-1][0] = clumped[-1][0].rstrip(" ")

        return clumped

    def speakContents(self, contents, speakRole=True):
        """Speaks each string in contents using the associated voice/acss"""
        utterances = self.getUtterancesFromContents(contents, speakRole)
        clumped = self.clumpUtterances(utterances)
        for [string, acss] in clumped:
            string = self.adjustForRepeats(string)
            speech.speak(string, acss, False)

    def speakCharacterAtOffset(self, obj, characterOffset):
        """Speaks the character at the given characterOffset in the
        given object."""
        character = self.getCharacterAtOffset(obj, characterOffset)
        if obj:
            if character and character != self.EMBEDDED_OBJECT_CHARACTER:
                speech.speakCharacter(character,
                                      self.getACSS(obj, character))
            elif obj.getRole() != pyatspi.ROLE_ENTRY:
                # We won't have a character if we move to the end of an
                # entry (in which case we're not on a character and therefore
                # have nothing to say), or when we hit a component with no
                # text (e.g. checkboxes) or reset the caret to the parent's
                # characterOffset (lists).  In these latter cases, we'll just
                # speak the entire component.
                #
                utterances = self.speechGenerator.getSpeech(obj, False)
                speech.speakUtterances(utterances)

    ####################################################################
    #                                                                  #
    # Methods to navigate to previous and next objects.                #
    #                                                                  #
    ####################################################################

    def setCaretOffset(self, obj, characterOffset):
        self.setCaretPosition(obj, characterOffset)
        self.updateBraille(obj)

    def setCaretPosition(self, obj, characterOffset):
        """Sets the caret position to the given character offset in the
        given object.
        """

        caretContext = self.getCaretContext()

        # Save where we are in this particular document frame.
        # We do this because the user might have several URLs
        # open in several different tabs, and we keep track of
        # where the caret is for each documentFrame.
        #
        documentFrame = self.getDocumentFrame()
        if documentFrame:
            self._documentFrameCaretContext[hash(documentFrame)] = caretContext

        if caretContext == [obj, characterOffset]:
            return

        self.setCaretContext(obj, characterOffset)

        # If the item is a focusable list in an HTML form, we're here
        # because we've arrowed to it.  We don't want to grab focus on
        # it and trap the user in the list. The same is true for combo
        # boxes.
        #
        if obj.getRole() in [pyatspi.ROLE_LIST, pyatspi.ROLE_COMBO_BOX] \
           and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            characterOffset = self.getCharacterOffsetInParent(obj)
            obj = obj.parent
            self.setCaretContext(obj, characterOffset)

        # Reset focus if need be.
        #
        if obj != orca_state.locusOfFocus:
            orca.setLocusOfFocus(None, obj, False)

            # We'd like the object to have focus if it can take focus.
            # Otherwise, we bubble up until we find a parent that can
            # take focus.  This is to allow us to help force focus out
            # of something such as a text area and back into the
            # document content.
            #
            self._objectForFocusGrab = obj
            while self._objectForFocusGrab and obj:
                role = self._objectForFocusGrab.getRole()
                if self._objectForFocusGrab.getState().contains(\
                    pyatspi.STATE_FOCUSABLE):
                    break
                # Links in image maps seem to lack state focusable. If we're
                # on such an object, we still want to grab focus on it.
                #
                elif role == pyatspi.ROLE_LINK:
                    parent = self._objectForFocusGrab.parent
                    if parent.getRole() == pyatspi.ROLE_IMAGE:
                        break

                self._objectForFocusGrab = self._objectForFocusGrab.parent

            if self._objectForFocusGrab:
                # [[[See https://bugzilla.mozilla.org/show_bug.cgi?id=363214.
                # We need to set focus on the parent of the document frame.]]]
                #
                # [[[WDW - additional note - just setting focus on the
                # first focusable object seems to do the trick, so we
                # won't follow the advice from 363214.  Besides, if we
                # follow that advice, it doesn't work.]]]
                #
                #if objectForFocus.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
                #    objectForFocus = objectForFocus.parent
                self._objectForFocusGrab.queryComponent().grabFocus()

        text = self.queryNonEmptyText(obj)
        if text:
            text.setCaretOffset(characterOffset)
            if characterOffset == text.characterCount:
                characterOffset -= 1
                mag.magnifyAccessible(None,
                                      obj,
                                      self.getExtents(obj,
                                                      characterOffset,
                                                      characterOffset + 1))

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

        [obj, startOffset, endOffset] = contents[0]
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
                [obj, startOffset, endOffset] = contents[0]

        self.setCaretPosition(obj, startOffset)
        self.updateBraille(obj)
        self.speakContents(contents)

    def goNextWord(self, inputEvent):
        """Positions the caret offset to the end of next word or object
        in the document window.
        """

        [obj, characterOffset] = self.getCaretContext()

        # Make sure we have a word.
        #
        characterOffset = max(0, characterOffset - 1)
        [obj, characterOffset] = \
            self.findNextCaretInOrder(obj, characterOffset)

        # To be consistent with Gecko's native navigation, we want to
        # move to the next word end boundary.
        #
        boundary = pyatspi.TEXT_BOUNDARY_WORD_END
        contents = self.getWordContentsAtOffset(obj, characterOffset, boundary)
        if not (len(contents) and contents[-1][2]):
            return

        [obj, startOffset, endOffset] = contents[-1]
        self.setCaretPosition(obj, endOffset)
        self.updateBraille(obj)
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
            currentLine = self.getLineContentsAtOffset(obj, characterOffset)

        prevObj = currentLine[0][0]
        prevOffset = currentLine[0][1]

        extents = self.getExtents(obj, characterOffset, characterOffset + 1)
        prevExtents = self.getExtents(prevObj, prevOffset, prevOffset + 1)
        while self.onSameLine(extents, prevExtents):
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
            documentFrame = self.getDocumentFrame()
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
                extents = self.getExtents(item[0], item[1], item[2])
                newX1 = extents[0]
                newX2 = newX1 + extents[2]
                if newX1 <= oldX <= newX2:
                    newObj = item[0]
                    newOffset = 0
                    text = self.queryNonEmptyText(prevObj)
                    if text:
                        newY = extents[1] + extents[3] / 2
                        newOffset = text.getOffsetAtPoint(oldX, newY, 0)
                        if newOffset >= 0:
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

        nextObj = currentLine[-1][0]
        nextOffset = currentLine[-1][2] - 1

        extents = self.getExtents(obj, characterOffset, characterOffset + 1)
        nextExtents = self.getExtents(nextObj, nextOffset, nextOffset + 1)
        while self.onSameLine(extents, nextExtents):
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
            documentFrame = self.getDocumentFrame()
            nextObj = self.findNextObject(nextObj, documentFrame)
            nextOffset = 0

        [nextObj, nextOffset] = \
                  self.findNextCaretInOrder(nextObj, max(0, nextOffset) - 1)

        if not script_settings.arrowToLineBeginning:
            extents = self.getExtents(obj,
                                      characterOffset,
                                      characterOffset + 1)
            oldX = extents[0]
            for item in nextLine:
                extents = self.getExtents(item[0], item[1], item[2])
                newX1 = extents[0]
                newX2 = newX1 + extents[2]
                if newX1 <= oldX <= newX2:
                    newObj = item[0]
                    newOffset = 0
                    text = self.queryNonEmptyText(nextObj)
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
        """
        [obj, characterOffset] = self.getCaretContext()
        [previousObj, previousCharOffset] = \
                                   self.findPreviousLine(obj, characterOffset)
        if not previousObj:
            return

        self.setCaretPosition(previousObj, previousCharOffset)
        self.presentLine(previousObj, previousCharOffset)

        # Debug...
        #
        #contents = self.getLineContentsAtOffset(previousObj,
        #                                        previousCharOffset)
        #self.dumpContents(inputEvent, contents)

    def goNextLine(self, inputEvent):
        """Positions the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.
        """

        [obj, characterOffset] = self.getCaretContext()
        [nextObj, nextCharOffset] = self.findNextLine(obj, characterOffset)

        if not nextObj:
            return

        self.setCaretPosition(nextObj, nextCharOffset)
        self.presentLine(nextObj, nextCharOffset)

        # Debug...
        #
        #contents = self.getLineContentsAtOffset(nextObj, nextCharOffset)
        #self.dumpContents(inputEvent, contents)

    def goBeginningOfLine(self, inputEvent):
        """Positions the caret offset at the beginning of the line."""

        [obj, characterOffset] = self.getCaretContext()
        line = self.currentLineContents \
               or self.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = line[0][0], line[0][1]
        self.setCaretPosition(obj, characterOffset)
        self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goEndOfLine(self, inputEvent):
        """Positions the caret offset at the end of the line."""

        [obj, characterOffset] = self.getCaretContext()
        line = self.currentLineContents \
               or self.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = line[-1][0], line[-1][2] - 1
        self.setCaretPosition(obj, characterOffset)
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
            comboBox = self.getAncestor(obj,
                                        [pyatspi.ROLE_COMBO_BOX],
                                        [pyatspi.ROLE_DOCUMENT_FRAME])
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
            characterOffset = self.getCharacterOffsetInParent(obj)
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
            if not self.isSameObject(obj, prevObj):
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

            elif self.isSameObject(obj, prevObj) \
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
            # Translators: when the user is attempting to locate a
            # particular object and the top of the web page has been
            # reached without that object being found, we "wrap" to
            # the bottom of the page and continuing looking upwards.
            # We need to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to bottom."))
            [prevObj, prevOffset] = self.getBottomOfFile()
            line = self.getLineContentsAtOffset(prevObj, prevOffset)
            useful = self.getMeaningfulObjectsFromLine(line)
            if useful:
                prevObj = useful[-1][0]
                prevOffset = useful[-1][1]
            found = not (prevObj is None)

        elif mayHaveGoneTooFar and self._nextLineContents:
            if not self.isSameObject(obj, prevObj):
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
            characterOffset = self.getCharacterOffsetInParent(obj)
            self.currentLineContents = None

        characterOffset = max(0, characterOffset)
        [nextObj, nextOffset] = [obj, characterOffset]
        found = False

        line = self.currentLineContents \
               or self.getLineContentsAtOffset(obj, characterOffset)

        while line and not found:
            useful = self.getMeaningfulObjectsFromLine(line)
            index = self.findObjectOnLine(nextObj, nextOffset, useful)
            if not self.isSameObject(obj, nextObj):
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
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the web page has been
            # reached without that object being found, we "wrap" to the
            # top of the page and continuing looking downwards. We need
            # to inform the user when this is taking place.
            #
            speech.speak(_("Wrapping to top."))
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
        if settings.inferLiveRegions:
            self.liveMngr.advancePoliteness(orca_state.locusOfFocus)
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            speech.speak(_("Live region support is off"))

    def monitorLiveRegions(self, inputEvent):
        if not settings.inferLiveRegions:
            settings.inferLiveRegions = True
            # Translators: this announces to the user that live region
            # are being monitored.
            #
            speech.speak(_("Live regions monitoring on"))
        else:
            settings.inferLiveRegions = False
            # Translators: this announces to the user that live region
            # are not being monitored.
            #
            self.liveMngr.flushMessages()
            speech.speak(_("Live regions monitoring off"))

    def setLivePolitenessOff(self, inputEvent):
        if settings.inferLiveRegions:
            self.liveMngr.setLivePolitenessOff()
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            speech.speak(_("Live region support is off"))

    def reviewLiveAnnouncement(self, inputEvent):
        if settings.inferLiveRegions:
            self.liveMngr.reviewLiveAnnouncement( \
                                    int(inputEvent.event_string[1:]))
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            speech.speak(_("Live region support is off"))

    def toggleCaretNavigation(self, inputEvent):
        """Toggles between Firefox native and Orca caret navigation."""

        if script_settings.controlCaretNavigation:
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.removeByHandler(keyBinding.handler)
            script_settings.controlCaretNavigation = False
            # Translators: Gecko native caret navigation is where
            # Firefox itself controls how the arrow keys move the caret
            # around HTML content.  It's often broken, so Orca needs
            # to provide its own support.  As such, Orca offers the user
            # the ability to switch between the Firefox mode and the
            # Orca mode.
            #
            string = _("Gecko is controlling the caret.")
        else:
            script_settings.controlCaretNavigation = True
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.add(keyBinding)
            # Translators: Gecko native caret navigation is where
            # Firefox itself controls how the arrow keys move the caret
            # around HTML content.  It's often broken, so Orca needs
            # to provide its own support.  As such, Orca offers the user
            # the ability to switch between the Firefox mode and the
            # Orca mode.
            #
            string = _("Orca is controlling the caret.")

        debug.println(debug.LEVEL_CONFIGURATION, string)
        speech.speak(string)
        braille.displayMessage(string)

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
