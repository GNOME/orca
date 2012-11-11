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
import re
import time
import urlparse

import orca.braille as braille
import orca.debug as debug
import orca.scripts.default as default
import orca.eventsynthesizer as eventsynthesizer
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.liveregions as liveregions
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
        self.grabFocusOnAncestorCheckButton = None

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

        # guessTheLabel() is an expensive method. If we cache the guessed
        # labels, we'll see a performance improvement when a form field
        # is Tab/Shift+Tab'ed/Arrowed back to. In addition, we can check
        # for non-label labels when looking at line content.
        #
        self._guessedLabels = {}

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

        # All of the text attributes available for presentation to the
        # user. This is necessary because the attributes used by Gecko
        # are different from the default set.
        #
        self.allTextAttributes = \
            "background-color:; color:; font-family:; font-size:; " \
            "font-style:normal; font-weight:400; language:none; " \
            "text-line-through-style:; text-align:start; text-indent:0px; " \
            "text-underline-style:; text-position:baseline; " \
            "invalid:none; writing-mode:lr;"

        # The default set of text attributes to present to the user. This
        # is necessary because the attributes used by Gecko are different
        # from the default set.
        #
        self.enabledBrailledTextAttributes = \
          "font-size:; font-family:; font-weight:400; text-indent:0px; " \
          "text-underline-style:none; text-align:start; " \
          "text-line-through-style:none; font-style:normal; invalid:none;"
        self.enabledSpokenTextAttributes = \
          "font-size:; font-family:; font-weight:400; text-indent:0px; " \
          "text-underline-style:none; text-align:start; " \
          "text-line-through-style:none; font-style:normal; invalid:none;"

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

        # We need to save our special attributes so that we can revert to
        # the default text attributes when giving up focus to another app
        # and restore them upon return.
        #
        self.savedEnabledBrailledTextAttributes = None
        self.savedEnabledSpokenTextAttributes = None
        self.savedAllTextAttributes = None

        # Keep track of the last object which appeared as a result of
        # the user routing the mouse pointer over an object. Also keep
        # track of the object which is associated with the mouse over
        # so that we can restore focus to it if need be.
        #
        self.lastMouseOverObject = None
        self.preMouseOverContext = [None, -1]
        self.inMouseOverObject = False

        # See bug 665522 - comment 5
        app.setCacheMask(pyatspi.cache.ALL ^ pyatspi.cache.CHILDREN)

    def activate(self):
        """Called when this script is activated."""
        self.savedEnabledBrailledTextAttributes = \
            _settingsManager.getSetting('enabledBrailledTextAttributes')
        _settingsManager.setSetting(
            'enabledBrailledTextAttributes', self.enabledBrailledTextAttributes)

        self.savedEnabledSpokenTextAttributes = \
            _settingsManager.getSetting('enabledSpokenTextAttributes')
        _settingsManager.setSetting(
            'enabledSpokenTextAttributes', self.enabledSpokenTextAttributes)

        self.savedAllTextAttributes = \
            _settingsManager.getSetting('allTextAttributes')
        _settingsManager.setSetting('allTextAttributes', self.allTextAttributes)

        default.Script.activate(self)

    def deactivate(self):
        """Called when this script is deactivated."""
        _settingsManager.setSetting('enabledBrailledTextAttributes',
                                    self.savedEnabledBrailledTextAttributes)
        _settingsManager.setSetting('enabledSpokenTextAttributes',
                                    self.savedEnabledSpokenTextAttributes)
        _settingsManager.setSetting('allTextAttributes',
                                    self.savedAllTextAttributes)

        default.Script.deactivate(self)

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
                # Translators: this string refers to an Orca command which
                # advances the live region "politeness" setting from one
                # level to the next.
                #
                # The term "live region" refers to dynamically updated
                # content, typically on a web page, about which a user
                # likely wants to be notified. For instance, a stock
                # ticker on a financial site or a table of updated scores
                # on a sports site. In contast, a countdown timer or clock
                # on a web site is NOT a live region.
                #
                # The "politeness" level is an indication of when the user
                # wishes to be notified about a change to live region content,
                # e.g. never ("off"), when idle ("polite"), or when there is
                # a change ("assertive").
                #
                _("Advance live region politeness setting."))

        self.inputEventHandlers["setLivePolitenessOff"] = \
            input_event.InputEventHandler(
                Script.setLivePolitenessOff,
                # Translators: this string refers to an Orca command which
                # turns changes the live region "politness" level to "off."
                #
                # The term "live region" refers to dynamically updated
                # content, typically on a web page, about which a user
                # likely wants to be notified. For instance, a stock
                # ticker on a financial site or a table of updated scores
                # on a sports site. In contast, a countdown timer or clock
                # on a web site is NOT a live region.
                #
                # The "politeness" level is an indication of when the user
                # wishes to be notified about a change to live region content,
                # e.g. never ("off"), when idle ("polite"), or when there is
                # a change ("assertive").
                #
                _("Set default live region politeness level to off."))

        self.inputEventHandlers["monitorLiveRegions"] = \
            input_event.InputEventHandler(
                Script.monitorLiveRegions,
                # Translators: this string refers to an Orca command which
                # allows the user to toggle whether or not Orca pays attention
                # to changes in live regions. Note that turning off monitoring
                # of live events is NOT the same as turning the politeness level
                # to "off". The user can opt to have no notifications presented
                # (politeness level of "off") and still manually review recent
                # updates to live regions via Orca commands for doing so -- as
                # long as the monitoring of live regions is enabled.
                #
                _("Monitor live regions."))

        self.inputEventHandlers["reviewLiveAnnouncement"] = \
            input_event.InputEventHandler(
                Script.reviewLiveAnnouncement,
                # Translators: this is for reviewing up to nine stored
                # previous live messages. Please see previous translator
                # notes for more information on live regions.
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

        self.inputEventHandlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                # Translators: a refreshable braille display is an
                # external hardware device that presents braille
                # character to the user.  There are a limited number
                # of cells on the display (typically 40 cells).  Orca
                # provides the feature to build up a longer logical
                # line and allow the user to press buttons on the
                # braille display so they can pan left and right over
                # this line.
                #
                _("Pans the braille display to the left."),
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                # Translators: a refreshable braille display is an
                # external hardware device that presents braille
                # character to the user.  There are a limited number
                # of cells on the display (typically 40 cells).  Orca
                # provides the feature to build up a longer logical
                # line and allow the user to press buttons on the
                # braille display so they can pan left and right over
                # this line.
                #
                _("Pans the braille display to the right."),
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["moveToMouseOverHandler"] = \
            input_event.InputEventHandler(
                Script.moveToMouseOver,
                # Translators: hovering the mouse over certain objects
                # on a web page causes a new object to appear such as
                # a pop-up menu. This command will move the user to the
                # object which just appeared as a result of the user
                # hovering the mouse. If the user is already in the
                # mouse over object, this command will hide the mouse
                # over and return the user to the object he/she was in.
                #
                _("Moves focus into and away from the current mouse over."))

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

        return listeners

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

        # Translators: this is the title of a panel holding options for
        # how to navigate HTML content (e.g., Orca caret navigation,
        # positioning of caret, etc.).
        #
        label = Gtk.Label(label="<b>%s</b>" % _("Page Navigation"))
        label.set_use_markup(True)
        generalFrame.set_label_widget(label)

        generalAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        generalAlignment.set_padding(0, 0, 12, 0)
        generalFrame.add(generalAlignment)
        generalGrid = Gtk.Grid()
        generalAlignment.add(generalGrid)

        # Translators: Gecko native caret navigation is where
        # Firefox itself controls how the arrow keys move the caret
        # around HTML content.  It's often broken, so Orca needs
        # to provide its own support.  As such, Orca offers the user
        # the ability to switch between the Firefox mode and the
        # Orca mode.
        #
        label = _("Use _Orca Caret Navigation")
        value = script_settings.controlCaretNavigation
        self.controlCaretNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.controlCaretNavigationCheckButton.set_active(value) 
        generalGrid.attach(self.controlCaretNavigationCheckButton, 0, 0, 1, 1)

        # Translators: Orca provides keystrokes to navigate HTML content
        # in a structural manner: go to previous/next header, list item,
        # table, etc.
        #
        label = _("Use Orca _Structural Navigation")
        value = self.structuralNavigation.enabled
        self.structuralNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.structuralNavigationCheckButton.set_active(value)
        generalGrid.attach(self.structuralNavigationCheckButton, 0, 1, 1, 1)

        # Translators: Orca has had to implement its own caret navigation
        # model to work around issues in Gecko/Firefox. In certain versions
        # of Firefox, we must perform a focus grab on each object being
        # navigated in order for things to work as expected; in other
        # versions of Firefox, we must avoid doing so in order for things
        # to work as expected. We cannot identify with certainty which
        # situation the user is in, so we must provide this as an option
        # within Orca.
        #
        label = _("_Grab focus on objects when navigating")
        value = script_settings.grabFocusOnAncestor
        self.grabFocusOnAncestorCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.grabFocusOnAncestorCheckButton.set_active(value)
        generalGrid.attach(self.grabFocusOnAncestorCheckButton, 0, 2, 1, 1)

        # Translators: when the user arrows up and down in HTML content,
        # it is some times beneficial to always position the cursor at the
        # beginning of the line rather than guessing the position directly
        # above the current cursor position.  This option allows the user
        # to decide the behavior they want.
        #
        label = \
            _("_Position cursor at start of line when navigating vertically")
        value = script_settings.arrowToLineBeginning
        self.arrowToLineBeginningCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.arrowToLineBeginningCheckButton.set_active(value)
        generalGrid.attach(self.arrowToLineBeginningCheckButton, 0, 3, 1, 1)

        # Translators: when the user loads a new page in Firefox, they
        # can optionally tell Orca to automatically start reading a
        # page from beginning to end.
        #
        label = \
            _("Automatically start speaking a page when it is first _loaded")
        value = script_settings.sayAllOnLoad
        self.sayAllOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.sayAllOnLoadCheckButton.set_active(value)
        generalGrid.attach(self.sayAllOnLoadCheckButton, 0, 4, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 1, 1, 1)

        # Translators: this is the title of a panel containing options
        # for specifying how to navigate tables in document content.
        #
        label = Gtk.Label(label="<b>%s</b>" % _("Table Navigation"))
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        # Translators: this is an option to tell Orca whether or not it
        # should speak table cell coordinates in document content.
        #
        label = _("Speak _cell coordinates")
        value = _settingsManager.getSetting('speakCellCoordinates')
        self.speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self.speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        # Translators: this is an option to tell Orca whether or not it
        # should speak the span size of a table cell (e.g., how many
        # rows and columns a particular table cell spans in a table).
        #
        label = _("Speak _multiple cell spans")
        value = _settingsManager.getSetting('speakCellSpan')
        self.speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self.speakCellSpanCheckButton, 0, 1, 1, 1)

        # Translators: this is an option for whether or not to speak
        # the header of a table cell in document content.
        #
        label = _("Announce cell _header")
        value = _settingsManager.getSetting('speakCellHeaders')
        self.speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self.speakCellHeadersCheckButton, 0, 2, 1, 1)
           
        # Translators: this is an option to allow users to skip over
        # empty/blank cells when navigating tables in document content.
        #
        label = _("Skip _blank cells")
        value = _settingsManager.getSetting('skipBlankCells')
        self.skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self.skipBlankCellsCheckButton, 0, 3, 1, 1)

        findFrame = Gtk.Frame()
        grid.attach(findFrame, 0, 2, 1, 1)

        # Translators: this is the title of a panel containing options
        # for using Firefox's Find toolbar.
        #
        label = Gtk.Label(label="<b>%s</b>" % _("Find Options"))
        label.set_use_markup(True)
        findFrame.set_label_widget(label)

        findAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        findAlignment.set_padding(0, 0, 12, 0)
        findFrame.add(findAlignment)
        findGrid = Gtk.Grid()
        findAlignment.add(findGrid)

        # Translators: this is an option to allow users to have Orca
        # automatically speak the line that contains the match while
        # the user is still in Firefox's Find toolbar.
        #
        label = _("Speak results during _find")
        value = script_settings.speakResultsDuringFind
        self.speakResultsDuringFindCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakResultsDuringFindCheckButton.set_active(value)
        findGrid.attach(self.speakResultsDuringFindCheckButton, 0, 0, 1, 1)

        # Translators: this is an option which dictates whether the line
        # that contains the match from the Find toolbar should always
        # be spoken, or only spoken if it is a different line than the
        # line which contained the last match.
        #
        label = _("Onl_y speak changed lines during find")
        value = script_settings.onlySpeakChangedLinesDuringFind
        self.changedLinesOnlyCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.changedLinesOnlyCheckButton.set_active(value)
        findGrid.attach(self.changedLinesOnlyCheckButton, 0, 1, 1, 1)

        hgrid = Gtk.Grid()
        findGrid.attach(hgrid, 0, 2, 1, 1)

        # Translators: this option allows the user to specify the number
        # of matched characters that must be present before Orca speaks
        # the line that contains the results from the Find toolbar.
        #
        self.minimumFindLengthLabel = \
              Gtk.Label(label=_("Minimum length of matched text:"))
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

        value = self.grabFocusOnAncestorCheckButton.get_active()
        prefs.writelines("%s.grabFocusOnAncestor = %s\n" % (prefix, value))
        script_settings.grabFocusOnAncestor = value

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
                if isinstance(element, basestring):
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

        notify = False

        # Find out if the caret really moved. Firefox 3.1 gives us caret-moved
        # events when certain focusable objects first get focus. If we haven't
        # really moved, there's no point in updating braille again -- which is
        # what we'll wind up doing if this event reaches the default script.
        #
        [obj, characterOffset] = self.getCaretContext()
        if max(0, characterOffset) == event.detail1 \
           and self.utilities.isSameObject(obj, event.source):
            return

        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            string, mods = self.utilities.lastKeyAndModifiers()
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
                if not self.utilities.isEntry(event.source) \
                   and self.utilities.isSameObject(
                        event.source, orca_state.locusOfFocus):
                    return

                # We are getting extraneous events that are not being caught
                # by the above, and which are causing us to loop. See bug
                # #552887. This is admittedly a rather broad check. However,
                # if we're here it's because we're controlling the caret in
                # which case we don't expect to get caret moved events of
                # interest other than those mentioned above.
                #
                if locusOfFocusRole == pyatspi.ROLE_IMAGE:
                    return
                elif locusOfFocusRole == pyatspi.ROLE_LINK:
                    # Be sure it's not a same-page link. While such beasts
                    # typically point to anchors, they can point to other
                    # objects referencing them by name or ID. Therefore,
                    # get the URI for the link of interest and parse it.
                    # parsed URI is returned as a tuple containing six
                    # components: 
                    # scheme://netloc/path;parameters?query#fragment.
                    try:
                        uri = self.utilities.uri(orca_state.locusOfFocus)
                        uriInfo = urlparse.urlparse(uri)
                    except:
                        pass
                    else:
                        if uriInfo and not uriInfo[5]:
                            return
                        else:
                            notify = True
                elif eventSourceRole == pyatspi.ROLE_SECTION:
                    # Google Calendar's Day grid seems to issue these quite
                    # a bit. If we don't ignore them, we'll loop.
                    #
                    return

            elif not self.isNavigableAria(event.source):
                if script_settings.controlCaretNavigation:
                    return

            elif self.isAriaWidget(orca_state.locusOfFocus) \
                 and self.utilities.isSameObject(event.source,
                                       orca_state.locusOfFocus.parent):
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
                if self.utilities.inFindToolbar():
                    self.presentFindResults(event.source, event.detail1)
                else:
                    self.setCaretContext(event.source, event.detail1)
                return

        # If we're still here, and in document content, update the caret
        # context and set the locusOfFocus so that the default script's
        # onCaretMoved will handle.
        #
        if eventSourceInDocument and not self.isAriaWidget(event.source):
            if not self.utilities.isEntry(event.source):
                [obj, characterOffset] = \
                    self.findFirstCaretContext(event.source, event.detail1)
            else:
                [obj, characterOffset] = [event.source, event.detail1]
            self.setCaretContext(obj, characterOffset)
            orca.setLocusOfFocus(event, obj, notifyScript=notify)
            if notify:
                # No point in double-brailling the locusOfFocus.
                #
                return

        # Pass the event along to the default script for processing.
        #
        default.Script.onCaretMoved(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an an object.

        Arguments:
        - event: the Event
        """

        self._destroyLineCache()

        # If text is removed from something which is not editable, trash our
        # saved guessed labels to be on the safe side.
        #
        if not event.source.getState().contains(pyatspi.STATE_EDITABLE):
            self._guessedLabels = {}

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

        # If text is inserted into something which is not editable, trash our
        # saved guessed labels to be on the safe side.
        #
        if not event.source.getState().contains(pyatspi.STATE_EDITABLE):
            self._guessedLabels = {}

        # handle live region events
        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

        default.Script.onTextInserted(self, event)

    def _getCtrlShiftSelectionsStrings(self):
        return [
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            _("line selected down from cursor position"),
            _("line unselected down from cursor position"),
            _("line selected up from cursor position"),
            _("line unselected up from cursor position"),
        ]

    def onTextSelectionChanged(self, event):
        """Called when an object's text selection changes.

        Arguments:
        - event: the Event
        """

        if not self.inDocumentContent(orca_state.locusOfFocus) \
           and self.inDocumentContent(event.source):
            return

        default.Script.onTextSelectionChanged(self, event)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        try:
            role = event.source.getRole()
        except:
            pass
        else:
            if role == pyatspi.ROLE_MENU:
                try:
                    parent = event.source.parent
                    parentRole = parent.getRole()
                except:
                    pass
                else:
                    if parentRole == pyatspi.ROLE_COMBO_BOX:
                        self.visualAppearanceChanged(event, parent)
                        return

        default.Script.onSelectionChanged(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed.  In particular, we are looking
        for addition events often associated with Javascipt insertion.  One such
        such example would be the programmatic insertion of a tooltip or alert
        dialog."""

        # If children are being added or removed, trash our saved guessed
        # labels to be on the safe side.
        #
        self._guessedLabels = {}

        # no need moving forward if we don't have our target.
        if event.any_data is None:
            return

        # If we just routed the mouse pointer to our current location,
        # we should say something about what resulted.
        #
        if self.lastMouseRoutingTime \
           and 0 < time.time() - self.lastMouseRoutingTime < 1 \
           and event.type.startswith("object:children-changed:add"):
            utterances = []
            # Translators: Orca has a command that moves the mouse
            # pointer to the current location on a web page. If
            # moving the mouse pointer caused an item to appear
            # such as a pop-up menu, we want to present that fact.
            #
            utterances.append(_("New item has been added"))
            utterances.extend(
                self.speechGenerator.generateSpeech(event.any_data,
                                                    force = True))
            speech.speak(utterances)
            self.lastMouseOverObject = event.any_data
            self.preMouseOverContext = self.getCaretContext()
            return

        # handle live region events
        if self.handleAsLiveRegion(event):
            self.liveMngr.handleEvent(event)
            return

        if event.type.startswith("object:children-changed:add"):
            try:
                role = event.source.getRole()
                childRole = event.any_data.getRole()
            except:
                return

            if not (childRole == pyatspi.ROLE_ALERT \
               and role in [pyatspi.ROLE_SCROLL_PANE, pyatspi.ROLE_FRAME]):
                return

            utterances = []
            utterances.append(
                self.speechGenerator.getLocalizedRoleName(event.any_data))
            verbosity = _settingsManager.getSetting('speechVerbosityLevel')
            if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                utterances.extend(
                    self.speechGenerator.generateSpeech(event.any_data))
            speech.speak(utterances)

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
        if self.utilities.isSameObject(event.source, self._objectForFocusGrab):
            [obj, characterOffset] = self.getCaretContext()
            if not self.utilities.isSameObject(event.source, obj):
                return

        self._objectForFocusGrab = None

        # We also ignore focus events on the panel that holds the document
        # frame.  We end up getting these typically because we've called
        # grabFocus on this panel when we're doing caret navigation.  In
        # those cases, we want the locus of focus to be the subcomponent
        # that really holds the caret.
        #
        if eventSourceRole == pyatspi.ROLE_PANEL:
            documentFrame = self.utilities.documentFrame()
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
                containingPanel = self.utilities.ancestorWithRole(
                    orca_state.locusOfFocus,
                    [pyatspi.ROLE_PANEL],
                    [pyatspi.ROLE_DOCUMENT_FRAME])
                if self.utilities.isSameObject(containingPanel, event.source):
                    return

        # When we get a focus event on the document frame, it's usually
        # because we did a grabFocus on its parent in setCaretPosition.
        # We try to handle this here by seeing if there is already a
        # caret context for the document frame.  If we succeed, then
        # we set the focus on the object that's holding the caret.
        #
        if eventSourceRole == pyatspi.ROLE_DOCUMENT_FRAME \
           and not event.source.getState().contains(pyatspi.STATE_EDITABLE):
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

        elif eventSourceRole != pyatspi.ROLE_LINK \
             and self.inDocumentContent(event.source) \
             and not self.isAriaWidget(event.source):
            [obj, characterOffset] = \
                self.findFirstCaretContext(event.source, 0)
            self.setCaretContext(obj, characterOffset)
            if not self.utilities.isSameObject(event.source, obj):
                if not self.utilities.isSameObject(
                        obj, orca_state.locusOfFocus):
                    orca.setLocusOfFocus(event, obj, notifyScript=False)
                    # If an alert got focus, let's do the best we can to 
                    # try to automatically speak its contents while also
                    # making sure the locus of focus and caret context
                    # are in the right spot for braille and caret navigation.
                    # http://bugzilla.gnome.org/show_bug.cgi?id=570551
                    #
                    if eventSourceRole == pyatspi.ROLE_ALERT:
                        speech.speak(self.speechGenerator.generateSpeech(
                                event.source))
                        self.updateBraille(obj)
                    else:
                        self.presentLine(obj, characterOffset)
                return

        default.Script.onFocus(self, event)

    def onLinkSelected(self, event):
        """Called when a link gets selected.  Note that in Firefox 3,
        link selected events are not issued when a link is selected.
        Instead, a focus: event is issued.  This is 'old' code left
        over from Yelp and Firefox 2.

        Arguments:
        - event: the Event
        """

        text = self.utilities.queryNonEmptyText(event.source)
        hypertext = event.source.queryHypertext()
        linkIndex = self.utilities.linkIndex(event.source, text.caretOffset)

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
            speech.speak(
                self.speechGenerator.getLocalizedRoleName(event.source),
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
            self.visualAppearanceChanged(event, event.source)
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
                    level = _settingsManager.getSetting('speechVerbosityLevel')
                    speakIt = level == settings.VERBOSITY_LEVEL_VERBOSE
                    if not speakIt \
                       and isinstance(orca_state.lastInputEvent, 
                                      input_event.KeyboardEvent):
                        keyEvent = orca_state.lastNonModifierKeyEvent
                        speakIt = (keyEvent.event_string == ("Down"))
                    if speakIt:
                        speech.speak(self.speechGenerator.getLocalizedRoleName(\
                                event.source, pyatspi.ROLE_AUTOCOMPLETE))

        # We care when the document frame changes it's busy state.  That
        # means it has started/stopped loading content.
        #
        if event.type.startswith("object:state-changed:busy"):
            if event.source \
                and (event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME):

                # If content is changing, trash our saved guessed labels.
                #
                self._guessedLabels = {}

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

                    # Translators: this is in reference to loading a web page
                    # or some other content.
                    #
                    message = _("Loading.  Please wait.")

                elif event.source.name:
                    # Translators: this is in reference to loading a web page
                    # or some other content.
                    #
                    message = _("Finished loading %s.") % event.source.name
                    finishedLoading = True

                else:
                    # Translators: this is in reference to loading a web page
                    # or some other content.
                    #
                    message = _("Finished loading.")
                    finishedLoading = True

                if not _settingsManager.getSetting('onlySpeakDisplayedText'):
                    self.presentMessage(message)

                if finishedLoading:
                    # Store the document frame otherwise the first time it
                    # gains focus (e.g. the first time the user arrows off
                    # of a link into non-focusable text), onStateFocused
                    # will start chatting unnecessarily.
                    #
                    self._currentFrame = event.source

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
                        speech.speak(self.speechGenerator.generateSpeech(obj))
                    elif not script_settings.sayAllOnLoad:
                        self.speakContents(\
                            self.getLineContentsAtOffset(obj,
                                                         characterOffset))
                    elif _settingsManager.getSetting('enableSpeech'):
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

            self.displayBrailleMessage(documentFrame.name)
            speech.stop()
            speech.speak(
                "%s %s" \
                % (documentFrame.name,
                   self.speechGenerator.getLocalizedRoleName(
                        documentFrame, pyatspi.ROLE_PAGE_TAB)))

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
        if not self.utilities.hasMatchingHierarchy(event.source, rolesList):
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

        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON \
           and self.utilities.isSameObject(orca_state.locusOfFocus, obj):
            msg = self.speechGenerator.generateSpeech(obj, alreadyFocused=True)
            if self.inDocumentContent(obj):
                speech.speak(msg)
            self.updateBraille(obj)
            return

        if (obj.getRole() == pyatspi.ROLE_CHECK_BOX) \
            and obj.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, obj, notifyScript=False)

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
        if self.utilities.isSameObject(oldLocusOfFocus, newLocusOfFocus):
            return

        # We always automatically go back to focus tracking mode when
        # the focus changes.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # Try to handle the case where a spurious focus event was tossed
        # at us.
        #
        if newLocusOfFocus and self.inDocumentContent(newLocusOfFocus):
            text = self.utilities.queryNonEmptyText(newLocusOfFocus)
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
                    oldFrame = self.utilities.ancestorWithRole(
                        oldLocusOfFocus, [pyatspi.ROLE_FRAME], [])
                    newFrame = self.utilities.ancestorWithRole(
                        newLocusOfFocus, [pyatspi.ROLE_FRAME], [])
                    if self.utilities.isSameObject(oldFrame, newFrame) or \
                           newLocusOfFocus.getRole() == pyatspi.ROLE_DIALOG:
                        self.setCaretPosition(newLocusOfFocus, caretOffset)
                        self.presentLine(newLocusOfFocus, caretOffset)
                        return

            else:
                caretOffset = 0
            [obj, characterOffset] = \
                  self.findFirstCaretContext(newLocusOfFocus, caretOffset)
            self.setCaretContext(obj, characterOffset)

        else:
            # If the newLocusOfFocus is not in document content, trash
            # our stored guessed labels. This will hopefully maximize
            # performance and accuracy when navigating amongst form 
            # fields while minimizing the cache size (Gecko creates and
            # destroys accessibles so frequently that hashing is of no
            # use).
            #
            self._guessedLabels = {}

        # If we've just landed in the Find toolbar, reset
        # self.madeFindAnnouncement.
        #
        if newLocusOfFocus and self.utilities.inFindToolbar(newLocusOfFocus):
            self.madeFindAnnouncement = False

        # We'll ignore focus changes when the document frame is busy.
        # This will keep Orca from chatting too much while a page is
        # loading. But we should check to be sure the document frame
        # is really busy first and also that the event is not coming
        # from an object within a dialog box or alert.
        #
        if self.inDocumentContent(event.source):
            documentFrame = self.utilities.documentFrame()
        else:
            documentFrame = None
        if documentFrame:
            self._loadingDocumentContent = \
                documentFrame.getState().contains(pyatspi.STATE_BUSY)

            if self._loadingDocumentContent and event and event.source:
                dialogRoles = [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]
                inDialog = event.source.getRole() in dialogRoles \
                    or self.utilities.ancestorWithRole(
                    event.source, dialogRoles, [pyatspi.ROLE_DOCUMENT_FRAME])

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
            speech.speak(
                self.speechGenerator.getLocalizedRoleName(newLocusOfFocus))
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

        if not self.inDocumentContent():
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
                # Translators: the 'h' below represents a heading level
                # attribute for content that you might find in something
                # such as HTML content (e.g., <h1>). The translated form
                # is meant to be a single character followed by a numeric
                # heading level, where the single character is to indicate
                # 'heading'.
                #
                headingString = _("h%d" % level)
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

        print("---")
        text = self.utilities.queryNonEmptyText(obj)
        if text and obj.getRole() != pyatspi.ROLE_DOCUMENT_FRAME:
            string = text.getText(0, -1)
        else:
            string = ""
        print(obj, obj.name, obj.getRole(), \
              obj.accessible.getIndexInParent(), string)
        offset = self.utilities.characterOffsetInParent(obj)
        if offset >= 0:
            print("  offset =", offset)

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
                if self.utilities.queryNonEmptyText(obj):
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
                        index = self.utilities.cellIndex(obj)
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
                text = self.utilities.queryNonEmptyText(obj)
                if text:
                    string += "[%s] text='%s' " % (obj.getRole(),
                                                   text.getText(startOffset,
                                                                endOffset))
                else:
                    string += "[%s] name='%s' " % (obj.getRole(), obj.name)
            else:
                string += "\nNEWLINE\n"
        print("===========================")
        print(string)
        self.drawOutline(extents[0], extents[1], extents[2], extents[3])

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

        if self._loadingDocumentContent:
            return False

        weHandleIt = True
        obj = orca_state.locusOfFocus
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
            if state.contains(pyatspi.STATE_SHOWING):
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

        # We will try to eliminate objects that cannot be considered live
        # regions.  We will handle everything else as a live region.  We
        # will do the cheap tests first
        if self._loadingDocumentContent \
           or not _settingsManager.getSetting('inferLiveRegions'):
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
                    attrList = attrs['xml-roles'].split()
                    if not 'alert' in attrList \
                       and not 'tooltip' in attrList:
                        return False
                    # Only present tooltips when user wants them presented
                    elif 'tooltip' in attrList \
                         and not _settingsManager.getSetting('presentToolTips'):
                        return False
            else:
                # Some alerts have been seen without the :system postfix.
                # We will take care of them separately.
                attrs = self._getAttrDictionary(event.any_data)
                if 'xml-roles' in attrs \
                   and 'alert' in attrs['xml-roles'].split():
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
        elif event.type.startswith('object:text-changed:insert'):
            # We do this since we sometimes get text inserted events
            # without the ":system" suffix for live regions (see bug
            # 550873).  [[[WDW - this probably could be conflated into
            # the block above, making that block check for just
            # object:text-changed:insert" events, but I wanted to be a
            # little more conservative since the live region stuff was
            # done long ago and I've forgotten many of the details.]]]
            #
            stateset = event.source.getState()
            if stateset.contains(pyatspi.STATE_FOCUSABLE) \
                   or stateset.contains(pyatspi.STATE_SELECTABLE) \
                   or not stateset.contains(pyatspi.STATE_VISIBLE):
                return False
            attrs = self._getAttrDictionary(event.source)
            return 'container-live' in attrs \
                   or event.source.getRole() == pyatspi.ROLE_ALERT 
        else:
            return False

        # This last filter gets rid of some events that come in after
        # window:activate event.  They are usually areas of a page that
        # are built dynamically.
        if time.time() - self._loadingDocumentTime > 2.0:
            return True
        else:
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
        if text and text != u'\u00A0':
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
                                text = textObj.getText(0, -1).decode("UTF-8")
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
            try:
                char = char.decode("UTF-8")
            except UnicodeEncodeError:
                pass
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
                try:
                    char = char.decode("UTF-8")
                except UnicodeEncodeError:
                    pass
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
        text = ""
        extents = (0, 0, 0, 0)
        isField = False
        parentTable = self.utilities.ancestorWithRole(
            cell, [pyatspi.ROLE_TABLE], [pyatspi.ROLE_DOCUMENT_FRAME])
        if not cell or cell.getRole() != pyatspi.ROLE_TABLE_CELL \
           or not parentTable:
            return [newCell, text, extents, isField]

        [row, col] = self.getCellCoordinates(cell)
        table = parentTable.queryTable()
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
            objects = self.getObjectsFromEOCs(newCell, 0)
            if len(objects):
                extents = self.getExtents(objects[0][0], 
                                          objects[0][1],
                                          objects[0][2])
            for obj in objects:
                if obj[0].getRole() == pyatspi.ROLE_IMAGE:
                    text += obj[0].name
                elif not self.isFormField(obj[0]):
                    text += obj[3]
                else:
                    isField = True
                    text = ""
                    exts = obj[0].queryComponent().getExtents(0)
                    extents = [exts.x, exts.y, exts.width, exts.height]
                    break

        return [newCell, text, extents, isField]

    def getObjectsFromEOCs(self, obj, offset, boundary=None):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with [obj, startOffset, endOffset, string] tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - offset: the character offset after which
        - boundary: the pyatspi text boundary type

        Returns a list of object tuples.
        """

        if not obj:
            return []

        elif boundary and obj.getRole() == pyatspi.ROLE_TABLE:
            # If this is a table, move to the first cell -- or the caption,
            # if present.
            # [[[TODOS - JD:
            #    1) It might be nice to announce the fact that we've just
            #       found a table, what its dimensions are, etc.
            #    2) It seems that down arrow moves us to the table, but up
            #       arrow moves us to the last row.  Possible side effect
            #       of our existing caret browsing implementation??]]]
            #    3) Figure out why the heck the table of contents for at
            #       least some Yelp content consists of a table whose sole
            #       child is a list!!!
            if obj[0] and obj[0].getRole() in [pyatspi.ROLE_CAPTION,
                                               pyatspi.ROLE_LIST]:
                obj = obj[0]
            else:
                obj = obj.queryTable().getAccessibleAt(0, 0)

            if not obj:
                # Yelp (or perhaps the work-in-progress a11y patch) seems
                # to be guilty of this. Although that may have been the
                # table of contents thing (see #3 above).
                #
                #print "getObjectsFromEOCs - in Table, missing an accessible"
                debug.printStack(debug.LEVEL_WARNING)
                return []

        objects = []
        text = self.utilities.queryNonEmptyText(obj)
        if text:
            if boundary:
                [string, start, end] = \
                    text.getTextAfterOffset(offset, boundary)
            else:
                start = offset
                end = text.characterCount
                string = text.getText(start, end)
        else:
            string = ""
            start = 0
            end = 1

        unicodeText = string.decode("UTF-8")
        objects.append([obj, start, end, unicodeText])

        pattern = re.compile(self.EMBEDDED_OBJECT_CHARACTER)
        matches = re.finditer(pattern, unicodeText)

        offset = 0
        for m in matches:
            # Adjust the last object's endOffset to the last character
            # before the EOC.
            #
            childOffset = m.start(0) + start
            lastObj = objects[-1]
            lastObj[2] = childOffset
            if lastObj[1] == lastObj[2]:
                # A zero-length object is an indication of something
                # whose sole contents was an EOC.  Delete it from the
                # list.
                #
                objects.pop()
            else:
                # Adjust the string to reflect just this segment.
                #
                lastObj[3] = unicodeText[offset:m.start(0)]

            offset = m.start(0) + 1
 
            # Recursively tack on the child's objects.
            #
            childIndex = self.getChildIndex(obj, childOffset)
            child = obj[childIndex]
            objects.extend(self.getObjectsFromEOCs(child, 0, boundary))

            # Tack on the remainder of the original object, if any.
            #
            if end > childOffset + 1:
                restOfText = unicodeText[offset:len(unicodeText)]
                objects.append([obj, childOffset + 1, end, restOfText])
 
        if obj.getRole() in [pyatspi.ROLE_IMAGE, pyatspi.ROLE_TABLE]:
            # Imagemaps that don't have alternative text won't implement
            # the text interface, but they will have children (essentially
            # EOCs) that we need to get. The same is true for tables.
            #
            toAdd = []
            for child in obj:
                toAdd.extend(self.getObjectsFromEOCs(child, 0, boundary))
            if len(toAdd):
                if self.utilities.isSameObject(objects[-1][0], obj):
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
            elif self.utilities.isEntry(item[0]):
                labelGuess = self.guessLabelFromLine(item[0])
                index = len(lineContents) - 1
                while labelGuess and index >= 0:
                    prevItem = lineContents[index]
                    prevText = self.utilities.queryNonEmptyText(prevItem[0])
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
                text = self.utilities.queryNonEmptyText(item[0])
                if text:
                    string = text.getText(item[1], item[2]).decode("UTF-8")
                    if not len(string.strip()):
                        continue

            lineContents.append(item)

        return lineContents

    def getPageSummary(self, obj):
        """Returns the quantity of headings, forms, tables, visited links,
        and unvisited links on the page containing obj.
        """

        if _settingsManager.getSetting('useCollection'):
            try:
                summary = self._collectionPageSummary()
            except:
                summary = self._iterativePageSummary(obj)
        else:
            summary = self._iterativePageSummary(obj)

        return summary

    def _collectionPageSummary(self):
        """Uses the Collection interface to get the quantity of headings,
        forms, tables, visited and unvisited links.
        """

        docframe = self.utilities.documentFrame()
        col = docframe.queryCollection()
        # We will initialize these after the queryCollection() call in case
        # Collection is not supported
        #
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

    def _iterativePageSummary(self, obj):
        """Reads the quantity of headings, forms, tables, visited and
        unvisited links.
        """

        headings = 0
        forms = 0
        tables = 0
        vlinks = 0
        uvlinks = 0
        percentRead = None
        nodetotal = 0
        obj_index = None
        currentobj = obj

        # Start at the first object after document frame.
        #
        obj = self.utilities.documentFrame()[0]
        while obj:
            nodetotal += 1
            if obj == currentobj:
                obj_index = nodetotal
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

            obj = self.findNextObject(obj)

        # Calculate the percentage of the document that has been read.
        #
        if obj_index:
            percentRead = int(obj_index*100/nodetotal)

        return [headings, forms, tables, vlinks, uvlinks, percentRead]

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
        lineContents = self.currentLineContents
        ourIndex = self.findObjectOnLine(obj, 0, lineContents)
        if ourIndex < 0:
            lineContents = self.getLineContentsAtOffset(obj, 0)
            ourIndex = self.findObjectOnLine(obj, 0, lineContents)

        thisObj = lineContents[ourIndex]
        objExtents = self.getExtents(thisObj[0], thisObj[1], thisObj[2])

        leftGuess = ""
        extents = objExtents
        for i in range (ourIndex - 1, -1, -1):
            candidate, start, end, string = lineContents[i]
            if self.isFormField(candidate):
                break

            prevExtents = self.getExtents(candidate, start, end)
            if -1 <= extents[0] - (prevExtents[0] + prevExtents[2]) < 75:
                # The candidate might be an image with alternative text.
                #
                string = string or candidate.name
                leftGuess = string + leftGuess
                extents = prevExtents

        # Normally we prefer what's on the left given a choice.  Reasons
        # to prefer what's on the right include looking at a radio button
        # or a checkbox. [[[TODO - JD: Language direction should also be
        # taken into account.]]]
        #
        preferRight = obj.getRole() in [pyatspi.ROLE_CHECK_BOX,
                                        pyatspi.ROLE_RADIO_BUTTON]

        # Sometimes we don't want the text on the right -- at least not
        # until we are able to present labels on the right after the
        # object we believe they are labeling, rather than before.
        #
        preventRight = obj.getRole() == pyatspi.ROLE_COMBO_BOX

        rightGuess = ""
        extents = objExtents
        if not preventRight and (preferRight or not leftGuess):
            for i in range (ourIndex + 1, len(lineContents)):
                candidate, start, end, string = lineContents[i]
                # If we're looking on the right and find text, and then
                # find another nearby form field, the text we've found
                # might be the label for that field rather than for this
                # one. We'll assume that for now and bail under these
                # conditions.
                #
                if self.isFormField(candidate):
                    if not preferRight:
                        rightGuess = ""
                    break

                nextExtents = self.getExtents(candidate, start, end)
                if -1 <= nextExtents[0] - (extents[0] + extents[2]) < 75:
                    # The candidate might be an image with alternative text.
                    #
                    string = string or candidate.name
                    rightGuess += string
                    extents = nextExtents

        guess = rightGuess or leftGuess
        return guess.strip()

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

        # The labels for combo boxes won't be found below the combo box
        # because expanding the combo box will cover up the label. Labels
        # for lists probably won't be below the list either.
        #
        if obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                             pyatspi.ROLE_MENU,
                             pyatspi.ROLE_MENU_ITEM,
                             pyatspi.ROLE_LIST,
                             pyatspi.ROLE_LIST_ITEM]:
            [nextObj, nextOffset] = [None, 0]
            nextLineContents = []
        else:
            nextLineContents = self._nextLineContents
            if index > 0 and nextLineContents:
                nextObj = nextLineContents[0][0]
                nextOffset = nextLineContents[0][1]
            else:
                [nextObj, nextOffset] = self.findNextLine(obj, 0, False)
                nextLineContents = self.getLineContentsAtOffset(nextObj,
                                                                nextOffset)
        above = None
        lastExtents = (0, 0, 0, 0)
        for content in prevLineContents:
            aboveExtents = self.getExtents(content[0], content[1], content[2])

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
            if not above:
                if (objExtents != aboveExtents) and not aboveIsFormField:
                    xDiff = objExtents[0] - aboveExtents[0]
                    guessThis = (0 <= abs(xDiff) <= 2)
                    if not guessThis and (0 <= xDiff <= 50):
                        guessThis = \
                            (aboveExtents[0] + aboveExtents[2] > objExtents[0])
                    if guessThis:
                        above = content[0]
                        guessAbove = content[3]
            else:
                # The "label" might be comprised of several objects (e.g.
                # text with links).
                #
                lastEnd = lastExtents[0] + lastExtents[2]
                if lastEnd - aboveExtents[0] < 10 and not aboveIsFormField:
                    guessAbove += content[3]
                else:
                    break

            lastExtents = aboveExtents

        below = None
        lastExtents = (0, 0, 0, 0)
        for content in nextLineContents:
            belowExtents = self.getExtents(content[0], content[1], content[2])

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

            # If the horizontal starting point of the object is the
            # same as the horizontal starting point of the text
            # below it, the text below it is probably serving as the
            # label. We'll allow for a 2 pixel difference.
            #
            if not below:
                if (objExtents != belowExtents) and not belowIsFormField \
                   and 0 <= abs(objExtents[0] - belowExtents[0]) <= 2:
                    below = content[0]
                    guessBelow = content[3]
            else:
                # The "label" might be comprised of several objects (e.g.
                # text with links).
                #
                lastEnd = lastExtents[0] + lastExtents[2]
                if lastEnd - belowExtents[0] < 10 and not belowIsFormField:
                    guessBelow += content[3]
                else:
                    break

            lastExtents = belowExtents

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

        # If we're not the sole occupant of a table cell, we're either
        # not in a table at all or are in a more complex layout table
        # than this approach can handle.
        #
        containingCell = self.utilities.ancestorWithRole(
            obj, [pyatspi.ROLE_TABLE_CELL], [pyatspi.ROLE_DOCUMENT_FRAME])
        if not containingCell or containingCell.childCount > 1:
            return guess

        extents = obj.queryComponent().getExtents(0)
        objExtents = [extents.x, extents.y, extents.width, extents.height]

        [cellLeft, leftText, leftExtents, leftIsField] = \
                   self.getNextCellInfo(containingCell, "left")
        [cellRight, rightText, rightExtents, rightIsField] = \
                   self.getNextCellInfo(containingCell, "right")
        [cellAbove, aboveText, aboveExtents, aboveIsField] = \
                   self.getNextCellInfo(containingCell, "up")

        # The labels for combo boxes won't be found below the combo box
        # because expanding the combo box will cover up the label. Labels
        # for lists probably won't be below the list either.
        #
        if obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                             pyatspi.ROLE_MENU,
                             pyatspi.ROLE_MENU_ITEM,
                             pyatspi.ROLE_LIST,
                             pyatspi.ROLE_LIST_ITEM]:
            [cellBelow, belowText, belowExtents, belowIsField] = \
                    [None, "", (0, 0, 0, 0), False]
        else:
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
            nextCell = containingCell
            while nextCell:
                [nextCell, text, extents, isField] = \
                        self.getNextCellInfo(nextCell, "up")
                if nextCell:
                    dWidth = abs(objExtents[2] - extents[2])
                    dHeight = abs(objExtents[3] - extents[3])
                    if (dWidth > 1 or dHeight > 1):
                        if not isField:
                            [row, col] = self.getCellCoordinates(nextCell)
                            if row == 0:
                                guess = text
                        break

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

        # Maybe we've already made a guess and saved it.
        #
        for field, label in list(self._guessedLabels.items()):
            if self.utilities.isSameObject(field, obj):
                return label

        parent = obj.parent
        text = self.utilities.queryNonEmptyText(parent)

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
            # cell -- or in a table cell which contains multiple items
            # and/or line breaks.
            #
            if parent.getRole() != pyatspi.ROLE_TABLE_CELL \
               or parent.childCount > 1 \
               or (text and text.getText(0, -1).find("\n") >= 0):
                guess = self.guessLabelFromOtherLines(obj)
                #print "guess from other lines: ", guess
        if not guess:
            # We've pretty much run out of options.  From Tom's overview
            # of the approach for all controls:
            # "... 4. title attribute."
            # The title attribute seems to be exposed as the name.
            #
            guess = obj.name
            #print "Guessing the name: ", guess

        if obj.parent.getRole() == pyatspi.ROLE_LIST:
            obj = obj.parent

        guess = guess.strip()
        self._guessedLabels[obj] = guess

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

        text = self.utilities.queryNonEmptyText(obj)
        if text:
            unicodeText = self.utilities.unicodeText(obj)
            if characterOffset >= len(unicodeText):
                if not self.utilities.isEntry(obj):
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
        elif obj.getRole() == pyatspi.ROLE_TABLE:
            if obj[0] and obj[0].getRole() in [pyatspi.ROLE_CAPTION,
                                               pyatspi.ROLE_LIST]:
                obj = obj[0]
            else:
                obj = obj.queryTable().getAccessibleAt(0, 0)
            return self.findFirstCaretContext(obj, 0)
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

        elif includeNonText and (startOffset < 0) \
             and (not self.utilities.isLayoutOnly(obj)):
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

        elif includeNonText and (startOffset < 0) \
            and (not self.utilities.isLayoutOnly(obj)):
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
                return string.encode("UTF-8"), caretOffset, startOffset

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

        # Yelp is seemingly fond of killing children for sport. Better
        # check for that.
        #
        try:
            state = obj.getState()
        except:
            return [None, -1]
        else:
            if state.contains(pyatspi.STATE_DEFUNCT):
                #print "getCaretContext: defunct object", obj
                debug.printStack(debug.LEVEL_WARNING)
                [obj, caretOffset] = [None, -1]

        return [obj, caretOffset]

    def getCharacterAtOffset(self, obj, characterOffset):
        """Returns the character at the given characterOffset in the
        given object or None if the object does not implement the
        accessible text specialization.
        """

        try:
            unicodeText = self.utilities.unicodeText(obj)
            return unicodeText[characterOffset].encode("UTF-8")
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

        contents = self.getObjectsFromEOCs(obj, characterOffset, boundary)
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
            [line, start, end] = text.getTextAtOffset(offset, boundary)

            # Unfortunately, we sometimes get bogus results from Gecko when
            # we ask for this line. If the offset is not within the range of
            # characters on this line, try the character reported as the end.
            #
            if not (start <= offset < end):
                [line, start, end] = text.getTextAfterOffset(end, boundary)

            # If we're still seeing bogusity, which we only seem to see when
            # moving up, locate the previous character and use it instead.
            #
            if not (start <= offset < end):
                pObj, pOffset = self.findPreviousCaretInOrder(obj, offset)
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
        objects = self.getObjectsFromEOCs(obj, offset, boundary)

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
                toAdd = self.getObjectsFromEOCs(prevObj, pOffset, boundary)
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

            # The offset reported as the end offset can vary with Gecko.
            # If the offset is one bigger than we expect, we are in danger
            # of skipping over an object. Therefore, start by decrementing
            # the end offset by 1. If we find the same object, try again.
            #
            [nextObj, nOffset] = self.findNextCaretInOrder(lastObj, end - 1)
            if self.utilities.isSameObject(lastObj, nextObj):
                [nextObj, nOffset] = \
                    self.findNextCaretInOrder(nextObj, nOffset)

            if not nextObj or self.utilities.isSameObject(nextObj, lastObj):
                break

            text = self.utilities.queryNonEmptyText(nextObj)
            if text:
                line = text.getTextAfterOffset(nOffset, boundary)
                nOffset = line[1]

            nextExtents = self.getExtents(nextObj, nOffset, nOffset + 1)

            if self.onSameLine(extents, nextExtents) \
               and extents != nextExtents \
               and lastExtents != nextExtents \
               or nextExtents == (0, 0, 0, 0):
                toAdd = self.getObjectsFromEOCs(nextObj, nOffset, boundary)
                toAdd = [x for x in toAdd if x not in objects]
                objects.extend(toAdd)
            elif (nextObj.getRole() in [pyatspi.ROLE_SECTION,
                                        pyatspi.ROLE_TABLE_CELL] \
                  and self.isUselessObject(nextObj)):
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

        return objects

    def getObjectContentsAtOffset(self, obj, characterOffset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset, string] tuple.  The list is 
        created via an in-order traversal of the document contents 
        starting and stopping at the given object.
        """

        return self.getObjectsFromEOCs(obj, characterOffset)

    ####################################################################
    #                                                                  #
    # Methods to speak current objects.                                #
    #                                                                  #
    ####################################################################

    # [[[TODO: WDW - this needs to be moved to the speech generator.]]]
    #
    def getACSS(self, obj, string):
        """Returns the ACSS to speak anything for the given obj."""

        try:
            string = string.decode("UTF-8")
        except UnicodeEncodeError:
            pass

        if obj.getRole() == pyatspi.ROLE_LINK:
            acss = self.voices[settings.HYPERLINK_VOICE]
        elif string and isinstance(string, basestring) \
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
        doNotSpeakRoles = [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_HEADING]

        utterances = []
        prevObj = None
        for content in contents:
            [obj, startOffset, endOffset, string] = content
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
            # we had to guess the label, odds are that the guessed label is
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
                if self.guessTheLabel(prevObj) == string.strip():
                    continue

            # The radio button's label gets added to the context in
            # default.locusOfFocusChanged() and not through the speech
            # generator -- unless we wind up having to guess the label.
            # Therefore, if we have a valid label for a radio button,
            # we need to add it here.
            #
            if (role == pyatspi.ROLE_RADIO_BUTTON) \
                and not self.isAriaWidget(obj):
                label = self.utilities.displayedLabel(obj)
                if label:
                    utterances.append([label, self.getACSS(obj, label)])

            # If we don't have a string, then use the speech generator.
            # Otherwise, we'll want to speak the string and possibly the
            # role.
            #
            if not len(string) \
               or self.utilities.isEntry(obj) \
               or self.utilities.isPasswordText(obj):
                rv = self.speechGenerator.generateSpeech(obj)
                # Crazy crap to make clump and friends happy until we can
                # kill them. (They don't deal well with what the speech
                # generator provides.)
                for item in rv:
                    if isinstance(item, basestring):
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
                 and isinstance(element, basestring) \
                 and isinstance(clumped[-1][0], basestring):
                clumped[-1][0] = clumped[-1][0].rstrip(" ")
                try:
                    clumped[-1][0] = clumped[-1][0].decode("UTF-8")
                except UnicodeEncodeError:
                    pass
                try:
                    element = element.decode("UTF-8")
                except UnicodeEncodeError:
                    pass
                clumped[-1][0] += " " + element
            else:
                clumped.append([element, acss])

        if (len(clumped) == 1) and (clumped[0][0] == "\n"):
            if _settingsManager.getSetting('speakBlankLines'):
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                return [[_("blank"), self.voices[settings.SYSTEM_VOICE]]]

        if len(clumped) and isinstance(clumped[-1][0], basestring):
            clumped[-1][0] = clumped[-1][0].rstrip(" ")

        return clumped

    def speakContents(self, contents, speakRole=True):
        """Speaks each string in contents using the associated voice/acss"""
        utterances = self.getUtterancesFromContents(contents, speakRole)
        clumped = self.clumpUtterances(utterances)
        for [element, acss] in clumped:
            if isinstance(element, basestring):
                element = self.utilities.adjustForRepeats(element)
            speech.speak(element, acss, False)

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

        # Clear the flat review context if the user is currently in a
        # flat review.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        caretContext = self.getCaretContext()

        # Save where we are in this particular document frame.
        # We do this because the user might have several URLs
        # open in several different tabs, and we keep track of
        # where the caret is for each documentFrame.
        #
        documentFrame = self.utilities.documentFrame()
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
        if obj \
           and obj.getRole() in [pyatspi.ROLE_LIST, pyatspi.ROLE_COMBO_BOX] \
           and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            characterOffset = self.utilities.characterOffsetInParent(obj)
            obj = obj.parent
            self.setCaretContext(obj, characterOffset)

        # Reset focus if need be.
        #
        if obj != orca_state.locusOfFocus:
            orca.setLocusOfFocus(None, obj, notifyScript=False)

            # We'd like the object to have focus if it can take focus.
            # Otherwise, we bubble up until we find a parent that can
            # take focus.  This is to allow us to help force focus out
            # of something such as a text area and back into the
            # document content.
            #
            if script_settings.grabFocusOnAncestor:
                self._objectForFocusGrab = obj
            else:
                self._objectForFocusGrab = None

            while self._objectForFocusGrab and obj:
                role = self._objectForFocusGrab.getRole()

                # If we're within a link whose children contain the text,
                # grabbing focus on the link will result in our looping
                # back to the link and never being able to arrow through
                # the text.
                #
                if role == pyatspi.ROLE_LINK \
                   and self.utilities.queryNonEmptyText(obj):
                    self._objectForFocusGrab = None
                    break

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

            # [[[JD - I *think* we still want to do a focus grab, even with
            # the issues identified in bug 608149. Nothing bad should result
            # from grabbing focus on a non-focusable object. But I might be
            # wrong.]]]
            #
            if obj and not self._objectForFocusGrab:
                try:
                    obj.queryComponent().grabFocus()
                except (LookupError, RuntimeError):
                    pass

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
                try:
                    self._objectForFocusGrab.queryComponent().grabFocus()
                except (LookupError, RuntimeError):
                    pass

        text = self.utilities.queryNonEmptyText(obj)
        if text:
            text.setCaretOffset(characterOffset)

    def moveToMouseOver(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the mouse over which has just appeared.
        """

        if not self.lastMouseOverObject:
            # Translators: hovering the mouse over certain objects on a
            # web page causes a new object to appear such as a pop-up
            # menu. Orca has a command will move the user to the object
            # which just appeared as a result of the user hovering the
            # mouse. If this command fails, Orca will present this message.
            #
            self.presentMessage(_("Mouse over object not found."))
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

        [obj, startOffset, endOffset, string] = contents[-1]
        self.setCaretPosition(obj, endOffset)
        self.updateBraille(obj)
        # Because we're getting the word based on the WORD_END boundary
        # rather than the WORD_START boundary, we need to increment our
        # offset.
        #
        self.speakMisspelledIndicator(obj, startOffset + 1)
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
        [previousObj, previousCharOffset] = \
                                   self.findPreviousLine(obj, characterOffset)
        if not previousObj:
            return False

        self.setCaretPosition(previousObj, previousCharOffset)
        self.presentLine(previousObj, previousCharOffset)

        # Debug...
        #
        #contents = self.getLineContentsAtOffset(previousObj,
        #                                        previousCharOffset)
        #self.dumpContents(inputEvent, contents)

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

        self.setCaretPosition(nextObj, nextCharOffset)
        self.presentLine(nextObj, nextCharOffset)

        # Debug...
        #
        #contents = self.getLineContentsAtOffset(nextObj, nextCharOffset)
        #self.dumpContents(inputEvent, contents)

        return True

    def goBeginningOfLine(self, inputEvent):
        """Positions the caret offset at the beginning of the line."""

        [obj, characterOffset] = self.getCaretContext()
        line = self.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = line[0][0], line[0][1]
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
            # Translators: when the user is attempting to locate a
            # particular object and the top of the page or list is
            # reached without that object being found, we "wrap" to
            # the bottom and continue looking upwards. We need to
            # inform the user when this is taking place.
            #
            self.presentMessage(_("Wrapping to bottom."))
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
            # Translators: when the user is attempting to locate a
            # particular object and the bottom of the page or list is
            # reached without that object being found, we "wrap" to the
            # top and continue looking downwards. We need to inform the
            # user when this is taking place.
            #
            self.presentMessage(_("Wrapping to top."))
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
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            self.presentMessage(_("Live region support is off"))

    def monitorLiveRegions(self, inputEvent):
        if not _settingsManager.getSetting('inferLiveRegions'):
            _settingsManager.setSetting('inferLiveRegions', True)
            # Translators: this announces to the user that live region
            # are being monitored.
            #
            self.presentMessage(_("Live regions monitoring on"))
        else:
            _settingsManager.setSetting('inferLiveRegions', False)
            # Translators: this announces to the user that live region
            # are not being monitored.
            #
            self.liveMngr.flushMessages()
            self.presentMessage(_("Live regions monitoring off"))

    def setLivePolitenessOff(self, inputEvent):
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.setLivePolitenessOff()
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            self.presentMessage(_("Live region support is off"))

    def reviewLiveAnnouncement(self, inputEvent):
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.reviewLiveAnnouncement( \
                                    int(inputEvent.event_string[1:]))
        else:
            # Translators: this announces to the user that live region
            # support has been turned off.
            #
            self.presentMessage(_("Live region support is off"))

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
